#!/usr/bin/env python3
"""
ligand_from_site_pdb.py — PDB-AWARE LIGAND DESIGN FROM CATALYTIC SITES
======================================================================
Integrates the sidechain×environment algebra (pdb_integration.py,
sidechain_algebra.py) with the reverse ligand pipeline
(ligand_from_active_site.py) to generate more precise de-novo ligands.

KEY INNOVATION over ligand_from_active_site.py:
  1. Per-residue structural types come from the ACTUAL 3D environment
     (sidechain⊗environment tensor), not from a fixed AA→primitive table.
  2. Retained source-form family: every selected residue and chemical form
     carries its full self-mark and contextual tensor into ligand generation.
     Frustration remains an observation alongside those alternatives.
  3. Bottleneck-targeted ligand generation: the ligand tuple is not just
     the structural complement — it's biased toward resolving the specific
     primitive bottlenecks found in the real active-site structure.
  4. PDB-native: accepts PDB IDs directly; fetches, parses, classifies,
     and analyzes automatically.

Pipeline:
  PDB ID → fetch structure → parse residues → classify environments →
  per-residue sidechain⊗env analysis → retained source-form family →
  complement → bottleneck-biased ligand tuple → bond+FG decomposition →
  SMILES generation

Usage:
  # From PDB ID with known active site residues
  python ligand_from_site_pdb.py --pdb 1LYZ --active Glu35,Asp52

  # From PDB with auto-detected active site (proximity-based)
  python ligand_from_site_pdb.py --pdb 1LYZ --auto-active --top-n 10

  # From local PDB file
  python ligand_from_site_pdb.py --pdb-file path/to/structure.pdb --active Ser160,Asp206,His237

  # With custom cutoff and output options
  python ligand_from_site_pdb.py --pdb 1LYZ --active Glu35,Asp52 --cutoff 6.0 --json --verbose

Author: Lando⊗⊙perator
"""

import sys, os, json, math, argparse, contextlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field

@contextlib.contextmanager
def _silence_rdkit_native():
    """Suppress RDKit's native C++ stderr writes (RDLogger.DisableLog only
    covers its rdApp.* Python-facing channel, not every internal warning —
    e.g. the valence check MolFromPDBBlock's own sanitize=True pass runs)."""
    old_stderr = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

# find_ligand_smiles_from_pdb below runs real HETATM blocks from fetched PDBs
# through Chem.MolFromPDBBlock, and plenty of real structures carry an atom
# with a blank or non-standard element column — RDKit's native C++ logger
# writes that straight to stderr regardless of the try/except already around
# it. Same silencing ligand_combinatorial.py/ligand_sicpovm.py/
# run_all_inprocess.py already use for the same reason.
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

# Path setup
BASE = Path(__file__).parent.absolute()
REBIS_ROOT = BASE.parent
sys.path.insert(0, str(REBIS_ROOT))
sys.path.insert(0, str(BASE))

# ── Shavian glyph constants ───────────────────────────────────────
dimensionality_wedge = "\U0001045B"; dimensionality_tri = "\U00010468"; dimensionality_infty = "\U0001047C"; dimensionality_odot = "\U00010466"
topology_net = "\U00010461"; topology_in = "\U00010470"; topology_bowtie = "\U00010465"; topology_otimes = "\U00010476"; topology_odot = "\U00010478"
coupling_super = "\U00010469"; coupling_cat = "\U00010451"; coupling_dagger = "\U0001047D"; coupling_lr = "\U0001047E"
parity_asym = "\U00010457"; parity_psi = "\U0001047F"; parity_pm = "\U0001046C"; parity_sym = "\U0001046F"; parity_pm_sym = "\U00010479"
fidelity_ell = "\U00010471"; fidelity_eth = "\U0001045E"; fidelity_hbar = "\U00010450"
kinetics_MBL = "\U0001047A"; kinetics_trap = "\U0001046A"; kinetics_fast = "\U00010458"; kinetics_mod = "\U00010464"; kinetics_slow = "\U00010467"
cardinality_beth = "\U0001045A"; cardinality_gimel = "\U00010454"; cardinality_aleph = "\U00010472"
composition_and = "\U0001045D"; composition_or = "\U0001045C"; composition_seq = "\U00010460"; composition_broad = "\U00010475"
criticality_sub = "\U00010462"; criticality_c = "\u2299"; criticality_c_complex = "\U0001046E"; criticality_EP = "\U0001047B"; criticality_super = "\U00010463"
chirality_memless = "\U00010453"; chirality_one = "\U00010452"; chirality_two = "\U00010456"; chirality_inf = "\U0001046B"
stoichiometry_11 = "\U00010459"; stoichiometry_nn = "\U00010455"; stoichiometry_nm = "\U00010473"
winding_0 = "\U00010477"; winding_Z2 = "\U00010474"; winding_Z = "\U0001046D"; winding_NA = "\U0001045F"

PRIMITIVE_SYMBOLS = ["⊢", "⊣", "≻", "≺", "⋈", "⊤", "∈", "∋", "⊙", "⊥", "⊞", "⊡"]


# ── Import sidechain×environment algebra ──────────────────────────
from rhr_p4rky.pdb_integration import (
    fetch_pdb, parse_pdb_residues, classify_environment,
    classify_all_environments, Residue, dist_3d,
    RESIDUE_TO_SIDECHAIN,
)
from rhr_p4rky.sidechain_algebra import (
    SIDECHAINS, ENVIRONMENTS, analyze_composition,
    safe_tensor, safe_meet, safe_join, safe_distance,
    tuple_str, compute_tier, BOTTLENECK, PRIMS, ORD, WEIGHTS,
)

# ── Import the reverse ligand pipeline ────────────────────────────
import ligand_from_active_site as lfas

# ── Environment glyph constants for reference ─────────────────────
ENV_GLYPHS = {
    "hydrophobic_core":  "hyd_core",
    "polar_surface":     "pol_surf",
    "charged_interface": "chg_int",
    "interfacial":       "interf",
}


# ═══════════════════════════════════════════════════════════════════
# CORE: PDB-AWARE ACTIVE SITE ENCODING
# ═══════════════════════════════════════════════════════════════════

