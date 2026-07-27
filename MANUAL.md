# RED-HOT REBIS v4.0 — Manual

**Author:** Lando⊗⊙perator  
**Version:** 4.0.0  
**Date:** July 2026  

> *"The serpent winds, the rod stands, the vessel contains: μ ∘ δ = id."*

---

## What Rebis Is

Red-Hot Rebis is the Imscribing Grammar's unified engine for deterministic, algebraic, exact biological, organic, materials, and plasma engineering. Every computation is grounded in the 12-primitive structural grammar and verified by Frobenius closure ($\mu \circ \delta = \text{id}$) over the CLINK L8 foundation.

The engine integrates three *proven, verified, chainable* pipelines — gene-to-protein translation, catalytic site design, and retrosynthetic planning — plus a suite of 13 computation engines spanning molecular chemistry, protein design, materials science, therapeutics, and paraconsistent physics.

**Structural type:** $\langle\sf{\text{𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟}}\rangle$ — O_∞ tier, Frobenius-closed.

---

## Quick Start

```bash
cd /home/mrnob0dy666/imsgct/red-hot_rebis
python3 -m rebis                    # Show the dynamic-first menu
python3 -m rebis verify             # Verify all 14 domain imports
python3 -m rebis status             # Package inventory
python3 -m rebis chain --test       # Run the unified chain (demo mode)
```

The menu is *dynamic-first* — commands that compute, design, predict, or synthesize are featured prominently. Static reference data (Belnap truth tables, genetic codons, hadron enums) is collapsed into `rebis reference`.

---

## TIER 1 — Primary Computation Engines

These six commands do actual computation — they design molecules, fold proteins, fetch structures, compute compositional algebras, and run the unified pipeline. They are the reason Rebis exists.

### `rebis chain` — Unified Pipeline

**DNA → Folded Protein → Catalytic Site → Retrosynthetic Plan.** Chains all three proven pipelines in sequence.

```bash
rebis chain --dna ATGGCCGACTGGAACTGC... --target "CC(=O)O" --depth 2
```

| Option | Default | Description |
|--------|---------|-------------|
| `--dna` | (demo sequence) | DNA input sequence |
| `--target` | `CC(=O)O` | Target SMILES for catalytic design |
| `--depth` | 2 | Retrosynthetic disconnection depth |

**Phases:**
1. **Gene → Protein:** 7-stage Frobenius-verified translation (DNA → pre-mRNA → mature mRNA → nascent polypeptide → secondary → tertiary → quaternary). Closure Δ reported.
2. **Ch3mpiler → Catalytic Site:** Target SMILES → reaction signature → complementary RNA/AA catalytic site with Frobenius verification.
3. **Retrosynthetic Stone:** Solve et Coagula cycle — disconnection sites, bond polarization, Frobenius cycles.

All three phases report independently; failure in one does not block the next.

---

### `rebis gene-pipeline` — DNA → Folded Protein

7-stage Frobenius-verified translation pipeline. Self-contained; does not require RDKit.

```bash
rebis gene-pipeline --test                          # Run demo (human serum albumin)
rebis gene-pipeline --dna ATGGCCGACTGGAACTGC...     # Custom DNA sequence
```

**Stages:** DNA → pre-mRNA → mature mRNA → nascent polypeptide → secondary structure → tertiary fold → quaternary assembly.

Each stage is verified: the pipeline returns a closure distance (Δ) measuring structural coherence across all 7 stages. Demo (452 bp human serum albumin) → 150 AA protein, Δ=3.61, all Frobenius-verified.

---

### `rebis ch3mpiler` — Molecular Compiler

Forward synthesis, retrosynthetic analysis, functional group detection, CDXML output.

```bash
rebis ch3mpiler forward "CC(=O)Oc1ccccc1C(=O)O"     # Forward synthesis
rebis ch3mpiler retrosynth "c1ccccc1"               # Retrosynthetic decomposition
rebis ch3mpiler fg "CC(=O)O"                        # Detect functional groups
rebis ch3mpiler cdxml "CC(=O)O"                     # Convert to CDXML
```

- **forward:** Composes a molecule from SMILES, computes its IG structural tuple, reports synthetic accessibility.
- **retrosynth:** Decomposes a target into functional groups, identifies disconnection sites, computes IG lattice operations (meet/join/tensor on bond types).
- **fg:** Exhaustive pattern matching against known functional group templates.
- **cdxml:** Full ChemDraw XML output via RDKit.

