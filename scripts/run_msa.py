#!/usr/bin/env python3
"""
Path 2: Multiple Sequence Alignment for SerpentRod.
Tests evolutionary conservation of activation patterns across species.

Author: Lando ⊗ ⊙perator
"""
_HELP_EXAMPLES = """  rebis.py run run_msa"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "scripts/run_msa.py"
    print(_doc)
    print()
    info_line("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import sys, os, json, urllib.request
_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REBIS_ROOT)
import rhr_p4rky.belnap
import rhr_p4rky.genetics_b4
import rhr_p4rky.genetic_code
from rhr_p4rky.serpent_rod import SerpentRod
from shared.rich_output import *


AA_PREFERRED = {"A":"GCU","R":"CGU","N":"AAU","D":"GAU","C":"UGU","Q":"CAA","E":"GAA","G":"GGU","H":"CAU","I":"AUU","L":"UUG","K":"AAA","M":"AUG","F":"UUU","P":"CCU","S":"UCU","T":"ACU","W":"UGG","Y":"UAU","V":"GUU"}

# Ubiquitin sequences from different species (UniProt)
UBIQUITIN_ORTHOLOGS = {
    "human": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
    "mouse": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
    "yeast": "MQIFVKTLTGKTITLEVESSDTIDNVKSKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
    "plant_arabidopsis": "MQIFVKTLTGKKITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
    "drosophila": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
}

# Cytochrome C
CYTC_ORTHOLOGS = {
    "human": "MGDVEKGKKIFIMKCSQCHTVEKGGKHKTGPNLHGLFGRKTGQAPGYSYTAANKNKGIIWGEDTLMEYLENPKKYIPGTKMIFAGIKKKGEREDLIAYLKKATNE",
    "horse": "MGDVEKGKKIFVQKCAQCHTVEKGGKHKTGPNLHGLFGRKTGQAPGFTYTDANKNKGITWKEETLMEYLENPKKYIPGTKMIFAGIKKKTEREDLIAYLKKATNE",
    "yeast": "MTEFKAGSAKKGATLFKTRCLQCHTVEKGGPHKVGPNLHGLFGRHSGQAEGYSYTDANIKKNVLWDENNMSEYLTNPKKYIPGTKMAFGGLKKEKDRNDLITYLKKACE",
    "wheat": "MAAFFGAKAGSTEKPGKKLFKTKCAQCHTVEKGGKHKTGPNLHGLFGRKTGQAAGFSYTDANKGKVEWEEDTLMEYLENPKKYIPGTKMIFAGIKKPAGERDDLTIAYLKQATG",
}

def analyze_family(name, orthologs):
    print(f"\n{'='*60}")
    print(f"FAMILY: {name}")
    print(f"{'='*60}")
    
    results = {}
    all_primitives = {}
    
    for species, seq in orthologs.items():
        rna = "".join(AA_PREFERRED.get(aa, "NNN") for aa in seq)
        sr = SerpentRod(rna, name=f"{name}_{species}")
        result = sr.report()
        
        # Extract activated primitives
        activated = set()
        for ap in result["activation_pattern"]:
            prim = ap["primitive"].split(" (")[1].rstrip(")") if "(" in ap["primitive"] else ap["primitive"]
            activated.add(prim)
        
        results[species] = {
            "seq_len": len(seq),
            "aa_sequence": result["aa_sequence"],
            "winding": result["winding_number"],
            "contacts": len(result["contacts"]),
            "subunits": result["subunit_count"],
            "frobenius": result["frobenius_verified"],
            "confidence": result["confidence"],
            "primitives_activated": list(activated),
            "num_activated": len(activated),
        }
        all_primitives[species] = activated
        
        print(f"\n  {species.upper()}:")
        info_line(f"    Length: {len(seq)} AA")
        info_line(f"    Winding: {result['winding_number']} B4 loops")
        info_line(f"    Contacts: {len(result['contacts'])}")
        info_line(f"    Subunits: {result['subunit_count']}")
        info_line(f"    Frobenius: {'✓' if result['frobenius_verified'] else '✗'}")
        info_line(f"    Primitives: {len(activated)}/12 — {sorted(activated)}")
    
    # Cross-species conservation
    if len(orthologs) >= 2:
        species_list = list(results.keys())
        conserved = set(all_primitives[species_list[0]])
        variable = set()
        for sp in species_list[1:]:
            conserved &= all_primitives[sp]
            variable |= all_primitives[sp] - conserved
        
        print(f"\n  CONSERVED primitives ({len(conserved)}/12): {sorted(conserved)}")
        info_line(f"  VARIABLE primitives: {sorted(variable)}")
        
        results["conserved_primitives"] = list(conserved)
        results["variable_primitives"] = list(variable)
        results["conservation_rate"] = len(conserved) / 12
    
    return results

all_results = {}

print("="*70)
info_line("🐍 SERPENTROD — EVOLUTIONARY CONSERVATION ANALYSIS 🐍")
print("="*70)

# Ubiquitin
all_results["ubiquitin"] = analyze_family("ubiquitin", UBIQUITIN_ORTHOLOGS)

# Cytochrome C
all_results["cytochrome_c"] = analyze_family("cytochrome_c", CYTC_ORTHOLOGS)

print(f"\n\n{'='*70}")
info_line("SUMMARY: EVOLUTIONARY CONSERVATION OF ACTIVATION PATTERNS")
print(f"{'='*70}")
for fam_name, fam_results in all_results.items():
    seqs = [k for k in fam_results.keys() if k not in ["conserved_primitives", "variable_primitives", "conservation_rate"]]
    print(f"\n{fam_name.upper()}: {len(seqs)} orthologs")
    for sp in seqs:
        r = fam_results[sp]
        info_line(f"  {sp:20s} len={r['seq_len']:3d} wind={r['winding']:3d} frob={'✓' if r['frobenius'] else '✗'} prim={r['num_activated']:2d}/12")
    if "conserved_primitives" in fam_results:
        info_line(f"  Conserved: {fam_results['conserved_primitives']}")
        info_line(f"  Variable:  {fam_results['variable_primitives']}")
        info_line(f"  Rate: {fam_results['conservation_rate']:.0%}")

with open("/home/mrnob0dy666/p4rakernel/msa_analysis.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\nResults saved to msa_analysis.json")
