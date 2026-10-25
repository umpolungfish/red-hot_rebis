"""End-to-end native-glut execution through both public protein paths."""
import contextlib
import io
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT))
from rhr_p4rky.serpent_rod_v2 import SerpentRodV2
from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
from rhr_p4rky.pdb_writer import write_pdb_from_gen2
from rhr_p4rky.protein_glut import self_marks

rna = ''.join(('AUG', 'GCU', 'CGU', 'AAU', 'GAU', 'UGU', 'GAA', 'GGU',
               'CAC', 'AUU', 'CUU', 'AAA', 'UAU', 'CCU', 'CAA', 'UCU',
               'ACU', 'GUU', 'UGG', 'UUU', 'UAA'))
log = io.StringIO()
with contextlib.redirect_stdout(log):
    predictor = SerpentRodV2(rna, name='all_residue_marks')
    predictor.verbose = False
    direct = predictor.predict()
    write_pdb_from_gen2(direct, str(OUT / 'gen2.pdb'))
    pipeline = GeneToProteinPipeline(rna, name='all_residue_marks', is_rna=True)
    pipeline.verbose = False
    report = pipeline.run(pdb_path=str(OUT / 'pipeline.pdb'))

assert len({r['aa'] for r in direct.protein_glut['residues']}) == 20
assert len(direct.protein_glut['residues']) == len(direct.aa_list) == 20
assert all(r['native_state'] == 'B' for r in direct.protein_glut['residues'])
assert len(self_marks('Asp')) == len(self_marks('Glu')) == 2
assert all(len(r['torsion_articulations']) == 16 for r in direct.protein_glut['residues'])
assert all(len(m['execution']['native_transition_table']) == 16
           for r in direct.protein_glut['residues'] for m in r['self_marks'])
assert direct.aa_sequence == report['aa_sequence']
def binding(residues):
    return [(r['aa'], [m['sha256'] for m in r['self_marks']]) for r in residues]
assert binding(direct.protein_glut['residues']) == binding(report['protein_glut']['residues'])
assert 'NATIVE PROTEIN STATE B' in (OUT / 'pipeline.pdb').read_text()
assert 'confidence' not in report['quaternary']['prediction']
assert report['quaternary']['prediction']['method'] == 'glut'
# Distinct full words must remain distinguishable even for identical tuples.
ala, arg = self_marks('Ala')[0], self_marks('Arg')[0]
assert ala['tuple'] == arg['tuple'] and ala['word'] != arg['word']
assert self_marks('Gly')[0]['tuple'] != ala['tuple']

(OUT / 'gen2.json').write_text(json.dumps(direct.protein_glut, indent=2, ensure_ascii=False) + '\n')
(OUT / 'pipeline.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
(OUT / 'run.log').write_text(log.getvalue())
print(json.dumps({'peptide': direct.aa_sequence, 'residues': len(direct.aa_list),
    'self_marks': sum(len(r['self_marks']) for r in direct.protein_glut['residues']),
    'native_state': direct.protein_glut['native_state'],
    'assembly': report['quaternary']['prediction'],
    'geometry_closed': direct.geometry_evidence['constraints_satisfied']}, indent=2))
