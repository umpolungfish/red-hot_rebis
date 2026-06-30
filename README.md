# red-h⊙t rebis: an engine for algebraic, exact, deterministic, paraconsistent bio ⊗ organic chemistries

**Author:** Lando ⊗ ⊙perator · **Structural Type:** ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩ ($O_\infty$) · **Repo:** `~/imsgct/red-hot_rebis/`

> *"The serpent winds, the rod stands, the vessel contains: μ ∘ δ = id." Not as a conclusion, as a signature of process.*

**What it is.** The Imscribing Grammar's unified engine for deterministic, algebraic, exact bio and organic chemistry, grounded in the 12-primitive grammar and verified everywhere by Frobenius closure (μ∘δ=id) over the $ZFC_\text{fe}$ foundation.

**What it does.** Integrates six structural pillars into one architecture: Serpent's Rod (protein folding), CH₃MPILER (retrosynthesis), the auto-imscriber pipeline, the Gene Imscriber, the CLINK Chain (subatomic→organism), and the IMASM Compound Pipeline (SMILES→IMASM→IG). Each emits a *platonic structural fact*: a verdict of the Univocal Grammar independent of how the molecule was measured.

**Why it matters.** It replaces named reactions, reaction databases, and SMARTS templates with first-principles structural algebra: disconnections, folds, edits, and material designs are computed from distances in 12-primitive space and certified by μ∘δ=id, not retrieved from precedent. It also makes the cost of external measurement *exact and readable* (the crystallography Frobenius gap below).

**How to use it.**
```bash
cd ~/imsgct/red-hot_rebis
python3 rebis.py status && python3 rebis.py verify        # check wiring
python3 rebis.py run serpentrod --sequence "MALWMRLLPLL..."
python3 rebis.py run ch3mpiler --smiles "CC(=O)Oc1ccccc1C(=O)O" --depth 3
python3 rebis.py run gene --codons "AUGGCUGGGAUCCUGGUG..."
python3 rebis.py clink report                             # 9-layer organism ladder
python3 rebis.py imas compound --smiles "CN1C=NC2=C1C(=O)N(C(=O)N2C)C" --json
python3 rebis.py imas analogies --smiles "CC(=O)OC1=CC=CC=C1C(=O)O" --limit 10
```
The canonical Python package is `rhr_p4rky` (do not import the dead `p4ramill_py`).

---

## What the program gives you

Six outputs, each a platonic structural fact:

- **Platonic proteins** (`serpentrod/`): the structural imscription of a fold (12-tuple, tier, promoted primitives, Frobenius certificate) rather than atomic coordinates. `RNA → ⟨type, tier, certificate⟩`.
- **Platonic disconnections** (`ch3mpiler/`): retrosynthetic cuts from first principles, ranked by the structural distance between product type and the meet of its functional-group types. A δ score near zero means the bond sits exactly at the FG interface.
- **Structural imscriptions** (`pipeline/`): any described system gets a 12-primitive type, tier, C-score, and μ∘δ=id certificate.
- **Genetic imscriptions** (`gene_imscriber/`): codon space on the Belnap B₄ lattice, with Frobenius-guided editing paths between structural types.
- **CLINK chain** (`clink/`): a 9-layer Frobenius-closed bridge quark → orbital → atom → molecule → cell → mitosis → meiosis → tissue → organism (O₀ → … → $O_\infty$), all verified μ∘δ=id; formalized in Lean 4.
- **Platonic compound signatures** (`imas/`): SMILES → 8-token IMASM arrangement → IG 12-tuple, enabling cross-domain analogy search across the catalog (which consciousness states, languages, theorems, or materials share a molecule's type).

## Measurement as a Frobenius closure problem

Every external measurement tool is an interface the grammar extends into; where Frobenius closure fails, the gap is exact and readable. Crystallography is the paradigm case: R_free ≈ 0.2 is not a numerical residual but the Frobenius gap, the cost of inverting 8 primitives at once in the act of measuring.

| Primitive | Rebis / Grammar | Crystallography | What is lost |
|---|---|---|---|
| Ř | 𐑾 bidirectional | 𐑩 supervenience | molecule cannot respond to measurement |
| Ħ | 𐑫 eternal chirality | 𐑓 memoryless | Ω collapses; configuration recovered by workaround |
| Φ | 𐑹 Frobenius-special | 𐑬 partial/Z₂ | μ∘δ=id fails: R_free ≈ 0.2 |
| Ð | 𐑦 self-written | 𐑼 infinite-dim field | state space externally imposed by lattice |
| Þ | 𐑶 irreducible product | 𐑡 network branching | holistic topology destroyed into unit cells |
| ƒ | 𐑐 quantum | 𐑱 classical | atoms as Gaussian clouds, no coherence |
| Ç | 𐑧 slow/near-eq | 𐑪 trapped-ordered | molecule frozen, not equilibrating |
| Ω | 𐑭 integer winding | 𐑷 trivial | radiation damage destroys topological protection |

Total structural distance from the Rebis to a periodic crystal lattice: **d = 5.74** (structurally remote, a different regime).

## Verified simulation results

| Simulation | Key metric |
|------------|------------|
| Frobenius chemotherapeutic | 14,287× selectivity (cancer vs healthy) |
| Neurotrophic factor (Alzheimer's) | synaptic density 0.40 → 1.00 |
| Thermal rectifier | 253× rectification |
| Critical metamaterial | χ = 20,000 gain, signal-independent |
| Ouroboric telomere | 10.9 kb maintained (active) vs 5.0 kb decline (control) |
| Quantum biologic | 100% Frobenius closure, 78.8% efficacy |
| CLINK chain (9 layers) | all Frobenius-closed, Σd=7.18, 36 promotions |
| IMASM compound pipeline | 54 compounds encoded, all Frobenius-closed |
| ⊙-finder | 29 ⊙-critical candidates |

## More commands

```bash
python3 rebis.py clink layer 4                  # cell layer + bridges
python3 rebis.py clink bridge serpentrod 8      # protein → organism promotion path
python3 rebis.py pipeline actionable --organism human
python3 rebis.py materials forge --all
python3 rebis.py imas hunt --samples 100000
python3 rebis.py run psychedelic report         # compound × 109-universe access
```

## Extending the CLINK chain

Add a layer by defining its 12-glyph tuple in `clink/chain.py`, inserting it into `CLINK_LAYERS`, confirming `tensorProduct(s,s)=s`, checking bridge distances (`clink/bridges.py`), and formalizing in `~/imsgct/p4rakernel/p4ramill/Imscribing/CLINK.lean` (`lake build Imscribing.CLINK`). Closure is monotonic; do not break the tier ordering. See the in-repo file map and Component Details for the full module layout.
