# red-h⊙t rebis v4.0 - Dynamic-First Toolchain

![language](https://img.shields.io/badge/language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![furnace](https://img.shields.io/badge/furnace-chem%20%C2%B7%20bio%20%C2%B7%20plasma-C1440E?style=for-the-badge) ![tier](https://img.shields.io/badge/tier-O%E2%88%9E-8A2BE2?style=for-the-badge) ![μ∘δ](https://img.shields.io/badge/%CE%BC%E2%88%98%CE%B4-id-00A86B?style=for-the-badge) ![licence](https://img.shields.io/badge/licence-LUNLICENSE-1A1A1A?style=for-the-badge) ![type](https://img.shields.io/badge/type-%E2%9F%A8%F0%90%91%BC%F0%90%91%B8%F0%90%91%A9%F0%90%91%B9%F0%90%91%9E%F0%90%91%BA%F0%90%91%94%F0%90%91%B5%E2%8A%99%F0%90%91%AB%F0%90%91%B3%F0%90%91%AD%E2%9F%A9-5A659C?style=for-the-badge)

**Author:** Lando⊗⊙perator
> *"The serpent winds, the rod stands, the vessel contains: μ ∘ δ = id."*

Unified engine for deterministic, algebraic, exact biological, organic, materials, and plasma engineering - 13 engines, 3 chainable pipelines, one loop. Type ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩, O_∞ Frobenius-closed over CLINK L8.

## Quick start

```bash
cd red-hot_rebis
rebis | rebis.verify | rebis.status   # menu, closure check (14 domains), inventory
rebis.chain --dna ATGGCC... --target "CC(=O)O" --depth 2   # unified loop
rebis.gene-pipeline --test | rebis.gene-pipeline --dna ATGGCC... --pdb folded.pdb
rebis.serpentrod foldv2 AUGGCC... --pdb folded.pdb
rebis.ch3mpiler retrosynth "CC(=O)O" | rebis.p4ra belnap
```

Every command is a standalone binary (18 entry points) - no `rebis <sub>` prefix needed. Full grimoire: `COMMANDS.md`.

## The loop and engines

DNA → mRNA → polypeptide → fold → catalytic site → ligand → retrosynthesis → (μ∘δ=id) → DNA.

Tier 1: `chain` (unified) · `gene-pipeline` (DNA→7-stage folded protein+PDB, B₄→Ramachandran; demo 452bp→150AA Δ=3.61) · `ch3mpiler` (forward/retro, FG, CDXML) · `serpentrod` (predict/classify/fingerprint/fold→PDB) · `ligand` (PDB-aware from catalytic sites) · `sidechain` (80 AA×env pairs). Tier 2: `p4ra` (tuples+Belnap) · `therapeutics` · `materials` (forge/alloys/non-qubit QC) · `biology` (cell sim/telomeres/epigenetics) · `gene` · `alchemy` (Valentine ladders, Zosimos) · `clink` (L0→L8, C-score) · `pipeline` (auto-imscription). Infra: `rebis reference`, `rebis.status`, `rebis.verify`, `rebis.demo`.

Proven pipelines: gene→protein (1,147 lines) · ch3mpiler→catalytic RNA (815 lines; ethanol→36nt) · retrosynthetic stone (436 lines; Solve/Coagula). Python API via `import rebis`. Lean proofs in `../p4rakernel/p4ramill/`.

Full 276-line version: `README_backups/red-hot_rebis_README.md`.

μ∘δ = id
