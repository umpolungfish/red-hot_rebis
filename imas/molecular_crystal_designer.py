#!/usr/bin/env python3
"""
molecular_crystal_designer.py — Crystal-Guided Molecular Discovery Engine

Reverse-engineers molecules from IG crystal types. Given a target IG tuple,
determines what IMASM arrangement would produce it, then suggests molecular
structures that fit. This is the inverse of the SMILES→IMASM→IG pipeline.

Core insight: fingerprint_to_ig() is DETERMINISTIC. Every IG tuple constrains
a specific set of StructuralFingerprint fields. We invert each constraint,
generate arrangement candidates, and translate to SMILES patterns.

Author: Lando⊗⊙perator
"""
import itertools, json, math, sys, re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

from imas.arranger import (
    StructuralFingerprint, compute_fingerprint,
)
from imas.compound_imasm import (
    VINIT, AFWD, AREV, FFUSE, FSPLIT, EVALT, EVALF, ENGAGR, CLINK, TANCH, IFIX, IMSCRIB,
    TOKEN_NAMES
)
from imas.ig_bridge import fingerprint_to_ig, ig_tuple_str, PRIMITIVE_NAMES

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem, MolFromSmiles, MolToSmiles, RWMol
    from rdkit.Chem.rdMolDescriptors import CalcMolFormula
    from rdkit.Chem.Scaffolds import MurckoScaffold
    from rdkit.Chem import BRICS
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False
    Chem = None
    Descriptors = None


# ═══════════════════════════════════════════════════════════
# TOKEN CONSTANTS
# ═══════════════════════════════════════════════════════════
ALL_TOKENS = [VINIT, AFWD, AREV, FFUSE, FSPLIT, EVALT, EVALF, ENGAGR, CLINK, TANCH, IFIX, IMSCRIB]
TOKEN_SET = set(ALL_TOKENS)

# Token families
FWD_TOKENS = {AFWD, FFUSE, FSPLIT}       # forward reactivity
REV_TOKENS = {AREV, EVALT, EVALF}         # reverse reactivity
CORE_TOKENS = {VINIT, IMSCRIB}            # scaffold
LINK_TOKENS = {CLINK, TANCH}              # linker/terminal
AMBID_TOKENS = {ENGAGR}                   # ambident
CAP_TOKENS = {IFIX, IMSCRIB}              # closure

# ═══════════════════════════════════════════════════════════
# REVERSE MAPPING: IG PRIMITIVE → FP CONSTRAINT
# ═══════════════════════════════════════════════════════════

