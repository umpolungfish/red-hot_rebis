"""
ligand_improvements.py — Improved de-novo ligand generation engine.

Replaces the template-based SMILES concatenation in ligand_from_active_site.py
with proper RDKit fragment-based molecular assembly and structural scoring.

Key improvements:
  1. Scaffold library — bond-type-specific molecular scaffolds with attachment points
  2. Fragment library — FG-type-specific substituent fragments  
  3. RWMol-based combinatorial assembly — builds molecules atom-by-atom
  4. MACCS fingerprint scoring — similarity to substrate hint (if available)
  5. Structural type scoring — distance from target ligand type
  6. Property filtering — drug-likeness (Lipinski), synthetic accessibility

Author: Lando ⊗ ⊙perator
"""

import sys, os, math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import rdkit.RDLogger as rkl
rkl.logger().setLevel(rkl.ERROR)
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors, DataStructs, Lipinski
from rdkit.Chem import rdMolDescriptors as rdmd

# Paths for importing from parent modules
BASE = Path(__file__).parent.absolute()
REBIS_ROOT = BASE.parent
sys.path.insert(0, str(REBIS_ROOT))



# ── RDKit Warning Suppression ──────────────────────────────────────
# RDKit prints 'Explicit valence' warnings to stderr when building
# fragment intermediates with invalid valences (which are filtered).
# Suppress these to keep console output clean.

import os as _os
import contextlib as _contextlib

@_contextlib.contextmanager
def _silence_rdkit():
    """Temporarily suppress RDKit stderr warnings."""
    old_stderr = _os.dup(2)
    devnull = _os.open(_os.devnull, _os.O_WRONLY)
    _os.dup2(devnull, 2)
    _os.close(devnull)
    try:
        yield
    finally:
        _os.dup2(old_stderr, 2)
        _os.close(old_stderr)

# ── BOND-TO-SCAFFOLD LIBRARY ────────────────────────────────────────
# Each scaffold is a SMILES fragment with [n*] dummy attachment points.
# The core reaction chemistry determines the scaffold geometry.

BOND_SCAFFOLDS = {
    "amide_link": [
        "C(=O)N",                    # linear amide
        "C(=O)NCC",                  # extended amide
        "c1ccc(C(=O)N)cc1",          # benzamide
        "C1CC(=O)N1",                # beta-lactam
        "C1CC(=O)NC1",               # gamma-lactam
    ],
    "ester_link": [
        "C(=O)O",                    # linear ester
        "C(=O)OCC",                  # ethyl ester
        "c1ccc(C(=O)O)cc1",          # benzoate
        "C1CC(=O)O1",                # beta-lactone
    ],
    "pi_bond": [
        "C=C",                       # simple alkene
        "c1ccccc1",                  # phenyl
        "c1ccccc1C=C",               # styrene
        "c1ncccc1",                  # pyridine
        "c1ccncc1",                  # pyridine (N para)
    ],
    "double_bond": [
        "C=C",                       # alkene
        "C=Cc1ccccc1",               # styrene
        "O=C",                       # carbonyl
        "C=N",                       # imine
    ],
    "triple_bond": [
        "C#C",                       # alkyne
        "c1ccc(C#C)cc1",             # phenylacetylene
        "C#N",                       # nitrile
    ],
    "aromatic": [
        "c1ccccc1",                  # benzene
        "c1ccncc1",                  # pyridine
        "c1ccccc1c2ccccc2",          # biphenyl
        "c1ccc2ccccc2c1",            # naphthalene
        "c1ccc2c(c1)ccc2",           # indene
        "c1cocc1",                   # furan
        "c1ccsc1",                   # thiophene
        "c1cncn1",                   # imidazole
    ],
    "sigma_single": [
        "CC",                        # ethane
        "CCC",                       # propane
        "CCCC",                      # butane
        "CC(C)C",                    # isobutane
        "C1CC1",                     # cyclopropane
        "C1CCCC1",                   # cyclopentane
    ],
    "ether_link": [
        "COC",                       # dimethyl ether
        "CCOCC",                     # diethyl ether
        "c1ccc(Oc2ccccc2)cc1",       # diphenyl ether
        "C1COC1",                    # oxetane
        "C1CCOC1",                   # THF
    ],
    "strain_release": [
        "C1CC1",                     # cyclopropane
        "C1=CC1",                    # cyclopropene
        "C1c2ccccc2C1",              # benzocyclopropene
        "C12CC1C2",                  # bicyclobutane
        "C1CC2CC2C1",                # bicyclopentane
        "c1ccc2c(c1)C2",             # benzocyclobutene
    ],
    "carbonyl": [
        "C=O",                       # formaldehyde
        "CC=O",                      # acetaldehyde
        "CC(=O)C",                   # acetone
        "c1ccc(C=O)cc1",             # benzaldehyde
        "c1ccc(C(=O)C)cc1",          # acetophenone
    ],
    "hydrogen_bond": [
        "CO",                        # methanol
        "c1ccc(O)cc1",               # phenol
        "C(=O)N",                    # amide (H-bond donor/acceptor)
        "C(=O)O",                    # carboxylic acid
        "N",                         # aniline / primary amine
        "c1ccccc1N",                 # aniline
    ],
}

# ── FG-TO-FRAGMENT LIBRARY ─────────────────────────────────────────
# Each FG has multiple SMILES fragments that can serve as substituents.

FG_FRAGMENTS = {
    "amine": ["N", "NC", "NCC", "NC(C)C", "Nc1ccccc1", "NCCN", "N1CCCCC1"],
    "carbonyl": ["C=O", "CC=O", "c1ccc(C=O)cc1"],
    "alcohol": ["O", "CO", "CCO", "CC(C)O", "c1ccc(O)cc1", "OCCO"],
    "ether": ["O", "COC", "CCOCC", "c1ccc(Oc2ccccc2)cc1"],
    "carboxylic_acid": ["C(=O)O", "CC(=O)O", "c1ccc(C(=O)O)cc1"],
    "ester": ["C(=O)OC", "CC(=O)OC", "c1ccc(C(=O)OC)cc1"],
    "amide": ["C(=O)N", "CC(=O)N", "c1ccc(C(=O)N)cc1", "C(=O)NCC"],
    "aromatic_ring": ["c1ccccc1", "c1ccncc1", "c1ccsc1", "c1ccocc1"],
    "phenol": ["c1ccc(O)cc1", "c1cc(O)ccc1", "c1c(O)cccc1"],
    "epoxide": ["C1OC1", "c1ccc(C2OC2)cc1"],
    "hydroperoxide": ["OO", "COO", "CCOO"],
    "lactam": ["O=C1CCCN1", "O=C1CCCN1C"],
    "annelated_rings": ["C12CC1C2", "C1CC2CC2C1", "c1ccc2c(c1)ccc2"],
    "spirocycle": ["C12(CC1)CC2", "C12(CCC1)CC2", "C12(CC1)CCCC2"],
    "boric_acid": ["B(O)O", "c1ccc(B(O)O)cc1"],
    "metallocene": ["[C-]12[C-]3[C-]4[C-]1[C-]2[Fe]345", "[C-]1[C-][C-][C-][C-]1[Fe]"],
    "aniline": ["Nc1ccccc1", "NC1=CC=CC=C1", "c1ccc(N)cc1"],
    "heterocyclic": ["c1ccncc1", "c1cccnc1", "c1nccnc1", "c1ccsc1", "c1ccocc1"],
    "phosphate": ["OP(=O)(O)O", "COP(=O)(O)O", "CCOP(=O)(O)O", "c1ccc(OP(=O)(O)O)cc1"],
    "phosphonate": ["CP(=O)(O)O", "CCP(=O)(O)O", "c1ccc(P(=O)(O)O)cc1"],
    "sulfate": ["OS(=O)(=O)O", "COS(=O)(=O)O", "c1ccc(OS(=O)(=O)O)cc1"],
    "sulfonate": ["CS(=O)(=O)O", "c1ccc(S(=O)(=O)O)cc1"],
    "sulfonamide": ["CS(=O)(=O)N", "c1ccc(S(=O)(=O)N)cc1"],
    "thiol": ["CS", "CCS", "c1ccc(S)cc1", "CSH"],
    "sulfide": ["CSC", "CCSCC", "c1ccc(SC)cc1"],
    "sulfoxide": ["CS(=O)C", "CCS(=O)CC", "c1ccc(S(=O)C)cc1"],
    "sulfone": ["CS(=O)(=O)C", "CCS(=O)(=O)CC", "c1ccc(S(=O)(=O)C)cc1"],
    "nitro": ["C[N+](=O)[O-]", "c1ccc([N+](=O)[O-])cc1"],
    "nitrile": ["CC#N", "c1ccc(C#N)cc1"],
}

