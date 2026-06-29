#!/usr/bin/env python3
"""
compound_imasm.py — Compound-to-IMASM Arrangement Encoder

Maps molecular structures (SMILES) to 8-token IMASM token arrangements
using functional group detection, bond topology, and ring system analysis.

The resulting arrangement produces a StructuralFingerprint that can be
mapped to an IG 12-primitive tuple via ig_bridge.py, registering the
compound as a first-class structural type in the Imscribing Grammar.

Token → Functional Group Role mapping:
  VINIT (0)  — Core scaffold / ring system anchor
  TANCH (1)  — Terminal group (methyl, halogen, end-cap)
  AFWD (2)  — Forward-directed reactive site (electrophile)
  AREV (3)  — Reverse-directed reactive site (nucleophile)
  CLINK (4) — Linker / bridge between fragments
  IMSCRIB(5) — Self-imscribing system (aromatic rings, conjugated)
  FSPLIT (6) — Disconnection point (labile bond, leaving group)
  FFUSE  (7) — Bond formation site (coupling partner)
  EVALT  (8) — Acidic functional group (proton donor)
  EVALF  (9) — Basic functional group (proton acceptor)
  ENGAGR(10) — Ambident / resonance-stabilized site
  IFIX  (11) — Irreversible group (protecting group, stable bond)

Author: Lando⊗⊙perator
"""
import sys, json, re
from pathlib import Path
from collections import Counter
from typing import Tuple, List, Dict, Optional
from shared.rich_output import *

try:
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False
    info_line("Warning: RDKit not available. Install with: uv pip install rdkit-pypi")

# ── IMASM Token definitions (mirrors arranger.py) ──
VINIT, TANCH, AFWD, AREV, CLINK = 0, 1, 2, 3, 4
IMSCRIB, FSPLIT, FFUSE = 5, 6, 7
EVALT, EVALF, ENGAGR, IFIX = 8, 9, 10, 11

TOKEN_NAMES = {
    0: "VINIT", 1: "TANCH", 2: "AFWD", 3: "AREV",
    4: "CLINK", 5: "IMSCRIB", 6: "FSPLIT", 7: "FFUSE",
    8: "EVALT", 9: "EVALF", 10: "ENGAGR", 11: "IFIX",
}

