#!/usr/bin/env python3
"""Materials simulation display — used by ghost_typer.py"""
print("=" * 65)
print("MATERIALS SIMULATION — 4 Engine Types")
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
    print(f"  {fname:35s}  {desc}")
print()
print("Common pattern: each simulation is typed by 12-IG primitive tuple,")
print("verified by Frobenius closure, and designed for O_∞ convergence.")
