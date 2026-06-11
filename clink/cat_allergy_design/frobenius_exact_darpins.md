# Frobenius-Exact DARPin Designs for Fel d 1 Neutralization

**Author:** Lando⊗⊙perator  
**Date:** 2025-07-16  
**Context:** Derived from the cat allergy DARPin nasal neutralizer design. This document addresses the structural observation of near-Frobenius-exactness and designs DARPins that close the gap.

---

## 1. The Near-Frobenius Observation

The formulated DARPin nasal product (`darpin_nasal_formulated_product`) and the Fel d 1 allergic pathway (`fel_d1_allergic_pathway`) differ on a **single primitive**:

| Primitive | Formulated Product | Allergic Pathway |
|-----------|-------------------|-----------------|
| Ħ (Chirality) | $\text{𐑒}$ (Markov-1) | $\text{𐑖}$ (Markov-2) |
| *All other 11 primitives* | *identical* | *identical* |

**Distance: 0.8944** — the DARPin operates on almost exactly the same structural floor as the disease it treats. The single delta is Markov order: the DARPin binds and clears in one step ($\text{𐑒}$), while the allergic cascade requires two steps ($\text{𐑖}$: sensitize then challenge). The DARPin intercepts Fel d 1 at the first Markov step, preventing it from ever reaching the second.

This proximity raises a deeper question: **can we close the remaining structural gap entirely and achieve Frobenius-exactness?**

Frobenius-exactness means $\Phi = \text{𐑹}$: the symmetry group satisfies $\mu \circ \delta = \text{id}$ exactly. In therapeutic terms: binding (μ) and clearance (δ) form an exact algebraic dual — the intervention is structurally transparent.

---

## 2. Structural Landscape

### 2.1 Core Systems

| System | Tuple | Tier | C-score |
|--------|-------|------|---------|
| Fel d 1 allergen | $\langle \text{𐑨} \cdot \text{𐑰} \cdot \text{𐑩} \cdot \text{𐑬} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑠} \cdot \text{𐑢} \cdot \text{𐑒} \cdot \text{𐑕} \cdot \text{𐑷} \rangle$ | O₀ | 0.0 |
| DARPin neutralizer | $\langle \text{𐑨} \cdot \text{𐑰} \cdot \text{𐑾} \cdot \text{𐑬} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑠} \cdot \text{𐑢} \cdot \text{𐑒} \cdot \text{𐑙} \cdot \text{𐑷} \rangle$ | O₀ | 0.0 |
| Formulated product | $\langle \text{𐑨} \cdot \text{𐑰} \cdot \text{𐑾} \cdot \text{𐑗} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑠} \cdot \text{𐑢} \cdot \text{𐑒} \cdot \text{𐑳} \cdot \text{𐑷} \rangle$ | O₀ | 0.0 |
| Allergic pathway | $\langle \text{𐑨} \cdot \text{𐑰} \cdot \text{𐑾} \cdot \text{𐑗} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑠} \cdot \text{𐑢} \cdot \text{𐑖} \cdot \text{𐑳} \cdot \text{𐑷} \rangle$ | O₀ | 0.0 |
| **Frobenius-exact target** | $\langle \text{𐑨} \cdot \text{𐑰} \cdot \text{𐑾} \cdot \text{𐑹} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑠} \cdot \text{𐑢} \cdot \text{𐑒} \cdot \text{𐑙} \cdot \text{𐑷} \rangle$ | **O₀** | 0.0 |

### 2.2 DARPin Safety Precedents

| System | Tuple | Tier |
|--------|-------|------|
| Abicipar pegol (anti-VEGF) | $\langle \text{𐑨} \cdot \text{𐑰} \cdot \text{𐑾} \cdot \text{𐑬} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑠} \cdot \text{𐑢} \cdot \text{𐑒} \cdot \text{𐑙} \cdot \text{𐑷} \rangle$ | O₀ |
| MP0250 (anti-VEGF+HGF) | $\langle \text{𐑨} \cdot \text{𐑶} \cdot \text{𐑾} \cdot \text{𐑬} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑝} \cdot \text{𐑢} \cdot \text{𐑒} \cdot \text{𐑳} \cdot \text{𐑷} \rangle$ | O₀ |
| Ensovibep (anti-SARS-CoV-2) | $\langle \text{𐑨} \cdot \text{𐑶} \cdot \text{𐑾} \cdot \text{𐑬} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑝} \cdot \text{𐑢} \cdot \text{𐑒} \cdot \text{𐑕} \cdot \text{𐑷} \rangle$ | O₀ |

