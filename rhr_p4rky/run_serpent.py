#!/usr/bin/env python3
"""Runner for the Serpent on the Rod of Asclepius."""
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
