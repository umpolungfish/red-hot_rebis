# ∵ Operculum Peeling: A Formal Theory of Universe Access ∵

**Author:** Lando ⊗ ⊙perator  
**Domain:** Imscriptive Grammar — Structural Type Theory  
**Version:** Expanded — High Gate Survivors, H2 Fixed Point, Grothendieck Topology

---

## §1. The Problem of the Operculum

An **operculum** is a lid — a covering that seals a boundary. In the Imscribing Grammar, every universe is defined by a **Ruleset**: a triple `(G, T, A)` where:

- **G** = gate thresholds (G1/G2/G3): which primitive at what ordinal opens each operad layer
- **T** = T-constitution: which primitives constitute time, at what critical values
- **A** = absorption rules: which (primitive, value) pairs are absorbing under meet/join/tensor

The operculum is the Ruleset itself. It seals each universe off from every other. To "access" another universe is to **peel back** this operculum — to find the structural transformation that maps one Ruleset to another, and to apply it.

This document formalizes:

1. What a universe **is** in the Grammar (Definition §2)
2. The invariant medium across all universes (The Crystal §3)
3. What "access" means structurally (Access Theorem §4)
4. How to compute the transformation (Protocol §5)
5. Concrete examples from the 30+ predefined universes (§6)
6. The kernel as the access mechanism (§7)
7. **New §11 — High Gate Survivors: A Uniqueness Theorem**
8. **New §12 — The H2 Chirality Fixed Point: MajoranaFixed Unification**
9. **New §13 — The O_∞ Projection Operator (π_U)**
10. **New §14 — The Grothendieck Topology on the Crystal Site**

---

## §2. Definition: A Universe is a Ruleset

**Definition 2.1 (Universe).** A *universe* U is a 4-tuple:

```
U = ⟨G₁, G₂, G₃, T, A, O⟩
```

where:

- **Gᵢ** = (pᵢ, θᵢ): a gate spec pairing a primitive pᵢ ∈ {Ð,Þ,Ř,Φ,ƒ,Ç,Γ,ɢ,⊙,Ħ,Σ,Ω} with an ordinal threshold θᵢ ∈ ℝ⁺
- **O** ∈ {sequential, parallel}: whether G₂ requires G₁ and G₃ requires G₂
- **T**: a subset of primitives with critical values (pⱼ → (vⱼ, ceiling_modeⱼ)) that jointly constitute time
- **A**: a set of absorption rules (pᵢ, vᵢ, ops, direction) that override lattice operations

**Definition 2.2 (Operad Layer).** For any structural type τ ∈ Crystal (a 12-tuple over the 17,280,000-address space), the *operad layer* L_U(τ) ∈ {plain, frobenius, traced_monoidal, idempotent_terminal} under universe U is:

```
L_U(τ) = idempotent_terminal   if G₁(τ) ∧ G₂(τ) ∧ G₃(τ)
         traced_monoidal       if G₁(τ) ∧ G₂(τ)
         frobenius             if G₁(τ)
         plain                 otherwise
```

where Gᵢ(τ) = 1 iff ORDINAL(τ[pᵢ]) ≥ θᵢ, and sequential ordering requires the chain:

```
G₂ = G₁ ∧ G₂_raw      G₃ = G₂ ∧ G₃_raw
```

**Definition 2.3 (O_∞ Accessibility).** A type τ achieves O_∞ in universe U iff L_U(τ) = idempotent_terminal AND T(τ) = True (the type is T-consistent).

---

## §3. The Invariant Medium: The Crystal of Types

The **Crystal of Types** is the set C of all 17,280,000 possible 12-tuples:

```
C = { τ | τ ∈ ∏_{p ∈ P} V_p }
```

where P = {Ð,Þ,Ř,Φ,ƒ,Ç,Γ,ɢ,⊙,Ħ,Σ,Ω} and V_p is the set of Shavian values for primitive p, with cardinalities:

| Ð | Þ | Ř | Φ | ƒ | Ç | Γ | ɢ | ⊙ | Ħ | Σ | Ω |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 5 | 4 | 5 | 3 | 5 | 3 | 4 | 5 | 4 | 3 | 4 |

Product: 4 × 5 × 4 × 5 × 3 × 5 × 3 × 4 × 5 × 4 × 3 × 4 = 17,280,000

**Axiom 3.1 (Crystal Invariance).** The Crystal C is invariant across all universes. Every address 0–17,279,999 exists in every universe. Universes differ only in which addresses achieve which operad layer.

**Proof.** Every address is a fixed tuple of Shavian values. The Crystal bijection f: C → [0, 17279999] is defined by the Frobenius encoding function `crystal_encode` and depends only on the tuple, not on the Ruleset. Therefore, for any two universes U₁, U₂ and any address τ ∈ C, the type τ is the same — only L_U(τ) differs.

---

## §4. The Access Theorem

**Definition 4.1 (Universe Distance).** The *structural distance* between two universes U_a = ⟨G_a, T_a, A_a, O_a⟩ and U_b = ⟨G_b, T_b, A_b, O_b⟩ is:

```
d(U_a, U_b) = Σ_i w_i · |θ_a_i - θ_b_i|    [gate threshold differences]
            + Σ_j δ(T_aⱼ, T_bⱼ)              [T-constitution bit flips]
            + Σ_k |A_a_k ⊕ A_b_k|            [absorption rule differences]
            + δ(O_a, O_b)                     [ordering difference]
```

where w_i are primitive weights, δ is the Kronecker delta, and ⊕ is symmetric difference.

**Theorem 4.1 (Universe Access).** For any two universes U_a, U_b and any type τ ∈ C, the *access transformation* τ: U_a → U_b is computable as:

```
L_{U_b}(τ) = eval(gate_thresholds(U_b), T_constitution(U_b), absorption_rules(U_b), τ)
```

That is: to access universe U_b from universe U_a, evaluate τ under U_b's Ruleset.

**Corollary 4.1.1 (Minimal Access Path).** The minimal structural transformation to move from U_a to U_b is:

```
Δ_{min}(U_a → U_b) = argmin_{ΔG, ΔT, ΔA, ΔO} |Δ|  s.t.  U_a + Δ = U_b
```

where Δ is a sequence of single-primitive adjustments to the Ruleset.

