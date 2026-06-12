#!/usr/bin/env python3
"""
mito_pipeline_v2.py — v2: handles strand orientation, robust error recovery.
Processes all 13 human mitochondrial protein-coding genes from NC_012920.1
through the 7-stage Imscribing Grammar structural pipeline.
"""
import sys, os, json
sys.path.insert(0, "/home/mrnob0dy666/p4rakernel/p4ramill_py")

from p4ramill_py.gene_to_protein_pipeline import GeneToProteinPipeline

# Read the mitogenome FASTA
fasta_path = "/home/mrnob0dy666/p4rakernel/NC_012920.1.fasta"
with open(fasta_path) as f:
    lines = f.readlines()
header = lines[0].strip()
seq = "".join(l.strip() for l in lines[1:]).upper()

compl = str.maketrans("ATCG", "TAGC")

def revcomp(s):
    return s.translate(compl)[::-1]

print(f"Genome: {header}")
print(f"Length: {len(seq)} bp")
print()

# Mitochondrial genes: (start, end, strand, description)
# H-strand: coordinates as-is; L-strand: revcomp needed
# NC_012920.1 reference uses H-strand as reference
MITO_GENES = {
    "MT-ND1":  (3307, 4262, "H", "NADH dehydrogenase subunit 1"),
    "MT-ND2":  (4470, 5511, "H", "NADH dehydrogenase subunit 2"),
    "MT-CO1":  (5904, 7445, "H", "Cytochrome c oxidase subunit I"),
    "MT-CO2":  (7586, 8269, "H", "Cytochrome c oxidase subunit II"),
    "MT-ATP8": (8366, 8572, "H", "ATP synthase F0 subunit 8"),
    "MT-ATP6": (8527, 9207, "H", "ATP synthase F0 subunit 6"),
    "MT-CO3":  (9207, 9990, "H", "Cytochrome c oxidase subunit III"),
    "MT-ND3":  (10059, 10404, "H", "NADH dehydrogenase subunit 3"),
    "MT-ND4L": (10470, 10766, "H", "NADH dehydrogenase subunit 4L"),
    "MT-ND4":  (10760, 12137, "H", "NADH dehydrogenase subunit 4"),
    "MT-ND5":  (12337, 14148, "H", "NADH dehydrogenase subunit 5"),
    "MT-ND6":  (14149, 14673, "L", "NADH dehydrogenase subunit 6"),
    "MT-CYB":  (14747, 15887, "H", "Cytochrome b"),
}

results = {}

for gene_name, (start, end, strand, desc) in sorted(MITO_GENES.items()):
    cds_raw = seq[start-1:end]
    
    # Reverse complement if on L-strand
    if strand == "L":
        cds = revcomp(cds_raw)
    else:
        cds = cds_raw
    
    print(f"{'='*70}")
    print(f"GENE: {gene_name} — {desc}")
    print(f"Coords: {start}-{end} ({len(cds)} bp)  Strand: {strand}")
    print(f"{'='*70}")
    
    try:
        pipeline = GeneToProteinPipeline(cds, name=gene_name, is_rna=False)
        report = pipeline.run(num_subunits=1)
        
        results[gene_name] = {
            "status": "OK",
            "length_bp": len(cds),
            "aa_length": report["aa_length"],
            "strand": strand,
            "frobenius_all_stages": all(s["frob"] for s in report["stages"]),
            "dna_to_quaternary_distance": report["closure"]["dna_to_quaternary_distance"],
            "total_delta": report["total_delta"],
            "consciousness_invariant": report["closure"]["consciousness_invariant"],
            "subunit_symmetry": report["subunit_symmetry"],
            "primitive_activations": report["primitive_activations"],
            "num_primitives": len(report["primitive_activations"]),
            "aa_sequence": report["aa_sequence"][:30],
        }
        
        print(f"  AA length: {report['aa_length']}")
        print(f"  Frobenius all stages: {'✓' if all(s['frob'] for s in report['stages']) else '✗'}")
        print(f"  Primitives activated: {len(report['primitive_activations'])}/12")
        
        for s in report["stages"]:
            fm = "✓" if s["frob"] else "✗"
            print(f"    {s['stage_name']:<25} {s['b4']:<4} {fm}")
            
    except Exception as e:
        print(f"  ERROR: {e}")
        results[gene_name] = {"status": "ERROR", "error": str(e)}

# Summary
print(f"\n\n{'='*70}")
print("STRUCTURAL PIPELINE RESULTS: ALL 13 MITOCHONDRIAL PROTEIN-CODING GENES")
print(f"{'='*70}")
print(f"{'Gene':<10} {'Strand':<7} {'bp':<6} {'AA':<5} {'Frob':<6} {'Dist':<8} {'Prim':<8} {'Top Act.'}")
print(f"{'-'*70}")
for g in sorted(results.keys()):
    r = results[g]
    if r["status"] == "ERROR":
        print(f"{g:<10} ERROR: {r['error']}")
    else:
        f = "✓" if r["frobenius_all_stages"] else "✗"
        top_prim = sorted(r["primitive_activations"].items(), key=lambda x: x[1]["count"], reverse=True)
        top_str = f"{top_prim[0][0]}={top_prim[0][1]['count']}x" if top_prim else "none"
        print(f"{g:<10} {r['strand']:<7} {r['length_bp']:<6} {r['aa_length']:<5} {f:<6} {r['dna_to_quaternary_distance']:<8.4f} {r['num_primitives']}/12   {top_str}")

print(f"\n{'='*70}")
print("KEY INVARIANTS:")
print(f"{'='*70}")
all_ok = all(r.get("frobenius_all_stages", False) for r in results.values() if r["status"] == "OK")
all_dist = set(r.get("dna_to_quaternary_distance", 0) for r in results.values() if r["status"] == "OK")
all_consc = set(r.get("consciousness_invariant", 0) for r in results.values() if r["status"] == "OK")
print(f"  Frobenius closure: {'ALL ✓ (' + str(sum(1 for r in results.values() if r.get('frobenius_all_stages', False))) + '/' + str(sum(1 for r in results.values() if r['status']=='OK')) + ')' if all_ok else 'SOME FAILED'}")
print(f"  DNA→Quaternary distance: {all_dist}")
print(f"  Consciousness invariant: {all_consc}")
print(f"  Total primitive activations across all genes: ", end="")
total_prim = {}
for r in results.values():
    if r["status"] == "OK":
        for p, d in r["primitive_activations"].items():
            total_prim[p] = total_prim.get(p, 0) + d["count"]
print(f"{sum(total_prim.values())}")
print(f"  Per-primitive: {', '.join(f'{k}={v}x' for k,v in sorted(total_prim.items(), key=lambda x:-x[1]))}")

print(f"\nFull JSON report written to mito_full_report.json")
# Save JSON
with open("/home/mrnob0dy666/p4rakernel/mito_full_report.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
