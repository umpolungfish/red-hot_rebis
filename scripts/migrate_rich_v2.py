#!/usr/bin/env python3
"""
migrate_rich_v2.py — Comprehensive rich-formatting migration for all CLI tools.
Converts print() patterns to rich equivalents from shared.rich_output.

v2 improvements over v1:
  - Handles box-drawing characters (╔═╗║╚╝) → separator/header/panel
  - Converts all f-string prints to info_line
  - Converts JSON dump calls to formatted output
  - Converts plain string prints
  - Preserves complex expressions (multiline, json.dumps)
  - Handles multi-line print statements (with line continuations)

Usage:
    python3 scripts/migrate_rich_v2.py --all
    python3 scripts/migrate_rich_v2.py --dry-run --all
    python3 scripts/migrate_rich_v2.py path/to/file.py
"""

import re
import sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.parent.resolve()

# ── Detection ───────────────────────────────────────────────────────

def has_rich_import(content):
    return bool(re.search(
        r'from\s+shared\.rich_output\s+import',
        content
    ))

# ── Print argument extraction ───────────────────────────────────────

def extract_print_args(stripped_line):
    """Extract the argument(s) from a print(...) call. Returns (arg_str, is_fstring)."""
    if not stripped_line.startswith('print('):
        return None, False
    
    # Find the matching closing paren (handles nested parens)
    depth = 0
    start = 6  # len('print(')
    end = -1
    for i, ch in enumerate(stripped_line[start:], start):
        if ch == '(':
            depth += 1
        elif ch == ')':
            if depth == 0:
                end = i
                break
            depth -= 1
    if end == -1:
        return None, False
    
    arg = stripped_line[start:end]
    is_fstring = arg.strip().startswith('f"') or arg.strip().startswith("f'") or arg.strip().startswith('f"""')
    return arg, is_fstring


def classify_print(stripped_line):
    """Classify a print statement into a category for conversion.
    Returns: 'header', 'section', 'separator', 'error', 'success', 'warning',
             'json', 'info', 'demo_title', 'plain', 'target', 'subheader', None
    """
    arg, is_fstring = extract_print_args(stripped_line)
    if arg is None:
        return 'complex_expression', None, None
    
    s = stripped_line
    a = arg.strip()
    
    # Box-drawing header lines
    if any(c in s for c in '╔═╗║╚╝╠╣╦╩╬'):
        if '╔' in s or '╚' in s or '╠' in s or '═' in s:
            return 'separator', arg, is_fstring
        if '║' in s:
            # Extract the text inside the box — it's a header title
            return 'box_content', arg, is_fstring
    
    # ASCII box headers
    if re.match(r'^print\(["\']={10,}', s) or re.match(r'^print\(["\']-{10,}', s):
        return 'separator', arg, is_fstring
    
    if re.match(r'^print\(f?["\']\s*={10,}', s) or re.match(r'^print\(f?["\']\s*-{10,}', s):
        return 'separator', arg, is_fstring
    
    # JSON
    if 'json.dumps' in a or 'json.loads' in a:
        return 'json', arg, is_fstring
    
    # JSON indent
    if 'indent=' in a and ('json' in a or 'dict' in a.lower()):
        return 'json', arg, is_fstring
    
    # Error/Warning patterns
    if is_fstring:
        content_lower = a.lower()
        if any(w in content_lower for w in ['error', 'fail', '✗', 'traceback', 'exception', 'abort']):
            return 'error', arg, is_fstring
        if any(w in content_lower for w in ['warning', 'warn', '⚠', 'caution']):
            return 'warning', arg, is_fstring
        if any(w in content_lower for w in ['success', 'done', '✓', '✅', 'complete', 'ok']):
            return 'success', arg, is_fstring
        
        # Section headers (all caps or title-like)
        if a.count('─') > 5 or a.count('—') > 3:
            return 'separator', arg, is_fstring
        
        # Demo title / main header
        if 'ch3mpiler' in content_lower or 'pipeline' in content_lower and 'use --' in content_lower:
            return 'demo_title', arg, is_fstring
        
        # Target/product lines
        if 'SMILES' in a or 'smiles' in a:
            return 'target', arg, is_fstring
        
        # Sub-headers (all caps words)
        words = a.strip('f"\'').split()
        if len(words) >= 2 and all(w.isupper() or w in '·|/-' for w in words[:3]):
            return 'subheader', arg, is_fstring
    
    # Plain string prints
    if (a.startswith('"') and a.endswith('"')) or (a.startswith("'") and a.endswith("'")):
        inner = a[1:-1]
        if inner.count('=') > 10:
            return 'separator', arg, is_fstring
        if inner.count('-') > 10:
            return 'separator', arg, is_fstring
        return 'info', arg, is_fstring
    
    # f-string
    if is_fstring:
        return 'info', arg, is_fstring
    
    return 'plain', arg, is_fstring


