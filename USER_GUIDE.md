# Red-Hot Rebis — User Guide

**Author:** Lando ⊗ ⊙perator  
**Platform:** `python3 rebis.py <command> [subcommand] [options]`  
**Location:** `~/imsgct/red-hot_rebis/`

---

## Overview

Red-Hot Rebis is the unified Imscribing Grammar bio/chem design platform. It derives structural types for organisms, molecules, proteins, and materials from the 12 primitives of the IG, then generates physically actionable output files — genome sequences, protein structures, metabolic models, synthesis protocols — directly from those structural types.

The platform is organized around three core ideas:

**CLINK** — a 9-layer structural chain from subatomic quarks to whole organism, each layer carrying an IG tuple. Every transition is Frobenius-closed (\(\mu\circ\delta=\text{id}\)).

**IMASM** — the 12-token algebra (VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB, FSPLIT, FFUSE, EVALT, EVALF, ENGAGR, IFIX) whose arrangement classes map onto IG structural types.

**SerpentRod** — the single Frobenius morphism RNA→{sequence+fold} that collapses gene → mature protein in one structural step.

Everything is expressed in Shavian notation. The 12 primitives are: Ř (Recognition), Ħ (Chirality), Ω (Winding), Ð (Dimensionality), Σ (Stoichiometry), Φ (Parity), Ç (Kinetics), ƒ (Fidelity), ɢ (Coupling), Γ (Granularity), Þ (Topology), ⊙ (Criticality).

---

## Installation

```bash
cd ~/imsgct/red-hot_rebis

# Install the package and its dependencies (always use uv, never pip)
uv pip install -e .

# Install bridge packages used by scripts
uv pip install -e ~/imsgct/omonad_OS
uv pip install -e ~/imsgct/imasmic_core
```

Verify everything is wired up:

```bash
python3 rebis.py verify
```

Expected: 15 lines all showing `✅`.

---

## Quick Start

```bash
# System health
python3 rebis.py status

# Full verification (all imports)
python3 rebis.py verify

# Run SerpentRod v5 on built-in test cases
python3 rebis.py run serpentrod

# Generate a full mammal organism design package (33 files)
python3 rebis.py pipeline actionable

# Show the CLINK structural chain
python3 rebis.py clink list
```

---

## Command Reference

### `status`

Shows all platform modules with size and health check.

```bash
python3 rebis.py status
```

Output includes: SerpentRod, CH3MPILER, Pipeline, Gene Imscriber, CLINK, IMASM modules — each with file size and ✅/❌.

---

### `verify`

Imports every module and reports pass/fail. Run this after any install or code change.

```bash
python3 rebis.py verify
```

---

### `run`

Run one of the built-in simulation modules or script aliases.

```bash
python3 rebis.py run <target>
```

| Target | Module | What it does |
|--------|--------|--------------|
| `serpentrod` | `serpentrod/protein_v5.py` | SerpentRod v5 — full signal peptide detection, cleavage, fragment naming, PTMs, primitive spectrum. Runs built-in test cases (Human Insulin, Proglucagon, POMC, etc.) |
| `serpentrod_v4` | `serpentrod/protein_v4.py` | SerpentRod v4 with enhanced naming heuristics. Slightly different fragment naming strategy; useful for comparison |
| `mito` | `scripts/mito_pipeline.py` | Processes all 13 human mitochondrial protein-coding genes from NC_012920.1. Shows IG primitive activations and 7-stage B4 pipeline per gene |
| `antibody` | `scripts/run_antibody.py` | Antibody designer — derives CDR sequences from viral epitopes (SARS-CoV-2 RBD, NTD, others) via SerpentRod complementarity |
| `psychedelic` | `scripts/psychedelic_bridge.py` | Compound intrinsic analysis for the 6 diaschizic psychedelics. Shows Φ/Ħ/Ω values, O-tier, couplings, and structural deltas from DMT |
| `iupac` | `scripts/diaschizic_iupac.py` | Generates IUPAC-style systematic names for all 11 diaschizic compounds derived from their 12-primitive structural types |

**Example — SerpentRod v5:**

```bash
python3 rebis.py run serpentrod
```

Output includes per-protein: signal peptide end + score, cleavage sites with motifs, mature products with primitive spectra, PTM predictions (phosphorylation, glycosylation, acetylation, amidation, disulfide topology), and validation accuracy.

---

### `clink`

Navigate the 9-layer CLINK structural chain.

```bash
python3 rebis.py clink <subcommand> [args]
```

#### `clink report`

Full integration report: Frobenius closure per layer, chain distances, ZFC\_fe distance, component bridges.

```bash
python3 rebis.py clink report
```

