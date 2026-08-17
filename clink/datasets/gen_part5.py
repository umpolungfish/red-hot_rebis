#!/usr/bin/env python3
"""PART 5: Fix generate_organism_design_package mkdir issue."""
import os
from shared.rich_output import *


PY = "/home/mrnob0dy666/red-hot_rebis/clink/datasets/generators.py"

# This is a generator script: running it rewrites generators.py. Importing it
# must not, so an import stops here rather than truncating the file that the
# package imports at load time.
if __name__ != "__main__":
    raise ImportError(
        "gen_part5 writes generators.py; run it directly, do not import it")


# Read entire file
with open(PY, 'r') as f:
    content = f.read()

# Fix the mkdir call
old = "            layer_dir.mkdir(exist_ok=True)"
new = "            layer_dir.mkdir(parents=True, exist_ok=True)"
content = content.replace(old, new)

# Also need to handle the ensure_output_dir in DatasetGenerator._ensure_output_dir
old2 = "        self.output_dir.mkdir(parents=True, exist_ok=True)"
# Already has parents=True - good

with open(PY, 'w') as f:
    f.write(content)

info_line("Fixed mkdir call")