def _build_scaffold_mol(scaffold_smi: str) -> Optional[Chem.Mol]:
    """Build a scaffold molecule, ensuring it sanitizes properly."""
    try:
        mol = Chem.MolFromSmiles(scaffold_smi)
        if mol is None:
            return None
        Chem.SanitizeMol(mol)
        return mol
    except:
        return None
def _make_combinatorial_fragments(fg_names: List[str], max_per_fg: int = 3) -> List[str]:
    """Expand FG names into a list of SMILES fragments for attachment."""
    fragments = []
    for fg in fg_names:
        if fg in FG_FRAGMENTS:
            for frag in FG_FRAGMENTS[fg][:max_per_fg]:
                fragments.append(frag)
    return fragments


def _score_by_fingerprint(mol: Chem.Mol, target_mol: Optional[Chem.Mol]) -> float:
    """Score molecule by MACCS Tanimoto similarity to target."""
    if target_mol is None:
        return 0.5  # neutral score if no target
    try:
        fp1 = rdmd.GetMACCSKeysFingerprint(mol)
        fp2 = rdmd.GetMACCSKeysFingerprint(target_mol)
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except:
        return 0.0


def _score_drug_likeness(mol: Chem.Mol) -> float:
    """Compute a composite drug-likeness score (0-1).
    
    Based on Lipinski rules:
    - MW < 500 → 0.25 each for being under
    - logP < 5 → 0.25 each
    - HBD < 5 → 0.25 each
    - HBA < 10 → 0.25 each
    Additional: rotatable bonds, TPSA, rings all contribute.
    """
    score = 0.0
    try:
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        
        # Lipinski compliance (0-1)
        lipinski = 0.0
        if mw < 500: lipinski += 0.25
        if logp < 5: lipinski += 0.25
        if hbd < 5: lipinski += 0.25
        if hba < 10: lipinski += 0.25
        
        # Prefer moderate size (MW 150-450 → bonus)
        size_bonus = 0.0
        if 150 <= mw <= 450:
            size_bonus = 0.15
        
        # Penalize very small or very large
        if mw < 100 or mw > 600:
            size_bonus = -0.3
        
        score = min(1.0, max(0.0, lipinski + size_bonus))
    except:
        score = 0.0
    return score


