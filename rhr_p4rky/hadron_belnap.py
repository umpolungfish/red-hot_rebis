"""
hadron_belnap.py — Meson and Baryon as tensor products of QuarkState.

Python mirror of Imscribing/Paraconsistent/HadronBelnap.lean.

Builds on QuarkBelnap (Color × Spin bilattice, confinement ceiling)
to construct composite hadrons:
    Meson  = q̄·q  (color + anticolor → White singlet)
    Baryon = q·q·q (three quarks → White singlet via SU(3) antisymmetry)

Theorems (matching Lean):
    - meson_is_white: mesons are color-singlet by construction
    - meson_frobenius: μ∘δ = id for mesons
    - baryon_is_white: baryons are color-singlet by construction
    - baryon_frobenius: μ∘δ = id for baryons
    - hadron_frobenius_unified: both mesons and baryons satisfy μ∘δ=id
"""

from __future__ import annotations
_HELP_EXAMPLES = """  rebis.py run hadron_belnap"""
import sys as _sys

if __name__ == "__main__":
    if '--help' in _sys.argv or '-h' in _sys.argv:
        _doc = __doc__.strip() if __doc__ else "rhr_p4rky/hadron_belnap.py"
        print(_doc)
        print()
        print("Examples:")
        print(_HELP_EXAMPLES)
        print()
        _sys.exit(0)

from dataclasses import dataclass
from typing import Optional, Tuple

import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

from quark_belnap import (
    ColorState, QuarkState, anti_color, color_join,
    color_meet, CEILING_STATE
)
from orbital_belnap import OrbitalState, pair
from shared.rich_output import *

# ═══════════════════════════════════════════════════════════════════════════
# §1  MESON = q̄·q
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Meson:
    """A color-anticolor pair combining to a white singlet."""
    quark: QuarkState
    antiquark: QuarkState

    def __post_init__(self):
        """Validate that colors are complementary (confinement)."""
        if self.quark.color != anti_color(self.antiquark.color):
            raise ValueError(
                f"Meson requires complementary colors: "
                f"{self.quark.color} vs {self.antiquark.color}"
            )

    @property
    def color(self) -> ColorState:
        """Effective color is always White (confinement)."""
        return ColorState.White

    @property
    def spin(self) -> OrbitalState:
        """Net spin is the orbital pair of constituents' spins."""
        return pair(self.quark.spin, self.antiquark.spin)

def try_make_meson(q1: QuarkState, q2: QuarkState) -> Optional[Meson]:
    """Construct a meson if colors are complementary, else None."""
    if q1.color == anti_color(q2.color):
        return Meson(quark=q1, antiquark=q2)
    return None

def meson_depair(m: Meson) -> Tuple[QuarkState, QuarkState]:
    """Meson depairing (δ): split into constituent quarks."""
    return (m.quark, m.antiquark)

def meson_pair(q1: QuarkState, q2: QuarkState) -> Optional[Meson]:
    """Meson pairing (μ): combine two complementary-color quarks."""
    return try_make_meson(q1, q2)

def meson_frobenius(m: Meson) -> bool:
    """Frobenius for mesons: μ∘δ = id."""
    d = meson_depair(m)
    result = meson_pair(d[0], d[1])
    return result == m

# ═══════════════════════════════════════════════════════════════════════════
# §2  BARYON = q·q·q
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Baryon:
    """Three quarks with distinct colors (R, G, B) → white singlet."""
    q1: QuarkState
    q2: QuarkState
    q3: QuarkState

    def __post_init__(self):
        """Validate colors are distinct and charged (not Vacuum/White)."""
        colors = [self.q1.color, self.q2.color, self.q3.color]
        # Must all be non-Vacuum, non-White
        for c in colors:
            if c in (ColorState.Vacuum, ColorState.White):
                raise ValueError(f"Baryon requires charged colors, got {c}")
        # Must all be distinct
        if len(set(colors)) != 3:
            raise ValueError(f"Baryon requires three distinct colors, got {colors}")
        # Join must be White
        join_all = color_join(color_join(self.q1.color, self.q2.color), self.q3.color)
        if join_all != ColorState.White:
            raise ValueError(f"Baryon colors must join to White, got {join_all}")

    @property
    def color(self) -> ColorState:
        """Effective color is always White (confinement)."""
        return ColorState.White

    @property
    def spin(self) -> OrbitalState:
        """Net spin is the three-way orbital pair."""
        return pair(pair(self.q1.spin, self.q2.spin), self.q3.spin)

