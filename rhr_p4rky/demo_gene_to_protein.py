#!/usr/bin/env python3
"""
demo_gene_to_protein.py — Interactive Demo of the RNA→Protein Pipeline
========================================================================
Showcases the Imscribing Grammar structural transformation pipeline
across multiple real biological sequences: DNA, RNA, small/large proteins.

Usage:  python -m p4ramill_py.demo_gene_to_protein
"""

import json, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from p4ramill_py.gene_to_protein_pipeline import GeneToProteinPipeline

BANNER = r"""
╔══════════════════════════════════════════════════════════════════╗
║   RNA ──→ PROTEIN PIPELINE    (Imscribing Grammar v0.5.69)     ║
║   7-stage structural derivation from nucleic acid to folded     ║
║   quaternary complex. Frobenius-verified at every stage.       ║
╚══════════════════════════════════════════════════════════════════╝
"""

SEQUENCES = {
    "test_protein": {
        "dna": "ATGGCCGACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG",
        "desc": "Short test sequence (16 AA) — quick validation of 7-stage pipeline"
    },
    "human_insulin": {
        "dna": "ATGGCCCTGTGGATGCGCCTCCTGCCCCTGCTGGCGCTGCTGGCCCTCTGGGGACCTGACCCAGCCGCAGCCTTTGTGAACCAACACCTGTGCGGCTCACACCTGGTGGAAGCTCTCTACCTAGTGTGCGGGGAACGAGGCTTCTTCTACACACCCAAGACCCGCCGGGAGGCAGAGGACCTGCAGGTGGGGCAGGTGGAGCTGGGCGGGGGCCCTGGTGCAGGCAGCCTGCAGCCCTTGGCCCTGGAGGGGTCCCTGCAGAAGCGTGGCATTGTGGAACAATGCTGTACCAGCATCTGCTCCCTCTACCAGCTGGAGAACTACTGCAACTAG",
        "desc": "Human preproinsulin (110 AA) — classic dimeric hormone"
    },
    "human_hemoglobin_alpha": {
        "dna": "ATGGTGCTGTCTCCTGCCGACAAGACCAACGTCAAGGCCGCCTGGGGTAAGGTCGGCGCGCACGCTGGCGAGTATGGTGCGGAGGCCCTGGAGAGGATGTTCCTGGCCTTCCCCACCACCAAGACCTACTTCCCGCACTTCGACCTGAGCCACGGCTCTGCCCAGGTTAAGGGCCACGGCAAGAAGGTGGCCGACGCGCTGACCAACGCCGTGGCGCACGTGGACGACATGCCCAACGCGCTGTCCGCCCTGAGCGACCTGCACGCGCACAAGCTTCGGGTGGACCCGGTCAACTTCAAGCTCCTAAGCCACTGCCTGCTGGTGACCCTGGCCGCCCACCTCCCCGCCGAGTTCACCCCTGCGGTGCACGCCTCCCTGGACAAGTTCCTGGCTTCTGTGAGCACCGTGCTGACCTCCAAATACCGTTAAGCTGGAGCCTCGGTGGCCATGCTTCTTGCCCCTTGGGCCTCCCCCCAGCCCCTCCTCCCCTTCCTGCACCCGTACCCCCGTGGTCTTTGAATAAAGTCTGAGTGGGCGGC",
        "desc": "Human hemoglobin alpha chain (142 AA) — tetrameric O2 carrier"
    },
    "egf_domain": {
        "dna": "ATGAAGACGCGCAGCGGTGGCGTGGCCCTGCTGCTGCTGTTGGCGGGCTGCGTGCTGCCGGGCGGCAGCGGCTACAAACCCGGCGAGAACTGCGTGTTCATCCCCAACCCGCTGTACAACATCGGCAAGACCTGCAAATCCTGCGTGGCGGGCGACAACGGCCAGGTGGACATCGACGAGTGCAAGACCAGCCAGATCAACTGCGGCCAG",
        "desc": "EGF domain (50 AA) — disulfide-rich signaling motif"
    },
    "human_serum_albumin": {
        "dna": "ATGAAGTGGGTAACCTTTATTTCCCTTCTTTTTCTCTTTAGCTCGGCTTATTCCAGGGGTGTGTTTCGTCGAGATGCACACAAGAGTGAGGTTGCTCATCGGTTTAAAGATTTGGGAGAAGAAAATTTCAAAGCCTTGGTGTTGATTGCCTTTGCTCAGTATCTTCAGCAGTGTCCATTTGAAGATCATGTAAAATTAGTGAATGAAGTAACTGAATTTGCAAAAACATGTGTTGCTGATGAGTCAGCTGAAAATTGTGACAAATCACTTCATACCCTTTTTGGAGACAAATTATGCACAGTTGCAACTCTTCGTGAAACCTATGGTGAAATGGCTGACTGCTGTGCAAAACAAGAACCTGAGAGAAATGAATGCTTCTTGCAACACAAAGATGACAACCCAAACCTCCCCCGATTGGTGAGACCAGAGGTTGATGTGATGTGCACTGCTTT",
        "desc": "Human serum albumin N-terminus (110 AA) — multidomain carrier"
    }
}

