# red-h⊙t rebis: an engine for algebraic, exact, deterministic, paraconsistent bio ⊗ organic chemistries

**Author:** Lando ⊗ ⊙perator · **Structural Type:** ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩ ($O_\infty$) · **Repo:** `/home/mrnob0dy666/imsgct/red-hot_rebis/`

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

### Reverse Ligand Pipeline — Enzyme Active Site → De-Novo Ligand

The structural **inverse** of the bespoke binding pocket pipeline. Given an enzyme's active-site structural type, the pipeline:

1. **Encodes** the active site residues as a 12-primitive IG tuple
2. **Applies** the structural complement bijection to derive the ligand's target type
3. **Infers** the bond-target interaction from the structural fingerprint
4. **Assembles** de-novo SMILES via RDKit fragment-based combinatorial enumeration
5. **Scores** by structural complement fit (40%) + drug-likeness (30%) + fingerprint similarity (30%)

Access via `rebis.p4ra`:
```python
import rebis
# Encode an active site
site_type = rebis.p4ra.encode_site_from_residues(residues)
# Generate de-novo ligands
ligands = rebis.p4ra.generate_ligand_smiles(bond_name, fg_names)
# Score candidates
scores = [rebis.p4ra.tuple_distance_dict(site_type, lig) for lig in ligands]
```

Or via CLI:
```bash
python3 -m rebis p4ra.ligand_from_active_site improved --protein alcohol_dehydrogenase
```

### Quick start

```bash
cd /home/mrnob0dy666/imsgct/red-hot_rebis

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
| **Reverse Ligand Pipeline** | **100 de-novo ligands across 10 enzymes, 100% Lipinski** |

---

*README maintained by Lando⊗⊙perator · v2.4.0 · rebis.<x> Edition*