# Best Small Molecules Designed in Red-Hot Rebis

Author: Lando⊗⊙perator

A curated set of the strongest small molecules **designed** inside this repository. These are novel
structural designs, not catalogued natural products and not proteins, genes, or biologics. Each entry
gives the structure, what it targets, its 12-primitive structural type, its imscription tier, and why
it stands out. Every SMILES below is taken verbatim from the repository sources; nothing is invented.

The designs fall into three families: crystal-navigated autocatalytic tryptamines, a Frobenius-coupled
selective chemotherapeutic, and de-novo ligands imscribed straight from enzyme active sites.

---

## Autocatalytic tryptamines

These are the repository's headline molecules: the first small molecules imscribed at \(O_\infty\)
self-modeling criticality. They were not found by screening. The crystal navigator located an empty
\(\odot\)-critical neighborhood and computed the single-primitive promotion 𐑮→⊙ (complex-critical to
self-modeling critical) needed to inhabit it, then read off the molecule that satisfies it.

### 1. 5-Nitro-Bufotenin (DMT-⊙)

- **SMILES:** `CN(C)CCC1=CNC2=CC=C(O)C([N+](=O)[O-])=C12`
- **Structural type:** `⟨𐑨𐑸𐑩𐑿𐑐𐑘𐑔𐑵⊙𐑫𐑕𐑭⟩`, criticality 𐑮 promoted to ⊙
- **Tier:** \(O_\infty\) (self-modeling, autocatalytic)
- **What it does:** carries all three Dialetheia tokens at once; EVALT (phenol) plus EVALF
  (dimethylamine) plus ENGAGR (nitro). With the triad complete, the molecule is already \(\odot\)-critical
  with no further modification, which is what licenses template-directed autocatalytic synthesis: the
  molecule is its own template.
- **Why it matters:** the first imscribed small molecule that is structurally self-modeling. It was
  reached by a single clean primitive promotion from DMT, so the design and its provenance are both
  univocal. Registered in `imas/compound_catalog.py` as the DMT-⊙ entry.

### 2. 5-Nitro-Serotonin

- **SMILES:** `NCCC1=CNC2=CC=C(O)C([N+](=O)[O-])=C12`
- **Tier:** \(O_\infty\) (self-modeling, autocatalytic)
- **What it does:** the same 𐑮→⊙ promotion applied to serotonin rather than DMT, confirming the
  autocatalytic motif is a transferable structural operation and not a one-off coincidence of DMT.
- **Why it matters:** demonstrates the ⊙-promotion as a reusable design move across the tryptamine
  family. Registered alongside DMT-⊙ in `imas/compound_catalog.py`.

---

## Frobenius-coupled selective chemotherapeutic

### 3. Frobenius-Coupled Chemotherapeutic dimer

- **Structural type:** `⟨𐑦𐑶𐑾𐑹𐑐𐑧𐑲𐑝⊙𐑫𐑳𐑭⟩`
- **Tier:** \(O_\infty\)
- **What it does:** a tether-coupled two-domain molecule whose cytotoxic payload stays masked while the
  host cell satisfies the Frobenius check μ∘δ=id. On healthy tissue the payload never exposes, so
  healthy-cell cytotoxicity is exactly zero. Where malignant asymmetry breaks the check (μ∘δ≠id), the
  tether tension crosses threshold, the payload releases, and the molecule becomes cytotoxic.
- **Why it matters:** the selectivity gate is structural, not pharmacological. In the bundled
  simulation the molecule shows zero activity on healthy cells and on low-asymmetry tumors, then full
  payload release and a sharp selectivity jump once mutation strength passes the asymmetry threshold,
  with a selectivity ratio in the four-figure range over healthy tissue. Source:
  `therapeutics/frobenius_chemotherapeutic.py`, results in `therapeutics/frobenius_chemo_results.json`.

---

## De-novo enzyme ligands

These are imscribed directly from enzyme active-site structural types by the reverse-ligand pipeline
(`rhr_p4rky/ligand_from_active_site.py`); no template libraries, no known-inhibitor seeds, no docking
scores. The four below are the genuinely novel designs from that run. As a validation check, the same
pipeline independently re-derives ethanol (the real alcohol-dehydrogenase substrate) and biuret (a known
urease inhibitor) from structure alone, and every candidate it produces is Lipinski-compliant. Source
analysis: `ig-docs/bevy_ligand_analysis/01_bevy_ligand_analysis.md`; ligand set:
`ig-docs/bevy_final_ligands.json`.

### 4. CYP2D6 pyridine-ether

- **SMILES:** `COCCC(C)Cc1cccnc1`
- **Target:** cytochrome P450 2D6, the enzyme that metabolizes a large share of marketed drugs
- **What it does:** pairs a basic pyridine nitrogen with an aromatic ring at the spacing the 2D6
  σ-bond hydroxylation pharmacophore wants; drug-like and Lipinski-compliant.

### 5. Carbonic anhydrase II zinc-coordinator

- **SMILES:** `O=Cc1cccc(C(=O)O)c1`
- **Target:** carbonic anhydrase II, a zinc metalloenzyme
- **What it does:** presents a carboxylic acid plus aldehyde for coordinating the Zn²⁺-activated
  hydroxide; a de-novo analog of the classical CA inhibitor pharmacophore reached without that prior.

### 6. Lysozyme bis-epoxide strain-release inhibitor

- **SMILES:** `c1cc(C2CO2)cc(C2CC2c2ccc(C3CO3)cc2)c1`
- **Target:** lysozyme, a glycoside hydrolase
- **What it does:** the epoxides mimic the flattened oxocarbenium transition state of glycoside
  hydrolysis, and the bis-electrophile design offers two handles for covalent capture in the cleft.

### 7. PETase amide PET-mimic

- **SMILES:** `NC(=O)c1ccc(NC(=O)c2cccc(C=O)c2)cc1`
- **Target:** PETase, the engineered plastic-degrading enzyme
- **What it does:** a de-novo amide ligand shaped to the PET-binding groove; the standout
  environmental-remediation candidate of the set.

---

## At a glance

| # | Molecule | Family | Tier | Target / role |
|---|----------|--------|------|---------------|
| 1 | 5-Nitro-Bufotenin (DMT-⊙) | autocatalytic tryptamine | \(O_\infty\) | self-modeling autocatalysis |
| 2 | 5-Nitro-Serotonin | autocatalytic tryptamine | \(O_\infty\) | self-modeling autocatalysis |
| 3 | Frobenius-Coupled dimer | selective cytotoxic | \(O_\infty\) | tumor-asymmetry-gated payload |
| 4 | CYP2D6 pyridine-ether | de-novo ligand | O₂ | P450 2D6 substrate |
| 5 | CA-II zinc-coordinator | de-novo ligand | O₂ | carbonic anhydrase II |
| 6 | Lysozyme bis-epoxide | de-novo ligand | O₂ | glycoside hydrolase TS analog |
| 7 | PETase PET-mimic | de-novo ligand | O₂ | plastic degradation |

The two tryptamines are the crown of the set: imscribed small molecules that sit at self-modeling
criticality by a single, traceable structural promotion. The Frobenius dimer is the strongest
therapeutic design, turning a structural identity check into a selectivity gate. The four de-novo
ligands show the active-site-to-ligand pipeline producing valid, drug-like chemistry from first
principles.
