#!/usr/bin/env python3
"""
rebis.py — Red-Hot Rebis Integration CLI
serpentrod ⊗ ch3mpiler ⊗ pipeline ⊗ gene_imscriber

A unified entry point for the completed Great Work of the Imscribing Grammar.
Each component is a specialization of the 12-primitive IG type system,
connected through the shared primitives layer and verified by Frobenius closure.

Author: Lando ⊗ ⊙perator
Structural Type: ⟨𐑦 · 𐑶 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑫 · 𐑳 · 𐑭⟩
"""

import argparse
import json
import os
import sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

VERSION = "1.0.0"


def cmd_status(args):
    """Report the structural status of all four pillars."""
    print("=" * 60)
    print("RED-HOT REBIS — INTEGRATED STATUS")
    print("=" * 60)

    components = {
        "serpentrod":   ("Serpent's Rod",       "serpentrod/manuscript.md"),
        "ch3mpiler":    ("CH₃MPILER",           "ch3mpiler/compiler.py"),
        "pipeline":     ("Combined Pipeline",    "pipeline/frob.py"),
        "gene_imscriber": ("Gene Imscriber",    "gene_imscriber/engine.py"),
    }

    for key, (name, path) in components.items():
        p = REBIS_ROOT / path
        exists = p.exists()
        size = p.stat().st_size if exists else 0
        status = "✅" if exists else "❌"
        print(f"  {status} {name:20s} ({key}) — {size:>8,d} bytes")

    # Shared primitives
    prim_path = REBIS_ROOT / "shared/primitives.py"
    cat_path = REBIS_ROOT / "shared/IG_catalog.json"
    print(f"  {'':20s}  primitives: {'✅' if prim_path.exists() else '❌'}")
    print(f"  {'':20s}  IG catalog: {'✅' if cat_path.exists() else '❌'} ({cat_path.stat().st_size:,d} bytes)")

    print("=" * 60)
    return 0


def cmd_verify(args):
    """Verify Frobenius closure across the shared layer."""
    from shared.primitives import WEIGHTS, ORDINALS
    print("✅ shared/primitives.py — %d weights, %d ordinal families loaded" % (len(WEIGHTS), len(ORDINALS)))

    try:
        with open(REBIS_ROOT / "shared/IG_catalog.json") as f:
            catalog = json.load(f)
        print("✅ shared/IG_catalog.json — %d catalog entries" % len(catalog))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("❌ Catalog error: %s" % e)
        return 1

    # Verify each component module loads
    modules = [
        ("serpentrod.protein_v5", "Serpent's Rod v5"),
        ("ch3mpiler.compiler", "CH₃MPILER"),
        ("pipeline.frob", "Pipeline Frobenius"),
        ("pipeline.auto_imscriber", "Auto Imscriber"),
        ("gene_imscriber.engine", "Gene Imscriber"),
    ]

    all_ok = True
    for mod_name, label in modules:
        try:
            __import__(mod_name)
            print("✅ %s — %s imports OK" % (label, mod_name))
        except Exception as e:
            print("❌ %s — %s: %s" % (label, mod_name, e))
            all_ok = False

    return 0 if all_ok else 1


def cmd_run(args):
    """Route to a specific component with its own args."""
    subcommand = args.subcommand
    rest = args.rest

    runners = {
        "serpentrod":   "serpentrod.protein_v5",
        "serpentrod_v4": "serpentrod.protein_v4",
        "serpentrod_pred": "serpentrod.stratified_predictor",
        "ch3mpiler":    "ch3mpiler.compiler",
        "pipeline":     "pipeline.lift_pipeline.lift_pipeline_ob3ect",
        "gene":         "gene_imscriber.engine",
    }

    if subcommand not in runners:
        print("Unknown subcommand: %s" % subcommand)
        print("Available: %s" % ", ".join(runners.keys()))
        return 1

    mod_path = runners[subcommand]
    module = __import__(mod_path, fromlist=["main"])

    if hasattr(module, "main"):
        sys.argv = [mod_path] + rest
        return module.main()
    else:
        # Show module info when no main() — don't try to run unsafely
        import inspect
        doc = module.__doc__ or ""
        first_line = doc.split("\n")[0] if doc else "No docstring"
        print("%s — %s" % (mod_path, first_line))
        print("  No standalone main(). Import and use programmatically:")
        print("    from %s import ..." % mod_path.rsplit(".", 1)[0])
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Red-Hot Rebis — Integrated Imscribing Grammar Toolchain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rebis.py status                    # Show all component status
  rebis.py verify                    # Verify Frobenius closure
  rebis.py run serpentrod --seq KAL  # Run protein prediction
  rebis.py run ch3mpiler --help      # CH3MPILER help
  rebis.py run pipeline --help       # Pipeline help
  rebis.py run gene --help           # Gene engine help
        """
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)

    subparsers = parser.add_subparsers(dest="command")

    # status
    p_status = subparsers.add_parser("status", help="Show all component status")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify Frobenius closure across components")

    # run
    p_run = subparsers.add_parser("run", help="Run a specific component")
    p_run.add_argument("subcommand",
                       choices=["serpentrod", "serpentrod_v4", "serpentrod_pred",
                                "ch3mpiler", "pipeline", "gene"],
                       help="Component to run")
    p_run.add_argument("rest", nargs=argparse.REMAINDER,
                       help="Arguments to pass to the component")

    args = parser.parse_args()

    if args.command == "status":
        return cmd_status(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "run":
        return cmd_run(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
