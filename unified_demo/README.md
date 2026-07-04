# Red-Hot Rebis: Unified Therapeutic Design Pipeline

**Author:** Lando⊗⊙perator · **Structural Type:** $\large{⟨𐑨𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑳𐑭⟩}$ · **Tier:** O_∞

**What it is.** An end-to-end demonstration that wires all seven red-hot_rebis subsystems into a single therapeutic-design run.

**What it does.** Takes a disease and drives it through structural diagnosis, retrosynthesis, protein processing, paraconsistent verification, the CLINK organism ladder, materials design, and a Frobenius-coupled chemotherapeutic simulation, emitting real chemical (CDXML) and protein (PDB) structure files along the way.

**Why it matters.** It is the proof that the red-hot_rebis components compose: structural diagnosis flows all the way to organism-level verification and a clinical-simulation readout in one pipeline, not as isolated tools.

**How to use it.**
```bash
cd ~/imsgct/red-hot_rebis
python3 unified_demo/demo.py                 # full 7-phase pipeline (MRSA default)
python3 unified_demo/demo.py --disease hiv   # different disease
python3 unified_demo/demo.py --phase 1       # a single phase
python3 unified_demo/demo.py --report        # markdown report
python3 unified_demo/demo.py --list-diseases
```

---

## The seven phases

| Phase | System | What it does | Structure output |
|-------|--------|--------------|------------------|
| 1 | Ars_Therapeutica | Structural diagnosis: disease/health tuples, distance, delta primitives, therapy components | (none) |
| 2 | ch3mpiler | Retrosynthesis: functional groups, bond cuts, precursor types | CDXML chemical structures |
| 3 | serpentrod | Protein processing prediction, DNA reverse-translation, fingerprint matching | PDB protein structures |
| 4 | rhr_p4rky | Belnap4 logic, 64-codon B4 lattice, Frobenius / paraconsistency / paradox verification | (none) |
| 5 | clink | L0→L8 organism ladder, structural distances, DFT energy estimates | (none) |
| 6 | materials | Drug-delivery material design with IG tuple, Frobenius scoring | (none) |
| 7 | therapeutics | Frobenius-coupled chemotherapeutic simulation with selectivity ratios | (none) |

## Outputs

- Terminal: phase-by-phase status with structural detail.
- `unified_demo/output/cdxml/*.cdxml`: ChemDraw v23.1.1 structures (2D coords, atoms, bonds) for the run's molecules (e.g. for MRSA: penicillin G, methicillin, ceftaroline, the β-lactam core, thiazolidine, a quorum-sensing inhibitor).
- `unified_demo/output/pdb/*.pdb`: CA-trace PDB models with phi/psi from secondary-structure prediction (e.g. PBP2A domain, a DARPin consensus scaffold), each with HEADER/TITLE/REMARK/ATOM records.
