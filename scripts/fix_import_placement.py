#!/usr/bin/env python3
import os, re, sys
from shared.rich_output import *
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REBIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_top_level_insert_point(lines):
    """Find where to insert a top-level import."""
    in_docstring = False
    docstring_style = None
    last_top_import = -1
    
    for i, l in enumerate(lines):
        s = l.strip()
        indent = len(l) - len(l.lstrip())
        
        if not in_docstring:
            if s.startswith('"""') or s.startswith("'''"):
                if '"""' in s[3:] or "'''" in s[3:]:
                    continue
                in_docstring = True
                docstring_style = '"""' if s.startswith('"""') else "'''"
                continue
        else:
            if docstring_style in s:
                in_docstring = False
                continue
            continue
        
        if s.startswith(('#!', '# -*-')):
            continue
        
        if indent == 0 and s.startswith(('import ', 'from ')):
            last_top_import = i
            continue
    
    return last_top_import + 1 if last_top_import >= 0 else 1


def fix_file(fp):
    content = open(fp).read()
    lines = content.split('\n')
    
    
    if rich_lines:
        for i in reversed(rich_lines):
            lines.pop(i)
        insert_at = find_top_level_insert_point(lines)
        open(fp, 'w').write('\n'.join(lines))
        return True
    return False


def main():
    os.chdir(REBIS)
    fixed = 0
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or '__pycache__' in root:
            continue
        for fn in files:
            if not fn.endswith('.py'):
                continue
            fp = os.path.join(root, fn)
            try:
                content = open(fp).read()
                if fix_file(fp):
                    fixed += 1
            except:
                pass
    info_line(f"Fixed {fixed} files")


if __name__ == '__main__':
    main()
