#!/usr/bin/env python3
"""
ligand_imasm.py — IMASM-BASED ACTIVE SITE → LIGAND ENCODING.

Encodes enzyme active sites as IMASM arrangements by mapping each
catalytic residue to an IMASM token based on its CHEMICAL PROPERTIES
(charge, polarity, aromaticity, nucleophilicity, size, flexibility).

The 8-residue arrangement is ordered N→C (preserving spatial topology).
Each residue's chemical character maps directly to one of the 12 IMASM tokens.
This replaces the old role-based mechanism-flow approach which collapsed
diverse amino acids (ARG, LYS, MET, PHE, TRP, ILE, LEU, VAL, PRO) into
a single "substrate_binding" → IMSCRIB bottleneck.

Token assignments by chemical class:
  Acidic   (ASP, GLU)    → EVALF  (evaluate-false = negative charge)
  Basic    (HIS, LYS)    → EVALT  (evaluate-true  = positive charge)
  Guanidinium (ARG)      → TANCH  (terminal = planar, rigid, strong H-bond)
  Nucleophile (SER,CYS,THR)→FSPLIT (split = attacks substrate)
  Aromatic (TYR, TRP)    → ENGAGR (paradox = multi-mode interaction)
  Aromatic-h (PHE)       → AFWD   (forward = directional π-stack)
  Polar-amide (ASN, GLN) → AREV   (reverse = bidirectional H-bond)
  Flexible (GLY)         → VINIT  (void = minimal steric constraint)
  Small-h (ALA)          → CLINK  (compose = methyl, ubiquitous)
  Branched-h (VAL,LEU,ILE)→IFIX   (irreversible = rigid, branched)
  Thioether (MET)        → AREV   (reverse = polarizable sulfur)
  Cyclic (PRO)           → IMSCRIB(identity = constrained backbone)

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
# AMINO ACID → IMASM TOKEN (chemical-property-based, not role-based)
# ═══════════════════════════════════════════════════════════════════

AA_TO_TOKEN = {
    # ── Acidic (negative charge at physiological pH) → EVALF ──
    "ASP": Token.EVALF,   # Aspartate: -COO⁻
    "GLU": Token.EVALF,   # Glutamate: -COO⁻

    # ── Basic (positive charge at physiological pH) → EVALT ──
    "HIS": Token.EVALT,   # Histidine: imidazole (pKa~6, both states)
    "LYS": Token.EVALT,   # Lysine: -NH₃⁺

    # ── Guanidinium (strongly basic, planar, rigid H-bond donor) → TANCH ──
    "ARG": Token.TANCH,   # Arginine: guanidinium — terminal/boundary object

    # ── Nucleophilic (attacks electrophilic centers) → FSPLIT ──
    "SER": Token.FSPLIT,  # Serine: -CH₂OH
    "CYS": Token.FSPLIT,  # Cysteine: -CH₂SH (stronger nucleophile)
    "THR": Token.FSPLIT,  # Threonine: -CH(OH)CH₃

    # ── Aromatic (multi-mode: H-bond + π-stack + hydrophobic) → ENGAGR ──
    "TYR": Token.ENGAGR,  # Tyrosine: phenol — H-bond donor/acceptor + aromatic
    "TRP": Token.ENGAGR,  # Tryptophan: indole — largest aromatic, N-H donor

    # ── Aromatic hydrophobic (directional π-stacking) → AFWD ──
    "PHE": Token.AFWD,    # Phenylalanine: benzyl — forward/directional π

    # ── Polar amide (bidirectional H-bond donor AND acceptor) → AREV ──
    "ASN": Token.AREV,    # Asparagine: -CH₂CONH₂
    "GLN": Token.AREV,    # Glutamine: -CH₂CH₂CONH₂

    # ── Flexible (minimal steric constraint) → VINIT ──
    "GLY": Token.VINIT,   # Glycine: -H only — void/initial

    # ── Small hydrophobic (methyl) → CLINK ──
    "ALA": Token.CLINK,   # Alanine: -CH₃ — compose, ubiquitous

    # ── Branched hydrophobic (rigid, sterically constrained) → IFIX ──
    "VAL": Token.IFIX,    # Valine: -CH(CH₃)₂
    "LEU": Token.IFIX,    # Leucine: -CH₂CH(CH₃)₂
    "ILE": Token.IFIX,    # Isoleucine: -CH(CH₃)CH₂CH₃

    # ── Thioether (polarizable sulfur, flexible) → AREV ──
    "MET": Token.AREV,    # Methionine: -CH₂CH₂SCH₃ — polarizable

    # ── Cyclic (conformationally constrained) → IMSCRIB ──
    "PRO": Token.IMSCRIB, # Proline: pyrrolidine ring — identity (constrained)
}

# Chemical class names for each amino acid (for diagnostics)
AA_CHEMICAL_CLASS = {
    "ASP": "acidic",       "GLU": "acidic",
    "HIS": "basic",        "LYS": "basic",
    "ARG": "guanidinium",
    "SER": "nucleophile",  "CYS": "nucleophile",  "THR": "nucleophile",
    "TYR": "aromatic",     "TRP": "aromatic",
    "PHE": "aromatic_hydrophobic",
    "ASN": "polar_amide",  "GLN": "polar_amide",
    "GLY": "flexible",
    "ALA": "small_hydrophobic",
    "VAL": "branched_h",   "LEU": "branched_h",   "ILE": "branched_h",
    "MET": "thioether",
    "PRO": "cyclic",
}

# Token → chemical interpretation (reverse lookup for diagnostics)
TOKEN_CHEM_MEANING = {
    Token.EVALF:   "acidic (negative)",
    Token.EVALT:   "basic (positive)",
    Token.TANCH:   "guanidinium (planar/rigid)",
    Token.FSPLIT:  "nucleophile (attacks)",
    Token.ENGAGR:  "aromatic (multi-mode)",
    Token.AFWD:    "aromatic-hydrophobic (π-stack)",
    Token.AREV:    "polar/H-bond (bidirectional)",
    Token.VINIT:   "flexible (minimal steric)",
    Token.CLINK:   "small hydrophobic (methyl)",
    Token.IFIX:    "branched hydrophobic (rigid)",
    Token.IMSCRIB: "cyclic (constrained)",
    Token.FFUSE:   "fuse (reserved)",
}


def _parse_aa_code(residue_str: str) -> Optional[str]:
    """Parse 'ARG116' → 'ARG'."""
    import re
    m = re.match(r'([A-Za-z]{3})', residue_str)
    return m.group(1).upper() if m else None


def encode_site_imasm(
    residues: List[str],
    substrate_hint: str = "",
) -> Optional[Dict]:
    """Full IMASM-based active site encoding with N→C spatial ordering.

    Pipeline:
      1. Residue → IMASM token (AA_TO_TOKEN, chemical-property-based)
      2. Order by residue number (N→C, preserving spatial topology)
      3. Fingerprint → IG tuple via biochemical mapping
      4. Also compute per-residue chemical class for diagnostics
    """
    if not residues:
        return None

    import re as _re

    # 1. Parse residues and map directly to tokens by chemical class
    parsed = []
    chem_classes = []
    for r in residues:
        code = _parse_aa_code(r)
        if code:
            token = AA_TO_TOKEN.get(code, Token.IMSCRIB)
            parsed.append((r, token.value, code, AA_CHEMICAL_CLASS.get(code, "unknown")))
            if AA_CHEMICAL_CLASS.get(code, "unknown") not in chem_classes:
                chem_classes.append(AA_CHEMICAL_CLASS.get(code, "unknown"))

    if not parsed:
        return None

    # 2. Order by residue number (N→C)
    def _res_num(item):
        m = _re.search(r'(\d+)', item[0])
        return int(m.group(1)) if m else 9999
    parsed.sort(key=_res_num)

    # 3. Assemble arrangement (N→C ordered, pad to 8)
    tokens = [t for _, t, _, _ in parsed]
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

    # 6. Diagnostic: per-residue chemical assignments
    residue_chem = [
        {"residue": r, "aa": aa, "token": Token(t).name, "chem_class": cc}
        for r, t, aa, cc in parsed
    ]

    return {
        'arrangement': arr,
        'arrangement_str': arrangement_str(arr),
        'fingerprint': fp,
        'canonical_class': canonical,
        'ig_tuple': ig,
        'ig_tuple_str': ig_tuple_str(ig),
        'ig_description': describe_ig(ig),
        'site_type': site_type,
        'chem_classes': chem_classes,
        'residue_chem': residue_chem,
    }
# ═══════════════════════════════════════════════════════════════════
# BIOCHEMISTRY-SPECIFIC FINGERPRINT → IG MAPPING
# ═══════════════════════════════════════════════════════════════════
#
# Maps the StructuralFingerprint of the IMASM arrangement to a
# 12-primitive IG tuple. With the new chemical-property-based token
# mapping, each primitive reflects the chemical character of the
# active site: charge distribution, polarity, aromaticity, size, etc.

def _fam_adj_discriminator(fp) -> int:
    """Extract a token-identity-aware discriminator.
    
    Uses both family adjacency mask AND token_mask to distinguish
    arrangements with different specific tokens (not just counts).
    Bits 0-3 from token_mask ensure AFWD vs AREV produce different values.
    """
    mask = fp.fam_adj_mask
    fam_disc = (mask ^ (mask >> 4)) & 0x3
    tok_disc = fp.token_mask & 0xF
    return (fam_disc << 4) | tok_disc



def _primary_token(token_mask: int) -> int:
    """Return the lowest token index present in the mask."""
    if token_mask == 0:
        return 0
    return (token_mask & -token_mask).bit_length() - 1

def fingerprint_to_ig_biochemical(fp) -> Tuple[str, ...]:
    """Map StructuralFingerprint → 12-primitive IG tuple (chemical semantics).

    With the chemical-property token mapping:
    - EVALF (acidic/negative) and EVALT (basic/positive) → charge balance
    - FSPLIT (nucleophile) → reactivity
    - ENGAGR (aromatic) → multi-mode interaction capacity
    - TANCH (guanidinium) → strong directional H-bonding
    - IFIX (branched hydrophobic) → steric constraint
    - VINIT (flexible) → conformational freedom
    - AREV (polar amide) → bidirectional H-bond network
    - AFWD (aromatic hydrophobic) → directional π-stacking
    - CLINK (small hydrophobic) → minimal interaction
    - IMSCRIB (cyclic) → backbone constraint
    """
    d = fp.token_diversity
    sig = fp.signature
    nz = sum(1 for c in sig if c > 0)
    token_mask = fp.token_mask
    fam_disc = _fam_adj_discriminator(fp)

    # Chemical class presence (derived from token_mask)
    has_acidic    = bool(token_mask & (1 << Token.EVALF.value))
    has_basic     = bool(token_mask & (1 << Token.EVALT.value))
    has_guanid    = bool(token_mask & (1 << Token.TANCH.value))
    has_nucleo    = bool(token_mask & (1 << Token.FSPLIT.value))
    has_aromatic  = bool(token_mask & (1 << Token.ENGAGR.value))
    has_arom_h    = bool(token_mask & (1 << Token.AFWD.value))
    has_polar     = bool(token_mask & (1 << Token.AREV.value))
    has_flexible  = bool(token_mask & (1 << Token.VINIT.value))
    has_small_h   = bool(token_mask & (1 << Token.CLINK.value))
    has_branched  = bool(token_mask & (1 << Token.IFIX.value))
    has_cyclic    = bool(token_mask & (1 << Token.IMSCRIB.value))

    n_acidic = 1 if has_acidic else 0
    n_basic = 1 if has_basic else 0
    n_charged = n_acidic + n_basic + (1 if has_guanid else 0)
    n_aromatic = (1 if has_aromatic else 0) + (1 if has_arom_h else 0)
    n_hydrophobic = (1 if has_branched else 0) + (1 if has_small_h else 0)

    # D: Dimensionality — chemical complexity
    if d >= 5:
        D = '𐑦'
    elif d >= 3:
        D = '𐑼'
    elif d == 2:
        D = '𐑨'
    else:
        D = '𐑛'

    # T: Topology — spatial residue connectivity
    if fp.self_ref:
        T = '𐑸' if n_aromatic >= 2 else '𐑥'
    elif n_charged >= 2:
        T = '𐑶'
    elif n_charged == 1:
        T = '𐑥'
    elif n_aromatic >= 1:
        T = '𐑰'
    elif n_hydrophobic >= 2:
        T = '𐑡'
    else:
        T = '𐑡'

    # R: Coupling — charge/H-bond interactions
    if has_acidic and has_basic:
        R = '𐑾'
    elif has_acidic and has_guanid:
        R = '𐑾'
    elif has_polar and (has_acidic or has_basic):
        R = '𐑽'
    elif has_polar:
        R = '𐑽'
    elif has_guanid:
        R = '𐑹'   # Strong directional H-bond (guanidinium)
    elif has_basic:
        R = '𐑑'   # Positive charge center
    elif has_acidic:
        R = '𐑽'   # Negative charge (conjugate base)
    else:
        R = '𐑩'

    # P: Parity — charge balance
    if has_acidic and has_basic:
        P = '𐑬'
    elif has_acidic and has_guanid:
        P = '𐑹'
    elif has_acidic:
        P = '𐑿'   # Negative-biased
    elif has_guanid:
        P = '𐑹'   # Guanidinium — strong directional (Frobenius-special)
    elif has_basic:
        P = '𐑿'   # Positive-biased
    elif has_polar:
        P = '𐑗'
    else:
        P = '𐑗'

    # F: Fidelity — quantum vs classical
    if has_nucleo and (has_acidic or has_basic):
        F = '𐑐'
    elif has_nucleo:
        F = '𐑞'
    elif n_charged >= 2:
        F = '𐑞'
    elif has_aromatic:
        F = '𐑞'
    else:
        F = '𐑱'

    # K: Kinetics — chemical diversity
    if d >= 5:
        K = '𐑧'
    elif d >= 3:
        K = '𐑪'
    elif d == 2:
        K = '𐑘'
    else:
        K = '𐑤'

    # G: Cardinality — spatial extent
    if n_charged >= 3:
        G = '𐑲'
    elif n_charged >= 2 or n_aromatic >= 2:
        G = '𐑔'
    else:
        G = '𐑚'

    # Gm: Composition — primary token + order sensitivity (fam_disc)
    prim_tok = _primary_token(token_mask)
    gm_idx = (prim_tok + (fam_disc >> 4)) % 4
    Gm = ('𐑠', '𐑵', '𐑜', '𐑝')[gm_idx]

    # Ph: Criticality — catalytic critical point
    if fp.self_ref and has_nucleo:
        Ph = '⊙'
    elif has_nucleo and (has_acidic or has_basic):
        Ph = '𐑻'
    elif fp.self_ref:
        Ph = '𐑮'
    elif has_aromatic and has_polar:
        Ph = '𐑣'
    elif d <= 2:
        Ph = '𐑢'
    else:
        Ph = '𐑣' if fam_disc <= 1 else '𐑻'

    # H: Chirality — uses primary token for identity awareness
    h_idx = (prim_tok // 4) % 4
    H = ('𐑓', '𐑒', '𐑖', '𐑫')[h_idx]

    # S: Stoichiometry — chemical class count
    if d == 1:
        S = '𐑙'
    elif d <= 3:
        S = '𐑕'
    else:
        S = '𐑳'

    # W: Winding — topological protection
    if has_nucleo and has_acidic and has_basic:
        W = '𐑭'
    elif has_nucleo or (has_acidic and has_basic):
        W = '𐑴'
    elif fp.self_ref:
        W = '𐑴'
    else:
        W = '𐑷'

    return (D, T, R, P, F, K, G, Gm, Ph, H, S, W)


# Override
_original_fingerprint_to_ig = fingerprint_to_ig
fingerprint_to_ig = fingerprint_to_ig_biochemical

# ═══════════════════════════════════════════════════════════════════
# TEST / CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    test_cases = {
        "8BSW (8x ARG — guanidinium)": ['ARG116','ARG173','ARG188','ARG27','ARG271','ARG279','ARG300','ARG308'],
        "8x LEU (branched hydrophobic)": ['LEU10','LEU20','LEU30','LEU40','LEU50','LEU60','LEU70','LEU80'],
        "8x PHE (aromatic hydrophobic)": ['PHE10','PHE20','PHE30','PHE40','PHE50','PHE60','PHE70','PHE80'],
        "8x LYS (basic)": ['LYS10','LYS20','LYS30','LYS40','LYS50','LYS60','LYS70','LYS80'],
        "8x ASP (acidic)": ['ASP10','ASP20','ASP30','ASP40','ASP50','ASP60','ASP70','ASP80'],
        "8x GLY (flexible)": ['GLY10','GLY20','GLY30','GLY40','GLY50','GLY60','GLY70','GLY80'],
        "8BTX (4xARG,4xASP — salt bridge)": ['ARG121','ARG131','ARG136','ARG41','ASP106','ASP115','ASP129','ASP178'],
        "8BW0 (mixed chemical classes)": ['ALA23','ALA24','ASP1','CYS22','GLN3','GLN5','GLU6','GLY111'],
        "Trypsin (SER,HIS,ASP)": ['SER195','HIS57','ASP102'],
        "Lysozyme (GLU,ASP)": ['GLU35','ASP52'],
        "CA II (3xHIS)": ['HIS94','HIS96','HIS119'],
        "HIV-1 protease": ['ASP25','ASP25','THR26','GLY27'],
        "CYP2D6 (CYS heme)": ['CYS443'],
        "AChE (SER,HIS,GLU)": ['SER203','HIS447','GLU334'],
        "Urease (HISx3,ASP,LYS)": ['HIS134','HIS136','HIS246','ASP360','LYS220'],
        "All 20 AAs (one each)": ['ALA1','ARG2','ASN3','ASP4','CYS5','GLN6','GLU7','GLY8',
                                   'HIS9','ILE10','LEU11','LYS12','MET13','PHE14',
                                   'PRO15','SER16','THR17','TRP18','TYR19','VAL20'],
        "Pure hydrophobic": ['VAL10','LEU20','ILE30','VAL40','LEU50','ILE60','VAL70','LEU80'],
    }
    
    print("=" * 72)
    print("IMASM-BASED ACTIVE SITE ENCODING — CHEMICAL PROPERTY MAPPING")
    print("=" * 72)
    
    for name, residues in test_cases.items():
        enc = encode_site_imasm(residues)
        if enc:
            st = enc['site_type']
            print(f"\n{name}:")
            print(f"  Chem:     {enc['chem_classes']}")
            print(f"  IMASM:    {enc['arrangement_str']}")
            print(f"  Canonical: {enc['canonical_class'] or '—'}")
            print(f"  IG:       {enc['ig_tuple_str']}")
    
    print("\n" + "=" * 72)
    print("DISTINCT IG TUPLES:")
    seen = {}
    for name, residues in test_cases.items():
        enc = encode_site_imasm(residues)
        if enc:
            tup = enc['ig_tuple_str']
            seen.setdefault(tup, []).append(name)
    
    n_unique = len(seen)
    n_total = len(test_cases)
    for tup, names in sorted(seen.items()):
        marker = " ⚠" if len(names) > 1 else " ✓"
        print(f"  {tup}  ← {', '.join(names)}{marker}")
    
    collisions = sum(1 for names in seen.values() if len(names) > 1)
    if collisions == 0:
        print(f"\n  ALL {n_unique}/{n_total} test cases produce UNIQUE IG tuples.")
    else:
        print(f"\n  {collisions} collision(s) — {n_unique}/{n_total} unique.")
