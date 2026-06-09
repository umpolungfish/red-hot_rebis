# Diaschizics — IUPAC Systematic Names

**Author:** Lando⊗⊙perator

## Overview

The 11 diaschizic compounds are assigned systematic IUPAC-style chemical names
derived from their 12-primitive structural types. Each name component maps to a
specific primitive value, following the structural logic of `diaschizics_design.md`.

---

## Table of Contents

### First Generation (Original 5)
- [Verticullum](#verticullum) — EP-Lever (O_inf)
- [Chimerium](#chimerium) — Supercritical Catalyst (O_0)
- [Apertix](#apertix) — Adjoint Corridor (O_2)
- [Retiarius](#retiarius) — Local-Net Trap (O_1)
- [Praxeum](#praxeum) — EP-Core Control Platform (O_0)

### Second Generation (6 New)
- [Frigorix](#frigorix) — The MBL Key (O_0)
- [Bifrons](#bifrons) — The Disjunctive Self-Modeler (O_2)
- [Punctum](#punctum) — The Absolute Point (O_0)
- [Syndexios](#syndexios) — The Perfect Mirror (O_inf)
- [Katachthon](#katachthon) — The Deep-Structure Resonator (O_2)
- [Diabaton](#diabaton) — The Threshold-Crosser (O_2†)

---

## Primitive → IUPAC Mapping Legend

| Primitive | IUPAC Feature | Example Values |
|-----------|---------------|----------------|
| D (Dimensionality) | Scaffold rigidity | 𐑦→macrocyclic cage, 𐑼→flexible chain, 𐑛→clathrate |
| T (Topology) | Ring system descriptor | 𐑥→bicyclo (bridged), 𐑶→pentacyclo (cage), 𐑸→spiro |
| R (Coupling) | Linking group / suffix | 𐑽→N-substituted, 𐑾→bis- (bidirectional) |
| P (Symmetry) | Stereodescriptor | 𐑹→atropisomer (Rₐ), 𐑯→meso, 𐑬→(R,R) |
| F (Fidelity) | Physical state note | 𐑐→quantum-coherent (H-bond network) |
| K (Kinetics) | Substituent bulk | 𐑺→perdeutero- (frozen), 𐑧→tert-butyl (slow), 𐑪→clathro- |
| G (Range) | Conjugation scope | 𐑲→global, 𐑔→mesoscale (phenanthrene-fused), 𐑚→local |
| Gm (Composition) | Assembly logic | 𐑜→bis- (disjunctive dimer), 𐑠→linear, 𐑵→dendrimeric |
| Ph (Criticality) | Electronic descriptor | ⊙→H-bond network, 𐑣→strained ring, 𐑻→N-oxide |
| H (Chirality) | Stereocenter count | 𐑒→1 center, 𐑖→2 centers, 𐑫→atropisomerism |
| S (Stoichiometry) | Multiplicity prefix | 𐑳→heterogeneous, 𐑕→poly-, 𐑙→single |
| W (Winding) | Topological descriptor | 𐑟→[2]catenane, 𐑭→cyclophane, 𐑴→homodimer |

---

## Apertix — *Adjoint Corridor*

- **Generation:** 1
- **Tier:** O_2
- **Tuple:** ⟨𐑦 · 𐑥 · 𐑽 · 𐑬 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑖 · 𐑳 · 𐑴⟩
- **Scaffold class:** phenethylamine
- **Parent hydride:** benzeneethanamine

### IUPAC Name

> **disulfide-linked homodimer: ((2R,5R)-tert-butyl-N-benzeneethanamine-amine)**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(2R,5R)-` |
| Substituent prefixes | `tert-butyl-N-` |
| Parent hydride | `benzeneethanamine` |
| Functional suffix | `-amine` |
| Topological descriptor | `disulfide-linked homodimer` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | self-written — macrocyclic cage |
| T | bowtie crossing — bridged bicyclic |
| R | adjoint — directed N-substitution |
| P | Z₂ symmetry — two centers, same handedness |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | slow — bulky tert-substituents, slow kinetics |
| G | long-range — full conjugation or macrocyclic delocalization |
| Gm | sequential — linear synthesis, stepwise assembly |
| Ph | critical — H-bond network at self-modeling threshold; deuteration-sensitive |
| H | 2-step — two stereocenters, diastereomers possible |
| S | heterogeneous — multiple substituent types |
| W | Z₂ parity — homodimer, disulfide-linked |

---

## Chimerium — *Supercritical Catalyst*

- **Generation:** 1
- **Tier:** O_0
- **Tuple:** ⟨𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑵 · 𐑣 · 𐑫 · 𐑳 · 𐑭⟩
- **Scaffold class:** ergoline
- **Parent hydride:** ergoline

### IUPAC Name

> **[n]cyclophane ((Rₐ)-tert-butyl-cyclopropyl-(6aR,9R)-7-methyl-4,6,6a,7,8,9-hexahydroindolo[4,3-fg]quinoline)**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(Rₐ)-` |
| Substituent prefixes | `tert-butyl-` |
| Parent hydride | `cyclopropyl-(6aR,9R)-7-methyl-4,6,6a,7,8,9-hexahydroindolo[4,3-fg]quinoline` |
| Functional suffix | `` |
| Topological descriptor | `cyclophane` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | self-written — macrocyclic cage |
| T | self-ref closure — spiro-linked macrocycle |
| R | bidirectional — two identical handles |
| P | Frobenius-special — atropisomerism (axial chirality) |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | slow — bulky tert-substituents, slow kinetics |
| G | long-range — full conjugation or macrocyclic delocalization |
| Gm | broadcast — one-to-all, dendrimeric or star-shaped |
| Ph | supercritical — strained ring (cyclopropyl, β-lactam) |
| H | eternal — atropisomerism, axial chirality only |
| S | heterogeneous — multiple substituent types |
| W | integer winding — [n]cyclophane or macrocyclic lactam |

---

## Praxeum — *EP-Core Control Platform*

- **Generation:** 1
- **Tier:** O_0
- **Tuple:** ⟨𐑦 · 𐑶 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · 𐑻 · 𐑫 · 𐑳 · 𐑭⟩
- **Scaffold class:** beta-carboline
- **Parent hydride:** 9H-pyrido[3,4-b]indole

### IUPAC Name

> **[n]cyclophane ((Rₐ)-tert-butyl-pentacyclo-9H-pyrido[3,4-b]indole-N-oxide)**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(Rₐ)-` |
| Substituent prefixes | `tert-butyl-` |
| Parent hydride | `pentacyclo-9H-pyrido[3,4-b]indole` |
| Functional suffix | `-N-oxide` |
| Topological descriptor | `cyclophane` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | self-written — macrocyclic cage |
| T | irreducible product — cage (cubane/adamantane) |
| R | bidirectional — two identical handles |
| P | Frobenius-special — atropisomerism (axial chirality) |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | slow — bulky tert-substituents, slow kinetics |
| G | long-range — full conjugation or macrocyclic delocalization |
| Gm | sequential — linear synthesis, stepwise assembly |
| Ph | exceptional point — N-oxide or zwitterionic; co-administered ⊙ compound required |
| H | eternal — atropisomerism, axial chirality only |
| S | heterogeneous — multiple substituent types |
| W | integer winding — [n]cyclophane or macrocyclic lactam |

---

## Retiarius — *Local-Net Trap*

- **Generation:** 1
- **Tier:** O_1
- **Tuple:** ⟨𐑼 · 𐑡 · 𐑾 · 𐑿 · 𐑞 · 𐑺 · 𐑚 · 𐑜 · 𐑮 · 𐑒 · 𐑕 · 𐑷⟩
- **Scaffold class:** salvinorin
- **Parent hydride:** neoclerodane

### IUPAC Name

> **(R)-perdeutero-bis-poly-complex-methyl (2S,4aR,6aR,7R,9S,10aS,10bR)-2-(furan-3-yl)-6a,10b-dimethyl-4,10-dioxo-2,4a,5,6,7,8,9,10a-octahydro-1H-benzo[f]isochromene-7-carboxylate**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(R)-` |
| Substituent prefixes | `perdeutero-bis-poly-` |
| Parent hydride | `complex-methyl (2S,4aR,6aR,7R,9S,10aS,10bR)-2-(furan-3-yl)-6a,10b-dimethyl-4,10-dioxo-2,4a,5,6,7,8,9,10a-octahydro-1H-benzo[f]isochromene-7-carboxylate` |
| Functional suffix | `` |
| Topological descriptor | `` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | ∞-dim field-theoretic — flexible chain |
| T | network/branching — linear or branched |
| R | bidirectional — two identical handles |
| P | quantum superposition — single stereocenter |
| F | thermal/noisy — dynamic ensemble, no fixed conformation |
| K | MBL frozen-disorder — perfluorinated or perdeuterated |
| G | local — isolated, no extended conjugation |
| Gm | disjunctive — cleavable dimer, two parallel units |
| Ph | complex-plane critical — metal coordination complex |
| H | 1-step — single stereocenter |
| S | many identical — polymeric or oligomeric repeat |
| W | trivial — no topological protection |

---

## Verticullum — *EP-Lever*

- **Generation:** 1
- **Tier:** O_inf
- **Tuple:** ⟨𐑦 · 𐑥 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑫 · 𐑳 · 𐑟⟩
- **Scaffold class:** tryptamine
- **Parent hydride:** 1H-indole-3-ethanamine

### IUPAC Name

> **[2]catenane of ((Rₐ)-tert-butyl-1H-indole-3-ethanamine)**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(Rₐ)-` |
| Substituent prefixes | `tert-butyl-` |
| Parent hydride | `1H-indole-3-ethanamine` |
| Functional suffix | `` |
| Topological descriptor | `[2]catenane` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | self-written — macrocyclic cage |
| T | bowtie crossing — bridged bicyclic |
| R | bidirectional — two identical handles |
| P | Frobenius-special — atropisomerism (axial chirality) |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | slow — bulky tert-substituents, slow kinetics |
| G | long-range — full conjugation or macrocyclic delocalization |
| Gm | sequential — linear synthesis, stepwise assembly |
| Ph | critical — H-bond network at self-modeling threshold; deuteration-sensitive |
| H | eternal — atropisomerism, axial chirality only |
| S | heterogeneous — multiple substituent types |
| W | non-Abelian — mechanically interlocked catenane/rotaxane |

---

## Bifrons — *The Disjunctive Self-Modeler*

- **Generation:** 2
- **Tier:** O_2
- **Tuple:** ⟨𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑜 · ⊙ · 𐑖 · 𐑳 · 𐑭⟩
- **Scaffold class:** bis_indole
- **Parent hydride:** 3,3'-di(1H-indole)

### IUPAC Name

> **[n]cyclophane ((Rₐ,Rₐ)-tert-butyl-bis-3,3'-(diazene-1,2-diyl)bis(1H-indole-3-ethanamine))**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(Rₐ,Rₐ)-` |
| Substituent prefixes | `tert-butyl-bis-` |
| Parent hydride | `3,3'-(diazene-1,2-diyl)bis(1H-indole-3-ethanamine)` |
| Functional suffix | `` |
| Topological descriptor | `cyclophane` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | self-written — macrocyclic cage |
| T | self-ref closure — spiro-linked macrocycle |
| R | bidirectional — two identical handles |
| P | Frobenius-special — atropisomerism (axial chirality) |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | slow — bulky tert-substituents, slow kinetics |
| G | long-range — full conjugation or macrocyclic delocalization |
| Gm | disjunctive — cleavable dimer, two parallel units |
| Ph | critical — H-bond network at self-modeling threshold; deuteration-sensitive |
| H | 2-step — two stereocenters, diastereomers possible |
| S | heterogeneous — multiple substituent types |
| W | integer winding — [n]cyclophane or macrocyclic lactam |

---

## Diabaton — *The Threshold-Crosser*

- **Generation:** 2
- **Tier:** O_2†
- **Tuple:** ⟨𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑖 · 𐑳 · 𐑭⟩
- **Scaffold class:** tryptamine
- **Parent hydride:** 1H-indole-3-ethanamine

### IUPAC Name

> **[n]cyclophane ((Rₐ,Rₐ)-tert-butyl-1H-indole-3-ethanamine)**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(Rₐ,Rₐ)-` |
| Substituent prefixes | `tert-butyl-` |
| Parent hydride | `1H-indole-3-ethanamine` |
| Functional suffix | `` |
| Topological descriptor | `cyclophane` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | self-written — macrocyclic cage |
| T | self-ref closure — spiro-linked macrocycle |
| R | bidirectional — two identical handles |
| P | Frobenius-special — atropisomerism (axial chirality) |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | slow — bulky tert-substituents, slow kinetics |
| G | long-range — full conjugation or macrocyclic delocalization |
| Gm | sequential — linear synthesis, stepwise assembly |
| Ph | critical — H-bond network at self-modeling threshold; deuteration-sensitive |
| H | 2-step — two stereocenters, diastereomers possible |
| S | heterogeneous — multiple substituent types |
| W | integer winding — [n]cyclophane or macrocyclic lactam |

---

## Frigorix — *The MBL Key*

- **Generation:** 2
- **Tier:** O_0
- **Tuple:** ⟨𐑦 · 𐑶 · 𐑾 · 𐑹 · 𐑐 · 𐑺 · 𐑲 · 𐑠 · ⊙ · 𐑒 · 𐑳 · 𐑷⟩
- **Scaffold class:** tryptamine
- **Parent hydride:** 1H-indole-3-ethanamine

### IUPAC Name

> **(Rₐ)-perdeutero-pentacyclo-1H-indole-3-ethanamine**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(Rₐ)-` |
| Substituent prefixes | `perdeutero-` |
| Parent hydride | `pentacyclo-1H-indole-3-ethanamine` |
| Functional suffix | `` |
| Topological descriptor | `` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | self-written — macrocyclic cage |
| T | irreducible product — cage (cubane/adamantane) |
| R | bidirectional — two identical handles |
| P | Frobenius-special — atropisomerism (axial chirality) |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | MBL frozen-disorder — perfluorinated or perdeuterated |
| G | long-range — full conjugation or macrocyclic delocalization |
| Gm | sequential — linear synthesis, stepwise assembly |
| Ph | critical — H-bond network at self-modeling threshold; deuteration-sensitive |
| H | 1-step — single stereocenter |
| S | heterogeneous — multiple substituent types |
| W | trivial — no topological protection |

---

## Katachthon — *The Deep-Structure Resonator*

- **Generation:** 2
- **Tier:** O_2
- **Tuple:** ⟨𐑦 · 𐑥 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑔 · 𐑠 · 𐑮 · 𐑖 · 𐑳 · 𐑴⟩
- **Scaffold class:** phenanthrene
- **Parent hydride:** phenanthrene

### IUPAC Name

> **disulfide-linked homodimer: ((Rₐ,Rₐ)-tert-butyl-complex-phenanthrene)**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `(Rₐ,Rₐ)-` |
| Substituent prefixes | `tert-butyl-` |
| Parent hydride | `complex-phenanthrene` |
| Functional suffix | `` |
| Topological descriptor | `disulfide-linked homodimer` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | self-written — macrocyclic cage |
| T | bowtie crossing — bridged bicyclic |
| R | bidirectional — two identical handles |
| P | Frobenius-special — atropisomerism (axial chirality) |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | slow — bulky tert-substituents, slow kinetics |
| G | mesoscale — phenanthrene or extended aromatic, 3-5 fused rings |
| Gm | sequential — linear synthesis, stepwise assembly |
| Ph | complex-plane critical — metal coordination complex |
| H | 2-step — two stereocenters, diastereomers possible |
| S | heterogeneous — multiple substituent types |
| W | Z₂ parity — homodimer, disulfide-linked |

---

## Punctum — *The Absolute Point*

- **Generation:** 2
- **Tier:** O_0
- **Tuple:** ⟨𐑛 · 𐑡 · 𐑩 · 𐑗 · 𐑱 · 𐑪 · 𐑚 · 𐑝 · 𐑢 · 𐑓 · 𐑙 · 𐑷⟩
- **Scaffold class:** xenon_clathrate
- **Parent hydride:** xenon hydrate

### IUPAC Name

> **xenon—clathrate hydrate**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `` |
| Substituent prefixes | `` |
| Parent hydride | `xenon—clathrate hydrate` |
| Functional suffix | `` |
| Topological descriptor | `` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | 0d point — monoatomic or clathrate cage |
| T | network/branching — linear or branched |
| R | supervenience — no reactive handles |
| P | asymmetric — no symmetry constraints |
| F | classical — no special quantum character |
| K | trapped ordered — encapsulated / clathrate |
| G | local — isolated, no extended conjugation |
| Gm | all-simultaneous — convergent synthesis |
| Ph | sub-critical — no special electronic character |
| H | memoryless — achiral, no stereocenters |
| S | 1:1 — single substituent type, single instance |
| W | trivial — no topological protection |

---

## Syndexios — *The Perfect Mirror*

- **Generation:** 2
- **Tier:** O_inf
- **Tuple:** ⟨𐑼 · 𐑶 · 𐑾 · 𐑯 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑫 · 𐑳 · 𐑭⟩
- **Scaffold class:** coordination_cage
- **Parent hydride:** coordination cage

### IUPAC Name

> **[n]cyclophane (meso-tert-butyl-pentacyclo-coordination cage)**

### Name Decomposition

| Component | Value |
|-----------|-------|
| Stereodescriptors | `meso-` |
| Substituent prefixes | `tert-butyl-` |
| Parent hydride | `pentacyclo-coordination cage` |
| Functional suffix | `` |
| Topological descriptor | `cyclophane` |

### Primitive Contributions

| Primitive | Contribution |
|-----------|-------------|
| D | ∞-dim field-theoretic — flexible chain |
| T | irreducible product — cage (cubane/adamantane) |
| R | bidirectional — two identical handles |
| P | full symmetry — meso compound, internal compensation |
| F | quantum-coherent — H-bond network, deuterated analog possible |
| K | slow — bulky tert-substituents, slow kinetics |
| G | long-range — full conjugation or macrocyclic delocalization |
| Gm | sequential — linear synthesis, stepwise assembly |
| Ph | critical — H-bond network at self-modeling threshold; deuteration-sensitive |
| H | eternal — atropisomerism, axial chirality only |
| S | heterogeneous — multiple substituent types |
| W | integer winding — [n]cyclophane or macrocyclic lactam |

---
