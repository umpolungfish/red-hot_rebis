#!/usr/bin/env python3
"""
rebis.gene_pipeline_entry — CL entry point for rebis.gene-pipeline
DNA → Folded Protein pipeline
"""
import argparse
import sys
from rebis.file_input import parse_with_file


def main():
    parser = argparse.ArgumentParser(
        prog="rebis.gene-pipeline",
        description="DNA → Folded Protein — 7-stage Frobenius-verified translation")
    parser.add_argument("--test", action="store_true",
                        help="Run demo/self-test")
    parser.add_argument("--dna", type=str,
                        help="DNA sequence")
    parser.add_argument("--seq", type=str,
                        help="RNA sequence (alias for --dna)")
    args = parse_with_file(parser)

    from rebis.cli import cmd_gene_pipeline
    return cmd_gene_pipeline(args)


if __name__ == "__main__":
    sys.exit(main())