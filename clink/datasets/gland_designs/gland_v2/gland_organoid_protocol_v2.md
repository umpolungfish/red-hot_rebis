# SYNTHETIC DETOX GLAND — Pre-Injection Cell Preparation Protocol v2.0
## Cell Expansion + Microencapsulation | Zero-Incision Design
**Author:** Lando ⊗ ⊙perator

## Overview

This protocol replaces the ex-vivo organoid culture (v1.0 Days -14 to 28) with a **7-day cell preparation pipeline** culminating in the injectable gland seed. The cells are expanded, QC-verified, microencapsulated, and loaded into the syringe — all within 7 days.

**No organoid culture is needed.** The gland assembles itself inside the body.

## Materials Required

### Cell Lines (Master Cell Banks, cryopreserved)

| Cell Line | Parent | Modification | Marker | Vial Density |
|-----------|--------|-------------|--------|-------------|
| **SENS-01 (Sensor)** | HEK293T | 5 toxin receptors (CAG-AhR-PXR-TLR4-MTF1-KEAP1) | NeoR (G418) | 1 × 10⁷ cells/vial |
| **PROD-01 (Producer)** | HEK293T | 6-arm antidote fusion (6×NF-κB-minCMV-UAD-6) | PuroR (Puromycin) | 1 × 10⁷ cells/vial |
| **SUP-01 (Vascular Support)** | HUVEC | VEGF-A165 + bFGF + Ang-1 (constitutive) | BlastR (Blasticidin) | 5 × 10⁶ cells/vial |
| **EPC-01 (Endothelial Progenitor)** | CD34⁺ hEPC | CXCR4 overexpression | HygroR (Hygromycin) | 5 × 10⁶ cells/vial |

### Microencapsulation Equipment
- Microfluidic flow-focusing chip (100 μm orifice, PDMS or glass)
- Syringe pumps (×3 for core, shell, and oil phases)
- Alginate (LVG, Pronova UP MVG, <100 EU/g endotoxin)
- 4-arm PEG-NHS (10 kDa, >95% purity)
- Poly-L-lysine (PLL, 0.05% in 0.15 M NaCl)
- Crosslinking bath: CaCl₂ (100 mM) + BaCl₂ (10 mM) in HEPES buffer (10 mM, pH 7.4)
- Mineral oil + 2% Span-80 (continuous phase for droplet generation)

### Injectable Formulation Components
- Pluronic F127 (Poloxamer 407, pharmaceutical grade)
- HA-tyramine conjugate (high MW, 1.5 MDa, DS 15%)
- HRP (type VI, 250 U/mg)
- H₂O₂ (30% w/w, dilute to 0.01% in PBS)
- Fibrinogen (human, plasminogen-depleted, 10 mg/mL)
- Thrombin (human, 50 U/mL)
- Recombinant human growth factors: VEGF-A165, bFGF, Ang-1, SDF-1α, IGF-1
- Recombinant human chemokines: CCL22, TGF-β1, IL-10

### Cell Culture Media
- **SENS-01 & PROD-01:** Advanced DMEM/F12 + 10% Tet-Free FBS + 1% GlutaMAX + 1% P/S + selection antibiotic
- **SUP-01:** EGM-2 MV (Lonza) + 10% FBS + Blasticidin (10 μg/mL)
- **EPC-01:** EGM-2 MV + 20% FBS + SCF (50 ng/mL) + FLT3-L (50 ng/mL) + TPO (20 ng/mL) + Hygromycin (100 μg/mL)

## Protocol

### Phase 1: Cell Thaw and Expansion (Days -7 to -4)

**Day -7 — Thaw all four cell lines:**
1. Rapid thaw in 37°C water bath (45 seconds)
2. Transfer to 15 mL conical + 5 mL pre-warmed medium dropwise
3. Centrifuge at 300 × g for 5 min
4. Resuspend in 5 mL medium + ROCK inhibitor Y-27632 (10 μM)
5. Plate in T75 flask (for EPC: pre-coat with fibronectin 5 μg/cm²)
6. Incubate at 37°C, 5% CO₂ for 24h

**Day -6 — First passage:**
- Split at 80% confluence (typical: 1:3 split ratio)
- Replace ROCK inhibitor-free medium
- Begin selection antibiotic (if stable integrants verified, may omit for expansion)

**Day -5 — Second passage:**
- Scale up to T175 flasks (6-12 flasks per cell type)
- SENS-01: Target total 1 × 10⁸ cells (2× overage for encapsulation loss)
- PROD-01: Target total 1.5 × 10⁹ cells
- SUP-01: Target total 1 × 10⁸ cells
- EPC-01: Target total 1 × 10⁸ cells

