"""Executable finite tables exported from the live Lean scripture.

The Python engines consume Lean's computed operations, not another transcription
of tensor rules. Re-export when any source dependency changes.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / 'p4rakernel/p4ramill'
SOURCES = [LEAN/'Imscribing/Primitives/Core.lean',
           LEAN/'Imscribing/Primitives/Imscription.lean',
           LEAN/'Imscribing/GeneticCode.lean',
           Path(__file__).with_name('ProteinTables.lean')]
MARKS = tuple('⊢⊣≻≺⋈⊤∈∋⊙⊥⊞⊡')


@lru_cache(maxsize=4)
def _export(binding):
    out = ROOT/'red-hot_rebis/measurements/lean_protein_tables'
    out.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(binding.encode()).hexdigest()
    path = out/(key+'.json')
    if path.exists():
        return json.loads(path.read_text())
    run = subprocess.run(['lake','env','lean',str(SOURCES[-1])], cwd=LEAN,
                         capture_output=True, text=True, check=True)
    axes, promoted = {}, {}
    for line in run.stdout.splitlines():
        parts = line.split('\t')
        if parts[0] == 'AXIS':
            _, mark, values, tensor, meet, join = parts
            axes[mark] = {'values': list(values), 'tensor': list(tensor),
                          'meet': list(meet), 'join': list(join)}
        if parts[0] == 'AA':
            _, aa, mark = parts
            if mark != '-':
                promoted[aa] = mark
    if set(axes) != set(MARKS) or len(promoted) != 12:
        raise RuntimeError('Incomplete Lean protein operation export')
    result = {'axes': axes, 'promoted': promoted, 'sources': json.loads(binding)}
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    return result


def tables():
    binding = json.dumps({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in SOURCES}, sort_keys=True)
    return _export(binding)


def operation(name, left, right):
    result = {}
    for mark, axis in tables()['axes'].items():
        values = axis['values']
        i, j = values.index(left[mark]), values.index(right[mark])
        result[mark] = axis[name][i*len(values)+j]
    return result
