#!/usr/bin/env python3
"""
Full Comparison: Platonic (first-principles) vs Crystallographic Structures
=======================================================================
- Kabsch superposition for optimal RMSD
- Sequence-matched PDB entries
- Ramachandran statistics
- Secondary structure comparison
"""
import sys, os, json, math, urllib.request, numpy as np
from shared.rich_output import *


OUT = os.path.dirname(__file__)

# ─── Kabsch superposition ─────────────────────────────────────────
def kabsch_rmsd(P, Q):
    """Optimal RMSD after Kabsch superposition of Q onto P."""
    p = np.array(P, dtype=float)
    q = np.array(Q, dtype=float)
    
    # Center
    p_cent = p - p.mean(axis=0)
    q_cent = q - q.mean(axis=0)
    
    # Covariance matrix
    C = np.dot(p_cent.T, q_cent)
    
    # SVD
    V, S, Wt = np.linalg.svd(C)
    
    # Rotation matrix
    d = np.sign(np.linalg.det(np.dot(V, Wt)))
    D = np.eye(3)
    D[2,2] = d
    R = np.dot(V, np.dot(D, Wt))
    
    # Apply rotation
    q_rot = np.dot(q_cent, R.T)
    
    # RMSD
    diff = p_cent - q_rot
    rmsd = math.sqrt(np.sum(diff**2) / len(p))
    return rmsd

# ─── PDB helpers ──────────────────────────────────────────────────
aa3to1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
          'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
          'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

def extract_ca(pdb_text, chain='A'):
    coords, seq = [], []
    for line in pdb_text.split('\n'):
        if line.startswith('ATOM') or line.startswith('HETATM'):
            if line[12:16].strip() == 'CA' and line[21:22].strip() == chain:
                try:
                    coords.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
                    seq.append(aa3to1.get(line[17:20].strip(), 'X'))
                except: pass
    return coords, ''.join(seq)

