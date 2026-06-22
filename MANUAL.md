# RED-HOT REBIS — Manual Page

**Author:** Lando$\otimes\odot$perator  
**Version:** 2.1.0 (IMASM+CLINK Edition)  
**Date:** 2026-06-11  
**Section:** 1 (General Commands)

---

## NAME

**red-hot\_rebis** — an engine for algebraic, exact, deterministic, and paraconsistent bio $\otimes$ organic chemistries. Unified CLI entry point for the five-pillar Great Work: Serpent's Rod, CH$_3$MPILER, Pipeline, Gene Imscriber, and CLINK Chain — all grounded in the 12-primitive Imscribing Grammar and verified by Frobenius closure ($\mu\circ\delta=\mathrm{id}$).

---

## SYNOPSIS

```
python3 rebis.py COMMAND [OPTIONS]
```

**Primary subcommands:**

| Command | Purpose |
|---------|---------|
| `rebis.py status` | Structural status of all packages |
| `rebis.py verify` | Frobenius closure verification |
| `rebis.py run TARGET` | Execute a runnable target |
| `rebis.py clink ACTION` | CLINK chain operations |
| `rebis.py pipeline ACTION` | Pipeline operations |
| `rebis.py materials ACTION` | Materials forge commands |
| `rebis.py imas ACTION` | IMASM arrangement analysis |
| `rebis.py scripts ACTION` | Standalone script runner |
| `rebis.py help` | Full help |

---

## DESCRIPTION

The Red-Hot Rebis is the Grammar's engine for deterministic, algebraic, exact bio and organic chemistries. It integrates five structural pillars into a single coherent architecture grounded in the 12-primitive Imscribing Grammar and verified by Frobenius closure.

**Foundation:** $ZFC_\text{fe}$ — Frobenius-exact ZFC ($\text{O}_{\infty}$ with $\text{{\igfont 𐑦}}$ self-written, $\text{{\igfont 𐑹}}$ Frobenius-special, $\text{{\igfont 𐑫}}$ eternal chirality), distinct from the weaker $ZFC_t$ ($\text{O}_{2}^{\dagger}$).

**Structural type:** $$\langle\text{{\igfont 𐑦}};\ \text{{\igfont 𐑸}};\ \text{{\igfont 𐑾}};\ \text{{\igfont 𐑹}};\ \text{{\igfont 𐑐}};\ \text{{\igfont 𐑧}};\ \text{{\igfont 𐑲}};\ \text{{\igfont 𐑵}};\ \odot;\ \text{{\igfont 𐑫}};\ \text{{\igfont 𐑳}};\ \text{{\igfont 𐑟}}\rangle$$ — $\text{O}_{\infty}$

---

## ARCHITECTURE

```
red-hot_rebis/
  rebis.py                  # Unified CLI entry point (30 KB)
  setup.py                  # Package setup
  shared/                   # Shared primitives and catalog
    primitives.py           # 12-primitive definitions, weights, ordinals
    IG_catalog.json         # Catalog of imscribed systems
  serpentrod/               # Pillar I: Serpent's Rod — Platonic Proteins
  ch3mpiler/                # Pillar II: CH3MPILER — Platonic Disconnections
  pipeline/                 # Pillar III: Auto-Imscription + Frobenius
  gene_imscriber/           # Pillar IV: Frobenius-Guided Gene Editing
  clink/                    # Pillar V: CLINK Chain — Subatomic to Organism
  imas/                     # IMASM arrangement analysis
  imasm_iterator/           # IMASM token arrangement space iterator
  materials/                # Sophick forge, metamaterials, Ouroboric alloys
  biology/                  # Biology simulations, telomere models
  therapeutics/             # Chemotherapeutics, neurotrophics, antidotes
  rhr_p4rky/                # Paraconsistent kernel (28 modules)
  scripts/                  # Standalone analysis and pipeline scripts
  popular_protein/          # Protein structure validation (9 comparison tools)
  data/                     # Shared data (FASTA, results, MSA)
  pdb/                      # PDB structure files (1L2Y, 1UBQ, 1VII, 1ZDD)
  genetics_animations/      # SVG genetics visualizations
  images/                   # Project images
  docs/                     # Documentation

## COMMANDS — Complete Reference

### `rebis.py status`

Report the structural status of all discovered packages. Lists each package with file count, total size, and Frobenius verification status. Also checks shared assets (`primitives.py`, `IG_catalog.json`).

```
$ python3 rebis.py status
RED-HOT REBIS v2.1 — IMASM+CLINK EDITION

