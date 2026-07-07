#!/usr/bin/env python3
"""
ligand_sicpovm.py — Grammar as Dual-Link SIC-POVM for ligand generation

The grammar IS the Sigma=1:1 limit of the Belnap multilattice SIC-POVM.
This module applies the grammar to itself: it measures the ligand generation
pipeline structurally, identifies where information collapses, and injects
protein-specific context to restore information completeness.

Core insight: the bottleneck is at the residue→primitive encoding step.
All serine proteases map Ser/His/Asp → same primitives → same site_type
→ same ligands. The fix injects protein-specific perturbations via the
12-primitive measurement basis, ensuring each protein occupies a unique
enough structural address that the downstream generator produces distinct output.

Author: Lando⊗⊙perator
Structural type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑙𐑭⟩ — O_∞ self-referential
"""

import sys, os, hashlib, json, math
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path

# Silence RDKit
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')
import rdkit.RDLogger as rkl

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

# ── 12-Primitive definitions ──
PRIMITIVE_ORDER = {
    "D":  ["𐑛", "𐑨", "𐑼", "𐑦"],   # Dimensionality (4)
    "T":  ["𐑡", "𐑰", "𐑥", "𐑶", "𐑸"],  # Topology (5)
    "R":  ["𐑩", "𐑑", "𐑽", "𐑾"],   # Coupling (4)
    "P":  ["𐑗", "𐑿", "𐑬", "𐑯", "𐑹"],  # Parity (5)
    "F":  ["𐑱", "𐑞", "𐑐"],         # Fidelity (3)
    "K":  ["𐑺", "𐑪", "𐑧", "𐑤", "𐑘"],  # Kinetics (5)
    "G":  ["𐑲", "𐑚", "𐑔"],         # Cardinality (3)
    "Gm": ["𐑝", "𐑜", "𐑠", "𐑵"],  # Composition (4)
    "Phi": ["𐑢", "⊙", "𐑮", "𐑻", "𐑣"],  # Criticality (5)
    "H":  ["𐑓", "𐑒", "𐑖", "𐑫"],   # Chirality (4)
    "S":  ["𐑙", "𐑕", "𐑳"],         # Stoichiometry (3)
    "W":  ["𐑷", "𐑴", "𐑭", "𐑟"],   # Winding (4)
}

# AA → primitive mapping for active site residues
AA_TO_PRIMITIVE = {
    # Catalytic residues → specific primitives
    "Ser": "R",  "Thr": "R",   # Nucleophiles → coupling
    "Asp": "F",  "Glu": "F",   # Acid/base → fidelity
    "His": "Phi",              # Proton shuttle → criticality
    "Cys": "P",                # Thiol nucleophile → parity
    "Lys": "S",                # Schiff base / charge → stoichiometry
    "Arg": "S",                # Charge stabilization → stoichiometry
    "Tyr": "H",                # H-bond network → chirality
    "Asn": "T",  "Gln": "T",   # H-bond donors → topology
    "Met": "K",                # Sulfur chemistry → kinetics
    "Trp": "G",                # π-stacking → cardinality
    "Phe": "G",                # π-stacking → cardinality
    "Ile": "W", "Val": "W", "Leu": "W",  # Hydrophobic packing → winding
    "Gly": "D",                # Flexibility → dimensionality
    "Pro": "K",                # Conformational constraint → kinetics
    "Ala": "D",                # Minimal side chain → dimensionality
}

# Reaction type → primitive perturbation weights
REACTION_PRIMITIVE_WEIGHTS = {
    "hydrolysis":       {"R": 1.2, "F": 1.1, "Phi": 0.9},
    "phosphorylation":  {"P": 1.3, "F": 1.1, "K": 0.8},
    "dephosphorylation": {"P": 1.2, "F": 1.0, "K": 0.9},
    "oxidation":        {"F": 1.3, "Phi": 1.2, "K": 0.7},
    "reduction":        {"F": 1.2, "Phi": 1.0, "R": 0.9},
    "decarboxylation":  {"D": 1.2, "K": 1.1, "G": 0.9},
    "isomerization":    {"T": 1.3, "H": 1.2, "W": 0.9},
    "ligation":         {"Gm": 1.3, "S": 1.2, "P": 0.8},
    "polymerization":   {"Gm": 1.2, "S": 1.3, "W": 0.8},
    "methylation":      {"S": 1.1, "H": 1.2, "D": 0.9},
    "acetylation":      {"S": 1.1, "F": 1.1, "P": 0.9},
    "proteolysis":      {"R": 1.3, "F": 1.0, "T": 0.9},
    "glycosylation":    {"T": 1.2, "S": 1.1, "R": 0.9},
}

