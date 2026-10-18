#!/usr/bin/env python3
"""Nuclear decay chain display — used by ghost_typer.py"""
import sys
from pathlib import Path

_REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REBIS_ROOT))
from shared.rich_output import *


def main():
    from rhr_p4rky.decay_chain import DECAY_SERIES

    info_line("=" * 65)
    info_line("NUCLEAR DECAY CHAIN — Each decay is one IMASM winding")
    info_line("=" * 65)
    for series_name, nuclides in list(DECAY_SERIES.items())[:3]:
        info_line(f"\n{series_name}:")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
