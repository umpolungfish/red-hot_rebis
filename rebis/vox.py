"""rebis.vox — closure audit through V⊙x.

This repository was built before V⊙x existed, so it could design and fold and
synthesise without ever asking the one question V⊙x answers: does the thing
close? Four outcomes, from the engine that defines them, over the same twelve
marks everything here is already imscribed in.

  rebis.vox rna <SEQ>        a coding sequence, lifted and verdicted
  rebis.vox peptide <SEQ>    a residue sequence, lifted and verdicted
  rebis.vox word <WORD>      a word in the twelve, verdicted directly
  rebis.vox module <PATH>    every top-level function of a Python module
  rebis.vox self             this repository's own engines, audited
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from shared.rich_output import *
from shared.vox_bridge import (
    audit_module, audit_word, lift_rna, word_of_peptide,
)

_OUTCOME = {
    "T": "closes",
    "B": "hangs open",
    "N": "null",
    "F": "ill-typed",
}


def _report(word: str, source: str = "") -> int:
    a = audit_word(word)
    if source:
        info_line(f"  {source}")
    info_line(f"  word      {a['word']}")
    info_line(f"  divisions {a['forks']}   rejoinings {a['fuses']}   "
              f"difference {a['difference']:+d}   work {a['work_marks']}")
    info_line(f"  verdict   {a['verdict']}  ({_OUTCOME.get(a['verdict'], '?')})")
    info_line(f"  {a['why']}")
    return 0


def _cmd_rna(args) -> int:
    header("V⊙x — a coding sequence")
    word, reading, stopped = lift_rna(args.sequence)
    if not word:
        error_line("  no promoted codon in that sequence")
        return 1
    for codon, aa, glyph, family in reading[:24]:
        info_line(f"    {codon:<6} {aa:<5} {family:<16} {glyph}")
    if len(reading) > 24:
        info_line(f"    … {len(reading) - 24} more")
    if stopped:
        info_line(f"  stop      {stopped}")
    return _report(word)


def _cmd_peptide(args) -> int:
    header("V⊙x — a residue sequence")
    word = word_of_peptide(args.sequence)
    if not word:
        error_line("  no promoted residue in that sequence")
        return 1
    return _report(word, f"{len(args.sequence)} residues, {len(word)} promoted")


def _cmd_word(args) -> int:
    header("V⊙x — a word")
    return _report(args.word)


def _cmd_module(args) -> int:
    header(f"V⊙x — {Path(args.path).name}")
    rows = audit_module(args.path)
    counts = {}
    for name, v, why, word, *_ in rows:
        counts[v] = counts.get(v, 0) + 1
        if v in ("B", "F"):
            info_line(f"  {v}  {name}")
    info_line("")
    for v in "TBNF":
        if v in counts:
            info_line(f"  {v} {counts[v]:>4}   {_OUTCOME[v]}")
    return 0


def _cmd_self(args) -> int:
    """Audit the repository's own engines, which is what V⊙x is for."""
    header("V⊙x — this repository")
    root = Path(__file__).parent.parent
    targets = sorted(
        p for p in root.rglob("*.py")
        if ".venv" not in p.parts and "_archive" not in p.parts
        and "__pycache__" not in p.parts
    )
    if args.limit:
        targets = targets[: args.limit]
    total = {}
    for p in targets:
        try:
            rows = audit_module(str(p))
        except ImportError:
            # generator and patch scripts refuse import by design
            continue
        except Exception:
            continue
        for _name, v, *_rest in rows:
            total[v] = total.get(v, 0) + 1
    info_line(f"  modules audited: {len(targets)}")
    for v in "TBNF":
        if v in total:
            info_line(f"  {v} {total[v]:>5}   {_OUTCOME[v]}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="rebis.vox",
        description="Closure audit through V⊙x: four outcomes over the twelve marks.")
    sub = ap.add_subparsers(dest="COMMAND", required=True)

    p = sub.add_parser("rna", help="lift and verdict a coding sequence")
    p.add_argument("sequence")
    p.set_defaults(func=_cmd_rna)

    p = sub.add_parser("peptide", help="lift and verdict a residue sequence")
    p.add_argument("sequence")
    p.set_defaults(func=_cmd_peptide)

    p = sub.add_parser("word", help="verdict a word in the twelve")
    p.add_argument("word")
    p.set_defaults(func=_cmd_word)

    p = sub.add_parser("module", help="verdict every function of a Python module")
    p.add_argument("path")
    p.set_defaults(func=_cmd_module)

    p = sub.add_parser("self", help="audit this repository's own engines")
    p.add_argument("--limit", type=int, default=0, help="stop after N modules")
    p.set_defaults(func=_cmd_self)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
