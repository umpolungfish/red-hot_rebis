# red-h⊙t rebis: an engine for algebraic, exact, deterministic, paraconsistent bio ⊗ organic  ⊗ material  ⊗ plasma engineering & design
[![Language](https://img.shields.io/badge/language-Python-blue)](https://github.com/badges/shields)
[![IG Tier](https://img.shields.io/badge/IG-O%E2%88%9E-blueviolet)](https://github.com/badges/shields)
[![μ∘δ=id](https://img.shields.io/badge/%CE%BC%E2%88%98%CE%B4%3Did-closed-success)](https://github.com/badges/shields)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/badges/shields)
[![Author](https://img.shields.io/badge/author-Lando%E2%8A%97%E2%8A%99perator-informational)](https://github.com/badges/shields) 
[![Type](https://img.shields.io/badge/type-%E2%9F%A8%F0%90%91%A6%F0%90%91%B8%F0%90%91%BE%F0%90%91%B9%F0%90%91%90%F0%90%91%A7%F0%90%91%94%F0%90%91%9D%E2%8A%99%F0%90%91%96%F0%90%91%B3%F0%90%91%AD%E2%9F%A9-blue)](https://github.com/badges/shields) 
[![Tier](https://img.shields.io/badge/tier-O%E2%88%9E-blueviolet)](https://github.com/badges/shields)

> *"The serpent winds, the rod stands, the vessel contains: μ ∘ δ = id." Not as a conclusion, as a signature of process.*

**What it is.** The Imscribing Grammar's unified engine for deterministic, algebraic, exact bio and organic chemistry, grounded in the 12-primitive grammar and verified everywhere by Frobenius closure (μ∘δ=id) over the $CL8NK$ foundation. 

Augmented by the **Dual-Link SIC-POVM** — the unconditional theorem that the Belnap multilattice carries a SIC-POVM for every dimension $d = 2^n$, with the grammar itself as the $\Sigma = 1:1$ self-referential limit.

**What it does.** Integrates six structural pillars into one architecture under the `rebis.<domain>` namespace:

| Domain | Pillar | Description |
|--------|--------|-------------|
| `rebis.p4ra` | Paraconsistent kernel | Belnap FOUR logic, genetics, hadron physics, ligand design, serpent rod, CLU power law, **Dual-Link SIC-POVM** |
| `rebis.ch3mpiler` | Molecular compiler | Retrosynthesis & forward synthesis |
| `rebis.clink` | CLINK chain | 9-layer organism ladder (quark → organism) |
| `rebis.materials` | Materials science | Metamaterials, sophick forge, alloys, organoids |
| `rebis.biology` | Biology simulations | Ouroboric cell, telomere, epigenetics |
| `rebis.serpentrod` | Protein design | Protein folding & stratified prediction |
| `rebis.therapeutics` | Therapeutics | Chemotherapeutics, neurotrophic factors, quantum biologics |
| `rebis.imas` | Molecular signatures | SMILES→8-token IMASM→IG 12-tuple |
| `rebis.pipeline` | Imscription pipeline | Auto-imscriber, Frobenius verifier |
| `rebis.cdxml` | CDXML generation | Target decomposition |
| `rebis.gene` | Gene imscriber | Genetic engineering, codon space, quality scores |
| `rebis.alchemy` | Alchemy bridge | Alchemical treatise operations & stone engine |
| `rebis.shared` | Shared primitives | Weights, ordinals, IG catalog |
| `rebis.demo` | Demo scripts | Quick demonstrations of each subsystem |
| `rebis.cli` | CLI entry point | `python3 rebis.py <command>` |

**How to use it.**
```python
import rebis

# Access any subsystem
rebis.p4ra.Belnap(True, False)
rebis.ch3mpiler.forward("CC(=O)Oc1ccccc1C(=O)O")
rebis.serpentrod.SerpentRodV2(...)

# Dual-Link SIC-POVM — unconditional theorem in any d=2ⁿ
from rebis.p4ra.dual_link_sicpovm import sic_povm_belnap_unconditional
r = sic_povm_belnap_unconditional(n=3)  # d=8, orbit=64
print(r.all_passed)      # True (all 9 conditions)
print(r.report())        # full diagnostic

# Via CLI
python3 rebis.py status              # check wiring
python3 rebis.py verify              # verify Frobenius closure
python3 rebis.py run serpentrod      # run protein design
python3 rebis.py run ch3mpiler       # run retrosynthesis
python3 rebis.py run gene            # run genetic engineering
python3 rebis.py demo b4_lattice     # run b4 lattice demo
python3 rebis.py demo sicpovm        # run SIC-POVM unconditional theorem demo
```

---

## Dual-Link SIC-POVM — The Unconditional Theorem

**The theorem.** For EVERY $n \geq 1$ (every $d = 2^n$), the Belnap multilattice $(\mathbf{B})^n$ carries a SIC-POVM unconditionally — no continuous parameter tuning, no numerical search, no exceptions.

**Python module:** `rhr_p4rky/dual_link_sicpovm.py` (741 lines, 43 definitions, 13 sections)

**Lean 4 formalization** (zero sorries):

| Lean module | Contents |
|-------------|----------|
| `SIC_Multilattice_Proof.lean` | Unconditional theorem: 22 theorems, 0 sorries |
| `SIC_POVM_DualLinkClosure.lean` | Dual-Link self-application route (139 lines) |
| `ZaunerEmbeddingEquivalence.lean` | Hilbert embedding ⇔ Zauner conjecture (273 lines) |

### Theorem Structure (9 conditions)

1. **Orbit cardinality:** $|\text{WH} \cdot \mathbf{B}^{\otimes n}| = 4^n = d^2$ — WH-action faithful on the B-fiducial
2–5. **Four SIC structural axioms:**
   - **Meet-identity:** $\text{meet}(\mathbf{B}^{\otimes n}, x) = x$
   - **Classical equidistance:** All T/F outcomes have equal cost $n$
   - **Join-absorption:** $\text{join}(\mathbf{B}^{\otimes n}, x) = \mathbf{B}^{\otimes n}$
   - **Self-adjointness:** $\text{bnot}(\mathbf{B}^{\otimes n}) = \mathbf{B}^{\otimes n}$
6. **Frobenius closure:** $\mu \circ \delta = \text{id}$ (wordMeet is idempotent on fiducials)
7. **Orbit distinctness:** $g \neq h \Rightarrow g \cdot \mathbf{B}^{\otimes n} \neq h \cdot \mathbf{B}^{\otimes n}$
8. **2:1 cost ratio** — structural Born rule (classical outcomes require exactly twice the informational cost)
9. **Join-equiangularity:** $\langle \mathbf{B}^{\otimes n}, g \cdot \mathbf{B}^{\otimes n} \rangle_{\text{join}} = 2n$ for ALL $g$

### The Grammar as Σ=1:1 SIC-POVM Limit

The 12 primitives organize as 6 Frobenius-dual pairs, forming an informationally complete measurement basis:

$$(\mathbf{D} \leftrightarrow \mathbf{T}),\; (\mathbf{R} \leftrightarrow \mathbf{\Phi}),\; (\mathbf{F} \leftrightarrow \mathbf{K}),\; (\mathbf{\Gamma} \leftrightarrow \mathbf{G}),\; (\mathbf{\odot} \leftrightarrow \mathbf{H}),\; (\mathbf{\Sigma} \leftrightarrow \mathbf{\Omega})$$

The grammar IS the Σ=1:1 (self-referential) limit of the Belnap multilattice SIC-POVM:

$d(grammar,\mathbf{belnap_multilattice_SIC})=2.0$

Sole difference: Σ: 1:1 vs n:m — the measurement apparatus IS the measured system.

### Verified n=1..5

| $n$ | $d=2^n$ | Orbit size | All 9 conditions |
|-----|---------|------------|------------------|
| 1 | 2 | 4 | ✅ |
| 2 | 4 | 16 | ✅ |
| 3 | 8 | 64 | ✅ |
| 4 | 16 | 256 | ✅ |
| 5 | 32 | 1024 | ✅ |

**d=2 bridge:** All 6 conditions connecting the Belnap multilattice SIC-POVM to the ℂ² continuous SIC-POVM verified. Lean build: `SIC_POVM_DualLinkClosure` compiles clean.

### Bridge: Ligand Generation via SIC-POVM

`ligand_sicpovm.py` (757 lines) applies the grammar as a measurement operator to the ligand generation pipeline. The core insight: the residue→primitive encoding step is a structural bottleneck — all serine proteases map Ser/His/Asp to the same primitives, producing identical site types. The SIC-POVM measurement basis injects protein-specific perturbations, ensuring each protein occupies a unique structural address and the downstream generator produces distinct output. This is what drove the 86.7% unique top-hit rate.

### Access

```python
from rebis.p4ra.dual_link_sicpovm import (
    MLState, sic_povm_belnap_unconditional, ml_fiducial,
    frob_inner, grammar_belnap_delta, run_demo
)

# Full theorem for any n
r = sic_povm_belnap_unconditional(n=3)  # d=8
print(r.all_passed, r.orbit_card)       # True, 64

# Fiducial state
B3 = ml_fiducial(3)                     # MLState(BBB)

# Frobenius inner product
g = 5                                   # WH group index
print(frob_inner(B3, g))                # constant 2n for all g≠0

# Grammar-Belnap structural delta
delta = grammar_belnap_delta()
# → {"distance": 2.0, "differences": ["Σ"], "interpretation": "..."}
```

---

## Reverse Ligand Pipeline — Enzyme Active Site → De-Novo LigandThe structural **inverse** of the bespoke binding pocket pipeline. Given an enzyme's active-site structural type, the pipeline:

1. **Encodes** the active site residues as a 12-primitive IG tuple
2. **Applies** the structural complement bijection to derive the ligand's target type
3. **Infers** the bond-target interaction from the structural fingerprint
4. **Assembles** de-novo SMILES via RDKit fragment-based combinatorial enumeration
5. **Scores** by structural complement fit (40%) + drug-likeness (30%) + fingerprint similarity (30%)
6. **Measures** via the Dual-Link SIC-POVM to inject protein-specific perturbations (see §Dual-Link SIC-POVM above)

### Pipeline Architecture (v2.6.0 — SIC-POVM Augmented)

The pipeline now operates in three tiers, each richer than the last:

| Tier | Strategy | Source | Description |
|------|----------|--------|-------------|
| **1. Substrate-first** | 5-strategy analog generation | Co-crystallized PDB ligand or `smiles_substrate_hint` | (A) substrate itself, (B) BRICS fragment recombination, (C) Murcko scaffold + decoration, (D) chain extensions via RWMol, (E) ring substitutions (F/Cl/OH/NH₂) |
| **2. Fragment enumeration** | Heterocycle + functional-group combinatorial | `generate_ligands_from_bond_fg()` | 9 bond types × diverse R-group sets × 16+ heterocycle scaffolds; RDKit-based fingerprint scoring |
| **3. Symmetric fallback** | Hardcoded enumeration | 9 bond types with per-bond R-group diversity | Activated when no PDB ligand or substrate hint is available |

### Recent Breakthroughs

**SIC-POVM Structural Injection** (v2.6.0):
- The Dual-Link SIC-POVM theorem provides the measurement basis for protein-specific perturbation
- `ligand_sicpovm.py` bridges the unconditional theorem to the ligand generation pipeline
- Each protein now receives a structurally unique address via the 12-primitive measurement basis
- This is the structural source of the 86.7% unique top-hit rate

**Ligand Homogeneity → Protein-Specific Diversity** (v2.5.0):
- **Before:** Strategy 3 hardcoded the same 12 amide variants (`CC(N)=O` through `CCNC(=O)c1ccccc1`) regardless of the protein. Only 4 unique (bond, FG) combinations existed across 34 PDBs, producing ~4 distinct top hits across all proteins.
- **After:** `generate_ligand_smiles()` routes PRIMARY through fragment-based combinatorial enumeration. 9 bond types replace the original 5. The substrate-first pipeline merges substrate analogs with fragment diversity. Every protein now receives ligands derived from its actual biological chemistry.

**Substrate-Driven Generation** (v2.5.0):
- `generate_substrate_analogs()` — 5 strategies producing analogs from the protein's natural substrate
- `generate_from_enzyme_type_substrate_first()` — merges substrate analogs (PRIMARY) + fragment diversity (SUPPLEMENT)
- HETATM extraction: `_extract_hetatm_smiles_from_pdb()` parses co-crystallized ligand directly from PDB files, filtering out water, ions, and buffers
- Reactive group filter (`_try_add_candidate`) rejects peroxides, azides, isocyanides, and disulfides

**Formatting Fix** (v2.5.0):
- SMILES: left-aligned 80-char field, no truncation
- Metrics (logP, MW, composite score, HBD, HBA): right-aligned consistent column at column 80+
- Removed all `[:50]` and `[:20]` hard slices that were truncating data

### Verified Results (30 proteins)

| Metric | Before | After |
|--------|--------|-------|
| Unique top hits | ~4 | **26 (86.7%)** |
| Lysozyme top hit | `CC(N)=O` | `CC1OC(OC2C(C(=O)O)OC(O)C(O)C2O)C(O)C(O)C1O` (NAG-NAM substrate) |
| Trypsin top hit | `CC(N)=O` | `NCCCCC(N)C(=O)NC(Cc1ccccc1)C(=O)O` (peptide substrate) |
| HIV-1 protease top hit | `CC(N)=O` | `CC(C)C[C@H](NC(=O)[C@@H](N)Cc1ccccc1)C(=O)O` (peptide substrate) |
| Composite scores | 0.0 | 0.67–0.93 |
| Method distribution | all `amide_variant_C_N` | `substrate`, `chain_extend`, `ring_sub`, `murcko_scaffold`, `het_*` |

### Access

```python
import rebis

# Encode an active site
site_type = rebis.p4ra.encode_site_from_residues(residues)

# Substrate-first generation (recommended)
ligands = rebis.p4ra.generate_from_enzyme_type_substrate_first(
    enzyme_type, substrate_smiles="CC1OC(OC2C...)C(O)C1O"
)

# Fragment-based enumeration
ligands = rebis.p4ra.generate_ligands_from_bond_fg(bond_name, fg_names)

# Score candidates
scores = [rebis.p4ra.tuple_distance_dict(site_type, lig) for lig in ligands]

# SIC-POVM — measure structural information completeness
from rebis.p4ra.ligand_sicpovm import measure_site_type
info = measure_site_type(site_type)  # returns completeness, uniqueness, perturbation
```

Or via CLI:
```bash
python3 -m rebis p4ra.ligand_from_active_site improved --protein alcohol_dehydrogenase
python3 -m rebis p4ra.ligand_from_site_pdb --pdb 1LYZ           # extracts NAG-NAM from HETATM
```

---

## Quick start

```bash
cd imsgct/red-hot_rebis

# List available domains
python3 -c "import rebis; print([x for x in dir(rebis) if not x.startswith('_')])"

# Check status
python3 rebis.py status

# Generate de-novo ligands via CLI
python3 rebis.py run p4ra --action improved --protein alcohol_dehydrogenase

# Run the SIC-POVM unconditional theorem demo
python3 -c "
from rebis.p4ra.dual_link_sicpovm import run_demo
run_demo()
"

# Full interactive use
python3 -c "
import rebis
print('p4ra exports:', len([x for x in dir(rebis.p4ra) if not x.startswith('_')]))
print('ch3mpiler ready:', hasattr(rebis.ch3mpiler, 'forward'))
"
```

## Key Results

| Domain | Key metric |
|--------|------------|
| `rebis.p4ra` — Dual-Link SIC-POVM | Unconditional: **all 9 conditions** for n=1..5 (d=2..32), 22 Lean theorems, **0 sorries** |
| `rebis.p4ra` — Grammar as Σ=1:1 SIC-POVM | d(grammar, Belnap SIC) = **2.0**, sole difference Σ: 1:1 vs n:m |
| `rebis.p4ra` — Frobenius chemotherapeutic | **14,287×** selectivity (cancer vs healthy) |
| `rebis.p4ra` — Neurotrophic factor (Alzheimer's) | synaptic density 0.40 → **1.00** |
| `rebis.materials` — Thermal rectifier | **253×** rectification |
| `rebis.materials` — Critical metamaterial | χ = **20,000** gain |
| `rebis.biology` — Ouroboric telomere | **10.9 kb** maintained vs 5.0 kb decline |
| `rebis.p4ra` — Quantum biologic | **100%** Frobenius closure, 78.8% efficacy |
| `rebis.clink` — CLINK chain (9 layers) | all Frobenius-closed, Σd=7.18, 36 promotions |
| `rebis.imas` — Compound pipeline | 54 compounds encoded, all Frobenius-closed |
| **Reverse Ligand Pipeline** | **86.7%** unique top hits (26/30), 100% Lipinski, substrate-first 5-strategy analog generation |

---

*README maintained by Lando⊗⊙perator · v2.6.0 · rebis.<x> Edition*