#!/usr/bin/env python3
"""
Fix double-close parentheses from migrate_rich.py bugs.
Pattern: info_line(f"...")) → info_line(f"...")
Also handles success_line, error_line, warning_line, separator, header, etc.
"""

import re
import sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.parent.resolve()

FUNCS = r'(info_line|success_line|error_line|warning_line|header|separator|subheader|reaction_header|panel|cprint)'

def fix_file(filepath):
    p = Path(filepath)
    content = p.read_text()
    
    # Pattern: funcName( ... )) at end of line → funcName( ... )
    content = re.sub(
        rf'({FUNCS})\(((?:[^)(]+|\([^)(]*\))*)\)\)$',
        r'\1(\2)',
        content,
        flags=re.MULTILINE
    )
    
    # Also handle triple parens: funcName( ... )))
    content = re.sub(
        rf'({FUNCS})\(((?:[^)(]+|\([^)(]*\))*)\)\)\)$',
        r'\1(\2)',
        content,
        flags=re.MULTILINE
    )
    
    # Fix specific bad patterns seen:
    # info_line(f"text")) → info_line(f"text")
    content = re.sub(
        rf'({FUNCS})\(((?:[^)(]+|\([^)(]*\))*)\)\)',
        r'\1(\2)',
        content
    )
    
    p.write_text(content)
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Fix all .py files")
    parser.add_argument("files", nargs="*", help="Specific files to fix")
    args = parser.parse_args()
    
    if args.all:
        result = list(REBIS_ROOT.rglob("*.py"))
        files = [f for f in result if '.venv' not in str(f) and '__pycache__' not in str(f)]
    else:
        files = [Path(f) for f in args.files]
    
    fixed = 0
    for f in files:
        try:
            fix_file(f)
            fixed += 1
        except Exception as e:
            print(f"  ❌ {f}: {e}")
    
    print(f"Fixed {fixed} files")

if __name__ == "__main__":
    main()
