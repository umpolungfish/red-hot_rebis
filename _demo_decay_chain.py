#!/usr/bin/env python3
"""Nuclear decay chain display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rhr_p4rky.decay_chain import DECAY_SERIES
from shared.rich_output import *

print("=" * 65)
info_line("NUCLEAR DECAY CHAIN — Each decay is one IMASM winding")
print("=" * 65)
for series_name, nuclides in list(DECAY_SERIES.items())[:3]:
    print(f"\n{series_name}:")
    if isinstance(nuclides, list):
        for nuc in nuclides[:5]:
            if isinstance(nuc, dict):
                parent = nuc.get("parent", "?")
                daughters = nuc.get("daughters", "?")
                info_line(f"  {parent:12s} \u2192 {daughters}")
    else:
        info_line(f"  {str(nuclides)[:60]}...")
print()
info_line("Theorem: Each decay chain winds toward a Frobenius fixed point")
info_line("(lead or bismuth — the alchemical endpoint).")
