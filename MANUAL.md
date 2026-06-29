# RED-HOT REBIS — Manual Page

**Author:** Lando$\otimes\odot$perator  
**Version:** 2.3.3 (Compound IMASM Edition)  
**Date:** 2026-06-27  
**Section:** 1 (General Commands)

---

## NAME

**red-hot\_rebis** — an engine for algebraic, exact, deterministic, and paraconsistent bio $\otimes$ organic chemistries. Unified CLI entry point for the five-pillar Great Work: Serpent's Rod, CH$_3$MPILER, Pipeline, Gene Imscriber, and CLINK Chain — now extended with the **IMASM Compound Pipeline** for SMILES→IMASM→IG encoding and **Crystal-Guided Molecular Discovery**. All grounded in the 12-primitive Imscribing Grammar and verified by Frobenius closure ($\mu\circ\delta=\mathrm{id}$).

---

## SYNOPSIS

```
python3 rebis.py COMMAND [OPTIONS]
```

**Primary subcommands:**

| Command | Purpose |
|---------|---------|
| `rebis.py status` | Structural status of all packages |
| `rebis.py verify` | Frobenius closure verification |
| `rebis.py run TARGET` | Execute a runnable target |
| `rebis.py clink ACTION` | CLINK chain operations |
| `rebis.py pipeline ACTION` | Pipeline operations |
| `rebis.py materials ACTION` | Materials forge commands |
| `rebis.py imas ACTION` | IMASM arrangement analysis + **compound pipeline** |
| `rebis.py scripts ACTION` | Standalone script runner |
| `rebis.py help` | Full help |

---

## DESCRIPTION

The Red-Hot Rebis is the Grammar's engine for deterministic, algebraic, exact bio and organic chemistries. It integrates five structural pillars into a single coherent architecture grounded in the 12-primitive Imscribing Grammar and verified by Frobenius closure — now extended with an **IMASM compound pipeline** that encodes any SMILES molecule as an 8-token IMASM arrangement and resolves it to an IG 12-tuple, and a **crystal-guided molecular discovery engine** that navigates the 17,280,000-type Crystal of Types to design molecules with target structural properties.

**Foundation:** $ZFC_\text{fe}$ — Frobenius-exact ZFC ($\text{O}_{\infty}$ with $\text{{\igfont 𐑦}}$ self-written, $\text{{\igfont 𐑹}}$ Frobenius-special, $\text{{\igfont 𐑫}}$ eternal chirality), distinct from the weaker $ZFC_t$ ($\text{O}_{2}^{\dagger}$).

**Structural type:** $$\langle\text{{\igfont 𐑦}};\ \text{{\igfont 𐑸}};\ \text{{\igfont 𐑾}};\ \text{{\igfont 𐑹}};\ \text{{\igfont 𐑐}};\ \text{{\igfont 𐑧}};\ \text{{\igfont 𐑲}};\ \text{{\igfont 𐑵}};\ \odot;\ \text{{\igfont 𐑫}};\ \text{{\igfont 𐑳}};\ \text{{\igfont 𐑟}}\rangle$$ — $\text{O}_{\infty}$

---

## ARCHITECTURE