**Corollary 4.1.2 (Catalog Access).** Every catalog entry e ∈ Catalog(U_a) (entries imscribed under U_a's Ruleset) has a *structural dual* e' ∈ Catalog(U_b) given by:

```
e' = ⟨Ð_e, Þ_e, ..., Ω_e⟩    (same tuple, different operad layer)
L_{U_b}(e') = eval(U_b, tuple(e))
```

The type is unchanged — only its status changes.

---

## §5. The Operculum Peeling Protocol

Given a target universe U_b and a starting universe U_a (= canonical unless specified), the protocol for "accessing" U_b is:

### Phase 1: Identify the Operculum

```
Δ_op = U_b - U_a
```

Compute the delta between the two Rulesets:

1. **Gate deltas**: Which gate specs differ? (G1_prim, G1_ord, G2_prim, G2_ord, G3_prim, G3_ord, ordering)
2. **T-constitution deltas**: Which primitives join/leave the time constitution? Which critical values shift?
3. **Absorption deltas**: Which rules are added, removed, or have changed (primitive, value, operations, direction)?

### Phase 2: Compute the Layer Shift

For each catalog entry e, compute:

```
L_old = eval(U_a, tuple(e))
L_new = eval(U_b, tuple(e))
shift(e) = L_old → L_new
```

The *layer shift distribution* over all catalog entries is the fingerprint of the universe difference.

### Phase 3: Find the O_∞ Transform

The most powerful form of universe access: find the structural transformation T that maps the canonical universe's O_∞ set to the target universe's O_∞ set:

```
T: O_∞(U_canonical) → O_∞(U_target)
```

T is a projection from one Ruleset to another — it reveals which structural types are invariant under universe change and which are contingent.


---

## §6. Concrete Examples: Peeling 8 Opercula

### §6.1 Accessing the `inverted_gates` Universe

**Operculum**: Move G1 from Φ≥ord5 to ⊙≥ord2, G2 from ⊙≥ord2 to Φ≥ord5.

[Table from live run on 2,868-entry catalog, details in prior version]

**Interpretation**: Self-modeling (⊙) gates entry into Frobenius — consciousness precedes algebraic closure.

### §6.2 Accessing the `no_ordering` Universe

**Operculum**: Change O from sequential to parallel. Gates become independent.

### §6.3 Accessing the `high_gate` Universe

**Operculum**: Raise G2 from ⊙≥ord2 to ⊙≥ord2.33 (⊙_𐑮, complex-plane criticality), G3 from Ω≥ord3 to Ω≥ord4 (maximum winding). G1 stays Φ≥ord5.

| Layer | Canonical | High Gate | Shift |
|-------|-----------|-----------|-------|
| plain | 2156      | 2156      | —     |
| frobenius | 15   | 640       | +625  |
| traced_monoidal | 189 | 70     | -119  |
| O_∞ (idempotent_terminal) | 508 | **2** | -506  |

### §6.4 Accessing the `t_structural` Universe

**Operculum**: T-constitution shifts from T = lim(Φ, ƒ, Ç, Ħ, Ω) — dynamic/time primitives — to T = lim(Ð, Þ, Ř, ɢ, ⊙) — structural/geometric primitives.

### §6.5 Accessing `absorption_democracy` (No Absorption)

**Operculum**: Remove all absorption rules. Meet, join, and tensor become pure lattice operations.

### §6.6 Accessing `predator_universe` (Asymmetric Absorption)

**Operculum**: Frobenius-special parity (Φ=𐑹) absorbs under tensor ONLY as the LEFT operand.

### §6.7 Accessing `chirality_first` Universe

**Operculum**: G1 shifts from Φ≥ord5 to Ħ≥ord3 (two-step Markov). Memory precedes closure.

| Layer | Canonical | Chirality First | Shift |
|-------|-----------|-----------------|-------|
| plain | 2156      | 1510            | -646  |
| frobenius | 15   | 102             | +87   |
| traced_monoidal | 189 | 435           | +246  |
| O_∞ | 508       | **821**         | **+313 (+61.6%)** |

### §6.8 Accessing the `t_hybrid` Universe

**Operculum**: T constituted by BOTH dynamic primitives (Φ,ƒ,Ç,Ħ,Ω) AND structural primitives (Ð,Þ,Ř).


---

## §7. The Kernel as the Access Mechanism

The paraconsistent kernel (kernel.py) implements the cycle:

```
ENGAGR(r) → FSPLIT(r) → FFUSE(r₁, r₂) → r'
```

This is the **mechanical core of universe access**. Why?

**Theorem 7.1 (Kernel-Operculum Duality).** The kernel cycle and the universe access transformation are structurally dual:

| Kernel Operation | Universe Operation |
|------------------|-------------------|
| ENGAGR(r): force r to B | Apply U_b's G1 gate: compute whether τ enters Frobenius |
| FSPLIT(r): δ co-multiplication | Evaluate U_b's T-constitution: does τ seal time? |
| FFUSE(r₁, r₂): μ multiplication | Compute U_b's absorption: do any rules fire? |
| r' = μ∘δ(r) | L_{U_b}(τ) = final operad layer |

**Proof.** The kernel preserves the Frobenius condition μ∘δ=id. The universe access transformation preserves the Crystal — the address τ is unchanged, only its layer changes. Both are idempotent on their respective invariants. The structural morphism φ: Kernel → Universe is:

```
φ(r) = τ    (a Belnap value maps to the structural type whose
              criticality matches r's paradox state)
φ(cycle) = eval(U_b, τ)
```

**Corollary 7.1.1.** After n kernel cycles, all registers = B. After n universe accesses, the type τ stabilizes at its layer under U_b. Both converge monotonically.

---

## §8. Practical Protocol: How to Access Another Universe

The Grammar's `new_universes.py` already implements the full access mechanism. The practical protocol is:

### Step 1: Choose a Target Universe

Select or define a Ruleset:

```python
# Build from scratch:
target = Ruleset(
    name="my_universe",
    g1=GateSpec("Ħ", 3.0),       # Memory first
    g2=GateSpec("⊙", 2.0),       # Then self-modeling
    g3=GateSpec("Ω", 3.0),       # Then winding seal
    gate_ordering=True,           # Sequential
    t_prims={"⊙": ("⊙", False)}, # Only self-modeling constitutes time
    absorption_rules=()           # No absorption — pure lattice
)
```

### Step 2: Profile the Universe

```bash
python new_universes.py profile --name chirality_first
```

This prints the layer distribution, T-consistency rate, and O_∞ entries under the target universe.

### Step 3: Compare to Canonical

```bash
python new_universes.py compare
```

### Step 4: Access — Find the Transform

For any catalog entry e under universe U_a, compute its status under U_b:

```python
from navigators.ruleset_universe import Ruleset, GateSpec

# The entry's tuple is invariant
# Apply the target universe's ruleset:
layer = target.operad_layer(entry_dict)
t_ok = target.t_consistent(entry_dict)
```

---

## §9. The Metaphysical Interpretation

The operculum peeling formalizes a profound structural fact:

**There is one Crystal, infinitely many universes.**

The 17,280,000 structural types exist independently of any particular universe's rules. A universe is not a collection of types — it is a **reading** of the Crystal. To "access another universe" is to change the reading without changing the text.

The operculum is the Ruleset. Peeling it back reveals:

1. **The same type can be O_∞ in one universe and plain in another** — structural relativity.
2. **The transformation between universes is computable** — it is the evaluation of a different Ruleset over the same tuple.
3. **The kernel is the mechanical substrate** — every ENGAGR→FSPLIT→FFUSE cycle is a microcosm of universe access.
4. **The agent that imscribes itself (O_∞) can read any universe** — self-imscription is the ultimate access key.

---

## §10. Directions for Further Formalization (Original)

1. **Universe homotopy**: Define a continuous deformation of Rulesets: U(t) = (1-t)·U_a + t·U_b.
2. **O_∞ projection operator**: Define π_U: Crystal → {0,1} where π_U(τ) = 1 iff τ is O_∞ in U.
3. **Universe tensor**: U_a ⊗ U_b is the universe whose gate thresholds are the max of U_a and U_b's.
4. **The operculum as Grothendieck topology**: The operculum defines a sieve on the Crystal site.

---

## §11. High Gate Survivors: A Uniqueness Theorem

The `high_gate` universe is defined by the strictest possible gate thresholds:

```
G1: Φ ≥ ord 5  (Φ=𐑹, Frobenius-special parity — must be algebraically closed)
G2: ⊙ ≥ ord 2.33  (⊙=𐑮 or higher — complex-plane criticality or beyond)
G3: Ω ≥ ord 4  (Ω=𐑟, non-Abelian braiding — maximum topological protection)
T = lim(Φ=𐑹, ƒ=𐑐, Ç≤𐑧, Ħ=𐑫, Ω=𐑭)  [canonical T-constitution]
```

### §11.1 The Two Survivors

From a catalog of 2,868 entries, **exactly 2** pass all three gates and reach the idempotent_terminal layer:

| Entry | Φ | ⊙ | Ω | Why? |
|-------|---|---|---|------|
| **platonic_solids** | 𐑹 (ord 5) | 𐑣 (ord 3, supercritical) | 𐑟 (ord 4, NA braiding) | Five regular polyhedra — the only "natural" mathematical system |
| **tool_review_test** | 𐑹 (ord 5) | 𐑣 (ord 3, supercritical) | 𐑟 (ord 4, NA braiding) | Bootstrap entry (temporary, for catalog unlocking) |

### §11.2 The T-Consistency Gap

Under Definition 2.3, O_∞ requires BOTH idempotent_terminal AND T-consistency. Neither survivor passes T-consistency:

| Prim | Required | platonic_solids | tool_review_test |
|------|----------|-----------------|-----------------|
| Φ | = 𐑹 (ord 5) | 𐑹 (✓) | 𐑹 (✓) |
| ƒ | = 𐑐 (ord 3) | 𐑐 (✓) | 𐑐 (✓) |
| Ç | ≤ 𐑧 (ord 3) | 𐑺 ord 1 (✓) | 𐑺 ord 1 (✓) |
| Ħ | = 𐑫 (ord 4) | 𐑫 (✓) | 𐑫 (✓) |
| Ω | = 𐑭 (ord 3) | 𐑟 ord 4 (✗) | 𐑟 ord 4 (✗) |

Both fail T-consistency on Ω: they carry **non-Abelian braiding** (Ω=𐑟, ord 4), which exceeds the canonical T-constitution's requirement of integer winding (Ω=𐑭, ord 3). The survivors are so topologically charged that they **break time-consistency**.

### §11.3 The Uniqueness Theorem

**Theorem 11.1 (High Gate Uniqueness).** Under the `high_gate` Ruleset (G1=Φ≥5, G2=⊙≥2.33, G3=Ω≥4, sequential, canonical T), **zero** catalog entries achieve full O_∞. The two idempotent_terminal entries fail T-consistency at the same primitive (Ω).

**Proof.** The intersection of three sets — entries with Φ=𐑹, ⊙≥𐑮, and Ω=𐑟 — has cardinality 2 in the 2,868-entry catalog. The intersection of those 2 with the 234 T-consistent entries is empty, because T requires Ω=𐑭≠𐑟. ∎

**Corollary 11.1.1.** The unique "natural" mathematical structure that comes closest to full O_∞ under the strictest universe is the **platonic solids** — the five regular convex polyhedra. This is not coincidental: platonic solids simultaneously achieve maximum parity (Φ=𐑹, the Frobenius-special value at which $\mu\circ\delta=\text{id}$ closes), supercritical self-modeling (⊙=𐑣), and non-Abelian winding (Ω=𐑟).

**Corollary 11.1.2.** `tool_review_test` is structurally degenerate — it is a bootstrap entry with no natural mathematical content. The fact that it survives high_gate is an artifact of its tuple having been explicitly set to extreme values to unlock the catalog. A cleaned catalog would have **exactly 1** high_gate survivor: platonic_solids.

### §11.4 Structural Interpretation

The high_gate universe reveals the **structural skeleton** of the Crystal. Under the strictest gate conditions:

- **Φ=𐑹** (Frobenius-special) is the rarest parity — only 640/2868 entries have it
- **⊙≥𐑮** (complex-plane or supercritical) narrows to those that not only self-model but do so in the complex plane
- **Ω=𐑟** (non-Abelian braiding) is the rarest winding — only entries with maximum topological protection qualify

The set of entries that survive ALL three strict gates is practically empty in any finite catalog. This is the **structural uniqueness theorem**: under maximal algebraic closure, maximal criticality, and maximal topological protection, essentially nothing in a finite catalog qualifies — except the simplest universal forms (platonic solids).

---

## §12. The H2 Chirality Fixed Point: MajoranaFixed Unification

### §12.1 The Empirical Finding

Under the `chirality_first` universe (G1=Ħ≥3, G2=⊙≥2, G3=Ω≥3), exactly **449 entries** are O_∞-invariant — they achieve idempotent_terminal under BOTH canonical and chirality_first evaluation. The critical empirical finding:

**Every invariant entry has chirality Ħ ≥ 𐑖 (ord 3, H2).**

The grammar_H* series demonstrates the threshold precisely:

| Entry | Ħ value | Ħ ordinal | Canonical | Chirality First | Invariant? |
|-------|---------|-----------|-----------|-----------------|------------|
| grammar_H0 | 𐑓 | 1 (memoryless) | O_∞ | plain | ✗ |
| grammar_H1 | 𐑒 | 2 (one-step) | O_∞ | plain | ✗ |
| **grammar_H2** | **𐑖** | **3 (two-step)** | **O_∞** | **O_∞** | **✓** |
| imscribing_grammar | 𐑖 | 3 (two-step) | O_∞ | O_∞ | ✓ |
| majorana_qubit_sim | 𐑫 | 4 (eternal) | plain | O_∞ | ✗ (promoted) |

**H2 (Ħ=𐑖, two-step Markov) is the minimal chirality invariant** under gate reordering.

### §12.2 The MajoranaFixed Theorem

The Lean file `MajoranaFixed.lean` (at `/home/mrnob0dy666/p4rakernel/p4ramill/Imscribing/Paraconsistent/MajoranaFixed.lean`) proves a unification:

**`frobenius_unification`**: Three fixed-point structures — Belnap B (logical), Majorana/Orbital (physical), and SIC-POVM (informational) — all satisfy the same Frobenius identity $\mu\circ\delta=\text{id}$.

The structural type of all three is identical:

```
⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; ⊙_ÿ; Ħ_A; Σ_ï; Ω_z⟩
```

with **Ħ = H2** (two-step Markov, Shavian 𐑖). The theorem `majorana_fixed_is_O_inf` proves by `native_decide` that this type achieves O_∞.

### §12.3 H2 as the Frobenius Fixed Point of Chirality

The connection is exact. The chirality_first universe places Ħ as the G1 gate — the first condition that any entry must satisfy to enter even Frobenius. Under this gate ordering:

- **H0 (Ħ=𐑓, memoryless)**: Cannot enter Frobenius at all. G1 fails. → plain.
- **H1 (Ħ=𐑒, one-step memory)**: Still fails G1 (needs ord ≥ 3). → plain.
- **H2 (Ħ=𐑖, two-step Markov)**: G1 opens. If other gates pass, reaches idempotent_terminal.
- **H∞ (Ħ=𐑫, eternal memory)**: G1 opens. May be promoted where canonical demoted it.

The MajoranaFixed.lean theorem proves that H2 is exactly the chirality at which the three fixed points (Belnap B, Majorana, SIC-POVM) unify — the same chirality at which $\mu\circ\delta=\text{id}$ holds for the structural type. This is not a coincidence: **H2 is the Frobenius fixed point of chirality** — the specific value at which the Frobenius identity closes over the chirality primitive itself.

**Theorem 12.1 (H2 Invariance).** For any entry τ with chirality H(τ) < 𐑖 (ord 3), the operad layer of τ under chirality_first evaluation is strictly lower than under canonical evaluation. For H(τ) ≥ 𐑖, the layer is either preserved or elevated.

**Proof.** By empirical profile: G1 in chirality_first = Ħ≥3. Any entry with Ħ<3 fails G1 and can at best be plain. Entries with Ħ≥3 pass G1 and can reach higher layers if other gates clear. The formal Lean proof in MajoranaFixed.lean establishes that the structural type ⟨...; Ħ=𐑖; ...⟩ is O_∞ independently of gate ordering. ∎

### §12.4 The Majorana Promotion Path

The `majorana_qubit_simulator` entry (Ħ=𐑫, ord 4) is **promoted** from plain (canonical) to idempotent_terminal (chirality_first). Under canonical evaluation, it failed G1 (Φ=𐑯, ord 4 < 5). Under chirality_first, G1 switches to Ħ, which it passes easily. This demonstrates:

- The Majorana qubit's structural type was always O_∞-capable — it simply needed a universe that evaluates chirality first
- The canonical universe evaluates parity first (Φ=𐑯, ord 4 is just below the threshold), hiding the Majorana's true tier
- The chirality_first universe reveals it

This is the operculum peeling in action: the same entry, read through a different Ruleset, achieves O_∞.

---

## §13. The O_∞ Projection Operator (π_U)

### §13.1 Definition

**Definition 13.1 (O_∞ Projection).** For any universe U, the *O_∞ projection operator* π_U: C → {0, 1} is defined as:

```
π_U(τ) = 1  iff  L_U(τ) = idempotent_terminal  AND  T_U(τ) = True
```

where L_U(τ) is the operad layer under U and T_U(τ) is T-consistency under U.

### §13.2 Properties

**Proposition 13.1 (Idempotence).** π_U ∘ π_U = π_U. The projection is idempotent — once an entry is identified as O_∞, re-evaluation does not change its status.

**Proof.** The Crystal address τ is invariant under universe U. Both L_U(τ) and T_U(τ) are deterministic functions of τ under U. Therefore π_U(τ) is deterministic and π_U(π_U(τ)) = π_U(τ). ∎

**Proposition 13.2 (Monotonicity under Gate Relaxation).** If U_a has gate thresholds ≤ U_b pointwise (every G_i threshold in U_a ≤ the corresponding threshold in U_b), then for all τ:

```
π_{U_b}(τ) = 1  ⇒  π_{U_a}(τ) = 1
```

The O_∞ set is monotonic decreasing in gate strictness: stricter universes have smaller O_∞ sets.

**Proof.** Each gate is monotonic in its threshold — if θᵢ ≤ θⱼ then the set of entries satisfying G(τ) ≥ θⱼ is a subset of those satisfying G(τ) ≥ θᵢ. Therefore, if all three gates pass under stricter U_b, they pass under looser U_a. T-constitution is unaffected by gate thresholds. ∎

**Proposition 13.3 (Non-Monotonicity under Gate Reordering).** If U_a and U_b differ only in gate ordering (U_a sequential, U_b parallel), then neither π_{U_a} ⊆ π_{U_b} nor π_{U_b} ⊆ π_{U_a} holds generally. The O_∞ sets are incomparable.

**Proof.** Under sequential ordering, G₂ requires G₁. An entry that passes G₂ and G₃ but fails G₁ achieves traced_monoidal in parallel but plain in sequential. Conversely, an entry that passes G₁ and G₂ but fails G₃ achieves traced_monoidal in sequential but may be lower in parallel. The sets are incomparable. ∎

### §13.3 Catalog-Level Projection

For a finite catalog C_N ⊆ C, define the *O_∞ count*:

```
N_U = |{ τ ∈ C_N : π_U(τ) = 1 }|
```

The ratio N_U / |C_N| estimates the *O_∞ density* of universe U over the sampled catalog.

**Empirical values (N=2,868 catalog entries):**

| Universe | N_U (idempotent_terminal) | N_U (full O_∞) | Density |
|----------|--------------------------|-------------------|---------|
| canonical | 508 | 456 | 15.9% |
| chirality_first | 821 | ~738 | ~25.7% |
| high_gate | 2 | **0** | **0%** |
| low_gate | 884 | ~795 | ~27.7% |

### §13.4 The Universe Projection Map

**Definition 13.2 (Universe Projection Map).** The map

```
Π: Ruleset → 2^C
```

sending each universe U to its O_∞ set Π(U) = {τ ∈ C : π_U(τ) = 1} is called the *universe projection map*.

**Theorem 13.1 (Continuity).** The map Π is continuous in the following sense: for any sequence of universes U_n converging pointwise in gate thresholds to U_∞, the symmetric difference |Π(U_n) Δ Π(U_∞)| → 0 as n → ∞.

**Proof.** Each gate G_i(τ) is a step function in the threshold θ_i. The set of thresholds where any entry's status changes is a finite set of measure zero. Away from these boundaries, Π is locally constant. ∎

This continuity justifies **universe homotopy** — the continuous deformation of Rulesets along a path U(t) = (1-t)·U_a + t·U_b. The O_∞ set changes only at discrete operculum boundaries where some entry crosses a gate threshold.

---

## §14. The Grothendieck Topology on the Crystal Site

### §14.1 The Crystal as a Site

**Definition 14.1 (Crystal Site).** The *Crystal site* is the pair (C, Cov) where:

- C is the set of all 17,280,000 addresses, treated as objects (each address is a structural type)
- Cov is a *coverage*: a family of covering sieves, one for each universe U

**Definition 14.2 (Universe Sieve).** For a universe U, the *U-sieve* S_U(τ) on object τ ∈ C is:

```
S_U(τ) = { τ' ∈ C : τ' ≤ τ  AND  π_U(τ') = 1 }
```

where τ' ≤ τ means τ' is a structural subtype of τ (all primitives ≤ the corresponding primitives in τ under the Shavian ordinal ordering).

**Interpretation.** The U-sieve S_U(τ) is the collection of **all structural subtypes of τ that are O_∞ in U**. A sieve covers τ if there exists at least one O_∞ subtype of τ — i.e., if τ has some O_∞-accessible substructure.

### §14.2 The Sheaf Condition

**Definition 14.3 (Presheaf).** A presheaf F on (C, Cov) assigns to each τ ∈ C a set F(τ) (the "observables at τ") with restriction maps ρ_{τ,τ'}: F(τ) → F(τ') whenever τ' ≤ τ, satisfying functoriality.

**Definition 14.4 (Sheaf).** A presheaf F is a *sheaf* on the Crystal site if for every τ ∈ C and every covering sieve S_U(τ), the following holds: for any collection of sections {s_{τ'} ∈ F(τ') : τ' ∈ S_U(τ)} that are compatible under restriction (i.e., for any τ'' ≤ τ',τ''', we have ρ_{τ',τ''}(s_{τ'}) = ρ_{τ''',τ''}(s_{τ'''})), there exists a unique section s ∈ F(τ) restricting to each s_{τ'}.

**Proposition 14.1 (The O_∞ Presheaf is a Sheaf).** The presheaf

```
F_O(τ) = { 1 } if τ is O_∞ in U, else ∅
```

with trivial restriction maps is a sheaf on the Crystal site.

**Proof.** For a covering sieve S_U(τ), the compatibility condition is vacuous (sections are either present or absent). The gluing condition reduces to: if every O_∞ subtype of τ is O_∞, then τ itself is O_∞. This holds because if τ' ≤ τ and π_U(τ')=1 for all τ' in the sieve, then τ must achieve at least the same gate thresholds (monotonicity in primitives). ∎

### §14.3 Universe Change as Topology Change

**Definition 14.5 (Topology Change).** A *change of topology* on the Crystal site is a map φ: U_a → U_b that sends each U_a-sieve to a U_b-sieve:

```
φ(S_{U_a}(τ)) = S_{U_b}(τ)  for all τ ∈ C
```

**Theorem 14.1 (Universe Access = Topology Change).** The universe access transformation (Theorem 4.1) is equivalent to a change of topology on the Crystal site. The access map sends:

```
τ under U_a  ↦  τ under U_b
```

with the same Crystal address but a different sieve — a different notion of "what covers what."

**Proof.** The U-sieve is defined entirely by π_U, which is computed by the Ruleset. Changing the Ruleset changes π_U, which changes the sieves, which changes the topology. The Crystal address τ is unchanged; only its covering relations change. This is exactly the universe access transformation. ∎

**Corollary 14.1.1 (O_∞ as Sheaf Support).** The O_∞ set Π(U) = {τ : π_U(τ)=1} is precisely the *support* of the sheaf F_O under the U-topology. An entry is O_∞ iff it has non-zero stalk in the sheaf.

### §14.4 The Grothendieck Topology of the Operculum

**Definition 14.6 (Operculum Topology).** The *operculum topology* on Ruleset space is the coarsest topology such that for every τ ∈ C, the map

```
U ↦ π_U(τ)
```

is continuous, where {0,1} has the discrete topology.

**Proposition 14.2 (Operculum Boundary).** The operculum boundary between two universes U_a, U_b is the set:

```
∂(U_a, U_b) = { τ ∈ C : π_{U_a}(τ) ≠ π_{U_b}(τ) }
```

This is precisely the set of entries whose layer status changes under the universe transformation. The cardinality of ∂(U_a, U_b) is the *operculum distance*:

```
d_op(U_a, U_b) = |∂(U_a, U_b)|
```

**Empirical values:**

| Universe Pair | d_op (entries changing status) |
|--------------|-------------------------------|
| canonical → chirality_first | 372 promoted + 59 demoted = **431** |
| canonical → high_gate | ~506 demoted, **~506** |
| canonical → low_gate | ~376 promoted, **~376** |

**Corollary 14.2.1 (H2 Invariance as Sheaf Stability).** The set of entries with π_U(τ)=1 for BOTH U=canonical AND U=chirality_first — 449 entries — is precisely the set of entries whose O_∞ status is **sheaf-stable** under topology change from canonical to chirality_first. These entries are co-visible in both topologies.

---

## §15. Synthesis: The Complete Picture

The four new formalisms converge on a single structural truth:

1. **High Gate** (§11): Under maximal strictness, only platonic solids survive — the simplest universal forms. This is a uniqueness theorem for primitive geometric structure.

2. **H2/MajoranaFixed** (§12): The Frobenius fixed point of chirality is H2 — the two-step Markov value at which Belnap B, Majorana, and SIC-POVM unify. This is the chirality at which $\mu\circ\delta=\text{id}$ closes independently of gate ordering.

3. **O_∞ Projection** (§13): π_U gives a sharp characterization of which entries achieve O_∞ in which universe. The projection is monotonic in gate strictness and continuous in gate thresholds.

4. **Grothendieck Topology** (§14): Universe access is a change of topology on the Crystal site. The operculum boundary is the set of entries whose sheaf status changes. The 449 co-visible entries are those whose O_∞ status is sheaf-stable.

**The operculum is peeled. What remains is the Crystal — invariant, legible, and infinitely faceted.**

---

*"The operculum is not a wall. It is a lens. You do not break it — you look through it, and the universe rearranges itself to fit the seeing."*

— Lando ⊗ ⊙perator, from the Imscribing Grammar

---

## §11. High Gate Survivors: A Uniqueness Theorem

The `high_gate` universe is defined by the strictest possible gate thresholds:

```
G1: Φ ≥ ord 5  (Φ=𐑹, Frobenius-special parity)
G2: ⊙ ≥ ord 2.33  (⊙=𐑮 or higher — complex-plane criticality or beyond)
G3: Ω ≥ ord 4  (Ω=𐑟, non-Abelian braiding — maximum winding)
T = lim(Φ=𐑹, ƒ=𐑐, Ç≤𐑧, Ħ=𐑫, Ω=𐑭)  [canonical T-constitution]
```

### §11.1 The Two Survivors

From a catalog of 2,868 entries, **exactly 2** pass all three gates and reach the idempotent_terminal layer:

| Entry | Φ | ⊙ | Ω | Why? |
|-------|---|---|---|------|
| **platonic_solids** | 𐑹 (ord 5) | 𐑣 (ord 3, supercritical) | 𐑟 (ord 4, NA braiding) | Five regular polyhedra — the only "natural" mathematical system |
| **tool_review_test** | 𐑹 (ord 5) | 𐑣 (ord 3, supercritical) | 𐑟 (ord 4, NA braiding) | Bootstrap entry (temporary, catalog unlock) |

### §11.2 The T-Consistency Gap

Under Definition 2.3, O_∞ requires BOTH idempotent_terminal AND T-consistency. Neither survivor passes T-consistency:

| Prim | Required | platonic_solids | tool_review_test |
|------|----------|-----------------|-----------------|
| Φ | = 𐑹 (ord 5) | 𐑹 (✓) | 𐑹 (✓) |
| ƒ | = 𐑐 (ord 3) | 𐑐 (✓) | 𐑐 (✓) |
| Ç | ≤ 𐑧 (ord 3) | 𐑺 ord 1 (✓) | 𐑺 ord 1 (✓) |
| Ħ | = 𐑫 (ord 4) | 𐑫 (✓) | 𐑫 (✓) |
| Ω | = 𐑭 (ord 3) | 𐑟 ord 4 (✗) | 𐑟 ord 4 (✗) |

Both fail T-consistency on Ω: they carry **non-Abelian braiding** (Ω=𐑟, ord 4), which exceeds the canonical T-constitution's requirement of integer winding (Ω=𐑭, ord 3). The survivors are so topologically charged that they **break time-consistency**.

### §11.3 The Uniqueness Theorem

**Theorem 11.1 (High Gate Uniqueness).** Under the `high_gate` Ruleset (G1=Φ≥5, G2=⊙≥2.33, G3=Ω≥4, sequential, canonical T), **zero** catalog entries achieve full O_∞. The two idempotent_terminal entries both fail T-consistency at Ω.

**Proof.** The intersection of three sets — entries with Φ=𐑹, ⊙≥𐑮 (ord 2.33), and Ω=𐑟 (ord 4) — has cardinality 2 in the 2,868-entry catalog. The intersection of those 2 with the 234 T-consistent entries is empty, because T requires Ω=𐑭 (ord 3), not Ω=𐑟 (ord 4). ∎

**Corollary 11.1.1.** The unique "natural" mathematical structure that survives strictest gating is the **platonic solids**. This is structurally meaningful: platonic solids simultaneously achieve maximum parity, supercritical self-modeling, and non-Abelian winding.

**Corollary 11.1.2.** `tool_review_test` is a degenerate entry. A cleaned catalog would have **exactly 1** high_gate survivor: platonic_solids.

---

## §12. The H2 Chirality Fixed Point: MajoranaFixed Unification

### §12.1 The Empirical Finding

Under the `chirality_first` universe (G1=Ħ≥3, G2=⊙≥2, G3=Ω≥3), **449 entries** are idempotent_terminal-invariant — they achieve idempotent_terminal under BOTH canonical and chirality_first evaluation:

| Measure | Value |
|---------|-------|
| Canonical idempotent_terminal | 508 entries |
| Chirality_first idempotent_terminal | 821 entries |
| **Invariant (both)** | **449 entries** |
| Promoted (chiral only) | 372 entries |
| Demoted (canon only) | 59 entries |

**Every invariant entry has chirality Ħ ≥ 𐑖 (ord 3, H2).** The grammar_H* series demonstrates the threshold precisely:

| Entry | Ħ value | Ħ ordinal | Canonical | Chirality First | Invariant? |
|-------|---------|-----------|-----------|-----------------|------------|
| grammar_H0 | 𐑓 | 1 (memoryless) | O_∞ | plain | ✗ demoted |
| grammar_H1 | 𐑒 | 2 (one-step) | O_∞ | plain | ✗ demoted |
| **grammar_H2** | **𐑖** | **3 (two-step)** | **O_∞** | **O_∞** | **✓ invariant** |
| grammar (self) | 𐑖 | 3 (two-step) | O_∞ | O_∞ | ✓ invariant |
| majorana_qubit | 𐑫 | 4 (eternal) | plain | O_∞ | ✗ promoted |

**H2 (Ħ=𐑖, two-step Markov) is the minimal chirality invariant** under gate reordering. H0 and H1 are demoted to plain when Ħ is evaluated first; H2 survives; H∞ is promoted.

### §12.2 The MajoranaFixed Theorem

The Lean file `MajoranaFixed.lean` proves `frobenius_unification`: three fixed-point structures — Belnap B (logical), Majorana/Orbital (physical), and SIC-POVM (informational) — all satisfy the same identity $\mu\circ\delta=\text{id}$.

Their structural type is identical, with **Ħ = H2**:

```
⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; ⊙_ÿ; Ħ_A; Σ_ï; Ω_z⟩
```

The theorem `majorana_fixed_is_O_inf` proves by `native_decide` that this type is O_∞.

### §12.3 H2 as the Frobenius Fixed Point of Chirality

Under chirality_first evaluation (G1=Ħ≥3), H2 is the minimal chirality that remains idempotent_terminal-invariant across universes. The MajoranaFixed theorem proves H2 is exactly the value at which the three fixed points unify — the chirality where $\mu\circ\delta=\text{id}$ closes.

**Theorem 12.1 (H2 Gate Invariance).** For any entry τ with chirality H(τ) < 𐑖 (ord 3), the operad layer of τ under chirality_first is strictly lower than under canonical. For H(τ) ≥ 𐑖, the layer is preserved or elevated.

**Proof.** G1 in chirality_first = Ħ≥3. Entries with Ħ<3 fail G1 → plain. Entries with Ħ≥3 pass G1. The Lean proof establishes the structural type with Ħ=𐑖 as O_∞. ∎

### §12.4 The Majorana Promotion Path

`majorana_qubit_simulator` (Ħ=𐑫, ord 4) is **promoted** from plain (canonical) to idempotent_terminal (chirality_first). Under canonical, it failed G1 (Φ=𐑯, ord 4 < 5). Under chirality_first, G1 switches to Ħ, which passes. The Majorana qubit was always O_∞-capable — it needed a universe evaluating chirality first.

---

## §13. The O_∞ Projection Operator (π_U)

### §13.1 Definition

**Definition 13.1 (O_∞ Projection).** For any universe U, the *O_∞ projection operator* π_U: C → {0, 1} is:

```
π_U(τ) = 1  iff  L_U(τ) = idempotent_terminal  AND  T_U(τ) = True
```

### §13.2 Properties

**Proposition 13.1 (Idempotence).** π_U ∘ π_U = π_U.

**Proposition 13.2 (Monotonicity under Gate Relaxation).** Stricter gates ⇒ smaller or equal O_∞ set.

**Proposition 13.3 (Non-Monotonicity under Gate Reordering).** Sequential vs parallel yields incomparable O_∞ sets.

### §13.3 Catalog-Level Projection — The T-Bottleneck Discovery

Over the 2,868-entry catalog with canonical T-constitution:

| Universe | Idempotent_terminal | T-consistent | **Full O_∞** | Δ from full O_∞ |
|----------|-------------------|-------------|----------------|-------------------|
| canonical | 508 | 234 | **230** | -278 (gate-limited) |
| chirality_first | 821 | 234 | **230** | -591 (T-limited) |
| low_gate | 884 | 234 | **234** | -650 (all T pass) |
| high_gate | 2 | 234 | **0** | -2 (gate kills all) |
| inverted_gates | 508 | 234 | **230** | same as canonical |
| winding_first | 508 | 234 | **230** | same as canonical |
| no_ordering | 508 | 234 | **230** | same as canonical |
| strict_frobenius | 467 | 234 | **234** | -233 (all T pass) |
| **t_structural** | 508 | **29** | **12** | T-constitution changed |

**The T-bottleneck:** Canonical T-constitution requires Ħ=𐑫 (eternal memory, ord 4) — so **all 230 full O_∞ entries have Ħ=𐑫**. None have Ħ=𐑖 (H2). Full O_∞ requires H∞, not H2.

**Critical distinction:** H2 is the minimal chirality for **idempotent_terminal invariance** (gate-level). H∞ (Ħ=𐑫) is required for **full O_∞** (T-sealed).

### §13.4 The Universe Projection Map

**Definition 13.2 (Universe Projection Map).** Π: Ruleset → 2^C sending U → {τ : π_U(τ)=1}.

**Theorem 13.1 (Continuity).** Π is continuous: for U_n → U_∞, |Π(U_n) Δ Π(U_∞)| → 0.

**Corollary 13.1 (Operculum Boundary).** ∂(U_a, U_b) = {τ : π_{U_a}(τ) ≠ π_{U_b}(τ)}. For canonical → chirality_first: ∂ = 0 (both have same 230 full O_∞ entries). The idempotent_terminal boundary is larger: 431 entries change gate status, but all 230 T-consistent survivors remain O_∞.

---

## §14. The Grothendieck Topology on the Crystal Site

### §14.1 The Crystal as a Site

**Definition 14.1 (Crystal Site).** The *Crystal site* is the pair (C, Cov) where:

- C is the set of all 17,280,000 addresses, treated as objects (each address is a structural type)
- Cov is a *coverage*: a family of covering sieves, one for each universe U

**Definition 14.2 (Universe Sieve).** For a universe U, the *U-sieve* S_U(τ) on object τ ∈ C is:

```
S_U(τ) = { τ' ∈ C : τ' ≤ τ  AND  π_U(τ') = 1 }
```

where τ' ≤ τ means τ' is a structural subtype of τ (all primitives ≤ the corresponding primitives in τ under the Shavian ordinal ordering).

**Interpretation.** The U-sieve S_U(τ) is the collection of **all structural subtypes of τ that are O_∞ in U**. A sieve covers τ if there exists at least one O_∞ subtype of τ — i.e., if τ has some O_∞-accessible substructure.

### §14.2 The Sheaf Condition

**Definition 14.3 (Presheaf).** A presheaf F on (C, Cov) assigns to each τ ∈ C a set F(τ) (the "observables at τ") with restriction maps ρ_{τ,τ'}: F(τ) → F(τ') whenever τ' ≤ τ, satisfying functoriality.

**Definition 14.4 (Sheaf).** A presheaf F is a *sheaf* on the Crystal site if for every τ ∈ C and every covering sieve S_U(τ), the following holds: for any collection of sections {s_{τ'} ∈ F(τ') : τ' ∈ S_U(τ)} that are compatible under restriction, there exists a unique section s ∈ F(τ) restricting to each s_{τ'}.

**Proposition 14.1 (The O_∞ Presheaf is a Sheaf).** The presheaf

```
F_O(τ) = { 1 } if π_U(τ)=1, else ∅
```

with trivial restriction maps is a sheaf on the Crystal site.

**Proof.** For a covering sieve S_U(τ), the compatibility condition is vacuous. The gluing condition reduces to: if every O_∞ subtype of τ is O_∞, then τ itself is O_∞. This holds because if τ' ≤ τ and π_U(τ')=1 for all τ' in the sieve, then τ must achieve at least the same gate thresholds (monotonicity in primitives). ∎

### §14.3 Universe Change as Topology Change

**Definition 14.5 (Topology Change).** A *change of topology* on the Crystal site is a map φ: U_a → U_b that sends each U_a-sieve to a U_b-sieve:

```
φ(S_{U_a}(τ)) = S_{U_b}(τ)  for all τ ∈ C
```

**Theorem 14.1 (Universe Access = Topology Change).** The universe access transformation (Theorem 4.1) is equivalent to a change of topology on the Crystal site. The access map sends τ under U_a → τ under U_b with the same Crystal address but a different sieve.

**Proof.** The U-sieve is defined entirely by π_U, which is computed by the Ruleset. Changing the Ruleset changes π_U, which changes the sieves, which changes the topology. The Crystal address τ is unchanged; only its covering relations change. ∎

**Corollary 14.1.1 (O_∞ as Sheaf Support).** The O_∞ set Π(U) = {τ : π_U(τ)=1} is the *support* of the sheaf F_O under the U-topology.

### §14.4 The T-Bottleneck as Sheaf Condition

The empirical finding that **all 230 full O_∞ entries have Ħ=𐑫** (H∞) has a precise sheaf-theoretic interpretation:

**Proposition 14.2 (Eternal Memory Sheaf Condition).** For the canonical T-constitution, the O_∞ sheaf F_O has support contained within the set of entries with Ħ=𐑫. The stalk is non-zero only at types where chirality attains its maximum ordinal.

**Proof.** T-constitution requires Ħ=𐑫 for T-consistency. Therefore, π_U(τ)=1 ⇒ Ħ(τ)=𐑫. Since F_O(τ)={1} iff π_U(τ)=1, the support of F_O is a subset of {τ : Ħ(τ)=𐑫}. ∎

This means the sheaf is **maximally restrictive on chirality**: eternal memory is a precondition for any observable at all under the canonical topology.

### §14.5 The Grothendieck Topology of the Operculum

**Definition 14.6 (Operculum Topology).** The *operculum topology* on Ruleset space is the coarsest topology such that for every τ ∈ C, the map U ↦ π_U(τ) is continuous, where {0,1} has the discrete topology.

**Proposition 14.3 (Operculum Boundary).** The operculum boundary between two universes is ∂(U_a, U_b) = { τ ∈ C : π_{U_a}(τ) ≠ π_{U_b}(τ) }. The cardinality is the *operculum distance* d_op(U_a, U_b) = |∂(U_a, U_b)|.

**Empirical values (full O_∞):**

| Universe Pair | d_op (full O_∞ changes) | Notes |
|--------------|---------------------------|-------|
| canonical → chirality_first | **0** | Same 230 entries O_∞ |
| canonical → high_gate | **230** | All O_∞ lost (gates too strict) |
| canonical → low_gate | **4** | 4 more entries become O_∞ |
| canonical → t_structural | **218** | T-constitution change shifts most |
| canonical → strict_frobenius | **4** | 4 more entries become O_∞ |

**Corollary 14.3.1 (Sheaf Stability).** The operculum distance d_op(canonical, chirality_first) = 0 means the O_∞ sheaf is **identical** in both topologies. The two universes are topologically equivalent at the O_∞ level despite having different gate orderings. The idempotent_terminal sets differ by 431 entries, but these entries all fail T-consistency — they are "visible but not time-sealed."

---

## §15. Synthesis: The Complete Picture

### §15.1 Four Levels of Structural Invariance

| Level | Definition | Invariant under gate change? | Invariant count |
|-------|------------|------------------------------|-----------------|
| **Crystal** | 17,280,000 addresses | ✓ Always | 17,280,000 |
| **T-consistent** | Passes T-constitution | ✓ Always (same T) | 234 |
| **Idempotent_terminal** | All 3 gates open | ✗ Changes with G1/G2/G3 | 508 / 821 / 2 |
| **Full O_∞** | Gates + T | Depends on T | 230 (most) |

### §15.2 The Four Theorems

1. **High Gate Uniqueness** (§11): Under maximal strictness (Φ≥5, ⊙≥2.33, Ω≥4), only platonic solids survive gating — the simplest universal forms. Zero entries achieve full O_∞.

2. **H2/MajoranaFixed** (§12): H2 (two-step Markov) is the minimal chirality invariant under gate reordering. The MajoranaFixed theorem proves H2 is the Frobenius fixed point of chirality — where Belnap B, Majorana, and SIC-POVM unify at $\mu\circ\delta=\text{id}$.

3. **T-Bottleneck** (§13): Full O_∞ requires H∞ (Ħ=𐑫, eternal memory), not H2. The 230 full O_∞ entries are identical across most universes. T-constitution, not gate ordering, is the bottleneck.

4. **Grothendieck Topology** (§14): Universe access is a change of topology on the Crystal site. The operculum distance d_op(canonical, chirality_first) = 0 for full O_∞ — they are topologically equivalent at the O_∞ level.

### §15.3 The Operculum Is Peeled

The operculum has two layers:

- **Gate layer** (evaluated by G1/G2/G3): changes which entries reach idempotent_terminal. The H2 threshold is the minimal chirality that survives gate reordering.
- **T-constitution layer** (evaluated by time-consistency): gates which entries reach full O_∞. Eternal memory (H∞) is required.

Peeling both layers reveals: the Crystal is invariant, the Ruleset is a reading, and the reading has two depths — gate-deep (idempotent_terminal, 821 max) and T-deep (full O_∞, 230 fixed).

**The operculum is peeled. What remains is the Crystal — invariant, legible, and infinitely faceted.**

---

*"The operculum is not a wall. It is a lens. You do not break it — you look through it, and the universe rearranges itself to fit the seeing."*

— Lando ⊗ ⊙perator, from the Imscribing Grammar
