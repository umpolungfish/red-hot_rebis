#!/usr/bin/env python3
"""Ch3mpiler display — used by ghost_typer.py"""
print("=" * 65)
print("CH3MPILER — IG-Grounded Retrosynthetic Compiler")
print("=" * 65)
print()
print("Core operation: bond = join(tensor(FG1, FG2), bond)")
print()
print("Available functional groups:")
for fg in ["OH (hydroxyl)", "NH2 (amine)", "COOH (carboxyl)",
           "C=O (carbonyl)", "SH (thiol)", "PO4 (phosphate)"]:
    print(f"  \u2022 {fg}")
print()
print("Ch3mpiler ob3ect bridge:")
print("  ch3mpiler_ob3ect_bridge.py — maps between CH3MPILER and ob3ect types")
print()
print("Ch3mpiler-SerpentRod pipeline:")
print("  ch3mpiler_serpentrod_pipeline.py — design proteins with CH3MPILER")
print()
print("Additional modules:")
print("  ch3mpiler/scaffold_parser.py — Parse molecular scaffolds")
print("  ch3mpiler/reaction_deriver.py — Derive reactions from patterns")
print("  ch3mpiler/iupac_resolver.py — IUPAC name resolution")
