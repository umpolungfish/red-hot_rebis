#!/usr/bin/env python3
"""
run_all_inprocess.py — Run ligand generation for ALL catalog proteins in-process.
Calls generate_combinatorial directly, no subprocess. Builds demo sheet.
"""
import sys, os, json, time, re
from collections import defaultdict

BASE = '/home/mrnob0dy666/imsgct/red-hot_rebis'
OUTDIR = '/home/mrnob0dy666/imsgct/ig-docs/ligand_demo_sheet'
os.makedirs(OUTDIR, exist_ok=True)

sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, 'rhr_p4rky'))

# Suppress RDKit warnings
from rdkit import RDLogger
RDLogger.logger().setLevel(RDLogger.ERROR)

from expanded_catalyzing_proteins import EXPANDED_PROTEIN_LOOKUP
from ligand_combinatorial import generate_combinatorial

def assign_ec(reaction):
    r = reaction.lower()
    if any(w in r for w in ['oxid','dehydrogen','oxygen','peroxidase','p450','dismutase',
                              'catalase','reductase','monooxygen','oxidase','hydroxylase']):
        return 'EC 1: Oxidoreductase'
    if any(w in r for w in ['phosphoryl','kinase','transferase','methyl','acetyl',
                              'glycosyl','polymerase','transaminase']):
        return 'EC 2: Transferase'
    if any(w in r for w in ['hydrolysis','protease','peptidase','lipase','nuclease',
                              'lactamase','glycosidase','esterase','amylase','urease',
                              'deiminase','deubiquitin','phosphatase','cholinesterase',
                              'deaminase','elastase','plasmin','thrombin','fibrin',
                              'kallikrein','caspase','cathepsin','papain','pepsin',
                              'renin','subtilisin','trypsin','chymotrypsin',
                              'phospholipase','metalloproteinase','gelatinase']):
        return 'EC 3: Hydrolase'
    if any(w in r for w in ['lyase','synthase','decarboxyl','aldolase','hydratase',
                              'ammonia lyase','dehydratase','cyclase','enolase',
                              'fumarase','anhydrase','dehydratase']):
        return 'EC 4: Lyase'
    if any(w in r for w in ['isomer','mutase','racemase','topoisomerase','epimerase']):
        return 'EC 5: Isomerase'
    if any(w in r for w in ['ligase','synthetase','carboxylase','ubiquitin ligase']):
        return 'EC 6: Ligase'
    if any(w in r for w in ['transloc','transport','pump','channel','atp synthase',
                              'efflux','reuptake','atpase','transporter']):
        return 'EC 7: Translocase'
    return 'Other'

# ── Prepare protein list ──
proteins = []
for name, entry in EXPANDED_PROTEIN_LOOKUP.items():
    pdb = entry.get('pdb','')
    if not pdb: continue
    reaction = entry.get('reaction','')
    proteins.append({
        'name': name, 'pdb': pdb,
        'organism': entry.get('organism',''),
        'reaction': reaction,
        'ec_class': assign_ec(reaction),
        'residues': entry.get('active_site_residues', []),
    })

# Deduplicate by PDB
seen_pdb = {}
unique_proteins = []
for p in proteins:
    if p['pdb'] not in seen_pdb:
        seen_pdb[p['pdb']] = p
        unique_proteins.append(p)

print(f"Running {len(unique_proteins)} unique proteins...")
print(f"{'='*80}")

# ── Run all ──
ALL_LIGANDS = []
SMILES_SET = set()
EC_COUNTS = defaultdict(lambda: {'proteins': set(), 'ligands': 0, 'smiles': set()})

total = len(unique_proteins)
for i, prot in enumerate(unique_proteins):
    t0 = time.time()
    try:
        candidates = generate_combinatorial(
            protein_context=EXPANDED_PROTEIN_LOOKUP[prot['name']],
            n_scaffolds=50,
            fragments_per_position=6,
            max_products=500,
            verbose=False,
        )
    except Exception as e:
        candidates = []
        print(f"[{i+1:3d}/{total}] {prot['pdb']:6s} | {prot['name']:<35s} | ERROR: {str(e)[:80]}")
        continue

    elapsed = time.time() - t0
    n_new = 0
    for c in candidates:
        smi = c.get('smiles','')
        if smi and smi not in SMILES_SET:
            SMILES_SET.add(smi)
            ALL_LIGANDS.append({
                'pdb': prot['pdb'], 'name': prot['name'],
                'ec_class': prot['ec_class'], 'organism': prot['organism'],
                'smiles': smi,
                'method': c.get('scaffold', c.get('method', '?')),
                'score': round(c.get('score', 0), 3),
                'logP': round(c.get('logp', c.get('logP', 0)), 1),
                'MW': round(c.get('mw', c.get('MW', 0)), 1),
            })
            n_new += 1
            EC_COUNTS[prot['ec_class']]['smiles'].add(smi)
    
    EC_COUNTS[prot['ec_class']]['proteins'].add(prot['pdb'])
    EC_COUNTS[prot['ec_class']]['ligands'] += n_new
    
    print(f"[{i+1:3d}/{total}] {prot['pdb']:6s} | {prot['name']:<35s} | {n_new:4d} new ({len(candidates):4d} total) | {prot['ec_class']:<30s} | {elapsed:.1f}s")
    sys.stdout.flush()

# ── Save ──
with open(f'{OUTDIR}/all_ligands.smi', 'w') as f:
    for lig in ALL_LIGANDS:
        f.write(f"{lig['smiles']}\t{lig['pdb']}\t{lig['name']}\t{lig['ec_class']}\n")

with open(f'{OUTDIR}/all_ligands.json', 'w') as f:
    json.dump(ALL_LIGANDS, f, indent=2)

# ── Per-protein SMILES files for demo sheet ──
for prot in unique_proteins:
    prot_smiles = [l for l in ALL_LIGANDS if l['pdb'] == prot['pdb']]
    if prot_smiles:
        with open(f'{OUTDIR}/by_protein/{prot["pdb"]}_{prot["name"]}.smi', 'w') as f:
            for lig in prot_smiles[:50]:
                f.write(f"{lig['smiles']}\t{lig['score']}\t{lig['logP']}\t{lig['MW']}\n")

# ── Summary ──
print(f"\n{'='*80}")
print(f"TOTAL: {len(ALL_LIGANDS)} ligands ({len(SMILES_SET)} unique) from {total} proteins")
print(f"\nBy EC Class:")
for ec in sorted(EC_COUNTS.keys()):
    c = EC_COUNTS[ec]
    print(f"  {ec:<35s} | {len(c['proteins']):3d} proteins | {c['ligands']:6d} ligands | {len(c['smiles']):6d} unique")
print(f"\nSaved:")
print(f"  {OUTDIR}/all_ligands.smi  — {len(ALL_LIGANDS)} SMILES with metadata")
print(f"  {OUTDIR}/all_ligands.json — full results with scores")
print(f"  {OUTDIR}/by_protein/     — per-protein SMILES files")
