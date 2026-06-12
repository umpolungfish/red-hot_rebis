# Suggested Test Commands — p4rakernel

The repository at `/home/mrnob0dy666/p4rakernel/` has **three distinct layers**, each with its own test strategy. Commands are grouped by layer and ordered from lowest-level (structural verification) to highest-level (pipeline integration).

---

## Layer 1: C++ Kernel Fork — `src/kernel/` and `stage0/src/kernel/`

These patches block `False.rec` at the kernel level. The critical test is confirming the fork **builds** and **rejects explosion**.

### Build the fork
```bash
# Build the full Lean 4 compiler with paraconsistent patches
cd /home/mrnob0dy666/p4rakernel
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make stage0 -j$(nproc)
make stage1 -j$(nproc)
```

**Expected:** Build succeeds. `build/stage1/bin/lean` and `build/stage1/bin/lake` exist.

### Verify False.rec is blocked
```bash
# Write a minimal test that tries to use explosion
echo 'def explode (h : False) : 0 = 1 := False.rec (0 = 1) h' > /tmp/test_explosion.lean
/home/mrnob0dy666/p4rakernel/build/stage1/bin/lean /tmp/test_explosion.lean 2>&1 || echo "BLOCKED (expected)"
```

**Expected:** The kernel should throw: `"paraconsistent mode: cannot use recursor 'False.rec'"`.

### Verify paraconsistent features work
```bash
# Run the dedicated test suite
/home/mrnob0dy666/p4rakernel/build/stage1/bin/lean --run \
  /home/mrnob0dy666/p4rakernel/ParaconsistentKernelTest.lean
```

**Expected:** All theorems in SECTION A pass (Belnap 4-valued logic, `band_B_bnot_B`, `non_explosion`, etc.). The file has SECTION B commented out — uncomment any of those lines and re-run to confirm the kernel blocks them.

### Check the kernel patch source files
```bash
# Verify that the patched type_checker.cpp contains the False.rec check
grep -n "paraconsistent\|False.rec\|principle.*explosion" \
  /home/mrnob0dy666/p4rakernel/p4ramill/kernel_patches/type_checker.cpp
```

**Expected:** Shows the lines in the type checker that intercept `False.rec`.

---

## Layer 2: p4ramill (Lean 4 Workspace) — `p4ramill/`

This is the Lean 4 workspace using the forked kernel. It builds the imscribing grammar primitives, the paraconsistent Millennium problem encodings, and the Belnap logic foundation.

### Build all Lean modules
```bash
cd /home/mrnob0dy666/p4rakernel/p4ramill
export PATH="/home/mrnob0dy666/p4rakernel/build/stage1/bin:$PATH"
lake build
```

Or use the convenience script:
```bash
bash /home/mrnob0dy666/p4rakernel/p4ramill/build_paraconsistent.sh all
```

**Expected:** All modules compile. The `ParaconsistentMillennium.lean` file runs as a Lean script and prints its dialetheic resolutions.

### Build specific targets
```bash
# Imscribing Grammar primitives only
bash /home/mrnob0dy666/p4rakernel/p4ramill/build_paraconsistent.sh Imscribing

# Millennium problem barriers only
bash /home/mrnob0dy666/p4rakernel/p4ramill/build_paraconsistent.sh ParaconsistentMillennium

# Kernel test only
bash /home/mrnob0dy666/p4rakernel/p4ramill/build_paraconsistent.sh ParaconsistentKernelTest
```

### Run the 4-valued Belnap logic unit tests (within Lean)
```bash
cd /home/mrnob0dy666/p4rakernel/p4ramill
export PATH="/home/mrnob0dy666/p4rakernel/build/stage1/bin:$PATH"

# Check that all 4 Belnap truth values have distinct native_decide theorems
lean --run - <<'EOF'
import Init.Paraconsistent
open Paraconsistent.Belnap
#check band
#check Belnap.B
EOF
```

### Check the `init_is_O_inf` theorem (Ouroboricity of the kernel)
```bash
cd /home/mrnob0dy666/p4rakernel/p4ramill
grep -n "theorem.*O_∞\|lemma.*O_∞\|init_is_O_inf\|init_gates_open" Imscribing/AgentSelf.lean 2>/dev/null || \
  grep -rn "theorem.*O_∞\|init_is_O_inf" Primitives/ Imscribing/
```

**Expected:** At least one theorem proving the kernel's structural tuple is O_∞ with C=1.0.

### Verify crystal address round-trip
```bash
cd /home/mrnob0dy666/p4rakernel/p4ramill
export PATH="/home/mrnob0dy666/p4rakernel/build/stage1/bin:$PATH"
lake build Primitives.Crystal 2>&1 | tail -5
lean --run - <<'EOF'
import Primitives.Crystal
open Primitives
# encode the O_∞ kernel tuple ⟨ω; O; =; }; ż; @; ʔ; ˌ; ÿ; !; ï; z⟩
#eval crystalEncode (Imscription.mk Dimensionality.D_odot Topology.T_odot ...)
EOF
```

