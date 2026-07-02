#!/usr/bin/env python3
"""
run_all_ligands.py — Run all PDB codes through the ligand pipeline,
extract SMILES from stdout table, save combined results for demo sheet.
"""
import subprocess, sys, os, re, json, time
from collections import defaultdict

BASE = '/home/mrnob0dy666/imsgct/red-hot_rebis'
OUTDIR = '/home/mrnob0dy666/imsgct/ig-docs/ligand_demo_sheet'
os.makedirs(OUTDIR, exist_ok=True)

# ── Load PDB codes ──
sys.path.insert(0, os.path.join(BASE, 'rhr_p4rky'))
from expanded_catalyzing_proteins import EXPANDED_PROTEIN_LOOKUP

PDB_META = {}
for name, entry in EXPANDED_PROTEIN_LOOKUP.items():
    pdb = entry.get('pdb','')
    if pdb:
        PDB_META[pdb] = {'name': name, 'organism': entry.get('organism',''),
                         'reaction': entry.get('reaction',''),
                         'residues': entry.get('active_site_residues',[]),
                         'roles': entry.get('catalytic_roles',[])}

def assign_ec(reaction):
    r = reaction.lower()
    if any(w in r for w in ['oxid','dehydrogen','oxygen','peroxidase','p450','dismutase',
                              'catalase','reductase','monooxygen']):
        return 'EC 1: Oxidoreductase'
    if any(w in r for w in ['phosphoryl','kinase','transferase','methyl','acetyl',
                              'glycosyl','polymerase']):
        return 'EC 2: Transferase'
    if any(w in r for w in ['hydrolysis','protease','peptidase','lipase','nuclease',
                              'lactamase','glycosidase','esterase','amylase','urease',
                              'deiminase','deubiquitin']):
        return 'EC 3: Hydrolase'
    if any(w in r for w in ['lyase','synthase','decarboxyl','aldolase','hydratase',
                              'ammonia lyase','dehydratase','cyclase']):
        return 'EC 4: Lyase'
    if any(w in r for w in ['isomer','mutase','racemase','topoisomerase','epimerase']):
        return 'EC 5: Isomerase'
    if any(w in r for w in ['ligase','synthetase','carboxylase','ubiquitin ligase']):
        return 'EC 6: Ligase'
    if any(w in r for w in ['transloc','transport','pump','channel','atp synthase',
                              'efflux','reuptake','atpase']):
        return 'EC 7: Translocase'
    return 'Other'

for pdb, meta in PDB_META.items():
    meta['ec_class'] = assign_ec(meta['reaction'])

PDB_CODES = sorted(PDB_META.keys())
print(f"Loaded {len(PDB_CODES)} PDB codes with metadata")

# ── Run pipeline ──
ALL_LIGANDS = []
SMILES_SET = set()
TABLE_RE = re.compile(r'\s*(\d+)\s+(.+?)\s{2,}(.+?)\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\s*$')

total = len(PDB_CODES)
for i, pdb in enumerate(PDB_CODES):
    meta = PDB_META[pdb]
    t0 = time.time()
    proc = subprocess.run(
        ['python3', '-m', 'rebis.p4ra', 'ligands', pdb],
        capture_output=True, text=True, timeout=120, cwd=BASE,
        env={**os.environ, 'PYTHONPATH': BASE}
    )
    elapsed = time.time() - t0
    n_parsed = 0
    
    for line in proc.stdout.split('\n'):
        m = TABLE_RE.match(line)
        if m:
            smi = m.group(3)
            if any(c in smi for c in 'CNOSP') and len(smi) > 3:
                if smi not in SMILES_SET:
                    SMILES_SET.add(smi)
                    try:
                        score, logP, mw = float(m.group(4)), float(m.group(5)), float(m.group(6))
                    except:
                        score, logP, mw = 0, 0, 0
                    ALL_LIGANDS.append({
                        'pdb': pdb, 'name': meta['name'], 'ec_class': meta['ec_class'],
                        'organism': meta['organism'], 'smiles': smi,
                        'method': m.group(2), 'score': score, 'logP': logP, 'MW': mw,
                    })
                    n_parsed += 1
    
    status = 'OK' if proc.returncode == 0 else f'ERR({proc.returncode})'
    print(f"[{i+1:3d}/{total}] {pdb:6s} | {meta['name']:<35s} | {n_parsed:3d} smiles | {elapsed:.1f}s | {status}")
    sys.stdout.flush()

# ── Save ──
with open(f'{OUTDIR}/all_ligands.smi', 'w') as f:
    for lig in ALL_LIGANDS:
        f.write(f"{lig['smiles']}\t{lig['pdb']}\t{lig['name']}\t{lig['ec_class']}\n")

with open(f'{OUTDIR}/all_ligands.json', 'w') as f:
    json.dump(ALL_LIGANDS, f, indent=2)

# ── Summary ──
ec_counts = defaultdict(lambda: {'proteins': set(), 'ligands': 0})
for lig in ALL_LIGANDS:
    ec = lig['ec_class']
    ec_counts[ec]['proteins'].add(lig['pdb'])
    ec_counts[ec]['ligands'] += 1

print(f"\n{'='*80}")
print(f"TOTAL: {len(ALL_LIGANDS)} ligands ({len(SMILES_SET)} unique) from {len(PDB_CODES)} proteins")
print(f"\nBy EC Class:")
for ec in sorted(ec_counts.keys()):
    c = ec_counts[ec]
    print(f"  {ec:<35s} | {len(c['proteins']):3d} proteins | {c['ligands']:5d} ligands")
print(f"\nSaved to: {OUTDIR}/")
print(f"  all_ligands.smi  — {len(ALL_LIGANDS)} SMILES")
print(f"  all_ligands.json — full results")
