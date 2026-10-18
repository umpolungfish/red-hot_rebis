#!/usr/bin/env python3
"""Assemble all nine historical dataset layers at an explicit output path."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from clink.datasets.gen_part1 import build_source as build_base
from clink.datasets.gen_part2 import build_source as append_first
from clink.datasets.gen_part3 import build_source as append_second
from clink.datasets.gen_part4 import build_source as append_last
from clink.datasets._generator_assembly import main as _main


def build_source():
    return append_last(append_second(append_first(build_base())))


def main(argv=None):
    return _main(build_source, argv)


if __name__ == '__main__':
    raise SystemExit(main())
