
from shared.rich_output import *
"""Insert fragment_smiles hook after best-cut child creation."""

with open('/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py', 'r') as f:
    lines = f.readlines()

# Find the line with 'route["child_b"] = self.deep_retrosynthesis(' 
for i, line in enumerate(lines):
    if 'route["child_b"] = self.deep_retrosynthesis(' in line and 'fg_hint=cut["fg2"])' in line:
        # Insert the fragment_smiles hook AFTER this line
        hook_lines = [
            '            # ── Pass 2: Attach actual fragment SMILES from scaffold map ──\n',
            '            # Ensures CDXML output shows real molecular fragments, not generic reagents\n',
            '            frag_a, frag_b = self._get_fragment_smiles_for_cut(\n',
            '                cut["fg1"], cut["fg2"], cut["bond"])\n',
            '            if frag_a:\n',
            '                route["child_a"].fragment_smiles = frag_a\n',
            '            if frag_b:\n',
            '                route["child_b"].fragment_smiles = frag_b\n',
        ]
        for t_line in reversed(hook_lines):
            lines.insert(i+1, t_line)
        success_line(f"Applied: fragment_smiles hook at line {i+1}")
        break

with open('/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py', 'w') as f:
    f.writelines(lines)

info_line("Patch 4 complete")
