#!/usr/bin/env python3
"""Runner for the Serpent on the Rod of Asclepius."""
_HELP_EXAMPLES = """  rebis.py run run_serpent"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "rhr_p4rky/run_serpent.py"
    print(_doc)
    print()
    print("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from serpent_rod import SerpentRod
import json
if __name__ == "__main__":
    # Test with the default sequence
    sr = SerpentRod("AUGGCCGACUGGAACUGCAAGAAGAUCGUGCCCAAGUACUACGGCCGCUG", name="test_protein")
    result = sr.report()
    print(json.dumps(result, indent=2))
