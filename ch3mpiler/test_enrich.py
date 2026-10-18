#!/usr/bin/env python3
"""Exercise the enriched precursor lattice and return failed search status."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.rich_output import *


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--depth', type=int, default=4, help='Maximum path search depth')
    args = parser.parse_args(argv)
    if args.depth < 0:
        parser.error('Depth must be nonnegative')
    from ch3mpiler.compiler import Ch3mpiler, FG, MOLECULE_FG_DB
    info_line("=== FG EXTENSIONS ===")
    for fg in ['nitro', 'cyclic', 'diazonium']:
        info_line(f'  {fg}: {fg in FG}')

    print()
    info_line("=== BENZENE -> PARACETAMOL ===")
    ch = Ch3mpiler()
    result = ch.path_to_target('benzene', 'paracetamol', depth=args.depth)
    info_line(f'Path found: {result.get("found")}')
    info_line(f'Match type: {result.get("match_type")}')
    if result.get('found'):
        for step in result.get('path', []):
            info_line(f'  Step {step["step"]}: {step["fg1"]} + {step["fg2"]} -> {step["product"]}')
            info_line(f'    Bond: {step["bond"]}  ({step["reaction"]})')
        info_line(f'Path length: {result.get("path_length")}')
    else:
        info_line("No path found via lattice")

    return int(not result.get("found"))


if __name__ == "__main__":
    raise SystemExit(main())
