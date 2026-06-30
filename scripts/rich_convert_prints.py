#!/usr/bin/env python3
"""
rich_convert_prints.py — Convert remaining print() calls to rich equivalents.
Handles files that already have 'from shared.rich_output import *' but still
use raw print() statements.
"""
import re, sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.parent.resolve()

def extract_print_args(stripped_line):
    if not stripped_line.startswith('print('):
        return None, False
    depth = 0
    start = 6
    end = -1
    for i, ch in enumerate(stripped_line[start:], start):
        if ch == '(': depth += 1
        elif ch == ')':
            if depth == 0:
                end = i
                break
            depth -= 1
    if end == -1:
        return None, False
    arg = stripped_line[start:end]
    is_f = arg.strip().startswith('f"') or arg.strip().startswith("f'") or arg.strip().startswith('f"""')
    return arg, is_f

def convert_print(line):
    stripped = line.strip()
    indent = line[:len(line) - len(line.lstrip())]
    arg, is_f = extract_print_args(stripped)
    if arg is None:
        return line  # can't parse, leave alone
    
    s = stripped
    a = arg.strip()
    
    # Box-drawing → separator
    if any(c in s for c in '╔═╗║╚╝╠╣╦╩╬'):
        if '║' in s:
            inner = a.strip('f"\'').strip('║').strip()
            if inner:
                return f'{indent}info_line(f"  {inner}")'
            return ''
        return f'{indent}separator()'
    
    # ASCII separator lines
    if re.match(r'^print\(["\']={10,}', s) or re.match(r'^print\(["\']-{10,}', s):
        return f'{indent}separator()'
    
    # JSON dumps — leave alone
    if 'json.dumps' in a or 'json.loads' in a:
        return line
    
    # Error patterns
    if is_f:
        al = a.lower()
        if any(w in al for w in ['error', 'fail', '✗', 'traceback', 'exception', 'abort', 'fatal']):
            return f'{indent}error_line({a})'
        if any(w in al for w in ['warning', 'warn', '⚠']):
            return f'{indent}warning_line({a})'
        if any(w in al for w in ['success', 'done', '✓', '✅', 'complete', 'ok']):
            return f'{indent}success_line({a})'
        # f-string → info_line
        return f'{indent}info_line({a})'
    
    # Plain string
    if (a.startswith('"') and a.endswith('"')) or (a.startswith("'") and a.endswith("'")):
        inner = a[1:-1]
        if inner.count('=') > 10 or inner.count('-') > 10 or inner.count('─') > 5:
            return f'{indent}separator()'
        return f'{indent}info_line({a})'
    
    # Complex expression — leave alone
    return line

def process_file(filepath, dry_run=False):
    p = Path(filepath)
    content = p.read_text()
    lines = content.split('\n')
    new_lines = []
    changed = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('print(') and not stripped.startswith('print(') == False:
            new_line = convert_print(line)
            if new_line != line:
                changed += 1
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if changed > 0:
        if not dry_run:
            p.write_text('\n'.join(new_lines))
        return (str(p.relative_to(REBIS_ROOT)), changed)
    return None

def main():
    dry_run = '--dry-run' in sys.argv
    target = None
    for a in sys.argv[1:]:
        if a != '--dry-run':
            target = a
    
    if target:
        files = [REBIS_ROOT / target]
    else:
        # Find all files with rich import but still have print() calls
        files = []
        for p in REBIS_ROOT.rglob('*.py'):
            rs = str(p.relative_to(REBIS_ROOT))
            if '.venv' in rs or '__pycache__' in rs:
                continue
            content = p.read_text()
            if 'from shared.rich_output import' in content and 'print(' in content:
                # Only count files where print() is used for output (not module-level)
                print_lines = [l for l in content.split('\n') if l.strip().startswith('print(')]
                if print_lines:
                    files.append(p)
    
    results = []
    for f in sorted(files):
        result = process_file(f, dry_run)
        if result:
            results.append(result)
    
    if not results:
        info_line("All print() calls already converted.")
        return
    
    total = sum(r[1] for r in results)
    info_line(f"\n{'File':<70} {'Prints→Rich'}")
    print('-' * 90)
    for path, count in sorted(results):
        info_line(f"{path:<70} {count}")
    
    if dry_run:
        info_line(f"\n🔍 DRY RUN: {len(results)} files, {total} print→rich conversions")
    else:
        success_line(f"\n✅ {len(results)} files updated, {total} print→rich conversions")


if __name__ == '__main__':
    main()
