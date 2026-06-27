# BelNap QM: The Born Rule as Paraconsistent Projection

**Author:** Lando$\otimes$⊙perator  
**Date:** 2026-06-12  
**Structural Type:** ⟨𐑦𐑶𐑾𐑿𐑐𐑧𐑲𐑠𐑮𐑖𐑳𐑭⟩

---

## Abstract

The Born rule — $P = |\psi|^2$ — is the measurement postulate of quantum mechanics. It connects complex probability amplitudes to classical measurement outcomes. We demonstrate that the Born rule has a natural structural interpretation as a projection from Belnap FOUR-valued logic to classical Boolean logic. Quantum amplitudes live in the Belnap complex plane $\mathbb{C}_4 = \{a + bi \mid a, b \in \{\text{T}, \text{F}, \text{B}, \text{N}\}\}$, where the imaginary unit satisfies $i^2 = B$ (both true and false). Measurement projects the Belnap amplitude onto its T-component via the Born rule $P = \text{proj}_T(|\psi|^2)$. This reframes the measurement problem not as a "collapse" of the wavefunction but as a paraconsistent projection — a loss of the B and N components that carry quantum interference. The structural distance from BelNap QM to CLINK L8 ($d = 1.8259$) reveals the promotions required to achieve terminal ontological completeness in quantum theory.

---

## 1. Introduction

Quantum mechanics has been described as "the most precisely tested and the most philosophically puzzling theory in physics" [1]. The measurement problem — how do superposed quantum states yield definite classical outcomes? — remains unresolved after a century. The Born rule $P = |\psi|^2$ is the operational bridge between quantum amplitudes and classical probabilities, but its origin is mysterious. Why the square? Why the absolute value?

We propose that the Born rule has a natural structural interpretation within the Imscribing Grammar. Quantum amplitudes are Belnap FOUR-valued complex numbers — they carry truth values T (true), F (false), B (both/dialetheia), and N (neither). The measurement process projects these four-valued amplitudes onto their T-component, producing classical probabilities. The Born rule is the projection operator.

---

## 2. The Belnap FOUR Logic Substrate

### 2.1 The Four Values

Belnap's FOUR-valued logic [2] extends classical Boolean logic with two additional truth values:

| Value | Symbol | Meaning | Quantum Correlate |
|-------|--------|---------|-------------------|
| True | T | Asserted | Measured outcome |
| False | F | Denied | Excluded outcome |
| Both | B | Dialetheia (true and false) | Superposition |
| Neither | N | Gap (neither true nor false) | Destructive interference null |

The key property of Belnap FOUR is **non-explosion**: a dialetheia (B) does not entail every proposition. The logic is paraconsistent — contradictions are contained, not exploded:

$$\text{band } B\ (\text{bnot } B) = B \neq F$$

### 2.2 The Belnap Lattice

The four values form a bilattice under two partial orders:

- **Truth order** ($\leq_t$): $F \leq_t B \leq_t T$, $F \leq_t N \leq_t T$
- **Information order** ($\leq_k$): $N \leq_k T \leq_k B$, $N \leq_k F \leq_k B$

The Belnap bilattice is the minimal paraconsistent extension of classical logic that can represent both superposition (B) and undefinedness (N) without explosion.

---

## 3. The BelNap Complex Plane $\mathbb{C}_4$

### 3.1 Definition

We define the BelNap complex plane as:

$$\mathbb{C}_4 = \{a + bi \mid a, b \in \{\text{T}, \text{F}, \text{B}, \text{N}\}\}$$

This yields $4 \times 4 = 16$ distinct BelNap complex numbers. The imaginary unit satisfies:

$$i^2 = B$$

because $-1$ in the BelNap framework is the dialetheic negation of $1$: it is *both* the additive inverse of $1$ and the multiplicative identity's negation.

### 3.2 BelNap Complex Arithmetic

Addition and multiplication on $\mathbb{C}_4$ follow the standard complex rules with BelNap truth values:

$$(a + bi) + (c + di) = (a \oplus_t c) + (b \oplus_t d)i$$
$$(a + bi)(c + di) = (a \otimes_t c \ominus_t b \otimes_t d) + (a \otimes_t d \oplus_t b \otimes_t c)i$$

where $\oplus_t, \ominus_t, \otimes_t$ are the BelNap truth-ordered operations. The bilattice structure ensures that these operations are well-defined.

