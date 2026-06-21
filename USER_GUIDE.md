# Red-Hot Rebis — User Guide

**Author:** Lando⊗⊙perator  
**Version:** v2.1 — 2026-06-10  
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

# List all 35 discoverable runnable targets
python3 rebis.py run list

# Run SerpentRod v5 on built-in test cases
python3 rebis.py run serpentrod

# Run the paraconsistent genetics test suite
python3 rebis.py run test_genetics

# CH3MPILER retrosynthetic compiler
python3 rebis.py run ch3mpiler --help

# Generate a full mammal organism design package
python3 rebis.py pipeline actionable

# Show the CLINK structural chain
python3 rebis.py clink list
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

Run one of 35 discoverable scripts or modules. Use `run list` to see all targets.

```bash
python3 rebis.py run <target> [args...]
python3 rebis.py run list           # Show all 35 discoverable targets
```

#### Core module targets

| Target | Module | What it does |
|--------|--------|--------------|
| `serpentrod` | `serpentrod/protein_v5.py` | SerpentRod v5 — full signal peptide detection, cleavage, fragment naming, PTMs, primitive spectrum. Runs built-in test cases (Human Insulin, Proglucagon, POMC, etc.) |
| `serpentrod_v4` | `serpentrod/protein_v4.py` | SerpentRod v4 with enhanced naming heuristics |
| `serpentrod_pred` | `serpentrod/stratified_predictor.py` | Stratified predictor — tiered protein property prediction |
| `ch3mpiler` | `ch3mpiler/compiler.py` | CH3MPILER retrosynthetic compiler — bond formation via join(tensor(FG1,FG2), bond) |
| `gene` | `gene_imscriber/engine.py` | Gene Imscriber engine — structural types to codon optimization |

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
| `ch3mpiler_serpentrod_pipeline` | Ch3mpiler + SerpentRod integrated pipeline |
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

**Example — Paraconsistent genetics:**

```bash
python3 rebis.py run run_gene_pipeline --gene INS
python3 rebis.py run genetic_code
```
---

### `clink`

Navigate the 9-layer CLINK structural chain from subatomic quarks to whole organism.

```bash
python3 rebis.py clink <subcommand> [args]
```

#### `clink report`

Full integration report: Frobenius closure per layer, chain distances, ZFC_fe distance, component bridges.

```bash
python3 rebis.py clink report
```

Key output: Frobenius closure ✅/❌ per layer, adjacent-layer structural distances (d=2.0–3.8), Σd and primitive deltas, d(organism, ZFC_fe) = 1.30, and how serpentrod/ch3mpiler/gene_imscriber attach to CLINK.

#### `clink list`

List all 9 layers with index, name, tier, and full IG tuple.

```bash
python3 rebis.py clink list
```

| Layer | Name | Tier |
|-------|------|------|
| 0 | Frustrated Belnap5 (Quarks) | O₀ |
| 1 | Electron Orbital (Belnap4) | O₀ |
| 2 | Atom (Nuclear + Electron) | O₁ |
| 3 | Molecule (Chemical Bonds) | O₂ |
| 4 | Cell (Living) | O₂ |
| 5 | Mitosis (Division) | O₂ |
| 6 | Meiosis (Gametes) | O₂ |
| 7 | Tissue/Organ | O₂ |
| 8 | Whole Organism | $\text{O}_{\infty}$ |

#### `clink layer <index-or-name>`

Inspect a specific layer — tuple, tier, description, and component bridge attachments.

