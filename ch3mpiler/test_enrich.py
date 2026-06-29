#!/usr/bin/env python3
"""Test the enriched precursor lattice."""
import sys
sys.path.insert(0, '/home/mrnob0dy666/imsgct/red-hot_rebis')
sys.path.insert(0, '.')
import compiler
from compiler import Ch3mpiler, FG
from shared.rich_output import *


info_line("=== FG EXTENSIONS ===")
for fg in ['nitro', 'cyclic', 'diazonium']:
    info_line(f'  {fg}: {fg in FG}')

print()
info_line("=== BENZENE -> PARACETAMOL ===")
ch = Ch3mpiler()
result = ch.path_to_target('benzene', 'paracetamol', depth=4)
print(f'Path found: {result.get("found")}')
print(f'Match type: {result.get("match_type")}')
if result.get('found'):
    for step in result.get('path', []):
        info_line(f'  Step {step["step"]}: {step["fg1"]} + {step["fg2"]} -> {step["product"]}')
        info_line(f'    Bond: {step["bond"]}  ({step["reaction"]})')
    print(f'Path length: {result.get("path_length")}')
else:
    info_line("No path found via lattice")