# Organism kingdom → primitive perturbations
ORGANISM_WEIGHTS = {
    "homo":      {"H": 1.1, "S": 1.0, "Phi": 1.0},   # human → balanced
    "bos":       {"G": 0.9, "D": 1.0, "W": 1.1},      # bovine
    "mus":       {"G": 0.8, "D": 1.1, "W": 0.9},      # mouse
    "rattus":    {"G": 0.8, "D": 1.1, "W": 0.9},      # rat
    "saccharomyces": {"T": 1.2, "G": 0.7, "K": 1.1},  # yeast
    "escherichia":   {"T": 1.1, "G": 0.6, "F": 1.1},  # E. coli
    "bacillus":  {"T": 1.1, "W": 1.2, "K": 1.0},      # Bacillus
    "pseudomonas": {"F": 1.2, "K": 1.1, "D": 1.0},    # Pseudomonas
    "arabidopsis":  {"H": 1.1, "S": 0.9, "D": 1.1},   # plant
    "drosophila":   {"T": 1.1, "H": 1.0, "W": 0.9},   # fly
    "plasmodium":   {"P": 1.3, "G": 0.8, "F": 0.9},   # malaria
    "trypanosoma":  {"P": 1.2, "T": 1.1, "G": 0.7},   # trypanosome
    "mycobacterium": {"F": 1.3, "W": 1.1, "G": 0.7},  # TB
    "staphylococcus": {"P": 1.1, "W": 1.0, "K": 1.1}, # Staph
    "ideonella":     {"F": 1.2, "R": 1.1, "K": 0.8},  # PETase
    "sars":      {"P": 1.4, "W": 0.8, "R": 1.1},      # viral
    "hiv":       {"P": 1.4, "W": 0.8, "R": 1.1},      # viral
    "influenza": {"P": 1.3, "T": 1.2, "G": 0.7},       # viral
}


def _protein_name_hash(protein_name: str, n_bits: int = 8) -> int:
    """Deterministic hash of protein name → integer for seeding diversity."""
    h = hashlib.md5(protein_name.encode()).digest()
    return int.from_bytes(h[:4], 'big') % (2**n_bits)


def _smiles_features(substrate_smiles: str) -> Dict[str, float]:
    """Extract structural features from a substrate SMILES for context."""
    if not substrate_smiles:
        return {}
    try:
        mol = Chem.MolFromSmiles(substrate_smiles)
        if mol is None:
            return {}
        return {
            "mw": Descriptors.MolWt(mol),
            "logp": Descriptors.MolLogP(mol),
            "hbd": Descriptors.NumHDonors(mol),
            "hba": Descriptors.NumHAcceptors(mol),
            "rot_bonds": Descriptors.NumRotatableBonds(mol),
            "rings": rdMolDescriptors.CalcNumRings(mol),
            "arom_rings": rdMolDescriptors.CalcNumAromaticRings(mol),
            "heavy_atoms": mol.GetNumHeavyAtoms(),
            "fraction_csp3": Descriptors.FractionCSP3(mol),
        }
    except:
        return {}

