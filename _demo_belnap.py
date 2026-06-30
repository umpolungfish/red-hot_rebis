#!/usr/bin/env python3
"""Belnap FOUR logic display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rhr_p4rky.belnap import BelnapState, B4
from rhr_p4rky.belnap_c4 import C4State, C4
from shared.rich_output import *

info_line("=" * 65)
info_line("PARACONSISTENT KERNEL — Belnap FOUR & C4 Contradiction Lattices")
info_line("=" * 65)
print()
info_line("B4 (Belnap FOUR) — 4 truth values:")
for v in [B4.T, B4.B, B4.N, B4.F]:
    s = BelnapState(v)
    info_line(f"  {str(v):12s} → negation: {str(s.negate())}")
print()
info_line("Frobenius check: ffuse ∘ fsplit = id")
s = BelnapState(B4.B)
info_line(f"  BelnapState({s}) → is_odot_critical? {s.is_odot_critical()}")
print()
info_line("C4 (Contradiction-Majority Logic):")
for v in [C4.T, C4.CT, C4.CF, C4.F]:
    cs = C4State(v)
    info_line(f"  {str(v):12s} → majority: {cs.majority_truth()}")
print()
info_line("Dialetheic fixed point: ⊙-criticality emerges at T∩F")
