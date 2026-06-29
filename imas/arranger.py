"""
arranger.py — IMASM Arrangement Engine
=======================================
Core engine for the IMASM token arrangement space: generation, fingerprinting,
classification, and search over the 430M possible length-8 token sequences.

The IMASM token space consists of 12 tokens in 4 algebraic families:
  Logical:     VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB  (6 tokens)
  Frobenius:   FSPLIT (δ), FFUSE (μ)                       (2 tokens)
  Dialetheia:  EVALT, EVALF, ENGAGR                         (3 tokens)
  Linear:      IFIX (!)                                     (1 token)

An arrangement is an 8-tuple of token indices from this 12-token universe.
Arrangements are structural programs — sentences in the grammar's combinatorial
language, whose fingerprints map to IG crystal types.

Author: Lando⊗⊙perator
Adapted from: /home/mrnob0dy666/IMSCRIBr/classifier.py + tokens.py
"""

from typing import Tuple, List, Dict, NamedTuple, Optional, Set
from collections import defaultdict
import itertools
from shared.rich_output import *


# ═══════════════════════════════════════════════════════════════════
# TOKEN DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

class Token:
    """Token indices and families."""
    # Logical family (6 tokens)
    VINIT   = 0
    TANCH   = 1
    AFWD    = 2
    AREV    = 3
    CLINK   = 4
    IMSCRIB = 5
    # Frobenius family (2 tokens)
    FSPLIT  = 6
    FFUSE   = 7
    # Dialetheia family (3 tokens)
    EVALT   = 8
    EVALF   = 9
    ENGAGR  = 10
    # Linear family (1 token)
    IFIX    = 11

TOKEN_NAMES = {
    0: "VINIT", 1: "TANCH", 2: "AFWD", 3: "AREV",
    4: "CLINK", 5: "IMSCRIB", 6: "FSPLIT", 7: "FFUSE",
    8: "EVALT", 9: "EVALF", 10: "ENGAGR", 11: "IFIX",
}

class Family:
    LOGICAL    = 0
    FROBENIUS  = 1
    DIALETHEIA = 2
    LINEAR     = 3

FAMILY_NAMES = {0: "Logical", 1: "Frobenius", 2: "Dialetheia", 3: "Linear"}

TOKEN_FAMILY = {
    0: Family.LOGICAL, 1: Family.LOGICAL, 2: Family.LOGICAL,
    3: Family.LOGICAL, 4: Family.LOGICAL, 5: Family.LOGICAL,
    6: Family.FROBENIUS, 7: Family.FROBENIUS,
    8: Family.DIALETHEIA, 9: Family.DIALETHEIA, 10: Family.DIALETHEIA,
    11: Family.LINEAR,
}

FAMILY_TOKENS = {
    Family.LOGICAL:    [0, 1, 2, 3, 4, 5],
    Family.FROBENIUS:  [6, 7],
    Family.DIALETHEIA: [8, 9, 10],
    Family.LINEAR:     [11],
}

TOKEN_COUNT = 12

def token_name(t: int) -> str:
    return TOKEN_NAMES.get(t, f"UNKNOWN({t})")

def token_family(t: int) -> int:
    return TOKEN_FAMILY[t]

def signature(arr: Tuple[int, ...]) -> Tuple[int, int, int, int]:
    """Family signature: (logical, frobenius, dialetheia, linear) counts."""
    sig = [0, 0, 0, 0]
    for t in arr:
        sig[TOKEN_FAMILY[t]] += 1
    return tuple(sig)


# ═══════════════════════════════════════════════════════════════════
# STRUCTURAL FINGERPRINT
# ═══════════════════════════════════════════════════════════════════

