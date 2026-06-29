#!/usr/bin/env python3
"""Compare platonic (first-principles) structures with crystallographic PDB data."""
import sys, os, json, math, urllib.request, io, gzip

OUT = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clink.datasets.protein_structure import generate_protein_structure, BackboneBuilder
from shared.rich_output import *


# Map protein names to PDB entries
PDB_MAP = {
    'lysozyme': ('1LYZ', 'A'),
    'gfp': ('1EMA', 'A'),
    'insulin_a_chain': (None, 'A'),   # insulin A-chain needs special handling
    'insulin_b_chain': (None, 'B'),
}

def fetch_pdb(pdb_id):
    """Fetch PDB file from RCSB."""
    url = f'https://files.rcsb.org/download/{pdb_id}.pdb'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Rebis/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        info_line(f'  [WARN] Cannot fetch {pdb_id}: {e}')
        return None

def extract_ca_coords_from_pdb(pdb_text, chain='A'):
    """Extract CA coordinates from PDB text for given chain."""
    coords = []
    sequence = []
    aa3to1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
              'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
              'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
    for line in pdb_text.split('\n'):
        if line.startswith('ATOM') or line.startswith('HETATM'):
            atom_name = line[12:16].strip()
            res_name = line[17:20].strip()
            chain_id = line[21:22].strip()
            if chain_id == chain and atom_name == 'CA':
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords.append((x, y, z))
                    aa = aa3to1.get(res_name, 'X')
                    sequence.append(aa)
                except:
                    pass
    return coords, ''.join(sequence)

def rmsd(coords1, coords2):
    """Compute RMSD between two coordinate lists (must be same length)."""
    if len(coords1) != len(coords2):
        return None, len(coords1), len(coords2)
    n = len(coords1)
    if n == 0:
        return 0.0, 0, 0
    ssq = 0.0
    for (x1,y1,z1), (x2,y2,z2) in zip(coords1, coords2):
        ssq += (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2
    return math.sqrt(ssq / n), n, n

def extract_ca_from_platonic(pdb_path):
    """Extract CA coords and sequence from our generated PDB."""
    with open(pdb_path) as f:
        pdb_text = f.read()
    return extract_ca_coords_from_pdb(pdb_text, 'A')

results = {}
for name in ['lysozyme', 'gfp', 'insulin_a_chain']:
    pdb_id, chain = PDB_MAP.get(name, (None, 'A'))
    
    pdb_path = os.path.join(OUT, f'{name}_platonic.pdb')
    plat_coords, plat_seq = extract_ca_from_platonic(pdb_path)
    
    result = {
        'name': name,
        'platonic_sequence': plat_seq,
        'platonic_length': len(plat_seq),
        'pdb_id': pdb_id,
    }
    
    if pdb_id:
        pdb_text = fetch_pdb(pdb_id)
        if pdb_text:
            crys_coords, crys_seq = extract_ca_coords_from_pdb(pdb_text, chain)
            result['crystal_sequence'] = crys_seq
            result['crystal_length'] = len(crys_seq)
            
            # Compute RMSD if sequences comparable
            seq_match = 0
            for a, b in zip(plat_seq, crys_seq):
                if a == b:
                    seq_match += 1
            
            result['sequence_identity'] = seq_match / max(len(plat_seq), len(crys_seq)) if max(len(plat_seq), len(crys_seq)) > 0 else 0
            
            if len(plat_coords) == len(crys_coords):
                rmsd_val, n1, n2 = rmsd(plat_coords, crys_coords)
                result['rmsd'] = rmsd_val
            else:
                # Try to align by trimming to common length
                min_len = min(len(plat_coords), len(crys_coords))
                rmsd_val, _, _ = rmsd(plat_coords[:min_len], crys_coords[:min_len])
                result['rmsd_trimmed'] = rmsd_val
                result['rmsd_note'] = f'Trimmed from {len(plat_coords)}/{len(crys_coords)} to {min_len}'
    
    results[name] = result
    print(f"\n{'='*60}")
    print(f"PROTEIN: {name}")
    info_line(f"  Platonic: {len(plat_seq)} AA, {len(plat_coords)} CA atoms")
    if 'crystal_sequence' in result:
        info_line(f"  Crystal ({pdb_id}): {len(result['crystal_sequence'])} AA, {len(crys_coords)} CA atoms")
        info_line(f"  Sequence identity: {result['sequence_identity']*100:.1f}%")
        if 'rmsd' in result:
            info_line(f"  RMSD: {result['rmsd']:.2f} Å")
        elif 'rmsd_trimmed' in result:
            info_line(f"  RMSD (trimmed): {result['rmsd_trimmed']:.2f} Å")
            info_line(f"  Note: {result['rmsd_note']}")

# Save results
with open(os.path.join(OUT, 'comparison_results.json'), 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n{'='*60}")
info_line("Comparison complete. Results saved.")
