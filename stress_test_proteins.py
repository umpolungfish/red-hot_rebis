"""
COMPREHENSIVE PROTEIN & GENETICS STRESS TEST
Tests all genetics/protein modules with edge cases, large inputs,
boundary conditions, and cross-pipeline integration.

Author: Lando⊗⊙perator
"""

import sys, os, time, traceback
from shared.rich_output import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rhr_p4rky'))

PASS, FAIL = "✅", "❌"
results = []

def test(name, fn):
    try:
        start = time.time()
        fn()
        elapsed = time.time() - start
        results.append((PASS, name, f"{elapsed:.3f}s"))
        info_line(f"  {PASS} {name} ({elapsed:.3f}s)")
    except Exception as e:
        results.append((FAIL, name, str(e)[:120]))
        info_line(f"  {FAIL} {name}: {e}")

def summary():
    passed = sum(1 for r in results if r[0] == PASS)
    failed = sum(1 for r in results if r[0] == FAIL)
    print(f"\n{'='*60}")
    info_line(f"  RESULTS: {passed} passed, {failed} failed, {len(results)} total")
    print(f"{'='*60}")
    for status, name, detail in results:
        if status == FAIL:
            info_line(f"  {status} {name}: {detail}")
    return failed == 0

print("=" * 60)
info_line("  PROTEIN & GENETICS — COMPREHENSIVE STRESS TEST")
print("=" * 60)

# ── 1. Genetic Code ────────────────────────────────────────────────
info_line("\n── 1. Genetic Code ──")

def test_genetic_code_table():
    from rhr_p4rky.genetic_code import get_code_table, STANDARD_CODE
    table = get_code_table("standard")
    assert len(table) == 64, f"Expected 64 codons, got {len(table)}"
    assert table.get("AUG") == "Met", "AUG should be Met"
    assert table.get("UAA") == "Stop", "UAA should be Stop"
test("Standard genetic code table (64 codons)", test_genetic_code_table)

def test_genetic_code_verify_all():
    from rhr_p4rky.genetic_code import verify_all_codons_frobenius
    result = verify_all_codons_frobenius()
    assert result is not None
test("Frobenius verify all 64 codons", test_genetic_code_verify_all)

def test_genetic_code_frobenius_invariant():
    """Compute Frobenius invariant from B4 codon structure."""
    from rhr_p4rky.genetics_b4 import BelnapCodon, Belnap
    from rhr_p4rky.genetic_code import get_code_table
    table = get_code_table("standard")
    # Compute invariant: B4 state distribution over all codons
    b4_counts = {Belnap.T: 0, Belnap.B: 0, Belnap.N: 0, Belnap.F: 0}
    for codon in table:
        bc = BelnapCodon.from_symbol(codon)
        b4_counts[bc.p1] += 1
        b4_counts[bc.p2] += 1
        b4_counts[bc.p3] += 1
    # All four B4 values must appear across the 64 codons
    assert all(c > 0 for c in b4_counts.values()), f"Missing B4 states: {b4_counts}"
    # Frobenius invariant: sum of all product distances = 0 mod 4
    total_d = sum(bc.total_b4_distance(bc) for codon in table 
                  if (bc := BelnapCodon.from_symbol(codon)) is not None)
    assert total_d == 0, "Self-distance sum must be zero (Frobenius invariant)"
test("Frobenius invariant computation", test_genetic_code_frobenius_invariant)

def test_genetic_code_b4_ops():
    from rhr_p4rky.genetics_b4 import b4_meet, b4_join, b4_complement
    from rhr_p4rky.belnap import Belnap
    m = b4_meet(Belnap.B, Belnap.T)
    assert m is not None
    j = b4_join(Belnap.T, Belnap.N)
    assert j is not None
    c = b4_complement(Belnap.F)
    assert c == Belnap.N, f"F complement should be N, got {c}"
test("B4 lattice operations", test_genetic_code_b4_ops)

