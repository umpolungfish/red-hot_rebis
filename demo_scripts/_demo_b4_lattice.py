#!/usr/bin/env python3
"""B4 Nucleotide Lattice display — used by ghost_typer.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rhr_p4rky.genetics_b4 import B4Lattice, CODON_B4_MAP
from shared.rich_output import *

b4 = B4Lattice()
info_line("=" * 65)
info_line("B4 NUCLEOTIDE LATTICE — 64 Codons on a Frobenius Algebra")
info_line("=" * 65)
info_line(f"Lattice shape: {b4.lattice.shape}")
info_line(f"Entries with confirmed B4 assignments: {len(CODON_B4_MAP)}/64")
print()
info_line("First 16 codons and their B4 B-vectors:")
for i, (codon, b4_vec) in enumerate(sorted(CODON_B4_MAP.items())[:16]):
    info_line(f"  {codon:12s} → B4({b4_vec})")
info_line("...")
print()
info_line("Key theorem: 17,280,000 / 64 = 270,000")
info_line("The genetic code partitions the Crystal of Types exactly.")