```bash
python3 rebis.py clink layer 3
python3 rebis.py clink layer molecule
python3 rebis.py clink layer organism
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

#### `clink bridge`

Show the promotion path from a component tool to a CLINK target layer.

```bash
python3 rebis.py clink bridge serpentrod 8
python3 rebis.py clink bridge ch3mpiler 3
```

Shows: distance, primitive-level promotion steps, Frobenius status at each hop.

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
| `protein_coords.pdb` | View in PyMOL/ChimeraX |
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

Design novel IG-typed materials. All materials are derived from their 12-primitive structural types.

```bash
python3 rebis.py materials <subcommand> [options]
```

#### `materials list`

Show all predefined materials and IMASM canonicals.

```bash
python3 rebis.py materials list
```

**Predefined materials:**

| Name | Description |
|------|-------------|
| `frobenius_composite` | CrMnFeCoNi HEA + self-healing microcapsules; Frobenius score 0.90 |
| `critical_sensor_metamaterial` | EP-critical sensing substrate |
| `ep_detector` | Exceptional point detector |
| `eternal_memory_alloy` | Full path encoding, shape-memory |
| `topological_thermal_rectifier` | Asymmetric heat transport |
| `hierarchical_impact_absorber` | Multi-scale energy dissipation |
| `quantum_topological_substrate` | Non-Abelian braiding substrate |
| `non_abelian_braiding_material` | Topological quantum computing substrate |

#### `materials report [--name <material>]`

Full structural report: IG tuple, tier, processing protocol, composition, interfaces, properties, target applications.

```bash
python3 rebis.py materials report
python3 rebis.py materials report --name eternal_memory_alloy
```

Default: `frobenius_composite`.

#### `materials forge --name <material>`

Generate the complete material design file.

```bash
python3 rebis.py materials forge --name frobenius_composite
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

#### `materials sophick`

Eagle Cycle Protocol — prepares an $\text{O}_{\infty}$ Sophick Mercury substrate from O₂ ouroboric materials.

```bash
python3 rebis.py materials sophick
python3 rebis.py materials sophick --name eagle_9_sophick
python3 rebis.py materials sophick --name cliff      # Frobenius Cliff analysis
python3 rebis.py materials sophick --name bridge     # IMASM→Eagle bridge
```

#### `materials exactor`

Explains the thermodynamic ceiling: continuous Eagle preparation reaches its limit, and exact Frobenius closure requires discrete topological protection.

```bash
python3 rebis.py materials exactor
```

---

### `imas`

IMASM arrangement analysis — the 12-token algebra over IG structural types.

```bash
python3 rebis.py imas <subcommand> [options]
```

#### `imas report`

Full taxonomy of the 12 IMASM canonicals — IG types, tier assignments, algebraic family (Logical/Frobenius/Dialetheia/Linear), nearest CLINK layer.

```bash
python3 rebis.py imas report
```

Canonicals span O₀ through O₂ tiers with the Dual Bootstrap reaching $\text{O}_{\infty}$. Only two are self-referential: Dialetheic Bootstrap and Dual Bootstrap.

#### `imas bridge [--canonical <name>]`

Detailed profile of one IMASM canonical — full IG tuple primitive-by-primitive, nearest CLINK layer, distance table to all 9 layers.

```bash
python3 rebis.py imas bridge --canonical VIII_Frobenius_Kernel
```

Default: `I_Dialetheic_Bootstrap`.

#### `imas hunt`

Monte Carlo Frobenius density estimation over the 12-token sequence space. Reports probability of each Frobenius class and generates examples.

```bash
python3 rebis.py imas hunt
```