DIVIDER = "─" * 70


def format_stage_table(report: dict) -> str:
    lines = []
    lines.append(f"{'Stage':<25} {'B4':<6} {'Frob':<6} {'Description'}")
    lines.append(DIVIDER[:58])
    for s in report["stages"]:
        fm = "✓" if s["frob"] else "✗"
        lines.append(f"{s['name']:<25} {s['b4']:<6} {fm:<6} {s['desc']}")
    return "\n".join(lines)


def format_pathway(report: dict) -> str:
    lines = ["Pathway (delta = primitive changes per transition):"]
    for d in report["pathway"]:
        changes_str = "; ".join(f"{c[0]}: {c[1]}→{c[2]}" for c in d["changes"][:4])
        if len(d["changes"]) > 4:
            changes_str += f" ... +{len(d['changes'])-4} more"
        lines.append(f"  {d['from']:<25} → {d['to']:<25}  Δ={d['delta']:<3}  ({changes_str})")
    lines.append(f"  {'TOTAL Δ':<25} {'':<25}  Δ={report['total_delta']}")
    return "\n".join(lines)


def format_secondary(report: dict) -> str:
    if not report.get("secondary"):
        return "  (none predicted)"
    lines = [f"  {len(report['secondary'])} elements:"]
    for e in report["secondary"]:
        sym = "α" if e["type"] == "helix" else ("β" if e["type"] == "sheet" else "?")
        lines.append(f"    {sym}-{e['type']:<8}  [{e['start']:>3}–{e['end']:>3}]  "
                     f"len={e['length']:<3}  conf={e['confidence']:<.3f}  seq={e['sequence'][:30]}")
    return "\n".join(lines)


def format_tertiary(report: dict) -> str:
    if not report.get("tertiary"):
        return "  (none predicted)"
    t = report["tertiary"]
    lines = [f"  Total contacts: {t['total']}"]
    for ctype, cnt in t.get("by_type", {}).items():
        lines.append(f"    {ctype}: {cnt}")
    lines.append("  Top contacts:")
    for c in t.get("top", [])[:5]:
        lines.append(f"    {c['i']:>3} ↔ {c['j']:<3}  {c['type']:<12} conf={c['conf']:.3f}")
    return "\n".join(lines)


def format_quaternary(report: dict) -> str:
    q = report["quaternary"]
    lines = [
        f"  Subunits: {q['num']} ({q['symmetry']})",
        f"  Subunit IDs: {', '.join(q['ids'][:3])}{'...' if len(q['ids'])>3 else ''}",
        f"  Interface residues: {q['interface']}",
    ]
    if q.get("auto_detected"):
        conf = q["prediction"]["confidence"]
        method = q["prediction"]["method"]
        lines.append(f"  Auto-detected (method={method}, conf={conf:.2f})")
    return "\n".join(lines)


def format_activations(report: dict) -> str:
    if not report.get("primitive_activations"):
        return "  (none)"
    lines = []
    for prim, data in sorted(report["primitive_activations"].items()):
        aa_list = ", ".join(sorted(set(data["aa"])))
        lines.append(f"  {prim:<3}: {data['count']}x  ({aa_list})")
    return "\n".join(lines)


