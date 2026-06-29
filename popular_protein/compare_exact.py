#!/usr/bin/env python3
"""Compare exact platonic folds against crystal structures."""
import json, math, sys, os, numpy as np
from pathlib import Path
from shared.rich_output import *


OUT = Path(__file__).parent

def parse_ca_atoms(pdb_path, chain='A'):
    """Extract CA coordinates from PDB."""
    coords = []
    res_nums = []
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                atom_name = line[12:16].strip()
                ch = line[21:22]
                if atom_name == 'CA' and ch == chain:
                    res_num = int(line[22:26])
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords.append((x, y, z))
                    res_nums.append(res_num)
    return coords, res_nums

def parse_exact_ca(exact_data):
    """Get CA coordinates from exact results."""
    return [(c[0], c[1], c[2]) for c in exact_data['ca_coords']]

def kabsch_rmsd(P, Q):
    """Kabsch-aligned RMSD."""
    P = np.array(P, dtype=float)
    Q = np.array(Q, dtype=float)
    p_cent = P.mean(axis=0)
    q_cent = Q.mean(axis=0)
    P_cent = P - p_cent
    Q_cent = Q - q_cent
    C = P_cent.T @ Q_cent
    V, S, Wt = np.linalg.svd(C)
    d = np.sign(np.linalg.det(V @ Wt))
    D = np.diag([1, 1, d])
    R = V @ D @ Wt
    P_rot = P_cent @ R
    diff = P_rot - Q_cent
    rmsd = np.sqrt(np.mean(np.sum(diff**2, axis=1)))
    per_res = np.sqrt(np.sum(diff**2, axis=1))
    return rmsd, per_res.tolist()

# Load exact results
with open(OUT / 'exact_phipsi_results.json') as f:
    exact_data = json.load(f)

# Load crystal phi/psi
with open(OUT / 'crystal_phipsi.json') as f:
    crystal_phi = json.load(f)

# Load comparison for old results
with open(OUT / 'comprehensive_comparison_results.json') as f:
    old_comp = json.load(f)

# Map: protein name -> (pdb_file, chain, n_res_expected)
CRYSTAL_MAP = {
    'lysozyme': ('1LYZ.pdb', 'A', 129),
    'insulin_a_chain': ('3I40.pdb', 'A', 21),
    'insulin_b_chain': ('3I40.pdb', 'B', 30),
    'gfp': ('2Y0G.pdb', 'A', 238),
}

results = {}

for name, (pdb_file, chain, n_expected) in CRYSTAL_MAP.items():
    if name not in exact_data:
        print(f"SKIP {name}: not in exact data")
        continue
    
    pdb_path = OUT / pdb_file
    if not pdb_path.exists():
        print(f"SKIP {name}: {pdb_file} not found")
        continue
    
    # Parse crystal CA
    crystal_ca, crystal_resnums = parse_ca_atoms(pdb_path, chain)
    print(f"\n{name}: crystal {len(crystal_ca)} CA, expected {n_expected}")
    
    # Exact CA
    exact_ca = parse_exact_ca(exact_data[name])
    info_line(f"  exact: {len(exact_ca)} CA")
    
    # Trim to matching length
    n = min(len(exact_ca), len(crystal_ca), n_expected)
    exact_ca_n = exact_ca[:n]
    crystal_ca_n = crystal_ca[:n]
    
    if n < 5:
        info_line(f"  SKIP: too few residues ({n})")
        continue
    
    # Kabsch RMSD
    rmsd, per_res = kabsch_rmsd(exact_ca_n, crystal_ca_n)
    
    # Compare phi/psi
    exact_phipsi = exact_data[name].get('phipsi', [])
    crystal_key = f"{pdb_file.replace('.pdb','')}_{chain}"
    
    phi_diffs = []
    psi_diffs = []
    if crystal_key in crystal_phi:
        cp = crystal_phi[crystal_key]['phi_psi']
        for ep in exact_phipsi:
            res = str(ep['res'])
            if res in cp and cp[res]['phi'] is not None:
                phi_diffs.append(abs(ep['phi'] - cp[res]['phi']))
            if res in cp and cp[res]['psi'] is not None:
                psi_diffs.append(abs(ep['psi'] - cp[res]['psi']))
    
    # Old RMSD
    old_rmsd = old_comp.get(name, {}).get('kabsch_rmsd', None)
    
    result = {
        'n_residues': n,
        'kabsch_rmsd': round(rmsd, 2),
        'mean_per_res': round(np.mean(per_res), 2),
        'median_per_res': round(np.median(per_res), 2),
        'max_per_res': round(np.max(per_res), 2),
        'phi_diff_mean': round(np.mean(phi_diffs), 1) if phi_diffs else None,
        'psi_diff_mean': round(np.mean(psi_diffs), 1) if psi_diffs else None,
        'old_rmsd': old_rmsd,
        'rmsd_improvement': round(old_rmsd - rmsd, 2) if old_rmsd else None,
    }
    
    results[name] = result
    info_line(f"  Kabsch RMSD: {rmsd:.2f} Å")
    info_line(f"  Mean per-res: {np.mean(per_res):.2f} Å")
    info_line(f"  Old RMSD: {old_rmsd} Å")
    if old_rmsd:
        improvement = old_rmsd - rmsd
        pct = 100 * improvement / old_rmsd
        info_line(f"  Improvement: {improvement:.2f} Å ({pct:.1f}%)")
    if phi_diffs:
        info_line(f"  φ mean diff: {np.mean(phi_diffs):.1f}°")
    if psi_diffs:
        info_line(f"  ψ mean diff: {np.mean(psi_diffs):.1f}°")

# Also handle small peptides — compare old canonical vs new exact
info_line("\n--- Small Peptides (no crystal) ---")
for name in ['acth', 'beta_endorphin', 'alpha_msh']:
    if name not in exact_data:
        continue
    ed = exact_data[name]
    phis = [e['phi'] for e in ed['phipsi']]
    psis = [e['psi'] for e in ed['phipsi']]
    print(f"{name}: φ={np.mean(phis):.1f}±{np.std(phis):.1f}°, ψ={np.mean(psis):.1f}±{np.std(psis):.1f}°")

with open(OUT / 'exact_comparison_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved to exact_comparison_results.json")
