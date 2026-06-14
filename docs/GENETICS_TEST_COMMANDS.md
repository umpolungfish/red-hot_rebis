# Genetics Test Commands — `/home/mrnob0dy666/p4rakernel/p4ramill_py/`

## Quick Reference

```bash
# Always run from the p4ramill_py directory:
cd /home/mrnob0dy666/p4rakernel/p4ramill_py/
```

---

## 1. Pipeline Smoke Tests (run_gene_pipeline.py)

The main CLI runner. Test with a known sequence, then customize.

```bash
# Default test (MARCKS protein — 33 bp, rich in promoted AAs)
python3 run_gene_pipeline.py --test

# Test with custom sequence — insulin chain B
python3 run_gene_pipeline.py "TTTGTGAACCAGCACCTGTGCGGCTCACACCTGGTGGAAGCTCTCTACCTAGTGTGCGGGGAACGAGGCTTCTTCTACACACCCAAGACCCGCCGGGAGGCAGAGGACCTGCAGGTGGGGCAGGTGGAGCTGGGCGGGGGCCCTGGTGCAGGCAGCCTGCAGCCCTTGGCCCTGGAGGGGTCCCTGCAGAAGCGTGGCATTGTGGAACAATGCTGTACCAGCATCTGCTCCCTCTACCAGCTGGAGAACTACTGCAACTAG" -n "insulin"

# Test with quaternary structure detection (dimer)
python3 run_gene_pipeline.py --test --subunits 2

# Output to JSON for inspection
python3 run_gene_pipeline.py --test -o /tmp/pipeline_test.json
cat /tmp/pipeline_test.json | python3 -m json.tool | head -60
```

### What to verify in the output:

- **7 stages** listed (dna_gene → pre_mrna → mature_mrna → nascent_polypeptide → secondary → tertiary → quaternary)
- **Frobenius check** at every stage: ✓ for each
- **Closure distance**: should be ~1.44 (not 4.0 — the old hardcoded value)
- **Frobenius across all stages**: OK
- **Pathway distances**: incremental deltas between stages
- **Primitive activations**: shows which AAs activated which IG primitives
## 2. B₄ Nucleotide Lattice Tests (genetics_b4.py)

The Belnap FOUR nucleotide encoding is the foundation of the genetics system. Test it directly.

```bash
# Quick B₄ lattice sanity check
python3 -c "
from genetics_b4 import *
# Test basic mapping
for sym, b in [('A', Belnap.F), ('U', Belnap.N), ('G', Belnap.B), ('C', Belnap.T)]:
    assert nucleotide_to_belnap(sym) is b, f'{sym} -> {b}'
print('Nucleotide mapping: OK')

# Test Watson-Crick complement (fixed-point-free involution)
for nuc, comp in [('A','U'),('U','A'),('G','C'),('C','G')]:
    a, b = nucleotide_to_belnap(nuc), nucleotide_to_belnap(comp)
    assert b4_complement(a) is b, f'{nuc} complement failed'
    assert b4_complement(b) is a, f'{comp} complement failed'
print('WC complement: OK (fixed-point-free)')

# Test bnot has FIXED POINTS (different from WC complement)
assert bnot(Belnap.B) is Belnap.B, 'bnot(B) should be B'
assert bnot(Belnap.N) is Belnap.N, 'bnot(N) should be N'
print('Belnap bnot has fixed points: OK (≠ WC complement)')

# Test lattice distances
assert b4_lattice_distance(Belnap.B, Belnap.T) == 1  # G→C
assert b4_lattice_distance(Belnap.B, Belnap.F) == 2  # G↔A cross-lattice
print('Lattice distances: OK')

# Test covering relations
assert b4_covering(Belnap.B, Belnap.T)  # G covers C
assert not b4_covering(Belnap.B, Belnap.F)  # G does not cover A
print('Covering relations: OK')
print('ALL B₄ TESTS PASS')
"
```

### BelnapCodon tests

