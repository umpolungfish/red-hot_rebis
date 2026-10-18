"""Scoped, validated repair of historical reaction-pipeline fragment hooks."""
import argparse
import ast
from pathlib import Path


def _subscript(node, owner, key):
    return (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
            and node.value.id == owner and isinstance(node.slice, ast.Constant)
            and node.slice.value == key)


def repair_source(source, include_metadata=False):
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    changes = []
    methods = [n for c in tree.body if isinstance(c, ast.ClassDef)
               and c.name == 'ReactionPipeline' for n in c.body
               if isinstance(n, ast.FunctionDef)]
    deep = next((n for n in methods if n.name == 'deep_retrosynthesis'), None)
    if deep is None:
        raise ValueError('No ReactionPipeline.deep_retrosynthesis method')
    children = [n for n in ast.walk(deep) if isinstance(n, ast.Assign)
                and any(_subscript(t, 'route', 'child_b') for t in n.targets)
                and isinstance(n.value, ast.Call)
                and isinstance(n.value.func, ast.Attribute)
                and n.value.func.attr == 'deep_retrosynthesis'
                and any(k.arg == 'fg_hint' and _subscript(k.value, 'cut', 'fg2')
                        for k in n.value.keywords)]
    if len(children) != 1:
        raise ValueError('Expected one best-cut child_b recursion')
    child = children[0]
    uses_argument = any(k.arg == 'fragment_smiles' for k in child.value.keywords)
    carried = {n.attr for n in ast.walk(deep) if isinstance(n, ast.Attribute)
               and isinstance(n.ctx, ast.Store)
               and _subscript(n.value, 'route', 'child_b')}
    if not uses_argument and 'fragment_smiles' not in carried:
        indent = ' ' * child.col_offset
        hook = ['frag_a, frag_b = self._get_fragment_smiles_for_cut(',
                '    cut["fg1"], cut["fg2"], cut["bond"])',
                'if frag_a:', '    route["child_a"].fragment_smiles = frag_a',
                'if frag_b:', '    route["child_b"].fragment_smiles = frag_b']
        changes.append((child.end_lineno, ''.join(indent + s + '\n' for s in hook)))
    if include_metadata:
        node_class = next((n for n in tree.body if isinstance(n, ast.ClassDef)
                           and n.name == 'RetrosyntheticNode'), None)
        init = next((n for n in node_class.body if isinstance(n, ast.FunctionDef)
                     and n.name == '__init__'), None) if node_class else None
        if init is None:
            raise ValueError('No RetrosyntheticNode initializer')
        assignments = [n for n in ast.walk(init) if isinstance(n, (ast.Assign, ast.AnnAssign))]
        def sets_attr(node, name):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            return any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                       and t.value.id == 'self' and t.attr == name for t in targets)
        if not any(sets_attr(n, 'fragment_smiles') for n in assignments):
            anchor = next((n for n in assignments if sets_attr(n, 'reagent_match')), None)
            if anchor is None:
                raise ValueError('No node metadata insertion anchor')
            changes.append((anchor.end_lineno, ' ' * anchor.col_offset + 'self.fragment_smiles = ""\n'))
        serializer = next((n for n in methods if n.name == '_tree_to_dict'), None)
        if serializer is None:
            raise ValueError('No tree serializer')
        if not any(_subscript(n, 'result', 'fragment_smiles') for n in ast.walk(serializer)):
            anchor = next((n for n in ast.walk(serializer) if isinstance(n, ast.If)
                           and isinstance(n.test, ast.Attribute)
                           and isinstance(n.test.value, ast.Name)
                           and n.test.value.id == 'node' and n.test.attr == 'reagent_match'), None)
            if anchor is None:
                raise ValueError('No serializer insertion anchor')
            indent = ' ' * anchor.col_offset
            changes.append((anchor.lineno - 1, indent + 'if node.fragment_smiles:\n' + indent + '    result["fragment_smiles"] = node.fragment_smiles\n'))
    for index, addition in sorted(changes, reverse=True):
        lines.insert(index, addition)
    revised = ''.join(lines)
    ast.parse(revised)
    return revised


def main(argv=None, include_metadata=False, repairer=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=Path(__file__).with_name('reaction_pipeline.py'))
    parser.add_argument('--check', action='store_true', help='Report required repairs without writing')
    args = parser.parse_args(argv)
    try:
        source = args.target.read_text(encoding='utf-8')
        revised = repairer(source) if repairer else repair_source(source, include_metadata)
        if revised == source:
            print('Fragment repair already present.')
            return 0
        if args.check:
            print(f'Repair required: {args.target}')
            return 1
        backup = args.target.with_suffix(args.target.suffix + '.before-fragment-repair')
        if not backup.exists():
            backup.write_text(source, encoding='utf-8')
        args.target.write_text(revised, encoding='utf-8')
        print(f'Repaired: {args.target}')
        return 0
    except (OSError, ValueError, SyntaxError) as exc:
        print(f'Repair failed: {exc}')
        return 1