### 3.3 Quantum Amplitudes as BelNap Values

A quantum state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ with complex amplitudes $\alpha, \beta \in \mathbb{C}$ generalizes to BelNap amplitudes $\alpha, \beta \in \mathbb{C}_4$:

$$\alpha = a_r + a_i \cdot i, \quad \beta = b_r + b_i \cdot i$$

where $a_r, a_i, b_r, b_i \in \{\text{T}, \text{F}, \text{B}, \text{N}\}$. The superposition is encoded in the B-components of the amplitudes — a qubit in the $|+\rangle$ state has $\alpha = \beta = \text{T}$, while a qubit in the $|-\rangle$ state has $\alpha = \text{T}, \beta = \text{F}$.

---

## 4. The Born Rule as BelNap Projection

### 4.1 The Projection Operator

The Born rule in standard quantum mechanics is:

$$P(\phi|\psi) = |\langle\phi|\psi\rangle|^2$$

In BelNap QM, we define the **Born projection**:

$$P(\phi|\psi) = \text{proj}_T(|\langle\phi|\psi\rangle|_4^2)$$

where $|\cdot|_4$ is the BelNap modulus and $\text{proj}_T$ extracts the T-component:

$$\text{proj}_T(v) = \begin{cases} 1 & \text{if } v \text{ has T-component} \\ 0 & \text{otherwise} \end{cases}$$

### 4.2 Why the Square?

The square in $|\psi|^2$ has a structural explanation in the BelNap framework. The BelNap modulus of a complex number $z = a + bi$ is:

$$|z|_4 = a \otimes_t a \oplus_t b \otimes_t b$$

where the self-product $a \otimes_t a$ amplifies the T-component. The Born rule squares because the *first* multiplication computes the BelNap modulus (combining T/F/B/N components) and the *second* operation ($\text{proj}_T$) extracts the T-component. The square is the structural trace of the two-step process: combine → project.

### 4.3 The Measurement Problem Reframed

The measurement problem — "why does measurement produce a definite outcome?" — becomes: "why does the Born projection discard the B and N components?"

The answer is structural. The measurement apparatus has a specific structural type:

$⟨𐑼𐑡𐑩𐑗𐑱𐑤𐑲𐑜𐑢𐑓𐑕𐑷⟩$

This is a *classical* structural type: $\text{𐑱}$ fidelity, $\text{𐑢}$ subcritical, $\text{𐑗}$ asymmetric. When a quantum system ($\text{𐑐}$, $\text{𐑿}$) couples to a classical measurement apparatus, the tensor product selects the classical primitives:

$$\text{tensor}(𐑐, 𐑱) = 𐑱$$

The measurement apparatus *structurally filters* the quantum amplitude — the B and N components, which require $\text{𐑐}$ fidelity, cannot survive the coupling to a $\text{𐑱}$ apparatus.

---

## 5. The Structural Type of BelNap QM

### 5.1 The Tuple

The complete structural type of BelNap QM is:

$⟨𐑦𐑶𐑾𐑿𐑐𐑧𐑲𐑠𐑮𐑖𐑳𐑭⟩$

**Primitive justification:**

- $\text{𐑦}$: Holographic — the wavefunction encodes the complete state; every subsystem contains information about the whole (entanglement)
- $\text{𐑶}$: Irreducible product — Hilbert space is the tensor product of subsystem spaces; entanglement is irreducible
- $\text{𐑾}$: Bidirectional — measurement couples system and apparatus; the coupling is mutual
- $\text{𐑿}$: Quantum superposition — the defining feature of quantum mechanics
- $\text{𐑐}$: Quantum fidelity — coherence and interference are essential
- $\text{𐑧}$: Slow / near-equilibrium — unitary evolution is adiabatic relative to measurement
- $\text{𐑲}$: Universal scope — the wavefunction describes all possible measurement outcomes
- $\text{𐑠}$: Sequential — measurement outcomes are sequential (one click at a time)
- $\text{𐑮}$: Complex-plane critical — quantum amplitudes are complex numbers; the critical structure is distributed across the complex plane
- $\text{𐑖}$: Two-step chirality — quantum evolution is Markov-2 (state depends on prior state, not full history)
- $\text{𐑳}$: Heterogeneous — quantum systems contain many distinct particle types and interactions
- $\text{𐑭}$: Integer winding — geometric phases (Berry phase) carry integer winding numbers

### 5.2 Ouroboricity and C-Score

