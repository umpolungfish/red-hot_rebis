#!/usr/bin/env python3
"""Exercise the enriched precursor lattice and return failed search status."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.rich_output import *


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--depth', type=int, default=5, help='Maximum path search depth')
    args = parser.parse_args(argv)
    if args.depth < 0:
        parser.error('Depth must be nonnegative')
    from ch3mpiler.compiler import Ch3mpiler, FG, MOLECULE_FG_DB
    info_line("=== FG TABLE CHECK ===")
    for fg_name in sorted(FG.keys()):
        if fg_name in ['nitro', 'cyclic', 'diazonium', 'phosphate', 'sulfonate']:
            info_line(f'  {fg_name}: {FG[fg_name]}')

    # Also check MOLECULE_FG_DB
    print()
    info_line("=== MOLECULE DB EXTENSIONS ===")

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

    failed = False
    for start, target, label in tests:
        info_line(f'\n--- {label} ---')
        r = ch.path_to_target(start, target, depth=args.depth)
        if r.get('found'):
            info_line(f'  ✓ FOUND ({r["path_length"]} steps)')
            for step in r['path']:
                info_line(f'    {step["step"]}. {step["fg1"]} + {step["fg2"]} → {step["product"]}')
                info_line(f'       [{step["bond"]}] {step["reaction"]}')
        else:
            failed = True
            info_line(f'  ✗ NOT FOUND (source: {r.get("source", "?")})')
            info_line(f'  Direct distance: {r.get("direct_structural_distance", "?")}')

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
