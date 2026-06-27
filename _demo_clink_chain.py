#!/usr/bin/env python3
"""CLINK Chain display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from clink import CLINK_NAMES, CLINK_TIERS, CLINK_LAYERS, format_tuple_glyphs
print("=" * 65)
print("CLINK CHAIN — The 9-Layer Ascent from Quarks to Organism")
print("=" * 65)
for i, (name, tier) in enumerate(zip(CLINK_NAMES, CLINK_TIERS)):
    tup = CLINK_LAYERS[i]
    print(f"  L{i}: {name:30s} {tier:10s}  {format_tuple_glyphs(tup)}")
print()
print(f"{len(CLINK_NAMES)} layers — Each promotion flips primitives toward O_inf")