class StructuralFingerprint(NamedTuple):
    """Compact fingerprint of an arrangement's structural properties."""
    length: int                    # 1-8
    sig_L: int                     # logical count
    sig_F: int                     # frobenius count
    sig_D: int                     # dialetheia count
    sig_X: int                     # linear count
    start_token: int               # 0-11
    end_token: int                 # 0-11
    self_ref: bool                 # start == end
    frobenius_order: int           # 0=none, 1=split→fuse, 2=fuse→split, 3=both
    dialetheia_complete: bool      # all 3 dialetheia present
    period: int                    # minimal period (1=constant)
    token_mask: int                # 12-bit bitmask
    fam_adj_mask: int              # 16-bit: family→family adjacency
    trans_sig: str                 # e.g. "LL:3,LF:1,FD:2,..."

    @property
    def signature(self) -> Tuple[int, int, int, int]:
        return (self.sig_L, self.sig_F, self.sig_D, self.sig_X)

    @property
    def token_diversity(self) -> int:
        return self.token_mask.bit_count()

    @property
    def is_periodic(self) -> bool:
        return self.period < self.length

    @property
    def is_constant(self) -> bool:
        return self.period == 1

    @property
    def has_frobenius_pair(self) -> bool:
        return self.frobenius_order > 0

    @property
    def frobenius_inverted(self) -> bool:
        return self.frobenius_order == 2

    def description(self) -> str:
        parts = []
        parts.append(f"sig=({self.sig_L},{self.sig_F},{self.sig_D},{self.sig_X})")
        parts.append(f"start={token_name(self.start_token)}")
        parts.append(f"end={token_name(self.end_token)}")
        if self.self_ref:
            parts.append("self-ref")
        if self.frobenius_order == 1:
            parts.append("Frobenius:split→fuse")
        elif self.frobenius_order == 2:
            parts.append("Frobenius:fuse→split(INVERTED)")
        elif self.frobenius_order == 3:
            parts.append("Frobenius:multiple")
        if self.dialetheia_complete:
            parts.append("Dialetheia:complete")
        if self.is_periodic:
            parts.append(f"period={self.period}")
        if self.is_constant:
            parts.append("constant")
        parts.append(f"diversity={self.token_diversity}/12")
        return " | ".join(parts)

    def coarse_key(self) -> str:
        return (
            f"{self.length}|{self.sig_L},{self.sig_F},{self.sig_D},{self.sig_X}|"
            f"{self.start_token}|{self.end_token}|{int(self.self_ref)}|"
            f"{self.frobenius_order}|{int(self.dialetheia_complete)}|"
            f"{self.period}|{self.token_diversity}"
        )

# ═══════════════════════════════════════════════════════════════════
# FINGERPRINT COMPUTATION
# ═══════════════════════════════════════════════════════════════════

def _frobenius_order(arr: Tuple[int, ...]) -> int:
    fsplit_positions = [i for i, t in enumerate(arr) if t == Token.FSPLIT]
    ffuse_positions = [i for i, t in enumerate(arr) if t == Token.FFUSE]
    if not fsplit_positions or not ffuse_positions:
        return 0
    first_split = min(fsplit_positions)
    first_fuse = min(ffuse_positions)
    has_split_first = first_split < max(ffuse_positions)
    has_fuse_first = first_fuse < max(fsplit_positions)
    if has_split_first and has_fuse_first:
        return 3
    elif first_split < first_fuse:
        return 1
    else:
        return 2

def _dialetheia_complete(arr: Tuple[int, ...]) -> bool:
    return Token.EVALT in arr and Token.EVALF in arr and Token.ENGAGR in arr

def _minimal_period(arr: Tuple[int, ...]) -> int:
    n = len(arr)
    for p in range(1, n + 1):
        if n % p != 0:
            continue
        if all(arr[i] == arr[i - p] for i in range(p, n)):
            return p
    return n

def _family_adjacency_mask(arr: Tuple[int, ...]) -> int:
    mask = 0
    for i in range(len(arr) - 1):
        f_from = TOKEN_FAMILY[arr[i]]
        f_to = TOKEN_FAMILY[arr[i + 1]]
        edge = f_from * 4 + f_to
        mask |= (1 << edge)
    return mask

def _transition_signature(arr: Tuple[int, ...]) -> str:
    from collections import Counter
    transitions = Counter()
    for i in range(len(arr) - 1):
        f_from = TOKEN_FAMILY[arr[i]]
        f_to = TOKEN_FAMILY[arr[i + 1]]
        key = f"{FAMILY_NAMES[f_from][0]}{FAMILY_NAMES[f_to][0]}"
        transitions[key] += 1
    return ",".join(f"{k}:{v}" for k, v in sorted(transitions.items()))

def compute_fingerprint(arr: Tuple[int, ...]) -> StructuralFingerprint:
    n = len(arr)
    sig = signature(arr)
    token_mask = 0
    for t in arr:
        token_mask |= (1 << t)
    return StructuralFingerprint(
        length=n,
        sig_L=sig[0], sig_F=sig[1], sig_D=sig[2], sig_X=sig[3],
        start_token=arr[0], end_token=arr[-1],
        self_ref=(arr[0] == arr[-1]),
        frobenius_order=_frobenius_order(arr),
        dialetheia_complete=_dialetheia_complete(arr),
        period=_minimal_period(arr),
        token_mask=token_mask,
        fam_adj_mask=_family_adjacency_mask(arr),
        trans_sig=_transition_signature(arr),
    )