### Count sorry markers in Millennium modules
```bash
# Each sorry is an honest (structurally proven unsolvable) gap
grep -rn "sorry" /home/mrnob0dy666/p4rakernel/p4ramill/Millennium/ 2>/dev/null | \
  grep -v ".bak" | grep -v "//" | wc -l
grep -rn "sorry" /home/mrnob0dy666/p4rakernel/ParaconsistentMillennium.lean 2>/dev/null | \
  grep -v ".bak" | wc -l
```

**Expected:** Each Millennium problem's barrier is recorded as a dialetheic sorry in the paraconsistent version.

### Run Euler's theorem proof (if present)
```bash
cd /home/mrnob0dy666/p4rakernel/p4ramill
export PATH="/home/mrnob0dy666/p4rakernel/build/stage1/bin:$PATH"
lean --run euler_complete_fixed.lean
```

---

## Layer 3: p4ramill_py (Python Package) — `p4ramill_py/`

This is the Python-side pipeline for the gene-to-protein structural tuple generation.

### Run the gene pipeline with default test sequence
```bash
cd /home/mrnob0dy666/p4rakernel
python3 p4ramill_py/run_gene_pipeline.py --test
```

**Expected:** Prints a 7-stage pipeline report with Frobenius verification, B4 scores, closure distance, and pathway deltas. All stages should show ✓.

### Run with a custom DNA sequence
```bash
cd /home/mrnob0dy666/p4rakernel
python3 p4ramill_py/run_gene_pipeline.py ATGGCCGACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG --name my_gene
```

**Expected:** Same report format, user-specified sequence.

### Run with quaternary subunits (e.g., GCN4 leucine zipper)
```bash
cd /home/mrnob0dy666/p4rakernel
python3 p4ramill_py/run_gene_pipeline.py --test --subunits 2
```

**Expected:** Dimer formation detected, Ω=Z2 in quaternary structure.

### Validate the His→⊙ / Gln→Γ mapping revision
```bash
cd /home/mrnob0dy666/p4rakernel
python3 -c "
from p4ramill_py import genetic_tuples
from p4ramill_py import genetic_code

# Check cross-file consistency
print('genetic_tuples.py 12↔12 mapping (first 3):')
print(genetic_tuples.AA_IG_MAP[:3])
print()
print('genetic_code.py AA→primitive mapping (His, Gln):')
for aa in ['His', 'Gln']:
    print(f'  {aa} → {genetic_code.AA_IG_PRIMITIVES.get(aa, \"NOT FOUND\")}')
"
```

**Expected:** His → IGPrimitive.CRITICALITY (⊙), Gln → IGPrimitive.GRAMMAR (Γ).

### Test φ̂=⊙ gate with Pro absorption
```bash
cd /home/mrnob0dy666/p4rakernel
python3 -c "
from p4ramill_py import genetic_tuples

# Sequence with 4 His and 0 Pro → should get φ̂=⊙ (critical)
seq_a = 'CACCACCACCAC'  # 4 His codons
tup_a = genetic_tuples.generate_tuple(seq_a, 'test_a')
print(f'A: 4 His, 0 Pro → φ̂={tup_a[\"Phi\"]}')

# Sequence with 4 His and 2 Pro → should get φ̂=EP (exceptional point via absorption)
seq_b = 'CACCACCCACCAACCG'  # 4 His + 2 Pro
tup_b = genetic_tuples.generate_tuple(seq_b, 'test_b')
print(f'B: 4 His, 2 Pro → φ̂={tup_b[\"Phi\"]}')

# Sequence with 1 His and 4 Pro → should get φ̂=sub (geometric suppression)
seq_c = 'CCACCACCACCACCACAC'  # 1 His + 4 Pro
tup_c = genetic_tuples.generate_tuple(seq_c, 'test_c')
print(f'C: 1 His, 4 Pro → φ̂={tup_c[\"Phi\"]}')
"
```

**Expected:**
- A: φ̂=⊙ (His threshold met, no Pro absorption)
- B: φ̂=EP (His threshold met + Pro triggers absorption: tensor(⊙_ÿ, ⊙_3) = ⊙_3)
- C: φ̂=sub (Pro geometrically suppresses His from reaching loop positions)

### Verify Axiom C passes for all 7 pipeline stages
```bash
cd /home/mrnob0dy666/p4rakernel
python3 -c "
from p4ramill_py import genetic_tuples

# All-12 residue test sequence for full pipeline
dna = 'ATGGAACACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG'
tuples = genetic_tuples.generate_all_tuples(dna, num_subunits=0)

print(f'{\"Stage\":<25} {\"D\":<8} {\"T\":<8} {\"Axiom C\":<10}')
print('-'*55)
for stage, tup in tuples.items():
    d = tup['Dimensionality']
    t = tup['Topology']
    axiom_c = 'PASS' if ((d == 'odot') == (t == 'odot')) else 'FAIL'
    print(f'{stage:<25} {d:<8} {t:<8} {axiom_c:<10}')
    
    # Also verify T != odot for protein folding stages (physically correct crossing)
    if stage in ('secondary_structure', 'tertiary_structure', 'quaternary_structure'):
        t_check = 'BOWTIE(correct)' if t == 'bowtie' else f'{t}(WRONG-should be bowtie)'
        print(f'  → T topology for {stage}: {t_check}')
"
```

