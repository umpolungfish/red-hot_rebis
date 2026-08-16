# At balance, closure is a non-trivial loop

The balance-zero ob3ect (722795f1) named the discriminant a non-trivial integer
winding number — a loop that cannot be deformed to a point — with ⊞ holding the
balanced pairing where "the distinction lies solely in the closure of the whole, not
in asymmetric composition." Measured, that is exactly the split.

Pair each ∈ to its ∋ under cyclic pairing and count the marks the pair encloses.
Across all 22 balance-zero words of the sweep:

    N   no loop at all (11 words, ∈=∋=0)
    N   one loop enclosing nothing — insulin B chain, ⋈∈∋⊙≻⊙◻≺≻◻⋈⋈≺⊞
    T   at least one loop enclosing work (9 words, smallest enclosure 1 to 3)

The rule is one line: **a balanced word closes iff some fork/fuse pair encloses at
least one mark.** A pair with nothing between it is a loop of zero circumference —
it forks and immediately refuses, deformable to a point, and the word registers N.

3I40 is the proof from inside the corpus. It is the insulin A and B chains
concatenated, and its loops enclose 0, 16 and 25 marks — it carries the B chain's
empty loop and still reads T, because the A chain's loops enclose work. One
non-trivial loop is enough; the empty one does not spoil it. The condition is
existential, not universal.

Confirmed on fresh words against both engines:

    ⊢∈∋⊣            loop encloses 0        tri N   imasm N
    ⊢∈⊤∋⊣           loop encloses 1        tri T   imasm T
    ⊢∈∋∈∋⊣          both loops enclose 0   tri N   imasm N
    ⊢∈∋∈⊤∋⊣         one loop encloses 1    tri T   imasm T
    ⊢⋈∈∋⊙◻⋈⊣        loop encloses 0        tri N   imasm N

The last is the sharpest: six marks of work in the word, all of it outside the loop,
and it does not close. Work adjacent to a fork is not work the fork does. Only what
the loop encloses counts.

The fold law, complete:

    sign of ∈ − ∋   > 0  →  B      surplus fork
                    < 0  →  F      surplus fuse
                    = 0  →  T if some pair encloses a mark, else N

Composition decides the two failures; enclosure decides closure. N is not a failed
fold — it is a fold that never opened. The distinction between N and T is not how
much work a word carries but whether any of it is held inside a division that later
closes, which is what a fold is.

## Correction: the enclosure must be work, not any mark

Stated above as "encloses at least one mark", which is too weak. Of the twelve,
seven do work — ≻ ≺ ⋈ ⊤ ⊥ ⊞ ◻ — and five do not: the two boundaries ⊢ ⊣, the
self-reference ⊙, and the fork and fuse themselves ∈ ∋. A loop enclosing only
no-work marks is still trivial:

    ⊢∈⊙∋⊣        encloses ⊙ alone           tri N   imasm N
    ⊢∈⊙⊙⊙∋⊣      encloses three ⊙           tri N   imasm N
    ⊢∈⊣∋⊣        encloses a boundary        tri N   imasm N
    ⊢∈⋈∋⊣        encloses ⋈, which works    tri T   imasm T
    ⊢∈◻∋⊣        encloses ◻, which works    tri T   imasm T

The law reads: at balance, T if some ∈…∋ pair encloses at least one of the seven
work marks, else N. Re-run over the sweep, the corrected test is still 65 of 65,
and no word in the corpus separates the two readings — every enclosure there that
holds a mark holds a work mark. The distinction is real all the same, and ⊢∈⊙∋⊣
is the witness.

This also sharpens the reading. ⊙ is self-reference and does no work; a fork that
encloses only self-reference has looked at itself and returned. That is N by the
same argument as the empty loop, and it is why N is a fold that never opened rather
than one that failed.