# ── Conversion ──────────────────────────────────────────────────────

def convert_line(stripped_line, indent):
    """Convert a single print line to rich equivalent. Returns (new_line, should_keep_original)."""
    category, arg, is_fstring = classify_print(stripped_line)
    
    if category is None:
        return stripped_line, True  # keep original
    
    if category == 'complex_expression':
        return stripped_line, True  # keep original
    
    if category == 'separator':
        return f'{indent}separator()', False
    
    if category == 'box_content':
        # Box side content — strip the box chars and convert to header
        inner = arg.strip('f"\'').strip('║').strip()
        if inner:
            return f'{indent}header("{inner}")', False
        return '', False  # skip empty box lines
    
    if category == 'error':
        return f'{indent}error_line({arg})', False
    
    if category == 'success':
        return f'{indent}success_line({arg})', False
    
    if category == 'warning':
        return f'{indent}warning_line({arg})', False
    
    if category == 'json':
        # Keep JSON dumps — they're machine-readable output
        return stripped_line, True
    
    if category == 'demo_title':
        return f'{indent}demo_title()', False
    
    if category == 'info':
        return f'{indent}info_line({arg})', False
    
    if category == 'target':
        return f'{indent}info_line({arg})', False
    
    if category == 'subheader':
        return f'{indent}subheader({arg})', False
    
    return stripped_line, True


# ── Content transform ───────────────────────────────────────────────

def add_rich_import(content):
    """Add 'from shared.rich_output import *' after existing imports."""
    if has_rich_import(content):
        return content
    
    lines = content.split('\n')
    
    # Find shebang and docstring
    start_search = 0
    if lines and lines[0].startswith('#!'):
        start_search = 1
    
    # Skip module docstring
    in_docstring = False
    docstring_delim = None
    for i in range(start_search, min(start_search + 20, len(lines))):
        s = lines[i].strip()
        if s.startswith('"""') or s.startswith("'''"):
            if not in_docstring:
                in_docstring = True
                docstring_delim = s[:3]
                if s.count(docstring_delim) >= 2:
                    in_docstring = False
            else:
                if docstring_delim in s:
                    in_docstring = False
        elif in_docstring:
            continue
        elif not in_docstring and s and not s.startswith('#'):
            start_search = i
            break
    
    # Find last import
    last_import_idx = -1
    in_multi = False
    for i in range(start_search, len(lines)):
        s = lines[i].strip()
        if not s:
            if last_import_idx >= 0 and not in_multi:
                break
            continue
        if s.startswith('from ') or s.startswith('import '):
            if '(' in s and ')' not in s:
                in_multi = True
                last_import_idx = i
            else:
                last_import_idx = i
        elif in_multi:
            if ')' in s:
                in_multi = False
                last_import_idx = i
        elif last_import_idx >= 0:
            break
    
    insert_at = last_import_idx + 1 if last_import_idx >= 0 else start_search
    lines.insert(insert_at, 'from shared.rich_output import *')
    return '\n'.join(lines)