# ── SMARTS → IMASM Token mapping ──
# Functional group SMARTS patterns map to one of the 12 IMASM tokens
# based on the group's chemical role.
FG_TOKEN_MAP = {
    # VINIT (0) — Core scaffolds and ring systems
    "benzene": VINIT,
    "aromatic": VINIT,
    "bridged_rings": VINIT,
    "annelated_rings": VINIT,
    "barbiturate": VINIT,
    "beta_lactam": VINIT,

    # TANCH (1) — Terminal groups
    "alkyl_bromide": TANCH,
    "alkyl_chloride": TANCH,
    "alkyl_fluoride": TANCH,
    "alkyl_iodide": TANCH,
    "alkyl_halide": TANCH,
    "aryl_bromide": TANCH,
    "aryl_chloride": TANCH,
    "aryl_fluoride": TANCH,
    "aryl_iodide": TANCH,
    "alkyl_thiol": TANCH,
    "aryl_thiol": TANCH,

    # AFWD (2) — Forward-directed reactive sites (electrophiles)
    "aldehyde": AFWD,
    "carbonyl": AFWD,
    "Michael_acceptor": AFWD,
    "carboxylic_ester": AFWD,
    "carbonic_acid_diester": AFWD,
    "acyl_halide": AFWD,
    "acid_anhydride": AFWD,
    "isocyanate": AFWD,
    "ketene": AFWD,
    "sulfonyl_halide": AFWD,
    "epoxide": AFWD,
    "aziridine": AFWD,
    "NH_aziridine": AFWD,

    # AREV (3) — Reverse-directed sites (nucleophiles)
    "alcohol": AREV,
    "amine": AREV,
    "aniline": AREV,
    "primary_amine": AREV,
    "secondary_amine": AREV,
    "tertiary_amine": AREV,
    "alkyl_thiol": AREV,
    "aryl_thiol": AREV,
    "hydrazine": AREV,
    "hydroxylamine": AREV,

    # CLINK (4) — Linkers / bridges
    "alkene": CLINK,
    "alkyne": CLINK,
    "allene": CLINK,
    "azo": CLINK,
    "carbodiimide": CLINK,
    "disulfide": CLINK,
    "ether": CLINK,
    "alkyl_aryl_ether": CLINK,
    "thioether": CLINK,
    "alkyl_aryl_thioether": CLINK,

    # IMSCRIB (5) — Self-imscribing systems
    "aromatic_NH": IMSCRIB,
    "aromatic_nitrogen": IMSCRIB,
    "heteroaromatic": IMSCRIB,
    "conjugated_diene": IMSCRIB,
    "enone": IMSCRIB,

    # FSPLIT (6) — Disconnection points
    "carboxylic_acid": FSPLIT,
    "aliphatic_carboxylic_acid": FSPLIT,
    "aromatic_carboxylic_acid": FSPLIT,
    "carboxylic_amide": FSPLIT,
    "carboxylic_imide": FSPLIT,
    "lactam": FSPLIT,
    "lactone": FSPLIT,
    "acetal": FSPLIT,
    "hemiacetal": FSPLIT,
    "boronic_acid": FSPLIT,
    "boronic_ester": FSPLIT,

    # FFUSE (7) — Bond formation sites
    "alkene": FFUSE,  # alkene can also be bond formation via Heck, metathesis
    "alkyne": FFUSE,  # alkyne for Sonogashira, click chemistry
    "azide": FFUSE,   # click chemistry
    "boronic_acid": FFUSE,  # Suzuki coupling
    "aryl_halide": FFUSE,   # cross-coupling
    "aryl_bromide": FFUSE,
    "aryl_chloride": FFUSE,
    "aryl_iodide": FFUSE,

    # EVALT (8) — Acidic functional groups
    "carboxylic_acid": EVALT,
    "aliphatic_carboxylic_acid": EVALT,
    "aromatic_carboxylic_acid": EVALT,
    "sulfonic_acid": EVALT,
    "sulfinic_acid": EVALT,
    "phosphonic_acid": EVALT,
    "phosphoric_acid": EVALT,
    "boric_acid": EVALT,
    "phenol": EVALT,
    "enol": EVALT,
    "alpha_hydroxy_acid": EVALT,
    "alpha_amino_acid": EVALT,
    "tetrazole": EVALT,
    "sulfonamide": EVALT,
    "imide": EVALT,
    "barbiturate": EVALT,
    "carbonic_acid_monoester": EVALT,

    # EVALF (9) — Basic functional groups
    "amine": EVALF,
    "primary_amine": EVALF,
    "secondary_amine": EVALF,
    "tertiary_amine": EVALF,
    "aniline": EVALF,
    "amidine": EVALF,
    "guanidine": EVALF,
    "imidazole": EVALF,
    "pyridine": EVALF,
    "aromatic_nitrogen": EVALF,
    "hydrazine": EVALF,
    "aziridine": EVALF,
    "NH_aziridine": EVALF,
    "hydroxylamine": EVALF,

    # ENGAGR (10) — Ambident / resonance-stabilized
    "enolate": ENGAGR,
    "enamine": ENGAGR,
    "nitrile": ENGAGR,
    "nitro": ENGAGR,
    "azo": ENGAGR,
    "azide": ENGAGR,
    "isocyanate": ENGAGR,
    "enone": ENGAGR,
    "Michael_acceptor": ENGAGR,
    "carboxylate": ENGAGR,
    "phenoxide": ENGAGR,
    "sulfoxide": ENGAGR,
    "sulfone": ENGAGR,
    "nitroso": ENGAGR,
    "diazo": ENGAGR,

    # IFIX (11) — Irreversible groups
    "protecting_group": IFIX,
    "silyl_ether": IFIX,
    "acetal": IFIX,
    "carbamate": IFIX,
    "alkyl_carbamate": IFIX,
    "benzyl": IFIX,
    "trityl": IFIX,
    "f_moc": IFIX,
    "b_o_c": IFIX,
    "c_b_z": IFIX,
    "t_m_s": IFIX,
    "t_b_d_m_s": IFIX,
    "p_m_b": IFIX,
    "m_m_t": IFIX,
}