# ═══════════════════════════════════════════════════════════════════
# THE 12 CANONICAL ARRANGEMENTS
# ═══════════════════════════════════════════════════════════════════

CANONICAL_ARRANGEMENTS: Dict[str, Tuple[int, ...]] = {
    "I_Dialetheic_Bootstrap":  (5, 8, 6, 9, 7, 10, 11, 5),
    "II_Void_Genesis":         (0, 1, 2, 6, 4, 7, 11, 5),
    "III_Anchor_Protocol":     (1, 3, 0, 2, 1, 4, 11, 5),
    "IV_Dual_Bootstrap":       (5, 2, 7, 6, 3, 4, 11, 5),
    "V_Linear_Chain":          (11, 11, 11, 11, 11, 11, 11, 11),
    "VI_Empty_Bootstrap":      (0, 5, 0, 5, 0, 5, 0, 5),
    "VII_Parakernel":          (9, 3, 6, 8, 2, 7, 10, 11),
    "VIII_Frobenius_Kernel":   (0, 6, 7, 1),
    "IX_Chiral_Pairs":         (2, 3, 2, 3, 2, 3, 2, 3),
    "X_Truth_Machine":         (5, 6, 8, 11, 5, 6, 9, 11),
    "XI_Eternal_Return":       (5, 2, 3, 5, 2, 3, 5, 2),
    "XII_ROM_Burn":            (8, 11, 9, 11, 10, 11, 5, 11),
}

CANONICAL_NAMES = [
    "I_Dialetheic_Bootstrap", "II_Void_Genesis", "III_Anchor_Protocol",
    "IV_Dual_Bootstrap", "V_Linear_Chain", "VI_Empty_Bootstrap",
    "VII_Parakernel", "VIII_Frobenius_Kernel", "IX_Chiral_Pairs",
    "X_Truth_Machine", "XI_Eternal_Return", "XII_ROM_Burn",
]

CANONICAL_DESCRIPTIONS = {
    "I_Dialetheic_Bootstrap":  "Self-bootstraps on paradox — contains all 3 Dialetheia + Frobenius pair",
    "II_Void_Genesis":         "Creation ex nihilo — boundary from nothing via forward morphism",
    "III_Anchor_Protocol":     "Sabbath cycle — boundary→void→boundary oscillation",
    "IV_Dual_Bootstrap":       "Synthesis before analysis — inverted Frobenius: fuse→split",
    "V_Linear_Chain":          "Pure irreversible recording — all IFIX, no return",
    "VI_Empty_Bootstrap":      "Void↔Identity alternation — minimal bootstrap oscillation",
    "VII_Parakernel":          "Paradox processing through Frobenius verification",
    "VIII_Frobenius_Kernel":   "Minimal μ∘δ=id atom — smallest Frobenius-closed arrangement",
    "IX_Chiral_Pairs":         "Forward↔Reverse morphism oscillation — chiral alternation",
    "X_Truth_Machine":         "Truth-value evaluation cycle with IFIX lock",
    "XI_Eternal_Return":       "Unclosed becoming — cycle without final IFIX lock",
    "XII_ROM_Burn":            "Truth-value recording — quantum superposition without Frobenius",
}

# Pre-computed fingerprints
CANONICAL_FINGERPRINTS: Dict[str, StructuralFingerprint] = {
    name: compute_fingerprint(arr)
    for name, arr in CANONICAL_ARRANGEMENTS.items()
}


# ═══════════════════════════════════════════════════════════════════
# ARRANGEMENT GENERATION & SEARCH
# ═══════════════════════════════════════════════════════════════════

def generate_random_arrangements(count: int, length: int = 8,
                                 seed: int = None) -> List[Tuple[int, ...]]:
    """Generate random arrangements from the 12-token universe."""
    import random

    if seed is not None:
        random.seed(seed)
    return [tuple(random.randrange(TOKEN_COUNT) for _ in range(length))
            for _ in range(count)]