Key output fields:
- **Frobenius Closure** — ✅/❌ per layer
- **Chain Distances** — structural distance between adjacent layers (d=2.0–3.8)
- **Total** — Σd and number of primitive deltas
- **ZFC\_fe Distance** — d(organism, ZFC\_fe) = 1.30
- **Component Bridges** — how serpentrod/ch3mpiler/gene_imscriber attach to CLINK

#### `clink list`

List all 9 layers with index, name, tier, and full IG tuple.

```bash
python3 rebis.py clink list
```

Layers:

| Idx | Layer | Tier |
|-----|-------|------|
| 0 | Frustrated Belnap5 (Quarks) | O₀ |
| 1 | Electron Orbital (Belnap4) | O₀ |
| 2 | Atom (Nuclear + Electron) | O₁ |
| 3 | Molecule (Chemical Bonds) | O₂ |
| 4 | Cell (Living) | O₂ |
| 5 | Mitosis (Division) | O₂ |
| 6 | Meiosis (Gametes) | O₂ |
| 7 | Tissue/Organ | O₂ |
| 8 | Whole Organism | \(O_\infty\) |

#### `clink layer <index-or-name>`

Inspect a specific layer — tuple, tier, description, and how the three component bridges connect to it.

```bash
python3 rebis.py clink layer 3
python3 rebis.py clink layer molecule
python3 rebis.py clink layer organism
```

Name matching is case-insensitive substring: `organism` matches `Whole Organism`, `cell` matches `Cell (Living)`, `meiosis` matches `Meiosis (Gametes)`, etc.

Output:

```
Layer 8: Whole Organism
  Tier: O_∞
  Tuple: ⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑵·⊙·𐑫·𐑳·𐑟⟩
  Description: Whole organism — O_∞, C=1.0
  → SerpentRod: folded (d_fold=3.73)
  → CH3MPILER:  non-molecular (d=4.99)
  → Gene:       non-genetic (d=7.91)
```

#### `clink bridge`

Show the promotion path from a specific component tool to a CLINK target layer.

