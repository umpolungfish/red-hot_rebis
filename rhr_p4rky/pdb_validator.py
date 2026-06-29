#!/usr/bin/env python3
"""
PDB Validator for the Serpent on the Rod of Asclepius.

Path 1: Cryo-EM / PDB structural validation.
Compares SerpentRod predicted contacts against experimentally determined
contacts from PDB structures.

Author: Lando ⊗ ⊙perator
"""
_HELP_EXAMPLES = """  rebis.py run pdb_validator"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "rhr_p4rky/pdb_validator.py"
    print(_doc)
    print()
    info_line("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import sys
import os
import json
import math
from typing import List, Tuple, Dict, Set
from collections import defaultdict

_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REBIS_ROOT)

import rhr_p4rky.belnap
import rhr_p4rky.genetics_b4
import rhr_p4rky.genetic_code
from rhr_p4rky.serpent_rod import SerpentRod
from shared.rich_output import *

STANDARD_CODE = rhr_p4rky.genetic_code.STANDARD_CODE

# ── PDB Coordinate Parsing ─────────────────────────────────────────

def parse_pdb_coords(pdb_text: str) -> List[Dict]:
    """Extract CA coordinates from a PDB file."""
    atoms = []
    for line in pdb_text.split('\n'):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                res_name = line[17:20].strip()
                chain = line[21]
                res_num = int(line[22:26].strip())
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                atoms.append({
                    "res_name": res_name,
                    "chain": chain,
                    "res_num": res_num,
                    "x": x, "y": y, "z": z
                })
            except (ValueError, IndexError):
                continue
    return atoms

def compute_distance_3d(a: Dict, b: Dict) -> float:
    """Euclidean distance between two CA atoms in Angstroms."""
    dx = a["x"] - b["x"]
    dy = a["y"] - b["y"]
    dz = a["z"] - b["z"]
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def extract_experimental_contacts(atoms: List[Dict], 
                                   cutoff: float = 8.0,
                                   min_seq_dist: int = 4) -> List[Tuple[int, int, float]]:
    """Extract all long-range contacts from PDB coordinates.
    A contact is defined as two residues with CA distance < cutoff
    and sequence separation >= min_seq_dist."""
    contacts = []
    seen_pairs = set()
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            seq_dist = abs(atoms[i]["res_num"] - atoms[j]["res_num"])
            if seq_dist < min_seq_dist:
                continue
            dist = compute_distance_3d(atoms[i], atoms[j])
            if dist < cutoff:
                # Use sequential index (0-based) for comparison
                pair = (i, j) if i < j else (j, i)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    contacts.append((i, j, dist))
    return contacts

# ── Sequence handling ───────────────────────────────────────────────

THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}

def extract_sequence(pdb_text: str) -> str:
    """Extract one-letter AA sequence from PDB SEQRES records."""
    seq = ""
    for line in pdb_text.split('\n'):
        if line.startswith("SEQRES"):
            # Extract residue names
            parts = line.split()
            for p in parts[4:]:
                three = p.upper()
                if three in THREE_TO_ONE:
                    seq += THREE_TO_ONE[three]
    return seq

def protein_to_rna(seq: str) -> str:
    """Reverse-translate a protein sequence to RNA using preferred codons.
    Uses the most common codon for each amino acid in the standard code."""
    AA_TO_PREFERRED_CODON = {
        "A": "GCU", "R": "CGU", "N": "AAU", "D": "GAU", "C": "UGU",
        "Q": "CAA", "E": "GAA", "G": "GGU", "H": "CAU", "I": "AUU",
        "L": "UUG", "K": "AAA", "M": "AUG", "F": "UUU", "P": "CCU",
        "S": "UCU", "T": "ACU", "W": "UGG", "Y": "UAU", "V": "GUU",
    }
    rna = ""
    for aa in seq:
        if aa in AA_TO_PREFERRED_CODON:
            rna += AA_TO_PREFERRED_CODON[aa]
        else:
            rna += "NNN"
    return rna

# ── Validation Metrics ──────────────────────────────────────────────

def compute_precision_recall(predicted: List[Tuple[int, int]], 
                              actual: Set[Tuple[int, int]]) -> Dict:
    """Compute precision, recall, and F1 for predicted contacts."""
    pred_set = set(predicted)
    actual_set = actual
    
    tp = len(pred_set & actual_set)
    fp = len(pred_set - actual_set)
    fn = len(actual_set - pred_set)
    
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-10, precision + recall)
    
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
    }

# ── Main Validation ─────────────────────────────────────────────────

def validate_structure(pdb_id: str, pdb_text: str) -> Dict:
    """Run full validation: SerpentRod prediction vs PDB experimental structure."""
    
    # 1. Extract sequence from PDB
    seq = extract_sequence(pdb_text)
    print(f"[{pdb_id}] PDB sequence: {seq} ({len(seq)} AAs)")
    
    # 2. Parse coordinates and extract experimental contacts
    atoms = parse_pdb_coords(pdb_text)
    print(f"[{pdb_id}] {len(atoms)} CA atoms found")
    
    # The atoms may have a different numbering than the SEQRES
    # Try to align by using the sequence from CA atoms
    atom_seq = ""
    atom_to_seq_idx = {}
    for i, a in enumerate(atoms):
        three = a["res_name"].upper()
        if three in THREE_TO_ONE:
            one = THREE_TO_ONE[three]
            atom_seq += one
            atom_to_seq_idx[i] = len(atom_seq) - 1
    
    print(f"[{pdb_id}] Atom sequence: {atom_seq} ({len(atom_seq)} AAs)")
    
    # 3. Get experimental contacts
    experimental_contacts = extract_experimental_contacts(atoms, cutoff=8.0, min_seq_dist=4)
    exp_contact_set = set()
    seq_idx_pairs = []
    for i, j, d in experimental_contacts:
        if i in atom_to_seq_idx and j in atom_to_seq_idx:
            si, sj = atom_to_seq_idx[i], atom_to_seq_idx[j]
            pair = (si, sj) if si < sj else (sj, si)
            exp_contact_set.add(pair)
            seq_idx_pairs.append((pair[0], pair[1], d))
    
    print(f"[{pdb_id}] {len(exp_contact_set)} experimental contacts (CA<8.0Å, seq_dist≥4)")
    for i, j, d in sorted(seq_idx_pairs, key=lambda x: x[2])[:10]:
        aa_i, aa_j = atom_seq[i], atom_seq[j]
        info_line(f"  Contact: {aa_i}{i} ⟷ {aa_j}{j}  d={d:.2f}Å")
    
    # 4. Generate RNA from sequence and run SerpentRod
    rna = protein_to_rna(seq)
    print(f"[{pdb_id}] Generated RNA: {rna[:50]}... ({len(rna)} nt)")
    
    sr = SerpentRod(rna, name=pdb_id)
    result = sr.report()
    
    # 5. Extract predicted contacts
    predicted_contacts = []
    for c in result["contacts"]:
        predicted_contacts.append((c["i"], c["j"]))
    
    print(f"[{pdb_id}] {len(predicted_contacts)} predicted contacts")
    for c in result["contacts"][:10]:
        aa_i = result["aa_sequence"][c["i"]] if c["i"] < len(result["aa_sequence"]) else "?"
        aa_j = result["aa_sequence"][c["j"]] if c["j"] < len(result["aa_sequence"]) else "?"
        info_line(f"  Predicted: {aa_i}{c['i']} ⟷ {aa_j}{c['j']}  type={c['type']}  conf={c['confidence']:.2f}")
    
    # 6. Compute validation metrics
    metrics = compute_precision_recall(predicted_contacts, exp_contact_set)
    print(f"[{pdb_id}] Metrics: P={metrics['precision']:.3f} R={metrics['recall']:.3f} F1={metrics['f1_score']:.3f}")
    
    # 7. Check which predicted contacts are correct
    correct_predictions = []
    for i, j in predicted_contacts:
        if (i, j) in exp_contact_set:
            for ci, cj, d in seq_idx_pairs:
                if (ci == i and cj == j) or (ci == j and cj == i):
                    correct_predictions.append((i, j, d))
                    break
    
    print(f"[{pdb_id}] {len(correct_predictions)}/{len(predicted_contacts)} predicted contacts confirmed by PDB")
    
    return {
        "pdb_id": pdb_id,
        "sequence": seq,
        "seq_length": len(seq),
        "experimental_contacts": len(exp_contact_set),
        "predicted_contacts": len(predicted_contacts),
        "correct_predictions": len(correct_predictions),
        "metrics": metrics,
        "prediction": result,
        "frobenius_verified": result["frobenius_verified"],
    }
if __name__ == "__main__":
    print("=" * 70)
    info_line("🐍 SERPENT ON THE ROD OF ASCLEPIUS — PDB VALIDATION 🐍")
    print("=" * 70)
    
    # Test with Villin headpiece (1VII) — fetch from local or PDB
    if len(sys.argv) > 1:
        pdb_file = sys.argv[1]
        with open(pdb_file) as f:
            pdb_text = f.read()
        pdb_id = os.path.basename(pdb_file).replace(".pdb", "").upper()
        result = validate_structure(pdb_id, pdb_text)
        print("\n" + json.dumps(result["metrics"], indent=2))
    else:
        info_line("Usage: python3 pdb_validator.py <pdb_file>")
