"""Resident protein glut and source-bound amino-acid self-marks.

The carrier contains co-present distinctions, never normalized weights.
Coordinates are a named readout, not a replacement for the resident object.
Full self-marks execute through Vox's existing observation transport machine.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_NAMES = {
    'Ala': ('alanine',), 'Arg': ('arginine',), 'Asn': ('asparagine',),
    'Asp': ('aspartate', 'aspartic_acid'), 'Cys': ('cysteine',),
    'Gln': ('glutamine',), 'Glu': ('glutamate', 'glutamic_acid'),
    'Gly': ('glycine',), 'His': ('histidine',), 'Ile': ('isoleucine',),
    'Leu': ('leucine',), 'Lys': ('lysine',), 'Met': ('methionine',),
    'Phe': ('phenylalanine',), 'Pro': ('proline',), 'Ser': ('serine',),
    'Thr': ('threonine',), 'Trp': ('tryptophan',), 'Tyr': ('tyrosine',),
    'Val': ('valine',),
}


def _read_mark(name):
    stem = name + '_as_peptide_component'
    path = _ROOT / 'ob3ect' / 'digital' / stem / (stem + '_ob3ect.json')
    raw = path.read_bytes()
    return path, raw


@lru_cache(maxsize=64)
def _decode_mark(path, raw):
    data = json.loads(raw)
    word = data['glyph_word']
    grounded = data['grounded_tuple']
    if not word or any(c not in '⊢⊣≻≺⋈⊙∈∋⊤⊥⊞⊡' for c in word):
        raise ValueError(f'Invalid self-mark in {path}')
    if len(grounded.strip('⟨⟩')) != 12:
        raise ValueError(f'Expected twelve grounded distinctions in {path}')
    return {
        'name': data['name'], 'artifact_id': data['artifact_id'],
        'word': word, 'tuple': grounded,
        'source': str(path.relative_to(_ROOT)), 'sha256': sha256(raw).hexdigest(),
        'grounding': data.get('grounding_reasoning', ''),
        'actions': data.get('phases', {}).get('phase_4', {}).get('steps', []),
    }


def self_marks(aa):
    """All retained chemical forms, including distinct acid/ion marks."""
    try:
        names = _NAMES[aa]
    except KeyError:
        raise ValueError(f'No amino-acid self-mark for {aa!r}') from None
    # Read each source before consulting the content-keyed decode cache.
    # A long-lived process observes a re-imscription on its next construction.
    return [deepcopy(_decode_mark(*_read_mark(name))) for name in names]


@dataclass
class ProteinGlut:
    """One resident sequence with co-held residue forms and observations.

    Native B is the starting condition, not inferred from a disagreement.
    Per-observable N/T/F/B remains distinct from that native condition and from
    the SIXTEEN_3 word machine's register. Neither is an energy value.
    """
    residues: list
    observations: list = field(default_factory=list)
    readouts: list = field(default_factory=list)
    native_state: str = 'B'

    @classmethod
    def prepare(cls, aa_list, codons=None):
        from .peptide_geometry import execute_self_marks
        if codons is not None and len(codons) != len(aa_list):
            raise ValueError('Codon and residue boundaries differ')
        residues, pending = [], []
        for i, aa in enumerate(aa_list):
            marks = self_marks(aa)
            residues.append({'index': i, 'aa': aa, 'codon': codons[i] if codons is not None else None,
                             'native_state': 'B', 'self_marks': marks})
            pending.extend(marks)
        flows = iter(execute_self_marks(pending))
        for residue in residues:
            for mark in residue['self_marks']:
                mark['execution'] = next(flows)
        return cls(residues)

    def observe(self, name, values):
        """Retain observations with ancestry; no observation overwrites B."""
        self.observations.append({'name': name, 'values': values})

    def readout(self, name, values):
        self.readouts.append({'name': name, 'values': values})

    def torsion_readout(self, table, transitions):
        """Retain every configured torsion articulation without a probability.

        The codon path names the coordinate readout. It does not delete other
        articulations or rank the chemical forms of a residue.
        """
        if len(transitions) != len(self.residues):
            raise ValueError('Torsion readout lost residue boundaries')
        for residue, transition in zip(self.residues, transitions):
            residue['torsion_articulations'] = [
                {'transition': list(key), 'phi': value['phi'], 'psi': value['psi'],
                 'structure': value['ss']}
                for key, value in table.items()]
            residue['coordinate_readout_transition'] = list(transition)
        self.readout('codon-aligned-torsions', [list(t) for t in transitions])

    def contacts(self, contacts):
        """Condition contact distinctions on both residues' full self-marks.

        Preserve every chemical-form pairing and every axis distinction. This
        relation is usable by later coupling without choosing a winning form.
        """
        edges = []
        for contact in contacts:
            left, right = contact.residue_i, contact.residue_j
            forms = []
            for a in self.residues[left]['self_marks']:
                for b in self.residues[right]['self_marks']:
                    x, y = a['tuple'].strip('⟨⟩'), b['tuple'].strip('⟨⟩')
                    forms.append({'left': a['artifact_id'], 'right': b['artifact_id'],
                                  'axes': [{'slot': i, 'left': u, 'right': v,
                                            'same': u == v}
                                           for i, (u, v) in enumerate(zip(x, y))]})
            edges.append({'left': left, 'right': right, 'kind': contact.interaction_type,
                          'distance_readout': contact.distance if hasattr(contact, 'distance')
                          else contact.distance_estimate, 'forms': forms})
        self.observe('contact-relations', edges)

    def as_dict(self):
        from dataclasses import asdict
        return {**asdict(self), 'semantics': 'native-glut',
                'weights': 'none', 'coordinate_role': 'boundary-readout',
                'word_register_basis': 'SIXTEEN_3 T,F,t,f; separate from Belnap evidence'}

# Sequence parsing and tuple boundaries shared by every protein-facing engine.
ONE_TO_THREE = dict(zip('ARNDCQEGHILKMFPSTWYV',
    ('Ala','Arg','Asn','Asp','Cys','Gln','Glu','Gly','His','Ile',
     'Leu','Lys','Met','Phe','Pro','Ser','Thr','Trp','Tyr','Val')))
MARKS = tuple('⊢⊣≻≺⋈⊤∈∋⊙⊥⊞⊡')
AXES = ("⊢","⊣","≻","≺","⋈","⊤","∈","∋","⊙","⊥","⊞","⊡")


def prepare_sequence(sequence):
    return ProteinGlut.prepare([ONE_TO_THREE[c] for c in sequence.upper()])


def retain_carrier(value):
    """Keep an existing carrier's residue banks and mutable observation lists."""
    if isinstance(value, ProteinGlut):
        return value
    if not isinstance(value, dict) or value.get('native_state') != 'B':
        raise ValueError('Expected a native protein glut')
    return ProteinGlut(value['residues'], value['observations'], value['readouts'], 'B')