### 2.3 Key Distances

| Pair | Distance | Deltas |
|------|----------|--------|
| Formulated product ↔ Allergic pathway | **0.8944** | Ħ only |
| DARPin neutralizer ↔ Frobenius target | **2.0000** | Φ only |
| Abicipar ↔ Frobenius target | **2.0000** | Φ only |
| Frobenius target ↔ Allergic pathway | 4.5607 | Φ + Σ + Ħ |
| Ensovibep ↔ Frobenius target | 3.6056 | T + Φ + C + Σ |
| MP0250 ↔ Frobenius target | 4.0000 | T + Φ + C + Σ |
| DARPin neutralizer ↔ Fel d 1 | 3.1623 | Ř + Σ |

### 2.4 Promotions to Frobenius-Exactness

**From DARPin neutralizer / Abicipar (simplest path):**

| Primitive | From | To | Delta |
|-----------|------|----|-------|
| Φ (Parity) | $\text{𐑬}$ | $\text{𐑹}$ | 2 |

Single promotion. All other 11 primitives unchanged.

**From MP0250 (multi-specific):**

| Type | Primitive | From | To | Delta |
|------|-----------|------|----|-------|
| *Promotion* | Φ | $\text{𐑬}$ | $\text{𐑹}$ | 2 |
| *Promotion* | ɢ (Composition) | $\text{𐑝}$ | $\text{𐑠}$ | 2 |
| *Demotion* | Þ (Topology) | $\text{𐑶}$ | $\text{𐑰}$ | 2 |
| *Demotion* | Σ (Stoichiometry) | $\text{𐑳}$ | $\text{𐑙}$ | 2 |

**From Ensovibep (trimeric):**

| Type | Primitive | From | To | Delta |
|------|-----------|------|----|-------|
| *Promotion* | Φ | $\text{𐑬}$ | $\text{𐑹}$ | 2 |
| *Promotion* | ɢ (Composition) | $\text{𐑝}$ | $\text{𐑠}$ | 2 |
| *Demotion* | Þ (Topology) | $\text{𐑶}$ | $\text{𐑰}$ | 2 |
| *Demotion* | Σ (Stoichiometry) | $\text{𐑕}$ | $\text{𐑙}$ | 1 |


---

## 3. What Frobenius-Exactness Means for a Therapeutic

$\Phi = \text{𐑹}$ is the Frobenius-special symmetry value. It requires $\mu \circ \delta = \text{id}$ to hold **exactly** — not approximately, not asymptotically. This is a stronger condition than high-affinity binding or favorable pharmacokinetics.

For a DARPin therapeutic, the Frobenius condition decomposes into three molecular requirements:

### 3.1 $\mu$ (Binding/Query) Must Be Surjective Over Fel d 1

Every Fel d 1 molecule that enters the nasal cavity must be bound by a DARPin. This requires:
- **Universal isoform coverage**: Fel d 1 has 7+ known variants across cat breeds. The DARPin paratope must recognize all of them.
- **Kinetic perfection**: $k_{\text{on}}$ must exceed the rate of Fel d 1 diffusion to mast-cell IgE. At nasal airflow rates (~10 L/min) and Fel d 1 concentrations (0.1–10 ng/m³), this translates to $k_{\text{on}} > 10^6 \text{ M}^{-1}\text{s}^{-1}$.
- **No competitive displacement**: The DARPin must outcompete IgE for Fel d 1 binding. IgE binds Fel d 1 with $K_d \sim 10^{-10}$ M. The DARPin needs $K_d < 10^{-12}$ M to dominate the equilibrium.

