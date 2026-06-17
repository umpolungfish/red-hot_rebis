#!/usr/bin/env python3
"""
Path 2: Multiple Sequence Alignment for SerpentRod.
Tests evolutionary conservation of activation patterns across species.

Author: Lando ⊗ ⊙perator
"""
import sys, os, json, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "p4ramill_py"))
import p4ramill_py.belnap, p4ramill_py.genetics_b4, p4ramill_py.genetic_code
import importlib.util, importlib.machinery, types

pkg_dir = os.path.join(os.path.dirname(__file__), "p4ramill_py")
loader = importlib.machinery.SourceFileLoader("p4ramill_py.serpent_rod", os.path.join(pkg_dir, "serpent_rod.py"))
spec = importlib.util.spec_from_loader("p4ramill_py.serpent_rod", loader)
mod = importlib.util.module_from_spec(spec)
sys.modules["p4ramill_py.serpent_rod"] = mod
mod.__package__ = "p4ramill_py"
loader.exec_module(mod)
SerpentRod = mod.SerpentRod

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
        print(f"    Length: {len(seq)} AA")
        print(f"    Winding: {result['winding_number']} B4 loops")
        print(f"    Contacts: {len(result['contacts'])}")
        print(f"    Subunits: {result['subunit_count']}")
        print(f"    Frobenius: {'✓' if result['frobenius_verified'] else '✗'}")
        print(f"    Primitives: {len(activated)}/12 — {sorted(activated)}")
    
    # Cross-species conservation
    if len(orthologs) >= 2:
        species_list = list(results.keys())
        conserved = set(all_primitives[species_list[0]])
        variable = set()
        for sp in species_list[1:]:
            conserved &= all_primitives[sp]
            variable |= all_primitives[sp] - conserved
        
        print(f"\n  CONSERVED primitives ({len(conserved)}/12): {sorted(conserved)}")
        print(f"  VARIABLE primitives: {sorted(variable)}")
        
        results["conserved_primitives"] = list(conserved)
        results["variable_primitives"] = list(variable)
        results["conservation_rate"] = len(conserved) / 12
    
    return results

all_results = {}

print("="*70)
print("🐍 SERPENTROD — EVOLUTIONARY CONSERVATION ANALYSIS 🐍")
print("="*70)

# Ubiquitin
all_results["ubiquitin"] = analyze_family("ubiquitin", UBIQUITIN_ORTHOLOGS)

# Cytochrome C
all_results["cytochrome_c"] = analyze_family("cytochrome_c", CYTC_ORTHOLOGS)

print(f"\n\n{'='*70}")
print("SUMMARY: EVOLUTIONARY CONSERVATION OF ACTIVATION PATTERNS")
print(f"{'='*70}")
for fam_name, fam_results in all_results.items():
    seqs = [k for k in fam_results.keys() if k not in ["conserved_primitives", "variable_primitives", "conservation_rate"]]
    print(f"\n{fam_name.upper()}: {len(seqs)} orthologs")
    for sp in seqs:
        r = fam_results[sp]
        print(f"  {sp:20s} len={r['seq_len']:3d} wind={r['winding']:3d} frob={'✓' if r['frobenius'] else '✗'} prim={r['num_activated']:2d}/12")
    if "conserved_primitives" in fam_results:
        print(f"  Conserved: {fam_results['conserved_primitives']}")
        print(f"  Variable:  {fam_results['variable_primitives']}")
        print(f"  Rate: {fam_results['conservation_rate']:.0%}")

with open("/home/mrnob0dy666/p4rakernel/msa_analysis.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\nResults saved to msa_analysis.json")
