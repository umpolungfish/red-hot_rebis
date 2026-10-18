#!/usr/bin/env python3
"""Belnap FOUR display — used by ghost_typer.py"""
import sys
from pathlib import Path

_REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REBIS_ROOT))
from shared.rich_output import *


def main():
    from rhr_p4rky.belnap import Belnap, meet, join, bnot, designated, dialetheic

    info_line("=" * 65)
    info_line("PARACONSISTENT KERNEL — Belnap FOUR")
    info_line("=" * 65)
    print()

    vals = [Belnap.T, Belnap.B, Belnap.N, Belnap.F]
    info_line("Four values, and what negation does to each:")
    for v in vals:
        info_line(f"  {v.name:2s} → negation {bnot(v).name:2s}"
                  f"   designated: {designated(v)}   dialetheic: {dialetheic(v)}")
    print()

    info_line("meet")
    info_line("        " + "  ".join(f"{v.name:>2}" for v in vals))
    for a in vals:
        info_line(f"     {a.name:>2} " + "  ".join(f"{meet(a, b).name:>2}" for b in vals))
    print()

    info_line("join")
    info_line("        " + "  ".join(f"{v.name:>2}" for v in vals))
    for a in vals:
        info_line(f"     {a.name:>2} " + "  ".join(f"{join(a, b).name:>2}" for b in vals))
    print()

    info_line("B is the fixed point of negation, and it is where a contradiction is held")
    info_line("rather than exploded. N is the other fixed point, and holds nothing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