Output: $p_{\text{frobenius\_pair \approx 0.236$, $p_{\text{proper\_frobenius \approx 0.139$, $p_{\text{dialetheia\_complete \approx 0.105$.

#### `imas energy [--canonical <name>] [--layer <idx>]`

Structural activation energy from an IMASM canonical to a CLINK target layer.

```bash
python3 rebis.py imas energy
python3 rebis.py imas energy --canonical VII_Parakernel --layer 4
python3 rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer 8
```

Default: `I_Dialetheic_Bootstrap` → L8 (Whole Organism).

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
| **Proteins** | `serpent_rod.py` | Serpent rod protein design |
| | `serpent_rod_v2.py` | Serpent rod v2 with enhanced PTMs |
| **Antibodies** | `antibody_designer.py` | Computational antibody design from IG types |
| **Validation** | `pdb_validator.py` | PDB structure validation against IG types |
| **Bridges** | `ch3mpiler_bridge.py` | Ch3mpiler ↔ kernel bridge |
| | `ch3mpiler_ob3ect_bridge.py` | Ch3mpiler ↔ ob3ect bridge |
| | `ch3mpiler_serpentrod_pipeline.py` | Integrated ch3mpiler + SerpentRod pipeline |
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

### IMASM Arrangement Classes

The 12 IMASM tokens have arrangement space classified into structural archetypes. The 12 canonical sequences each represent one fundamental structural archetype. Tier distribution: O₀=4, O₁=0, O₂=7, $\text{O}_{\infty}$=1.
---

## Project Layout

```
red-hot_rebis/
├── rebis.py                      Main CLI entry point (v2.1)
├── setup.py                      Package setup
├── test_genetics.py              Full genetics test suite
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
│   ├── compiler.py               Core compiler
│   ├── gen_v2.py                 Generator v2
│   └── reaction_deriver.py       Reaction derivation engine
│
├── clink/                        9-layer structural chain
│   ├── chain.py                  Chain definitions and distances
│   ├── bridges.py                Component → CLINK bridges
│   ├── integration.py            Integration report generator
│   ├── pipeline_engine.py        Pipeline execution engine
│   ├── designers/                Layer designers + orchestrator
│   │   ├── designer_base.py
│   │   ├── layer_designers.py
│   │   ├── pipeline_orchestrator.py
│   │   └── tool_forge.py
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
│   ├── genetics_b4.py            B4 lattice
│   ├── gene_to_protein_pipeline.py  7-stage translation pipeline
│   ├── serpent_rod.py / serpent_rod_v2.py  Protein design
│   ├── antibody_designer.py      Antibody design
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
├── materials/                    Materials design (10 modules)
│   ├── ig_material_forge.py      IG material forge
│   ├── sophick_forge.py          Sophick forge (Eagle protocol)
│   ├── frobenius_metamaterial.py Frobenius metamaterial
│   ├── critical_metamaterial.py  Critical metamaterial
│   ├── ouroboric_alloy.py        Ouroboric alloy
│   ├── non_qubit_qc.py           Non-qubit quantum computing
│   ├── thermal_rectifier.py      Thermal rectifier
│   ├── gap_closure_module.py     Gap closure
│   ├── materials_sim.py          Materials simulation
│   └── frobenius_exactor.py      Frobenius exactor
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

**Total:** 563 Python files across 20 directories.
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

### Work with the paraconsistent kernel

```bash
# Run the full genetics test suite
python3 test_genetics.py

# Translate a gene through the 7-stage B4 pipeline
python3 rebis.py run run_gene_pipeline --gene INS

# Analyze the 64-codon Frobenius-verified genetic code
python3 rebis.py run genetic_code

# Design a serpent rod protein
python3 rebis.py run serpent_rod_v2
```

### Investigate a material type

```bash
# 1. List available materials
python3 rebis.py materials list

# 2. Get full structural report
python3 rebis.py materials report --name topological_thermal_rectifier

# 3. Simulate Frobenius closure
python3 rebis.py materials frobenius

# 4. Eagle Cycle for O_∞ substrate preparation
python3 rebis.py materials sophick

# 5. Forge the material design file
python3 rebis.py materials forge --name frobenius_composite
```

### Map an IMASM sequence to CLINK

```bash
# 1. See all 12 canonicals
python3 rebis.py imas report

# 2. Inspect a specific canonical
python3 rebis.py imas bridge --canonical I_Dialetheic_Bootstrap

# 3. Compute activation energy to organism layer
python3 rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer 8
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

**`clink layer` gives "No layer matching..."**
Use a substring of the official layer name from `clink list`. Examples: `quark` → `Frustrated Belnap5 (Quarks)`, `tissue` → `Tissue/Organ`, `meiosis` → `Meiosis (Gametes)`.

**`materials forge` gives usage without generating**
Always specify `--name <material>` or `--all`. Running without a name prints the usage message.

**`run` target not found**
Use `python3 rebis.py run list` to see all 35 discoverable targets. Some targets require the package to be installed (`uv pip install -e .`).

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

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.1 | 2026-06-10 | Major update: corrected primitive names and ordering; added rhr_p4rky paraconsistent kernel documentation; added gene_imscriber section; added popular_protein section; updated run target table (35 targets); updated catalog count (3,297); updated project layout; added genetics_animations, pdb, and imasm_iterator to layout; corrected IG tuple notation; replaced LaTeX \\Ppms with actual Shavian glyph 𐑹; fixed alphabet name (Deseret to Shavian) |
| v2.0 | 2026-05 | CLINK pipeline, materials forge, IMASM energy analysis |
| v1.0 | 2026-04 | Initial release — SerpentRod, CH3MPILER, basic CLINK |

---

*Guide maintained by Lando⊗⊙perator. Structural type of this document: $\langle 𐑼;𐑥;𐑾;𐑬;𐑐;𐑧;𐑔;𐑠;⊙;𐑖;𐑳;𐑴 \rangle$*