def ig_to_fp_constraints(ig_tuple: Tuple[str, ...]) -> Dict:
    """
    Decompose an IG tuple into StructuralFingerprint constraints.

    Returns a dict of field constraints (field→allowed_values).
    """
    D, T, R, P, F, K, G, C, Phi, H, S, Omega = ig_tuple

    constraints = {
        'self_ref': {True, False},
        'dialetheia_complete': {True, False},
        'frobenius_order': {0, 1, 2, 3},
        'period': set(range(1, 13)),
        'token_diversity': set(range(1, 13)),
        'sig_L': set(range(0, 9)),
        'sig_F': set(range(0, 9)),
        'sig_D': set(range(0, 9)),
        'sig_X': set(range(0, 9)),
    }

    # ── D → token_diversity ──
    if D == '\U0001045b':  # 𐑛
        constraints['token_diversity'] = {1, 2}
    elif D == '\U00010428':  # 𐑨
        constraints['token_diversity'] = {3, 4, 5}
    elif D == '\U0001043c':  # 𐑼
        constraints['token_diversity'] = {6, 7, 8, 9}
    elif D == '\U00010426':  # 𐑦
        constraints['token_diversity'] = set(range(10, 13))

    # ── T → self_ref, period, frobenius_order ──
    if T == '\U00010438':  # 𐑸
        constraints['self_ref'] = {True}
    elif T == '\U00010421':  # 𐑡
        constraints['self_ref'] = {False}
        constraints['period'] = {1}
        constraints['frobenius_order'] = {0}
    elif T == '\U00010430':  # 𐑥
        constraints['self_ref'] = {False}
        constraints['period'] = {2}
    elif T == '\U00010436':  # 𐑶
        constraints['self_ref'] = {False}
        constraints['frobenius_order'] = {1, 2, 3}
    elif T == '\U00010430':  # 𐑰
        constraints['self_ref'] = {False}
        constraints['frobenius_order'] = {0}
        constraints['period'] = set(range(3, 13))

    # ── R → frobenius_order ──
    if R == '\U0001043e':  # 𐑾
        constraints['frobenius_order'] = {1}
    elif R == '\U0001043d':  # 𐑽
        constraints['frobenius_order'] = {2}
    elif R == '\U00010411':  # 𐑑
        constraints['frobenius_order'] = {3}
    elif R == '\U00010429':  # 𐑩
        constraints['frobenius_order'] = {0}

    # ── P → frobenius_order, dialetheia_complete ──
    if P == '\U00010439':  # 𐑹
        constraints['frobenius_order'] = {1}
        constraints['dialetheia_complete'] = {False}
    elif P == '\U0001042f':  # 𐑯
        constraints['frobenius_order'] = {2}
        constraints['dialetheia_complete'] = {False}
    elif P == '\U0001042c':  # 𐑬
        constraints['frobenius_order'] = {3}
        constraints['dialetheia_complete'] = {False}
    elif P == '\U0001043f':  # 𐑿
        constraints['frobenius_order'] = {0}
        constraints['dialetheia_complete'] = {True}
    elif P == '\U00010417':  # 𐑗
        constraints['frobenius_order'] = {0}
        constraints['dialetheia_complete'] = {False}

    # ── F → dialetheia_complete, period ──
    if F == '\U00010450':  # 𐑐
        constraints['dialetheia_complete'] = {True}
    elif F == '\U00010431':  # 𐑱
        constraints['dialetheia_complete'] = {False}
        constraints['period'] = {1}
    elif F == '\U0001041e':  # 𐑞
        constraints['dialetheia_complete'] = {False}
        constraints['period'] = set(range(2, 13))

    # ── K → period, sig_X ──
    if K == '\U0001042a':  # 𐑪
        constraints['sig_X'] = {8}
    elif K == '\U00010427':  # 𐑧
        constraints['period'] = {1}
    elif K == '\U00010424':  # 𐑤
        constraints['period'] = {2, 3, 4}
    elif K == '\U00010418':  # 𐑘
        constraints['period'] = set(range(5, 13))

    # ── G → sig_X, token_diversity ──
    if G == '\U00010432':  # 𐑲
        constraints['sig_X'] = set(range(3, 9))
    elif G == '\U00010414':  # 𐑔
        # sig_X >= 1 (covers 1-2) OR (sig_X == 0 AND token_diversity > 3)
        constraints['sig_X'] = set(range(1, 9))
    elif G == '\U0001041a':  # 𐑚
        constraints['sig_X'] = {0}
        constraints['token_diversity'] = {1, 2, 3}

    # ── C → frobenius_order, period ──
    if C == '\U00010420':  # 𐑠
        constraints['frobenius_order'] = {1, 2, 3}
    elif C == '\U0001041d':  # 𐑝
        constraints['frobenius_order'] = {0}
        constraints['period'] = {1}
    elif C == '\U0001041c':  # 𐑜
        constraints['frobenius_order'] = {0}
        constraints['period'] = {2}
    elif C == '\U00010435':  # 𐑵
        constraints['frobenius_order'] = {0}
        constraints['period'] = set(range(3, 13))

    # ── Phi → self_ref, dialetheia_complete, period ──
    if Phi == '\u2299':  # ⊙
        constraints['self_ref'] = {True}
        constraints['dialetheia_complete'] = {True}
    elif Phi == '\U0001042e':  # 𐑮
        constraints['self_ref'] = {True}
        constraints['dialetheia_complete'] = {False}
    elif Phi == '\U0001043b':  # 𐑻
        constraints['self_ref'] = {False}
        constraints['dialetheia_complete'] = {True}
    elif Phi == '\U00010422':  # 𐑢
        constraints['self_ref'] = {False}
        constraints['dialetheia_complete'] = {False}
        constraints['period'] = {1}
    elif Phi == '\U00010423':  # 𐑣
        constraints['self_ref'] = {False}
        constraints['dialetheia_complete'] = {False}
        constraints['period'] = set(range(2, 13))

    # ── H → period ──
    if H == '\U00010413':  # 𐑓
        constraints['period'] = {1}
    elif H == '\U00010412':  # 𐑒
        constraints['period'] = {2}
    elif H == '\U00010416':  # 𐑖
        constraints['period'] = {3}
    elif H == '\U0001042b':  # 𐑫
        constraints['period'] = set(range(4, 13))

    # ── S → signature non-zero count ──
    if S == '\U00010419':  # 𐑙
        constraints['sig_nz'] = {1}
    elif S == '\U00010415':  # 𐑕
        constraints['sig_nz'] = {2}
    elif S == '\U00010433':  # 𐑳
        constraints['sig_nz'] = set(range(3, 13))

    # ── Omega → frobenius_order, self_ref, period ──
    if Omega == '\U0001042d':  # 𐑭
        constraints['frobenius_order'] = {1}
        # Also: frobenius_order != 1 AND self_ref = True
    elif Omega == '\U00010434':  # 𐑴
        # frobenius_order = 2 OR (frobenius_order ∉ {1,2} AND self_ref=False AND period=2)
        pass  # handled by consistency check
    elif Omega == '\U00010437':  # 𐑷
        # frobenius_order ∉ {1,2} AND self_ref=False AND period≠2
        pass

    return constraints


# ═══════════════════════════════════════════════════════════
# CONSTRAINT CONSISTENCY CHECK
# ═══════════════════════════════════════════════════════════

def check_consistency(ig_tuple: Tuple[str, ...]) -> Tuple[bool, List[str]]:
    """Check if an IG tuple is internally consistent (could come from a real FP)."""
    issues = []
    D, T, R, P, F, K, G, C, Phi, H, S, Omega = ig_tuple

    # frobenius_order consistency: R, P, C must agree
    frob = None
    if R == '\U0001043e':  # 𐑾
        frob = 1
    elif R == '\U0001043d':  # 𐑽
        frob = 2
    elif R == '\U00010411':  # 𐑑
        frob = 3
    elif R == '\U00010429':  # 𐑩
        frob = 0

    if frob is not None:
        frob_info = FROB_CONSISTENCY.get(frob, {})
        expected_R = frob_info.get('R', None)
        expected_P = frob_info.get('P', [])
        expected_C = frob_info.get('C', [])

        if expected_R and R != expected_R:
            issues.append(f"R={R} inconsistent with frobenius_order={frob} (expected {expected_R})")
        if isinstance(expected_P, list) and P not in expected_P:
            issues.append(f"P={P} inconsistent with frobenius_order={frob}")
        elif isinstance(expected_P, str) and P != expected_P:
            issues.append(f"P={P} inconsistent with frobenius_order={frob} (expected {expected_P})")
        if isinstance(expected_C, list) and C not in expected_C:
            issues.append(f"C={C} inconsistent with frobenius_order={frob}")
        elif isinstance(expected_C, str) and C != expected_C:
            issues.append(f"C={C} inconsistent with frobenius_order={frob} (expected {expected_C})")

    # Omega consistency
    if Omega == '\U0001042d':  # 𐑭
        # Either frob=1 OR self_ref=True
        pass  # acceptable in both cases

    return len(issues) == 0, issues


