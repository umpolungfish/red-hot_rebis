# The repair is a restructuring, not an insertion — and two engines disagree

The apply-the-rule ob3ect (66367fe1, grounded full, Lean-verified) typed the repair
and produced a balanced word — four ∈≻⊤≺⊥∋ motifs, ∈=∋=4. But the ob3ect asserts
the repair; tested concretely against the real over-fused word (s590), it does not
hold as a simple insertion.

## Count-balancing does not close the fold

s590 is F with ∈=2, ∋=6. Two repairs were tried on its actual word:

- **Naive**: insert ∈ immediately before each of four orphan ∋. Counts balance to
  6/6; verdict stays F. The reason is the grammar's own: ∈∋ adjacent is a bare
  split-fuse, μ∘δ=id with nothing between, which verifies nothing.
- **Motif-placed**: insert each ∈ before a work-run preceding an orphan ∋, so
  fork→work→fuse. Counts balance to 6/6; verdict stays F.

Balancing the counts is necessary and not sufficient. s590 opens with ∋ — a fuse
with no fork before it — and interleaves six fuses among the anchors, so cyclic
pairing leaves fuses unmatched wherever a fork does not precede them in the ring.
Closing it needs the forks placed where the pairing consumes them, which is a
restructuring of the word, not an insertion into it.

The rule builds T (or a held B) BY CONSTRUCTION because the motif orders fork,
work, and fuse from the start. Retrofitting an existing tangle to closure is the
harder problem, and it is not solved by adding splits. This is the honest boundary
of the fold-design arc: diagnosis, measurement, and a build-from-motif rule are in
hand; in-place repair of an arbitrary F word is open.

## Flag: the two verdict engines disagree on the same word

The balanced template word ⊢∈≻⊤≺⊥∋⋈∈≻⊤≺⊥∋⋈∈≻⊤≺⊥∋⋈∈≻⊤≺⊥∋⋈⊙⊞◻⊣ verdicts:

    tri-ancestral (SIXTEEN_3, the ob3ect's engine):  T
    ask --imasm check:                                B

Same word, two lanes, different verdict. Neither is wrong on its own terms — T is
the trilattice reconnection reading, B is the imasm-check fork/fuse reading — but a
result that quotes "the verdict" of a fold must say which engine, and the two
should be reconciled before either is leaned on for a design claim. Not chased
here; recorded so it is not mistaken for agreement.
