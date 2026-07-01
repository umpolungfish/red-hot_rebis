"""
rebis.demo — Demonstration Scripts
══════════════════════════════════
Exposes all demo scripts under rebis.demo.<x>.

Each function runs a self-contained demonstration of a subsystem.

Functions:
  b4_lattice()          — B4 lattice demo
  belnap()              — Belnap logic demo
  ch3mpiler()           — Ch3mpiler compiler demo
  clink_chain()         — CLINK chain demo
  decay_chain()         — Decay chain demo
  materials()           — Materials demo
  materials_sim()       — Materials simulation demo
  catalytic_site()      — Novel catalytic site demo
  pipeline()            — Pipeline demo
  reverse_ligand()      — Reverse ligand pipeline demo
  serpentrod()          — Serpent rod demo
  therapeutics()        — Therapeutics demo
  real_demo()           — Full real demo

Structural Type: ⟨𐑨𐑸𐑑𐑹𐑐𐑧𐑔𐑵⊙𐑖𐑳𐑭⟩
"""

import sys
import subprocess
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
_DEMO_DIR = _REBIS_ROOT / "demo_scripts"

def _run_demo(name):
    script = _DEMO_DIR / f"_demo_{name}.py"
    if not script.exists():
        # try without prefix
        script = _DEMO_DIR / f"{name}.py"
    if not script.exists():
        raise FileNotFoundError(f"No demo script found: {name}")
    result = subprocess.run([sys.executable, str(script)], capture_output=False)
    return result.returncode

def b4_lattice():
    """Demonstrate the B4 lattice."""
    _run_demo("b4_lattice")

def belnap():
    """Demonstrate Belnap FOUR logic."""
    _run_demo("belnap")

def ch3mpiler():
    """Demonstrate the ch3mpiler molecular compiler."""
    _run_demo("ch3mpiler")

def clink_chain():
    """Demonstrate the CLINK chain."""
    _run_demo("clink_chain")

def decay_chain():
    """Demonstrate decay chain analysis."""
    _run_demo("decay_chain")

def materials():
    """Demonstrate materials design."""
    _run_demo("materials")

def materials_sim():
    """Demonstrate materials simulation."""
    _run_demo("materials_sim")

def catalytic_site():
    """Demonstrate novel catalytic site design."""
    _run_demo("novel_catalytic_site")

def pipeline():
    """Demonstrate the imscription pipeline."""
    _run_demo("pipeline")

def reverse_ligand():
    """Demonstrate the reverse ligand pipeline."""
    _run_demo("reverse_ligand")

def serpentrod():
    """Demonstrate serpent rod protein design."""
    _run_demo("serpentrod")

def therapeutics():
    """Demonstrate therapeutic design."""
    _run_demo("therapeutics")

def real_demo():
    """Run the full real demo."""
    _run_demo("real_demo")

def all():
    """Run all demos sequentially."""
    for name in ["b4_lattice", "belnap", "ch3mpiler", "clink_chain",
                 "decay_chain", "materials", "materials_sim",
                 "pipeline", "serpentrod", "therapeutics"]:
        print(f"\n{'='*60}")
        print(f"  Running demo: {name}")
        print(f"{'='*60}")
        _run_demo(name)

__all__ = [
    "b4_lattice", "belnap", "ch3mpiler", "clink_chain",
    "decay_chain", "materials", "materials_sim",
    "catalytic_site", "pipeline", "reverse_ligand",
    "serpentrod", "therapeutics", "real_demo", "all",
]