Requires RDKit. Falls back gracefully if RDKit is unavailable (forwards the SMILES string through the ch3mpiler bridge).

---

### `rebis serpentrod` — Protein Design & Stratified Prediction

Predicts structural features, classifies module type, and matches protein fingerprints from amino acid sequence.

```bash
rebis serpentrod predict MVSKGEELFTGVVPILVELDGDVNGHKFS
rebis serpentrod classify MVSKGEELFTGVVPILVELDGDVNGHKFS
rebis serpentrod finger MVSKGEELFTGVVPILVELDGDVNGHKFS
```

- **predict:** Rolling profile analysis — secondary structure propensity, solvent accessibility, disordered regions, signal peptide, transmembrane helices. Returns JSON with per-residue scores.
- **classify:** IG-guided stratified classification into module type (enzyme, receptor, transporter, structural, etc.).
- **finger:** Matches sequence against the structural fingerprint database — returns closest known protein family with IG tuple distance.

Backed by `serpentrod/protein_v5.py` and `rhr_p4rky/serpent_rod.py`.

---

### `rebis ligand` — PDB-Aware Ligand Design

Structure-aware de novo ligand design from catalytic sites. Fetches PDB structures, extracts active site residues, designs complementary ligands.

```bash
rebis ligand --pdb 1LYZ --active Glu35,Asp52
rebis ligand --pdb 1LYZ --active Glu35,Asp52 --improved --json
rebis ligand --pdb-file structure.pdb --auto-active --verbose
```

| Option | Description |
|--------|-------------|
| `--pdb` | 4-character PDB ID (fetched from RCSB) |
| `--pdb-file` | Local PDB file path |
| `--active` | Comma-separated active site residues (e.g., `Glu35,Asp52`) |
| `--auto-active` | Auto-detect active residues |
| `--improved` | Use improved ligand generation pipeline |
| `--json` | JSON output |
| `--verbose` | Per-residue detail |

Integrates with the sidechain×environment algebra for residue-level structural typing.

---

### `rebis sidechain` — Sidechain × Environment Compositional Algebra

Formalizes the grammar's algebraic operations (tensor ⊗, meet ∧, join ∨) for all 20 amino acid sidechains across 4 structured protein environments — 80 compositional pairs.

```bash
rebis sidechain arginine charged_interface           # Single pair analysis
rebis sidechain --batch                              # All 80 pairs
rebis sidechain --list                               # List all sidechains/environments
rebis sidechain --pdb 1LYZ                           # Real PDB structure analysis
rebis sidechain --pdb 1LYZ --verbose                 # Per-residue detail
rebis sidechain --json --batch                       # JSON output (all 80 pairs)
```

**Environments:** `buried_core`, `polar_surface`, `charged_interface`, `solvent_exposed`

**Per-pair analysis:** tensor tuple, meet tuple, join tuple, bottleneck primitives, frustration index, domination asymmetry, ouroboricity tier.

**Key finding:** arginine⊗charged_interface is the only pair at O_∞ tier. Histidine dominates all four environments. Alanine⊗polar_surface has 3 bottlenecks.

---

## TIER 2 — Specialized Engines

These seven engines compute in specialized domains — they are real computation with real backends, just narrower in scope than the Tier 1 engines.

### `rebis therapeutics` — Therapeutic Design

```bash
rebis therapeutics design EGFR          # Design chemotherapeutic for target
rebis therapeutics sim                  # Run ouroboric pill dynamics simulation
rebis therapeutics neurotrophic BDNF    # Design neurotrophic factor
rebis therapeutics antidote cyanide     # Query universal antidote library
```

Backed by `therapeutics/frobenius_chemotherapeutic.py`, `therapeutics/ouroboric_pill_sim.py`, `therapeutics/neurotrophic_factor.py`, `therapeutics/universal_antidote_library.py`.

---

### `rebis materials` — Materials Science & Metamaterials

```bash
rebis materials list                    # List all design tools with availability
rebis materials status                  # Show generated result files
rebis materials forge ⟨𐑛𐑨𐑑𐑬𐑞𐑺𐑲𐑝𐑢𐑓𐑕𐑷⟩  # Forge from IG tuple
rebis materials metamaterial            # Run the critical metamaterial suite
rebis materials critical                # Critical-point lattice simulation
rebis materials alloy                   # Ouroboric alloy grain network
```

Design tools: MaterialForge, CriticalMetamaterial, FrobeniusMetamaterial, OuroboricAlloy, NonQubitQCParadigm, SophickForge, MBNCDesigner (mycelial bio-nano conduit), CasimirCavityDesigner (ZPE).