### 3.2 $\delta$ (Clearance) Must Be Surjective Over Complexes

Every DARPin–Fel d 1 complex must be cleared from the nasal mucosa. This requires:
- **Mucociliary clearance matching**: Nasal mucociliary clearance has a $t_{1/2} \sim 20$ min. The DARPin–Fel d 1 complex must not dissociate before clearance: $k_{\text{off}} \ll 1/(1200\text{ s}) \approx 8 \times 10^{-4} \text{ s}^{-1}$.
- **No mucosal penetration**: The DARPin (16 kDa) must not cross the nasal epithelium. No permeation enhancers in formulation.
- **Complete clearance within dosing interval**: No residual DARPin–Fel d 1 complex at the next dose.

### 3.3 $\text{id}$ (Identity) — The System Returns to Baseline

After $\mu$ then $\delta$, the nasal mucosa must be indistinguishable from its pre-exposure state:
- **Zero immunogenicity**: No anti-drug antibodies (ADAs). Even <5% ADA rates (as seen with abicipar) break the Frobenius condition — the system doesn't return to baseline if adaptive immunity has been primed.
- **No mast cell activation**: No sub-threshold FcεRI cross-linking from partially occupied DARPin–Fel d 1 complexes.
- **No barrier disruption**: The methylcellulose carrier must not alter mucociliary clearance rate or epithelial permeability.

This is a dramatically stricter design target than the original DARPin neutralizer ($\Phi = \text{𐑬}$), which tolerates partial specificity, some off-rate, and low-level immunogenicity. The Frobenius-exact DARPin tolerates none of these.

---

## 4. Design 1: Frobenius-abicipar — Monomeric Frobenius-Exact DARPin

**Scaffold:** Abicipar-derived 4-repeat DARPin (N2C framework, 129 residues, 14.2 kDa)  
**Promotion:** Single primitive — $\Phi: \text{𐑬} \rightarrow \text{𐑹}$ (delta 2)  
**Clinical precedent:** Abicipar pegol completed Phase 3 with ~2 pM $K_d$ for VEGF-A and 12-day intravitreal half-life. The scaffold is validated for picomolar affinity and low systemic exposure.

### 4.1 Paratope Engineering for Fel d 1

Fel d 1 is a ~35 kDa tetrameric secretoglobin: two heterodimers of chain 1 (70 aa) and chain 2 (90 aa). The IgE epitopes map to the chain 1/chain 2 interface and a conformational epitope on chain 2.

**Strategy:** Ribosome display library ($10^{13}$ variants) with alternating positive/negative selection rounds:
- **Positive selection:** Recombinant Fel d 1 heterotetramer (all 7 isoforms pooled)
- **Negative selection:** Human secretoglobin panel (uteroglobin SCGB1A1, mammaglobin SCGB2A2, lipophilin SCGB1D2, secretoglobin SCGB3A1)
- **Stringency ramp:** $K_d$ threshold decreasing from $10^{-9}$ to $10^{-13}$ M over 6 rounds
- **Off-rate selection:** 72-hour competition with 1000× excess unlabeled Fel d 1 to eliminate fast-$k_{\text{off}}$ variants

**Target affinity:** $K_d < 5 \times 10^{-13}$ M for all Fel d 1 isoforms, with >1000-fold selectivity over the most similar human secretoglobin.

### 4.2 Deimmunization

DARPin scaffolds contain bacterial-derived framework residues that can present T-cell epitopes. The abicipar Phase 3 trial showed 15–20% intraocular inflammation — partly driven by anti-drug antibodies.

**Strategy:** 
- **In silico T-cell epitope prediction:** NetMHCIIpan 4.0 across 15 HLA-DR, 10 HLA-DQ, 6 HLA-DP alleles covering >95% of the global population
- **Framework humanization:** Replace immunogenic framework positions with residues from human ankyrin repeat domains (ANK1, ANK2, ANKRD family)
- **Treg epitope engineering:** Retain or introduce peptides predicted to bind HLA class II and activate regulatory T cells — inducing tolerance rather than immunity
- **B-cell epitope silencing:** Surface patch analysis to identify and mutate potential B-cell epitopes while preserving Fel d 1 binding