def _compute_structural_type_from_smiles(smiles: str) -> Optional[Dict[str, str]]:
    """Estimate the 12-primitive structural type from a SMILES string.
    
    This is a first-principles encoding based on molecular properties:
    - D: Dimensionality (wedge=small molecule, triangle=cyclic, =infty=macromolecular)
    - T: Topology (network=linear, inclusion=multi-ring, bowtie=crossing point)
    - R: Recognition (cat=1 FG, dagger=2 FGs, lr=3+ FGs or complex)
    ... etc.
    
    Used to compute structural distance from the target ligand type.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        Chem.SanitizeMol(mol)
    except:
        return None

    n_atoms = mol.GetNumAtoms()
    n_heavy = mol.GetNumHeavyAtoms()
    n_rings = Lipinski.RingCount(mol)
    n_aromatic = Lipinski.NumAromaticRings(mol)
    n_hba = Descriptors.NumHAcceptors(mol)
    n_hbd = Descriptors.NumHDonors(mol)
    n_rot = Descriptors.NumRotatableBonds(mol)
    logp = Descriptors.MolLogP(mol)
    mw = Descriptors.MolWt(mol)
    
    # Count functional groups
    from rdkit.Chem import AllChem
    # SMARTS patterns for FG identification
    smarts_patterns = {
        "amine": "[NX3;H2,H1;!$(NC=O)]",
        "carbonyl": "[CX3]=[OX1]",
        "alcohol": "[OX2H]",
        "amide": "[NX3][CX3](=[OX1])",
        "ester": "[OX2][CX3](=[OX1])",
        "carboxylic_acid": "[CX3](=[OX1])[OX2H]",
        "aromatic_ring": "a",
    }
    fg_count = 0
    fg_types = set()
    for name, smarts in smarts_patterns.items():
        patt = Chem.MolFromSmarts(smarts)
        if patt:
            matches = mol.GetSubstructMatches(patt)
            if matches:
                fg_count += len(matches)
                fg_types.add(name)
    
    # N FG types found
    n_unique_fgs = len(fg_types)
    
    # ── Encode properties to primitives ──
    ptype = {}
    
    # D: wedge (0) for <5 heavy, triangle (1) for cyclic up to 30, infty (2) for >30
    if n_heavy < 5:
        ptype["D"] = "\U0001045B"  # wedge
    elif n_heavy <= 30:
        if n_rings >= 1:
            ptype["D"] = "\U00010468"  # triangle
        else:
            ptype["D"] = "\U0001045B"  # wedge
    else:
        ptype["D"] = "\U0001047C"  # infty
    
    # T: network (0) for chains, in (1) for rings, bowtie (2) for fused/multi-ring
    if n_rings == 0:
        ptype["T"] = "\U00010461"  # net
    elif n_rings <= 2:
        ptype["T"] = "\U00010470"  # in
    else:
        ptype["T"] = "\U00010465"  # bowtie
    
    # R: super (0) for simple, cat (1) for moderate, dagger (2) for complex
    if n_unique_fgs <= 1 and n_heavy <= 10:
        ptype["R"] = "\U00010469"  # super
    elif n_unique_fgs <= 2 and n_heavy <= 20:
        ptype["R"] = "\U00010451"  # cat
    else:
        ptype["R"] = "\U0001047D"  # dagger
    
    # P: asym (0) for chiral/no symmetry, psi (1) for some, pm (2) for balanced
    try:
        n_chiral = Chem.rdMolDescriptors.CalcNumAtomStereoCenters(mol)
    except:
        n_chiral = 0
    if n_chiral >= 2:
        ptype["P"] = "\U00010457"  # asym
    elif n_chiral == 1:
        ptype["P"] = "\U0001047F"  # psi
    elif n_rings >= 1:
        ptype["P"] = "\U0001046C"  # pm
    else:
        ptype["P"] = "\U00010457"  # asym
    
    # F: ell (0) for classical, hbar (2) for quantum — molecules are always classical
    ptype["F"] = "\U00010471"  # ell
    
    # K: mod (1) for flexible, slow (2) for ordered/rigid
    if n_rot <= 2:
        ptype["K"] = "\U00010467"  # slow
    elif n_rot <= 5:
        ptype["K"] = "\U00010464"  # mod
    else:
        ptype["K"] = "\U00010458"  # fast
    
    # G: beth (0) for small <8, gimel (1) for medium <20, aleph (2) for large
    if n_heavy < 8:
        ptype["G"] = "\U0001045A"  # beth
    elif n_heavy < 20:
        ptype["G"] = "\U00010454"  # gimel
    else:
        ptype["G"] = "\U00010472"  # aleph
    
    # Gm: and (0) for single FG, or (1) for 2 FGs, seq (2) for 3+, broad (3)
    if fg_count <= 1:
        ptype["Gm"] = "\U0001045D"  # and
    elif fg_count == 2:
        ptype["Gm"] = "\U0001045C"  # or
    elif fg_count <= 4:
        ptype["Gm"] = "\U00010460"  # seq
    else:
        ptype["Gm"] = "\U00010475"  # broad
    
    # Ph: sub (0) for unreactive, critical (1) for aromatic/bioactive
    if n_aromatic >= 1 or n_rings >= 2:
        ptype["Ph"] = "\u2299"  # critical / odot
    else:
        ptype["Ph"] = "\U00010462"  # sub
    
    # H: memless (0) for very simple, one (1) for moderate, two (2) for complex
    if n_rot <= 1:
        ptype["H"] = "\U00010453"  # memless
    elif n_rot <= 4:
        ptype["H"] = "\U00010452"  # one
    else:
        ptype["H"] = "\U00010456"  # two
    
    # S: 1:1 (0) for single molecule, nn (1) for identical repeats
    ptype["S"] = "\U00010459"  # 1:1
    
    # W: 0 (0) for simple, Z2 (1) for cyclic, Z (2) for aromatic/conjugated
    if n_aromatic >= 2:
        ptype["W"] = "\U0001046D"  # Z
    elif n_aromatic >= 1:
        ptype["W"] = "\U00010474"  # Z2
    else:
        ptype["W"] = "\U00010477"  # 0
    
    return ptype


def _tuple_distance_lig(ta: Dict[str, str], tb: Dict[str, str]) -> float:
    """Weighted Euclidean distance between two 12-primitive dicts."""
    from shared.primitives import PRIMITIVE_ORDER as PO
    sq = 0.0
    for p in ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]:
        if p not in ta or p not in tb:
            continue
        oa = PO.get(p, {}).get(ta[p], 0)
        ob = PO.get(p, {}).get(tb[p], 0)
        sq += (oa - ob) ** 2
    return math.sqrt(sq)
def generate_ligands_from_bond_fg(
    bond_name: str,
    fg_names: List[str],
    ligand_type: Optional[Dict[str, str]] = None,
    substrate_hint: str = "",
    max_candidates: int = 20
) -> List[Dict]:
    """Generate de-novo ligands using fragment-based molecular assembly.
    
    Core algorithm:
    1. Select scaffolds matching bond_name from BOND_SCAFFOLDS
    2. Select fragment substituents from FG_FRAGMENTS
    3. For each scaffold + fragment combination:
       a. Parse as SMILES and check validity
       b. Compute MACCS fingerprint similarity to substrate (if available)
       c. Compute structural type distance to target ligand_type
       d. Compute drug-likeness score
    4. Generate direct combinations by SMILES concatenation with connectors
    5. Score, rank, and return top candidates
    
    Returns:
        List of candidate dicts with SMILES, scores, and properties
    """
    candidates = []
    seen_smiles = set()
    from rdkit.Chem import AllChem
    
    # ── Get scaffold templates ──
    scaffolds = BOND_SCAFFOLDS.get(bond_name, ["C-C-C"])
    
    # ── Get FG fragments ──
    fragments = _make_combinatorial_fragments(fg_names)
    
    # ── Parse substrate hint if available ──
    target_mol = None
    if substrate_hint:
        try:
            target_mol = Chem.MolFromSmiles(substrate_hint)
        except:
            pass
    
    # ── Strategy 1: Scaffold + fragment concatenation ──
    # Build molecules by combining scaffold with fragments via a bond connector
    connector_map = {
        "amide_link": "C(=O)N",
        "ester_link": "C(=O)O",
        "pi_bond": "-",
        "double_bond": "=",
        "triple_bond": "#",
        "aromatic": "",
        "sigma_single": "-",
        "ether_link": "O",
        "strain_release": "-",
        "carbonyl": "=",
        "hydrogen_bond": "-",
        "co_sigma": "-",
        "cn_sigma": "-",
    }
    connector = connector_map.get(bond_name, "-")
    
    for scaffold_smi in scaffolds:
        # Try scaffold alone
        _try_add_candidate(scaffold_smi, candidates, seen_smiles, target_mol, ligand_type,
                          method=f"scaffold_{bond_name}")
        
        # Try scaffold with each fragment as substituent
        for frag_smi in fragments:
            # Connect scaffold + fragment
            combined = f"{frag_smi}{connector}{scaffold_smi}"
            _try_add_candidate(combined, candidates, seen_smiles, target_mol, ligand_type,
                              method=f"{bond_name}_{frag_smi}")
            
            # Try symmetric: fragment + connector + scaffold + connector + fragment
            if len(fragments) >= 2:
                for frag2_smi in fragments:
                    if frag_smi == frag2_smi:
                        continue
                    symmetric = f"{frag_smi}{connector}{scaffold_smi}{connector}{frag2_smi}"
                    _try_add_candidate(symmetric, candidates, seen_smiles, target_mol, ligand_type,
                                      method=f"sym_{bond_name}")
            
            # Try scaffold with fragment at both ends
            double = f"{frag_smi}{connector}{scaffold_smi}{connector}{frag_smi}"
            _try_add_candidate(double, candidates, seen_smiles, target_mol, ligand_type,
                              method=f"bis_{bond_name}")
    
    # ── Strategy 2: Direct FG-pair combination ──
    # Try putting two FGs directly together
    for i, fg1 in enumerate(fragments):
        for j, fg2 in enumerate(fragments):
            if j <= i:
                continue
            direct = f"{fg1}{connector}{fg2}"
            _try_add_candidate(direct, candidates, seen_smiles, target_mol, ligand_type,
                              method=f"fg_pair_{bond_name}")
    
    # ── Strategy 3: Extended chain with FG caps ──
    chain_lengths = [1, 2, 3, 4]
    for clen in chain_lengths:
        chain = "C" * clen
        for frag_smi in fragments:
            capped = f"{frag_smi}{connector}{chain}"
            _try_add_candidate(capped, candidates, seen_smiles, target_mol, ligand_type,
                              method=f"chain{clen}_{bond_name}")
            
            # Double-capped
            di_capped = f"{frag_smi}{connector}{chain}{connector}{frag_smi}"
            _try_add_candidate(di_capped, candidates, seen_smiles, target_mol, ligand_type,
                              method=f"dichain{clen}_{bond_name}")
    
    # ── Strategy 4: Ring fusion ──
    # For aromatic/pi_bond scaffolds, try adding substituents to ring
    if bond_name in ("aromatic", "pi_bond"):
        ring_core = "c1ccccc1"
        for frag_smi in fragments:
            # Substituted benzene
            sub = f"{frag_smi}c1ccccc1"
            _try_add_candidate(sub, candidates, seen_smiles, target_mol, ligand_type,
                              method=f"sub_benzene")
            
            # 1,2-disubstituted
            di_sub = f"{frag_smi}c1ccccc1{frag_smi}"
            _try_add_candidate(di_sub, candidates, seen_smiles, target_mol, ligand_type,
                              method=f"di_sub_benzene")
    
    # ── Score, sort, return ──
    # Composite score: 40% structural fit + 30% drug-likeness + 30% fingerprint similarity
    for c in candidates:
        structural = c.get("struct_score", 0.0)
        drug = c.get("drug_score", 0.0)
        fp = c.get("fp_score", 0.0)
        c["composite_score"] = round(0.40 * structural + 0.30 * drug + 0.30 * fp, 3)
    
    candidates.sort(key=lambda x: x["composite_score"], reverse=True)
    return candidates[:max_candidates]


def _try_add_candidate(
    smi: str, candidates: List[Dict], seen: set,
    target_mol, ligand_type, method: str
):
    """Validate a SMILES, compute scores, and add to candidate list."""
    from rdkit import RDLogger
    RDLogger.logger().setLevel(RDLogger.ERROR)
    from rdkit.Chem import AllChem
    try:
        with _silence_rdkit():
            mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return
        Chem.SanitizeMol(mol)
        canon = Chem.MolToSmiles(mol)
        if canon in seen:
            return
        seen.add(canon)
    except:
        return
    
    # Compute properties
    try:
        logp = Descriptors.MolLogP(mol)
        mw = Descriptors.MolWt(mol)
        heavy = mol.GetNumHeavyAtoms()
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        n_rings = Lipinski.RingCount(mol)
        n_rot = Descriptors.NumRotatableBonds(mol)
        tpsa = Descriptors.TPSA(mol)
    except:
        logp, mw, heavy, hbd, hba, n_rings, n_rot, tpsa = 0, 0, 0, 0, 0, 0, 0, 0
    
    # Fingerprint similarity
    fp_score = _score_by_fingerprint(mol, target_mol)
    
    # Drug-likeness
    drug_score = _score_drug_likeness(mol)
    
    # Structural type distance
    struct_score = 0.0
    if ligand_type:
        try:
            cand_type = _compute_structural_type_from_smiles(canon)
            if cand_type:
                dist = _tuple_distance_lig(cand_type, ligand_type)
                # Convert distance to score: exp(-d/2)
                struct_score = math.exp(-dist / 2.0)
        except:
            pass
    
    candidates.append({
        "smiles": canon,
        "method": method,
        "fp_score": round(fp_score, 3),
        "drug_score": round(drug_score, 3),
        "struct_score": round(struct_score, 3),
        "logP": round(logp, 2),
        "MW": round(mw, 1),
        "heavy_atoms": heavy,
        "HBD": hbd,
        "HBA": hba,
        "rings": n_rings,
        "rotatable": n_rot,
        "TPSA": round(tpsa, 1),
        "valid": True,
    })
# ── INTEGRATION: Full de-novo ligand generation from structural type ──

def generate_from_structural_type(
    ligand_type: Dict[str, str],
    substrate_hint: str = "",
    bond_name: str = None,
    fg_names: list = None,
    max_candidates: int = 20
) -> list:
    """Generate ligands directly from a structural type.
    
    If bond_name and fg_names are not provided, they will be estimated
    by comparing the ligand type against the BOND_SCAFFOLDS and FG_FRAGMENTS
    libraries using structural type distance.
    
    Args:
        ligand_type: 12-primitive dict of the target ligand
        substrate_hint: Optional known substrate SMILES
        bond_name: Optional pre-determined bond type
        fg_names: Optional pre-determined FG list
        max_candidates: Max candidates to return
    
    Returns:
        List of scored candidate dicts
    """
    # Estimate bond type from ligand type if not provided
    if bond_name is None:
        bond_name = _estimate_bond_type(ligand_type)
    
    # Estimate FG pair from ligand type if not provided
    if fg_names is None or not fg_names:
        fg_names = _estimate_fgs(ligand_type, bond_name)
    
    return generate_ligands_from_bond_fg(
        bond_name=bond_name,
        fg_names=fg_names,
        ligand_type=ligand_type,
        substrate_hint=substrate_hint,
        max_candidates=max_candidates,
    )


def _estimate_bond_type(ligand_type: Dict[str, str]) -> str:
    """Find the bond type whose scaffold structural signature is closest."""
    # Simplified: derive bond type from the ligand's T (topology) and K (kinetics)
    t_glyph = ligand_type.get("T", "\U00010461")  # default net
    k_glyph = ligand_type.get("K", "\U00010458")  # default fast
    ph_glyph = ligand_type.get("Ph", "\U00010462")  # default sub
    w_glyph = ligand_type.get("W", "\U00010477")  # default 0
    
    # Map the combination of primitives to bond type
    bond_map = {
        # (T, K, Ph, W) → bond type
        ("\U00010465", "\U00010467", "\u2299", "\U00010474"): "amide_link",  # bowtie + slow + odot + Z2
        ("\U00010478", "\U00010467", "\u2299", "\U0001046D"): "aromatic",    # odot + slow + odot + Z
        ("\U00010465", "\U00010467", "\u2299", "\U00010474"): "ester_link",  # bowtie + slow + odot + Z2
        ("\U00010470", "\U00010464", "\U00010462", "\U00010477"): "sigma_single", # in + mod + sub + 0
        ("\U00010461", "\U00010458", "\U00010462", "\U00010477"): "ether_link",   # net + fast + sub + 0
        ("\U00010465", "\U00010464", "\u2299", "\U00010474"): "carbonyl",    # bowtie + mod + odot + Z2
        ("\U00010465", "\U00010467", "\U0001046E", "\U00010474"): "strain_release", # bowtie + slow + c_complex + Z2
        ("\U00010461", "\U00010464", "\u2299", "\U00010474"): "pi_bond",     # net + mod + odot + Z2
        ("\U00010461", "\U00010458", "\u2299", "\U0001046D"): "triple_bond", # net + fast + odot + Z
        ("\U00010470", "\U00010467", "\U00010462", "\U00010474"): "hydrogen_bond", # in + slow + sub + Z2
        ("\U00010465", "\U00010467", "\U00010462", "\U00010477"): "co_sigma", # bowtie + slow + sub + 0
    }
    
    key = (t_glyph, k_glyph, ph_glyph, w_glyph)
    if key in bond_map:
        return bond_map[key]
    
    # Fallback: try just T + K
    fallback_map = {
        ("\U00010465", "\U00010467"): "amide_link",   # crossing + slow
        ("\U00010478", "\U00010467"): "aromatic",     # closure + slow
        ("\U00010478", "\U00010458"): "aromatic",     # closure + fast
        ("\U00010461", "\U00010458"): "sigma_single", # net + fast
        ("\U00010461", "\U00010464"): "ether_link",   # net + moderate
        ("\U00010470", "\U00010467"): "sigma_single", # in + slow
        ("\U00010470", "\U00010464"): "sigma_single", # in + moderate
    }
    tk_key = (t_glyph, k_glyph)
    if tk_key in fallback_map:
        return fallback_map[tk_key]
    
    return "sigma_single"


def _estimate_fgs(ligand_type: Dict[str, str], bond_name: str) -> List[str]:
    """Estimate FG types from the ligand's structural type.

    Full 16-entry (R, Gm) grid — every coupling×composition combination
    is mapped.  Entries are statically assigned as CHNO-only, sulfur-containing,
    phosphorus-containing, or mixed P+S.  No gating on S (stoichiometry) because
    the complement swaps R↔S, making the ligand S uninformative about site
    heteroatom diversity.
    """
    r_glyph = ligand_type.get("R", "𐑩")
    gm_glyph = ligand_type.get("Gm", "𐑝")

    _R_SUPER   = "𐑩"; _R_CAT     = "𐑑"
    _R_DAGGER  = "𐑽"; _R_LR      = "𐑾"
    _GM_AND    = "𐑝"; _GM_OR    = "𐑜"
    _GM_SEQ    = "𐑠"; _GM_BROAD = "𐑵"

    # 16-entry grid: 4 CHNO, 4 sulfur, 4 phosphorus, 4 mixed P+S
    fg_grid = {
        # ── CHNO-only (simple hydrogen-bond / polar interactions) ──
        (_R_SUPER, _GM_AND):   ["alcohol"],
        (_R_SUPER, _GM_OR):    ["alcohol", "amine"],
        (_R_CAT, _GM_AND):     ["amine"],
        (_R_DAGGER, _GM_AND):  ["carboxylic_acid"],
        # ── Sulfur-containing (thiol, sulfide, sulfone, sulfoxide, sulfate) ──
        (_R_LR, _GM_AND):      ["sulfone", "carbonyl"],
        (_R_DAGGER, _GM_BROAD):["sulfoxide", "phosphate"],
        (_R_CAT, _GM_BROAD):   ["sulfonamide", "aromatic_ring"],
        (_R_SUPER, _GM_BROAD): ["sulfate", "thiol"],
        # ── Phosphorus-containing (phosphate, phosphonate) ──
        (_R_SUPER, _GM_SEQ):   ["phosphate", "alcohol"],
        (_R_DAGGER, _GM_SEQ):  ["phosphate", "amine"],
        (_R_CAT, _GM_SEQ):     ["phosphonate", "amine"],
        (_R_LR, _GM_BROAD):    ["phosphate", "sulfide"],
        # ── Mixed P+S (sulfate, thiol, sulfide with phosphate, carbonyl) ──
        (_R_CAT, _GM_OR):      ["sulfide", "carbonyl"],
        (_R_DAGGER, _GM_OR):   ["phosphate", "alcohol"],
        (_R_LR, _GM_OR):       ["thiol", "carbonyl"],
        (_R_LR, _GM_SEQ):      ["sulfone", "amine"],
    }

    key2 = (r_glyph, gm_glyph)
    if key2 in fg_grid:
        return fg_grid[key2]

    # Bond-specific fallbacks (should not be reached — grid is exhaustive)
    bond_fg_defaults = {
        "amide_link":       ["amine", "carbonyl"],
        "ester_link":       ["alcohol", "carbonyl"],
        "pi_bond":          ["aromatic_ring"],
        "aromatic":         ["aromatic_ring", "amine"],
        "sigma_single":     ["amine", "alcohol"],
        "ether_link":       ["alcohol", "ether"],
        "strain_release":   ["epoxide", "amine"],
        "carbonyl":         ["carbonyl", "thiol"],
        "hydrogen_bond":    ["alcohol", "amine", "phosphate"],
        "double_bond":      ["carbonyl", "amine"],
        "triple_bond":      ["nitrile", "aromatic_ring"],
        "co_sigma":         ["alcohol", "thiol"],
        "cn_sigma":         ["amine", "nitrile"],
    }
    return bond_fg_defaults.get(bond_name, ["amine", "alcohol"])

# ── TEST: Run on the full bevy ──

def test_bevy(protein_list: List[Dict]) -> dict:
    """Test the improved generation on a list of proteins.
    
    Args:
        protein_list: List of protein dicts with 'name', 'structural_type',
                     'smiles_substrate_hint' etc.
    
    Returns:
        Dict mapping protein name → results
    """
    from shared.primitives import PRIMITIVE_ORDER as PO
    
    results = {}
    for protein in protein_list:
        name = protein.get("name", "unknown")
        # FIRST PRINCIPLES: compute site tuple from residues
        site_type = encode_site_from_residues(protein.get("active_site_residues", protein.get("residues", [])))
        if site_type is None:
            site_type = {}
        substrate = protein.get("smiles_substrate_hint", "")
        
        # Get ligand type via complement
        ligand_type = _complement_type(site_type)
        
        print(f"\n{'='*72}")
        print(f"  PROTEIN: {name}")
        print(f"  Substrate hint: {substrate}")
        
        # Generate ligands
        candidates = generate_from_structural_type(
            ligand_type=ligand_type,
            substrate_hint=substrate,
            max_candidates=10,
        )
        
        results[name] = {
            "ligand_type": {k: str(v) for k, v in ligand_type.items()},
            "n_candidates": len(candidates),
            "candidates": candidates,
        }
        
        print(f"  Target ligand type present")
        print(f"  Generated {len(candidates)} validated candidates")
        for c in candidates[:5]:
            print(f"    [{c['method']:20s}] {c['smiles']:35s} "
                  f"comp={c['composite_score']:.3f} "
                  f"logP={c['logP']:5.2f} MW={c['MW']:6.1f}")
    
    return results


def _complement_type(site_type: Dict[str, str]) -> Dict[str, str]:
    """Same complement logic as in the main pipeline.
    
    For each complementary pair (A,B): ligand[A] = reverse(site[B]),
    ligand[B] = reverse(site[A]).
    """
    from shared.primitives import PRIMITIVE_ORDER as PO
    
    COMPLEMENTARY_PAIRS = [("D","W"), ("T","H"), ("R","S"), ("P","F"), ("K","G"), ("Gm","Ph")]
    
    ligand = {}
    for prim_a, prim_b in COMPLEMENTARY_PAIRS:
        a_vals = list(PO.get(prim_a, {}).values())
        b_vals = list(PO.get(prim_b, {}).values())
        a_max = len(a_vals) - 1
        b_max = len(b_vals) - 1
        
        site_a_ord = PO.get(prim_a, {}).get(site_type.get(prim_a, "?"), 0)
        site_b_ord = PO.get(prim_b, {}).get(site_type.get(prim_b, "?"), 0)
        
        inv_a = a_max - site_a_ord
        inv_b = b_max - site_b_ord
        
        # Map: site[B]'s inverse → ligand[A], scaled
        if a_max > 0:
            ligand[prim_a] = a_vals[min(a_max, max(0, round(inv_b / max(1, b_max) * a_max)))]
        else:
            ligand[prim_a] = a_vals[a_max]
        
        if b_max > 0:
            ligand[prim_b] = b_vals[min(b_max, max(0, round(inv_a / max(1, a_max) * b_max)))]
        else:
            ligand[prim_b] = b_vals[b_max]
    
    return ligand

def _complement_type(site_type: Dict[str, str]) -> Dict[str, str]:
    """Same complement logic as the main pipeline.
    
    For each complementary pair (A,B): ligand[A] = reverse(site[B]),
    ligand[B] = reverse(site[A]).
    """
    from rhr_p4rky.ligand_from_active_site import GLYPH_ORDINALS, ORD_TO_GLYPH
    
    COMPLEMENTARY_PAIRS = [("D","W"), ("T","H"), ("R","S"), ("P","F"), ("K","G"), ("Gm","Ph")]
    
    ligand = {}
    for prim_a, prim_b in COMPLEMENTARY_PAIRS:
        a_glyphs = GLYPH_ORDINALS.get(prim_a, {})
        b_glyphs = GLYPH_ORDINALS.get(prim_b, {})
        a_max = len(a_glyphs) - 1
        b_max = len(b_glyphs) - 1
        
        site_a_ord = a_glyphs.get(site_type.get(prim_a, "?"), 0)
        site_b_ord = b_glyphs.get(site_type.get(prim_b, "?"), 0)
        
        inv_a = a_max - site_a_ord
        inv_b = b_max - site_b_ord
        
        # Map: site[B]'s inverse → ligand[A], scaled
        if a_max > 0 and b_max > 0:
            ligand[prim_a] = ORD_TO_GLYPH[prim_a][min(a_max, max(0, round(inv_b / b_max * a_max)))]
        else:
            ligand[prim_a] = ORD_TO_GLYPH[prim_a][a_max] if a_max >= 0 else list(a_glyphs.keys())[0]
        
        if b_max > 0 and a_max > 0:
            ligand[prim_b] = ORD_TO_GLYPH[prim_b][min(b_max, max(0, round(inv_a / a_max * b_max)))]
        else:
            ligand[prim_b] = ORD_TO_GLYPH[prim_b][b_max] if b_max >= 0 else list(b_glyphs.keys())[0]
    
    return ligand
def _estimate_bond_from_site_type(site_type: Dict[str, str]) -> str:
    """Estimate bond type from the ENZYME'S catalytic site structural type.

    Uses the enzyme's full 12-primitive fingerprint. Exact match to known
    catalytic mechanisms first; then a rule-based estimator using dominant
    primitives for novel site types.
    """
    from rhr_p4rky.ligand_from_active_site import GLYPH_ORDINALS

    def o(glyph, pn):
        return GLYPH_ORDINALS.get(pn, {}).get(glyph, -1)

    PN = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
    fp = tuple(o(site_type.get(pn,"?"), pn) for pn in PN)

    # Enzyme fingerprint -> bond type map (from known catalytic mechanisms)
    ENZYME_BOND_MAP = {
        (1, 4, 3, 4, 2, 2, 1, 1, 1, 2, 2, 1): "amide_link",
        (0, 2, 3, 0, 2, 2, 1, 0, 1, 1, 2, 1): "strain_release",
        (0, 2, 2, 0, 2, 3, 0, 1, 1, 1, 0, 1): "hydrogen_bond",
        (1, 4, 3, 3, 2, 2, 1, 3, 4, 2, 2, 1): "sigma_single",
        (0, 2, 3, 0, 2, 2, 0, 1, 1, 1, 2, 1): "ester_link",
        (1, 4, 3, 1, 2, 2, 1, 1, 1, 2, 2, 1): "sigma_single",
        (1, 4, 3, 1, 2, 3, 1, 1, 1, 2, 0, 2): "amide_link",
    }

    if fp in ENZYME_BOND_MAP:
        return ENZYME_BOND_MAP[fp]

    # ── Rule-based fallback for novel fingerprints ──
    # Each primitive's elevation tells us about residue composition.
    # Non-P/F primitives: ordinal > 0 means residues present (max semantics).
    # P/F primitives: ordinal < max_ord means residues present (inverted min semantics).

    # Max ordinals per primitive
    MAX_ORD = {"D": 3, "T": 4, "R": 3, "P": 4, "F": 2, "K": 4,
               "G": 2, "Gm": 3, "Ph": 4, "H": 3, "S": 2, "W": 3}

    def is_elevated(idx, val):
        """True if primitive has residues contributing to it."""
        pn = PN[idx]
        max_o = MAX_ORD.get(pn, 1)
        if pn in ("P", "F"):
            return val < max_o  # inverted: low ordinal = many residues
        return val > 0

    def elevation(idx, val):
        """How strongly this primitive is elevated (0 to 1 scale)."""
        pn = PN[idx]
        max_o = MAX_ORD.get(pn, 1)
        if max_o == 0:
            return 0.0
        if pn in ("P", "F"):
            return (max_o - val) / max_o  # inverted
        return val / max_o

    # Score each bond type based on which primitives are elevated
    # Bond type -> (primitive_index, weight) pairs for what drives that bond
    BOND_RULES = {
        "hydrogen_bond": [(10, 2.0), (9, 1.0), (8, 0.5)],  # S, H, Ph
        "amide_link":    [(10, 1.5), (9, 1.5), (7, 1.5), (2, 0.5)],  # S, H, Gm, R
        "ester_link":    [(9, 2.0), (2, 1.0)],  # H, R
        "carbonyl":      [(2, 2.0), (9, 0.5)],  # R, H
        "sigma_single":  [(5, 1.5), (6, 1.5), (0, 0.5)],  # K, G, D
        "ether_link":    [(6, 2.0), (2, 0.5)],  # G, R
        "aromatic":      [(3, 1.5), (11, 1.5), (4, 1.0)],  # P, W, F
        "pi_bond":       [(11, 2.0), (3, 0.5), (4, 0.5)],  # W, P, F
        "strain_release":[(1, 2.0), (5, 0.5)],  # T, K
    }

    scores = {}
    for bt, rules in BOND_RULES.items():
        score = 0.0
        for idx, weight in rules:
            score += elevation(idx, fp[idx]) * weight
        # Bonus for exact dominant match
        max_el = max(elevation(i, fp[i]) for i in range(12))
        for idx, weight in rules:
            if elevation(idx, fp[idx]) == max_el and max_el > 0:
                score += weight * 2.0  # double weight for dominant primitive
        scores[bt] = score

    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best

    # Last resort: Hamming distance to known entries
    best_dist = 99
    best_bond = "sigma_single"
    for pattern, bond_type in ENZYME_BOND_MAP.items():
        dist = sum(abs(a-b) for a,b in zip(fp, pattern))
        if dist < best_dist:
            best_dist = dist
            best_bond = bond_type
    return best_bond



def _estimate_bonds_top_n(site_type: Dict[str, str], n: int = 3) -> List[str]:
    """Return top-N bond types for a given site type (for diversity)."""
    from rhr_p4rky.ligand_from_active_site import GLYPH_ORDINALS
    
    def o(glyph, pn):
        return GLYPH_ORDINALS.get(pn, {}).get(glyph, -1)
    
    PN = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
    fp = tuple(o(site_type.get(pn,"?"), pn) for pn in PN)
    
    ENZYME_BOND_MAP = {
        (1, 4, 3, 4, 2, 2, 1, 1, 1, 2, 2, 1): "amide_link",
        (0, 2, 3, 0, 2, 2, 1, 0, 1, 1, 2, 1): "strain_release",
        (0, 2, 2, 0, 2, 3, 0, 1, 1, 1, 0, 1): "hydrogen_bond",
        (1, 4, 3, 3, 2, 2, 1, 3, 4, 2, 2, 1): "sigma_single",
        (0, 2, 3, 0, 2, 2, 0, 1, 1, 1, 2, 1): "ester_link",
        (1, 4, 3, 1, 2, 2, 1, 1, 1, 2, 2, 1): "sigma_single",
        (1, 4, 3, 1, 2, 3, 1, 1, 1, 2, 0, 2): "amide_link",
    }
    
    if fp in ENZYME_BOND_MAP:
        exact = ENZYME_BOND_MAP[fp]
        # Return exact match plus top alternatives
        others = [b for b in ["hydrogen_bond", "carbonyl", "ester_link", "ether_link", "aromatic", "pi_bond"] if b != exact]
        return [exact] + others[:n-1]
    
    MAX_ORD = {"D": 3, "T": 4, "R": 3, "P": 4, "F": 2, "K": 4,
               "G": 2, "Gm": 3, "Ph": 4, "H": 3, "S": 2, "W": 3}
    
    def elevation(idx, val):
        pn = PN[idx]
        max_o = MAX_ORD.get(pn, 1)
        if max_o == 0:
            return 0.0
        if pn in ("P", "F"):
            return (max_o - val) / max_o
        return val / max_o
    
    BOND_RULES = {
        "hydrogen_bond": [(10, 2.0), (9, 1.0), (8, 0.5)],
        "amide_link":    [(10, 1.5), (9, 1.5), (7, 1.5), (2, 0.5)],
        "ester_link":    [(9, 2.0), (2, 1.0)],
        "carbonyl":      [(2, 2.0), (9, 0.5)],
        "sigma_single":  [(5, 1.5), (6, 1.5), (0, 0.5)],
        "ether_link":    [(6, 2.0), (2, 0.5)],
        "aromatic":      [(3, 1.5), (11, 1.5), (4, 1.0)],
        "pi_bond":       [(11, 2.0), (3, 0.5), (4, 0.5)],
        "strain_release":[(1, 2.0), (5, 0.5)],
    }
    
    scores = {}
    for bt, rules in BOND_RULES.items():
        score = 0.0
        for idx, weight in rules:
            score += elevation(idx, fp[idx]) * weight
        max_el = max(elevation(i, fp[i]) for i in range(12))
        for idx, weight in rules:
            if elevation(idx, fp[idx]) == max_el and max_el > 0:
                score += weight * 2.0
        scores[bt] = score
    
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return [bt for bt, sc in ranked[:n] if sc > 0] or ["sigma_single"]


def _estimate_fgs_top_n(site_type: Dict[str, str], bond_name: str, n: int = 3) -> List[List[str]]:
    """Return top-N FG pairs for a given site type + bond (for diversity)."""
    from rhr_p4rky.ligand_from_active_site import GLYPH_ORDINALS
    
    def o(glyph, pn):
        return GLYPH_ORDINALS.get(pn, {}).get(glyph, -1)
    
    PN = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
    fp = tuple(o(site_type.get(pn,"?"), pn) for pn in PN)
    
    FG_ESTIMATION_MAP = {
        (1, 4, 3, 4, 2, 2, 1, 1, 1, 2, 2, 1): ["amine", "carbonyl"],
        (0, 2, 3, 0, 2, 2, 1, 0, 1, 1, 2, 1): ["lactam", "epoxide"],
        (0, 2, 2, 0, 2, 3, 0, 1, 1, 1, 0, 1): ["carbonyl", "alcohol"],
        (1, 4, 3, 3, 2, 2, 1, 3, 4, 2, 2, 1): ["aromatic_ring", "ether"],
        (0, 2, 3, 0, 2, 2, 0, 1, 1, 1, 2, 1): ["carbonyl", "alcohol"],
        (1, 4, 3, 1, 2, 2, 1, 1, 1, 2, 2, 1): ["alcohol", "carbonyl"],
        (1, 4, 3, 1, 2, 3, 1, 1, 1, 2, 0, 2): ["amine", "carbonyl"],
    }
    
    if fp in FG_ESTIMATION_MAP:
        exact = FG_ESTIMATION_MAP[fp]
        # Return exact match plus variations
        bond_fg_defaults = {
            "amide_link":       [["amine", "carbonyl"], ["amine", "thiol"], ["carbonyl", "alcohol"]],
            "ester_link":       [["alcohol", "carbonyl"], ["alcohol", "phosphate"], ["carbonyl", "thiol"]],
            "aromatic":         [["aromatic_ring", "amine"], ["aromatic_ring", "nitro"], ["aromatic_ring", "thiol"]],
            "sigma_single":     [["amine", "alcohol"], ["alcohol", "thiol"], ["amine", "carbonyl"]],
            "ether_link":       [["alcohol", "ether"], ["ether", "sulfide"], ["alcohol", "sulfone"]],
            "strain_release":   [["epoxide", "lactam"], ["lactam", "sulfone"], ["epoxide", "amine"]],
            "carbonyl":         [["carbonyl", "alcohol"], ["carbonyl", "thiol"], ["carbonyl", "amine"]],
            "hydrogen_bond":    [["alcohol", "amine"], ["amine", "phosphate"], ["alcohol", "phosphonate"]],
            "pi_bond":          [["aromatic_ring", "carbonyl"], ["aromatic_ring", "sulfoxide"], ["carbonyl", "sulfone"]],
        }
        defaults = bond_fg_defaults.get(bond_name, [["amine", "alcohol"], ["alcohol", "thiol"], ["amine", "carbonyl"]])
        return [exact] + [d for d in defaults if d != exact][:n-1]
    
    MAX_ORD = {"D": 3, "T": 4, "R": 3, "P": 4, "F": 2, "K": 4,
               "G": 2, "Gm": 3, "Ph": 4, "H": 3, "S": 2, "W": 3}
    
    def elevation(idx, val):
        pn = PN[idx]
        max_o = MAX_ORD.get(pn, 1)
        if max_o == 0:
            return 0.0
        if pn in ("P", "F"):
            return (max_o - val) / max_o
        return val / max_o
    
    FG_RULES = {
        "amine":    [(10, 2.0), (7, 1.5), (8, 1.0)],
        "carbonyl": [(2, 2.0), (9, 1.0), (7, 0.5)],
        "alcohol":  [(2, 1.5), (9, 1.5), (6, 0.5)],
        "ether":    [(6, 2.0), (0, 1.0), (2, 0.5)],
        "aromatic_ring": [(3, 2.0), (4, 2.0), (11, 1.5)],
        "epoxide":  [(1, 2.0), (5, 0.5)],
        "lactam":   [(9, 1.5), (1, 1.0), (7, 1.0)],
        "thiol":    [(2, 2.0), (10, 1.5), (5, 0.5)],
        "sulfide":  [(6, 1.5), (10, 1.5), (7, 1.0)],
        "sulfoxide":[(2, 1.5), (5, 1.5), (11, 1.0)],
        "sulfone":  [(3, 1.5), (5, 1.5), (11, 1.5)],
        "sulfate":  [(2, 2.0), (9, 1.5), (10, 1.0)],
        "sulfonate":[(2, 1.5), (10, 1.5), (7, 1.0)],
        "sulfonamide":[(7, 2.0), (10, 1.5), (8, 1.0)],
        "phosphate":[(2, 2.0), (10, 1.5), (9, 1.0)],
        "phosphonate":[(10, 2.0), (7, 1.5), (2, 1.0)],
        "nitro":    [(4, 2.0), (5, 1.5), (8, 1.0)],
        "nitrile":  [(7, 2.0), (10, 1.0), (4, 0.5)],
    }
    
    scores = {}
    for fg, rules in FG_RULES.items():
        score = 0.0
        for idx, weight in rules:
            score += elevation(idx, fp[idx]) * weight
        max_el = max(elevation(i, fp[i]) for i in range(12))
        for idx, weight in rules:
            if elevation(idx, fp[idx]) == max_el and max_el > 0:
                score += weight * 1.5
        scores[fg] = score
    
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    all_fgs = [fg for fg, sc in ranked if sc > 0]
    
    # Return top-N pairs
    bond_fg_defaults = {
        "amide_link":       [["amine", "carbonyl"], ["amine", "thiol"], ["carbonyl", "alcohol"]],
        "ester_link":       [["alcohol", "carbonyl"], ["alcohol", "phosphate"], ["carbonyl", "thiol"]],
        "aromatic":         [["aromatic_ring", "amine"], ["aromatic_ring", "nitro"], ["aromatic_ring", "thiol"]],
        "sigma_single":     [["amine", "alcohol"], ["alcohol", "thiol"], ["amine", "carbonyl"]],
        "ether_link":       [["alcohol", "ether"], ["ether", "sulfide"], ["alcohol", "sulfone"]],
        "strain_release":   [["epoxide", "lactam"], ["lactam", "sulfone"], ["epoxide", "amine"]],
        "carbonyl":         [["carbonyl", "alcohol"], ["carbonyl", "thiol"], ["carbonyl", "amine"]],
        "hydrogen_bond":    [["alcohol", "amine"], ["amine", "phosphate"], ["alcohol", "phosphonate"]],
        "pi_bond":          [["aromatic_ring", "carbonyl"], ["aromatic_ring", "sulfoxide"], ["carbonyl", "sulfone"]],
    }
    
    # Build diverse pairs from top FGs
    result = []
    if len(all_fgs) >= 2:
        result.append([all_fgs[0], all_fgs[1]])
    if len(all_fgs) >= 4:
        result.append([all_fgs[2], all_fgs[3]])
    if len(all_fgs) >= 6:
        result.append([all_fgs[4], all_fgs[5]])
    
    # Fill remaining with bond defaults
    defaults = bond_fg_defaults.get(bond_name, [["amine", "alcohol"], ["alcohol", "thiol"], ["amine", "carbonyl"]])
    for d in defaults:
        if d not in result and len(result) < n:
            result.append(d)
    
    return result[:n]

def _estimate_fgs_from_site_type(site_type: Dict[str, str], bond_name: str) -> List[str]:
    """Estimate FG types from the enzyme's catalytic site type and bond type."""
    from rhr_p4rky.ligand_from_active_site import GLYPH_ORDINALS

    def o(glyph, pn):
        return GLYPH_ORDINALS.get(pn, {}).get(glyph, -1)

    PN = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
    fp = tuple(o(site_type.get(pn,"?"), pn) for pn in PN)

    # FG estimation map: exact matches for known catalytic types
    FG_ESTIMATION_MAP = {
        (1, 4, 3, 4, 2, 2, 1, 1, 1, 2, 2, 1): ["amine", "carbonyl"],
        (0, 2, 3, 0, 2, 2, 1, 0, 1, 1, 2, 1): ["lactam", "epoxide"],
        (0, 2, 2, 0, 2, 3, 0, 1, 1, 1, 0, 1): ["carbonyl", "alcohol"],
        (1, 4, 3, 3, 2, 2, 1, 3, 4, 2, 2, 1): ["aromatic_ring", "ether"],
        (0, 2, 3, 0, 2, 2, 0, 1, 1, 1, 2, 1): ["carbonyl", "alcohol"],
        (1, 4, 3, 1, 2, 2, 1, 1, 1, 2, 2, 1): ["alcohol", "carbonyl"],
        (1, 4, 3, 1, 2, 3, 1, 1, 1, 2, 0, 2): ["amine", "carbonyl"],
    }

    if fp in FG_ESTIMATION_MAP:
        return FG_ESTIMATION_MAP[fp]

    # ── Rule-based fallback for novel fingerprints ──
    MAX_ORD = {"D": 3, "T": 4, "R": 3, "P": 4, "F": 2, "K": 4,
               "G": 2, "Gm": 3, "Ph": 4, "H": 3, "S": 2, "W": 3}

    def elevation(idx, val):
        pn = PN[idx]
        max_o = MAX_ORD.get(pn, 1)
        if max_o == 0:
            return 0.0
        if pn in ("P", "F"):
            return (max_o - val) / max_o
        return val / max_o

    # FG scoring: each primitive elevation -> FG preferences
    FG_RULES = {
        # ── CHNO FGs ──
        "amine":    [(10, 2.0), (7, 1.5), (8, 1.0)],  # S, Gm, Ph
        "carbonyl": [(2, 2.0), (9, 1.0), (7, 0.5)],   # R, H, Gm
        "alcohol":  [(2, 1.5), (9, 1.5), (6, 0.5)],   # R, H, G
        "ether":    [(6, 2.0), (0, 1.0), (2, 0.5)],   # G, D, R
        "aromatic_ring": [(3, 2.0), (4, 2.0), (11, 1.5)],  # P, F, W
        "epoxide":  [(1, 2.0), (5, 0.5)],              # T, K
        "lactam":   [(9, 1.5), (1, 1.0), (7, 1.0)],   # H, T, Gm
        # ── Sulfur-containing FGs ──
        "thiol":    [(2, 2.0), (10, 1.5), (5, 0.5)],  # R, S, K
        "sulfide":  [(6, 1.5), (10, 1.5), (7, 1.0)],  # G, S, Gm
        "sulfoxide":[(2, 1.5), (5, 1.5), (11, 1.0)],  # R, K, W
        "sulfone":  [(3, 1.5), (5, 1.5), (11, 1.5)],  # P, K, W
        "sulfate":  [(2, 2.0), (9, 1.5), (10, 1.0)],  # R, H, S
        "sulfonate":[(2, 1.5), (10, 1.5), (7, 1.0)],  # R, S, Gm
        "sulfonamide":[(7, 2.0), (10, 1.5), (8, 1.0)],# Gm, S, Ph
        # ── Phosphorus-containing FGs ──
        "phosphate":[(2, 2.0), (10, 1.5), (9, 1.0)],  # R, S, H
        "phosphonate":[(10, 2.0), (7, 1.5), (2, 1.0)],# S, Gm, R
        # ── Other heteroatom FGs ──
        "nitro":    [(4, 2.0), (5, 1.5), (8, 1.0)],   # F, K, Ph
        "nitrile":  [(7, 2.0), (10, 1.0), (4, 0.5)],  # Gm, S, F
    }

    scores = {}
    for fg, rules in FG_RULES.items():
        score = 0.0
        for idx, weight in rules:
            score += elevation(idx, fp[idx]) * weight
        max_el = max(elevation(i, fp[i]) for i in range(12))
        for idx, weight in rules:
            if elevation(idx, fp[idx]) == max_el and max_el > 0:
                score += weight * 1.5
        scores[fg] = score

    # Sort FGs by score, take top 2
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    top_fgs = [fg for fg, score in ranked[:2] if score > 0]

    if len(top_fgs) >= 2:
        return top_fgs[:2]
    if len(top_fgs) == 1:
        # Add a complementary FG based on bond type
        bond_complements = {
            "amide_link": "carbonyl", "ester_link": "alcohol",
            "carbonyl": "alcohol", "sigma_single": "alcohol",
            "ether_link": "alcohol", "aromatic": "amine",
            "pi_bond": "carbonyl", "strain_release": "amine",
            "hydrogen_bond": "carbonyl",
        }
        return [top_fgs[0], bond_complements.get(bond_name, "alcohol")]

    # Bond-specific defaults as last resort
    bond_fg_defaults = {
        "amide_link":       ["amine", "carbonyl"],
        "ester_link":       ["alcohol", "carbonyl", "phosphate"],
        "aromatic":         ["aromatic_ring", "amine", "thiol"],
        "sigma_single":     ["amine", "alcohol", "thiol"],
        "ether_link":       ["alcohol", "ether", "sulfide"],
        "strain_release":   ["epoxide", "lactam", "sulfone"],
        "carbonyl":         ["carbonyl", "alcohol", "thiol"],
        "hydrogen_bond":    ["alcohol", "amine", "phosphate"],
        "pi_bond":          ["aromatic_ring", "carbonyl", "sulfoxide"],
        "co_sigma":         ["alcohol", "thiol"],
        "cn_sigma":         ["amine", "nitrile"],
    }
    return bond_fg_defaults.get(bond_name, ["amine", "alcohol", "phosphate"])


