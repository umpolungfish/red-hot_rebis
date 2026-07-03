#!/usr/bin/env python3
"""
rebis.ligand — PDB-Aware Ligand Design from Catalytic Sites
═══════════════════════════════════════════════════════════

Integrates the sidechain×environment algebra with the reverse ligand
pipeline for structure-aware de-novo ligand design.

Usage:
  rebis.ligand --pdb 1LYZ --active Glu35,Asp52
  rebis.ligand --pdb 1LYZ --active Glu35,Asp52 --improved --json
  rebis.ligand --pdb-file structure.pdb --auto-active --verbose
"""

import sys
import os
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(_REBIS_ROOT))
sys.path.insert(0, str(_REBIS_ROOT / "rhr_p4rky"))


def main():
    """Entry point — delegates to ligand_from_site_pdb.main()."""
    from rhr_p4rky.ligand_from_site_pdb import main as _main
    _main()


if __name__ == "__main__":
    main()