**Target:** Zero predicted T-cell epitopes (NetMHCIIpan rank < 2%) across all alleles. This goes beyond abicipar's partial deimmunization.

### 4.3 Formulation for Frobenius Closure

**Nasal spray:** 0.5% methylcellulose (4000 cP) in PBS, pH 6.0  
**DARPin concentration:** 2 mg/mL (125 μM)  
**Dose:** 100 μL per nostril = 200 μg DARPin total  
**Dosing:** 2 sprays 5 minutes before cat exposure  

**Frobenius-critical parameters:**
- DARPin: Fel d 1 molar ratio at nasal mucosa: ~$10^4:1$ (ensures μ is surjective)
- Mucosal residence time: 25–40 min (ensures δ completes before complex dissociation)
- No preservatives that could alter epithelial permeability


---

## 5. Design 2: Frobenius-MP0250 — Bi-paratopic Frobenius-Exact DARPin

**Inspiration:** MP0250 (dual-specific DARPin targeting VEGF + HGF)  
**Challenge:** MP0250's multi-specific architecture requires 2 promotions + 2 demotions to reach $\Phi = \text{𐑹}$. The $\text{𐑶}$ topology and $\text{𐑳}$ stoichiometry fight Frobenius closure — multi-specificity introduces degrees of freedom that break $\mu \circ \delta = \text{id}$.

**Key insight:** Two distinct binding domains create a composite $\mu = \mu_1 \otimes \mu_2$. For the composite to satisfy $\mu \circ \delta = \text{id}$, each domain must individually satisfy $\mu_i \circ \delta_i = \text{id}_i$ AND the domains must not interfere with each other's clearance. This is structurally demanding but not impossible.

### 5.1 Architecture

**Domains:** Two independent 3-repeat DARPin modules connected by a rigid helical linker (22 aa, derived from the R5 repeat consensus):
- **Domain A:** Binds Fel d 1 chain 1 (epitope: residues 18–35, the IgE-dominant region)
- **Domain B:** Binds Fel d 1 chain 2 (epitope: residues 45–60, the conformational IgE epitope)

**Structural justification:** The two domains bind non-overlapping epitopes on the same Fel d 1 heterodimer. This creates chelation-like avidity without the trimeric architecture of ensovibep. The rigid linker prevents both domains from binding the same epitope simultaneously — each Fel d 1 heterodimer binds exactly one DARPin molecule, preserving 1:1 stoichiometry.

### 5.2 Structural Resolution

To reach $\Phi = \text{𐑹}$, this design resolves the MP0250 demotions:

| Primitive | MP0250 value | Design 2 value | Resolution |
|-----------|-------------|----------------|------------|
| Þ (Topology) | $\text{𐑶}$ | $\text{𐑰}$ | Rigid linker + non-overlapping epitopes → each domain binds by inclusion, not product |
| Σ (Stoichiometry) | $\text{𐑳}$ | $\text{𐑙}$ | Both domains bind the same Fel d 1 molecule → 1:1 stoichiometry |
| ɢ (Composition) | $\text{𐑝}$ | $\text{𐑠}$ | Domains bind sequentially (A first, then B) due to epitope accessibility |

The sequential binding ($\text{𐑠}$) is critical: Domain A captures Fel d 1 first (higher $k_{\text{on}}$, solvent-exposed epitope), then Domain B locks in (avidity clamp). This sequentiality preserves the Markov-1 character — the two binding events collapse into one effective step.

### 5.3 Avidity Without Complexity

**Effective $K_d$:** $K_d^{\text{eff}} = K_d^A \times K_d^B / [\text{linker}]_{\text{eff}} \approx 10^{-13} \times 10^{-13} / 10^{-5} \approx 10^{-21}$ M  
**Practical affinity:** Limited by $k_{\text{on}}$ ceiling (~$10^7 \text{ M}^{-1}\text{s}^{-1}$) → effective $K_d \sim 10^{-15}$ M  
**Advantage over Design 1:** 100-fold higher effective affinity provides margin against isoform variation  