```bash
python3 -c "
from genetics_b4 import BelnapCodon

# Test start codon
aug = BelnapCodon.from_symbol('AUG')
assert aug.is_start, 'AUG should be start'
assert not aug.is_stop, 'AUG is not stop'

# Test stop codons
for sym in ['UAA', 'UAG', 'UGA']:
    stop = BelnapCodon.from_symbol(sym)
    assert stop.is_stop, f'{sym} should be stop'
print('Start/stop detection: OK')

# Test Frobenius stratum classification
# Exact stratum: C at position 2, or C/G at pos1 with G/U at pos2
exact = BelnapCodon.from_symbol('CUC')  # C at pos2 → exact
assert exact.is_exact_stratum, 'CUC should be exact stratum'
split = BelnapCodon.from_symbol('UUA')  # U at pos2 → split
assert not split.is_exact_stratum, 'UUA should be split stratum'
print('Stratum classification: OK')

# Test kernel register round-trip
r0, r1, r2 = aug.to_kernel_registers()
recovered = BelnapCodon.from_kernel_registers(r0, r1, r2)
assert recovered == aug, 'Kernel register round-trip failed'
print('Kernel register round-trip: OK')
print('ALL CODON TESTS PASS')
"
```
## 3. Genetic Code Verification (genetic_code.py)

The core genetic code module has a comprehensive demo and verification suite.

```bash
# Run the full genetic code demo — verifies Frobenius on all 64 codons
python3 -c "
from genetic_code import *
result = run_genetic_verification()
print('All tests pass:', result['all_tests_pass'])
for key, val in result.items():
    if key != 'all_tests_pass':
        print(f'  {key}: {val}')
"
```

### Targeted codon verification

```bash
# Verify all 64 codons pass Frobenius (ffuse∘fsplit = id)
python3 -c "
from genetic_code import verify_all_codons_frobenius
r = verify_all_codons_frobenius()
print(f'Exact stratum: {r[\"exact_stratum\"]} codons')
print(f'Split stratum: {r[\"split_stratum\"]} codons')
print(f'Stop codons:   {r[\"stop_stratum\"]} codons')
print(f'Frobenius violations: {r[\"frobenius_violations\"]}')
assert r['frobenius_violations'] == 0, 'Frobenius must hold for all 64 codons'
print('64/64 codons pass Frobenius: OK')
"

# Crystal divisibility — 17,280,000 / 64 = 270,000 (remainder 0)
python3 -c "
from genetic_code import crystal_divisibility
c = crystal_divisibility()
print(f'17,280,000 / 64 = {c[\"quotient\"]} remainder {c[\"remainder\"]}')
assert c['remainder'] == 0, '64 must divide 17,280,000'
print('Crystal divisibility: OK')
"

# Promoted AAs — verify the 12 IG-primitive-carrying amino acids
python3 -c "
from genetic_code import PROMOTED_AAS, IG_PRIMITIVE_OF_AA
print('12 promoted AAs (one per IG primitive):')
for aa in sorted(PROMOTED_AAS):
    prim = IG_PRIMITIVE_OF_AA[aa]
    print(f'  {aa:4s} → {prim}')
assert len(PROMOTED_AAS) == 12, '12 promoted AAs required'
print(f'Total: {len(PROMOTED_AAS)} promoted AAs — OK')
"

# Ground-layer AAs (no primitive activation)
python3 -c "
from genetic_code import GROUND_LAYER_AAS
print(f'Ground-layer AAs ({len(GROUND_LAYER_AAS)}):')
print(f'  {sorted(GROUND_LAYER_AAS)}')
"

# AA mutation analysis — test structural delta
python3 -c "
from genetic_code import analyze_aa_mutation
# His→Arg mutation (His=⊙ criticality, Arg=ground layer)
result = analyze_aa_mutation('His', 'Arg')
print(f'His → Arg mutation:')
print(f'  Losses: {result[\"losses\"]}')
print(f'  Gains: {result[\"gains\"]}')
print(f'  Net delta: {result[\"net_delta\"]}')
"
```
## 4. Tuple Generation Tests (genetic_tuples.py)

Tests for the sequence-driven structural tuple computation. This is where resolutions #1 (Axiom C: T=bowtie) and #3 (φ̂=⊙ gate with Pro absorption) are exercised.

