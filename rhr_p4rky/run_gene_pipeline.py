#!/usr/bin/env python3
"""
run_gene_pipeline.py — Standalone runner for the Gene → Protein Pipeline.

Fixed: --test no longer hard-overrides user-supplied sequences.
When --test AND a sequence are given, the user's sequence is used.
When --test is given alone, the standard test sequence is used.
"""

import sys
import os
import json

# Fix imports for standalone use
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rhr_p4rky.gene_to_protein_pipeline as gpp
from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
from rhr_p4rky.gene_to_protein_pipeline import STAGE_TUPLES, ONE_LETTER

TEST_SEQUENCE = "ATGGCCGACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gene to Protein Pipeline")
    parser.add_argument("sequence", nargs="?", help="DNA sequence")
    parser.add_argument("--file", "-f", help="FASTA file")
    parser.add_argument("--name", "-n", default="gene")
    parser.add_argument("--subunits", "-s", type=int, default=0)
    parser.add_argument("--output", "-o", help="Output JSON")
    parser.add_argument("--test", "-t", action="store_true",
                        help="Use test sequence as DEFAULT (user-supplied sequence takes priority)")
    args = parser.parse_args()

    sequence = None
    
    # Priority: explicit sequence > file > --test default
    if args.sequence:
        sequence = args.sequence
        if args.test and args.name == "gene":
            args.name = "user_sequence"
    elif args.file:
        with open(args.file) as f:
            lines = [l.strip() for l in f if not l.startswith(">")]
            sequence = "".join(lines)
    elif args.test:
        sequence = TEST_SEQUENCE
        args.name = "test_protein"
    else:
        parser.print_help()
        sys.exit(1)

    valid = set("ATCGUatcgu")
    for sym in sequence:
        if sym not in valid:
            print(f"ERROR: Invalid nucleotide '{sym}'")
            sys.exit(1)

    pipeline = GeneToProteinPipeline(sequence, name=args.name)
    report = pipeline.run(num_subunits=args.subunits)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {args.output}")
    else:
        dna_display = report['dna_sequence'][:60]
        print(f"\n{'='*60}")
        print(f"GENE -> PROTEIN: {report['pipeline']}")
        print(f"{'='*60}")
        print(f"DNA: {dna_display}{'...' if len(report['dna_sequence']) > 60 else ''} ({report['dna_length']} bp)")
        print(f"AA:  {report['aa_sequence']}")
        print(f"Length: {report['aa_length']} AAs, Subunits: {report['subunits']}")
        print()
        print(f"{'Stage':<25} {'B4':<6} {'Frob':<6} Description")
        print("-"*60)
        for s in report["stages"]:
            tick = chr(10003) if s["frob"] else chr(10007)
            print(f"{s['name']:<25} {s['b4']:<6} {tick:<6} {s['desc']}")
        print()
        print("Pathway Distances:")
        for d in report["pathway"]:
            print(f"  {d['from']} -> {d['to']}: delta={d['delta']}")
        print(f"  TOTAL: delta={report['total_delta']}")
        print()
        print("Primitive Activations:")
        for prim, data in sorted(report["primitive_activations"].items()):
            print(f"  {prim}: {data['count']}x")
        print()
        print(f"Closure: DNA<->Quaternary distance={report['closure']['dna_to_quaternary_distance']}")
        print(f"Frobenius across all stages: {'OK' if report['closure']['frobenius_across_pathway'] else 'FAIL'}")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
