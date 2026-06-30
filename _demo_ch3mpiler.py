
from shared.rich_output import *
#!/usr/bin/env python3
"""Ch3mpiler display — used by ghost_typer.py"""
info_line("=" * 65)
info_line("CH3MPILER — IG-Grounded Retrosynthetic Compiler")
info_line("=" * 65)
print()
info_line("Core operation: bond = join(tensor(FG1, FG2), bond)")
print()
info_line("Available functional groups:")
for fg in ["OH (hydroxyl)", "NH2 (amine)", "COOH (carboxyl)",
           "C=O (carbonyl)", "SH (thiol)", "PO4 (phosphate)"]:
    info_line(f"  \u2022 {fg}")
print()
info_line("Ch3mpiler ob3ect bridge:")
info_line("  ch3mpiler_ob3ect_bridge.py — maps between CH3MPILER and ob3ect types")
print()
info_line("Ch3mpiler-SerpentRod pipeline:")
info_line("  ch3mpiler_serpentrod_pipeline.py — design proteins with CH3MPILER")
print()
info_line("Additional modules:")
info_line("  ch3mpiler/scaffold_parser.py — Parse molecular scaffolds")
info_line("  ch3mpiler/reaction_deriver.py — Derive reactions from patterns")
info_line("  ch3mpiler/iupac_resolver.py — IUPAC name resolution")
