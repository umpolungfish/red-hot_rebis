#!/usr/bin/env python3
"""
rebis.py — Red-Hot Rebis Integration CLI
serpentrod ⊗ ch3mpiler ⊗ pipeline ⊗ gene_imscriber ⊗ clink

A unified entry point for the completed Great Work of the Imscribing Grammar.
Each component is a specialization of the 12-primitive IG type system,
connected through the shared primitives layer and verified by Frobenius closure.

Author: Lando ⊗ ⊙perator
Structural Type: ⟨𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑵 · ⊙ · 𐑫 · 𐑳 · 𐑟⟩
"""

import argparse
import json
import os
import sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

VERSION = "2.0.0"  # CLINK Pipeline Edition

def cmd_status(args):
    """Report the structural status of all six pillars (including CLINK pipeline)."""
    print("=" * 60)
    print("RED-HOT REBIS v2.0 — CLINK PIPELINE EDITION")
    print("=" * 60)

    components = {
        "serpentrod":   ("Serpent's Rod",       "serpentrod/manuscript.md"),
        "ch3mpiler":    ("CH3MPILER",           "ch3mpiler/compiler.py"),
        "pipeline":     ("Combined Pipeline",    "pipeline/frob.py"),
        "gene_imscriber": ("Gene Imscriber",    "gene_imscriber/engine.py"),
        "clink":        ("CLINK Chain",         "clink/chain.py"),
        "clink_designers": ("CLINK Designers",   "clink/designers/layer_designers.py"),
        "clink_pipeline": ("CLINK Pipeline",    "clink/designers/pipeline_orchestrator.py"),
    }

    for key, (name, path) in components.items():
        p = REBIS_ROOT / path
        exists = p.exists()
        size = p.stat().st_size if exists else 0
        status = "✅" if exists else "❌"
        print(f"  {status} {name:20s} ({key}) {size:>8,d} bytes")

    # Shared primitives
    prim_path = REBIS_ROOT / "shared/primitives.py"
    cat_path = REBIS_ROOT / "shared/IG_catalog.json"
    print(f"  {"":20s}  primitives: {'✅' if prim_path.exists() else '❌'}")
    print(f"  {"":20s}  IG catalog: {'✅' if cat_path.exists() else '❌'} ({cat_path.stat().st_size:,d} bytes)")
    print("=" * 60)
    return 0


