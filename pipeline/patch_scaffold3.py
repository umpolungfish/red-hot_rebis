"""Patch 3: Attach fragment_smiles to child nodes in deep_retrosynthesis."""

with open('/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py', 'r') as f:
    lines = f.readlines()

# Find the child_b best-cut line
for i, line in enumerate(lines):
    if i > 435 and i < 450:
        if 'route["child_b"] = self.deep_retrosynthesis(' in line and 'fg_hint=cut["fg2"])' in line:
            # Insert fragment_smiles hook after this line
            hook = '''\n            # ── Pass 2: Attach actual fragment SMILES from scaffold map ──
            # Ensures CDXML shows actual molecular fragments, not generic reagents
            frag_a, frag_b = self._get_fragment_smiles_for_cut(
                cut["fg1"], cut["fg2"], cut["bond"])
            if frag_a:
                route["child_a"].fragment_smiles = frag_a
            if frag_b:
                route["child_b"].fragment_smiles = frag_b
'''
            # Insert the lines one by one
            for t_line in reversed(hook.split('\n')):
                lines.insert(i+1, t_line + '\n')
            print(f"Applied: Inserted fragment_smiles hook at line {i+1}")
            break

# Also add fragment_smiles to RetrosyntheticNode.__init__
for i, line in enumerate(lines):
    if 'self.reagent_match: Optional[Dict] = None' in line and i > 10:
        lines.insert(i+1, '        self.fragment_smiles: Optional[str] = ""  # actual molecular fragment from scaffold cut\n')
        print(f"Applied: Added fragment_smiles field to RetrosyntheticNode at line {i+1}")
        break

# Also add fragment_smiles to _tree_to_dict
for i, line in enumerate(lines):
    if 'if node.reagent_match:' in line:
        lines.insert(i, '        if node.fragment_smiles:\n            result["fragment_smiles"] = node.fragment_smiles\n')
        print(f"Applied: Added fragment_smiles to _tree_to_dict at line {i}")
        break

with open('/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py', 'w') as f:
    f.writelines(lines)

print("Patch 3 complete")