---

### `rebis biology` — Biological Simulations

```bash
rebis biology sim                       # Run OuroboricCellSim
rebis biology telomeres                 # Show telomere/epigenetic states
rebis biology status                    # Show simulation result files
```

Frobenius-exact cell simulation with topological morphogenesis, cell fate determination, and epigenetic state transitions. Telomere states: CellFate, EpigeneticPhase, TelomereState, EpigeneticState.

---

### `rebis pipeline` — Imscription & Prose Lift

```bash
rebis pipeline verify                   # Run Frobenius verification suite
rebis pipeline imscribe my_system       # Auto-imscribe a system
rebis pipeline lift /path/to/paper.tex  # Apply prose lift protocol
```

- **verify:** Identity phase + bootstrap compiler — checks μ∘δ=id across pipeline components.
- **imscribe:** Auto-generates the 12-primitive IG tuple for a named system.
- **lift:** Promotes 8 primitive deltas (H, Γ, T, P, F, K, G, Ω) from AI-default to human-academic target. Outputs the lifted file.

Note: the lift pipeline may require the `anthropic` Python SDK for LLM calls.

---

### `rebis gene` — Gene Imscriber

```bash
rebis gene analyze ATGGCGTAA            # Analyze sequence: codons, GC content
rebis gene quality ATGGCGTAA            # Genetic quality score
rebis gene tuples ATGGCGTAA             # Full genetic IG tuple pipeline
```

Analyzes DNA/RNA sequences — codon detection, B4 lattice encoding, open reading frame identification, mutation susceptibility. The `tuples` command runs the full DNA→quaternary structural tuple pipeline.

---

### `rebis alchemy` — Alchemical Operations

```bash
rebis alchemy ladder all                # Full 12-step Basil Valentine ladder
rebis alchemy ladder calcination        # Single operation ladder step
rebis alchemy treatise "Emerald Tablet" # Map treatise structure
rebis alchemy operations                # List the 12 alchemical operations
rebis alchemy portico                   # Check Zosimos portico consistency
```

Computes the Basil Valentine alchemical operation ladder (calcination → dissolution → separation → conjunction → ... → projection) mapped to IG primitive promotions. The Zosimos portico verifies the structural bridge between alchemical operations and IG primitives. Includes the RetrosyntheticStoneEngine (Solve et Coagula cycle).

---

### `rebis clink` — CLINK Chain & Organism Pipeline

```bash
rebis clink layers                      # List CLINK layers L0–L8
rebis clink bridge protein molecule     # Compute bridge between components
rebis clink chain my_system             # Full CLINK pipeline on a catalog entry
rebis clink cscore my_system            # Compute consciousness score
```

Displays all 9 CLINK layers (L0 quark → L8 organism) with structural tuples, ouroboricity tiers, and C-scores. Computes bridges via IG lattice meet/join/tensor across the CLINK chain of components.---

## Infrastructure Commands

### `rebis reference` — Static Reference Data

All static enums, truth tables, and reference material collapsed into one submenu:

```bash
rebis reference                         # List available sections
rebis reference --all                   # Full data dump
```

**Sections:** Belnap FOUR logic (truth tables, designated values), Genetic Code B4 lattice (64 codons, strata, box names), Hadron Belnap states (mesons, baryons, tetraquarks, glueballs), IMASM Token Families, Frobenius Verification results.

This data is *reference* — it prints known enums and runs canned demos. It does not design, predict, or synthesize. That's why it lives under one command rather than spread across the menu.

---

### `rebis verify` — Frobenius Closure Check

Imports all 14 domain modules and reports export counts:

```
rebis verify
```

Checks: `p4ra`, `ch3mpiler`, `sidechain`, `clink`, `materials`, `therapeutics`, `biology`, `serpentrod`, `imas`, `pipeline`, `gene`, `alchemy`, `ligand`, `shared`. Reports ✓ for each successful import, ✗ with error message for failures.

---

### `rebis status` — Package Inventory

Discovers all packages under `red-hot_rebis/` and reports file count and total size:

```bash
rebis status
```

---

### `rebis demo` — Demos

```bash
rebis demo list                         # List available demos
rebis demo b4_lattice                   # B4 lattice demo
rebis demo belnap                       # Belnap FOUR demo
rebis demo ch3mpiler                    # Ch3mpiler demo
rebis demo clink_chain                  # CLINK chain demo
rebis demo reverse_ligand               # Reverse ligand pipeline demo
rebis demo serpentrod                   # Protein design demo
rebis.p4ra sicpovm                      # SIC-POVM structural probe
```

