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
    print("Examples:")
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
    """Use the same model, chain and conformer selection as validation."""
    from scripts.run_pdb_validation import parse_ca_coords
    atoms, seq = parse_ca_coords(pdb_text)
    return [(a['x'], a['y'], a['z']) for a in atoms], seq

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
    
    # Stratify observed CA contacts by sequence-index separation.
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
    
    if result["aa_sequence"] != seq:
        raise ValueError("Translated sequence differs from observed CA sequence")

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
    
    # Compare only annotations on the selected observed chain. PDB residue
    # numbering and insertion codes remain attached through this comparison.
    from scripts.run_pdb_validation import parse_ca_coords
    observed, _ = parse_ca_coords(pdb_text)
    chain = observed[0]['chain'] if observed else None
    regions = {'HELIX': [], 'SHEET': []}
    for line in pdb_text.splitlines():
        kind = line[:6].strip()
        if kind not in regions:
            continue
        if kind == 'HELIX':
            start_chain, end_chain = line[19:20], line[31:32]
            start, end = (line[21:25], line[25:26]), (line[33:37], line[37:38])
        else:
            start_chain, end_chain = line[21:22], line[32:33]
            start, end = (line[22:26], line[26:27]), (line[33:37], line[37:38])
        if start_chain != chain or end_chain != chain:
            continue
        try:
            regions[kind].append(((int(start[0]), start[1]), (int(end[0]), end[1])))
        except ValueError as exc:
            raise ValueError(f'Invalid {kind} annotation: {line}') from exc
    observed_helix = set()
    for idx, atom in enumerate(observed):
        residue = (int(atom['residue_id']), atom['insertion_code'])
        if any(start <= residue <= end for start, end in regions['HELIX']):
            observed_helix.add(idx)
    predicted_helix = {i for e in helices_predicted for i in range(e['start'], e['end'])}
    matched = observed_helix & predicted_helix
    info_line(f"\nPDB secondary structure on selected chain {chain!r}:")
    info_line(f"  Helices: {regions['HELIX']}")
    info_line(f"  Sheets: {regions['SHEET']}")
    info_line(f"  Helix agreement: {len(matched)}/{len(observed_helix)} observed residues matched")


if __name__ == '__main__':
    for pdb_id in ['1VII', '1UBQ']:
        analyze(pdb_id)
