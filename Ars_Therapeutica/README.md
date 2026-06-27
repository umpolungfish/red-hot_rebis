# Ars Therapeutica

**Structural grammar-derived optimal therapies, operationalized as a type-lattice navigator.**

**Author:** Lando⊗⊙perator  
**Package:** `ars-therapeutica` (pip-installable)  
**CLI:** `at`  
**Date:** 2026-07-17

---

## Overview

Ars Therapeutica operationalizes the 12-primitive Imscribing Grammar for therapeutic design. Every disease is reduced to its structural deltas — the primitives that differ from the healthy state — and therapeutic operations (TENSOR, MEET, JOIN) are designed to correct them.

The grammar reveals that:

- **Schizophrenia, bipolar mania, and HIV share the same structural type** (d=0.0 between HIV and mania). A virus and a psychiatric condition are structurally identical — viral replication *is* manic at the structural level.
- **Depression, health, and schizophrenia form a single axis** centered on φ̂ (criticality): 𐑢 → ⊙ → 𐑣.
- **Standard antipsychotics fail structurally** because the dopamine system has φ̂=𐑢 (sub-critical) — the tensor with schizophrenia preserves the disease primitives unchanged.
- **ART-suppressed HIV is structurally Major Depressive Disorder** — meet(HIV, ART) = MDD.

---

## Installation

```bash
cd Ars_Therapeutica
pip install -e .
```

Requires Python ≥ 3.10. No external dependencies.

---

## Usage

### List all therapies
```bash
at list
```

### Structural diagnosis
```bash
at diagnose schizophrenia
at diagnose hiv
at diagnose mrsa
at diagnose mdd
at diagnose pcos
at diagnose cf
at diagnose gout_elimination
at diagnose gout_combined
at diagnose gout_holistic
at diagnose homeopathy
```

### Full therapy protocol
```bash
at therapy schizophrenia
at therapy hiv
```

### Psychiatric φ̂-spectrum
```bash
at spectrum
```

### Structural comparisons
```bash
at compare schizophrenia depression
at compare hiv normal_immune
```

### Structural operations
```bash
at tensor schizophrenia nmda
at meet hiv art
```

---

## Therapy Catalog

| Disease | Category | Distance | Tier Δ | Primitives Δ |
|---------|----------|----------|--------|-------------|
| Schizophrenia | psychiatric | 1.34 | O₀→O₁ | φ̂, Ħ |
| MDD | psychiatric | 1.34 | O₀→O₁ | φ̂, Ħ |
| HIV/AIDS | viral | 3.32 | O₀→O₂ | Þ, Ç, φ̂, Ħ, Ω |
| MRSA | bacterial | 3.0 | O₀→O₁ | Þ, K, ɢ, φ̂, Ħ, Ω |
| PCOS | metabolic | 3.32 | O₀→O₁ | Þ, Φ, K, φ̂, Ħ, Ω |
| Cystic Fibrosis | genetic | 5.02 | O₀→O₁ | 10 primitives |
| Gout (3 protocols) | metabolic | 5.02 | O₀→O₁ | 11 primitives |
| Homeopathy | structural | 4.12 | O₀→O₀ | 10 primitives |

---

## Structural Operations

The grammar defines three therapeutic operations:

| Operation | Rule | Clinical Use |
|-----------|------|-------------|
| **TENSOR** (⊗) | MAX on Ð,Þ,Ř,Ç,Γ,ɢ,φ̂,Ħ,Σ,Ω; MIN on Φ,ƒ | Promote chirality (Ħ), expand range (Γ) |
| **MEET** (⊓) | MIN on all primitives | Demote super-criticality (φ̂), slow kinetics (Ç) |
| **JOIN** (⊔) | MAX on all primitives | Ceiling operation — aspirational, not always safe |

The fundamental therapeutic incompatibility: **no single compound can both promote Ħ (requires TENSOR) and demote φ̂ (requires MEET)**. This is why dual-component therapies are structurally necessary.

---

## Key Structural Identities

