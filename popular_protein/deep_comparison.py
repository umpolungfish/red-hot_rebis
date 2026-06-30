#!/usr/bin/env python3
"""
Deep Comparison: Platonic vs Crystallographic — with Ramachandran, SS, and per-residue analysis.
"""
import sys, os, json, math, urllib.request
import numpy as np
from shared.rich_output import *


OUT = os.path.dirname(__file__)

# ─── Kabsch superposition ───────────────────────────────────
def kabsch(P, Q):
    p = np.array(P, dtype=float)
    q = np.array(Q, dtype=float)
    p_c = p - p.mean(axis=0)
    q_c = q - q.mean(axis=0)
    C = np.dot(p_c.T, q_c)
    V, S, Wt = np.linalg.svd(C)
    d = np.sign(np.linalg.det(np.dot(V, Wt)))
    D = np.eye(3); D[2,2] = d
    R = np.dot(V, np.dot(D, Wt))
    q_rot = np.dot(q_c, R.T)
    rmsd = math.sqrt(np.sum((p_c - q_rot)**2) / len(p))
    return rmsd, q_rot, p_c, R

# ─── PDB helpers ────────────────────────────────────────────
aa3to1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
          'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
          'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

def extract_atoms(pdb_text, chain='A'):
    """Extract N, CA, C coordinates for Ramachandran analysis."""
    residues = {}
    for line in pdb_text.split('\n'):
        if line.startswith('ATOM') or line.startswith('HETATM'):
            atom = line[12:16].strip()
            ch = line[21:22].strip()
            if ch != chain: continue
            try:
                res_num = int(line[22:26])
                x,y,z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                if res_num not in residues:
                    residues[res_num] = {'N':None,'CA':None,'C':None,'res':aa3to1.get(line[17:20].strip(),'X')}
                if atom in ('N','CA','C'):
                    residues[res_num][atom] = (x,y,z)
            except: pass
    return residues

def compute_phi_psi(residues):
    """Compute phi/psi angles for each residue."""
    result = {}
    sorted_keys = sorted(residues.keys())
    for i, rn in enumerate(sorted_keys):
        r = residues[rn]
        phi, psi = None, None
        # Phi: C(i-1)-N(i)-CA(i)-C(i)
        if i > 0:
            prev = residues[sorted_keys[i-1]]
            if all(prev.get(a) for a in ['C']) and all(r.get(a) for a in ['N','CA','C']):
                phi = dihedral(prev['C'], r['N'], r['CA'], r['C'])
        # Psi: N(i)-CA(i)-C(i)-N(i+1)
        if i < len(sorted_keys)-1:
            nxt = residues[sorted_keys[i+1]]
            if all(r.get(a) for a in ['N','CA','C']) and nxt.get('N'):
                psi = dihedral(r['N'], r['CA'], r['C'], nxt['N'])
        result[rn] = {'phi': phi, 'psi': psi, 'res': r['res']}
    return result

def dihedral(p1, p2, p3, p4):
    """Compute dihedral angle in degrees."""
    b1 = np.array(p2) - np.array(p1)
    b2 = np.array(p3) - np.array(p2)
    b3 = np.array(p4) - np.array(p3)
    n1 = np.cross(b1, b2)
    n2 = np.cross(b2, b3)
    n1 /= np.linalg.norm(n1)
    n2 /= np.linalg.norm(n2)
    b2 /= np.linalg.norm(b2)
    m1 = np.cross(n1, b2)
    x = np.dot(n1, n2)
    y = np.dot(m1, n2)
    return math.degrees(math.atan2(y, x))