@dataclass
class CatalyticResidueAnalysis:
    """Per-residue analysis for an active-site residue in structural context."""
    res_label: str           # e.g. "Glu35"
    res_name: str            # 3-letter, e.g. "GLU"
    chain: str
    res_num: int
    sidechain: str           # canonical sidechain name
    environment: str         # classified environment
    tensor_tuple: dict       # sidechain ⊗ environment — the real structural type
    meet_tuple: dict         # sidechain ⊓ environment — shared floor
    frustration: float       # structural mismatch score
    n_bottlenecks: int
    bottleneck_primitives: List[str]  # which primitives are strained
    n_shared: int            # shared primitives with environment
    tier: str                # Ouroboricity tier of tensor
    pre_distance: float      # sidechain–environment raw distance
    domination: str          # which side dominates the composite
    b_factor: float
    n_neighbors: int


def _extract_hetatm_smiles_from_pdb(pdb_text: str) -> list:
    """Extract SMILES from HETATM records in a PDB file.
    
    Parses HETATM residues (non-standard: ligands, cofactors, modified AAs)
    and converts them to SMILES using RDKit. Filters out water, ions, and
    buffer molecules.
    
    Returns list of (smiles, residue_name) tuples, sorted by heavy atom count.
    """
    if not pdb_text:
        return []
    
    from collections import defaultdict
    from rdkit import Chem
    
    # Collect HETATM lines by residue
    het_residues = defaultdict(list)
    for line in pdb_text.split('\n'):
        if line.startswith('HETATM') or line.startswith('HETSYN'):
            res_name = line[17:20].strip()
            res_num = line[22:26].strip()
            chain = line[21].strip()
            key = f"{res_name}_{res_num}_{chain}"
            het_residues[key].append(line)
    
    # Filter out water, ions, buffers
    skip_set = {'HOH', 'WAT', 'DOD', 'NA', 'CL', 'K', 'MG', 'CA', 'ZN', 'MN',
                'FE', 'CU', 'CO', 'NI', 'SO4', 'PO4', 'EDO', 'GOL', 'ACT',
                'EPE', 'TRS', 'BME', 'DTT', 'PEG', 'MPD', 'DMS', 'DMF'}
    
    smiles_list = []
    for key, lines in het_residues.items():
        parts = key.split('_')
        res_name = parts[0]
        if res_name in skip_set:
            continue
        
        # Build a minimal PDB block for this residue
        block = '\n'.join(lines)
        try:
            with _silence_rdkit_native():
                mol = Chem.MolFromPDBBlock(block, sanitize=True, removeHs=True)
            if mol is not None and mol.GetNumHeavyAtoms() >= 3:
                smi = Chem.MolToSmiles(mol)
                if smi and len(smi) > 3:
                    smiles_list.append((smi, res_name, mol.GetNumHeavyAtoms()))
        except Exception:
            pass
    
    # Sort by size (largest first — most likely the real ligand)
    smiles_list.sort(key=lambda x: -x[2])
    return [s[0] for s in smiles_list]