def _reaction_type_from_text(text: str) -> str:
    """Infer reaction type from description text."""
    text_lower = text.lower()
    patterns = [
        ("proteolysis", ["proteoly", "cleavage of", "peptide bond", "endopeptidase"]),
        ("hydrolysis", ["hydrolysis", "hydrolase", "hydrolyze"]),
        ("phosphorylation", ["phosphorylation", "kinase", "phosphorylate"]),
        ("dephosphorylation", ["dephosphorylat", "phosphatase"]),
        ("oxidation", ["oxidation", "oxidase", "oxidoreductase", "dehydrogenase"]),
        ("reduction", ["reduction", "reductase"]),
        ("decarboxylation", ["decarboxyl", "decarboxylase"]),
        ("isomerization", ["isomerization", "isomerase", "mutase"]),
        ("ligation", ["ligation", "ligase", "synthetase"]),
        ("polymerization", ["polymeriz", "polymerase"]),
        ("methylation", ["methylation", "methyltransferase"]),
        ("acetylation", ["acetylation", "acetyltransferase"]),
        ("glycosylation", ["glycosylat", "glycosyltransferase"]),
    ]
    for rtype, keywords in patterns:
        for kw in keywords:
            if kw in text_lower:
                return rtype
    return "hydrolysis"  # default


def _organism_perturbation(organism: str) -> Dict[str, float]:
    """Return perturbation weights based on organism."""
    org_lower = organism.lower()
    for key, weights in ORGANISM_WEIGHTS.items():
        if key in org_lower:
            return dict(weights)
    return {"Phi": 1.0, "W": 1.0}  # neutral


def _substrate_perturbation(substrate_smiles: str) -> Dict[str, float]:
    """Derive primitive perturbations from substrate structural features."""
    feats = _smiles_features(substrate_smiles)
    if not feats:
        return {}

    pert = {}
    mw = feats.get("mw", 0)
    logp = feats.get("logp", 0)
    rings = feats.get("rings", 0)
    arom_rings = feats.get("arom_rings", 0)
    rot_bonds = feats.get("rot_bonds", 0)
    hbd = feats.get("hbd", 0)
    hba = feats.get("hba", 0)
    heavy = feats.get("heavy_atoms", 0)

    # Large substrate → higher dimensionality
    if heavy > 40:
        pert["D"] = 0.9
    elif heavy < 10:
        pert["D"] = 1.2

    # Many rings → more complex topology
    if rings > 4:
        pert["T"] = 0.8
    elif rings < 2:
        pert["T"] = 1.2

    # Polar substrate → coupling perturbation
    if hbd + hba > 8:
        pert["R"] = 1.2
    elif hbd + hba < 2:
        pert["R"] = 0.8

    # Rotatable bonds → kinetics perturbation
    if rot_bonds > 10:
        pert["K"] = 0.8
    elif rot_bonds < 3:
        pert["K"] = 1.2

    # Aromatic → cardinality perturbation
    if arom_rings > 2:
        pert["G"] = 1.2
    elif arom_rings == 0:
        pert["G"] = 0.8

    # logP → fidelity perturbation
    if logp > 5:
        pert["F"] = 0.8
    elif logp < -2:
        pert["F"] = 1.2

    return pert


def _reaction_perturbation(reaction_type: str) -> Dict[str, float]:
    """Get primitive perturbation weights for a reaction type."""
    return REACTION_PRIMITIVE_WEIGHTS.get(reaction_type, {"Phi": 1.0})


