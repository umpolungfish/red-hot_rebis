#!/usr/bin/env python3
"""
rebis.file_input — Universal --file / --stdin / positional-file support
══════════════════════════════════════════════════════════════════════
Adds --file/-f, --stdin/-i, and positional-filepath detection to any argparse
parser. Merges file contents with CLI args (CLI overrides file).

Supports TWO file categories:
  1. JSON files (.json, .yml, .yaml, .toml, .jsn) → parsed as JSON dict
  2. Biological sequence files (.fasta, .fa, .fna, .ffn, .faa, .frn, .txt)
     → parsed as FASTA or plain-text sequence, mapped to the first
       sequence-type argument the parser accepts (--dna, --seq, --sequence,
       --protein, --smiles)

Usage in any module's main():
    from rebis.file_input import add_file_input, parse_with_file

    parser = argparse.ArgumentParser(...)
    # ... set up subparsers, args, etc ...
    args = parse_with_file(parser)

Supported modes:
    rebis.ch3mpiler forward CC(=O)O              # direct CLI (existing)
    rebis.ch3mpiler --file input.json            # JSON filepath
    rebis.chain --file gene.fasta                # FASTA filepath
    rebis.chain -f gene.fasta --target CC(=O)O   # FASTA + CLI overrides
    rebis.ch3mpiler --stdin < input.json         # stdin entry
    rebis.ch3mpiler input.json                   # positional auto-detect
    rebis.chain gene.fasta                       # positional FASTA auto-detect

JSON format (simple flat):
    {"dna": "ATGGCC...", "target": "CC(=O)O", "depth": 2}

JSON format (with sub-command):
    {"command": "forward", "smiles": "CC(=O)O"}

FASTA format:
    >gene1 description
    ATGGCCGACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG
    GTGAACTGCAAGAAGATCGTGCCC
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ── File type detection ──────────────────────────────────────────────

JSON_EXTS = ('.json', '.yml', '.yaml', '.toml', '.jsn')
SEQ_EXTS = ('.fasta', '.fa', '.fna', '.ffn', '.faa', '.frn', '.txt', '.seq', '.genbank', '.gb')
# Argument names (in priority order) that accept biological sequences
SEQ_ARG_NAMES = ['dna', 'seq', 'sequence', 'protein', 'smiles', 'peptide', 'rna']


def _is_json_like(path: str) -> bool:
    """Check if a path looks like a JSON input file."""
    return path.lower().endswith(JSON_EXTS)


def _is_seq_like(path: str) -> bool:
    """Check if a path looks like a biological sequence file."""
    return path.lower().endswith(SEQ_EXTS)


def _is_input_file(path: str) -> bool:
    """Check if a path is any recognized input file type."""
    return _is_json_like(path) or _is_seq_like(path)


# ── Sequence file parsing ────────────────────────────────────────────

def _parse_fasta(text: str) -> str:
    """
    Parse FASTA-formatted text and return the concatenated sequence.
    Handles multi-line sequences and multiple records (concatenates all).
    Also handles plain-text sequences (no FASTA header).
    """
    lines = text.strip().splitlines()
    if not lines:
        raise ValueError("Empty sequence file")

    sequence_parts = []
    has_header = False

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            # FASTA header — skip
            has_header = True
            continue
        if line.startswith(';'):
            # FASTA comment — skip
            continue
        # Sequence line — strip whitespace and accumulate
        sequence_parts.append(line)

    if not sequence_parts:
        raise ValueError("No sequence data found in file")

    sequence = ''.join(sequence_parts)

    # Basic validation: allow nucleotide and amino acid characters
    valid_chars = re.match(r'^[ACGTUNRYSWKMBDHVACDEFGHIKLMNPQRSTVWY*\-\.]+$', sequence, re.IGNORECASE)
    if not valid_chars:
        # If it doesn't look like a sequence, still return it —
        # might be a SMILES string or other molecular notation
        pass

    return sequence


def _load_seq_file(path: str) -> dict:
    """
    Load a biological sequence file and return a dict mapping the
    best-matching argument name to the extracted sequence.

    Returns e.g. {"dna": "ATGGCC..."} — the key is determined later
    by _find_seq_arg_name() based on what the parser actually accepts.
    For now, use a sentinel key that will be remapped.
    """
    with open(path, 'r') as f:
        text = f.read()
    sequence = _parse_fasta(text)
    # Use a sentinel key; will be remapped to the correct arg name
    # by inspecting the parser in parse_with_file()
    return {'__sequence__': sequence}


# ── JSON loading (unchanged) ─────────────────────────────────────────

def _load_json_file(path: str) -> dict:
    """Load a JSON file and return as dict."""
    with open(path, 'r') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON file must contain a dict/object, got {type(data).__name__}")
    return data


def _load_stdin() -> dict:
    """Read JSON from stdin."""
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"stdin JSON must be a dict/object, got {type(data).__name__}")
    return data


# ── Parser inspection ────────────────────────────────────────────────

def _find_seq_arg_name(parser: argparse.ArgumentParser) -> str | None:
    """
    Inspect the parser's arguments to find which sequence-type argument
    it accepts. Returns the dest name (e.g. 'dna') or None.
    Priority order: dna > seq > sequence > protein > smiles > peptide > rna
    """
    # Collect all dest names from the parser
    dest_names = set()
    for action in parser._actions:
        if action.dest:
            dest_names.add(action.dest)

    for name in SEQ_ARG_NAMES:
        if name in dest_names:
            return name
    return None


def _remap_sequence(file_data: dict, parser: argparse.ArgumentParser) -> dict:
    """
    If file_data contains the __sequence__ sentinel, remap it to the
    best-matching argument name the parser accepts.
    """
    if '__sequence__' not in file_data:
        return file_data

    sequence = file_data.pop('__sequence__')
    arg_name = _find_seq_arg_name(parser)

    if arg_name:
        file_data[arg_name] = sequence
    else:
        # Fallback: try 'dna' even if not in parser — parser.set_defaults
        # will add it harmlessly, and cmd_chain checks args.dna
        file_data['dna'] = sequence

    return file_data


# ── Public API ───────────────────────────────────────────────────────

def add_file_input(parser: argparse.ArgumentParser,
                   allow_positional: bool = True) -> argparse.ArgumentParser:
    """
    Add --file and --stdin arguments to an existing parser.
    Returns the parser (mutated in place) so it can be chained.
    """
    existing = {a.option_strings[0] if a.option_strings else ''
                for a in parser._actions}
    if '--file' not in existing and '-f' not in existing:
        parser.add_argument('--file', '-f', type=str, default=None,
                           help='Input file (JSON or FASTA/sequence)')
    if '--stdin' not in existing and '-i' not in existing:
        parser.add_argument('--stdin', '-i', action='store_true',
                           default=False,
                           help='Read JSON arguments from stdin')
    return parser


def parse_with_file(parser: argparse.ArgumentParser,
                    args=None,
                    allow_positional: bool = True):
    """
    Parse args with file/stdin/positional support.

    Pipeline:
    1. Detect file source (--file, --stdin, positional file)
    2. Load data from whichever source (JSON or sequence format)
    3. Set file data as parser defaults
    4. Parse remaining CLI args on top (CLI overrides file)
    5. Restore --file/--stdin values in namespace if they were used

    Returns: argparse.Namespace
    """
    add_file_input(parser, allow_positional=allow_positional)

    original_argv = list(args) if args is not None else sys.argv[1:]

    file_data = {}
    from_file = False
    file_path_used = None
    stdin_used = False

    # ── Phase 1: detect file source via a throwaway parse ──
    tmp_parser = argparse.ArgumentParser(add_help=False)
    tmp_parser.add_argument('--file', '-f', type=str, default=None)
    tmp_parser.add_argument('--stdin', '-i', action='store_true', default=False)
    try:
        tmp_args, remaining = tmp_parser.parse_known_args(original_argv)
    except SystemExit:
        tmp_args = argparse.Namespace(file=None, stdin=False)
        remaining = list(original_argv)

    # Check positional filepath (only if --file not already given)
    if not tmp_args.file and allow_positional and remaining:
        candidate = remaining[0]
        if (not candidate.startswith('-')
                and os.path.isfile(candidate)
                and _is_input_file(candidate)):
            file_path_used = candidate
    else:
        file_path_used = tmp_args.file

    stdin_used = tmp_args.stdin

    # ── Phase 2: load file data ──
    if file_path_used and os.path.isfile(file_path_used):
        try:
            if _is_json_like(file_path_used):
                file_data = _load_json_file(file_path_used)
            else:
                # Try sequence format (FASTA, plain text)
                file_data = _load_seq_file(file_path_used)
            from_file = True
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: failed to parse {file_path_used}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: failed to read {file_path_used}: {e}", file=sys.stderr)
    elif stdin_used:
        try:
            file_data = _load_stdin()
            from_file = True
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: failed to parse stdin: {e}", file=sys.stderr)

    # Remap __sequence__ sentinel to the correct arg name
    if from_file and file_data:
        file_data = _remap_sequence(file_data, parser)

    # ── Phase 3: build argv for real parse ──
    if from_file and file_data:
        argv_for_parse = list(original_argv)

        # Strip file-positional if it was auto-detected
        if (allow_positional and file_path_used
                and argv_for_parse and argv_for_parse[0] == file_path_used):
            argv_for_parse.pop(0)

        # Strip --file / -f and its value, --stdin / -i
        stripped = []
        skip_next = False
        for i, a in enumerate(argv_for_parse):
            if skip_next:
                skip_next = False
                continue
            if a in ('--file', '-f'):
                skip_next = True  # skip the value too
                continue
            if a in ('--stdin', '-i'):
                continue  # skip the flag
            stripped.append(a)
        argv_for_parse = stripped

        # Set file data as parser defaults
        parser.set_defaults(**file_data)

    else:
        argv_for_parse = args  # pass through original args=None

    # ── Phase 4: parse ──
    parsed = parser.parse_args(argv_for_parse if from_file else args)

    # ── Phase 5: restore file/stdin status ──
    if file_path_used:
        parsed.file = file_path_used
    if stdin_used:
        parsed.stdin = True

    return parsed
