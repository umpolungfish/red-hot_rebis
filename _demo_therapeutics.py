
from shared.rich_output import *
#!/usr/bin/env python3
"""Therapeutics display — used by ghost_typer.py"""
info_line("=" * 65)
info_line("THERAPEUTICS — 5 Frobenius-verified Drug Design Pipelines")
info_line("=" * 65)
therapeutics = [
    ("frobenius_chemotherapeutic.py", "Cancer therapeutic — Frobenius exact"),
    ("neurotrophic_factor.py",       "Neurotrophic factor design"),
    ("ouroboric_pill_sim.py",        "Ouroboric pill — circadian release"),
    ("quantum_biologic_prototype.py", "Quantum biologic — coherence-gated"),
    ("universal_antidote_library.py", "Universal antidote — broad-spectrum"),
]
for fname, desc in therapeutics:
    info_line(f"  {fname:40s}  \u2192 {desc}")
print()
info_line("Integration: each therapeutic is typed by 12-IG primitive tuple")
info_line("and verified via Frobenius closure (mu \u2218 delta = id).")
