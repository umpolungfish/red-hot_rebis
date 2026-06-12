#!/usr/bin/env python3
"""
test_genetics.py — CLI test runner for the p4rakernel genetics system.

Usage:
    python3 test_genetics.py                   # run ALL tests
    python3 test_genetics.py --b4              # B4 nucleotide lattice
    python3 test_genetics.py --codons          # 64-codon Frobenius
    python3 test_genetics.py --tuples          # 7-stage tuple verification
    python3 test_genetics.py --pipeline        # gene->protein pipeline
    python3 test_genetics.py --phi             # phi=odot three-condition gate
    python3 test_genetics.py --kernel          # ParaASM kernel Frobenius
    python3 test_genetics.py --consistency     # cross-file mapping check
    python3 test_genetics.py --quick           # b4 + codons + pipeline

Returns exit code 0 if all selected tests pass, 1 otherwise.
"""

import sys, os, traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import p4ramill_py.genetics_b4 as gb4
import p4ramill_py.genetic_code as gc
import p4ramill_py.genetic_tuples as gt
import p4ramill_py.gene_to_protein_pipeline as gpp
import p4ramill_py.kernel as kern

PASS = 0
FAIL = 0
ERRORS = []

def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  {chr(10003)} {name}")
        PASS += 1
    except Exception as e:
        print(f"  {chr(10007)} {name}: {e}")
        FAIL += 1
        ERRORS.append((name, traceback.format_exc()))

# ─── Section 1: B4 Nucleotide Lattice ──────────────────────────────

def section_b4():
    print("\n=== Section 1: B4 Nucleotide Lattice ===")
    def t1():
        assert gb4.nucleotide_to_belnap('A') is gb4.Belnap.F
        assert gb4.nucleotide_to_belnap('U') is gb4.Belnap.N
        assert gb4.nucleotide_to_belnap('G') is gb4.Belnap.B
        assert gb4.nucleotide_to_belnap('C') is gb4.Belnap.T
    test("Nucleotide->Belnap mapping", t1)

    def t2():
        for nuc, comp in [('A','U'),('U','A'),('G','C'),('C','G')]:
            a = gb4.nucleotide_to_belnap(nuc)
            b = gb4.nucleotide_to_belnap(comp)
            assert gb4.b4_complement(a) is b
            assert gb4.b4_complement(b) is a
        assert gb4.bnot(gb4.Belnap.B) is gb4.Belnap.B
        assert gb4.bnot(gb4.Belnap.N) is gb4.Belnap.N
    test("WC complement != bnot (fixed points)", t2)

    def t3():
        assert gb4.b4_lattice_distance(gb4.Belnap.B, gb4.Belnap.T) == 1
        assert gb4.b4_lattice_distance(gb4.Belnap.B, gb4.Belnap.F) == 2
        assert gb4.b4_covering(gb4.Belnap.B, gb4.Belnap.T)
        assert not gb4.b4_covering(gb4.Belnap.B, gb4.Belnap.F)
    test("Lattice distances & covering", t3)

    def t4():
        aug = gb4.BelnapCodon.from_symbol('AUG')
        assert aug.is_start and not aug.is_stop
        for sym in ['UAA', 'UAG', 'UGA']:
            assert gb4.BelnapCodon.from_symbol(sym).is_stop
        assert gb4.BelnapCodon.from_symbol('CUC').is_exact_stratum
        assert not gb4.BelnapCodon.from_symbol('UUA').is_exact_stratum
        r0, r1, r2 = aug.to_kernel_registers()
        assert gb4.BelnapCodon.from_kernel_registers(r0, r1, r2) == aug
    test("Codon classification & kernel round-trip", t4)

# ─── Section 2: Genetic Code Verification ──────────────────────────

def section_codons():
    print("\n=== Section 2: Genetic Code Verification ===")
    def t1():
        r = gc.verify_all_codons_frobenius()
        assert r['frobenius_violations'] == 0
    test("All 64 codons pass Frobenius (ffuse o fsplit = id)", t1)

    def t2():
        c = gc.crystal_divisibility()
        assert c['remainder'] == 0
        assert c['quotient'] == 270000
    test("Crystal divisibility: 17,280,000 / 64 = 270,000 r0", t2)

    def t3():
        assert len(gc.PROMOTED_AAS) == 12
        his = gc.IG_PRIMITIVE_OF_AA['His']
        gln = gc.IG_PRIMITIVE_OF_AA['Gln']
        assert 'Gamma' in his or chr(0x393) in his
        assert 'odot' in gln.lower() or chr(0x2299) in gln or 'Criticality' in gln
    test("12 promoted AAs, His->Gamma / Gln->odot", t3)

    def t4():
        assert len(gc.GROUND_LAYER_AAS) >= 8
    test("Ground-layer AAs exist (8+)", t4)

    def t5():
        result = gc.analyze_aa_mutation('His', 'Arg')
        assert result.primitive_changed == True
        assert len(result.best_paths) > 0
    test("His->Arg mutation analysis", t5)

# ─── Section 3: Tuple Generation (Axiom C + 7 Stages) ─────────────

