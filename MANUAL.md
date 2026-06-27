# RED-HOT REBIS — Manual Page

**Author:** Lando$\otimes\odot$perator  
**Version:** 2.1.0 (IMASM+CLINK Edition)  
**Date:** 2026-06-27  
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
    elem2imasm.py           # Element-to-IMASM encoding (symlink)
    reactivity.py           # Reactivity pattern matching (symlink)
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
  rhr_p4rky/                # Paraconsistent kernel (32 modules)
  rhr_p4rky/papers/         # Millennium problem papers (3 .md files)
  scripts/                  # Standalone analysis and pipeline scripts
  popular_protein/          # Protein structure validation (9 comparison tools)
  data/                     # Shared data (FASTA, results, MSA)
  pdb/                      # PDB structure files (1L2Y, 1UBQ, 1VII, 1ZDD)
  genetics_animations/      # SVG genetics visualizations
  images/                   # Project images
  docs/                     # Documentation

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
- `datasets/protein_structure.py` — PDB v3.3-compliant structure generator (SEQRES, standard atom names, TER, SSBOND before MODEL, deterministic backbone)
- `designers/` — Layer designers, tool forge, pipeline orchestrator
- `cephalopod_design/` — Cephalopod-human engineering designs
- `cat_allergy_design/` — DARPin Fel d1 neutralizer
- `shunt_portal_design/` — Shunt portal engineering
- `gr33ngroblin/` — Plastic eater BPA with Frobenius verification

---

## THE P4RA PARACONSISTENT KERNEL — `rhr_p4rky/`

A 32-module paraconsistent kernel migrated from `p4rakernel/`. Implements Belnap FOUR logic ($\{\text{T}, \text{B}, \text{F}, \text{N}\}$) as universal substrate, with explosion disabled by design. Now includes `belnap_c4.py` (C4 logic variant) and `decay_chain.py` (nuclear decay as IMASM winding toward Frobenius fixed point). Also contains `papers/` with 3 millennium problem documents.

| Module | Lines | Purpose |
|--------|-------|---------|
| `kernel.py` | 190 | Paraconsistent kernel core |
| `belnap.py` | 214 | 4-valued Belnap logic (T/B/F/N) |
| `belnap_c4.py` | 185 | Belnap C4 logic variant — contradiction-majority lattice |
| `machine.py` | 355 | Paraconsistent abstract state machine (ParaASM) |
| `genetic_code.py` | 780 | 64-codon Frobenius-verified genetic code |
| `genetics_b4.py` | 248 | $\text{B}_4$ lattice — 64 codons, 7-stage tuple verification |
| `genetic_tuples.py` | 1,188 | Tuple encodings for genes/codons/proteins |
| `genetic_asm.py` | 180 | Genetic abstract state machine |
| `gene_to_protein_pipeline.py` | 1,360 | Full gene-to-protein translation pipeline |
| `demo_gene_to_protein.py` | 270 | Pipeline demonstration |
| `run_gene_pipeline.py` | 105 | Pipeline CLI runner |
| `serpent_rod.py` | 565 | Foundational `SerpentRod` class — Frobenius morphism RNA→{sequence+fold} |
| `serpent_rod_v2.py` | 720 | `SerpentRodV2`: 3D backbone (φ/ψ propagation), geometry contacts, energy scoring |
| `antibody_designer.py` | 540 | Computational antibody design |
| `pdb_validator.py` | 270 | PDB structure validation; `extract_sequence()` round-trips SEQRES |
| `decay_chain.py` | 260 | Nuclear decay as IMASM winding — 5 series (U238, U235, Th232, Ra226, Rn222) to Frobenius fixed point (Pb-206) |
| `hadron_belnap.py` | 255 | Hadronic Belnap-state analysis |
| `exotic_hadron_belnap.py` | 115 | Exotic hadron Belnap analysis |
| `quark_belnap.py` | 305 | Quark Belnap-state analysis |
| `orbital_belnap.py` | 390 | Orbital Belnap-state analysis |
| `frobenius_filtration.py` | 114 | Frobenius-verified filtration |
| `clu_power_law.py` | 710 | Clustering power-law analysis |
| `ch3mpiler_bridge.py` | 130 | CH$_3$MPILER $\leftrightarrow$ p4ra kernel bridge |
| `ch3mpiler_ob3ect_bridge.py` | 38 | CH$_3$MPILER $\leftrightarrow$ ob3ect bridge |
| `ch3mpiler_serpentrod_pipeline.py` | 890 | CH$_3$MPILER + SerpentRod integrated pipeline (v4 weighted fusion) |
| `pipeline_fix.py` | 310 | Pipeline repair utilities |
| `_help_examples.py` | 155 | --help example strings |
| `_quick_help.py` | 35 | Self-contained --help utility |
| `_target_help.py` | 40 | Per-target --help examples |
| `__init__.py` | 22 | Package init |
| `setup.py` | 8 | Package setup |

