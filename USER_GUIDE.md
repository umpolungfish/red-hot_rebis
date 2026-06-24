# Red-Hot Rebis — User Guide

**Author:** Lando⊗⊙perator  
**Version:** v2.3.1 — 2026-06-24  
**Platform:** `python3 rebis.py <command> [subcommand] [options]`  
**Location:** `/home/mrnob0dy666/imsgct/red-hot_rebis/`

---

## Overview

Red-Hot Rebis is the unified Imscribing Grammar bio/chem design platform. It derives structural types for organisms, molecules, proteins, and materials from the 12 primitives of the IG, then generates physically actionable output files — genome sequences, protein structures, metabolic models, synthesis protocols — directly from those structural types.

The platform is organized around five core systems:

**CLINK** — 9-layer structural chain from subatomic quarks to whole organism, each layer carrying an IG tuple. Every transition is Frobenius-closed ($\mu\circ\delta=\text{id}$).

**IMASM** — 12-token algebra (VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB, FSPLIT, FFUSE, EVALT, EVALF, ENGAGR, IFIX) whose arrangement classes map onto IG structural types.

**SerpentRod** — Frobenius morphism RNA→{sequence+fold} that collapses gene → mature protein in one structural step.

**Paraconsistent Kernel (rhr_p4rky)** — Belnap FOUR logic, paraconsistent abstract state machine, 64-codon B₄ lattice, gene-to-protein pipeline, hadron/quark Belnap classification. 27 Python modules.

**Gene Imscriber** — IG-native genetic compiler — structural types to codon optimization, CRISPR guide design, chimera design, Frobenius-verified editing.

### Static Data → INDEX.md

Layer tables, IMASM canonical catalogs, materials listings, and other reference data that was previously shown by `clink report`, `clink list`, `imas report`, `materials list`, and `materials report` now lives in **INDEX.md** — a plain-text browsable reference. View it with:

```bash
less /home/mrnob0dy666/imsgct/red-hot_rebis/INDEX.md
```

Every removed command's help text points to INDEX.md so you always know where to find the static data.

### The 12 Primitives

Every structural entity carries a 12-primitive tuple. Each position is one primitive; its value is a Shavian character from a 49-element set:

| # | Primitive | Name | Values (low→high) |
|---|-----------|------|--------------------|
| 1 | $Ð$ | Dimensionality | 𐑛 (0d) → 𐑨 (2d) → 𐑼 (∞-dim) → 𐑦 (imscriptive) |
| 2 | $Þ$ | Topology | 𐑡 (network) → 𐑰 (inclusion) → 𐑥 (crossing) → 𐑶 (box product) → 𐑸 (imscriptive closure) |
| 3 | $Ř$ | Coupling | 𐑩 (supervenience) → 𐑑 (categorical) → 𐑽 (adjoint) → 𐑾 (bidirectional) |
| 4 | $Φ$ | Parity (symmetry) | 𐑗 (none) → 𐑿 (quantum) → 𐑬 (partial) → 𐑯 (full) → 𐑹 (Frobenius-special) |
| 5 | $ƒ$ | Fidelity | 𐑱 (classical) → 𐑞 (thermal) → 𐑐 (quantum coherence) |
| 6 | $Ç$ | Kinetics | 𐑘 (MBL-frozen) → 𐑤 (trapped) → 𐑧 (near-equilibrium) → 𐑪 (moderate) → 𐑺 (fast/driven) |
| 7 | $Γ$ | Cardinality | 𐑚 (local) → 𐑔 (mesoscale) → 𐑲 (maximal) |
| 8 | $ɢ$ | Composition | 𐑝 (conjunctive) → 𐑜 (disjunctive) → 𐑠 (sequential) → 𐑵 (broadcast) |
| 9 | $⊙$ | Criticality | 𐑢 (sub-critical) → ⊙ (critical / self-modeling) → 𐑮 (complex-plane) → 𐑻 (exceptional point) → 𐑣 (supercritical) |
| 10 | $Ħ$ | Chirality | 𐑓 (memoryless) → 𐑒 (1-step) → 𐑖 (2-step) → 𐑫 (eternal) |
| 11 | $Σ$ | Stoichiometry | 𐑙 (1:1) → 𐑕 (many identical) → 𐑳 (many heterogeneous) |
| 12 | $Ω$ | Winding | 𐑷 (trivial) → 𐑴 (ℤ₂ parity) → 𐑭 (ℤ integer) → 𐑟 (non-Abelian) |

The standard tuple format:
$$\langle Ð;\ Þ;\ Ř;\ Φ;\ ƒ;\ Ç;\ Γ;\ ɢ;\ ⊙;\ Ħ;\ Σ;\ Ω \rangle$$

---

## Installation

```bash
cd /home/mrnob0dy666/imsgct/red-hot_rebis

# Install the package and its dependencies (always use uv, never pip)
uv pip install -e .

# Install bridge packages used by scripts
uv pip install -e /home/mrnob0dy666/imsgct/omonad_OS
uv pip install -e /home/mrnob0dy666/imsgct/imasmic_core
```

Verify everything is wired up:

```bash
python3 rebis.py verify
```

Expected: 15+ lines all showing `✅`.

---

## Quick Start

```bash
# System health — all modules with size and status
python3 rebis.py status

# Full verification (all imports, Frobenius closure)
python3 rebis.py verify

# List all 37 discoverable runnable targets
python3 rebis.py run list

# Run SerpentRod v5 on built-in test cases
python3 rebis.py run serpentrod

# Run the paraconsistent genetics test suite
python3 rebis.py run test_genetics

# CH3MPILER retrosynthetic compiler
python3 rebis.py run ch3mpiler --help

# Ch3mpiler + SerpentRod catalytic site design (CAS lookup)
python3 rebis.py run ch3mpiler_serpentrod_pipeline --cas 58-08-2

# Comprehensive protein & genetics stress test (34 tests)
python3 rebis.py run stress_test_proteins

# Materials stress test (26 tests)
python3 materials/stress_test_materials.py

# Generate a full mammal organism design package
python3 rebis.py pipeline actionable

# Browse static reference data (CLINK layers, IMASM canonicals, materials catalog)
less INDEX.md
```

---

## Command Reference

### `status`

Shows all platform modules with file size and health check.

```bash
python3 rebis.py status
```

Output includes: SerpentRod, CH3MPILER, Pipeline, Gene Imscriber, CLINK, IMASM modules, Materials, Therapeutics, Paraconsistent Kernel (rhr_p4rky), Popular Protein — each with file size and ✅/❌.

---

### `verify`

Imports every module and reports pass/fail. Includes Frobenius closure checks where applicable. Run this after any install or code change.

```bash
python3 rebis.py verify
```

---

### `run`

