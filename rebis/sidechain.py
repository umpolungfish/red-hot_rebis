"""
rebis.sidechain — Sidechain × Environment Compositional Algebra
═══════════════════════════════════════════════════════════════

Formalizes the Imscribing Grammar's algebraic operations (tensor ⊗,
meet ∧, join ∨) for all 20 amino acid sidechains in 4 structured
protein environments — 80 compositional pairs with bottleneck,
frustration, domination asymmetry, and tier analysis.

Callable from anywhere:
  rebis.sidechain <sidechain> <environment>
  rebis.sidechain --batch
  rebis.sidechain --list
  rebis.sidechain --pdb <PDB_ID>
  rebis.sidechain --pdb <PDB_ID> --json
  rebis.sidechain --pdb <PDB_ID> --verbose
  rebis.sidechain --info

Examples:
  rebis.sidechain arginine charged_interface
  rebis.sidechain alanine polar_surface
  rebis.sidechain --batch
"""

import sys as _sys
from rebis.file_input import parse_with_file
import io as _io
import argparse
import json
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path as _Path

_REBIS_ROOT = _Path(__file__).parent.parent.absolute()
_sys.path.insert(0, str(_REBIS_ROOT))
_sys.path.insert(0, str(_REBIS_ROOT / "rhr_p4rky"))

# ── Suppress stdout during import ──
_quiet = _io.StringIO()
with redirect_stdout(_quiet), redirect_stderr(_quiet):
    from rhr_p4rky.sidechain_algebra import (
        SIDECHAINS, ENVIRONMENTS,
        analyze_composition, batch_analyze,
        print_analysis, print_frustration_matrix,
        print_dominance_matrix, print_tier_matrix,
        tuple_str,
    )

__all__ = sorted([k for k in dir() if not k.startswith('_')
                   and k not in ('_sys', '_io', '_Path', '_REBIS_ROOT', '_quiet',
                                 'redirect_stdout', 'redirect_stderr')])

from rhr_p4rky.pdb_integration import analyze_pdb_structure, print_pdb_analysis

SC_NAMES = sorted(SIDECHAINS.keys())
ENV_NAMES = sorted(ENVIRONMENTS.keys())


def main():
    parser = argparse.ArgumentParser(
        description="Sidechain × Environment Compositional Algebra",
        prog="rebis.sidechain")
    parser.add_argument("sidechain", nargs="?", help="Sidechain name")
    parser.add_argument("environment", nargs="?", help="Environment name")
    parser.add_argument("--batch", action="store_true",
                        help="Analyze all 80 pairs")
    parser.add_argument("--list", action="store_true",
                        help="List all sidechains and environments")
    parser.add_argument("--info", action="store_true",
                        help="Show module info")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON (for --batch)")
    parser.add_argument("--pdb", type=str, default=None,
                        help="Analyze a real PDB structure (ID or file path)")
    parser.add_argument("--cutoff", type=float, default=8.0,
                        help="Neighbor cutoff in Å for environment classification (default: 8.0)")
    parser.add_argument("--verbose", action="store_true",
                        help="Per-residue output for PDB analysis")

    args = parse_with_file(parser)


    if args.pdb:
        result = analyze_pdb_structure(args.pdb, cutoff=args.cutoff, verbose=not args.json)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print_pdb_analysis(result, verbose=args.verbose)
        return 0

    if args.info or (not args.sidechain and not args.batch and not args.list and not args.pdb):
        print("SIDECHAIN × ENVIRONMENT COMPOSITIONAL ALGEBRA")
        print("=" * 60)
        print(f"  {len(SC_NAMES)} sidechains × {len(ENV_NAMES)} environments = "
              f"{len(SC_NAMES)*len(ENV_NAMES)} pairs")
        print()
        print("Sidechains:", ", ".join(SC_NAMES))
        print("Environments:", ", ".join(ENV_NAMES))
        print()
        print("Usage:")
        print("  rebis.sidechain <sidechain> <environment>  — single analysis")
        print("  rebis.sidechain --batch                     — all 80 pairs")
        print("  rebis.sidechain --list                      — all tuples")
        print("  rebis.sidechain --pdb <PDB_ID>              — real structure analysis")
        print("  rebis.sidechain --pdb <PDB_ID> --verbose    — per-residue detail")
        print("  rebis.sidechain --json --batch             — JSON output")
        print()
        print("Key findings:")
        print("  arginine⊗charged_interface  →  O_∞  (only pair at self-referential tier)")
        print("  histidine dominates ALL four environments")
        print("  alanine⊗polar_surface: 3 bottlenecks, solvent dominates")
        return 0

    if args.list:
        print("SIDECHAINS:")
        for sc in SC_NAMES:
            print(f"  {sc:22s}  {tuple_str(SIDECHAINS[sc])}")
        print("\nENVIRONMENTS:")
        for env in ENV_NAMES:
            print(f"  {env:22s}  {tuple_str(ENVIRONMENTS[env])}")
        return 0

    if args.batch:
        data = batch_analyze(verbose=not args.json)
        if args.json:
            # Re-run quietly for JSON
            data = batch_analyze(verbose=False)
            out = {
                "summary": {
                    "frustration": {
                        sc: {env: data["summary"]["frustration"].get(sc, {}).get(env, None)
                             for env in ENV_NAMES}
                        for sc in SC_NAMES
                    },
                    "dominance": {
                        sc: {env: data["summary"]["dominance"].get(sc, {}).get(env, None)
                             for env in ENV_NAMES}
                        for sc in SC_NAMES
                    },
                    "tiers": {
                        sc: {env: data["summary"]["tier_matrix"].get(sc, {}).get(env, None)
                             for env in ENV_NAMES}
                        for sc in SC_NAMES
                    },
                }
            }
            print(json.dumps(out, indent=2))
        else:
            print_frustration_matrix(data["summary"])
            print_dominance_matrix(data["summary"])
            print_tier_matrix(data["summary"])
        return 0

    if args.sidechain and args.environment:
        sc = args.sidechain.lower().replace(" ", "_")
        env = args.environment.lower().replace(" ", "_")

        if sc not in SIDECHAINS:
            print(f"Unknown sidechain: '{sc}'. Choices: {', '.join(SC_NAMES)}")
            return 1
        if env not in ENVIRONMENTS:
            print(f"Unknown environment: '{env}'. Choices: {', '.join(ENV_NAMES)}")
            return 1

        analysis = analyze_composition(sc, env)
        print_analysis(analysis)
        return 0

    return 0


if __name__ == "__main__":
    _sys.exit(main())