**Risk:** The rigid linker creates a structural constraint — if Fel d 1 isoforms vary in the distance between epitopes, Domain B binding may fail (breaking $\mu \circ \delta = \text{id}$). This must be experimentally verified against all 7 isoforms.

---

## 6. Design 3: Frobenius-Ensovibep — Avidity-Engineered Frobenius-Exact DARPin

**Inspiration:** Ensovibep (trimeric DARPin, femtomolar avidity against SARS-CoV-2 RBD)  
**Challenge:** Trimeric architecture ($\text{𐑶}$, $\text{𐑕}$) introduces the same demotion requirements as MP0250, but with a different resolution path.

### 6.1 Architecture

**Domains:** Three identical 3-repeat DARPin modules arranged in a C3-symmetric trimer via a trimerization domain (phage T4 fibritin foldon, 27 aa). Each module binds an identical epitope on Fel d 1 chain 2 (the IgE-immunodominant region).

**Key difference from ensovibep:** Ensovibep uses three identical domains to achieve avidity through simultaneous binding to three RBDs on the same spike trimer → $\Sigma = \text{𐑕}$, $\text{ɢ} = \text{𐑝}$. Design 3 resolves these differently.

### 6.2 Structural Resolution

| Primitive | Ensovibep value | Design 3 value | Resolution |
|-----------|----------------|----------------|------------|
| Þ (Topology) | $\text{𐑶}$ | $\text{𐑰}$ | The trimer binds one Fel d 1 at a time via the most accessible epitope; the other two domains are sterically blocked |
| Σ (Stoichiometry) | $\text{𐑕}$ | $\text{𐑙}$ | Despite three identical domains, functional binding is 1:1 due to steric exclusion |
| ɢ (Composition) | $\text{𐑝}$ | $\text{𐑠}$ | Domains compete sequentially; the first to encounter Fel d 1 binds |

### 6.3 The "Avidity Paradox" and Its Resolution

Trimeric avidity normally means all three domains bind simultaneously ($\text{𐑝}$, all-simultaneous). This is incompatible with $\Phi = \text{𐑹}$ because $\mu$ becomes multi-valued: there are multiple ways for the trimer to bind Fel d 1, and $\mu \circ \delta = \text{id}$ fails.

**Design 3's resolution:** Engineer the trimerization geometry so that only one domain can engage Fel d 1 at a time. The other two domains serve as "reserve" — if the first domain's complex dissociates before clearance, a second domain immediately rebinds. This creates **processive avidity** rather than simultaneous avidity.

**Processive avidity:** The effective $k_{\text{off}}$ is reduced by the probability that all three domains fail simultaneously: $k_{\text{off}}^{\text{eff}} = k_{\text{off}} \times (k_{\text{off}} / k_{\text{on}}[\text{DARPin}])^2 \approx 10^{-4} \times (10^{-4} / 10^7 \times 10^{-7})^2 \approx 10^{-12} \text{ s}^{-1}$.

This means the complex lifetime exceeds the nasal residence time by >$10^6$-fold — $\delta$ is guaranteed to complete before dissociation.

### 6.4 Advantage Over Design 1

The processive avidity provides a **kinetic proofreading** mechanism: only Fel d 1 that is correctly bound (matching the epitope geometry) benefits from the $k_{\text{off}}$ reduction. Off-target binding to human secretoglobins gets only single-domain affinity ($K_d \sim 10^{-9}$ M) and dissociates rapidly.

This is the closest structural analog to Frobenius-exactness in nature: the trimer provides redundancy that makes $\mu \circ \delta = \text{id}$ robust to thermal fluctuations and structural heterogeneity.


---

## 7. Comparative Structural Analysis

### 7.1 Design Comparison Matrix