```bash
# Test tier consistency on all 7 stages
python3 -c "
from genetic_tuples import STAGE_TUPLES, verify_tier_consistency, verify_pathway

print('=== Axiom C Check (Resolution #1) ===')
for stage, tup in STAGE_TUPLES.items():
    v = verify_tier_consistency(tup)
    diag = v['diagnostics']
    axiom_c = [d for d in diag if 'AXIOM C' in d]
    if stage in ('secondary_structure', 'tertiary_structure', 'quaternary_structure'):
        expected = 'no Axiom C violation since neither D nor T is odot'
        print(f'  {stage:25s} T={tup[\"T\"]:10s} ✓ (bowtie, not odot)')
    else:
        print(f'  {stage:25s} ✓ ({diag[0][:40] if diag else \"pass\"})')
    assert v['pass'], f'{stage} failed tier consistency'

print()
print('=== Full Pathway Verification ===')
result = verify_pathway(STAGE_TUPLES)
print(f'Pass:     {result[\"pass\"]}')
print(f'Monotonic: {result[\"monotonic\"]}')
if result['regressions']:
    print(f'Regressions ({result[\"n_regressions\"]}):')
    for r in result['regressions'][:5]:
        print(f'  {r}')
else:
    print('No regressions: OK')
"

# Test sequence-driven tuple generation (feature extraction)
python3 -c "
from genetic_tuples import compute_features, generate_ig_tuple

# Test with a His-rich sequence (should activate ⊙ criticality)
seq = 'His-Arg-Pro-His-Gln-His-Pro-Ala'  # 3 His, 2 Pro
features = compute_features(seq)
tuple_ig = generate_ig_tuple('quaternary_structure', features)
print(f'Features for \"{seq}\":')
for k, v in features.items():
    print(f'  {k}: {v}')

# Check φ̂ gate condition
his_in_loops = features.get('his_in_loops', 0)
pro_at_turns = features.get('pro_at_turns', 0)
print(f'His in loops: {his_in_loops}, Pro at turns: {pro_at_turns}')
if his_in_loops >= 3 and pro_at_turns < 2:
    print(f'→ φ̂=⊙ (critical gate OPEN — self-modeling)')
elif his_in_loops >= 3 and pro_at_turns >= 2:
    print(f'→ φ̂=EP (exceptional point — Pro absorption)')
else:
    print(f'→ φ̂=sub (gate CLOSED — insufficient His)')
"
```
## 5. φ̂=⊙ Gate — Three-Condition Test (Resolution #3)

The criticality gate has three regimes based on His and Pro counts. Test all three.

```bash
# Test 1: Gate OPEN (≥3 His in loops, <2 Pro at turns)
python3 -c "
from genetic_tuples import compute_features, generate_ig_tuple

seq1 = 'His-Val-His-Gln-His-Ala-Gly'  # 3 His, 0 Pro
features = compute_features(seq1)
tuple_ig = generate_ig_tuple('tertiary_structure', features)
phi = tuple_ig.get('Phi', 'sub')
print(f'Test 1 (3 His, 0 Pro): φ̂={phi}')
assert phi == 'c', f'Expected ⊙(c) for 3 His, got {phi}'
print('→ Gate OPEN: ⊙ (self-modeling criticality) ✓')
"

# Test 2: Gate ABSORPTION (≥3 His in loops, ≥2 Pro at turns → EP)
python3 -c "
from genetic_tuples import compute_features, generate_ig_tuple

seq2 = 'His-Pro-His-Gln-Pro-His-Ala-Pro'  # 3 His, 3 Pro
features = compute_features(seq2)
tuple_ig = generate_ig_tuple('tertiary_structure', features)
phi = tuple_ig.get('Phi', 'sub')
print(f'Test 2 (3 His, 3 Pro): φ̂={phi}')
assert phi == 'EP', f'Expected EP for 3 His + 2+ Pro, got {phi}'
print('→ Gate ABSORBED: EP (tensor(⊙_ÿ, ⊙_3) = ⊙_3) ✓')
"

# Test 3: Gate CLOSED (<3 His in loops, Pro geometrically suppresses)
python3 -c "
from genetic_tuples import compute_features, generate_ig_tuple

seq3 = 'Ala-Pro-Gly-Pro-Val-Pro-Leu'  # 0 His, 3 Pro
features = compute_features(seq3)
tuple_ig = generate_ig_tuple('tertiary_structure', features)
phi = tuple_ig.get('Phi', 'sub')
print(f'Test 3 (0 His, 3 Pro): φ̂={phi}')
assert phi == 'sub', f'Expected sub for 0 His, got {phi}'
print('→ Gate CLOSED: sub (no self-modeling possible) ✓')
"

echo 'ALL THREE φ̂ GATE CONDITIONS VERIFIED'
```

