
from shared.rich_output import *
#!/usr/bin/env python3
"""Materials simulation display — used by ghost_typer.py"""
print("=" * 65)
info_line("MATERIALS SIMULATION — 4 Engine Types")
print("=" * 65)
sims = [
    ("materials_sim.py",         "Multi-physics materials simulation"),
    ("thermal_rectifier.py",     "Asymmetric thermal diode — phonon ratchet"),
    ("ouroboric_alloy.py",       "Self-healing alloy — cyclic regeneration"),
    ("critical_metamaterial.py", "Near-zero-index metamaterial at ⊙ criticality"),
    ("frobenius_metamaterial.py", "Frobenius-closed meta-atom array"),
    ("non_qubit_qc.py",          "Non-qubit quantum computing — 12-state"),
]
for fname, desc in sims:
    info_line(f"  {fname:35s}  {desc}")
print()
info_line("Common pattern: each simulation is typed by 12-IG primitive tuple,")
info_line("verified by Frobenius closure, and designed for O_∞ convergence.")
