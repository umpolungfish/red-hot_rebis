#!/usr/bin/env python3
"""Append historical dataset assembly part 2 to an explicit destination."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from clink.datasets._generator_assembly import append_template, main as _main


def build_source(source):
    template = Path(__file__).with_name('gen_part2_template.py.txt').read_text(encoding='utf-8')
    return append_template(source, template)


def main(argv=None):
    return _main(build_source, argv, append=True)


if __name__ == '__main__':
    raise SystemExit(main())
