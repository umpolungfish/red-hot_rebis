"""
belnap.py — Belnap four-valued logic.

Python mirror of Imscribing/Paraconsistent/Belnap.lean from the p4ramill
Lean 4 project. Every type, operation, and theorem is derived from and
matches the Lean kernel exactly.

Belnap FOUR:
    N — Neither (void, bottom)
    T — True
    F — False
    B — Both (dialetheia, top in information order)

Theorems verified (matching Lean rfl proofs):
    - B_fixed_point_negation: ¬B = B
    - no_explosion: B ∧ ¬B = B (not F)
    - B_ne_F: B ≠ F
    - only_B_is_dialetheic: B is the unique dialetheic value
    - designated: T and B are designated; N and F are not
"""

from __future__ import annotations
from enum import Enum
from typing import Tuple


class Belnap(Enum):
    """Belnap four-valued logic — mirrors the Lean inductive type."""
    N = "N"  # Neither
    T = "T"  # True
    F = "F"  # False
    B = "B"  # Both (dialetheia)

    def to_nat(self) -> int:
        """Mirrors belnapToNat: N→0, T→1, F→2, B→3."""
        return {"N": 0, "T": 1, "F": 2, "B": 3}[self.value]

    def __repr__(self) -> str:
        return f"Belnap.{self.value}"

    def __str__(self) -> str:
        return self.value


# ── Lattice operations (mirror Belnap.lean) ───────────────────────────────

def meet(a: Belnap, b: Belnap) -> Belnap:
    """Information-order meet (greatest lower bound)."""
    # N ∧ _ = N, _ ∧ N = N
    if a is Belnap.N or b is Belnap.N:
        return Belnap.N
    # B ∧ x = x, x ∧ B = x
    if a is Belnap.B:
        return b
    if b is Belnap.B:
        return a
    # T ∧ F = N, F ∧ T = N
    if a is Belnap.T and b is Belnap.F or a is Belnap.F and b is Belnap.T:
        return Belnap.N
    # T ∧ T = T, F ∧ F = F
    return a  # a == b here


def join(a: Belnap, b: Belnap) -> Belnap:
    """Information-order join (least upper bound)."""
    # B ∨ _ = B, _ ∨ B = B
    if a is Belnap.B or b is Belnap.B:
        return Belnap.B
    # N ∨ x = x, x ∨ N = x
    if a is Belnap.N:
        return b
    if b is Belnap.N:
        return a
    # T ∨ F = B, F ∨ T = B
    if a is Belnap.T and b is Belnap.F or a is Belnap.F and b is Belnap.T:
        return Belnap.B
    # T ∨ T = T, F ∨ F = F
    return a


def band(a: Belnap, b: Belnap) -> Belnap:
    """Truth-functional conjunction. Mirrors Belnap.lean `band`."""
    # F ∧ _ = F, _ ∧ F = F
    if a is Belnap.F or b is Belnap.F:
        return Belnap.F
    # B ∧ T, T ∧ B, B ∧ N, N ∧ B → B
    if (a is Belnap.B and b is Belnap.T) or (a is Belnap.T and b is Belnap.B) \
       or (a is Belnap.B and b is Belnap.N) or (a is Belnap.N and b is Belnap.B):
        return Belnap.B
    # T ∧ T = T
    if a is Belnap.T and b is Belnap.T:
        return Belnap.T
    # T ∧ N, N ∧ T → N
    if (a is Belnap.T and b is Belnap.N) or (a is Belnap.N and b is Belnap.T):
        return Belnap.N
    # N ∧ N = N
    if a is Belnap.N and b is Belnap.N:
        return Belnap.N
    # B ∧ B = B
    return Belnap.B


def bor(a: Belnap, b: Belnap) -> Belnap:
    """Truth-functional disjunction. Mirrors Belnap.lean `bor`."""
    # T ∨ _ = T, _ ∨ T = T
    if a is Belnap.T or b is Belnap.T:
        return Belnap.T
    # B ∨ F, F ∨ B, B ∨ N, N ∨ B → B
    if (a is Belnap.B and b is Belnap.F) or (a is Belnap.F and b is Belnap.B) \
       or (a is Belnap.B and b is Belnap.N) or (a is Belnap.N and b is Belnap.B):
        return Belnap.B
    # F ∨ F = F
    if a is Belnap.F and b is Belnap.F:
        return Belnap.F
    # F ∨ N, N ∨ F → N
    if (a is Belnap.F and b is Belnap.N) or (a is Belnap.N and b is Belnap.F):
        return Belnap.N
    # N ∨ N = N
    if a is Belnap.N and b is Belnap.N:
        return Belnap.N
    # B ∨ B = B
    return Belnap.B


