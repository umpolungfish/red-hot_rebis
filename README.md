# Red-Hot Rebis

Primitive labels and tuple keys use `⊢ ⊣ ≻ ≺ ⋈ ⊤ ∈ ∋ ⊙ ⊥ ⊞ ⊡`, in that order, with the Shavian values defined in [`SNS_PRIME.md`](../SNS_PRIME.md).

Red-Hot Rebis connects the Imscribing Grammar's protein, molecular, materials and lattice tools through Python APIs and command-line programs. Its protein workflow carries the amino-acid self-marks and native protein glut from translation through folding, catalytic coupling and ligand generation. The live Lean definitions supply its tuple operations and promoted-residue correspondence.

## Setup

Run from the `red-hot_rebis` checkout:

```bash
uv pip install -e .
rebis --help
rebis.status
```

The protein paths require the sibling `Vox`, `p4rakernel/p4ramill` and `ob3ect` checkouts. Full amino-acid records are read from `../ob3ect/digital/*_as_peptide_component/`. Install `rustc` for the source-bound Vox adapter and make `lake` and the project's Lean environment available for operation-table export. Ligand and molecular generation also require RDKit in the active Python environment.

## RNA to protein and ligand

These examples use the RNA from the integrated execution receipt. It translates to `MARNDCEGHILKYPQSTVWF`, covering all twenty amino acids.

```bash
rna=AUGGCUCGUAAUGAUUGUGAAGGUCACAUUCUUAAAUAUCCUCAAUCUACUGUUUGGUUUUAA
rebis.serpentrod fold "$rna"
rebis.serpentrod foldv2 "$rna" --pdb folded.pdb
rebis.gene-pipeline --seq "$rna" --pdb protein.pdb
rebis.ligand --pdb-file protein.pdb --active Asp5,Glu7 --improved --json
rebis.chain --seq "$rna" --target 'CC(=O)O' --depth 1 --pdb chain.pdb
```

The unified chain passes the gene's existing protein carrier into catalytic coupling. The target supplies context to that carrier. Source sequence, chemical forms, word executions, contact relations and earlier observations remain attached to the return.

| Output | Contents |
|---|---|
| `protein.pdb` | Coordinate readout with backbone and sidechain atoms; REMARK 900 carries geometry observations and REMARK 901 identifies the native carrier and sources. |
| `protein.pdb.glut.json` | Complete resident carrier bound to the PDB's SHA-256. Keep it beside the PDB when passing the structure to ligand generation. |
| `chain.pdb.chain.json` | Protein, catalytic coupling, retained ligand family/candidates and synthesis results. The chain's PDB sidecar is refreshed with the same final carrier. |

Ligand JSON returns `protein_glut`, `site_family`, `ligand_family` and candidates with `source_forms`. Each residue/form branch retains its ancestry. The scalar site tuple is an explicitly named first-source-form readout.

## Full amino-acid words through Vox

```bash
rebis.vox peptide MARNDCEGHILKYPQSTVWF --json
rebis.vox rna "$rna" --json
rebis.vox peptide AGPSTVLR --json
```

All twenty residues execute their full IMASM self-marks on grounded tuple payloads. Asp and Glu retain acid and ion forms, giving twenty-two source records. Each form keeps its own word execution and irreversible-fix boundary. The twelve promoted-primitive annotations remain a separate view supplied by Lean.

Protein B is the native carrier condition. Observational N/T/F/B evidence stays separately attached. Chemical forms, configured torsion alternatives and competing assembly proposals remain co-held without probability weights. Exported coordinates are a named boundary readout.

## Verification and current testing scope

```bash
python3 measurements/resident_glut_integration_20261020/run.py
```

The integrated runner covers legacy folding, processing, Gen2 geometry, the gene pipeline, PDB export, sidechain/environment composition, both PDB ligand APIs, shared catalytic coupling and installed commands. It checks source-form retention, candidate ancestry, coding-source mismatch rejection and equality of the final chain and sidecar carrier. Its source-bound receipt and command logs are saved beside the runner.

The representative coverage campaign additionally ran 30 complete UniProt chains across seven organisms, from 97 to 1,464 residues, through Vox protein/RNA input, legacy folding, Gen2 and the gene pipeline. Sequence/form retention and exported coordinate agreement passed across the tested routes. RNA inputs were canonical reverse translations of the downloaded proteins. All 30 cases retain coordinate clashes; 20 also report angle conflicts. This measures compiler behavior and geometry predicates; reference-structure folding accuracy remains unmeasured. See the [coverage matrix and receipts](../ig-docs/protein_global_coverage_20261020.md). Import checks (`rebis.verify`) report package availability.

## Documentation

- [User guide](../ig-docs/red-hot-rebis-user-guide.md)
- [Command reference](COMMANDS.md)
- [Resident carrier implementation and execution](../ig-docs/rebis_native_protein_glut_20261020.md)
- [Executable inventory and original assessment](../ig-docs/rebis_executable_assessment_20261020.md)

Use `rebis` for the command menu, or `python3 -m rebis` from the checkout. Installed `rebis.<name>` commands are also available directly. Lean ground truth lives in `../p4rakernel/p4ramill/Imscribing`.
