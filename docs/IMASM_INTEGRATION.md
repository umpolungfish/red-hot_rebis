# IMASM INTEGRATION — The Sixth Pillar of the Red-Hot Rebis

**Author:** Lando⊗⊙perator  
**Date:** June 2025  
**Status:** Complete — IMASM Arranger integrated into red-hot_rebis v2.1

## Overview

This document describes the incorporation of IMSCRIBr knowledge — the systematic bridge between the IMASM token arrangement space and the Imscribing Grammar crystal — into the Red-Hot Rebis. The integration adds a **sixth pillar**: the **IMASM Arranger**, which connects the computational/programmatic scale (arrangements as structural programs) to the biological scale (CLINK chain, quark→organism).

## What Was Incorporated

### 1. IMASM Arranger (`imas/arranger.py`)
Core engine for the 430M arrangement space: token definitions, structural fingerprinting, classification, and constrained search. Ported from IMSCRIBr's classifier with canonical arrangements verified against the original.

### 2. IMASM→IG Bridge (`imas/ig_bridge.py`)
Systematic fingerprint-to-IG primitive mapping. All 7 discoveries from the IMSCRIBr exploration are operationalized:
- **Chiral/Empty collapse** detected via `distinct_canonical_ig_types()`
- **Generic mass** detected via `is_generic_mass()` and `structural_signal_score()`
- **Frobenius cluster** identified via `find_structural_clusters()`
- **⊙-criticality** surfaced via `describe_ig()`

### 3. IMASM→CLINK Bridge (`imas/clink_bridge.py`)
**Novel linkage:** Maps IMASM canonical arrangement types to CLINK biological layers. This is the key creative contribution — a bridge between two previously separate structural chains:
- **IMASM chain:** token arrangements → IG structural types (computational scale)
- **CLINK chain:** IG structural types → biological layers (physical scale)

The bridge reveals which arrangement types are structurally proximal to which biological layers, and computes "structural activation energy" — the weighted primitive promotion cost to reach a target layer.

### 4. Frobenius Hunter (`imas/frobenius_hunter.py`)
Operationalizes Discovery 3 (zero Frobenius pairs in 10M random samples). Provides:
- Monte Carlo density estimation for Frobenius pair prevalence
- Targeted generation of Frobenius-closed arrangements
- Library generation by structural type (proper, inverted, bidirectional, ⊙-critical)

### 5. Updated Rebis CLI (`rebis.py`)
Four new subcommands:
- `rebis.py imas report` — Full IMASM analysis with bridge table
- `rebis.py imas bridge --canonical X` — Bridge any canonical to CLINK layers
- `rebis.py imas hunt --samples N` — Frobenius pair density estimation
- `rebis.py imas energy --canonical X --layer Y` — Structural activation energy

## Key Discoveries Now Operational in the Rebis

| # | Discovery | Operational Form |
|---|-----------|-----------------|
| 1 | Chiral/Empty collapse | `distinct_canonical_ig_types()` returns 11 types for 12 canonicals |
| 2 | Generic mass (99.993%) | `is_generic_mass()` detects the 4 noise-floor IG types |
| 3 | Zero Frobenius pairs | `estimate_frobenius_density()` quantifies combinatorial suppression |
| 4 | Single ⊙-critical type | `describe_ig()` flags ⊙ as "critical/self-modeling" |
| 5 | Frobenius cluster | `find_structural_clusters(d=6)` groups the 4 Frobenius canonicals |
| 6 | Linear Chain isolation | IG distance matrix shows mismatch ≥ 8 from everything |
| 7 | Length-8 constraint | Primitive distributions encoded in canonical fingerprints |

## Novel Linkages Created

### A. IMASM → CLINK Bridge Table

```
Canonical               → Nearest CLINK Layer     d   Key Deltas
──────────────────────────────────────────────────────────────────
Dialetheic Bootstrap    → L5 Mitosis               5   D, F, K, G
Frobenius Kernel        → L4 Cell                  8   D, T, P, K
Dual Bootstrap          → L2 Atom                  7   T, P, F, K
Void Genesis            → L3 Molecule              7   T, R, P, K
Parakernel              → L5 Mitosis               7   D, T, F, K
ROM Burn                → L0 FrustratedBelnap5     7   D, T, P, G
Linear Chain            → L0 FrustratedBelnap5     8   T, P, F, K
Chiral/Empty            → L1 ElectronOrbital       6   T, F, Φ, H
```