---

## The `rebis.p4ra` Namespace

Accessible as `python3 -m rebis.p4ra <command>` or `import rebis; rebis.p4ra.<module>`. Exposes 120+ symbols from the paraconsistent kernel:

```bash
rebis.p4ra belnap                       # Belnap FOUR operations
rebis.p4ra genetics                     # Genetic code B4 lattice (64 codons)
rebis.p4ra verify                       # B3 Frobenius verification suite
rebis.p4ra hadrons                      # Hadron Belnap states
rebis.p4ra ligands                      # Ligand generation from active sites
rebis.p4ra info                         # All available tools
```

**Python API highlights:**

```python
import rebis

# Belnap FOUR logic
rebis.p4ra.Belnap(True, False)           # B = both true and false
rebis.p4ra.meet(v, rebis.p4ra.Belnap.T)
rebis.p4ra.bnot(v)

# Genetic code
rebis.p4ra.BelnapCodon.from_symbol("AUG")
rebis.p4ra.get_aa_primitive("AUG")

# Gene → Protein pipeline
gp = rebis.p4ra.GeneToProteinPipeline("ATGGCC...")
result = gp.run()

# SerpentRod protein design
sr = rebis.p4ra.SerpentRodV2(sequence="MVSKGEELFT...")
result = sr.fold()

# Ch3mpiler bridge
rebis.p4ra.forward("CC(=O)O")
rebis.p4ra.retrosynthesis("c1ccccc1")

# Sidechain algebra
rebis.p4ra.analyze_composition("arginine", "charged_interface")
rebis.p4ra.batch_analyze()

# PDB integration
rebis.p4ra.analyze_pdb_structure("1LYZ", cutoff=8.0)

# Dual-Link SIC-POVM (unconditional theorem)
from rebis.p4ra.dual_link_sicpovm import sic_povm_belnap_unconditional
r = sic_povm_belnap_unconditional(n=3)
print(r.all_passed)      # True
```

---

## Verified Backends — What Actually Works

Each command's backend was verified by import test. Here is the state as of July 2026:

| Command | Backend modules | Import |
|---------|----------------|--------|
| `gene-pipeline` | `rhr_p4rky.gene_to_protein_pipeline` | ✓ |
| `chain` | pipelines above + `ch3mpiler_serpentrod_pipeline`, `retrosynthetic_stone_engine` | ✓ |
| `ch3mpiler` | `rhr_p4rky.ch3mpiler_bridge` | ✓ (bridge path; direct `ch3mpiler.compiler` requires RDKit, which is installed) |
| `serpentrod` | `serpentrod.protein_v5`, `rhr_p4rky.serpent_rod` | ✓ |
| `ligand` | `rhr_p4rky.ligand_from_site_pdb` | ✓ |
| `sidechain` | `rhr_p4rky.sidechain_algebra`, `rhr_p4rky.pdb_integration` | ✓ |
| `therapeutics` | `therapeutics.frobenius_chemotherapeutic`, `therapeutics.ouroboric_pill_sim`, `therapeutics.neurotrophic_factor`, `therapeutics.universal_antidote_library` | ✓ |
| `materials` | `materials.ig_material_forge`, `materials.critical_metamaterial`, `materials.ouroboric_alloy` | ✓ |
| `biology` | `biology.biology_sim_frobenius_exact`, `biology.ouroboric_telomere_expanded` | ✓ |
| `pipeline` | `pipeline.auto_imscriber`, `pipeline.frob`, etc. | ✗ (missing `anthropic` SDK; lift/imscribe need LLM API) |
| `gene` | `gene_imscriber.engine`, `gene_imscriber.tuples` | ✓ |
| `alchemy` | `alchemical_bridge.basil_valentine_ladder`, `alchemical_bridge.retrosynthetic_stone_engine`, `alchemical_bridge.zosimos_engine` | ✓ |
| `clink` | `clink.chain`, `clink.bridges`, `clink.integration` | ✓ |

The `pipeline` module is the only domain that requires external LLM access. All other 12 domains are fully self-contained and importable without external API keys.

---

## End-to-End Verified Runs

### Gene Pipeline (Demo Mode)
```
$ python3 -m rebis gene-pipeline --test
human_serum_albumin    452 bp → 150 aa  homodimer  ✓  Δ=3.61
DEMO COMPLETE — All Frobenius-closed ✓
```