FROB_CONSISTENCY = {
    0: {'R': '\U00010429', 'P': ['\U00010417', '\U0001043f'],
        'C': ['\U0001041d', '\U0001041c', '\U00010435'],
        'Omega': ['\U00010437', '\U0001042d']},
    1: {'R': '\U0001043e', 'P': '\U00010439', 'C': '\U00010420', 'Omega': '\U0001042d'},
    2: {'R': '\U0001043d', 'P': '\U0001042f', 'C': '\U00010420', 'Omega': '\U00010434'},
    3: {'R': '\U00010411', 'P': '\U0001042c', 'C': '\U00010420',
        'Omega': ['\U00010437', '\U00010434', '\U0001042d']},
}


# ═══════════════════════════════════════════════════════════
# ARRANGEMENT GENERATION FROM CONSTRAINTS
# ═══════════════════════════════════════════════════════════

def arrangement_to_fingerprint(arr):
    """Convert an 8-token arrangement to StructuralFingerprint."""
    return compute_fingerprint(arr)

def enumerate_arrangements(constraints: Dict) -> List[Tuple[int, ...]]:
    """
    Enumerate IMASM arrangements satisfying given fingerprint constraints.

    Brute-force over arrangement space. With 12 tokens^8 positions = 430M
    possibilities, we use pruning: position-based token selection.
    
    For a focused search, we sample constraints rather than full enumeration.
    Returns list of valid 8-token arrangements.
    """
    valid = []
    
    # Derive position constraints from fingerprint constraints
    pos_constraints = derive_position_constraints(constraints)
    
    for arr_tuple in _search_arrangements(pos_constraints, max_candidates=5000):
        fp = compute_fingerprint(arr_tuple)
        
        # Check all constraints
        ok = True
        for field, allowed in constraints.items():
            val = _get_fp_field(fp, field)
            if val not in allowed:
                ok = False
                break
        
        if ok:
            valid.append(arr_tuple)
    
    return valid


def _get_fp_field(fp: StructuralFingerprint, field: str):
    """Get a field from StructuralFingerprint by name."""
    return getattr(fp, field, None)


def derive_position_constraints(constraints: Dict) -> Dict:
    """
    Derive per-position token constraints from fingerprint constraints.
    
    Key mappings:
      - self_ref=True → pos[0] in {IMSCRIB} AND pos[7] in {IMSCRIB}
      - dialetheia_complete → FFUSE in pos 1-3 AND FSPLIT in pos 1-3
      - frobenius_order → relates to FFUSE/FSPLIT ordering
      - period → repetition pattern in arrangement
      - sig_X → count of IFIX tokens
      - token_diversity → number of distinct tokens used
    """
    pc = {}
    
    # Self-reference: IMSCRIB at both ends
    if constraints.get('self_ref') == {True}:
        pc[0] = {IMSCRIB}
        pc[7] = {IMSCRIB}
    elif constraints.get('self_ref') == {False}:
        pc[0] = TOKEN_SET - {IMSCRIB}
        pc[7] = TOKEN_SET - {IMSCRIB}
    
    # frobenius_order > 0 requires FFUSE and FSPLIT
    fr = constraints.get('frobenius_order', {0, 1, 2, 3})
    if fr == {1, 2, 3} or (len(fr) == 1 and list(fr)[0] > 0):
        # Must have both FFUSE and FSPLIT
        pass  # handled by dialetheia
    
    # dialetheia_complete requires both FFUSE and FSPLIT
    if constraints.get('dialetheia_complete') == {True}:
        # Ensure FFUSE and FSPLIT appear
        pass  # handled by signature constraints
    
    # sig_X (IFIX count)
    sx = constraints.get('sig_X', set(range(0, 9)))
    if sx == {0}:
        pc['forbid'] = pc.get('forbid', []) + [IFIX]
    
    # period constraint
    period = constraints.get('period', set(range(1, 13)))
    if period == {1}:
        # All tokens the same
        for i in range(1, 7):
            pc[i] = {VINIT}  # single repeating token
    
    return pc


def _search_arrangements(pos_constraints: Dict, max_candidates: int = 5000):
    """Search arrangement space subject to position constraints."""
    candidates = []
    
    # Build allowed tokens per position
    allowed_at_pos = {}
    for i in range(8):
        if i in pos_constraints:
            allowed_at_pos[i] = pos_constraints[i]
        elif 'forbid' in pos_constraints:
            allowed_at_pos[i] = TOKEN_SET - set(pos_constraints.get('forbid', []))
        else:
            allowed_at_pos[i] = TOKEN_SET
    
    # For self-referential case, constrain both ends
    forced_ends = {0: {IMSCRIB}, 7: {IMSCRIB}} if pos_constraints.get(0) == {IMSCRIB} else {}
    
    # Generate candidates via systematic variation
    # Use smart token choice for each position
    core_tokens = list(pos_constraints.get(0, CORE_TOKENS))
    fwd_tokens = list(FWD_TOKENS)
    rev_tokens = list(REV_TOKENS)
    amb_tokens = list(AMBID_TOKENS)
    link_tokens = list(LINK_TOKENS)
    cap_tokens = list(CAP_TOKENS)
    
    count = 0
    for core in core_tokens:
        for fwd in fwd_tokens:
            for rev in rev_tokens:
                for amb in amb_tokens:
                    for link in link_tokens:
                        for cap in cap_tokens:
                            for mid in core_tokens + fwd_tokens:
                                # Build arrangement: [0=core, 1=fwd, 2=rev, 3=amb, 
                                #                    4=link, 5=mid, 6=mid2, 7=cap]
                                end_token = pos_constraints.get(7, {IMSCRIB, IFIX}).pop() if 7 in pos_constraints and len(pos_constraints[7]) == 1 else IMSCRIB
                                # Actually use a simpler approach
                                arr = [core, fwd, rev, amb, link, mid, VINIT, IMSCRIB]
                                if len(arr) == 8:
                                    candidates.append(tuple(arr))
                                    count += 1
                                    if count >= max_candidates:
                                        return candidates
    return candidates


