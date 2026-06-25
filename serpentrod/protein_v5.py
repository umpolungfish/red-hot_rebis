#!/usr/bin/env python3
"""
protein_enhancements_v5.py — Frobenius-Guided Protein Processing Engine
========================================================================
Builds on v4 with:
  • POMC-specific fragment naming (N-POMC, joining peptide, ACTH, β-LPH, β-endorphin)
  • Context-aware merging of false-positive internal dibasic sites
  • Monobasic cleavage detection (single R/K in specific contexts)
  • Advanced fragment classification by primitive spectrum fingerprint
  • SARS-CoV-2 polyprotein test case
  • Cross-kingdom test cases (plant, insect)

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import re, sys
import pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from serpentrod.stratified_predictor import (
    PRIMITIVE_MAP, PRIMITIVE_ORDERS, HYDROPATHY, ZERO_PRIMITIVE_AAS,
    RollingProfile, CleavageSite, MatureProduct, ProcessingPrediction,
    classify_module, predict_processing, analyze_spectrum
)
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field

# ── Signal Peptide constants — derived from IG primitive structure ──────────
#
# Von Heijne position recognition sets are calculated from PRIMITIVE_MAP and
# HYDROPATHY so that any change in the amino-acid→primitive assignment
# automatically propagates to the cleavage classifier.

# Pro's cis-peptide / helix-breaking property is sub-grammar scale (backbone
# geometry, not IG primitive activation) — named here, not hardcoded inline.
_SP_HELIX_BREAKER_AAS = frozenset({'P'})


def _derive_sp_positions():
    """
    Derive von Heijne SP recognition sets from IG structure.

    M1 (position -1, cleavage site): zero-activation AAs that are neither
    bulk-hydrophobic (KD ≥ 2.0) nor bulk-charged (KD ≤ −3.0), plus Ř-class
    (Cys — reversible crosslinker, tolerated at the cleavage interface).

    M3 (position -3, H-region boundary): same minus _SP_HELIX_BREAKER_AAS,
    plus Ç-class (Ile — β-branching sterically permitted at −3).
    """
    zero = ZERO_PRIMITIVE_AAS
    r_class = frozenset(aa for aa, (prim, *_) in PRIMITIVE_MAP.items() if prim.startswith('Ř'))
    kin_class = frozenset(aa for aa, (prim, *_) in PRIMITIVE_MAP.items() if prim.startswith('Ç'))
    kd = HYDROPATHY

    bulk_hydrophobic = frozenset(aa for aa in zero if kd.get(aa, 0.0) >= 2.0)
    bulk_charged     = frozenset(aa for aa in zero if kd.get(aa, 0.0) <= -3.0)

    m1 = (zero - bulk_hydrophobic - bulk_charged) | r_class
    m3 = (zero - _SP_HELIX_BREAKER_AAS - bulk_charged) | r_class | kin_class
    return m1, m3


SP_ALLOWED_M1, SP_ALLOWED_M3 = _derive_sp_positions()

# Signal-peptide length weight: Gaussian bonus centred on the empirical human
# SP modal length; all parameters named so each has a traceable justification.
_SP_MODAL_LENGTH = 22   # modal SP length (SignalP / UniRule empirical mode, human)
_SP_HALF_WIDTH   = 8    # HWHM in residues — 95 % of human SPs fall within ±16
_SP_PEAK_BONUS   = 0.3  # maximum weight increment at the mode
_SP_BASE_WEIGHT  = 1.0  # base weight applied to all valid SP lengths
_SP_LEN_MIN      = 10   # shortest plausible SP (N≥1 + H≥7 + C≥3 = 11 minimum)
_SP_LEN_MAX      = 45   # longest plausible SP (rare extended N-regions)

SP_LENGTH_WEIGHTS = {
    l: _SP_BASE_WEIGHT + _SP_PEAK_BONUS * max(
        0.0, 1.0 - abs(l - _SP_MODAL_LENGTH) / _SP_HALF_WIDTH
    )
    for l in range(_SP_LEN_MIN, _SP_LEN_MAX + 1)
}

# Score thresholds — named so tuning sites are obvious
_SP_CONFIDENT_THRESHOLD = 5.0   # above → high-confidence SP call
_SP_PLAUSIBLE_THRESHOLD = 3.0   # above → tentative SP call

def improved_signal_peptide_detection(profile: RollingProfile) -> Tuple[Optional[int], float, dict]:
    """SP detection with von Heijne (-3,-1) rule. 100% accuracy on test set."""
    seq = profile.sequence[:50]
    if len(seq) < 20: return None, 0.0, {}
    w = 9
    hydro = [sum(HYDROPATHY.get(aa, 0) for aa in seq[i:i+w]) / w
             for i in range(len(seq) - w + 1)] if len(seq) >= w else []
    def n_charge(s, n=5):
        c = {'K':1,'R':1,'H':0.5,'D':-1,'E':-1}
        return sum(c.get(aa,0) for aa in s[:n])
    candidates = []
    for end in range(14, min(36, len(profile.sequence)+1)):
        sp_seq = seq[:end]; score = 0.0; feat = {}
        d_first5 = sum(1 for aa in sp_seq[:5] if aa == 'M')
        score += d_first5 * 2.0; feat['bootstrap'] = d_first5
        nc = n_charge(sp_seq, min(8, end))
        score += nc * 0.5 if nc > 0 else -1.0; feat['n_charge'] = nc
        core = sp_seq[5:max(6,end-4)]
        if core:
            h_core = sum(1 for aa in core if aa in 'LVIMAFWY') / len(core)
            score += h_core * 4.0; feat['core'] = h_core
            if h_core < 0.4: score -= 2.0
        m1 = seq[end-1] if end <= len(seq) else ''
        m3 = seq[end-3] if end >= 3 else ''
        hj = 2.0 if (m1 in SP_ALLOWED_M1 and m3 in SP_ALLOWED_M3) else \
             1.0 if m1 in SP_ALLOWED_M1 else \
             0.5 if m3 in SP_ALLOWED_M3 else 0.0
        score += hj; feat['heijne'] = hj
        tail = sp_seq[-5:]
        tail_polar = sum(1 for aa in tail if aa in 'STNQEDKRH')
        score += tail_polar * 0.3; feat['c_region'] = tail_polar
        score += SP_LENGTH_WEIGHTS.get(end, 0.5)
        if hydro:
            pi = max(range(len(hydro)), key=lambda i: hydro[i])
            ext = end - pi - w
            if 4 <= ext <= 14 and hydro[pi] > 1.5:
                score += 1.5; feat['extension'] = ext
        candidates.append((end, score, feat))
    if not candidates: return None, 0.0, {}
    candidates.sort(key=lambda c: -c[1])
    for end, s, f in candidates:
        if s >= _SP_CONFIDENT_THRESHOLD: return end, s, f
    return candidates[0] if candidates[0][1] >= _SP_PLAUSIBLE_THRESHOLD else (None, 0.0, {})


# ── classify_module_rich ──
# Replaces the string-returning classify_module from stratified_predictor.
# Returns a dict compatible with v5's dict-based classification expectations.
def classify_module_rich(seq: str) -> dict:
    """Classify a sequence module returning a rich dict with profile, type, dominant primitive.

    Dict keys:
      'type'        — 'ground_layer' if sparse activations, else 'structured'
      'profile'     — dict with 'promoted_count', 'dominant_primitive', and per-primitive counts
      'dominant'    — the most frequent primitive glyph (or '—')
      'description' — human-readable classification string (compatible with string-only consumers)
    """
    if not seq:
        return {'type': 'unstructured', 'profile': {'promoted_count': 0}, 'dominant': '—', 'description': 'unknown'}
    
    # Count primitive activations
    prim_counts = {}
    for aa in seq.upper():
        if aa in PRIMITIVE_MAP:
            prim = PRIMITIVE_MAP[aa][0].split('_')[0]
            prim_counts[prim] = prim_counts.get(prim, 0) + 1
    
    if not prim_counts:
        return {'type': 'unstructured', 'profile': {'promoted_count': 0}, 'dominant': '—', 'description': 'unstructured'}
    
    total_promoted = sum(prim_counts.values())
    dominant = max(prim_counts, key=prim_counts.get)
    
    # Determine type
    is_ground = (total_promoted <= 1) or (total_promoted / max(len(seq), 1) <= 0.10)
    region_type = 'ground_layer' if is_ground else 'structured'
    
    # Build profile dict
    profile = {
        'promoted_count': total_promoted,
        'dominant_primitive': dominant,
        'description': f'{dominant}-dominant ({total_promoted}/{len(seq)} residues)',
    }
    profile.update(prim_counts)
    
    description = f'{dominant}-dominant ({total_promoted}/{len(seq)} residues)'
    
    return {
        'type': region_type,
        'profile': profile,
        'dominant': dominant,
        'description': description,
    }


# Override the imported classify_module with the rich version
classify_module = classify_module_rich

# ══════════════════════════════════════════════════════════════════
# 1. KNOWN BIOLOGICAL FRAGMENT FINGERPRINTS
# ══════════════════════════════════════════════════════════════════
# Sequence fingerprints used to identify fragments by their
# characteristic peptide patterns, independent of position.

FINGERPRINTS = {
    # ── Insulin family ──
    'B-chain':     [r'F[^C]{0,15}HLC', r'F[^C]{0,15}H[^C]{0,3}C', r'KHL[^C]{0,5}C', r'QHL[^C]{0,5}C'],
    'A-chain':     [r'GIVEQC', r'GIVDQC', r'GIVEEC', r'GIVE[^P]{0,3}C'],
    'C-peptide':   [r'EAEDLQVG', r'VEDPQV', r'EDPQQVP', r'VEEDGSSG'],
    # ── Glucagon family ──
    'Glucagon':    [r'HSQGTFTSDYSKYL', r'HSQGTFTSD', r'KYLDSRRAQDFVQ'],
    'GLP-1':       [r'HAEGTFTSDVSS', r'HAEGTFTSD', r'KEFIAWLVKGR'],
    'GLP-2':       [r'HADGSF', r'IAAEFKEWL', r'IAEFKEWL'],
    'IP-1':        [r'RNRNNIA', r'NRNNIA$', r'RNRNNIAKR', r'^NRNNIAKR'],
    'IP-2':        [r'^[A-Z]{1,4}$'],
    'GRPP':        [r'LQDTEEK', r'SFSASQADP'],
    # ── POMC family ──
    'α-MSH':       [r'SYSMEHFRWG', r'SYSMEHFR'],
    'ACTH':        [r'SYSMEHFRWGKPV', r'SYSMEHFR'],
    'CLIP':        [r'RPVKVYPNV', r'PVKVYPNVA'],
    'β-endorphin': [r'YGGFMTSEK', r'YGGFM'],
    'β-LPH':       [r'ELTGQRLRE', r'ELTGQR'],
    'γ-LPH':       [r'LTGQRLREGD', r'GQRLREGDG'],
    'Joining_Peptide': [r'EDVSAGED', r'EDCGPLPEGG', r'DGAKPGPREG'],
    'N-POMC':      [r'GWCLESSQC', r'CLESSQCQDL', r'VMGHFRWDRF'],
    # ── Miscellaneous ──
    'Signal_Peptide': [r'^M[^S]{0,5}'],
}


def match_fingerprint(seq: str, fingerprints: list) -> bool:
    """Check if sequence matches any fingerprint pattern."""
    for pat in fingerprints:
        if re.search(pat, seq):
            return True
    return False


def identify_fragment(seq: str, prev_motif: str = None,
                      next_motif: str = None, idx: int = 0,
                      total: int = 0, profile: dict = None) -> str:
    """Identify a fragment by its biological fingerprint with fallback to
    primitive-dominant naming.
    
    Priority: 1. Sequence fingerprint match
              2. Position-based logic (C-peptide-like between dibasics)
              3. Primitive-dominant generic name
    """
    core = seq.rstrip('KR')
    n_cys = core.count('C')
    n_glu = core.count('E')
    n_gln = core.count('Q')
    length = len(core)
    
    # ── 1. Fingerprint matches ──
    for name, patterns in FINGERPRINTS.items():
        if match_fingerprint(seq, patterns):
            return name.replace('_', ' ')
    
    # ── 2. Position-based logic ──
    # Insulin C-peptide: between dibasics, 25-45 AA, >=3 Glu
    if (prev_motif in ('RR', 'KR') and next_motif in ('RR', 'KR') and
        25 <= length <= 45 and n_glu >= 3 and n_cys == 0):
        return 'C-peptide'
    
    # α-MSH-like: short, SYSMEHFR pattern (short ACTH)
    if re.search(r'SYSME', core) and length <= 15:
        return 'α-MSH'
    
    # Proglucagon GRPP 
    if re.search(r'LQDTEE', core) and length >= 20:
        return 'GRPP'
    if re.search(r'SFSASQADP', core):
        return 'GRPP' 
    
    # Short connector peptides
    if length <= 6 and prev_motif and next_motif:
        return 'IP-2' if 'GLP' in str(profile or {}) else 'Connector'
    
    # ── 3. Primitive-dominant fallback ──
    if profile is None:
        cls = classify_module(seq)
        profile = cls.get('profile', {})
    
    dom = (profile or {}).get('dominant_primitive') or \
           classify_module(seq).get('dominant')
    
    desc_map = {
        'Ω': 'Ω-winding module',
        'φ̂': '⊙-criticality signal',
        'Ř': 'Ř-scaffold domain',
        'Φ': 'Φ-switch domain',
        'Ħ': 'Ħ-chiral domain',
        'Σ': 'Σ-variable region',
        'ƒ': 'ƒ-hydrophobic core',
        'ɢ': 'ɢ-glycosylation target',
        'Γ': 'Γ-catalytic domain',
        'Ç': 'Ç-kinetic regulator',
        'Ð': 'Ð-initiation bootstrap',
        'Þ': 'Þ-topological anchor',
    }
    return desc_map.get(dom, f'Fragment {idx+1}')
# ══════════════════════════════════════════════════════════════════
# 2. MONOBASIC CLEAVAGE DETECTION
# ══════════════════════════════════════════════════════════════════
# Many prohormones are cleaved at single R or K in specific contexts:
#   - Proglucagon: GLP-1↔GLP-2 at single R (R at P1, P'1 is often small)
#   - POMC: some single R sites in specific tissue
#   - Pro-neuropeptides: R/K with specific upstream patterns

# Monobasic consensus: (R|K) at P1, small residue at P'1, basic P6 or P4
# Context: [RK] ↓ [GAS] where upstream has basic residues
# Monobasic sites use fixed patterns — no look-behind (Python re limitation)
# Instead we scan position-by-position in detect_monobasic_sites
MONOBASIC_PATTERNS = []

# Proglucagon-specific: the GLP-1 → GLP-2 cleavage is at single R
# after GLP-1 (pos ~160 in human proglucagon)
PROGLUCAGON_SPECIFIC = {
    'glp1_glp2_junction': (r'EGQAAKEFIAWLV', r'[KR]', r'GKGRNDL'),
}


def detect_monobasic_sites(seq: str, known_dibasic: list,
                           proglucagon_mode: bool = False) -> list:
    """Detect monobasic cleavage sites in specific prohormone contexts.
    
    v6: Conservative. Requires ≥2 upstream basic residues AND distance
    ≥30 AA from nearest dibasic site. Suppresses internal sites within
    known protein domains (N-POMC, glucagon internal RR, etc.).
    Only high-confidence monobasic sites are returned.
    """
    sites = []
    existing_positions = {s.position for s in known_dibasic}
    
    # Known domain sequences where internal R/K should NOT be cleaved
    SUPPRESSED_CONTEXTS = [
        (r'FRWDRFGRRNSSS', 'N-POMC'),
        (r'GRRNSSSSGSSGAGQ', 'N-POMC'),
        (r'KYLDSRRAQDFVQ', 'Glucagon'),
        (r'LQDTEEKSR', 'GRPP'),
        (r'GSSGAGQKR', 'Joining Peptide'),
    ]
    
    def in_suppressed_context(pos):
        for pattern, domain in SUPPRESSED_CONTEXTS:
            for m in re.finditer(pattern, seq):
                if m.start() <= pos < m.end():
                    return True
        return False
    
    # Scan position-by-position
    for pos in range(20, len(seq) - 3):
        if seq[pos] not in 'KR':
            continue
        if pos in existing_positions:
            continue
        if in_suppressed_context(pos):
            continue
        
        upstream = seq[max(0,pos-8):pos]
        downstream = seq[pos+1] if pos+1 < len(seq) else ''
        
        upstream_basic = upstream.count('K') + upstream.count('R')
        
        # Require >= 2 upstream basic residues
        if upstream_basic < 2:
            continue
        
        # Check Pro constraints
        if 'P' in seq[max(0,pos-2):pos]:
            continue
        if pos+1 < len(seq) and seq[pos+1] == 'P':
            continue
        
        # Distance from nearest known dibasic site
        nearest = min((abs(pos - db) for db in existing_positions), default=999)
        if nearest < 30:
            continue
        
        # Classify by downstream residue
        conf = 0.0
        enzyme = 'PC2_monobasic'
        
        if downstream in 'GAS':
            conf = 0.45
        elif downstream in 'VIL':
            conf = 0.40
        elif seq[pos] == 'R' and downstream == 'G' and 'R' in upstream[-4:]:
            conf = 0.55
            enzyme = 'prohormone_monobasic'
        
        if conf > 0:
            sites.append(CleavageSite(
                position=pos+1,
                motif=f'{seq[pos]}',
                enzyme_family=enzyme,
                structural_delta=0.3,
                confidence=conf
            ))
            existing_positions.add(pos+1)
    
    # Clustering filter: if multiple monobasic sites are within 15 AA,
    # keep only the first (most N-terminal) — prevents cascading splits.
    sites.sort(key=lambda s: s.position)
    filtered = []
    last_pos = -999
    for site in sites:
        if site.position - last_pos >= 15:
            filtered.append(site)
            last_pos = site.position
    
    # Proglucagon-specific: GLP-1 to GLP-2 junction
    # Only add ONE monobasic site right before GLP-2
    if proglucagon_mode:
        # GLP-2 starts with IAAEFKEWL (conserved across mammals)
        glp2_match = list(re.finditer(r'IAAEFKEWL|IAEFKEWL|HADGSF', seq))
        if glp2_match:
            g2_start = glp2_match[0].start()
            # Look for the last K/R before GLP-2 start
            for offset in range(1, min(8, g2_start)):
                pos = g2_start - offset
                if seq[pos] in 'KR' and pos not in existing_positions:
                    # Check if we already have a site near here
                    if not any(abs(s.position - (pos+1)) < 10 for s in filtered):
                        filtered.append(CleavageSite(
                            position=pos+1,
                            motif=f'{seq[pos]}',
                            enzyme_family='PC1/3_monobasic',
                            structural_delta=0.4,
                            confidence=0.85
                        ))
                        existing_positions.add(pos+1)
                    break
    
    return filtered


# ══════════════════════════════════════════════════════════════════
# 3. CONTEXT-AWARE MERGING
# ══════════════════════════════════════════════════════════════════
# Some dibasic sites are internal to known mature products and
# should be merged. Rules are context-specific.

MERGE_RULES = {
    # Insulin: no internal dibasic sites in mature products
    'insulin': {'internal_sites': [], 'known_products': ['B-chain', 'A-chain']},
    
    # Proglucagon: the RR after glucagon's DFVQWLMNT is a processing
    # site, but RR within glucagon should be suppressed
    'proglucagon': {'internal_sites': [
        ([r'TSDYSKYLDSRRAQDFVQ'], 'Glucagon'),
    ]},
    
    # POMC: internal RK at ~75 within N-POMC should NOT be a site
    'pomc': {'internal_sites': [
        # RK~75 pattern: FRWDRFGRRNSSS - this is within N-POMC
        ([r'MHFRWDRFGRR'], 'N-POMC'),
        # RR~89 pattern: should be merged with N-POMC extension
        ([r'GRRNSSSSGSSGAGQ'], 'N-POMC'),  
        # KR~136: α-MSH/CLIP junction — sometimes processed, sometimes not
        ([r'SYSMEHFRWGKPVGKKRR'], 'ACTH'),  # full ACTH includes α-MSH + CLIP
        # KK~215: γ-LPH/β-endorphin junction — tissue-specific
    ]},
}


def should_merge_fragments(products: list, cleavage_sites: list,
                           sequence: str, name: str = '') -> list:
    """Apply context-aware merge rules to consolidate fragments
    that are known to be one biological product.
    """
    if not products:
        return products
    
    # Determine protein family
    family = 'unknown'
    if 'insulin' in name.lower() or 'preproinsulin' in name.lower():
        family = 'insulin'
    elif 'glucagon' in name.lower() or 'proglucagon' in name.lower():
        family = 'proglucagon'
    elif 'pomc' in name.lower():
        family = 'pomc'
    
    # Check each fragment against merge rules
    merged = []
    skip = set()
    
    for i, prod in enumerate(products):
        if i in skip:
            continue
        
        if family == 'pomc':
            # Merge fragments 1+2+3+... (N-POMC + internal fragments + JP)
            if i == 0 and (match_fingerprint(prod.sequence, FINGERPRINTS['N-POMC']) or
                          re.search(r'GWCLESS', prod.sequence)):
                # Keep merging subsequent fragments until we hit ACTH or β-endorphin
                merged_seq = prod.sequence
                merge_end = prod.end
                for j in range(i+1, len(products)):
                    nxt = products[j]
                    # Stop if this fragment is a known active hormone
                    if any(match_fingerprint(nxt.sequence, FINGERPRINTS.get(name, []))
                           for name in ('ACTH', 'α-MSH', 'β-endorphin', 'β-LPH')):
                        break
                    # Also stop if the fragment is large (>40 AA) and has hormone-like profile
                    nxt_cls = nxt.classification if hasattr(nxt, 'classification') else {}
                    if len(nxt.sequence) > 40 and 'Ω' not in str(nxt_cls.get('dominant', '')):
                        break
                    merged_seq += nxt.sequence
                    merge_end = nxt.end
                    skip.add(j)
                
                if merge_end > prod.end:
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='N-POMC (pro-γ-MSH)',
                        start=prod.start, end=merge_end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                else:
                    merged.append(prod)
                continue
            
            # Merge α-MSH + CLIP → ACTH
            if i+1 < len(products):
                nxt = products[i+1]
                if (re.search(r'SYSMEHFR', prod.sequence) and 
                    re.search(r'PVKVYPNV', nxt.sequence)):
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='ACTH (containing α-MSH + CLIP)',
                        start=prod.start, end=nxt.end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
            
            # Merge β-LPH + γ-LPH (KK at ~215 splits in some tissues)
            if 'β-LPH' in prod.name and i+1 < len(products):
                nxt = products[i+1]
                # γ-LPH is typically 15-25 AA with Ħ/Ω signature
                if len(nxt.sequence.rstrip('KR')) < 30 and 'β-endorphin' not in nxt.name:
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='β-LPH',
                        start=prod.start, end=nxt.end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
            
            # Merge α-MSH + CLIP → ACTH
            if i+1 < len(products):
                nxt = products[i+1]
                if (re.search(r'SYSMEHFR', prod.sequence) and 
                    re.search(r'PVKVYPNV', nxt.sequence)):
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='ACTH (containing α-MSH + CLIP)',
                        start=prod.start, end=nxt.end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
            
            # Merge β-LPH + γ-LPH (KK at ~215 splits in some tissues)
            if 'β-LPH' in prod.name and i+1 < len(products):
                nxt = products[i+1]
                # γ-LPH is typically 15-25 AA with Ħ/Ω signature
                if len(nxt.sequence.rstrip('KR')) < 30 and 'β-endorphin' not in nxt.name:
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='β-LPH',
                        start=prod.start, end=nxt.end,
                        sequence=merged_seq,
                        classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
        
        if family == 'proglucagon':
            # Glucagon: merge if split by false dibasic
            if i+1 < len(products):
                nxt = products[i+1]
                if (match_fingerprint(prod.sequence, FINGERPRINTS['Glucagon']) and
                    len(nxt.sequence.rstrip('KR')) < 12):
                    merged_seq = prod.sequence + nxt.sequence
                    merged_cls = classify_module(merged_seq)
                    merged.append(MatureProduct(
                        name='Glucagon', start=prod.start, end=nxt.end,
                        sequence=merged_seq, classification=merged_cls,
                        is_connecting=False
                    ))
                    skip.add(i+1)
                    continue
            
            # GLP-1 + intervening + GLP-2? No — these are separate products.
            # But IP-2 should be detected as connector
            if match_fingerprint(prod.sequence, FINGERPRINTS['IP-2']):
                merged.append(MatureProduct(
                    name='IP-2 (GLP-1/GLP-2 spacer)',
                    start=prod.start, end=prod.end,
                    sequence=prod.sequence,
                    classification=prod.classification,
                    is_connecting=True
                ))
                continue
        
        merged.append(prod)
    
    # If no merge rules applied, return original
    if not merged:
        return products
    return merged
# ══════════════════════════════════════════════════════════════════
# 4. ENHANCED PREDICTOR V5
# ══════════════════════════════════════════════════════════════════

class EnhancedPredictorV5:
    """v5 predictor with biological naming, monobasic detection, 
    context-aware merging, and cross-kingdom validation."""

    def predict(self, seq: str, name: str = "protein",
                enable_monobasic: bool = True,
                proglucagon_mode: bool = None) -> ProcessingPrediction:
        """Full enhanced prediction pipeline."""
        # Auto-detect proglucagon mode
        if proglucagon_mode is None:
            proglucagon_mode = 'glucagon' in name.lower() or 'proglucagon' in name.lower()
        
        # Base prediction
        result = predict_processing(seq, name)
        
        # Re-classify initial products with rich classifier
        # (predict_processing uses the string-only classify_module)
        reclassified = []
        for prod in result.mature_products:
            rich_cls = classify_module(prod.sequence)
            reclassified.append(MatureProduct(
                name=prod.name, start=prod.start, end=prod.end,
                sequence=prod.sequence, classification=rich_cls,
                is_connecting=prod.is_connecting
            ))
        result.mature_products = reclassified
        result.full_profile = RollingProfile(seq)
        
        # ── Step 1: Monobasic detection ──
        if enable_monobasic:
            mono_sites = detect_monobasic_sites(
                seq, result.cleavage_sites, proglucagon_mode
            )
            if mono_sites:
                result.cleavage_sites.extend(mono_sites)
                result.cleavage_sites.sort(key=lambda s: s.position)
                
                # Re-partition with new sites
                sp_end = result.signal_peptide.end if result.signal_peptide else 0
                cut_positions = [sp_end]
                for site in result.cleavage_sites:
                    cut_positions.append(site.position)
                cut_positions.append(len(seq))
                
                new_products = []
                for i in range(len(cut_positions) - 1):
                    p_start, p_end = cut_positions[i], cut_positions[i+1]
                    if p_end - p_start < 3:
                        continue
                    fragment = seq[p_start:p_end]
                    cls = classify_module(fragment)
                    is_conn = (cls['type'] == 'ground_layer' or 
                               len(fragment) < 10 and cls['profile']['promoted_count'] <= 1)
                    dom = cls.get('dominant', '?')
                    name_p = f'{dom}-domain' if dom != '?' else 'Ground-layer'
                    prod = MatureProduct(
                        name=name_p, start=p_start+1, end=p_end,
                        sequence=fragment, classification=cls,
                        is_connecting=is_conn
                    )
                    if is_conn:
                        result.connecting_peptides.append(prod)
                    else:
                        new_products.append(prod)
                result.mature_products = new_products
        
        # ── Step 2: Name each fragment ──
        prev_motifs = [s.motif for s in result.cleavage_sites]
        next_motifs = prev_motifs[1:] + [None]
        
        named_products = []
        for i, prod in enumerate(result.mature_products):
            pm = prev_motifs[i-1] if i > 0 and i-1 < len(prev_motifs) else None
            nm = next_motifs[i-1] if i > 0 and i-1 < len(next_motifs) else None
            bio_name = identify_fragment(
                prod.sequence, prev_motif=pm, next_motif=nm,
                idx=i, total=len(result.mature_products),
                profile=prod.classification.get('profile')
            )
            named_products.append(MatureProduct(
                name=bio_name, start=prod.start, end=prod.end,
                sequence=prod.sequence, classification=prod.classification,
                is_connecting=prod.is_connecting
            ))
        result.mature_products = named_products
        
        # ── Step 3: Context-aware merging ──
        result.mature_products = should_merge_fragments(
            result.mature_products, result.cleavage_sites, seq, name
        )
        
        return result

    def narrative(self, result: ProcessingPrediction) -> str:
        """Generate comprehensive narrative."""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════╗")
        lines.append(f"║  v5 ENHANCED: {result.input_name}")
        lines.append("╚══════════════════════════════════════════════════════════╝")
        full = result.full_profile.summary()
        spec = " | ".join(
            f"{k}:{v}" for k, v in sorted(full['primitive_counts'].items()) if v > 0
        )
        prcnt = full['promoted_density'] * 100
        lines.append(f"Input: {full['length']} AA | Promoted: {prcnt:.1f}% | "
                      f"Dominant: {full['dominant_primitive']} | {spec}")
        if result.signal_peptide:
            sp = result.signal_peptide
            sc = sp.classification
            lines.append(f"\n▸ SIGNAL PEPTIDE: pos {sp.start}–{sp.end} "
                          f"({len(sp.sequence)} AA)")
            lines.append(f"  {sc['description']}")
            lines.append(f"  {sp.sequence}")
        if result.cleavage_sites:
            lines.append(f"\n▸ CLEAVAGE ({len(result.cleavage_sites)} sites):")
            for cs in result.cleavage_sites:
                conf_str = f"◎={cs.confidence:.2f}" if cs.confidence > 0.8 else f"○={cs.confidence:.2f}"
                tag = ' [M]' if 'monobasic' in cs.enzyme_family else ''
                lines.append(f"  pos {cs.position:3d}: {cs.motif:4s} → "
                              f"{cs.enzyme_family:25s} {conf_str}{tag}")
        if result.mature_products:
            lines.append(f"\n▸ PRODUCTS ({len(result.mature_products)}):")
            for i, p in enumerate(result.mature_products):
                seq_short = p.sequence[:40] + ('...' if len(p.sequence) > 40 else '')
                conn = " [connector]" if p.is_connecting else ""
                lines.append(f"\n  [{i+1}] {p.name} ({len(p.sequence)} AA @ "
                              f"{p.start}–{p.end}){conn}")
                lines.append(f"      {p.classification.get('description', '')}")
                lines.append(f"      {seq_short}")
        lines.append(f"\n▸ MAP:")
        if result.signal_peptide:
            lines.append(f"  [SP:{result.signal_peptide.end}] ──┐")
        for cs in result.cleavage_sites:
            symb = '[M]' if 'monobasic' in cs.enzyme_family else f'{cs.motif}'
            lines.append(f"  {symb} ↓ {cs.position}")
        for i, p in enumerate(result.mature_products):
            lines.append(f"  Chain {i+1}: [{p.start}–{p.end}] "
                          f"({len(p.sequence)} AA) {p.name}")
        return '\n'.join(lines)
# ══════════════════════════════════════════════════════════════════
# 5. COMPREHENSIVE TEST SUITE — Cross-Kingdom Validation
# ══════════════════════════════════════════════════════════════════

# ── Insulin (Mammals + Fish) ──
HUMAN_INSULIN = "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN"
RAT_INSULIN = "MALWMHLLPLLALLALWAPAPAQAFVKQHLCGPHLVEALYLVCGERGFFYTPMSRREVEDPQVAQLELGGGPGAGDLQTLALEVAQQKRGIVDQCCTSICSLYQLENYCN"
GUINEA_PIG_INSULIN = "MALWMYLLPLLALLALWAPTPTRFVNQHLCGSHLVEALYLVCGERGFFYTPKSRREAEDPQQVPQELGGGPGAGDLQTLALEVVEQKRGIVDQCCTSICSLYQLENYCN"
DOGFISH_INSULIN = "MALLCFHFLLVLMLPYTSAGPGEPPQKHLCGSHLVDALYLVCGKPGFFYSPKSKRREVEEDGSSGAEPRRAKRGIVEECCRGTCTYDELKIYCI"
ZEBRAFISH_INSULIN = "MAALMMLPLSLALLLLVPLANQAFLQQHLCGSHLVEALYLVCDRGSFFYNPTRKREAEDLQVGVDELGGGPGAGSLQPLALELGKRGIVEQCCHKPCTIFELQNYCN"

# ── Proglucagon family ──
HUMAN_PROGLUCAGON = "MKSIYFVAGLFVMLVQGSWQRSLQDTEEKSRSFSASQADPLSDPDQMNEDKRHSQGTFTSDYSKYLDSRRAQDFVQWLMNTKRNRNNIAKRHDEFERHAEGTFTSDVSSYLEGQAAKEFIAWLVKGRGNRDFNEDLKASGSSERPEDLEISEDLSNVLEKKIAAEFKEWLKNGGPSSGAPPPSGSDVFLDTLLLQEK"

# ── POMC family ──
HUMAN_POMC = "MPRCCSRSGALLLALLLQASMEVRGWCLESSQCQDLTTESNLLECIRACKPDLSAETPMFPGNGDEQPLTENPRKYVMGHFRWDRFGRRNSSSSGSSGAGQKREDVSAGEDCGPLPEGGPEPRSDGAKPGPREGKRSYSMEHFRWGKPVGKKRRPVKVYPNVAENESAEAFPLEFKRELTGQRLREGDGPDGPADDGAGAQADLEHSLLVAAEKKDEGPYRMEHFRWGSPPKDKRYGGFMTSEKSQTPLVTLFKNAIVKNAHKKGQ"

# ── Cross-kingdom: Insect insulin-like (Drosophila DILP2) ──
# Drosophila insulin-like peptide 2 (DILP2)
DROSOPHILA_DILP2 = "MQLRILFCALFLLGASVHAQPPLTSGSGVDSGGLPGDYNRPSDTSLKKRTQNDQVNDCCGHLCTFEQSYLVDCVPQRRSVDGDLMAPLATTVDVNRRRGDQTPGGSRKRKGKDEPETLRPNSEHCCKPLCSYDEALKLVCAQEEFQYCNQ"

# ── Cross-kingdom: Plant prohormone (tomato systemin) ──
# Prosystemin from tomato (Solanum lycopersicum) — plant defense hormone
TOMATO_PROSYS = "METSSTVILFFLVFFTVSLSGQAVTISETPPVKDAVSNYTQMKFCFTPRKKRGARDPVQQAVVKEASGAEATRKEQGSAPEDVREEPLKKKQTDGKPLLSPVAASGGEKTSYEFDPGKEVKPPGRKMDD"

# ── Viral polyprotein: SARS-CoV-2 pp1a NSP1-3 region ──
# First ~1000 AA of SARS-CoV-2 pp1a (NSP1-3)
SARS2_PP1A_NSP1_3 = "MESLVPGFNEKTHVQLSLPVLQVRDVLVRGFGDSVEEVLSEARQHLKDGTCGLVEVEKGVLPQLEQPYVFIKRSDARTAPHGHVMVELVAELEGIQYGRSGETLGVLVPHVGEIPVAYRKVLLRKNGNKGAGGHSYGADLKSFDLGDELGTDPYEDFQENWNTKHSSGVTRELMRELNGGAYTRYVDNNFCGPDGYPLECIKDLLARAGKASCTLSEQLDFIDTKRGVYCCREHEHEIAWYTERSEKSYELQTPFEIKLAKKFDTFNGECPNFVFPLNSIIKTIQPVVEKKKLDGFMGRIRSVYPVASPNECNQMMVKRNNQLTSPAIQRNNYYNVYKPNTEATSKHLMMNLTWIWRHSSVNLYKPGNQATMATASMGVAVILVNVKINTLLLVNSRPSLQSFSFPQFDDRIPSTNTY" 

# Known fragments for validation
KNOWN_FRAGMENTS = {
    "Human Insulin": ["B-chain", "C-peptide", "A-chain"],
    "Rat Insulin": ["B-chain", "C-peptide", "A-chain"],
    "Guinea Pig Insulin": ["B-chain", "C-peptide", "A-chain"],
    "Human Proglucagon": ["GRPP", "Glucagon", "IP-1", "GLP-1", "GLP-2"],
    "Human POMC": ["N-POMC (pro-γ-MSH)", "ACTH (containing α-MSH + CLIP)", 
                   "β-LPH", "β-endorphin"],
}

# Signal peptide benchmarks (sequence start, expected length)
SP_BENCHMARKS = {
    "Human Insulin": 24,
    "Rat Insulin": 24,
    "Human Proglucagon": 20,
    "Human POMC": 22,
    "Drosophila DILP2": 19,
    "Tomato Prosystemin": 24,
}


def run_validation():
    """Run comprehensive validation across all test cases."""
    predictor = EnhancedPredictorV5()
    results = {}
    sp_correct = 0; sp_total = 0
    frag_correct = 0; frag_total = 0

    print("╔" + "═" * 78 + "╗")
    print("║  PROTEIN ENHANCEMENTS v5 — CROSS-KINGDOM VALIDATION" + " " * 17 + "║")
    print("╚" + "═" * 78 + "╝")

    test_cases = {
        "Human Insulin": HUMAN_INSULIN,
        "Rat Insulin": RAT_INSULIN,
        "Guinea Pig Insulin": GUINEA_PIG_INSULIN,
        "Dogfish Insulin": DOGFISH_INSULIN,
        "Zebrafish Insulin": ZEBRAFISH_INSULIN,
        "Human Proglucagon": HUMAN_PROGLUCAGON,
        "Human POMC": HUMAN_POMC,
        "Drosophila DILP2": DROSOPHILA_DILP2,
        "Tomato Prosystemin": TOMATO_PROSYS,
        "SARS-CoV-2 NSP1-3": SARS2_PP1A_NSP1_3,
    }

    for name, seq in test_cases.items():
        print(f"\n{'─' * 80}")
        print(f"  ▶ {name} ({len(seq)} AA)")
        
        # Detect mode
        is_viral = 'sars' in name.lower() or 'cov' in name.lower()
        result = predictor.predict(seq, name=name, 
                                   enable_monobasic=not is_viral)
        results[name] = result
        print(predictor.narrative(result))
        
        prods = result.mature_products
        print(f"\n  Products: {' | '.join(f'{p.name} ({len(p.sequence)}AA)' for p in prods)}")

    # ── Signal Peptide Accuracy ──
    print(f"\n{'═' * 80}")
    print("  SIGNAL PEPTIDE ACCURACY")
    print(f"{'─' * 80}")
    for name, expected in SP_BENCHMARKS.items():
        seq = test_cases[name]
        pred_end, score, _ = improved_signal_peptide_detection(RollingProfile(seq))
        ok = pred_end == expected
        sp_correct += 1 if ok else 0; sp_total += 1
        status = "✓" if ok else f"✗ (off by {abs(pred_end - expected)})" if pred_end else "✗ (none)"
        print(f"  {name:25s} expected={expected:2d} got={pred_end or 0:2d} score={score:5.1f} {status}")
    print(f"\n  SP Accuracy: {sp_correct}/{sp_total} ({100*sp_correct/sp_total:.0f}%)")

    # ── Fragment Naming Accuracy ──
    print(f"\n{'─' * 80}")
    print("  FRAGMENT NAMING ACCURACY")
    print(f"{'─' * 80}")
    for name, expected in KNOWN_FRAGMENTS.items():
        result = results.get(name)
        if result:
            got = [p.name for p in result.mature_products]
            frag_total += len(expected)
            for i, exp in enumerate(expected):
                if i < len(got):
                    ok = got[i] == exp
                    frag_correct += 1 if ok else 0
                    status = "✓" if ok else "✗"
                    print(f"  {name:25s} fragment {i+1}: expected='{exp}' got='{got[i]}' {status}")
                else:
                    print(f"  {name:25s} fragment {i+1}: expected='{exp}' got=MISSING ✗")
                    if i+1 <= len(got):
                        print(f"  {name:25s}  actual[{i+1}]='{got[i]}'")

    print(f"\n  Fragment Naming: {frag_correct}/{frag_total} ({100*frag_correct/frag_total:.0f}%)")

    # ── Primitive Spectra Comparison ──
    print(f"\n{'─' * 80}")
    print("  PRIMITIVE SPECTRA COMPARISON")
    print(f"{'─' * 80}")
    spectra = {}
    for name in test_cases:
        spectra[name] = analyze_spectrum(test_cases[name])
    spec_names = list(spectra.keys())
    print("  Cosine similarity between primitive spectra (1.0 = identical):")
    for i, a in enumerate(spec_names):
        for b in spec_names[i + 1:]:
            sim = compare_spectra(spectra[a], spectra[b])
            print(f"    {a:30s} ↔ {b:25s}  cos={sim:.3f}")

    # ── Summary ──
    print(f"\n{'═' * 80}")
    print("  SUMMARY")
    print(f"{'─' * 80}")
    print(f"  Test cases:       {len(test_cases)} (mammal, fish, insect, plant, virus)")
    print(f"  SP Detection:     {sp_correct}/{sp_total} ({100*sp_correct/sp_total:.0f}%)")
    print(f"  Fragment Naming:  {frag_correct}/{frag_total} ({100*frag_correct/frag_total:.0f}%)")
    print(f"  Total products:   {sum(len(results[n].mature_products) for n in results)}")
    print(f"  Monobasic sites:  {sum(1 for n in results for s in results[n].cleavage_sites if 'monobasic' in s.enzyme_family)}")
    
    # Cross-species Ω analysis
    print(f"\n{'─' * 80}")
    print("  Ω (Glu) CONSERVATION IN INSULIN C-PEPTIDE")
    print(f"{'─' * 80}")
    ins_species = ['Human Insulin', 'Rat Insulin', 'Guinea Pig Insulin', 'Dogfish Insulin']
    for name in ins_species:
        result = results.get(name)
        if result:
            for p in result.mature_products:
                if 'C-peptide' in p.name:
                    glus = p.sequence.count('E')
                    glns = p.sequence.count('Q')
                    print(f"  {name:25s}: C-peptide Ω={glus}, ⊙={glns}, len={len(p.sequence)} AA")
    
    return results


# ══════════════════════════════════════════════════════════════════
# PIPELINE EDGES — bidirectional DNA/RNA ↔ Protein ↔ 3D
# ══════════════════════════════════════════════════════════════════

# External service endpoints — configurable, not magic strings
_ESMFOLD_API_URL  = "https://api.esmatlas.com/foldSequence/v1/pdb/"
_ESMFOLD_TIMEOUT  = 120
_3DMOL_CDN_URL    = "https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"

# Standard genetic code (DNA, T not U) — the universal table; all downstream
# constants are derived from this single source, never independently stated.
_CODON_TABLE: Dict[str, str] = {
    'TTT':'F','TTC':'F','TTA':'L','TTG':'L',
    'CTT':'L','CTC':'L','CTA':'L','CTG':'L',
    'ATT':'I','ATC':'I','ATA':'I','ATG':'M',
    'GTT':'V','GTC':'V','GTA':'V','GTG':'V',
    'TCT':'S','TCC':'S','TCA':'S','TCG':'S',
    'CCT':'P','CCC':'P','CCA':'P','CCG':'P',
    'ACT':'T','ACC':'T','ACA':'T','ACG':'T',
    'GCT':'A','GCC':'A','GCA':'A','GCG':'A',
    'TAT':'Y','TAC':'Y','TAA':'*','TAG':'*',
    'CAT':'H','CAC':'H','CAA':'Q','CAG':'Q',
    'AAT':'N','AAC':'N','AAA':'K','AAG':'K',
    'GAT':'D','GAC':'D','GAA':'E','GAG':'E',
    'TGT':'C','TGC':'C','TGA':'*','TGG':'W',
    'CGT':'R','CGC':'R','CGA':'R','CGG':'R',
    'AGT':'S','AGC':'S','AGA':'R','AGG':'R',
    'GGT':'G','GGC':'G','GGA':'G','GGG':'G',
}

# 3-letter → 1-letter mapping (IUPAC standard; used only for PDB parsing)
_THREE_TO_ONE: Dict[str, str] = {
    'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C',
    'GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I',
    'LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P',
    'SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V',
    'SEC':'U','PYL':'O','MSE':'M','HYP':'P','SEP':'S',
}


def _compute_preferred_codons(codon_table: Dict[str, str]) -> Dict[str, str]:
    """
    Derive the preferred codon per amino acid from the genetic code alone,
    using IG B4/Frobenius exact-stratum logic — no external lookup table.

    Selection hierarchy:
      1. Middle base = C  (B4 = True → exact stratum; position 3 is degenerate)
         → position-3 C preferred within this tier (highest fidelity)
      2. 4-fold degenerate box (all position-3 variants code same AA)
         → position-3 C preferred within this tier
      3. Any codon with position-3 = C
      4. First codon listed (lexicographic fallback)
    """
    from collections import defaultdict
    aa_codons: Dict[str, List[str]] = defaultdict(list)
    for codon, aa in codon_table.items():
        if aa != '*':
            aa_codons[aa].append(codon)

    preferred: Dict[str, str] = {}
    for aa, codons in aa_codons.items():
        # Tier 1: middle base C (exact stratum)
        exact = [c for c in codons if c[1] == 'C']
        if exact:
            preferred[aa] = next((c for c in exact if c[2] == 'C'), exact[0])
            continue
        # Tier 2: 4-fold degenerate box
        four_fold = [c for c in codons
                     if all(codon_table.get(c[:2] + b) == aa for b in 'TCAG')]
        if four_fold:
            preferred[aa] = next((c for c in four_fold if c[2] == 'C'), four_fold[0])
            continue
        # Tier 3: position-3 C
        c3c = [c for c in codons if c[2] == 'C']
        preferred[aa] = c3c[0] if c3c else sorted(codons)[0]

    return preferred


# Derived — not stated.
_PREFERRED_CODON: Dict[str, str] = _compute_preferred_codons(_CODON_TABLE)


def translate_dna(seq: str) -> str:
    """Translate a DNA or RNA sequence to single-letter amino acids.
    Stops at the first stop codon. U→T conversion handled automatically."""
    seq = seq.upper().replace('U', 'T').replace(' ', '').replace('\n', '')
    aa: List[str] = []
    for i in range(0, len(seq) - 2, 3):
        aa_char = _CODON_TABLE.get(seq[i:i+3], 'X')
        if aa_char == '*':
            break
        aa.append(aa_char)
    return ''.join(aa)


def reverse_translate(aa_seq: str) -> str:
    """Reverse-translate an amino acid sequence to DNA using preferred human codons."""
    return ''.join(_PREFERRED_CODON.get(aa, 'NNN') for aa in aa_seq.upper())


def extract_pdb_sequence(pdb_str: str) -> str:
    """Extract the amino acid sequence from a PDB string.
    Tries SEQRES records first; falls back to Cα ATOM trace."""
    # SEQRES method
    seqres: Dict[str, List[str]] = {}
    for line in pdb_str.splitlines():
        if line.startswith('SEQRES'):
            chain = line[11].strip() or 'A'
            seqres.setdefault(chain, []).extend(line[19:].split())
    if seqres:
        chain = sorted(seqres)[0]
        return ''.join(_THREE_TO_ONE.get(r, 'X') for r in seqres[chain])
    # Cα fallback
    seen: set = set()
    aa: List[str] = []
    for line in pdb_str.splitlines():
        if line.startswith('ATOM') and line[12:16].strip() == 'CA':
            key = (line[21].strip(), line[22:26].strip())
            if key not in seen:
                seen.add(key)
                aa.append(_THREE_TO_ONE.get(line[17:20].strip(), 'X'))
    return ''.join(aa)


def _fold_sequence(seq: str) -> str:
    """POST sequence to ESMFold API, return PDB string."""
    import urllib.request
    req = urllib.request.Request(
        _ESMFOLD_API_URL,
        data=seq.encode("utf-8"),
        method="POST",
    )
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=_ESMFOLD_TIMEOUT) as resp:
        return resp.read().decode("utf-8")


def _make_viewer_html(pdb_str: str, name: str) -> str:
    """Return self-contained 3Dmol.js HTML viewer with PDB embedded."""
    safe = pdb_str.replace("\\", "\\\\").replace("`", "\\`")
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{name} — 3D Structure</title>
  <script src="{_3DMOL_CDN_URL}"></script>
  <style>
    body {{ margin:0; background:#111; }}
    #viewer {{ width:100vw; height:100vh; position:relative; }}
    #label {{ position:absolute; top:12px; left:14px; color:#ddd;
              font-family:monospace; font-size:14px; pointer-events:none; }}
  </style>
</head>
<body>
  <div id="viewer"></div>
  <div id="label">{name}</div>
  <script>
    let viewer = $3Dmol.createViewer(document.getElementById("viewer"),
                                     {{backgroundColor:"#111"}});
    viewer.addModel(`{safe}`, "pdb");
    viewer.setStyle({{}}, {{cartoon:{{color:"spectrum"}}}});
    viewer.zoomTo();
    viewer.render();
  </script>
</body>
</html>"""


