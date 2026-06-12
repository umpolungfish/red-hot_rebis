# Genetics CLI — Quick Reference

All commands run from `/home/mrnob0dy666/p4rakernel/`.

---

## Test Runner (Python)

```bash
# Run ALL genetics tests (7 sections, ~25 individual tests)
python3 test_genetics.py

# Run specific sections
python3 test_genetics.py --b4          # B₄ nucleotide lattice
python3 test_genetics.py --codons      # 64-codon Frobenius verification
python3 test_genetics.py --tuples      # 7-stage tuple generation + Axiom C
python3 test_genetics.py --pipeline    # gene→protein CLI smoke test
python3 test_genetics.py --phi         # φ̂=⊙ three-condition gate (OPEN/ABSORBED/CLOSED)
python3 test_genetics.py --kernel      # ParaASM kernel Frobenius invariant
python3 test_genetics.py --consistency # cross-file His→⊙ / Gln→Γ check

# Quick smoke (b4 + codons + pipeline only — ~10s)
python3 test_genetics.py --quick

# Help
python3 test_genetics.py --help
```

Examples:
```bash
cd /home/mrnob0dy666/p4rakernel

# Full suite
python3 test_genetics.py

# Just check the phi gate
python3 test_genetics.py --phi

# Smoke test before committing
python3 test_genetics.py --quick
```

## Makefile (even shorter)

```bash
# Run ALL genetics tests
make test-genetics

# Individual sections
make test-b4
make test-codons
make test-tuples
make test-pipeline
make test-phi
make test-kernel
make test-consistency
```

## Pipeline CLI (standalone)

```bash
# Default test — MARCKS protein (33bp, rich in promoted AAs)
python3 p4ramill_py/run_gene_pipeline.py --test

# Custom sequence — insulin chain B
python3 p4ramill_py/run_gene_pipeline.py "TTTGTGAACCAGCACCTGTGCGGCTCACACCTGGTGGAAGCTCTCTACCTAGTGTGCGGGGAACGAGGCTTCTTCTACACACCCAAGACCCGCCGGGAGGCAGAGGACCTGCAGGTGGGGCAGGTGGAGCTGGGCGGGGGCCCTGGTGCAGGCAGCCTGCAGCCCTTGGCCCTGGAGGGGTCCCTGCAGAAGCGTGGCATTGTGGAACAATGCTGTACCAGCATCTGCTCCCTCTACCAGCTGGAGAACTACTGCAACTAG" -n insulin

# Dimer detection
python3 p4ramill_py/run_gene_pipeline.py --test --subunits 2

# JSON output
python3 p4ramill_py/run_gene_pipeline.py --test -o /tmp/pipeline_test.json
```

## Single-line checks (inline)

```bash
# Quick B₄ sanity
python3 -c "from genetics_b4 import *; print('A→', nucleotide_to_belnap('A').name); print('G→', nucleotide_to_belnap('G').name); print('WC complement B→', b4_complement(Belnap.B).name); print('bnot B→', bnot(Belnap.B).name)"

# 64 codons count
python3 -c "from genetic_code import verify_all_codons_frobenius; r=verify_all_codons_frobenius(); print(f'Exact: {r[\"exact_stratum\"]}, Split: {r[\"split_stratum\"]}, Stops: {r[\"stop_stratum\"]}, Violations: {r[\"frobenius_violations\"]}')"

# Promoted AAs
python3 -c "from genetic_code import PROMOTED_AAS, IG_PRIMITIVE_OF_AA; [print(f'{aa:4s} → {IG_PRIMITIVE_OF_AA[aa]}') for aa in sorted(PROMOTED_AAS)]"

# Crystal divisibility
python3 -c "from genetic_code import crystal_divisibility; c=crystal_divisibility(); print(f'{c[\"dividend\"]}/{c[\"divisor\"]} = {c[\"quotient\"]} r{c[\"remainder\"]}')"

# Kernel Frobenius
python3 -c "from kernel import verify_frobenius_invariant; print('ffuse∘fsplit=id:', verify_frobenius_invariant())"
```

## Expected output

```
p4rakernel Genetics Test Suite — running: b4 + codons + tuples + pipeline + phi + kernel + consistency
...
  ✓ All 7 stages pass tier consistency
  ✓ 64/64 codons pass Frobenius
  ✓ Gate OPEN (3 His, 0 Pro) → φ̂=⊙
  ✓ Gate ABSORBED (3 His, ≥2 Pro) → φ̂=EP
  ✓ Gate CLOSED (0 His) → φ̂=sub
...
  25 passed  |  0 failed  |  25 total
```