Package               Files       Size  Root file
  ✅ serpentrod            5     2,437  __init__.py
  ✅ ch3mpiler             6    10,231  __init__.py
  ✅ pipeline              7     2,896  __init__.py
  ✅ gene_imscriber       11    31,852  __init__.py
  ✅ clink                 8    16,443  __init__.py
  ...
```

### `rebis.py verify`

Verify Frobenius closure across the shared layer and CLINK chain. Validates:
- Primitive definitions (weights, ordinals)
- Catalog integrity (entry count, format)
- Component imports (all 5 pillars + CLINK)
- CLINK Frobenius closure: `tensorProduct(s, s) == s` for all 9 layers

```
$ python3 rebis.py verify
✅ shared/primitives.py — 12 weights, 12 ordinal families
✅ shared/IG_catalog.json — 3297 entries
✅ serpentrod: OK
✅ ch3mpiler: OK
✅ pipeline: OK
✅ gene_imscriber: OK
✅ CLINK chain: 9/9 layers Frobenius-closed
```

### `rebis.py run TARGET [OPTIONS]`

Execute a runnable target. Available targets:

| Target | Description | Key Options |
|--------|-------------|-------------|
| `serpentrod` | Serpent's Rod protein folding | `--sequence SEQ` (AA sequence) |
| `ch3mpiler` | Retrosynthetic disconnection | `--smiles SMILES`, `--depth N` |
| `gene` | Gene Imscriber codon analysis | `--codons SEQ` (codon sequence) |
| `mito` | Mitochondrial gene pipeline | (processes all 13 mtDNA genes) |
| `antibody` | Antibody CDR designer | (viral epitope → CDR loops) |
| `psychedelic` | Compound intrinsics + coupling | `report` for full 109-universe access |
| `iupac` | Diaschizic IUPAC generator | (11 diaschizic compounds) |

### `rebis.py clink ACTION`

CLINK Chain operations — the 9-layer Frobenius-closed bridge from quark to organism.

| Action | Description |
|--------|-------------|
| `clink report` | Full integration report with all 9 layers |
| `clink list` | All 9 layers with tuples and tiers |
| `clink layer N` | Layer N details + bridges (N = 0..8) |
| `clink bridge COMPONENT N` | Promotion path from component to CLINK layer N |

### `rebis.py pipeline ACTION`

| Action | Description |
|--------|-------------|
| `pipeline actionable --organism TYPE` | Generate actionable organism designs (mammal, human) |

### `rebis.py materials ACTION`

| Action | Description |
|--------|-------------|
| `materials forge --all` | Run all material forges |
| `materials sophick --name NAME` | Sophick forge a named material |

### `rebis.py imas ACTION`

IMASM arrangement space analysis. Operates on the $12^8 = 429{,}981{,}696$ IMASM token arrangements, mapped into structural fingerprint classes.

| Action | Description |
|--------|-------------|
| `imas report` | IMASM space map summary report |
| `imas hunt --samples N` | Frobenius-closure hunting (N arrangement samples) |

### `rebis.py scripts ACTION`

Standalone script runner — dispatches to any script in `scripts/`.

| Action | Description |
|--------|-------------|
| `scripts list` | List all available scripts |
| `scripts run NAME` | Run a named script (e.g., `compute_promotions`, `omonad_bridge`) |

### `rebis.py help`

Display the full help text with all subcommands and examples.

---

## THE FIVE PILLARS

### Pillar I: Serpent's Rod — `serpentrod/`

**What it produces:** Platonic Proteins — the structural imscription of a folded protein: its 12-primitive tuple, ouroboricity tier, and the full set of promoted primitives that distinguish the folded state from the unfolded sequence.

```
RNA sequence → [serpentrod] → ⟨structural type, tier, Frobenius certificate⟩
```

**Key files (5 modules, 2,437 lines):**
- `protein_v5.py` — V5 protein enhancement engine (743 lines, primary)
- `protein_v4.py` — V4 protein enhancement (475 lines)
- `stratified_predictor.py` — Stratified prediction model (876 lines)
- `manuscript.md` — Complete theory (437 lines)
- `report.md` — Processing report (343 lines)

**Canonical platonic protein type:** $\langle\text{{\igfont 𐑦}};\ \text{{\igfont 𐑥}};\ \text{{\igfont 𐑾}};\ \text{{\igfont 𐑬}};\ \text{{\igfont 𐑞}};\ \text{{\igfont 𐑧}};\ \text{{\igfont 𐑲}};\ \text{{\igfont 𐑠}};\ \odot;\ \text{{\igfont 𐑒}};\ \text{{\igfont 𐑳}};\ \text{{\igfont 𐑭}}\rangle$ — $\text{O}_2$

**6-Promotion Fold Path:** $\text{{\igfont 𐑼}}\!\to\!\text{{\igfont 𐑦}}$, $\text{{\igfont 𐑡}}\!\to\!\text{{\igfont 𐑥}}$, $\text{{\igfont 𐑑}}\!\to\!\text{{\igfont 𐑾}}$, $\text{{\igfont 𐑿}}\!\to\!\text{{\igfont 𐑬}}$, $\text{{\igfont 𐑤}}\!\to\!\text{{\igfont 𐑧}}$, $\text{{\igfont 𐑢}}\!\to\!\odot$ — verified Frobenius-closed.

### Pillar II: CH$_3$MPILER — `ch3mpiler/`

**What it produces:** Platonic Disconnections — retrosynthetic cuts derived from first principles. No named reactions, no reaction databases. Every disconnection is computed from the structural distance between the product's 12-primitive type and the meet of its constituent functional group types.

```
Target molecule → [ch3mpiler] → ranked disconnections with δ scores
```

**Key files (6 modules, 10,231 lines):**
- `compiler.py` — Main retrosynthetic compiler (883 lines)
- `gen_v2.py` — V2 generator
- `reaction_deriver.py` — Reaction derivation from FG meets
- `docs/` — Full documentation
- `ob3ect/ch3mpiler_ob3ect.py` — Self-verifying ob3ect vessel
- `CAS_cache.json` — Chemical Abstracts Service cache

**Bond formation model:** $\text{product} = \text{join}(\text{tensor}(\text{FG}_1, \text{FG}_2), \text{bond})$

### Pillar III: Pipeline — `pipeline/`

The combined auto-imscription + Frobenius verification pipeline. Assigns any described system a 12-primitive type and verifies $\mu\circ\delta=\mathrm{id}$.

**Key files (7 modules, 2,896 lines):**
- `auto_imscriber.py` — Auto-classify system descriptions (91 lines)
- `frob.py` — Frobenius phase computation (138 lines)
- `imscribe_agent.py` — Agent orchestration
- `imscribe_tool.py` — IG tool wrapper
- `ob3ect_imscriber.py` — Ob3ect-level imscriber (44 lines)
- `reaction_pipeline.py` — Reaction pipeline integration
- `lift_pipeline/` — Prose lift pipeline

### Pillar IV: Gene Imscriber — `gene_imscriber/`

The Frobenius-guided gene editing engine. The genetic code is re-imscribed as a stratified Frobenius algebra on $\text{B}_4^3$ codon space, with exact editing operations that respect the 8/8 split of codon boxes. The Chimera Theorem governs multi-primitive edits as tensorial (not additive) operations.

**Key files (11 modules, 31,852 lines):**
- `engine.py` — Core gene editing engine (2,198 lines)
- `tuples.py` — Genetic tuple definitions
- `genetics_ig_prelim.py` — Preliminary IG genetics analysis
- `genetics_ig_promotions.py` — Promotion pathways
- `genetics_qs.py` — Quantum simulation of codon space
- `ig_genetics_answer.py` — Project answer synthesis
- `scripts/` — GUIDE-seq analysis, base editor stratum, clinical safety

### Pillar V: CLINK Chain — `clink/`

The 9-layer Frobenius-closed bridge from subatomic particles to whole organisms — spanning 21 orders of magnitude ($10^{-15}$ m to $10^0$ m) in a single grammatical framework. All 9 layers verified $\mu\circ\delta=\mathrm{id}$. Formalized in Lean 4 (572 lines, 23 theorems, all `native_decide`-closed).

**Key files (8 modules, 16,443 lines):**
- `chain.py` — 9-layer chain with Frobenius closure checks (247 lines)
- `bridges.py` — Cross-component bridges (237 lines)
- `integration.py` — Unified integration reporting (205 lines)
- `pipeline_engine.py` — Pipeline orchestration
- `designers/` — Layer designers, tool forge, pipeline orchestrator
- `cephalopod_design/` — Cephalopod-human engineering designs
- `cat_allergy_design/` — DARPin Fel d1 neutralizer
- `shunt_portal_design/` — Shunt portal engineering
- `gr33ngroblin/` — Plastic eater BPA with Frobenius verification

---

## THE P4RA PARACONSISTENT KERNEL — `rhr_p4rky/`

A 28-module paraconsistent kernel migrated from `p4rakernel/`. Implements Belnap FOUR logic ($\{\text{T}, \text{B}, \text{F}, \text{N}\}$) as universal substrate, with explosion disabled by design.

| Module | Lines | Purpose |
|--------|-------|---------|
| `kernel.py` | — | Paraconsistent kernel core |
| `belnap.py` | — | 4-valued Belnap logic (T/B/F/N) |
| `machine.py` | — | Paraconsistent abstract state machine (ParaASM) |
| `genetic_code.py` | — | 64-codon Frobenius-verified genetic code |
| `genetics_b4.py` | — | $\text{B}_4$ lattice — 64 codons, 7-stage tuple verification |
| `genetic_tuples.py` | — | Tuple encodings for genes/codons/proteins |
| `gene_to_protein_pipeline.py` | — | Full gene-to-protein translation pipeline |
| `serpent_rod.py` / `_v2.py` | — | Serpent rod protein design |
| `antibody_designer.py` | — | Computational antibody design |
| `pdb_validator.py` | — | PDB structure validation |
| `hadron_belnap.py` | — | Hadronic Belnap-state analysis |
| `exotic_hadron_belnap.py` | — | Exotic hadron Belnap analysis |
| `quark_belnap.py` | — | Quark Belnap-state analysis |
| `orbital_belnap.py` | — | Orbital Belnap-state analysis |
| `frobenius_filtration.py` | — | Frobenius-verified filtration |
| `clu_power_law.py` | — | Clustering power-law analysis |
| `ch3mpiler_bridge.py` | — | CH$_3$MPILER $\leftrightarrow$ p4ra kernel bridge |
| `ch3mpiler_ob3ect_bridge.py` | — | CH$_3$MPILER $\leftrightarrow$ ob3ect bridge |
| `ch3mpiler_serpentrod_pipeline.py` | — | CH$_3$MPILER + SerpentRod integrated pipeline |

```
$ python3 -m rhr_p4rky.kernel
$ python3 rhr_p4rky/run_gene_pipeline.py --gene MT-ND5
$ python3 rhr_p4rky/run_serpent.py --fasta input.fasta
```

## THE CLINK CHAIN — Subatomic $\to$ Whole Organism

The CLINK chain is a 9-layer Frobenius-closed bridge, formalized in Lean 4 at `p4rakernel/p4ramill/Imscribing/CLINK.lean` (572 lines, 23 theorems, all `native_decide`-closed).

| # | Layer | Tier | Key Innovation |
|---|-------|------|----------------|
| 0 | **Frustrated Belnap5** (Quarks) | $\text{O}_0$ | SU(3) color confinement as frustrated 5-valued bilattice |
| 1 | **Electron Orbital** (Belnap4) | $\text{O}_0$ | 4-valued paraconsistent orbital occupancy |
| 2 | **Atom** (Nuclear + Electron) | $\text{O}_1$ | Complex-plane criticality from nuclear fusion resonance |
| 3 | **Molecule** (Chemical Bonds) | $\text{O}_2$ | $\odot$ criticality + $\text{{\igfont 𐑭}}$ integer winding |
| 4 | **Cell** (Living) | $\text{O}_2$ | Self-written state space + self-referential topology — minimal life |
| 5 | **Mitosis** (Cell Division) | $\text{O}_2$ | Frobenius-special parity for sister chromatid symmetry |
| 6 | **Meiosis** (Gametes) | $\text{O}_2$ | Adjoint pairing for homologous recombination |
| 7 | **Tissue / Organ** (Multi-cellular) | $\text{O}_2$ | Broadcast grammar for intercellular signaling |
| 8 | **Whole Organism** | $\text{O}_{\infty}$ | Eternal chirality + non-Abelian braiding — self-modeling life |

**Verified results:**
- Frobenius closure: $\checkmark$ All 9 layers ($\text{tensor}(s, s) = s$)
- Total structural distance: $\Sigma d = 7.18$ (10 primitive deltas)
- Total promotions: 36
- Lean 4 theorems: 23, all `native_decide`-closed
- Tier monotonicity: $\text{O}_0 \to \text{O}_0 \to \text{O}_1 \to \text{O}_2 \to \text{O}_2 \to \text{O}_2 \to \text{O}_2 \to \text{O}_2 \to \text{O}_{\infty}$

**Key insight — Mitosis is NOT $\text{O}_{\infty}$:** The spindle checkpoint operates at an exceptional point ($\text{{\igfont 𐑻}}$). The $\odot_3$ absorption rule $\text{tensor}(\odot, \text{{\igfont 𐑻}}) = \text{{\igfont 𐑻}}$ destroys the self-modeling gate. Only the whole organism achieves $\text{O}_{\infty}$.

---

## MATERIALS FORGE — `materials/`

| Tool | Purpose |
|------|---------|
| `ig_material_forge.py` | IG-guided material synthesis |
| `sophick_forge.py` | Sophick elemental forge |
| `frobenius_metamaterial.py` | Frobenius-closed metamaterial design |
| `critical_metamaterial.py` | Critical-point metamaterials |
| `ouroboric_alloy.py` | Ouroboric alloy simulation |
| `non_qubit_qc.py` | Non-qubit quantum computing prototype |
| `thermal_rectifier.py` | Thermal rectifier design |
| `gap_closure_module.py` | Gap closure module |
| `materials_sim.py` | Unified materials simulation |
| `frobenius_closure_complete.py` | Complete Frobenius closure verification |

---

## BIOLOGY & THERAPEUTICS — `biology/`, `therapeutics/`

| Module | Purpose |
|--------|---------|
| `biology_sim_frobenius_exact.py` | Frobenius-exact biological simulation |
| `ouroboric_telomere_expanded.py` | Ouroboric telomere simulation |
| `frobenius_chemotherapeutic.py` | Frobenius-verified chemotherapy design |
| `neurotrophic_factor.py` | Neurotrophic factor simulation |
| `ouroboric_pill_sim.py` | Ouroboric pill simulation |
| `quantum_biologic_prototype.py` | Quantum biologic prototype |
| `universal_antidote_library.py` | Universal antidote library |

## STANDALONE SCRIPTS — `scripts/`

14 standalone analysis and pipeline scripts (no package `__init__.py`):

| Script | Purpose |
|--------|---------|
| `run_antibody.py` | Antibody CDR designer — viral epitope $\to$ CDR loops |
| `run_serpent.py` | Serpent's Rod runner with import fix |
| `run_msa.py` | Multiple sequence alignment for SerpentRod conservation |
| `run_pdb_validation.py` | PDB validation pipeline — download, predict, compare |
| `mito_pipeline.py` | Mitochondrial genome pipeline (all 13 human mtDNA genes) |
| `msa_analysis.py` | MSA conservation analysis across ubiquitin orthologs |
| `analyze_validation.py` | Deep analysis of PDB validation results |
| `compute_promotions.py` | Primitive mismatch computation for Millennium Problems |
| `diaschizic_iupac.py` | IUPAC systematic name generator for diaschizics |
| `frob_design.py` | Frobenius design tool |
| `frobenius_exact_design.py` | Plastic-degrading enzyme design (complete 6/6 AND logic) |
| `gen_univ_map.py` | Universe-compound mapping document generator |
| `omonad_bridge.py` | Red-Hot Rebis $\leftrightarrow$ omonad\_OS integration bridge |
| `psychedelic_bridge.py` | p4rakernel $\times$ Novel Psychedelics integration |

```
$ python3 rebis.py scripts list
$ python3 rebis.py scripts run mito_pipeline
$ python3 rebis.py scripts run compute_promotions
```

---

## FROBENIUS VERIFICATION

Every tool in the Red-Hot Rebis satisfies $\mu \circ \delta = \mathrm{id}$ — verification is structural, not behavioral. The dual-pair architecture registers every tool as `(emit_fn, verify_fn)` where the verify function reconstructs the input from the output exactly.

**Crystallography as Frobenius gap:** At the crystallographic interface, $R_\text{free} \approx 0.2$ is not a numerical residual — it is the exact cost of inverting 8 primitives simultaneously in the act of measurement:

| Primitive | Rebis value | Crystallography | Lost |
|-----------|-------------|-----------------|------|
| Ř | $\text{{\igfont 𐑾}}$ bidirectional | $\text{{\igfont 𐑩}}$ supervenience | Molecule cannot respond |
| Ħ | $\text{{\igfont 𐑫}}$ eternal chirality | $\text{{\igfont 𐑓}}$ memoryless | Winding collapse $\text{{\igfont 𐑭}}\!\to\!\text{{\igfont 𐑷}}$ |
| Φ | $\text{{\igfont 𐑹}}$ Frobenius-special | $\text{{\igfont 𐑬}}$ partial/Z$_2$ | $\mu\circ\delta\neq\mathrm{id}$ |
| Ð | $\text{{\igfont 𐑦}}$ self-written | $\text{{\igfont 𐑼}}$ infinite-dim field | State space externally imposed |
| Þ | $\text{{\igfont 𐑶}}$ irreducible product | $\text{{\igfont 𐑡}}$ network branching | Holistic topology destroyed |
| ƒ | $\text{{\igfont 𐑐}}$ quantum | $\text{{\igfont 𐑱}}$ classical | No coherence |
| Ç | $\text{{\igfont 𐑧}}$ slow/near-eq | $\text{{\igfont 𐑪}}$ trapped-ordered | Molecule frozen, not equilibrating |
| Ω | $\text{{\igfont 𐑭}}$ integer winding | $\text{{\igfont 𐑷}}$ trivial | Radiation damage destroys protection |

Total structural distance: $d = 5.74$ — well into "structurally remote, different regime."

---

## ENVIRONMENT

**Python:** 3.12+  
**Dependencies:** numpy ($\ge$ 2.4.6), imasmic\_core ($\ge$ 0.5.69)  
**Virtual environment:** `.venv/` at repository root  
**Lean 4 (optional):** Mathlib v4.28.0 at `p4rakernel/p4ramill/` for formal verification  

```
cd /home/mrnob0dy666/imsgct/red-hot_rebis
source .venv/bin/activate   # if using venv
python3 rebis.py status     # verify everything is wired
```

## FILES

```
red-hot_rebis/
├── rebis.py                     # Unified CLI (30 KB, ~850 lines)
├── setup.py                     # Package setup
├── Makefile                     # Build/verify/test automation
├── README.md                    # Project overview (632 lines)
├── USER_GUIDE.md                # User guide (925 lines)
├── MANUAL.md                    # This manual
├── shared/
│   ├── primitives.py            # 12 primitives, 49 glyphs, weights, ordinals
│   └── IG_catalog.json          # 3,297 cataloged systems
├── serpentrod/                  # Pillar I — Platonic Proteins (5 .py, 2,437 loc)
├── ch3mpiler/                   # Pillar II — Platonic Disconnections (6 .py, 10,231 loc)
├── pipeline/                    # Pillar III — Auto-Imscription (7 .py, 2,896 loc)
├── gene_imscriber/              # Pillar IV — Gene Editing (11 .py, 31,852 loc)
├── clink/                       # Pillar V — CLINK Chain (8 .py, 16,443 loc)
├── imas/                        # IMASM arrangement analysis (5 .py)
├── imasm_iterator/              # IMASM space map iterator (6 .py, ~3,500 loc)
├── materials/                   # Sophick forge, metamaterials (15 .py)
├── biology/                     # Biology simulations, telomere models
├── therapeutics/                # Chemotherapeutics, neurotrophics
├── rhr_p4rky/                   # Paraconsistent kernel (28 .py)
├── scripts/                     # Standalone scripts (14 .py)
├── popular_protein/             # PDB structure validation (15 files)
├── serpentrod/                  # SerpentRod + stratified predictor (5 .py)
├── data/                        # Shared data (FASTA, results, MSA) (12 files)
├── pdb/                         # PDB structures (4 files: 1L2Y, 1UBQ, 1VII, 1ZDD)
├── genetics_animations/         # SVG visualizations (6 files)
├── images/                      # Project images
└── docs/                        # Documentation
```

**Totals:** 151 Python files, ~58,815 lines of code across 18 top-level packages + 14 standalone scripts.

---

## EXAMPLES

```bash
# ── Status and verification ──────────────────────────────────────────
python3 rebis.py status
python3 rebis.py verify

