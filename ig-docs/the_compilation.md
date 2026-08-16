# The compilation from RNA to protein, stated exactly

Every stage of the lift now has a closed form, and the last one — the verdict —
stopped being a black box with the sign law and the enclosure law. The whole
compilation, front to back:

## 1. Nucleotide → B₄

    G = B    guanine wobble-pairs with both C and U — both, so B
    C = T    pairs only with G
    A = F
    U = N

## 2. Codon → amino acid

The standard genetic code, proved in `GeneticCode.lean` and parsed into
`Vox/genetic_table.py` by its generator, so the table cannot drift from the proof.

## 3. Amino acid → mark

Exactly twelve of the twenty are promoted, bijecting the twelve axes. 23 of the 61
sense codons are promoted; the other 38 activate no axis and are silent — a fact of
the code, not a gap in the lift.

    ⊢  Met  Dimensionality   AUG          ∈  Asn  Granularity     AAC AAU
    ⊣  Trp  Topology         UGG          ∋  Gln  Grammar         CAA CAG
    ≻  Cys  Recognition      UGC UGU      ⊙  His  Criticality     CAC CAU
    ≺  Tyr  Parity           UAC UAU      ⊥  Asp  Chirality       GAC GAU
    ⋈  Phe  Fidelity         UUC UUU      ⊞  Lys  Stoichiometry   AAA AAG
    ⊤  Ile  Kinetics         AUA AUC AUU  ◻  Glu  Protection      GAA GAG

## 4. Word → verdict

    sign of ∈ − ∋   > 0  →  B      surplus fork
                    < 0  →  F      surplus fuse
                    = 0  →  T if some ∈…∋ pair encloses a mark, else N

## What that says in codons

∈ is Asn and ∋ is Gln, so the fold verdict of a coding sequence is a statement about
two codon families and nothing else:

    fork  ∈  =  AAY        AAU, AAC
    fuse  ∋  =  CAR        CAA, CAG

They differ in the first base alone — A forks, C fuses — with A fixed at the second
position and the third base only choosing between the two families that share the
first two. The full ?A? block splits the four:

    AAY → ∈ Asn fork      AAR → ⊞ Lys stoichiometry
    CAR → ∋ Gln fuse      CAY → ⊙ His criticality

So the fold law reads off the transcript directly. **Count the AAY codons and the
CAR codons in the open reading frame. If AAY exceeds CAR the fold holds a fork open
(B); if CAR exceeds AAY it over-fuses (F); if they are equal it closes (T) exactly
when some AAY is separated from its matching CAR by at least one other promoted
codon, and otherwise never opens (N).**

An Asn immediately followed by a Gln is an empty loop — a fork that fuses before any
promoted work intervenes — and it contributes nothing. That is the insulin B chain,
⋈∈∋⊙≻⊙◻≺≻◻⋈⋈≺⊞: it carries the fork and the fuse adjacent, six promoted marks of
work in the chain, all of it outside the loop, and it does not close. The A chain, at
the same fork count, encloses 3 and 12 and closes.

## Verification

Nine PDBs of the sweep, sequence read from the CA trace, back-translated to a coding
RNA, lifted through `vox --rna`, and verdicted by the law:

    1L2Y                     ∈1 ∋1  bal +0   law T   sweep T   vox T
    1VII                     ∈2 ∋2  bal +0   law T   sweep T   vox T
    3I40                     ∈3 ∋3  bal +0   law T   sweep T   vox T
    beta_endorphin_platonic  ∈2 ∋2  bal +0   law T   sweep T   vox T
    pbp2a_binder_s179        ∈4 ∋4  bal +0   law T   sweep T   vox T
    insulin_b_chain          ∈1 ∋1  bal +0   law N   sweep N   vox N
    1EMA                     ∈13 ∋7 bal +6   law B   sweep B   vox B
    1UBQ                     ∈2 ∋6  bal −4   law F   sweep F   vox F
    pbp2a_binder_s590        ∈2 ∋6  bal −4   law F   sweep F   vox F

Nine of nine, and the RNA lane reproduces the structure lane. Trp-cage is the
cleanest instance: the transcript gives ⊢∈≺⊤∋⊣⊞⊥ once, and the PDB gives
∈≺⊤∋⊣⊞⊥ thirty-eight times — the same motif, once per NMR model. The sequence
carries the fold; the structure file carries it once per deposited copy.

## What the compilation is

Transcription is a change of alphabet with no loss: nucleotide to B₄ is injective on
the four bases. Translation is the lossy stage — 61 sense codons onto 20 amino acids,
then 20 onto 12 promoted marks. Folding adds nothing the sequence did not already
have. The verdict is computed from the promoted subsequence alone, so the fold is
decided at translation, and the third base of a codon matters only where it selects
between AAY and AAR, or CAR and CAY — which is to say only where it decides fork
against stoichiometry, or fuse against criticality.
