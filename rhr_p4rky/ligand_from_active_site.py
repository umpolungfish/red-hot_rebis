#!/usr/bin/env python3
"""
ligand_from_active_site.py — REVERSE PIPELINE: Active Site → De-Novo Ligand.

Structural inversion of the ch3mpiler_serpentrod_pipeline:

  FORWARD (ch3mpiler_serpentrod_pipeline.py):
    Reaction (bond + FG1 + FG2) → fuse → fused tuple → complement → site tuple → AAs

  REVERSE (this module):
    Enzyme active site (AA residues) → encode → site tuple → complement → ligand tuple
    → decompose into bond + FG features → generate de-novo SMILES

Key insight: complement_type_v2() IS ITS OWN INVERSE. The same complementary
bijection that maps reaction → catalytic site also maps catalytic site → ligand.
The structural complement pairs (D↔W, T↔H, R↔S, P↔F, K↔G, Gm↔Ph) are symmetric.

Given a "bevy" of catalyzing proteins, this module:
  1. Loads their active sites (specified by PDB/crystal structure or known residues)
  2. Encodes them as 12-primitive structural types via the AA→primitive bijection
  3. Applies complement to get the ligand structural type
  4. Decomposes into bond type + FG pair matching the ch3mpiler's BOND_TYPES/FG tables
  5. Generates de-novo SMILES ligands using RDKit

Author: Lando ⊗ ⊙perator
"""

import sys, os, json, math, itertools
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D

# Paths
BASE = Path(__file__).parent.absolute()
REBIS_ROOT = BASE.parent
sys.path.insert(0, str(REBIS_ROOT))
sys.path.insert(0, str(BASE))

from shared.rich_output import *
from shared.primitives import ORDINALS, WEIGHTS, PRIMITIVE_ORDER, tuple_distance

# ── Reuse the forward pipeline's complement machinery ──────────────
# Import the glyph_ord, ord_to_glyph, complement_type_v2 from the forward pipeline
_forward_pipeline = None
def _get_forward():
    global _forward_pipeline
    if _forward_pipeline is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ch3mpiler_serpentrod_pipeline", 
            BASE / "ch3mpiler_serpentrod_pipeline.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _forward_pipeline = mod
    return _forward_pipeline


# ── AA-to-Primitive bijection (mirrors the forward pipeline) ────────

PRIMITIVE_NAMES_SHORT = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]
PRIMITIVE_FULL_NAMES = [
    "Dimensionality", "Topology", "Recognition", "Parity", "Fidelity",
    "Kinetics", "Granularity", "Coupling", "Criticality", "Chirality",
    "Stoichiometry", "Winding"
]

# Each AA has a dominant primitive (from the serpentrod bijection)
AA_TO_PRIMITIVE = {
    "Met": "D", "Trp": "T", "Cys": "R", "Tyr": "P", "Phe": "F",
    "Ile": "K", "His": "G", "Asn": "Gm", "Gln": "Ph",
    "Asp": "H", "Lys": "S", "Glu": "W"
}

# Primitive → complementary primitive pairs
COMPLEMENTARY_PAIRS = [("D","W"), ("T","H"), ("R","S"), ("P","F"), ("K","G"), ("Gm","Ph")]