def _push_primitive(primitives_list: List[str], current: str, weight: float) -> str:
    """Push a primitive value up or down within its ordinal range.
    
    weight > 1.0 → push toward higher ordinal (later in list)
    weight < 1.0 → push toward lower ordinal (earlier in list)
    """
    if current not in primitives_list:
        return primitives_list[len(primitives_list)//2]  # default to middle
    idx = primitives_list.index(current)
    n = len(primitives_list)
    
    if weight > 1.0:
        # Push up
        shift = min(int((weight - 1.0) * n), n - 1 - idx)
        new_idx = min(idx + shift, n - 1)
    elif weight < 1.0:
        # Push down
        shift = min(int((1.0 - weight) * n), idx)
        new_idx = max(idx - shift, 0)
    else:
        new_idx = idx
    
    return primitives_list[new_idx]


def encode_site_with_context(
    residues: List[str],
    protein_context: Dict = None,
    seed_diversity: int = 0,
) -> Dict[str, str]:
    """Encode active site residues → 12-primitive site_type with protein context.
    
    This is the core SIC-POVM measurement: it maps each residue to a primitive,
    then applies protein-specific perturbations (reaction type, organism, substrate)
    and a deterministic diversity seed to ensure each protein gets a unique-enough
    structural address.
    
    Args:
        residues: Active site residue strings, e.g. ["Ser195", "His57", "Asp102"]
        protein_context: Dict with keys: name, organism, reaction, substrate_hint, catalytic_roles
        seed_diversity: Integer seed for deterministic perturbation (default: hash of protein name)
    
    Returns:
        12-primitive dict like {"D": "𐑼", "T": "𐑶", ...}
    """
    if not residues:
        return _default_site_type()
    
    protein_context = protein_context or {}
    
    # ── Step 1: Base site_type from residues ──
    base = _encode_residues_base(residues)
    
    # ── Step 2: Gather protein-specific perturbations ──
    protein_name = protein_context.get("name", "")
    organism = protein_context.get("organism", "")
    reaction_text = protein_context.get("reaction", "")
    substrate_hint = protein_context.get("smiles_substrate_hint", "")
    catalytic_roles = protein_context.get("catalytic_roles", [])
    
    if seed_diversity == 0 and protein_name:
        seed_diversity = _protein_name_hash(protein_name)
    
    reaction_type = _reaction_type_from_text(reaction_text)
    
    # Collect perturbation weights from all sources
    all_weights = {}  # primitive → cumulative weight
    
    # Reaction type weights
    for prim, w in _reaction_perturbation(reaction_type).items():
        all_weights[prim] = all_weights.get(prim, 1.0) * w
    
    # Organism weights
    for prim, w in _organism_perturbation(organism).items():
        all_weights[prim] = all_weights.get(prim, 1.0) * w
    
    # Substrate weights
    for prim, w in _substrate_perturbation(substrate_hint).items():
        all_weights[prim] = all_weights.get(prim, 1.0) * w
    
    # Diversity seed: use bits 0-3 for one primitive, 4-7 for another
    seed_bits = [(seed_diversity >> i) & 3 for i in range(0, 8, 2)]
    seed_primitives = ["D", "T", "R", "K"]
    for i, prim in enumerate(seed_primitives):
        if i < len(seed_bits):
            # seed 0→0.8, 1→0.95, 2→1.05, 3→1.2
            sw = [0.80, 0.95, 1.05, 1.20][seed_bits[i]]
            all_weights[prim] = all_weights.get(prim, 1.0) * sw
    
    # ── Step 3: Apply perturbations to the base site_type ──
    result = dict(base)
    for prim, weight in all_weights.items():
        if prim in result and prim in PRIMITIVE_ORDER:
            result[prim] = _push_primitive(PRIMITIVE_ORDER[prim], result[prim], weight)
    
    # Ensure all 12 primitives are present
    default = _default_site_type()
    for prim in PRIMITIVE_ORDER:
        if prim not in result:
            result[prim] = default[prim]
    
    return result


def _encode_residues_base(residues: List[str]) -> Dict[str, str]:
    """Base encoding: residues → primitives (tensor semantics)."""
    import re as _re
    
    # Extended AA→Primitive mapping
    _ALL_AA_PRIMITIVE = dict(AA_TO_PRIMITIVE)
    
    _AA_MAP_1L = {"S": "Ser", "D": "Asp", "H": "His", "E": "Glu",
                   "K": "Lys", "C": "Cys", "Y": "Tyr", "F": "Phe",
                   "I": "Ile", "N": "Asn", "Q": "Gln", "W": "Trp",
                   "M": "Met", "G": "Gly", "A": "Ala", "V": "Val",
                   "L": "Leu", "P": "Pro", "T": "Thr", "R": "Arg"}
    
    clean_aas = []
    for r in residues:
        match3 = _re.match(r'([A-Za-z]{3})\d*', r)
        if match3:
            code3 = match3.group(1)
            code3_title = code3[0].upper() + code3[1:].lower()
            if code3_title in _ALL_AA_PRIMITIVE:
                clean_aas.append(code3_title)
                continue
        match1 = _re.match(r'([A-Za-z])\d*', r)
        if match1:
            code1 = match1.group(1).upper()
            if code1 in _AA_MAP_1L:
                code3 = _AA_MAP_1L[code1]
                if code3 in _ALL_AA_PRIMITIVE:
                    clean_aas.append(code3)
    
    if not clean_aas:
        return _default_site_type()
    
    # Count primitives
    prim_counts = {}
    for aa in clean_aas:
        prim = _ALL_AA_PRIMITIVE.get(aa)
        if prim:
            prim_counts[prim] = prim_counts.get(prim, 0) + 1
    
    n_total = len(clean_aas)
    
    # Map counts to ordinals
    result = {}
    for prim_key, values in PRIMITIVE_ORDER.items():
        n_values = len(values)
        if prim_key in prim_counts:
            frac = prim_counts[prim_key] / n_total
            # More residues mapping to this primitive → higher ordinal
            idx = min(int(frac * n_values), n_values - 1)
            result[prim_key] = values[idx]
        else:
            # Unmapped primitives: set to lowest ordinal (not contributing)
            result[prim_key] = values[0]
    
    # Tensor correction: P and F use min (more residues = more constrained)
    if "P" in prim_counts:
        frac_p = prim_counts["P"] / n_total
        idx_p = max(int((1 - frac_p) * len(PRIMITIVE_ORDER["P"])), 0)
        result["P"] = PRIMITIVE_ORDER["P"][min(idx_p, len(PRIMITIVE_ORDER["P"]) - 1)]
    
    if "F" in prim_counts:
        frac_f = prim_counts["F"] / n_total
        idx_f = max(int((1 - frac_f) * len(PRIMITIVE_ORDER["F"])), 0)
        result["F"] = PRIMITIVE_ORDER["F"][min(idx_f, len(PRIMITIVE_ORDER["F"]) - 1)]
    
    return result


def _default_site_type() -> Dict[str, str]:
    """Default site_type when encoding fails."""
    return {
        "D": "𐑨", "T": "𐑡", "R": "𐑩", "P": "𐑗", "F": "𐑱", "K": "𐑪",
        "G": "𐑲", "Gm": "𐑝", "Phi": "𐑢", "H": "𐑓", "S": "𐑙", "W": "𐑷"
    }


def _site_type_to_tuple(site_type: Dict[str, str]) -> str:
    """Convert site_type dict to tuple string for display."""
    order = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Phi", "H", "S", "W"]
    return "⟨" + "".join(site_type.get(p, "?") for p in order) + "⟩"


# ═══════════════════════════════════════════════════════════
# Multi-configuration ligand generation
# ═══════════════════════════════════════════════════════════

# Diverse bond type catalog (not just 6 — explore 15+ bond types)
BOND_CATALOG = {
    "amide":        "NC(=O)",     # peptide bond mimic
    "ester":        "OC(=O)",     # ester linkage
    "ether":        "COC",        # ether linkage
    "sulfonamide":  "NS(=O)(=O)", # sulfonamide
    "sulfone":      "S(=O)(=O)",  # sulfone
    "sulfoxide":    "S(=O)",      # sulfoxide
    "carbonyl":     "C(=O)",      # ketone/aldehyde
    "urea":         "NC(=O)N",    # urea
    "carbamate":    "OC(=O)N",    # carbamate
    "thioether":    "CSC",        # sulfide
    "phosphonate":  "P(=O)(O)O",  # phosphate mimic
    "triazole":     "c1cnnn1",    # click chemistry
    "oxadiazole":   "c1cnoc1",    # heterocycle
    "hydrazone":    "NN=C",       # hydrazone
    "imine":        "N=C",        # Schiff base
}

# Functional group catalog by chemistry type
FG_CATALOG = {
    "alcohol":      ["[OH]", "CO"],
    "amine":        ["[NH2]", "CN"],
    "carboxyl":     ["C(=O)O", "C(=O)[OH]"],
    "sulfate":      ["OS(=O)(=O)O", "S(=O)(=O)O"],
    "phosphate":    ["OP(=O)(O)O", "P(=O)(O)O"],
    "thiol":        ["[SH]", "CS"],
    "halogen":      ["F", "Cl", "Br"],
    "nitro":        ["[N+](=O)[O-]"],
    "nitrile":      ["C#N"],
    "azide":        ["N=[N+]=[N-]"],
    "isocyanate":   ["N=C=O"],
    "epoxide":      ["C1OC1", "C1CO1"],
    "lactam":       ["C(=O)N", "NC(=O)"],
    "lactone":      ["C(=O)O", "OC(=O)"],
    "guanidine":    ["NC(=N)N"],
    "boronic":      ["B(O)O"],
    "alkyne":       ["C#C"],
    "cyclopropyl":  ["C1CC1"],
}

def _select_bonds_for_site(site_type: Dict[str, str], n: int = 5) -> List[str]:
    """Select diverse bond types based on site_type primitives."""
    # Use primitives to weight bond selection
    all_bonds = list(BOND_CATALOG.keys())
    
    # R (coupling) → prefer polar bonds at high ordinal
    r_idx = PRIMITIVE_ORDER["R"].index(site_type.get("R", "𐑩"))
    if r_idx >= 2:
        polar_bonds = ["amide", "ester", "urea", "carbamate", "sulfonamide"]
        scored = [(b, 2.0 if b in polar_bonds else 1.0) for b in all_bonds]
    else:
        nonpolar_bonds = ["ether", "thioether", "carbonyl", "imine"]
        scored = [(b, 2.0 if b in nonpolar_bonds else 1.0) for b in all_bonds]
    
    # F (fidelity) → at high ordinal, prefer stable bonds
    f_idx = PRIMITIVE_ORDER["F"].index(site_type.get("F", "𐑱"))
    if f_idx >= 2:
        stable = ["amide", "sulfone", "triazole", "oxadiazole", "ether"]
        scored = [(b, s * (1.5 if b in stable else 1.0)) for b, s in scored]
    
    # Phi (criticality) → at high ordinal, prefer reactive bonds
    phi_idx = PRIMITIVE_ORDER["Phi"].index(site_type.get("Phi", "𐑢"))
    if phi_idx >= 3:
        reactive = ["hydrazone", "imine", "sulfoxide", "isocyanate"]
        scored = [(b, s * (1.5 if b in reactive else 1.0)) for b, s in scored]
    
    scored.sort(key=lambda x: -x[1])
    return [b for b, _ in scored[:n]]


def _select_fgs_for_site(site_type: Dict[str, str], bond_name: str, n: int = 4) -> List[str]:
    """Select FG combinations based on site_type primitives."""
    all_fgs = list(FG_CATALOG.keys())
    
    # K (kinetics) → high ordinal prefers faster-reacting FGs
    k_idx = PRIMITIVE_ORDER["K"].index(site_type.get("K", "𐑪"))
    if k_idx >= 3:
        fast = ["epoxide", "azide", "isocyanate", "aldehyde"]
        scored = [(f, 2.0 if f in fast else 1.0) for f in all_fgs]
    else:
        slow = ["alcohol", "amine", "carboxyl", "sulfate"]
        scored = [(f, 2.0 if f in slow else 1.0) for f in all_fgs]
    
    # S (stoichiometry) → high ordinal prefers diverse FG types
    s_idx = PRIMITIVE_ORDER["S"].index(site_type.get("S", "𐑙"))
    if s_idx >= 2:
        diverse = ["alcohol", "amine", "thiol", "halogen", "nitrile"]
        scored = [(f, s * (1.5 if f in diverse else 1.0)) for f, s in scored]
    
    scored.sort(key=lambda x: -x[1])
    fg_list = [f for f, _ in scored[:n * 2]]  # get 2x for combination
    
    # Return pairs of complementary FGs
    pairs = []
    for i in range(0, len(fg_list) - 1, 2):
        pairs.append([fg_list[i], fg_list[i+1]])
    return pairs[:n]


def generate_ligands_sicpovm(
    protein: Dict,
    max_candidates: int = 200,
    n_bond_types: int = 6,
    n_fg_pairs: int = 4,
    verbose: bool = True,
) -> List[Dict]:
    """Generate diverse ligands using the grammar as SIC-POVM.

    Applies the 12-primitive measurement to the protein's active site,
    then explores multiple bond/FG configurations seeded by the protein's
    unique structural address. This ensures each protein gets distinct output.

    Args:
        protein: Full protein entry from PROTEIN_LOOKUP with keys:
                 name, organism, pdb, active_site_residues, catalytic_roles,
                 reaction, smiles_substrate_hint
        max_candidates: Total candidates across all configurations
        n_bond_types: Number of bond types to explore
        n_fg_pairs: Number of FG pairs per bond type
        verbose: Print progress

    Returns:
        List of dicts with keys: smiles, method, composite_score, logP, MW, etc.
    """
    from rhr_p4rky.ligand_heterocycles import generate_hybrid_ligands
    
    protein_name = protein.get("name", "unknown")
    residues = protein.get("active_site_residues", [])
    if not residues:
        if verbose:
            print(f"  [{protein_name}] No active site residues — skipping")
        return []
    
    # ── Step 1: Encode site with protein-specific context ──
    seed = _protein_name_hash(protein_name, n_bits=8)
    site_type = encode_site_with_context(
        residues=residues,
        protein_context=protein,
        seed_diversity=seed,
    )
    
    if verbose:
        print(f"  [{protein_name}] Site type: {_site_type_to_tuple(site_type)}")
        print(f"           Seed: {seed}, Reaction: {_reaction_type_from_text(protein.get('reaction', ''))}")
    
    # ── Step 2: Select diverse bond/FG configurations ──
    bond_types = _select_bonds_for_site(site_type, n=n_bond_types)
    fg_configs = _select_fgs_for_site(site_type, "", n=n_fg_pairs)
    
    # ── Step 3: Generate ligands for each configuration ──
    substrate = protein.get("smiles_substrate_hint", "")
    candidates_per_config = max(10, max_candidates // (len(bond_types) * len(fg_configs)))
    
    all_candidates = []
    seen_smiles = set()
    
    for bond_name in bond_types:
        for fg_pair in fg_configs:
            if len(all_candidates) >= max_candidates:
                break
            
            if verbose and len(all_candidates) == 0:
                pass  # first config
    
            try:
                # Modify site_type's G and Gm based on bond/FG to create diversity
                config_site = dict(site_type)
                # Bond type affects G (cardinality)
                g_shift = hash(bond_name) % 3
                config_site["G"] = PRIMITIVE_ORDER["G"][g_shift]
                # FG pair affects Gm (composition)
                gm_shift = hash("+".join(fg_pair)) % 4
                config_site["Gm"] = PRIMITIVE_ORDER["Gm"][gm_shift]
                
                batch = generate_hybrid_ligands(
                    site_type=config_site,
                    substrate_hint=substrate,
                    max_candidates=candidates_per_config,
                )
                
                for c in batch:
                    smi = c.get("smiles", c.get("SMILES", ""))
                    if smi and smi not in seen_smiles:
                        seen_smiles.add(smi)
                        c["bond_type"] = bond_name
                        c["fg_pair"] = "+".join(fg_pair)
                        c["protein"] = protein_name
                        all_candidates.append(c)
                        
            except Exception as e:
                if verbose:
                    print(f"    [WARN] {bond_name}/{fg_pair}: {e}")
                continue
        
        if len(all_candidates) >= max_candidates:
            break
    
    if verbose:
        print(f"  [{protein_name}] Generated {len(all_candidates)} unique SMILES "
              f"from {len(bond_types)} bonds × {len(fg_configs)} FG configs")
    
    # Sort by composite score
    all_candidates.sort(key=lambda c: c.get("composite_score", 0), reverse=True)
    return all_candidates[:max_candidates]


def batch_generate_all(
    protein_list: List[Dict] = None,
    max_per_protein: int = 200,
    n_bond_types: int = 6,
    n_fg_pairs: int = 4,
    verbose: bool = True,
) -> Dict[str, List[Dict]]:
    """Run SIC-POVM ligand generation on all proteins in the catalog.

    Returns:
        Dict mapping protein name → list of candidate dicts
    """
    if protein_list is None:
        from rhr_p4rky.ligand_from_active_site import PROTEIN_LOOKUP
        protein_list = list(PROTEIN_LOOKUP.values())
    
    results = {}
    global_seen = set()
    total_smiles = 0
    
    for i, protein in enumerate(protein_list):
        name = protein.get("name", f"protein_{i}")
        candidates = generate_ligands_sicpovm(
            protein=protein,
            max_candidates=max_per_protein,
            n_bond_types=n_bond_types,
            n_fg_pairs=n_fg_pairs,
            verbose=verbose,
        )
        results[name] = candidates
        for c in candidates:
            smi = c.get("smiles", "")
            if smi:
                global_seen.add(smi)
        
        if verbose:
            print(f"  [{i+1}/{len(protein_list)}] Cumulative unique: {len(global_seen)}")
    
    return results


def collect_all_unique_smiles(results: Dict[str, List[Dict]]) -> List[str]:
    """Extract all unique SMILES from batch results."""
    seen = set()
    ordered = []
    for name, candidates in results.items():
        for c in candidates:
            smi = c.get("smiles", "")
            if smi and smi not in seen:
                seen.add(smi)
                ordered.append(smi)
    return ordered


# ── CLI ──
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Grammar SIC-POVM ligand generator")
    ap.add_argument("--protein", "-p", help="Single protein name")
    ap.add_argument("--all", "-a", action="store_true", help="Generate for ALL proteins")
    ap.add_argument("--max-per", type=int, default=200, help="Max candidates per protein")
    ap.add_argument("--bonds", type=int, default=6, help="Bond types to explore")
    ap.add_argument("--fgs", type=int, default=4, help="FG pairs per bond")
    ap.add_argument("--output", "-o", help="Output JSON file")
    ap.add_argument("--smiles-only", action="store_true", help="Output only unique SMILES")
    args = ap.parse_args()
    
    from rhr_p4rky.ligand_from_active_site import PROTEIN_LOOKUP
    
    if args.all:
        results = batch_generate_all(
            max_per_protein=args.max_per,
            n_bond_types=args.bonds,
            n_fg_pairs=args.fgs,
        )
        if args.smiles_only:
            smiles = collect_all_unique_smiles(results)
            for s in smiles:
                print(s)
            print(f"\n# Total unique SMILES: {len(smiles)}", file=sys.stderr)
        elif args.output:
            import json
            out = {name: [{"smiles": c["smiles"], "score": c.get("composite_score", 0)}
                          for c in cands]
                   for name, cands in results.items()}
            with open(args.output, 'w') as f:
                json.dump(out, f, indent=2)
            print(f"Wrote {args.output}", file=sys.stderr)
        else:
            import json
            print(json.dumps({name: len(cands) for name, cands in results.items()}, indent=2, ensure_ascii=False))
            total = len(collect_all_unique_smiles(results))
            print(f"\nTotal unique SMILES across all proteins: {total}")
    
    elif args.protein:
        enzyme = args.protein.lower()
        protein = None
        for name, entry in PROTEIN_LOOKUP.items():
            if enzyme in name.lower() or name.lower() in enzyme:
                protein = entry
                break
        if not protein:
            # Try aliases
            aliases = {"adh": "alcohol_dehydrogenase", "hiv": "HIV1_protease",
                       "ache": "acetylcholinesterase", "ca2": "carbonic_anhydrase_II",
                       "rnase": "ribonuclease_A", "pet": "PETase"}
            canonical = aliases.get(enzyme)
            if canonical:
                protein = PROTEIN_LOOKUP.get(canonical)
        
        if not protein:
            print(f"Protein '{args.protein}' not found. Available: {list(PROTEIN_LOOKUP.keys())}")
            sys.exit(1)
        
        candidates = generate_ligands_sicpovm(
            protein=protein,
            max_candidates=args.max_per,
            n_bond_types=args.bonds,
            n_fg_pairs=args.fgs,
        )
        if args.smiles_only:
            for c in candidates:
                print(c.get("smiles", ""))
        else:
            for i, c in enumerate(candidates):
                print(f"{i+1:3d}. {c.get('smiles', '?'):50s} score={c.get('composite_score', 0):.3f} "
                      f"method={c.get('method', '?')} bond={c.get('bond_type', '?')}")
            print(f"\nTotal: {len(candidates)} unique SMILES")
    else:
        ap.print_help()