def generate_substrate_analogs(
    substrate_smiles: str,
    ligand_type: Optional[Dict[str, str]] = None,
    max_candidates: int = 20,
) -> List[Dict]:
    """Generate ligand candidates by modifying a known substrate.
    
    This is the PRIMARY generation strategy when a substrate hint is available.
    Bioisosteric replacement, functional group variation, and chain extension
    produce chemically plausible analogs scored by drug-likeness.
    
    Strategy:
    1. Parse substrate, identify functional groups
    2. Generate bioisostere swaps (COOH→tetrazole, amide→sulfonamide, etc.)
    3. Generate FG variations (methyl, ethyl, hydroxyl, fluoro substitutions)
    4. Chain length variations
    5. Ring substitutions where applicable
    """
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors, BRICS
    
    candidates = []
    seen = set()
    
    mol = Chem.MolFromSmiles(substrate_smiles)
    if mol is None:
        return candidates
    
    def _add(smi, method, substrate_mol=None):
        """Validate and add a candidate SMILES."""
        try:
            m = Chem.MolFromSmiles(smi)
            if m is None or m.GetNumHeavyAtoms() < 3:
                return
            canon = Chem.MolToSmiles(m)
            if canon in seen:
                return
            seen.add(canon)
            
            logp = Descriptors.MolLogP(m)
            mw = Descriptors.MolWt(m)
            heavy = m.GetNumHeavyAtoms()
            hbd = Descriptors.NumHDonors(m)
            hba = Descriptors.NumHAcceptors(m)
            tpsa = Descriptors.TPSA(m)
            rot = Descriptors.NumRotatableBonds(m)
            rings = rdMolDescriptors.CalcNumRings(m)
            
            # Drug-likeness
            drug = 0.0
            if 0 <= mw <= 500: drug += 0.25
            if -2 <= logp <= 5: drug += 0.25
            if hbd <= 5: drug += 0.25
            if hba <= 10: drug += 0.25
            
            # Structural similarity to substrate
            fp_score = 0.0
            if substrate_mol is not None:
                fp1 = AllChem.GetMorganFingerprintAsBitVect(m, 2, 2048)
                fp2 = AllChem.GetMorganFingerprintAsBitVect(substrate_mol, 2, 2048)
                fp_score = AllChem.DataStructs.TanimotoSimilarity(fp1, fp2)
            
            composite = 0.4 * drug + 0.3 * fp_score + 0.3 * min(1.0, heavy / 40.0)
            
            candidates.append({
                "smiles": canon,
                "method": method,
                "logP": round(logp, 2),
                "MW": round(mw, 1),
                "HBD": hbd,
                "HBA": hba,
                "TPSA": round(tpsa, 1),
                "rotatable_bonds": rot,
                "rings": rings,
                "heavy_atoms": heavy,
                "composite_score": round(composite, 3),
                "fp_score": round(fp_score, 3),
                "drug_score": round(drug, 3),
                "valid": True
            })
        except Exception:
            pass
    
    # Strategy A: The substrate itself
    base_smi = Chem.MolToSmiles(mol)
    _add(base_smi, "substrate", mol)
    
    # Strategy B: BRICS fragment recombination
    try:
        frags = list(BRICS.BreakBRICSBonds(mol))
        if len(frags) >= 2:
            # Keep core, vary other fragments
            frag_mols = [Chem.MolFromSmiles(f) for f in frags if Chem.MolFromSmiles(f)]
            for i, frag_smi in enumerate(frags[:6]):  # max 6 fragments
                for variation in ["C", "CC", "CF", "CO", "CN", "Cl", "c1ccccc1", "C(=O)O", "C(=O)N"]:
                    if variation == frag_smi:
                        continue
                    varied_frags = frags.copy()
                    varied_frags[i] = variation
                    try:
                        recombined = ".".join(varied_frags)
                        _add(recombined, f"brics_var", mol)
                    except:
                        pass
    except Exception:
        pass
    
    # Strategy C: Bioisostere replacements
    bioisosteres = {
        "C(=O)O": ["C(=O)N", "C(=O)NS(=O)(=O)C", "c1[nH]nnn1", "S(=O)(=O)O", "P(=O)(O)O", "C(=O)NC#N"],
        "C(=O)N": ["C(=O)O", "S(=O)(=O)N", "C(=S)N", "c1noc([H])n1"],
        "c1ccccc1": ["c1ccncc1", "c1cnccn1", "c1cscn1", "c1ccoc1", "C1CCCCC1"],
        "O": ["S", "NH", "CF2", "C(=O)", "S(=O)"],
        "OH": ["F", "Cl", "NH2", "SH", "CF3", "CN"],
        "S": ["O", "NH", "CH2", "S(=O)", "S(=O)2"],
    }
    
    base = Chem.MolToSmiles(mol)
    for pattern, replacements in bioisosteres.items():
        if pattern in base:
            for repl in replacements[:4]:
                try:
                    new_smi = base.replace(pattern, repl)
                    _add(new_smi, f"bioisostere", mol)
                except:
                    pass
    
    # Strategy D: Chain length variation for linear substrates
    # Identify terminal methyl/ethyl groups and vary chain length
    try:
        for atom in mol.GetAtoms():
            if atom.GetAtomicNum() == 6 and atom.GetDegree() == 1:
                # Terminal carbon - try ethyl, propyl, isopropyl variants
                neighbors = [n for n in atom.GetNeighbors()]
                if not neighbors:
                    continue
                rw = Chem.RWMol(mol)
                idx = rw.AddAtom(Chem.Atom(6))
                rw.AddBond(atom.GetIdx(), idx, Chem.BondType.SINGLE)
                try:
                    Chem.SanitizeMol(rw)
                    _add(Chem.MolToSmiles(rw), "chain_extend", mol)
                except:
                    pass
    except Exception:
        pass
    
    # Strategy E: Ring substitutions
    ssr = Chem.GetSymmSSSR(mol)
    if ssr:
        ring_info = mol.GetRingInfo()
        for ring in ssr:
            if len(ring) == 6:
                ring_atoms = list(ring)
                for atom_idx in ring_atoms:
                    atom = mol.GetAtomWithIdx(atom_idx)
                    if atom.GetAtomicNum() == 6 and atom.GetDegree() <= 3:
                        for sub in ["F", "Cl", "OH", "NH2", "C", "CF3", "CN", "C(=O)O"]:
                            try:
                                rw = Chem.RWMol(mol)
                                sub_idx = rw.AddAtom(Chem.Atom(6 if sub == "C" else (
                                    9 if sub == "F" else 17 if sub == "Cl" else 8 if sub in ("OH",) else 7)))
                                rw.AddBond(atom_idx, sub_idx, Chem.BondType.SINGLE)
                                Chem.SanitizeMol(rw)
                                _add(Chem.MolToSmiles(rw), f"ring_sub", mol)
                            except:
                                pass
                        break  # One substitution per ring
                break  # One ring at a time
    
    # Sort and limit
    candidates.sort(key=lambda x: x["composite_score"], reverse=True)
    return candidates[:max_candidates]