# Ordinal mappings (glyph → ordinal 0-based)
# These match GLYPH_ORDINALS from the forward pipeline
GLYPH_ORDINALS = {
    "D": {"𐑛": 0, "𐑨": 1, "𐑼": 2, "𐑦": 3},
    "T": {"𐑡": 0, "𐑰": 1, "𐑥": 2, "𐑶": 3, "𐑸": 4},
    "R": {"𐑩": 0, "𐑑": 1, "𐑽": 2, "𐑾": 3},
    "P": {"𐑗": 0, "𐑿": 1, "𐑬": 2, "𐑯": 3, "𐑹": 4},
    "F": {"𐑱": 0, "𐑞": 1, "𐑐": 2},
    "K": {"𐑘": 0, "𐑤": 1, "𐑧": 2, "𐑺": 3, "𐑪": 4},
    "G": {"𐑚": 0, "𐑔": 1, "𐑲": 2},
    "Gm": {"𐑝": 0, "𐑜": 1, "𐑠": 2, "𐑵": 3},
    "Ph": {"𐑢": 0, "⊙": 1, "𐑮": 2, "𐑻": 3, "𐑣": 4},
    "H": {"𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3},
    "S": {"𐑙": 0, "𐑕": 1, "𐑳": 2},
    "W": {"𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3}
}

ORD_TO_GLYPH = {}
for prim, mapping in GLYPH_ORDINALS.items():
    rev = {v: k for k, v in mapping.items()}
    ORD_TO_GLYPH[prim] = rev


def glyph_ord(prim: str, glyph: str) -> int:
    return GLYPH_ORDINALS.get(prim, {}).get(glyph, 0)


def ord_to_glyph(prim: str, ordinal: int) -> str:
    return ORD_TO_GLYPH.get(prim, {}).get(ordinal, "?")


def fmt_tuple(t: dict) -> str:
    """Format a 12-primitive dict as ⟨...> string."""
    return "<" + "".join(t.get(p, "?") for p in PRIMITIVE_NAMES_SHORT) + ">"


def tuple_distance_dict(t1: dict, t2: dict) -> float:
    """Weighted Euclidean distance between two 12-primitive dicts."""
    sq = 0.0
    for p in PRIMITIVE_NAMES_SHORT:
        o1 = glyph_ord(p, t1.get(p, "?"))
        o2 = glyph_ord(p, t2.get(p, "?"))
        w = 1.0  # uniform weight
        sq += w * (o1 - o2) ** 2
    return math.sqrt(sq)



# ── Catalog-backed structural matching (FIRST PRINCIPLES) ──────────
# Bond types and functional groups are imscribed in the grammar catalog
# via the 12-primitive imscription procedure. Matching uses catalog
# entries rather than hardcoded fallback tuples.

_CATALOG_CACHE = None

def _load_catalog():
    """Load the imscribed catalog for structural matching. Cached."""
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE
    import json as _json
    catalog_paths = [
        str(REBIS_ROOT / "shared" / "IG_catalog.json"),
        str(REBIS_ROOT.parent / "imscribing_grammar" / "IG_catalog.json"),
        str(REBIS_ROOT.parent / "imscribe.com" / "IG_catalog.json"),
    ]
    for cp in catalog_paths:
        if Path(cp).exists():
            with open(cp) as f:
                _CATALOG_CACHE = _json.load(f)
            return _CATALOG_CACHE
    _CATALOG_CACHE = []
    return _CATALOG_CACHE

# Bond type names in the catalog (imscribed from first principles)
_CATALOG_BOND_NAMES = [
    "sigma_single_bond", "carbonyl_bond", "amide_bond",
    "ester_bond", "aromatic_ring",
]

# FG names in the catalog (imscribed from first principles)
_CATALOG_FG_NAMES = [
    "alcohol_fg", "amine_fg", "carboxylic_acid_fg",
    # Additional FGs can be added as they are imscribed
]

# Map catalog primitive keys to short names
_CATALOG_KEY_MAP = {
    "Ð": "D", "Þ": "T", "Ř": "R", "Φ": "P", "ƒ": "F",
    "Ç": "K", "Γ": "G", "ɢ": "Gm", "⊙": "Ph",
    "Ħ": "H", "Σ": "S", "Ω": "W",
}

def _catalog_entry_to_tuple(entry: dict) -> dict:
    """Convert a catalog entry dict to a 12-primitive dict with short keys."""
    result = {}
    for cat_key, short_key in _CATALOG_KEY_MAP.items():
        if cat_key in entry:
            result[short_key] = entry[cat_key]
    return result

def _get_catalog_tuples_by_name(names: list) -> dict:
    """Return {name: 12-primitive-dict} for names found in the catalog."""
    cat = _load_catalog()
    result = {}
    if not cat:
        return result
    if isinstance(cat, list):
        for name in names:
            for entry in cat:
                if entry.get("name") == name:
                    result[name] = _catalog_entry_to_tuple(entry)
                    break
    elif isinstance(cat, dict):
        entries = cat.get("entries", cat.get("catalog", {}))
        if isinstance(entries, dict):
            for name in names:
                if name in entries:
                    result[name] = _catalog_entry_to_tuple(entries[name])
    return result

# ── Load ch3mpiler's BOND_TYPES and FG tables ──────────────────────

_ch3mpiler_module = None

def _get_ch3mpiler():
    """Try to load ch3mpiler; return None on failure (uses fallback tables)."""
    global _ch3mpiler_module
    if _ch3mpiler_module is not None:
        return _ch3mpiler_module
    try:
        import importlib.util
        # Fix path: compiler.py is in ch3mpiler/ subdir, not REBIS_ROOT directly
        compiler_path = REBIS_ROOT / "ch3mpiler" / "compiler.py"
        if not compiler_path.exists():
            compiler_path = REBIS_ROOT.parent / "ch3mpiler" / "compiler.py"
        if not compiler_path.exists():
            return None
        spec = importlib.util.spec_from_file_location(
            "ch3mpiler_compiler", compiler_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ch3mpiler_compiler"] = mod
        # Set __package__ so relative imports work
        mod.__package__ = "ch3mpiler"
        mod.__path__ = [str(compiler_path.parent)]
        # Insert path for relative imports
        sys.path.insert(0, str(compiler_path.parent))
        spec.loader.exec_module(mod)
        _ch3mpiler_module = mod
    except Exception as e:
        _ch3mpiler_module = None  # signal to use fallback
    return _ch3mpiler_module


def get_bond_types() -> dict:
    """Get the BOND_TYPES dict from ch3mpiler, or empty dict as fallback."""
    ch3 = _get_ch3mpiler()
    if ch3 is None:
        return {}
    return getattr(ch3, 'BOND_TYPES', {})


def get_fg_table() -> dict:
    """Get the FG dict from ch3mpiler, or empty dict as fallback."""
    ch3 = _get_ch3mpiler()
    if ch3 is None:
        return {}
    return getattr(ch3, 'FG', {})


# ── BEVY OF CATALYZING PROTEINS ────────────────────────────────────
# Each entry: name, active-site residues (canonical), catalytic role,
# structural type if known, and literature reference.

CATALYZING_PROTEINS = [
    {
        "name": "lysozyme",
        "organism": "Gallus gallus (chicken egg white)",
        "pdb": "1LYZ",
        "active_site_residues": ["Glu35", "Asp52"],
        "catalytic_roles": ["acid/base (Glu35)", "nucleophile (Asp52)"],
        "reaction": "Hydrolysis of β-1,4 glycosidic bonds in peptidoglycan",
        "smiles_substrate_hint": "CC1OC(OC2C(O)C(O)C(O)OC2C(=O)O)C(O)C(O)C1O"
    },
    {
        "name": "pETase",
        "organism": "Ideonella sakaiensis",
        "pdb": "",
        "active_site_residues": ["Ser160", "Asp206", "His237"],
        "catalytic_roles": ["nucleophile (Ser160)", "base (Asp206)", "acid/base (His237)"],
        "reaction": "Hydrolysis of PET (polyethylene terephthalate) to MHET + TPA",
        "smiles_substrate_hint": "O=C(Oc1ccc(C(=O)O)cc1)c2ccc(C(=O)O)cc2"
    },
    {
        "name": "trypsin",
        "organism": "Bos taurus",
        "pdb": "",
        "active_site_residues": ["Ser195", "His57", "Asp102"],
        "catalytic_roles": ["nucleophile (Ser195)", "general base (His57)", "charge relay (Asp102)"],
        "reaction": "Hydrolysis of peptide bonds C-terminal to Arg/Lys",
        "smiles_substrate_hint": "O=C(NC(C(=O)O)Cc1ccccc1)C(N)CCCCN"
    },
    {
        "name": "carbonic_anhydrase_II",
        "organism": "Homo sapiens",
        "pdb": "",
        "active_site_residues": ["His94", "His96", "His119"],
        "catalytic_roles": ["Zn²⁺ ligand (His94)", "Zn²⁺ ligand (His96)", "Zn²⁺ ligand (His119)"],
        "reaction": "Reversible hydration of CO₂ to HCO₃⁻",
        "smiles_substrate_hint": "O=C=O"
    },
    {
        "name": "acetylcholinesterase",
        "organism": "Homo sapiens",
        "pdb": "",
        "active_site_residues": ["Ser203", "His447", "Glu334"],
        "catalytic_roles": ["nucleophile (Ser203)", "general base (His447)", "charge relay (Glu334)"],
        "reaction": "Hydrolysis of acetylcholine to choline + acetate",
        "smiles_substrate_hint": "CC(=O)OCC[N+](C)(C)C"
    },
    {
        "name": "cytochrome_P450_2D6",
        "organism": "Homo sapiens",
        "pdb": "",
        "active_site_residues": ["Cys443"],
        "catalytic_roles": ["heme axial ligand (Cys443)"],
        "reaction": "Monooxygenation of xenobiotics (C-H hydroxylation, N/O-dealkylation)",
        "smiles_substrate_hint": "COc1ccc2CCN(C)Cc2c1"
    },
    {
        "name": "ribonuclease_A",
        "organism": "Bos taurus",
        "pdb": "",
        "active_site_residues": ["His12", "His119", "Lys41"],
        "catalytic_roles": ["general base (His12)", "general acid (His119)", "stabilization (Lys41)"],
        "reaction": "Endonucleolytic cleavage of RNA at 3'-phosphate",
        "smiles_substrate_hint": "c1cn(C2CC(O)C(O)C2O)c(=O)[nH]c1=O"
    },
    {
        "name": "alcohol_dehydrogenase",
        "organism": "Saccharomyces cerevisiae",
        "pdb": "",
        "active_site_residues": ["Cys43", "His66", "Cys153"],
        "catalytic_roles": ["Zn²⁺ ligand (Cys43)", "Zn²⁺ ligand (His66)", "Zn²⁺ ligand (Cys153)"],
        "reaction": "Reversible oxidation of alcohols to aldehydes/ketones (NAD⁺ dependent)",
        "smiles_substrate_hint": "CCO"
    },
    {
        "name": "HIV1_protease",
        "organism": "Human immunodeficiency virus 1",
        "pdb": "",
        "active_site_residues": ["Asp25", "Asp25'", "Thr26", "Gly27"],
        "catalytic_roles": ["catalytic Asp dyad (Asp25/Asp25')", "flap residues (Thr26/Gly27)"],
        "reaction": "Hydrolysis of viral Gag-Pol polyprotein at specific peptide bonds",
        "smiles_substrate_hint": "CC(C)C[C@H](NC(=O)[C@H](Cc1ccccc1)NC(=O)[C@H](CCCN=C(N)N)NC(=O)[C@H](CCCN=C(N)N)N)C(=O)O"
    },
    {
        "name": "urease",
        "organism": "Canavalia ensiformis (jack bean)",
        "pdb": "",
        "active_site_residues": ["His134", "His136", "His246", "Asp360", "Lys220"],
        "catalytic_roles": ["Ni²⁺ ligands (His134, His136, His246)", "base (Asp360)", "substrate binding (Lys220)"],
        "reaction": "Hydrolysis of urea to ammonia + CO₂",
        "smiles_substrate_hint": "NC(=O)N"
    },
]


# ── AA-to-Primitive bijection (mirrors the forward pipeline) ────────

PRIMITIVE_NAMES_SHORT = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]
PRIMITIVE_FULL_NAMES = [
    "Dimensionality", "Topology", "Recognition", "Parity", "Fidelity",
    "Kinetics", "Granularity", "Coupling", "Criticality", "Chirality",
    "Stoichiometry", "Winding"
]

# Each AA has a dominant primitive (from the serpentrod bijection)
AA_TO_PRIMITIVE = {
    "Met": "D", "Trp": "T", "Cys": "R", "Tyr": "P", "Phe": "F",
    "Ile": "K", "His": "G", "Asn": "Gm", "Gln": "Ph",
    "Asp": "H", "Lys": "S", "Glu": "W"
}

# Primitive → complementary primitive pairs
COMPLEMENTARY_PAIRS = [("D","W"), ("T","H"), ("R","S"), ("P","F"), ("K","G"), ("Gm","Ph")]

# Ordinal mappings (glyph → ordinal 0-based)
# These match GLYPH_ORDINALS from the forward pipeline
GLYPH_ORDINALS = {
    "D": {"\U0001045B": 0, "\U00010468": 1, "\U0001047C": 2, "\U00010466": 3},
    "T": {"\U00010461": 0, "\U00010470": 1, "\U00010465": 2, "\U00010476": 3, "\U00010478": 4},
    "R": {"\U00010469": 0, "\U00010451": 1, "\U0001047D": 2, "\U0001047E": 3},
    "P": {"\U00010457": 0, "\U0001047F": 1, "\U0001046C": 2, "\U0001046F": 3, "\U00010479": 4},
    "F": {"\U00010471": 0, "\U0001045E": 1, "\U00010450": 2},
    "K": {"\U00010458": 0, "\U00010464": 1, "\U00010467": 2, "\U0001047A": 3, "\U0001046A": 4},
    "G": {"\U0001045A": 0, "\U00010454": 1, "\U00010472": 2},
    "Gm": {"\U0001045D": 0, "\U0001045C": 1, "\U00010460": 2, "\U00010475": 3},
    "Ph": {"\U00010462": 0, "\u2299": 1, "\U0001046E": 2, "\U0001047B": 3, "\U00010463": 4},
    "H": {"\U00010453": 0, "\U00010452": 1, "\U00010456": 2, "\U0001046B": 3},
    "S": {"\U00010459": 0, "\U00010455": 1, "\U00010473": 2},
    "W": {"\U00010477": 0, "\U00010474": 1, "\U0001046D": 2, "\U0001045F": 3}
}

ORD_TO_GLYPH = {}
for prim, mapping in GLYPH_ORDINALS.items():
    rev = {v: k for k, v in mapping.items()}
    ORD_TO_GLYPH[prim] = rev


def glyph_ord(prim: str, glyph: str) -> int:
    return GLYPH_ORDINALS.get(prim, {}).get(glyph, 0)


def ord_to_glyph(prim: str, ordinal: int) -> str:
    return ORD_TO_GLYPH.get(prim, {}).get(ordinal, "?")


def fmt_tuple(t: dict) -> str:
    """Format a 12-primitive dict as angle-bracket string."""
    return "<" + "".join(t.get(p, "?") for p in PRIMITIVE_NAMES_SHORT) + ">"


def tuple_distance_dict(t1: dict, t2: dict) -> float:
    """Weighted Euclidean distance between two 12-primitive dicts."""
    sq = 0.0
    for p in PRIMITIVE_NAMES_SHORT:
        o1 = glyph_ord(p, t1.get(p, "?"))
        o2 = glyph_ord(p, t2.get(p, "?"))
        sq += (o1 - o2) ** 2
    return math.sqrt(sq)


# ── Load ch3mpiler's BOND_TYPES and FG tables ──────────────────────

_ch3mpiler_module = None

def _get_ch3mpiler():
    """Try to load ch3mpiler; return None on failure (uses fallback tables)."""
    global _ch3mpiler_module
    if _ch3mpiler_module is not None:
        return _ch3mpiler_module
    try:
        import importlib.util
        # Fix path: compiler.py is in ch3mpiler/ subdir, not REBIS_ROOT directly
        compiler_path = REBIS_ROOT / "ch3mpiler" / "compiler.py"
        if not compiler_path.exists():
            compiler_path = REBIS_ROOT.parent / "ch3mpiler" / "compiler.py"
        if not compiler_path.exists():
            return None
        spec = importlib.util.spec_from_file_location(
            "ch3mpiler_compiler", compiler_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ch3mpiler_compiler"] = mod
        # Set __package__ so relative imports work
        mod.__package__ = "ch3mpiler"
        mod.__path__ = [str(compiler_path.parent)]
        # Insert path for relative imports
        sys.path.insert(0, str(compiler_path.parent))
        spec.loader.exec_module(mod)
        _ch3mpiler_module = mod
    except Exception as e:
        _ch3mpiler_module = None  # signal to use fallback
    return _ch3mpiler_module


def get_bond_types() -> dict:
    """Get the BOND_TYPES dict from ch3mpiler, or empty dict as fallback."""
    ch3 = _get_ch3mpiler()
    if ch3 is None:
        return {}
    return getattr(ch3, 'BOND_TYPES', {})


def get_fg_table() -> dict:
    """Get the FG dict from ch3mpiler, or empty dict as fallback."""
    ch3 = _get_ch3mpiler()
    if ch3 is None:
        return {}
    return getattr(ch3, 'FG', {})

# ── BEVY OF CATALYZING PROTEINS ────────────────────────────────────

# Shavian glyph constants for readability
D_wedge = "\U0001045B"   # 0
D_tri = "\U00010468"     # 1
D_infty = "\U0001047C"   # 2
D_odot = "\U00010466"    # 3

T_net = "\U00010461"      # 0
T_in = "\U00010470"       # 1
T_bowtie = "\U00010465"   # 2
T_otimes = "\U00010476"   # 3
T_odot = "\U00010478"     # 4

R_super = "\U00010469"    # 0
R_cat = "\U00010451"      # 1
R_dagger = "\U0001047D"   # 2
R_lr = "\U0001047E"       # 3

P_asym = "\U00010457"     # 0
P_psi = "\U0001047F"      # 1
P_pm = "\U0001046C"       # 2
P_sym = "\U0001046F"      # 3
P_pm_sym = "\U00010479"   # 4

F_ell = "\U00010471"      # 0
F_eth = "\U0001045E"      # 1
F_hbar = "\U00010450"     # 2

K_fast = "\U00010458"     # 0
K_mod = "\U00010464"      # 1
K_slow = "\U00010467"     # 2
K_MBL = "\U0001047A"      # 3
K_trap = "\U0001046A"     # 4

G_beth = "\U0001045A"     # 0
G_gimel = "\U00010454"    # 1
G_aleph = "\U00010472"    # 2

Gm_and = "\U0001045D"     # 0
Gm_or = "\U0001045C"      # 1
Gm_seq = "\U00010460"     # 2
Gm_broad = "\U00010475"   # 3

Ph_sub = "\U00010462"     # 0
Ph_c = "\u2299"           # 1 (odot)
Ph_c_complex = "\U0001046E"  # 2
Ph_EP = "\U0001047B"      # 3
Ph_super = "\U00010463"   # 4

H_memless = "\U00010453"  # 0
H_one = "\U00010452"      # 1
H_two = "\U00010456"      # 2
H_inf = "\U0001046B"      # 3

S_11 = "\U00010459"       # 0
S_nn = "\U00010455"       # 1
S_nm = "\U00010473"       # 2

W_0 = "\U00010477"        # 0
W_Z2 = "\U00010474"       # 1
W_Z = "\U0001046D"        # 2
W_NA = "\U0001045F"       # 3

CATALYZING_PROTEINS = [
    {
        "name": "lysozyme",
        "organism": "Gallus gallus (chicken egg white)",
        "pdb": "1LYZ",
        "active_site_residues": ["Glu35", "Asp52"],
        "catalytic_roles": ["acid/base (Glu35)", "nucleophile (Asp52)"],
        "reaction": "Hydrolysis of beta-1,4 glycosidic bonds in peptidoglycan",
        "smiles_substrate_hint": "CC1OC(OC2C(O)C(O)C(O)OC2C(=O)O)C(O)C(O)C1O"
    },
    {
        "name": "PETase",
        "organism": "Ideonella sakaiensis",
        "pdb": "",
        "active_site_residues": ["Ser160", "Asp206", "His237"],
        "catalytic_roles": ["nucleophile (Ser160)", "base (Asp206)", "acid/base (His237)"],
        "reaction": "Hydrolysis of PET to MHET + terephthalic acid",
        "smiles_substrate_hint": "O=C(Oc1ccc(C(=O)O)cc1)c2ccc(C(=O)O)cc2"
    },
    {
        "name": "trypsin",
        "organism": "Bos taurus",
        "pdb": "",
        "active_site_residues": ["Ser195", "His57", "Asp102"],
        "catalytic_roles": ["nucleophile (Ser195)", "general base (His57)", "charge relay (Asp102)"],
        "reaction": "Hydrolysis of peptide bonds C-terminal to Arg/Lys",
        "smiles_substrate_hint": "O=C(NC(C(=O)O)Cc1ccccc1)C(N)CCCCN"
    },
    {
        "name": "carbonic_anhydrase_II",
        "organism": "Homo sapiens",
        "pdb": "",
        "active_site_residues": ["His94", "His96", "His119"],
        "catalytic_roles": ["Zn2+ ligand (His94)", "Zn2+ ligand (His96)", "Zn2+ ligand (His119)"],
        "reaction": "Reversible hydration of CO2 to bicarbonate",
        "smiles_substrate_hint": "O=C=O"
    },
    {
        "name": "acetylcholinesterase",
        "organism": "Homo sapiens",
        "pdb": "",
        "active_site_residues": ["Ser203", "His447", "Glu334"],
        "catalytic_roles": ["nucleophile (Ser203)", "general base (His447)", "charge relay (Glu334)"],
        "reaction": "Hydrolysis of acetylcholine to choline + acetate",
        "smiles_substrate_hint": "CC(=O)OCC[N+](C)(C)C"
    },
    {
        "name": "cytochrome_P450_2D6",
        "organism": "Homo sapiens",
        "pdb": "",
        "active_site_residues": ["Cys443"],
        "catalytic_roles": ["heme axial ligand (Cys443)"],
        "reaction": "Monooxygenation (C-H hydroxylation, N/O-dealkylation)",
        "smiles_substrate_hint": "COc1ccc2CCN(C)Cc2c1"
    },
    {
        "name": "ribonuclease_A",
        "organism": "Bos taurus",
        "pdb": "",
        "active_site_residues": ["His12", "His119", "Lys41"],
        "catalytic_roles": ["general base (His12)", "general acid (His119)", "stabilization (Lys41)"],
        "reaction": "Endonucleolytic cleavage of RNA at 3-prime-phosphate",
        "smiles_substrate_hint": "c1cn(C2CC(O)C(O)C2O)c(=O)[nH]c1=O"
    },
    {
        "name": "alcohol_dehydrogenase",
        "organism": "Saccharomyces cerevisiae",
        "pdb": "",
        "active_site_residues": ["Cys43", "His66", "Cys153"],
        "catalytic_roles": ["Zn2+ ligands (Cys43, His66, Cys153)"],
        "reaction": "Reversible oxidation of alcohols to aldehydes (NAD+ dependent)",
        "smiles_substrate_hint": "CCO"
    },
    {
        "name": "HIV1_protease",
        "organism": "Human immunodeficiency virus 1",
        "pdb": "",
        "active_site_residues": ["Asp25", "Asp25_prime", "Thr26", "Gly27"],
        "catalytic_roles": ["catalytic Asp dyad (Asp25/Asp25')", "flap residues"],
        "reaction": "Hydrolysis of viral Gag-Pol polyprotein",
        "smiles_substrate_hint": "CC(C)C[C@H](NC(=O)[C@H](Cc1ccccc1)N)C(=O)O"
    },
    {
        "name": "urease",
        "organism": "Canavalia ensiformis (jack bean)",
        "pdb": "",
        "active_site_residues": ["His134", "His136", "His246", "Asp360", "Lys220"],
        "catalytic_roles": ["Ni2+ ligands", "base (Asp360)", "substrate binding (Lys220)"],
        "reaction": "Hydrolysis of urea to ammonia + CO2",
        "smiles_substrate_hint": "NC(=O)N"
    },
]

# Build lookup by name
PROTEIN_LOOKUP = {p["name"]: p for p in CATALYZING_PROTEINS}

# ── CORE PIPELINE FUNCTIONS ─────────────────────────────────────────

def complement_type(site_type: dict) -> dict:
    """Structural complement of a catalytic site type → ligand type.
    
    This is the same function as complement_type_v2 in the forward pipeline.
    For each complementary pair (A,B), applies the inverse mapping:
      ligand[A] = INVERSE(site[B])
      ligand[B] = INVERSE(site[A])
    """
    ligand = {}
    for prim_a, prim_b in COMPLEMENTARY_PAIRS:
        a_max = len(GLYPH_ORDINALS.get(prim_a, {})) - 1
        b_max = len(GLYPH_ORDINALS.get(prim_b, {})) - 1
        
        site_a = glyph_ord(prim_a, site_type.get(prim_a, "?"))
        site_b = glyph_ord(prim_b, site_type.get(prim_b, "?"))
        
        inv_a = a_max - site_a
        inv_b = b_max - site_b
        
        if a_max > 0:
            ligand[prim_b] = ord_to_glyph(prim_b, min(b_max, max(0, round(inv_a / a_max * b_max))))
        else:
            ligand[prim_b] = ord_to_glyph(prim_b, b_max)
        
        if b_max > 0:
            ligand[prim_a] = ord_to_glyph(prim_a, min(a_max, max(0, round(inv_b / b_max * a_max))))
        else:
            ligand[prim_a] = ord_to_glyph(prim_a, a_max)
    
    return ligand


def encode_site_from_residues(residues: list) -> dict:
    """Encode active site residues as a 12-primitive structural type.

    Maps each catalytic residue to its dominant primitive, then scales
    each primitive's ordinal proportionally to how many residues map to it.

    Tensor semantics: max on most primitives (more residues → higher ordinal),
    min on P and F (more residues → more constrained → lower fidelity/parity).

    Args:
        residues: List of residue strings, e.g. ["ARG105", "Glu", "Asp"]

    Returns:
        12-primitive dict, or None if no residues could be parsed
    """
    if not residues:
        return None

    import re as _re

    # Extended AA_TO_PRIMITIVE with all 20 standard AAs
    _ALL_AA_PRIMITIVE = dict(AA_TO_PRIMITIVE)
    _ALL_AA_PRIMITIVE.update({
        "Ala": "G", "Gly": "G", "Val": "K", "Leu": "K", "Ile": "K",
        "Pro": "T", "Ser": "R", "Thr": "R", "Arg": "S", "Lys": "S"
    })

    # Parse residues to clean 3-letter codes
    clean_aas = []
    aa_map_1l = {"S": "Ser", "D": "Asp", "H": "His", "E": "Glu",
                "K": "Lys", "C": "Cys", "Y": "Tyr", "F": "Phe",
                "I": "Ile", "N": "Asn", "Q": "Gln", "W": "Trp",
                "M": "Met", "G": "Gly", "A": "Ala", "V": "Val",
                "L": "Leu", "P": "Pro", "T": "Thr", "R": "Arg"}

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
            if code1 in aa_map_1l:
                clean_aas.append(aa_map_1l[code1])

    if not clean_aas:
        return None

    # Count residues per primitive
    prim_counts = {p: 0 for p in PRIMITIVE_NAMES_SHORT}
    for aa in clean_aas:
        prim = _ALL_AA_PRIMITIVE.get(aa)
        if prim:
            prim_counts[prim] += 1

    # Scale each primitive's ordinal proportionally to count
    # Non-P/F primitives (max semantics):
    #   0 residues → ordinal 0 (minimum, no contribution)
    #   N residues → min(N, max_ordinal)
    # P and F primitives (tensor-min semantics):
    #   0 residues → ordinal max_ord (no constraint → highest fidelity/parity)
    #   N residues → max(0, max_ord - N) (more residues → more constrained)
    result = {}
    for p in PRIMITIVE_NAMES_SHORT:
        max_ord = len(GLYPH_ORDINALS[p]) - 1
        count = prim_counts.get(p, 0)

        if p in ("P", "F"):
            # Tensor-min: more residues → lower ordinal
            # 0 residues = unconstrained = max ordinal
            if count == 0:
                result[p] = ord_to_glyph(p, max_ord)
            else:
                result[p] = ord_to_glyph(p, max(0, max_ord - min(count, max_ord)))
        elif count == 0:
            # Non-P/F, no residues: minimum ordinal
            result[p] = ord_to_glyph(p, 0)
        else:
            # Non-P/F, has residues: ordinal proportional to count
            result[p] = ord_to_glyph(p, min(count, max_ord))

    return result

def closest_bond_type(ligand_type: dict) -> Tuple[str, dict, float]:
    """Find the bond type whose structural type is closest to the ligand type.
    
    Returns:
        (bond_name, bond_tuple, distance)
    """
    ch3 = _get_ch3mpiler()
    bond_types = {}
    if ch3 is not None:
        bond_types = getattr(ch3, 'BOND_TYPES', {})
    
    if not bond_types:
        # FIRST PRINCIPLES: load imscribed bond types from catalog
        bond_types = _get_catalog_tuples_by_name(_CATALOG_BOND_NAMES)
        if not bond_types:
            # Absolute last resort: minimal fallback (only sigma_single_bond)
            bond_types = {
                "sigma_single": {"D": D_wedge, "T": T_net, "R": R_cat, "P": P_asym,
                               "F": F_eth, "K": K_mod, "G": G_beth, "Gm": Gm_and,
                               "Ph": Ph_sub, "H": H_memless, "S": S_11, "W": W_0},
            }

    best_name = None
    best_tuple = None
    best_dist = float('inf')
    
    for name, bt in bond_types.items():
        if not isinstance(bt, dict):
            continue
        # Extract 12-primitive fields if present
        bt_tuple = {}
        for p in PRIMITIVE_NAMES_SHORT:
            if p in bt:
                bt_tuple[p] = bt[p]
            elif {"D": "Ð", "T": "Þ", "R": "Ř", "P": "Φ", "F": "ƒ", 
                  "K": "Ç", "G": "Γ", "Gm": "ɢ", "Ph": "⊙", 
                  "H": "Ħ", "S": "Σ", "W": "Ω"}.get(p, "") in bt:
                key = {"D": "Ð", "T": "Þ", "R": "Ř", "P": "Φ", "F": "ƒ", 
                       "K": "Ç", "G": "Γ", "Gm": "ɢ", "Ph": "⊙", 
                       "H": "Ħ", "S": "Σ", "W": "Ω"}[p]
                bt_tuple[p] = bt[key]
            else:
                continue
        
        if len(bt_tuple) < 12:
            continue
        
        dist = tuple_distance_dict(ligand_type, bt_tuple)
        if dist < best_dist:
            best_dist = dist
            best_name = name
            best_tuple = bt_tuple
    
    return best_name, best_tuple, best_dist


def closest_fg_pair(ligand_type: dict, bond_type: dict = None) -> Tuple[list, dict, float]:
    """Find the closest FG pair to the residual (ligand minus bond) type.
    
    If bond_type is given, compute residual:
      residual = ligand_type "minus" bond_type (inverse of fuse_reaction_types)
    
    Returns:
        ([fg1_name, fg2_name], fused_fg_tuple, distance)
    """
    ch3 = _get_ch3mpiler()
    fg_table = {}
    if ch3 is not None:
        fg_table = getattr(ch3, 'FG', {})
    
    if not fg_table:
        # FIRST PRINCIPLES: load imscribed FGs from catalog
        fg_table = _get_catalog_tuples_by_name(_CATALOG_FG_NAMES)
        if not fg_table:
            # Absolute last resort: minimal fallback
            fg_table = {
                "amine": {"D": D_wedge, "T": T_net, "R": R_cat, "P": P_asym,
                         "F": F_hbar, "K": K_fast, "G": G_beth, "Gm": Gm_and,
                         "Ph": Ph_sub, "H": H_memless, "S": S_11, "W": W_0},
            }

    # Try all FG pairs (including single FGs and pairs)
    best_pair = None
    best_fused = None
    best_dist = float('inf')
    
    fg_names = list(fg_table.keys())
    
    # Try single FGs first
    for fg1 in fg_names:
        fg1_t = fg_table[fg1]
        if not isinstance(fg1_t, dict):
            continue
        fg1_tup = {}
        for p in PRIMITIVE_NAMES_SHORT:
            if p in fg1_t:
                fg1_tup[p] = fg1_t[p]
            else:
                continue
        if len(fg1_tup) < 12:
            continue
        
        dist = tuple_distance_dict(ligand_type, fg1_tup)
        if dist < best_dist:
            best_dist = dist
            best_pair = [fg1]
            best_fused = fg1_tup
    
    # Try FG pairs (tensor product)
    for fg1 in fg_names:
        for fg2 in fg_names:
            if fg1 >= fg2:
                continue
            fg1_t = fg_table.get(fg1, {})
            fg2_t = fg_table.get(fg2, {})
            if not isinstance(fg1_t, dict) or not isinstance(fg2_t, dict):
                continue
            
            # Tensor product: max on most, min on P and F
            fused = {}
            for p in PRIMITIVE_NAMES_SHORT:
                v1 = fg1_t.get(p) if p in fg1_t else fg1_t.get({"D":"Ð","T":"Þ","R":"Ř","P":"Φ","F":"ƒ","K":"Ç","G":"Γ","Gm":"ɢ","Ph":"⊙","H":"Ħ","S":"Σ","W":"Ω"}[p], "")
                v2 = fg2_t.get(p) if p in fg2_t else fg2_t.get({"D":"Ð","T":"Þ","R":"Ř","P":"Φ","F":"ƒ","K":"Ç","G":"Γ","Gm":"ɢ","Ph":"⊙","H":"Ħ","S":"Σ","W":"Ω"}[p], "")
                o1 = glyph_ord(p, v1) if v1 else 0
                o2 = glyph_ord(p, v2) if v2 else 0
                fused[p] = ord_to_glyph(p, min(o1, o2) if p in ("P", "F") else max(o1, o2))
            
            dist = tuple_distance_dict(ligand_type, fused)
            if dist < best_dist:
                best_dist = dist
                best_pair = [fg1, fg2]
                best_fused = fused
    
    return best_pair, best_fused, best_dist

# ── SMILES GENERATION ───────────────────────────────────────────────

# SMILES patterns for functional groups (scaffold fragments)
FG_SMILES_PATTERNS = {
    "amine": "C(N)",
    "carbonyl": "C(=O)",
    "alcohol": "CO",
    "ether": "COC",
    "carboxylic_acid": "C(=O)O",
    "ester": "C(=O)OC",
    "amide": "C(=O)N",
    "aromatic_ring": "c1ccccc1",
    "phenol": "c1ccc(O)cc1",
    "alkene": "C=C",
    "alkyne": "C#C",
    "nitrile": "C#N",
    "halide": "CF",
    "thiol": "CS",
    "ketone": "CC(=O)C",
    "aldehyde": "C(=O)C",
    "nitro": "C[N+](=O)[O-]",
    "imine": "C=NC",
    "lactam": "O=C1CCCN1",
    "phosphate": "COP(=O)(O)O",
    "sulfate": "COS(=O)(=O)O",
    "sulfide": "CSC",
    "oxetane": "C1COC1",
    "beta_lactam": "O=C1CCN1"
}

# Bond → SMILES connector patterns
BOND_SMILES_PATTERNS = {
    "sigma_single": "-",
    "pi_bond": "=",
    "double_bond": "=",
    "triple_bond": "#",
    "carbonyl": "=O",
    "co_sigma": "O",
    "cn_sigma": "N",
    "amide_link": "C(=O)N",
    "ester_link": "C(=O)O",
    "aromatic": "c",
    "ether_link": "O",
    "strain_release": "-",
    "hydrogen_bond": "-"
}


def generate_ligand_smiles(bond_name: str, fg_names: list, 
                           substrate_hint: str = "") -> list:
    """Generate de-novo SMILES ligands from bond + FG decomposition.
    
    Uses first-principles molecular assembly:
    1. Start with the bond type as the reaction center
    2. Attach FGs as substituents
    3. Vary R-group substituents to create a ligand family
    4. Validate with RDKit
    
    Returns:
        List of (smiles, logP, MW, score) tuples
    """
    candidates = []
    
    # Strategy 1: Scaffold from FG SMILES patterns
    if fg_names:
        # Build a scaffold combining the FGs
        fg_smiles_list = []
        for fg in fg_names[:3]:  # max 3 FGs
            if fg in FG_SMILES_PATTERNS:
                fg_smiles_list.append(FG_SMILES_PATTERNS[fg])
        
        if fg_smiles_list:
            # Connect FGs via the bond type
            connector = BOND_SMILES_PATTERNS.get(bond_name, "-")
            scaffold = connector.join(fg_smiles_list)
            candidates.append((scaffold, "fg_scaffold"))
            
            # Try with methyl substitution
            methyl_variant = scaffold.replace("C(", "C(C)(")
            candidates.append((methyl_variant, "methylated"))
    
    # Strategy 2: Use the substrate hint if available
    if substrate_hint:
        try:
            mol = Chem.MolFromSmiles(substrate_hint)
            if mol is not None:
                # Generate analogs by adding/subtracting functional groups
                base_smi = Chem.MolToSmiles(mol)
                candidates.append((base_smi, "substrate_analog"))
                
                # Add ethyl extension
                try:
                    from rdkit.Chem import AllChem
                    # Ethyl extension on available positions
                    extended = Chem.RWMol(mol)
                    extended.AddAtom(Chem.Atom(6))  # C
                    extended.AddAtom(Chem.Atom(6))  # C
                    ei_smi = Chem.MolToSmiles(extended)
                    candidates.append((ei_smi, "extended_chain"))
                except:
                    pass
        except:
            pass
    
    # Strategy 3: First-principles de-novo construction
    # Use the bond type to determine scaffold geometry
    if bond_name in ("amide_link", "carbonyl"):
        # Amide-like scaffold with R-groups
        for r1 in ["C", "CC", "CCC", "c1ccccc1"]:
            for r2 in ["N", "NC", "NCC"]:
                smi = f"{r1}C(=O){r2}"
                candidates.append((smi, f"amide_variant_{r1}_{r2}"))
    
    elif bond_name in ("ester_link",):
        for r1 in ["C", "CC", "c1ccccc1"]:
            for r2 in ["O", "OC", "OCC"]:
                smi = f"{r1}C(=O){r2}"
                candidates.append((smi, f"ester_variant_{r1}_{r2}"))
    
    elif bond_name == "aromatic":
        for sub in ["O", "N", "C(=O)O", "C(=O)N"]:
            smi = f"c1ccccc1{sub}"
            candidates.append((smi, f"aromatic_{sub}"))
    
    elif bond_name in ("sigma_single", "co_sigma", "ether_link"):
        # Simple chain
        for chain_len in [1, 2, 3, 4]:
            chain = "C" * chain_len
            if fg_names:
                fg_tag = fg_names[0]
                if fg_tag in FG_SMILES_PATTERNS:
                    smi = f"{FG_SMILES_PATTERNS[fg_tag]}{chain}"
                    candidates.append((smi, f"chain_{chain_len}"))
    
    # Validate and deduplicate
    validated = []
    seen = set()
    for smi, method in candidates:
        try:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                continue
            canon = Chem.MolToSmiles(mol)
            if canon in seen:
                continue
            seen.add(canon)
            
            # Compute properties
            logp = Descriptors.MolLogP(mol)
            mw = Descriptors.MolWt(mol)
            heavy = mol.GetNumHeavyAtoms()
            
            validated.append({
                "smiles": canon,
                "method": method,
                "logP": round(logp, 2),
                "MW": round(mw, 1),
                "heavy_atoms": heavy,
                "valid": True
            })
        except Exception as e:
            pass
    
    # Sort by heavy atom count (reasonable size first)
    validated.sort(key=lambda x: x["heavy_atoms"])
    
    return validated


def decompose_and_generate(site_type: dict, substrate_hint: str = "") -> dict:
    """Full pipeline: complement site type, decompose, generate ligands.
    
    Args:
        site_type: 12-primitive dict of the active site
        substrate_hint: Optional SMILES of known substrate
    
    Returns:
        Dict with full analysis
    """
    # Step 1: Complement → ligand type
    ligand_type = complement_type(site_type)
    
    # Step 2: Find closest bond type
    bond_name, bond_tuple, bond_dist = closest_bond_type(ligand_type)
    
    # Step 3: Find closest FG pair
    fg_names, fg_tuple, fg_dist = closest_fg_pair(ligand_type, bond_tuple)
    
    # Step 4: Generate ligands
    ligands = generate_ligand_smiles(bond_name or "sigma_single", 
                                      fg_names or ["amine"],
                                      substrate_hint)
    
    return {
        "ligand_type": ligand_type,
        "ligand_type_fmt": fmt_tuple(ligand_type),
        "closest_bond": bond_name,
        "bond_distance": round(bond_dist, 3) if bond_dist else None,
        "closest_fgs": fg_names,
        "fg_distance": round(fg_dist, 3) if fg_dist else None,
        "ligand_candidates": ligands
    }


# ── BEVY ANALYSIS ───────────────────────────────────────────────────

def analyze_bevy(protein_names: list = None) -> list:
    """Run the full reverse pipeline on a bevy of catalyzing proteins.
    
    Args:
        protein_names: List of protein names from CATALYZING_PROTEINS.
                       If None, runs on ALL.
    
    Returns:
        List of analysis results per protein
    """
    if protein_names:
        proteins = [PROTEIN_LOOKUP[n] for n in protein_names if n in PROTEIN_LOOKUP]
        if not proteins:
            raise ValueError(f"No known proteins: {protein_names}. "
                           f"Available: {list(PROTEIN_LOOKUP.keys())}")
    else:
        proteins = CATALYZING_PROTEINS
    
    results = []
    for protein in proteins:
        name = protein["name"]
        # FIRST PRINCIPLES: compute site tuple from residues
        site_type = encode_site_from_residues(protein["active_site_residues"])
        substrate = protein.get("smiles_substrate_hint", "")
        
        if not site_type:
            continue
        
        result = decompose_and_generate(site_type, substrate)
        result["protein_name"] = name
        result["organism"] = protein["organism"]
        result["reaction"] = protein["reaction"]
        result["active_site"] = protein["active_site_residues"]
        result["site_type"] = site_type
        result["site_type_fmt"] = fmt_tuple(site_type)
        results.append(result)
    
    return results


# ── MAIN CLI ─────────────────────────────────────────────────────────

# ── IMPROVED ENGINE INTEGRATION ─────────────────────────────────────
# This replaces the template-based generation with RDKit fragment-based
# enumeration and structural scoring.

_IMPROVED_IMPORTED = False
_IMPROVED_MODULE = None

def _get_improved():
    """Lazy-import the improved generation engine."""
    global _IMPROVED_IMPORTED, _IMPROVED_MODULE
    if _IMPROVED_IMPORTED:
        return _IMPROVED_MODULE
    try:
        sys.path.insert(0, str(BASE))
        from rhr_p4rky import ligand_improvements as limprov
        _IMPROVED_MODULE = limprov
        _IMPROVED_IMPORTED = True
        return limprov
    except Exception as e:
        debug_line(f"Improved engine not available: {e}")
        _IMPROVED_IMPORTED = True  # don't retry
        return None


def analyze_bevy_improved(protein_names: list = None, max_candidates: int = 10) -> list:
    """Run the IMPROVED reverse pipeline on the bevy.
    
    Uses enzyme structural type → bond type → FG estimation → fragment-based
    molecular enumeration → structural scoring.
    """
    limprov = _get_improved()
    if limprov is None:
        warning_line("Improved engine not available. Falling back to default.")
        return analyze_bevy(protein_names)
    
    if protein_names:
        proteins = [PROTEIN_LOOKUP[n] for n in protein_names if n in PROTEIN_LOOKUP]
    else:
        proteins = CATALYZING_PROTEINS
    
    results = []
    for p in proteins:
        name = p["name"]
        # FIRST PRINCIPLES: compute site tuple from residues
        site_type = encode_site_from_residues(p["active_site_residues"])
        substrate = p.get("smiles_substrate_hint", "")
        
        # Try heterocycle/polycyclic engine first, fall back to fragment-based
        try:
            from rhr_p4rky.ligand_heterocycles import generate_hybrid_ligands
            candidates = generate_hybrid_ligands(
                site_type=site_type,
                substrate_hint=substrate,
                max_candidates=max_candidates,
                heterocycle_fraction=0.65,
            )
        except Exception:
            candidates = limprov.generate_from_enzyme_type(
                site_type=site_type,
                substrate_hint=substrate,
                max_candidates=max_candidates,
            )
        
        # Also get the ligand type via complement for reference
        ligand_type = limprov._complement_type(site_type)
        bond_name = limprov._estimate_bond_from_site_type(site_type)
        fg_names = limprov._estimate_fgs_from_site_type(site_type, bond_name)
        
        results.append({
            "protein_name": name,
            "organism": p["organism"],
            "reaction": p["reaction"],
            "active_site": p["active_site_residues"],
            "site_type": site_type,
            "site_type_fmt": fmt_tuple(site_type),
            "ligand_type": ligand_type,
            "ligand_type_fmt": fmt_tuple(ligand_type),
            "estimated_bond": bond_name,
            "estimated_fgs": fg_names,
            "n_candidates": len(candidates),
            "ligand_candidates": candidates
        })
    
    return results


def main():
    """CLI entry point for the reverse pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ligand-from-active-site: Generate de-novo ligands from active site imscriptions"
    )
    parser.add_argument("action", nargs="?", default="list",
                        choices=["list", "analyze", "single", "all", "improved", "enrich"],
                        help="Action: list=show bevy, analyze=run pipeline on bevy, single=one protein, all=full bevy")
    parser.add_argument("--protein", "-p", type=str, default="",
                        help="Protein name for single/analyze mode")
    parser.add_argument("--json", "-j", action="store_true",
                        help="JSON output")
    parser.add_argument("--output", "-o", type=str, default="",
                        help="Save results to JSON file")
    parser.add_argument("--max", "-m", type=int, default=10,
                        help="Max candidates per protein (improved/enrich mode)")
    
    args = parser.parse_args()
    
    if args.action == "list":
        info_line("=" * 72)
        info_line("  BEVY OF CATALYZING PROTEINS")
        info_line("=" * 72)
        for p in CATALYZING_PROTEINS:
            st = p.get("structural_type", {})
            info_line(f"\n  {p['name']:30s} ({p['organism']})")
            info_line(f"  Active site:       {', '.join(p['active_site_residues'])}")
            info_line(f"  Reaction:          {p['reaction']}")
            info_line(f"  Structural type:   {fmt_tuple(st)}")
        info_line("\n" + "-" * 72)
        info_line(f"  Total: {len(CATALYZING_PROTEINS)} catalyzing proteins")
        return 0
    
    elif args.action in ("single", "analyze"):
        if not args.protein:
            error_line("Error: --protein is required for single/analyze mode")
            info_line(f"Available: {list(PROTEIN_LOOKUP.keys())}")
            return 1
        if args.protein not in PROTEIN_LOOKUP:
            error_line(f"Error: unknown protein '{args.protein}'")
            info_line(f"Available: {list(PROTEIN_LOOKUP.keys())}")
            return 1
        results = analyze_bevy([args.protein])
    
    elif args.action == "all":
        results = analyze_bevy()
    
    elif args.action in ("improved", "enrich"):
        if args.protein:
            if args.protein not in PROTEIN_LOOKUP:
                error_line(f"Error: unknown protein '{args.protein}'")
                info_line(f"Available: {list(PROTEIN_LOOKUP.keys())}")
                return 1
            results = analyze_bevy_improved([args.protein], max_candidates=args.max)
        else:
            results = analyze_bevy_improved(max_candidates=args.max)
    
    else:
        results = analyze_bevy()
    
    # Display results
    for r in results:
        info_line("=" * 72)
        info_line(f"  PROTEIN: {r['protein_name']}")
        info_line(f"  Organism: {r['organism']}")
        info_line(f"  Reaction: {r['reaction']}")
        info_line(f"  Active site: {', '.join(r['active_site'])}")
        info_line(f"  Site type:   {r['site_type_fmt']}")
        if 'estimated_bond' in r:
            info_line(f"  Estimated bond: {r['estimated_bond']}")
            info_line(f"  Estimated FGs:  {r['estimated_fgs']}")
            info_line(f"  Ligand type:    {r['ligand_type_fmt']}")
        else:
            info_line(f"  Ligand type: {r['ligand_type_fmt']}")
            info_line(f"  Closest bond: {r['closest_bond']} (d={r['bond_distance']})")
            info_line(f"  Closest FGs:  {r['closest_fgs']} (d={r['fg_distance']})")
        info_line("-" * 72)
        
        if r.get("ligand_candidates"):
            label = "DE-NOVO LIGAND CANDIDATES"
            if 'n_candidates' in r:
                label += f" ({r['n_candidates']} total, showing {len(r['ligand_candidates'])})"
            else:
                label += f" ({len(r['ligand_candidates'])})"
            info_line(f"  {label}:")
            for l in r["ligand_candidates"]:
                score_str = f" comp={l['composite_score']:.3f}" if 'composite_score' in l else ""
                extra = f" HBD={l.get('HBD','?')} HBA={l.get('HBA','?')} rings={l.get('rings','?')}" if 'composite_score' in l else ""
                info_line(f"    [{l['method']:20s}] {l['smiles']:40s}  "
                         f"logP={l['logP']:6.2f}  MW={l['MW']:7.1f}{score_str}")
        else:
            warning_line("  No de-novo ligand candidates generated")
        print()
    
    if args.output and results:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        info_line(f"Results saved to: {args.output}")


if __name__ == "__main__":
    main()
