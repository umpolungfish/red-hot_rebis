#!/usr/bin/env python3
"""Test the enriched precursor lattice — comprehensive."""
import sys
sys.path.insert(0, '/home/mrnob0dy666/imsgct/red-hot_rebis')
sys.path.insert(0, '.')
import compiler
from compiler import Ch3mpiler, FG

# Check FG extensions more carefully
info_line("=== FG TABLE CHECK ===")
for fg_name in sorted(FG.keys()):
    if fg_name in ['nitro', 'cyclic', 'diazonium', 'phosphate', 'sulfonate']:
        info_line(f'  {fg_name}: {FG[fg_name]}')

# Also check MOLECULE_FG_DB
print()
info_line("=== MOLECULE DB EXTENSIONS ===")
from compiler import MOLECULE_FG_DB
from shared.rich_output import *

for name in ['4_aminophenol', '4_nitrophenol', 'acetic_anhydride', 'isobutylbenzene']:
    if name in MOLECULE_FG_DB:
        info_line(f'  {name}: {MOLECULE_FG_DB[name]}')

print()
info_line("=== PATHFINDING TESTS ===")
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
    info_line(f'\n--- {label} ---')
    r = ch.path_to_target(start, target, depth=5)
    if r.get('found'):
        info_line(f'  ✓ FOUND ({r["path_length"]} steps)')
        for step in r['path']:
            info_line(f'    {step["step"]}. {step["fg1"]} + {step["fg2"]} → {step["product"]}')
            info_line(f'       [{step["bond"]}] {step["reaction"]}')
    else:
        info_line(f'  ✗ NOT FOUND (source: {r.get("source", "?")})')
        info_line(f'  Direct distance: {r.get("direct_structural_distance", "?")}')