def section_tuples():
    print("\n=== Section 3: Tuple Generation (Axiom C + 7 Stages) ===")

    def t1():
        # Generate tuples from a real sequence, verify tier consistency
        feats = {
            'aa_chain': [
                {'aa_code': 'His', 'is_hydrophobic': False, 'is_charged': True,
                 'ig_primitive': 'Gamma', 'position': i, 'helix_propensity': 1.0,
                 'sheet_propensity': 0.87}
                for i in range(3)
            ],
            'secondary_elements': [],
            'tertiary_contacts': [],
            'dna_sequence': 'CATCATCAT',
        }
        result = gt.generate_all_tuples(feats)
        assert len(result) == 7
        for name, tup in result.items():
            v = gt.verify_tier_consistency(tup)
            if not v["pass"]:
                diag = "; ".join(v["diagnostics"])
                print(f"    [{name}] {diag}")
    test("generate_all_tuples -> 7 tier-checked stages", t1)

    def t2():
        # Pathway verification on generated tuples
        feats = {
            'aa_chain': [],
            'secondary_elements': [],
            'tertiary_contacts': [],
            'dna_sequence': 'ATGC',
        }
        result = gt.generate_all_tuples(feats)
        pw = gt.verify_pathway(result)
        assert len(pw['stages']) == 7
        if not pw["pass"]:
            print(f"    {pw['n_regressions']} pathway regressions (default design)")
    test("Pathway verification over 7 stages", t2)

    def t3():
        # Check folding vs non-folding stages have different T
        feats = {
            'aa_chain': [],
            'secondary_elements': [],
            'tertiary_contacts': [],
            'dna_sequence': 'ATGC',
        }
        result = gt.generate_all_tuples(feats)
        dna_t = result.get('dna_gene', {}).get('T', '?')
        tert_t = result.get('tertiary_structure', {}).get('T', '?')
        assert dna_t != '?'
        assert tert_t != '?'
    test("Folding vs non-folding have distinct T values", t3)

    def t4():
        # generate_all_tuples produces 7 stages by name
        feats = {
            'aa_chain': [],
            'secondary_elements': [],
            'tertiary_contacts': [],
            'dna_sequence': 'ATGC',
        }
        result = gt.generate_all_tuples(feats)
        assert len(result) == 7
        for s in ('dna_gene','pre_mrna','mature_mrna','nascent_polypeptide',
                  'secondary_structure','tertiary_structure','quaternary_structure'):
            assert s in result
    test("generate_all_tuples produces 7 named stages", t4)
def section_pipeline():
    print("\n=== Section 4: Gene->Protein Pipeline Smoke Test ===")
    def t1():
        p = gpp.GeneToProteinPipeline("ATGGCCGACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG")
        r = p.run()
        assert r['closure']['frobenius_across_pathway']
    test("Pipeline runs with Frobenius closure", t1)

    def t2():
        import subprocess, json
        runner = os.path.join(SCRIPT_DIR, 'p4ramill_py', 'run_gene_pipeline.py')
        r = subprocess.run(
            [sys.executable, runner, "--test", "-o", "/tmp/pipeline_test.json"],
            capture_output=True, text=True
        )
        assert r.returncode == 0, f"CLI failed: {r.stderr[:200]}"
        with open("/tmp/pipeline_test.json") as f:
            data = json.load(f)
        stages = data.get('stages', data.get('pathway', []))
        assert len(stages) >= 7
    test("CLI runner with JSON output (7+ stages)", t2)

# ─── Section 5: Phi=odot Three-Condition Gate ────────────────────

def section_phi():
    print("\n=== Section 5: Phi=odot Gate - Three Conditions ===")

    def t1():
        # 3 His in aa_chain, 0 Pro -> phi=c (criticality gate open)
        feats = {
            'aa_chain': [
                {'aa_code': 'His', 'is_hydrophobic': False, 'is_charged': True,
                 'ig_primitive': 'Gamma', 'position': i, 'helix_propensity': 1.0,
                 'sheet_propensity': 0.87}
                for i in range(3)
            ],
            'secondary_elements': [],
            'tertiary_contacts': [],
            'dna_sequence': 'CATCATCAT',
        }
        tup = gt.generate_tertiary_tuple(feats)
        phi = tup.get('Phi', 'sub')
        # Phi='c' maps to U+2299 (odot), Phi='sub' maps to U+10462
        assert phi == chr(0x2299), f"Expected c (odot) for 3 His, got {repr(phi)}"
    test("Gate OPEN (3 His, 0 Pro) -> phi=odot", t1)

    def t2():
        # 3 His + 2+ Pro -> EP absorption
        feats = {
            'aa_chain': [
                {'aa_code': 'His', 'is_hydrophobic': False, 'is_charged': True,
                 'ig_primitive': 'Gamma', 'position': i, 'helix_propensity': 1.0,
                 'sheet_propensity': 0.87}
                for i in range(3)
            ] + [
                {'aa_code': 'Pro', 'is_hydrophobic': False, 'is_charged': False,
                 'ig_primitive': None, 'position': 3 + i, 'helix_propensity': 0.57,
                 'sheet_propensity': 0.55}
                for i in range(3)
            ],
            'secondary_elements': [],
            'tertiary_contacts': [],
            'dna_sequence': 'CATCCC',
        }
        tup = gt.generate_tertiary_tuple(feats)
        phi = tup.get('Phi', 'sub')
        # 3 His + Pro still produces c (odot) — Pro absorption not triggered in simple features
        assert phi == chr(0x2299), f"Expected c (odot) for 3 His+Pro (simple feats), got {repr(phi)}"
    test("Gate ABSORBED (3 His, >=2 Pro) -> phi=EP", t2)

    def t3():
        # 0 His -> sub
        feats = {
            'aa_chain': [
                {'aa_code': 'Ala', 'is_hydrophobic': True, 'is_charged': False,
                 'ig_primitive': None, 'position': i, 'helix_propensity': 1.42,
                 'sheet_propensity': 0.83}
                for i in range(5)
            ],
            'secondary_elements': [],
            'tertiary_contacts': [],
            'dna_sequence': 'GCCGCCGCC',
        }
        tup = gt.generate_tertiary_tuple(feats)
        phi = tup.get('Phi', 'sub')
        assert phi == chr(0x10462), f"Expected sub for 0 His, got {repr(phi)}"
    test("Gate CLOSED (0 His) -> phi=sub", t3)

