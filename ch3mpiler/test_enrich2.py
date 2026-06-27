#!/usr/bin/env python3
"""Test the enriched precursor lattice — comprehensive."""
import sys
sys.path.insert(0, '/home/mrnob0dy666/imsgct/red-hot_rebis')
sys.path.insert(0, '.')
import compiler
from compiler import Ch3mpiler, FG

# Check FG extensions more carefully
print('=== FG TABLE CHECK ===')
for fg_name in sorted(FG.keys()):
    if fg_name in ['nitro', 'cyclic', 'diazonium', 'phosphate', 'sulfonate']:
        print(f'  {fg_name}: {FG[fg_name]}')

# Also check MOLECULE_FG_DB
print()
print('=== MOLECULE DB EXTENSIONS ===')
from compiler import MOLECULE_FG_DB
for name in ['4_aminophenol', '4_nitrophenol', 'acetic_anhydride', 'isobutylbenzene']:
    if name in MOLECULE_FG_DB:
        print(f'  {name}: {MOLECULE_FG_DB[name]}')

print()
print('=== PATHFINDING TESTS ===')
ch = Ch3mpiler()

tests = [
    ('benzene', 'paracetamol', 'Benzene -> Paracetamol'),
    ('benzene', 'aspirin', 'Benzene -> Aspirin'),
    ('toluene', 'benzaldehyde', 'Toluene -> Benzaldehyde'),
    ('benzene', 'ibuprofen', 'Benzene -> Ibuprofen'),
    ('benzene', 'aniline', 'Benzene -> Aniline'),
    ('nitrobenzene', 'paracetamol', 'Nitrobenzene -> Paracetamol'),
]

for start, target, label in tests:
    print(f'\n--- {label} ---')
    r = ch.path_to_target(start, target, depth=5)
    if r.get('found'):
        print(f'  ✓ FOUND ({r["path_length"]} steps)')
        for step in r['path']:
            print(f'    {step["step"]}. {step["fg1"]} + {step["fg2"]} → {step["product"]}')
            print(f'       [{step["bond"]}] {step["reaction"]}')
    else:
        print(f'  ✗ NOT FOUND (source: {r.get("source", "?")})')
        print(f'  Direct distance: {r.get("direct_structural_distance", "?")}')