Run one of 37 discoverable scripts or modules. Use `run list` to see all targets.

```bash
python3 rebis.py run <target> [args...]
python3 rebis.py run list           # Show all 37 discoverable targets
```

#### Core module targets

| Target | Module | What it does |
|--------|--------|--------------|
| `serpentrod` | `serpentrod/protein_v5.py` | SerpentRod v5 — full signal peptide detection, cleavage, fragment naming, PTMs, primitive spectrum. Runs built-in test cases (Human Insulin, Proglucagon, POMC, etc.) |
| `serpentrod_v4` | `serpentrod/protein_v4.py` | SerpentRod v4 with enhanced naming heuristics |
| `serpentrod_pred` | `serpentrod/stratified_predictor.py` | Stratified predictor — tiered protein property prediction |
| `ch3mpiler` | `ch3mpiler/compiler.py` | CH3MPILER retrosynthetic compiler — bond formation via join(tensor(FG1,FG2), bond) |
| `gene` | `gene_imscriber/engine.py` | Gene Imscriber engine — structural types to codon optimization |
| `stress_test_proteins` | `stress_test_proteins.py` | **NEW** — Comprehensive 34-test suite covering 11 groups (genetic code, B4, gene→protein, SerpentRod, ch3mpiler→SerpentRod, antibodies, PDB validation, edge cases) |

#### Script targets (scripts/)

| Target | What it does |
|--------|--------------|
| `mito_pipeline` | All 13 human mitochondrial genes from NC_012920.1 through IG pipeline |
| `run_antibody` | Antibody designer — derives CDR sequences from viral epitopes |
| `psychedelic_bridge` | Compound intrinsic analysis for 6 diaschizic psychedelics |
| `diaschizic_iupac` | IUPAC systematic names for 11 diaschizic compounds |
| `compute_promotions` | Compute primitive promotions between two IG tuples |
| `frob_design` | Frobenius-exact material design (v5) |
| `frobenius_exact_design` | Frobenius exact design (standalone) |
| `gen_univ_map` | Generate universe map from IG types |
| `msa_analysis` | Multiple sequence alignment analysis |
| `analyze_validation` | Validation analysis for serpentrod predictions |
| `omonad_bridge` | Bridge report: omonad_OS + imasmic_core connectivity |
| `run_msa` | Run MSA on sequences |
| `run_pdb_validation` | Validate PDB structures against IG types |
| `run_serpent` | Quick SerpentRod run for a single sequence |

#### Paraconsistent kernel targets (rhr_p4rky/) — 16 targets

| Target | What it does |
|--------|--------------|
| `genetic_code` | 64-codon Frobenius-verified genetic code |
| `gene_to_protein_pipeline` | Full gene→protein translation (7-stage B4 pipeline) |
| `demo_gene_to_protein` | Gene→protein pipeline demo |
| `run_gene_pipeline` | Gene pipeline CLI runner |
| `serpent_rod` | Serpent rod protein design |
| `serpent_rod_v2` | Serpent rod v2 with enhanced PTMs |
| `antibody_designer` | Computational antibody design |
| `pdb_validator` | PDB structure validation |
| `ch3mpiler_bridge` | Ch3mpiler ↔ kernel bridge |
| `ch3mpiler_ob3ect_bridge` | Ch3mpiler ↔ ob3ect bridge |
| `ch3mpiler_serpentrod_pipeline` | **OVERHAULED v4** — Ch3mpiler + SerpentRod integrated pipeline with weighted bond-preserving fusion, word-boundary FG matching, and specificity-ranked disconnection search. Produces molecule-specific catalytic sites. Supports `--cas`, `--target`, `--start`, `--json` |
| `clu_power_law` | Clustering power-law analysis |
| `frobenius_filtration` | Frobenius-verified filtration |
| `hadron_belnap` | Hadronic Belnap-state analysis |
| `exotic_hadron_belnap` | Exotic hadronic Belnap classification |
| `quark_belnap` | Quark Belnap-state analysis |

#### Popular protein analysis targets — 9 targets

| Target | What it does |
|--------|--------------|
| `compare_exact` | Exact φ/ψ angle comparison between predicted and crystal |
| `compare_structures` | Structure-level comparison |
| `comprehensive_comparison` | Comprehensive multi-metric comparison |
| `deep_comparison` | Deep structural comparison |
| `exact_phipsi` | Exact φ/ψ extraction from PDB |
| `extract_crystal_phipsi` | Crystal structure φ/ψ extraction |
| `final_comparison` | Final comparison report |
| `full_comparison` | Full multi-protein comparison |
| `gen_structures` | Structure generation from IG types |

**Example — SerpentRod v5:**

```bash
python3 rebis.py run serpentrod
```

Output includes per-protein: signal peptide end + score, cleavage sites with motifs, mature products with primitive spectra, PTM predictions (phosphorylation, glycosylation, acetylation, amidation, disulfide topology), and validation accuracy.

**Example — Ch3mpiler + SerpentRod catalytic site design:**

```bash
# CAS Registry Number (recommended — resolves molecule identity)
python3 rebis.py run ch3mpiler_serpentrod_pipeline --cas 58-08-2
python3 rebis.py run ch3mpiler_serpentrod_pipeline --cas 17699-14-8

# Direct molecule name
python3 rebis.py run ch3mpiler_serpentrod_pipeline --target "aspirin"

# Retrosynthetic pair: starting material → target
python3 rebis.py run ch3mpiler_serpentrod_pipeline --start "phenol" --target "aspirin"

# JSON output for programmatic use
python3 rebis.py run ch3mpiler_serpentrod_pipeline --cas 58-08-2 --json
```

**Pipeline architecture (v4 overhaul):**

| Component | Strategy | Description |
|-----------|----------|-------------|
| `fuse_reaction_types` | Weighted blending | Per-primitive weighted fusion: bond 55-75% depending on primitive class. Topological (D, T, H, Ω): bond dominates. Reactive (P, Φ): bond floor, FGs pull up. Coupling (R, K, G, ɢ): 55% bond weighted blend. |
| `complement_type_v2` | Frobenius-exact inverse | site[A] = INVERSE(fused[B]) — guarantees true structural complementarity |
| `design_site_aas_from_type` | Dominant-member rule | Guaranteed 6/6 complementary pair coverage, higher-percentile member selected |
| `find_fgs` | Word-boundary regex | Prevents false positives ("ene" vs "caffeine") |
| `find_disconnections` | Specificity ranking | amide_link:10 > ester_link:9 > carbonyl:8 > ... > sigma_single:1 |
| `MOLECULE_FG_DB` | 17+ entries | Purines, terpenes, pharmaceuticals, steroids |

