#!/usr/bin/env python3
"""
migrate_rich.py — Auto-migrate Python files to use rich formatting.
Adds import and replaces common print patterns with rich equivalents.

Usage:
    python3 scripts/migrate_rich.py path/to/file.py [path/to/file2.py ...]
    python3 scripts/migrate_rich.py --all     # All files with print() in red-hot_rebis
    python3 scripts/migrate_rich.py --dry-run file.py  # Preview changes only
"""

import re
import subprocess
import sys
from pathlib import Path

# Don't import from shared.rich_output here — this script modifies
# other files, not itself.

REBIS_ROOT = Path(__file__).parent.parent.resolve()


def has_rich_import(content):
    return bool(re.search(
        r'(from\s+(ch3mpiler|shared)\.rich_output\s+import|'
        r'import\s+(ch3mpiler|shared)\.rich_output)',
        content
    ))


def add_rich_import(content):
    """Add 'from shared.rich_output import *' after existing imports."""
    lines = content.split('\n')
    import_line = "from shared.rich_output import *"

    # Check if it already has rich import
    if has_rich_import(content):
        return content

    # Find last import line position
    last_import_idx = -1
    in_multi_import = False
    for i, line in enumerate(lines):
        s = line.strip()
        # Track multi-line imports like from x import ( ... )
        if s.startswith('from ') or s.startswith('import '):
            if '(' in s and ')' not in s:
                in_multi_import = True
            elif ')' in s and '(' not in s:
                in_multi_import = False
                last_import_idx = i
            else:
                last_import_idx = i
        elif in_multi_import:
            if ')' in s:
                in_multi_import = False
                last_import_idx = i

    if last_import_idx >= 0:
        insert_at = last_import_idx + 1
    else:
        # No imports — check for docstring
        insert_at = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('"""', "'''", '"""', "'''")):
                insert_at = i + 1

    # Don't insert if it would be inside a docstring
    if insert_at > 0 and insert_at < len(lines):
        prev_line = lines[insert_at - 1].strip()
        if prev_line.endswith(('"""', "'''")) and not prev_line.startswith(('"""', "'''")):
            insert_at = insert_at + 1

    lines.insert(insert_at, import_line)
    return '\n'.join(lines)


def _strip_prefix(s):
    """Remove common print prefixes like '  ' from a line."""
    return s.lstrip()


def _is_print_stdout(line):
    """Check if line is print() or sys.stdout.write() call."""
    stripped = line.strip()
    if stripped.startswith('print('):
        return True
    if stripped.startswith('sys.stdout.write('):
        return True
    return False


def _extract_print_arg(line):
    """Extract the argument of a print(...) call."""
    stripped = line.strip()
    if not stripped.startswith('print('):
        return None
    inner = stripped[6:]
    if inner.endswith(')'):
        inner = inner[:-1]
    return inner


def migrate_file(filepath, dry_run=False):
    """Migrate a single file to use rich formatting."""
    p = Path(filepath)
    if not p.exists():
        return (str(p), "NOT FOUND", [])

    content = p.read_text()
    if has_rich_import(content):
        return (str(p), "SKIP (already has rich)", [])

    changes = []

    # 1. Add import
    new_content = add_rich_import(content)
    if new_content != content:
        content = new_content
        changes.append("added import")

    # 2. Replace print patterns
    lines = content.split('\n')
    new_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = line[:len(line) - len(line.lstrip())]

        if not stripped:
            new_lines.append(line)
            continue

        # Box-drawing headers
        if (stripped.startswith('print("╔') or stripped.startswith("print('╔") or
            stripped.startswith('print("═') or stripped.startswith("print('═") or
            stripped.startswith('print("╚') or stripped.startswith("print('╚")):
            new_lines.append(f'{indent}separator()')
            if 'header' not in changes:
                changes.append('header → separator')
            continue

        if (stripped.startswith('print("║') or stripped.startswith("print('║")):
            # Skip box side lines
            new_lines.append('')
            if 'side' not in changes:
                changes.append('side skipped')
            continue

        # Separator lines
        if stripped.startswith('print("=') and stripped.count('=') > 5:
            new_lines.append(f'{indent}separator()')
            if 'sep' not in changes:
                changes.append('"=" → separator()')
            continue

        if stripped.startswith("print('=") and stripped.count('=') > 5:
            new_lines.append(f'{indent}separator()')
            continue

        if stripped.startswith('print("─') and stripped.count('─') > 3:
            new_lines.append(f'{indent}separator()')
            continue

        # Error lines
        if re.search(r'print\(.*(Error|ERROR|✗|FAIL)', stripped):
            arg = _extract_print_arg(stripped)
            if arg:
                new_lines.append(f'{indent}error_line({arg})')
                if 'error' not in changes:
                    changes.append('print → error_line')
                continue

        # Success lines
        if re.search(r'print\(.*(✅|✓|Success|Done|success)', stripped):
            arg = _extract_print_arg(stripped)
            if arg:
                new_lines.append(f'{indent}success_line({arg})')
                if 'success' not in changes:
                    changes.append('print → success_line')
                continue

        # Warning lines
        if re.search(r'print\(.*(Warning|⚠|warn)', stripped):
            arg = _extract_print_arg(stripped)
            if arg:
                new_lines.append(f'{indent}warning_line({arg})')
                if 'warn' not in changes:
                    changes.append('print → warning_line')
                continue

        # JSON dump lines — keep as print
        if 'json.dumps' in stripped or 'json.loads' in stripped:
            new_lines.append(line)
            continue

        # Plain print() calls — convert to info_line
        if _is_print_stdout(stripped):
            arg = _extract_print_arg(stripped)
            if arg:
                # Check if it's a simple string literal (no f-string, no complex expr)
                if (arg.startswith('"') and arg.endswith('"')) or \
                   (arg.startswith("'") and arg.endswith("'")):
                    new_lines.append(f'{indent}info_line({arg})')
                    if 'info' not in changes:
                        changes.append('print → info_line')
                elif arg.startswith('f"') or arg.startswith("f'"):
                    new_lines.append(f'{indent}info_line({arg})')
                    if 'info-f' not in changes:
                        changes.append('print → info_line(f"...")')
                else:
                    # Variable print — keep as print
                    new_lines.append(line)
                continue

        new_lines.append(line)

    new_content = '\n'.join(new_lines)

    if not dry_run and new_content != content:
        p.write_text(new_content)

    return (str(p), "OK" if changes else "No changes", changes)


def migrate_directory(root_dir, dry_run=False):
    """Migrate all .py files in directory tree."""
    results = []
    for p in sorted(root_dir.rglob('*.py')):
        # Skip venv and cache
        rel = p.relative_to(REBIS_ROOT)
        if '.venv' in str(rel) or '__pycache__' in str(rel):
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
                # Try relative to REBIS_ROOT
                p = REBIS_ROOT / a
            if p.exists():
                result = migrate_file(p, dry_run)
                r.append(result)
            else:
                info_line(f"NOT FOUND: {a}")

    if not r:
        info_line("No files needed changes.")
        return

    info_line(f"\n{'File':<60} {'Status':<15} {'Changes'}")
    print('-' * 95)
    for path, status, changes in sorted(r, key=lambda x: x[0]):
        rel = Path(path).relative_to(REBIS_ROOT)
        info_line(f"{str(rel):<60} {status:<15} {', '.join(changes)}")

    migrated = sum(1 for _, s, _ in r if s == "OK" and _)
    if not dry_run:
        success_line(f"\n✅ {migrated} files migrated.")


if __name__ == '__main__':
    main()
