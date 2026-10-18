"""Source-bound adapter to Vox's shared peptide geometry and four-valued evidence.

The adapter compiles only the three canonical geometry modules, without Cargo,
model execution, or a duplicate Python geometry implementation. Artifacts stay
inside this repository and rebuild when any bound source changes.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

_REPO = Path(__file__).resolve().parents[1]
_ADAPTER = Path(__file__).with_name('peptide_bridge.rs')
_VOX = _REPO.parent / 'Vox' / 'src'
_SOURCES = [_ADAPTER, *(_VOX / name for name in
                       ('fold3d.rs', 'peptide_geometry.rs', 'peptide_closure.rs'))]
_CACHE = _REPO / 'measurements' / 'native_peptide_bridge'


def _helper():
    _CACHE.mkdir(parents=True, exist_ok=True)
    binding = {str(path.relative_to(_REPO.parent)):
               hashlib.sha256(path.read_bytes()).hexdigest() for path in _SOURCES}
    fingerprint = hashlib.sha256(json.dumps(binding, sort_keys=True).encode()).hexdigest()
    binary = _CACHE / ('peptide_bridge_' + fingerprint[:20])
    manifest = binary.with_suffix('.json')
    try:
        current = json.loads(manifest.read_text()) if manifest.exists() else {}
    except (json.JSONDecodeError, OSError):
        current = {}
    if (not binary.exists() or current.get('binary_sha256') !=
            hashlib.sha256(binary.read_bytes()).hexdigest()):
        pending = binary.with_name(binary.name + f'.{os.getpid()}.pending')
        try:
            subprocess.run(['rustc', '--edition=2021', '-O', str(_ADAPTER),
                            '-o', str(pending)], check=True, capture_output=True, text=True)
            after = {str(path.relative_to(_REPO.parent)):
                     hashlib.sha256(path.read_bytes()).hexdigest() for path in _SOURCES}
            if after != binding:
                raise RuntimeError('Canonical peptide sources changed during compilation; retry construction')
            pending.replace(binary)
        except subprocess.CalledProcessError as error:
            raise RuntimeError('Shared Vox peptide adapter could not compile:\n' + error.stderr) from error
        current = {'sources': binding, 'source_fingerprint': fingerprint,
                   'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}
        pending_manifest = manifest.with_name(manifest.name + f'.{os.getpid()}.pending')
        pending_manifest.write_text(json.dumps(current, indent=2) + '\n')
        pending_manifest.replace(manifest)
    return binary, current


def construct(aa_list, phi_psi, sequence_labels=None, backbone_labels=None, *, coordinates=None):
    """Return the complete coordinates, coordinate evidence and valid B states."""
    size = len(aa_list)
    if len(phi_psi) != size:
        raise ValueError('One retained phi/psi pair is required per residue')
    sequence_labels = ['-'] * size if sequence_labels is None else sequence_labels
    backbone_labels = ['-'] * size if backbone_labels is None else backbone_labels
    if len(sequence_labels) != size or len(backbone_labels) != size:
        raise ValueError('One observation from each classifier is required per residue')
    rows = []
    for aa, (phi, psi), sequence, backbone in zip(aa_list, phi_psi, sequence_labels, backbone_labels):
        aa = aa[:1].upper() + aa[1:].lower()
        if any(any(c.isspace() for c in item) for item in (aa, sequence, backbone)):
            raise ValueError('Residue and label fields must be single tokens')
        rows.append(f'{aa} {float(phi):.17g} {float(psi):.17g} {sequence} {backbone}')
    binary, binding = _helper()
    command = [str(binary)]
    wire = '\n'.join(rows)
    if coordinates is not None:
        if len(coordinates) != size:
            raise ValueError('One complete coordinate frame is required per residue')
        command.append('--assess')
        atoms = []
        for i, frame in enumerate(coordinates):
            for name in ('n', 'ca', 'c', 'o'):
                atoms.append(f'{i} {name.upper()} ' + ' '.join(format(float(v), '.17g') for v in frame[name]))
            for atom in frame['sidechain']:
                name = atom['name'].strip()
                if not name or any(c.isspace() for c in name):
                    raise ValueError('Atom names must be single tokens')
                atoms.append(f'{i} {name} ' + ' '.join(format(float(v), '.17g') for v in atom['xyz']))
        wire += '\nCOORDINATES\n' + '\n'.join(atoms)
    result = subprocess.run(command, input=wire, capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Shared peptide construction rejected input: ' + result.stderr.strip())
    payload = json.loads(result.stdout)
    payload['source_binding'] = binding
    return payload