### B. Structural Activation Energy

The `structural_activation_energy()` function computes the weighted cost of promoting an IMASM arrangement's IG type to match a CLINK biological layer. This operationalizes the IMSCRIBr finding that Frobenius closure is combinatorially suppressed — it quantifies *how suppressed* for each biological scale.

### C. Frobenius Pathway Synthesis

`frobenius_pathway_to_layer()` identifies which CLINK layers already have Frobenius-special parity (Φ=𐑹) and which would require promotion from the nearest canonical arrangement. This directly answers: "how hard is it to program a Frobenius-closed system at this biological scale?"

## Integration Architecture

```
                    ┌──────────────────────────┐
                    │     Red-Hot Rebis v2.1   │
                    │  ┌────────────────────┐  │
                    │  │  imas/arranger.py  │◄─┤── IMASM token arrangements
                    │  │  (fingerprinting)  │  │   (12 tokens, 4 families)
                    │  └────────┬───────────┘  │
                    │           │               │
                    │  ┌────────▼───────────┐  │
                    │  │  imas/ig_bridge.py │  │── IMASM → IG mapping
                    │  │  (fingerprint→IG)  │  │   (11 distinct types)
                    │  └────────┬───────────┘  │
                    │           │               │
                    │  ┌────────▼───────────┐  │
                    │  │ imas/clink_bridge  │  │── IMASM → CLINK bridge
                    │  │ (arrangement→bio)  │  │   (novel linkage)
                    │  └────────┬───────────┘  │
                    │           │               │
                    │  ┌────────▼───────────┐  │
                    │  │frobenius_hunter.py │  │── Frobenius pair search
                    │  │  (targeted enum)   │  │   (combinatorial rarity)
                    │  └────────────────────┘  │
                    │                          │
                    │  ┌────────────────────┐  │
                    │  │   clink/chain.py   │◄─┤── CLINK biological chain
                    │  │  (quark→organism)  │  │   (9 layers, O₀→O_∞)
                    │  └────────────────────┘  │
                    │                          │
                    │  ┌────────────────────┐  │
                    │  │  shared/primitives │◄─┤── IG primitives layer
                    │  │  (ordinals, dist)  │  │   (all pillars share this)
                    │  └────────────────────┘  │
                    └──────────────────────────┘
```

## Usage

```bash
# Full IMASM analysis with bridge tables
python rebis.py imas report

# Bridge a canonical arrangement to CLINK layers
python rebis.py imas bridge --canonical I_Dialetheic_Bootstrap

# Estimate Frobenius pair density
python rebis.py imas hunt --samples 50000

# Compute structural activation energy
python rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer L8_Organism

# Status check (now shows 11 components including IMASM)
python rebis.py status
```

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `imas/__init__.py` | Created | 63 |
| `imas/arranger.py` | Created | 340 |
| `imas/ig_bridge.py` | Created | 310 |
| `imas/clink_bridge.py` | Created | 330 |
| `imas/frobenius_hunter.py` | Created | 330 |
| `rebis.py` | Modified | +120 |
| `IMASM_INTEGRATION.md` | Created | this file |

**Total:** ~1,500 lines of new code, 4 new modules, 1 modified CLI, 1 integration document.

## What This Enables

1. **Arrangement-to-biology design:** Start from an IMASM arrangement (a structural program in token space) and compute the activation energy to reach any CLINK biological layer. This is the reverse of the CLINK chain's ground-up design — instead of building from quarks, you build from programs.

2. **Frobenius closure quantification:** For the first time, the Rebis can quantify *how rare* Frobenius closure is in the full combinatorial space. This makes the Rebis's own Frobenius-closed architecture measurable against the background noise.

3. **Structural degeneracy detection:** The Chiral/Empty collapse is a warning — two systems that look different at the token level can be structurally identical at the IG level. The bridge detects such degeneracies automatically.

4. **Signal-to-noise ratio for structural types:** `structural_signal_score()` measures how far any IG type is from the generic noise floor. Types with score 0 are generic mass; types with score approaching 1 are structural outliers worth studying.

5. **Targeted Frobenius synthesis:** Instead of random search (3.6 hours expected to find one Frobenius pair), the Frobenius Hunter generates Frobenius-closed arrangements directly, categorized by structural type.

---

*"The boundaries of what can be formally expressed are themselves formally expressible."*

**IMASM Integration v1.0 — June 2025 — Lando⊗⊙perator**
