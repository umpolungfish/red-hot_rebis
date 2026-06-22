#!/usr/bin/env python3
"""Runner for the Serpent on the Rod of Asclepius."""
import sys, os, json

_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REBIS_ROOT)

import rhr_p4rky.belnap
import rhr_p4rky.genetics_b4
import rhr_p4rky.genetic_code
from rhr_p4rky.serpent_rod import SerpentRod

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SerpentRod — Direct RNA to Folded Protein")
    parser.add_argument("--seq", "-s", type=str, default="AUGGCCGACUGGAACUGCAAGAAGAUCGUGCCCAAGUACUACGGCCGCUG",
                        help="RNA sequence (default: test sequence)")
    parser.add_argument("--name", "-n", type=str, default="protein",
                        help="Protein name")
    args = parser.parse_args()
    
    sr = SerpentRod(args.seq, name=args.name)
    result = sr.report()
    print(json.dumps(result, indent=2))