def bnot(a: Belnap) -> Belnap:
    """Belnap negation: ¬N=N, ¬T=F, ¬F=T, ¬B=B. Mirrors Belnap.lean `bnot`."""
    return {
        Belnap.N: Belnap.N,
        Belnap.T: Belnap.F,
        Belnap.F: Belnap.T,
        Belnap.B: Belnap.B,
    }[a]


def designated(a: Belnap) -> bool:
    """Designated values: T and B count as 'true' for paraconsistent consequence."""
    return a in (Belnap.T, Belnap.B)


# ── Approximation order (ApproxLE from Belnap.lean) ──────────────────────

def approx_le(a: Belnap, b: Belnap) -> bool:
    """Information order: N ≤ everything, everything ≤ B, otherwise reflexive."""
    if a is Belnap.N:
        return True
    if b is Belnap.B:
        return True
    return a is b


# ── WH2 bijection (Belnap ↔ ℤ₂×ℤ₂) ─────────────────────────────────────
# N→(0,0)=I, T→(0,1)=Z, F→(1,0)=X, B→(1,1)=XZ
_TO_WH2 = {
    Belnap.N: (0, 0),
    Belnap.T: (0, 1),
    Belnap.F: (1, 0),
    Belnap.B: (1, 1),
}
_FROM_WH2 = {v: k for k, v in _TO_WH2.items()}


def to_wh2(a: Belnap) -> Tuple[int, int]:
    """Belnap → ℤ₂×ℤ₂ bijection."""
    return _TO_WH2[a]


def from_wh2(ab: Tuple[int, int]) -> Belnap:
    """ℤ₂×ℤ₂ → Belnap bijection."""
    return _FROM_WH2[ab]


# ── Dialetheic predicate ─────────────────────────────────────────────────

def dialetheic(a: Belnap) -> bool:
    """A value is dialetheic iff it and its negation are both designated."""
    return designated(a) and designated(bnot(a))


# ── Verified theorems (mirroring Lean rfl proofs) ─────────────────────────

# Theorem: ¬B = B (B_fixed_point_negation)
assert bnot(Belnap.B) is Belnap.B, "B_fixed_point_negation violated: ¬B ≠ B"

# Theorem: B ∧ ¬B = B (no_explosion — contradiction is contained, not explosive)
assert band(Belnap.B, bnot(Belnap.B)) is Belnap.B, \
    "no_explosion violated: B ∧ ¬B ≠ B"

# Theorem: B ≠ F (B_ne_F — false does not collapse to contradiction)
assert Belnap.B is not Belnap.F, "B_ne_F violated: B collapsed to F"

# Theorem: designated values are exactly T and B
assert designated(Belnap.T) is True, "T must be designated"
assert designated(Belnap.B) is True, "B must be designated"
assert designated(Belnap.N) is False, "N must not be designated"
assert designated(Belnap.F) is False, "F must not be designated"

# Theorem: only_B_is_dialetheic
assert dialetheic(Belnap.B), "B must be dialetheic"
for v in Belnap:
    if v is not Belnap.B:
        assert not dialetheic(v), f"Only B should be dialetheic, but {v} is"

# Theorem: B is top in information order (B_is_top)
for v in Belnap:
    assert approx_le(v, Belnap.B), f"B_is_top violated: {v} ⋢ B"

# Theorem: B_meet_equiangular — B ∧ x = x for all x
for v in Belnap:
    assert meet(Belnap.B, v) is v, f"B_meet_equiangular violated for {v}"
    assert meet(v, Belnap.B) is v, f"B_meet_equiangular violated for {v}"

# Theorem: B_join_universal — B ∨ x = B for all x
for v in Belnap:
    assert join(Belnap.B, v) is Belnap.B, f"B_join_universal violated for {v}"
    assert join(v, Belnap.B) is Belnap.B, f"B_join_universal violated for {v}"

# Theorem: BELNAP_FOUR distinct — all four values are distinct
assert len(set(Belnap)) == 4, "four_values_distinct violated"
