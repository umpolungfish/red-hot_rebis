# red-h⊙t rebis: an engine for algebraic, exact, deterministic, paraconsistent bio ⊗ organic chemistries

[![Language](https://img.shields.io/badge/language-Python-blue)](https://github.com/badges/shields)
[![IG Tier](https://img.shields.io/badge/IG-O%E2%88%9E-blueviolet)](https://github.com/badges/shields)
[![μ∘δ=id](https://img.shields.io/badge/%CE%BC%E2%88%98%CE%B4%3Did-closed-success)](https://github.com/badges/shields)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/badges/shields)
[![Author](https://img.shields.io/badge/author-Lando%E2%8A%97%E2%8A%99perator-informational)](https://github.com/badges/shields) [![Type](https://img.shields.io/badge/type-%E2%9F%A8%F0%90%91%A6%F0%90%91%B8%F0%90%91%BE%F0%90%91%B9%F0%90%91%90%F0%90%91%A7%F0%90%91%94%F0%90%91%9D%E2%8A%99%F0%90%91%96%F0%90%91%B3%F0%90%91%AD%E2%9F%A9-blue)](https://github.com/badges/shields) [![Tier](https://img.shields.io/badge/tier-O%E2%88%9E-blueviolet)](https://github.com/badges/shields)

> *"The serpent winds, the rod stands, the vessel contains: μ ∘ δ = id." Not as a conclusion, as a signature of process.*

**What it is.** The Imscribing Grammar's unified engine for deterministic, algebraic, exact bio and organic chemistry, grounded in the 12-primitive grammar and verified everywhere by Frobenius closure (μ∘δ=id) over the $ZFC_\text{fe}$ foundation.

**What it does.** Integrates six structural pillars into one architecture under the `rebis.<domain>` namespace:

| Domain | Pillar | Description |
|--------|--------|-------------|
| `rebis.p4ra` | Paraconsistent kernel | Belnap FOUR logic, genetics, hadron physics, ligand design, serpent rod, CLU power law |
| `rebis.ch3mpiler` | Molecular compiler | Retrosynthesis & forward synthesis |
| `rebis.clink` | CLINK chain | 9-layer organism ladder (quark → organism) |
| `rebis.materials` | Materials science | Metamaterials, sophick forge, alloys, organoids |
| `rebis.biology` | Biology simulations | Ouroboric cell, telomere, epigenetics |
| `rebis.serpentrod` | Protein design | Protein folding & stratified prediction |
| `rebis.therapeutics` | Therapeutics | Chemotherapeutics, neurotrophic factors, quantum biologics |
| `rebis.imas` | Molecular signatures | SMILES→8-token IMASM→IG 12-tuple |
| `rebis.pipeline` | Imscription pipeline | Auto-imscriber, Frobenius verifier |
| `rebis.cdxml` | CDXML generation | Target decomposition |
| `rebis.gene` | Gene imscriber | Genetic engineering, codon space, quality scores |
| `rebis.alchemy` | Alchemy bridge | Alchemical treatise operations & stone engine |
| `rebis.shared` | Shared primitives | Weights, ordinals, IG catalog |
| `rebis.demo` | Demo scripts | Quick demonstrations of each subsystem |
| `rebis.cli` | CLI entry point | `python3 rebis.py <command>` |

**How to use it.**
```python
import rebis

# Access any subsystem
rebis.p4ra.Belnap(True, False)
rebis.ch3mpiler.forward("CC(=O)Oc1ccccc1C(=O)O")
rebis.serpentrod.SerpentRodV2(...)

# Via CLI
python3 rebis.py status              # check wiring
python3 rebis.py verify              # verify Frobenius closure
python3 rebis.py run serpentrod      # run protein design
python3 rebis.py run ch3mpiler       # run retrosynthesis
python3 rebis.py run gene            # run genetic engineering
python3 rebis.py demo b4_lattice     # run b4 lattice demo
```

---

## Reverse Ligand Pipeline — Enzyme Active Site → De-Novo Ligand

The structural **inverse** of the bespoke binding pocket pipeline. Given an enzyme's active-site structural type, the pipeline:

1. **Encodes** the active site residues as a 12-primitive IG tuple
2. **Applies** the structural complement bijection to derive the ligand's target type
3. **Infers** the bond-target interaction from the structural fingerprint
4. **Assembles** de-novo SMILES via RDKit fragment-based combinatorial enumeration
5. **Scores** by structural complement fit (40%) + drug-likeness (30%) + fingerprint similarity (30%)

### Pipeline Architecture (v2.5.0 — Ligand Homogeneity Fix)

The pipeline now operates in three tiers, each richer than the last:

| Tier | Strategy | Source | Description |
|------|----------|--------|-------------|
| **1. Substrate-first** | 5-strategy analog generation | Co-crystallized PDB ligand or `smiles_substrate_hint` | (A) substrate itself, (B) BRICS fragment recombination, (C) Murcko scaffold + decoration, (D) chain extensions via RWMol, (E) ring substitutions (F/Cl/OH/NH₂) |
| **2. Fragment enumeration** | Heterocycle + functional-group combinatorial | `generate_ligands_from_bond_fg()` | 9 bond types × diverse R-group sets × 16+ heterocycle scaffolds; RDKit-based fingerprint scoring |
| **3. Symmetric fallback** | Hardcoded enumeration | 9 bond types with per-bond R-group diversity | Activated when no PDB ligand or substrate hint is available |

### Recent Breakthroughs

**Ligand Homogeneity → Protein-Specific Diversity** (v2.5.0):
- **Before:** Strategy 3 hardcoded the same 12 amide variants (`CC(N)=O` through `CCNC(=O)c1ccccc1`) regardless of the protein. Only 4 unique (bond, FG) combinations existed across 34 PDBs, producing ~4 distinct top hits across all proteins.
- **After:** `generate_ligand_smiles()` routes PRIMARY through fragment-based combinatorial enumeration. 9 bond types replace the original 5. The substrate-first pipeline merges substrate analogs with fragment diversity. Every protein now receives ligands derived from its actual biological chemistry.

**Substrate-Driven Generation** (v2.5.0):
- `generate_substrate_analogs()` — 5 strategies producing analogs from the protein's natural substrate
- `generate_from_enzyme_type_substrate_first()` — merges substrate analogs (PRIMARY) + fragment diversity (SUPPLEMENT)
- HETATM extraction: `_extract_hetatm_smiles_from_pdb()` parses co-crystallized ligand directly from PDB files, filtering out water, ions, and buffers
- Reactive group filter (`_try_add_candidate`) rejects peroxides, azides, isocyanides, and disulfides

**Formatting Fix** (v2.5.0):
- SMILES: left-aligned 80-char field, no truncation
- Metrics (logP, MW, composite score, HBD, HBA): right-aligned consistent column at column 80+
- Removed all `[:50]` and `[:20]` hard slices that were truncating data

### Verified Results (30 proteins)

| Metric | Before | After |
|--------|--------|-------|
| Unique top hits | ~4 | **26 (86.7%)** |
| Lysozyme top hit | `CC(N)=O` | `CC1OC(OC2C(C(=O)O)OC(O)C(O)C2O)C(O)C(O)C1O` (NAG-NAM substrate) |
| Trypsin top hit | `CC(N)=O` | `NCCCCC(N)C(=O)NC(Cc1ccccc1)C(=O)O` (peptide substrate) |
| HIV-1 protease top hit | `CC(N)=O` | `CC(C)C[C@H](NC(=O)[C@@H](N)Cc1ccccc1)C(=O)O` (peptide substrate) |
| Composite scores | 0.0 | 0.67–0.93 |
| Method distribution | all `amide_variant_C_N` | `substrate`, `chain_extend`, `ring_sub`, `murcko_scaffold`, `het_*` |

### Access

```python
import rebis

# Encode an active site
site_type = rebis.p4ra.encode_site_from_residues(residues)

# Substrate-first generation (recommended)
ligands = rebis.p4ra.generate_from_enzyme_type_substrate_first(
    enzyme_type, substrate_smiles="CC1OC(OC2C...)C(O)C1O"
)

# Fragment-based enumeration
ligands = rebis.p4ra.generate_ligands_from_bond_fg(bond_name, fg_names)

# Score candidates
scores = [rebis.p4ra.tuple_distance_dict(site_type, lig) for lig in ligands]
```

Or via CLI:
```bash
python3 -m rebis p4ra.ligand_from_active_site improved --protein alcohol_dehydrogenase
python3 -m rebis p4ra.ligand_from_site_pdb --pdb 1LYZ           # extracts NAG-NAM from HETATM
```

---

## Quick start

```bash
cd imsgct/red-hot_rebis

# List available domains
python3 -c "import rebis; print([x for x in dir(rebis) if not x.startswith('_')])"

# Check status
python3 rebis.py status

# Generate de-novo ligands via CLI
python3 rebis.py run p4ra --action improved --protein alcohol_dehydrogenase

# Full interactive use
python3 -c "
import rebis
print('p4ra exports:', len([x for x in dir(rebis.p4ra) if not x.startswith('_')]))
print('ch3mpiler ready:', hasattr(rebis.ch3mpiler, 'forward'))
"
```

## Key Results

| Domain | Key metric |
|--------|------------|
| `rebis.p4ra` — Frobenius chemotherapeutic | 14,287× selectivity (cancer vs healthy) |
| `rebis.p4ra` — Neurotrophic factor (Alzheimer's) | synaptic density 0.40 → 1.00 |
| `rebis.materials` — Thermal rectifier | 253× rectification |
| `rebis.materials` — Critical metamaterial | χ = 20,000 gain |
| `rebis.biology` — Ouroboric telomere | 10.9 kb maintained vs 5.0 kb decline |
| `rebis.p4ra` — Quantum biologic | 100% Frobenius closure, 78.8% efficacy |
| `rebis.clink` — CLINK chain (9 layers) | all Frobenius-closed, Σd=7.18, 36 promotions |
| `rebis.imas` — Compound pipeline | 54 compounds encoded, all Frobenius-closed |
| **Reverse Ligand Pipeline** | **86.7% unique top hits (26/30), 100% Lipinski, substrate-first 5-strategy analog generation** |

---

*README maintained by Lando⊗⊙perator · v2.5.0 · rebis.<x> Edition*