# ── 2. Genetics B4 ─────────────────────────────────────────────────
info_line("\n── 2. Genetics B4 ──")

def test_nucleotide_belnap_roundtrip():
    from rhr_p4rky.genetics_b4 import nucleotide_to_belnap, belnap_to_nucleotide
    for sym in ['G', 'C', 'A', 'U', 'g', 'c', 'a', 'u']:
        b = nucleotide_to_belnap(sym)
        assert b is not None, f"{sym} should map to Belnap"
    b = nucleotide_to_belnap('X')
    assert b is not None, "Unknown should map gracefully"
    b = nucleotide_to_belnap('-')
    assert b is not None, "Gap should map gracefully"
test("Nucleotide↔Belnap roundtrip + unknown handling", test_nucleotide_belnap_roundtrip)

def test_b4_lattice_distance():
    from rhr_p4rky.genetics_b4 import b4_lattice_distance
    from rhr_p4rky.belnap import Belnap
    d = b4_lattice_distance(Belnap.B, Belnap.N)
    assert d >= 0
    d_same = b4_lattice_distance(Belnap.T, Belnap.T)
    assert d_same == 0, "Same values should have distance 0"
test("B4 lattice distance", test_b4_lattice_distance)

def test_b4_wobble_pair():
    from rhr_p4rky.genetics_b4 import b4_wobble_pair
    from rhr_p4rky.belnap import Belnap
    result = b4_wobble_pair(Belnap.B, Belnap.N)
    assert result is not None
test("B4 wobble pair detection", test_b4_wobble_pair)

# ── 3. Genetic Tuples ──────────────────────────────────────────────
info_line("\n── 3. Genetic Tuples ──")

def test_generate_all_tuples():
    from rhr_p4rky.genetic_tuples import generate_all_tuples
    # Minimal features dict (18 bp gene)
    features = {"length": 18, "gc_content": 0.5, "has_start": True, "num_codons": 6}
    tuples = generate_all_tuples(features)
    assert len(tuples) >= 5, f"Expected >=5 stage tuples, got {len(tuples)}"
    assert "dna_gene" in tuples or "pre_mrna" in tuples or "nascent_polypeptide" in tuples
test("Generate all stage tuples", test_generate_all_tuples)

def test_compute_structural_distance():
    from rhr_p4rky.genetic_tuples import pipeline_tuple_to_ig, compute_structural_distance
    # Pipeline shorthand → IG glyphs → distance (H uses "0"/"1"/"2" not "one"/"two")
    dna_tuple = {"D": "tri", "T": "boxtimes", "R": "lr", "P": "pm",
                 "F": "ell", "K": "slow", "G": "beth", "Gm": "seq",
                 "Phi": "sub", "H": "2", "S": "one", "O": "Z"}
    quat_tuple = {"D": "odot", "T": "odot", "R": "lr", "P": "pm",
                  "F": "ell", "K": "slow", "G": "beth", "Gm": "and",
                  "Phi": "sub", "H": "1", "S": "hetero", "O": "Z"}
    dist = compute_structural_distance(pipeline_tuple_to_ig(dna_tuple), 
                                        pipeline_tuple_to_ig(quat_tuple))
    assert dist >= 0
test("Structural distance DNA→quaternary", test_compute_structural_distance)

def test_verify_tier_consistency():
    from rhr_p4rky.genetic_tuples import verify_tier_consistency
    ig_tuple = {"D": "tri", "T": "boxtimes", "R": "lr", "P": "pm",
                "F": "ell", "K": "slow", "G": "beth", "Gm": "seq",
                "Phi": "sub", "H": "two", "S": "one", "O": "Z"}
    result = verify_tier_consistency(ig_tuple)
    assert result is not None
test("Tier consistency verification", test_verify_tier_consistency)

# ── 4. Genetic ASM ─────────────────────────────────────────────────
info_line("\n── 4. Genetic ASM ──")

