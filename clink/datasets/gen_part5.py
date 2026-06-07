#!/usr/bin/env python3
"""PART 5: Fix generate_organism_design_package mkdir issue."""
import os

PY = "/home/mrnob0dy666/red-hot_rebis/clink/datasets/generators.py"

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

print("Fixed mkdir call")
