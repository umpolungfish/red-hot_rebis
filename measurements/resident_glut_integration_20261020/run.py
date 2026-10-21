"""Exercise the complete repaired carrier across the existing executable paths."""
import contextlib
import io
import json
import hashlib
import subprocess
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from rhr_p4rky.lean_protein import tables
from rhr_p4rky.protein_glut import prepare_sequence, self_marks
from rhr_p4rky.serpent_rod import SerpentRod
from rhr_p4rky.serpent_rod_v2 import SerpentRodV2
from rhr_p4rky.pdb_writer import write_pdb_from_gen2
from rhr_p4rky.ligand_from_site_pdb import design_ligand_from_pdb, design_ligand_from_pdb_improved, result_to_json
from rhr_p4rky.sidechain_algebra import batch_analyze
from serpentrod.stratified_predictor import ProteinStratifiedPredictor, analyze_spectrum, RollingProfile
from clink.datasets.protein_structure import generate_protein_structure, pdb_from_sequence
from rhr_p4rky.ch3mpiler_serpentrod_pipeline import run_pipeline, format_report
from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
rna = ''.join(('AUG','GCU','CGU','AAU','GAU','UGU','GAA','GGU','CAC','AUU','CUU','AAA','UAU','CCU','CAA','UCU','ACU','GUU','UGG','UUU','UAA'))
sequence='MARNDCEGHILKYPQSTVWF'
log=io.StringIO()
with contextlib.redirect_stdout(log):
    assert tables()['promoted']['His']=='∈'
    assert tables()['promoted']['Asn']=='∋'
    assert tables()['promoted']['Gln']=='⊙'
    v1=SerpentRod(rna);v1.verbose=False;legacy=v1.report()
    assert legacy['aa_sequence']==sequence and len(legacy['protein_glut']['residues'])==20
    assert len(legacy['activation_pattern'])==20
    for residue in legacy['protein_glut']['residues']:
        originals = self_marks(residue['aa'])
        assert [(f['word'], f['tuple'], f['sha256']) for f in residue['self_marks']] == [
            (f['word'], f['tuple'], f['sha256']) for f in originals]
    processing=ProteinStratifiedPredictor(sequence).run_full_pipeline()
    assert len(processing['protein_glut']['residues'])==20
    assert all(sum(analyze_spectrum(aa).values())>0 for aa in 'AGPSTVLR')
    assert len(RollingProfile('AGPSTVLR').summary()['protein_glut']['residues'])==8
    v2=SerpentRodV2(rna);v2.verbose=False;model=v2.predict()
    pdb=OUT/'protein.pdb';write_pdb_from_gen2(model,str(pdb))
    assert Path(str(pdb)+'.glut.json').exists()
    labels=[f'{aa}{i+1}' for i,aa in enumerate(model.aa_list)]
    ligand=design_ligand_from_pdb(str(pdb),labels,max_candidates=2)
    output=result_to_json(ligand)
    assert len(output['site_family'])==len(output['ligand_family'])==22
    assert {f['artifact_id'] for f in output['site_family']}=={m['artifact_id'] for r in model.protein_glut['residues'] for m in r['self_marks']}
    assert any(x['name']=='secondary-structure' for x in output['protein_glut']['observations'])
    assert any(x['name']=='ligand-coupling' for x in output['protein_glut']['observations'])
    assert output['ligand_candidates'] and all(c['source_forms'] for c in output['ligand_candidates'])
    assert ligand.ligand_tuple == output['ligand_family'][0]['ligand_tuple']
    improved_ligand = design_ligand_from_pdb_improved(str(pdb), labels, max_candidates=2)
    improved_output = result_to_json(improved_ligand)
    assert len(improved_output['ligand_family']) == 22
    assert improved_ligand.ligand_tuple == improved_output['ligand_family'][0]['ligand_tuple']
    assert improved_output['protein_glut']['residues'] == output['protein_glut']['residues']
    sides=batch_analyze(verbose=False)
    assert len(sides['results'])==80
    assert all(row.get('self_mark_alternatives') for row in sides['results'].values())
    structure=generate_protein_structure(sequence)
    assert len(structure.protein_glut['residues'])==20
    assert 'NATIVE PROTEIN STATE B' in pdb_from_sequence(sequence)
    gene=GeneToProteinPipeline(rna,is_rna=True);gene.verbose=False
    report=gene.run()
    old_observations=list(report['protein_glut']['observations'])
    site=run_pipeline(target_molecule='CC(=O)O',depth=1,verbose=False,protein_result=report)
    assert site.site_aa_sequence==sequence
    assert len(site.ligand_family)==22 and site.ligand_candidates
    assert site.protein_glut['observations'][:len(old_observations)]==old_observations
    assert len(site.protein_glut['observations'])>len(old_observations)
    assert site.secondary_elements == report['secondary']
    assert site.contacts and all(c['forms'] for c in site.contacts)
    assert site.frobenius_verified == report['closure']['frobenius_across_pathway']
    assert site.protein_glut['residues'] == report['protein_glut']['residues']
    assert 'Long-range contacts:' in format_report(site)
    # Reject a matching peptide carried from a different synonymous RNA source.
    changed = rna[:3] + 'GCC' + rna[6:]
    try:
        SerpentRod(changed, protein_glut=legacy['protein_glut']).predict()
    except ValueError as error:
        assert 'coding source' in str(error)
    else:
        raise AssertionError('Mismatched coding source was accepted')
