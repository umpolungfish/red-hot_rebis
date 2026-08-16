# The census is a sign, not a proportion

The composition-census ob3ect (1c111c59) typed the diagnostic as a boundary/work
proportion with a critical ratio at ⊙ and the threshold held as B at ⊞. Measured
across the 65-word PDB sweep, the proportion does not separate the verdicts. Every
definition of boundary versus work overlaps:

    anchors ⊢⊣ / work ≻≺⊤⊥⊙◻     T 0.000–0.750   F 0.050–1.000   N 0.000–1.000
    ⊢⊣⋈ / work                    T 0.000–1.750   F 0.150–1.412   N 0.167–1.500
    ⊢⊣⋈⊞ / work                   T 0.000–3.000   F 0.375–1.588   N 0.167–2.000

What does separate them, on all 65 words with no exception, is the sign of a single
difference — fork count minus fuse count:

    ∈ − ∋ > 0   →  B     22 of 22
    ∈ − ∋ < 0   →  F     21 of 21
    ∈ − ∋ = 0   →  T or N (9 T, 13 N)

The magnitude carries nothing: B runs +1 to +36 and F runs −1 to −5, and the verdict
is the same across each range. It is the sign alone. Surplus fork is B, surplus fuse
is F, and only balance can close.

Balance is necessary for T, not sufficient. The sweep's balance-zero words split
9 T / 13 N, and the census does not decide which. Where the census does decide: a
word with no forks and no fuses at all (∈=∋=0) is N in every case — nothing was
split, so nothing closes. The remaining T/N split at ∈=∋≥1 is not a composition
question; ⊢∈⊤∋⊣ is T while the sweep's insulin_b chain at the same counts is N, so
the discriminant there is arrangement, which is where order re-enters.

This corrects the anchor-saturation reading of s590 (fold_repair_is_rebuild.md).
s590 is F because ∈−∋ = −4, not because ⊢ 8 / ⊣ 9 / ⋈ 7 outweigh its single ≻. The
anchor counts are real but they are not the discriminant — anchor-heavy words appear
at every verdict. The rebuild conclusion stands on the arithmetic that was already
there: insertion could not fix the sign under cyclic pairing and reordering cannot
change a multiset's sign at all.

The census, stated whole: read ∈ − ∋. Its sign is the verdict for the two failing
cases, and zero is the entry condition for closure. Order decides only what happens
inside a balanced word.
