#!/usr/bin/env python3
"""Fix files where rich_output import was placed between multi-line import parens."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def fix_file(fp):
    content = open(fp).read()
    lines = content.split('\n')
    modified = False
    
    # Pattern: a line ending with `(` (start of multi-line import),
    # followed by `from shared.rich_output import *`,
    # followed by indented continuation lines.
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if this line is `from ... import (`
        if re.match(r'^from\s+\S+\s+import\s+\($', line.strip()):
            # Check if next line is the rich import
            if i + 1 < len(lines) and 'rich_output' in lines[i+1] and not lines[i+1].startswith((' ', '\t')):
                # Move the rich import ABOVE the multi-line import
                rich_line = lines.pop(i + 1)
                lines.insert(i, rich_line)
                modified = True
                i += 2  # skip past both
                continue
        i += 1
    
    if modified:
        open(fp, 'w').write('\n'.join(lines))
        return True
    return False

def main():
    fixed = 0
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or '__pycache__' in root:
            continue
        for fn in files:
            if not fn.endswith('.py'):
                continue
            fp = os.path.join(root, fn)
            if fix_file(fp):
                success_line(f"  ✅ {fp[len('./'):]}")
                fixed += 1
    info_line(f"\nFixed {fixed} files")

if __name__ == '__main__':
    main()
