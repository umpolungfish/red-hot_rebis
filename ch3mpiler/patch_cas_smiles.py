
from shared.rich_output import *
#!/usr/bin/env python3
"""Targeted patch: only fix the --cas SMILES propagation in the pipeline."""
PIPELINE_PATH = "/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py"

with open(PIPELINE_PATH) as f:
    lines = f.readlines()

# The line we need to change is inside `if args.cas:` → `else:` → 
#   pipeline._target_smiles = args.smiles or ""
# identified by being 12 spaces indent, preceded by `if args.cas:` and `else:`
target_old = '            pipeline._target_smiles = args.smiles or ""'
target_new = '            pipeline._target_smiles = info.get("cas_info", {}).get("smiles", "") or args.smiles or ""'

count = 0
for i, line in enumerate(lines):
    if line.rstrip() == target_old and i > 0:
        # Check if this is inside the `if args.cas:` block
        # Look backwards for `if args.cas:` — unique to that block
        for j in range(i-1, max(0, i-10), -1):
            if 'if args.cas:' in lines[j]:
                lines[i] = line.replace(target_old, target_new)
                count += 1
                break
            if 'if args.' in lines[j]:
                break  # wrong block

assert count == 1, f"Expected exactly 1 replacement in --cas block, got {count}"

with open(PIPELINE_PATH, "w") as f:
    f.writelines(lines)

print(f"[OK] Patched {PIPELINE_PATH}")
info_line(f"  Changed: {target_old}")
info_line(f"  To:      {target_new}")
print()
info_line("Now when --cas is used, pipeline._target_smiles gets:")
info_line("  1. SMILES from CAS resolver (PubChem property endpoint)")
info_line("  2. Falls back to --smiles CLI arg if CAS has no SMILES")
print("  3. Falls back to '' (FG-only decomposition, legacy behavior)")

# Verify
with open(PIPELINE_PATH) as f:
    verifying = f.read()
assert 'info.get("cas_info", {}).get("smiles", "")' in verifying
info_line("[OK] Verified: SMILES propagation from CAS resolver is active")