def encode_site_from_pdb(
    pdb_id_or_path: str,
    active_residues: List[str],
    cutoff: float = 8.0,
    verbose: bool = False,
    protein_glut=None,
) -> Tuple[Optional[dict], List[CatalyticResidueAnalysis], Dict]:
    """Encode a catalytic site from a PDB structure using sidechain×environment algebra.

    This is the CORE INTEGRATION FUNCTION. For each specified active-site residue:
      1. Look up the residue in the parsed PDB structure
      2. Classify its local environment (hydrophobic_core, polar_surface, etc.)
      3. Run analyze_composition(sidechain, environment) → sidechain⊗environment tensor
      4. Record frustration, bottlenecks, tier, and the full tensor tuple

    Then aggregate all catalytic residues into a single site tuple:
      - Each residue contributes its tensor tuple
      - Weighted by frustration (more frustrated residues contribute more)
      - Aggregated using tensor semantics (max on most, min on P/F)

    Args:
        pdb_id_or_path: PDB ID (e.g. '1LYZ') or path to .pdb file
        active_residues: List of residue labels, e.g. ["Glu35", "Asp52"]
        cutoff: Neighbor distance cutoff for environment classification
        verbose: Print progress

    Returns:
        (site_tuple_dict, per_residue_analyses, summary_dict)
    """
    # ── Load PDB ──
    if os.path.exists(pdb_id_or_path):
        if verbose:
            print(f"  Reading PDB: {pdb_id_or_path}")
        with open(pdb_id_or_path, 'r') as f:
            pdb_text = f.read()
        pdb_id = os.path.splitext(os.path.basename(pdb_id_or_path))[0].upper()
    else:
        pdb_id = pdb_id_or_path.strip().upper()
        if verbose:
            print(f"  Fetching PDB {pdb_id} from RCSB...")
        pdb_text = fetch_pdb(pdb_id)

    # ── Parse ──
    residues = parse_pdb_residues(pdb_text)
    if verbose:
        print(f"  Parsed {len(residues)} residues")

    from rhr_p4rky.protein_glut import ProteinGlut, retain_carrier, _NAMES
    from pathlib import Path
    import hashlib
    if protein_glut is None and os.path.exists(pdb_id_or_path):
        sidecar = Path(str(pdb_id_or_path) + '.glut.json')
        if sidecar.exists():
            saved = json.loads(sidecar.read_text())
            if saved['pdb_sha256'] != hashlib.sha256(Path(pdb_id_or_path).read_bytes()).hexdigest():
                raise ValueError('PDB and resident glut sidecar differ')
            protein_glut = saved['protein_glut']
    native_residues = [r for r in residues if r.sidechain_name in SIDECHAINS]
    aas = [next(aa for aa, names in _NAMES.items() if r.sidechain_name in names) for r in native_residues]
    glut = retain_carrier(protein_glut) if protein_glut is not None else ProteinGlut.prepare(aas)
    if [r['aa'] for r in glut.residues] != aas:
        raise ValueError('PDB sequence and resident protein differ')
    native_index = {(r.chain, r.res_num, r.ins_code): i for i, r in enumerate(native_residues)}
    for r, retained in zip(native_residues, glut.residues):
        identity = {'chain': r.chain, 'number': r.res_num, 'insertion': r.ins_code}
        if 'pdb_identity' in retained and retained['pdb_identity'] != identity:
            raise ValueError('PDB residue identity changed across the carrier boundary')
        retained['pdb_identity'] = identity
    site_family = []

    # ── Classify environments ──
    env_map = classify_all_environments(residues, cutoff)

    # ── Build lookup and helper for residue resolution ──
    import re as _re
    residue_lookup = {}
    for r in residues:
        # 3-letter label
        label_3l = f"{r.res_name}{r.res_num}"
        aa_3to1 = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V', 'MSE': 'M', 'HYP': 'P'}
        code1 = aa_3to1.get(r.res_name, "X")
        label_1l = f"{code1}{r.res_num}"
        chain_label_3l = f"{r.chain}:{r.res_name}{r.res_num}"
        chain_label_1l = f"{r.chain}:{code1}{r.res_num}"
        for lbl in [label_3l, label_1l, chain_label_3l, chain_label_1l]:
            residue_lookup[lbl.lower()] = r

    def _find_residue(res_label):
        """Robust residue lookup with fuzzy matching."""
        key = res_label.strip()
        # Direct lookup
        r = residue_lookup.get(key.lower())
        if r is not None:
            return r
        # Parse as 3-letter + number (case-insensitive)
        match = _re.match(r'([A-Za-z]{3})\s*(\d+)', key)
        if match:
            code3 = match.group(1).upper()
            num = int(match.group(2))
            for res in residues:
                if res.res_name.upper() == code3 and res.res_num == num:
                    return res
        # Parse as 1-letter + number
        match = _re.match(r'([A-Za-z])\s*(\d+)', key)
        if match:
            code1 = match.group(1).upper()
            num = int(match.group(2))
            aa_1to3 = {'A': 'ALA', 'R': 'ARG', 'N': 'ASN', 'D': 'ASP', 'C': 'CYS', 'Q': 'GLN', 'E': 'GLU', 'G': 'GLY', 'H': 'HIS', 'I': 'ILE', 'L': 'LEU', 'K': 'LYS', 'M': 'MET', 'F': 'PHE', 'P': 'PRO', 'S': 'SER', 'T': 'THR', 'W': 'TRP', 'Y': 'TYR', 'V': 'VAL'}
            code3 = aa_1to3.get(code1)
            if code3:
                for res in residues:
                    if res.res_name.upper() == code3 and res.res_num == num:
                        return res
        return None

    # ── Compute neighbor counts ──
    neighbor_counts = {}
    for r in residues:
        n = sum(1 for o in residues if o is not r and dist_3d(r, o) <= cutoff)
        neighbor_counts[(r.chain, r.res_num, r.ins_code)] = n

    # ── Analyze each active-site residue ──
    per_residue: List[CatalyticResidueAnalysis] = []
    not_found = []

    for res_label in active_residues:
        r = _find_residue(res_label)
        if r is None:
            not_found.append(res_label)
            if verbose:
                print(f"  ⚠ Residue '{res_label}' not found in structure")
            continue

        sc_name = r.sidechain_name
        if sc_name is None or sc_name not in SIDECHAINS:
            if verbose:
                print(f"  ⚠ {res_label}: no sidechain tuple available (non-standard: {r.res_name})")
            continue

        env_name = env_map.get((r.chain, r.res_num, r.ins_code), "polar_surface")
        key = (r.chain, r.res_num, r.ins_code)
        n_nbrs = neighbor_counts.get(key, 0)

        index = native_index[key]
        analysis = analyze_composition(sc_name, env_name, glut.residues[index]['self_marks'])
        for alternative in analysis.get('self_mark_alternatives', []):
            site_family.append({**alternative, 'residue_index': index,
                'residue_identity': glut.residues[index]['pdb_identity'],
                'environment': env_name,
                'tuple': dict(alternative['tensor'])})
        if "error" in analysis:
            if verbose:
                print(f"  ⚠ {res_label}: analysis error — {analysis['error']}")
            continue

        cra = CatalyticResidueAnalysis(
            res_label=f"{r.res_name}{r.res_num}",
            res_name=r.res_name,
            chain=r.chain,
            res_num=r.res_num,
            sidechain=sc_name,
            environment=env_name,
            tensor_tuple=analysis["tensor"],
            meet_tuple=analysis["meet"],
            frustration=analysis["frustration"],
            n_bottlenecks=analysis["n_bottlenecks"],
            bottleneck_primitives=[b["primitive"] for b in analysis.get("bottlenecks", [])],
            n_shared=analysis["n_shared"],
            tier=analysis["tier_tensor"],
            pre_distance=analysis["distance_pre"],
            domination=analysis["domination"],
            b_factor=r.b_factor,
            n_neighbors=n_nbrs,
        )
        per_residue.append(cra)

        if verbose:
            tup_str = tuple_str(analysis["tensor"])
            print(f"  {cra.res_label:8s} {sc_name:14s} ⊗ {env_name:20s} "
                  f"→ {tup_str}  "
                  f"d={cra.pre_distance:.2f}  frust={cra.frustration:.2f}  "
                  f"bn={cra.n_bottlenecks}  tier={cra.tier}")

    if not per_residue:
        return None, [], {"error": "No active-site residues could be analyzed",
                          "not_found": not_found}

    # The scalar is a named boundary. Production below executes every family
    # branch and returns their correlated provenance on this same carrier.
    site_tuple = dict(site_family[0]['tuple'])
    glut.observe('active-site', site_family)

    # ── Build summary ──
    total_frustration = sum(c.frustration for c in per_residue)
    avg_frustration = total_frustration / len(per_residue)
    all_bottlenecks = []
    for c in per_residue:
        all_bottlenecks.extend(c.bottleneck_primitives)
    bn_counts = defaultdict(int)
    for b in all_bottlenecks:
        bn_counts[b] += 1
    top_bottlenecks = sorted(bn_counts.items(), key=lambda x: -x[1])

    summary = {
        "pdb_id": pdb_id,
        "pdb_text": pdb_text,
        "n_catalytic": len(per_residue),
        "not_found": not_found,
        "site_tuple": site_tuple,
        "site_family": site_family,
        "protein_glut": glut.as_dict(),
        "readout": {"method": "first-source-form", "residue_index": site_family[0]['residue_index'],
                    "artifact_id": site_family[0]['artifact_id']},
        "site_tuple_str": lfas.fmt_tuple(site_tuple),
        "avg_frustration": round(avg_frustration, 3),
        "total_frustration": round(total_frustration, 3),
        "bottleneck_consensus": top_bottlenecks[:5],
        "tiers": list(set(c.tier for c in per_residue)),
        "environments": list(set(c.environment for c in per_residue)),
    }

    return site_tuple, per_residue, summary


def _aggregate_residue_tuples(
    per_residue: List[CatalyticResidueAnalysis],
    verbose: bool = False,
) -> dict:
    """Compatibility boundary; retain the family in encode_site_from_pdb.

    No weighted ordinal averaging. Actual ligand production visits every
    source-form branch and returns the family alongside the scalar readout.
    """
    if not per_residue:
        return {}
    return dict(per_residue[0].tensor_tuple)


