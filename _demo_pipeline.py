#!/usr/bin/env python3
"""Pipeline modules display — used by ghost_typer.py"""
from pathlib import Path
import os
p = Path("pipeline")
py_files = sorted(p.glob("*.py"))
print("=" * 65)
print("PIPELINE MODULES — Verification, Scaffolding, Reaction Design")
print("=" * 65)
for f in py_files:
    lines = len(f.read_text().splitlines())
    print(f"  {f.name:30s}  {lines:5d} lines")
print()
print("Key tools:")
print("  pipeline/frob.py           — Frobenius verification")
print("  pipeline/auto_imscriber.py — Auto-imscription pipeline")
print("  pipeline/reaction_pipeline.py — Chemical reaction design")
print("  pipeline/imscribe_agent.py — IG imscription agent")
print("  pipeline/patch_scaffold*   — Scaffold patching tools")