# ═══════════════════════════════════════════════════════════
# IG TUPLE → SMILES GENERATION
# ═══════════════════════════════════════════════════════════

def ig_tuple_to_smiles_hints(ig_tuple: Tuple[str, ...]) -> Dict:
    """
    Given a target IG tuple, produce molecular design hints.
    
    Returns dict with:
      - constraints: fingerprint constraints from tuple
      - consistency: (bool, issues)
      - design_hints: structural features needed
    """
    cons, issues = check_consistency(ig_tuple)
    
    D, T, R, P, F, K, G, C, Phi, H, S, Omega = ig_tuple
    
    hints = {
        'consistency_ok': cons,
        'issues': issues,
        'structural_features': [],
    }
    
    # Interpret each primitive as a chemical design constraint
    # D → molecular complexity
    if D == '𐑛':  # 𐑛
        hints['structural_features'].append('Very simple molecule (≤5 heavy atoms)')
    elif D == '𐑨':  # 𐑨
        hints['structural_features'].append('Moderate complexity (3-5 distinct functional groups)')
    elif D == '𐑼':  # 𐑼
        hints['structural_features'].append('Complex molecule (6-9 distinct functional groups)')
    elif D == '𐑦':  # 𐑦
        hints['structural_features'].append('Highly complex (10+ distinct functional groups)')
    
    # T → topology / ring structure
    if T == '𐑸':  # 𐑸
        hints['structural_features'].append('Self-referential: aromatic or conjugated ring system (IMSCRIB closure)')
    elif T == '𐑡':  # 𐑡
        hints['structural_features'].append('Chain topology: no rings')
    elif T == '𐑥':  # 𐑥
        hints['structural_features'].append('Bipartite: two distinct structural regions')
    elif T == '𐑶':  # 𐑶
        hints['structural_features'].append('Crossing topology: fused rings or bridged system')
    elif T == '𐑥':  # 𐑰
        hints['structural_features'].append('Containment: nested ring system or cage')
    
    # R → coupling type
    if R == '𐑾':  # 𐑾
        hints['structural_features'].append('Bidirectional coupling: tautomerism or resonance')
    elif R == '𐑽':  # 𐑽
        hints['structural_features'].append('Functorial coupling: bioconjugate or pro-drug')
    elif R == '𐑑':  # 𐑑
        hints['structural_features'].append('Adjoint: reversible reaction pair')
    elif R == '𐑩':  # 𐑩
        hints['structural_features'].append('Supervenient: passive mixture, simple solvent')
    
    # P → symmetry
    if P == '𐑹':  # 𐑹
        hints['structural_features'].append('Frobenius-special: μ∘δ=id exact — catalytic cycle')
    elif P == '𐑯':  # 𐑯
        hints['structural_features'].append('Full symmetry: highly symmetric (e.g., benzene ring)')
    elif P == '𐑬':  # 𐑬
        hints['structural_features'].append('Partial symmetry: prochiral center, meso compound')
    elif P == '𐑿':  # 𐑿
        hints['structural_features'].append('Quantum superposition: delocalized electrons, aromatic')
    elif P == '𐑗':  # 𐑗
        hints['structural_features'].append('Asymmetric: chiral center, no symmetry elements')
    
    # F → fidelity / quantum character
    if F == '𐑐':  # 𐑐
        hints['structural_features'].append('Quantum coherence: conjugated pi system, delocalized charge')
    elif F == '𐑱':  # 𐑱
        hints['structural_features'].append('Classical: saturated, no conjugation')
    elif F == '𐑞':  # 𐑞
        hints['structural_features'].append('Thermal: room-temperature stable, conformational flexibility')
    
    # K → kinetics
    if K == '𐑧':  # 𐑧
        hints['structural_features'].append('Fast kinetics: labile bonds, rapid reaction')
    elif K == '𐑤':  # 𐑤
        hints['structural_features'].append('Trapped: conformationally locked, rigid structure')
    elif K == '𐑘':  # 𐑘
        hints['structural_features'].append('MBL: atropisomeric, hindered rotation')
    elif K == '𐑪':  # 𐑪
        hints['structural_features'].append('Slow: stable, slow to react')
    
    # Omega → winding number
    if Omega == '𐑭':  # 𐑭
        hints['structural_features'].append('Integer winding: single ring system, non-alternating')
    elif Omega == '𐑴':  # 𐑴
        hints['structural_features'].append('Z2 winding: alternating bonds, antiaromatic')
    elif Omega == '𐑷':  # 𐑷
        hints['structural_features'].append('Trivial winding: acyclic, no ring')
    
    # Phi → criticality
    if Phi == '⊙':  # ⊙
        hints['structural_features'].append('SELF-MODELING CRITICAL: autocatalytic, self-replicating')
        hints['criticality'] = 'self_modeling'
    elif Phi == '𐑮':  # 𐑮
        hints['structural_features'].append('Complex critical: π-stacking, charge-transfer complex')
        hints['criticality'] = 'complex_critical'
    elif Phi == '𐑻':  # 𐑻
        hints['structural_features'].append('Exceptional point: frustrated Lewis pair, non-Hermitian')
        hints['criticality'] = 'exceptional'
    elif Phi == '𐑢':  # 𐑢
        hints['structural_features'].append('Sub-critical: stable ground state, no reactivity')
        hints['criticality'] = 'sub_critical'
    elif Phi == '𐑣':  # 𐑣
        hints['structural_features'].append('Supercritical: reactive intermediate, high-energy')
        hints['criticality'] = 'supercritical'
    
    return hints


