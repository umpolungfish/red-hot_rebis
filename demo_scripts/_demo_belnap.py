#!/usr/bin/env python3
"""Belnap FOUR display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rhr_p4rky.belnap import Belnap, meet, join, bnot, designated, dialetheic
from shared.rich_output import *

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