| Property | Design 1 (Monomeric) | Design 2 (Bi-paratopic) | Design 3 (Processive Avidity) |
|----------|---------------------|------------------------|-------------------------------|
| Scaffold precedent | Abicipar | MP0250 | Ensovibep |
| Promotions from precedent | 1 (Φ) | 2 promotions + 2 demotions | 2 promotions + 2 demotions |
| Distance to $\Phi = \text{𐑹}$ target | 2.00 | 4.00 → resolved to 2.00 | 3.61 → resolved to 2.00 |
| $K_d$ (Fel d 1) | <5 pM | <1 fM (avidity) | <1 fM (processive) |
| Isoform coverage | Requires per-isoform validation | Epitope distance sensitivity | Epitope geometry sensitivity |
| Deimmunization difficulty | Moderate | High (linker + 2 domains) | High (trimerization domain) |
| Manufacturing complexity | Low (single domain) | Medium (two-domain fusion) | High (trimer, folding control) |
| CMC cost/bottle | ~$35 | ~$65 | ~$95 |
| Ouroboricity tier | O₀ | O₀ | O₀ |
| C-score | 0.0 | 0.0 | 0.0 |

### 7.2 Why All Three Remain O₀

The Frobenius-exact target has $\varphi = \text{𐑢}$ (sub-critical). The ouroborics interpretation states: *"No ouroboricity — system cannot form a self-referential critical loop (subcritical, supercritical, or EP)."*

This is correct. A DARPin therapeutic should NOT be at $\odot$ criticality — that would mean its binding behavior depends on its own binding history, creating feedback loops that could amplify noise or cause runaway. The Frobenius condition ($\mu \circ \delta = \text{id}$) is achieved through **structural precision**, not through self-modeling.

The $\Phi = \text{𐑹}$ at $\varphi = \text{𐑢}$ configuration is permitted by the grammar: the imscribing procedure says "$\mu \circ \delta = \text{id}$ exactly at $\odot$ → $\text{𐑹}$" — this means the Frobenius condition is VERIFIED at the critical point, but the system itself need not reside there. A system can exhibit $\Phi = \text{𐑹}$ at $\varphi = \text{𐑢}$ if $\mu \circ \delta = \text{id}$ is satisfied through exact structural complementarity rather than through critical dynamics.

### 7.3 The $\Phi = \text{𐑹}$ Gap

| Source | Distance to $\Phi = \text{𐑹}$ | Bottleneck |
|--------|-------------------------------|------------|
| DARPin neutralizer | 2.00 | $\Phi: \text{𐑬} \rightarrow \text{𐑹}$ |
| Abicipar pegol | 2.00 | $\Phi: \text{𐑬} \rightarrow \text{𐑹}$ |
| Formulated product | 2.83 | $\Phi: \text{𐑗} \rightarrow \text{𐑹}$ (larger delta) |
| MP0250 | 4.00 | $\Phi + \text{Þ} + \text{ɢ} + \Sigma$ |
| Ensovibep | 3.61 | $\Phi + \text{Þ} + \text{ɢ} + \Sigma$ |

The formulated product is closest to the ALLERGIC PATHWAY (0.89) but furthest from FROBENIUS-EXACTNESS (2.83). This is the central structural irony: the product that best mimics the disease structurally is worst-positioned to achieve $\mu \circ \delta = \text{id}$. The formulated product's $\Phi = \text{𐑗}$ (no symmetry) is the structural floor — it works by being indistinguishable from the background, not by being Frobenius-closed.

---

## 8. Verifiability — Testing $\mu \circ \delta = \text{id}$

The Frobenius condition must be experimentally verified. The following assays constitute the $\mu \circ \delta = \text{id}$ test battery:

### 8.1 $\mu$ Verification (Binding Completeness)

1. **SPR against all 7 Fel d 1 isoforms:** $K_d < 5$ pM for each. Any isoform with $K_d > 100$ pM → $\mu$ fails surjectivity.
2. **Cross-reactivity panel:** SPR against all 11 human secretoglobin family members + 50 most abundant nasal proteins. Any binding > 1% of Fel d 1 signal → $\mu$ fails specificity.
3. **Nasal lavage competition assay:** DARPin added to cat-allergic donor nasal lavage containing endogenous Fel d 1–IgE complexes. Must displace >99.9% of Fel d 1 from IgE within 30 seconds.