# Multiple mappings per token for priority ordering
TOKEN_FG_PRIORITY = {
    VINIT:  {"benzene", "aromatic", "bridged_rings", "annelated_rings",
             "barbiturate", "beta_lactam", "heteroaromatic"},
    TANCH:  {"alkyl_halide", "aryl_halide", "alkyl_bromide", "alkyl_chloride",
             "alkyl_fluoride", "alkyl_iodide", "aryl_bromide", "aryl_chloride",
             "aryl_fluoride", "aryl_iodide", "alkyl_thiol", "aryl_thiol"},
    AFWD:   {"aldehyde", "carbonyl", "Michael_acceptor", "carboxylic_ester",
             "acyl_halide", "acid_anhydride", "isocyanate", "ketene",
             "epoxide", "aziridine"},
    AREV:   {"alcohol", "amine", "aniline", "primary_amine", "secondary_amine",
             "tertiary_amine"},
    CLINK:  {"alkene", "alkyne", "allene", "azo", "carbodiimide", "disulfide",
             "ether", "thioether"},
    IMSCRIB: {"aromatic_NH", "aromatic_nitrogen", "heteroaromatic",
              "conjugated_diene", "enone"},
    FSPLIT: {"carboxylic_acid", "carboxylic_amide", "carboxylic_imide",
             "lactam", "lactone", "acetal", "hemiacetal", "boronic_acid",
             "boronic_ester"},
    FFUSE:  {"azide", "alkyne", "boronic_acid", "aryl_halide",
             "aryl_bromide", "aryl_chloride", "aryl_iodide"},
    EVALT:  {"carboxylic_acid", "sulfonic_acid", "sulfinic_acid",
             "phosphonic_acid", "boric_acid", "phenol", "enol",
             "tetrazole", "sulfonamide", "imide"},
    EVALF:  {"amine", "primary_amine", "secondary_amine", "tertiary_amine",
             "aniline", "amidine", "guanidine", "imidazole", "pyridine"},
    ENGAGR: {"enolate", "enamine", "nitrile", "nitro", "azide", "enone",
             "Michael_acceptor", "sulfoxide", "sulfone", "nitroso", "diazo"},
    IFIX:   {"silyl_ether", "carbamate", "alkyl_carbamate", "benzyl",
             "trityl", "f_moc", "b_o_c", "c_b_z", "t_m_s", "t_b_d_m_s"},
}

# Reverse lookup: token → list of FG names
TOKEN_TO_FG_NAMES: Dict[int, List[str]] = {}
for fg_name, tok in FG_TOKEN_MAP.items():
    TOKEN_TO_FG_NAMES.setdefault(tok, []).append(fg_name)


# ── Token weighting: which token dominates when multiple patterns match ──
# Higher number = more dominant (overrides lower weights in arrangement construction)
TOKEN_WEIGHTS = {
    VINIT:   10,   # Core scaffold determines identity
    IMSCRIB:  9,   # Self-imscribing rings are defining
    FSPLIT:   8,   # Disconnection points are structurally important
    FFUSE:    8,   # Bond formation sites are key
    CLINK:    7,   # Linkers mediate connectivity
    AFWD:     6,   # Forward reactivity
    AREV:     6,   # Reverse reactivity
    ENGAGR:   6,   # Ambident sites span multiple reactivities
    EVALT:    5,   # Acidity is secondary
    EVALF:    5,   # Basicity is secondary
    TANCH:    4,   # Terminals are low-weight
    IFIX:     3,   # Protecting groups are temporary
}


def _unique(arr):
    """Deduplicate while preserving order."""
    seen = set()
    result = []
    for x in arr:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result


def _pad_to_8(arr: List[int]) -> Tuple[int, ...]:
    """Pad or truncate to exactly 8 tokens."""
    if len(arr) >= 8:
        return tuple(arr[:8])
    # Pad with CLINK (neutral linker) or repeated last token
    pad_token = CLINK
    while len(arr) < 8:
        arr.append(pad_token)
    return tuple(arr)


# ── Core detection functions ──

def detect_functional_groups(smiles: str) -> Dict[str, List[int]]:
    """Detect which SMARTS patterns match an atom in the molecule.

    Returns {fg_name: [atom_indices]} for all matching functional groups.
    Uses fg_exhaustive.SMARTS_PATTERNS if available, otherwise basic patterns.
    """
    if not HAS_RDKIT:
        return _basic_pattern_match(smiles)

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {}

    mol = Chem.AddHs(mol)
    Chem.SanitizeMol(mol)
    results = {}

    # Try importing the exhaustive database first
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "ch3mpiler"))
        from fg_exhaustive import SMARTS_PATTERNS as EXHAUSTIVE_PATTERNS
        patterns = EXHAUSTIVE_PATTERNS
    except ImportError:
        patterns = _basic_smarts_patterns()

    for fg_name, smarts in patterns.items():
        if fg_name not in FG_TOKEN_MAP:
            continue
        pat = Chem.MolFromSmarts(smarts)
        if pat is None:
            continue
        matches = mol.GetSubstructMatches(pat)
        if matches:
            # Flatten matched atom indices
            atoms = set()
            for m in matches:
                atoms.update(m)
            results[fg_name] = sorted(atoms)

    return results


