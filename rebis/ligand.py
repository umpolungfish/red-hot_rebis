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
  rebis.ligand --file design.json                    # filepath entry
  rebis.ligand design.json                           # positional entry
  rebis.ligand --stdin < design.json                 # stdin entry
"""

import sys
import importlib as _importlib
from rebis.file_input import parse_with_file

_EXPORTS = {'design_ligand_from_pdb': 'rhr_p4rky.ligand_from_site_pdb', 'design_ligand_from_pdb_improved': 'rhr_p4rky.ligand_from_site_pdb', 'encode_site_from_pdb': 'rhr_p4rky.ligand_from_site_pdb', 'auto_detect_active_site': 'rhr_p4rky.ligand_from_site_pdb', 'complement_with_bottleneck_bias': 'rhr_p4rky.ligand_from_site_pdb', 'print_ligand_result': 'rhr_p4rky.ligand_from_site_pdb', 'result_to_json': 'rhr_p4rky.ligand_from_site_pdb', 'CatalyticResidueAnalysis': 'rhr_p4rky.ligand_from_site_pdb', 'LigandDesignResult': 'rhr_p4rky.ligand_from_site_pdb', 'fingerprint_to_ig_biochemical': 'rhr_p4rky.ligand_imasm_v2'}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(_importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value

import os
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(_REBIS_ROOT))
sys.path.insert(0, str(_REBIS_ROOT / "rhr_p4rky"))


def main():
    """Entry point — delegates to ligand_from_site_pdb.main() with file support."""
    import argparse
    from rhr_p4rky.ligand_from_site_pdb import main as _main

    # Use the module's own parser building + our file support
    # Build a wrapper that captures the underlying parser
    parser = argparse.ArgumentParser(
        prog="rebis.ligand",
        description="PDB-aware ligand design from catalytic sites",
        add_help=False)
    # Mirror ligand_from_site_pdb's args
    parser.add_argument("--pdb", type=str, default=None,
                        help="PDB ID to fetch and analyze")
    parser.add_argument("--pdb-file", type=str, default=None,
                        help="Local PDB file path")
    parser.add_argument("--active", type=str, default=None,
                        help="Comma-separated active site residues (e.g. Glu35,Asp52)")
    parser.add_argument("--auto-active", action="store_true", default=False,
                        help="Auto-detect active site residues by proximity")
    parser.add_argument("--top-n", type=int, default=10,
                        help="Number of top residues for auto-detection")
    parser.add_argument("--cutoff", type=float, default=8.0,
                        help="Distance cutoff for auto-active detection (Å)")
    parser.add_argument("--proximity", type=float, default=12.0)
    parser.add_argument("--bottleneck-bias", type=float, default=0.5)
    parser.add_argument("--improved", action="store_true", default=False,
                        help="Use improved PDB parsing method")
    parser.add_argument("--json", action="store_true", default=False,
                        help="Output as JSON")
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Verbose output")
    parser.add_argument("--help", "-h", action="store_true",
                        help="Show help")

    args = parse_with_file(parser)

    if args.help:
        parser.print_help()
        return 0

    # Build sys.argv to pass through to the real handler
    # This is ugly but the delegate expects argparse.parse_args()
    saved_argv = sys.argv
    new_argv = [sys.argv[0]]
    if args.pdb:
        new_argv.extend(['--pdb', args.pdb])
    if args.pdb_file:
        new_argv.extend(['--pdb-file', args.pdb_file])
    if args.active:
        new_argv.extend(['--active', args.active])
    if args.auto_active:
        new_argv.append('--auto-active')
    if args.top_n != 10:
        new_argv.extend(['--top-n', str(args.top_n)])
    new_argv.extend(['--cutoff', str(args.cutoff)])
    new_argv.extend(['--proximity', str(args.proximity)])
    new_argv.extend(['--bottleneck-bias', str(args.bottleneck_bias)])
    if args.improved:
        new_argv.append('--improved')
    if args.json:
        new_argv.append('--json')
    if args.verbose:
        new_argv.append('--verbose')
    sys.argv = new_argv
    try:
        return _main()
    finally:
        sys.argv = saved_argv


if __name__ == "__main__":
    sys.exit(main())