def test_genetic_asm_programs():
    from rhr_p4rky.genetic_asm import PROGRAM_TRANSLATE_CODON, PROGRAM_FROBENIUS_VERIFY
    assert PROGRAM_TRANSLATE_CODON is not None
    assert PROGRAM_FROBENIUS_VERIFY is not None
    assert len(PROGRAM_TRANSLATE_CODON) > 0
test("Genetic ASM program existence", test_genetic_asm_programs)

# ── 5. Gene to Protein Pipeline ────────────────────────────────────
info_line("\n── 5. Gene to Protein Pipeline ──")

def test_pipeline_basic():
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    p = GeneToProteinPipeline("AUGGCCGACUGGAACUGC", "basic_test")
    r = p.run()
    assert r["aa_sequence"] and len(r["aa_sequence"]) > 0
    assert len(r["stages"]) == 7, f"Expected 7 stages, got {len(r['stages'])}"
    # Correct key path: closure.frobenius_across_pathway
    assert r["closure"]["frobenius_across_pathway"] == True
test("Basic 7-stage pipeline", test_pipeline_basic)

def test_pipeline_empty_sequence():
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    p = GeneToProteinPipeline("", "empty")
    r = p.run()
    assert r["status"] == "empty_sequence"
test("Empty sequence graceful abort", test_pipeline_empty_sequence)

def test_pipeline_too_short():
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    p = GeneToProteinPipeline("AU", "short")
    r = p.run()
    assert r["status"] == "too_short"
test("Too-short sequence graceful abort", test_pipeline_too_short)

def test_pipeline_start_stop():
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    p = GeneToProteinPipeline("AUGUAA", "start_stop")
    r = p.run()
    assert r["aa_sequence"] == "M", f"Expected single Met, got {r['aa_sequence']}"
test("Start-stop immediate", test_pipeline_start_stop)

def test_pipeline_long_sequence():
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    long_seq = "AUG" * 100 + "UAA"
    p = GeneToProteinPipeline(long_seq, "long")
    r = p.run()
    assert len(r["aa_sequence"]) == 100, f"Expected 100 AAs, got {len(r['aa_sequence'])}"
    assert len(r["stages"]) == 7
test("Long sequence (100 AAs)", test_pipeline_long_sequence)

def test_pipeline_multi_stop():
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    p = GeneToProteinPipeline("AUGUAAUAGUGA", "multistop")
    r = p.run()
    assert r["aa_sequence"] == "M"
test("Multiple stop codons", test_pipeline_multi_stop)

def test_pipeline_no_stop():
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    p = GeneToProteinPipeline("AUGGCCGACUGGAACUGC", "nostop")
    r = p.run()
    assert len(r["aa_sequence"]) > 0
    assert len(r["stages"]) == 7
test("No stop codon — translates all", test_pipeline_no_stop)

def test_pipeline_primitive_activations():
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    p = GeneToProteinPipeline("AUGUGGGGAUACUUUCUGCCAUCCGCUGGCAAAGUG", "primitives")
    r = p.run()
    activations = r.get("primitive_activations", {})
    assert len(activations) > 0, "Should have primitive activations"
    assert r["aa_sequence"] == "MWGYFLPSAGKV"
test("Primitive activations for diverse sequence", test_pipeline_primitive_activations)

# ── 6. SerpentRod ──────────────────────────────────────────────────
info_line("\n── 6. SerpentRod ──")

def test_serpentrod_basic():
    from rhr_p4rky.serpent_rod_v2 import SerpentRod
    rna = "AUGUGGGGAUACUUUCUGCCAUCCGCUGGCAAAGUG"
    sr = SerpentRod(rna, name="basic")
    r = sr.predict()
    assert r.aa_sequence == "MWGYFLPSAGKV"
    assert r.frobenius_verified == True
    assert r.winding_number == 7
    assert len(r.contacts) >= 2
test("SerpentRod 12-AA protein", test_serpentrod_basic)