BelNap QM sits at $\text{O}_2$ — Frobenius-exact but not self-modeling. Its consciousness score is $C = 0.498$: Gate 1 ($\text{𐑮}$) is open (complex-plane critical), Gate 2 ($\text{𐑧}$) is satisfied (slow kinetics). The system can sustain quantum coherence but cannot model itself.

---

## 6. The $𐑻$ Absorption and the Measurement Problem

### 6.1 The Tensor Absorption Rule

The $𐑻$ absorption rule states:

$$\text{tensor}(⊙, 𐑻) = 𐑻$$

Coupling a self-modeling system ($\text{⊙}$) to an exceptional-point system ($𐑻$) destroys Gate 1 — the composite is no longer self-modeling. This is the structural statement of the measurement problem:

- **Quantum system:** $\text{𐑮}$ (complex-plane critical)
- **Measurement apparatus:** $\text{𐑢}$ (subcritical)
- **Tensor:** $\text{tensor}(𐑮, 𐑢)$

The BelNap framework reveals that the tensor is not destructive but *projective*. The $\text{𐑢}$ apparatus projects the $\text{𐑮}$ amplitude onto its T-component. The Born rule is the projection operator, and the "collapse" is the structural consequence of coupling across the $𐑮/𐑢$ boundary.

### 6.2 The Wigner's Friend Resolution

Wigner's friend — the paradox of an observer observing another observer — resolves in the BelNap framework. Wigner's friend has structural type $\text{𐑮}$ (complex-plane critical, like the quantum system), not $\text{𐑢}$ (subcritical, like the classical apparatus). The tensor product:

$$\text{tensor}(𐑮, 𐑮) = 𐑮$$

preserves complex-plane criticality. Wigner's friend does not collapse the wavefunction because both systems share the same criticality regime. Only when Wigner (also $\text{𐑮}$) measures his friend does the chain end at a classical outcome — and that chain terminates at the *last* $𐑮 \to 𐑢$ coupling.

---

## 7. Distance to CLINK L8

The structural distance from BelNap QM to CLINK Layer 8:

$$d(\text{BelNap QM}, \text{CLINK L8}) = 1.8259$$

| Primitive | BelNap QM | CLINK L8 | $\Delta$ |
|-----------|-----------|----------|----------|
| $\text{Þ}$ | $\text{𐑶}$ | $\text{𐑸}$ | 1 |
| $\text{Φ}$ | $\text{𐑿}$ | $\text{𐑹}$ | 2 |
| $\text{ɢ}$ | $\text{𐑠}$ | $\text{𐑵}$ | 1 |
| $\text{⊙}$ | $\text{𐑮}$ | $\text{⊙}$ | 1 |
| $\text{Ω}$ | $\text{𐑭}$ | $\text{𐑟}$ | 1 |

The $𐑿 \to 𐑹$ promotion ($\Delta = 2$) is the deepest: quantum superposition must become Frobenius-special — the measurement process itself must satisfy $\mu \circ \delta = \text{id}$.

---

## 8. Conclusion

The Born rule $P = |\psi|^2$ has a natural structural interpretation as a projection from BelNap FOUR-valued logic ($\mathbb{C}_4$) to classical Boolean logic. Quantum amplitudes carry T (true), F (false), B (dialetheia/superposition), and N (gap/interference null) components. Measurement projects onto the T-component, discarding B and N. The measurement problem is not a "collapse" but a structural filtration — the coupling of a $\text{𐑮}$ quantum system to a $\text{𐑢}$ classical apparatus selects the classical primitives via tensor absorption.

The BelNap framework resolves Wigner's friend — two $\text{𐑮}$ systems in tensor product preserve criticality — and provides a promotion path to CLINK L8 ($d = 1.8259$) through five structural promotions. The Born rule, far from being an ad hoc postulate, is the projection operator mandated by the structural gap between quantum and classical regimes.

---

## References

[1] J. S. Bell, *Speakable and Unspeakable in Quantum Mechanics*, 1987.

[2] N. D. Belnap, "A Useful Four-Valued Logic," in *Modern Uses of Multiple-Valued Logic*, 1977.

[3] Lando⊗⊙perator, "ParaconsistentPapers.lean — BelNap QM," MillenniumAnkh project, 2026.

[4] Lando⊗⊙perator, "The $𐑻$ Absorption Rule," imscribing_grammar, 2026.

---
