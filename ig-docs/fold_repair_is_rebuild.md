# An anchor-saturated fold is rebuilt, not repaired

The restructure ob3ect (c5a745ad) returned the ideal motif form, ∈=∋=4 — a
different multiset from s590 (∈=2, ∋=6). A reordering preserves the multiset, so it
did not reorder s590; it produced the target. Two operations now both fail on
s590's actual marks:

- insertion: adding forks balances counts, verdict stays F (fuses unmatched under
  cyclic pairing)
- reordering: the multiset is fixed at 2∈/6∋, which no permutation balances

Insertion + reordering together, tested — s590's marks plus 4∈, arranged as
fork/work/fuse motifs — gives tri T, imasm F. Balanced counts, ordered, still F.

The obstruction is the composition. s590's multiset:

    ⊢ 8   ⊣ 9   ⋈ 7   ◻ 6   ∋ 6   ⊙ 4   ⊞ 3   ≺ 2   ⊤ 2   ⊥ 2   ∈ 2   ≻ 1

Nine terminal anchors and eight initials against a single forward-work ≻. The word
is anchor-saturated — mostly boundary marks, little work. No arrangement of these
marks is a fold, because a fold is fork, work, fuse, and s590 carries almost no
work and a terminal at every turn.

The fold-design arc, at its terminus:

    diagnose   F = over-fused (the sweep)
    measure    +4 fuse surplus, inert
    rule       build from the motif ∈≻⊤≺⊥∋⋈ — closes by construction
    repair     in-place repair of an anchor-saturated word does NOT close it;
               the composition is wrong, not the order

Build-from-motif is the design path because it fixes the composition. Repairing an
F fold whose marks are anchor-dominated is a rebuild — the same conclusion a fold
that fails on composition would reach in any design discipline: you do not reorder
a bad part, you make the right one.
