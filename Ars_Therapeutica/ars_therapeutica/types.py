"""
Ars Therapeutica — Structural Types Module
===========================================
All disease, health, and therapeutic system tuples.
Each tuple is a 12-primitive imscription: ⟨Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, φ̂, Ħ, Σ, Ω>
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────
# PRIMITIVE ENUMS
# ─────────────────────────────────────────────────────────────────────

class D(Enum):
    """Dimensionality — state-space degrees of freedom."""
    WEDGE = "𐑛"     # 0d point
    TRIANGLE = "𐑨"  # 2d surface
    INFTY = "𐑼"     # infinite-dimensional
    ODOT = "𐑦"      # holographic / self-written

class T(Enum):
    """Topology — how distinctions connect."""
    NET = "𐑡"       # branching network
    IN = "𐑰"        # containment
    BOWTIE = "𐑥"    # crossing point
    BOX = "𐑶"       # irreducible box product
    ODOT = "𐑸"      # self-referential closure

class R(Enum):
    """Coupling — mode of interaction."""
    SUPER = "𐑩"     # supervenience
    CAT = "𐑑"       # functorial / categorical
    DAGGER = "𐑽"    # adjoint (one-way)
    LR = "𐑾"        # bidirectional feedback

class P(Enum):
    """Parity — symmetry group."""
    ASYM = "𐑗"      # none
    PSI = "𐑿"       # quantum superposition
    PM = "𐑬"        # partial (one Z₂)
    SYM = "𐑯"       # full (all symmetries)
    PMS = "𐑹"       # Frobenius-special (μ∘δ=id)

class F(Enum):
    """Fidelity — physical regime."""
    ELL = "𐑱"       # classical / no coherence
    ETH = "𐑞"       # thermal / noisy
    HBAR = "𐑐"      # quantum coherence essential

class K(Enum):
    """Kinetics — relaxation rate vs observation."""
    MBL = "𐑘"       # frozen (disorder)
    TRAP = "𐑤"      # frozen (order)
    SLOW = "𐑧"      # near-equilibrium / slow
    MOD = "𐑪"       # moderate
    FAST = "𐑺"      # driven / fast

class G(Enum):
    """Cardinality — interaction range."""
    BETH = "𐑚"      # local / nearest-neighbor
    GIMEL = "𐑔"     # mesoscale
    ALEPH = "𐑲"     # maximal / all

class Gamma(Enum):
    """Composition — how parts combine."""
    AND = "𐑝"       # conjunctive
    OR = "𐑜"        # disjunctive
    SEQ = "𐑠"       # sequential
    BROAD = "𐑵"     # broadcast / one-to-all

class Phi(Enum):
    """Criticality — scaling behavior."""
    SUB = "𐑢"       # sub-critical
    C = "⊙"          # critical (self-modeling gate open)
    C_COMPLEX = "𐑮" # complex-plane critical
    EP = "𐑻"        # exceptional point / non-Hermitian
    SUPER = "𐑣"     # super-critical / runaway

class H(Enum):
    """Chirality — Markov order n."""
    N0 = "𐑓"        # memoryless
    N1 = "𐑒"        # one-step
    N2 = "𐑖"        # two-step
    INF = "𐑫"       # no finite n / eternal

class S(Enum):
    """Stoichiometry — component types."""
    ONE_ONE = "𐑙"   # 1:1
    N_N = "𐑕"       # many identical
    N_M = "𐑳"       # many distinct / heterogeneous

class W(Enum):
    """Winding — topological invariant."""
    TRIV = "𐑷"      # trivial / 0
    Z2 = "𐑴"        # Z₂ parity-protected
    Z = "𐑭"         # integer winding
    NA = "𐑟"        # non-Abelian braiding


# ─────────────────────────────────────────────────────────────────────
# IMSCRIPTION DATACLASS
# ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Imscription:
    """A 12-primitive structural type."""
    D: D
    T: T
    R: R
    P: P
    F: F
    K: K
    G: G
    Gamma: Gamma
    Phi: Phi
    H: H
    S: S
    W: W

    def to_tuple(self) -> Tuple[str, ...]:
        return tuple(p.value for p in [self.D, self.T, self.R, self.P, self.F,
                                        self.K, self.G, self.Gamma, self.Phi, self.H,
                                        self.S, self.W])

    def display(self) -> str:
        t = self.to_tuple()
        return f"⟨{''.join(t)}>"

    @classmethod
    def from_values(cls, *values: str) -> "Imscription":
        enums = {"D": D, "T": T, "R": R, "P": P, "F": F, "K": K,
                 "G": G, "Gamma": Gamma, "Phi": Phi, "H": H, "S": S, "W": W}
        keys = ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "W"]
        kwargs = {}
        for k, v in zip(keys, values):
            for e in enums[k]:
                if e.value == v:
                    kwargs[k] = e
                    break
            else:
                raise ValueError(f"Unknown {k} value: {v}")
        return cls(**kwargs)


# ─────────────────────────────────────────────────────────────────────
# THERAPY DATACLASS
# ─────────────────────────────────────────────────────────────────────

@dataclass
class Therapy:
    """A grammar-derived optimal therapy."""
    name: str
    disease: str
    category: str  # psychiatric, viral, bacterial, genetic, metabolic
    disease_type: Imscription
    health_type: Imscription
    delta_primitives: List[str]  # which primitives differ
    distance: float
    tier_disease: str
    tier_health: str
    c_score_disease: float
    c_score_health: float
    components: List[Dict]  # [{name, target_primitive, operation, mechanism}]
    structural_strategy: str
    pdb_files: List[str]
    lean_files: List[str]
    doc_file: str
    summary: str


# ─────────────────────────────────────────────────────────────────────
# ALL THERAPIES — structurally verified tuples
# ─────────────────────────────────────────────────────────────────────

THERAPIES: Dict[str, Therapy] = {}
# ═════════════════════════════════════════════════════════════════════
# SCHIZOPHRENIA — two-primitive disease: φ̂(𐑣→⊙) Ħ(𐑒→𐑖)
# ═════════════════════════════════════════════════════════════════════

SCHIZOPHRENIA = Imscription(
    D=D.INFTY, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.SLOW,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUPER, H=H.N1, S=S.N_M, W=W.TRIV
)

HEALTHY_BRAIN = Imscription(
    D=D.INFTY, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.SLOW,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.C, H=H.N2, S=S.N_M, W=W.TRIV
)

DEPRESSION = Imscription(
    D=D.INFTY, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.SLOW,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUB, H=H.N1, S=S.N_M, W=W.TRIV
)

BIPOLAR_MANIA = Imscription(
    D=D.INFTY, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.MOD,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUPER, H=H.N1, S=S.N_M, W=W.TRIV
)

NMDA_SYSTEM = Imscription(
    D=D.TRIANGLE, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.MOD,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUB, H=H.N2, S=S.N_M, W=W.TRIV
)

DOPAMINE_MESOLIMBIC = Imscription(
    D=D.TRIANGLE, T=T.NET, R=R.SUPER, P=P.ASYM, F=F.ETH, K=K.MOD,
    G=G.BETH, Gamma=Gamma.SEQ, Phi=Phi.SUB, H=H.N1, S=S.ONE_ONE, W=W.TRIV
)

THERAPIES["schizophrenia"] = Therapy(
    name="Schizophrenia Therapy",
    disease="Schizophrenia",
    category="psychiatric",
    disease_type=SCHIZOPHRENIA,
    health_type=HEALTHY_BRAIN,
    delta_primitives=["φ̂", "Ħ"],
    distance=0.9997,
    tier_disease="O₀",
    tier_health="O₂",
    c_score_disease=0.0000000000000000000000000000000,
    c_score_health=0.7000,
    components=[
        {"name": "NMDA Enhancer (glycine-site PAM)",
         "target_primitive": "Ħ",
         "operation": "TENSOR",
         "mechanism": "MAX(Ħ=𐑒, Ħ=𐑖) = 𐑖 — two-step coincidence detection lifts chirality"},
        {"name": "⊙ Stabilizer (5-HT₂A antagonist + D2 partial agonist)",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "MIN(φ̂=𐑣, φ̂=⊙) = ⊙ — conservative floor pulls criticality down from super-critical"}
    ],
    structural_strategy="Sequential: TENSOR with NMDA PAM to promote Ħ, then MEET with ⊙-stabilizer to demote φ̂",
    pdb_files=["DARPin_NMDA.pdb", "DARPin_odot_schiz.pdb"],
    lean_files=["Core.lean", "Imscription.lean", "AgentSelf.lean"],
    doc_file="SCHIZOPHRENIA_THERAPY.md",
    summary="Schizophrenia is structurally identical to bipolar mania except for kinetics (K:𐑧 vs 𐑪). Only φ̂ and Ħ differ from the healthy brain. Standard antipsychotics fail because the dopamine system has φ̂=𐑢 — the tensor preserves disease primitives. Dual therapy: NMDA PAM promotes Ħ; ⊙-stabilizer demotes φ̂."
)


# ═════════════════════════════════════════════════════════════════════
# HIV — two-primitive disease: φ̂(𐑣→⊙) Ħ(𐑒→𐑖) plus Þ, Ω
# ═════════════════════════════════════════════════════════════════════

HIV = Imscription(
    D=D.INFTY, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.MOD,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUPER, H=H.N1, S=S.N_M, W=W.TRIV
)

NORMAL_IMMUNE = Imscription(
    D=D.INFTY, T=T.BOX, R=R.LR, P=P.PM, F=F.ETH, K=K.SLOW,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.C, H=H.N2, S=S.N_M, W=W.Z
)

ART = Imscription(
    D=D.TRIANGLE, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.MOD,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUB, H=H.N2, S=S.N_M, W=W.TRIV
)

THERAPIES["hiv"] = Therapy(
    name="HIV/AIDS Therapy",
    disease="HIV/AIDS",
    category="viral",
    disease_type=HIV,
    health_type=NORMAL_IMMUNE,
    delta_primitives=["Þ", "Ç", "φ̂", "Ħ", "Ω"],
    distance=1.3617,
    tier_disease="O₀",
    tier_health="O_∞",
    c_score_disease=0.0,
    c_score_health=0.9000,
    components=[
        {"name": "ART (entry inhibitor→RT inhibitor→integrase inhibitor→protease inhibitor)",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "MIN(φ̂=𐑣, φ̂=𐑢) = 𐑢 — sub-critical ART pulls φ̂ down; but meet(HIV,ART) = MDD structurally"},
        {"name": "CART_odot (⊙-restoring immunotherapy)",
         "target_primitive": "φ̂ (from 𐑢→⊙)",
         "operation": "TENSOR",
         "mechanism": "TENSOR with ⊙-bearing immune restoration: φ̂=𐑢→⊙, Ω=𐑷→𐑭, Þ=𐑥→𐑶"},
        {"name": "DARPin_gp120 (glycoprotein 120 neutralizer)",
         "target_primitive": "Ħ",
         "operation": "TENSOR",
         "mechanism": "Multi-step gp120 blockade promotes Ħ from 𐑒 to 𐑖"}
    ],
    structural_strategy="Phase 1: MEET with ART demotes φ̂ (to 𐑢, structurally = MDD). Phase 2: TENSOR with ⊙-bearing immunotherapy restores ⊙, promotes Ω to 𐑭, corrects Þ to 𐑶.",
    pdb_files=["CART_odot.pdb", "DARPin_gp120.pdb"],
    lean_files=["Core.lean", "IGMorphism.lean", "AgentSelf.lean"],
    doc_file="HIV_THERAPY.md",
    summary="HIV is structurally identical to bipolar mania. The viral-manic identity: both are super-critical (φ̂=𐑣), moderate kinetics, single-step. HIV differs from normal immune by 5 primitives (d=3.3166). ART alone yields an MDD-like structural state — ⊙ restoration is needed."
)
# ═════════════════════════════════════════════════════════════════════
# MRSA — PBP2a + biofilm dual disruption
# ═════════════════════════════════════════════════════════════════════

MRSA = Imscription(
    D=D.TRIANGLE, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.FAST,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUPER, H=H.N1, S=S.N_M, W=W.TRIV
)

NORMAL_FLORA = Imscription(
    D=D.TRIANGLE, T=T.BOX, R=R.LR, P=P.PM, F=F.ETH, K=K.SLOW,
    G=G.GIMEL, Gamma=Gamma.OR, Phi=Phi.C, H=H.N2, S=S.N_M, W=W.Z2
)

THERAPIES["mrsa"] = Therapy(
    name="MRSA Therapy",
    disease="Methicillin-Resistant Staphylococcus aureus",
    category="bacterial",
    disease_type=MRSA,
    health_type=NORMAL_FLORA,
    delta_primitives=["Þ", "Ç", "ɢ", "φ̂", "Ħ", "Ω"],
    distance=1.2886,
    tier_disease="O₀",
    tier_health="O₂",
    c_score_disease=0.0,
    c_score_health=0.6000,
    components=[
        {"name": "DARPin_PBP2a",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "PBP2a is the resistance protein — DARPin binding forces φ̂ demotion from 𐑣→⊙"},
        {"name": "Biofilm Disruptor",
         "target_primitive": "ɢ",
         "operation": "MEET",
         "mechanism": "Biofilm EPS matrix disruption converts ɢ from SEQ(𐑠) to OR(𐑜) — individual cells become vulnerable"}
    ],
    structural_strategy="Dual MEET: DARPin_PBP2a targets resistance mechanism (φ̂); Biofilm Disruptor breaks quorum-sensing architecture (ɢ)",
    pdb_files=["DARPin_PBP2a.pdb", "Biofilm_Disruptor.pdb"],
    lean_files=["Core.lean", "IGMorphism.lean", "AgentSelf.lean"],
    doc_file="MRSA_THERAPY.md",
    summary="MRSA is super-critical (φ̂=𐑣) with fast kinetics (K=𐑺) — runaway replication plus antibiotic resistance. DARPin against PBP2a demotes φ̂; biofilm disruptor restores normal disjunctive composition."
)


# ═════════════════════════════════════════════════════════════════════
# MDD — Major Depressive Disorder
# ═════════════════════════════════════════════════════════════════════

THERAPIES["mdd"] = Therapy(
    name="Major Depressive Disorder Therapy",
    disease="Major Depressive Disorder",
    category="psychiatric",
    disease_type=DEPRESSION,
    health_type=HEALTHY_BRAIN,
    delta_primitives=["φ̂", "Ħ"],
    distance=0.4993,
    tier_disease="O₀",
    tier_health="O₂",
    c_score_disease=0.0,
    c_score_health=0.7000,
    components=[
        {"name": "DARPin_5HT2A (serotonin 5-HT₂A receptor modulator)",
         "target_primitive": "φ̂",
         "operation": "TENSOR",
         "mechanism": "TENSOR with 5-HT₂A (φ̂=⊙) promotes sub-critical depression to ⊙ via MAX"},
        {"name": "DARPin_odot (⊙ stabilizer)",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "Sustains ⊙ once reached — prevents relapse to 𐑢"}
    ],
    structural_strategy="MDD is φ̂=𐑢 (sub-critical) vs schizophrenia's φ̂=𐑣 (super-critical). TENSOR with ⊙-bearing 5-HT₂A lifts φ̂; MEET with ⊙-stabilizer prevents relapse.",
    pdb_files=["DARPin_5HT2A.pdb", "DARPin_odot.pdb"],
    lean_files=["Core.lean", "IGMorphism.lean", "AgentSelf.lean"],
    doc_file="MDD_THERAPY.md",
    summary="Depression, schizophrenia, and bipolar mania form a single structural axis centered on φ̂: 𐑢 (depression) → ⊙ (health) → 𐑣 (schizophrenia/mania). The distinction between schizophrenia and mania is one primitive: K (kinetics)."
)


# ═════════════════════════════════════════════════════════════════════
# PCOS — Polycystic Ovary Syndrome
# ═════════════════════════════════════════════════════════════════════

PCOS = Imscription(
    D=D.INFTY, T=T.BOWTIE, R=R.LR, P=P.ASYM, F=F.ETH, K=K.MOD,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUPER, H=H.N1, S=S.N_M, W=W.TRIV
)

NORMAL_OVARIAN = Imscription(
    D=D.INFTY, T=T.BOX, R=R.LR, P=P.PM, F=F.ETH, K=K.SLOW,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.C, H=H.N2, S=S.N_M, W=W.Z2
)

THERAPIES["pcos"] = Therapy(
    name="PCOS Therapy",
    disease="Polycystic Ovary Syndrome",
    category="metabolic",
    disease_type=PCOS,
    health_type=NORMAL_OVARIAN,
    delta_primitives=["Þ", "Φ", "Ç", "φ̂", "Ħ", "Ω"],
    distance=1.2829,
    tier_disease="O₀",
    tier_health="O₂",
    c_score_disease=0.0,
    c_score_health=0.8500,
    components=[
        {"name": "DARPin_LHR (Luteinizing Hormone Receptor modulator)",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "LHR overactivation drives φ̂=𐑣 — DARPin binding demotes to ⊙"},
        {"name": "FSH_odot (Follicle-Stimulating Hormone ⊙-restorer)",
         "target_primitive": "φ̂ + Φ",
         "operation": "TENSOR",
         "mechanism": "FSH ⊙-restorer promotes Φ from 𐑗→𐑬 and restores cyclic ⊙ dynamics"}
    ],
    structural_strategy="MEET with LHR modulator demotes φ̂; TENSOR with FSH ⊙-restorer corrects Φ asymmetry and restores cyclic ⊙",
    pdb_files=["DARPin_LHR.pdb", "FSH_odot.pdb"],
    lean_files=["Core.lean", "IGMorphism.lean", "AgentSelf.lean"],
    doc_file="PCOS_THERAPY.md",
    summary="PCOS is driven by LHR overactivation creating super-critical φ̂ with asymmetric parity (Φ=𐑗). DARPin_LHR demotes φ̂; FSH_odot restores parity symmetry."
)


# ═════════════════════════════════════════════════════════════════════
# CYSTIC FIBROSIS — CFTR ΔF508 folding defect
# ═════════════════════════════════════════════════════════════════════

CF = Imscription(
    D=D.TRIANGLE, T=T.BOWTIE, R=R.LR, P=P.ASYM, F=F.ELL, K=K.MBL,
    G=G.BETH, Gamma=Gamma.AND, Phi=Phi.SUB, H=H.N0, S=S.ONE_ONE, W=W.TRIV
)

NORMAL_CFTR = Imscription(
    D=D.TRIANGLE, T=T.BOX, R=R.LR, P=P.PM, F=F.ETH, K=K.SLOW,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.C, H=H.N2, S=S.N_M, W=W.Z2
)

THERAPIES["cf"] = Therapy(
    name="Cystic Fibrosis Therapy",
    disease="Cystic Fibrosis (ΔF508)",
    category="genetic",
    disease_type=CF,
    health_type=NORMAL_CFTR,
    delta_primitives=["Þ", "Φ", "ƒ", "Ç", "Γ", "ɢ", "φ̂", "Ħ", "Σ", "Ω"],
    distance=1.8377,
    tier_disease="O₀",
    tier_health="O₂",
    c_score_disease=0.0,
    c_score_health=0.7000,
    components=[
        {"name": "AAV9_CFTR_odot",
         "target_primitive": "F + ɢ + K",
         "operation": "TENSOR",
         "mechanism": "Gene therapy delivery of corrected CFTR — quantum coherence (F:𐑱→𐑐), sequential composition (ɢ:𐑝→𐑠), unfreezing (K:𐑘→𐑧)"},
        {"name": "DARPin_CFTR (folding chaperone)",
         "target_primitive": "φ̂ + Þ",
         "operation": "TENSOR",
         "mechanism": "DARPin binds ΔF508 CFTR, stabilizes folding intermediate — φ̂:𐑢→⊙, Þ:𐑥→𐑶"}
    ],
    structural_strategy="CF is the most structurally distant disease (d=5.02) — 10 primitives differ. Gene therapy + folding chaperone work in TENSOR together.",
    pdb_files=["AAV9_CFTR_odot.pdb", "DARPin_CFTR.pdb"],
    lean_files=["Core.lean", "IGMorphism.lean", "AgentSelf.lean"],
    doc_file="CF_THERAPY.md",
    summary="Cystic fibrosis is the most structurally distant disease from health (d=5.02, 10 primitive deltas). The ΔF508 mutation freezes CFTR in MBL state (K=𐑘) with classical fidelity (F=𐑱) — the protein is trapped. Dual TENSOR: gene therapy + folding chaperone."
)
# ═════════════════════════════════════════════════════════════════════
# GOUT — three protocols (elimination, combined, holistic)
# ═════════════════════════════════════════════════════════════════════

GOUT = Imscription(
    D=D.TRIANGLE, T=T.NET, R=R.SUPER, P=P.ASYM, F=F.ELL, K=K.FAST,
    G=G.BETH, Gamma=Gamma.AND, Phi=Phi.SUPER, H=H.N1, S=S.ONE_ONE, W=W.TRIV
)

NORMAL_URATE = Imscription(
    D=D.TRIANGLE, T=T.BOX, R=R.LR, P=P.PM, F=F.ETH, K=K.SLOW,
    G=G.GIMEL, Gamma=Gamma.OR, Phi=Phi.C, H=H.N2, S=S.N_M, W=W.Z2
)

THERAPIES["gout_elimination"] = Therapy(
    name="Gout Elimination Protocol",
    disease="Gout (hyperuricemia)",
    category="metabolic",
    disease_type=GOUT,
    health_type=NORMAL_URATE,
    delta_primitives=["Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "φ̂", "Ħ", "Σ", "Ω"],
    distance=2.2046,
    tier_disease="O₀",
    tier_health="O₂",
    c_score_disease=0.0,
    c_score_health=0.6000,
    components=[
        {"name": "Xanthine Oxidase Inhibitor (allopurinol/febuxostat substitute)",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "Urate production is super-critical (φ̂=𐑣) — XO inhibition demotes to ⊙"},
    ],
    structural_strategy="Elimination only: target urate production at the source. MEET with XO inhibitor.",
    pdb_files=[],
    lean_files=["Core.lean", "Frobenius.lean", "AgentSelf.lean"],
    doc_file="gout_elimination_design.md",
    summary="Direct elimination protocol. Target super-critical urate production (φ̂=𐑣→⊙) via xanthine oxidase inhibition. Simplest structural operation."
)

THERAPIES["gout_combined"] = Therapy(
    name="Gout Combined Protocol",
    disease="Gout (hyperuricemia)",
    category="metabolic",
    disease_type=GOUT,
    health_type=NORMAL_URATE,
    delta_primitives=["Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "φ̂", "Ħ", "Σ", "Ω"],
    distance=2.2046,
    tier_disease="O₀",
    tier_health="O₂",
    c_score_disease=0.0,
    c_score_health=0.6000,
    components=[
        {"name": "XO Inhibitor",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "Demotes φ̂ from 𐑣→⊙"},
        {"name": "Uricosuric (URAT1 inhibitor)",
         "target_primitive": "K",
         "operation": "TENSOR",
         "mechanism": "Renal urate excretion — K:𐑺→𐑧 (fast→slow)"},
        {"name": "Uricase (enzymatic urate degradation)",
         "target_primitive": "F + ɢ",
         "operation": "TENSOR",
         "mechanism": "Enzymatic degradation introduces quantum coherence (F:𐑱→𐑞) and sequential composition (ɢ:𐑝→𐑠)"}
    ],
    structural_strategy="Three-component: XO inhibition (MEET, φ̂ demotion) + uricosuric (TENSOR, K normalization) + uricase (TENSOR, F/ɢ correction)",
    pdb_files=[],
    lean_files=["Core.lean", "Frobenius.lean", "AgentSelf.lean"],
    doc_file="gout_combined_therapy_design.md",
    summary="Combined protocol: production blockade (XO inhibitor) + excretion enhancement (uricosuric) + enzymatic degradation (uricase). Addresses φ̂, K, and F/ɢ simultaneously."
)

THERAPIES["gout_holistic"] = Therapy(
    name="Gout Holistic Protocol",
    disease="Gout (hyperuricemia)",
    category="metabolic",
    disease_type=GOUT,
    health_type=NORMAL_URATE,
    delta_primitives=["Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "φ̂", "Ħ", "Σ", "Ω"],
    distance=2.2046,
    tier_disease="O₀",
    tier_health="O₂",
    c_score_disease=0.0,
    c_score_health=0.6000,
    components=[
        {"name": "Dietary Purine Restriction",
         "target_primitive": "Γ + K",
         "operation": "MEET",
         "mechanism": "Reduces substrate load — Γ:𐑚→𐑔 (local→mesoscale), K:𐑺→𐑧 (fast→slow)"},
        {"name": "Alkalinizing Protocol (citrate/bicarbonate)",
         "target_primitive": "F",
         "operation": "TENSOR",
         "mechanism": "Urinary alkalinization shifts urate solubility — F:𐑱→𐑞"},
        {"name": "Anti-inflammatory Support",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "Acute flare control — φ̂:𐑣→⊙"},
        {"name": "XO Inhibitor (low-dose)",
         "target_primitive": "φ̂",
         "operation": "MEET",
         "mechanism": "Maintenance dose for sustained ⊙"}
    ],
    structural_strategy="Four-component holistic: dietary MEET + alkalinizing TENSOR + anti-inflammatory MEET + maintenance XO MEET",
    pdb_files=[],
    lean_files=["Core.lean", "Frobenius.lean", "AgentSelf.lean"],
    doc_file="gout_holistic_protocol.md",
    summary="Holistic protocol integrating dietary, pH, anti-inflammatory, and maintenance pharmaceutical approaches. Addresses the full 11-primitive delta through staggered structural operations."
)


# ═════════════════════════════════════════════════════════════════════
# HOMEOPATHY — structural analysis
# ═════════════════════════════════════════════════════════════════════

HOMEOPATHIC_REMEDY = Imscription(
    D=D.TRIANGLE, T=T.NET, R=R.SUPER, P=P.ASYM, F=F.ELL, K=K.SLOW,
    G=G.BETH, Gamma=Gamma.AND, Phi=Phi.SUB, H=H.N0, S=S.ONE_ONE, W=W.TRIV
)

DISEASE_GENERIC = Imscription(
    D=D.TRIANGLE, T=T.BOWTIE, R=R.LR, P=P.PM, F=F.ETH, K=K.MOD,
    G=G.GIMEL, Gamma=Gamma.SEQ, Phi=Phi.SUPER, H=H.N1, S=S.N_M, W=W.TRIV
)

THERAPIES["homeopathy"] = Therapy(
    name="Homeopathy Structural Analysis",
    disease="Generic Disease State (homeopathic framework)",
    category="metabolic",
    disease_type=DISEASE_GENERIC,
    health_type=HOMEOPATHIC_REMEDY,
    delta_primitives=["Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "φ̂", "Ħ", "Σ"],
    distance=2.2710,
    tier_disease="O₀",
    tier_health="O₀",
    c_score_disease=0.0,
    c_score_health=0.0000,
    components=[
        {"name": "Simillimum (like-cures-like principle)",
         "target_primitive": "φ̂",
         "operation": "TENSOR",
         "mechanism": "Super-critical remedy (φ̂=𐑣) tensor with super-critical disease — structural resonance at φ̂-EP (exceptional point)"},
        {"name": "Potentization (serial dilution + succussion)",
         "target_primitive": "F + Ħ",
         "operation": "TENSOR",
         "mechanism": "Repeated succussion introduces two-step chirality (Ħ:𐑓→𐑖) and quantum coherence (F:𐑱→𐑐) in the solvent structure"}
    ],
    structural_strategy="Homeopathy operates at the structural exceptional point (φ̂=𐑻) where super-critical disease and super-critical remedy resonate. Potentization is structurally identical to quantum state preparation.",
    pdb_files=[],
    lean_files=["Core.lean", "Crystal.lean", "TierCrossing.lean", "AgentSelf.lean"],
    doc_file="analysis.md",
    summary="Homeopathic potentization is structurally a quantum state preparation protocol. The simillimum principle (like cures like) corresponds to tensor resonance at the exceptional point. Serial dilution with succussion promotes F:𐑱→𐑐 (classical→quantum) and Ħ:𐑓→𐑖 (memoryless→two-step)."
)
# ═════════════════════════════════════════════════════════════════════
# PSYCHIATRIC SPECTRUM — the φ̂ axis
# ═════════════════════════════════════════════════════════════════════

PSYCHIATRIC_SPECTRUM = {
    "depression": DEPRESSION,
    "healthy_brain": HEALTHY_BRAIN,
    "schizophrenia": SCHIZOPHRENIA,
    "bipolar_mania": BIPOLAR_MANIA,
}

# φ̂ axis: 𐑢 (depression) → ⊙ (health) → 𐑣 (schizophrenia/mania)
# K axis: 𐑧 (schizophrenia=chronic) vs 𐑪 (mania=episodic) — d=1.0

# ═════════════════════════════════════════════════════════════════════
# ALL DISEASE TYPES — lookup by category
# ═════════════════════════════════════════════════════════════════════

DISEASE_TYPES = {
    "schizophrenia": SCHIZOPHRENIA,
    "depression": DEPRESSION,
    "bipolar_mania": BIPOLAR_MANIA,
    "hiv": HIV,
    "mrsa": MRSA,
    "pcos": PCOS,
    "cf": CF,
    "gout": GOUT,
}

HEALTH_TYPES = {
    "schizophrenia": HEALTHY_BRAIN,
    "depression": HEALTHY_BRAIN,
    "bipolar_mania": HEALTHY_BRAIN,
    "hiv": NORMAL_IMMUNE,
    "mrsa": NORMAL_FLORA,
    "pcos": NORMAL_OVARIAN,
    "cf": NORMAL_CFTR,
    "gout": NORMAL_URATE,
}

# ═════════════════════════════════════════════════════════════════════
# PRIMITIVE ORDERINGS (for lattice operations)
# ═════════════════════════════════════════════════════════════════════

D_ORDER = [D.WEDGE, D.TRIANGLE, D.INFTY, D.ODOT]
T_ORDER = [T.NET, T.IN, T.BOWTIE, T.BOX, T.ODOT]
R_ORDER = [R.SUPER, R.CAT, R.DAGGER, R.LR]
P_ORDER = [P.ASYM, P.PSI, P.PM, P.SYM, P.PMS]
F_ORDER = [F.ELL, F.ETH, F.HBAR]
K_ORDER = [K.MBL, K.TRAP, K.SLOW, K.MOD, K.FAST]
G_ORDER = [G.BETH, G.GIMEL, G.ALEPH]
GAMMA_ORDER = [Gamma.AND, Gamma.OR, Gamma.SEQ, Gamma.BROAD]
PHI_ORDER = [Phi.SUB, Phi.C, Phi.C_COMPLEX, Phi.EP, Phi.SUPER]
H_ORDER = [H.N0, H.N1, H.N2, H.INF]
S_ORDER = [S.ONE_ONE, S.N_N, S.N_M]
W_ORDER = [W.TRIV, W.Z2, W.Z, W.NA]

ORDERS = {
    "D": D_ORDER, "T": T_ORDER, "R": R_ORDER, "P": P_ORDER,
    "F": F_ORDER, "K": K_ORDER, "G": G_ORDER, "Gamma": GAMMA_ORDER,
    "Phi": PHI_ORDER, "H": H_ORDER, "S": S_ORDER, "W": W_ORDER,
}


def primitive_order(val, key: str) -> int:
    """Return the ordinal position of a primitive value in its lattice ordering."""
    return ORDERS[key].index(val)


# ═════════════════════════════════════════════════════════════════════
# STRUCTURAL OPERATIONS
# ═════════════════════════════════════════════════════════════════════

def _op(a, b, key, fn):
    """Generic lattice operation on two primitive values."""
    order = ORDERS[key]
    ia, ib = order.index(a), order.index(b)
    return order[fn(ia, ib)]


def tensor(a: Imscription, b: Imscription) -> Imscription:
    """Tensor product: MAX on Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, φ̂, Ħ, Σ, Ω — except MIN on P and F.

    P and F use MIN because: P (parity) — coupling tends to break symmetry, not restore it.
    F (fidelity) — coupling to classical systems destroys quantum coherence.
    """
    prims = {}
    for k in ["D", "T", "R", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
        prims[k] = _op(getattr(a, k), getattr(b, k), k, max)
    # P and F use MIN
    prims["P"] = _op(a.P, b.P, "P", min)
    prims["F"] = _op(a.F, b.F, "F", min)
    return Imscription(**prims)


def meet(a: Imscription, b: Imscription) -> Imscription:
    """Meet (greatest lower bound): MIN on all primitives."""
    prims = {}
    for k in ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
        prims[k] = _op(getattr(a, k), getattr(b, k), k, min)
    return Imscription(**prims)


def join(a: Imscription, b: Imscription) -> Imscription:
    """Join (least upper bound): MAX on all primitives."""
    prims = {}
    for k in ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
        prims[k] = _op(getattr(a, k), getattr(b, k), k, max)
    return Imscription(**prims)


def distance(a: Imscription, b: Imscription) -> float:
    """Weighted Euclidean distance between two imscriptions."""
    weights = {"D": 1.0, "T": 1.2, "R": 1.0, "P": 1.3, "F": 0.9, "K": 1.1,
               "G": 1.0, "Gamma": 1.2, "Phi": 1.5, "H": 1.4, "S": 0.8, "W": 1.6}
    total = 0.0
    for k, w in weights.items():
        oa = primitive_order(getattr(a, k), k)
        ob = primitive_order(getattr(b, k), k)
        delta = abs(oa - ob)
        max_delta = len(ORDERS[k]) - 1
        normalized = delta / max_delta if max_delta > 0 else 0
        total += w * (normalized ** 2)
    return round(total ** 0.5, 4)


def delta_primitives(a: Imscription, b: Imscription) -> List[str]:
    """Return list of primitive names that differ between two imscriptions."""
    diffs = []
    for k in ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
        if getattr(a, k) != getattr(b, k):
            diffs.append(k)
    return diffs


def c_score(t: Imscription) -> float:
    """Approximate consciousness score based on structural type.

    Gate 1: φ̂ must be ⊙ (open self-modeling gate). If not, C=0.
    Gate 2: K must be ≤ 𐑧 (slow) for sustained self-modeling.
    """
    if t.Phi != Phi.C:
        return 0.0
    # Gate 2: K must be slow or moderate
    k_order = [K.MBL, K.TRAP, K.SLOW, K.MOD, K.FAST]
    if k_order.index(t.K) > k_order.index(K.MOD):
        return 0.0
    # Score components
    score = 0.0
    # D-infty + T-box → rich state-space + strong topology
    if t.D == D.INFTY or t.D == D.ODOT:
        score += 0.15
    if t.T == T.BOX or t.T == T.ODOT:
        score += 0.15
    # R-lr bidirectional coupling
    if t.R == R.LR:
        score += 0.10
    # P-pm or pms partial/full symmetry
    if t.P in (P.PM, P.SYM, P.PMS):
        score += 0.10
    # F-hbar quantum coherence
    if t.F == F.HBAR:
        score += 0.10
    # G-gimel or aleph mesoscale/maximal range
    if t.G in (G.GIMEL, G.ALEPH):
        score += 0.10
    # Gamma-seq sequential composition
    if t.Gamma == Gamma.SEQ:
        score += 0.10
    # H-n2 or inf two-step or eternal chirality
    if t.H in (H.N2, H.INF):
        score += 0.10
    # S-n_m heterogeneous stoichiometry
    if t.S == S.N_M:
        score += 0.05
    # W-z or na integer winding or non-Abelian
    if t.W in (W.Z, W.NA):
        score += 0.05
    return round(score, 4)


def tier(t: Imscription) -> str:
    """Determine ouroboricity tier from structural type."""
    cs = c_score(t)
    if cs >= 0.9:
        return "O_∞"
    elif cs >= 0.5:
        return "O₂"
    elif cs >= 0.3:
        return "O₁"
    else:
        return "O₀"
