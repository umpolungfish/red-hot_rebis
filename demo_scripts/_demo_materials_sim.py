
from shared.rich_output import *
import sys
from pathlib import Path

_REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REBIS_ROOT))
from shared.rich_output import *


def main():
    #!/usr/bin/env python3
    """Materials simulation display — used by ghost_typer.py"""
    info_line("=" * 65)
    info_line("MATERIALS SIMULATION — Engine Types")
    info_line("=" * 65)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
