#!/usr/bin/env python3
"""Nuclear decay chain display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rhr_p4rky.decay_chain import DECAY_SERIES
print("=" * 65)
print("NUCLEAR DECAY CHAIN — Each decay is one IMASM winding")
print("=" * 65)
for series_name, nuclides in list(DECAY_SERIES.items())[:3]:
    print(f"\n{series_name}:")
    if isinstance(nuclides, list):
        for nuc in nuclides[:5]:
            if isinstance(nuc, dict):
                parent = nuc.get("parent", "?")
                daughters = nuc.get("daughters", "?")
                print(f"  {parent:12s} \u2192 {daughters}")
    else:
        print(f"  {str(nuclides)[:60]}...")
print()
print("Theorem: Each decay chain winds toward a Frobenius fixed point")
print("(lead or bismuth — the alchemical endpoint).")