def search_arrangements(length: int = 8,
                        frobenius_order: int = None,
                        dialetheia_complete: bool = None,
                        self_ref: bool = None,
                        min_diversity: int = None,
                        max_diversity: int = None,
                        required_tokens: Set[int] = None,
                        forbidden_tokens: Set[int] = None,
                        max_results: int = 1000) -> List[Tuple[int, ...]]:
    """Constrained search over the arrangement space.

    Enumerates all length-L tuples from 12 tokens and filters by structural
    constraints. For full enumeration (no constraints), the space is 12^L.
    Use with caution at L=8 (~430M combinations).

    Args:
        length: arrangement length (1-8)
        frobenius_order: 0=none, 1=split→fuse, 2=fuse→split, 3=both
        dialetheia_complete: require all 3 Dialetheia tokens
        self_ref: require start == end
        min_diversity: minimum distinct token count
        max_diversity: maximum distinct token count
        required_tokens: tokens that must appear
        forbidden_tokens: tokens that must not appear
        max_results: stop after finding this many matches
    """
    results = []
    for arr in itertools.product(range(TOKEN_COUNT), repeat=length):
        fp = compute_fingerprint(arr)
        if frobenius_order is not None and fp.frobenius_order != frobenius_order:
            continue
        if dialetheia_complete is not None and fp.dialetheia_complete != dialetheia_complete:
            continue
        if self_ref is not None and fp.self_ref != self_ref:
            continue
        if min_diversity is not None and fp.token_diversity < min_diversity:
            continue
        if max_diversity is not None and fp.token_diversity > max_diversity:
            continue
        if required_tokens and not all(t in arr for t in required_tokens):
            continue
        if forbidden_tokens and any(t in arr for t in forbidden_tokens):
            continue
        results.append(arr)
        if len(results) >= max_results:
            break
    return results

def count_arrangements(length: int = 8, **kwargs) -> int:
    """Count arrangements matching constraints (faster than search — no list build)."""
    count = 0
    kwargs['max_results'] = float('inf')
    # Reuse search logic but just count
    for arr in itertools.product(range(TOKEN_COUNT), repeat=length):
        fp = compute_fingerprint(arr)
        match = True
        if 'frobenius_order' in kwargs and fp.frobenius_order != kwargs['frobenius_order']:
            match = False
        if kwargs.get('dialetheia_complete') is not None and fp.dialetheia_complete != kwargs['dialetheia_complete']:
            match = False
        if kwargs.get('self_ref') is not None and fp.self_ref != kwargs['self_ref']:
            match = False
        if match:
            count += 1
    return count

def structural_entropy_cost(length: int = 8) -> Dict[str, float]:
    """Compute the structural entropy cost of each combined constraint.

    Returns the fraction of the full arrangement space that satisfies
    each structural condition, measured as -log2(fraction) in bits.
    """
    total = TOKEN_COUNT ** length
    costs = {}
    # Frobenius pair (split→fuse order)
    count_frob = count_arrangements(length, frobenius_order=1)
    costs['frobenius_pair'] = -np.log2(count_frob / total) if count_frob > 0 else float('inf')
    # Dialetheia complete
    count_dial = count_arrangements(length, dialetheia_complete=True)
    costs['dialetheia_complete'] = -np.log2(count_dial / total) if count_dial > 0 else float('inf')
    # Self-ref
    count_self = count_arrangements(length, self_ref=True)
    costs['self_ref'] = -np.log2(count_self / total) if count_self > 0 else float('inf')
    # Combined: Frobenius + dialetheia + self-ref (⊙ criticality)
    # Approximation by product of fractions (upper bound on actual intersection)
    costs['⊙_critical_approx'] = costs['frobenius_pair'] + costs['dialetheia_complete'] + costs['self_ref']
    return costs


# ═══════════════════════════════════════════════════════════════════
# ARRANGEMENT → ARRANGEMENT METRICS
# ═══════════════════════════════════════════════════════════════════

def arrangement_distance(a: Tuple[int, ...], b: Tuple[int, ...]) -> float:
    """Number of position mismatches between two arrangements."""
    return sum(1 for x, y in zip(a, b) if x != y)

def fingerprint_distance(fp_a: StructuralFingerprint,
                         fp_b: StructuralFingerprint) -> Dict[str, bool]:
    """Which fingerprint fields differ between two arrangements?"""
    diffs = {}
    diffs['length'] = fp_a.length != fp_b.length
    diffs['signature'] = fp_a.signature != fp_b.signature
    diffs['self_ref'] = fp_a.self_ref != fp_b.self_ref
    diffs['frobenius_order'] = fp_a.frobenius_order != fp_b.frobenius_order
    diffs['dialetheia_complete'] = fp_a.dialetheia_complete != fp_b.dialetheia_complete
    diffs['period'] = fp_a.period != fp_b.period
    diffs['token_diversity'] = fp_a.token_diversity != fp_b.token_diversity
    return diffs