```
red-hot_rebis/
  rebis.py                  # Unified CLI entry point (30 KB)
  setup.py                  # Package setup
  shared/                   # Shared primitives and catalog
    primitives.py           # 12-primitive definitions, weights, ordinals
    IG_catalog.json         # Catalog of imscribed systems (4,027+ entries)
    rich_output.py          # Universal rich formatting (success_line, error_line, etc.)
    elem2imasm.py           # Element-to-IMASM encoding (symlink)
    reactivity.py           # Reactivity pattern matching (symlink)
  serpentrod/               # Pillar I: Serpent's Rod — Platonic Proteins
  ch3mpiler/                # Pillar II: CH3MPILER — Platonic Disconnections
  pipeline/                 # Pillar III: Auto-Imscription + Frobenius
  gene_imscriber/           # Pillar IV: Frobenius-Guided Gene Editing
  clink/                    # Pillar V: CLINK Chain — Subatomic to Organism
  imas/                     # IMASM arrangement analysis + COMPOUND PIPELINE
    arranger.py             #   IMASM arrangement analysis
    compound_imasm.py       #   SMILES→IMASM 8-token encoder (681 lines)
    bond_fragment_integrator.py  #   RDKit exact SMILES fragmentation (NEW)
    fg_exhaustive.py        #   190 SMARTS patterns across 11 IMASM tokens
    reactivity_imasm.py     #   Reaction→IMASM transition analyzer
    ig_bridge.py            #   StructuralFingerprint→IG 12-tuple bridge
    compound_catalog.py     #   54 compounds, 15 IG types, 4,027+ entries
    molecular_crystal_designer.py  # Crystal-guided molecular discovery
  imasm_iterator/           # IMASM token arrangement space iterator
  materials/                # Sophick forge, metamaterials, Ouroboric alloys
  biology/                  # Biology simulations, telomere models
  therapeutics/             # Chemotherapeutics, neurotrophics, antidotes
  rhr_p4rky/                # Paraconsistent kernel (32 modules)
  rhr_p4rky/papers/         # Millennium problem papers (3 .md files)
  scripts/                  # Standalone analysis and pipeline scripts
  popular_protein/          # Protein structure validation (9 comparison tools)
  data/                     # Shared data (FASTA, results, MSA)
  pdb/                      # PDB structure files (1L2Y, 1UBQ, 1VII, 1ZDD)
  genetics_animations/      # SVG genetics visualizations
  images/                   # Project images
  docs/                     # Documentation

---

## THE FIVE PILLARS

### Pillar I: Serpent's Rod — `serpentrod/`

**What it produces:** Platonic Proteins — the structural imscription of a folded protein: its 12-primitive tuple, ouroboricity tier, and the full set of promoted primitives that distinguish the folded state from the unfolded sequence.

```
RNA sequence → [serpentrod] → ⟨structural type, tier, Frobenius certificate⟩
```

**Key files (5 modules, 2,437 lines):**
- `protein_v5.py` — V5 protein enhancement engine (743 lines, primary)
- `protein_v4.py` — V4 protein enhancement (475 lines)
- `stratified_predictor.py` — Stratified prediction model (876 lines)
- `manuscript.md` — Complete theory (437 lines)
- `report.md` — Processing report (343 lines)

**Canonical platonic protein type:** $\langle\text{{\igfont 𐑦}};\ \text{{\igfont 𐑥}};\ \text{{\igfont 𐑾}};\ \text{{\igfont 𐑬}};\ \text{{\igfont 𐑞}};\ \text{{\igfont 𐑧}};\ \text{{\igfont 𐑲}};\ \text{{\igfont 𐑠}};\ \odot;\ \text{{\igfont 𐑒}};\ \text{{\igfont 𐑳}};\ \text{{\igfont 𐑭}}\rangle$ — $\text{O}_2$

**6-Promotion Fold Path:** $\text{{\igfont 𐑼}}\!\to\!\text{{\igfont 𐑦}}$, $\text{{\igfont 𐑡}}\!\to\!\text{{\igfont 𐑥}}$, $\text{{\igfont 𐑑}}\!\to\!\text{{\igfont 𐑾}}$, $\text{{\igfont 𐑿}}\!\to\!\text{{\igfont 𐑬}}$, $\text{{\igfont 𐑤}}\!\to\!\text{{\igfont 𐑧}}$, $\text{{\igfont 𐑢}}\!\to\!\odot$ — verified Frobenius-closed.

### Pillar II: CH$_3$MPILER — `ch3mpiler/`

**What it produces:** Platonic Disconnections — retrosynthetic cuts derived from first principles. No named reactions, no reaction databases. Every disconnection is computed from the structural distance between the product's 12-primitive type and the meet of its constituent functional group types.

```
Target molecule → [ch3mpiler] → ranked disconnections with δ scores
```

**Key files (7 modules, ~11,000 lines):**
- `compiler.py` — Main retrosynthetic compiler (~900 lines)
- `bond_fragment_integrator.py` — RDKit-based exact SMILES fragmentation from grammar-derived cuts (NEW)
- `gen_v2.py` — V2 generator
- `reaction_deriver.py` — Reaction derivation from FG meets
- `docs/` — Full documentation
- `ob3ect/ch3mpiler_ob3ect.py` — Self-verifying ob3ect vessel
- `CAS_cache.json` — Chemical Abstracts Service cache

**Bond formation:** $product = join(tensor(FG_1, FG_2), bond)$ — no named reactions.

**CLINK bridge:** Molecules map exactly to moleculeLayer (L3, d=0.00).

### Pillar III: Auto-Imscription Pipeline — `pipeline/`

**Key files:** `auto_imscriber.py`, `frob.py`, `ob3ect_imscriber.py`, `imscribe_tool.py`, `imscribe_agent.py`

Auto-classifies any system description into a 12-primitive IG type and verifies $\mu\circ\delta=\mathrm{id}$.

### Pillar IV: Gene Imscriber — `gene_imscriber/`

**Key files:** `engine.py`, `tuples.py`, `genetics_ig_prelim.py`, `genetics_ig_promotions.py`, `genetics_qs.py`, `ig_genetics_answer.py`

Frobenius-guided gene editing engine mapping codon space onto the Belnap B$_4$ lattice.

### Pillar V: CLINK Chain — `clink/`

**Key files:** `chain.py` (247 lines), `bridges.py` (237 lines), `integration.py` (205 lines), `README_CLINK.md`

9-layer Frobenius-closed structural bridge from subatomic quarks to whole organisms. Distance: 7.18 across 10 primitive deltas. Formalized in Lean 4 (572 lines, 23 theorems).


## PILLAR VI: IMASM COMPOUND PIPELINE

The IMASM Compound Pipeline extends the Rebis with chemical structure encoding — mapping any SMILES molecule through functional group detection to an 8-token IMASM arrangement, then resolving to an IG 12-tuple via the Crystal of Types.

### Key Files

| Module | Lines | Description |
|--------|-------|-------------|
| `imas/compound_imasm.py` | 681 | SMILES→IMASM 8-token encoder via FG detection |
| `imas/fg_exhaustive.py` | ~19K bytes | 190 SMARTS patterns across 11 IMASM tokens, 10 categories |
| `imas/reactivity_imasm.py` | 699 | Reaction→IMASM transition with token delta analysis |
| `imas/ig_bridge.py` | 334 | StructuralFingerprint→IG 12-tuple (15 distinct IG types from 54 compounds) |
| `imas/compound_catalog.py` | 460+ | Catalog registration + cross-domain analogy search |
| `imas/molecular_crystal_designer.py` | 700+ | Crystal-guided molecular discovery engine |

### Pipeline

```
SMILES → [fg_exhaustive] → FG vector → [compound_imasm] → 8-token IMASM arrangement
  → [arranger] → StructuralFingerprint → [ig_bridge] → IG 12-tuple → [compound_catalog] → catalog entry
