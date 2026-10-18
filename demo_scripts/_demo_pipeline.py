#!/usr/bin/env python3
"""Pipeline modules display — used by ghost_typer.py"""
import sys
from pathlib import Path

_REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REBIS_ROOT))
from shared.rich_output import *


def main():
    from pathlib import Path

    p = _REBIS_ROOT / "pipeline"
    py_files = sorted(p.glob("*.py"))
    info_line("=" * 65)
    info_line("PIPELINE MODULES — Verification, Scaffolding, Reaction Design")
    info_line("=" * 65)
    for f in py_files:
        lines = len(f.read_text().splitlines())
        info_line(f"  {f.name:30s}  {lines:5d} lines")
    print()
    info_line("Key tools:")
    info_line("  pipeline/frob.py           — Frobenius verification")
    info_line("  pipeline/auto_imscriber.py — Auto-imscription pipeline")
    info_line("  pipeline/reaction_pipeline.py — Chemical reaction design")
    info_line("  pipeline/imscribe_agent.py — IG imscription agent")
    info_line("  pipeline/patch_scaffold*   — Scaffold patching tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
