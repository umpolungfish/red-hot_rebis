#!/usr/bin/env python3
"""SerpentRod display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from serpentrod.stratified_predictor import classify_module
print("=" * 65)
print("SERPENTROD v5 — Protein Classification by Primitive Spectrum")
print("=" * 65)
for seq, name in [("KAL", "Kinase-like"), ("ALMV", "Membrane helix"), ("MALMVL", "Test peptide")]:
    cls = classify_module(seq)
    print(f"  {name:20s} ({seq:8s}) → {cls}")
print()
print("Each residue maps to 1 of 12 IG primitives.")
print("Classification = majority primitive vote across the sequence.")
print()
print("12-AA primitive map (each amino acid → one of 12 IG primitives):")
from rhr_p4rky.genetic_code import PRIMITIVE_MAP
for aa, (prim, _) in sorted(PRIMITIVE_MAP.items(), key=lambda x: x[1][0]):
    print(f"  {aa:3s} → {prim}")