def try_make_baryon(q1: QuarkState, q2: QuarkState, q3: QuarkState) -> Optional[Baryon]:
    """Construct a baryon if colors are distinct charged colors, else None."""
    try:
        b = Baryon(q1=q1, q2=q2, q3=q3)
        return b
    except ValueError:
        return None

def baryon_depair(b: Baryon) -> Tuple[QuarkState, QuarkState, QuarkState]:
    """Baryon depairing (δ): split into three constituent quarks."""
    return (b.q1, b.q2, b.q3)

def baryon_pair(q1: QuarkState, q2: QuarkState, q3: QuarkState) -> Optional[Baryon]:
    """Baryon pairing (μ): combine three quarks into a white singlet."""
    return try_make_baryon(q1, q2, q3)

# ═══════════════════════════════════════════════════════════════════════════
# §3  FROBENIUS FOR HADRONS
# ═══════════════════════════════════════════════════════════════════════════

def baryon_frobenius(b: Baryon) -> bool:
    """Frobenius for baryons: μ∘δ = id."""
    d = baryon_depair(b)
    result = baryon_pair(d[0], d[1], d[2])
    return result == b

def hadron_frobenius_unified(m: Meson, b: Baryon) -> Tuple[bool, bool]:
    """Both mesons and baryons satisfy μ∘δ = id."""
    return (meson_frobenius(m), baryon_frobenius(b))

# ═══════════════════════════════════════════════════════════════════════════
# §4  SELF-TESTS
# ═══════════════════════════════════════════════════════════════════════════

def build_meson_example() -> Meson:
    """Build a sample meson: Red-quark + antiRed-quark → white singlet."""
    q_red = QuarkState(ColorState.Red, OrbitalState.spinUp)
    q_antired = QuarkState(ColorState.Red, OrbitalState.spinDown)
    return Meson(quark=q_red, antiquark=q_antired)

def build_baryon_example() -> Baryon:
    """Build a sample baryon: R↑, G↓, B↑ → white singlet."""
    q_r = QuarkState(ColorState.Red, OrbitalState.spinUp)
    q_g = QuarkState(ColorState.Green, OrbitalState.spinDown)
    q_b = QuarkState(ColorState.Blue, OrbitalState.spinUp)
    return Baryon(q1=q_r, q2=q_g, q3=q_b)

def test_hadron_belnap() -> None:
    """Run all hadron Belnap tests."""
    # Meson tests
    m = build_meson_example()
    assert m.color == ColorState.White
    assert meson_frobenius(m)

    # Meson construction failure
    q_r = QuarkState(ColorState.Red, OrbitalState.spinUp)
    q_g = QuarkState(ColorState.Green, OrbitalState.spinDown)
    assert try_make_meson(q_r, q_g) is None  # different colors, not anti

    # Baryon tests
    b = build_baryon_example()
    assert b.color == ColorState.White
    assert baryon_frobenius(b)

    # Baryon construction failure (duplicate colors)
    q_r2 = QuarkState(ColorState.Red, OrbitalState.spinDown)
    assert try_make_baryon(q_r, q_r2, q_g) is None

    # Unified Frobenius
    m_both, b_both = hadron_frobenius_unified(m, b)
    assert m_both and b_both

    info_line("✅ hadron_belnap.py: all tests pass")
if __name__ == "__main__":
    test_hadron_belnap()