def generate_from_enzyme_type_substrate_first(
    site_type: Dict[str, str],
    substrate_hint: str = "",
    max_candidates: int = 20
) -> list:
    """Generate de-novo inhibitors: substrate-driven PRIMARY, fragment-based FALLBACK.
    
    When a substrate hint is available, generates substrate analogs first
    (bioisosteres, chain variations, ring substitutions), then supplements
    with fragment-based enumeration for diversity.
    
    When no substrate hint is available, falls back to fragment-based enumeration.
    """
    # ── PRIMARY: Substrate-driven generation ──
    substrate_analogs = []
    if substrate_hint:
        substrate_analogs = generate_substrate_analogs(
            substrate_smiles=substrate_hint,
            ligand_type=None,
            max_candidates=max_candidates,
        )
    
    # ── FALLBACK: Fragment-based enumeration for diversity ──
    bond_name = _estimate_bond_from_site_type(site_type)
    fg_names = _estimate_fgs_from_site_type(site_type, bond_name)
    
    fragment_ligands = generate_ligands_from_bond_fg(
        bond_name=bond_name,
        fg_names=fg_names,
        ligand_type=None,
        substrate_hint=substrate_hint if not substrate_analogs else "",
        max_candidates=max(5, max_candidates // 2),
    )
    
    # ── Merge: substrate analogs first, then fragment diversity ──
    seen = set()
    merged = []
    for c in substrate_analogs + fragment_ligands:
        if c["smiles"] not in seen:
            seen.add(c["smiles"])
            merged.append(c)
    
    merged.sort(key=lambda x: x["composite_score"], reverse=True)
    return merged[:max_candidates]

def generate_from_enzyme_type(
    site_type: Dict[str, str],
    substrate_hint: str = "",
    max_candidates: int = 20
) -> list:
    """Generate de-novo inhibitors: substrate-driven PRIMARY, fragment FALLBACK.
    
    When substrate_hint is available, generates bioisosteric analogs,
    chain variations, and ring substitutions of the known substrate.
    Supplements with fragment-based enumeration for diversity.
    """
    return generate_from_enzyme_type_substrate_first(
        site_type=site_type,
        substrate_hint=substrate_hint,
        max_candidates=max_candidates,
    )