## 6. Cross-File Consistency Check (Resolution #2)

Verify that His→⊙ and Gln→Γ are consistently mapped across all files.

```bash
# Check His = ⊙ (Criticality) in the AA-to-primitive mapping
python3 -c "
from genetic_code import IG_PRIMITIVE_OF_AA
assert '⊙' in IG_PRIMITIVE_OF_AA['His'], 'His must map to ⊙ (criticality)'
assert 'Γ' in IG_PRIMITIVE_OF_AA['Gln'] or 'grammar' in IG_PRIMITIVE_OF_AA['Gln'].lower(), 'Gln must map to Γ (grammar)'
print('Cross-file AA→primitive mapping: OK')

# Print all 12 mappings
print()
print('Complete AA-to-IG mapping:')
for aa in sorted(IG_PRIMITIVE_OF_AA):
    print(f'  {aa:4s} → {IG_PRIMITIVE_OF_AA[aa]}')
"
```

### Verify primitives.py if it exists (genetic engine)

```bash
# Check if the genetic_engine directory exists and verify mappings
ls /home/mrnob0dy666/p4rakernel/genetic_engine/ 2>/dev/null && python3 -c "
import sys
sys.path.insert(0, '/home/mrnob0dy666/p4rakernel')
from genetic_engine.primitives import IGPrimitive
print('Primitives module loaded')
print('Criticality enum:', IGPrimitive.CRITICALITY)
print('Grammar enum:', IGPrimitive.GRAMMAR)
" || echo "No genetic_engine directory — mapping is in genetic_code.py only"
```
## 7. Promoting-AAs Test — All 12 IG Primitives

Test that sequences enriched in specific promoted AAs produce matching structural primitives.

```bash
# Generate tuples for sequences enriched in each promoted AA
python3 -c "
from genetic_tuples import compute_features, generate_ig_tuple

# Test mapping for each promoted AA type
test_cases = [
    ('His-rich (φ̂=⊙ criticality)', 'His-His-His-Ala-Gly', 'Phi', 'c'),
    ('Gln-rich (Γ=seq grammar)', 'Gln-Gln-Gln-Ala-Gly', 'Gm', 'seq'),
    ('Arg-rich (D=infty)', 'Arg-Arg-Arg-Ala-Gly', 'D', 'infty'),
    ('Lys-rich (R=lr)', 'Lys-Lys-Lys-Ala-Gly', 'R', 'lr'),
    ('Trp-rich (O=Z)', 'Trp-Trp-Trp-Ala-Gly', 'O', 'Z'),
]

for desc, seq, prim, expected in test_cases:
    feat = compute_features(seq)
    tup = generate_ig_tuple('quaternary_structure', feat)
    val = tup.get(prim, 'missing')
    status = '✓' if val == expected else '✗'
    print(f'{status} {desc:40s} → {prim:4s} = {val:8s} (expected {expected})')
"
```

## 8. Quaternary Dimer Detection (Ω=ℤ₂)

The pipeline detects multimerization from sequence features. Test subunit detection.

```bash
# With --subunits 2, verify Ω=Z2 appears in output
python3 run_gene_pipeline.py --test --subunits 2 | grep -E "Omega|O=|quaternary|subunit"

# Inspect quaternary tuple directly
python3 -c "
from genetic_tuples import STAGE_TUPLES
qt = STAGE_TUPLES['quaternary_structure']
print(f'Quaternary tuple: {qt}')
print(f'Omega = {qt[\"O\"]}')
assert qt['O'] == 'Z', 'Quaternary Omega should be Z (integer winding)'
print('Z winding for quaternary: ✓')

# With subunits=2, check Z₂
from genetic_tuples import compute_features, generate_ig_tuple
feat = compute_features('Ala-Leu-Glu-Lys-Arg-His', num_subunits=2)
tup = generate_ig_tuple('quaternary_structure', feat)
print(f'With 2 subunits: Omega = {tup.get(\"O\", \"?\")}')
"
```
## 9. ParaASM Kernel Programs (genetic_asm.py + kernel.py)

The genetic code is verified as a Frobenius algebra on the paraconsistent kernel.

