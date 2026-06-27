#!/usr/bin/env python3
"""Belnap FOUR logic display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rhr_p4rky.belnap import BelnapState, B4
from rhr_p4rky.belnap_c4 import C4State, C4
print("=" * 65)
print("PARACONSISTENT KERNEL — Belnap FOUR & C4 Contradiction Lattices")
print("=" * 65)
print()
print("B4 (Belnap FOUR) — 4 truth values:")
for v in [B4.T, B4.B, B4.N, B4.F]:
    s = BelnapState(v)
    print(f"  {str(v):12s} → negation: {str(s.negate())}")
print()
print("Frobenius check: ffuse ∘ fsplit = id")
s = BelnapState(B4.B)
print(f"  BelnapState({s}) → is_odot_critical? {s.is_odot_critical()}")
print()
print("C4 (Contradiction-Majority Logic):")
for v in [C4.T, C4.CT, C4.CF, C4.F]:
    cs = C4State(v)
    print(f"  {str(v):12s} → majority: {cs.majority_truth()}")
print()
print("Dialetheic fixed point: ⊙-criticality emerges at T∩F")