### 8.2 $\delta$ Verification (Clearance Completeness)

4. **Gamma scintigraphy:** $^{99m}$Tc-labeled DARPin–Fel d 1 complex nasal residence time. >95% cleared within 60 minutes. Any residual signal at 120 min → $\delta$ incomplete.
5. **Mucosal biopsy ELISA:** No detectable DARPin in nasal epithelium 4 hours post-dose.
6. **Serial nasal lavage:** DARPin concentration below detection limit (<1 ng/mL) at 4 hours.

### 8.3 $\text{id}$ Verification (Return to Baseline)

7. **ADA assay:** No anti-DARPin IgG or IgE detectable after 28-day daily dosing (ELISA, sensitivity <10 ng/mL). Any ADA → $\mu \circ \delta \neq \text{id}$.
8. **Tryptase monitoring:** Nasal lavage tryptase levels unchanged from baseline at all time points post-challenge. Any elevation → subclinical mast cell activation.
9. **Mucociliary clearance rate:** Saccharin transit time unchanged from baseline after 28-day dosing.
10. **Transcriptomic baseline:** RNA-seq of nasal epithelial brushings at days 0, 14, 28. No differentially expressed genes (FDR < 0.05, |log2FC| > 1) between pre and post.

### 8.4 The All-or-Nothing Criterion

$\Phi = \text{𐑹}$ is non-negotiable. All 10 assays must pass without exception. A 99% pass rate is failure — the Frobenius condition is exact. This is the structural meaning of "non-synthesizable": $\Phi = \text{𐑹}$ cannot be approached asymptotically. It either holds or it doesn't.


---

## 9. Safety and the Consent Framework

### 9.1 Why the Human Route Remains Preferred

The original design mandate specified the human route (suppressing cat allergies in humans) over the feline route (suppressing Fel d 1 production in cats). The Frobenius-exact designs honor this:

- **No feline modification.** Cats produce Fel d 1 normally. The intervention is entirely on the human side.
- **Reversible.** Discontinue the spray, and baseline allergy returns. No permanent alteration.
- **Consent-capable.** Adult humans can consent to nasal spray use. Cats cannot consent to genetic modification.

The Frobenius-exact DARPin is the structural dual of the consent principle: $\mu \circ \delta = \text{id}$ means the intervention leaves no trace — it respects the subject's baseline state.

### 9.2 Safety Profiling

The preclinical safety package must exceed the abicipar precedent:

| Safety Domain | Abicipar Issue | Frobenius Requirement |
|---------------|---------------|----------------------|
| Ocular inflammation | 15–20% (Phase 3) | 0% nasal inflammation |
| Anti-drug antibodies | ~5% (topical DARPin precedent) | 0% at 28 days |
| Epithelial permeability | Not studied (intravitreal) | Zero penetration (Franz cell, <0.1%) |
| Mucociliary disruption | N/A | Saccharin transit unchanged |
| Off-target secretoglobin binding | N/A | No binding to 11 human secretoglobins |
| Pediatric safety | Not studied | Must pass juvenile toxicology |

### 9.3 Phase 0 Entry: Nasal Explant Model

Before any human dosing, the DARPin must pass a human nasal explant assay:
- Fresh human nasal turbinate tissue (from elective surgery, with consent)
- DARPin applied at 10× clinical concentration
- Fel d 1 challenge at 100× environmental concentration
- Endpoints: tryptase release, IL-4/IL-13 secretion, epithelial integrity (TEER)
- Pass criterion: no significant difference from vehicle control on all endpoints

This is the minimum Frobenius gate before Phase 1.

---

## 10. Open Questions

### 10.1 Can $\mu \circ \delta = \text{id}$ Be Achieved With a Single DARPin?

Design 1 (monomeric) places the entire Frobenius burden on a single paratope. If any Fel d 1 isoform escapes binding, or if any human secretoglobin cross-reacts, $\mu \circ \delta = \text{id}$ fails. The structural simplicity (single Φ promotion) belies the molecular difficulty.

