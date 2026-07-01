"""
belnap_c4.py — Belnap Complex Plane C₄
========================================

Extends the Belnap FOUR-valued logic (belnap.py) with the BelNap
complex plane C₄, where quantum amplitudes live:

    C₄ = {a + bi | a, b ∈ {T, F, B, N}}

The imaginary unit satisfies i² = B (both true and false), reflecting
the dialetheic structure of quantum superposition. The Born rule is a
projection from C₄ to classical probability via:

    P = proj_T(|ψ|²)

Derived from ig-docs/publishing/cleaned_papers/belnap_qm.md.

Author: Lando⊗⊙perator
"""

import sys, os
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from belnap import Belnap, band, bor, bnot
from shared.rich_output import *

T = Belnap.T
F = Belnap.F
B = Belnap.B
N = Belnap.N


class BelnapComplex:
    """A Belnap FOUR-valued complex number in C₄: a + bi where a,b ∈ {T,F,B,N}."""

    ELEMENTS = {}

    def __init__(self, real, imag):
        assert real in (T, F, B, N), f"Real must be Belnap value, got {real}"
        assert imag in (T, F, B, N), f"Imag must be Belnap value, got {imag}"
        self.real = real
        self.imag = imag

    @classmethod
    def _init_elements(cls):
        for r in (T, F, B, N):
            for i in (T, F, B, N):
                cls.ELEMENTS[(r, i)] = BelnapComplex(r, i)

    def __repr__(self):
        return f"BelnapComplex({self.real.name}, {self.imag.name}i)"

    def __eq__(self, other):
        if not isinstance(other, BelnapComplex):
            return False
        return self.real == other.real and self.imag == other.imag

    def __hash__(self):
        return hash((self.real, self.imag))

    def __add__(self, other):
        """(a+bi)+(c+di) = (a⊕c)+(b⊕d)i using Belnap join (bor)."""
        if not isinstance(other, BelnapComplex):
            return NotImplemented
        return BelnapComplex(bor(self.real, other.real), bor(self.imag, other.imag))

    def __sub__(self, other):
        """(a+bi)-(c+di) = (a∧¬c)+(b∧¬d)i."""
        if not isinstance(other, BelnapComplex):
            return NotImplemented
        return BelnapComplex(
            band(self.real, bnot(other.real)),
            band(self.imag, bnot(other.imag))
        )

    def __mul__(self, other):
        """(a+bi)(c+di) = (ac−bd)+(ad+bc)i.  i² = B (dialetheic)."""
        if not isinstance(other, BelnapComplex):
            return NotImplemented
        ac = band(self.real, other.real)
        bd = band(self.imag, other.imag)
        bd_times_B = band(bd, B)
        real_part = band(ac, bnot(bd_times_B))
        ad = band(self.real, other.imag)
        bc = band(self.imag, other.real)
        imag_part = bor(ad, bc)
        return BelnapComplex(real_part, imag_part)

    def conjugate(self):
        """(a+bi)* = a + (-b)i."""
        return BelnapComplex(self.real, bnot(self.imag))

    def magnitude_squared(self):
        """|a+bi|² = a² ⊕ b² using Belnap arithmetic."""
        a2 = band(self.real, self.real)
        b2 = band(self.imag, self.imag)
        return bor(a2, b2)

    def born_projection(self):
        """Born rule: extract probability from |ψ|²."""
        mag = self.magnitude_squared()
        if mag == T:
            return 1.0
        elif mag == F:
            return 0.0
        elif mag == B:
            return 0.5
        else:  # N
            return 0.0

    def is_superposed(self):
        return self.real == B or self.imag == B

    def is_destructive_interference(self):
        return self.real == N or self.imag == N


# ── Named C₄ Elements (definitional constants) ────────────────────

BelnapComplex._init_elements()

C4_0 = BelnapComplex(F, F)      # zero
C4_1 = BelnapComplex(T, F)      # one
C4_I = BelnapComplex(F, T)      # imaginary unit
C4_NEG1 = C4_I * C4_I           # i² computed dynamically

C4_PLUS  = BelnapComplex(T, T)  # |+>
C4_MINUS = BelnapComplex(T, F)  # |−>
C4_ZERO  = BelnapComplex(T, F)  # |0>
C4_ONE   = BelnapComplex(F, T)  # |1>

# ── Utility Functions ──────────────────────────────────────────────

def complex_to_belnap(z, epsilon=1e-10):
    """Convert a classical complex number to the nearest C₄ element."""
    def quantize(x):
        if abs(x) < epsilon:
            return N
        elif x > epsilon:
            return T
        elif x < -epsilon:
            return F
        else:
            return B
    return BelnapComplex(quantize(z.real), quantize(z.imag))


def amplitude_to_probability(amplitude):
    """Born rule: amplitude → classical probability."""
    import cmath

    if isinstance(amplitude, BelnapComplex):
        return amplitude.born_projection()
    else:
        return abs(amplitude) ** 2


def belnap_tensor_product(psi_a, psi_b):
    """Belnap tensor product of two state vectors."""
    return {
        "00": psi_a["0"].__mul__(psi_b["0"]),
        "01": psi_a["0"].__mul__(psi_b["1"]),
        "10": psi_a["1"].__mul__(psi_b["0"]),
        "11": psi_a["1"].__mul__(psi_b["1"]),
    }


if __name__ == "__main__":
    info_line("=== Belnap Complex Plane C₄ ===")
    info_line(f"Total elements: {len(BelnapComplex.ELEMENTS)}")
    print()
    i_squared = C4_I * C4_I
    info_line(f"i² = {i_squared}")
    print()
    info_line("Born projections:")
    for name, z in [("0", C4_0), ("1", C4_1), ("i", C4_I),
                    ("|+>", C4_PLUS), ("|−>", C4_MINUS)]:
        info_line(f"  P({name}) = {z.born_projection()}")
    print()
    psi_plus = {"0": BelnapComplex(T, F), "1": BelnapComplex(T, F)}
    result = belnap_tensor_product(psi_plus, psi_plus)
    info_line("|+> ⊗ |+> amplitudes:")
    for basis, amp in result.items():
        info_line(f"  |{basis}>: {amp}")