(OUT/'run.log').write_text(log.getvalue())
(OUT/'ligand.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
(OUT/'chain.json').write_text(json.dumps(site.to_dict(),indent=2,ensure_ascii=False)+'\n')
(OUT/'processing.json').write_text(json.dumps(processing,indent=2,ensure_ascii=False)+'\n')
checks = {}
for name, arguments in (
    ('vox_peptide', ['rebis.vox', 'peptide', sequence, '--json']),
    ('vox_rna', ['rebis.vox', 'rna', rna, '--json']),
    ('vox_former_ground', ['rebis.vox', 'peptide', 'AGPSTVLR', '--json']),
    ('legacy_fold', ['rebis.serpentrod', 'fold', rna]),
    ('ligand_cli', ['rebis.ligand', '--pdb-file', str(pdb), '--active',
                    ','.join(labels), '--top-n', '2', '--improved', '--json']),
    ('chain_cli', ['rebis', 'chain', '--seq', rna, '--target', 'CC(=O)O',
                   '--depth', '1', '--pdb', str(OUT/'chain_cli.pdb')]),
):
    run = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True)
    (OUT/(name+'.stdout')).write_text(run.stdout)
    (OUT/(name+'.stderr')).write_text(run.stderr)
    assert run.returncode == 0, (arguments, run.stderr, run.stdout[-2000:])
    checks[name] = {'command': arguments, 'exit_code': run.returncode}
    if name.startswith('vox'):
        carrier = json.loads(run.stdout)
        assert len(carrier['residues']) == (8 if name == 'vox_former_ground' else 20)
        assert all(len(f['execution']['native_transition_table']) == 16
                   for r in carrier['residues'] for f in r['self_marks'])
        assert sum(len(r['self_marks']) for r in carrier['residues']) == (8 if name == 'vox_former_ground' else 22)
    elif name == 'ligand_cli':
        saved = json.loads(run.stdout)
        assert len(saved['ligand_family']) == 22 and saved['ligand_candidates']
        assert all(c['source_forms'] for c in saved['ligand_candidates'])
    elif name == 'legacy_fold':
        assert '"protein_glut"' in run.stdout and '"self_marks"' in run.stdout
chain = json.loads((OUT/'chain_cli.pdb.chain.json').read_text())
assert chain['protein']['protein_glut'] == chain['catalytic']['protein_glut']
assert chain['catalytic']['ligand_family'] and chain['catalytic']['ligand_candidates']
sidecar = json.loads((OUT/'chain_cli.pdb.glut.json').read_text())
assert sidecar['protein_glut'] == chain['catalytic']['protein_glut']
assert sidecar['pdb_sha256'] == hashlib.sha256((OUT/'chain_cli.pdb').read_bytes()).hexdigest()
result = {'residues':20,'forms':22,'sidechain_compositions':len(sides['results']),
    'ligand_candidates':len(output['ligand_candidates']), 'chain_candidates':len(site.ligand_candidates),
    'commands': checks, 'lean_sources': tables()['sources'],
    'source_bindings': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(ROOT.rglob('*.py'))
                        if '.venv' not in p.parts and '_archive' not in p.parts},
    'status':'passed'}
(OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('source_bindings','lean_sources')},indent=2))