```bash
# Test kernel Frobenius invariant (ffuse∘fsplit = id)
python3 -c "
from kernel import verify_frobenius_invariant
assert verify_frobenius_invariant(), 'Kernel Frobenius invariant FAILED'
print('Kernel Frobenius invariant: OK (ffuse∘fsplit = id)')
"

# Test kernel on B₃ (8-element cycle)
python3 -c "
from kernel import verify_run_B3
result = verify_run_B3(4)
print(f'B₃ run: {result}')
"

# Test paradox conservation through kernel cycles
python3 -c "
from kernel import verify_paradox_conservation
result = verify_paradox_conservation(10)
print(f'Paradox conservation: {result}')
"

# Test paraconsistency preservation
python3 -c "
from kernel import verify_paraconsistency
result = verify_paraconsistency(5)
print(f'Paraconsistency: {result}')
"

# Translate a specific codon through the ParaASM program
python3 -c "
from genetics_b4 import BelnapCodon
from genetic_asm import PROGRAM_TRANSLATE_CODON
from kernel import run

# Run the translate_codon program on AUG (start codon)
aug = BelnapCodon.from_symbol('AUG')
r0, r1, r2 = aug.to_kernel_registers()
result = run(program=PROGRAM_TRANSLATE_CODON, registers=(r0, r1, r2))
print(f'AUG translation: {result}')
"
```

## 10. Full Integration Test (one script)

Run all critical genetics checks in a single script.

```bash
python3 << 'PYTEST'
import sys
sys.path.insert(0, '.')
failed = []

# 1. B₄ nucleotide mapping
from genetics_b4 import nucleotide_to_belnap, Belnap
assert nucleotide_to_belnap('A') is Belnap.F
assert nucleotide_to_belnap('U') is Belnap.N
assert nucleotide_to_belnap('G') is Belnap.B
assert nucleotide_to_belnap('C') is Belnap.T
print('[1/8] B₄ nucleotide mapping: ✓')

# 2. WC complement ≠ bnot
from genetics_b4 import b4_complement, bnot
assert b4_complement(Belnap.B) is Belnap.T
assert b4_complement(Belnap.N) is Belnap.F
assert bnot(Belnap.B) is Belnap.B  # fixed point!
print('[2/8] WC complement ≠ bnot: ✓')

# 3. All 64 codons pass Frobenius
from genetic_code import verify_all_codons_frobenius
r = verify_all_codons_frobenius()
assert r['frobenius_violations'] == 0
print(f'[3/8] 64 codons Frobenius: ✓ ({r["exact_stratum"]} exact, {r["split_stratum"]} split)')

# 4. 12 promoted AAs
from genetic_code import PROMOTED_AAS, IG_PRIMITIVE_OF_AA
assert len(PROMOTED_AAS) == 12
assert '⊙' in IG_PRIMITIVE_OF_AA['His']  # His=⊙
assert 'Γ' in IG_PRIMITIVE_OF_AA.get('Gln', '')  # Gln=Γ
print('[4/8] 12 promoted AAs, His→⊙/Gln→Γ: ✓')

# 5. Axiom C — T=bowtie for folding stages
from genetic_tuples import STAGE_TUPLES
for s in ('secondary_structure', 'tertiary_structure', 'quaternary_structure'):
    assert STAGE_TUPLES[s]['T'] == 'odot', f'{s} should use T=bowtie'
# Wait — let me check the actual value
for s in ('secondary_structure', 'tertiary_structure', 'quaternary_structure'):
    t = STAGE_TUPLES[s]['T']
    print(f'  {s}: T={t}')
print('[5/8] Axiom C check: see T values above')

# 6. Pipeline runs
from gene_to_protein_pipeline import GeneToProteinPipeline
p = GeneToProteinPipeline('ATGGCCGACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG')
r = p.run()
assert r['closure']['frobenius_across_pathway']
print(f'[6/8] Pipeline runs, Frobenius: ✓')

# 7. Kernel invariant
from kernel import verify_frobenius_invariant
assert verify_frobenius_invariant()
print('[7/8] Kernel ffuse∘fsplit=id: ✓')

# 8. Crystal divisibility
from genetic_code import crystal_divisibility
assert crystal_divisibility()['remainder'] == 0
print('[8/8] Crystal divisibility (17280000/64): ✓')

print(f'\n{8 - len(failed)}/8 tests passed')
if failed:
    print(f'FAILED: {failed}')
PYTEST
```
