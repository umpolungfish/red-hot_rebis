#!/usr/bin/env python3
"""
rebis.file_input — Universal --file / --stdin / positional-file support
══════════════════════════════════════════════════════════════════════
Adds --file/-f, --stdin/-i, and positional-filepath detection to any argparse
parser. Merges file contents with CLI args (CLI overrides file).

Supports TWO file categories:
  1. Configuration files (.json, .jsn, .yml, .yaml, .toml) → parsed as a dict
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
import copy
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
        sequence_parts.append(''.join(line.split()))

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
    if path.lower().endswith(('.genbank', '.gb')):
        records = []
        in_origin = False
        for line in text.splitlines():
            if line.startswith('ORIGIN'):
                in_origin = True
            elif line.startswith('//'):
                in_origin = False
            elif in_origin:
                records.append(re.sub(r'[\s0-9]', '', line))
        if not records:
            raise ValueError('GenBank file has no ORIGIN sequence')
        sequence = ''.join(records)
    else:
        sequence = _parse_fasta(text)
    # Use a sentinel key; will be remapped to the correct arg name
    # by inspecting the parser in parse_with_file()
    return {'__sequence__': sequence}


# ── JSON loading (unchanged) ─────────────────────────────────────────

def _load_json_file(path: str) -> dict:
    """Load a JSON file and return as dict."""
    suffix = Path(path).suffix.lower()
    with open(path, 'r', encoding='utf-8') as f:
        if suffix == '.toml':
            import tomllib
            data = tomllib.loads(f.read())
        elif suffix in ('.yml', '.yaml'):
            try:
                import yaml
            except ImportError as exc:
                raise ValueError('YAML input requires PyYAML') from exc
            data = yaml.safe_load(f)
        else:
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

    file_data = dict(file_data)
    sequence = file_data.pop('__sequence__')
    arg_name = _find_seq_arg_name(parser)

    if arg_name:
        file_data[arg_name] = sequence
    else:
        raise ValueError('Selected command has no sequence argument')

    return file_data


# ── Public API ───────────────────────────────────────────────────────

def add_file_input(parser: argparse.ArgumentParser,
                   allow_positional: bool = True) -> argparse.ArgumentParser:
    """
    Add --file and --stdin arguments to an existing parser.
    Returns the parser (mutated in place) so it can be chained.
    """
    existing = {option for action in parser._actions
                for option in action.option_strings}
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
    tmp_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    tmp_parser.add_argument('--file', '-f', type=str, default=None)
    tmp_parser.add_argument('--stdin', '-i', action='store_true', default=False)
    try:
        tmp_args, remaining = tmp_parser.parse_known_args(original_argv)
    except SystemExit:
        parser.error('Invalid --file/--stdin arguments')

    positional_index = None
    file_path_used = tmp_args.file
    if not file_path_used and allow_positional:
        current_parser = parser
        index = 0
        while index < len(remaining):
            token = remaining[index]
            subaction = next((a for a in current_parser._actions
                              if isinstance(a, argparse._SubParsersAction)
                              and token in a.choices), None)
            if subaction is None:
                break
            current_parser = subaction.choices[token]
            index += 1
        if index < len(remaining):
            candidate = remaining[index]
            if not candidate.startswith('-') and os.path.isfile(candidate) and _is_input_file(candidate):
                file_path_used = candidate
                positional_index = index

    stdin_used = tmp_args.stdin
    if file_path_used and stdin_used:
        parser.error('Choose one input source: --file or --stdin')
    if file_path_used and not os.path.isfile(file_path_used):
        parser.error(f'Input file does not exist: {file_path_used}')

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
            parser.error(f"Failed to parse {file_path_used}: {e}")
        except Exception as e:
            parser.error(f"Failed to read {file_path_used}: {e}")
    elif stdin_used:
        try:
            file_data = _load_stdin()
            from_file = True
        except (json.JSONDecodeError, ValueError) as e:
            parser.error(f"Failed to parse stdin: {e}")

    # The preliminary parser already removes all file option spellings,
    # including --file=path and -fpath.
    argv_for_parse = list(remaining)
    if positional_index is not None:
        argv_for_parse.pop(positional_index)
    # Work on a private parser so required flags, positional arity and defaults
    # retain their original meaning on the caller's next invocation.
    effective = copy.deepcopy(parser)
    selected = [effective]
    current = effective
    command_from_file = file_data.get('command')
    command_consumed = False
    for token in list(argv_for_parse):
        subactions = [a for a in current._actions
                      if isinstance(a, argparse._SubParsersAction)]
        match = next((a.choices[token] for a in subactions
                      if token in a.choices), None)
        if match is not None:
            selected.append(match)
            current = match
            command_consumed = True
    if command_from_file is not None and not command_consumed:
        subaction = next((a for a in effective._actions
                          if isinstance(a, argparse._SubParsersAction)), None)
        if subaction is None or command_from_file not in subaction.choices:
            parser.error(f'Unknown input command: {command_from_file}')
        argv_for_parse.insert(0, command_from_file)
        current = subaction.choices[command_from_file]
        selected.append(current)
    try:
        file_data = _remap_sequence(file_data, current)
    except ValueError as exc:
        parser.error(str(exc))
    actions = {a.dest: (owner, a) for owner in selected for a in owner._actions
               if not isinstance(a, argparse._SubParsersAction)}
    for key, value in file_data.items():
        if key == 'command':
            continue
        if key not in actions or key in ('help', 'file', 'stdin'):
            parser.error(f'Unknown input argument for selected command: {key}')
        owner, action = actions[key]
        try:
            if value is None and action.required:
                raise ValueError('required argument cannot be null')
            if action.nargs in ('+', '*') or isinstance(action.nargs, int) and action.nargs > 0:
                if not isinstance(value, list):
                    raise ValueError('expected a list of argument values')
                if action.nargs == '+' and not value:
                    raise ValueError('expected at least one argument value')
                if isinstance(action.nargs, int) and len(value) != action.nargs:
                    raise ValueError(f'expected {action.nargs} argument values')
            if action.type is not None and value is not None:
                value = ([action.type(v) for v in value] if isinstance(value, list)
                         else action.type(value))
            if isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction, argparse.BooleanOptionalAction)):
                if not isinstance(value, bool):
                    raise ValueError('expected a JSON boolean')
            values = value if isinstance(value, list) else [value]
            if action.choices is not None and any(v not in action.choices for v in values):
                raise ValueError(f'expected one of {list(action.choices)}')
        except (ValueError, TypeError) as exc:
            parser.error(f'Invalid input argument {key}: {exc}')
        owner.set_defaults(**{key: value})
        action.required = False
        if not action.option_strings and action.nargs is None:
            action.nargs = '?'
        elif not action.option_strings and action.nargs == '+':
            action.nargs = '*'
    parsed = effective.parse_args(argv_for_parse)
    if file_path_used:
        parsed.file = file_path_used
    if stdin_used:
        parsed.stdin = True
    return parsed
