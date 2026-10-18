#!/usr/bin/env python3
"""
PDB Validation Pipeline — Path 1 of the Serpent on the Rod.
Downloads PDB structures, runs SerpentRod predictions, compares contacts.

Author: Lando ⊗ ⊙perator
"""
_HELP_EXAMPLES = """  rebis.py run run_pdb_validation"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "scripts/run_pdb_validation.py"
    print(_doc)
    print()
    print("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import sys, os, json, math, urllib.request, tempfile
from typing import List, Tuple, Dict, Set
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rhr_p4rky.serpent_rod import SerpentRod
from shared.rich_output import *

THREE_TO_ONE = {
    "ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C",
    "GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I",
    "LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P",
    "SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V",
}

AA_TO_PREFERRED_CODON = {
    "A":"GCU","R":"CGU","N":"AAU","D":"GAU","C":"UGU",
    "Q":"CAA","E":"GAA","G":"GGU","H":"CAU","I":"AUU",
    "L":"UUG","K":"AAA","M":"AUG","F":"UUU","P":"CCU",
    "S":"UCU","T":"ACU","W":"UGG","Y":"UAU","V":"GUU",
}

def fetch_pdb(pdb_id: str) -> str:
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode()

def extract_sequence(pdb_text: str) -> str:
    seq = ""
    for line in pdb_text.split('\n'):
        if line.startswith("SEQRES"):
            parts = line.split()
            for p in parts[4:]:
                three = p.upper()
                if three in THREE_TO_ONE:
                    seq += THREE_TO_ONE[three]
    return seq

def parse_ca_coords(pdb_text: str) -> Tuple[List[Dict], str]:
    """Read one chain from the first model, choosing one conformer per residue.

    Blank and A alternate locations are preferred, then highest occupancy.
    Residue identifiers are retained beside the coordinate-derived sequence.
    """
    residues = {}
    selected_chain = None
    for line in pdb_text.splitlines():
        if line.startswith('ENDMDL'):
            break
        if not line.startswith('ATOM') or line[12:16].strip() != 'CA':
            continue
        three = line[17:20].strip().upper()
        if three not in THREE_TO_ONE:
            continue
        chain = line[21:22]
        try:
            xyz = tuple(float(line[start:start+8]) for start in (30, 38, 46))
            if not all(math.isfinite(v) for v in xyz):
                raise ValueError('nonfinite coordinate')
            occupancy = float(line[54:60].strip() or 0)
        except ValueError as exc:
            raise ValueError(f'Invalid CA coordinate: {line}') from exc
        if selected_chain is None:
            selected_chain = chain
        if chain != selected_chain:
            continue
        alt = line[16:17]
        key = (chain, line[22:26].strip(), line[26:27])
        preference = (2 if alt == ' ' else 1 if alt == 'A' else 0, occupancy)
        old = residues.get(key)
        if old is not None and old['_preference'] >= preference:
            continue
        residues[key] = dict(one=THREE_TO_ONE[three], x=xyz[0], y=xyz[1],
                             z=xyz[2], chain=chain, residue_id=key[1],
                             insertion_code=key[2], alternate_location=alt,
                             _preference=preference)
    atoms = list(residues.values())
    for atom in atoms:
        atom.pop('_preference')
    return atoms, ''.join(atom['one'] for atom in atoms)

def extract_contacts(atoms: List[Dict], cutoff=8.0, min_dist=4) -> Set[Tuple[int,int]]:
    contacts = set()
    for i in range(len(atoms)):
        for j in range(i+min_dist, len(atoms)):
            dx = atoms[i]["x"] - atoms[j]["x"]
            dy = atoms[i]["y"] - atoms[j]["y"]
            dz = atoms[i]["z"] - atoms[j]["z"]
            d = math.sqrt(dx*dx + dy*dy + dz*dz)
            if d < cutoff:
                contacts.add((i,j))
    return contacts

def protein_to_rna(seq: str) -> str:
    return "".join(AA_TO_PREFERRED_CODON.get(aa, "NNN") for aa in seq)

def validate(pdb_id: str, pdb_text: str) -> Dict:
    info_line(f"\n{'='*60}")
    info_line(f"VALIDATING: {pdb_id}")
    info_line(f"{'='*60}")
    
    # Extract sequence
    declared_seq = extract_sequence(pdb_text)
    info_line(f"SEQRES sequence ({len(declared_seq)} AA): {declared_seq}")
    
    # Parse CA coordinates
    atoms, atom_seq = parse_ca_coords(pdb_text)
    seq = atom_seq
    info_line(f"CA atoms parsed: {len(atoms)} (seq: {atom_seq})")
    
    if len(atoms) < 5:
        return {"pdb_id": pdb_id, "error": "Too few atoms", "sequence": seq}
    
    # Extract experimental contacts
    exp_contacts = extract_contacts(atoms, cutoff=8.0, min_dist=4)
    info_line(f"Experimental contacts (CA<8.0Å, seq_dist≥4): {len(exp_contacts)}")
    
    # Show top contacts
    for i, j in sorted(exp_contacts)[:8]:
        info_line(f"  Contact: {atom_seq[i]}{i} ⟷ {atom_seq[j]}{j}")
    
    # Generate RNA and run SerpentRod
    rna = protein_to_rna(seq)
    info_line(f"Generated RNA ({len(rna)} nt): {rna[:60]}...")
    
    sr = SerpentRod(rna, name=pdb_id)
    result = sr.report()
    
    pred_seq = result["aa_sequence"]
    info_line(f"Predicted AA: {pred_seq} ({len(pred_seq)} AAs)")
    info_line(f"Winding: {result['winding_number']} B4 loops")
    error_line(f"Frobenius: {'✓' if result['frobenius_verified'] else '✗'}")
    
    # Predicted contacts
    pred_contacts = set()
    for c in result["contacts"]:
        pred_contacts.add((c["i"], c["j"]))
    info_line(f"Predicted contacts: {len(pred_contacts)}")
    for c in result["contacts"][:8]:
        aa_i = pred_seq[c["i"]] if c["i"] < len(pred_seq) else "?"
        aa_j = pred_seq[c["j"]] if c["j"] < len(pred_seq) else "?"
        info_line(f"  {aa_i}{c['i']} ⟷ {aa_j}{c['j']}  {c['type']}  conf={c['confidence']}")
    
    # Both contact sets use the same observed-residue sequence and index space.
    # A changed translation cannot be compared by raw indices.
    if pred_seq != atom_seq:
        raise ValueError('Translated sequence differs from observed CA sequence')
    tp = len(pred_contacts & exp_contacts)
    fp = len(pred_contacts - exp_contacts)
    fn = len(exp_contacts - pred_contacts)
    
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-10, precision + recall)
    
    info_line(f"\n  TP={tp}, FP={fp}, FN={fn}")
    info_line(f"  Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
    
    # Check which specific contacts were correctly predicted
    correct = [(i,j) for i,j in pred_contacts if (i,j) in exp_contacts]
    for i,j in correct[:5]:
        info_line(f"  ✓ CORRECT: {atom_seq[i]}{i} ⟷ {atom_seq[j]}{j}")
    
    return {
        "pdb_id": pdb_id,
        "sequence": seq,
        "declared_seqres_sequence": declared_seq,
        "comparison_scope": "first model, first observed chain, observed CA residues",
        "residue_identifiers": [{k: atom[k] for k in
                                 ('chain', 'residue_id', 'insertion_code', 'alternate_location')}
                                for atom in atoms],
        "seq_len": len(seq),
        "atom_seq": atom_seq,
        "atom_count": len(atoms),
        "experimental_contacts": len(exp_contacts),
        "predicted_contacts": len(pred_contacts),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "frobenius_verified": result["frobenius_verified"],
        "winding_number": result["winding_number"],
        "activation_coverage": result["activation_coverage"],
    }
if __name__ == "__main__":
    pdb_ids = ["1VII", "1UBQ", "1ZDD", "2MTP", "1L2Y"]
    results = []
    
    for pdb_id in pdb_ids:
        try:
            pdb_text = fetch_pdb(pdb_id)
            r = validate(pdb_id, pdb_text)
            results.append(r)
        except Exception as e:
            error_line(f"ERROR fetching {pdb_id}: {e}")
            results.append({"pdb_id": pdb_id, "error": str(e)})
    
    info_line(f"\n\n{'='*60}")
    info_line("VALIDATION SUMMARY")
    info_line(f"{'='*60}")
    for r in results:
        if "error" in r:
            error_line(f"{r['pdb_id']}: ERROR - {r['error']}")
        else:
            print(f"{r['pdb_id']}: seq={r['seq_len']}aa, "
                  f"exp_contacts={r['experimental_contacts']}, "
                  f"pred_contacts={r['predicted_contacts']}, "
                  f"P={r['precision']:.3f} R={r['recall']:.3f} F1={r['f1_score']:.3f}")
    
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pdb_validation_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    info_line(f"\nResults saved to pdb_validation_results.json")

    if any("error" in result for result in results):
        sys.exit(1)
