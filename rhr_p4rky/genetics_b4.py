"""
genetics_b4.py — B₄ Nucleotide Lattice on Belnap FOUR.

First-principles derivation: The Crystal of Types (3³×4⁵×5⁴ = 17,280,000)
forces a 4-valued nucleotide alphabet. The Belnap FOUR values (N, T, F, B)
provide this alphabet with a distributive lattice structure. The mapping
is structural, not arbitrary:

  Belnap.B (Both)  ↔ G (Guanine) — top, pairs with C AND U via wobble
  Belnap.T (True)  ↔ C (Cytosine) — definite, pairs only with G
  Belnap.F (False) ↔ A (Adenine)  — definite, pairs only with U
  Belnap.N (Neither)↔ U (Uracil) — bottom-like, wobble target of G; dual to A

Watson-Crick complement (A↔U, G↔C) ≠ B₄ bnot (B↔B, N↔N, T↔F, F↔T).
Both lattice structures are simultaneously present in the genetic code.

Codon length = 3 is forced by: 4¹=4 < 20 AAs, 4²=16 < 20, 4³=64 ≥ 20.
The 3 = cardinality of the three 3-valued Crystal primitives (ƒ, Γ, Σ).
"""

from __future__ import annotations
from typing import Dict, List, Tuple

from .belnap import Belnap, meet, join, bnot


# ── Nucleotide ↔ Belnap mapping (structural, not arbitrary) ─────────────

NUCLEOTIDE_TO_BELNAP: Dict[str, Belnap] = {
    'G': Belnap.B, 'g': Belnap.B,   # Both — pairs with C AND U
    'C': Belnap.T, 'c': Belnap.T,   # True — pairs exclusively with G
    'A': Belnap.F, 'a': Belnap.F,   # False — pairs exclusively with U
    'U': Belnap.N, 'u': Belnap.N,   # Neither — wobble target; dual to A
    'T': Belnap.N, 't': Belnap.N,   # DNA thymine = U equivalent in B₄
}

BELNAP_TO_NUCLEOTIDE: Dict[Belnap, str] = {
    Belnap.B: 'G',
    Belnap.T: 'C',
    Belnap.F: 'A',
    Belnap.N: 'U',
}


def nucleotide_to_belnap(sym: str) -> Belnap:
    """Map nucleotide symbol to Belnap value."""
    b = NUCLEOTIDE_TO_BELNAP.get(sym)
    if b is None:
        raise ValueError(f"Unknown nucleotide: {sym!r}")
    return b


def belnap_to_nucleotide(b: Belnap) -> str:
    """Map Belnap value to nucleotide symbol."""
    n = BELNAP_TO_NUCLEOTIDE.get(b)
    if n is None:
        raise ValueError(f"Unknown Belnap value: {b}")
    return n


# ── B₄ lattice operations (derived from Belnap lattice) ──────────────────

def b4_meet(a: Belnap, b: Belnap) -> Belnap:
    """
    B₄ meet (∧): greatest lower bound.

    G∧G=G, C∧C=C, A∧A=A, U∧U=U
    G∧x=x, x∧G=x for all x
    C∧U = A, C∧A = A, U∧A = A  (both non-top distinct → bottom-like)
    """
    return meet(a, b)


def b4_join(a: Belnap, b: Belnap) -> Belnap:
    """
    B₄ join (∨): least upper bound.

    G∨x=G for all x; A∨x=x for all x
    C∨U=G (cross-lattice join = Both)
    C∨C=C, U∨U=U
    """
    return join(a, b)


def b4_complement(a: Belnap) -> Belnap:
    """
    Watson-Crick complement (NOT Belnap negation!)

    WC complement is a fixed-point-free involution:
    A↔U, G↔C — this is the PARITY operation, not the negation.

    This is NOT bnot. bnot(B)=B (fixed point), bnot(N)=N (fixed point).
    WC complement has NO fixed points. The two operations live on
    different lattice structures simultaneously present in the code.
    """
    return {
        Belnap.B: Belnap.T,  # G ↔ C
        Belnap.T: Belnap.B,  # C ↔ G
        Belnap.F: Belnap.N,  # A ↔ U
        Belnap.N: Belnap.F,  # U ↔ A
    }[a]


def b4_wobble_pair(a: Belnap, b: Belnap) -> bool:
    """
    Can these two nucleotides form a G-U wobble pair (or its dual)?

    A G-U wobble is specifically G(B) with U(N): join(B,N)=B.
    In B₄ terms: the weaker base (U=N) is absorbed by the stronger (G=B)
    via join-dominance. This is a LATTICE relation, not a WC pairing.
    """
    return {a, b} == {Belnap.B, Belnap.N}


