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
    """Run a utility with separate CLI tokens and preserve its exit status."""
    script = _SCRIPT_DIR / f"{name}.py"
    if not script.exists():
        raise FileNotFoundError(f"No script found: {name}")
    cmd = [sys.executable, str(script)] + [str(arg) for arg in args if arg != ""]
    result = subprocess.run(cmd, capture_output=False, cwd=_REBIS_ROOT)
    return result.returncode

def test_genetics(*args):
    """Run the genetics test suite."""
    return _run_script("test_genetics", *args)

def frob_design(spec: str = "", *args):
    """Run Frobenius exact design."""
    return _run_script("frobenius_exact_design", spec, *args)

def mito_pipeline(spec: str = "", *args):
    """Run the mitochondrial pipeline."""
    return _run_script("mito_pipeline", spec, *args)

def msa_analysis(*args):
    """Run MSA analysis."""
    return _run_script("msa_analysis", *args)

def compute_promotions(source: str = "", *args):
    """Compute structural promotion paths."""
    return _run_script("compute_promotions", source, *args)

def analyze_validation(data: str = "", *args):
    """Analyze validation results."""
    return _run_script("analyze_validation", data, *args)

def run_antibody(target: str = "", *args):
    """Run a built-in target by name, or pass separate backend option tokens."""
    if target and not target.startswith("-"):
        return _run_script("run_antibody", "--builtin", target, *args)
    return _run_script("run_antibody", target, *args)

def run_serpent(spec: str = "", *args):
    """Run serpent rod design."""
    return _run_script("run_serpent", spec, *args)

def run_msa(*args):
    """Run MSA."""
    return _run_script("run_msa", *args)

def run_pdb_validation(pdb_path: str = "", *args):
    """Run PDB validation."""
    return _run_script("run_pdb_validation", pdb_path, *args)

def psychedelic_bridge(spec: str = "", *args):
    """Run the psychedelic bridge."""
    return _run_script("psychedelic_bridge", spec, *args)

def gen_univ_map(*args):
    """Generate universal map."""
    return _run_script("gen_univ_map", *args)

def omonad_bridge(spec: str = "", *args):
    """Run the omonad bridge."""
    return _run_script("omonad_bridge", spec, *args)

def ghost_typer(spec: str = "", *args):
    """Ghost typing analysis."""
    return _run_script("ghost_typer", spec, *args)

def stress_test_proteins(*args):
    """Protein stress test suite."""
    return _run_script("stress_test_proteins", *args)

def fix_broken_multiline(file_path: str):
    """Fix broken multiline strings in a file."""
    return _run_script("fix_broken_multiline", file_path)

def fix_double_parens(file_path: str):
    """Fix double parentheses in a file."""
    return _run_script("fix_double_parens", file_path)

__all__ = [
    "test_genetics", "frob_design", "mito_pipeline", "msa_analysis",
    "compute_promotions", "analyze_validation", "run_antibody",
    "run_serpent", "run_msa", "run_pdb_validation",
    "psychedelic_bridge", "gen_univ_map", "omonad_bridge",
    "ghost_typer", "stress_test_proteins",
    "fix_broken_multiline", "fix_double_parens",
]