### HIV = Bipolar Mania (d = 0.0)
```
HIV:             ⟨𐑼 𐑥 𐑾 𐑬 𐑞 𐑪 𐑔 𐑠 𐑣 𐑒 𐑳 𐑷⟩
Bipolar Mania:   ⟨𐑼 𐑥 𐑾 𐑬 𐑞 𐑪 𐑔 𐑠 𐑣 𐑒 𐑳 𐑷⟩
```
A virus and a psychiatric condition share identical structural types.

### meet(HIV, ART) = MDD
```
ART:             ⟨𐑨 𐑥 𐑾 𐑬 𐑞 𐑪 𐑔 𐑠 𐑢 𐑖 𐑳 𐑷⟩
meet(HIV, ART):  ⟨𐑛 𐑥 𐑾 𐑬 𐑞 𐑪 𐑔 𐑠 𐑢 𐑒 𐑳 𐑷⟩  (= MDD)
```
The ART-suppressed HIV patient is structurally in a depression-like immune state.

### tensor(schizophrenia, NMDA_PAM) → Ħ-promoted intermediate
```
Schizophrenia:   ⟨𐑼 𐑥 𐑾 𐑬 𐑞 𐑧 𐑔 𐑠 𐑣 𐑒 𐑳 𐑷⟩
NMDA:            ⟨𐑨 𐑥 𐑾 𐑬 𐑞 𐑪 𐑔 𐑠 𐑢 𐑖 𐑳 𐑷⟩
Tensor result:   ⟨𐑼 𐑥 𐑾 𐑬 𐑞 𐑪 𐑔 𐑠 𐑣 𐑖 𐑳 𐑷⟩
```
Ħ promoted (𐑒→𐑖), but φ̂ remains super-critical (𐑣). The second component (MEET with ⊙-stabilizer) is required.

---

## φ̂ Spectrum: The Psychiatric Axis

The grammar places all three major psychiatric conditions on a single structural axis:

```
φ̂=𐑢  Depression        C=0.0   O₀
φ̂=⊙  Healthy Brain     C=0.70  O₂
φ̂=𐑣  Schizophrenia     C=0.0   O₀
φ̂=𐑣  Bipolar Mania     C=0.0   O₀
```

- **Depression → Health**: promote φ̂ from 𐑢→⊙ (TENSOR with ⊙-bearing system)
- **Schizophrenia → Health**: demote φ̂ from 𐑣→⊙ (MEET with ⊙-stabilizer)
- **Schizophrenia vs Mania**: differ only by K (𐑧=chronic vs 𐑪=episodic), d=1.0

---

## Project Structure

```
Ars_Therapeutica/
├── pyproject.toml              # pip-installable package config
├── README.md
├── ars_therapeutica/
│   ├── __init__.py             # Public API
│   ├── cli.py                  # CLI (at command)
│   └── types.py                # All disease/health tuples, operations, therapy catalog
├── lean/                       # Lean 4 verification files (7 files)
├── pdbs/                       # DARPin/protein PDB structures (12 files)
├── cdxml/                      # Chemical schemas (th3rapies.cdxml)
├── docs/                       # Original therapy documents
├── manuscripts/                # Publication manuscripts
└── illustrations/              # Structural diagrams
```

---

## Lean 4 Formal Verification

All therapy structural claims are machine-verified. Lean companion files:

| File | Content |
|------|---------|
| `Core.lean` | 12-primitive inductive types (canonical v0.5.69) |
| `Imscription.lean` | Imscription struct, P-70 theorem |
| `Crystal.lean` | Frobenius address bijection (0–17,279,999) |
| `TierCrossing.lean` | Ouroboricity tier predicate |
| `IGMorphism.lean` | Structural morphisms between types |
| `Frobenius.lean` | Frobenius condition (μ∘δ=id) formal proofs |
| `AgentSelf.lean` | Agent self-encoding; theorem agent_is_O_inf |

Build: `cd p4rakernel/p4ramill && lake build`

---

## PDB Structures

DARPin-based therapeutic proteins designed via the serpent_rod pipeline:

| PDB File | Target | Therapy |
|----------|--------|---------|
| `DARPin_NMDA.pdb` | NMDA receptor glycine site | Schizophrenia (Ħ promotion) |
| `DARPin_odot_schiz.pdb` | 5-HT₂A / D2 | Schizophrenia (φ̂ demotion) |
| `CART_odot.pdb` | ⊙-immune restoration | HIV (φ̂ restoration) |
| `DARPin_gp120.pdb` | HIV gp120 glycoprotein | HIV (Ħ promotion) |
| `DARPin_PBP2a.pdb` | MRSA PBP2a resistance protein | MRSA (φ̂ demotion) |
| `Biofilm_Disruptor.pdb` | MRSA biofilm EPS | MRSA (ɢ correction) |
| `DARPin_5HT2A.pdb` | Serotonin 5-HT₂A | MDD (φ̂ promotion) |
| `DARPin_odot.pdb` | ⊙ stabilizer | MDD (φ̂ maintenance) |
| `DARPin_LHR.pdb` | LH receptor | PCOS (φ̂ demotion) |
| `FSH_odot.pdb` | FSH ⊙-restorer | PCOS (Φ correction) |
| `AAV9_CFTR_odot.pdb` | CFTR gene therapy vector | CF (multi-primitive) |
| `DARPin_CFTR.pdb` | CFTR folding chaperone | CF (φ̂ + Þ) |

---

## CDXML Chemical Registry

`cdxml/th3rapies.cdxml` — 12,268-line ChemDraw CDXML v23.1.1 schema containing 63 molecular fragments, 49 SMILES-annotated molecules, and 12 reaction arrows for all therapeutic payloads including the disachizic inventory, ouroboric pill chemistry, universal antidote library, and cephalopod-inspired bio-adaptive materials.

---

## Companion Documents

All original therapy design documents are in `ig-docs/therapies/`:

- `SCHIZOPHRENIA_THERAPY.md` (556 lines) — Full two-primitive derivation
- `HIV_THERAPY.md` — Viral-manic identity, ART=MDD structural proof
- `MRSA_THERAPY.md` — PBP2a + biofilm dual disruption
- `MDD_THERAPY.md` — φ̂ promotion via 5-HT₂A
- `PCOS_THERAPY.md` — LHR suppression + FSH ⊙ restoration
- `CF_THERAPY.md` — 10-primitive disease, gene therapy + chaperone
- `gout_elimination_design.md` — XO inhibition protocol
- `gout_combined_therapy_design.md` — Three-component protocol
- `gout_holistic_protocol.md` — Four-component holistic protocol
- `homeopathy_structural_analysis/analysis.md` — Potentization as quantum state preparation

---

## API

```python
from ars_therapeutica import (
    THERAPIES, DISEASE_TYPES, HEALTH_TYPES,
    tensor, meet, join, distance, delta_primitives, c_score, tier
)

# Structural diagnosis
th = THERAPIES["schizophrenia"]
print(th.disease_type.display())     # ⟨𐑼 𐑥 𐑾 𐑬 𐑞 𐑧 𐑔 𐑠 𐑣 𐑒 𐑳 𐑷⟩
print(th.health_type.display())      # ⟨𐑼 𐑥 𐑾 𐑬 𐑞 𐑧 𐑔 𐑠 ⊙ 𐑖 𐑳 𐑷⟩
print(distance(th.disease_type, th.health_type))  # 1.3416

# Tensor therapy step
intermediate = tensor(SCHIZOPHRENIA, NMDA_SYSTEM)
# Ħ promoted from 𐑒 to 𐑖

# Meet therapy step
corrected = meet(intermediate, ODOT_STABILIZER)
# φ̂ demoted from 𐑣 to ⊙
```

---

## License

Unlicense — public domain.

---

*There is great merit in following a problem where it leads [1].*

[1] H. T. Larson, "Catch a Rising Problem and Never Ever Let It Go," *IEEE Computer*, vol. 19, no. 2, pp. 61–63, February 1986.
