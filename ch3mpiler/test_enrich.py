#!/usr/bin/env python3
"""Test the enriched precursor lattice."""
import sys
sys.path.insert(0, '/home/mrnob0dy666/imsgct/red-hot_rebis')
sys.path.insert(0, '.')
import compiler
from compiler import Ch3mpiler, FG

print('=== FG EXTENSIONS ===')
for fg in ['nitro', 'cyclic', 'diazonium']:
    print(f'  {fg}: {fg in FG}')

print()
print('=== BENZENE -> PARACETAMOL ===')
ch = Ch3mpiler()
result = ch.path_to_target('benzene', 'paracetamol', depth=4)
print(f'Path found: {result.get("found")}')
print(f'Match type: {result.get("match_type")}')
if result.get('found'):
    for step in result.get('path', []):
        print(f'  Step {step["step"]}: {step["fg1"]} + {step["fg2"]} -> {step["product"]}')
        print(f'    Bond: {step["bond"]}  ({step["reaction"]})')
    print(f'Path length: {result.get("path_length")}')
else:
    print('No path found via lattice')
