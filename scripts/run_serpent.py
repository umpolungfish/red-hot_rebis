#!/usr/bin/env python3
"""Runner for the Serpent on the Rod of Asclepius — with import fix."""
_HELP_EXAMPLES = """  rebis.py run run_serpent"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "scripts/run_serpent.py"
    print(_doc)
    print()
    print("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

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
