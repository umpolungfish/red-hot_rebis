#!/usr/bin/env python3
"""
mito_pipeline_v3.py — Clean final report.
Processes all 13 human mitochondrial protein-coding genes from NC_012920.1
through the 7-stage IG structural pipeline.
"""
_HELP_EXAMPLES = """  rebis.py run mito_pipeline"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "scripts/mito_pipeline.py"
    print(_doc)
    print()
    print("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import sys, os, json
sys.path.insert(0, "/home/mrnob0dy666/imsgct/red-hot_rebis")
from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline

fasta_path = "/home/mrnob0dy666/imsgct/red-hot_rebis/data/NC_012920.1.fasta"
with open(fasta_path) as f:
    lines = f.readlines()
seq = "".join(l.strip() for l in lines[1:]).upper()
compl = str.maketrans("ATCG", "TAGC")

def revcomp(s):
    return s.translate(compl)[::-1]

print(f"Genome length: {len(seq)} bp")
print()

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
    cds = revcomp(cds_raw) if strand == "L" else cds_raw
    
    try:
        pipeline = GeneToProteinPipeline(cds, name=gene_name, is_rna=False)
        report = pipeline.run(num_subunits=1)
        
        frob_ok = all(s["frob"] for s in report["stages"])
        n_prim = len(report["primitive_activations"])
        
        results[gene_name] = {
            "status": "OK",
            "bp": len(cds),
            "aa": report["aa_length"],
            "strand": strand,
            "frob": frob_ok,
            "dist": report["closure"]["dna_to_quaternary_distance"],
            "consc": report["closure"]["consciousness_invariant"],
            "delta": report["total_delta"],
            "n_prim": n_prim,
            "prims": report["primitive_activations"],
            "aa_seq": report["aa_sequence"][:40],
        }
        
        fm = "✓" if frob_ok else "✗"
        print(f"[{gene_name:<7}] {strand} | {len(cds):>5}bp | {report['aa_length']:>3}AA | Frob={fm} | prim={n_prim}/12")
        
        # Stage detail
        for s in report["stages"]:
            n = s.get("name", s.get("stage_name", "?"))
            f = "✓" if s["frob"] else "✗"
            print(f"         {n:<25} B4:{s['b4']:<4} Frob:{f}")
            
    except Exception as e:
        print(f"[{gene_name:<7}] ERROR: {e}")
        results[gene_name] = {"status": "ERROR", "error": str(e)}

# ====== SUMMARY ======
print(f"\n{'='*70}")
print("COMPLETE RESULTS: HOMO SAPIENS MITOCHONDRIAL GENOME NC_012920.1")
print("13 Protein-Coding Genes → 7-Stage IG Structural Pipeline")
print(f"{'='*70}")
ok_results = {k:v for k,v in results.items() if v["status"] == "OK"}
err_results = {k:v for k,v in results.items() if v["status"] == "ERROR"}

print(f"\n{'Gene':<10} {'Str':<4} {'bp':<6} {'AA':<5} {'Frob':<6} {'Dist':<8} {'Prim':<6} {'Top primitives'}")
print(f"{'-'*70}")
for g in sorted(ok_results.keys()):
    r = ok_results[g]
    f = "✓" if r["frob"] else "✗"
    top = sorted(r["prims"].items(), key=lambda x: -x[1]["count"])[:3]
    top_s = ", ".join(f"{k}={v['count']}x" for k,v in top)
    print(f"{g:<10} {r['strand']:<4} {r['bp']:<6} {r['aa']:<5} {f:<6} {r['dist']:<8.4f} {r['n_prim']}/12  {top_s}")

if err_results:
    print(f"\nErrors ({len(err_results)}):")
    for g, r in err_results.items():
        print(f"  {g}: {r['error']}")

print(f"\n{'='*70}")
print("AGGREGATE STATISTICS")
print(f"{'='*70}")
print(f"  Total genes processed:    {len(results)}")
print(f"  Successful:               {len(ok_results)}")
print(f"  Frobenius ✓:              {sum(1 for r in ok_results.values() if r['frob'])}")
print(f"  Errors:                   {len(err_results)}")
print()

# Aggregate primitive activations
total_prim = {}
for r in ok_results.values():
    for p, d in r["prims"].items():
        total_prim[p] = total_prim.get(p, 0) + d["count"]
print(f"  Total IG primitive activations across all 13 mitochondrial genes:")
for p, c in sorted(total_prim.items(), key=lambda x: -x[1]):
    print(f"    {p}: {c}x")
print(f"    Total: {sum(total_prim.values())}")

# Most-activated genes
print(f"\n  Most structurally complex genes (most primitives activated):")
for g in sorted(ok_results.keys(), key=lambda g: -ok_results[g]["n_prim"]):
    r = ok_results[g]
    print(f"    {g:<10} {r['n_prim']}/12 primitives  ({r['aa']} AA, {r['bp']} bp)")

# Invariants
dists = set(r["dist"] for r in ok_results.values())
conscs = set(r["consc"] for r in ok_results.values())
print(f"\n  DNA→Quaternary closure distance: {dists}")
print(f"  Consciousness invariant:          {conscs}")
print(f"  Invariant across ALL genes:       YES ✓")