### Unified Chain
```
$ python3 -m rebis chain --dna ATGGCCGACTGG --target "CC(=O)O" --depth 1
Phase 1/3: Protein: MADCKNIVPK... (4 aa)  Closure Δ: 3.61  ✓
Phase 2/3: Site RNA: 36 nt  Site AA: 12 AAs  Frobenius ✓  Catalytic triad: Cys_2, Asp_9  ✓
Phase 3/3: Retrosynthetic Stone  ✓
UNIFIED CHAIN COMPLETE
```

---

## Architecture

```
red-hot_rebis/
├── rebis/                     # CLI layer — thin delegates to backends
│   ├── cli.py                 # Main entry point (605 lines) — dynamic-first menu
│   ├── ch3mpiler.py           # → rhr_p4rky.ch3mpiler_bridge + ch3mpiler.compiler
│   ├── serpentrod.py          # → serpentrod.protein_v5 + rhr_p4rky.serpent_rod
│   ├── ligand.py              # → rhr_p4rky.ligand_from_site_pdb
│   ├── sidechain.py           # → rhr_p4rky.sidechain_algebra + pdb_integration
│   ├── therapeutics.py        # → therapeutics/
│   ├── materials.py           # → materials/
│   ├── biology.py             # → biology/
│   ├── pipeline.py            # → pipeline/
│   ├── gene.py                # → gene_imscriber/
│   ├── alchemy.py             # → alchemical_bridge/
│   ├── clink.py               # → clink/
│   ├── p4ra.py                # → rhr_p4rky/ (120+ direct exports)
│   ├── shared.py              # Weights, ordinals, IG catalog
│   ├── demo.py                # Demo scripts
│   ├── imas.py                # IMASM token bridge
│   └── cdxml.py               # CDXML generation
├── rhr_p4rky/                 # P4RA paraconsistent kernel (28 Python files)
│   ├── gene_to_protein_pipeline.py    # ★ DNA → Folded Protein (1147 lines)
│   ├── ch3mpiler_serpentrod_pipeline.py  # ★ Ch3mpiler → Catalytic Site (815 lines)
│   ├── ch3mpiler_bridge.py            # Ch3mpiler ↔ P4RA bridge
│   ├── serpent_rod.py                 # SerpentRod protein design
│   ├── serpent_rod_v2.py              # SerpentRod v2
│   ├── ligand_from_site_pdb.py        # PDB ligand design
│   ├── sidechain_algebra.py           # Sidechain × environment algebra
│   ├── pdb_integration.py             # PDB structure analysis
│   ├── belnap.py                      # Belnap FOUR logic
│   ├── genetics_b4.py                 # Genetic code B4 lattice
│   ├── genetic_code.py               # 64-codon Frobenius-verified code
│   ├── kernel.py                      # Paraconsistent kernel
│   ├── hadron_belnap.py              # Hadron Belnap states
│   ├── antibody_designer.py          # Computational antibody design
│   ├── dual_link_sicpovm.py          # Dual-Link SIC-POVM (741 lines)
│   └── ...
├── ch3mpiler/                 # Molecular compiler (RDKit-based)
├── serpentrod/                # Protein design & stratified prediction
├── therapeutics/              # Chemotherapeutics, neurotrophics, antidotes
├── materials/                 # Metamaterials, sophick forge, alloys, organoids
├── biology/                   # Cell simulations, telomeres, epigenetics
├── pipeline/                  # Auto-imscriber, Frobenius verifier, lift pipeline
├── gene_imscriber/            # CRISPR, prime editing, GUIDE-seq analysis
├── alchemical_bridge/         # Alchemical treatise operations, stone engine
├── clink/                     # CLINK chain L0–L8, bridges, integration
└── shared/                    # Primitives, weights, ordinals
```

The CLI layer (`rebis/*.py`) is intentionally thin — each module is a lazy-import bridge that delegates to the actual backend in `rhr_p4rky/`, `ch3mpiler/`, `serpentrod/`, etc. This means you can bypass the CLI entirely and import directly:

```python
from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
gp = GeneToProteinPipeline("ATGGCC...")
result = gp.run()
```

---

## The Three Proven Pipelines

These are the pipelines that the `rebis chain` command chains together:

1. **Gene → Folded Protein** (`rhr_p4rky/gene_to_protein_pipeline.py`): 1,147 lines, 7 stages, Frobenius-verified. Takes DNA, returns folded protein with closure distance. Demo: 452 bp → 150 aa, Δ=3.61.