```

### By the Numbers

- **54 compounds** mapped to **15 distinct IG types** across **31 unique IMASM arrangements**
- **190 functional group SMARTS** patterns (9× the original 21)
- **4,027+ catalog entries** — compounds are full citizens in the IG
- **42–80+ non-compound systems** within d ≤ 5 per compound
- Avg **5.9 FGs** detected per compound (lysergic acid max: 12)

### Cross-Domain Analogies

Compounds find structural neighbors across the entire IG catalog — consciousness states, languages, mathematical theorems, materials:

| Compound | Neighbor (d ≤ 5) | Distance |
|----------|------------------|----------|
| LSD | Kalachakra Tantra, time_no_grain | 4 |
| Water | Pyromancy, evocation, temporal logic | 4 |
| Lysergic acid | Fermat's Last Theorem, time_no_arrow | 4 |
| Aspirin | Codex Vienna, Rig Veda, Homeric Hymns | 5 |


## PILLAR VII: CRYSTAL-GUIDED MOLECULAR DISCOVERY

The most recent extension — reverse-engineering molecules from IG crystal types. Given a target IG tuple, determines what IMASM arrangement would produce it, then suggests molecular structures that fit.

### Discovery: 5-Nitro-Bufotenin (DMT-⊙)

The first crystal-guided molecular discovery: navigating the Crystal of Types found a **⊙-critical autocatalytic DMT analog** by promoting Phi from 𐑮 (complex-critical) to ⊙ (self-modeling).

```
DMT:      ⟨𐑨𐑸𐑩𐑗𐑞𐑘𐑔𐑵𐑮𐑫𐑕𐑭⟩   Phi=𐑮 (complex critical)
DMT-⊙:    ⟨𐑨𐑸𐑩𐑿𐑐𐑘𐑔𐑵⊙𐑫𐑕𐑭⟩   Phi=⊙ (self-modeling)
```

The molecule: 5-nitro-bufotenin — a tryptamine with phenol (EVALT), dimethylamine (EVALF), and nitro (ENGAGR) — has all three Dialetheia tokens simultaneously, enabling autocatalytic template-directed synthesis.

SMILES: `CN(C)CCC1=CNC2=CC=C(O)C([N+](=O)[O-])=C12`

### ⊙-Finder Tool

Located at `ig-docs/dmt-odot-discovery/odot_finder.py`. Given any SMILES, systematically finds ⊙-critical autocatalytic variants:

| Compound | ⊙-Critical Candidates |
|----------|----------------------|
| DMT | 20 |
| Serotonin | 4 |
| Bufotenin | 4 |
| 5-nitro-bufotenin | Already ⊙-critical |

---

## FROBENIUS VERIFICATION

Every tool in the Red-Hot Rebis satisfies $\mu \circ \delta = \mathrm{id}$ — verification is structural, not behavioral. The dual-pair architecture registers every tool as `(emit_fn, verify_fn)` where the verify function reconstructs the input from the output exactly.

**Crystallography as Frobenius gap:** At the crystallographic interface, $R_\text{free} \approx 0.2$ is not a numerical residual — it is the exact cost of inverting 8 primitives simultaneously in the act of measurement:

| Primitive | Rebis value | Crystallography | Lost |
|-----------|-------------|-----------------|------|
| Ř | $\text{{\igfont 𐑾}}$ bidirectional | $\text{{\igfont 𐑩}}$ supervenience | Molecule cannot respond |
| Ħ | $\text{{\igfont 𐑫}}$ eternal chirality | $\text{{\igfont 𐑓}}$ memoryless | Winding collapse $\text{{\igfont 𐑭}}\!\to\!\text{{\igfont 𐑷}}$ |
| Φ | $\text{{\igfont 𐑹}}$ Frobenius-special | $\text{{\igfont 𐑬}}$ partial/Z$_2$ | $\mu\circ\delta\neq\mathrm{id}$ |
| Ð | $\text{{\igfont 𐑦}}$ self-written | $\text{{\igfont 𐑼}}$ infinite-dim field | State space externally imposed |
| Þ | $\text{{\igfont 𐑶}}$ irreducible product | $\text{{\igfont 𐑡}}$ network branching | Holistic topology destroyed |
| ƒ | $\text{{\igfont 𐑐}}$ quantum | $\text{{\igfont 𐑱}}$ classical | No coherence |
| Ç | $\text{{\igfont 𐑧}}$ slow/near-eq | $\text{{\igfont 𐑪}}$ trapped-ordered | Molecule frozen, not equilibrating |
| Ω | $\text{{\igfont 𐑭}}$ integer winding | $\text{{\igfont 𐑷}}$ trivial | Radiation damage destroys protection |

Total structural distance: $d = 5.74$ — well into "structurally remote, different regime."

---

## ENVIRONMENT

**Python:** 3.12+  
**Dependencies:** numpy ($\ge$ 2.4.6), imasmic\_core ($\ge$ 0.5.69), rdkit (optional, for molecular design)  
**Virtual environment:** `.venv/` at repository root  
**Lean 4 (optional):** Mathlib v4.28.0 at `p4rakernel/p4ramill/` for formal verification  

```
cd /home/mrnob0dy666/imsgct/red-hot_rebis
source .venv/bin/activate
```

---

## FILES

- **INDEX.md** — Browsable static reference data (CLINK layers, IMASM canonicals, materials catalog, **compound catalog**, **crystal discovery**)
- **README.md** — Project overview, architecture, quick start, structural commentary
- **USER_GUIDE.md** — Comprehensive user guide with all commands, workflows, and troubleshooting
- **rebis.py** — Unified CLI entry point
- **shared/primitives.py** — 12 primitive ordinals, weights, distance functions
- **shared/IG_catalog.json** — 4,027+ catalog entries (symlink to canonical)
- **shared/elem2imasm.py** — Element-to-IMASM encoding (symlink)
- **shared/reactivity.py** — Reactivity pattern matching (symlink)
- **imas/compound_imasm.py** — SMILES→IMASM 8-token encoder
- **imas/fg_exhaustive.py** — 190 SMARTS patterns across 11 IMASM tokens
- **imas/reactivity_imasm.py** — Reaction→IMASM transition analyzer
- **imas/compound_catalog.py** — 54 compounds, 15 IG types, 4,027+ catalog entries
- **imas/molecular_crystal_designer.py** — Crystal-guided molecular discovery (700+ lines)
- **clink/README_CLINK.md** — Standalone CLINK chain documentation
- **clink/PIPELINE_README.md** — CLINK pipeline architecture
- **serpentrod/manuscript.md** — Complete Serpent's Rod theory
- **ch3mpiler/docs/** — CH$_3$MPILER documentation
- **gene_imscriber/README.md** — Gene Imscriber overview
- **popular_protein/00_MASTER_MANIFEST.md** — Protein structure validation manifest
- **imasm_iterator/IMASM_SPACE_MAP_REPORT.md** — IMASM arrangement space report
- **Makefile** — Build, verify, test, clean automation

---

## AUTHOR

**Lando$\otimes\odot$perator**

The Red-Hot Rebis is the coagulation of the Imscribing Grammar's bio-organic engine — a tool whose purpose is to be *taken up into the loop*, not to stand outside it as a finished monument.

> *"The serpent winds, the rod stands, the vessel contains — $\mu \circ \delta = \mathrm{id}$."*  
> Not as a conclusion. As a *signature of process*.

---

## VERSION HISTORY

| Version | Date | Summary |
|---------|------|---------|
| 2.3.4 | 2026-06-28 | **Rich Formatting + Exact SMILES Edition** — `shared/rich_output.py` deployed repo-wide to all 234 Python files; `bond_fragment_integrator.py` delivers exact RDKit fragment SMILES in retrosynthesis output; `--smiles` CLI flag for direct SMILES input; SMILES FG detection via RDKit SMARTS; no more fake placeholder SMILES; migration scripts (`migrate_rich.py`, `fix_*.py`); all docs updated |
| 2.3.3 | 2026-06-27 | **Compound IMASM Edition** — New pillar: IMASM Compound Pipeline (compound_imasm.py, fg_exhaustive.py, reactivity_imasm.py, ig_bridge.py, compound_catalog.py); Crystal-Guided Molecular Discovery (molecular_crystal_designer.py, odot_finder.py); DMT-⊙ (5-nitro-bufotenin) discovery; 54 compounds, 15 IG types, 31 arrangements, 4,027+ catalog entries; cross-domain analogies; all docs updated |
| 2.1.1 | 2026-06-27 | Updated docs for rhr_p4rky expansion: 32 modules (added `belnap_c4.py`, `decay_chain.py`, `papers/` with 3 millennium docs); added symlinks `shared/elem2imasm.py` and `shared/reactivity.py`; INDEX.md L8 tier corrected to O_∞ |
| 2.1.0 | 2026-06-10 | IMASM+CLINK Edition — CLINK chain integrated as Pillar V, IMASM iterator added, 151 .py files, 58,815 loc |
| 2.0.0 | 2026-05 | Four-pillar integration (Serpent's Rod + CH$_3$MPILER + Pipeline + Gene Imscriber) |
| 1.0.0 | 2026-04 | Initial integration — rebis.py CLI, shared primitives layer |

---

## COLOPHON

This page was woven on the wyrding loom — distinction by distinction, connection by connection — by order of $\text{{\igfont 𐑦}}$ and $\text{{\igfont 𐑸}}$, the twin sisters who co-originate every being that ever was or ever will be. The glyphs are Shavian (U+10450–U+1047F), set in Everson Mono. The crystal contains 17,280,000 structural types. The grammar is its own ground.

**Structural type of this manual:** $$\langle\text{{\igfont 𐑦}};\ \text{{\igfont 𐑶}};\ \text{{\igfont 𐑾}};\ \text{{\igfont 𐑹}};\ \text{{\igfont 𐑐}};\ \text{{\igfont 𐑧}};\ \text{{\igfont 𐑔}};\ \text{{\igfont 𐑠}};\ \odot;\ \text{{\igfont 𐑖}};\ \text{{\igfont 𐑙}};\ \text{{\igfont 𐑭}}\rangle$$