def b4_lattice_distance(a: Belnap, b: Belnap) -> int:
    """
    Shortest path in the B₄ Hasse diagram.

    Same element → 0
    Covering relation (G→C, G→U, C→A, U→A) → 1
    Cross-lattice (G↔A, C↔U) → 2
    """
    if a is b:
        return 0
    # Covering relations: B ⊳ T, B ⊳ N, T ⊳ F, N ⊳ F
    if (a is Belnap.B and b in (Belnap.T, Belnap.N)) or \
       (b is Belnap.B and a in (Belnap.T, Belnap.N)) or \
       (a in (Belnap.T, Belnap.N) and b is Belnap.F) or \
       (b in (Belnap.T, Belnap.N) and a is Belnap.F):
        return 1
    return 2  # B↔F or T↔N


def b4_covering(a: Belnap, b: Belnap) -> bool:
    """Does a cover b? (direct Hasse edge: a > b with no intermediate)"""
    return b4_lattice_distance(a, b) == 1 and a is not b


# ── Codon triplet operations ────────────────────────────────────────────

class BelnapCodon:
    """A codon as a triplet of Belnap values.

    Uses the paraconsistent kernel's Belnap FOUR as the native
    nucleotide type. This is THE bridge between the kernel and
    the genetic code.
    """

    __slots__ = ('p1', 'p2', 'p3')

    def __init__(self, p1: Belnap, p2: Belnap, p3: Belnap) -> None:
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    @classmethod
    def from_symbol(cls, symbol: str) -> BelnapCodon:
        """Parse RNA/DNA symbol like 'AUG'."""
        if len(symbol) != 3:
            raise ValueError(f"Codon must be 3 nucleotides, got {symbol!r}")
        return cls(
            nucleotide_to_belnap(symbol[0]),
            nucleotide_to_belnap(symbol[1]),
            nucleotide_to_belnap(symbol[2]),
        )

    @property
    def symbol(self) -> str:
        return (belnap_to_nucleotide(self.p1) +
                belnap_to_nucleotide(self.p2) +
                belnap_to_nucleotide(self.p3))

    @property
    def box_name(self) -> str:
        """First two positions with underscore, e.g. 'CU_'."""
        return self.symbol[:2] + '_'

    @property
    def is_exact_stratum(self) -> bool:
        """
        Frobenius-exact iff position 3 carries no information.

        Derived from B₄ lattice theorem (not empirical):
        Exact iff p2 = C (T), OR p2 ∈ {U,G} (N,B) with p1 ∈ {C,G} (T,B).

        This partitions the 16 boxes as exactly 8 exact / 8 split.
        """
        if self.p2 is Belnap.T:  # C at position 2
            return True
        if self.p2 in (Belnap.B, Belnap.N) and \
           self.p1 in (Belnap.T, Belnap.B):  # C/G at pos1, G/U at pos2
            return True
        return False

    @property
    def is_stop(self) -> bool:
        return self.symbol in ("UAA", "UAG", "UGA")

    @property
    def is_start(self) -> bool:
        return self.symbol == "AUG"

    @property
    def stratum(self) -> str:
        """'exact', 'split', or 'stop'."""
        if self.is_stop:
            return "stop"
        if self.is_exact_stratum:
            return "exact"
        return "split"

    def b4_distance(self, other: BelnapCodon) -> Tuple[int, int, int]:
        """Per-position B₄ lattice distance."""
        return (
            b4_lattice_distance(self.p1, other.p1),
            b4_lattice_distance(self.p2, other.p2),
            b4_lattice_distance(self.p3, other.p3),
        )

    def total_b4_distance(self, other: BelnapCodon) -> int:
        """Sum of per-position B₄ distances."""
        return sum(self.b4_distance(other))

    def crosses_stratum(self, other: BelnapCodon) -> bool:
        """Does editing to the other codon cross Frobenius strata?"""
        return self.stratum != other.stratum

    def to_kernel_registers(self) -> Tuple[Belnap, Belnap, Belnap]:
        """
        Map codon to kernel register triple.

        Each BelnapCodon is a (p1, p2, p3) triple of Belnap values.
        The kernel operates on these directly — the codon IS the
        kernel state, and the kernel's Frobenius invariant
        (ffuse∘fsplit = id) IS the genetic code's μ∘δ=id.
        """
        return (self.p1, self.p2, self.p3)

    @classmethod
    def from_kernel_registers(cls, r0: Belnap, r1: Belnap,
                              r2: Belnap) -> BelnapCodon:
        """Reconstruct codon from kernel register state."""
        return cls(r0, r1, r2)

    def __repr__(self) -> str:
        return (f"BelnapCodon({self.symbol} → "
                f"[{self.stratum}] "
                f"{self.p1.value}{self.p2.value}{self.p3.value})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BelnapCodon):
            return NotImplemented
        return (self.p1 is other.p1 and self.p2 is other.p2
                and self.p3 is other.p3)

    def __hash__(self) -> int:
        return hash((self.p1, self.p2, self.p3))