def _basic_smarts_patterns() -> Dict[str, str]:
    """Fallback minimal SMARTS patterns when fg_exhaustive is unavailable."""
    return {
        "aromatic": "a",
        "alcohol": "[CX4][OH1]",
        "amine": "[NX3;H2,H1;!$(N=*)]",
        "carbonyl": "[CX3]=[OX1]",
        "carboxylic_acid": "[CX3](=O)[OX2H,OX1-]",
        "carboxylic_ester": "[#6][CX3](=[OX1])[OX2][#6]",
        "carboxylic_amide": "[CX3](=[OX1])[NX3]",
        "aldehyde": "[CX3H1](=O)[#6]",
        "alkene": "[CX3]=[CX3]",
        "alkyne": "[CX2]#[CX2]",
        "nitro": "[NX3+](=O)[O-]",
        "nitrile": "[NX1]#[CX2]",
        "ether": "[OD2]([#6])[#6]",
        "aryl_halide": "[F,Cl,Br,I][c]",
        "alkyl_halide": "[F,Cl,Br,I][CX4]",
        "phenol": "[OX2H][c]",
        "aniline": "[NX3;H2,H1][c]",
        "azide": "[NX2-]=[NX2+]=[NX1-]",
        "thiol": "[SX2H]",
        "sulfonic_acid": "[SX4](=O)(=O)[OX2H,OX1-]",
        "boronic_acid": "[BX3]([OX2H])([OX2H])[#6]",
    }


def _basic_pattern_match(smiles: str) -> Dict[str, List[int]]:
    """Basic SMARTS matching without RDKit (fallback for non-RDKit envs).

    Only detects simple patterns by string matching.
    """
    if not HAS_RDKIT:
        return {}
    return {}


def tokenize_molecule(mol) -> List[int]:
    """Convert an RDKit Mol to a list of IMASM tokens.

    Strategy:
    1. Detect ring systems → assign VINIT, IMSCRIB tokens
    2. Detect functional groups → assign AFWD, AREV, FSPLIT, FFUSE, etc.
    3. Classify bond types → assign CLINK tokens
    4. Detect terminals → assign TANCH tokens
    5. Order by topological importance
    6. Pad/trim to exactly 8 tokens
    """
    from rdkit import Chem
    from rdkit.Chem import rdMolDescriptors

    tokens = []

    # Step 1: Ring system analysis
    ri = mol.GetRingInfo()
    ring_count = ri.NumRings()
    aromatic_rings = sum(1 for ring in ri.AtomRings()
                         if all(mol.GetAtomWithIdx(a).GetIsAromatic() for a in ring))

    if ring_count > 0:
        if aromatic_rings > 0 and aromatic_rings == ring_count:
            # Purely aromatic: IMSCRIB
            tokens.append(IMSCRIB)
        else:
            # Mixed or non-aromatic ring system: VINIT
            tokens.append(VINIT)

    # Step 2: Detect functional groups using exhaustive database
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "ch3mpiler"))
        from fg_exhaustive import SMARTS_PATTERNS as EXHAUSTIVE_PATTERNS
        patterns = EXHAUSTIVE_PATTERNS
    except ImportError:
        patterns = _basic_smarts_patterns()

    # Collect all token assignments from matched functional groups
    fg_votes = []  # List of (token, weight) pairs
    matched_fgs = set()

    for fg_name, smarts in patterns.items():
        tok = FG_TOKEN_MAP.get(fg_name)
        if tok is None:
            continue
        pat = Chem.MolFromSmarts(smarts)
        if pat is None:
            continue
        matches = mol.GetSubstructMatches(pat)
        if matches:
            matched_fgs.add(fg_name)
            fg_votes.append((tok, TOKEN_WEIGHTS.get(tok, 5)))
            # Check for secondary mappings (e.g., carboxylic_acid → FSPLIT AND EVALT)
            for alt_tok, alt_fgs in TOKEN_FG_PRIORITY.items():
                if alt_tok != tok and fg_name in alt_fgs:
                    fg_votes.append((alt_tok, TOKEN_WEIGHTS.get(alt_tok, 5) - 1))

    # Step 3: Count bond types
    num_double = 0
    num_triple = 0
    for bond in mol.GetBonds():
        if bond.GetBondType() == Chem.BondType.DOUBLE:
            num_double += 1
        elif bond.GetBondType() == Chem.BondType.TRIPLE:
            num_triple += 1

    if num_double > 1:
        fg_votes.append((CLINK, 7))  # conjugated system
    if num_triple > 0:
        fg_votes.append((CLINK, 7))

    # Step 4: Check for terminal groups (methyl, halogens not in rings)
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 6 and atom.GetDegree() == 1 and not atom.GetIsAromatic():
            # Methyl group
            fg_votes.append((TANCH, TOKEN_WEIGHTS[TANCH]))
            break  # one is enough

    # Step 5: Check for heteroatom basicity/acidity
    for atom in mol.GetAtoms():
        atomic_num = atom.GetAtomicNum()
        if atomic_num == 7 and not atom.GetIsAromatic():
            if atom.GetFormalCharge() == 0:
                fg_votes.append((EVALF, TOKEN_WEIGHTS[EVALF]))
                break
        elif atomic_num == 8 and atom.GetDegree() == 1:
            if atom.GetTotalNumHs() > 0:
                fg_votes.append((EVALT, TOKEN_WEIGHTS[EVALT]))
                break

    # Step 6: Sort by weight descending, deduplicate
    fg_votes.sort(key=lambda x: -x[1])
    for tok, _ in fg_votes:
        if tok not in tokens:
            tokens.append(tok)

    # Step 7: Ensure we have at least VINIT as baseline
    if not tokens:
        tokens = [VINIT]

    return tokens


