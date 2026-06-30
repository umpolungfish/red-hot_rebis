#!/usr/bin/env python3
"""
FINAL: Corrected Platonic vs Crystallographic Comparison
- Only ATOM records (not HETATM)
- Only standard amino acids
- Proper Kabsch RMSD
- Full Ramachandran + SS comparison
"""
import sys, os, json, math, urllib.request
import numpy as np
from shared.rich_output import *


OUT = os.path.dirname(__file__)

# Standard amino acids only
AA3TO1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
          'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
          'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

def kabsch(P, Q):
    p = np.array(P, dtype=float); q = np.array(Q, dtype=float)
    p_c = p - p.mean(axis=0); q_c = q - q.mean(axis=0)
    C = np.dot(p_c.T, q_c)
    V, S, Wt = np.linalg.svd(C)
    d = np.sign(np.linalg.det(np.dot(V, Wt)))
    D = np.eye(3); D[2,2] = d
    R = np.dot(V, np.dot(D, Wt))
    q_rot = np.dot(q_c, R.T)
    rmsd = math.sqrt(np.sum((p_c - q_rot)**2) / len(p))
    return rmsd, q_rot, p_c

def dihedral(p1,p2,p3,p4):
    b1=np.array(p2)-np.array(p1); b2=np.array(p3)-np.array(p2); b3=np.array(p4)-np.array(p3)
    n1=np.cross(b1,b2); n2=np.cross(b2,b3)
    n1/=np.linalg.norm(n1); n2/=np.linalg.norm(n2)
    b2/=np.linalg.norm(b2); m1=np.cross(n1,b2)
    return math.degrees(math.atan2(np.dot(m1,n2), np.dot(n1,n2)))

def extract_backbone(pdb_text, chain='A'):
    """Extract N, CA, C for standard residues only (ATOM records only)."""
    residues = {}
    for line in pdb_text.split('\n'):
        if not line.startswith('ATOM'):  # ATOM only, skip HETATM
            continue
        atom = line[12:16].strip()
        ch = line[21:22].strip()
        res_name = line[17:20].strip()
        if ch != chain: continue
        if res_name not in AA3TO1: continue  # Standard AA only
        try:
            res_num = int(line[22:26])
            x,y,z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            if res_num not in residues:
                residues[res_num] = {'N':None,'CA':None,'C':None,'res':AA3TO1[res_name]}
            if atom in ('N','CA','C'):
                residues[res_num][atom] = (x,y,z)
        except: pass
    return residues

def compute_phi_psi(residues):
    result = {}
    keys = sorted(residues.keys())
    for i, rn in enumerate(keys):
        r = residues[rn]
        phi = psi = None
        if i > 0:
            prev = residues[keys[i-1]]
            if prev.get('C') and r.get('N') and r.get('CA') and r.get('C'):
                phi = dihedral(prev['C'], r['N'], r['CA'], r['C'])
        if i < len(keys)-1:
            nxt = residues[keys[i+1]]
            if r.get('N') and r.get('CA') and r.get('C') and nxt.get('N'):
                psi = dihedral(r['N'], r['CA'], r['C'], nxt['N'])
        result[rn] = {'phi':phi, 'psi':psi, 'res':r['res']}
    return result

def ramachandran_region(phi, psi):
    if phi is None or psi is None: return 'none'
    if -180 <= phi <= -30 and -100 <= psi <= 30: return 'alpha'
    elif -180 <= phi <= -30 and 60 <= psi <= 180: return 'beta'
    elif 30 <= phi <= 120 and -60 <= psi <= 60: return 'left'
    elif -180 <= phi <= -30 and -180 <= psi <= -100: return 'ppii'
    else: return 'other'

