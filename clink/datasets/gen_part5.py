#!/usr/bin/env python3
"""Repair historical dataset directory creation without rewriting unchanged files."""
import argparse
import ast
from pathlib import Path

OLD = '            layer_dir.mkdir(exist_ok=True)'
NEW = '            layer_dir.mkdir(parents=True, exist_ok=True)'


def repair_source(content):
    """Return a validated repair, accepting the already-repaired form."""
    if OLD not in content and NEW not in content:
        raise ValueError('Dataset source has no recognized layer directory creation')
    revised = content.replace(OLD, NEW)
    ast.parse(revised)
    return revised


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path,
                        default=Path(__file__).resolve().with_name('generators.py'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    original = args.target.read_text()
    revised = repair_source(original)
    if original == revised:
        print('Directory creation already repaired.')
        return 0
    if args.check:
        print(f'Repair required: {args.target}')
        return 1
    backup = args.target.with_suffix(args.target.suffix + '.before-mkdir-repair')
    if not backup.exists():
        backup.write_text(original)
    args.target.write_text(revised)
    print(f'Repaired directory creation: {args.target}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
