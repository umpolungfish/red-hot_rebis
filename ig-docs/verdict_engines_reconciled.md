# The two verdict engines split only at ⊞

The engine-reconciliation ob3ect (9ebd366d) typed the reconciler as ⊙ criticality
under cyclic closure. Tested across words, the condition is exact: the two engines
agree on every word that contains no ⊞ (ENGAGR), and split only where ⊞ is present.

    ⊢∈⊤∋⊣            tri T   imasm T   agree
    ⊢∈≻⊤≺⊥∋⋈⊙◻⊣      tri T   imasm T   agree
    ⊢∈⊤∋⊞⊣           tri T   imasm B   split
    ⊢∈≻⊤≺⊥∋⋈⊙⊞◻⊣     tri T   imasm B   split

Adding ⊞ to an agreeing word flips imasm-check T→B while the tri-ancestral verdict
holds at T; removing it restores agreement. Motif repetition and count balance do
not move it — a balanced four-motif word agrees T/T with ⊙◻ and splits T/B with
⊙⊞◻.

⊞ engages a dialetheia — a B held at both arms. The imasm-check lane surfaces the
held B; the tri-ancestral lane reports the T of the closure the B sits inside. The
split is not a discrepancy in the structure. It is the two faces of an engaged B: B
is both T and F, and each lane names one face. Absent ⊞ there is no held paradox
and the verdict is single.

Condition for a fold verdict: if the word contains ⊞, name the lane — imasm-check
reports the paradox (B), tri-ancestral reports the enclosing closure (T). If it
does not, the two agree and the verdict stands alone.