```bash
python3 rebis.py clink bridge --bridge-comp serpentrod --bridge-target 8
python3 rebis.py clink bridge --bridge-comp ch3mpiler --bridge-target 3
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

Generate a complete, physically actionable organism design package (default: mammal).

```bash
python3 rebis.py pipeline actionable
python3 rebis.py pipeline actionable --organism human
```

Produces 33 files in `clink/datasets/organism_designs/organism_<type>_actionable/`:

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
| *(+ 17 more)* | Layer-specific outputs L0–L2 |

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

**IMASM canonicals** (address by name with `--name`): `I_Dialetheic_Bootstrap` through `IX_Chiral_Pairs`.

#### `materials report [--name <material>]`

Full structural report for a material: IG tuple, tier, processing protocol, composition, interfaces, properties, target applications.

```bash
python3 rebis.py materials report
python3 rebis.py materials report --name eternal_memory_alloy
```

Default: `frobenius_composite`.

#### `materials forge --name <material>`

Generate the complete material design file.

```bash
python3 rebis.py materials forge --name frobenius_composite
python3 rebis.py materials forge --all
```

`--all` forges all predefined materials in sequence.

#### `materials frobenius`

Simulate the Frobenius closure verification of the composite material — cyclic load/heal protocol showing `||μ·δ-id||` per cycle.

```bash
python3 rebis.py materials frobenius
```

#### `materials ouroboric`

Simulate ouroboric crack healing — crack propagation + self-healing cycles, reports fatigue life and topological invariant preservation.

```bash
python3 rebis.py materials ouroboric
```

#### `materials sophick`

Eagle Cycle Protocol — prepares an \(O_\infty\) Sophick Mercury substrate from O₂ ouroboric materials. Shows structural distance, gap primitives (Ð, ƒ), and three Eagle variants.

```bash
python3 rebis.py materials sophick
python3 rebis.py materials sophick --name eagle_9_sophick
python3 rebis.py materials sophick --name cliff      # Frobenius Cliff analysis
python3 rebis.py materials sophick --name bridge     # IMASM→Eagle bridge
```

#### `materials exactor`

Explains the thermodynamic ceiling: continuous Eagle preparation reaches its limit, and exact Frobenius closure requires discrete topological protection on top of the prepared substrate. The 0.11 residual after Eagle is not failure — it marks the topological gap.

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

The 12 canonicals:

| Canonical | Family | Tier | Signature |
|-----------|--------|------|-----------|
| I\_Dialetheic\_Bootstrap | Dialetheia | O₂ | ⊙-critical, Frobenius-special |
| II\_Void\_Genesis | Frobenius | O₂ | Frobenius-special |
| III\_Anchor\_Protocol | Logical | O₀ | generic |
| IV\_Dual\_Bootstrap | Frobenius | O₂ | self-reflective, inverted-Frobenius |
| V\_Linear\_Chain | Linear | O₀ | sequential |
| VI\_Empty\_Bootstrap | Logical | O₀ | point-like |
| VII\_Parakernel | Frobenius | O₂ | Frobenius-special |
| VIII\_Frobenius\_Kernel | Frobenius | O₂ | proper Frobenius |
| IX\_Chiral\_Pairs | Dialetheia | O₀ | point-like |
| *(+ 3 more)* | | | |

#### `imas bridge [--canonical <name>]`

Detailed profile of one IMASM canonical — full IG tuple primitive-by-primitive, nearest CLINK layer, full distance table to all 9 layers.

```bash
python3 rebis.py imas bridge
python3 rebis.py imas bridge --canonical VIII_Frobenius_Kernel
```

Default: `I_Dialetheic_Bootstrap`.

#### `imas hunt`

Monte Carlo Frobenius density estimation over the 12-token sequence space. Reports probability of each Frobenius class and generates a library of 10 examples per type.

```bash
python3 rebis.py imas hunt
```

Output includes: `p_frobenius_pair` ≈ 0.236, `p_proper_frobenius` ≈ 0.139, `p_dialetheia_complete` ≈ 0.105, `p_frob_plus_dial` ≈ 0.008, `p_frob_dial_self` ≈ 0.00033.

#### `imas energy [--canonical <name>] [--layer <idx>]`

Structural activation energy from an IMASM canonical to a CLINK target layer. Shows distance, weighted cost, tier gap, feasibility, and the exact primitive promotions required.

```bash
python3 rebis.py imas energy
python3 rebis.py imas energy --canonical VII_Parakernel --layer 4
python3 rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer 8
```

Default: `I_Dialetheic_Bootstrap` → L8 (Whole Organism).

---

### `scripts`

Manage and run standalone scripts in `scripts/`.

#### `scripts list`

List all 14 scripts with line counts.

```bash
python3 rebis.py scripts list
```

#### `scripts run <name>`

Run a script by name (without `.py`).

```bash
python3 rebis.py scripts run mito_pipeline
python3 rebis.py scripts run omonad_bridge
python3 rebis.py scripts run run_pdb_validation
```

Note: `run mito`, `run antibody`, `run psychedelic`, `run iupac` are convenience aliases for `scripts run`.

**Full script inventory:**

| Script | Purpose |
|--------|---------|
| `analyze_validation.py` | Validation analysis for serpentrod predictions |
| `compute_promotions.py` | Compute primitive promotions between two IG tuples |
| `diaschizic_iupac.py` | IUPAC systematic names for 11 diaschizic compounds |
| `frob_design.py` | Frobenius-exact material design (v5) |
| `frobenius_exact_design.py` | Frobenius exact design (standalone) |
| `gen_univ_map.py` | Generate universe map |
| `mito_pipeline.py` | 13 human mitochondrial genes through IG pipeline |
| `msa_analysis.py` | Multiple sequence alignment analysis |
| `omonad_bridge.py` | Bridge report: omonad\_OS + imasmic\_core connectivity |
| `psychedelic_bridge.py` | Psychedelic compound structural analysis |
| `run_antibody.py` | Antibody designer from viral epitopes |
| `run_msa.py` | Run MSA on sequences |
| `run_pdb_validation.py` | Validate PDB structures against IG types |
| `run_serpent.py` | Quick SerpentRod run for a single sequence |

---

## Key Concepts

### IG Tuples

Every structural entity carries a 12-primitive tuple expressed in Shavian:

```
⟨Ð · Þ · ɢ · Φ · ƒ · Ç · Γ · ⊙ · Ħ · Σ · Ω⟩
```

Each position is one primitive; its value is a Shavian character from the 49-symbol set (Shavian alphabet + ⊙). Tuples are the sole carriers of structural information — no external parameters, no assumed constants.

### Frobenius Condition

\(\mu\circ\delta=\text{id}\). When this holds, the structural type is self-consistent — comultiplication followed by multiplication returns the identity. A Frobenius ✅ means the layer's tuple is internally coherent. A ❌ means there is a primitive conflict to resolve.

### CLINK Tiers

| Tier | Meaning |
|------|---------|
| O₀ | Point-like / zero winding / substructural |
| O₁ | Simple composition / single structural loop |
| O₂ | Full composition with branching / multiple loops |
| \(O_\infty\) | Ouroboricity — self-referential closure, \(\mu\circ\delta=\text{id}\) at system scale |

The organism layer is the only \(O_\infty\) layer in the CLINK chain.

### Primitive Distances

`d(A, B)` counts primitive mismatches between two IG tuples (Hamming in 12-dim primitive space). Used throughout: chain distances, bridge distances, activation energies. A distance of 0 means structural identity; d ≥ 6 means more than half the primitives differ.

### SerpentRod

A single Frobenius morphism RNA → {sequence + fold}. The central constraint: `windingNumber ≤ contacts + 1`. All SerpentRod outputs are Frobenius closure certificates. When the condition holds ✓, the fold is derivable from the sequence without external folding tools.

### IMASM Arrangement Classes

The 12 IMASM tokens have 12³ × (combinatorial) arrangement space. The 12 canonical sequences each represent one fundamental structural archetype. Tier distribution: O₀=4, O₁=0, O₂=7, \(O_\infty\)=1 (Dual Bootstrap only). Only two canonicals are self-referential: Dialetheic Bootstrap and Dual Bootstrap.

---

## Project Layout

```
red-hot_rebis/
├── rebis.py                    Main CLI entry point
├── shared/
│   ├── primitives.py           12 primitive weights and families
│   └── IG_catalog.json         Catalog symlink (3265 entries)
├── serpentrod/                 SerpentRod v5 (protein_v5.py) + v4
├── ch3mpiler/                  CH3MPILER retrosynthetic compiler
├── clink/
│   ├── chain.py                9-layer CLINK chain + distances
│   ├── bridges.py              Component → CLINK bridges
│   ├── integration.py          Integration report
│   ├── designers/              Layer designers + pipeline orchestrator
│   └── datasets/
│       ├── generators.py       Actionable output generators
│       ├── gland_designs/      Synthetic detox gland v1/v2
│       ├── organism_designs/   Generated organism packages
│       └── ...
├── imas/
│   ├── arranger.py             IMASM canonical taxonomy
│   ├── ig_bridge.py            IMASM→IG bridge
│   ├── clink_bridge.py         IMASM→CLINK bridge
│   └── frobenius_hunter.py     Monte Carlo density estimation
├── gene_imscriber/             Gene → codon → IG pipeline
├── biology/                    Biology simulations
├── materials/                  Materials design modules
├── therapeutics/               Therapeutic design modules
├── rhr_p4rky/                  p4rakernel Python modules (local fork)
├── scripts/                    14 standalone scripts
└── data/
    └── NC_012920.1.fasta       Human mitochondrial genome