# ═══════════════════════════════════════════════════════════════════
# BOTTLENECK-TARGETED LIGAND DESIGN
# ═══════════════════════════════════════════════════════════════════

def complement_with_bottleneck_bias(
    site_tuple: dict,
    bottleneck_primitives: List[str],
    bias_strength: float = 0.5,
) -> dict:
    """Generate a ligand tuple biased toward resolving specific bottlenecks.

    Standard complement (complement_type) maps the site tuple to a ligand tuple
    via the complementary pairs: ⊢↔⊡, ⊣↔⊥, ≻↔⊞, ≺↔⋈, ⊤↔∈, ∋↔⊙.

    Bottleneck bias: for primitives that are bottlenecks, the ligand tuple is
    pushed further from the site's value — making the ligand more "aggressive"
    in resolving the structural mismatch.

    Args:
        site_tuple: The aggregated catalytic site tuple
        bottleneck_primitives: Which primitives are bottlenecks (strained)
        bias_strength: How much to amplify the complement (0=standard, 1=max)

    Returns:
        Biased ligand tuple dict
    """
    # Start with standard complement
    ligand = {}
    for prim_a, prim_b in lfas.COMPLEMENTARY_PAIRS:
        a_max = len(lfas.GLYPH_ORDINALS.get(prim_a, {})) - 1
        b_max = len(lfas.GLYPH_ORDINALS.get(prim_b, {})) - 1

        site_a = lfas.glyph_ord(prim_a, site_tuple.get(prim_a, "?"))
        site_b = lfas.glyph_ord(prim_b, site_tuple.get(prim_b, "?"))

        # Standard inverse
        inv_a = a_max - site_a if a_max > 0 else 0
        inv_b = b_max - site_b if b_max > 0 else 0

        # Bottleneck amplification: if a primitive IS a bottleneck,
        # push its complement further from center
        if prim_a in bottleneck_primitives and a_max > 0:
            # Push toward the extreme that opposes the site value
            if site_a <= a_max // 2:
                inv_a = a_max  # site at low end → ligand at high end
            else:
                inv_a = 0      # site at high end → ligand at low end

        if prim_b in bottleneck_primitives and b_max > 0:
            if site_b <= b_max // 2:
                inv_b = b_max
            else:
                inv_b = 0

        # Map back to glyphs, scaled to target range
        if a_max > 0:
            ligand[prim_b] = lfas.ord_to_glyph(prim_b,
                min(b_max, max(0, round(inv_a / a_max * b_max))))
        else:
            ligand[prim_b] = lfas.ord_to_glyph(prim_b, b_max)

        if b_max > 0:
            ligand[prim_a] = lfas.ord_to_glyph(prim_a,
                min(a_max, max(0, round(inv_b / b_max * a_max))))
        else:
            ligand[prim_a] = lfas.ord_to_glyph(prim_a, a_max)

    return ligand


# ═══════════════════════════════════════════════════════════════════
# FULL INTEGRATED PIPELINE
# ═══════════════════════════════════════════════════════════════════

@dataclass
class LigandDesignResult:
    """Complete result of the PDB-aware ligand design pipeline."""
    pdb_id: str
    active_residues: List[str]
    site_tuple: dict
    site_tuple_str: str
    per_residue: List[CatalyticResidueAnalysis]
    site_summary: dict
    ligand_tuple: dict
    ligand_tuple_str: str
    bottleneck_primitives: List[str]
    closest_bond: str
    bond_distance: float
    closest_fgs: List[str]
    fg_distance: float
    ligand_candidates: List[dict]
    comparison: dict  # comparison with standard (non-PDB-aware) encoding


