#!/usr/bin/env python3
"""
rebis.chain_entry — CL entry point for rebis.chain
Unified pipeline: DNA→Protein→Catalyst→Synthesis
"""
import argparse
import sys
from rebis.file_input import parse_with_file


def main():
    parser = argparse.ArgumentParser(
        prog="rebis.chain",
        description="UNIFIED PIPELINE: DNA→Protein→CatalyticSite→RetrosyntheticPlan")
    parser.add_argument("--dna", type=str, help="DNA/RNA sequence")
    parser.add_argument("--seq", type=str, help="RNA sequence (alias for --dna)")
    parser.add_argument("--target", type=str, default="CC(=O)O",
                        help="Target SMILES (default: acetic acid)")
    parser.add_argument("--depth", type=int, default=2,
                        help="Retrosynthesis depth (default: 2)")
    parser.add_argument("--pdb", type=str,
                        help="Output PDB structure file for folded protein")
    args = parse_with_file(parser)

    from rebis.cli import cmd_chain
    return cmd_chain(args)


if __name__ == "__main__":
    sys.exit(main())