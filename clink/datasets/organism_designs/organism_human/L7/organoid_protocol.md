# Human Intestinal Organoid Protocol — CLINK v2.0
**Author:** Lando⊗⊙perator | **Based on:** Clevers lab method (Sato et al. 2011 Nature 469:415-418)

## Source Material
- Human intestinal crypts from endoscopic biopsy (sigmoid colon preferred)
- IRB approval required; informed consent mandatory
- Process within 2 h of collection; transport on ice in DMEM + 10% FBS

## Crypt Isolation
1. Wash biopsy vigorously with ice-cold PBS (Ca²⁺/Mg²⁺-free) — 5× washes, 10 mL each
2. Transfer to 2 mM EDTA in PBS (pre-warmed to 37°C)
3. Incubate 30 min at 37°C with gentle agitation (orbital shaker, 80 rpm)
4. Transfer to fresh cold PBS
5. Shake vigorously by hand for 20 sec (critical step — releases crypts)
6. Pass through 70 μm cell strainer into 50 mL conical
7. Examine flow-through under microscope — expect ~500 crypts per biopsy
8. Centrifuge 200×g, 5 min, 4°C
9. Resuspend pellet in cold PBS, count crypts using inverted microscope
10. Calculate: aim for 500 crypts per 50 μL Matrigel dome

## Embedding (Day 0)
1. Pellet crypts again (200×g, 3 min)
2. Remove supernatant completely, place tube on ice
3. Resuspend in cold Matrigel GFR (Corning #354230) at ~500 crypts/50 μL
   — Keep Matrigel on ice at ALL times; it polymerizes above 10°C
4. Using pre-chilled pipette tips, plate 50 μL domes in pre-warmed 24-well plate
5. Place plate in incubator: 10 min at 37°C to solidify (do not disturb)
6. Overlay each dome with 500 μL pre-warmed IntestiCult™ OGM Human (StemCell #06010)

## Days 1-7: Establishment Phase
- Day 1: Add Y-27632 (10 μM final) to medium — ROCK inhibitor prevents anoikis
- Day 2-3: Replace medium (without Y-27632) — expected: small spherical structures
- Day 4-5: Budding crypt-like structures visible, dark lumen under phase contrast
- Day 6-7: Replace medium, organoids 100-300 μm diameter

## Days 7-14: Maintenance
- Passage when organoids reach 300-500 μm or become overly dense
- Mechanical passaging: pipette up/down 20× with P1000 to break Matrigel
- Optional enzymatic: TrypLE Express, 2 min at 37°C (avoid over-digestion)
- Wash with cold PBS, re-embed in fresh Matrigel at 1:3-1:5 split ratio
- Expect 10-20× expansion every 7-10 days

## Differentiation (Optional)
- Remove Wnt3a/R-Spondin-1 from medium to drive differentiation
- Enterocyte enrichment: no additional factors
- Goblet cell: DAPT (10 μM, Notch inhibitor), 3-5 days → MUC2+ cells
- Enteroendocrine cell: DAPT + high N2 supplement
- Paneth cell: requires Wnt3a (NOT removed)

## Quality Control Markers
| Cell Type | Marker | Detection |
|---|---|---|
| Stem cell | LGR5, OLFM4, ASCL2 | RNAscope / qPCR |
| Transit amplifying | KI67, MKI67 | IF |
| Enterocyte | Villin, FABP1, ALPI | IF / qPCR |
| Goblet cell | MUC2, TFF3 | IF / PAS stain |
| Enteroendocrine | CHGA, SYP | IF |
| Paneth cell | LYZ, DEFA5 | IF |

## Troubleshooting
| Problem | Cause | Solution |
|---|---|---|
| No crypts isolated | Biopsy too small, over-washed | Use at least 4 biopsies |
| Matrigel domes collapse | Too warm during plating | Pre-chill tips, work fast on ice |
| Organoids cystic (no budding) | Low Wnt, high BMP | Check R-Spondin-1 concentration |
| Bacterial contamination | Non-sterile biopsy | Add Primocin 100 μg/mL days 0-3 |
| Organoids die after passage | Over-digested, too small | Mechanical only; keep fragments >50 cells |

## Reference
- Sato T et al. (2011) Long-term expansion of epithelial organoids from human colon, adenoma, adenocarcinoma, and Barrett's epithelium. *Nature* 469:415-418.
- van de Wetering M et al. (2015) Prospective derivation of a living organoid biobank of colorectal cancer patients. *Cell* 161:933-945.
