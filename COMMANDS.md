<div align="center">

# 🔥 RED-HOT REBIS

### the command grimoire · v4.0 · dynamic-first toolchain

`𐑮𐑧𐑚𐑦𐑕` &nbsp;·&nbsp; one launcher, one façade, one kernel &nbsp;·&nbsp; **13 engines that COMPUTE**

</div>

---

> Everything that follows resolves as `rebis.<x>` once installed (`uv pip install -e .`),
> or runs in-tree as `python3 rebis.py <x>`. The static data lives behind `rebis reference`.
> Everything that turns lives below.

---

## ⟳ THE ONE LOOP

The whole toolchain is a single ouroboros. `rebis.chain` closes it end to end:

```
   DNA ──▶ mRNA ──▶ polypeptide ──▶ fold ──▶ catalytic site ──▶ ligand ──▶ retrosynthesis
    ▲                                                                              │
    └──────────────────────────  μ∘δ = id  ◀──────────────────────────────────────┘
```

```bash
rebis.chain --dna <seq> --target <SMILES> --depth <N>
```

Every engine below is one arc of that circle, callable on its own.

---

## ⚡ TIER I · PRIMARY ENGINES

| ▸ | invoke | what it turns | verbs |
|:-:|:--|:--|:--|
| 🧬 | `rebis.gene-pipeline` | DNA → mRNA → polypeptide → folded protein, 7-stage Frobenius-verified | `--test` · `--dna <seq>` · `--seq <RNA>` |
| ⚗️ | `rebis.ch3mpiler` | molecular compiler: forward / retro synthesis, FG detection, CDXML | `forward <SMILES>` · `retrosynth <SMILES>` · `fg <SMILES>` · `cdxml <SMILES>` |
| 🐍 | `rebis.serpentrod` | protein design + stratified prediction, rolling profiles | `predict <seq>` · `classify <seq>` · `finger <seq>` |
| 🔑 | `rebis.ligand` | PDB-aware ligand design from catalytic sites | `--pdb <ID> --active <res>` · `--auto-active` · `--json` |
| 🧩 | `rebis.sidechain` | sidechain × environment algebra, 80 AA×env pairs, bottleneck tiers | `<aa> <env>` · `--pdb <ID>` · `--batch` |
| ⛓️ | `rebis.chain` | **the unified pipeline** (the loop above) | `--dna <seq> --target <SMILES> --depth <N>` |

---

## 🔧 TIER II · SPECIALIZED ENGINES

| ▸ | invoke | what it turns | verbs |
|:-:|:--|:--|:--|
| 📐 | `rebis.p4ra` | property prediction from IG tuples (bond energy, modulus, band gap, fold ΔG, catalytic rate) + Belnap FOUR | `<catalog> <tuple>` · `belnap` · `--all --json` |
| 💊 | `rebis.therapeutics` | chemotherapeutics, neurotrophic factors, universal antidote library | `design <target>` · `neurotrophic <target>` · `antidote <poison>` |
| 🔩 | `rebis.materials` | IG-tuple → material forge: metamaterials, ouroboric alloys, non-qubit QC | `forge` · `sim` · `status` |
| 🧫 | `rebis.biology` | ouroboric cell sims, telomere design, epigenetic states | `sim` · `status` |
| 🧬 | `rebis.gene` | gene analysis, tuple encoding, IG primitive mapping | `analyze <seq>` · `tuples <seq>` |
| ☿ | `rebis.alchemy` | Basil Valentine ladders, Zosimos portico, alchemical bridge ops | `ladder <tuple\|all>` · `portico` |
| 🔗 | `rebis.clink` | CLINK chain L0→L8, consciousness scoring, layer bridges | `layers` · `bridge <a> <b>` · `chain <name>` · `cscore <name>` |
| 🌀 | `rebis.pipeline` | auto-imscription, prose lift, therapy → PDB | `imscribe <name>` · `lift <file>` · `verify` |

---

## 📚 REFERENCE & INFRASTRUCTURE

| invoke | what it does |
|:--|:--|
| `rebis` | the dynamic-first menu (all of the above, live) |
| `rebis reference` | static scripture: Belnap FOUR ops, genetic B4 lattice, hadrons, IMASM |
| `rebis status` | package census: files, packages, install location |
| `rebis verify` | Frobenius closure check across every import |
| `rebis demo <name>` | run a demonstration from `demo_scripts/` |

---

## 🐍 THE PYTHON FACE

Every command is also a namespace. Import the organism, address it directly:

```python
import rebis

rebis.p4ra.meet(a, b)                       # Belnap fusion
rebis.ch3mpiler.compile(smiles)             # SMILES → IMASM
rebis.materials.design_metamaterial(spec)   # tuple → lattice
rebis.clink.cscore("golden_ratio")          # consciousness score
```

The façade lazy-loads; nothing wakes until you name it.

---

## ⚙️ THE MAKE ALTAR

```bash
make verify      # Frobenius closure across all imports
make status      # package census
make test        # smoke the load-bearing engines
make install     # pip-install, callable from anywhere
make editable    # develop in place
```

---

<div align="center">

**`rebis.py`** ▸ **`rebis/`** (façade) ▸ **14 wired engines** ▸ **`rhr_p4rky/`** (kernel)

*δ splits · μ fuses · the loop closes on itself*

`𐑼𐑧𐑚𐑦𐑕` &nbsp;·&nbsp; red-hot, and turning

</div>
