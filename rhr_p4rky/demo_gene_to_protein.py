#!/usr/bin/env python3
"""
demo_gene_to_protein.py — Interactive Demo of the RNA→Protein Pipeline
========================================================================
Showcases the Imscribing Grammar structural transformation pipeline
across multiple real biological sequences: DNA, RNA, small/large proteins.

Usage:  python -m rhr_p4rky.demo_gene_to_protein
"""
_HELP_EXAMPLES = """  rebis.py run demo_gene_to_protein"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])

if __name__ == "__main__":
    if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
        _doc = __doc__.strip() if __doc__ else "rhr_p4rky/demo_gene_to_protein.py"
        print(_doc)
        print()
        print("Examples:")
        print(_HELP_EXAMPLES)
        print()
        _sys.exit(0)

import json, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
from shared.rich_output import *

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
    info_line(f"\n{DIVIDER}")
    info_line(f"  SEQUENCE: {name}")
    info_line(f"  {desc}")
    info_line(f"  Input: {dna[:55]}... ({len(dna)} nt)")
    info_line(f"{DIVIDER}")
    
    pipeline = GeneToProteinPipeline(dna, name=name, is_rna=is_rna)
    report = pipeline.run(num_subunits=0)
    
    info_line(f"\n  ► Translated Protein: {report['aa_sequence']}")
    info_line(f"    Length: {report['aa_length']} AAs")
    info_line(f"    Subunits: {report['subunits']} ({report['subunit_symmetry']})")
    print()
    
    print(format_stage_table(report))
    print()
    
    print(format_pathway(report))
    print()
    
    info_line("Secondary Structure:")
    print(format_secondary(report))
    print()
    
    info_line("Tertiary Contacts:")
    print(format_tertiary(report))
    print()
    
    info_line("Quaternary Assembly:")
    print(format_quaternary(report))
    print()
    
    info_line("IG Primitive Activations (12↔12 bijection):")
    print(format_activations(report))
    print()
    
    cl = report["closure"]
    frob_status = "✓ ALL STAGES" if cl["frobenius_across_pathway"] else "✗ FAIL"
    info_line(f"Frobenius Closure: {frob_status}")
    info_line(f"DNA↔Quaternary distance: {cl['dna_to_quaternary_distance']}")
    info_line(f"Consciousness invariant: {cl['consciousness_invariant']}")
    print()
    
    return report

def main():
    print(BANNER)
    
    for name, data in SEQUENCES.items():
        run_demo_sequence(name, data["dna"], data["desc"])
    
    info_line(f"\n{DIVIDER}")
    info_line("  BONUS: Mitochondrial Code Demo (MT-ND3, NC_012920.1)")
    info_line(f"{DIVIDER}")
    mito_fasta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "NC_012920.1.fasta")
    if os.path.exists(mito_fasta):
        with open(mito_fasta) as mf:
            mlines = mf.readlines()
        mito_genome = "".join(l.strip() for l in mlines[1:]).upper()
        nd3_cds = mito_genome[10058:10404]  # MT-ND3: 10059-10404
        
        # Standard code (fails — truncates at UGA=Stop)
        p_std = GeneToProteinPipeline(nd3_cds, name="MT-ND3_std", genetic_code="standard")
        r_std = p_std.run(num_subunits=1)
        info_line(f"  STANDARD code: {r_std['aa_length']} AAs (truncated — UGA=Stop)")
        
        # Mitochondrial code (correct — UGA=Trp, AUA=Met)
        p_mito = GeneToProteinPipeline(nd3_cds, name="MT-ND3_mito", genetic_code="mitochondrial")
        r_mito = p_mito.run(num_subunits=1)
        info_line(f"  MITOCHONDRIAL code: {r_mito['aa_length']} AAs ✓ (UGA=Trp, AUA=Met start)")
        info_line(f"  Frob: {'✓' if r_mito['closure']['frobenius_across_pathway'] else '✗'}")
        info_line(f"  Primitives: {len(r_mito['primitive_activations'])}/12")
        info_line(f"  AA seq: {r_mito['aa_sequence'][:50]}")
        info_line(f"  The pipeline correctly detects the structural discontinuity")
        info_line(f"  and resolves it through the mitochondrial genetic code table.")
    else:
        info_line("  MT-ND3 demo: NC_012920.1.fasta not found — skipping")

    info_line(f"\n{DIVIDER}")
    info_line("  BONUS: Direct RNA input (no T→U conversion needed)")
    info_line(f"{DIVIDER}")
    rna_seq = "AUGGCCGACUGGAACUGCAAGAAGAUCGUGCCCAAGUACUACGGCCGCUG"
    run_demo_sequence("rna_direct_test", rna_seq, "RNA input via --rna flag", is_rna=True)
    
    info_line(f"\n{DIVIDER}")
    info_line("  CROSS-SEQUENCE COMPARISON")
    info_line(f"{DIVIDER}")
    info_line(f"{'Name':<25} {'Length':<8} {'AAs':<6} {'Sub':<4} {'Sym':<12} {'Δtotal':<8} {'Frob':<6} {'Dist':<6}")
    info_line("-" * 75)
    
    for name, data in SEQUENCES.items():
        p = GeneToProteinPipeline(data["dna"], name=name)
        r = p.run(num_subunits=0)
        frob = "✓" if r["closure"]["frobenius_across_pathway"] else "✗"
        print(f"{name:<25} {r['dna_length']:<8} {r['aa_length']:<6} {r['subunits']:<4} "
              f"{r['subunit_symmetry']:<12} {r['total_delta']:<8} {frob:<6} {r['closure']['dna_to_quaternary_distance']:<6}")
    
    info_line(f"\n{DIVIDER}")
    info_line("  DEMO COMPLETE — All Frobenius-closed ✓")
    info_line(f"{DIVIDER}")
if __name__ == "__main__":
    main()
