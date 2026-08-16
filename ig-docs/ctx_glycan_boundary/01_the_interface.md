# The glycopeptide boundary interface, and what is already grounded

A glycopeptide is a boundary interface in the corpus's own sense: the peptide is
the bulk, the glycan is the environment-facing boundary, and the sequon is the seam
between them. Three layers, and only the first two are grounded.

## Grounded already

**The peptide (bulk).** `vox aa | fasta | pdb` lifts an amino-acid sequence to a
word in the twelve. The twelve promoted amino acids biject the twelve axes
(Met Trp Cys Tyr Phe Ile Asn Gln His Asp Lys Glu), Lean-derived, and this map
agrees with red-hot_rebis's own AA→primitive table.

**The interface (seam).** `vox glyco` locates the sites. N-linked sequons are
determinate — Asn-X-[Ser/Thr], X≠Pro — and Asn is ∈, the recognition gate, so an
N-site is an ∈ in the peptide word that opens a sequon. O-linked candidates
(Ser/Thr) are ground-layer and carry no mark, so they are invisible in the word: a
fact of the code, reported as such.

**The functional-group grammar.** `imas/fg_exhaustive.py` maps a SMARTS functional
group to one of the twelve opcodes with a rank — e.g. `saccharide_oh` (`[CX4][OX2H]`,
a sugar OH) → EVALT. So a molecule's functional-group census already produces marks
through a grounded route, never a hand table.

## Not grounded — the frontier

**The glycan (boundary).** A glycan is a BRANCHED tree of monosaccharides, not a
linear chain. Its natural reading is a fork/fuse topology: the reducing end (bonded
to Asn) is the anchor, each branch point is a split, each terminus a leaf. The
monosaccharides of mammalian N-glycans are a small set — GlcNAc, GalNAc, Mannose,
Galactose, Glucose, Fucose, Sialic acid (NeuAc), Xylose — each a ring carrying a
characteristic set of functional groups (ring O, several OH, and for GlcNAc/GalNAc
an N-acetyl, for NeuAc a carboxyl).

Because each monosaccharide is a molecule, its grammar type is DERIVABLE from its
functional groups through the chem pipeline — not stipulated. That derivation is
what is missing, and it is the whole of what these asks are for.