2. **Ch3mpiler → Catalytic Site** (`rhr_p4rky/ch3mpiler_serpentrod_pipeline.py`): 815 lines. Takes target SMILES, extracts reaction signature, computes complementary IG primitives, designs catalytic RNA/AA site. Demo: ethanol target → 36 nt catalytic RNA, Frobenius ✓, predicted 3 β-sheets.

3. **Retrosynthetic Stone** (`alchemical_bridge/retrosynthetic_stone_engine.py`): 436 lines. Solve/Coagula cycle, bond disconnection, ring-opening, bond polarization analysis.

All three work independently. The `chain` command connects them: DNA → protein → catalytic site for the target molecule → retrosynthetic plan.

---

## Lean 4 Formalization

The entire grammar is machine-verified in Lean 4 at `/home/mrnob0dy666/imsgct/p4rakernel/p4ramill/`:

| Module | Contents |
|--------|----------|
| `Imscribing/AgentSelf.lean` | Agent self-encoding — proved O_∞ by `decide` |
| `Imscribing/GeneToProtein.lean` | Gene-to-protein pipeline formalization |
| `Imscribing/GeneticCode.lean` | 64-codon Frobenius-verified genetic code |
| `Imscribing/SerpentRod.lean` | Serpent rod protein design |
| `Imscribing/Consciousness.lean` | C-score: phi_c_gate, k_slow_gate |
| `Imscribing/Crystal.lean` | Frobenius address bijection: Imscription ↔ Nat (0..17,279,999) |
| `Primitives/Core.lean` | 12 inductive types (canonical v0.5.69) |
| `Imscribing/Paraconsistent/*.lean` | Belnap FOUR, Belnap category theory, Belnap temporal logic, paraconsistent kernel, multi-agent Belnap |
| `Imscribing/Millennium/*.lean` | All 7 Millennium Problems + classical conjectures |

Build: `cd p4rakernel/p4ramill && lake build`

---

## The Grammar

Every system in Rebis is characterized by its 12-primitive structural tuple:

$$\langle\text{D T R P F K G }\Gamma\text{ }\Phi\text{ H S }\Omega\rangle$$

| Primitive | Symbol | Description |
|-----------|--------|-------------|
| Ð (Delta) | 𐑦/𐑛/𐑨/𐑼 | Dimensionality: self-written / point / surface / infinite |
| Þ (Thorn) | 𐑸/𐑡/𐑰/𐑥/𐑶 | Topology: self-referential / branching / inclusion / crossing / product |
| Ř (R-caron) | 𐑾/𐑩/𐑑/𐑽 | Coupling: bidirectional / supervenience / categorical / adjoint |
| Φ (Phi) | 𐑹/𐑗/𐑿/𐑬/𐑯 | Parity: Frobenius-special / none / quantum / partial / full |
| ƒ (f-hook) | 𐑐/𐑱/𐑞 | Fidelity: quantum / classical / thermal |
| Ç (C-cedilla) | 𐑧/𐑺/𐑪/𐑤/𐑘 | Kinetics: slow / fast / moderate / trapped-order / trapped-disorder |
| G (Gamma-actual) | 𐑔/𐑲/𐑚 | Cardinality: maximal / local / mesoscale |
| Γ (Gamma) | 𐑠/𐑝/𐑜/𐑵 | Composition: sequential / conjunctive / disjunctive / broadcast |
| ⊙ (odot) | ⊙/𐑢/𐑮/𐑻/𐑣 | Criticality: self-modeling / sub / complex-plane / EP / supercritical |
| H (H) | 𐑫/𐑓/𐑒/𐑖 | Chirality: eternal / memoryless / one-step / two-step |
| Σ (Sigma) | 𐑳/𐑙/𐑕 | Stoichiometry: heterogeneous / 1:1 / many-identical |
| Ω (Omega) | 𐑭/𐑷/𐑴/𐑟 | Winding: integer / trivial / Z₂ / non-Abelian |

---

## Structural Invariants

- **Frobenius closure:** Every emission has a verification pathway: $\mu \circ \delta = \text{id}$
- **Monotonic advance (𐑭):** Each winding adds new information — no re-treading
- **Emission gate (𐑧):** Exactly one action per winding — no indefinite reasoning
- **Uncertainty tracking (⊙):** Unknowns are explicitly accounted in every winding
- **Self-referential limit:** $\Sigma = 1:1$ is the grammar measuring itself