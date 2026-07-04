# Ars Therapeutica

**Author:** Lando⊗⊙perator · **Package:** `ars-therapeutica` (pip) · **CLI:** `at`

**What it is.** A type-lattice navigator that operationalizes the 12-primitive Imscribing Grammar for therapeutic design.

**What it does.** Reduces each disease to its structural deltas (the primitives differing from the healthy state) and designs therapeutic operations (TENSOR, MEET, JOIN) to correct them, exposed as a CLI for diagnosis, full therapy protocols, and structural comparisons.

**Why it matters.** It surfaces structural identities invisible to conventional nosology: HIV and bipolar mania are the same type (d=0.0, viral replication is structurally manic); ART-suppressed HIV is structurally major depression; and standard antipsychotics fail structurally because the dopamine system is sub-critical (φ̂=𐑢), so its tensor with schizophrenia leaves the disease primitives unchanged. It also proves why dual-component therapies are necessary: no single compound can both promote Ħ and demote φ̂.

**How to use it.**
```bash
cd Ars_Therapeutica && pip install -e .    # Python ≥ 3.10, no external deps
at list                       # all therapies
at diagnose schizophrenia     # structural diagnosis
at therapy hiv                # full therapy protocol
at spectrum                   # psychiatric φ̂-spectrum
at compare schizophrenia depression
at tensor schizophrenia nmda  # structural operation
at meet hiv art
```

---

## Therapy catalog

| Disease | Category | Distance | Tier Δ | Primitives Δ |
|---------|----------|----------|--------|--------------|
| Schizophrenia | psychiatric | 1.34 | O₀→O₁ | φ̂, Ħ |
| MDD | psychiatric | 1.34 | O₀→O₁ | φ̂, Ħ |
| HIV/AIDS | viral | 3.32 | O₀→O₂ | Þ, Ç, φ̂, Ħ, Ω |
| MRSA | bacterial | 3.0 | O₀→O₁ | Þ, K, ɢ, φ̂, Ħ, Ω |
| PCOS | metabolic | 3.32 | O₀→O₁ | Þ, Φ, K, φ̂, Ħ, Ω |
| Cystic Fibrosis | genetic | 5.02 | O₀→O₁ | 10 primitives |
| Gout (3 protocols) | metabolic | 5.02 | O₀→O₁ | 11 primitives |
| Homeopathy | structural | 4.12 | O₀→O₀ | 10 primitives |

## Structural operations

| Operation | Rule | Clinical use |
|-----------|------|--------------|
| **TENSOR** (⊗) | MAX on Ð,Þ,Ř,Ç,Γ,ɢ,φ̂,Ħ,Σ,Ω; MIN on Φ,ƒ | Promote chirality (Ħ), expand range (Γ) |
| **MEET** (⊓) | MIN on all primitives | Demote super-criticality (φ̂), slow kinetics (Ç) |
| **JOIN** (⊔) | MAX on all primitives | Ceiling operation; aspirational, not always safe |

The fundamental incompatibility: no single compound can both promote Ħ (needs TENSOR) and demote φ̂ (needs MEET). This is why dual-component therapies are structurally necessary.

## Key structural identities

**HIV = Bipolar Mania (d = 0.0).** Both imscribe to `⟨𐑼 𐑥 𐑾 𐑬 𐑞 𐑪 𐑔 𐑠 𐑣 𐑒 𐑳 𐑷⟩`; a virus and a psychiatric condition share an identical structural type.

**meet(HIV, ART) = MDD.** The ART-suppressed patient is structurally in a depression-like immune state.

**tensor(schizophrenia, NMDA_PAM)** promotes Ħ (𐑒→𐑖) but leaves φ̂ super-critical (𐑣); a second MEET with a ⊙-stabilizer is required.

## φ̂ spectrum: the psychiatric axis

```
φ̂=𐑢  Depression     C=0.0   O₀
φ̂=⊙  Healthy Brain  C=0.70  O₂
φ̂=𐑣  Schizophrenia  C=0.0   O₀
φ̂=𐑣  Bipolar Mania  C=0.0   O₀
```

Depression → health promotes φ̂ (𐑢→⊙, TENSOR with a ⊙-bearing system); schizophrenia → health demotes φ̂ (𐑣→⊙, MEET with a ⊙-stabilizer). Schizophrenia and mania differ only by kinetics (chronic vs episodic), d=1.0.

## Verification and companions

Structural claims are checked against the Lean 4 formalization in `imsgct/p4rakernel/p4ramill`; the repo also carries PDB structures, a CDXML chemical registry, and companion documents (see in-repo). Public domain (Unlicense).