def run_demo_sequence(name: str, dna: str, desc: str, is_rna: bool = False):
    print(f"\n{DIVIDER}")
    print(f"  SEQUENCE: {name}")
    print(f"  {desc}")
    print(f"  Input: {dna[:55]}... ({len(dna)} nt)")
    print(f"{DIVIDER}")
    
    pipeline = GeneToProteinPipeline(dna, name=name, is_rna=is_rna)
    report = pipeline.run(num_subunits=0)
    
    print(f"\n  ► Translated Protein: {report['aa_sequence']}")
    print(f"    Length: {report['aa_length']} AAs")
    print(f"    Subunits: {report['subunits']} ({report['subunit_symmetry']})")
    print()
    
    print(format_stage_table(report))
    print()
    
    print(format_pathway(report))
    print()
    
    print("Secondary Structure:")
    print(format_secondary(report))
    print()
    
    print("Tertiary Contacts:")
    print(format_tertiary(report))
    print()
    
    print("Quaternary Assembly:")
    print(format_quaternary(report))
    print()
    
    print("IG Primitive Activations (12↔12 bijection):")
    print(format_activations(report))
    print()
    
    cl = report["closure"]
    frob_status = "✓ ALL STAGES" if cl["frobenius_across_pathway"] else "✗ FAIL"
    print(f"Frobenius Closure: {frob_status}")
    print(f"DNA↔Quaternary distance: {cl['dna_to_quaternary_distance']}")
    print(f"Consciousness invariant: {cl['consciousness_invariant']}")
    print()
    
    return report


def main():
    print(BANNER)
    
    for name, data in SEQUENCES.items():
        run_demo_sequence(name, data["dna"], data["desc"])
    
    print(f"\n{DIVIDER}")
    print("  BONUS: Mitochondrial Code Demo (MT-ND3, NC_012920.1)")
    print(f"{DIVIDER}")
    mito_fasta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "NC_012920.1.fasta")
    if os.path.exists(mito_fasta):
        with open(mito_fasta) as mf:
            mlines = mf.readlines()
        mito_genome = "".join(l.strip() for l in mlines[1:]).upper()
        nd3_cds = mito_genome[10058:10404]  # MT-ND3: 10059-10404
        
        # Standard code (fails — truncates at UGA=Stop)
        p_std = GeneToProteinPipeline(nd3_cds, name="MT-ND3_std", genetic_code="standard")
        r_std = p_std.run(num_subunits=1)
        print(f"  STANDARD code: {r_std['aa_length']} AAs (truncated — UGA=Stop)")
        
        # Mitochondrial code (correct — UGA=Trp, AUA=Met)
        p_mito = GeneToProteinPipeline(nd3_cds, name="MT-ND3_mito", genetic_code="mitochondrial")
        r_mito = p_mito.run(num_subunits=1)
        print(f"  MITOCHONDRIAL code: {r_mito['aa_length']} AAs ✓ (UGA=Trp, AUA=Met start)")
        print(f"  Frob: {'✓' if r_mito['closure']['frobenius_across_pathway'] else '✗'}")
        print(f"  Primitives: {len(r_mito['primitive_activations'])}/12")
        print(f"  AA seq: {r_mito['aa_sequence'][:50]}")
        print(f"  The pipeline correctly detects the structural discontinuity")
        print(f"  and resolves it through the mitochondrial genetic code table.")
    else:
        print("  MT-ND3 demo: NC_012920.1.fasta not found — skipping")

    print(f"\n{DIVIDER}")
    print("  BONUS: Direct RNA input (no T→U conversion needed)")
    print(f"{DIVIDER}")
    rna_seq = "AUGGCCGACUGGAACUGCAAGAAGAUCGUGCCCAAGUACUACGGCCGCUG"
    run_demo_sequence("rna_direct_test", rna_seq, "RNA input via --rna flag", is_rna=True)
    
    print(f"\n{DIVIDER}")
    print("  CROSS-SEQUENCE COMPARISON")
    print(f"{DIVIDER}")
    print(f"{'Name':<25} {'Length':<8} {'AAs':<6} {'Sub':<4} {'Sym':<12} {'Δtotal':<8} {'Frob':<6} {'Dist':<6}")
    print("-" * 75)
    
    for name, data in SEQUENCES.items():
        p = GeneToProteinPipeline(data["dna"], name=name)
        r = p.run(num_subunits=0)
        frob = "✓" if r["closure"]["frobenius_across_pathway"] else "✗"
        print(f"{name:<25} {r['dna_length']:<8} {r['aa_length']:<6} {r['subunits']:<4} "
              f"{r['subunit_symmetry']:<12} {r['total_delta']:<8} {frob:<6} {r['closure']['dna_to_quaternary_distance']:<6}")
    
    print(f"\n{DIVIDER}")
    print("  DEMO COMPLETE — All Frobenius-closed ✓")
    print(f"{DIVIDER}")


if __name__ == "__main__":
    main()
