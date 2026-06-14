# Mitosis Checkpoint Assay Protocol — Human Cells
**Author:** Lando⊗⊙perator | **Version:** 2.0

## Scope
Validate spindle assembly checkpoint (SAC) function in CLINK-designed human cell lines. Target: Aurora-B spatial phosphorylation gradient (⊙=𐑻 mechanism).

## Cell Lines
- Primary: RPE1-hTERT (diploid, 2n=46) — normal checkpoint
- Control: HeLa (hypertriploid) — checkpoint-competent cancer line
- Negative control: MAD2 knockdown (siRNA) — checkpoint-deficient

## Materials

| Reagent | Supplier | Cat# | Notes |
|---|---|---|---|
| DMEM/F-12 | ThermoFisher | 11320033 | With L-glutamine |
| FBS | Corning | 35-010-CV | Heat-inactivated |
| Nocodazole | Sigma | M1404 | 100 μg/mL stock in DMSO |
| MG132 | Sigma | M7449 | 10 mM stock in DMSO |
| Thymidine | Sigma | T1895 | 200 mM stock in PBS |
| Anti-Aurora B (phospho-T232) | Abcam | ab18256 | Rabbit monoclonal |
| Anti-MAD2 | BD Biosciences | 610403 | Mouse monoclonal |
| Anti-α-tubulin | Sigma | T9026 | DM1A clone |
| Alexa Fluor 488/594 secondaries | Invitrogen | — | Donkey anti-rabbit/mouse |
| DAPI | Sigma | D9542 | 1 μg/mL |
| ProLong Gold | Invitrogen | P36930 | Antifade mountant |

## Procedure

### Day 0: Cell Seeding
1. Trypsinize and count cells (Trypan Blue exclusion)
2. Seed 5×10⁴ cells/well in 6-well plate with 22×22 mm #1.5 coverslips
3. Grow overnight in complete DMEM/F-12 + 10% FBS

### Day 1: Synchronization (Double Thymidine Block)
4. Add thymidine to 2 mM final (from 200 mM stock)
5. Incubate 18 h at 37°C, 5% CO₂
6. Release: wash 3x with warm PBS, add fresh complete medium
7. Incubate 9 h
8. Add thymidine to 2 mM (second block)
9. Incubate 15 h
10. Release: wash 3x with warm PBS → G1/S boundary synchronized

### Day 2: Spindle Disruption + Fixation
11. 6 h post-release: add nocodazole (100 ng/mL) + MG132 (10 μM)
12. Incubate 2 h (prometaphase arrest, SAC active)
13. Fix: 4% PFA in PBS, 15 min, RT
14. Permeabilize: 0.5% Triton X-100 in PBS, 10 min
15. Block: 5% BSA in PBST, 1 h, RT

### Day 2-3: Immunostaining
16. Primary antibody cocktail (Anti-pAuroraB 1:500 + Anti-MAD2 1:200 + Anti-α-tubulin 1:1000) in 1% BSA/PBST
17. Incubate overnight at 4°C in humidified chamber
18. Wash 3×5 min PBST
19. Secondary antibody cocktail (Alexa Fluor 488 anti-rabbit + Alexa Fluor 594 anti-mouse, both 1:1000) + DAPI 1 μg/mL
20. Incubate 1 h, RT, dark
21. Wash 3×5 min PBST
22. Mount on slide with ProLong Gold, cure 24 h

### Imaging
23. Confocal microscope (60×/1.4 NA oil immersion)
24. Z-stack: 0.3 μm step, 10-15 slices
25. Channels: DAPI (405 nm), Alexa 488 (488 nm), Alexa 594 (561 nm)

### Expected Results
| Condition | Aurora-B Localization | MAD2 | Phenotype |
|---|---|---|---|
| Nocodazole + MG132 | Inner centromere (between sister kinetochores) | Kinetochore (active SAC) | Prometaphase arrest, >80% round cells |
| MG132 only | Centromere → diminished | Negative | Metaphase plate alignment |
| MAD2 siRNA + Nocodazole | Inner centromere | Absent | Mitotic slippage, micronuclei |
| Untreated | Centromere → midzone (anaphase) | Negative (satisfied) | Normal division |

### Quantification
- Count >100 mitotic cells per condition, 3 biological replicates
- Aurora-B inter-kinetochore distance: 0.8-1.2 μm (prometaphase) vs 0.5-0.7 μm (metaphase)
- SAC activity: % MAD2-positive kinetochores (>5 puncta/cell = active)

### Reference
- Lampson & Cheeseman (2011) *Curr Opin Cell Biol* 23:96-101
- Welburn et al. (2010) *Dev Cell* 19:698-711
