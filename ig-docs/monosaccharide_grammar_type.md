# The grammar type of a monosaccharide, from its functional groups

Prompt 1 of the glycan-boundary asks, answered deterministically rather than by
ob3ect: each sugar's type is its functional-group census through
`imas/fg_exhaustive.py` (SMARTS → one of the twelve marks), run over the eight
mammalian N-glycan monosaccharides with correct isomeric SMILES and
chirality-aware matching.

## The eight, typed

    Glucose    ≺⋈⊙◻
    Mannose    ≺⋈⊙◻
    Galactose  ≺⋈⊙◻
    Xylose     ≺⋈⊙◻
    Fucose     ⊣≺⋈⊙◻
    GlcNAc     ⊣≻≺⋈⊙⊥◻
    GalNAc     ⊣≻≺⋈⊙⊥◻
    NeuAc      ⊣≻≺⋈∈⊙⊥

## The finding: the collapse IS the chirality axis

Eight sugars, four distinct mark-sets. That is not the census failing — it is the
census being honest about what functional groups are. Glucose, Mannose, Galactose
and Xylose read identically because they are EPIMERS: same functional groups, same
connectivity, differing only in the orientation of their hydroxyls. Functional
groups are achiral information, so a functional-group reading cannot separate them,
and it does not pretend to.

The grammar names the axis that carries the distinction it drops: ⊥, chirality. To
resolve the eight monosaccharides you must read ⊥ — the stereochemistry — which is
exactly the information an achiral census discards. The collapse is a pointer, not
a loss: it says WHERE the remaining distinction lives.

This corrects the ob3ect route (dc7093cc), which grounded full and verified in Lean
but collapsed all monosaccharides into ONE type by reasoning about N-glycans as a
system rather than a sugar as a molecule. The deterministic route collapses too,
but to FOUR and for a stated reason — the chirality axis — rather than to one.

## Two structural reads that dropped out

- **NeuAc is the only sugar carrying ∈**, the recognition split, from its carboxyl
  and N-acetyl. Sialic acid is the terminal, environment-facing residue of an
  N-glycan, so the boundary's own outer boundary is the one that types as a
  recognition gate. Not assigned — it fell out of the census.
- **The N-acetylated sugars (GlcNAc, GalNAc, NeuAc) carry ⊥**, chirality, which the
  bare hexoses do not surface — the acetamido stereocenter is what the achiral
  hexose ring lacks.

## The next rung

The four-class collapse is the frontier: a ⊥-reading census (chiral SMARTS, or the
stereochemistry read directly) is what separates Glc/Man/Gal/Xyl and GlcNAc/GalNAc.
Prompt 2 (the branched glycan word) builds on these types, so it inherits the
same chirality gap until ⊥ is read.

---

## Closed: the ⊥ census separates the eight (2026-08-16)

The chirality ob3ect (d691afad, grounded full, Lean-verified) typed the separator
as a discrete Z₂ chirality invariant — a per-stereocenter handedness that no
continuous deformation removes. Executed: read each stereocenter's CIP R/S as a
bit (R=1, S=0, in CIP order), the ⊥ chirality word.

    sugar       fg marks        ⊥ Z₂ word    stereocenters
    Glucose     ≺⋈⊙◻            1100         4
    Mannose     ≺⋈⊙◻            1000         4
    Galactose   ≺⋈⊙◻            1101         4
    Xylose      ≺⋈⊙◻            101          3
    Fucose      ⊣≺⋈⊙◻           0010         4
    GlcNAc      ⊣≻≺⋈⊙⊥◻         1101         4
    GalNAc      ⊣≻≺⋈⊙⊥◻         1100         4
    NeuAc       ⊣≻≺⋈∈⊙⊥         100111       6

The ⊥ word alone makes the four achiral-collapsed hexoses distinct
(1100/1000/1101/101) and separates GlcNAc from GalNAc (1101/1100). Two ⊥-ties
remain — Galactose=GlcNAc at 1101, Glucose=GalNAc at 1100 — and each is broken by
the functional-group census, since the N-acetylated pair carries ⊣≻⊥ the bare
hexoses lack.

So the PAIR (functional-group marks, ⊥ chirality word) separates all eight
monosaccharides, derived end to end through the chem pipeline and RDKit's CIP
assignment, with no hand-typed sugar table. Prompt 1 is closed: eight sugars, eight
distinct types. The achiral census names the connectivity class; the ⊥ census names
the handedness within it; the two together are the monosaccharide's grammar type.
