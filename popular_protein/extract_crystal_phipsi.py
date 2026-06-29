#!/usr/bin/env python3
"""Extract phi/psi from crystal structure PDBs for comparison."""
import sys, json, math, os
from pathlib import Path
from shared.rich_output import *


OUT = Path(__file__).parent

def parse_pdb_atoms(pdb_path):
    """Parse ATOM records from PDB, return {resnum: {atom_name: (x,y,z)}}."""
    atoms = {}
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                atom_name = line[12:16].strip()
                res_name = line[17:20].strip()
                chain = line[21:22]
                res_num = int(line[22:26])
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                key = (chain, res_num)
                if key not in atoms:
                    atoms[key] = {}
                atoms[key][atom_name] = (x, y, z)
    return atoms

def compute_dihedral(p1, p2, p3, p4):
    """Compute dihedral angle p1-p2-p3-p4 in degrees [-180, 180]."""
    b1 = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
    b2 = (p3[0]-p2[0], p3[1]-p2[1], p3[2]-p2[2])
    b3 = (p4[0]-p3[0], p4[1]-p3[1], p4[2]-p3[2])
    
    # Normal to plane p2-p3-p4
    n1 = (b1[1]*b2[2]-b1[2]*b2[1], b1[2]*b2[0]-b1[0]*b2[2], b1[0]*b2[1]-b1[1]*b2[0])
    n2 = (b2[1]*b3[2]-b2[2]*b3[1], b2[2]*b3[0]-b2[0]*b3[2], b2[0]*b3[1]-b2[1]*b3[0])
    
    # Normalize
    n1m = math.sqrt(n1[0]**2 + n1[1]**2 + n1[2]**2)
    n2m = math.sqrt(n2[0]**2 + n2[1]**2 + n2[2]**2)
    if n1m < 1e-10 or n2m < 1e-10:
        return None
    n1 = (n1[0]/n1m, n1[1]/n1m, n1[2]/n1m)
    n2 = (n2[0]/n2m, n2[1]/n2m, n2[2]/n2m)
    
    b2m = math.sqrt(b2[0]**2 + b2[1]**2 + b2[2]**2)
    b2n = (b2[0]/b2m, b2[1]/b2m, b2[2]/b2m)
    
    # cross product
    m1 = (n1[1]*n2[2]-n1[2]*n2[1], n1[2]*n2[0]-n1[0]*n2[2], n1[0]*n2[1]-n1[1]*n2[0])
    y = m1[0]*b2n[0] + m1[1]*b2n[1] + m1[2]*b2n[2]
    x = n1[0]*n2[0] + n1[1]*n2[1] + n1[2]*n2[2]
    
    return math.degrees(math.atan2(y, x))

def extract_phipsi(atoms, chain="A"):
    """Extract phi/psi for each residue."""
    # Build ordered list of residues for the chain
    chain_res = sorted([(num, k[1]) for k in chain_res_keys], key=lambda x: x[0])
    # Actually let me do this differently
    chain_keys = sorted([k for k in atoms.keys() if k[0] == chain], key=lambda k: k[1])
    
    phipsi = {}
    for i, key in enumerate(chain_keys):
        res_num = key[1]
        atom_dict = atoms[key]
        
        phi = None
        psi = None
        
        # phi(i): C(i-1) - N(i) - CA(i) - C(i)
        if i > 0:
            prev_key = chain_keys[i-1]
            prev_atoms = atoms[prev_key]
            if all(a in prev_atoms for a in ['C']) and all(a in atom_dict for a in ['N', 'CA', 'C']):
                phi = compute_dihedral(
                    prev_atoms['C'], atom_dict['N'], atom_dict['CA'], atom_dict['C']
                )
        
        # psi(i): N(i) - CA(i) - C(i) - N(i+1)
        if i < len(chain_keys) - 1:
            next_key = chain_keys[i+1]
            next_atoms = atoms[next_key]
            if all(a in atom_dict for a in ['N', 'CA', 'C']) and all(a in next_atoms for a in ['N']):
                psi = compute_dihedral(
                    atom_dict['N'], atom_dict['CA'], atom_dict['C'], next_atoms['N']
                )
        
        phipsi[res_num] = {'phi': phi, 'psi': psi}
    
    return phipsi

# Parse each crystal PDB
results = {}

for pdb_name, pdb_file in [('1LYZ', '1LYZ.pdb'), ('3I40', '3I40.pdb'), ('2Y0G', '2Y0G.pdb')]:
    pdb_path = OUT / pdb_file
    if not pdb_path.exists():
        print(f"SKIP {pdb_name}: file not found")
        continue
    
    atoms = parse_pdb_atoms(pdb_path)
    
    # Get all chains
    chains = sorted(set(k[0] for k in atoms.keys()))
    print(f"{pdb_name}: chains = {chains}, residues = {len(atoms)}")
    
    for chain in chains:
        chain_keys = sorted([k for k in atoms.keys() if k[0] == chain], key=lambda k: k[1])
        phipsi = {}
        
        for i, key in enumerate(chain_keys):
            res_num = key[1]
            atom_dict = atoms[key]
            
            phi = None
            psi = None
            
            # phi(i): C(i-1) - N(i) - CA(i) - C(i)
            if i > 0:
                prev_key = chain_keys[i-1]
                prev_atoms = atoms[prev_key]
                if all(a in prev_atoms for a in ['C']) and all(a in atom_dict for a in ['N', 'CA', 'C']):
                    phi = compute_dihedral(
                        prev_atoms['C'], atom_dict['N'], atom_dict['CA'], atom_dict['C']
                    )
            
            # psi(i): N(i) - CA(i) - C(i) - N(i+1)
            if i < len(chain_keys) - 1:
                next_key = chain_keys[i+1]
                next_atoms = atoms[next_key]
                if all(a in atom_dict for a in ['N', 'CA', 'C']) and all(a in next_atoms for a in ['N']):
                    psi = compute_dihedral(
                        atom_dict['N'], atom_dict['CA'], atom_dict['C'], next_atoms['N']
                    )
            
            phipsi[res_num] = {'phi': phi, 'psi': psi}
        
        key = f"{pdb_name}_{chain}"
        results[key] = {
            'chain': chain,
            'n_res': len(chain_keys),
            'phi_psi': {str(k): v for k, v in phipsi.items()}
        }
        
        # Stats
        phis = [v['phi'] for v in phipsi.values() if v['phi'] is not None]
        psis = [v['psi'] for v in phipsi.values() if v['psi'] is not None]
        if phis:
            info_line(f"  {chain}: {len(chain_keys)} res, phi mean={sum(phis)/len(phis):.1f}, psi mean={sum(psis)/len(psis):.1f}")
        else:
            info_line(f"  {chain}: {len(chain_keys)} res (no dihedrals)")

with open(OUT / 'crystal_phipsi.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nSaved to crystal_phipsi.json")