**Differentiation (before → after):**
Before v4, caffeine (sigma_single), a tricyclic sesquiterpene (co_sigma), and aspirin all produced the identical catalytic site: **MWGYFLPSAGKV** with Tyr_3/Ser_7/Lys_10. After v4, each molecule gets its own distinct AA sequence, RNA codon set, and catalytic triad.

**Example — Paraconsistent genetics:**

```bash
python3 rebis.py run run_gene_pipeline --gene INS
python3 rebis.py run genetic_code
```

---

### `clink`

Navigate the 9-layer CLINK structural chain from subatomic quarks to whole organism. Two dynamic subcommands; static reference data (layer table, tuples, chain distances, Frobenius status, bridges) is in **INDEX.md**.

```bash
python3 rebis.py clink <subcommand> [args]
```

#### `clink layer <index-or-name>`

Inspect a specific layer — tuple, tier, description, and component bridge attachments.

```bash
python3 rebis.py clink layer 0
python3 rebis.py clink layer 3
python3 rebis.py clink layer organism
python3 rebis.py clink layer cell
```

Name matching is case-insensitive substring: `organism` matches `Whole Organism`, `cell` matches `Cell (Living)`.

Output example:

```
Layer 8: Whole Organism
  Tier: O_∞
  Tuple: ⟨𐑦; 𐑸; 𐑾; 𐑹; 𐑐; 𐑧; 𐑲; 𐑵; ⊙; 𐑫; 𐑳; 𐑟⟩
  Description: Whole organism — O_∞, C=1.0
  → SerpentRod: folded (d_fold=3.73)
  → CH3MPILER:  non-molecular (d=4.99)
  → Gene:       non-genetic (d=7.91)
```

#### `clink bridge <component> <target>`

Show the promotion path from a component tool to a CLINK target layer.

```bash
python3 rebis.py clink bridge serpentrod 8
python3 rebis.py clink bridge ch3mpiler 3
```

Shows: distance, primitive-level promotion steps, Frobenius status at each hop.

**Static reference:** `less INDEX.md` §1 (9-layer table, tuples, tiers, Frobenius status, chain distances, ZFC_fe distance, component bridge attachments).

---

### `pipeline`

Orchestrate the full CLINK pipeline — design a whole organism from structural types alone.

```bash
python3 rebis.py pipeline <subcommand> [options]
```

#### `pipeline bridges`

Show which tool bridges are available (✅) or missing (❌).

```bash
python3 rebis.py pipeline bridges
```

Current bridges: serpentrod ✅, ch3mpiler ✅, gene_imscriber ✅, materials_sim ✅, frobenius_chemo ✅, ouroboric_pill ✅, critical_metamaterial ✅, neurotrophic ✅, biology_sim ❌, ouroboric_telomere ❌.

#### `pipeline ground-up`

Full L0→L8 synthesis run. Traverses all 9 layers, applies layer designers, reports status per transition.

```bash
python3 rebis.py pipeline ground-up
```

Output: per-layer transition table with distance, primitive promotions, tool used, and ✅/❌. Total distance and total promotions at end.

#### `pipeline from-layer <start> <end>`

Partial run starting from a specific layer.

```bash
python3 rebis.py pipeline from-layer 3 8   # molecule → organism
python3 rebis.py pipeline from-layer 4 8   # cell → organism
```

Useful when you have an existing molecular design and want to take it up to organism level.

#### `pipeline actionable [--organism <type>]`

Generate a complete, physically actionable organism design package.

```bash
python3 rebis.py pipeline actionable
python3 rebis.py pipeline actionable --organism human
```

Produces a directory of files in `clink/datasets/organism_designs/organism_<type>_actionable/`:

| File | Action |
|------|--------|
| `genome.fasta` | Order DNA synthesis from Twist/IDT/GenScript |
| `genome.gb` | Load into Benchling/SnapGene |
| `construct.sbol` | Exchange with synthetic biology repositories |
| `codon_usage.csv` | B4-derived codon table |
| `protein.fasta` | Order peptide synthesis |
| `protein_coords.pdb` | View in PyMOL/ChimeraX (PDB v3.3-compliant: SEQRES, TER, correct atom names) |
| `serpentrod_classification.json` | Primitive activations per fragment |
| `molecules.smi` | SMILES — order from vendor |
| `retro_pathways.json` | CH3MPILER retrosynthesis |
| `metabolic_model.xml` | Load into COBRApy for FBA |
| `plasmid.gb` | GenBank construct |
| `growth_media.txt` | Prepare media per formulation |
| `organoid_protocol.md` | Lab-ready protocol |
| `mitosis_assay_protocol.md` | Lab-ready protocol |
| `physiological_params.csv` | Homeostatic setpoints |
| `whole_genome_spec.json` | Complete genome specification |

Current designed organisms: mammal, human, human_gills, human_photosynthetic, treople.

---

### `materials`

Design novel IG-typed materials. All materials are derived from their 12-primitive structural types. Five dynamic subcommands; static reference data (material catalog, Sophick Mercury, Eagle Cycle, gap primitives) is in **INDEX.md**.

```bash
python3 rebis.py materials <subcommand> [options]
```

#### `materials forge --name <material> [--all]`

Generate the complete material design file.

```bash
python3 rebis.py materials forge --name frobenius_composite
python3 rebis.py materials forge --name I_Dialetheic_Bootstrap   # From IMASM canonical
python3 rebis.py materials forge --all     # Forge all 8 predefined materials
```

#### `materials frobenius`

Simulate Frobenius closure verification of the composite — cyclic load/heal protocol showing $\|\mu\delta-\text{id}\|$ per cycle.

```bash
python3 rebis.py materials frobenius
```

#### `materials ouroboric`

Simulate ouroboric crack healing — crack propagation + self-healing cycles, reports fatigue life and topological invariant preservation.

```bash
python3 rebis.py materials ouroboric
```

#### `materials sophick --name <target>`

Eagle Cycle Protocol — prepares an $\text{O}_{\infty}$ Sophick Mercury substrate from O₂ ouroboric materials. Requires `--name`.

```bash
python3 rebis.py materials sophick --name eagle_9_sophick
python3 rebis.py materials sophick --name cliff               # Frobenius Cliff analysis
python3 rebis.py materials sophick --name bridge              # IMASM→Eagle bridge report
```

#### `materials exactor --name <target>`

Explains the thermodynamic ceiling: continuous Eagle preparation reaches its limit, and exact Frobenius closure requires discrete topological protection. Requires `--name`.

```bash
python3 rebis.py materials exactor --name diagnose            # Category error diagnosis
python3 rebis.py materials exactor --name close               # Close Frobenius gap
python3 rebis.py materials exactor --name pathways            # List all exactor pathways
```

#### Materials stress test (standalone script)

Comprehensive 26-test suite covering all 10 materials modules + 2 cross-module integration tests:

```bash
python3 materials/stress_test_materials.py
```