def design_ligand_from_pdb(
    pdb_id_or_path: str,
    active_residues: List[str],
    cutoff: float = 8.0,
    max_candidates: int = 10,
    bottleneck_bias: float = 0.5,
    verbose: bool = False,
    protein_glut=None,
) -> LigandDesignResult:
    """Run the complete PDB-aware ligand design pipeline.

    1. Fetch & parse PDB → classify environments → sidechain×env analysis
    2. Encode active site using frustration-weighted aggregation
    3. Identify consensus bottleneck primitives
    4. Generate bottleneck-biased ligand tuple via structural complement
    5. Decompose into bond + FG features
    6. Generate de-novo SMILES ligands with RDKit
    7. Compare with standard (non-PDB-aware) encoding
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"  PDB-AWARE LIGAND DESIGN PIPELINE")
        print(f"  PDB: {pdb_id_or_path}")
        print(f"  Active site: {', '.join(active_residues)}")
        print(f"{'='*70}\n")

    # ── Step 1: Encode site from PDB ──
    site_tuple, per_residue, summary = encode_site_from_pdb(
        pdb_id_or_path, active_residues, cutoff=cutoff, verbose=verbose, protein_glut=protein_glut)

    if site_tuple is None:
        raise RuntimeError(f"Could not encode active site: {summary.get('error', 'unknown')}")

    # ── Step 2: Identify bottleneck consensus ──
    bottleneck_primitives = [b for b, count in summary.get("bottleneck_consensus", [])]

    if verbose:
        print(f"\n  Site tuple: {lfas.fmt_tuple(site_tuple)}")
        print(f"  Avg frustration: {summary['avg_frustration']}")
        print(f"  Bottleneck consensus: {bottleneck_primitives}")

    # ── Step 3: Generate ligand tuple (bottleneck-biased complement) ──
    ligand_tuple = complement_with_bottleneck_bias(
        site_tuple, bottleneck_primitives, bias_strength=bottleneck_bias)
    ligand_str = lfas.fmt_tuple(ligand_tuple)

    if verbose:
        print(f"  Ligand tuple: {lfas.fmt_tuple(ligand_tuple)}")

    # ── Step 4: Decompose into bond + FG ──
    bond_name, bond_tuple, bond_dist = lfas.closest_bond_type(ligand_tuple)
    fg_pair, fg_fused, fg_dist = lfas.closest_fg_pair(ligand_tuple)

    if verbose:
        print(f"  Closest bond: {bond_name} (d={bond_dist:.3f})")
        print(f"  Closest FGs:   {fg_pair} (d={fg_dist:.3f})")

    # ── Step 5: Generate SMILES candidates ──
    substrate_hint = ""
    # Try to find substrate hint from protein lookup
    for p in lfas.CATALYZING_PROTEINS:
        if p.get("pdb", "").upper() == summary.get("pdb_id", "").upper():
            substrate_hint = p.get("smiles_substrate_hint", "")
            break
    
    # Extract HETATM ligands from PDB as additional substrate hints
    het_smiles = _extract_hetatm_smiles_from_pdb(summary.get("pdb_text", ""))
    if het_smiles and not substrate_hint:
        substrate_hint = het_smiles[0]  # Use largest co-crystallized ligand
        if verbose:
            print(f"  Extracted substrate from PDB HETATM: {substrate_hint}")

    # Try improved engine first, fall back to standard
    improved = None
    try:
        improved = lfas._get_improved()
    except Exception:
        pass
    
    if improved is not None:
        try:
            if verbose:
                print(f"  Using improved fragment-based engine...")
            candidates = improved.generate_from_enzyme_type(
                site_type=site_tuple,
                substrate_hint=substrate_hint,
                max_candidates=max_candidates,
            )
            gen_result = {
                "ligand_type": ligand_tuple,
                "ligand_type_fmt": lfas.fmt_tuple(ligand_tuple),
                "closest_bond": improved._estimate_bond_from_site_type(site_tuple),
                "closest_fgs": improved._estimate_fgs_from_site_type(site_tuple, ""),
                "ligand_candidates": candidates,
            }
        except Exception as e:
            if verbose:
                print(f"  Improved engine failed ({e}), falling back to standard")
            improved = None
    
    if improved is None:
        # Use decompose_and_generate for full pipeline including SMILES
        gen_result = lfas.decompose_and_generate(
            site_type=ligand_tuple,
            substrate_hint=substrate_hint)
    candidates = gen_result.get("ligand_candidates", [])
    # Update bond/fg from decompose result if ours were None
    if not bond_name:
        bond_name = gen_result.get("closest_bond", "")
        bond_dist = gen_result.get("bond_distance", 999)
    if not fg_pair:
        fg_pair = gen_result.get("closest_fgs", [])
        fg_dist = gen_result.get("fg_distance", 999)

    if verbose:
        print(f"\n  Generated {len(candidates)} ligand candidates:")

    # ── Step 6: Compare with standard encoding ──
    standard_site = lfas.encode_site_from_residues(active_residues)
    comparison = _compare_encodings(standard_site, site_tuple, active_residues, per_residue)

    if verbose and standard_site:
        std_str = lfas.fmt_tuple(standard_site)
        site_str = lfas.fmt_tuple(site_tuple)
        dist = comparison["distance"]
        print(f"\n  Comparison with standard encoding:")
        print(f"    Standard (AA→primitive): {std_str}")
        print(f"    PDB-aware (sidechain⊗env): {site_str}")
        print(f"    Distance between encodings: {dist:.3f}")
        if comparison["key_differences"]:
            print(f"    Key differences:")
            for diff in comparison["key_differences"][:5]:
                print(f"      {diff['primitive']}: standard={diff['standard_glyph']} "
                      f"pdb_aware={diff['pdb_glyph']} (Δord={diff['delta_ord']})")

    result = LigandDesignResult(
        pdb_id=summary["pdb_id"],
        active_residues=active_residues,
        site_tuple=site_tuple,
        site_tuple_str=summary["site_tuple_str"],
        per_residue=per_residue,
        site_summary=summary,
        ligand_tuple=ligand_tuple,
        ligand_tuple_str=ligand_str,
        bottleneck_primitives=bottleneck_primitives,
        closest_bond=bond_name or "",
        bond_distance=bond_dist,
        closest_fgs=fg_pair or [],
        fg_distance=fg_dist,
        ligand_candidates=candidates,
        comparison=comparison,
    )
    return _retain_ligand_family(result, max_candidates, improved=improved,
                                 substrate_hint=substrate_hint)


def _retain_ligand_family(result, max_candidates, improved=None, substrate_hint=''):
    from rhr_p4rky.protein_glut import retain_carrier, produce_ligand_family
    glut = retain_carrier(result.site_summary['protein_glut'])
    def generate(site_type):
        produced = lfas.decompose_and_generate(site_type, substrate_hint=substrate_hint)
        if improved is not None:
            generated = improved.generate_from_enzyme_type(
                site_type=site_type, substrate_hint=substrate_hint,
                max_candidates=max_candidates)
            if generated:
                produced['ligand_candidates'] = generated
                produced['generator'] = 'fragment-engine'
        return produced
    family, candidates = produce_ligand_family(
        glut, result.site_summary['site_family'], max_candidates, generator=generate)
    result.ligand_tuple = family[0]['ligand_tuple']
    result.ligand_tuple_str = lfas.fmt_tuple(result.ligand_tuple)
    result.closest_bond, _, result.bond_distance = lfas.closest_bond_type(result.ligand_tuple)
    result.closest_fgs, _, result.fg_distance = lfas.closest_fg_pair(result.ligand_tuple)
    result.ligand_candidates = candidates
    result.site_summary['ligand_family'] = family
    result.site_summary['protein_glut'] = glut.as_dict()
    return result


def _compare_encodings(
    standard_site: Optional[dict],
    pdb_site: dict,
    residue_labels: List[str],
    per_residue: List[CatalyticResidueAnalysis],
) -> dict:
    """Compare standard (AA→primitive) encoding with PDB-aware encoding."""
    if standard_site is None:
        return {"distance": None, "key_differences": [], "note": "no standard encoding available"}

    dist = lfas.tuple_distance_dict(standard_site, pdb_site)

    key_diffs = []
    for p in PRIMITIVE_SYMBOLS:
        std_ord = lfas.glyph_ord(p, standard_site.get(p, "?"))
        pdb_ord = lfas.glyph_ord(p, pdb_site.get(p, "?"))
        delta = pdb_ord - std_ord
        if delta != 0:
            key_diffs.append({
                "primitive": p,
                "standard_ord": std_ord,
                "pdb_ord": pdb_ord,
                "delta_ord": delta,
                "standard_glyph": lfas.ord_to_glyph(p, std_ord),
                "pdb_glyph": lfas.ord_to_glyph(p, pdb_ord),
            })

    # Per-residue environment detail
    env_detail = []
    for cra in per_residue:
        env_detail.append({
            "residue": cra.res_label,
            "sidechain": cra.sidechain,
            "environment": cra.environment,
            "frustration": cra.frustration,
            "tier": cra.tier,
            "bottlenecks": cra.bottleneck_primitives,
        })

    return {
        "distance": round(dist, 3),
        "key_differences": key_diffs,
        "n_differences": len(key_diffs),
        "per_residue_env": env_detail,
    }


# ═══════════════════════════════════════════════════════════════════
# AUTO-DETECTION OF ACTIVE SITES
# ═══════════════════════════════════════════════════════════════════

# Catalytic residues by function (canonical 3-letter codes)
CATALYTIC_RESIDUE_TYPES = {
    "nucleophile":   ["SER", "CYS", "THR", "ASP", "GLU", "LYS", "HIS", "TYR"],
    "acid_base":     ["HIS", "ASP", "GLU", "LYS", "CYS", "TYR", "SER", "ARG"],
    "metal_ligand":  ["HIS", "CYS", "ASP", "GLU", "MET"],
    "charge_relay":  ["ASP", "GLU", "HIS"],
    "oxyanion_hole": ["GLY", "ALA", "SER", "THR"],
    "substrate_binding": ["ARG", "LYS", "HIS", "TRP", "TYR", "PHE", "ASN", "GLN", "SER", "THR"],
}

# All potential catalytic residue types (union)
ALL_CATALYTIC_TYPES = list(set(
    CATALYTIC_RESIDUE_TYPES["nucleophile"] +
    CATALYTIC_RESIDUE_TYPES["acid_base"] +
    CATALYTIC_RESIDUE_TYPES["metal_ligand"]
))


def auto_detect_active_site(
    pdb_id_or_path: str,
    cutoff: float = 8.0,
    proximity_cutoff: float = 12.0,
    min_cluster: int = 2,
    verbose: bool = False,
) -> List[str]:
    """Auto-detect likely active-site residues from PDB structure.

    Strategy:
      1. Parse all residues from the PDB
      2. Identify residues whose type is in the catalytic set
         (SER, CYS, HIS, ASP, GLU, LYS — the classic catalytic residues)
      3. Find spatial clusters of catalytic-type residues (proximity_cutoff)
      4. The largest/best cluster is the putative active site
      5. Rank residues by: catalytic potential × structural frustration
      6. Return the top cluster as residue labels

    Args:
        pdb_id_or_path: PDB ID or file path
        cutoff: Environment classification cutoff
        proximity_cutoff: Max distance (Å) for residues to be in same cluster
        min_cluster: Minimum cluster size to consider
        verbose: Print diagnostics

    Returns:
        List of residue labels (e.g. ["GLU35", "ASP52"])
    """
    # Load and parse
    if os.path.exists(pdb_id_or_path):
        with open(pdb_id_or_path, 'r') as f:
            pdb_text = f.read()
    else:
        pdb_text = fetch_pdb(pdb_id_or_path.strip().upper())

    residues = parse_pdb_residues(pdb_text)
    env_map = classify_all_environments(residues, cutoff)

    # Find catalytic-type residues
    catalytic_residues = []
    for r in residues:
        if r.res_name in ALL_CATALYTIC_TYPES:
            env = env_map.get((r.chain, r.res_num, r.ins_code), "polar_surface")
            # Structural frustration: if sidechain is available, compute it
            sc_name = r.sidechain_name
            frustration = 0.0
            if sc_name and sc_name in SIDECHAINS and env in ENVIRONMENTS:
                analysis = analyze_composition(sc_name, env)
                frustration = analysis.get("frustration", 0.0)

            catalytic_residues.append({
                "residue": r,
                "label": f"{r.res_name}{r.res_num}",
                "environment": env,
                "frustration": frustration,
                "sidechain": sc_name,
            })

    if verbose:
        print(f"  Found {len(catalytic_residues)} catalytic-type residues")

    if len(catalytic_residues) < min_cluster:
        # Return all catalytic-type residues if too few for clustering
        return [c["label"] for c in catalytic_residues]

    # Spatial clustering (single-linkage)
    clusters = []
    assigned = set()

    for i, cr in enumerate(catalytic_residues):
        if i in assigned:
            continue
        cluster = [cr]
        assigned.add(i)

        # Expand cluster
        changed = True
        while changed:
            changed = False
            for j, cr2 in enumerate(catalytic_residues):
                if j in assigned:
                    continue
                # Check distance to ANY member of current cluster
                for member in cluster:
                    d = dist_3d(cr["residue"], cr2["residue"]) if member is cr else \
                        dist_3d(member["residue"], cr2["residue"])
                    if d <= proximity_cutoff:
                        cluster.append(cr2)
                        assigned.add(j)
                        changed = True
                        break

        if len(cluster) >= min_cluster:
            clusters.append(cluster)

    if not clusters:
        # Fallback: return all catalytic-type residues
        return [c["label"] for c in catalytic_residues]

    # Score clusters by: size + avg_frustration
    def cluster_score(cluster):
        avg_frust = sum(c["frustration"] for c in cluster) / max(len(cluster), 1)
        return len(cluster) * (1.0 + avg_frust)

    clusters.sort(key=cluster_score, reverse=True)
    best = clusters[0]

    # Cap cluster size: if cluster is too large, rank by frustration and keep top N
    MAX_CLUSTER_SIZE = 25
    if len(best) > MAX_CLUSTER_SIZE:
        # Sort by frustration (descending) — frustrated residues are the pressure points
        best.sort(key=lambda c: c["frustration"], reverse=True)
        best = best[:MAX_CLUSTER_SIZE]

    if verbose:
        print(f"  Best cluster: {len(best)} residues, "
              f"avg frust={sum(c['frustration'] for c in best)/len(best):.3f}")
        for c in best[:30]:
            print(f"    {c['label']:8s} env={c['environment']:20s} frust={c['frustration']:.2f}")

    return [c["label"] for c in best]


# ═══════════════════════════════════════════════════════════════════
# PRETTY-PRINTING
# ═══════════════════════════════════════════════════════════════════

def print_ligand_result(result: LigandDesignResult):
    """Pretty-print a full ligand design result."""
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}  PDB-AWARE LIGAND DESIGN — {result.pdb_id}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}")

    # Active site
    print(f"\n{YELLOW}▶ Active site:{RESET} {', '.join(result.active_residues)}")
    print(f"  Residues analyzed: {len(result.per_residue)}")
    for cra in result.per_residue:
        env_short = cra.environment.replace("_", " ")[:20]
        print(f"    {cra.res_label:8s} {cra.sidechain:12s} ⊗ {env_short:22s}  "
              f"frust={cra.frustration:.2f}  bn={cra.n_bottlenecks}  tier={cra.tier}")

    # Site encoding
    print(f"\n{YELLOW}▶ Catalytic site structural type:{RESET}")
    print(f"    {lfas.fmt_tuple(result.site_tuple)}")
    print(f"    Avg frustration: {result.site_summary['avg_frustration']:.3f}")
    print(f"    Bottleneck consensus: {result.bottleneck_primitives}")

    # Comparison with standard
    comp = result.comparison
    if comp.get("distance") is not None:
        print(f"\n{YELLOW}▶ vs. Standard (AA→primitive) encoding:{RESET}")
        print(f"    Distance: {comp['distance']:.3f}  "
              f"({comp['n_differences']} primitives differ)")
        for diff in comp.get("key_differences", [])[:3]:
            print(f"    {diff['primitive']}: standard={diff['standard_glyph']}  "
                  f"pdb_aware={diff['pdb_glyph']}  (Δ={diff['delta_ord']:+d})")

    # Ligand tuple
    print(f"\n{YELLOW}▶ Ligand structural type (bottleneck-biased complement):{RESET}")
    print(f"    {lfas.fmt_tuple(result.ligand_tuple)}")

    # Decomposition
    print(f"\n{YELLOW}▶ Bond + FG decomposition:{RESET}")
    print(f"    Bond: {result.closest_bond}  (d={result.bond_distance:.3f})")
    print(f"    FGs:  {result.closest_fgs}  (d={result.fg_distance:.3f})")

    # Candidates
    print(f"\n{YELLOW}▶ Ligand candidates ({len(result.ligand_candidates)}):{RESET}\n")
    if result.ligand_candidates:
        header = f"  {'SMILES':50s} {'Score':8s} {'logP':6s} {'MW':7s} {'HBD':4s} {'HBA':4s} {'Method':20s}"
        print(header)
        print(f"  {'-'*50} {'-'*8} {'-'*6} {'-'*7} {'-'*4} {'-'*4} {'-'*20}")
        for c in result.ligand_candidates[:15]:
            # Handle both dict format and tuple format
            if isinstance(c, dict):
                smiles = c.get('smiles', '?')
                score = c.get('composite_score', 0)
                logp = c.get('logP', 0)
                mw = c.get('MW', 0)
                hbd = c.get('HBD', 0)
                hba = c.get('HBA', 0)
                method = c.get('method', '?')
                bn_targeted = c.get('bottleneck_targeted', False)
            elif isinstance(c, (tuple, list)) and len(c) >= 2:
                smiles = str(c[0])
                method = str(c[1])
                score = 0; logp = 0; mw = 0; hbd = 0; hba = 0
                bn_targeted = False
            else:
                continue
            marker = ""
            if c.get('bottleneck_targeted'):
                marker = f" {GREEN}★{RESET}"
            metrics = f"score={score:6.3f}  logP={logp:5.2f}  MW={mw:6.1f}  HBD={hbd}  HBA={hba}"
            print(f"  {smiles:<80s} {method:22s} {metrics:>56s}{marker}")

        # Drug-likeness
        lipinski_count = sum(
            1 for c in result.ligand_candidates
            if (isinstance(c, dict) and 
                c.get('MW', 999) <= 500 and c.get('logP', 999) <= 5
                and c.get('HBD', 999) <= 5 and c.get('HBA', 999) <= 10)
        )
        print(f"\n  Lipinski-compliant: {lipinski_count}/{len(result.ligand_candidates)}")

    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}  DESIGN COMPLETE{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}")


def result_to_json(result: LigandDesignResult) -> dict:
    """Serialize a LigandDesignResult to JSON-serializable dict."""
    return {
        "pdb_id": result.pdb_id,
        "protein_glut": result.site_summary['protein_glut'],
        "site_family": result.site_summary['site_family'],
        "ligand_family": result.site_summary['ligand_family'],
        "readout": result.site_summary['readout'],
        "active_residues": result.active_residues,
        "site_tuple_str": result.site_tuple_str,
        "site_summary": {
            "pdb_id": result.site_summary["pdb_id"],
            "n_catalytic": result.site_summary["n_catalytic"],
            "avg_frustration": result.site_summary["avg_frustration"],
            "bottleneck_consensus": result.site_summary.get("bottleneck_consensus", []),
            "tiers": result.site_summary.get("tiers", []),
        },
        "ligand_tuple_str": result.ligand_tuple_str,
        "bottleneck_primitives": result.bottleneck_primitives,
        "closest_bond": result.closest_bond,
        "bond_distance": result.bond_distance,
        "closest_fgs": result.closest_fgs,
        "fg_distance": result.fg_distance,
        "ligand_candidates": result.ligand_candidates,
        "n_candidates": len(result.ligand_candidates),
        "comparison": {
            "distance": result.comparison.get("distance"),
            "n_differences": result.comparison.get("n_differences", 0),
            "key_differences": result.comparison.get("key_differences", [])[:5],
        },
        "per_residue": [
            {
                "residue": cra.res_label,
                "sidechain": cra.sidechain,
                "environment": cra.environment,
                "frustration": cra.frustration,
                "tier": cra.tier,
                "n_neighbors": cra.n_neighbors,
                "bottlenecks": cra.bottleneck_primitives,
            }
            for cra in result.per_residue
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="PDB-Aware Ligand Design from Catalytic Sites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Known active site
  python ligand_from_site_pdb.py --pdb 1LYZ --active Glu35,Asp52

  # Auto-detect active site
  python ligand_from_site_pdb.py --pdb 1LYZ --auto-active

  # From local file with JSON output
  python ligand_from_site_pdb.py --pdb-file structure.pdb --active Ser160,Asp206,His237 --json

  # Full verbose output
  python ligand_from_site_pdb.py --pdb 1LYZ --active Glu35,Asp52 --verbose --top-n 15
        """)

    parser.add_argument("--pdb", help="PDB ID to fetch from RCSB (e.g. 1LYZ)")
    parser.add_argument("--pdb-file", help="Path to local PDB file")
    parser.add_argument("--active", help="Comma-separated active site residues (e.g. Glu35,Asp52)")
    parser.add_argument("--auto-active", action="store_true",
                        help="Auto-detect active site from catalytic residue clusters")
    parser.add_argument("--cutoff", type=float, default=8.0,
                        help="Neighbor cutoff for environment classification (default: 8.0 Å)")
    parser.add_argument("--proximity", type=float, default=12.0,
                        help="Proximity cutoff for active-site clustering (default: 12.0 Å)")
    parser.add_argument("--top-n", type=int, default=10,
                        help="Number of ligand candidates to generate (default: 10)")
    parser.add_argument("--bottleneck-bias", type=float, default=0.5,
                        help="Bottleneck bias strength 0-1 (default: 0.5)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--improved", action="store_true",
                        help="Use improved fragment-based engine (RDKit)")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose output")

    args = parser.parse_args()

    # Determine PDB source
    if args.pdb_file:
        pdb_source = args.pdb_file
    elif args.pdb:
        pdb_source = args.pdb
    else:
        parser.error("Must specify --pdb or --pdb-file")

    # Determine active residues
    if args.active:
        active_residues = [r.strip() for r in args.active.split(",")]
    elif args.auto_active:
        if args.verbose:
            print("Auto-detecting active site...")
        active_residues = auto_detect_active_site(
            pdb_source, cutoff=args.cutoff,
            proximity_cutoff=args.proximity, verbose=args.verbose)
        if not active_residues:
            print("ERROR: No catalytic residues detected.", file=sys.stderr)
            sys.exit(1)
        if args.verbose:
            print(f"\nDetected active site: {', '.join(active_residues)}")
    else:
        parser.error("Must specify --active or --auto-active")

    # Run pipeline (improved or standard)
    try:
        if args.improved:
            result = design_ligand_from_pdb_improved(
                pdb_source, active_residues,
                cutoff=args.cutoff, max_candidates=args.top_n,
                bottleneck_bias=args.bottleneck_bias,
                verbose=args.verbose)
        else:
            result = design_ligand_from_pdb(
                pdb_source, active_residues,
                cutoff=args.cutoff, max_candidates=args.top_n,
                bottleneck_bias=args.bottleneck_bias,
                verbose=args.verbose)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Output
    if args.json:
        print(json.dumps(result_to_json(result), indent=2, ensure_ascii=False))
    else:
        print_ligand_result(result)



