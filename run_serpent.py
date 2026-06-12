#!/usr/bin/env python3
"""Runner for the Serpent on the Rod of Asclepius — with import fix."""
import sys
import os
import importlib.util

# Add the package directory to path
pkg_dir = os.path.join(os.path.dirname(__file__), "p4ramill_py")
sys.path.insert(0, pkg_dir)

# Monkey-patch the module to fix relative imports
import p4ramill_py.belnap
import p4ramill_py.genetics_b4
import p4ramill_py.genetic_code

# Now import using absolute import syntax
spec = importlib.util.spec_from_file_location(
    "serpent_rod_module",
    os.path.join(pkg_dir, "serpent_rod.py")
)

# Patch sys.modules so relative imports resolve
import types
class SerpentRodModule(types.ModuleType):
    pass

# Load the module with __package__ set
import importlib.machinery
loader = importlib.machinery.SourceFileLoader("p4ramill_py.serpent_rod", os.path.join(pkg_dir, "serpent_rod.py"))
spec = importlib.util.spec_from_loader("p4ramill_py.serpent_rod", loader, origin=os.path.join(pkg_dir, "serpent_rod.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["p4ramill_py.serpent_rod"] = mod
mod.__package__ = "p4ramill_py"
loader.exec_module(mod)

SerpentRod = mod.SerpentRod
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
