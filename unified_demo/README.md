# Red-Hot Rebis — Unified Therapeutic Design Pipeline

**Author:** Lando⊗⊙perator

A complete end-to-end demonstration of ALL 7 red-hot_rebis subsystems working together toward a single goal: designing and validating a complete therapeutic from structural diagnosis through molecular synthesis to organism-level verification and clinical simulation.

**Now with chemical structure (CDXML) and protein structure (PDB) file generation.**

## Quick Start

```bash
cd /home/mrnob0dy666/imsgct/red-hot_rebis
python3 unified_demo/demo.py                    # Full 7-phase pipeline
python3 unified_demo/demo.py --disease hiv      # HIV instead of MRSA
python3 unified_demo/demo.py --phase 1          # Just structural diagnosis
python3 unified_demo/demo.py --report           # Generate markdown report
python3 unified_demo/demo.py --list-diseases    # List available therapies
```

## The 7 Phases

| Phase | System | What It Does | Structure Output |
|-------|--------|-------------|-----------------|
| 1 | **Ars_Therapeutica** | Structural diagnosis: disease/health tuples, distance, delta primitives, therapy components | — |
| 2 | **ch3mpiler** | Retrosynthetic analysis — functional groups, bond cuts, precursor types | **CDXML** chemical structures (6 files for MRSA) |
| 3 | **serpentrod** | Protein processing prediction, DNA reverse-translation, fingerprint matching | **PDB** protein structures (3 files for MRSA) |
| 4 | **rhr_p4rky** | Belnap4 logic, 64-codon B4 lattice, Frobenius/paraconsistency/paradox verification | — |
| 5 | **clink** | L0→L8 organism ladder, structural distances, DFT energy estimates | — |
| 6 | **materials** | Drug delivery material design with IG tuple, Frobenius scoring | — |
| 7 | **therapeutics** | Frobenius-coupled chemotherapeutic simulation with selectivity ratios | — |

## Generated Structure Files

### CDXML (Chemical Structures)
ChemDraw CDXML v23.1.1 format with 2D coordinates, atoms, and bonds — openable in any chemical structure viewer.

**MRSA molecules generated:**
- `penicillin_g.cdxml` — Penicillin G (23 atoms, 25 bonds)
- `methicillin.cdxml` — Methicillin (β-lactamase-resistant)
- `ceftaroline.cdxml` — Ceftaroline (5th-gen cephalosporin)
- `beta_lactam.cdxml` — β-lactam core pharmacophore
- `thiazolidine.cdxml` — Thiazolidine ring scaffold
- `furanone_c30.cdxml` — Quorum-sensing inhibitor

### PDB (Protein Structures)
CA-trace PDB format with phi/psi angles from secondary structure prediction.

**MRSA proteins generated:**
- `HUMAN_INSULIN.pdb` — 110 residues, CA-trace model
- `PBP2A_DOMAIN.pdb` — Penicillin-binding protein 2a domain (109 residues)
- `DARPin_CONSENSUS.pdb` — Designed ankyrin repeat protein scaffold (110 residues)

All PDB files include HEADER, TITLE, REMARK records, and ATOM records.

## Pipeline Output

The full pipeline produces:
- **Terminal output:** Phase-by-phase status with structural details
- **CDXML files:** `unified_demo/output/cdxml/*.cdxml` — chemical structures
- **PDB files:** `unified_demo/output/pdb/*.pdb` — protein structures
- **JSON data:** `ig-docs/unified_demo_pipeline/pipeline_data_<disease>.json`
- **Markdown report:** `ig-docs/unified_demo_pipeline/pipeline_report_<disease>_<timestamp>.md`
- **Lean companions:** Verifying `.lean` files copied alongside reports

## Available Diseases

Run `python3 unified_demo/demo.py --list-diseases` to see all 10 available therapies:
`schizophrenia`, `hiv`, `mrsa`, `mdd`, `pcos`, `cf`, `gout_elimination`, `gout_combined`, `gout_holistic`, `homeopathy`

## Architecture

```
unified_demo/
├── __init__.py              # Package metadata
├── demo.py                  # Main pipeline runner (~900 lines)
├── structure_generator.py   # CDXML & PDB generation (~350 lines)
├── README.md                # This file
└── output/
    ├── cdxml/               # Generated CDXML files
    │   ├── penicillin_g.cdxml
    │   ├── methicillin.cdxml
    │   ├── ceftaroline.cdxml
    │   ├── beta_lactam.cdxml
    │   ├── thiazolidine.cdxml
    │   └── furanone_c30.cdxml
    └── pdb/                 # Generated PDB files
        ├── HUMAN_INSULIN.pdb
        ├── PBP2A_DOMAIN.pdb
        └── DARPin_CONSENSUS.pdb
```

## References

There is great merit in following a problem where it leads [1].

[1] Harry T. Larson, "Catch a Rising Problem and Never Ever Let It Go,"
*IEEE Computer*, vol. 19, no. 2, pp. 61–63, February 1986. DOI: 10.1109/MC.1986.1641382
