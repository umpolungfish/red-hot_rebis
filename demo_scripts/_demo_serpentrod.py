#!/usr/bin/env python3
"""SerpentRod display — used by ghost_typer.py"""
import sys
from pathlib import Path

_REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REBIS_ROOT))
from shared.rich_output import *


def main():
    from serpentrod.stratified_predictor import classify_module

    info_line("=" * 65)
    info_line("SERPENTROD v5 — Protein Classification by Primitive Spectrum")
    info_line("=" * 65)
    for seq, name in [("KAL", "Kinase-like"), ("ALMV", "Membrane helix"), ("MALMVL", "Test peptide")]:
        cls = classify_module(seq)
        info_line(f"  {name:20s} ({seq:8s}) → {cls}")
    print()
    info_line("Each residue maps to 1 of 12 IG primitives.")
    info_line("Classification = majority primitive vote across the sequence.")
    print()
    info_line("12-AA primitive map (each amino acid → one of 12 IG primitives):")
    from serpentrod.stratified_predictor import PRIMITIVE_MAP

    for aa, (prim, axis, _note) in sorted(PRIMITIVE_MAP.items(), key=lambda x: x[1][0]):
        info_line(f"  {aa:3s} → {prim}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