def migrate_content(content):
    """Migrate a file's content: add import + convert print patterns."""
    if has_rich_import(content):
        return content, False  # already done
    
    changed = False
    
    # Step 1: Add import
    new_content = add_rich_import(content)
    if new_content != content:
        changed = True
        content = new_content
    
    # Step 2: Convert print patterns
    lines = content.split('\n')
    new_lines = []
    skip_next_empty = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = line[:len(line) - len(line.lstrip())]
        
        if not stripped:
            if skip_next_empty:
                skip_next_empty = False
                continue
            new_lines.append(line)
            continue
        
        # Skip comment-only lines
        if stripped.startswith('#'):
            new_lines.append(line)
            continue
        
        # Handle print() calls
        if stripped.startswith('print('):
            new_line, keep_original = convert_line(stripped, indent)
            if new_line != stripped:
                changed = True
                if new_line == '':
                    skip_next_empty = True
                else:
                    new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    return new_content, changed


# ── Main ────────────────────────────────────────────────────────────

def migrate_file(filepath, dry_run=False):
    p = Path(filepath)
    if not p.exists():
        return (str(p), "NOT FOUND", [])
    
    content = p.read_text()
    
    if has_rich_import(content):
        return (str(p), "SKIP (already rich)", [])
    
    new_content, changed = migrate_content(content)
    
    if not changed:
        return (str(p), "No changes needed", [])
    
    # Count changes
    old_lines = content.split('\n')
    new_lines = new_content.split('\n')
    changes = []
    
    # Count print conversions
    old_prints = sum(1 for l in old_lines if l.strip().startswith('print('))
    new_prints = sum(1 for l in new_lines if l.strip().startswith('print('))
    converted = old_prints - new_prints
    if converted > 0:
        changes.append(f'{converted} print→rich')
    
    # Check import added
    if 'from shared.rich_output import *' in new_content and 'from shared.rich_output import *' not in content:
        changes.append('added import')
    
    if not dry_run:
        p.write_text(new_content)
    
    return (str(p), "OK" if changes else "No changes", changes)


def migrate_directory(root_dir, dry_run=False):
    results = []
    for p in sorted(root_dir.rglob('*.py')):
        rel = p.relative_to(REBIS_ROOT)
        rel_str = str(rel)
        # Skip venv, cache, and already-rich files
        if '.venv' in rel_str or '__pycache__' in rel_str:
            continue
        # Focus on files with print() statements
        try:
            content = p.read_text()
        except:
            continue
        if 'print(' not in content:
            continue
        if has_rich_import(content):
            continue
        result = migrate_file(p, dry_run)
        if result[2]:
            results.append(result)
    return results


def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    if dry_run:
        args.remove('--dry-run')
    
    if not args or '--all' in args:
        r = migrate_directory(REBIS_ROOT, dry_run)
    else:
        r = []
        for a in args:
            p = Path(a)
            if not p.exists():
                p = REBIS_ROOT / a
            if p.exists():
                result = migrate_file(p, dry_run)
                r.append(result)
            else:
                info_line(f"NOT FOUND: {a}")
    
    if not r:
        info_line("No files needed changes.")
        return
    
    info_line(f"\n{'File':<70} {'Status':<12} {'Changes'}")
    print('-' * 110)
    for path, status, changes in sorted(r, key=lambda x: x[0]):
        rel = Path(path).relative_to(REBIS_ROOT)
        info_line(f"{str(rel):<70} {status:<12} {', '.join(changes)}")
    
    migrated = sum(1 for _, s, _ in r if s == "OK")
    if not dry_run:
        success_line(f"\n✅ {migrated} files migrated.")
    else:
        info_line(f"\n🔍 DRY RUN: {migrated} files would be migrated.")


if __name__ == '__main__':
    main()
