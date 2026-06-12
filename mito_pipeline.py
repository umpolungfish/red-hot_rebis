#!/usr/bin/env python3
"""
mito_pipeline.py — Process the human mitochondrial genome (NC_012920.1)
through the RNA→Protein structural pipeline.

Extracts all 13 protein-coding genes and runs the 7-stage IG derivation.
"""
import sys, os, json, math
sys.path.insert(0, "/home/mrnob0dy666/p4rakernel")
sys.path.insert(0, "/home/mrnob0dy666/p4rakernel/p4ramill_py")

from p4ramill_py.gene_to_protein_pipeline import GeneToProteinPipeline

# Read the mitogenome FASTA
fasta_path = "/home/mrnob0dy666/p4rakernel/NC_012920.1.fasta"
with open(fasta_path) as f:
    lines = f.readlines()
header = lines[0].strip()
seq = "".join(l.strip() for l in lines[1:]).upper()
print(f"Genome: {header}")
print(f"Length: {len(seq)} bp")

# Mitochondrial protein-coding gene coordinates (1-based)
# Source: MITOMAP / NC_012920.1 annotation
MITO_GENES = {
    "MT-ND1":  (3307, 4262, "NADH dehydrogenase subunit 1"),
    "MT-ND2":  (4470, 5511, "NADH dehydrogenase subunit 2"),
    "MT-CO1":  (5904, 7445, "Cytochrome c oxidase subunit I"),
    "MT-CO2":  (7586, 8269, "Cytochrome c oxidase subunit II"),
    "MT-ATP8": (8366, 8572, "ATP synthase F0 subunit 8"),
    "MT-ATP6": (8527, 9207, "ATP synthase F0 subunit 6"),
    "MT-CO3":  (9207, 9990, "Cytochrome c oxidase subunit III"),
    "MT-ND3":  (10059, 10404, "NADH dehydrogenase subunit 3"),
    "MT-ND4L": (10470, 10766, "NADH dehydrogenase subunit 4L"),
    "MT-ND4":  (10760, 12137, "NADH dehydrogenase subunit 4"),
    "MT-ND5":  (12337, 14148, "NADH dehydrogenase subunit 5"),
    "MT-ND6":  (14149, 14673, "NADH dehydrogenase subunit 6"),
    "MT-CYB":  (14747, 15887, "Cytochrome b"),
}

results = {}

for gene_name, (start, end, desc) in MITO_GENES.items():
    # 1-based to 0-based
    cds = seq[start-1:end]
    
    # Determine subunit count from known biology
    if gene_name in ("MT-CO1", "MT-CO2", "MT-CO3", "MT-CYB"):
        subunits = 1  # Core subunit of larger complex
    elif gene_name == "MT-ATP8":
        subunits = 1
    elif gene_name == "MT-ATP6":
        subunits = 1
    elif "ND" in gene_name:
        subunits = 1
    else:
        subunits = 1
    
    print(f"\n{'='*70}")
    print(f"GENE: {gene_name} — {desc}")
    print(f"Coords: {start}-{end} ({len(cds)} bp)")
    print(f"{'='*70}")
    
    try:
        pipeline = GeneToProteinPipeline(cds, name=gene_name, is_rna=False)
        report = pipeline.run(num_subunits=subunits)
        
        results[gene_name] = {
            "length_bp": len(cds),
            "aa_length": report["aa_length"],
            "frobenius_all_stages": all(s["frob"] for s in report["stages"]),
            "dna_to_quaternary_distance": report["closure"]["dna_to_quaternary_distance"],
            "total_delta": report["total_delta"],
            "consciousness_invariant": report["closure"]["consciousness_invariant"],
            "subunit_symmetry": report["subunit_symmetry"],
            "primitive_activations": report["primitive_activations"],
            "aa_sequence": report["aa_sequence"][:40] + "...",
        }
        
        print(f"  AA length: {report['aa_length']}")
        print(f"  Frobenius all stages: {'✓' if all(s['frob'] for s in report['stages']) else '✗'}")
        print(f"  DNA→Quaternary distance: {report['closure']['dna_to_quaternary_distance']:.4f}")
        print(f"  Consciousness invariant: {report['closure']['consciousness_invariant']}")
        
        print(f"\n  {'Stage':<25} {'B4':<6} {'Frob':<6} Description")
        print(f"  {'-'*58}")
        for s in report["stages"]:
            fm = "✓" if s["frob"] else "✗"
            print(f"  {s['name']:<25} {s['b4']:<6} {fm:<6} {s['desc']}")
        
        print(f"\n  Primitive activations:")
        for prim, data in sorted(report["primitive_activations"].items()):
            print(f"    {prim}: {data['count']}x")
            
    except Exception as e:
        print(f"  ERROR: {e}")
        results[gene_name] = {"error": str(e)}

# Summary table
print(f"\n\n{'='*70}")
print("SUMMARY: ALL 13 MITOCHONDRIAL PROTEIN-CODING GENES")
print(f"{'='*70}")
print(f"{'Gene':<10} {'bp':<6} {'AA':<5} {'Frob':<6} {'ClosureDist':<12} {'Consc':<6} {'Primitives':<12}")
print(f"{'-'*60}")
for g in sorted(results.keys()):
    r = results[g]
    if "error" in r:
        print(f"{g:<10} ERROR: {r['error']}")
    else:
        f = "✓" if r["frobenius_all_stages"] else "✗"
        pcount = len(r["primitive_activations"])
        print(f"{g:<10} {r['length_bp']:<6} {r['aa_length']:<5} {f:<6} {r['dna_to_quaternary_distance']:<12.4f} {r['consciousness_invariant']:<6} {pcount}/12")