def mark_counts(residue):
    """Unweighted full-word occurrences, with every chemical form retained."""
    from collections import Counter
    return Counter(c for form in residue['self_marks'] for c in form['word'])


def site_alternatives(carrier, indices=None, contexts=None):
    """Source-bound residue/form tensors; no averaging or Cartesian expansion.

    An optional context is the sidechain/environment composite on that residue.
    Each alternative remains linked to its original resident residue and word.
    """
    glut = retain_carrier(carrier)
    from .sidechain_algebra import safe_tensor
    rows = []
    selected = range(len(glut.residues)) if indices is None else indices
    for index in selected:
        residue = glut.residues[index]
        for form in residue['self_marks']:
            native = dict(zip(MARKS, form['tuple'].strip('⟨⟩')))
            tensor = safe_tensor(native, contexts[index]) if contexts and index in contexts else native
            rows.append({'residue_index': index, 'aa': residue['aa'],
                'artifact_id': form['artifact_id'], 'sha256': form['sha256'],
                'word': form['word'], 'execution': form['execution'],
                'tuple': dict(tensor),
                'native_tuple': native,
                'context': contexts.get(index) if contexts else None})
    return rows


def produce_ligand_family(carrier, site_family, max_candidates=10, generator=None):
    """Execute every distinct site tuple and retain all source-form supports."""
    from . import ligand_from_active_site as lfas
    generator = generator or lfas.decompose_and_generate
    glut = retain_carrier(carrier)
    family, cache, candidates = [], {}, {}
    for branch in site_family:
        key = tuple(branch['tuple'][p] for p in AXES)
        if key not in cache:
            cache[key] = generator(branch['tuple'])
        produced = cache[key]
        ancestry = {k: branch[k] for k in ('residue_index','artifact_id','sha256')}
        family.append({**ancestry, 'site_tuple': branch['tuple'],
                       'ligand_tuple': produced['ligand_type'],
                       'generator': produced.get('generator', 'decompose-and-generate')})
        for candidate in produced['ligand_candidates'][:max_candidates]:
            smiles = candidate['smiles']
            if smiles not in candidates:
                candidates[smiles] = {**candidate, 'source_forms': []}
            candidates[smiles]['source_forms'].append(ancestry)
    values = list(candidates.values())
    glut.observe('ligand-coupling', {'family': family, 'candidates': values})
    return family, values