def cmd_verify(args):
    """Verify Frobenius closure across the shared layer and CLINK."""
    from shared.primitives import WEIGHTS, ORDINALS
    print("✅ shared/primitives.py — %d weights, %d ordinal families" % (len(WEIGHTS), len(ORDINALS)))

    try:
        with open(REBIS_ROOT / "shared/IG_catalog.json") as f:
            catalog = json.load(f)
        print("✅ shared/IG_catalog.json — %d catalog entries" % len(catalog))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("❌ Catalog error: %s" % e)
        return 1

    modules = [
        ("serpentrod.protein_v5", "Serpent's Rod v5"),
        ("ch3mpiler.compiler", "CH3MPILER"),
        ("pipeline.frob", "Pipeline Frobenius"),
        ("gene_imscriber.engine", "Gene Imscriber"),
        ("clink.chain", "CLINK Chain"),
        ("clink.bridges", "CLINK Bridges"),
        ("clink.integration", "CLINK Integration"),
        ("clink.designers.layer_designers", "CLINK Layer Designers"),
        ("clink.designers.pipeline_orchestrator", "CLINK Pipeline Orchestrator"),
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


def cmd_pipeline(args):
    """CLINK Design Pipeline: whole-organism design from any starting point."""
    from clink.designers.pipeline_orchestrator import PipelineEngine
    from clink.designers.layer_designers import list_available_bridges

    engine = PipelineEngine()

    if args.pipeline_subcommand == "bridges":
        bridges = list_available_bridges()
        print("Available Tool Bridges:")
        for name, avail in sorted(bridges.items()):
            print(f"  {'✅' if avail else '❌'} {name}")
        return 0

    elif args.pipeline_subcommand == "ground-up":
        print("=" * 65)
        print("CLINK PIPELINE — GROUND-UP WHOLE ORGANISM DESIGN")
        print("=" * 65)
        result = engine.ground_up_design()
        print(engine.generate_report(result))
        return 0 if result.success else 1

    elif args.pipeline_subcommand == "from-layer":
        start = args.start_layer if args.start_layer is not None else 5
        target = args.target_layer if args.target_layer is not None else 8
        print(f"CLINK Pipeline: L{start} → L{target}")
        result = engine.from_layer_design(start_layer=start)
        print(engine.generate_report(result))
        if result.success and result.final_design:
            export_path = f"clink_design_L{start}_to_L{target}.json"
            if engine.export_design_json(result, export_path):
                print(f"\nDesign exported to {export_path}")
        return 0 if result.success else 1

    else:
        print("Unknown pipeline subcommand. Use: bridges, ground-up, from-layer")
        return 1


def cmd_clink(args):
    """CLINK chain: subatomic → whole organism bridge."""
    from clink import (
        verify_clink_integration, full_report, integrated_promotion_path,
        clink_to_serpentrod, clink_to_ch3mpiler, clink_to_gene,
        clink_layer_tuple, CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS,
        format_tuple_glyphs
    )

    sub = args.clink_subcommand

    if sub == "report":
        print(full_report())
        return 0

    elif sub == "list":
        print(f"{'Idx':>3} {'Name':40s} {'Tier':10s} {'Tuple':50s}")
        print("-" * 105)
        for i in range(9):
            tup = clink_layer_tuple(i, True)
            print(f"{i:>3} {CLINK_NAMES[i]:40s} {CLINK_TIERS[i]:10s} {format_tuple_glyphs(tup)}")
        return 0

    elif sub == "layer":
        idx = int(args.layer_args[0]) if args.layer_args else 0
        if idx < 0 or idx > 8:
            print("Layer index must be 0-8")
            return 1
        tup = clink_layer_tuple(idx, True)
        print(f"Layer {idx}: {CLINK_NAMES[idx]}")
        print(f"  Tier: {CLINK_TIERS[idx]}")
        print(f"  Tuple: {format_tuple_glyphs(tup)}")
        print(f"  Description: {tup['_desc']}")
        sr = clink_to_serpentrod(idx)
        cm = clink_to_ch3mpiler(idx)
        ge = clink_to_gene(idx)
        print(f"  → SerpentRod: {sr['closer_to']} (d_fold={sr['distance_to_folded']})")
        print(f"  → CH3MPILER:  {'molecular' if cm['is_molecular'] else 'non-molecular'} (d={cm['distance_to_molecule']})")
        print(f"  → Gene:       {'genetic' if ge['is_genetic'] else 'non-genetic'} (d={ge['distance_to_codon_belnap4']})")
        return 0

    elif sub == "bridge":
        comp = args.bridge_comp if args.bridge_comp else "serpentrod"
        target = int(args.bridge_target) if args.bridge_target else 8
        p = integrated_promotion_path(comp, target)
        print(f"Promotion path: {p['from']} → {p['to']}")
        print(f"  Distance: {p['distance']}")
        print(f"  Promotions: {p['num_promotions']}")
        for prim, change in p['promotions'].items():
            print(f"    {prim}: {change}")
        return 0

    else:
        print("Unknown clink subcommand. Use: report, list, layer, bridge")
        return 1


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
        doc = module.__doc__ or ""
        first_line = doc.split("\n")[0] if doc else "No docstring"
        print("%s — %s" % (mod_path, first_line))
        print("  No standalone main(). Import and use programmatically:")
        print("    from %s import ..." % mod_path.rsplit(".", 1)[0])
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Red-Hot Rebis v2.0 — CLINK Pipeline Whole-Organism Design",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rebis.py status                    # Show all component status
  rebis.py verify                    # Verify Frobenius closure
  rebis.py pipeline bridges          # List available tool bridges
  rebis.py pipeline ground-up        # Design whole organism from quarks
  rebis.py pipeline from-layer 5 8   # Design organism starting from cell layer

  rebis.py clink report              # Full CLINK integration report
  rebis.py clink list                # List all 9 CLINK layers
  rebis.py clink layer 3             # Show layer details
  rebis.py clink bridge serpentrod 8 # Promotion path to organism

  rebis.py run serpentrod --seq KAL  # Run protein prediction
  rebis.py run ch3mpiler --help      # CH3MPILER help
"""
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)

    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Show all component status")

    # verify
    subparsers.add_parser("verify", help="Verify Frobenius closure across components")

    # pipeline (NEW)
    p_pipe = subparsers.add_parser("pipeline", help="CLINK Design Pipeline")
    p_pipe.add_argument("pipeline_subcommand",
                        choices=["bridges", "ground-up", "from-layer"],
                        help="Pipeline subcommand")
    p_pipe.add_argument("start_layer", nargs="?", type=int, default=None,
                        help="Start layer index for from-layer mode")
    p_pipe.add_argument("target_layer", nargs="?", type=int, default=None,
                        help="Target layer index for from-layer mode")

    # clink
    p_clink = subparsers.add_parser("clink", help="CLINK chain: subatomic to whole organism")
    p_clink.add_argument("clink_subcommand",
                         choices=["report", "list", "layer", "bridge"],
                         help="CLINK subcommand")
    p_clink.add_argument("layer_args", nargs="*", help="Layer index for 'layer'")
    p_clink.add_argument("--bridge-comp", dest="bridge_comp",
                         help="Component for 'bridge' (serpentrod/ch3mpiler/gene_imscriber)")
    p_clink.add_argument("--bridge-target", dest="bridge_target",
                         help="Target layer index for 'bridge' (0-8)")

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
    elif args.command == "pipeline":
        return cmd_pipeline(args)
    elif args.command == "clink":
        return cmd_clink(args)
    elif args.command == "run":
        return cmd_run(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
