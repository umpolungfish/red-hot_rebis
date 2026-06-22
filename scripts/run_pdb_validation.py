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

# Patch imports
import rhr_p4rky.belnap
import rhr_p4rky.genetics_b4
import rhr_p4rky.genetic_code
import importlib.util, importlib.machinery, types

pkg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rhr_p4rky")
loader = importlib.machinery.SourceFileLoader("rhr_p4rky.serpent_rod",
    os.path.join(pkg_dir, "serpent_rod.py"))
spec = importlib.util.spec_from_loader("rhr_p4rky.serpent_rod", loader)
mod = importlib.util.module_from_spec(spec)
sys.modules["rhr_p4rky.serpent_rod"] = mod
mod.__package__ = "rhr_p4rky"
loader.exec_module(mod)
SerpentRod = mod.SerpentRod
STANDARD_CODE = rhr_p4rky.genetic_code.STANDARD_CODE

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
    atoms = []
    atom_seq = ""
    for line in pdb_text.split('\n'):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                three = line[17:20].strip().upper()
                if three not in THREE_TO_ONE: continue
                one = THREE_TO_ONE[three]
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                atoms.append({"one": one, "x": x, "y": y, "z": z})
                atom_seq += one
            except: continue
    return atoms, atom_seq

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
    print(f"\n{'='*60}")
    print(f"VALIDATING: {pdb_id}")
    print(f"{'='*60}")
    
    # Extract sequence
    seq = extract_sequence(pdb_text)
    print(f"SEQRES sequence ({len(seq)} AA): {seq}")
    
    # Parse CA coordinates
    atoms, atom_seq = parse_ca_coords(pdb_text)
    print(f"CA atoms parsed: {len(atoms)} (seq: {atom_seq})")
    
    if len(atoms) < 5:
        return {"pdb_id": pdb_id, "error": "Too few atoms", "sequence": seq}
    
    # Extract experimental contacts
    exp_contacts = extract_contacts(atoms, cutoff=8.0, min_dist=4)
    print(f"Experimental contacts (CA<8.0Å, seq_dist≥4): {len(exp_contacts)}")
    
    # Show top contacts
    for i, j in sorted(exp_contacts)[:8]:
        print(f"  Contact: {atom_seq[i]}{i} ⟷ {atom_seq[j]}{j}")
    
    # Generate RNA and run SerpentRod
    rna = protein_to_rna(seq)
    print(f"Generated RNA ({len(rna)} nt): {rna[:60]}...")
    
    sr = SerpentRod(rna, name=pdb_id)
    result = sr.report()
    
    pred_seq = result["aa_sequence"]
    print(f"Predicted AA: {pred_seq} ({len(pred_seq)} AAs)")
    print(f"Winding: {result['winding_number']} B4 loops")
    print(f"Frobenius: {'✓' if result['frobenius_verified'] else '✗'}")
    
    # Predicted contacts
    pred_contacts = set()
    for c in result["contacts"]:
        pred_contacts.add((c["i"], c["j"]))
    print(f"Predicted contacts: {len(pred_contacts)}")
    for c in result["contacts"][:8]:
        aa_i = pred_seq[c["i"]] if c["i"] < len(pred_seq) else "?"
        aa_j = pred_seq[c["j"]] if c["j"] < len(pred_seq) else "?"
        print(f"  {aa_i}{c['i']} ⟷ {aa_j}{c['j']}  {c['type']}  conf={c['confidence']}")
    
    # If predicted and experimental sequences differ in length, adjust
    # Map predicted indices to experimental indices using sequence alignment
    tp = len(pred_contacts & exp_contacts)
    fp = len(pred_contacts - exp_contacts)
    fn = len(exp_contacts - pred_contacts)
    
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-10, precision + recall)
    
    print(f"\n  TP={tp}, FP={fp}, FN={fn}")
    print(f"  Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
    
    # Check which specific contacts were correctly predicted
    correct = [(i,j) for i,j in pred_contacts if (i,j) in exp_contacts]
    for i,j in correct[:5]:
        print(f"  ✓ CORRECT: {atom_seq[i]}{i} ⟷ {atom_seq[j]}{j}")
    
    return {
        "pdb_id": pdb_id,
        "sequence": seq,
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
            print(f"ERROR fetching {pdb_id}: {e}")
            results.append({"pdb_id": pdb_id, "error": str(e)})
    
    print(f"\n\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    for r in results:
        if "error" in r:
            print(f"{r['pdb_id']}: ERROR - {r['error']}")
        else:
            print(f"{r['pdb_id']}: seq={r['seq_len']}aa, "
                  f"exp_contacts={r['experimental_contacts']}, "
                  f"pred_contacts={r['predicted_contacts']}, "
                  f"P={r['precision']:.3f} R={r['recall']:.3f} F1={r['f1_score']:.3f}")
    
    with open("/home/mrnob0dy666/p4rakernel/pdb_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to pdb_validation_results.json")