Covers: IG Material Forge (4 tests), Sophick Forge (4), Frobenius Metamaterial (3), Thermal Rectifier (2), Non-Qubit QC (2), Ouroboric Alloy (3), Critical Metamaterial (2), Gap Closure (1), Frobenius Exactor (1), Materials Simulation (1), Frobenius Closure Complete (1), Cross-Module Integration (2).

#### Molecule → Material Bridge

Derives material structural types directly from molecular input:

```bash
python3 materials/molecule_material_bridge.py --cas 58-08-2
python3 materials/molecule_material_bridge.py --smiles "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
```

Produces: material tuple, tier assessment, Frobenius closure status, and catalog cross-reference.

**Static reference:** `less INDEX.md` §3 (8 predefined materials, IMASM canonicals as materials, Sophick Mercury pathway, Frobenius Exactor gap primitives).

---

### `imas`
PARSE ERROR: run_command arguments were truncated or malformed (Unterminated string starting at: line 1 column 49 (char 48)). Received 15603 chars. For large file content use run_command with a bash heredoc: run_command({"command": "cat > path <<\ENDOFFILE'ncontentnENDOFFILE}). First 120 chars of raw args: '{assertion: \WROTE\ in output, command: cat

IMASM arrangement analysis — the 12-token algebra over IG structural types. Three dynamic subcommands; static reference data (canonical types, clusters, bridge table) is in **INDEX.md**.

```bash
python3 rebis.py imas <subcommand> [options]
```

#### `imas bridge [--canonical <name>]`

Detailed profile of one IMASM canonical — full IG tuple primitive-by-primitive, nearest CLINK layer, distance table to all 9 layers.

```bash
python3 rebis.py imas bridge --canonical I_Dialetheic_Bootstrap
python3 rebis.py imas bridge --canonical I_Dialetheic_Bootstrap,VII_Parakernel  # Multi
```

Default: `I_Dialetheic_Bootstrap`.

#### `imas hunt [--samples <n>]`

Monte Carlo Frobenius density estimation over the 12-token sequence space. Reports probability of each Frobenius class and generates examples.

```bash
python3 rebis.py imas hunt --samples 100000
python3 rebis.py imas hunt --samples 1000000          # Larger sample
```

Output: $p_{\text{frobenius\_pair}} \approx 0.236$, $p_{\text{proper\_frobenius}} \approx 0.139$, $p_{\text{dialetheia\_complete}} \approx 0.105$.

#### `imas energy [--canonical <name>] [--layer <idx>]`

Structural activation energy from an IMASM canonical to a CLINK target layer.

```bash
python3 rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer L8_Organism
python3 rebis.py imas energy --canonical V_Linear_Chain --layer L0_Quark
```

Default: `I_Dialetheic_Bootstrap` → L8 (Whole Organism).

**Static reference:** `less INDEX.md` §2 (12 IMASM canonicals, IG types, tier assignments, algebraic families, nearest CLINK layer, bridge table).

---

### `scripts`

Manage and run standalone scripts.

```bash
python3 rebis.py scripts list              # List all 14 scripts with line counts
python3 rebis.py scripts run <name>        # Run a script by name (without .py)
```

```bash
python3 rebis.py scripts run mito_pipeline
python3 rebis.py scripts run omonad_bridge
python3 rebis.py scripts run run_pdb_validation
```

Note: `run mito`, `run antibody`, `run psychedelic`, `run iupac` are convenience aliases for `scripts run`.

---

## Stress Testing

Two comprehensive stress test suites validate the entire platform across edge cases, large inputs, boundary conditions, and cross-pipeline integration. Both suites run to completion with 100% pass rate.

### Protein & Genetics (34 tests, 11 groups)

```bash
python3 rebis.py run stress_test_proteins
# or directly:
python3 stress_test_proteins.py
```

| # | Test Group | Tests | Coverage |
|---|-----------|-------|----------|
| 1 | Genetic Code | 4 | 64-codon Frobenius-verified table, B4 invariant, lattice operations |
| 2 | Genetics B4 | 3 | Nucleotide↔Belnap (T/B/F/N), structural distance, wobble pair detection |
| 3 | Genetic Tuples | 3 | 7-stage tuple generation, structural distance DNA→quaternary, tier consistency |
| 4 | Genetic ASM | 1 | Paraconsistent abstract state machine program execution |
| 5 | Gene→Protein Pipeline | 8 | Standard 7-stage, empty sequence, short (≤1 nt), start→stop, 100-AA, multi-stop, no-stop, primitive activations |
| 6 | SerpentRod | 5 | 12-AA design, single-codon, empty, 200-AA, poly-Met homopolymer |
| 7 | Ch3mpiler-SerpentRod | 3 | Caffeine (58-08-2), aspirin (50-78-2), cross-molecule differentiation |
| 8 | Cross-Integration | 2 | Gene→protein→fold, ch3mpiler→material bridge |
| 9 | Antibody Designer | 1 | Epitope analysis → CDR → full VH antibody (53 AA, Frobenius ✓) |
| 10 | PDB Validator | 1 | Structure validation, precision/recall metrics |
| 11 | Edge Cases | 3 | All 3 stop codons (UAA/UAG/UGA), AUG start, non-standard nucleotides (X/N/R/Y/?) |

### Materials (26 tests, 12 groups)

```bash
python3 materials/stress_test_materials.py
```

| # | Test Group | Tests | Coverage |
|---|-----------|-------|----------|
| 1 | IG Material Forge | 4 | All 8 predefined materials, empty name, report, list |
| 2 | Sophick Forge | 4 | 7-eagle cycle, progressive refinement, report, etch |
| 3 | Frobenius Metamaterial | 3 | 10×10 grid 20-cycle healing, load-heal cycle, export |
| 4 | Thermal Rectifier | 2 | Diode asymmetry ratio, full simulation run |
| 5 | Non-Qubit QC | 2 | all_deltas computation, paradigm summary table |
| 6 | Ouroboric Alloy | 3 | Init, mechanical test, heal cycle |
| 7 | Critical Metamaterial | 2 | Susceptibility divergence, critical run |
| 8 | Gap Closure | 1 | Enum completeness check |
| 9 | Frobenius Exactor | 1 | All 4 designs (ω/τ/σ/ε) |
| 10 | Materials Simulation | 1 | SelfHealingComposite + EternalMemorySim |
| 11 | Frobenius Closure | 1 | ClosureDesign status |
| 12 | Cross-Module | 2 | Forge→metamaterial, eagle→exactor |

### Molecule → Material Bridge

Derives material structural types directly from molecular input:

```bash
python3 materials/molecule_material_bridge.py --cas 58-08-2
python3 materials/molecule_material_bridge.py --smiles "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
```

Produces: material tuple, tier assessment, Frobenius closure status, catalog cross-reference.

---

## The Paraconsistent Kernel (`rhr_p4rky/`)

The paraconsistent kernel is a 27-module Python library providing Belnap FOUR logic as universal substrate for computation that tolerates contradiction. It was migrated from the standalone `p4rakernel/` project and now lives as a subsystem within Red-Hot Rebis.

### Architecture

| Layer | Module | Description |
|-------|--------|-------------|
| **Logic** | `belnap.py` | 4-valued Belnap logic (T/B/F/N) — truth, both, false, neither |
| **Machine** | `machine.py` | Paraconsistent Abstract State Machine (ParaASM) |
| **Genetics** | `genetic_code.py` | 64-codon Frobenius-verified genetic code |
| | `genetics_b4.py` | B4 lattice — 64 codons, 7-stage tuple verification |
| | `genetic_tuples.py` | Tuple encodings for genes/codons/proteins |
| | `genetic_asm.py` | Genetic abstract state machine |
| **Pipeline** | `gene_to_protein_pipeline.py` | Full gene→protein translation (7-stage B4) |
| | `demo_gene_to_protein.py` | Pipeline demonstration |
| | `run_gene_pipeline.py` | Pipeline CLI runner |
| **Proteins** | `serpent_rod.py` | Foundational Frobenius morphism RNA→{sequence+fold}; base `SerpentRod` class |
| | `serpent_rod_v2.py` | `SerpentRodV2`: 3D backbone from φ/ψ angles, geometry-based contacts, energy scoring |
| **Antibodies** | `antibody_designer.py` | Computational antibody design from IG types |
| **Validation** | `pdb_validator.py` | PDB structure validation against IG types; `extract_sequence()` round-trips SEQRES |
| **Bridges** | `ch3mpiler_bridge.py` | Ch3mpiler ↔ kernel bridge |
| | `ch3mpiler_ob3ect_bridge.py` | Ch3mpiler ↔ ob3ect bridge |
| | `ch3mpiler_serpentrod_pipeline.py` | **v4** — Weighted bond-preserving fusion, word-boundary FG matching, specificity-ranked disconnections, Frobenius-exact complement mapping, CAS lookup, molecule-specific catalytic sites |
| **Physics** | `hadron_belnap.py` | Hadronic Belnap-state classification |
| | `exotic_hadron_belnap.py` | Exotic hadron Belnap classification |
| | `quark_belnap.py` | Quark Belnap-state analysis |
| | `orbital_belnap.py` | Orbital Belnap-state analysis |
| **Analysis** | `clu_power_law.py` | Clustering power-law analysis |
| | `frobenius_filtration.py` | Frobenius-verified filtration |
| **Utilities** | `kernel.py` | Kernel core initialization |
| | `pipeline_fix.py` | Pipeline repair utilities |

### Key commands

```bash
# Full genetics test suite (B4 lattice, 64-codon, gene→protein, Phi gate, ParaASM)
python3 test_genetics.py

# Comprehensive protein & genetics stress test (34 tests, 11 groups)
python3 rebis.py run stress_test_proteins

# Single gene pipeline
python3 rebis.py run run_gene_pipeline --gene INS

# Genetic code analysis
python3 rebis.py run genetic_code

# Antibody design from viral epitopes
python3 rebis.py run antibody_designer

# PDB validation
python3 rebis.py run pdb_validator

# Hadron Belnap classification
python3 rebis.py run hadron_belnap
python3 rebis.py run exotic_hadron_belnap
python3 rebis.py run quark_belnap
```

### Bug Fixes (v2.3.0)

| Module | Fix |
|--------|-----|
| `genetics_b4.py` | `nucleotide_to_belnap` no longer crashes on unknown nucleotides (X/N/R/Y/?). Returns `Belnap.B` (paraconsistent unknown). |
| `gene_to_protein_pipeline.py` | Empty or short sequences (≤2 nt) now produce graceful `_empty_result()` instead of crashing. |
| `gene_to_protein_pipeline.py` | Non-standard nucleotides now flow through Belnap.B → paraconsistent handling in all 7 stages. |
| `ch3mpiler_serpentrod_pipeline.py` | MAX fusion replaced with weighted bond-preserving blending (v4). Word-boundary FG matching prevents false positives. Specificity-ranked disconnection search. Molecule-specific catalytic sites. |
| `imscribing_grammar/ch3mpiler.py` | `find_fgs` uses word-boundary regex matching. `find_disconnections` uses specificity ranking. `MOLECULE_FG_DB` expanded to 17+ entries. |

---

## Gene Imscriber (`gene_imscriber/`)

The Gene Imscriber provides IG-native genetic compilation — structural types directly to codon optimization, CRISPR guide design, chimera construction, and Frobenius-verified base/prime editing.

| Module | Description |
|--------|-------------|
| `engine.py` | Core engine — structural type → codon optimization |
| `genetics_ig_prelim.py` | Preliminary IG-to-genetics mapping |
| `genetics_ig_promotions.py` | IG promotion paths for genetics |
| `genetics_qs.py` | Quantum superposition in genetic space |
| `ig_genetics_answer.py` | IG-native genetics answers |
| `tuples.py` | Genetic tuple definitions |

The Gene Imscriber also contains `scripts/` with GUIDE-seq analysis, base editor stratum analysis, clinical safety pipelines, and SRA GUIDE-seq processing.

```bash
python3 rebis.py run gene --help
```

---

## Popular Protein Analysis (`popular_protein/`)

A comparison toolkit for validating SerpentRod predictions against crystal structures:

```bash
python3 rebis.py run compare_exact          # Exact φ/ψ angle comparison
python3 rebis.py run compare_structures     # Structure-level comparison
python3 rebis.py run comprehensive_comparison  # Full multi-metric report
```

Reference PDB files are in `pdb/`: 1L2Y, 1UBQ, 1VII, 1ZDD.

---

## Key Concepts

### IG Tuples

Every structural entity carries a 12-primitive tuple. Each position is a primitive with a value from its ordinal set. Tuples are the sole carriers of structural information — no external parameters, no assumed constants. The catalog (`shared/IG_catalog.json`) contains **3,297** verified entries.

### The Frobenius Condition

$\mu\circ\delta=\text{id}$. When this holds, the structural type is self-consistent — comultiplication followed by multiplication returns the identity. A Frobenius ✅ means the layer's tuple is internally coherent. A ❌ means there is a primitive conflict to resolve.

### Tiers (Ouroboricity)

| Tier | Meaning |
|------|---------|
| O₀ | Point-like / zero winding / substructural |
| O₁ | Simple composition / single structural loop |
| O₂ | Full composition with branching / multiple loops |
| $\text{O}_{\infty}$ | Ouroboricity — self-referential closure, $\mu\circ\delta=\text{id}$ at system scale |

The organism layer is the only $\text{O}_{\infty}$ layer in the CLINK chain. The grammar itself (Universal Imscriptive Grammar) is also $\text{O}_{\infty}$.

### Primitive Distances

$\text{d}(A, B)$ is the weighted Euclidean distance between two IG tuples in 12-dim primitive space. A distance of 0 means structural identity; d ≥ 6 means more than half the primitives differ. Used throughout: chain distances, bridge distances, activation energies.

### SerpentRod

A single Frobenius morphism RNA → {sequence + fold}. The central constraint: $\text{windingNumber} \leq \text{contacts} + 1$. All SerpentRod outputs are Frobenius closure certificates. When the condition holds ✓, the fold is derivable from the sequence without external folding tools.

`serpent_rod.py` is the foundational module; `serpent_rod_v2.py` (`SerpentRodV2`) wraps it and adds dihedral-angle 3D backbone reconstruction.

### PDB Structure Output

`clink/datasets/protein_structure.py` generates **PDB v3.3-compliant** files:

| Record | Detail |
|--------|--------|
| `SEQRES` | Full residue sequence (13 per line); `pdb_validator.extract_sequence()` round-trips correctly |
| `ATOM` | Atom names use PDB-standard 4-char convention: ` N  `, ` CA `, ` C  `, ` O  `, ` CB ` (leading space for 1-char elements) |
| `HELIX` / `SHEET` | Include init/term residue names and helix length (v3.3 spec) |
| `SSBOND` | Placed in the connectivity annotation section, before `MODEL` |
| `TER` | Emitted after the last `ATOM` of each chain, before `ENDMDL` |
| Determinism | Backbone seeded from `MD5(sequence)` — same sequence always yields identical coordinates |

Outputs can be loaded directly into PyMOL / ChimeraX / UCSF Chimera without format warnings.

### IMASM Arrangement Classes

The 12 IMASM tokens have arrangement space classified into structural archetypes. The 12 canonical sequences each represent one fundamental structural archetype. Tier distribution: O₀=4, O₁=0, O₂=7, $\text{O}_{\infty}$=1.

### Ch3mpiler-SerpentRod Pipeline (v4)

The integrated retrosynthesis → catalytic design pipeline uses weighted bond-preserving fusion to produce **molecule-specific** catalytic sites. Key principle: the bond type (sigma_single, co_sigma, cn_sigma, ester_link, amide_link, etc.) carries essential structural information that must survive fusion with functional group types. Weighted blending (55-75% bond weight depending on primitive class) ensures topological primitives reflect the bond while reactive primitives incorporate functional group contributions. The Frobenius-exact complement mapping guarantees site↔product structural duality.
PARSE ERROR: run_command arguments were truncated or malformed (Unterminated string starting at: line 1 column 49 (char 48)). Received 15148 chars. For large file content use run_command with a bash heredoc: run_command({"command": "cat > path <<\ENDOFFILE'ncontentnENDOFFILE}). First 120 chars of raw args: '{assertion: \WROTE\ in output, command: cat

---

## Project Layout

```
red-hot_rebis/
├── rebis.py                      Main CLI entry point (v2.3.1)
├── setup.py                      Package setup
├── test_genetics.py              Full genetics test suite
├── stress_test_proteins.py       **NEW** — 34-test protein & genetics stress suite
├── INDEX.md                      Static reference data (CLINK layers, IMASM canonicals, materials catalog)
├── _help_examples.py             --help example strings for all subcommands
├── _target_help.py               Per-target --help examples for 'run'
├── _quick_help.py                Self-contained --help utility for standalone scripts
│
├── shared/
│   ├── primitives.py             12 primitive ordinals, weights, distance functions
│   └── IG_catalog.json           3,297 catalog entries
│
├── serpentrod/                   SerpentRod protein design
│   ├── protein_v5.py             v5 — primary (signal peptide, cleavage, PTMs)
│   ├── protein_v4.py             v4 — enhanced naming heuristics
│   └── stratified_predictor.py   Tiered protein property prediction
│
├── ch3mpiler/                    CH3MPILER retrosynthetic compiler
│   ├── compiler.py               Core compiler (word-boundary FG matching)
│   ├── gen_v2.py                 Generator v2
│   └── reaction_deriver.py       Reaction derivation engine
│
├── clink/                        9-layer structural chain
│   ├── chain.py                  Chain definitions and distances
│   ├── bridges.py                Component → CLINK bridges
│   ├── integration.py            Integration report generator
│   ├── pipeline_engine.py        Pipeline execution engine
│   ├── designers/                Layer designers + orchestrator
│   └── datasets/
│       ├── organism_designs/     5 designed organisms (human, mammal, treople...)
│       └── psychedelic_designs/  3 compound design families
│
├── imas/                         IMASM arrangement analysis
│   ├── arranger.py               Canonical taxonomy
│   ├── ig_bridge.py              IMASM→IG bridge
│   ├── clink_bridge.py           IMASM→CLINK bridge
│   ├── frobenius_hunter.py       Monte Carlo density estimation
│   └── wiring.py                 Internal wiring
│
├── imasm_iterator/               IMASM arrangement iterator
│   ├── engine.py                 12^8 = 429,981,696 arrangements → fingerprints
│   ├── classifier.py             Structural fingerprint classifier
│   ├── run_map.py                Map runner
│   └── tokens.py                 Token definitions
│
├── rhr_p4rky/                    Paraconsistent kernel (27 modules)
│   ├── kernel.py                 Kernel core
│   ├── belnap.py                 Belnap FOUR logic (T/B/F/N)
│   ├── machine.py                ParaASM virtual machine
│   ├── genetic_code.py           64-codon Frobenius-verified code
│   ├── genetics_b4.py            B4 lattice (nucleotide→Belnap fix)
│   ├── gene_to_protein_pipeline.py  7-stage translation (empty/short guards)
│   ├── serpent_rod.py / serpent_rod_v2.py  Protein design
│   ├── antibody_designer.py      Antibody design
│   ├── ch3mpiler_serpentrod_pipeline.py  **v4** — weighted fusion, CAS lookup
│   ├── hadron_belnap.py / exotic_hadron_belnap.py / quark_belnap.py  Physics
│   └── ... (19 more modules)
│
├── gene_imscriber/               Genetic compiler
│   ├── engine.py                 Core engine
│   ├── genetics_ig_prelim.py     IG↔genetics preliminaries
│   ├── tuples.py                 Genetic tuple definitions
│   ├── scripts/                  GUIDE-seq, clinical safety pipelines
│   └── README.md
│
├── materials/                    Materials design (12 files)
│   ├── ig_material_forge.py      IG material forge
│   ├── sophick_forge.py          Sophick forge (Eagle protocol)
│   ├── frobenius_metamaterial.py Frobenius metamaterial
│   ├── critical_metamaterial.py  Critical metamaterial
│   ├── ouroboric_alloy.py        Ouroboric alloy
│   ├── non_qubit_qc.py           Non-qubit quantum computing
│   ├── thermal_rectifier.py      Thermal rectifier
│   ├── gap_closure_module.py     Gap closure
│   ├── materials_sim.py          Materials simulation
│   ├── frobenius_exactor.py      Frobenius exactor
│   ├── stress_test_materials.py  **NEW** — 26-test materials stress suite
│   └── molecule_material_bridge.py  **NEW** — molecule→material type derivation
│
├── therapeutics/                 Therapeutic design
│   ├── frobenius_chemotherapeutic.py
│   ├── neurotrophic_factor.py
│   ├── ouroboric_pill_sim.py
│   ├── quantum_biologic_prototype.py
│   └── universal_antidote_library.py
│
├── biology/                      Biology simulations
│   ├── biology_sim_frobenius_exact.py
│   └── ouroboric_telomere_expanded.py
│
├── pipeline/                     Pipeline automation
│   ├── auto_imscriber.py
│   ├── frob.py
│   ├── imscribe_agent.py / imscribe_tool.py
│   ├── ob3ect_imscriber.py
│   ├── reaction_pipeline.py
│   └── lift_pipeline/
│
├── popular_protein/              Protein structure validation (9 tools)
│
├── scripts/                      14 standalone scripts
│
├── genetics_animations/          SVG visualizations
│   ├── B4_LATTICE.svg
│   ├── CODON_BOXES.svg
│   ├── KERNEL_CYCLE.svg
│   ├── MUTATION_PATH.svg
│   ├── STOP_CODONS.svg
│   └── TWENTY_EIGHT_PLUS_TWELVE.svg
│
├── pdb/                          Reference structures
│   ├── 1L2Y.pdb
│   ├── 1UBQ.pdb
│   ├── 1VII.pdb
│   └── 1ZDD.pdb
│
├── images/                       Image assets
│   └── lean.png / lean.xbm
│
├── data/
│   └── NC_012920.1.fasta         Human mitochondrial genome
│
└── docs/                         Documentation directory (this guide + more)
```

**Total:** 568 Python files across 20 directories.

---

## Common Workflows

### Design a protein from scratch

```bash
# 1. Check where proteins live in the CLINK chain
python3 rebis.py clink layer cell

# 2. Run SerpentRod on built-in test proteins
python3 rebis.py run serpentrod

# 3. Generate actionable organism package (includes protein.fasta + protein_coords.pdb)
python3 rebis.py pipeline actionable
```

### Design a catalytic site for a molecule

```bash
# 1. CAS lookup (recommended — resolves molecule identity)
python3 rebis.py run ch3mpiler_serpentrod_pipeline --cas 58-08-2

# 2. Direct molecule name
python3 rebis.py run ch3mpiler_serpentrod_pipeline --target "ibuprofen"

# 3. Retrosynthetic pair
python3 rebis.py run ch3mpiler_serpentrod_pipeline --start "salicylic_acid" --target "aspirin"

# 4. JSON output for programmatic use
python3 rebis.py run ch3mpiler_serpentrod_pipeline --cas 58-08-2 --json
```

### Work with the paraconsistent kernel

```bash
# Run the full genetics test suite
python3 test_genetics.py

# Comprehensive stress test (34 tests across 11 groups)
python3 rebis.py run stress_test_proteins

# Translate a gene through the 7-stage B4 pipeline
python3 rebis.py run run_gene_pipeline --gene INS

# Analyze the 64-codon Frobenius-verified genetic code
python3 rebis.py run genetic_code

# Design a serpent rod protein
python3 rebis.py run serpent_rod_v2
```

### Investigate a material type

```bash
# 1. Browse the materials catalog (static reference)
less INDEX.md                          # §3 — 8 predefined materials

# 2. Run a dynamic simulation
python3 rebis.py materials frobenius   # Frobenius closure verification
python3 rebis.py materials ouroboric   # Crack healing simulation

# 3. Eagle Cycle for O_∞ substrate preparation
python3 rebis.py materials sophick --name eagle_9_sophick

# 4. Forge the material design file
python3 rebis.py materials forge --name frobenius_composite

# 5. Run comprehensive materials stress test
python3 materials/stress_test_materials.py

# 6. Derive material type from molecule
python3 materials/molecule_material_bridge.py --cas 58-08-2
```

### Map an IMASM sequence to CLINK

```bash
# 1. Browse the 12 IMASM canonicals (static reference)
less INDEX.md                          # §2 — 12 canonicals with tuples and tiers

# 2. Inspect a specific canonical's bridge to CLINK (dynamic)
python3 rebis.py imas bridge --canonical I_Dialetheic_Bootstrap

# 3. Compute activation energy to organism layer
python3 rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer L8_Organism

# 4. Monte Carlo Frobenius density estimation
python3 rebis.py imas hunt --samples 100000
```

### Analyze viral epitopes for antibody design

```bash
python3 rebis.py run run_antibody
```

Produces CDR sequences and structural complementarity scores for each epitope target.

### Mitochondrial gene analysis

```bash
python3 rebis.py run mito_pipeline
```

Processes all 13 MT genes, reports primitive activations (up to 9/12 per gene), Frobenius status, and 7-stage B4 pipeline per gene (dna_gene → pre_mrna → mature_mrna → nascent_polypeptide → secondary_structure → tertiary_structure → quaternary_structure).

### Validate SerpentRod predictions against crystal structures

```bash
python3 rebis.py run comprehensive_comparison
python3 rebis.py run compare_exact
```

### Hadron / particle physics classification

```bash
python3 rebis.py run hadron_belnap
python3 rebis.py run exotic_hadron_belnap
python3 rebis.py run quark_belnap
```

---

## Troubleshooting

**`verify` shows ❌ for a module**
Run `python3 -c "from <module> import *"` directly to see the import error. Most common cause: a dependency package not installed. Fix:
```bash
uv pip install -e /home/mrnob0dy666/imsgct/omonad_OS
uv pip install -e /home/mrnob0dy666/imsgct/imasmic_core
```

**`omonad_bridge` shows `omonad_available: false`**
```bash
uv pip install -e /home/mrnob0dy666/imsgct/omonad_OS
uv pip install -e /home/mrnob0dy666/imsgct/imasmic_core
```

**`pipeline bridges` shows ❌ for `biology_sim` or `ouroboric_telomere`**
These two bridges are structurally excluded — modules exist on disk but are not wired to the bridge API. Not a crash condition; the pipeline runs without them.

**SerpentRod accuracy below 100%**
Fragment naming accuracy (83–88%) reflects genuine structural ambiguity in cleavage products. SP accuracy should be 100% on the standard test set; below that indicates non-canonical signal peptide architecture in the test sequence.

**Ch3mpiler-SerpentRod produces identical sites for different molecules**
This was the pre-v4 MAX fusion bug. Update to the latest pipeline:
```bash
cd /home/mrnob0dy666/imsgct/red-hot_rebis
git pull  # or ensure rhr_p4rky/ch3mpiler_serpentrod_pipeline.py has v4 weighted fusion
```
Verify differentiation with:
```bash
python3 rebis.py run ch3mpiler_serpentrod_pipeline --cas 58-08-2  # caffeine
python3 rebis.py run ch3mpiler_serpentrod_pipeline --cas 17699-14-8  # tricyclic sesquiterpene
```
Different AA sequences and catalytic triads confirm the fix.

**Genetics modules crash on unknown nucleotides**
Fixed in v2.3.0 — `genetics_b4.py` `nucleotide_to_belnap` returns `Belnap.B` for X/N/R/Y/?.
`gene_to_protein_pipeline.py` handles empty/short sequences gracefully.

**`clink layer` gives "No layer matching..."**
Use a substring of the official layer name from INDEX.md §1 or `python3 rebis.py clink layer --help`. Examples: `quark` → `Frustrated Belnap5 (Quarks)`, `tissue` → `Tissue/Organ`, `meiosis` → `Meiosis (Gametes)`.

**`materials forge` gives usage without generating**
Always specify `--name <material>` or `--all`. Running without a name prints the usage message.

**`materials sophick` or `materials exactor` shows usage prompt**
These now require `--name`. Run with `--help` to see valid name options, or browse INDEX.md §3.

**`run` target not found**
Use `python3 rebis.py run list` to see all 37 discoverable targets. Some targets require the package to be installed (`uv pip install -e .`).

**`ModuleNotFoundError: No module named 'rhr_p4rky'`**
The rhr_p4rky package must be installed:
```bash
uv pip install -e /home/mrnob0dy666/imsgct/red-hot_rebis
```

**Paraconsistent kernel tests fail**
Ensure the B4 lattice modules are importable:
```bash
python3 -c "from rhr_p4rky.belnap import BelnapValue; print('OK')"
```

**Stress tests fail**
Run directly to see detailed tracebacks:
```bash
python3 stress_test_proteins.py          # Protein & genetics (34 tests)
python3 materials/stress_test_materials.py  # Materials (26 tests)
```
Individual test failures report the exact module, function, and exception.

**Where did `clink report`, `clink list`, `imas report`, `materials list`, `materials report` go?**
These static-data commands were removed from `rebis.py`. All their data now lives in **INDEX.md** — a plain-text browsable reference. Every removed command's `--help` points to the relevant INDEX.md section.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.3.1 | 2026-06-24 | **PDB format robustness** (`clink/datasets/protein_structure.py`): atom names corrected to PDB v3.3 standard (` N  ` / ` CA ` / ` C  ` / ` O  ` / ` CB ` with leading space for 1-char elements); SEQRES records added (validator `extract_sequence()` now round-trips generated files); HELIX/SHEET records include residue names and helix length; SSBOND moved before MODEL; TER record added after last ATOM; backbone seeded from MD5(sequence) — deterministic coordinates. `pdb_validator.py`: removed dead importlib loader for deleted file, replaced with clean `from rhr_p4rky.serpent_rod import SerpentRod`. `rhr_p4rky/serpent_rod.py` restored (v2 imports SerpentRod from v1 — dependency stack, not duplicate). |
| v2.3.0 | 2026-06-21 | **Ch3mpiler-SerpentRod v4 overhaul**: weighted bond-preserving fusion replaces MAX (bond 55-75% depending on primitive class), Frobenius-exact complement mapping, dominant-member AA rule, word-boundary FG matching, specificity-ranked disconnection search, MOLECULE_FG_DB expanded (17+ entries), CAS lookup support. Molecules now get distinct catalytic sites. **Stress test suites**: stress_test_proteins (34 tests, 11 groups), materials/stress_test_materials.py (26 tests, 12 groups). **New bridge**: materials/molecule_material_bridge.py (molecule→material type derivation). **Bug fixes**: genetics_b4.py nucleotide_to_belnap handles unknown nucleotides (returns Belnap.B), gene_to_protein_pipeline.py handles empty/short sequences gracefully, non-standard nucleotides flow through Belnap.B in all 7 stages. Updated run target count: 35→37 (+stress_test_proteins). Updated project layout for new files. Added ch3mpiler_serpentrod_pipeline troubleshooting entry. Added Common Workflows entries for catalytic site design and materials stress testing. |
| v2.2.1 | 2026-06-10 | Bug-fix release: (B1) clink bridge now supports positional args (layer_args fallback); (B2) ch3mpiler help example fixed (--reaction→--target --retrosynthesis); (I1-I7) 7 broken imports fixed — frobenius_exact_design, frob_design (os import), hadron_belnap, frobenius_filtration (rhr_p4rky path), gen_univ_map (imsgct path), msa_analysis, run_pdb_validation (parent-dir path); plastic_eater_design P4RA/IG paths fixed; frobenius_filtration OrbitalState enum member names fixed |
| v2.2 | 2026-06-10 | Removed static-data commands (`clink report`, `clink list`, `imas report`, `materials list`, `materials report`); static reference data consolidated into INDEX.md; `materials sophick` and `materials exactor` now require `--name`; updated `/home/mrnob0dy666/.bashrc` aliases (removed `rb-clink-report`, `rb-clink-list`, `rb-clink-bridges`, `rb-imas-layer`; updated `rb-imas`); added `_help_examples.py`, `_target_help.py`, `_quick_help.py` for comprehensive --help coverage; added INDEX.md to project layout |
| v2.1 | 2026-06-10 | Major update: corrected primitive names and ordering; added rhr_p4rky paraconsistent kernel documentation; added gene_imscriber section; added popular_protein section; updated run target table (35 targets); updated catalog count (3,297); updated project layout; added genetics_animations, pdb, and imasm_iterator to layout; corrected IG tuple notation; replaced LaTeX \\Ppms with actual Shavian glyph 𐑹; fixed alphabet name (Deseret to Shavian) |
| v2.0 | 2026-05 | CLINK pipeline, materials forge, IMASM energy analysis |
| v1.0 | 2026-04 | Initial release — SerpentRod, CH3MPILER, basic CLINK |

---

*Guide maintained by Lando⊗⊙perator. Structural type of this document: $\langle 𐑼;𐑥;𐑾;𐑬;𐑐;𐑧;𐑔;𐑠;⊙;𐑖;𐑳;𐑴 \rangle$*