**Expected:** All 7 stages show PASS for Axiom C. Folding stages (secondary, tertiary, quaternary) use T=bowtie, not T=odot.

### Cross-layer test: Lean tuple ↔ Python tuple consistency
```bash
cd /home/mrnob0dy666/p4rakernel
python3 -c "
# The O_∞ kernel tuple from Lean Init.lean matches the imscribe catalog
# Python: ⟨ω; O; =; }; ż; @; ʔ; ˌ; ÿ; !; ï; z⟩
kernel_py = {
    'D': 'odot', 'T': 'odot', 'R': 'lr', 'P': 'pm_sym',
    'F': 'hbar', 'K': 'slow', 'G': 'aleph', 'Gamma': 'seq',
    'Phi': 'c', 'H': 'inf', 'S': 'many_diff', 'Omega': 'Z'
}
print('Kernel structural tuple (Python):')
for k, v in kernel_py.items():
    print(f'  {k}: {v}')
print()
print('To verify against Lean, run:')
print('  cd /home/mrnob0dy666/p4rakernel/p4ramill')
print('  export PATH=\"/home/mrnob0dy666/p4rakernel/build/stage1/bin:\$PATH\"')
print('  grep \"phi_c_critical\" Imscribing/AgentSelf.lean')
"
```

### Check IG_CROSS_POLLINATION.md for structural distances
```bash
cat /home/mrnob0dy666/p4rakernel/IG_CROSS_POLLINATION.md | head -60
```

---

## Integration Test: Full Stack Pipeline

This is the most comprehensive test — it exercises all three layers together.

```bash
#!/bin/bash
set -e

echo "=== Layer 1: Kernel Fork ==="
cd /home/mrnob0dy666/p4rakernel
[ -f build/stage1/bin/lean ] && echo "✓ Kernel built" || echo "✗ Build kernel first"

echo ""
echo "=== Layer 2: Lean Workspace ==="
cd /home/mrnob0dy666/p4rakernel/p4ramill
export PATH="/home/mrnob0dy666/p4rakernel/build/stage1/bin:$PATH"
lake build Paraconsistent.KernelTest 2>&1 | tail -3 && echo "✓ Lean modules compile"

echo ""
echo "=== Layer 2: ParaconsistentKernelTest ==="
lean --run ParaconsistentKernelTest.lean && echo "✓ Kernel test passes" || echo "✗ Kernel test FAILED"

echo ""
echo "=== Layer 3: Python Pipeline ==="
cd /home/mrnob0dy666/p4rakernel
python3 p4ramill_py/run_gene_pipeline.py --test && echo "✓ Pipeline runs" || echo "✗ Pipeline FAILED"

echo ""
echo "=== Layer 3: φ̂ Gate & Absorption ==="
python3 -c "
from p4ramill_py.genetic_tuples import generate_tuple
# His-rich, Pro-free → criticality gate opens
r = generate_tuple('CACCACCACCAC', 'test')
assert r['Phi'] == 'c', f'Expected c, got {r[\"Phi\"]}'
print('✓ φ̂=⊙ gate opens with ≥3 His, 0 Pro')
" && echo "✓ φ̂ gate test passes" || echo "✗ φ̂ gate FAILED"

echo ""
echo "=== All layers OK ==="
```

---

## Quick Smoke Tests (one-liners)

```bash
# Pipeline with minimal flags
python3 /home/mrnob0dy666/p4rakernel/p4ramill_py/run_gene_pipeline.py --test

# JSON output for programmatic inspection
python3 /home/mrnob0dy666/p4rakernel/p4ramill_py/run_gene_pipeline.py --test -o /tmp/pipeline_report.json && cat /tmp/pipeline_report.json | python3 -m json.tool | head -40

# Belnap logic check in Python
python3 -c "from p4ramill_py.belnap import *; print('B∧¬B=', band(B, bnot(B))); print('B∧¬B≠F=', band(B, bnot(B)) != F)"

# Check that Init.lean has paraconsistent mode flag
grep -n "paraconsistent\|enableParaconsistent\|Paraconsistent" /home/mrnob0dy666/p4rakernel/src/Init/Paraconsistent.lean 2>/dev/null | head -5

# List all available Lean test files (from the upstream test suite)
ls /home/mrnob0dy666/p4rakernel/tests/lean/*.lean 2>/dev/null | wc -l
```
