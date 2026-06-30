#!/usr/bin/env python3
"""Generate platonic PDB structures for all popular proteins."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clink.datasets.protein_structure import generate_protein_structure, BackboneBuilder
from shared.rich_output import *


with open(os.path.join(os.path.dirname(__file__), 'platonic_folds.json')) as f:
    data = json.load(f)

OUT = os.path.dirname(__file__)
results = {}

for name, info in data.items():
    seq = info['sequence']
    info_line(f"\n{'='*60}")
    info_line(f"PROTEIN: {name}  ({len(seq)} AA)")
    info_line(f"SEQ: {seq[:50]}{'...' if len(seq)>50 else ''}")
    
    struct = generate_protein_structure(seq, name)
    builder = BackboneBuilder(seq, struct.secondary_structure)
    pdb_str = builder.to_pdb(struct.residues, title=f'{name.upper()} PLATONIC FOLD')
    
    pdb_path = os.path.join(OUT, f'{name}_platonic.pdb')
    with open(pdb_path, 'w') as fout:
        fout.write(pdb_str)
    
    ca_coords = []
    for res in struct.residues:
        for atom in res.atoms:
            if atom.name.strip() == 'CA':
                ca_coords.append((atom.x, atom.y, atom.z))
                break
    
    results[name] = {
        'sequence': seq,
        'length': len(seq),
        'ss': struct.secondary_structure,
        'n_helix': struct.n_helix,
        'n_strand': struct.n_strand,
        'n_coil': struct.n_coil,
        'pdb_path': pdb_path,
        'pdb_size': len(pdb_str),
    }
    
    info_line(f"  SS: {struct.secondary_structure}")
    info_line(f"  {struct.n_helix}H / {struct.n_strand}E / {struct.n_coil}C")
    info_line(f"  PDB → {pdb_path} ({len(pdb_str)} bytes)")

with open(os.path.join(OUT, 'structure_summary.json'), 'w') as f:
    json.dump(results, f, indent=2)

info_line(f"\n{'='*60}")
success_line(f"DONE. {len(results)} structures saved.")
