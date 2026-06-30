#!/usr/bin/env python3
"""Materials Forge display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from materials.ig_material_forge import PREDEFINED_MATERIALS
from shared.rich_output import *

info_line("=" * 65)
info_line("IG MATERIAL FORGE — 8 Predefined Novel Materials")
info_line("=" * 65)
for name, data in sorted(PREDEFINED_MATERIALS.items()):
    desc = data.get("description", "")[:60]
    info_line(f"  {name:35s}  {desc}")
print()
info_line("Available subcommands:")
info_line("  rebis.py materials forge --all        # Forge all 8 materials")
info_line("  rebis.py materials frobenius          # Meta-material simulation")
info_line("  rebis.py materials ouroboric          # Ouroboric alloy")
info_line("  rebis.py materials sophick            # Sophick Mercury analysis")
info_line("  rebis.py materials exactor            # Frobenius gap closure")