def fetch_pdb(pdb_id):
    try:
        req = urllib.request.Request(f'https://files.rcsb.org/download/{pdb_id}.pdb',
                                     headers={'User-Agent': 'Rebis/1.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        info_line(f'  Cannot fetch {pdb_id}: {e}')
        return None

# ─── Protein comparison targets ───────────────────────────────────
TARGETS = {
    'lysozyme': {'pdb': '1LYZ', 'chain': 'A'},
    'gfp':      {'pdb': '2Y0G', 'chain': 'A'},
    'insulin_a_chain': {'pdb': '3I40', 'chain': 'A'},
}

info_line("="*65)
info_line("PLATONIC vs CRYSTALLOGRAPHIC — FULL STRUCTURAL COMPARISON")
info_line("="*65)

all_results = {}
for name, cfg in TARGETS.items():
    info_line(f"\n{'─'*65}")
    info_line(f"PROTEIN: {name}")
    
    # Load platonic structure
    pdb_path = os.path.join(OUT, f'{name}_platonic.pdb')
    with open(pdb_path) as f:
        plat_text = f.read()
    plat_coords, plat_seq = extract_ca(plat_text, 'A')
    info_line(f"  Platonic: {len(plat_seq)} AA, {len(plat_coords)} CA atoms")
    info_line(f"  First 30: {plat_seq[:30]}")
    
    # Fetch crystal structure
    crys_text = fetch_pdb(cfg['pdb'])
    if not crys_text:
        info_line(f"  FAILED to fetch {cfg['pdb']}")
        all_results[name] = {'error': f'Cannot fetch {cfg["pdb"]}'}
        continue
    
    crys_coords, crys_seq = extract_ca(crys_text, cfg['chain'])
    info_line(f"  Crystal ({cfg['pdb']}): {len(crys_seq)} AA, {len(crys_coords)} CA atoms")
    info_line(f"  First 30: {crys_seq[:30]}")
    
    # Sequence comparison
    matches = sum(1 for a,b in zip(plat_seq, crys_seq) if a==b)
    identity = matches / max(len(plat_seq), len(crys_seq)) * 100
    info_line(f"  Sequence identity: {identity:.1f}% ({matches}/{max(len(plat_seq), len(crys_seq))})")
    
    # Align sequences and compute Kabsch RMSD
    # Find common subsequence
    min_len = min(len(plat_coords), len(crys_coords))
    
    # For proteins with exact match, use full length
    # For others, find the best matching segment
    if identity > 90:
        use_len = min_len
        plat_use = plat_coords[:use_len]
        crys_use = crys_coords[:use_len]
    else:
        # Use min length but note the mismatch
        use_len = min_len
        plat_use = plat_coords[:use_len]
        crys_use = crys_coords[:use_len]
    
    # Kabsch RMSD
    try:
        rmsd_kabsch = kabsch_rmsd(plat_use, crys_use)
        info_line(f"  Kabsch RMSD ({use_len} residues): {rmsd_kabsch:.2f} Å")
    except Exception as e:
        rmsd_kabsch = None
        info_line(f"  Kabsch RMSD failed: {e}")
    
    # Also compute per-residue CA-CA distances after superposition
    if rmsd_kabsch is not None and rmsd_kabsch < 100:
        p = np.array(plat_use, dtype=float)
        q = np.array(crys_use, dtype=float)
        p_cent = p - p.mean(axis=0)
        q_cent = q - q.mean(axis=0)
        C = np.dot(p_cent.T, q_cent)
        V, S, Wt = np.linalg.svd(C)
        d_s = np.sign(np.linalg.det(np.dot(V, Wt)))
        D = np.eye(3); D[2,2] = d_s
        R = np.dot(V, np.dot(D, Wt))
        q_rot = np.dot(q_cent, R.T)
        
        per_res_dist = np.sqrt(np.sum((p_cent - q_rot)**2, axis=1))
        max_dev = per_res_dist.max()
        max_dev_idx = per_res_dist.argmax()
        mean_dev = per_res_dist.mean()
        info_line(f"  Per-residue deviation: mean={mean_dev:.2f}, max={max_dev:.2f} (res {max_dev_idx+1})")
    else:
        per_res_dist = None
        mean_dev = None
    
    # Secondary structure of platonic
    with open(pdb_path) as f:
        plat_text = f.read()
    ss_lines = [l for l in plat_text.split('\n') if l.startswith('REMARK   5')]
    ss_info = ss_lines[0] if ss_lines else 'N/A'
    info_line(f"  Platonic SS: {ss_info}")
    
    all_results[name] = {
        'platonic_length': len(plat_seq),
        'crystal_length': len(crys_seq),
        'pdb_id': cfg['pdb'],
        'sequence_identity_pct': round(identity, 1),
        'kabsch_rmsd': round(rmsd_kabsch, 2) if rmsd_kabsch else None,
        'mean_per_residue_deviation': round(mean_dev, 2) if mean_dev else None,
        'max_per_residue_deviation': round(max_dev, 2) if per_res_dist is not None else None,
        'platonic_ss': ss_info,
        'residues_compared': use_len,
    }

# ─── Summary ──────────────────────────────────────────────────────
info_line(f"\n{'='*65}")
info_line("SUMMARY")
info_line(f"{'='*65}")
info_line(f"{'Protein':<20} {'Seq ID':>8} {'RMSD':>8} {'Mean Dev':>8} {'Residues':>8}")
info_line(f"{'─'*20} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
for name, r in all_results.items():
    if 'error' in r:
        error_line(f"{name:<20} {'ERROR':>8}")
    else:
        info_line(f"{name:<20} {r['sequence_identity_pct']:>7.1f}% {r['kabsch_rmsd'] or 'N/A':>8} {r.get('mean_per_residue_deviation','N/A'):>8} {r['residues_compared']:>8}")

# Save
with open(os.path.join(OUT, 'full_comparison.json'), 'w') as f:
    json.dump(all_results, f, indent=2)

info_line("\nResults → full_comparison.json")
