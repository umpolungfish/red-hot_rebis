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
from rebis.file_input import parse_with_file
import os
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(_REBIS_ROOT))
sys.path.insert(0, str(_REBIS_ROOT / "rhr_p4rky"))


def main():
    """Entry point — delegates to ligand_from_site_pdb.main() with file support."""
    import argparse
    from rhr_p4rky.ligand_from_site_pdb import main as _main
    import rhr_p4rky.ligand_from_site_pdb as _mod

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
    parser.add_argument("--cutoff", type=float, default=6.0,
                        help="Distance cutoff for auto-active detection (Å)")
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
    if args.cutoff != 6.0:
        new_argv.extend(['--cutoff', str(args.cutoff)])
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
    main()