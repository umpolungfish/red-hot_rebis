#!/usr/bin/env python3
"""Material forge display — used by ghost_typer.py"""
import sys
from pathlib import Path

_REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REBIS_ROOT))
from shared.rich_output import *


def main():
    from materials.ig_material_forge import predefined_novel_materials

    materials = predefined_novel_materials()

    info_line("=" * 65)
    info_line(f"IG MATERIAL FORGE — {len(materials)} predefined novel materials")
    info_line("=" * 65)
    for name, data in sorted(materials.items()):
        if isinstance(data, dict):
            shown = str(data.get("description", ""))[:60]
        else:
            shown = "⟨" + "".join(data) + "⟩"
        info_line(f"  {name:35s}  {shown}")
    print()
    info_line("Available subcommands:")
    info_line("  rebis.materials forge        # forge every material")
    info_line("  rebis.materials frobenius    # metamaterial simulation")
    info_line("  rebis.materials ouroboric    # ouroboric alloy")
    info_line("  rebis.materials sophick      # sophick mercury analysis")
    info_line("  rebis.materials exactor      # Frobenius gap closure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
