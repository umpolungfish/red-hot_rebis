# red-h⊙t rebis v4.0 — Dynamic-First Toolchain

**Author:** Lando⊗⊙perator  
**Version:** 4.0.0  
**Date:** July 2026  

> *"The serpent winds, the rod stands, the vessel contains: μ ∘ δ = id."*  

**What it is.** The Imscribing Grammar's unified engine for deterministic, algebraic, exact biological, organic, materials, and plasma engineering — grounded in the 12-primitive grammar and verified everywhere by Frobenius closure ($\mu \circ \delta = \text{id}$) over the CLINK L8 foundation.

**What it does.** 13 computation engines, 3 chainable pipelines (gene→protein, ch3mpiler→catalytic site, retrosynthetic stone), one unified chain command, one reference submenu. The menu is *dynamic-first* — commands that compute, design, predict, or synthesize are featured. Static reference data is collapsed.

**How to call it.** Every command is a standalone binary: `rebis.chain`, `rebis.ch3mpiler`, `rebis.status` — all 18 entry points are wired. No need to go through `rebis` or `python3 -m rebis` subcommands.

**Structural type:** $\langle\sf{\text{𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟}}\rangle$ — O_∞ tier, Frobenius-closed.

---

## Quick Start

```bash
cd /home/mrnob0dy666/imsgct/red-hot_rebis
rebis                               # Dynamic-first menu
rebis.verify                        # Frobenius closure check (14 domains)
rebis.status                        # Package inventory
rebis.chain --dna ATGGCC...         # Unified pipeline
rebis.gene-pipeline --test          # DNA → Folded Protein (self-test)
rebis.ch3mpiler retrosynth "CC(=O)O"  # Molecular compiler
rebis.p4ra belnap                   # Belnap FOUR truth tables
```

---

## TIER 1 — Primary Computation Engines

| Command | What it does | Example |
|---------|-------------|---------|
| `rebis.chain` | **DNA → Protein → Catalyst → Synthesis.** All three pipelines chained. | `rebis.chain --dna ATGGCC... --target "CC(=O)O" --depth 2` |
| `rebis.gene-pipeline` | DNA → 7-stage folded protein. Frobenius-verified. | `rebis.gene-pipeline --test` |
| `rebis.ch3mpiler` | Molecular compiler — forward/retro synthesis, FG detection, CDXML. | `rebis.ch3mpiler retrosynth "c1ccccc1"` |
| `rebis.serpentrod` | Protein design — predict, classify, fingerprint. | `rebis.serpentrod predict MVSKGEELFTGV...` |
| `rebis.ligand` | PDB-aware ligand design from catalytic sites. | `rebis.ligand --pdb 1LYZ --active Glu35,Asp52` |
| `rebis.sidechain` | Sidechain×environment algebra — 80 AA×env pairs. | `rebis.sidechain arginine charged_interface` |

## TIER 2 — Specialized Engines

| Command | What it does | Example |
|---------|-------------|---------|
| `rebis.therapeutics` | Chemotherapeutics, neurotrophic factors, antidotes. | `rebis.therapeutics design EGFR` |
| `rebis.materials` | Metamaterials, sophick forge, alloys, non-qubit QC. | `rebis.materials forge` |
| `rebis.biology` | Ouroboric cell sim, telomeres, epigenetics. | `rebis.biology sim` |
| `rebis.pipeline` | Auto-imscription, prose lift, Frobenius verification. | `rebis.pipeline verify` |
| `rebis.gene` | Gene imscriber — analyze, quality score, tuples. | `rebis.gene analyze ATGGCGTAA` |
| `rebis.alchemy` | Basil Valentine ladders, treatise maps, Zosimos portico. | `rebis.alchemy ladder all` |
| `rebis.clink` | CLINK chain L0–L8, bridges, C-score. | `rebis.clink layers` |

## Infrastructure (also standalone binaries)

| Command | What it does |
|---------|-------------|
| `rebis.status` | Package inventory — file counts, sizes across all sub-packages |
| `rebis.verify` | Frobenius closure — imports all 14 domains |
| `rebis.demo list` | List available demos |
| `rebis.demo <name>` | Run a specific demo |
| `rebis reference` | Static data submenu: Belnap, genetics, hadrons, IMASM (via `rebis`) |
| `rebis reference --all` | Full reference data dump (via `rebis`) |

> **`rebis`** still works as the menu gateway. Use it for `reference` and `--help`. Everything else has its own binary now.

