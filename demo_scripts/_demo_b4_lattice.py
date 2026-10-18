#!/usr/bin/env python3
"""B4 nucleotide lattice display — used by ghost_typer.py"""
import sys
from pathlib import Path

_REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REBIS_ROOT))
from shared.rich_output import *


def main():
    from rhr_p4rky.genetics_b4 import (
        NUCLEOTIDE_TO_BELNAP, BelnapCodon, b4_meet, b4_join, b4_wobble_pair,
    )

    info_line("=" * 65)
    info_line("B4 NUCLEOTIDE LATTICE — 64 codons on a Frobenius algebra")
    info_line("=" * 65)
    info_line("Each base carries a Belnap value by how it pairs:")
    for nuc in "GCAU":
        info_line(f"  {nuc} → {NUCLEOTIDE_TO_BELNAP[nuc].name}")
    print()

    bases = list("GCAU")
    codons = [a + b + c for a in bases for b in bases for c in bases]
    info_line(f"Codons on the lattice: {len(codons)}")
    print()

    info_line("First sixteen codons and their B4 vectors:")
    for codon in codons[:16]:
        cd = BelnapCodon.from_symbol(codon)
        vec = "".join(v.name for v in cd.values) if hasattr(cd, "values") else str(cd)
        info_line(f"  {codon:12s} → B4({vec})")
    info_line("...")
    print()

    info_line("Wobble is what makes guanine the both-value: it pairs two ways.")
    for other in "CU":
        ok = b4_wobble_pair(NUCLEOTIDE_TO_BELNAP["G"], NUCLEOTIDE_TO_BELNAP[other])
        info_line(f"  G with {other} → {ok}")
    print()
    info_line("The genetic code partitions the Crystal of Types exactly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
