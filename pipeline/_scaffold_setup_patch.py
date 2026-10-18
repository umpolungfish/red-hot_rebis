"""Validated historical scaffold setup and CLI repairs."""
import ast
from ._scaffold_patch import repair_source as repair_fragments

METHODS = '\n    def resolve_and_parse_scaffold(self, target: str, smiles: str = "") -> bool:\n        """Pass 1: Resolve target to SMILES and parse scaffold decomposition.\n\n        This builds the scaffold map that maps FG-pair cuts to actual\n        fragment SMILES from the target molecule. Non-terminal nodes in\n        the retrosynthetic tree will carry fragment_smiles from this map\n        for CDXML output.\n\n        Args:\n            target: Molecule name\n            smiles: Optional SMILES string (if already known)\n\n        Returns:\n            True if scaffold was successfully parsed\n        """\n        if not smiles:\n            # Try to resolve name to SMILES via PubChem\n            smiles = resolve_name_to_smiles(target)\n\n        if not smiles:\n            info_line(f"  [scaffold] WARNING: Could not resolve \'{target}\' to SMILES. "\nf"Using FG-only decomposition (no fragment structures).")\n            return False\n\n        try:\n            parser = ScaffoldParser()\n            parser.load(smiles, name=target)\n            decomp = parser.get_full_scaffold_decomposition()\n\n            # Store scaffold map: FG-pair tuples -> list of bond cuts with fragment SMILES\n            self._scaffold_map = {}\n            for pair_str, bonds in decomp.get("fg_pair_bonds", {}).items():\n                # pair_str is "(\'fg1\', \'fg2\')" — parse it back\n                import ast\n\n                pair = ast.literal_eval(pair_str)\n                pair_key = tuple(sorted(pair))\n                if pair_key not in self._scaffold_map:\n                    self._scaffold_map[pair_key] = []\n                self._scaffold_map[pair_key].extend(bonds)\n\n            self._target_smiles = smiles\n            n_bonds = sum(len(v) for v in self._scaffold_map.values())\n\n            info_line(f"  [scaffold] Pass 1: Parsed {target} [{smiles}]")\n            info_line(f"  [scaffold]   {decomp[\'num_atoms\']} atoms, {decomp[\'num_bonds\']} bonds, "\nf"{len(decomp[\'fgs\'])} FGs: {\', \'.join(decomp[\'fgs\'])}")\n            info_line(f"  [scaffold]   {n_bonds} strategic disconnections across "\nf"{len(self._scaffold_map)} FG-pair types")\n            for pair, bonds in sorted(self._scaffold_map.items()):\n                info_line(f"  [scaffold]     {pair[0]} + {pair[1]}: {len(bonds)} bond(s)")\n            return True\n\n        except Exception as e:\n            info_line(f"  [scaffold] ERROR parsing scaffold: {e}")\n            return False\n\n    def _get_fragment_smiles_for_cut(self, fg1: str, fg2: str, bond_type: str) -> tuple:\n        """Pass 2: Look up fragment SMILES for a specific FG-pair cut.\n\n        If the scaffold map has this FG pair, returns the fragment SMILES\n        for both sides of the cut. Otherwise returns (None, None).\n\n        The returned tuple is (fragment_smiles_a, fragment_smiles_b).\n        """\n        pair = tuple(sorted([fg1, fg2]))\n        bonds = self._scaffold_map.get(pair, [])\n        if not bonds:\n            return None, None\n\n        # Use the first matching bond cut (prefer strategic ones)\n        bond = bonds[0]\n        return bond.get("fragment_smiles_a"), bond.get("fragment_smiles_b")\n\n'


def _context(source):
    tree = ast.parse(source)
    cls = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ReactionPipeline'), None)
    if cls is None:
        raise ValueError('No ReactionPipeline class')
    return tree, cls, {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}


def _apply(source, edits):
    lines = source.splitlines(keepends=True)
    grouped = {}
    for index, text in edits:
        grouped[index] = grouped.get(index, '') + text
    for index in sorted(grouped, reverse=True):
        lines.insert(index, grouped[index])
    revised = ''.join(lines)
    ast.parse(revised)
    return revised


