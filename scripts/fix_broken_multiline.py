#!/usr/bin/env python3
"""Fix broken multi-line f-strings from migrate_rich.py."""

import re

FILES_FIXES = {
    'therapeutics/frobenius_chemotherapeutic.py': [
        (r'info_line\(f"  t=\{self\.time:5\.1f\} \| "\)',
         'info_line(f"  t={self.time:5.1f} | "'),
    ],
    'materials/frobenius_metamaterial.py': [
        (r'info_line\(f"  \{status\} \{cycle:3d\}  \{max_load:8\.2f\}%  \{frob_before:12\.4f\}  "\)',
         'info_line(f"  {status} {cycle:3d}  {max_load:8.2f}%  {frob_before:12.4f}  "'),
    ],
    'materials/ig_material_forge.py': [
        (r'info_line\(f"  \{name:40s\} \{design\.ouroboricity_tier:6s\} Frob=\{design\.frobenius_score:\.2f\}  "\)',
         'info_line(f"  {name:40s} {design.ouroboricity_tier:6s} Frob={design.frobenius_score:.2f}  "'),
    ],
}

def fix_file(fp, fixes):
    content = open(fp).read()
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    open(fp, 'w').write(content)
    print(f"Fixed: {fp}")

for fp, fixes in FILES_FIXES.items():
    fix_file(fp, fixes)