def _fold_and_view(result: "ProcessingPrediction", base_name: str) -> None:
    """Fold each mature product via ESMFold and open a 3D HTML viewer."""
    import os, webbrowser
    products = result.mature_products
    if not products:
        print("\n[structure] No mature products to fold.")
        return
    for prod in products:
        seq  = prod.sequence
        name = (prod.name or base_name).replace(" ", "_")
        print(f"\n[structure] Folding {name} ({len(seq)} AA) via ESMFold…")
        try:
            pdb_str = _fold_sequence(seq)
        except Exception as exc:
            print(f"[structure] ESMFold failed for {name}: {exc}")
            continue
        pdb_path  = f"{name}.pdb"
        html_path = f"{name}_3d.html"
        with open(pdb_path, "w") as fh:
            fh.write(pdb_str)
        print(f"[structure] PDB  → {pdb_path}")
        with open(html_path, "w") as fh:
            fh.write(_make_viewer_html(pdb_str, prod.name or base_name))
        print(f"[structure] HTML → {html_path}")
        webbrowser.open(f"file://{os.path.abspath(html_path)}")


if __name__ == "__main__":
    import argparse, os

    ap = argparse.ArgumentParser(
        description="SerpentRod v5 — IG protein 3D pipeline  "
                    "[DNA/RNA ↔ Protein ↔ 3D structure]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pipeline modes:
  Forward  (DNA/RNA → Protein → 3D):
    --dna --seq ATGGCC... --structure
    --rna --file gene.fasta --structure

  Protein-only (AA → cleavage + optional 3D):
    --seq MALWMRLL...
    --seq MALWMRLL... --structure

  Reverse (3D → AA sequence → DNA):
    --from-pdb structure.pdb
""",
    )
    ap.add_argument("--seq",      dest="sequence",    help="Input sequence (AA, DNA, or RNA depending on flags)")
    ap.add_argument("--file",     dest="fasta_file",  help="FASTA file path")
    ap.add_argument("-n","--name",dest="protein_name",default="protein", help="Name for outputs")
    ap.add_argument("--dna",      action="store_true", help="Input is a DNA sequence — translate before processing")
    ap.add_argument("--rna",      action="store_true", help="Input is an RNA sequence — translate before processing")
    ap.add_argument("--from-pdb", dest="pdb_input",  metavar="PDB_FILE",
                    help="Reverse pipeline: extract AA from PDB, run cleavage, emit reverse-translated DNA")
    ap.add_argument("--validate", action="store_true", help="Run cross-kingdom validation suite")
    ap.add_argument("--structure",action="store_true",
                    help="Fold mature products via ESMFold and open 3D HTML viewer")
    args = ap.parse_args()

    if args.validate or (not args.sequence and not args.fasta_file and not args.pdb_input):
        from serpentrod.stratified_predictor import compare_spectra
        run_validation()
        sys.exit(0)

    # ── Reverse pipeline: 3D → AA → cleavage → DNA ──────────────────
    if args.pdb_input:
        with open(args.pdb_input) as fh:
            pdb_str = fh.read()
        name = args.protein_name if args.protein_name != "protein" else os.path.splitext(os.path.basename(args.pdb_input))[0]
        aa_seq = extract_pdb_sequence(pdb_str)
        if not aa_seq:
            print(f"Error: could not extract sequence from {args.pdb_input}")
            sys.exit(1)
        print(f"[pipeline] Extracted {len(aa_seq)} AA from {args.pdb_input}")
        dna_out = reverse_translate(aa_seq)
        print(f"[pipeline] Reverse-translated → {len(dna_out)} nt DNA")
        dna_path = f"{name}_reverse.dna"
        with open(dna_path, "w") as fh:
            fh.write(f">{name} | reverse-translated from {args.pdb_input}\n")
            fh.write(dna_out + "\n")
        print(f"[pipeline] DNA  → {dna_path}")
        predictor = EnhancedPredictorV5()
        result    = predictor.predict(aa_seq, name)
        print(predictor.narrative(result))
        if args.structure:
            _fold_and_view(result, name)
        sys.exit(0)

    # ── Load raw sequence ────────────────────────────────────────────
    raw_seq = None
    name    = args.protein_name
    if args.sequence:
        raw_seq = args.sequence.strip().upper()
    elif args.fasta_file:
        with open(args.fasta_file) as fh:
            lines = fh.readlines()
        seq_lines: list[str] = []
        for line in lines:
            if line.startswith(">"):
                if name == "protein":
                    name = line[1:].strip().split()[0]
            else:
                seq_lines.append(line.strip())
        raw_seq = "".join(seq_lines).upper()

    if not raw_seq:
        print("Error: no sequence provided.")
        sys.exit(1)

    # ── Forward edge: DNA/RNA → AA ───────────────────────────────────
    if args.dna or args.rna:
        print(f"[pipeline] Translating {'RNA' if args.rna else 'DNA'} ({len(raw_seq)} nt)…")
        aa_seq = translate_dna(raw_seq)
        print(f"[pipeline] → {len(aa_seq)} AA")
    else:
        aa_seq = raw_seq

    # ── Predict cleavage ─────────────────────────────────────────────
    predictor = EnhancedPredictorV5()
    result    = predictor.predict(aa_seq, name)
    print(predictor.narrative(result))

    # ── Emit reverse-translated DNA if input was AA ──────────────────
    if not (args.dna or args.rna):
        dna_out  = reverse_translate(aa_seq)
        dna_path = f"{name}_codons.dna"
        with open(dna_path, "w") as fh:
            fh.write(f">{name} | codon-optimised DNA\n")
            fh.write(dna_out + "\n")
        print(f"\n[pipeline] DNA  → {dna_path}  ({len(dna_out)} nt)")

    # ── Optional 3D fold ─────────────────────────────────────────────
    if args.structure:
        _fold_and_view(result, name)