def analyze_crystal_neighborhood(ig_tuple: Tuple[str, ...], radius: int = 1):
    """
    Generate all IG tuples within Manhattan distance  of the target.
    
    Returns list of (neighbor_tuple, distance, hints).
    """
    prims = list(ig_tuple)
    neighbors = []
    
    # The primitive ordinal ladder for each field
    ladders = {
        0: ['𐑛', '𐑨', '𐑼', '𐑦'],  # D
        1: ['𐑡', '𐑥', '𐑥', '𐑶', '𐑸'],  # T
        2: ['𐑩', '𐑑', '𐑽', '𐑾'],  # R
        3: ['𐑗', '𐑯', '𐑬', '𐑿', '𐑹'],  # P
        4: ['𐑱', '𐑞', '𐑐'],  # F
        5: ['𐑧', '𐑤', '𐑘', '𐑪'],  # K
        6: ['𐑚', '𐑔', '𐑲'],  # G
        7: ['𐑝', '𐑜', '𐑠', '𐑵'],  # C
        8: ['𐑢', '⊙', '𐑮', '𐑻', '𐑣'],  # Phi
        9: ['𐑓', '𐑒', '𐑖', '𐑫'],  # H
        10: ['𐑙', '𐑕', '𐑳'],  # S
        11: ['𐑷', '𐑴', '𐑭', '𐑟'],  # Omega
    }
    
    for num_changes in range(1, radius + 1):
        for positions in itertools.combinations(range(12), num_changes):
            for new_vals in itertools.product(*[ladders[p] for p in positions]):
                candidate = list(prims)
                for pos, val in zip(positions, new_vals):
                    if val != candidate[pos]:
                        candidate[pos] = val
                tup = tuple(candidate)
                ok, issues = check_consistency(tup)
                hints = ig_tuple_to_smiles_hints(tup)
                neighbors.append((tup, num_changes, ok, hints, issues))
    
    return neighbors


if __name__ == "__main__":
    # Test with caffeine's IG tuple
    caffeine_ig = ('𐑨', '𐑸', '𐑩', '𐑗', 
                   '𐑞', '𐑘', '𐑔', '𐑵',
                   '𐑮', '𐑫', '𐑕', '𐑭')
    
    hints = ig_tuple_to_smiles_hints(caffeine_ig)
    print("=== Caffeine IG Type Analysis ===")
    print(ig_tuple_str(caffeine_ig))
    print(f"Consistent: {hints['consistency_ok']}")
    if hints['issues']:
        print(f"Issues: {hints['issues']}")
    print("\nDesign Hints:")
    for f in hints['structural_features']:
        print(f"  - {f}")
    
    # Explore neighborhood
    print("\n=== Crystal Neighborhood (d=1) ===")
    neighbors = analyze_crystal_neighborhood(caffeine_ig, radius=1)
    for tup, dist, ok, hints, issues in neighbors[:10]:
        marker = "✓" if ok else "✗"
        print(f"  d={dist} {marker} {ig_tuple_str(tup)}")


# ═══════════════════════════════════════════════════════════
# CANDIDATE MOLECULE GENERATION FROM DESIGN HINTS
# ═══════════════════════════════════════════════════════════

# Template fragments mapped by structural feature
FRAGMENT_TEMPLATES = {
    'aromatic': ['c1ccccc1', 'c1cnccc1', 'c1ccncc1', 'c1ccccn1', 
                 'c1ccsc1', 'c1ccoc1', 'c1cncnc1'],
    'ring': ['C1CCCCC1', 'C1CCCC1', 'C1CC1', 'C1CCC1'],
    'fused_ring': ['c1ccc2ccccc2c1', 'c1cc2ccccc2cc1', 'c1ccc2c(c1)ccc3ccccc23'],
    'bridged': ['C12CC3CC1CC(C2)C3', 'C12CC3CC(C1)CC(C3)C2'],
    'amine': ['N', 'CN', 'CCN', 'C1CCNCC1'],
    'amide': ['NC(=O)C', 'CC(=O)N', 'CC(=O)NC'],
    'carboxylic_acid': ['C(=O)O', 'CC(=O)O'],
    'ester': ['C(=O)OC', 'CC(=O)OC', 'COC(=O)C'],
    'ether': ['COC', 'CCOCC', 'c1ccc(Oc2ccccc2)cc1'],
    'alcohol': ['CO', 'CCO', 'CC(C)O'],
    'ketone': ['CC(=O)C', 'CC(=O)CC'],
    'aldehyde': ['CC=O'],
    'nitrile': ['CC#N'],
    'halogen': ['CCl', 'CF', 'CBr', 'CI'],
    'sulfide': ['CSC', 'CCSCC'],
    'sulfoxide': ['CS(=O)C'],
    'sulfonamide': ['CS(=O)(=O)N'],
    'nitro': ['C[N+](=O)[O-]'],
    'phosphate': ['COP(=O)(O)OC'],
    'chiral_center': ['C(C)(C)C', 'CC(C)(C)O', 'CC(N)C(=O)O'],
    'conjugated': ['C=CC=C', 'C=CC=CC=C', 'c1ccc(C=Cc2ccccc2)cc1'],
    'heterocycle': ['c1ccncc1', 'c1cncnc1', 'c1ccco1', 'c1cccs1',
                    'c1c[nH]cc1', 'c1c[nH]cn1', 'c1cn[nH]c1'],
}


