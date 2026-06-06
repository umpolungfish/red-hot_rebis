# Ouroboric Pill — Chemical Specification

## DNA Origami Chassis

### Scaffold
- **Source:** M13mp18 bacteriophage DNA
- **Length:** 7249 nt
- **Sequence:** Standard M13mp18 (GenBank: L08821.1)
- **Modifications:** 5' biotin-TEG, 3' cholesterol-TEG
- **Storage buffer:** 1× TE (10 mM Tris-HCl, 1 mM EDTA, pH 8.0)

### Staple Strands (176 total)
- **Length range:** 32–56 nt
- **Modification:** HPLC purification, desalted
- **Key modified staples:**
  - 12× Cy3-labeled (FRET donor, emission 570 nm)
  - 12× Cy5-labeled (FRET acceptor, emission 670 nm)
  - 6× biotin-TEG (for streptavidin conjugation)
  - 4× folate-PEG (for targeting)

### Folding Protocol
- **Buffer:** 1× TAE-Mg²⁺ (40 mM Tris, 20 mM acetic acid, 1 mM EDTA, 12.5 mM MgCl₂, pH 8.0)
- **Staple/scaffold ratio:** 10:1 (2 µM scaffold, 20 µM each staple)
- **Annealing:** 95°C for 5 min, then cool from 95°C to 4°C at −1°C/min
- **Purification:** Amicon Ultra 100 kDa MWCO centrifugal filter, 3× wash with TAE-Mg²⁺
- **Yield:** 60–80% folded barrels
- **Quality control:** AFM imaging, TEM, agarose gel electrophoresis

## Aptamer Sequences

### IL-6 Aptamer (KD = 12.4 nM)
5'-GCGAATTCGTGGAAGGGTCGATCCGGAGCTAGTTAGGGCTCCTAGCTAAAGCTAGGCCGTG-3'
- **Length:** 58 nt
- **Modifications:** 3' BHQ-1 quencher, 5' Cy3 fluorophore
- **Folding buffer:** 10 mM HEPES, 150 mM NaCl, 5 mM KCl, 2 mM MgCl₂, pH 7.4
- **Refolding:** 95°C for 5 min, snap cool on ice for 10 min

### TNF-alpha Aptamer (KD = 8.7 nM)
5'-CGTGCAGTCCGGCGTAGGGCGATCGATCGATCGATCGATCGTAGGCTCGGATCCTAGCTAGCT-3'
- **Length:** 62 nt
- **Modifications:** 3' BHQ-2 quencher, 5' Cy5 fluorophore

### IFN-gamma Aptamer (KD = 15.2 nM)
5'-GGGAGCUCAGCCUUCACUUCUCCGAGCUAGCUAGCUAGCUAGGGAUCCGAUAGCUAGCUAGC-3'
- **Length:** 60 nt
- **Modifications:** 3' Iowa Black RQ quencher, 5' FAM fluorophore

### VEGF Aptamer (KD = 0.5 nM)
5'-CGCAUCGUAUGGUUGGUGUGGUUUGGGAGCUAGCUAGCUAGCUAGGAUCCGAUAGCUA-3'
- **Length:** 55 nt
- **Modifications:** 3' BHQ-3 quencher, 5' Texas Red fluorophore

### cMyc Aptamer (KD = 3.8 nM)
5'-GGAUGGAUGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAU-3'
- **Length:** 60 nt
- **Modifications:** 3' Iowa Black FQ quencher, 5' Cy5.5 fluorophore

## Quantum Dot Logic Gates

### QD Composition
- **Core:** CdSe
- **Shell:** ZnS (4 monolayers)
- **Core diameter:** 4.2 nm
- **Ligand:** DHLA-PEG-OMe (dihydrolipoic acid-PEG-methyl ether, MW 750)
- **Solvent:** Aqueous (10 mM borate buffer, pH 8.5)

### QD Emission Wavelengths
| QD | λ_max (nm) | FWHM (nm) | QY (%) | Logic Gate |
|----|-----------|-----------|--------|-----------|
| QD525 | 525 | 28 | 65 | AND |
| QD585 | 585 | 30 | 70 | OR |
| QD625 | 625 | 32 | 60 | NOT |
| QD665 | 665 | 34 | 55 | MAJORITY |
| QD705 | 705 | 35 | 50 | Readout |

### FRET Pair Configuration
- **Donor:** QD (gate output)
- **Acceptor:** Cy5 dye on aptamer extension
- **Distance:** 8–12 nm (within Förster radius)
- **Förster radius (R₀):** 6.5 nm for QD525-Cy3, 7.2 nm for QD585-Cy5

## Drug Payload Chemistry

### Dexamethasone
- **IUPAC:** (8S,9R,10S,11S,13S,14S,16R,17R)-9-fluoro-11,17-dihydroxy-17-(2-hydroxyacetyl)-10,13,16-trimethyl-6,7,8,11,12,14,15,16-octahydrocyclopenta[a]phenanthren-3-one
- **Formula:** C₂₂H₂₉FO₅
- **MW:** 392.46 g/mol
- **SMILES:** CC1CC2C3CCC4=CC(=O)C=CC4(C)C3(F)C(O)CC2(C)C1(=O)CO
- **Solubility:** 0.1 mg/mL in water, 50 mg/mL in DMSO
- **LogP:** 1.83
- **Encapsulation:** Hydrophobic core of DNA origami barrel

### Anti-TNF Fab Fragment
- **Sequence:** EVQLVESGGGLVQPGGSLRLSCAASGYTFTSYWMHWVRQAPGKGLEWVGFISYGGSSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAREGYYGSGSYYFDYWGQGTLVTVSS
- **MW:** ~47.45 kDa
- **Expression:** E. coli SHuffle T7
- **Purification:** Protein A affinity + SEC
- **Conjugation:** Maleimide-PEG₂₄-NHS linker to DNA origami

## PEG Coating
- **MW:** 5 kDa
- **Grafting density:** 1 PEG per 100 nm²
- **Conjugation:** NHS-ester to amine-modified staples
- **Effect:** 15× increase in circulation half-life

## Quality Control Assays
1. **Origami folding:** AFM imaging (Veeco MultiMode), TEM (JEOL 1400)
2. **Aptamer binding:** Surface plasmon resonance (Biacore T200)
3. **QD logic gate:** Fluorescence spectroscopy (Horiba Fluorolog-3)
4. **Drug loading:** LC-MS/MS (Agilent 6470 triple quad)
5. **Release kinetics:** Dialysis + fluorescence monitoring
6. **Sterility:** 0.22 µm filtration + LAL endotoxin test
