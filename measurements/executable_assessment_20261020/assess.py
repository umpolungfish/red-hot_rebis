"""Inventory local executable surfaces without importing their implementations."""
import ast
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SKIP = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'target'}
modules = {}
errors = []
files = []
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or SKIP.intersection(p.relative_to(ROOT).parts):
        continue
    rel = str(p.relative_to(ROOT))
    if p.suffix != '.py':
        if os.access(p, os.X_OK):
            files.append({'path': rel, 'kind': 'executable-file', 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
        continue
    raw = p.read_bytes()
    try:
        tree = ast.parse(raw, filename=rel)
    except (SyntaxError, ValueError) as exc:
        errors.append({'path': rel, 'error': str(exc)})
        continue
    mod = rel[:-3].replace('/', '.')
    if mod.endswith('.__init__'):
        mod = mod[:-9]
    imports = []
    signals = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(n.name for n in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.level:
                package = mod.split('.')[:-node.level]
                imports.append('.'.join(package + [node.module]))
            else:
                imports.append(node.module)
        if isinstance(node, ast.Name) and node.id in {'ProteinGlut','SerpentRod','SerpentRodV2','GeneToProteinPipeline','AA_MARK','word_of_peptide'}:
            signals.add(node.id)
    guards = [node.lineno for node in ast.walk(tree) if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and any(isinstance(v, ast.Constant) and v.value == '__main__' for v in node.test.comparators)]
    row = {'path': rel, 'sha256': hashlib.sha256(raw).hexdigest(), 'imports': sorted(set(imports)), 'summary': (ast.get_docstring(tree) or '').split('\n\n')[0][:900], 'functions': [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))], 'review_locations': [{'line': i, 'text': line.strip()[:200]} for i, line in enumerate(raw.decode('utf-8-sig').splitlines(), 1) if re.search(r'ProteinGlut|SerpentRod|GeneToProteinPipeline|AA_MARK|word_of_peptide|SIDECHAINS|requests\.|https?://|random\.|np\.random|confidence|probabilit|weighted_ord|ob3ect|subprocess\.', line)], 'signals': sorted(signals), 'main_guards': guards, 'executable_bit': os.access(p, os.X_OK), 'category': 'measurement' if rel.startswith('measurements/') else 'archive' if any('archive' in part.lower() or 'backup' in part.lower() for part in p.parts) else 'source'}
    modules[mod] = row
    if guards or row['executable_bit'] or p.name == '__main__.py' or raw.startswith(b'#!') or 'main' in row['functions']:
        files.append({**row, 'kind': 'python-entry'})

projects = []
for manifest in sorted(ROOT.rglob('pyproject.toml')):
    if SKIP.intersection(manifest.relative_to(ROOT).parts):
        continue
    config = tomllib.loads(manifest.read_text())
    for name, entry in config.get('project', {}).get('scripts', {}).items():
        module, function = entry.split(':')
        projects.append({'command': name, 'entry': entry, 'manifest': str(manifest.relative_to(ROOT)), 'installed': shutil.which(name), 'source': modules.get(module, {}).get('path')})

# Import reachability is a discovery map. Lazy string imports are not executed
# calls, and this intentionally does not claim runtime mechanism participation.
for entry in projects:
    seen = set()
    stack = [entry['entry'].split(':')[0]]
    while stack:
        m = stack.pop()
        if m in seen or m not in modules:
            continue
        seen.add(m)
        stack.extend(modules[m]['imports'])
    entry['static_reachable_modules'] = sorted(seen)
    entry['protein_connections'] = {m: modules[m]['signals'] for m in sorted(seen) if modules[m]['signals']}

help_results = []
for entry in projects:
    name = entry['command']
    if name == 'at':
        # The independent nested distribution is assessed separately, without
        # substituting an unrelated globally installed `at` command.
        argv = [sys.executable, '-c', 'from ars_therapeutica.cli import main; import sys; sys.exit(main())', '--help']
        pythonpath = str(ROOT / 'Ars_Therapeutica') + os.pathsep + str(ROOT)
    else:
        module, fn = entry['entry'].split(':')
        argv = [sys.executable, '-c', f'from {module} import {fn}; import sys; sys.exit({fn}())', '--help']
        pythonpath = str(ROOT)
    try:
        result = subprocess.run(argv, cwd=ROOT, env={**os.environ, 'PYTHONPATH': pythonpath}, capture_output=True, text=True, timeout=20)
        (OUT / (name + '.help.log')).write_text(result.stdout + result.stderr)
        help_results.append({'command': name, 'returncode': result.returncode, 'log': name + '.help.log'})
    except subprocess.TimeoutExpired:
        help_results.append({'command': name, 'timeout_seconds': 20})

report = {'scope': str(ROOT), 'python_modules_parsed': len(modules), 'parse_errors': errors, 'console_entries': projects, 'modules': modules, 'executable_surfaces': files, 'help_results': help_results, 'limits': 'Static inventory plus console help execution. Reachability is not proof of computational participation. Standalone scripts, generation, network and campaign workloads were not blindly launched.'}
(OUT / 'inventory.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print(json.dumps({'modules': len(modules), 'executable_surfaces': len(files), 'console_entries': len(projects), 'parse_errors': errors, 'help_results': help_results}, indent=2))
