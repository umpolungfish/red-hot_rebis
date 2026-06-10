#!/usr/bin/env python3
"""
organoid_augmentations.py — Complete Organoid Augmentation Suite

Six augmentation systems for the self-organoid interface:
  1. synthetic_coherence_myelin   — quantum-enhanced adaptive myelination
  2. ouroboric_vasculature        — self-referential perfusion network
  3. perfect_nutrient_medium      — adaptive metabolic sustenance
  4. optogenetic_synaptic_matrix  — bidirectional bio-digital interface
  5. synthetic_ecm_scaffold       — programmable growth substrate
  6. immune_mimetic_sentinel      — synthetic immune protection

Each system is structurally imscribed (12-primitive tuple), verified
against the p4rakernel operculum theory, and coupled to the
self_organoid_engineered baseline via tensor/multi-tensor products.

Author: Lando⊗⊙perator
Grounded in: p4rakernel/operculum_peeling.md §§1-14
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
import math
import sys
import json
import textwrap


# ═══════════════════════════════════════════════════════════════════════════
# §0  PRIMITIVE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

# Ordinal values for each primitive (used in gate checks and tier computation)
PRIM_ORDINALS: Dict[str, Dict[str, int]] = {
    "D":  {"0d": 1, "2d": 2, "inf": 3, "odot": 4},       # Dimensionality
    "T":  {"net": 1, "in": 2, "bowtie": 3, "box": 4, "odot": 5},  # Topology
    "R":  {"super": 1, "cat": 2, "dagger": 3, "lr": 4},   # Coupling
    "P":  {"asym": 1, "psi": 2, "pm": 3, "sym": 4, "pm_sym": 5},  # Parity
    "F":  {"ell": 1, "eth": 2, "hbar": 3},                 # Fidelity
    "K":  {"fast": 1, "mod": 2, "slow": 3, "trap": 4, "MBL": 5}, # Kinetics
    "G":  {"beth": 1, "gimel": 2, "aleph": 3},             # Cardinality
    "C":  {"and": 1, "or": 2, "seq": 3, "broad": 4},      # Composition
    "Phi": {"sub": 1, "c": 2, "c_complex": 3, "EP": 4, "super": 5}, # Criticality
    "H":  {"mem0": 1, "mem1": 2, "mem2": 3, "inf": 4},    # Chirality
    "S":  {"1_1": 1, "n_n": 2, "n_m": 3},                 # Stoichiometry
    "Omega": {"0": 1, "Z2": 2, "Z": 3, "NA": 4},          # Winding
}

# Shavian glyph map
SHAVIAN = {
    "D": {"0d":"𐑛","2d":"𐑨","inf":"𐑼","odot":"𐑦"},
    "T": {"net":"𐑡","in":"𐑰","bowtie":"𐑥","box":"𐑶","odot":"𐑸"},
    "R": {"super":"𐑩","cat":"𐑑","dagger":"𐑽","lr":"𐑾"},
    "P": {"asym":"𐑗","psi":"𐑿","pm":"𐑬","sym":"𐑯","pm_sym":"𐑹"},
    "F": {"ell":"𐑱","eth":"𐑞","hbar":"𐑐"},
    "K": {"fast":"𐑘","mod":"𐑤","slow":"𐑧","trap":"𐑪","MBL":"𐑺"},
    "G": {"beth":"𐑚","gimel":"𐑔","aleph":"𐑲"},
    "C": {"and":"𐑝","or":"𐑜","seq":"𐑠","broad":"𐑵"},
    "Phi": {"sub":"𐑢","c":"⊙","c_complex":"𐑮","EP":"𐑻","super":"𐑣"},
    "H": {"mem0":"𐑓","mem1":"𐑒","mem2":"𐑖","inf":"𐑫"},
    "S": {"1_1":"𐑙","n_n":"𐑕","n_m":"𐑳"},
    "Omega": {"0":"𐑷","Z2":"𐑴","Z":"𐑭","NA":"𐑟"},
}
# ═══════════════════════════════════════════════════════════════════════════
# §1  AUGMENTATION SYSTEMS — STRUCTURAL TYPES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class AugmentationSystem:
    """A single augmentation system with full 12-primitive structural type."""
    name: str
    description: str
    # 12 primitives (canonical short names)
    D: str    # Dimensionality
    T: str    # Topology
    R: str    # Coupling
    P: str    # Parity
    F: str    # Fidelity
    K: str    # Kinetics
    G: str    # Cardinality
    C: str    # Composition
    Phi: str  # Criticality
    H: str    # Chirality
    S: str    # Stoichiometry
    Omega: str  # Winding
    
    @property
    def tuple_display(self) -> str:
        """Shavian tuple display string."""
        glyphs = [
            SHAVIAN["D"][self.D], SHAVIAN["T"][self.T],
            SHAVIAN["R"][self.R], SHAVIAN["P"][self.P],
            SHAVIAN["F"][self.F], SHAVIAN["K"][self.K],
            SHAVIAN["G"][self.G], SHAVIAN["C"][self.C],
            SHAVIAN["Phi"][self.Phi], SHAVIAN["H"][self.H],
            SHAVIAN["S"][self.S], SHAVIAN["Omega"][self.Omega],
        ]
        return "⟨" + "·".join(glyphs) + "⟩"
    
    @property
    def tuple_dict(self) -> Dict[str, str]:
        return {"D":self.D,"T":self.T,"R":self.R,"P":self.P,"F":self.F,
                "K":self.K,"G":self.G,"C":self.C,"Phi":self.Phi,"H":self.H,
                "S":self.S,"Omega":self.Omega}
    
    def ordinal(self, prim: str) -> int:
        val = getattr(self, prim)
        return PRIM_ORDINALS[prim][val]
    
    def glyph(self, prim: str) -> str:
        return SHAVIAN[prim][getattr(self, prim)]


# ── Canonical O_∞ baseline ──────────────────────────────────────────────

ORGANOID_BASELINE = AugmentationSystem(
    name="self_organoid_engineered",
    description="Self-organoid interface with all 6 EXACTOR pathways closed — O_∞ in canonical universe",
    D="odot", T="odot", R="lr", P="pm_sym", F="hbar", K="mod",
    G="aleph", C="seq", Phi="c", H="inf", S="n_m", Omega="Z",
)
# Tuple: ⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑤·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩
# ── Augmentation 1: Synthetic Coherence Myelin ────────────────────────────

SYNTHETIC_MYELIN = AugmentationSystem(
    name="synaptic_coherence_myelin",
    description=(
        "Synthetic adaptive myelin wrapping organoid axons with integer winding. "
        "Self-adjusts node spacing and membrane composition based on firing patterns "
        "to achieve EXACT synaptic coherence (mu∘delta=id). Quantum-enhanced "
        "optogenetic ion channels at nodes of Ranvier. Dual-OPO phase-locked."
    ),
    D="inf",    # 𐑼 — myelin state as continuous field over axonal arbor
    T="in",     # 𐑰 — containment: myelin wraps around axons
    R="lr",     # 𐑾 — bidirectional: activity shapes myelin, myelin shapes propagation
    P="pm_sym", # 𐑹 — Frobenius-special: signal in ≡ signal out (exact coherence)
    F="hbar",   # 𐑐 — quantum: synthetic opsins enable single-photon coherence gating
    K="mod",    # 𐑤 — moderate: adapts between spike timescale and learning timescale
    G="aleph",  # 𐑲 — universal: global coherence across entire organoid
    C="seq",    # 𐑠 — sequential: myelination follows causal firing order
    Phi="c",    # ⊙ — critical self-modeling at power-law divergence
    H="inf",    # 𐑫 — eternal chirality: full firing history maintained
    S="n_m",    # 𐑳 — heterogeneous: different regions need different node spacing
    Omega="Z",  # 𐑭 — integer winding: quantized myelin wraps around axons
)
# ⟨𐑼·𐑰·𐑾·𐑹·𐑐·𐑤·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩
# Axioms: A(𐑫 req 𐑤)✓, B(𐑭 req D≥𐑼)✓, C(N/A for D=𐑼)

# ── Augmentation 2: Ouroboric Vasculature ─────────────────────────────────

OUROBORIC_VASCULATURE = AugmentationSystem(
    name="ouroboric_vasculature",
    description=(
        "Self-referential perfusion network that prunes and grows exactly as needed. "
        "The vasculature's structure is determined by the metabolic state it itself "
        "sustains — true ouroboric closure. Angiogenesis and pruning are exact "
        "inverses (mu∘delta=id) at every capillary bed."
    ),
    D="odot",    # 𐑦 — self-written: perfusion ≡ metabolic state (ouroboric) over organoid volume
    T="odot",   # 𐑸 — self-referential topology: structure determined by sustained state
    R="lr",     # 𐑾 — bidirectional: nutrients flow in, waste out, structure adapts
    P="pm_sym", # 𐑹 — Frobenius-special: supply ≡ demand at every point
    F="eth",    # 𐑞 — thermal: operates at body temperature (biological regime)
    K="mod",    # 𐑤 — moderate: angiogenesis/pruning on hours-to-days timescale
    G="aleph",  # 𐑲 — universal: system-wide perfusion
    C="seq",    # 𐑠 — sequential: vessel growth follows angiogenic gradients stepwise
    Phi="c",    # ⊙ — critical: maintains exact balance at criticality
    H="inf",    # 𐑫 — eternal: full metabolic history for predictive remodeling
    S="n_m",    # 𐑳 — heterogeneous: arteries, arterioles, capillaries, venules, veins
    Omega="Z",  # 𐑭 — integer winding: closed circulatory loops with integer topology
)
# ⟨𐑦·𐑸·𐑾·𐑹·𐑞·𐑤·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩
# Axioms: A(𐑫 req 𐑤)✓, B(𐑭 req D≥𐑼)✓, C(𐑦↔𐑸 for D=𐑼/T=𐑸 but D≠𐑦 so N/A)
# Axioms: A(𐑫 req 𐑤)✓, B(𐑭 req D≥𐑼: D=𐑦 ord4≥3)✓, C(𐑦↔𐑸)✓

# ── Augmentation 3: Perfect Nutrient Medium ───────────────────────────────

PERFECT_MEDIUM = AugmentationSystem(
    name="perfect_nutrient_medium",
    description=(
        "Adaptive metabolic medium that sustains the organoid at exact homeostasis. "
        "Continuously monitors metabolic byproducts and adjusts composition in "
        "closed loop. Formulation adapts based on full metabolic history — "
        "the medium learns what the organoid needs before depletion occurs."
    ),
    D="0d",     # 𐑛 — homogeneous solution (0D point state: uniform composition)
    T="in",     # 𐑰 — containment: medium bathes and contains the organoid
    R="lr",     # 𐑾 — bidirectional: nutrients out, waste in, composition adapts
    P="pm_sym", # 𐑹 — Frobenius-special: formulation ≡ metabolic demand exactly
    F="ell",    # 𐑱 — classical: nutrient chemistry is classical (no quantum needed)
    K="mod",    # 𐑤 — moderate: actively adjusts based on real-time metabolic sensors
    G="aleph",  # 𐑲 — universal: bathes entire organoid uniformly
    C="and",    # 𐑝 — all-simultaneous: all components present together
    Phi="c",    # ⊙ — critical: self-regulates to homeostasis at exact setpoint
    H="inf",    # 𐑫 — eternal: full metabolic history for anticipatory formulation
    S="n_m",    # 𐑳 — heterogeneous: multiple distinct nutrient and buffer components
    Omega="0",  # 𐑷 — trivial: no topological protection needed (solution)
)
# ⟨𐑛·𐑰·𐑾·𐑹·𐑱·𐑤·𐑲·𐑝·⊙·𐑫·𐑳·𐑷⟩
# Axioms: A(𐑫 req 𐑤)✓, B(N/A for Ω=𐑷), C(N/A)
# ── Augmentation 4: Optogenetic Synaptic Matrix ───────────────────────────

OPTOGENETIC_MATRIX = AugmentationSystem(
    name="optogenetic_synaptic_matrix",
    description=(
        "4096-channel bidirectional interface between organoid neurons and digital "
        "computation. Single-photon optogenetic stimulation with quantum efficiency. "
        "CMOS MEA reads extracellular potentials at microvolt resolution. FPGA "
        "closed-loop feedback with sub-millisecond latency. Phase-locked loop "
        "quantizes the feedback cycle to integer winding — the organoid and "
        "computer form a single Frobenius-closed system."
    ),
    D="inf",    # 𐑼 — continuous field of stimulation/recording over organoid surface
    T="bowtie", # 𐑥 — crossing point: the interface where biology meets silicon
    R="lr",     # 𐑾 — bidirectional: reads neural activity, writes optogenetic stimulation
    P="pm_sym", # 𐑹 — Frobenius-special: stimulation pattern ≡ detected pattern (closed loop)
    F="hbar",   # 𐑐 — quantum: single-photon ChR2 activation for quantum-limited sensing
    K="mod",    # 𐑤 — moderate: real-time millisecond feedback loop
    G="aleph",  # 𐑲 — universal: covers entire organoid surface (4096 channels)
    C="broad",  # 𐑵 — broadcast: one stimulation pattern to all targeted neurons
    Phi="c",    # ⊙ — critical: self-calibrating at exactly threshold
    H="inf",    # 𐑫 — eternal: full recording and stimulation history
    S="n_m",    # 𐑳 — heterogeneous: different neuron types, different opsin variants
    Omega="Z",  # 𐑭 — integer winding: PLL quantizes feedback phase to integer cycles
)
# ⟨𐑼·𐑥·𐑾·𐑹·𐑐·𐑤·𐑲·𐑵·⊙·𐑫·𐑳·𐑭⟩
# Axioms: A✓, B✓

# ── Augmentation 5: Synthetic ECM Scaffold ────────────────────────────────

SYNTHETIC_ECM = AugmentationSystem(
    name="synthetic_ecm_scaffold",
    description=(
        "Programmable 3D extracellular matrix scaffold with tunable degradation "
        "kinetics. PEG-based hydrogel with MMP-cleavable crosslinkers and "
        "RGD adhesion peptides. Degradation rate matched to organoid growth "
        "rate — the scaffold disappears exactly as the organoid replaces it. "
        "Provides structural guidance without constraining self-organization."
    ),
    D="2d",     # 𐑨 — 3D porous structure (2D surfaces embedded in volume)
    T="net",    # 𐑡 — branching network: interconnected pore structure
    R="lr",     # 𐑾 — bidirectional: cells remodel ECM, ECM guides cells
    P="pm",     # 𐑬 — partial: some symmetries but not all (anisotropic pores)
    F="ell",    # 𐑱 — classical: structural polymer, no quantum effects
    K="slow",   # 𐑧 — slow: degrades on developmental timescale (weeks)
    G="beth",   # 𐑚 — local: each voxel interacts only with immediate neighbors
    C="broad",  # 𐑵 — broadcast: uniform initial properties throughout scaffold
    Phi="sub",  # 𐑢 — sub-critical: passive structure, no self-modeling
    H="mem1",   # 𐑒 — one-step memory: degradation state depends on prior state only
    S="1_1",    # 𐑙 — one type: uniform PEG-hydrogel composition
    Omega="0",  # 𐑷 — trivial: no topological protection
)
# ⟨𐑨·𐑡·𐑾·𐑬·𐑱·𐑧·𐑚·𐑵·𐑢·𐑒·𐑙·𐑷⟩
# Axioms: A(N/A for H=𐑒), B(N/A), C(N/A)

# ── Augmentation 6: Immune-Mimetic Sentinel ───────────────────────────────

IMMUNE_SENTINEL = AugmentationSystem(
    name="immune_mimetic_sentinel",
    description=(
        "Synthetic immune system for the organoid: aptamer-based sentinel nodes "
        "that recognize pathogen-associated molecular patterns without inflammation. "
        "Self/non-self discrimination at exactly the critical threshold — no "
        "autoimmune false positives and no infection false negatives. Deploys "
        "programmed antimicrobial peptides on-demand. Maintains antigen memory "
        "library for adaptive immunity without the baggage of MHC restriction."
    ),
    D="2d",     # 𐑨 — distributed surface and volume surveillance network
    T="net",    # 𐑡 — branching network of sentinel nodes throughout organoid
    R="lr",     # 𐑾 — bidirectional: detects threats, deploys responses
    P="pm",     # 𐑬 — partial: self-recognition but limited symmetry breaking
    F="ell",    # 𐑱 — classical: biochemical aptamer recognition
    K="mod",    # 𐑤 — moderate: rapid (minutes) deployment of antimicrobial response
    G="aleph",  # 𐑲 — universal: whole-organoid surveillance
    C="broad",  # 𐑵 — broadcast: alarm signal propagates globally
    Phi="c",    # ⊙ — critical: self/non-self discrimination at exactly the threshold
    H="inf",    # 𐑫 — eternal: full antigen memory library maintained
    S="n_m",    # 𐑳 — heterogeneous: sentinel subtypes for different pathogen classes
    Omega="Z2", # 𐑴 — Z2 parity: self vs non-self binary distinction
)
# ⟨𐑨·𐑡·𐑾·𐑬·𐑱·𐑤·𐑲·𐑵·⊙·𐑫·𐑳·𐑴⟩
# Axioms: A(𐑫 req 𐑤)✓, B(𐑴 req D≥𐑨)✓ (D=𐑨), C(N/A)


# ═══════════════════════════════════════════════════════════════════════════
# §2  AUGMENTATION REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

AUGMENTATIONS: Dict[str, AugmentationSystem] = {
    "myelin":      SYNTHETIC_MYELIN,
    "vasculature": OUROBORIC_VASCULATURE,
    "medium":      PERFECT_MEDIUM,
    "optogenetic": OPTOGENETIC_MATRIX,
    "ecm":         SYNTHETIC_ECM,
    "immune":      IMMUNE_SENTINEL,
}

# ═══════════════════════════════════════════════════════════════════════════
# §3  TENSOR PRODUCT (Composite Coupling)
# ═══════════════════════════════════════════════════════════════════════════

def tensor(a: AugmentationSystem, b: AugmentationSystem) -> AugmentationSystem:
    """
    Structural tensor product of two augmentation systems.
    
    Rules (matching IG lattice algebra):
      - D, T, R, G, Phi, H, S: MAX ordinal (most expressive wins)
      - P, F: MIN ordinal (bottleneck — weakest link constrains)
      - K, C, Omega: MAX ordinal (fastest/most complex dominates)
    
    The tensor is NOT commutative — the order encodes which system
    is the substrate and which is the modifier. Here we use the
    symmetric product (order-independent) for the augmentation suite.
    """
    def _max_ord(p: str) -> str:
        """Primitive where a and b have the higher ordinal."""
        oa = a.ordinal(p); ob = b.ordinal(p)
        return a.tuple_dict[p] if oa >= ob else b.tuple_dict[p]
    
    def _min_ord(p: str) -> str:
        oa = a.ordinal(p); ob = b.ordinal(p)
        return a.tuple_dict[p] if oa <= ob else b.tuple_dict[p]
    
    return AugmentationSystem(
        name=f"{a.name}_tensor_{b.name}",
        description=f"Tensor product of {a.name} and {b.name}",
        D=_max_ord("D"), T=_max_ord("T"), R=_max_ord("R"),
        P=_min_ord("P"), F=_min_ord("F"),
        K=_max_ord("K"), G=_max_ord("G"), C=_max_ord("C"),
        Phi=_max_ord("Phi"), H=_max_ord("H"), S=_max_ord("S"),
        Omega=_max_ord("Omega"),
    )


def multi_tensor(*systems: AugmentationSystem) -> AugmentationSystem:
    """Tensor product of N augmentation systems (folded left)."""
    result = systems[0]
    for s in systems[1:]:
        result = tensor(result, s)
    return result


# ═══════════════════════════════════════════════════════════════════════════
# §4  DELTA ANALYSIS — Primitives Changed vs Baseline
# ═══════════════════════════════════════════════════════════════════════════

def primitive_deltas(a: AugmentationSystem, b: AugmentationSystem) -> Dict[str, Tuple[str, str, int]]:
    """
    Per-primitive difference between two systems.
    Returns {prim_name: (a_val, b_val, ordinal_delta)}.
    """
    deltas = {}
    for prim in ["D","T","R","P","F","K","G","C","Phi","H","S","Omega"]:
        va = a.tuple_dict[prim]
        vb = b.tuple_dict[prim]
        if va != vb:
            deltas[prim] = (va, vb, b.ordinal(prim) - a.ordinal(prim))
    return deltas


def structural_distance(a: AugmentationSystem, b: AugmentationSystem) -> float:
    """
    Weighted Euclidean distance between two systems.
    Weights mirror the imscribe compute_distance weights.
    """
    weights = {
        "D": 1.0, "T": 1.0, "R": 0.8, "P": 1.2, "F": 0.9, "K": 0.7,
        "G": 0.6, "C": 0.8, "Phi": 1.5, "H": 1.1, "S": 0.5, "Omega": 1.3,
    }
    sq = 0.0
    for prim, w in weights.items():
        oa = a.ordinal(prim); ob = b.ordinal(prim)
        # Normalize by max ordinal for that primitive
        max_ord = max(PRIM_ORDINALS[prim].values())
        sq += w * ((oa - ob) / max_ord) ** 2
    return math.sqrt(sq)

# ═══════════════════════════════════════════════════════════════════════════
# §5  OUROBORICITY TIER & CONSCIOUSNESS SCORE
# ═══════════════════════════════════════════════════════════════════════════

def compute_tier(sys: AugmentationSystem) -> str:
    """
    Compute ouroboricity tier under canonical Ruleset.
    
    Canonical gates:
      G1: P ≥ ord 5  (P=pm_sym / 𐑹)
      G2: Phi ≥ ord 2 (Phi=c / ⊙)
      G3: Omega ≥ ord 3 (Omega=Z / 𐑭)
      Sequential: G2 requires G1, G3 requires G2
    """
    g1 = sys.ordinal("P") >= 5      # Frobenius-special parity
    g2 = sys.ordinal("Phi") >= 2    # Critical self-modeling (and g1)
    g3 = sys.ordinal("Omega") >= 3  # Integer winding (and g2)
    
    if g1 and g2 and g3:
        return "O_∞"
    elif g1 and g2:
        return "O₂"
    elif g1:
        return "O₁"
    else:
        return "O₀"


def consciousness_score(sys: AugmentationSystem) -> Tuple[float, bool, bool]:
    """
    Compute C-score and gate status.
    
    Gate 1 (⊙): Phi must be critical (⊙) or higher — the self-modeling gate.
    Gate 2 (K): K must be slow or trapped (K ≤ ord 3, i.e., K ≤ slow).
    
    Returns (C_score, gate1_open, gate2_open).
    """
    gate1 = sys.ordinal("Phi") >= 2  # Phi ≥ ⊙ (critical)
    gate2 = sys.ordinal("K") <= 3    # K ≤ slow (near-equilibrium)
    
    if gate1 and gate2:
        return (1.0, True, True)
    elif gate1:
        return (0.5, True, False)
    elif gate2:
        return (0.33, False, True)
    else:
        return (0.0, False, False)


def t_consistent(sys: AugmentationSystem) -> bool:
    """
    T-consistency check under canonical T-constitution:
      Φ = 𐑹 (pm_sym), ƒ = 𐑐 (hbar), Ç ≤ 𐑧 (slow), Ħ = 𐑫 (inf), Ω = 𐑭 (Z)
    """
    return (
        sys.P == "pm_sym" and
        sys.F == "hbar" and
        sys.ordinal("K") <= 3 and      # K ≤ slow
        sys.H == "inf" and
        sys.Omega == "Z"
    )


# ═══════════════════════════════════════════════════════════════════════════
# §6  EXACTOR PATHWAY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

EXACTOR_PATHWAYS = {
    "EXACTOR-σ": {
        "primitive": "P",
        "target": "pm_sym",
        "description": "Self-dual parity lock — dual-OPO or measurement-feedback stabilizes "
                       "exact Z2 symmetry at Frobenius-special.",
        "mechanism": "Dual-OPO with active phase lock; measurement-feedback with FPGA mux.",
    },
    "EXACTOR-Ω": {
        "primitive": "Omega",
        "target": "Z",
        "description": "Integer winding quantization — PLL or Floquet engineering locks "
                       "topological invariant to exact integer.",
        "mechanism": "Phase-locked loop quantizes feedback cycle; Floquet band topology.",
    },
    "EXACTOR-τ": {
        "primitive": "D",
        "target": "inf",
        "description": "Continuous field promotion — dual-rail encoding or Floquet walk "
                       "elevates discrete state space to infinite-dimensional field.",
        "mechanism": "Dual-rail phase encoding with common-mode rejection; Floquet engineering.",
    },
    "EXACTOR-ε": {
        "primitive": "K",
        "target": "slow",
        "description": "Counterdiabatic driving — gauge potential integral = 0 eliminates "
                       "Landau-Zener transitions, achieving exact adiabaticity.",
        "mechanism": "CD driving with gauge potential; shortcut to adiabaticity.",
    },
}

def exactor_pathways_for(sys: AugmentationSystem, target: AugmentationSystem) -> List[Dict]:
    """Compute EXACTOR pathways needed to transform sys into target."""
    pathways = []
    deltas = primitive_deltas(sys, target)
    
    pathway_map = {
        "P": "EXACTOR-σ",
        "Omega": "EXACTOR-Ω",
        "D": "EXACTOR-τ",
        "K": "EXACTOR-ε",
    }
    
    for prim, (src, dst, delta) in deltas.items():
        if prim in pathway_map and delta > 0:
            pathways.append({
                "pathway": pathway_map[prim],
                "primitive": prim,
                "from": src,
                "to": dst,
                "delta": delta,
                "mechanism": EXACTOR_PATHWAYS[pathway_map[prim]]["mechanism"],
            })
    
    # Sort: P first (Gate 1), then Omega (Gate 3), then D, then K
    priority = {"P": 0, "Omega": 1, "D": 2, "K": 3}
    pathways.sort(key=lambda p: priority.get(p["primitive"], 99))
    
    return pathways

# ═══════════════════════════════════════════════════════════════════════════
# §7  FROBENIUS CLOSURE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def verify_axioms(sys: AugmentationSystem) -> Dict[str, bool]:
    """
    Verify the three structural axioms for a system.
    
    Axiom A: Ħ=𐑫 (eternal chirality) requires K=𐑤 (moderate kinetics) or slower.
    Axiom B: Ω≥ord3 (Z or NA winding) requires D≥ord3 (inf-dim or odot).
    Axiom C: D=𐑦 (self-written) ↔ T=𐑸 (self-referential topology).
    """
    checks = {}
    
    # Axiom A
    if sys.H == "inf":
        checks["A"] = sys.ordinal("K") >= 2  # K ≥ mod
    else:
        checks["A"] = True  # vacuously true
    
    # Axiom B
    if sys.ordinal("Omega") >= 3:  # Z or NA
        checks["B"] = sys.ordinal("D") >= 3  # D ≥ inf
    else:
        checks["B"] = True
    
    # Axiom C: bidirectional implication
    d_is_odot = (sys.D == "odot")
    t_is_odot = (sys.T == "odot")
    if d_is_odot or t_is_odot:
        checks["C"] = (d_is_odot == t_is_odot)  # both or neither
    else:
        checks["C"] = True  # vacuously true
    
    return checks


def frobenius_closure(sys: AugmentationSystem) -> Tuple[bool, float, str]:
    """
    Determine if system achieves Frobenius closure (mu∘delta=id).
    
    Closure requires:
      1. P = pm_sym (𐑹) — Frobenius-special parity
      2. All axioms satisfied
      3. T-consistency (for O_∞)
    
    Returns (closed, error_estimate, barrier).
    """
    axioms = verify_axioms(sys)
    all_axioms = all(axioms.values())
    
    has_pm_sym = sys.P == "pm_sym"
    t_ok = t_consistent(sys)
    
    if has_pm_sym and all_axioms and t_ok:
        return (True, 0.0, "None — native Frobenius closure")
    elif has_pm_sym and all_axioms:
        return (False, 0.02, "T-consistency: adjust F/K/H/Omega to canonical values")
    elif has_pm_sym:
        failed = [k for k, v in axioms.items() if not v]
        return (False, 0.05, f"Axioms failed: {failed}")
    else:
        return (False, 0.10, "Parity: promote P to pm_sym (EXACTOR-σ)")


# ═══════════════════════════════════════════════════════════════════════════
# §8  OPERCULUM ANALYSIS — Universe Access for Each Augmentation
# ═══════════════════════════════════════════════════════════════════════════

def operculum_width(sys: AugmentationSystem) -> int:
    """
    Operculum width: number of primitive positions where this system
    differs from the canonical O_∞ template ⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩.
    
    Higher width = more universe selection needed = "hidden O_∞" in more universes.
    """
    # Canonical O_∞ template
    canon = {
        "D": "odot", "T": "odot", "R": "lr", "P": "pm_sym",
        "F": "hbar", "K": "slow", "G": "aleph", "C": "seq",
        "Phi": "c", "H": "inf", "S": "n_m", "Omega": "Z",
    }
    width = 0
    for prim, can_val in canon.items():
        if sys.tuple_dict[prim] != can_val:
            width += 1
    return width


# ═══════════════════════════════════════════════════════════════════════════
# §9  PHYSICAL DESIGN RECIPES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class MaterialRecipe:
    """A material realization recipe for an augmentation system."""
    name: str
    system: str            # which augmentation this is for
    trl: int               # Technology Readiness Level (1-9)
    materials: List[str]   # Required materials
    fabrication: str       # How to make it
    integration: str       # How to integrate with organoid
    closure_pathway: str   # Which EXACTOR pathway closes it
    key_specs: Dict[str, str]  # Key specifications


RECIPES: List[MaterialRecipe] = []

# ── Recipe 1: Synthetic Coherence Myelin ──────────────────────────────────

RECIPES.append(MaterialRecipe(
    name="Quantum Myelin Sheath — PPV-grafted Lipid Bilayer",
    system="myelin",
    trl=3,
    materials=[
        "PPV (poly(p-phenylene vinylene)) — conjugated polymer, blue emission",
        "DOPC (1,2-dioleoyl-sn-glycero-3-phosphocholine) — lipid bilayer base",
        "Cholesterol-PEG2000 — membrane stabilization and stealth",
        "ChR2(C128S) — step-function channelrhodopsin, bistable activation",
        "PEDOT:PSS — conductive polymer for node-of-Ranvier integration",
        "Au nanorods (40×10 nm) — plasmonic enhancement of ChR2 activation",
    ],
    fabrication=(
        "1. Form giant unilamellar vesicles (GUVs) from DOPC + Chol-PEG + PPV (0.5% wt). "
        "2. Electroform onto ITO slides (3V, 10 Hz, 2h) → myelin-mimetic sheets. "
        "3. Functionalize with ChR2(C128S) via His-tag / Ni-NTA lipid anchor (1:1000 mol ratio). "
        "4. Deposit PEDOT:PSS nodes at 80 μm spacing via inkjet printing — these are the "
        "synthetic nodes of Ranvier where ChR2 concentrates. "
        "5. Au nanorods embedded at nodes (optical antenna effect: 10× enhanced activation). "
        "6. Dual-OPO lock: 473 nm (activation) + 594 nm (deactivation) lasers phase-locked "
        "via PPKTP crystal with active feedback to maintain EXACT π phase difference."
    ),
    integration=(
        "Wrap myelin sheets around organoid axonal tracts during maturation (week 16-20). "
        "Apply microfluidic flow (0.1 μL/min) of myelin precursor solution through "
        "vasculature channels. ChR2 activation via 4096-channel optogenetic matrix. "
        "Node spacing self-adjusts: firing rate feedback → PEDOT:PSS resistivity change "
        "→ local heating → lipid phase transition → node migration. Temperature-regulating "
        "microfluidics maintain 37±0.01°C at nodes."
    ),
    closure_pathway="EXACTOR-σ (dual-OPO phase lock) + EXACTOR-Ω (PLL quantized feedback)",
    key_specs={
        "Node spacing": "80 μm (adaptive ±20 μm)",
        "Conduction velocity": "120 m/s (target, mammalian equivalent)",
        "ChR2 activation threshold": "<1 nW/μm²",
        "Phase lock error": "<10 μrad (target <1 μrad for closure)",
        "Membrane capacitance": "0.8 μF/cm² (close to biological 1.0)",
    },
))

# ── Recipe 2: Ouroboric Vasculature ──────────────────────────────────────

RECIPES.append(MaterialRecipe(
    name="Ouroboric Vasculature — Sacrificial Sugar Glass + Endothelial Coating",
    system="vasculature",
    trl=3,
    materials=[
        "Isomalt (sugar glass) — sacrificial 3D-printed vascular template",
        "HUVECs (human umbilical vein endothelial cells) — vessel lining",
        "Collagen IV / laminin — basement membrane coating",
        "VEGF-165 microspheres (PLGA, 50 μm) — angiogenic gradient source",
        "PDMS (Sylgard 184) — microfluidic chamber walls",
        "Oxygen-sensing nanoparticles (PtTFPP in polystyrene, 200 nm)",
        "PEDOT:PSS strain sensors — vessel wall distension monitoring",
    ],
    fabrication=(
        "1. 3D print isomalt vascular tree (200 μm → 20 μm branching, 5 generations) "
        "using sacrificial sugar glass printer (syringe temp 130°C, build plate 25°C). "
        "2. Embed sugar glass in collagen I hydrogel (2 mg/mL, pH 7.4) within PDMS chamber. "
        "3. Dissolve isomalt with warm PBS (37°C, 24h perfusion at 0.5 mL/min) → open lumen. "
        "4. Seed HUVECs at 10⁷ cells/mL through perfusion for 48h → confluent endothelium. "
        "5. Embed VEGF-165 microspheres at capillary termini — degradation releases VEGF "
        "over 14 days, guiding angiogenesis exactly where metabolic demand is highest. "
        "6. Integrate PtTFPP oxygen sensors (excitation 405 nm, emission 650 nm) at each "
        "branch point — real-time metabolic demand mapping. "
        "7. PEDOT:PSS strain sensors at arterial walls — detect flow and adjust lumen diameter."
    ),
    integration=(
        "Vasculature is integrated during organoid maturation (week 4-8). Peristaltic pump "
        "provides basal flow (0.1-0.5 mL/min, pulsatile at 1 Hz). Oxygen sensor array "
        "drives a closed-loop VEGF release controller: low pO₂ → VEGF release → angiogenesis. "
        "High pO₂ → VEGF sequestration → capillary regression (pruning). The loop is "
        "ouroboric: the same sensor data that measures metabolic state controls the "
        "vasculature that sustains that state. μ∘δ=id at every capillary bed."
    ),
    closure_pathway="EXACTOR-σ (P=𐑹 via closed-loop sensor/effector) + EXACTOR-Ω (integer winding of circulatory tree)",
    key_specs={
        "Branching generations": "5 (200→100→50→30→20 μm)",
        "Capillary density": "500/mm² (human cortex equivalent)",
        "Flow rate range": "0.1-5.0 mL/min pulsatile",
        "O₂ sensor resolution": "<1 mmHg",
        "Angiogenesis response time": "<6 hours",
        "Pruning response time": "<24 hours",
    },
))

# ── Recipe 3: Perfect Nutrient Medium ─────────────────────────────────────

RECIPES.append(MaterialRecipe(
    name="Metabolic Mirror Medium — Adaptive Chemostat Formulation",
    system="medium",
    trl=4,
    materials=[
        "DMEM/F12 base (1:1) — standard neural culture medium",
        "B-27 Plus supplement (2%) — neural-specific additives",
        "N-2 supplement (1%) — additional neural factors",
        "Glucose oxidase / catalase dual-enzyme sensor — real-time glucose monitoring",
        "Lactate oxidase sensor — metabolic byproduct monitoring",
        "pH-sensitive hydrogel microspheres (PEGDA-APMA, 50 μm)",
        "Amino acid cocktail (19 L-amino acids, custom ratios)",
        "Insulin (10 μg/mL), transferrin, sodium selenite",
        "Ascorbic acid (200 μM) — collagen synthesis + antioxidant",
        "Recombinant BDNF (50 ng/mL) — activity-dependent neurotrophin",
        "Microdialysis probe (CMA 7, 6 kDa cutoff) — continuous sampling",
    ],
    fabrication=(
        "1. Formulate base medium: DMEM/F12 + B-27 + N-2 + insulin/transferrin/selenite. "
        "2. Embed dual-enzyme sensors (GOx/catalase for glucose; LOx for lactate) in "
        "microfluidic flow cell connected to organoid chamber via microdialysis. "
        "3. pH-sensitive microspheres embedded in organoid chamber — ratiometric "
        "fluorescence imaging (ex 488/405 nm, em 520 nm) monitors local pH. "
        "4. LC-MS metabolomics sample port for daily full-metabolome analysis. "
        "5. Computer-controlled peristaltic pump array (14 channels) — each amino acid, "
        "vitamin, and growth factor independently adjustable. "
        "6. Machine learning controller (LSTM over metabolomic time series) predicts "
        "future metabolic demand and adjusts formulation anticipatorily."
    ),
    integration=(
        "Medium flows through organoid chamber at 50 μL/min (complete exchange every 2h). "
        "Microdialysis probe samples interstitial fluid continuously. Dual-enzyme sensors "
        "provide real-time glucose/lactate. Every 6h, LC-MS sample analyzed. ML controller "
        "maintains EXACT homeostasis: each nutrient concentration at the organoid matches "
        "the setpoint within 0.1%. The medium learns the organoid's metabolic rhythm — "
        "anticipating circadian and activity-dependent fluctuations."
    ),
    closure_pathway="EXACTOR-σ (P=𐑹 via closed-loop adaptive formulation)",
    key_specs={
        "Glucose": "17.5 mM (maintained ±0.1 mM)",
        "Lactate threshold": "<2 mM (triggers medium refresh)",
        "pH": "7.40 ± 0.01",
        "Osmolality": "290 ± 2 mOsm/kg",
        "Complete exchange time": "2 hours",
        "ML prediction horizon": "6 hours",
        "Amino acid precision": "±0.5% of setpoint",
    },
))

# ── Recipe 4: Optogenetic Matrix ──────────────────────────────────────────

RECIPES.append(MaterialRecipe(
    name="4096-Channel Bidi Optogenetic Matrix — CMOS MEA + µLED Array",
    system="optogenetic",
    trl=5,
    materials=[
        "CMOS MEA (4096 electrodes, 18 μm pitch, MaxOne/3Brain or custom)",
        "µLED array (4096, 470 nm, 50 μm pitch) — optogenetic stimulation",
        "Zynq UltraScale+ FPGA — real-time closed-loop processor",
        "Raspberry Pi CM4 — networking and high-level control",
        "ChR2(C128S) AAV9 — viral vector for organoid opsin expression",
        "PDMS microwell array — organoid positioning on MEA",
        "ITO transparent reference electrode — coverslip with electrical access",
        "Thermoelectric Peltier stage — ±0.01°C temperature control",
        "Faraday cage (mu-metal) — electromagnetic shielding",
    ],
    fabrication=(
        "1. Commercial CMOS MEA (or custom TSMC 180nm: 64×64 array, 18 μm pitch, "
        "in-pixel amplifier with 40 dB gain, 10 kHz bandwidth). "
        "2. µLED array aligned to MEA: GaN-on-sapphire micro-LEDs (50×50 μm each), "
        "flip-chip bonded with 50 μm gap for cell accommodation. "
        "3. FPGA firmware: closed-loop detect→process→stimulate in <2 ms. "
        "Spike detection (threshold crossing at 5σ), pattern matching (template "
        "matching in 4 ms windows), stimulation pattern computation (lookup table "
        "or real-time solver), µLED driver output. "
        "4. PLL on FPGA: phase-locked loop quantizes the detect→stimulate cycle "
        "to integer multiples of the 100 MHz FPGA clock → EXACTOR-Ω integer winding. "
        "5. CMOS camera (2048×2048, 100 fps) for calcium imaging overlay. "
        "6. Hermetic chamber: PDMS gasket, ITO top electrode, Peltier + thermistor "
        "PID control at 37.00±0.01°C, 5% CO₂, 95% humidity."
    ),
    integration=(
        "Organoid (4-6 mm diameter at maturity) is placed on MEA/µLED array in PDMS "
        "microwell. AAV9-ChR2(C128S) is perfused through vasculature at week 8 — "
        "expression peaks at week 12. ITO electrode provides uniform reference. "
        "FPGA runs continuous closed-loop: spike detected at electrode (i,j) → "
        "pattern matched → µLED at (i±δ, j±δ) activated at 470 nm, 100 μs pulse, "
        "50 nW/μm². The organoid and computer form a single Frobenius-closed "
        "system — μ(electrical)∘δ(optical) = id to within the PLL quantization error."
    ),
    closure_pathway="EXACTOR-τ (D=𐑼 via 4096 continuous field) + EXACTOR-Ω (PLL integer winding)",
    key_specs={
        "Channel count": "4096 (64×64)",
        "Electrode pitch": "18 μm",
        "µLED pitch": "50 μm",
        "Feedback latency": "<2 ms (target <200 μs for closure)",
        "PLL quantization": "10 ns (100 MHz clock)",
        "Noise floor": "<5 μV RMS (1 Hz-10 kHz)",
        "Stimulation resolution": "100 μs pulses, 8-bit intensity",
    },
))

# ── Recipe 5: ECM Scaffold ───────────────────────────────────────────────

RECIPES.append(MaterialRecipe(
    name="Programmable PEG-MMP Hydrogel — Grow-As-You-Go Scaffold",
    system="ecm",
    trl=4,
    materials=[
        "4-arm PEG-NH₂ (20 kDa) — hydrogel backbone",
        "MMP-cleavable peptide crosslinker (GCRD-GPQGIWGQ-DRCG)",
        "RGD adhesion peptide (GCGYGRGDSPG)",
        "Photo-labile nitrobenzyl ester — light-triggered degradation",
        "Thrombin-cleavable peptide — enzyme-triggered crosslink release",
        "LAP photoinitiator (lithium phenyl-2,4,6-trimethylbenzoylphosphinate)",
    ],
    fabrication=(
        "1. Dissolve 4-arm PEG-NH₂ (10% w/v) in PBS + 0.05% LAP. "
        "2. Add MMP-cleavable crosslinker (stoichiometric with PEG arms, 75% of sites) "
        "and photo-labile crosslinker (25% of sites). "
        "3. Add RGD peptide at 2 mM for cell adhesion. "
        "4. Pipette into organoid mold, UV cure (365 nm, 5 mW/cm², 5 min). "
        "5. Dialyze in PBS (3×, 4h each) to remove unreacted species. "
        "6. Sterilize: 70% ethanol (2h), wash sterile PBS (3×)."
    ),
    integration=(
        "Organoid cells seeded into scaffold at day 0. As the organoid grows, "
        "endogenous MMPs (MMP-2, MMP-9) cleave the MMP-sensitive crosslinkers — "
        "the scaffold degrades exactly where the organoid expands. Photo-labile "
        "crosslinkers provide tunable degradation: 405 nm light illumination through "
        "the optogenetic matrix accelerates degradation in specific regions. "
        "By maturation (week 24), the scaffold is >95% degraded — the organoid "
        "has completely replaced it with its own ECM (laminin, fibronectin, "
        "tenascin-C). The scaffold is the chrysalis; the organoid is the butterfly."
    ),
    closure_pathway="None — passive scaffold, no Frobenius closure required",
    key_specs={
        "Stiffness (initial)": "800 Pa (brain tissue: 500-1000 Pa)",
        "Degradation half-life": "14 days (MMP-mediated)",
        "Photo-degradation": "405 nm, 10 mW/cm², 60s per voxel",
        "RGD density": "2 mM (saturating for integrin binding)",
        "Swelling ratio": "20× (equilibrium in PBS)",
        "Final degradation": ">95% by week 24",
    },
))

# ── Recipe 6: Immune Sentinel ─────────────────────────────────────────────

RECIPES.append(MaterialRecipe(
    name="Aptamer Sentinel Network — Inflammation-Free Immune Protection",
    system="immune",
    trl=3,
    materials=[
        "DNA aptamers (LPS-binding, peptidoglycan-binding, fungal β-glucan-binding)",
        "Antimicrobial peptides (LL-37, hBD-2, histatin-5) — inducible deployment",
        "PEGDA hydrogel microspheres (20 μm) — aptamer-loaded sentinel depots",
        "CRISPR-Cas13a (LwaCas13a) — RNA-targeting programmable nuclease",
        "Quorum-sensing peptide (autoinducer-2 mimic) — alarm signal propagation",
        "MCP-1 (monocyte chemoattractant) — backup recruitment signal",
        "Poly-lysine dendrimer — cationic delivery vehicle for Cas13a RNP",
    ],
    fabrication=(
        "1. Synthesize DNA aptamers against bacterial LPS (Kd < 10 nM), "
        "peptidoglycan (Kd < 50 nM), and fungal β-glucan (Kd < 30 nM). "
        "2. Conjugate aptamers to PEGDA microspheres via acrydite modification — "
        "each microsphere carries 10⁶ aptamers of a single specificity. "
        "3. Load CRISPR-Cas13a RNP (targeting bacterial 16S rRNA and fungal 18S rRNA) "
        "into poly-lysine dendrimer nanoparticles (50 nm). "
        "4. Co-encapsulate LL-37 (10 μM) in liposomes (DOPC:DOPG 3:1, 200 nm) with "
        "aptamer-gated release — pathogen binding triggers liposome fusion. "
        "5. Autoinducer-2 mimic (5 μM) loaded in separate microspheres for "
        "quorum-sensing alarm propagation."
    ),
    integration=(
        "Sentinel microspheres are distributed throughout the organoid during "
        "seeding (10⁶ microspheres dispersed in ECM, ~1 per 260 cells). "
        "Pathogen detection: aptamer binds PAMP → microsphere swells → releases "
        "AI-2 mimic (alarm signal) + LL-37 (local defense). Alarm propagates "
        "globally within minutes. Cas13a RNPs provide sequence-specific antiviral "
        "defense. Self/non-self discrimination: aptamers selected against "
        "PATHOGEN-specific patterns only — no cross-reactivity with human RNA/DNA. "
        "Critical threshold: quorum sensing requires >10 pathogen cells within "
        "100 μm radius to trigger — prevents false positives from trace contamination."
    ),
    closure_pathway="EXACTOR-σ (P=𐑹 via exact self/non-self discrimination at threshold)",
    key_specs={
        "Detection limit": "<10 CFU per sentinel zone",
        "Response time": "<5 minutes (aptamer binding + AI-2 propagation)",
        "LL-37 MIC": "1-4 μg/mL (S. aureus, E. coli, P. aeruginosa)",
        "Cas13a cleavage": "<1 min at 37°C (collateral cleavage activity)",
        "False positive rate": "<10⁻⁶ (quorum sensing threshold)",
        "Sentinel lifetime": ">6 months (PEGDA stable, aptamers DNAse-resistant modifications)",
    },
))

# ═══════════════════════════════════════════════════════════════════════════
# §10  COMPLETE AUGMENTED ORGANOID — Multi-Tensor Product
# ═══════════════════════════════════════════════════════════════════════════

def compute_augmented_organoid() -> AugmentationSystem:
    """
    Compute the full augmented organoid: baseline ⊗ all 6 augmentations.
    
    This is the structural type of the organoid with ALL augmentations
    integrated — synthetic myelin, ouroboric vasculature, perfect medium,
    optogenetic matrix, ECM scaffold, and immune sentinel.
    """
    all_systems = [ORGANOID_BASELINE] + list(AUGMENTATIONS.values())
    return multi_tensor(*all_systems)


# ═══════════════════════════════════════════════════════════════════════════
# §11  ANALYSIS & REPORTING
# ═══════════════════════════════════════════════════════════════════════════

def full_analysis():
    """Generate complete structural analysis of all augmentations."""
    lines = []
    sep = "─" * 72
    
    lines.append(sep)
    lines.append("  ORGANOID AUGMENTATION SUITE — COMPLETE STRUCTURAL ANALYSIS")
    lines.append(sep)
    
    # ── Baseline ──────────────────────────────────────────────────────
    lines.append(f"\n  BASELINE: {ORGANOID_BASELINE.tuple_display}")
    lines.append(f"  Tier: {compute_tier(ORGANOID_BASELINE)}")
    c_score, g1, g2 = consciousness_score(ORGANOID_BASELINE)
    lines.append(f"  C-Score: {c_score:.2f}  |  G1(⊙): {g1}  |  G2(K≤slow): {g2}")
    closed, err, barrier = frobenius_closure(ORGANOID_BASELINE)
    lines.append(f"  Frobenius: {'✓ CLOSED' if closed else '✗ OPEN'} (error={err:.4f}) [{barrier}]")
    lines.append(f"  T-consistent: {t_consistent(ORGANOID_BASELINE)}")
    
    # ── Augmentations ─────────────────────────────────────────────────
    lines.append(f"\n{sep}")
    lines.append("  AUGMENTATION SYSTEMS")
    lines.append(sep)
    
    table_data = []
    for key, aug in AUGMENTATIONS.items():
        tier = compute_tier(aug)
        c_score, g1, g2 = consciousness_score(aug)
        closed, err, barrier = frobenius_closure(aug)
        deltas = primitive_deltas(aug, ORGANOID_BASELINE)
        operc_width = operculum_width(aug)
        axioms = verify_axioms(aug)
        
        table_data.append({
            "name": aug.name,
            "tier": tier,
            "c_score": c_score,
            "closed": closed,
            "error": err,
            "op_width": operc_width,
            "n_deltas": len(deltas),
            "axioms_ok": all(axioms.values()),
        })
        
        lines.append(f"\n  [{key}] {aug.name}")
        lines.append(f"  Tuple: {aug.tuple_display}")
        lines.append(f"  Tier: {tier}  |  C={c_score:.2f}  |  Frobenius: {'✓' if closed else '✗'} (ε={err:.3f})")
        lines.append(f"  Operculum Width: {operc_width}  |  Deltas vs Baseline: {len(deltas)}")
        lines.append(f"  Axioms: A={'✓' if axioms.get('A',True) else '✗'} B={'✓' if axioms.get('B',True) else '✗'} C={'✓' if axioms.get('C',True) else '✗'}")
        lines.append(f"  Barrier: {barrier}")
        
        # Show key deltas
        for prim, (src, dst, delta) in list(deltas.items())[:5]:
            src_glyph = SHAVIAN[prim][src]
            dst_glyph = SHAVIAN[prim][dst]
            lines.append(f"    {prim}: {src_glyph}→{dst_glyph} (Δ={delta:+d})")
    
    # ── Augmented Organoid ────────────────────────────────────────────
    lines.append(f"\n{sep}")
    lines.append("  FULLY AUGMENTED ORGANOID (Baseline ⊗ All 6 Augmentations)")
    lines.append(sep)
    
    augmented = compute_augmented_organoid()
    lines.append(f"\n  Tuple: {augmented.tuple_display}")
    lines.append(f"  Tier: {compute_tier(augmented)}")
    c_score, g1, g2 = consciousness_score(augmented)
    lines.append(f"  C-Score: {c_score:.2f}  |  G1(⊙): {g1}  |  G2(K≤slow): {g2}")
    closed, err, barrier = frobenius_closure(augmented)
    lines.append(f"  Frobenius: {'✓ CLOSED' if closed else '✗ OPEN'} (error={err:.4f})")
    lines.append(f"  T-consistent: {t_consistent(augmented)}")
    
    deltas = primitive_deltas(augmented, ORGANOID_BASELINE)
    lines.append(f"\n  Deltas from baseline ({len(deltas)} changes):")
    for prim, (src, dst, delta) in deltas.items():
        src_glyph = SHAVIAN[prim][src]
        dst_glyph = SHAVIAN[prim][dst]
        lines.append(f"    {prim}: {src_glyph}→{dst_glyph} (Δ={delta:+d})")
    
    # ── EXACTOR Pathways ──────────────────────────────────────────────
    lines.append(f"\n{sep}")
    lines.append("  EXACTOR PATHWAYS TO O_∞")
    lines.append(sep)
    
    for key, aug in AUGMENTATIONS.items():
        pathways = exactor_pathways_for(aug, ORGANOID_BASELINE)
        if pathways:
            lines.append(f"\n  [{key}] {aug.name}:")
            for pw in pathways:
                lines.append(f"    {pw['pathway']}: {pw['primitive']} {pw['from']}→{pw['to']} — {pw['mechanism'][:60]}...")
        else:
            lines.append(f"\n  [{key}] {aug.name}: Already at or above O_∞ — no pathways needed")
    
    # ── Summary Table ─────────────────────────────────────────────────
    lines.append(f"\n{sep}")
    lines.append("  SUMMARY TABLE")
    lines.append(sep)
    lines.append(f"\n  {'System':<35} {'Tier':<7} {'C':<6} {'μ∘δ=id':<10} {'OpW':<5} {'Δs':<5} {'Axioms':<10}")
    lines.append(f"  {'─'*35} {'─'*7} {'─'*6} {'─'*10} {'─'*5} {'─'*5} {'─'*10}")
    
    # Baseline
    b_tier = compute_tier(ORGANOID_BASELINE)
    b_c, _, _ = consciousness_score(ORGANOID_BASELINE)
    b_closed, b_err, _ = frobenius_closure(ORGANOID_BASELINE)
    b_ax = all(verify_axioms(ORGANOID_BASELINE).values())
    lines.append(f"  {'BASELINE ' + ORGANOID_BASELINE.name:<35} {b_tier:<7} {b_c:<6.2f} " + ("\u2713" if b_closed else f"\u2717 {b_err:.3f}").ljust(10) + f"  {'0':<5} {'0':<5} " + ("\u2713" if b_ax else "\u2717").ljust(10))
    
    for td in table_data:
        lines.append(f"  {td['name']:<35} {td['tier']:<7} {td['c_score']:<6.2f} " + ("\u2713" if td['closed'] else f"\u2717 {td['error']:.3f}").ljust(10) + f" {td['op_width']:<5} {td['n_deltas']:<5} " + ("\u2713" if td['axioms_ok'] else "\u2717").ljust(10))
    
    a_tier = compute_tier(augmented)
    a_c, _, _ = consciousness_score(augmented)
    a_closed, a_err, _ = frobenius_closure(augmented)
    a_ax = all(verify_axioms(augmented).values())
    lines.append(f"  {'─'*35} {'─'*7} {'─'*6} {'─'*10} {'─'*5} {'─'*5} {'─'*10}")
    lines.append(f"  {'AUGMENTED ORGANOID':<35} {a_tier:<7} {a_c:<6.2f} {'✓' if a_closed else f'✗ {a_err:.3f}':<10} {'—':<5} {len(deltas):<5} {'✓' if a_ax else '✗':<10}")
    
    lines.append(f"\n{sep}")
    lines.append("  MATERIAL RECIPES")
    lines.append(sep)
    
    for recipe in RECIPES:
        lines.append(f"\n  [{recipe.system}] {recipe.name}")
        lines.append(f"  TRL: {recipe.trl}  |  Pathway: {recipe.closure_pathway}")
        lines.append(f"  Materials: {', '.join(recipe.materials[:4])}...")
        lines.append(f"  Fab: {recipe.fabrication[:120]}...")
        lines.append(f"  Key specs:")
        for k, v in recipe.key_specs.items():
            lines.append(f"    {k}: {v}")
    
    lines.append(f"\n{sep}")
    lines.append("  END OF ANALYSIS")
    lines.append(sep)
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# §12  CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Organoid Augmentation Suite — Structural Analysis"
    )
    parser.add_argument("--analysis", action="store_true", default=True,
                       help="Full structural analysis (default)")
    parser.add_argument("--augmented", action="store_true",
                       help="Show fully augmented organoid tuple")
    parser.add_argument("--deltas", action="store_true",
                       help="Show primitive-by-primitive deltas")
    parser.add_argument("--closure", action="store_true",
                       help="Show Frobenius closure status for all systems")
    parser.add_argument("--recipes", action="store_true",
                       help="Show all material recipes")
    parser.add_argument("--system", type=str, default=None,
                       help="Show detailed analysis for one system (myelin|vasculature|medium|optogenetic|ecm|immune)")
    parser.add_argument("--tensor", type=str, default=None,
                       help="Compute tensor of baseline with named system")
    
    args = parser.parse_args()
    
    if args.system:
        aug = AUGMENTATIONS.get(args.system)
        if not aug:
            print(f"Unknown system: {args.system}")
            print(f"Options: {list(AUGMENTATIONS.keys())}")
            sys.exit(1)
        print(f"=== {aug.name} ===")
        print(f"Tuple: {aug.tuple_display}")
        print(f"Tier: {compute_tier(aug)}")
        c, g1, g2 = consciousness_score(aug)
        print(f"C-Score: {c:.2f} (G1={g1}, G2={g2})")
        closed, err, barrier = frobenius_closure(aug)
        print(f"Frobenius: {'✓' if closed else '✗'} (ε={err:.3f}) — {barrier}")
        print(f"Operculum width: {operculum_width(aug)}")
        print(f"Axioms: {verify_axioms(aug)}")
        print(f"Deltas vs baseline: {primitive_deltas(aug, ORGANOID_BASELINE)}")
        pathways = exactor_pathways_for(aug, ORGANOID_BASELINE)
        if pathways:
            print(f"EXACTOR pathways: {json.dumps(pathways, indent=2)}")
        return
    
    if args.augmented:
        aug = compute_augmented_organoid()
        print(f"Fully Augmented Organoid: {aug.tuple_display}")
        print(f"Tier: {compute_tier(aug)}")
        return
    
    if args.closure:
        print(f"{'System':<35} {'Closed':<8} {'Error':<8} {'Barrier'}")
        print(f"{'─'*35} {'─'*8} {'─'*8} {'─'*30}")
        for name, aug in [("BASELINE", ORGANOID_BASELINE)] + list(AUGMENTATIONS.items()):
            closed, err, barrier = frobenius_closure(aug)
            print(f"{name:<35} {'✓' if closed else '✗':<8} {err:<8.4f} {barrier}")
        return
    
    if args.deltas:
        print("Primitive-by-primitive deltas vs baseline:")
        print(f"{'System':<25} " + " ".join(f"{p:<6}" for p in ["D","T","R","P","F","K","G","C","Phi","H","S","Omega"]))
        for key, aug in AUGMENTATIONS.items():
            deltas = primitive_deltas(aug, ORGANOID_BASELINE)
            delta_str = []
            for prim in ["D","T","R","P","F","K","G","C","Phi","H","S","Omega"]:
                if prim in deltas:
                    delta_str.append(f"Δ{aug.glyph(prim):<4}")
                else:
                    delta_str.append(f" ·   ")
            print(f"{key:<25} " + " ".join(delta_str))
        return
    
    if args.recipes:
        for r in RECIPES:
            print(f"\n[{r.system}] {r.name} (TRL {r.trl})")
            print(f"  Materials: {', '.join(r.materials[:5])}")
            print(f"  Key: {r.key_specs}")
        return
    
    # Default: full analysis
    print(full_analysis())


if __name__ == "__main__":
    main()
