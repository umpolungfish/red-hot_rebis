# SYNTHETIC DETOX GLAND — Organoid Assembly Protocol
## Version 1.0 | CLINK Pipeline | Lando ⊗ ⊙perator

### Materials Required

**Cell Lines (3 types):**
- SENS-01: HEK293T-GLSensor — Constitutively expresses 5 toxin receptor classes
- PROD-01: HEK293T-GLProducer — Inducible antidote fusion protein expression
- SUP-01: HUVEC-GLVasc — Vascular support factors (VEGFA, ANGPT1)

**Hydrogel Scaffold:**
- Hyaluronic acid (HA), 10 mg/mL, high MW (1.5 MDa)
- Collagen type I, rat tail, 5 mg/mL
- PEG-4MAL crosslinker, 4-arm, 10 kDa
- Alginate (ultrapure, low-endotoxin), 20 mg/mL
- Laminin-111, 100 µg/mL
- Y-27632 ROCK inhibitor (10 µM)

**Growth Factors (all recombinant human):**
- VEGF-A165 (100 ng/mL)
- bFGF (50 ng/mL)
- EGF (50 ng/mL)
- IGF-1 (50 ng/mL)
- Angiopoietin-1 (200 ng/mL)
- Heparin (10 µg/mL)

**Media:**
- Advanced DMEM/F12 + 10% FBS (Tet-Free) + 1% GlutaMAX + 1% P/S
- Differentiation Medium: DMEM/F12 + 2% FBS + 1% ITS-X + 1% N2 + 1% B27
- Endothelial Medium: EGM-2 MV (Lonza) + 10% FBS

### Protocol — Day 0 through Day 28

#### Phase 1: Cell Expansion (Days -14 to -3)

1. **Thaw sensor cells (SENS-01)** and culture in Advanced DMEM/F12 + 10% Tet-Free FBS
   - p0 → p3 expansion over 10 days
   - Target: 5 × 10⁷ cells
   - Selection: G418 (400 µg/mL) for stable integrants

2. **Thaw producer cells (PROD-01)** and culture in same medium
   - p0 → p3 expansion over 10 days
   - Target: 9 × 10⁸ cells   
   - Selection: Puromycin (1 µg/mL)

3. **Thaw support cells (SUP-01)** and culture in EGM-2 MV
   - p0 → p3 expansion over 10 days
   - Target: 5 × 10⁷ cells

#### Phase 2: Hydrogel Scaffold Preparation (Day -2)

1. Prepare HA-Collagen-PEG4MAL hydrogel:
   - Mix 200 µL HA (10 mg/mL) + 100 µL collagen I (5 mg/mL) + 20 µL laminin (100 µg/mL)
   - Add 50 µL PEG-4MAL crosslinker (20 mM in PBS)
   - Add 30 µL alginate (20 mg/mL) for mechanical stability
   - Adjust pH to 7.4 with NaOH
   - In 24-well ultralow attachment plate, add 400 µL per well
   - Polymerize at 37°C for 30 min

2. **Vascular channel template:**
   - Place 200 µm diameter nylon filament array into hydrogel before polymerization
   - Remove filaments after polymerization → microchannel network
   - Flush channels with endothelial medium

#### Phase 3: Organoid Assembly (Day 0)

1. **Dissociate all three cell types** using TrypLE Express (5 min, 37°C)
2. **Count and mix at ratio:**
   - 5% sensor cells (SENS-01)
   - 90% producer cells (PROD-01)
   - 5% support cells (SUP-01)
3. **Re-suspend at 2 × 10⁷ cells/mL** in differentiation medium + 10 µM Y-27632
4. **Seed 5 × 10⁵ cells per hydrogel scaffold** (25 µL cell suspension per well)
5. **Centrifuge** at 200 × g for 5 min to embed cells
6. **Incubate at 37°C, 5% CO₂** for 2 hours

#### Phase 4: Maturation (Days 1-28)

**Days 1-7 (Proliferation Phase):**
- Medium: Differentiation Medium + 10 µM Y-27632 (days 1-3 only)
- Growth factors: VEGF 100 ng/mL + bFGF 50 ng/mL + EGF 50 ng/mL
- Change medium every 48 hours
- Monitor: Cell viability (live/dead assay), organoid diameter

**Days 7-14 (Differentiation Phase):**
- Medium: Differentiation Medium (no Y-27632)
- Growth factors: VEGF 50 ng/mL + Ang-1 200 ng/mL + IGF-1 50 ng/mL
- Induce detox pathway: Add 10 ng/mL TNFα + 1 µg/mL LPS for 24h on day 10
  → Confirms NF-κB pathway in producer cells is functional

**Days 14-21 (Vascularization Phase):**
- Perfuse microchannels with endothelial medium + VEGF 100 ng/mL
- Add SUP-01 support cells directly into microchannels (5 × 10⁵ cells/mL)
- Continue perfusion at 1 µL/min using syringe pump
- Monitor: Dextran-FITC perfusion assay for vessel patency

**Days 21-28 (Maturation Phase):**
- Reduce growth factors: VEGF 20 ng/mL only
- Medium: 50% Differentiation Medium + 50% endothelial medium
- Functional testing: Add 10 µM paraoxon (organophosphate) to medium
  → Measure antidote secretion at 0, 1, 6, 24, 48h via ELISA

#### Quality Control Checks

| Check | Method | Criteria |
|-------|--------|----------|
| Viability | Live/Dead (Calcein-AM/PI) | > 85% viable |
| Sensor expression | Western blot (anti-AhR, anti-TLR4) | All 5 sensors detectable |
| Antidote production | ELISA (anti-CYP3A4, anti-PON1) | > 100 ng/mL/10⁶ cells/24h |
| Vascularization | CD31 immunostaining | Perfusable channels present |
| Toxin clearance | LC-MS/MS of medium | > 50% paraoxon degraded in 24h |
| Sterility | Agar plate culture | No bacterial/fungal growth |

### Scaling to Implantable Size

For a 3 cm³ gland (human implant scale):
- Scale cell numbers 1000× (5 × 10⁸ sensor, 9 × 10⁹ producer, 5 × 10⁸ support)
- Use 3D-printed HA-alginate scaffold (cryogenic 3D printing)
- Integrate with omental arteriovenous loop for immediate perfusion
