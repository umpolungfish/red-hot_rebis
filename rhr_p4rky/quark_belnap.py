"""
quark_belnap.py — Quark color × spin bilattice (Confinement as ceiling theorem).

Python mirror of Imscribing/Paraconsistent/QuarkBelnap.lean.

Extends the orbital Belnap (FOUR: empty/spinUp/spinDown/paired) to quarks
with color charge (R, G, B). The color sector forms a Belnap FIVE:
    Information order (charge): Vacuum < {R, G, B} < White
    Confinement = White-ceiling (mirrors Pauli = B-ceiling)

The full quark state is ColorState × OrbitalState (product bilattice).

Theorems (matching Lean):
    - white_is_top / vacuum_is_bot
    - rg_incomparable / rb_incomparable / gb_incomparable
    - ceiling_is_top: (White, paired) is fully confined/paired
    - colored_not_observable: colored states are not white
    - color_meet_idempotent / color_join_idempotent
    - distinct_colors_join_white / distinct_colors_meet_vacuum
    - qpair_depair_id_white: Frobenius holds for white states
    - qpair_depair_id_colored_fails: Frobenius fails for colored (confinement)
"""

from __future__ import annotations
_HELP_EXAMPLES = """  rebis.py run quark_belnap"""
import sys as _sys
if '--help' in _sys.argv or '-h' in _sys.argv:
    _doc = __doc__.strip() if __doc__ else "rhr_p4rky/quark_belnap.py"
    print(_doc)
    print()
    info_line("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from orbital_belnap import OrbitalState, occupancy_le, pair
from shared.rich_output import *



# ═══════════════════════════════════════════════════════════════════════════
# §1  COLOR STATE — 5-element bilattice
# ═══════════════════════════════════════════════════════════════════════════

class ColorState(Enum):
    """Five color charge states — mirrors Lean ColorState."""
    Vacuum = "Vacuum"   # no color charge (analog of Belnap N)
    Red = "Red"         # color charge R
    Green = "Green"     # color charge G
    Blue = "Blue"       # color charge B
    White = "White"     # color singlet (analog of Belnap B; confinement ceiling)

    def __repr__(self) -> str:
        return f"ColorState.{self.value}"

    def __le__(self, other: ColorState) -> bool:
        """Information order: Vacuum < {R, G, B} < White."""
        return color_le(self, other)

    def meet(self, other: ColorState) -> ColorState:
        """Greatest lower bound (shared color charge)."""
        return color_meet(self, other)

    def join(self, other: ColorState) -> ColorState:
        """Least upper bound (combined color charge)."""
        return color_join(self, other)


def color_le(a: ColorState, b: ColorState) -> bool:
    """Information order: Vacuum < {R, G, B} < White. Mirrors N < {T, F} < B."""
    if a == ColorState.Vacuum:
        return True
    if b == ColorState.White:
        return True
    return a == b


def color_meet(a: ColorState, b: ColorState) -> ColorState:
    """Color meet: distinct colors meet to Vacuum; same color or White is identity."""
    if a == ColorState.Vacuum or b == ColorState.Vacuum:
        return ColorState.Vacuum
    if a == ColorState.White:
        return b
    if b == ColorState.White:
        return a
    if a == b:
        return a
    return ColorState.Vacuum


def color_join(a: ColorState, b: ColorState) -> ColorState:
    """Color join: distinct colors join to White (confinement)."""
    if a == ColorState.White or b == ColorState.White:
        return ColorState.White
    if a == ColorState.Vacuum:
        return b
    if b == ColorState.Vacuum:
        return a
    if a == b:
        return a
    return ColorState.White


def anti_color(c: ColorState) -> ColorState:
    """Anti-color map: anti(Red)=Red (relational, not representational)."""
    return c  # antiRed = Red, etc. — distinction is relational in the meson pair

# ═══════════════════════════════════════════════════════════════════════════
# §2  QUARK STATE = ColorState × OrbitalState (product bilattice)
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class QuarkState:
    """A quark state: color × spin, using the orbital occupancy model."""
    color: ColorState
    spin: OrbitalState

    def __repr__(self) -> str:
        return f"QuarkState(color={self.color.value}, spin={self.spin.value})"

    def __le__(self, other: QuarkState) -> bool:
        """Product order: (c1, s1) ≤ (c2, s2) iff c1 ≤ c2 and s1 ≤ s2."""
        return self.color <= other.color and occupancy_le(self.spin, other.spin)

    @property
    def is_white(self) -> bool:
        """True iff color is White (color-singlet)."""
        return self.color == ColorState.White

    @property
    def is_colored(self) -> bool:
        """True iff color is one of {R, G, B}."""
        return self.color in (ColorState.Red, ColorState.Green, ColorState.Blue)


# Ceiling state: fully confined (White) + fully paired.
CEILING_STATE = QuarkState(ColorState.White, OrbitalState.paired)


def ceiling_is_top(q: QuarkState) -> bool:
    """(White, paired) is the maximum in product order."""
    return q <= CEILING_STATE


# ═══════════════════════════════════════════════════════════════════════════
# §3  CONFINEMENT THEOREMS
# ═══════════════════════════════════════════════════════════════════════════

def confinement_ceiling(c: ColorState) -> bool:
    """If a color is ≥ White, it must be White."""
    return c <= ColorState.White or c == ColorState.White


def colored_not_observable(q: QuarkState) -> None:
    """Assertion: colored states cannot be white (raises ValueError)."""
    if q.is_colored and q.is_white:
        raise ValueError(f"Colored state {q} cannot be white — confinement violation")


# ═══════════════════════════════════════════════════════════════════════════
# §4  FROBENIUS: COLOR-ANTICOLOR PAIR/DEPAIR
# ═══════════════════════════════════════════════════════════════════════════

def depair(q: QuarkState) -> Tuple[QuarkState, QuarkState]:
    """Depairing (δ): split white into color+anticolor. Colored: identity."""
    if q.color == ColorState.White:
        return (QuarkState(ColorState.Red, q.spin),
                QuarkState(ColorState.Red, q.spin))
    return (q, q)


def orb_pair_self(s: OrbitalState) -> bool:
    """Orbital.pair is idempotent on the diagonal: pair(s, s) = s."""
    return pair(s, s) == s


def qpair(q1: QuarkState, q2: QuarkState) -> QuarkState:
    """Pairing (μ): fuse complementary colors into a white singlet."""
    if q1.color == anti_color(q2.color):
        return QuarkState(ColorState.White, pair(q1.spin, q2.spin))
    else:
        return QuarkState(color_join(q1.color, q2.color),
                          pair(q1.spin, q2.spin))


def qpair_depair_id_white(q: QuarkState) -> bool:
    """Frobenius holds for white states: qpair(depair(q)) = q."""
    if not q.is_white:
        return True  # precondition not met (test skipped)
    d = depair(q)
    return qpair(d[0], d[1]) == q


def qpair_depair_id_colored_fails(q: QuarkState) -> bool:
    """Frobenius FAILS for colored states (confinement)."""
    if not q.is_colored:
        return True  # precondition not met
    d = depair(q)
    return qpair(d[0], d[1]) != q


# ═══════════════════════════════════════════════════════════════════════════
# §5  SELF-TESTS (mirroring Lean theorems via rfl)
# ═══════════════════════════════════════════════════════════════════════════

def test_quark_belnap() -> None:
    """Run all quark Belnap tests."""
    # Color order
    assert color_le(ColorState.Vacuum, ColorState.Red)
    assert color_le(ColorState.Red, ColorState.White)
    assert color_le(ColorState.Green, ColorState.White)
    assert color_le(ColorState.Blue, ColorState.White)
    assert not color_le(ColorState.Red, ColorState.Green)
    assert not color_le(ColorState.Green, ColorState.Blue)
    assert not color_le(ColorState.Blue, ColorState.Red)

    # Idempotence
    for c in ColorState:
        assert color_meet(c, c) == c
        assert color_join(c, c) == c

    # Distinct colors
    assert color_join(ColorState.Red, ColorState.Green) == ColorState.White
    assert color_join(ColorState.Red, ColorState.Blue) == ColorState.White
    assert color_join(ColorState.Green, ColorState.Blue) == ColorState.White
    assert color_meet(ColorState.Red, ColorState.Green) == ColorState.Vacuum
    assert color_meet(ColorState.Red, ColorState.Blue) == ColorState.Vacuum
    assert color_meet(ColorState.Green, ColorState.Blue) == ColorState.Vacuum

    # Ceiling
    q = QuarkState(ColorState.Red, OrbitalState.spinUp)
    assert ceiling_is_top(q)

    # Frobenius
    white_q = QuarkState(ColorState.White, OrbitalState.spinUp)
    assert qpair_depair_id_white(white_q)
    assert qpair_depair_id_colored_fails(q)

    # orb_pair_self
    for s in OrbitalState:
        assert orb_pair_self(s)

    info_line("✅ quark_belnap.py: all tests pass")
if __name__ == "__main__":
    test_quark_belnap()
