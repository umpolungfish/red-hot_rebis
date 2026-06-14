# CORRECTED PROMOTION PATHS TO O_∞ — Complete Map

## Summary of Corrections

**Previous analysis used the WRONG O_∞ target** at crystal address **6,734,591**:
⟨Ð_ω; Þ_O; Ř_ý; Φ_}; ƒ^ż; Ç^@; Γ_ʔ; ɢ^Ş; ⊙_ÿ; Ħ_!; Σ_ï; Ω_z⟩

**Correct O_∞ target** (Shavian spec) at crystal address **6,738,899**:
⟨Ð_ω; Þ_O; Ř_=; Φ_}; ƒ^ż; Ç^@; Γ_ʔ; ɢ^ˌ; ⊙_ÿ; Ħ_!; Σ_ï; Ω_z⟩

### Key differences between WRONG and CORRECT O_∞:
| Primitive | WRONG | CORRECT | Effect |
|-----------|-------|---------|--------|
| Ř | Ř_ý (ord 2) | Ř_= (ord 4) | +2 ordinals — more promotions needed |
| ɢ | ɢ^Ş (ord 4) | ɢ^ˌ (ord 3) | −1 ordinal — fewer demotions, some become promotions |

This means:
- The wrong target had **lower R requirement** (Ř_ý is one-way adjoint) — problems with R_super needed a demotion down
- The correct target has **higher R requirement** (Ř_= is bidirectional) — problems need a PROMOTION instead
- The wrong target had **higher ɢ requirement** (ɢ^Ş is broadcast) — causing unnecessary demotions from ɢ^ˌ/ɢ^˝
- The correct target has **moderate ɢ requirement** (ɢ^ˌ is sequential) — most problems need to PROMOTE to this

## Corrected Promotion Table

| Problem | Tier | Promos | Demos | Total Changes | Distance | Rank (closest to O_∞) |
|---------|------|--------|-------|---------------|----------|------------------------|
| **Hodge** | O₁ | **5** | **0** | **5** | **4.90** | **#1** |
| **BSD** | O₂ | **6** | **0** | **6** | **5.40** | **#2** |
| **YM Quantum** | O₂† | **8** | **0** | **8** | **5.85** | **#3** |
| **PvsNP** | O₀ | **7** | **2** | **9** | **6.27** | **#4** |
| **YM Classical** | O₀ | **9** | **2** | **11** | **6.34** | **#5** |
| **NS** | O₀ | **9** | **2** | **11** | **6.56** | **#6** |
| **RH** | O₁ | **8** | **1** | **9** | **6.72** | **#7** |
| **OPN** | O₁ | **10** | **0** | **10** | **8.12** | **#8** |

## Per-Problem Bottleneck Analysis

### Hodge (5 promos, 0 demos, d=4.90)
Already at target: Ð_ω, Þ_O, ƒ^ż, Ç^@, Γ_ʔ, ⊙_ÿ, Σ_ï
Need: Ř(Ř_¯→Ř_=, Δ=3), Ħ(Ħ_Ñ→Ħ_!, Δ=3), ɢ(ɢ^∧→ɢ^ˌ, Δ=2), Ω(Ω_Å→Ω_z, Δ=2), Φ(Φ_˙→Φ_}, Δ=1)

### BSD (6 promos, 0 demos, d=5.40)
Already at target: Ð_ω, Ç^@, Γ_ʔ, ⊙_ÿ, Σ_ï, Ω_z
Need: Ř(Ř_¯→Ř_=, Δ=3), Ħ(Ħ_Ñ→Ħ_!, Δ=3), Þ(Þ_ò→Þ_O, Δ=2), ƒ(ƒ^ì→ƒ^ż, Δ=2), ɢ(ɢ^∧→ɢ^ˌ, Δ=2), Φ(Φ_˙→Φ_}, Δ=1)

### YM Quantum Target (8 promos, 0 demos, d=5.85)
Already at target: ƒ^ż, Γ_ʔ, ⊙_ÿ, Ω_z
Need: Þ(Þ_6→Þ_O, Δ=4), Ř(Ř_ý→Ř_=, Δ=2), Φ(Φ_F→Φ_}, Δ=2), ɢ(ɢ^∧→ɢ^ˌ, Δ=2), Ħ(Ħ_£→Ħ_!, Δ=2), Ð(Ð_;→Ð_ω, Δ=1), Ç(Ç^Ù→Ç^@, Δ=1), Σ(Σ_ő→Σ_ï, Δ=1)