# ── Arrangement construction ──

def molecule_to_arrangement(smiles: str) -> Optional[Tuple[int, ...]]:
    """Convert a SMILES string to an 8-token IMASM arrangement.

    The arrangement encodes the molecule's structural fingerprint:
    - Position 0: Core scaffold type (VINIT, IMSCRIB)
    - Positions 1-2: Primary reactive sites (AFWD, AREV, FSPLIT, FFUSE)
    - Positions 3-4: Secondary features (EVALT, EVALF, ENGAGR)
    - Positions 5-6: Linkers and terminals (CLINK, TANCH)
    - Position 7: Capping token (IMSCRIB or IFIX if stabilized)

    Returns (8-tuple) or None if SMILES is invalid.
    """
    if not HAS_RDKIT:
        return None

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    mol = Chem.AddHs(mol)
    Chem.SanitizeMol(mol)
    tokens = tokenize_molecule(mol)
    return _arrange_from_tokens(tokens, smiles)


def _arrange_from_tokens(tokens: List[int], smiles_hint: str = "") -> Tuple[int, ...]:
    """Build an 8-token arrangement from a list of detected tokens.

    Positional logic:
      [0] — Core (VINIT / IMSCRIB) — molecule's backbone identity
      [1] — Primary forward reactivity (AFWD / FFUSE / FSPLIT)
      [2] — Primary reverse reactivity (AREV / EVALT / EVALF)
      [3] — Secondary / ambident site (ENGAGR / EVALT / EVALF)
      [4] — Linker / conjugation (CLINK)
      [5] — Terminal / capping (TANCH / IFIX)
      [6] — Space-filler — most characteristic remaining token
      [7] — Closure token (IMSCRIB for self-consistent structures, IFIX for locked)
    """
    arr = [VINIT] * 8  # default scaffold

    # Slot 0: Core scaffold
    for tok in [IMSCRIB, VINIT]:
        if tok in tokens:
            arr[0] = tok
            break

    # Slot 1: Primary forward reactivity
    for tok in [FFUSE, AFWD, FSPLIT]:
        if tok in tokens:
            arr[1] = tok
            break

    # Slot 2: Primary reverse / acidic
    for tok in [EVALT, AREV, EVALF]:
        if tok in tokens:
            arr[2] = tok
            break

    # Slot 3: Ambident or secondary
    for tok in [ENGAGR, EVALF, EVALT]:
        if tok in tokens and tok != arr[2]:
            arr[3] = tok
            break

    # Slot 4: Linker
    if CLINK in tokens:
        arr[4] = CLINK

    # Slot 5: Terminal
    for tok in [TANCH, IFIX]:
        if tok in tokens:
            arr[5] = tok
            break

    # Slot 6: Most characteristic remaining
    remaining = [t for t in tokens if t not in arr[:6]]
    if remaining:
        arr[6] = remaining[0]

    # Slot 7: Closure
    if IMSCRIB in tokens and arr[0] != IMSCRIB:
        arr[7] = IMSCRIB
    elif IFIX in tokens:
        arr[7] = IFIX
    else:
        arr[7] = IMSCRIB  # default closure

    return tuple(arr)


