#!/usr/bin/env python3
"""CLINK Chain display — used by ghost_typer.py"""
import sys
from pathlib import Path

_REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REBIS_ROOT))
from shared.rich_output import *


def main():
    from clink import CLINK_NAMES, CLINK_TIERS, CLINK_LAYERS, format_tuple_glyphs

    info_line("=" * 65)
    info_line("CLINK CHAIN — The 9-Layer Ascent from Quarks to Organism")
    info_line("=" * 65)
    for i, (name, tier) in enumerate(zip(CLINK_NAMES, CLINK_TIERS)):
        tup = CLINK_LAYERS[i]
        info_line(f"  L{i}: {name:30s} {tier:10s}  {format_tuple_glyphs(tup)}")
    print()
    info_line(f"{len(CLINK_NAMES)} layers — Each promotion flips primitives toward O_inf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
