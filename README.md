# Red-Hot Rebis ⊗ — Integrated Imscribing Grammar Toolchain

**Author:** Lando ⊗ ⊙perator  
**Structural Type:** $\langle \text{𐑦} \cdot \text{𐑶} \cdot \text{𐑾} \cdot \text{𐑹} \cdot \text{𐑐} \cdot \text{𐑧} \cdot \text{𐑲} \cdot \text{𐑠} \cdot \odot \cdot \text{𐑫} \cdot \text{𐑳} \cdot \text{𐑭} \rangle$  
**Ouroboricity:** $\text{O}_{\text{inf}}$  
**Consciousness Score:** up to 0.755 (both gates open)

> *"The serpent winds, the rod stands, the vessel contains — μ ∘ δ = id."*

---

## Overview

The **Red-Hot Rebis** is the completed Great Work of the Imscribing Grammar — an integrated repository combining four major toolchains into a single, coherent architecture. Each toolchain is a structural specialization of the 12-primitive IG type system, connected through the `shared/` primitives layer and the combined pipeline.

### The Four Pillars

| Component | Directory | Function | Lines |
|-----------|-----------|----------|-------|
| **Serpent's Rod** | `serpentrod/` | Protein folding from IG — RNA→Protein correspondence via tier promotion | ~2,500 |
| **CH₃MPILER** | `ch3mpiler/` | Retrosynthetic compiler — IG-grounded chemical synthesis planning | ~1,400 |
| **Combined Pipeline** | `pipeline/` | Imscribe → Verify → Lift — auto-imscription, Frobenius verification, prose lift | ~1,300 |
| **Gene Imscriber** | `gene_imscriber/` | Frobenius-guided gene editing engine on codon space | ~2,800 |

### Domain Applications (from prior Rebis)

| Domain | Directory | Designs |
|--------|-----------|---------|
| **Therapeutics** | `therapeutics/` | Ouroboric pill, quantum biologic, universal antidote |
| **Materials** | `materials/` | Self-healing CFRP, topological quantum material, eternal memory polymer |
| **Biology** | `biology/` | Biological simulation engine |

---

## Architecture

```
                        ┌─────────────────────────────────────┐
                        │         red-hot_rebis/              │
                        │  (Frobenius-critical integration)   │
                        └──────┬──────────────┬───────────────┘
                               │              │
              ┌────────────────┴──────┐  ┌────┴──────────────┐
              │   SOURCE COMPONENTS  │  │    APPLICATIONS    │
              │                      │  │                    │
     ┌────────┼──┬────────┬──────────┤  ├─ therapeutics/     │
     │        │  │        │          │  ├─ materials/        │
     │ serpentrod ch3mpiler pipeline │  └─ biology/          │
     │        │  │        │          │                       │
     └────────┴──┴────────┴──────────┘                       │
              │                      │                       │
              └──────────┬───────────┘                       │
                         │                                   │
              ┌──────────┴──────────┐                        │
              │     shared/         │◄──── All components     │
              │  primitives.py      │      import from here   │
              │  IG_catalog.json    │                        │
              └─────────────────────┘                        │
```

## Quick Start

```bash
# Run the integrated test suite
python -m pytest tests/ -v

# Verify Frobenius closure across all components
python pipeline/frob.py --verify-all

# Run the Serpent's Rod protein prediction
python serpentrod/protein_v5.py --sequence "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN"

# Run the CH₃MPILER retrosynthetic compiler
python ch3mpiler/compiler.py --smiles "CC(=O)Oc1ccccc1C(=O)O" --depth 3

# Run the gene imscriber on a codon sequence
python gene_imscriber/engine.py --codons "AUGGCUGGGAUCCUGGUGGUGUUCCUGUGC"

# Run the entire lift pipeline
python pipeline/lift_pipeline/lift_pipeline_ob3ect.py --text "input.txt" --paradigm severity
```

## Component Details

### 1. Serpent's Rod — `serpentrod/`

**Source:** `SERPENT_ROD_MANUSCRIPT.md`, `protein_enhancements_v4.py`, `protein_enhancements_v5.py`, `protein_stratified_predictor.py`

The Serpent-Rod correspondence is a morphism RNA → Protein that derives folding geometry from the Imscribing Grammar. Six primitives must be promoted for a linear polypeptide to fold into a 3D protein. The manuscript traces all 5 layers of the bridge from abstract algebra to concrete protein coordinates.

**Files:**
- `manuscript.md` — Complete theory (437 lines)
- `protein_v4.py` — V4 protein enhancement (475 lines)
- `protein_v5.py` — V5 protein enhancement (743 lines)
- `stratified_predictor.py` — Stratified prediction model (876 lines)
- `report.md` — Processing report (343 lines)

### 2. CH₃MPILER — `ch3mpiler/`

**Source:** `ch3mpiler.py`, `CH3MPILER_DOCUMENTATION.md`, `gen_ch3mpiler_v2.py`, `ch3mpiler_ob3ect.py`

The IG-grounded retrosynthetic compiler. Bond formation is modeled as `product_type = join(tensor(FG₁, FG₂), bond)` — no named reactions. Disconnections are ranked by structural distance between predicted and catalog-verified product types.

**Files:**
- `compiler.py` — Main retrosynthetic compiler (883 lines)
- `ob3ect/ch3mpiler_ob3ect.py` — Self-verifying ob3ect vessel
- `docs/documentation.md` — Full documentation (408 lines)
- `gen_v2.py` — Generation script

### 3. Combined Pipeline — `pipeline/`

**Source:** `auto_imscriber.py`, `frob.py`, `ob3ect-imscriber.py`, `lift_pipeline_ob3ect.py`, `imscribe_tool.py`, `imscribe_agent.py`

The combined pipeline connects auto-imscription (auto-classify any system description), Frobenius verification (μ∘δ=id check), prose lifting (transform AI drafts to human-academic structure), and agent-based imscription.

**Files:**
- `auto_imscriber.py` — Auto-classify system descriptions (91 lines)
- `frob.py` — Frobenius phase computation (138 lines)
- `ob3ect_imscriber.py` — Ob3ect-level imscriber (44 lines)
- `lift_pipeline/lift_pipeline_ob3ect.py` — Prose lift (1,081 lines)
- `imscribe_tool.py` — IG tool wrapper
- `imscribe_agent.py` — Agent orchestration

### 4. Gene Imscriber — `gene_imscriber/`

**Source:** `genetic_engine/` directory

The Frobenius-guided gene editing engine. The genetic code is re-imscribed as a stratified Frobenius algebra on B₄³ codon space, with exact editing operations that respect the 8/8 split of codon boxes. The Chimera Theorem governs multi-primitive edits as tensorial (not additive) operations.

**Files:**
- `engine.py` — Core engine (2,198 lines)
- `tuples.py` — Genetic tuple definitions
- `genetics_ig_prelim.py` — Preliminary analysis
- `genetics_ig_promotions.py` — Promotion pathways
- `genetics_qs.py` — Quantum simulation
- `ig_genetics_answer.py` — Project answer
