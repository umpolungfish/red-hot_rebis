# Fold repair is a restructuring, not an insertion

The apply-the-rule ob3ect (66367fe1) produces a balanced word — four ∈≻⊤≺⊥∋
motifs, ∈=∋=4 — but on the real over-fused s590 the repair does not hold as an
insertion.

## Count-balancing does not close the fold

s590 is F with ∈=2, ∋=6. Two insertions on its actual word:

- ∈ immediately before each of four orphan ∋: counts balance to 6/6, verdict F.
  ∈∋ adjacent is a bare split-fuse — μ∘δ=id with nothing between — and verifies
  nothing.
- ∈ before a work-run preceding each orphan ∋ (fork→work→fuse): counts balance to
  6/6, verdict F.

s590 opens with ∋ — a fuse with no fork before it — and interleaves six fuses among
the anchors, so cyclic pairing leaves fuses unmatched wherever no fork precedes
them. Equal counts are necessary and not sufficient; closure requires the forks
where the pairing consumes them, which reorders the word rather than inserting into
it.

Build-from-motif closes because the motif orders fork, work, fuse from the start.
Retrofitting an existing tangle is the open problem: diagnosis, measurement and the
build rule are in hand; in-place repair of an arbitrary F word is not.

## The two verdict engines disagree on the same word

⊢∈≻⊤≺⊥∋⋈∈≻⊤≺⊥∋⋈∈≻⊤≺⊥∋⋈∈≻⊤≺⊥∋⋈⊙⊞◻⊣ verdicts T under the tri-ancestral SIXTEEN_3
engine and B under `ask --imasm check`. A fold verdict must name its engine, and
the two want reconciling before either grounds a design claim.