# ── Serpent's Rod: fold a protein ─────────────────────────────────────
python3 rebis.py run serpentrod --sequence "MALWMRLLPLLALLALWGPDPAAAFVNQ..."

# ── CH3MPILER: retrosynthetic analysis ────────────────────────────────
python3 rebis.py run ch3mpiler --smiles "CC(=O)Oc1ccccc1C(=O)O" --depth 3

# ── Gene Imscriber: analyze codon sequence ────────────────────────────
python3 rebis.py run gene --codons "AUGGCUGGGAUCCUGGUGGUGUUCCUGUGC"

# ── CLINK Chain: full integration report ──────────────────────────────
python3 rebis.py clink report
python3 rebis.py clink list
python3 rebis.py clink layer 4          # Cell layer details
python3 rebis.py clink bridge serpentrod 8  # Protein → organism path

# ── Actionable organism design ────────────────────────────────────────
python3 rebis.py pipeline actionable --organism human

# ── Materials forge ───────────────────────────────────────────────────
python3 rebis.py materials forge --all
python3 rebis.py materials sophick --name eagle_9_sophick

# ── IMASM analysis ────────────────────────────────────────────────────
python3 rebis.py imas report
python3 rebis.py imas hunt --samples 100000

# ── Standalone scripts ─────────────────────────────────────────────────
python3 rebis.py scripts list
python3 rebis.py run mito                   # mtDNA pipeline
python3 rebis.py run antibody               # Antibody CDR design
python3 rebis.py run psychedelic report     # 109-universe compound report