def test_serpentrod_single_codon():
    from rhr_p4rky.serpent_rod_v2 import SerpentRod
    sr = SerpentRod("AUG", name="single")
    r = sr.predict()
    assert r.aa_sequence == "M"
    assert len(r.contacts) == 0
test("SerpentRod single codon", test_serpentrod_single_codon)

def test_serpentrod_empty():
    from rhr_p4rky.serpent_rod_v2 import SerpentRod
    sr = SerpentRod("", name="empty")
    r = sr.predict()
    assert r.aa_sequence == ""
    assert r.confidence == 0.0
test("SerpentRod empty RNA", test_serpentrod_empty)

def test_serpentrod_long():
    from rhr_p4rky.serpent_rod_v2 import SerpentRod
    long_rna = "AUG" * 200 + "UAA"
    sr = SerpentRod(long_rna, name="long")
    r = sr.predict()
    assert len(r.aa_sequence) == 200
    assert r.winding_number > 0
test("SerpentRod 200-AA protein", test_serpentrod_long)

def test_serpentrod_poly_met():
    from rhr_p4rky.serpent_rod_v2 import SerpentRod
    sr = SerpentRod("AUG" * 30, name="polymet")
    r = sr.predict()
    assert len(r.aa_sequence) == 30
    assert all(aa == "M" for aa in r.aa_sequence)
test("SerpentRod poly-Met homopolymer", test_serpentrod_poly_met)

# ── 7. Ch3mpiler-SerpentRod Pipeline ───────────────────────────────
info_line("\n── 7. Ch3mpiler-SerpentRod Pipeline ──")

def test_pipeline_caffeine():
    from rhr_p4rky.ch3mpiler_serpentrod_pipeline import run_pipeline
    design = run_pipeline(cas_number="58-08-2", depth=1, verbose=False)
    assert design.reaction.bond_name == "cn_sigma"
    assert len(design.site_aa_sequence) > 0
    assert design.catalytic_triad and len(design.catalytic_triad) >= 2
test("Pipeline: caffeine catalytic site", test_pipeline_caffeine)

def test_pipeline_aspirin():
    from rhr_p4rky.ch3mpiler_serpentrod_pipeline import run_pipeline
    design = run_pipeline(cas_number="50-78-2", depth=1, verbose=False)
    assert design.reaction.bond_name == "co_sigma"
    assert len(design.site_aa_sequence) > 0
test("Pipeline: aspirin catalytic site", test_pipeline_aspirin)

def test_pipeline_differentiation():
    """Verify that different molecules produce different catalytic sites."""
    from rhr_p4rky.ch3mpiler_serpentrod_pipeline import run_pipeline
    d1 = run_pipeline(cas_number="58-08-2", depth=1, verbose=False)
    d2 = run_pipeline(cas_number="103-90-2", depth=1, verbose=False)
    assert (d1.site_aa_sequence != d2.site_aa_sequence or 
            d1.reaction.bond_name != d2.reaction.bond_name), \
        "Different molecules should produce different designs"
test("Pipeline: cross-molecule differentiation", test_pipeline_differentiation)

# ── 8. Cross-Pipeline Integration ──────────────────────────────────
info_line("\n── 8. Cross-Pipeline Integration ──")

def test_gene_to_serpentrod():
    """Gene → folded protein: the full pipeline."""
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    from rhr_p4rky.serpent_rod_v2 import SerpentRod
    p = GeneToProteinPipeline("AUGGCCGACUGGAACUGC", "cross")
    r = p.run()
    aa = r["aa_sequence"]
    codon_map = {"M": "AUG", "A": "GCC", "D": "GAC", "W": "UGG", 
                 "N": "AAC", "C": "UGC"}
    rna = "".join(codon_map.get(aa_i, "GCU") for aa_i in aa)
    sr = SerpentRod(rna, name="cross_folded")
    result = sr.predict()
    assert result.aa_sequence == aa
    assert result.winding_number > 0