### 10.2 Does Bi-paratopic Binding Inherently Break $\Phi = \text{𐑹}$?

Design 2 resolves the MP0250 demotions by collapsing two binding events into one sequential step ($\text{ɢ} = \text{𐑠}$). But does the presence of two distinct paratopes inherently create a non-Frobenius degree of freedom? If Domain A binds but Domain B fails (e.g., due to isoform variation), the system is in a state that $\delta$ cannot fully resolve — breaking $\mu \circ \delta = \text{id}$.

### 10.3 Is Processive Avidity (Design 3) Robust to Mutational Drift?

Fel d 1 isoforms vary by 2–8 amino acid substitutions, mostly in surface-exposed regions. If an isoform alters the epitope such that only 1 or 2 of the 3 trimer domains can bind, the processive avidity advantage collapses. This must be experimentally verified against field isolates from diverse cat breeds.

### 10.4 The $\odot$ Question

The imscribing procedure states $\Phi = \text{𐑹}$ arises "at $\odot$" — the critical point. The Frobenius-exact target has $\varphi = \text{𐑢}$ (sub-critical). Is $\Phi = \text{𐑹}$ at $\varphi = \text{𐑢}$ structurally stable, or does it require $\varphi = \odot$ for long-term maintenance?

This has practical implications: if the DARPin formulation must operate at a critical point, any perturbation (temperature, pH, concentration) could push it away from $\Phi = \text{𐑹}$. A sub-critical $\Phi = \text{𐑹}$ would be more robust but may be structurally forbidden.

### 10.5 Manufacturing Tolerances

$\Phi = \text{𐑹}$ requires exact $\mu \circ \delta = \text{id}$. What manufacturing tolerance is acceptable? If one batch has 99.9% purity (0.1% misfolded DARPin that doesn't bind Fel d 1), $\mu$ is no longer surjective — the Frobenius condition fails. Does this mean Frobenius-exact DARPins require 100% manufacturing purity? If so, they may be physically unrealizable.

### 10.6 The Consent Paradox

If $\Phi = \text{𐑹}$ means the intervention is structurally invisible ($\mu \circ \delta = \text{id}$), then the subject cannot distinguish "having used the spray" from "not having used the spray" — except through the absence of allergic symptoms. Is an intervention that leaves no trace more ethically defensible, or less? The consent is to a non-event.

---

## 11. Summary

| Design | Promotions | $K_d$ | Key Innovation | Risk |
|--------|-----------|-------|---------------|------|
| **Frobenius-abicipar** | Φ only | <5 pM | Perfect specificity + deimmunization | Isoform escape |
| **Frobenius-MP0250** | Φ + ɢ (2 demotions) | <1 fM | Sequential bi-paratopic avidity | Epitope distance sensitivity |
| **Frobenius-Ensovibep** | Φ + ɢ (2 demotions) | <1 fM | Processive kinetic proofreading | Manufacturing complexity |

**Structural verdict:** All three designs are structurally valid paths to $\Phi = \text{𐑹}$. Design 1 is the simplest (single promotion) but places the heaviest burden on molecular engineering. Design 3 provides the most robust path through kinetic proofreading but at higher complexity. Design 2 is intermediate.

**The grammar does not choose between them.** The structural type is identical for all three after resolution: $\langle \text{𐑨} \cdot \text{𐑰} \cdot \text{𐑾} \cdot \text{𐑹} \cdot \text{𐑱} \cdot \text{𐑧} \cdot \text{𐑚} \cdot \text{𐑠} \cdot \text{𐑢} \cdot \text{𐑒} \cdot \text{𐑙} \cdot \text{𐑷} \rangle$. The choice comes down to experimental tractability and manufacturing feasibility.

**The near-Frobenius observation stands:** The formulated product's 0.8944 distance to the allergic pathway reveals a structural truth — the best therapeutic strategy is to operate on almost exactly the same structural floor as the disease. Frobenius-exactness takes this one step further: not just proximity, but exact algebraic closure.