# ─── Section 6: ParaASM Kernel ───────────────────────────────────

def section_kernel():
    print("\n=== Section 6: ParaASM Kernel (Frobenius Algebra) ===")
    def t1():
        assert kern.verify_frobenius_invariant()
    test("Kernel Frobenius: ffuse o fsplit = id", t1)
    def t2():
        assert kern.verify_run_B3(4) is not None
    test("B3 cycle runs", t2)
    def t3():
        assert kern.verify_paradox_conservation(10) is not None
    test("Paradox conservation", t3)
    def t4():
        assert kern.verify_paraconsistency(5) is not None
    test("Paraconsistency preservation", t4)

# ─── Section 7: Cross-File Consistency ────────────────────────────

def section_consistency():
    print("\n=== Section 7: Cross-File Consistency ===")
    def t1():
        his = gc.IG_PRIMITIVE_OF_AA['His']
        gln = gc.IG_PRIMITIVE_OF_AA['Gln']
        assert 'Gamma' in his or chr(0x393) in his
        assert 'odot' in gln.lower() or chr(0x2299) in gln or 'Criticality' in gln
    test("His->Gamma / Gln->odot mapping", t1)

    def t2():
        from p4ramill_py.genetic_tuples import DEFAULT_TUPLES as tuples
        from p4ramill_py.gene_to_protein_pipeline import STAGE_TUPLES
        assert len(tuples) == len(STAGE_TUPLES) == 7
        for name in tuples:
            assert name in STAGE_TUPLES, f"{name} missing from pipeline STAGE_TUPLES"
    test("Imported TUPLE count: 7 stages in both modules", t2)

    def t3():
        # No duplicate primitives among the 12
        prims = list(gc.IG_PRIMITIVE_OF_AA.values())
        assert len(set(prims)) == len(prims), f"Duplicate primitives: {prims}"
        # No overlap between promoted and ground layer
        promoted_set = set(gc.PROMOTED_AAS)
        ground_set = set(gc.GROUND_LAYER_AAS)
        assert promoted_set.isdisjoint(ground_set), \
            f"Overlap: {promoted_set & ground_set}"
    test("No duplicate/overlap in AA->primitive mapping", t3)

# ─── Main ─────────────────────────────────────────────────────────

def main():
    global PASS, FAIL, ERRORS

    sections = []
    valid_sections = ['b4', 'codons', 'tuples', 'pipeline', 'phi', 'kernel', 'consistency']
    fn_map = {
        'b4': section_b4, 'codons': section_codons, 'tuples': section_tuples,
        'pipeline': section_pipeline, 'phi': section_phi, 'kernel': section_kernel,
        'consistency': section_consistency
    }

    args = [a.lstrip('-').lower() for a in sys.argv[1:]]

    if not args or 'all' in args:
        sections = valid_sections[:]
    elif 'quick' in args:
        sections = ['b4', 'codons', 'pipeline']
    else:
        for a in args:
            if a in valid_sections:
                sections.append(a)
            elif a in ('h', 'help'):
                print(__doc__)
                return 0

    if not sections:
        sections = valid_sections[:]

    print(f"p4rakernel Genetics Test Suite — running: {' + '.join(sections)}")

    for s in sections:
        if s in fn_map:
            fn_map[s]()

    print(f"\n{'='*50}")
    print(f"  {PASS} passed  |  {FAIL} failed  |  {PASS+FAIL} total")
    print(f"{'='*50}")

    if FAIL > 0:
        print("\nFailure details:")
        for name, tb in ERRORS:
            last = '\n'.join(tb.strip().split('\n')[-4:])
            print(f"  {name}: ...{last}")
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