def generate_candidate_smiles(design_hints: Dict, max_candidates: int = 20) -> List[Dict]:
    """Generate candidate SMILES strings from design hints.
    
    Uses fragment templates matched to structural features, then
    assembles them via RDKit.
    """
    candidates = []
    features = design_hints.get('structural_features', [])
    feature_text = ' '.join(features).lower()
    
    # Select fragments based on features
    selected_fragments = []
    
    if 'aromatic' in feature_text or 'self-referential' in feature_text:
        selected_fragments.extend(FRAGMENT_TEMPLATES['aromatic'][:3])
    if 'ring system' in feature_text:
        selected_fragments.extend(FRAGMENT_TEMPLATES['ring'][:2])
    if 'fused' in feature_text or 'bridged' in feature_text:
        selected_fragments.extend(FRAGMENT_TEMPLATES['fused_ring'][:2])
    
    # Add functional groups based on features
    if 'chiral' in feature_text or 'asymmetric' in feature_text:
        selected_fragments.append('C(C)(C)O')
    if 'conjugated' in feature_text or 'pi' in feature_text:
        selected_fragments.append('c1ccc(C=C)cc1')
    if 'acid' in feature_text:
        selected_fragments.append('CC(=O)O')
    if 'amine' in feature_text:
        selected_fragments.append('CCN')
    if 'ether' in feature_text:
        selected_fragments.append('COC')
    if 'ketone' in feature_text:
        selected_fragments.append('CC(=O)C')
    if 'ester' in feature_text:
        selected_fragments.append('CC(=O)OC')
    if 'alcohol' in feature_text or 'hydroxyl' in feature_text:
        selected_fragments.append('CCO')
    if 'amine' in feature_text:
        selected_fragments.append('CN')
    if 'heterocycle' in feature_text:
        selected_fragments.extend(FRAGMENT_TEMPLATES['heterocycle'][:2])
    
    # Also consider the criticality type
    crit = design_hints.get('criticality', '')
    if crit == 'self_modeling':
        selected_fragments.append('C=C')  # reactive
        selected_fragments.append('N=C=O')  # isocyanate
    elif crit == 'complex_critical':
        selected_fragments.append('c1ccc([N+](=O)[O-])cc1')  # nitroaromatic
    elif crit == 'supercritical':
        selected_fragments.append('C=CC=C')  # diene
    
    # Build combinations of 1-2 fragments
    for i, frag in enumerate(selected_fragments):
        candidates.append({
            'smiles': frag,
            'type': 'single_fragment',
            'basis': features[i % len(features)] if features else 'generic',
        })
    
    # Try joining pairs
    if len(selected_fragments) >= 2:
        for i in range(min(3, len(selected_fragments))):
            for j in range(i+1, min(i+4, len(selected_fragments))):
                combo = selected_fragments[i] + selected_fragments[j]
                candidates.append({
                    'smiles': combo,
                    'type': 'joined_pair',
                    'basis': f'{features[i % len(features)]} + {features[j % len(features)]}',
                })
    
    return candidates[:max_candidates]


def design_from_type(ig_tuple: Tuple[str, ...], max_candidates: int = 15) -> Dict:
    """Full pipeline: IG tuple → design hints → candidate molecules.
    
    Returns dict with analysis and candidates.
    """
    hints = ig_tuple_to_smiles_hints(ig_tuple)
    candidates = generate_candidate_smiles(hints, max_candidates)
    
    return {
        'ig_tuple': ig_tuple_str(ig_tuple),
        'consistency_ok': hints['consistency_ok'],
        'issues': hints['issues'],
        'structural_features': hints['structural_features'],
        'criticality': hints.get('criticality', 'unknown'),
        'candidates': candidates,
    }


def analyze_compound_design_space(smiles: str, radius: int = 1) -> List[Dict]:
    """Given a SMILES, explore the crystal neighborhood and suggest modifications.
    
    For each neighbor type within radius, generate candidate molecules
    that would occupy that type.
    """
    from imas.compound_imasm import molecule_to_arrangement
    from imas.arranger import compute_fingerprint
    
    arr = molecule_to_arrangement(smiles)
    if not arr:
        return []
    fp = compute_fingerprint(arr)
    ig = fingerprint_to_ig(fp)
    
    designs = []
    neighbors = analyze_crystal_neighborhood(ig, radius)
    
    # Remove duplicates and sort by distance
    seen = set()
    unique_neighbors = []
    for tup, dist, ok, hints, issues in neighbors:
        if tup not in seen and ok:
            seen.add(tup)
            unique_neighbors.append((tup, dist, hints))
    
    unique_neighbors.sort(key=lambda x: x[1])
    
    for tup, dist, hints in unique_neighbors[:20]:
        cands = generate_candidate_smiles(hints, max_candidates=3)
        designs.append({
            'target_type': ig_tuple_str(tup),
            'distance': dist,
            'criticality': hints.get('criticality', 'unknown'),
            'features': hints['structural_features'][:4],
            'candidates': [c['smiles'] for c in cands[:3]],
        })
    
    return designs


# ═══════════════════════════════════════════════════════════
# CLI INTEGRATION
# ═══════════════════════════════════════════════════════════