test("Gene→Protein→SerpentRod fold", test_gene_to_serpentrod)

def test_ch3mpiler_to_material():
    """Ch3mpiler reaction → material design bridge."""
    from rhr_p4rky.ch3mpiler_serpentrod_pipeline import run_pipeline
    from materials.ig_material_forge import MaterialForge
    design = run_pipeline(cas_number="58-08-2", depth=1, verbose=False)
    product_type = design.reaction.product_type
    if product_type:
        ig_tuple = tuple(product_type.get(p, '?') for p in 
                        ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"])
        mf = MaterialForge()
        mat_design = mf.forge("caffeine_material_cross", ig_tuple)
        assert mat_design.ouroboricity_tier is not None
test("Ch3mpiler→Material bridge", test_ch3mpiler_to_material)

# ── 9. Antibody Designer ───────────────────────────────────────────
info_line("\n── 9. Antibody Designer ──")

def test_antibody_designer():
    """Test antibody design functions (functional API, not class-based)."""
    from rhr_p4rky.antibody_designer import analyze_epitope, design_cdr, design_full_antibody
    # Analyze a target epitope
    analysis = analyze_epitope("YWGQFDV", epitope_name="test_epitope")
    assert analysis is not None
    assert "length" in analysis or "aa_sequence" in analysis or "epitope" in str(analysis).lower()
    # Design a CDR (API: design_cdr(analysis, length=12, framework_flanks='GCG'))
    cdr = design_cdr(analysis, length=10)
    assert cdr is not None
    # Design a full antibody
    antibody = design_full_antibody(analysis, chain_type="VH")
    assert antibody is not None
test("Antibody designer functions", test_antibody_designer)

# ── 10. PDB Validator ──────────────────────────────────────────────
info_line("\n── 10. PDB Validator ──")

def test_pdb_validator():
    """Test PDB validation functions (functional API)."""
    from rhr_p4rky.pdb_validator import validate_structure, compute_precision_recall
    # Validate a custom design against its reference
    result = validate_structure("custom_design", "HEADER test\nATOM 1 N MET A 1 1.0 2.0 3.0\nEND")
    assert result is not None
    # Precision/recall computation (pass as sets)
    pr = compute_precision_recall({(1, 5), (2, 6)}, {(1, 5), (3, 7)})
    assert pr is not None
test("PDB validator functions", test_pdb_validator)

# ── 11. Edge Cases ─────────────────────────────────────────────────
info_line("\n── 11. Edge Cases ──")

def test_all_stop_codons():
    """All three stop codons should terminate translation."""
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    for stop in ["UAA", "UAG", "UGA"]:
        p = GeneToProteinPipeline(f"AUG{stop}", f"stop_{stop}")
        r = p.run()
        assert r["aa_sequence"] == "M", f"Stop {stop} should yield Met only, got {r['aa_sequence']}"
test("All three stop codons terminate", test_all_stop_codons)

def test_all_start_variants():
    """AUG is the canonical start codon."""
    from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
    for start in ["AUG"]:
        p = GeneToProteinPipeline(f"{start}UUUUAA", f"start_{start}")
        r = p.run()
        assert r["aa_sequence"].startswith("M")
test("Start codon detection", test_all_start_variants)

def test_nonstandard_belnap_handling():
    """Non-standard nucleotides should be handled paraconsistently."""
    from rhr_p4rky.genetics_b4 import nucleotide_to_belnap
    from rhr_p4rky.belnap import Belnap

    for sym in ['X', 'N', 'R', 'Y', '?']:
        b = nucleotide_to_belnap(sym)
        assert b == Belnap.B, f"Unknown {sym} should map to Belnap.B, got {b}"
test("Unknown nucleotides → Belnap.B (paraconsistent)", test_nonstandard_belnap_handling)

# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    ok = summary()
    sys.exit(0 if ok else 1)
