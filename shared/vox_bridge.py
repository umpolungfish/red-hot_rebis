"""shared/vox_bridge.py — the one residue-to-mark correspondence, from V⊙x.

This repository predates V⊙x and grew four copies of the correspondence between
the twelve promoted amino acids and the twelve marks. Four copies drift, and
they had: three of them carried a pre-revision assignment with histidine,
asparagine and glutamine in the wrong places, which is the division and the
rejoining themselves.

V⊙x holds the correspondence in `genetic_table.py`, which is generated from the
Lean that proves it, so it cannot drift from the proof. Every consumer here
reads it through this module, and nothing here writes it down again.

What this module offers:

    AA_MARK        three-letter residue -> mark, for the twelve promoted
    MARK_AA        the inverse
    CODON_MARK     codon -> mark, for the twenty-three promoted codons
    mark_of        residue (one or three letter) -> mark, or None
    lift_rna       a coding sequence -> (word, reading, stop codon)
    verdict        a word -> (outcome, why), by the closure engine itself
    audit_word     a word -> a dict carrying the outcome and the counts
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_VOX = Path.home() / "imsgct" / "Vox"
if _VOX.exists() and str(_VOX) not in sys.path:
    sys.path.insert(0, str(_VOX))

import genetic_table as _gt      # noqa: E402  (path is set immediately above)
import vox as _vox               # noqa: E402

# ── the correspondence, read from V⊙x rather than restated ──────────────────

AA_MARK: Dict[str, str] = {aa: entry[0] for aa, entry in _gt.AA_GLYPH.items()}
AA_AXIS: Dict[str, str] = {aa: entry[1] for aa, entry in _gt.AA_GLYPH.items()}
MARK_AA: Dict[str, str] = {mark: aa for aa, mark in AA_MARK.items()}

CODON_MARK: Dict[str, str] = {
    codon: AA_MARK[val]
    for codon, (kind, val) in _gt.CODON.items()
    if kind == "aa" and val in AA_MARK
}

_ONE_TO_THREE = {
    "A": "Ala", "R": "Arg", "N": "Asn", "D": "Asp", "C": "Cys", "Q": "Gln",
    "E": "Glu", "G": "Gly", "H": "His", "I": "Ile", "L": "Leu", "K": "Lys",
    "M": "Met", "F": "Phe", "P": "Pro", "S": "Ser", "T": "Thr", "W": "Trp",
    "Y": "Tyr", "V": "Val",
}

# The marks that transform what they act on. A region enclosing none of these
# is not substantial, whatever its length.
WORK_MARKS = frozenset("≻≺⋈⊤⊥⊞◻")
FORK, FUSE = "∈", "∋"


def mark_of(residue: str) -> Optional[str]:
    """The mark a residue activates, or None for the eight that are silent.

    Accepts one-letter and three-letter codes in any case.
    """
    r = residue.strip()
    if len(r) == 1:
        r = _ONE_TO_THREE.get(r.upper(), r)
    r = r[:1].upper() + r[1:].lower()
    return AA_MARK.get(r)


def word_of_peptide(sequence: str) -> str:
    """A residue sequence -> its word, silent residues emitting nothing."""
    return "".join(m for m in (mark_of(c) for c in sequence) if m)


def lift_rna(sequence: str) -> Tuple[str, List[tuple], Optional[str]]:
    """A coding sequence -> (word, reading, stop codon), through V⊙x."""
    word, reading, stopped = _vox.lift_rna(sequence)
    return "".join(word), reading, stopped


def verdict(word: str) -> Tuple[str, str]:
    """The closure outcome of a word, from the engine that defines it."""
    return _vox.verdict(list(word))


def audit_word(word: str) -> dict:
    """The outcome with the counts it rests on."""
    v, why = verdict(word)
    forks, fuses = word.count(FORK), word.count(FUSE)
    return {
        "word": word,
        "verdict": v,
        "why": why,
        "forks": forks,
        "fuses": fuses,
        "difference": forks - fuses,
        "work_marks": sum(1 for m in word if m in WORK_MARKS),
    }


def audit_module(path: str) -> List[tuple]:
    """Lift and verdict every top-level function of a Python module.

    V⊙x loads a file on its own, which is right for a standalone script and
    wrong for a module inside a package: a package-relative import has no
    parent to resolve against and the load fails. When the file sits under a
    package here, it is imported by its dotted name instead and its functions
    are lifted the same way.
    """
    try:
        return _vox.scan_module(path)
    except (ImportError, SystemExit, ValueError):
        pass

    import importlib
    root = Path(__file__).resolve().parent.parent
    target = Path(path).resolve()
    try:
        rel = target.relative_to(root)
    except ValueError:
        raise
    dotted = ".".join(rel.with_suffix("").parts)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    mod = importlib.import_module(dotted)
    results = []
    for name in dir(mod):
        obj = getattr(mod, name)
        if callable(obj) and getattr(obj, "__code__", None) is not None \
                and getattr(obj, "__module__", None) == dotted:
            word = _vox.lift_function(obj)
            v, why = _vox.verdict(word)
            results.append((name, v, why, "".join(word)))
    return results


__all__ = [
    "AA_MARK", "AA_AXIS", "MARK_AA", "CODON_MARK", "WORK_MARKS", "FORK", "FUSE",
    "mark_of", "word_of_peptide", "lift_rna", "verdict", "audit_word",
    "audit_module",
]
