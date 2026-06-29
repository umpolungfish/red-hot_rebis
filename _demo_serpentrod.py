#!/usr/bin/env python3
"""SerpentRod display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from serpentrod.stratified_predictor import classify_module
print("=" * 65)
info_line("SERPENTROD v5 — Protein Classification by Primitive Spectrum")
print("=" * 65)
for seq, name in [("KAL", "Kinase-like"), ("ALMV", "Membrane helix"), ("MALMVL", "Test peptide")]:
    cls = classify_module(seq)
    info_line(f"  {name:20s} ({seq:8s}) → {cls}")
print()
info_line("Each residue maps to 1 of 12 IG primitives.")
info_line("Classification = majority primitive vote across the sequence.")
print()
info_line("12-AA primitive map (each amino acid → one of 12 IG primitives):")
from rhr_p4rky.genetic_code import PRIMITIVE_MAP
from shared.rich_output import *

for aa, (prim, _) in sorted(PRIMITIVE_MAP.items(), key=lambda x: x[1][0]):
    info_line(f"  {aa:3s} → {prim}")