def _sets(node, owner, field):
    targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
    return any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
               and t.value.id == owner and t.attr == field for t in targets)


def repair_setup(source):
    tree, cls, methods = _context(source)
    init = methods.get('__init__')
    if init is None:
        raise ValueError('No pipeline initializer')
    edits = []
    imported = {a.asname or a.name for n in tree.body if isinstance(n, ast.ImportFrom)
                and n.module == 'ch3mpiler.scaffold_parser' for a in n.names}
    missing = {'ScaffoldParser', 'resolve_name_to_smiles'} - imported
    if missing:
        # Insert after the module docstring and any future imports.
        prefix = 1 if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str) else 0
        while prefix < len(tree.body) and isinstance(tree.body[prefix], ast.ImportFrom) and tree.body[prefix].module == '__future__':
            prefix += 1
        index = tree.body[prefix-1].end_lineno if prefix else 0
        edits.append((index, 'from ch3mpiler.scaffold_parser import ' + ', '.join(sorted(missing)) + '\n'))
    addition = ''
    for field, value in [('_scaffold_map', '{}'), ('_target_smiles', '""')]:
        if not any(_sets(n, 'self', field) for n in ast.walk(init)):
            addition += ' ' * (init.col_offset + 4) + 'self.' + field + ' = ' + value + '\n'
    if addition:
        edits.append((init.end_lineno, addition))
    extra = ''
    template = "class _Template:\n" + METHODS
    for method in ast.parse(template).body[0].body:
        if method.name not in methods:
            extra += '\n' + '\n'.join('    ' + line for line in ast.get_source_segment(template, method).splitlines()) + '\n'
    if extra:
        edits.append((cls.end_lineno, extra))
    return _apply(source, edits)


def repair_dispatch(source):
    tree, cls, methods = _context(source)
    if not {'resolve_and_parse_scaffold', '_get_fragment_smiles_for_cut'} <= methods.keys():
        raise ValueError('Apply scaffold setup before dispatch repair')
    deep = methods.get('deep_retrosynthesis')
    if deep is None:
        raise ValueError('No recursive method')
    edits = []
    if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'resolve_and_parse_scaffold' for n in ast.walk(deep)):
        anchor = next((n for n in deep.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'RetrosyntheticNode'), None)
        if anchor is None:
            raise ValueError('No root node insertion anchor')
        pad = ' ' * anchor.col_offset
        hook = ['if depth == 0 and not fg_hint:',
                '    self.resolve_and_parse_scaffold(target, self._target_smiles or "")']
        edits.append((anchor.lineno-1, ''.join(pad + s + '\n' for s in hook)))
    main = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main'), None)
    if main is None:
        raise ValueError('No CLI main function')
    flags = [n for n in ast.walk(main) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == 'add_argument']
    if not any(any(isinstance(a, ast.Constant) and a.value == '--smiles' for a in n.value.args) for n in flags):
        anchor = next((n for n in flags if any(isinstance(a, ast.Constant) and a.value == '--target' for a in n.value.args)), None)
        if anchor is None:
            raise ValueError('No CLI target option')
        edits.append((anchor.end_lineno, ' ' * anchor.col_offset + 'parser.add_argument("--smiles", help="Target SMILES")\n'))
    for branch in ast.walk(main):
        if not isinstance(branch, ast.If) or not isinstance(branch.test, ast.Attribute) or not isinstance(branch.test.value, ast.Name) or branch.test.value.id != 'args' or branch.test.attr not in ('target', 'cas'):
            continue
        for statement in ast.walk(branch):
            if not isinstance(statement, ast.Assign) or not isinstance(statement.value, ast.Call) or not isinstance(statement.value.func, ast.Attribute) or statement.value.func.attr != 'deep_retrosynthesis':
                continue
            if any(_sets(n, 'pipeline', '_target_smiles') and n.lineno < statement.lineno for n in ast.walk(branch)):
                continue
            edits.append((statement.lineno-1, ' ' * statement.col_offset + 'pipeline._target_smiles = args.smiles or ""\n'))
    revised = _apply(source, edits)
    return repair_fragments(revised)
