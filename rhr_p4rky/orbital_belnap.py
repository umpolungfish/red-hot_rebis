"""
orbital_belnap.py — Electron orbital occupancy as Belnap FOUR bilattice.

Python mirror of Imscribing/Paraconsistent/OrbitalBelnap.lean from the
p4ramill Lean 4 project. Every type, operation, and theorem is derived
from and matches the Lean kernel exactly.

The four orbital occupancy states map to Belnap FOUR:
    empty   → N (neither)    — no electrons
    spinUp  → T (true)       — one electron, spin ↑ (positive Ħ-chirality)
    spinDown→ F (false)      — one electron, spin ↓ (negative Ħ-chirality)
    paired  → B (both)       — two electrons ↑↓ (Φ-sealed at lattice top)

Two orderings (bilattice):
    Information order (occupancy): empty < spinUp, spinDown < paired
    Truth order (chirality):       spinDown < {empty, paired} < spinUp

Theorems verified (matching Lean rfl proofs):
    - orbToB4_bijective: orbital states ↔ Belnap FOUR bijection
    - orbToB4_orderIso: order isomorphism for information order
    - paired_is_top: paired is the maximum in information order
    - pauli_exclusion: nothing lies strictly above paired (B-ceiling)
    - spinDown_is_truth_bot / spinUp_is_truth_top
    - empty_paired_truth_incomparable
    - pair_depair_id: pair ∘ depair = id (Frobenius condition)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from belnap import Belnap


class OrbitalState(Enum):
    """Four occupancy states of an atomic orbital — mirrors Lean OrbitalState."""
    empty = "empty"           # no electrons     → N
    spinUp = "spinUp"         # one electron ↑   → T
    spinDown = "spinDown"     # one electron ↓   → F
    paired = "paired"         # two electrons ↑↓ → B

    def __repr__(self) -> str:
        return f"OrbitalState.{self.value}"

    def __str__(self) -> str:
        return self.value


# ═══════════════════════════════════════════════════════════════════════════
# §2  ORBITAL → B₄ MAPPING
# ═══════════════════════════════════════════════════════════════════════════

ORB_TO_B4 = {
    OrbitalState.empty:    Belnap.N,
    OrbitalState.spinUp:   Belnap.T,
    OrbitalState.spinDown: Belnap.F,
    OrbitalState.paired:   Belnap.B,
}

B4_TO_ORB = {v: k for k, v in ORB_TO_B4.items()}


def orb_to_b4(s: OrbitalState) -> Belnap:
    """Orbital state → Belnap FOUR."""
    return ORB_TO_B4[s]


def b4_to_orb(b: Belnap) -> OrbitalState:
    """Belnap FOUR → orbital state."""
    return B4_TO_ORB[b]


def orb_to_b4_bijective() -> bool:
    """Theorem: orbToB4 is bijective (injective and surjective)."""
    # Injective: distinct orbitals map to distinct Belnap values
    seen = set()
    for s in OrbitalState:
        b = orb_to_b4(s)
        if b in seen:
            return False
        seen.add(b)
    # Surjective: every Belnap value is hit
    for b in Belnap:
        if b not in B4_TO_ORB:
            return False
    return True


# ═══════════════════════════════════════════════════════════════════════════
# §3  INFORMATION ORDER (occupancy)
#     empty ⊑ spinUp, spinDown ⊑ paired — mirrors N ⊑ T, F ⊑ B
# ═══════════════════════════════════════════════════════════════════════════

def occupancy_le(a: OrbitalState, b: OrbitalState) -> bool:
    """Information order: how much occupancy information is present."""
    if a is OrbitalState.empty:
        return True  # empty_bot: empty ≤ everything
    if a is b:
        return True  # reflexive
    if a is OrbitalState.spinUp and b is OrbitalState.paired:
        return True  # su_paired
    if a is OrbitalState.spinDown and b is OrbitalState.paired:
        return True  # sd_paired
    return False


def orb_to_b4_mono(a: OrbitalState, b: OrbitalState) -> bool:
    """Theorem: orbToB4 preserves the information order."""
    if not occupancy_le(a, b):
        return True  # vacuous
    return belnap_approx_le(orb_to_b4(a), orb_to_b4(b))


def belnap_approx_le(a: Belnap, b: Belnap) -> bool:
    """Belnap information order (from belnap.py)."""
    if a is Belnap.N:
        return True
    if b is Belnap.B:
        return True
    return a is b


def orb_to_b4_order_iso(a: OrbitalState, b: OrbitalState) -> bool:
    """Theorem: a ≤ b in occupancy order iff orbToB4(a) ≤ orbToB4(b) in Belnap order."""
    return occupancy_le(a, b) == belnap_approx_le(orb_to_b4(a), orb_to_b4(b))


# ═══════════════════════════════════════════════════════════════════════════
# §4  PAULI EXCLUSION = ANTI-EXTENSIONALITY CEILING ON B
# ═══════════════════════════════════════════════════════════════════════════

def paired_is_top(s: OrbitalState) -> bool:
    """Theorem: paired is the information-order maximum."""
    return occupancy_le(s, OrbitalState.paired)


def pauli_exclusion(s: OrbitalState) -> bool:
    """Theorem: nothing lies strictly above paired in the information order.
    If paired ≤ s, then s = paired. A third electron cannot be added;
    the B-ceiling is closed."""
    if not occupancy_le(OrbitalState.paired, s):
        return True  # vacuous
    return s is OrbitalState.paired


# ═══════════════════════════════════════════════════════════════════════════
# §5  TRUTH ORDER (chirality / Ħ-axis)
#     spinDown <_t {empty, paired} <_t spinUp — mirrors F <_t N, B <_t T
# ═══════════════════════════════════════════════════════════════════════════

def chirality_le(a: OrbitalState, b: OrbitalState) -> bool:
    """Truth order: how much positive Ħ-chirality is asserted."""
    if a is OrbitalState.spinDown:
        return True  # sd_bot: spinDown ≤ everything
    if a is b:
        return True  # reflexive
    if a is OrbitalState.empty and b is OrbitalState.spinUp:
        return True  # empty_su
    if a is OrbitalState.paired and b is OrbitalState.spinUp:
        return True  # paired_su
    return False


def spinDown_is_truth_bot(s: OrbitalState) -> bool:
    """Theorem: spinDown (F) is the truth-order minimum."""
    return chirality_le(OrbitalState.spinDown, s)


def spinUp_is_truth_top(s: OrbitalState) -> bool:
    """Theorem: spinUp (T) is the truth-order maximum."""
    return chirality_le(s, OrbitalState.spinUp)


def empty_paired_truth_incomparable() -> bool:
    """Theorem: empty (N) and paired (B) are incomparable in the truth order."""
    return (not chirality_le(OrbitalState.empty, OrbitalState.paired)
            and not chirality_le(OrbitalState.paired, OrbitalState.empty))


# ═══════════════════════════════════════════════════════════════════════════
# §6  FROBENIUS: PAIRING / DEPAIRING (Cooper pair morphisms)
#     depair : OrbitalState → (OrbitalState, OrbitalState)    ← δ
#     pair   : (OrbitalState, OrbitalState) → OrbitalState    ← μ
#     pair ∘ depair = id   — Frobenius identity at orbital level
# ═══════════════════════════════════════════════════════════════════════════

def depair(s: OrbitalState) -> Tuple[OrbitalState, OrbitalState]:
    """Depairing (δ): resolve an orbital into its two spin components."""
    return {
        OrbitalState.paired:   (OrbitalState.spinUp, OrbitalState.spinDown),
        OrbitalState.spinUp:   (OrbitalState.spinUp, OrbitalState.empty),
        OrbitalState.spinDown: (OrbitalState.empty, OrbitalState.spinDown),
        OrbitalState.empty:    (OrbitalState.empty, OrbitalState.empty),
    }[s]


def pair(a: OrbitalState, b: OrbitalState) -> OrbitalState:
    """Pairing (μ): combine two spin components into an orbital.
    Opposite spins fill the orbital; same-spin is Pauli-blocked."""
    # Opposite spins → paired
    if {a, b} == {OrbitalState.spinUp, OrbitalState.spinDown}:
        return OrbitalState.paired
    # Anything with paired → paired (already filled state absorbs)
    if a is OrbitalState.paired or b is OrbitalState.paired:
        return OrbitalState.paired
    # Same-spin: keep first
    if a is b:
        return a
    # One empty, one occupied: return the occupied one
    if a is OrbitalState.empty:
        return b
    if b is OrbitalState.empty:
        return a
    # Fallback (should not be reachable)
    return OrbitalState.empty


def pair_depair_id(s: OrbitalState) -> bool:
    """Theorem: Frobenius identity — pair(depair(s).0, depair(s).1) = s.
    For all orbital states, splitting and fusing recovers the original state."""
    (a, b) = depair(s)
    return pair(a, b) is s


# ═══════════════════════════════════════════════════════════════════════════
# §7  BILATTICE OPERATIONS (meet/join in both orders)
# ═══════════════════════════════════════════════════════════════════════════

def occupancy_meet(a: OrbitalState, b: OrbitalState) -> OrbitalState:
    """Meet in information order (occupancy)."""
    # empty ∧ _ = _, _ ∧ empty = empty
    if a is OrbitalState.empty or b is OrbitalState.empty:
        return OrbitalState.empty
    # paired ∧ x = x, x ∧ paired = x
    if a is OrbitalState.paired:
        return b
    if b is OrbitalState.paired:
        return a
    # spinUp ∧ spinDown = empty, spinDown ∧ spinUp = empty
    if {a, b} == {OrbitalState.spinUp, OrbitalState.spinDown}:
        return OrbitalState.empty
    # a = b → return a
    return a


def occupancy_join(a: OrbitalState, b: OrbitalState) -> OrbitalState:
    """Join in information order (occupancy)."""
    # paired ∨ _ = _, _ ∨ paired = paired
    if a is OrbitalState.paired or b is OrbitalState.paired:
        return OrbitalState.paired
    # empty ∨ x = x, x ∨ empty = x
    if a is OrbitalState.empty:
        return b
    if b is OrbitalState.empty:
        return a
    # spinUp ∨ spinDown = paired
    if {a, b} == {OrbitalState.spinUp, OrbitalState.spinDown}:
        return OrbitalState.paired
    # a = b → return a
    return a


# ═══════════════════════════════════════════════════════════════════════════
# §8  SELF-TEST: verify all theorems on import
# ═══════════════════════════════════════════════════════════════════════════

assert orb_to_b4_bijective(), "orbToB4_bijective FAILED"

for s in OrbitalState:
    assert paired_is_top(s), f"paired_is_top FAILED for {s}"
    assert pauli_exclusion(s), f"pauli_exclusion FAILED for {s}"
    assert pair_depair_id(s), f"pair_depair_id FAILED for {s}: pair(depair({s})) ≠ {s}"

# Verify all four orbital states map to four distinct Belnap values
assert len(set(orb_to_b4(s) for s in OrbitalState)) == 4, \
    "orbToB4 must map to 4 distinct Belnap values"

# Verify information order isomorphism
for a in OrbitalState:
    for b in OrbitalState:
        assert orb_to_b4_order_iso(a, b), \
            f"orbToB4_order_iso FAILED for ({a}, {b})"

# Verify truth order properties
for s in OrbitalState:
    assert spinDown_is_truth_bot(s), f"spinDown_is_truth_bot FAILED for {s}"
    assert spinUp_is_truth_top(s), f"spinUp_is_truth_top FAILED for {s}"

assert empty_paired_truth_incomparable(), \
    "empty_paired_truth_incomparable FAILED"

print("OrbitalBelnap: All theorems verified ✓")
print(f"  {len(OrbitalState)} orbital states ↔ {len(Belnap)} Belnap values")
print("  Frobenius condition (pair ∘ depair = id): holds for all states")
print("  Pauli exclusion: B-ceiling is closed")