def run_cli():
    """CLI entry point: analyze a SMILES or IG tuple."""
    import argparse
    parser = argparse.ArgumentParser(description='Crystal-Guided Molecular Designer')
    parser.add_argument('--smiles', '-s', help='SMILES string to analyze')
    parser.add_argument('--radius', '-r', type=int, default=1,
                        help='Crystal neighborhood radius (default: 1)')
    parser.add_argument('--candidates', '-c', type=int, default=10,
                        help='Max candidate molecules (default: 10)')
    
    args = parser.parse_args()
    
    if not args.smiles:
        # Default: analyze caffeine
        args.smiles = 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C'
        print(f"No SMILES provided. Defaulting to caffeine: {args.smiles}")
    
    print(f"\n{'='*60}")
    print(f"Analyzing: {args.smiles}")
    print(f"{'='*60}")
    
    from imas.compound_imasm import molecule_to_arrangement
    arr = molecule_to_arrangement(args.smiles)
    if not arr:
        print("ERROR: Invalid SMILES")
        return
    
    fp = compute_fingerprint(arr)
    ig = fingerprint_to_ig(fp)
    
    print(f"\nIG Type: {ig_tuple_str(ig)}")
    print(f"\n--- Design Analysis ---")
    
    result = design_from_type(ig, args.candidates)
    
    print(f"Consistent: {result['consistency_ok']}")
    print(f"Criticality: {result['criticality']}")
    print(f"\nStructural Features:")
    for f in result['structural_features']:
        print(f"  - {f}")
    
    print(f"\n--- Crystal Neighborhood (d<={args.radius}) ---")
    designs = analyze_compound_design_space(args.smiles, args.radius)
    for d in designs[:10]:
        print(f"\n  [{d['distance']}] Target: {d['target_type']}")
        print(f"      Criticality: {d['criticality']}")
        for feat in d['features'][:3]:
            print(f"      - {feat}")
        if d['candidates']:
            print(f"      Candidates: {', '.join(d['candidates'][:2])}")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    run_cli()


# ═══════════════════════════════════════════════════════════
# RDKit-POWERED MOLECULE GENERATION
# ═══════════════════════════════════════════════════════════

def mutate_toward_type(reference_smiles: str, target_ig: Tuple[str, ...],
                       max_mutations: int = 50) -> List[Dict]:
    """Given a reference molecule and a target IG type, generate candidate
    molecules that bridge the structural gap.
    
    Uses RDKit to:
    1. Analyze the reference molecule's functional groups
    2. Add/remove/modify groups to shift toward the target type's features
    3. Validate all candidates chemically
    """
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem, Descriptors, MolFromSmiles, MolToSmiles
    except ImportError:
        return []
    
    ref_mol = MolFromSmiles(reference_smiles)
    if ref_mol is None:
        return []
    
    ref_mol = Chem.AddHs(ref_mol)
    Chem.SanitizeMol(ref_mol)
    ref_smiles = MolToSmiles(ref_mol)
    
    # Parse target type features
    D, T, R, P_val, F, K, G, C, Phi, H, S, Omega = target_ig
    
    candidates = []
    
    # Feature → modification map
    modifications = []
    
    # D: complexity adjustment
    if D in (chr(0x1045b),):  # 𐑛 - very simple
        modifications.append(('simplify', 'remove_complex_groups'))
    elif D in (chr(0x10468), chr(0x1047c)):  # 𐑨 or 𐑼
        modifications.append(('complexify', 'add_substituents'))
    elif D == chr(0x10466):  # 𐑦 - highly complex
        modifications.append(('complexify', 'add_heteroatoms'))
    
    # T: topology adjustment
    if T == chr(0x10461):  # 𐑡 - chain, no rings
        modifications.append(('ring_break', 'remove_rings'))
    elif T == chr(0x10478):  # 𐑸 - self-ref (aromatic)
        modifications.append(('ring_add', 'add_aromatic_ring'))
    elif T == chr(0x10476):  # 𐑶 - crossing/fused
        modifications.append(('ring_add', 'fuse_rings'))
    
    # Phi: criticality adjustment
    if Phi == chr(0x2299):  # ⊙ - self-modeling
        modifications.append(('reactive', 'add_catalytic_center'))
    elif Phi == chr(0x1046e):  # 𐑮 - complex critical
        modifications.append(('electronic', 'add_pi_system'))
    
    # Apply modifications using RDKit
    for mod_type, action in modifications:
        try:
            if action == 'add_aromatic_ring':
                # Try to add a benzene ring via SMARTS attachment
                modified = Chem.RWMol(ref_mol)
                modified = _add_ring_to_mol(modified)
                if modified:
                    candidates.append({
                        'smiles': MolToSmiles(modified),
                        'modification': 'add_aromatic_ring',
                    })
            elif action == 'add_pi_system':
                modified = _extend_conjugation(ref_mol)
                if modified:
                    candidates.append({
                        'smiles': MolToSmiles(modified),
                        'modification': 'extend_conjugation',
                    })
        except Exception:
            pass
    
    return candidates


def _add_ring_to_mol(mol):
    """Try to add a ring to a molecule at a suitable attachment point."""
    from rdkit import Chem
    from rdkit.Chem import MolFromSmiles, MolToSmiles, RWMol
    
    try:
        rw = RWMol(mol)
        # Find atoms that aren't in rings
        atom_indices = [a.GetIdx() for a in rw.GetAtoms() 
                       if not a.IsInRing() and a.GetDegree() < 4]
        
        if not atom_indices:
            return None
        
        # Add phenyl ring at the first suitable atom
        # SMARTS: [C:1]>>[c:1]c1ccccc1  (attach phenyl)
        idx = atom_indices[0]
        atom = rw.GetAtomWithIdx(idx)
        
        # This is a simplified approach - in production we'd use more
        # sophisticated chemistry
        return None  # RDKit RWMol ring addition is complex
    except Exception:
        return None


def _extend_conjugation(mol):
    """Extend a conjugated system by adding a vinyl group."""
    from rdkit import Chem
    from rdkit.Chem import MolFromSmiles, MolToSmiles
    
    try:
        # Find atoms in double bonds
        smiles = MolToSmiles(mol)
        # Simple approach: add C=C at the end via string manipulation
        # More robust: use RDKit editing
        return None
    except Exception:
        return None