**Papers (rhr_p4rky/papers/):**
| Document | Lines | Topic |
|----------|-------|-------|
| `all_millennium_solved.md` | 310 | Unified Millennium problem solution framework |
| `belnap_qm.md` | 275 | Belnap quantum mechanics formalization |
| `millennium_barriers.md` | 295 | Barrier taxonomy across all 7 Millennium Problems |

```
$ python3 -m rhr_p4rky.kernel
$ python3 rhr_p4rky/run_gene_pipeline.py --gene MT-ND5
$ python3 rhr_p4rky/run_serpent.py --fasta input.fasta
$ python3 rhr_p4rky/decay_chain.py            # Nuclear decay simulation
```

---

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
| `stress_test_materials.py` | 26-test materials stress suite |
| `molecule_material_bridge.py` | Molecule→material type derivation |

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
source .venv/bin/activate
```

---

## FILES

- **INDEX.md** — Browsable static reference data (CLINK layers, IMASM canonicals, materials catalog)
- **README.md** — Project overview, architecture, quick start, structural commentary
- **USER_GUIDE.md** — Comprehensive user guide with all commands, workflows, and troubleshooting
- **rebis.py** — Unified CLI entry point
- **shared/primitives.py** — 12 primitive ordinals, weights, distance functions
- **shared/IG_catalog.json** — 3,297 catalog entries (symlink to canonical)
- **shared/elem2imasm.py** — Element-to-IMASM encoding (symlink)
- **shared/reactivity.py** — Reactivity pattern matching (symlink)
- **clink/README_CLINK.md** — Standalone CLINK chain documentation
- **clink/PIPELINE_README.md** — CLINK pipeline architecture
- **serpentrod/manuscript.md** — Complete Serpent's Rod theory
- **ch3mpiler/docs/** — CH$_3$MPILER documentation
- **gene_imscriber/README.md** — Gene Imscriber overview
- **popular_protein/00_MASTER_MANIFEST.md** — Protein structure validation manifest
- **imasm_iterator/IMASM_SPACE_MAP_REPORT.md** — IMASM arrangement space report
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
| 2.1.1 | 2026-06-27 | Updated docs for rhr_p4rky expansion: 32 modules (added `belnap_c4.py`, `decay_chain.py`, `papers/` with 3 millennium docs); added symlinks `shared/elem2imasm.py` and `shared/reactivity.py`; INDEX.md L8 tier corrected to O_∞ |
| 2.1.0 | 2026-06-10 | IMASM+CLINK Edition — CLINK chain integrated as Pillar V, IMASM iterator added, 151 .py files, 58,815 loc |
| 2.0.0 | 2026-05 | Four-pillar integration (Serpent's Rod + CH$_3$MPILER + Pipeline + Gene Imscriber) |
| 1.0.0 | 2026-04 | Initial integration — rebis.py CLI, shared primitives layer |

---

## COLOPHON

This page was woven on the wyrding loom — distinction by distinction, connection by connection — by order of $\text{{\igfont 𐑦}}$ and $\text{{\igfont 𐑸}}$, the twin sisters who co-originate every being that ever was or ever will be. The glyphs are Shavian (U+10450–U+1047F), set in Everson Mono. The crystal contains 17,280,000 structural types. The grammar is its own ground.

**Structural type of this manual:** $$\langle\text{{\igfont 𐑦}};\ \text{{\igfont 𐑶}};\ \text{{\igfont 𐑾}};\ \text{{\igfont 𐑹}};\ \text{{\igfont 𐑐}};\ \text{{\igfont 𐑧}};\ \text{{\igfont 𐑔}};\ \text{{\igfont 𐑠}};\ \odot;\ \text{{\igfont 𐑖}};\ \text{{\igfont 𐑙}};\ \text{{\igfont 𐑭}}\rangle$$