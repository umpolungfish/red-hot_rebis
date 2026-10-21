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
    audit_module, audit_word,
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


def _show_carrier(glut, args):
    import json
    # Each self-mark retains its own source/IFIX boundary. Flattening would
    # cause an earlier residue's irreversible fix to silence later residues.
    for residue in glut.residues:
        for form in residue['self_marks']:
            form['structural_audit'] = audit_word(form['word'])
    output = glut.as_dict()
    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        header("V⊙x: resident amino-acid self-marks")
        info_line(f"  native B; {len(glut.residues)} residues; forms co-held")
        for residue in glut.residues:
            for form in residue['self_marks']:
                info_line(f"  {residue['index']} {residue['aa']} {form['name']} {form['word']}")
                info_line(f"    register {form['execution']['register']}; structural {form['structural_audit']['verdict']}")
    return 0


def _cmd_rna(args) -> int:
    from rhr_p4rky.serpent_rod import SerpentRod
    from rhr_p4rky.protein_glut import ProteinGlut
    source = SerpentRod(args.sequence)
    aas = source.translate_to_aa()
    glut = ProteinGlut.prepare(aas, [source.rna[3*i:3*i+3] for i in range(len(aas))])
    return _show_carrier(glut, args)


def _cmd_peptide(args) -> int:
    from rhr_p4rky.protein_glut import prepare_sequence
    return _show_carrier(prepare_sequence(args.sequence), args)


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
    audited = 0
    failed = []
    for p in targets:
        try:
            rows = audit_module(str(p))
        except (Exception, SystemExit) as exc:
            failed.append((str(p.relative_to(root)), str(exc)))
            continue
        audited += 1
        for _name, v, *_rest in rows:
            total[v] = total.get(v, 0) + 1
    info_line(f"  modules audited: {audited} of {len(targets)} selected")
    for path, reason in failed:
        error_line(f"  audit failed: {path}: {reason}")
    for v in "TBNF":
        if v in total:
            info_line(f"  {v} {total[v]:>5}   {_OUTCOME[v]}")
    return 1 if failed else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="rebis.vox",
        description="Closure audit through V⊙x: four outcomes over the twelve marks.")
    sub = ap.add_subparsers(dest="COMMAND", required=True)

    p = sub.add_parser("rna", help="execute full AA self-marks from coding RNA; retain chemical forms")
    p.add_argument("sequence")
    p.add_argument("--json", action="store_true", help="Return complete carrier, source forms and native word executions")
    p.set_defaults(func=_cmd_rna)

    p = sub.add_parser("peptide", help="execute full self-marks for every residue, retaining native glut")
    p.add_argument("sequence")
    p.add_argument("--json", action="store_true", help="Return complete carrier without flattening residue/form boundaries")
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
    if getattr(args, "limit", 0) < 0:
        ap.error("--limit must be nonnegative")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