def fetch_pdb(pdb_id):
    try:
        req = urllib.request.Request(f'https://files.rcsb.org/download/{pdb_id}.pdb',
                                     headers={'User-Agent': 'Rebis/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        return None

# ─── Ramachandran classification ──────────────────────────────
def ramachandran_region(phi, psi):
    """Classify phi/psi into Ramachandran regions."""
    if phi is None or psi is None:
        return 'none'
    # Core regions
    if -180 <= phi <= -30 and -100 <= psi <= 30:
        return 'alpha'   # Alpha-helix / right-handed
    elif -180 <= phi <= -30 and 60 <= psi <= 180:
        return 'beta'    # Beta-sheet
    elif 30 <= phi <= 120 and -60 <= psi <= 60:
        return 'left'    # Left-handed helix
    elif -180 <= phi <= -30 and -180 <= psi <= -100:
        return 'ppii'    # Polyproline II
    else:
        return 'other'

# ─── Main comparison ─────────────────────────────────────────
TARGETS = {
    'lysozyme':       {'pdb': '1LYZ', 'chain': 'A'},
    'insulin_a_chain': {'pdb': '3I40', 'chain': 'A'},
}

info_line("="*70)
info_line("DEEP STRUCTURAL COMPARISON — PLATONIC vs CRYSTALLOGRAPHIC")
info_line("="*70)

all_data = {}

for name, cfg in TARGETS.items():
    info_line(f"\n{'─'*70}")
    info_line(f"PROTEIN: {name}")
    
    # Load platonic
    plat_path = os.path.join(OUT, f'{name}_platonic.pdb')
    with open(plat_path) as f:
        plat_text = f.read()
    plat_res = extract_atoms(plat_text, 'A')
    plat_pp = compute_phi_psi(plat_res)
    
    # Load crystal
    crys_text = fetch_pdb(cfg['pdb'])
    if not crys_text:
        continue
    crys_res = extract_atoms(crys_text, cfg['chain'])
    crys_pp = compute_phi_psi(crys_res)
    
    # Match residues by sequence
    plat_keys = sorted(plat_res.keys())
    crys_keys = sorted(crys_res.keys())
    
    # Build sequence-based alignment
    plat_seq = ''.join(plat_res[k]['res'] for k in plat_keys)
    crys_seq = ''.join(crys_res[k]['res'] for k in crys_keys)
    
    info_line(f"  Platonic: {len(plat_keys)} residues: {plat_seq[:40]}...")
    info_line(f"  Crystal:  {len(crys_keys)} residues: {crys_seq[:40]}...")
    
    # Ramachandran stats
    plat_rama = {'alpha':0,'beta':0,'left':0,'ppii':0,'other':0,'none':0}
    crys_rama = {'alpha':0,'beta':0,'left':0,'ppii':0,'other':0,'none':0}
    
    for rn, data in plat_pp.items():
        region = ramachandran_region(data['phi'], data['psi'])
        plat_rama[region] = plat_rama.get(region, 0) + 1
    for rn, data in crys_pp.items():
        region = ramachandran_region(data['phi'], data['psi'])
        crys_rama[region] = crys_rama.get(region, 0) + 1
    
    info_line(f"\n  RAMACHANDRAN DISTRIBUTION:")
    info_line(f"  {'Region':<12} {'Platonic':>10} {'Crystal':>10} {'Delta':>10}")
    info_line(f"  {'─'*12} {'─'*10} {'─'*10} {'─'*10}")
    for region in ['alpha','beta','ppii','left','other','none']:
        pct_p = plat_rama[region]/len(plat_pp)*100 if plat_pp else 0
        pct_c = crys_rama[region]/len(crys_pp)*100 if crys_pp else 0
        info_line(f"  {region:<12} {pct_p:>9.1f}% {pct_c:>9.1f}% {pct_p-pct_c:>+9.1f}%")
    
    # Phi/Psi comparison for matching residues
    min_len = min(len(plat_keys), len(crys_keys))
    phi_diffs = []
    psi_diffs = []
    for i in range(min_len):
        pk = plat_keys[i]
        ck = crys_keys[i]
        pp = plat_pp.get(pk, {})
        cp = crys_pp.get(ck, {})
        if pp.get('phi') is not None and cp.get('phi') is not None:
            phi_diffs.append(abs(pp['phi'] - cp['phi']))
        if pp.get('psi') is not None and cp.get('psi') is not None:
            psi_diffs.append(abs(pp['psi'] - cp['psi']))
    
    if phi_diffs:
        info_line(f"\n  PHI/PSI DEVIATION:")
        info_line(f"  Mean |Δφ|: {np.mean(phi_diffs):.1f}°  Median: {np.median(phi_diffs):.1f}°  Max: {np.max(phi_diffs):.1f}°")
        info_line(f"  Mean |Δψ|: {np.mean(psi_diffs):.1f}°  Median: {np.median(psi_diffs):.1f}°  Max: {np.max(psi_diffs):.1f}°")
    
    # Kabsch RMSD
    plat_ca = [plat_res[k]['CA'] for k in plat_keys if plat_res[k]['CA']]
    crys_ca = [crys_res[k]['CA'] for k in crys_keys[:len(plat_ca)] if crys_res[k]['CA']]
    min_ca = min(len(plat_ca), len(crys_ca))
    rmsd_val, _, _, _ = kabsch(plat_ca[:min_ca], crys_ca[:min_ca])
    info_line(f"\n  KABSCH RMSD: {rmsd_val:.2f} Å ({min_ca} CA atoms)")
    
    all_data[name] = {
        'platonic_residues': len(plat_keys),
        'crystal_residues': len(crys_keys),
        'platonic_rama': plat_rama,
        'crystal_rama': crys_rama,
        'mean_phi_diff': round(np.mean(phi_diffs),1) if phi_diffs else None,
        'mean_psi_diff': round(np.mean(psi_diffs),1) if psi_diffs else None,
        'kabsch_rmsd': round(rmsd_val,2),
    }

# Save
with open(os.path.join(OUT, 'deep_comparison.json'), 'w') as f:
    json.dump(all_data, f, indent=2)

info_line(f"\n{'='*70}")
info_line("Deep comparison complete → deep_comparison.json")
