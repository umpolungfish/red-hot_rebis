#!/usr/bin/env python3
"""
rebis.py — Red-Hot Rebis CLI (thin wrapper)
═════════════════════════════════════════════
Delegates to rebis.cli.main() — the rebis.<x> namespace package.

All tools are now accessible as:  rebis.<domain>.<function>(...)

  import rebis
  rebis.p4ra.meet(a, b)
  rebis.ch3mpiler.compile(smiles)
  rebis.materials.design_metamaterial(spec)
  rebis.demo.b4_lattice()

Structural Type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩
"""

import sys
import os
from pathlib import Path

# Ensure rebis/ package is importable
_REBIS_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(_REBIS_ROOT))

if __name__ == "__main__":
    from rebis.cli import main
    sys.exit(main())
