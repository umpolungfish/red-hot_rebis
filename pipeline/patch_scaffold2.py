
from shared.rich_output import *
"""Patch 2: Modify deep_retrosynthesis() and main() for scaffold awareness."""

with open('/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')

patches = []

# === Patch 4: At the start of deep_retrosynthesis, run scaffold parse at root ===
# Find "node = RetrosyntheticNode(target, depth)" — the first line of the method body
for i, line in enumerate(lines):
    if 'node = RetrosyntheticNode(target, depth)' in line:
        # Insert after the docstring/args, before the terminal checks
        # We want to insert right before the "max depth" check
        scaffold_hook = '''\n        # ── Pass 1: Scaffold parsing (only at root, depth=0) ──
        if depth == 0 and not fg_hint:
            # First time: resolve target to SMILES and parse scaffold
            if hasattr(self, '_target_smiles') and self._target_smiles:
                # Already resolved externally (from --smiles flag)
                self.resolve_and_parse_scaffold(target, self._target_smiles)
            else:
                # Auto-resolve from name
                self.resolve_and_parse_scaffold(target)
        \n'''
        patches.append((i, 0, scaffold_hook))
        print(f"Patch 4: Insert scaffold hook at line {i}")
        break

# === Patch 5: Add fragment_smiles to child nodes in the best cut ===
# Look for the pattern where child_a and child_b are created from best cut
for i, line in enumerate(lines):
    if 'route["child_a"] = self.deep_retrosynthesis(' in line and 'depth + 1, fg_hint=cut["fg1"])' in line:
        # Before this line, add fragment_smiles lookup
        fragment_hook = '''\n            # ── Pass 2: Attach actual fragment SMILES from scaffold map ──
            # This ensures CDXML output shows the real molecular fragment,
            # not a generic reagent match.
            frag_a, frag_b = self._get_fragment_smiles_for_cut(
                cut["fg1"], cut["fg2"], cut["bond"])
            if frag_a:
                route["child_a"].fragment_smiles = frag_a
            if frag_b:
                route["child_b"].fragment_smiles = frag_b
            \n'''
        # Insert AFTER the two child_a/child_b lines (find child_b line too)
        for j in range(i, min(i+5, len(lines))):
            if 'route["child_b"] = self.deep_retrosynthesis(' in lines[j] and 'fg_hint=cut["fg2"])' in lines[j]:
                patches.append((j+1, 0, fragment_hook))
                print(f"Patch 5: Insert fragment_smiles hook after line {j}")
                break
        break

# === Patch 6: Add --smiles flag to main() ===
for i, line in enumerate(lines):
    if 'parser.add_argument("--target"' in line:
        patches.append((i+1, 0, '    parser.add_argument("--smiles", help="Target SMILES (bypasses name resolution)")\n'))
        print(f"Patch 6: Add --smiles argument at line {i+1}")
        break

# === Patch 7: In --target processing, resolve SMILES before deep_retrosynthesis ===
# Look for the --target block in main()
# Find: "if args.target:"
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == 'if args.target:' and i > 500:
        # Find the deep_retrosynthesis call inside
        for j in range(i, min(i+30, len(lines))):
            if 'tree = pipeline.deep_retrosynthesis(args.target)' in lines[j]:
                # Insert SMILES resolution before this
                smiles_block = '''\n            # Resolve SMILES (Pass 1 scaffold parsing) before retrosynthesis
            pipeline._target_smiles = args.smiles or ""
            \n'''
                patches.append((j, 0, smiles_block))
                print(f"Patch 7: Insert SMILES resolution at line {j}")
                break
        break

# === Patch 8: Also for --cas path ===
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == "if args.cas:" and i > 400:
        for j in range(i, min(i+30, len(lines))):
            if 'tree = pipeline.deep_retrosynthesis(name)' in lines[j]:
                smiles_block = '''\n            pipeline._target_smiles = args.smiles or ""
            \n'''
                patches.append((j, 0, smiles_block))
                print(f"Patch 8: Insert SMILES resolution (CAS path) at line {j}")
                break
        break

# === Apply patches in reverse order ===
patches.sort(key=lambda x: x[0], reverse=True)

for line_no, count, text in patches:
    for t in text.split('\n'):
        lines.insert(line_no, t)

result = '\n'.join(lines)
with open('/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py', 'w') as f:
    f.write(result)

print(f"\nApplied {len(patches)} patches successfully")
