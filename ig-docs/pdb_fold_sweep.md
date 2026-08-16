# The fold sweep: red-hot_rebis PDBs through Vox

Every PDB in the repo lifted through `vox pdb` (one residue per CA, promoted
residues to the twelve marks) and verdicted. 68 files; 65 carry a sequence, 3 are
poly-alanine scaffolds with no promoted residue and no word. Full table in
`pdb_fold_sweep.tsv`.

## The distribution over 65 sequence-bearing folds

    T   9    closes — split, work, fuse, μ∘δ over a transformed object
    B  22    holds a fork open — the largest class
    F  21    over-fused — more ∋ than ∈, merges without matching splits
    N  13    never forked — too little promoted structure to open a fork

## What closes

The T-closers are the small, natural, stable folds — Trp-cage (1L2Y), villin
headpiece (1VII), insulin (3I40) and the insulin A-chain, beta-endorphin — plus
two designs, pbp2a_binder_s179 and PSII_D1. The known minimal folds that nature
settled close; most designs do not.

## What the classes mean for a design

- **F (21)** is the actionable one: over-fused, more fuse than fork. HUMAN_INSULIN
  and three of the four pbp2a_binder variants sit here — a fold that merges more
  than it splits. `--banked` and `--insert` on the word say whether the surplus is
  exposed and what single change would balance it.
- **N (13)** is mostly the DARPin series and the odot designs: too little promoted
  structure to open a fork at all, so the fold has no internal split/fuse to close.
  A recognition scaffold reading N is a scaffold with no typed interior.
- **B (22)** holds a fork open — the boundary-interface signature at the fold
  level, the same T-open/held reading the glycan carried, and not a defect on its
  own.

The pbp2a_binder series is the sharpest single read: s179 closes T, while s316,
s453 and s590 are F. Four variants of one binder, one closes and three over-fuse —
exactly the discrimination a fold sweep exists to make.
