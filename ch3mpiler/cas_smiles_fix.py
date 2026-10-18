#!/usr/bin/env python3
"""Repair historical CAS SMILES propagation; validate both sources before writing.

Importing this module performs no edits. --check reports required changes.
The current compiler and pipeline should report no changes.
"""
import argparse
import ast
from pathlib import Path

old_parse = '        try:\n            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/JSON"\n            req = urllib.request.Request(url, headers={"User-Agent": "ch3mpiler/1.0"})\n            resp = urllib.request.urlopen(req, timeout=10)\n            data = json.loads(resp.read())\n            props = {}\n            if "PC_Compounds" in data and data["PC_Compounds"]:\n                for prop in data["PC_Compounds"][0].get("props", []):\n                    urn = prop.get("urn", {}).get("label", "")\n                    val = prop.get("value", {}).get("sval", "")\n                    props[urn] = val\n            name = props.get("IUPAC Name", props.get("Molecular Formula", cas))\n            formula = props.get("Molecular Formula", "")\n            entry = {"cas": cas, "name": name, "formula": formula, "source": "pubchem", "type_hint": ""}\n            self._cache[cas] = entry\n            self._save_cache()\n            return entry'

new_parse = '        try:\n            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/property/CanonicalSMILES,MolecularFormula,IUPACName/JSON"\n            req = urllib.request.Request(url, headers={"User-Agent": "ch3mpiler/1.0"})\n            resp = urllib.request.urlopen(req, timeout=10)\n            data = json.loads(resp.read())\n            props = data.get("PropertyTable", {}).get("Properties", [{}])[0]\n            name = props.get("IUPACName", props.get("MolecularFormula", cas))\n            formula = props.get("MolecularFormula", "")\n            smiles = props.get("CanonicalSMILES", "")\n            entry = {"cas": cas, "name": name, "formula": formula,\n                     "smiles": smiles, "source": "pubchem", "type_hint": ""}\n            self._cache[cas] = entry\n            self._save_cache()\n            return entry'

def patched_sources(compiler, pipeline):
    if compiler.count(old_parse) == 1:
        compiler = compiler.replace(old_parse, new_parse)
    else:
        tree = ast.parse(compiler)
        resolver = next(node for node in tree.body
                        if isinstance(node, ast.ClassDef) and node.name == 'CASResolver')
        method = next(node for node in resolver.body
                      if isinstance(node, ast.FunctionDef) and node.name == 'resolve')
        segment = ast.get_source_segment(compiler, method)
        if not all(token in segment for token in ('PropertyTable', 'smiles', 'CanonicalSMILES')):
            raise ValueError('Unrecognized CASResolver.resolve implementation')
    tree = ast.parse(pipeline)
    blocks = [node for node in ast.walk(tree)
              if isinstance(node, ast.If) and ast.unparse(node.test) == 'args.cas']
    changes = []
    assignments = 0
    for block in blocks:
        for node in ast.walk(ast.Module(body=block.body, type_ignores=[])):
            if not isinstance(node, ast.Assign):
                continue
            if not any(ast.unparse(target) == 'pipeline._target_smiles' for target in node.targets):
                continue
            assignments += 1
            expression = ast.unparse(node.value)
            if expression == "args.smiles or ''":
                changes.append(node)
            elif 'smiles' not in expression or 'cas_info' not in expression:
                raise ValueError('Unrecognized CAS target SMILES assignment')
    if not blocks or not assignments:
        raise ValueError('No CAS target SMILES assignment found')
    lines = pipeline.splitlines(keepends=True)
    for node in sorted(changes, key=lambda n: n.lineno, reverse=True):
        indent = ' ' * node.col_offset
        lines[node.lineno - 1:node.end_lineno] = [
            indent + 'pipeline._target_smiles = info.get("cas_info", {}).get("smiles", "") or args.smiles or ""\n']
    pipeline = ''.join(lines)
    ast.parse(compiler)
    ast.parse(pipeline)
    return compiler, pipeline


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    paths = [root / 'ch3mpiler/compiler.py', root / 'pipeline/reaction_pipeline.py']
    original = tuple(path.read_text() for path in paths)
    revised = patched_sources(*original)
    pending = [path for path, old, new in zip(paths, original, revised) if old != new]
    for path in pending:
        print(f"Repair required: {path}")
    if args.check:
        return 1 if pending else 0
    for path, old, new in zip(paths, original, revised):
        if old != new:
            backup = path.with_suffix(path.suffix + '.before-cas-repair')
            if not backup.exists():
                backup.write_text(old)
            path.write_text(new)
    print('CAS compiler and pipeline repair verified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
