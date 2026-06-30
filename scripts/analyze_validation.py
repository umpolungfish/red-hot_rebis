#!/usr/bin/env python3
"""
Deep analysis of PDB validation results for the SerpentRod.
Focus on what the IG primitive contacts ACTUALLY capture.

Author: Lando ⊗ ⊙perator
"""
_HELP_EXAMPLES = """  rebis.py run analyze_validation"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "scripts/analyze_validation.py"
    print(_doc)
    print()
    info_line("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import sys, os, json, math, urllib.request
from typing import List, Tuple, Set
_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REBIS_ROOT)
import rhr_p4rky.belnap
import rhr_p4rky.genetics_b4
import rhr_p4rky.genetic_code
from rhr_p4rky.serpent_rod import SerpentRod
from shared.rich_output import *


THREE_TO_ONE = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
AA_TO_CODON = {"A":"GCU","R":"CGU","N":"AAU","D":"GAU","C":"UGU","Q":"CAA","E":"GAA","G":"GGU","H":"CAU","I":"AUU","L":"UUG","K":"AAA","M":"AUG","F":"UUU","P":"CCU","S":"UCU","T":"ACU","W":"UGG","Y":"UAU","V":"GUU"}

def fetch_pdb(pdb_id):
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode()

def extract_single_model_ca(pdb_text: str) -> Tuple[List[Tuple[float,float,float]], str]:
    """Extract CA from first MODEL only (NMR ensembles have multiple models)."""
    atoms = []
    seq = ""
    in_model = True
    model_count = 0
    for line in pdb_text.split('\n'):
        if line.startswith("MODEL"):
            model_count += 1
            if model_count > 1:
                in_model = False
            else:
                in_model = True
        if line.startswith("ENDMDL"):
            in_model = False
        if line.startswith("ATOM") and in_model and line[12:16].strip() == "CA":
            try:
                three = line[17:20].strip().upper()
                if three not in THREE_TO_ONE: continue
                one = THREE_TO_ONE[three]
                x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                atoms.append((x,y,z))
                seq += one
            except: continue
    return atoms, seq

def get_contacts(atoms, cutoff=8.0, min_dist=6):
    """Get contacts with stricter criteria."""
    contacts = set()
    for i in range(len(atoms)):
        for j in range(i+min_dist, len(atoms)):
            dx, dy, dz = atoms[i][0]-atoms[j][0], atoms[i][1]-atoms[j][1], atoms[i][2]-atoms[j][2]
            d = math.sqrt(dx*dx+dy*dy+dz*dz)
            if d < cutoff:
                contacts.add((i,j))
    return contacts

def analyze(pdb_id: str):
    info_line(f"\n{'='*70}")
    info_line(f"DEEP ANALYSIS: {pdb_id}")
    info_line(f"{'='*70}")
    
    pdb_text = fetch_pdb(pdb_id)
    atoms, seq = extract_single_model_ca(pdb_text)
    info_line(f"Single-model CA atoms: {len(atoms)}, Sequence: {seq}")
    
    if len(atoms) < 5:
        info_line("Too few atoms, skipping")
        return
    
    # Get experimental contacts at multiple cutoffs
    for cutoff in [5.0, 6.0, 8.0, 10.0]:
        for min_dist in [4, 6, 12]:
            c = get_contacts(atoms, cutoff, min_dist)
            info_line(f"  cutoff={cutoff}Å, min_dist≥{min_dist}: {len(c)} contacts")
    
    # Get standard CASP-style long-range contacts (Cβ-Cβ < 8.0Å, seq sep ≥ 24)
    contacts_long = get_contacts(atoms, 8.0, 24)
    contacts_medium = get_contacts(atoms, 8.0, 12)
    contacts_short = get_contacts(atoms, 8.0, 6)
    contacts_all = get_contacts(atoms, 8.0, 4)
    
    info_line(f"\nContact stratification (8.0Å cutoff):")
    info_line(f"  Short-range (4-6): {len(contacts_all) - len(contacts_short)}")
    info_line(f"  Medium-range (6-12): {len(contacts_short) - len(contacts_medium)}")
    info_line(f"  Long-range (12-24): {len(contacts_medium) - len(contacts_long)}")
    info_line(f"  Very long-range (≥24): {len(contacts_long)}")
    
    # Run SerpentRod
    rna = "".join(AA_TO_CODON.get(aa, "NNN") for aa in seq)
    sr = SerpentRod(rna, name=pdb_id)
    result = sr.report()
    
    # Get predicted contacts
    pred_contacts = set((c["i"], c["j"]) for c in result["contacts"])
    
    info_line(f"\nSerpentRod predictions:")
    info_line(f"  Predicted contacts: {len(pred_contacts)}")
    info_line(f"  Winding number: {result['winding_number']}")
    info_line(f"  Subunits: {result['subunit_count']}")
    info_line(f"  Frobenius: {'✓' if result['frobenius_verified'] else '✗'}")
    
    # Analyze each predicted contact
    info_line(f"\nPredicted contact analysis:")
    for c in result["contacts"]:
        i, j = c["i"], c["j"]
        if i < len(seq) and j < len(seq):
            # Get actual distance from PDB
            if i < len(atoms) and j < len(atoms):
                dx = atoms[i][0]-atoms[j][0]
                dy = atoms[i][1]-atoms[j][1]
                dz = atoms[i][2]-atoms[j][2]
                d = math.sqrt(dx*dx+dy*dy+dz*dz)
                
                classifications = []
                if (i,j) in contacts_long: classifications.append("VERY_LONG")
                elif (i,j) in contacts_medium: classifications.append("LONG")
                elif (i,j) in contacts_short: classifications.append("MEDIUM")
                elif (i,j) in contacts_all: classifications.append("SHORT")
                else: classifications.append("NO_CONTACT")
                
                info_line(f"  {seq[i]}{i} ⟷ {seq[j]}{j}  {c['type']:25s}  "
f"actual_d={d:.2f}Å  {classifications[0]:12s}  "
                      f"conf={c['confidence']:.2f}")
    
    # Check critical secondary structure prediction
    info_line(f"\nSecondary structure prediction:")
    helices_predicted = [e for e in result["secondary_elements"] if e["type"] == "helix"]
    sheets_predicted = [e for e in result["secondary_elements"] if e["type"] == "sheet"]
    info_line(f"  Predicted helices: {len(helices_predicted)}")
    info_line(f"  Predicted sheets: {len(sheets_predicted)}")
    
    # Compare with PDB HELIX/SHEET records
    pdb_helices = []
    pdb_sheets = []
    for line in pdb_text.split('\n'):
        if line.startswith("HELIX"):
            try:
                start = int(line[21:25].strip())
                end = int(line[33:37].strip())
                pdb_helices.append((start, end))
            except: pass
        if line.startswith("SHEET"):
            try:
                start = int(line[33:37].strip())
                end = int(line[38:42].strip())
                pdb_sheets.append((start, end))
            except: pass
    
    # Map PDB residue numbers to sequence indices
    seq_idx_map = {}
    idx = 0
    for line in pdb_text.split('\n'):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                res_num = int(line[22:26].strip())
                seq_idx_map[res_num] = idx
                idx += 1
            except: pass
            break  # Just get first CA's resnum
    
    # Build index map
    seq_idx_map = {}
    idx = 0
    first_res = None
    for line in pdb_text.split('\n'):
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            try:
                res_num = int(line[22:26].strip())
                if first_res is None:
                    first_res = res_num
                seq_idx_map[res_num] = idx
                idx += 1
            except: pass
    
    info_line(f"\nPDB secondary structure (from PDB records):")
    info_line(f"  Helices: {pdb_helices}")
    info_line(f"  Sheets: {pdb_sheets}")
    
    # Accuracy of secondary structure
    correct_helix = 0
    predicted_helix_regions = set()
    for e in helices_predicted:
        for i in range(e["start"], e["end"]):
            predicted_helix_regions.add(i)
    
    for start, end in pdb_helices:
        for res_num in range(start, end+1):
            if res_num in seq_idx_map:
                idx = seq_idx_map[res_num]
                if idx in predicted_helix_regions:
                    correct_helix += 1
    
    total_pdb_helix = sum(end-start+1 for start,end in pdb_helices)
    info_line(f"\n  Helix accuracy: {correct_helix}/{total_pdb_helix} residues matched")

# Run on best candidates
for pdb_id in ["1VII", "1UBQ"]:
    analyze(pdb_id)