# ═══════════════════════════════════════════════════════════════════
# IMPROVED ENGINE INTEGRATION (RDKit fragment-based)
# ═══════════════════════════════════════════════════════════════════

def _get_improved_engine():
    """Get the improved ligand generation engine (fragment-based, with scoring)."""
    try:
        return lfas._get_improved()
    except Exception:
        return None


def design_ligand_from_pdb_improved(
    pdb_id_or_path: str,
    active_residues: List[str],
    cutoff: float = 8.0,
    max_candidates: int = 10,
    bottleneck_bias: float = 0.5,
    verbose: bool = False,
    protein_glut=None,
) -> LigandDesignResult:
    """Run the PDB-aware pipeline with the IMPROVED fragment-based ligand engine.

    Same as design_ligand_from_pdb but uses RDKit fragment-based enumeration
    with structural scoring (logP, MW, HBD, HBA, TPSA, composite score).
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"  PDB-AWARE LIGAND DESIGN (IMPROVED ENGINE)")
        print(f"  PDB: {pdb_id_or_path}")
        print(f"  Active site: {', '.join(active_residues)}")
        print(f"{'='*70}\n")

    # ── Step 1: Encode site from PDB ──
    site_tuple, per_residue, summary = encode_site_from_pdb(
        pdb_id_or_path, active_residues, cutoff=cutoff, verbose=verbose, protein_glut=protein_glut)

    if site_tuple is None:
        raise RuntimeError(f"Could not encode active site: {summary.get('error', 'unknown')}")

    # ── Step 2: Identify bottlenecks ──
    bottleneck_primitives = [b for b, _ in summary.get("bottleneck_consensus", [])]

    # ── Step 3: Generate bottleneck-biased ligand tuple ──
    ligand_tuple = complement_with_bottleneck_bias(
        site_tuple, bottleneck_primitives, bias_strength=bottleneck_bias)
    ligand_str = lfas.fmt_tuple(ligand_tuple)

    if verbose:
        print(f"\n  Site tuple: {lfas.fmt_tuple(site_tuple)}")
        print(f"  Bottlenecks: {bottleneck_primitives}")
        print(f"  Ligand tuple: {ligand_str}")

    # ── Step 4: Try improved engine, fall back to standard ──
    improved = _get_improved_engine()
    candidates = []
    bond_name = ""
    fg_pair = []

    if improved is not None:
        try:
            if verbose:
                print(f"  Using improved fragment-based engine...")
            candidates = improved.generate_from_enzyme_type(
                site_type=site_tuple,
                substrate_hint="",
                max_candidates=max_candidates,
            )
            bond_name = improved._estimate_bond_from_site_type(site_tuple)
            fg_pair = improved._estimate_fgs_from_site_type(site_tuple, bond_name)
        except Exception as e:
            if verbose:
                print(f"  Improved engine failed: {e}, falling back to standard")
            improved = None

    if improved is None or not candidates:
        # Fall back to standard decompose_and_generate
        gen_result = lfas.decompose_and_generate(site_type=ligand_tuple, substrate_hint="")
        candidates_raw = gen_result.get("ligand_candidates", [])
        bond_name = gen_result.get("closest_bond", "")
        fg_pair = gen_result.get("closest_fgs", [])
        # Convert tuple format to dict format for consistent display
        candidates = []
        for c in candidates_raw:
            if isinstance(c, (tuple, list)) and len(c) >= 2:
                candidates.append({"smiles": c[0], "method": c[1],
                                   "composite_score": 0, "logP": 0, "MW": 0,
                                   "HBD": 0, "HBA": 0, "TPSA": 0})
            elif isinstance(c, dict):
                candidates.append(c)

    # ── Step 5: Bond/FG decomposition for reference ──
    bond_name2, bond_tuple2, bond_dist = lfas.closest_bond_type(ligand_tuple)
    fg_pair2, fg_fused2, fg_dist = lfas.closest_fg_pair(ligand_tuple)

    if verbose and candidates:
        print(f"\n  Generated {len(candidates)} ligand candidates:")

    # ── Step 6: Compare with standard encoding ──
    standard_site = lfas.encode_site_from_residues(active_residues)
    comparison = _compare_encodings(standard_site, site_tuple, active_residues, per_residue)

    result = LigandDesignResult(
        pdb_id=summary["pdb_id"],
        active_residues=active_residues,
        site_tuple=site_tuple,
        site_tuple_str=summary["site_tuple_str"],
        per_residue=per_residue,
        site_summary=summary,
        ligand_tuple=ligand_tuple,
        ligand_tuple_str=ligand_str,
        bottleneck_primitives=bottleneck_primitives,
        closest_bond=bond_name or bond_name2 or "",
        bond_distance=bond_dist,
        closest_fgs=fg_pair or fg_pair2 or [],
        fg_distance=fg_dist,
        ligand_candidates=candidates,
        comparison=comparison,
    )
    return _retain_ligand_family(result, max_candidates, improved=improved)

if __name__ == "__main__":
    main()