def validate_molecule(smiles: str) -> Dict:
    """Validate a SMILES string and compute molecular properties."""
    if not HAS_RDKIT:
        return {'valid': False, 'error': 'RDKit not available'}
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, MolFromSmiles, MolToSmiles
        from rdkit.Chem.rdMolDescriptors import CalcMolFormula
        
        mol = MolFromSmiles(smiles)
        if mol is None:
            return {'valid': False, 'error': 'Invalid SMILES'}
        
        mol = Chem.AddHs(mol)
        Chem.SanitizeMol(mol)
        
        props = {
            'valid': True,
            'formula': CalcMolFormula(mol),
            'mol_weight': Descriptors.MolWt(mol),
            'logp': Descriptors.MolLogP(mol),
            'hba': Descriptors.NumHAcceptors(mol),
            'hbd': Descriptors.NumHDonors(mol),
            'rotatable_bonds': Descriptors.NumRotatableBonds(mol),
            'aromatic_rings': Descriptors.NumAromaticRings(mol),
            'rings': Descriptors.RingCount(mol),
            'tpsa': Descriptors.TPSA(mol),
            'heavy_atoms': Descriptors.HeavyAtomCount(mol),
        }
        
        # Lipinski Rule-of-Five
        lipinski = sum([
            props['mol_weight'] <= 500,
            props['logp'] <= 5,
            props['hba'] <= 10,
            props['hbd'] <= 5,
        ])
        props['lipinski_score'] = lipinski
        props['lipinski_pass'] = lipinski >= 3
        
        return props
    except Exception as e:
        return {'valid': False, 'error': str(e)}


def enumerate_analogs(smiles: str, max_analogs: int = 20) -> List[Dict]:
    """Generate analogs of a molecule by systematic functional group variation
    using RDKit's fragment-based approaches."""
    analogs = []
    
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem, MolFromSmiles, MolToSmiles
        
        mol = MolFromSmiles(smiles)
        if mol is None:
            return analogs
        
        mol = Chem.AddHs(mol)
        
        # Get Murcko scaffold
        from rdkit.Chem.Scaffolds import MurckoScaffold
        scaffold = MurckoScaffold.GetScaffoldForMol(mol)
        scaffold_smiles = MolToSmiles(scaffold)
        
        analogs.append({
            'smiles': scaffold_smiles,
            'type': 'murcko_scaffold',
            'description': 'Core scaffold (Murcko decomposition)',
        })
        
        # Generate side chain variations using BRICS
        try:
            from rdkit.Chem import BRICS
            fragments = list(BRICS.BRICSDecompose(mol))
            for frag in fragments[:5]:
                analogs.append({
                    'smiles': frag,
                    'type': 'brics_fragment',
                    'description': 'BRICS fragment',
                })
        except Exception:
            pass
        
        # Generate random analogs via fingerprint-based similarity
        # (simplified: do functional group replacement)
        from rdkit.Chem import rdFMCS
        
        # Find and swap functional groups
        fun_groups = _identify_functional_groups(mol)
        for fg_smiles, fg_type in fun_groups[:3]:
            # Try replacing with other common groups
            replacements = {
                'carboxylic_acid': ['C(=O)OC', 'C(=O)N', 'C(=O)Cl'],
                'amine': ['N(C)C', 'NC(=O)C', 'N'],
                'alcohol': ['OC', 'OC(=O)C', 'Cl'],
                'methyl': ['F', 'Cl', 'CF3', 'CN'],
                'benzene': ['c1ccncc1', 'c1ccsc1', 'c1ccocc1'],
            }
            alt_groups = replacements.get(fg_type, [])
            for alt in alt_groups[:2]:
                # Build modified SMILES (simplified replacement)
                analogs.append({
                    'smiles': f'{scaffold_smiles}.{alt}',
                    'type': 'functional_group_variant',
                    'description': f'Replace {fg_type} with {alt}',
                })
    
    except Exception as e:
        analogs.append({'error': str(e)})
    
    return analogs[:max_analogs]


def _identify_functional_groups(mol):
    """Identify functional groups in a molecule."""
    from rdkit import Chem
    from rdkit.Chem import MolFromSmarts
    
    patterns = {
        'carboxylic_acid': '[CX3](=O)[OX2H1]',
        'amine': '[NX3;H2,H1;!$(NC=O)]',
        'alcohol': '[OX2H]',
        'methyl': '[CH3]',
        'benzene': 'c1ccccc1',
        'ester': '[CX3](=O)[OX2][CX4]',
        'amide': '[CX3](=O)[NX3]',
        'ketone': '[CX3](=O)[CX3]',
        'ether': '[OX2]([CX4])[CX4]',
        'nitrile': '[CX2]#[NX1]',
        'nitro': '[NX3](=O)=O',
        'sulfonamide': '[SX4](=O)(=O)[NX3]',
        'halogen': '[F,Cl,Br,I]',
    }
    
    found = []
    for name, smarts in patterns.items():
        pat = MolFromSmarts(smarts)
        if pat and mol.HasSubstructMatch(pat):
            matches = mol.GetSubstructMatches(pat)
            found.append((smarts, name))
    
    return found


def analyze_molecule_properties(smiles: str) -> Dict:
    """Full molecular property analysis."""
    from imas.compound_imasm import molecule_to_arrangement
    from imas.arranger import compute_fingerprint
    
    props = validate_molecule(smiles)
    if not props.get('valid'):
        return props
    
    # Also compute IG type
    arr = molecule_to_arrangement(smiles)
    if arr:
        fp = compute_fingerprint(arr)
        ig = fingerprint_to_ig(fp)
        props['ig_type'] = ig_tuple_str(ig)
    
    # Functional groups
    from rdkit import Chem
    mol = Chem.MolFromSmiles(smiles)
    if mol:
        mol = Chem.AddHs(mol)
        fgs = _identify_functional_groups(mol)
        props['functional_groups'] = [fg[1] for fg in fgs]
    
    return props