# ── Paraconsistent kernel ─────────────────────────────────────────────
python3 -m rhr_p4rky.kernel
python3 rhr_p4rky/run_gene_pipeline.py --gene MT-ND5
```

## SEE ALSO

- **README.md** — Project overview, structural type, the five vapours, crystallography gap
- **USER_GUIDE.md** — Full user guide with 12-primitive reference, all 35 runnable targets
- **SNS\_PRIME.md** — Shavian Notation Specification v0.6.0 — authoritative glyph reference
- **ig-docs/** — Imscribing Grammar documentation
- **p4rakernel/p4ramill/** — Lean 4 formal verification (165 modules, Mathlib v4.28.0)
- **imscribe.com/** — Web API and inquiry endpoint
- **clink/README\_CLINK.md** — Standalone CLINK chain documentation
- **clink/PIPELINE\_README.md** — CLINK pipeline architecture
- **serpentrod/manuscript.md** — Complete Serpent's Rod theory
- **ch3mpiler/docs/** — CH$_3$MPILER documentation
- **gene\_imscriber/README.md** — Gene Imscriber overview
- **popular\_protein/00\_MASTER\_MANIFEST.md** — Protein structure validation manifest
- **imasm\_iterator/IMASM\_SPACE\_MAP\_REPORT.md** — IMASM arrangement space report
- **Makefile** — Build, verify, test, clean automation

---

## AUTHOR

**Lando$\otimes\odot$perator**

The Red-Hot Rebis is the coagulation of the Imscribing Grammar's bio-organic engine — a tool whose purpose is to be *taken up into the loop*, not to stand outside it as a finished monument.

> *"The serpent winds, the rod stands, the vessel contains — $\mu \circ \delta = \mathrm{id}$."*  
> Not as a conclusion. As a *signature of process*.

---

## VERSION HISTORY

| Version | Date | Summary |
|---------|------|---------|
| 2.1.0 | 2026-06-10 | IMASM+CLINK Edition — CLINK chain integrated as Pillar V, IMASM iterator added, 151 .py files, 58,815 loc |
| 2.0.0 | 2026-05 | Four-pillar integration (Serpent's Rod + CH$_3$MPILER + Pipeline + Gene Imscriber) |
| 1.0.0 | 2026-04 | Initial integration — rebis.py CLI, shared primitives layer |

---

## COLOPHON

This page was woven on the wyrding loom — distinction by distinction, connection by connection — by order of $\text{{\igfont 𐑦}}$ and $\text{{\igfont 𐑸}}$, the twin sisters who co-originate every being that ever was or ever will be. The glyphs are Shavian (U+10450–U+1047F), set in Everson Mono. The crystal contains 17,280,000 structural types. The grammar is its own ground.

**Structural type of this manual:** $$\langle\text{{\igfont 𐑦}};\ \text{{\igfont 𐑶}};\ \text{{\igfont 𐑾}};\ \text{{\igfont 𐑹}};\ \text{{\igfont 𐑐}};\ \text{{\igfont 𐑧}};\ \text{{\igfont 𐑔}};\ \text{{\igfont 𐑠}};\ \odot;\ \text{{\igfont 𐑖}};\ \text{{\igfont 𐑙}};\ \text{{\igfont 𐑭}}\rangle$$