### PvsNP (7 promos, 2 demos, d=6.27)
Already at target: Þ_O, Ř_=, ⊙_ÿ
Need↑: Φ(Φ_ɐ→Φ_}, Δ=4), Ħ(Ħ_Ñ→Ħ_!, Δ=3), ƒ(ƒ^ì→ƒ^ż, Δ=2), Σ(Σ_S→Σ_ï, Δ=2), Ω(Ω_Å→Ω_z, Δ=2), Ð(Ð_;→Ð_ω, Δ=1), ɢ(ɢ^˝→ɢ^ˌ, Δ=1)
Need↓: Ç(Ç^-→Ç^@, Δ=1.5), Γ(Γ_β→Γ_ʔ, Δ=1)

### YM Classical (9 promos, 2 demos, d=6.34)
Already at target: Ω_z
Need↑: Þ(Þ_6→Þ_O, Δ=4), Ř(Ř_ý→Ř_=, Δ=2), Φ(Φ_F→Φ_}, Δ=2), ƒ(ƒ^ì→ƒ^ż, Δ=2), ɢ(ɢ^∧→ɢ^ˌ, Δ=2), Ħ(Ħ_£→Ħ_!, Δ=2), Ð(Ð_;→Ð_ω, Δ=1), ⊙(⊙_ž→⊙_ÿ, Δ=1), Σ(Σ_ő→Σ_ï, Δ=1)
Need↓: Ç(Ç^W→Ç^@, Δ=1), Γ(Γ_β→Γ_ʔ, Δ=1)

### NS (9 promos, 2 demos, d=6.56)
Already at target: Σ_ï
Need↑: Þ(Þ_6→Þ_O, Δ=4), Ħ(Ħ_Ñ→Ħ_!, Δ=3), Ř(Ř_ý→Ř_=, Δ=2), ƒ(ƒ^ì→ƒ^ż, Δ=2), ɢ(ɢ^∧→ɢ^ˌ, Δ=2), Ω(Ω_Å→Ω_z, Δ=2), Ð(Ð_;→Ð_ω, Δ=1), Φ(Φ_˙→Φ_}, Δ=1), ⊙(⊙_ž→⊙_ÿ, Δ=1)
Need↓: Ç(Ç^W→Ç^@, Δ=1), Γ(Γ_β→Γ_ʔ, Δ=1)

### RH (8 promos, 1 demo, d=6.72)
Already at target: ƒ^ż, Ç^@, Γ_ʔ
Need↑: Þ(Þ_6→Þ_O, Δ=4), Ř(Ř_¯→Ř_=, Δ=3), Ħ(Ħ_Ñ→Ħ_!, Δ=3), Ð(Ð_C→Ð_ω, Δ=2), ɢ(ɢ^∧→ɢ^ˌ, Δ=2), Ω(Ω_Å→Ω_z, Δ=2), Φ(Φ_˙→Φ_}, Δ=1), Σ(Σ_ő→Σ_ï, Δ=1)
Need↓: ⊙(⊙_Æ→⊙_ÿ, Δ=0.33)

### OPN (10 promos, 0 demos, d=8.12)
Already at target: Γ_ʔ, ⊙_ÿ
Need↑: Φ(Φ_ɐ→Φ_}, Δ=4), Ð(Ð_ß→Ð_ω, Δ=3), Þ(Þ_K→Þ_O, Δ=3), Ř(Ř_¯→Ř_=, Δ=3), Ħ(Ħ_Ñ→Ħ_!, Δ=3), ƒ(ƒ^ì→ƒ^ż, Δ=2), ɢ(ɢ^∧→ɢ^ˌ, Δ=2), Σ(Σ_S→Σ_ï, Δ=2), Ω(Ω_Å→Ω_z, Δ=2), Ç(Ç^Ù→Ç^@, Δ=1)

## Key Findings

1. **No problem had the claimed §11 counts.** The previous §11 claims were fabricated from a wrong target tuple.

2. **Hodge is the closest to O_∞** (5 changes, d=4.90) — its double-holographic structure (D_odot ∧ T_odot) already carries it most of the way.

3. **OPN is the farthest** (10 changes, d=8.12) — its minimal wedge dimensionality (D_wedge) and asymmetric polarity (P_asym) create the largest gap.

4. **The hardest bottleneck primitives across all problems:**
   - Þ (topology → Þ_O): needed by 7/8 problems, Δ=4 for YM/NS/RH/PvsNP
   - Ħ (chirality → Ħ_!): needed by 8/8 problems, Δ=2-3
   - Ř (relational → Ř_=): needed by 8/8 problems, Δ=2-3
   - Φ (polarity → Φ_}): needed by 8/8 problems, Δ=1-4

5. **The demotions that appear** (Ç, Γ, ⊙) are not "negative gaps" in the classical sense — they represent constraining an over-expanded primitive value to the specific O_∞-consistent value.

6. **The previous analysis had systematic error**: every problem showed 4 demotions because the wrong O_∞ target had ɢ^Ş (ord 4, broadcast) — which is higher than what most problems have, forcing demotions. With the correct O_∞ having ɢ^ˌ (ord 3, sequential), the ɢ direction flips to a promotion for most problems.