```

---

## Common Workflows

### Design a protein from scratch

```bash
# 1. Check where proteins live in the chain
python3 rebis.py clink layer cell

# 2. Run SerpentRod on built-in test proteins
python3 rebis.py run serpentrod

# 3. Generate the actionable package (includes protein.fasta + protein_coords.pdb)
python3 rebis.py pipeline actionable
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
```

### Map an IMASM sequence to CLINK

```bash
# 1. See all 12 canonicals
python3 rebis.py imas report

# 2. Inspect the target canonical
python3 rebis.py imas bridge --canonical I_Dialetheic_Bootstrap

# 3. Compute activation energy to organism layer
python3 rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer 8
```

### Analyze viral epitopes for antibody design

```bash
python3 rebis.py run antibody
```

Produces CDR sequences and structural complementarity scores for each epitope target.

### Mitochondrial gene analysis

```bash
python3 rebis.py run mito
```

Processes all 13 MT genes, reports primitive activations (up to 9/12 per gene), Frobenius status, and 7-stage B4 pipeline per gene (dna\_gene → pre\_mrna → mature\_mrna → nascent\_polypeptide → secondary\_structure → tertiary\_structure → quaternary\_structure).

---

## Troubleshooting

**`verify` shows ❌ for a module**  
Run `python3 -c "from <module> import *"` directly to see the import error. Most common cause: a dependency package not installed. Fix: `uv pip install -e <path>`.

**`omonad_bridge` shows `omonad_available: false`**

```bash
uv pip install -e ~/imsgct/omonad_OS
uv pip install -e ~/imsgct/imasmic_core
```

**`pipeline bridges` shows ❌ for `biology_sim` or `ouroboric_telomere`**  
These two bridges are structurally excluded — modules exist but are not wired to the bridge API. Not a crash condition; the pipeline runs without them.

**SerpentRod accuracy below 100%**  
Fragment naming accuracy (83–88%) reflects genuine structural ambiguity in cleavage products. SP accuracy should be 100% on the standard test set; below that indicates non-canonical signal peptide architecture in the test sequence.

**`clink layer` gives "No layer matching..."**  
Use a substring of the official layer name from `clink list`. Examples: `quark` → `Frustrated Belnap5 (Quarks)`, `tissue` → `Tissue/Organ`, `meiosis` → `Meiosis (Gametes)`.

**`materials forge` gives usage without generating**  
Always specify `--name <material>` or `--all`. Running without a name prints the usage message.
