#!/usr/bin/env python3
"""Runner for the Serpent on the Rod of Asclepius — with import fix."""
import sys
import os
import importlib.util

_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REBIS_ROOT)
import rhr_p4rky.belnap
import rhr_p4rky.genetics_b4
import rhr_p4rky.genetic_code
from rhr_p4rky.serpent_rod import SerpentRod
import json

if __name__ == "__main__":
    # Test sequence
    sr = SerpentRod("AUGGCCGACUGGAACUGCAAGAAGAUCGUGCCCAAGUACUACGGCCGCUG", name="test_protein")
    result = sr.report()
    print(json.dumps(result, indent=2))
    
    # Second test: longer sequence
    print("\n\n=== SECOND TEST: 108 nt ===")
    sr2 = SerpentRod("AUGGCCGACUGGAACUGCAAGAAGAUCGUGCCCAAGUACUACGGCCGCUGGAACUGCAAGAAGAUCGUGCCCAAGUACUACGGC", name="extended")
    result2 = sr2.report()
    print(f"AA: {result2['aa_sequence']} ({result2['aa_length']} AAs)")
    print(f"Winding: {result2['winding_number']}")
    print(f"Contacts: {len(result2['contacts'])}")
    print(f"Frobenius: {'✓' if result2['frobenius_verified'] else '✗'}")
