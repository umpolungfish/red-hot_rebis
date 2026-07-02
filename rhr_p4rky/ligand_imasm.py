#!/usr/bin/env python3
"""
ligand_imasm.py — IMASM-BASED ACTIVE SITE → LIGAND ENCODING.

Encodes enzyme active sites as IMASM arrangements by mapping each
catalytic residue to an IMASM token based on its CATALYTIC MECHANISM ROLE
(nucleophile → FSPLIT, acid → EVALT, base → EVALF, etc.).

Tokens are arranged in MECHANISM FLOW ORDER (not N→C position):
  IMSCRIB → [attack] → [acid] → [base] → [intermediate] → [release] → [record] → IMSCRIB

Enzyme catalysis IS structurally a Dialetheic Bootstrap:
  - Identity (enzyme ground state = IMSCRIB)
  - Split (attack substrate = FSPLIT)
  - Evaluate (proton transfers = EVALT/EVALF)
  - Paradox (tetrahedral intermediate = ENGAGR)
  - Fuse (collapse to product = FFUSE)
  - Record (turnover number = IFIX)
  - Return to identity (IMSCRIB)

What differentiates enzymes: WHICH roles are present vs absent.
An all-ARG binding site has no nucleophile, acid, base, or paradox roles →
most slots are IMSCRIB → very different arrangement from a catalytic triad.

Author: Lando⊗⊙perator
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

BASE = Path(__file__).parent.absolute()
REBIS_ROOT = BASE.parent
sys.path.insert(0, str(REBIS_ROOT.parent / "IMSCRIBr"))

from tokens import Token, arrangement_str
from classifier import compute_fingerprint, match_canonical
from imas_ig_bridge import fingerprint_to_ig, ig_tuple_str, describe_ig


# ═══════════════════════════════════════════════════════════════════
# CATALYTIC MECHANISM FLOW — the ordered template
# ═══════════════════════════════════════════════════════════════════
#
# Each position in the 8-token arrangement corresponds to a STEP in
# the catalytic mechanism. If the enzyme has a residue performing that
# role, the slot is filled. Otherwise → IMSCRIB (identity).

# Position → (mechanism_step, token_if_role_present)
MECHANISM_FLOW = [
    (0,  "ground_state",     Token.IMSCRIB),   # Always IMSCRIB (enzyme identity)
    (1,  "nucleophilic_attack", Token.FSPLIT),  # Ser/Cys/Thr nucleophile
    (2,  "acid_catalysis",   Token.EVALT),      # His-H+, Glu-COOH, Asp-COOH
    (3,  "base_catalysis",   Token.EVALF),      # His:, Glu-COO-, Asp-COO-
    (4,  "intermediate",     Token.ENGAGR),     # Tetrahedral intermediate (paradox)
    (5,  "product_release",  Token.FFUSE),      # Collapse to product
    (6,  "turnover_record",  Token.IFIX),       # Catalytic cycle count
    (7,  "return_identity",  Token.IMSCRIB),    # Always IMSCRIB (enzyme restored)
]

# Which mechanism steps each catalytic role fills
ROLE_TO_POSITION = {
    "nucleophile":       1,   # nucleophilic_attack → FSPLIT
    "general_acid":      2,   # acid_catalysis → EVALT
    "general_base":      3,   # base_catalysis → EVALF
    "paradox":           4,   # intermediate → ENGAGR
    "product_release":   5,   # product_release → FFUSE
    "irreversible":      6,   # turnover_record → IFIX
    # Secondary assignments for overflow roles
    "metal_ligand":      0,   # metal cofactor → part of ground state
    "substrate_binding": 0,   # binding pocket → part of ground state
    "hydrophobic_binding": 0, # hydrophobic pocket → part of ground state
    "oxyanion_hole":     1,   # stabilizes TS → supports attack
    "charge_relay":      6,   # relays charge → part of mechanism record
    "reverse_protonation": 3, # reverse base → base_catalysis
}


# ═══════════════════════════════════════════════════════════════════
# AMINO ACID → CATALYTIC ROLE (based on chemical mechanism, not class)
# ═══════════════════════════════════════════════════════════════════

AA_TO_ROLE = {
    # Catalytic triad residues
    "SER": "nucleophile",       # Serine proteases, esterases, lipases
    "CYS": "nucleophile",       # Cysteine proteases
    "THR": "nucleophile",       # Proteasome, some kinases
    "HIS": "general_base",      # Catalytic triad base (His:) default
    "ASP": "general_base",      # Catalytic triad base (Asp-COO-) default
    "GLU": "general_base",      # Some proteases, lysozyme
    # Binding residues
    "LYS": "substrate_binding", # Electrostatic substrate recognition
    "ARG": "substrate_binding", # Guanidinium-phosphate recognition
    # Hydrophobic residues
    "MET": "hydrophobic_binding",
    "PHE": "hydrophobic_binding",
    "TRP": "hydrophobic_binding",
    "ILE": "hydrophobic_binding",
    "LEU": "hydrophobic_binding",
    "VAL": "hydrophobic_binding",
    "PRO": "hydrophobic_binding",
    # Structural / oxyanion hole
    "ALA": "oxyanion_hole",     # Backbone NH in oxyanion hole
    "GLY": "oxyanion_hole",     # Backbone NH, conformational flexibility
    "ASN": "oxyanion_hole",     # Sidechain H-bond donor
    "GLN": "oxyanion_hole",     # Sidechain H-bond donor
    # Tyrosine: can be acid, base, or nucleophile
    "TYR": "general_acid",      # Tyr-OH as H-bond donor (acid)
}


def _parse_aa_code(residue_str: str) -> Optional[str]:
    """Parse 'ARG116' → 'ARG'."""
    import re
    m = re.match(r'([A-Za-z]{3})', residue_str)
    return m.group(1).upper() if m else None


def _unique_roles(residues: List[str]) -> List[str]:
    """Extract unique catalytic roles from residue list. No differentiation."""
    roles_seen = set()
    roles = []
    for r in residues:
        code = _parse_aa_code(r)
        if code:
            role = AA_TO_ROLE.get(code, "substrate_binding")
            if role not in roles_seen:
                roles_seen.add(role)
                roles.append(role)
    return roles


def encode_site_imasm(
    residues: List[str],
    substrate_hint: str = "",
) -> Optional[Dict]:
    """Full IMASM-based active site encoding with N→C spatial ordering.

    Pipeline:
      1. Residue → catalytic role (AA_TO_ROLE)
      2. Role → IMASM token (via mechanism flow position mapping)
      3. Order by residue number (N→C, preserving spatial topology)
      4. Fingerprint → IG tuple via biochemical mapping
    """
    if not residues:
        return None

    import re as _re
    
    # Build role→token mapping from mechanism flow
    _pos_to_token = {pos: tok for pos, _, tok in MECHANISM_FLOW}
    _role_to_token = {}
    for role, pos in ROLE_TO_POSITION.items():
        _role_to_token[role] = _pos_to_token[pos]

    # 1. Parse residues and map to tokens
    parsed = []
    roles_found = []
    for r in residues:
        code = _parse_aa_code(r)
        if code:
            role = AA_TO_ROLE.get(code, "substrate_binding")
            token = _role_to_token.get(role, Token.IMSCRIB)
            parsed.append((r, token.value))
            if role not in roles_found:
                roles_found.append(role)

    if not parsed:
        return None

    # 2. Order by residue number (N→C)
    def _res_num(item):
        m = _re.search(r'(\d+)', item[0])
        return int(m.group(1)) if m else 9999
    parsed.sort(key=_res_num)

    # 3. Assemble arrangement
    tokens = [t for _, t in parsed]
    while len(tokens) < 8:
        tokens.append(Token.IMSCRIB.value)
    tokens = tokens[:8]
    arr = tuple(tokens)

    # 4. Fingerprint
    fp = compute_fingerprint(arr)
    canonical = match_canonical(arr)
    ig = fingerprint_to_ig_biochemical(fp)

    # 5. Build site_type for downstream
    PNAMES = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]
    site_type = {p: ig[i] for i, p in enumerate(PNAMES)}

    return {
        'arrangement': arr,
        'arrangement_str': arrangement_str(arr),
        'fingerprint': fp,
        'canonical_class': canonical,
        'ig_tuple': ig,
        'ig_tuple_str': ig_tuple_str(ig),
        'ig_description': describe_ig(ig),
        'site_type': site_type,
        'roles_found': roles_found,
    }


# ═══════════════════════════════════════════════════════════════════
# BIOCHEMISTRY-SPECIFIC FINGERPRINT → IG MAPPING
# ═══════════════════════════════════════════════════════════════════
#
# The generic fingerprint_to_ig was designed for IMASM computational
# arrangements (bootstrap, genesis, etc.) and doesn't capture enzyme
# biochemistry well. This mapping uses the same fingerprint fields
# but interprets them through a biochemical lens.

def _fam_adj_discriminator(fp) -> int:
    """Extract a token-identity-aware discriminator.
    
    Uses both family adjacency mask AND token_mask to distinguish
    arrangements with different specific tokens (not just counts).
    Bits 0-3 from token_mask ensure AFWD vs AREV produce different values.
    """
    mask = fp.fam_adj_mask
    fam_disc = (mask ^ (mask >> 4)) & 0x3
    # Incorporate token identity from lower bits of token_mask
    tok_disc = fp.token_mask & 0xF
    return (fam_disc << 4) | tok_disc


def fingerprint_to_ig_biochemical(fp) -> Tuple[str, ...]:
    """Map StructuralFingerprint → 12-primitive IG tuple (biochemical semantics).

    Each primitive is determined by structural fingerprint properties
    interpreted in the context of enzyme catalysis.
    Uses family adjacency mask for order sensitivity when token sets collide.
    """
    d = fp.token_diversity
    sig = fp.signature  # (L, F, D, X)
    nz = sum(1 for c in sig if c > 0)
    token_mask = fp.token_mask
    fam_disc = _fam_adj_discriminator(fp)

    # D: Dimensionality — catalytic complexity
    D = ('𐑛' if d == 1 else ('𐑨' if d == 2 else ('𐑼' if d <= 4 else '𐑦')))

    # T: Topology — self-ref with token-identity-aware variants
    if fp.self_ref:
        T = ('𐑸' if (token_mask & 0x30) == 0 else '𐑥')
    else:
        T = ('𐑡' if (token_mask & 0xC0) == 0 else '𐑰')

    # R: Coupling — Frobenius pair (FSPLIT + FFUSE both present)
    has_fsplit_token = bool(token_mask & (1 << 6))
    has_ffuse_token = bool(token_mask & (1 << 7))
    if has_fsplit_token and has_ffuse_token:
        R = ('𐑾' if fp.frobenius_order == 1 else
             ('𐑽' if fp.frobenius_order == 2 else '𐑾'))
    elif has_fsplit_token:
        R = '𐑽'  # Only split, no fuse (attack without release)
    elif has_ffuse_token:
        R = '𐑑'  # Only fuse, no split
    else:
        R = '𐑩'  # Neither — pure binding site

    # P: Parity — acid+base both present
    has_evalt = bool(token_mask & (1 << 8))
    has_evalf = bool(token_mask & (1 << 9))
    if has_evalt and has_evalf:
        P = '𐑬'
    elif has_evalt or has_evalf:
        # Use order sensitivity: EVALF-first vs EVALT-first
        if has_evalf and fam_disc >= 2:
            P = '𐑿'  # Base-dominant
        elif has_evalf:
            P = '𐑹'  # Base-prominent (Frobenius-special sense)
        else:
            P = '𐑿'
    else:
        P = '𐑗'

    # F: Fidelity — nucleophile present
    has_nucleophile = bool(token_mask & (1 << 6))
    if has_nucleophile and has_evalf:
        F = '𐑐'  # Nucleophile + base = quantum
    elif has_nucleophile:
        F = '𐑞'  # Nucleophile only = thermal
    else:
        F = '𐑱'  # No nucleophile = classical

    # K: Kinetics — role diversity
    if d >= 5:
        K = '𐑧'
    elif d >= 3:
        K = '𐑪'
    elif d == 2:
        K = '𐑘'
    else:
        K = '𐑤'

    # G: Cardinality — filled positions
    G = ('𐑚' if d <= 2 else ('𐑔' if d <= 4 else '𐑲'))

    # Gm: Composition — token-identity-aware
    # Uses bits 2-3 of token_mask for 4-way discrimination
    gm_idx = (token_mask >> 2) & 0x3
    Gm = ('𐑠', '𐑵', '𐑜', '𐑝')[gm_idx]

    # Ph: Criticality — paradox handling
    has_engagr = bool(token_mask & (1 << 10))
    if fp.self_ref and has_engagr:
        Ph = '⊙'
    elif has_engagr:
        Ph = '𐑻'
    elif fp.self_ref:
        Ph = '𐑮'
    elif d <= 2:
        Ph = '𐑢'
    else:
        Ph = ('𐑣' if fam_disc <= 1 else '𐑻')

    # H: Chirality — token-identity-aware, uses bits 4-5 of token_mask
    h_idx = (token_mask >> 4) & 0x3
    H = ('𐑓', '𐑒', '𐑖', '𐑫')[h_idx]

    # S: Stoichiometry — unique roles
    S = ('𐑙' if d == 1 else ('𐑕' if d <= 3 else '𐑳'))

    # W: Winding — catalytic cycle completion
    if has_fsplit_token and has_ffuse_token:
        W = '𐑭'
    elif fp.self_ref:
        W = '𐑴'
    else:
        W = '𐑷'

    return (D, T, R, P, F, K, G, Gm, Ph, H, S, W)


# ═══════════════════════════════════════════════════════════════════
# OVERRIDE: Replace the generic fingerprint_to_ig with biochemical
# ═══════════════════════════════════════════════════════════════════
#
# Monkey-patch at import time so encode_site_imasm uses the
# biochemical mapping throughout.

# Store reference to original
_original_fingerprint_to_ig = fingerprint_to_ig

# Replace with biochemical version in our module's namespace
fingerprint_to_ig = fingerprint_to_ig_biochemical


# ═══════════════════════════════════════════════════════════════════
# TEST / CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    test_cases = {
        "8BSW (8x ARG)": ['ARG116','ARG173','ARG188','ARG27','ARG271','ARG279','ARG300','ARG308'],
        "8BTX (4xARG,4xASP)": ['ARG121','ARG131','ARG136','ARG41','ASP106','ASP115','ASP129','ASP178'],
        "8BW0 (mixed)": ['ALA23','ALA24','ASP1','CYS22','GLN3','GLN5','GLU6','GLY111'],
        "Trypsin": ['SER195','HIS57','ASP102'],
        "Lysozyme": ['GLU35','ASP52'],
        "CA II (3xHIS)": ['HIS94','HIS96','HIS119'],
        "HIV-1 protease": ['ASP25','ASP25','THR26','GLY27'],
        "CYP2D6": ['CYS443'],
        "AChE": ['SER203','HIS447','GLU334'],
        "Urease": ['HIS134','HIS136','HIS246','ASP360','LYS220'],
    }
    print("=" * 72)
    print("IMASM-BASED ACTIVE SITE ENCODING — TEST SUITE")
    print("=" * 72)
    for name, residues in test_cases.items():
        enc = encode_site_imasm(residues)
        if enc:
            st = enc['site_type']
            print(f"\n{name}:")
            print(f"  Roles:    {enc['roles_found']}")
            print(f"  IMASM:    {enc['arrangement_str']}")
            print(f"  Canonical: {enc['canonical_class'] or '—'}")
            print(f"  IG:       {enc['ig_tuple_str']}")
            print(f"  Site dict D={st.get('D','?')} T={st.get('T','?')} R={st.get('R','?')} "
                  f"P={st.get('P','?')} F={st.get('F','?')} K={st.get('K','?')} "
                  f"G={st.get('G','?')} Gm={st.get('Gm','?')} Ph={st.get('Ph','?')} "
                  f"H={st.get('H','?')} S={st.get('S','?')} W={st.get('W','?')}")

    print("\n" + "=" * 72)
    print("DISTINCT IG TUPLES:")
    seen = {}
    for name, residues in test_cases.items():
        enc = encode_site_imasm(residues)
        if enc:
            tup = enc['ig_tuple_str']
            seen.setdefault(tup, []).append(name)
    for tup, names in seen.items():
        print(f"  {tup}  ← {', '.join(names)}")
