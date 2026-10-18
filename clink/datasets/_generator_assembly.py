"""Validate and write historical dataset source assemblies."""
import argparse
import ast
from pathlib import Path


def validate_source(source):
    tree = ast.parse(source)
    names = [n.name for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))]
    if len(names) != len(set(names)):
        raise ValueError('Assembly contains duplicate top-level definitions')
    classes = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
    if any(isinstance(base, ast.Name) and base.id == 'DatasetGenerator'
           for n in tree.body if isinstance(n, ast.ClassDef) for base in n.bases):
        if 'DatasetGenerator' not in classes:
            raise ValueError('Assemble the dataset base before layer definitions')
    return source


def append_template(source, template, required_layers=()):
    validate_source(source)
    classes = {n.name for n in ast.parse(source).body if isinstance(n, ast.ClassDef)}
    if any(f"Layer{i}DatasetGenerator" not in classes for i in required_layers):
        raise ValueError("Output is missing earlier layer assembly parts")
    ast.parse(template)
    if template in source:
        return source
    return validate_source(source.rstrip() + '\n\n' + template)


def main(build, argv=None, append=False):
    parser = argparse.ArgumentParser(description='Assemble validated historical dataset source')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check', action='store_true', help='Check without writing')
    args = parser.parse_args(argv)
    try:
        previous = args.output.read_bytes() if args.output.exists() else None
        if append and previous is None:
            raise ValueError('Output must contain the earlier assembly parts')
        source = build(previous.decode('utf-8')) if append else build()
        validate_source(source)
        if previous == source.encode('utf-8'):
            print('Assembly already matches.')
            return 0
        if args.check:
            print(f'Assembly differs: {args.output}')
            return 1
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if previous is not None:
            backup = args.output.with_suffix(args.output.suffix + '.before-generator-assembly')
            if not backup.exists():
                backup.write_bytes(previous)
        args.output.write_text(source, encoding='utf-8')
        print(f'Wrote assembly: {args.output}')
        return 0
    except (OSError, SyntaxError, ValueError, UnicodeError) as exc:
        print(f'Assembly failed: {exc}')
        return 1