def fetch_pdb(pdb_id):
    try:
        req = urllib.request.Request(f'https://files.rcsb.org/download/{pdb_id}.pdb',
                                     headers={'User-Agent': 'Rebis/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8')
    except: return None

TARGETS = {
    'lysozyme':       {'pdb': '1LYZ', 'chain': 'A'},
    'insulin_a_chain': {'pdb': '3I40', 'chain': 'A'},
}

info_line("="*70)
info_line("FINAL: PLATONIC vs CRYSTALLOGRAPHIC STRUCTURAL COMPARISON")
info_line("="*70)

all_data = {}

for name, cfg in TARGETS.items():
    info_line(f"\n{'─'*70}")
    info_line(f"PROTEIN: {name}")
    
    # Platonic
    with open(os.path.join(OUT, f'{name}_platonic.pdb')) as f:
        plat_text = f.read()
    plat_res = extract_backbone(plat_text, 'A')
    plat_pp = compute_phi_psi(plat_res)
    
    # Crystal
    crys_text = fetch_pdb(cfg['pdb'])
    if not crys_text:
        info_line("  FAILED to fetch crystal structure")
        continue
    crys_res = extract_backbone(crys_text, cfg['chain'])
    crys_pp = compute_phi_psi(crys_res)
    
    plat_keys = sorted(plat_res.keys())
    crys_keys = sorted(crys_res.keys())
    plat_seq = ''.join(plat_res[k]['res'] for k in plat_keys)
    crys_seq = ''.join(crys_res[k]['res'] for k in crys_keys)
    
    info_line(f"  Platonic: {len(plat_keys)} residues  seq: {plat_seq[:50]}...")
    info_line(f"  Crystal:  {len(crys_keys)} residues  seq: {crys_seq[:50]}...")
    
    # Sequence match
    min_len = min(len(plat_keys), len(crys_keys))
    matches = sum(1 for i in range(min_len) if plat_keys[i] < len(plat_seq) and 
                  crys_keys[i] < len(crys_seq) and 
                  plat_res[plat_keys[i]]['res'] == crys_res[crys_keys[i]]['res'])
    identity = matches / max(len(plat_keys), len(crys_keys)) * 100
    info_line(f"  Sequence identity: {identity:.1f}% ({matches}/{max(len(plat_keys),len(crys_keys))})")
    
    # Ramachandran
    plat_rama = {'alpha':0,'beta':0,'left':0,'ppii':0,'other':0,'none':0}
    crys_rama = {'alpha':0,'beta':0,'left':0,'ppii':0,'other':0,'none':0}
    for rn, d in plat_pp.items():
        plat_rama[ramachandran_region(d['phi'], d['psi'])] += 1
    for rn, d in crys_pp.items():
        crys_rama[ramachandran_region(d['phi'], d['psi'])] += 1
    
    n_plat = len(plat_pp); n_crys = len(crys_pp)
    info_line(f"\n  RAMACHANDRAN DISTRIBUTION:")
    info_line(f"  {'Region':<10} {'Platonic':>10} {'Crystal':>10} {'Δ':>8}")
    for r in ['alpha','beta','ppii','left','other','none']:
        info_line(f"  {r:<10} {plat_rama[r]/n_plat*100:>9.1f}% {crys_rama[r]/n_crys*100:>9.1f}% {plat_rama[r]/n_plat*100 - crys_rama[r]/n_crys*100:>+7.1f}%")
    
    # Phi/Psi for residues with complete backbone
    phi_diffs, psi_diffs = [], []
    for i in range(min_len):
        pk, ck = plat_keys[i], crys_keys[i]
        pp = plat_pp.get(pk, {}); cp = crys_pp.get(ck, {})
        if pp.get('phi') is not None and cp.get('phi') is not None:
            phi_diffs.append(abs(pp['phi'] - cp['phi']))
        if pp.get('psi') is not None and cp.get('psi') is not None:
            psi_diffs.append(abs(pp['psi'] - cp['psi']))
    
    n_comp = len(phi_diffs)
    info_line(f"\n  PHI/PSI COMPARISON ({n_comp} comparable residues):")
    info_line(f"  Mean |Δφ|: {np.mean(phi_diffs):.1f}°  |  Mean |Δψ|: {np.mean(psi_diffs):.1f}°")
    info_line(f"  Median |Δφ|: {np.median(phi_diffs):.1f}°  |  Median |Δψ|: {np.median(psi_diffs):.1f}°")
    
    # Kabsch RMSD
    plat_ca = [plat_res[k]['CA'] for k in plat_keys if plat_res[k]['CA']]
    crys_ca = [crys_res[k]['CA'] for k in crys_keys[:len(plat_ca)] if crys_res[k]['CA']]
    min_ca = min(len(plat_ca), len(crys_ca))
    rmsd_val, q_rot, p_c = kabsch(plat_ca[:min_ca], crys_ca[:min_ca])
    info_line(f"\n  KABSCH RMSD: {rmsd_val:.2f} Å over {min_ca} CA atoms")
    
    # Per-residue deviation
    per_res = np.sqrt(np.sum((p_c - q_rot)**2, axis=1))
    info_line(f"  Per-residue: mean={np.mean(per_res):.2f} Å, median={np.median(per_res):.2f} Å, max={np.max(per_res):.2f} Å (res {np.argmax(per_res)+1})")
    
    # Top 5 deviating residues
    top5 = np.argsort(per_res)[-5:][::-1]
    info_line(f"  Top 5 deviating residues:")
    for idx in top5:
        aa = plat_res[plat_keys[idx]]['res'] if idx < len(plat_keys) else '?'
        info_line(f"    Res {idx+1} ({aa}): {per_res[idx]:.2f} Å")
    
    all_data[name] = {
        'platonic_residues': len(plat_keys),
        'crystal_residues': len(crys_keys),
        'sequence_identity_pct': round(identity, 1),
        'platonic_rama': plat_rama,
        'crystal_rama': crys_rama,
        'mean_phi_diff': round(np.mean(phi_diffs), 1) if phi_diffs else None,
        'mean_psi_diff': round(np.mean(psi_diffs), 1) if psi_diffs else None,
        'kabsch_rmsd': round(rmsd_val, 2),
        'mean_per_res': round(np.mean(per_res), 2),
        'max_per_res': round(np.max(per_res), 2),
    }

with open(os.path.join(OUT, 'final_comparison.json'), 'w') as f:
    json.dump(all_data, f, indent=2)

info_line(f"\n{'='*70}")
info_line("Final comparison complete → final_comparison.json")