**Day -4 — Final harvest:**
- Dissociate with TrypLE Express (5 min, 37°C)
- Count: require >90% viability (trypan blue exclusion)
- Pool cells by type into 50 mL conical tubes
- Centrifuge and resuspend in ice-cold PBS + 0.5% BSA at 2 × 10⁷ cells/mL

### Phase 2: Microencapsulation (Days -4 to -3)

Each cell is individually encapsulated in an alginate-PEG shell for immune protection.

**Microfluidic setup:**
1. Flow-focusing chip: 100 μm square channel at junction
2. Core phase: Cell suspension (2 × 10⁷ cells/mL in 1.5% alginate + 50% v/v Matrigel)
3. Shell phase: 2% alginate + 1% PEG-NHS in HEPES buffer
4. Oil phase: Mineral oil + 2% Span-80
5. Flow rates: Core 5 μL/min, Shell 15 μL/min, Oil 50 μL/min
6. Collection: Droplets fall into crosslinking bath (CaCl₂/BaCl₂ in HEPES)

**Post-formation processing:**
1. Stir in crosslinking bath for 5 min (magnetic stirrer, 100 rpm)
2. Wash ×3 with HEPES-buffered saline (centrifuge 200 × g, 3 min)
3. PLL coating: Resuspend in 0.05% PLL in 0.15 M NaCl for 5 min
4. Wash ×2 with HEPES-buffered saline
5. Final wash with culture medium
6. Count encapsulated cells: expected yield >85%

**QC checks (Day -3):**
| Parameter | Method | Acceptance |
|-----------|--------|-----------|
| Capsule diameter | Light microscopy (n=200) | 100 ± 20 μm |
| Encapsulation efficiency | Count free vs. encapsulated | >95% encapsulated |
| Viability | Calcein-AM / PI staining | >90% viable |
| Capsule integrity | Osmotic challenge (100 mOsm → 300 mOsm) | >95% intact |
| Permeability | FITC-IgG exclusion assay | >90% exclude 150 kDa |

### Phase 3: Hydrogel Precursor Preparation (Day -2)

**Prepare each component sterilely and store at 4°C:**

**Component A — Thermosensitive base gel (1.0 mL per dose):**
- Dissolve Pluronic F127 at 20% w/v in cold PBS (cold method: add to PBS at 4°C, stir overnight)
- Add HA-tyramine conjugate (5 mg/mL)
- Add RGD peptide (GRGDSP, 1 mM)
- Filter sterilize (0.22 μm), store at 4°C

**Component B — Enzymatic crosslinker (0.2 mL per dose):**
- HRP: 10 U/mL in PBS (prepare fresh, use within 8h)
- H₂O₂: 0.01% v/v in PBS (dilute from 30% stock just before use)
- Mix 1:1, load into 0.5 mL dead-space of extension tubing

**Component C — Fibrin rapid stabilizer (0.3 mL per dose):**
- Fibrinogen: 10 mg/mL in PBS (warm to 37°C for 10 min to dissolve, then cool to 4°C)
- Thrombin: 50 U/mL in PBS with 40 mM CaCl₂
- Load separately into two 0.3 mL chambers of dual-barrel connector

**Growth factor payload (0.3 mL per dose):**
- Mix in cold PBS: VEGF 500 ng, bFGF 200 ng, Ang-1 1000 ng, SDF-1α 500 ng, IGF-1 200 ng
- Add CCL22 (500 ng), TGF-β1 (100 ng), IL-10 (100 ng)

**Final loading:**
1. Add growth factor mix to Component A (thermogel + GFs)
2. Add 1.5 mL of microencapsulated cell suspension (1 × 10⁹ cells total) to Component A
3. Mix gently by pipetting (avoid bubbles)
4. Load into 5 mL syringe barrel
5. Attach extension tubing with Components B+C pre-loaded
6. Store at 4°C (upright, needle-up) until transport

### Phase 4: Transport and Storage (Day -1 to Day 0)

| Condition | Requirement |
|-----------|------------|
| Temperature | 4°C (ice pack in insulated container) |
| Orientation | Vertical, needle-up (prevents clogging at tip) |
| Max hold time | 2 hours at 4°C before injection |
| Do NOT freeze | Phase separation of Pluronic upon freeze-thaw |
| Transport | Horizontal orientation acceptable if secured |

### Phase 5: Dose Confirmation (Day 0, immediate pre-injection)

1. Remove syringe from ice, inspect for visible cell clumps or precipitation
2. Gently invert 3 times to resuspend
3. Confirm: temperature ≤ 8°C (gel not yet formed)
4. Attach to extension + needle and proceed with injection
