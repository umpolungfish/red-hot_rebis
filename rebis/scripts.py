"""
rebis.scripts — Utility Scripts
════════════════════════════════
Exposes key scripts/ under rebis.scripts.<x>.

Functions:
  test_genetics()               — Run genetics tests
  frob_design(spec)             — Frobenius exact design
  mito_pipeline(spec)           — Mitochondrial pipeline
  msa_analysis(seqs)            — MSA analysis
  compute_promotions(source)    — Compute promotion paths
  analyze_validation(data)      — Validation analysis
  run_antibody(target)          — Run antibody design
  run_serpent(spec)             — Run serpent rod
  run_msa(seqs)                 — Run MSA
  run_pdb_validation(pdb)       — PDB validation runner
  psychedelic_bridge(spec)      — Psychedelic bridge
  gen_univ_map()                — Generate universal map
  omonad_bridge(spec)           — Omonad bridge
  ghost_typer(spec)             — Ghost typer
  stress_test_proteins()        — Protein stress tests
  fix_broken_multiline(file)    — Fix broken multiline in file
  fix_double_parens(file)       — Fix double parentheses

Structural Type: ⟨𐑨𐑸𐑑𐑹𐑐𐑧𐑔𐑵⊙𐑖𐑳𐑭⟩
"""

import sys
import subprocess
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
_SCRIPT_DIR = _REBIS_ROOT / "scripts"

def _run_script(name, *args):
    script = _SCRIPT_DIR / f"{name}.py"
    if not script.exists():
        raise FileNotFoundError(f"No script found: {name}")
    cmd = [sys.executable, str(script)] + list(args)
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode

def test_genetics():
    """Run the genetics test suite."""
    _run_script("test_genetics")

def frob_design(spec: str = ""):
    """Run Frobenius exact design."""
    _run_script("frobenius_exact_design", spec) if spec else _run_script("frobenius_exact_design")

def mito_pipeline(spec: str = ""):
    """Run the mitochondrial pipeline."""
    _run_script("mito_pipeline", spec)

def msa_analysis(*args):
    """Run MSA analysis."""
    _run_script("msa_analysis", *args)

def compute_promotions(source: str = ""):
    """Compute structural promotion paths."""
    _run_script("compute_promotions", source)

def analyze_validation(data: str = ""):
    """Analyze validation results."""
    _run_script("analyze_validation", data)

def run_antibody(target: str = ""):
    """Run antibody design for a target."""
    _run_script("run_antibody", target)

def run_serpent(spec: str = ""):
    """Run serpent rod design."""
    _run_script("run_serpent", spec)

def run_msa(*args):
    """Run MSA."""
    _run_script("run_msa", *args)

def run_pdb_validation(pdb_path: str = ""):
    """Run PDB validation."""
    _run_script("run_pdb_validation", pdb_path)

def psychedelic_bridge(spec: str = ""):
    """Run the psychedelic bridge."""
    _run_script("psychedelic_bridge", spec)

def gen_univ_map():
    """Generate universal map."""
    _run_script("gen_univ_map")

def omonad_bridge(spec: str = ""):
    """Run the omonad bridge."""
    _run_script("omonad_bridge", spec)

def ghost_typer(spec: str = ""):
    """Ghost typing analysis."""
    _run_script("ghost_typer", spec)

def stress_test_proteins():
    """Protein stress test suite."""
    _run_script("stress_test_proteins")

def fix_broken_multiline(file_path: str):
    """Fix broken multiline strings in a file."""
    _run_script("fix_broken_multiline", file_path)

def fix_double_parens(file_path: str):
    """Fix double parentheses in a file."""
    _run_script("fix_double_parens", file_path)

__all__ = [
    "test_genetics", "frob_design", "mito_pipeline", "msa_analysis",
    "compute_promotions", "analyze_validation", "run_antibody",
    "run_serpent", "run_msa", "run_pdb_validation",
    "psychedelic_bridge", "gen_univ_map", "omonad_bridge",
    "ghost_typer", "stress_test_proteins",
    "fix_broken_multiline", "fix_double_parens",
]
