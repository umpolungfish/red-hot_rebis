# RED-HOT REBIS CORPUS RUN — SUMMARY
200 real sequences (100 RNA + 100 proteins, UniProt/GenBank) run through the rebis engine tree, 2025-08-23.

## Engines run (per record)
| Engine | Corpus | Count | Status |
|---|---|---|---|
| rebis.serpentrod predict (stratified processing) | proteins | 100 | 100/100 ok |
| rebis.gene tuples (IG tuple derivation) | proteins | 100 | 100/100 ok |
| rebis.gene tuples | RNA | 100 | 100/100 ok |
| rebis.py predict (p4ra physical prediction from tuple) | proteins | 100 | 100/100 ok |
| rebis.py predict | RNA | 100 | 100/100 ok |
| rebis.serpentrod foldv2 (RNA→protein→PDB) | RNA | 100 | 100/100 ok (100 PDBs) |
| rebis.gene-pipeline (RNA→protein, ΔG) | RNA | 100 | 100/100 ok |
| serpentrod/protein_v5.py (v5 enhanced) | proteins | 100 | 100/100 ok |
| rhr_p4rky.serpent_rod_v2 (kernel) | proteins | 3 | 3/3 ok |
| rhr_p4rky.gene_to_protein_pipeline (kernel) | RNA | 3 | 3/3 ok |

## Cross-engine sample sweep (data/corpus_run/engines/)
materials forge (protein+RNA tuples), alchemy ladder + portico, biology sim, therapeutics design EGFR + neurotrophic BDNF, clink cscore (protein tuple + representative_sequence_corpus), clink bridge, rebis.chain unified loop (2 RNA → protein → ligand → retrosynth, target acetic acid) — all rc=0.

## Distribution findings
- distinct IG tuples: 2/100 proteins, 3/100 RNA
- foldv2 energy total (LJ-dominated): min -3.947, median 5.104, max 8.18e14; 76/100 records <1e6 (mean 2.2e4); 20/100 negative. Extreme positives are genuine LJ terms from long structured ncRNA folds.
- winding: min 11 mean 273 max 842
- frobenius=true: 61/100 | activation: min 0 mean 5 max 12
- clink cscore(representative_sequence_corpus) = 1.0, tier O_∞

## Files
- proteins_summary.tsv, rna_summary.tsv (this directory)
- json/: per-record engine outputs (806 files)
- pdb/: 100 folded RNA-derived protein PDBs
- proteins/, rna/: per-record FASTA


## Verification note
Energy distribution verified against raw foldv2.json (LJ term drives extremes; not an extraction artifact).
