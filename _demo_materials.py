#!/usr/bin/env python3
"""Materials Forge display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from materials.ig_material_forge import PREDEFINED_MATERIALS
print("=" * 65)
print("IG MATERIAL FORGE — 8 Predefined Novel Materials")
print("=" * 65)
for name, data in sorted(PREDEFINED_MATERIALS.items()):
    desc = data.get("description", "")[:60]
    print(f"  {name:35s}  {desc}")
print()
print("Available subcommands:")
print("  rebis.py materials forge --all        # Forge all 8 materials")
print("  rebis.py materials frobenius          # Meta-material simulation")
print("  rebis.py materials ouroboric          # Ouroboric alloy")
print("  rebis.py materials sophick            # Sophick Mercury analysis")
print("  rebis.py materials exactor            # Frobenius gap closure")