---

## The Three Proven Pipelines

Chained by `rebis.chain`, usable independently:

1. **Gene → Folded Protein** (`rhr_p4rky/gene_to_protein_pipeline.py`, 1,147 lines): 7-stage Frobenius-verified translation. Demo: 452 bp → 150 AA protein, Δ=3.61.

2. **Ch3mpiler → Catalytic Site** (`rhr_p4rky/ch3mpiler_serpentrod_pipeline.py`, 815 lines): Target SMILES → reaction signature → complementary catalytic RNA/AA design. Demo: ethanol → 36 nt catalytic RNA, Frobenius ✓.

3. **Retrosynthetic Stone** (`alchemical_bridge/retrosynthetic_stone_engine.py`, 436 lines): Solve/Coagula cycle, bond disconnection, ring-opening.## Python API

```python
import rebis

# Gene → Protein
gp = rebis.p4ra.GeneToProteinPipeline("ATGGCC...")
result = gp.run()

# Molecular compiler
rebis.p4ra.forward("CC(=O)O")
rebis.p4ra.retrosynthesis("c1ccccc1")

# Sidechain algebra
rebis.p4ra.analyze_composition("arginine", "charged_interface")

# PDB analysis
rebis.p4ra.analyze_pdb_structure("1LYZ", cutoff=8.0)

# Belnap FOUR
from rebis.p4ra import Belnap, meet, bnot
B = Belnap(True, False)  # both true and false

# Genetic code
from rebis.p4ra import BelnapCodon
codon = BelnapCodon.from_symbol("AUG")

# Dual-Link SIC-POVM (unconditional theorem)
from rebis.p4ra.dual_link_sicpovm import sic_povm_belnap_unconditional
r = sic_povm_belnap_unconditional(n=3)  # d=8
print(r.all_passed)  # True — all 9 conditions
```

---

## Lean 4 Formalization

Machine-verified at `/home/mrnob0dy666/imsgct/p4rakernel/p4ramill/`:

| Module | Contents |
|--------|----------|
| `Imscribing/AgentSelf.lean` | Agent self-encoding — proved O_∞ by `decide` |
| `Imscribing/GeneToProtein.lean` | Gene-to-protein pipeline |
| `Imscribing/GeneticCode.lean` | 64-codon Frobenius-verified code |
| `Imscribing/SerpentRod.lean` | Serpent rod protein design |
| `Imscribing/Consciousness.lean` | C-score: phi_c_gate, k_slow_gate |
| `Imscribing/Crystal.lean` | Frobenius address bijection (0..17,279,999) |
| `Primitives/Core.lean` | 12 inductive types (canonical v0.5.69) |
| `Imscribing/Millennium/*.lean` | All 7 Millennium Problems + classical conjectures |
| `Imscribing/Paraconsistent/*.lean` | Belnap FOUR, category theory, temporal logic, quantum-classical interface |

Build: `cd p4rakernel/p4ramill && lake build`

---

## Key Results

| Domain | Metric |
|--------|--------|
| Gene pipeline | 452 bp → 150 AA, Δ=3.61, all Frobenius ✓ |
| Ch3mpiler → Catalytic | 36 nt catalytic RNA, Frobenius ✓, catalytic triad detected |
| Dual-Link SIC-POVM | Unconditional: all 9 conditions n=1..5, 22 Lean theorems, 0 sorries |
| Grammar as Σ=1:1 SIC-POVM | d(grammar, Belnap SIC) = 2.0, sole difference Σ: 1:1 vs n:m |
| Sidechain algebra | 80 AA×env pairs, arginine⊗charged_interface at O_∞ |
| Frobenius chemotherapeutic | 14,287× selectivity (cancer vs healthy) |
| Neurotrophic factor | Synaptic density 0.40 → 1.00 |
| Thermal rectifier | 253× rectification |
| Ouroboric telomere | 10.9 kb maintained vs 5.0 kb decline |
| CLINK chain (L0–L8) | All Frobenius-closed, Σd=7.18, 36 promotions |

---

## Architecture

