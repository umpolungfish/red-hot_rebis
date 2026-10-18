#!/usr/bin/env python3
"""Render the historical dataset generator base to an explicit output path.

This is the first assembly part; layer definitions are supplied by later parts.
"""
import argparse
import ast
from pathlib import Path


def build_source():
    source = Path(__file__).with_name('gen_part1_template.py.txt').read_text(encoding='utf-8')
    ast.parse(source)
    return source


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Destination Python source')
    parser.add_argument('--check', action='store_true', help='Check without creating or changing files')
    args = parser.parse_args(argv)
    try:
        source = build_source()
        previous = args.output.read_bytes() if args.output.exists() else None
        if previous == source.encode('utf-8'):
            print('Generator base already matches.')
            return 0
        if args.check:
            print(f'Generator base differs: {args.output}')
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if previous is not None:
            backup = args.output.with_suffix(args.output.suffix + '.before-generator-base')
            if not backup.exists():
                backup.write_bytes(previous)
        args.output.write_text(source, encoding='utf-8')
        print(f'Wrote generator base: {args.output}')
        return 0
    except (OSError, SyntaxError, UnicodeError) as exc:
        print(f'Generator base failed: {exc}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
