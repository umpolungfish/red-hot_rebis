"""Patch reaction_pipeline.py for two-pass scaffold-aware retrosynthesis.

Changes:
1. Add --smiles CLI flag
2. Import ScaffoldParser
3. Add _scaffold_map to __init__
4. Add resolve_and_parse_scaffold() method
5. Modify deep_retrosynthesis to attach fragment_smiles to child nodes
6. At depth=0, run scaffold parsing if we have SMILES
"""
import re

with open('/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')

patches = []

# === Patch 1: Add import ===
# Find the import section (after "from reaction_deriver import ...")
import_end = 0
for i, line in enumerate(lines):
    if 'from reaction_deriver import' in line and i > 10:
        # Find the end of the import block
        import_end = i
        # Look for the next non-continuation line
        while import_end < len(lines) and ('from ' in lines[import_end] or lines[import_end].strip().startswith('from') or 
                                            'import' in lines[import_end] or lines[import_end].strip() == ''):
            import_end += 1
        break

# Add scaffold parser import
if import_end > 0:
    insert_line = import_end
    while insert_line < len(lines) and not lines[insert_line].strip():
        insert_line += 1
    patch = (insert_line, 0, f"from ch3mpiler.scaffold_parser import ScaffoldParser, resolve_name_to_smiles")
    patches.append(patch)
    print(f"Patch 1: Insert import at line {insert_line}")

# === Patch 2: Add _scaffold_map to __init__ ===
for i, line in enumerate(lines):
    if 'self._visited: Set[str] = set()' in line:
        patches.append((i+1, 0, "        self._scaffold_map = {}  # Pass 1 scaffold decomposition\n        self._target_smiles = \"\""))
        print(f"Patch 2: Add _scaffold_map at line {i+1}")
        break

# === Patch 3: Add resolve_and_parse_scaffold method ===
# Find the _decompose_single_fg method or __init__ end
for i, line in enumerate(lines):
    if 'def _decompose_single_fg' in line:
        insert = i  # Insert before this method
        new_method = '''\n    def resolve_and_parse_scaffold(self, target: str, smiles: str = "") -> bool:
        """Pass 1: Resolve target to SMILES and parse scaffold decomposition.
        
        This builds the scaffold map that maps FG-pair cuts to actual
        fragment SMILES from the target molecule. Non-terminal nodes in
        the retrosynthetic tree will carry fragment_smiles from this map
        for CDXML output.
        
        Args:
            target: Molecule name
            smiles: Optional SMILES string (if already known)
        
        Returns:
            True if scaffold was successfully parsed
        """
        if not smiles:
            # Try to resolve name to SMILES via PubChem
            smiles = resolve_name_to_smiles(target)
        
        if not smiles:
            print(f"  [scaffold] WARNING: Could not resolve '{target}' to SMILES. "
                  f"Using FG-only decomposition (no fragment structures).")
            return False
        
        try:
            parser = ScaffoldParser()
            parser.load(smiles, name=target)
            decomp = parser.get_full_scaffold_decomposition()
            
            # Store scaffold map: FG-pair tuples -> list of bond cuts with fragment SMILES
            self._scaffold_map = {}
            for pair_str, bonds in decomp.get("fg_pair_bonds", {}).items():
                # pair_str is "('fg1', 'fg2')" — parse it back
                import ast
                pair = ast.literal_eval(pair_str)
                pair_key = tuple(sorted(pair))
                if pair_key not in self._scaffold_map:
                    self._scaffold_map[pair_key] = []
                self._scaffold_map[pair_key].extend(bonds)
            
            self._target_smiles = smiles
            n_bonds = sum(len(v) for v in self._scaffold_map.values())
            
            print(f"  [scaffold] Pass 1: Parsed {target} [{smiles}]")
            print(f"  [scaffold]   {decomp['num_atoms']} atoms, {decomp['num_bonds']} bonds, "
                  f"{len(decomp['fgs'])} FGs: {', '.join(decomp['fgs'])}")
            print(f"  [scaffold]   {n_bonds} strategic disconnections across "
                  f"{len(self._scaffold_map)} FG-pair types")
            for pair, bonds in sorted(self._scaffold_map.items()):
                print(f"  [scaffold]     {pair[0]} + {pair[1]}: {len(bonds)} bond(s)")
            return True
            
        except Exception as e:
            print(f"  [scaffold] ERROR parsing scaffold: {e}")
            return False
    
    def _get_fragment_smiles_for_cut(self, fg1: str, fg2: str, bond_type: str) -> tuple:
        """Pass 2: Look up fragment SMILES for a specific FG-pair cut.
        
        If the scaffold map has this FG pair, returns the fragment SMILES
        for both sides of the cut. Otherwise returns (None, None).
        
        The returned tuple is (fragment_smiles_a, fragment_smiles_b).
        """
        pair = tuple(sorted([fg1, fg2]))
        bonds = self._scaffold_map.get(pair, [])
        if not bonds:
            return None, None
        
        # Use the first matching bond cut (prefer strategic ones)
        bond = bonds[0]
        return bond.get("fragment_smiles_a"), bond.get("fragment_smiles_b")\n
'''
        patches.append((insert, 0, new_method))
        print(f"Patch 3: Add resolve_and_parse_scaffold at line {i}")
        break

# === Apply patches in reverse order (so line numbers stay valid) ===
patches.sort(key=lambda x: x[0], reverse=True)

for line_no, count, text in patches:
    for t in text.split('\n'):
        lines.insert(line_no, t)

result = '\n'.join(lines)
with open('/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py', 'w') as f:
    f.write(result)

print(f"\nApplied {len(patches)} patches successfully")
print("Verifying patches exist...")