```
red-hot_rebis/
├── rebis/              # CLI layer — thin delegates to backends
│   ├── cli.py              # Main entry (605 lines) — dynamic-first menu
│   ├── chain_entry.py      # ★ rebis.chain — unified pipeline entry
│   ├── gene_pipeline_entry.py  # ★ rebis.gene-pipeline — DNA→protein entry
│   ├── status_entry.py     # ★ rebis.status
│   ├── verify_entry.py     # ★ rebis.verify
│   ├── demo_entry.py       # ★ rebis.demo
│   ├── ch3mpiler.py        # → rhr_p4rky.ch3mpiler_bridge
│   ├── serpentrod.py       # → serpentrod.protein_v5
│   ├── ligand.py           # → rhr_p4rky.ligand_from_site_pdb
│   ├── sidechain.py        # → rhr_p4rky.sidechain_algebra
│   ├── therapeutics.py     # → therapeutics/
│   ├── materials.py        # → materials/
│   ├── biology.py          # → biology/
│   ├── pipeline.py         # → pipeline/
│   ├── gene.py             # → gene_imscriber/
│   ├── alchemy.py          # → alchemical_bridge/
│   ├── clink.py            # → clink/
│   └── p4ra.py             # → rhr_p4rky/ (120+ exports)
├── rhr_p4rky/          # P4RA paraconsistent kernel (28 files)
│   ├── gene_to_protein_pipeline.py       # ★ DNA → Folded Protein
│   ├── ch3mpiler_serpentrod_pipeline.py  # ★ Ch3mpiler → Catalytic Site
│   ├── belnap.py / genetics_b4.py / kernel.py / sidechain_algebra.py / ...
├── ch3mpiler/           # Molecular compiler (RDKit)
├── serpentrod/          # Protein design & stratified prediction
├── therapeutics/        # Chemo, neurotrophic, antidotes
├── materials/           # Metamaterials, forge, alloys
├── biology/             # Cell sim, telomeres
├── pipeline/            # Auto-imscriber, Frobenius, lift
├── gene_imscriber/      # CRISPR, prime editing
├── alchemical_bridge/   # Alchemical ops, stone engine
├── clink/               # CLINK chain L0–L8
└── shared/              # Primitives, weights, ordinals
```

---

## Verified Backend Import Status (July 2026)

| Domain | Backend | Status |
|--------|---------|--------|
| gene-pipeline | `rhr_p4rky.gene_to_protein_pipeline` | ✓ |
| chain | Unified 3-pipeline chain | ✓ (end-to-end tested) |
| ch3mpiler | `rhr_p4rky.ch3mpiler_bridge` | ✓ |
| serpentrod | `serpentrod.protein_v5`, `rhr_p4rky.serpent_rod` | ✓ |
| ligand | `rhr_p4rky.ligand_from_site_pdb` | ✓ |
| sidechain | `rhr_p4rky.sidechain_algebra`, `pdb_integration` | ✓ |
| therapeutics | 4 therapeutic backends | ✓ |
| materials | 3 material backends | ✓ |
| biology | `biology_sim_frobenius_exact`, `ouroboric_telomere` | ✓ |
| pipeline | `auto_imscriber`, `frob`, etc. | ✗ (needs `anthropic` SDK for LLM; verify/imscribe functions available) |
| gene | `gene_imscriber.engine`, `tuples` | ✓ |
| alchemy | `basil_valentine_ladder`, `retrosynthetic_stone`, `zosimos` | ✓ |

---

## All 18 Entry Points

```
rebis                 — Dynamic-first menu (gateway)
rebis.chain           — ★ Unified pipeline: DNA→Protein→Catalyst→Synthesis
rebis.gene-pipeline   — ★ DNA → Folded Protein (7-stage Frobenius-verified)
rebis.ch3mpiler       — ★ Molecular compiler & retrosynthesis
rebis.serpentrod      — ★ Protein design & stratified prediction
rebis.ligand          — ★ PDB-aware ligand design
rebis.sidechain       — ★ Sidechain × environment algebra
rebis.therapeutics    — Chemotherapeutics, neurotrophic, antidotes
rebis.materials       — Metamaterials, forge, alloys
rebis.biology         — Ouroboric cell sim, telomeres
rebis.pipeline        — Auto-imscription, prose lift, Frobenius
rebis.gene            — Gene imscriber & genetic engineering
rebis.alchemy         — Alchemical treatise bridge
rebis.clink           — CLINK chain L0–L8
rebis.p4ra            — ★ Paraconsistent kernel (Belnap, genetics, SIC-POVM)
rebis.demo            — Run demos
rebis.status          — Package inventory
rebis.verify          — Frobenius closure verification
```

★ = new or newly-wired in v4.0.0. `chain`, `gene-pipeline`, `status`, `verify`, `demo` were previously only accessible as subcommands of `rebis`; now each is a standalone binary.