def arrangement_to_tokens(arr: Tuple[int, ...]) -> List[str]:
    """Convert a numeric arrangement to human-readable token names."""
    return [TOKEN_NAMES.get(t, f"UNKNOWN({t})") for t in arr]


def format_arrangement(arr: Tuple[int, ...]) -> str:
    """Format arrangement as arrow-separated string: IMSCRIB → AFWD → ..."""
    return " → ".join(arrangement_to_tokens(arr))


# ── Compound analysis ──

def analyze_molecule(smiles: str) -> Dict:
    """Full structural analysis of a SMILES string.

    Returns a dict with the molecule's IMASM arrangement, fingerprint,
    functional group assignments, and IG type bridge.
    """
    result = {
        "smiles": smiles,
        "valid": False,
        "arrangement": None,
        "tokens": [],
        "functional_groups": [],
        "ring_count": 0,
        "aromatic_rings": 0,
    }

    if not HAS_RDKIT or not smiles:
        return result

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return result

    mol = Chem.AddHs(mol)
    Chem.SanitizeMol(mol)

    # Ring analysis
    ri = mol.GetRingInfo()
    result["ring_count"] = ri.NumRings()
    result["aromatic_rings"] = sum(
        1 for ring in ri.AtomRings()
        if all(mol.GetAtomWithIdx(a).GetIsAromatic() for a in ring)
    )

    # Functional groups
    fg_results = detect_functional_groups(smiles)
    result["functional_groups"] = list(fg_results.keys())

    # IMASM tokens
    tokens = tokenize_molecule(mol)
    result["tokens_raw"] = [TOKEN_NAMES[t] for t in tokens]

    # Arrangement
    arr = molecule_to_arrangement(smiles)
    if arr:
        result["arrangement"] = list(arr)
        result["tokens"] = arrangement_to_tokens(arr)
        result["valid"] = True

    return result


# ── CLI entry point ──

def main():
    import argparse

    parser = argparse.ArgumentParser(description="IMASM compound encoder")
    parser.add_argument("smiles", nargs="?", help="SMILES string")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--arrangement-only", "-a", action="store_true",
                        help="Output only the arrangement tuple")
    args = parser.parse_args()

    if not args.smiles:
        # Demo mode
        demos = [
            ("aspirin", "CC(=O)OC1=CC=CC=C1C(=O)O"),
            ("paracetamol", "CC(=O)NC1=CC=C(C=C1)O"),
            ("ibuprofen", "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"),
            ("caffeine", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"),
            ("taxol", "CC1=C2C(C(=O)C3(C(CC4C(C3C(C(C2(C)C)(CC1OC(=O)C(C(C5=CC=CC=C5)NC(=O)C6=CC=CC=C6)O)O)OC(=O)C7=CC=CC=C7)(CO4)OC(=O)C)O)C)OC(=O)C"),
            ("benzene", "c1ccccc1"),
            ("ethanol", "CCO"),
            ("styrene", "C=CC1=CC=CC=C1"),
            ("resveratrol", "C1=CC(=CC=C1C=CC2=CC(=CC(=C2)O)O)O"),
        ]
        for name, smi in demos:
            arr = molecule_to_arrangement(smi)
            if arr:
                print(f"{name:20s} → {format_arrangement(arr)}")
        return

    arr = molecule_to_arrangement(args.smiles)
    if arr is None:
        print(f"Error: invalid SMILES: {args.smiles}", file=sys.stderr)
        sys.exit(1)

    if args.arrangement_only:
        print(format_arrangement(arr))
    elif args.json:
        result = analyze_molecule(args.smiles)
        print(json.dumps(result, indent=2))
    else:
        print(f"Arrangement: {format_arrangement(arr)}")
        names = arrangement_to_tokens(arr)
        print(f"Tokens: {', '.join(names)}")


if __name__ == "__main__":
    main()
