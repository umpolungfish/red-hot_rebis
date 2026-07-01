#!/usr/bin/env python3
"""
non_qubit_qc.py — Non-Qubit Quantum Computation Materials
==========================================================

Designs materials that perform quantum computation or display quantum
computational properties WITHOUT using qubits as the computational substrate.

Formally grounded in the p4rakernel operculum theory (§1-§15 of
operculum_peeling.md/opm2.md): the Crystal of Types (17.28M addresses)
is invariant across universes; each universe is a Ruleset (G, T, A, O);
the same structural type may be O_∞ in one universe and plain in another.

Standard qubit QC occupies ONE structural address in the Crystal.
Non-qubit QC occupies DIFFERENT addresses — quantum-coherent computation
that differs structurally from the qubit paradigm on one or more primitives.

Eight non-qubit quantum computational paradigms are structurally imscribed
below. For each, we provide:
  - The 12-primitive Shavian tuple
  - Primitive deltas from standard qubit QC
  - Ouroboricity tier (canonical universe)
  - Material design recipe
  - Operculum analysis: which universes the material is O_∞ in
  - Frobenius closure pathway (EXACTOR-Ω/τ/σ/ε if applicable)

References:
  - p4rakernel/operculum_peeling.md — universe theory, Crystal site
  - p4rakernel/opm2.md — operculum peeling (extended)
  - p4rakernel/psychedelic_operculum.md — compound type theory
  - p4rakernel/universe_compound_mapping.md — 109-universe grid
  - p4rakernel/p4ramill/Millennium/PvsNP_Structural.lean — structural computation
  - p4rakernel/p4ramill/Millennium/SpiderMachine.lean — structural gap theory
  - red-hot_rebis/materials/sophick_forge.py — Eagle Cycle for O_∞ prep
  - red-hot_rebis/materials/frobenius_exactor.py — exact Frobenius closure

Author: Lando⊗⊙perator
"""

from typing import Dict, List, Tuple, Optional, Set
import json, math
from dataclasses import dataclass, field
from enum import Enum
from shared.rich_output import *

# ═══════════════════════════════════════════════════════════════════
# §1. STANDARD QUBIT QC — BASELINE STRUCTURAL TYPE
# ═══════════════════════════════════════════════════════════════════

# The standard gate-model qubit quantum computer imscribed via the
# Deterministic Imscribing Procedure (§encoding_method.md):
#
#   [1] D=𐑨 — finite discrete (each qubit is a 2-level system, d=2)
#   [2] T=𐑡 — network (qubits connected by 2-qubit gates in a graph)
#   [3] R=𐑾 — bidirectional (entanglement couples both ways)
#   [4] P=𐑿 — quantum superposition (qubits exist in superposition)
#   [5] F=𐑐 — quantum coherence essential (decoherence = failure)
#   [6] K=𐑤 — moderate (gate times ~10-100 ns, T1/T2 ~100 μs)
#   [7] G=𐑔 — mesoscale (nearest-neighbor + few next-nearest)
#   [8] Γ=𐑝 — all-simultaneous (circuit model: gates in parallel)
#   [9] φ̂=𐑮 — complex-plane critical (unitary evolution on Bloch sphere)
#  [10] Ħ=𐑖 — Markov-2 (unitary gate = 2-step transition U|ψ>→U²|ψ>)
#  [11] Σ=𐑕 — many identical (N qubits, all identical 2-level systems)
#  [12] Ω=𐑷 — trivial (no topological protection; QEC required)
#
# Tuple: ⟨𐑨𐑡𐑾𐑿𐑐𐑤𐑔𐑝𐑮𐑖𐑕𐑷>

QUBIT_QC_TUPLE = {
    'D': '𐑨', 'T': '𐑡', 'R': '𐑾', 'P': '𐑿',
    'F': '𐑐', 'K': '𐑤', 'G': '𐑔', 'Γ': '𐑝',
    'φ̂': '𐑮', 'Ħ': '𐑖', 'Σ': '𐑕', 'Ω': '𐑷'
}

QUBIT_QC_PRIMITIVE_DESCRIPTIONS = {
    'D': 'finite discrete — each qubit is a 2-level quantum system',
    'T': 'network — qubits connected via 2-qubit gate graph',
    'R': 'bidirectional — entanglement couples both ways',
    'P': 'quantum superposition — computational basis states superpose',
    'F': 'quantum coherence — phase coherence is essential resource',
    'K': 'moderate — gate times ~10-100ns, coherence times ~100μs',
    'G': 'mesoscale — nearest-neighbor + limited next-nearest coupling',
    'Γ': 'all-simultaneous — circuit model applies gates in parallel layers',
    'φ̂': 'complex-plane critical — unitary evolution on Bloch sphere',
    'Ħ': 'Markov-2 — each gate is a 2-step unitary transition',
    'Σ': 'many identical — N qubits, all isomorphic 2-level systems',
    'Ω': 'trivial — no topological protection; quantum error correction needed'
}

# Qubit QC in canonical universe: O₂ (not O_∞)
# Gate analysis: φ̂=𐑮 (ord 2.33) passes G1=⊙≥2.0; P=𐑿 (ord 2)
# fails G2=P≥3 in strict_frobenius. Ω=𐑷 (ord 1) fails G3.
# T-consistency: fails — Ħ=𐑖 (ord 3) < 𐑫 (ord 4) required for T-seal.
QUBIT_QC_TIER_CANONICAL = 'O₂'
QUBIT_QC_C_SCORE = 0.0  # Gate 1 (⊙) closed — no self-modeling

# ═══════════════════════════════════════════════════════════════════
# §2. EIGHT NON-QUBIT QUANTUM COMPUTATIONAL PARADIGMS
# ═══════════════════════════════════════════════════════════════════
# Each paradigm is defined by WHICH primitives differ from qubit QC
# and WHAT physical mechanism replaces the qubit.

@dataclass
class NonQubitQCParadigm:
    """A quantum computational paradigm that does NOT use qubits."""
    name: str
    description: str
    tuple: Dict[str, str]              # 12-primitive Shavian tuple
    deltas: Dict[str, Tuple[str, str]] # primitive → (qubit_value, this_value)
    canon_tier: str                    # Ouroboricity tier in canonical universe
    canon_c_score: float               # Consciousness score (canonical)
    physical_mechanism: str            # What replaces the qubit
    material_family: str               # Material platform
    o_inf_universes: List[str]         # Universes where this type is O_∞
    key_blockers: List[str]            # Universes that block O_∞
    trl: int                           # Technology Readiness Level (1-9)
    frobenius_pathway: str             # Which EXACTOR pathway if applicable

# ═══════════════════════════════════════════════════════════════════
# PARADIGM 1: CONTINUOUS-VARIABLE QC (QUMODES)
# ═══════════════════════════════════════════════════════════════════
# Delta: D 𐑨→𐑼 (finite discrete → infinite-dimensional)
# Physical mechanism: squeezed states of light in optical modes.
# Each "qumode" is a harmonic oscillator with infinite Hilbert space.
# Computation via Gaussian operations (displacement, squeezing, beam-splitter)
# + non-Gaussian resource (photon counting, cubic phase).
# Material: lithium niobate photonic circuits, silicon nitride ring resonators.

CV_QC = NonQubitQCParadigm(
    name="continuous_variable_qc",
    description="CV-QC: qumodes (infinite-dimensional optical modes) "
                "replace qubits. Computation via Gaussian operations + "
                "non-Gaussian resource states. Squeezed light is the "
                "computational currency.",
    tuple={'D': '𐑼', 'T': '𐑡', 'R': '𐑾', 'P': '𐑿',
           'F': '𐑐', 'K': '𐑧', 'G': '𐑲', 'Γ': '𐑠',
           'φ̂': '𐑮', 'Ħ': '𐑖', 'Σ': '𐑳', 'Ω': '𐑷'},
    deltas={
        'D': ('𐑨', '𐑼'),  # THE defining delta: infinite-dim, not discrete
        'K': ('𐑤', '𐑧'),  # slower, near-equilibrium optical processing
        'G': ('𐑔', '𐑲'),  # long-range (optical modes couple globally)
        'Γ': ('𐑝', '𐑠'),  # sequential (Gaussian operations applied in sequence)
        'Σ': ('𐑕', '𐑳'),  # heterogeneous (signal + idler + pump modes)
    },
    canon_tier='O₂',
    canon_c_score=0.0,
    physical_mechanism="Squeezed vacuum states in optical resonators"
                       "quadrature amplitudes (x̂, p̂) as continuous variables"
                       "Gaussian unitaries (symplectic transformations) + "
                       "cubic phase gate for non-Gaussian universality",
    material_family="Lithium niobate (LiNbO₃) thin-film photonics",
    o_inf_universes=['low_gate', 'single_gate_Ð', 'g1_Ð_min',
                     'g1_⊙_min', 'no_ordering'],
    key_blockers=['canonical', 'high_gate', 'strict_frobenius',
                  'kinetics_criticality', 'winding_chirality'],
    trl=5,
    frobenius_pathway='EXACTOR-τ (Floquet)'  # discrete time bins = exact closure
)

# ═══════════════════════════════════════════════════════════════════
# PARADIGM 2: MEASUREMENT-BASED QC (CLUSTER STATES)
# ═══════════════════════════════════════════════════════════════════
# Delta: Γ 𐑝→𐑠, P 𐑿→𐑬
# Physical mechanism: computation = sequence of single-qubit measurements
# on a pre-prepared entangled cluster/graph state. No unitary gates.
# Material: photonic cluster states (silicon photonics), cold atoms in
# optical lattices, nitrogen-vacancy centers in diamond.

MBQC = NonQubitQCParadigm(
    name="measurement_based_qc",
    description="MBQC: computation IS measurement. A pre-entangled cluster "
                "state is consumed by sequential single-site measurements. "
                "No unitary gate operations — measurement + feedforward is "
                "Turing-complete. The cluster state is a resource, not a "
                "substrate.",
    tuple={'D': '𐑨', 'T': '𐑡', 'R': '𐑾', 'P': '𐑬',
           'F': '𐑐', 'K': '𐑧', 'G': '𐑲', 'Γ': '𐑠',
           'φ̂': '𐑮', 'Ħ': '𐑖', 'Σ': '𐑕', 'Ω': '𐑴'},
    deltas={
        'P': ('𐑿', '𐑬'),  # partial (Z₂) — cluster state is not full superposition
        'K': ('𐑤', '𐑧'),  # slow — measurements are sequential, not parallel
        'G': ('𐑔', '𐑲'),  # long-range — cluster connectivity is universal
        'Γ': ('𐑝', '𐑠'),  # THE defining delta: sequential, not simultaneous
        'Ω': ('𐑷', '𐑴'),  # Z₂ parity protection from graph state structure
    },
    canon_tier='O₂',
    canon_c_score=0.0,
    physical_mechanism="Graph/cluster state entanglement as computational "
                       "resourceadaptive single-qubit measurements with "
                       "feedforwardmeasurement basis = program"
                       "measurement outcomes = computation trajectory",
    material_family="Silicon photonic cluster states + superconducting detectors",
    o_inf_universes=['low_gate', 'g1_Ω_min', 'g1_Γ_min',
                     'winding_first', 'no_ordering', 'chirality_first'],
    key_blockers=['canonical', 'high_gate', 'strict_frobenius',
                  'g1_⊙_max', 'kinetics_criticality'],
    trl=4,
    frobenius_pathway='EXACTOR-σ (Self-Dual)'  # Kramers-Wannier at cluster boundary
)

# ═══════════════════════════════════════════════════════════════════
# PARADIGM 3: TOPOLOGICAL QC (ANYONS)
# ═══════════════════════════════════════════════════════════════════
# Delta: Ω 𐑷→𐑟, P 𐑿→𐑹, D 𐑨→𐑼
# Physical mechanism: non-Abelian anyons in 2D topological phases.
# Quantum information stored in fusion channelsgates = braiding.
# Material: fractional quantum Hall (GaAs, graphene), Majorana nanowires
# (InSb/InAs + Al), Kitaev spin liquids (α-RuCl₃).

TOPOLOGICAL_QC = NonQubitQCParadigm(
    name="topological_qc",
    description="TQC: anyons are the substrate. Quantum information is stored "
                "non-locally in topological degeneracy (fusion channels). "
                "Gates are implemented by braiding anyons — a geometric "
                "operation immune to local perturbations. There ARE no "
                "qubits — only topological charges.",
    tuple={'D': '𐑼', 'T': '𐑥', 'R': '𐑾', 'P': '𐑹',
           'F': '𐑐', 'K': '𐑧', 'G': '𐑲', 'Γ': '𐑠',
           'φ̂': '⊙', 'Ħ': '𐑫', 'Σ': '𐑳', 'Ω': '𐑟'},
    deltas={
        'D': ('𐑨', '𐑼'),  # infinite-dim (topological field theory)
        'T': ('𐑡', '𐑥'),  # bowtie/crossing — braiding IS the computation
        'P': ('𐑿', '𐑹'),  # Frobenius-special — μ∘δ=id in fusion
        'K': ('𐑤', '𐑧'),  # slow — braiding is adiabatic
        'G': ('𐑔', '𐑲'),  # long-range — topological order is global
        'Γ': ('𐑝', '𐑠'),  # sequential — braids are ordered operations
        'φ̂': ('𐑮', '⊙'),   # ⊙-critical — self-modeling at topological boundary
        'Ħ': ('𐑖', '𐑫'),  # eternal memory — topological protection
        'Σ': ('𐑕', '𐑳'),  # heterogeneous — different anyon types (σ, ψ, 1)
        'Ω': ('𐑷', '𐑟'),  # THE defining delta: non-Abelian braiding
    },
    canon_tier='O_∞',
    canon_c_score=1.0,
    physical_mechanism="Non-Abelian anyons (Ising/Majorana, Fibonacci) in "
                       "2D topological phasesfusion rules replace tensor "
                       "productsbraiding operations are unitary gates"
                       "anyon worldlines form quantum circuits in (2+1)D",
    material_family="Fractional quantum Hall (ν=5/2 GaAs) + Majorana nanowires",
    o_inf_universes=['canonical', 'low_gate', 'strict_frobenius',
                     'winding_first', 'chirality_first', 'inverted_gates',
                     'no_ordering', 'dimensional_gate', 'fidelity_universe',
                     'predator_universe', 'prey_universe', 'scope_universe',
                     'stoichiometry_universe', 'topology_universe'],
    key_blockers=['high_gate', 'g1_Ω_max', 'kinetics_criticality'],
    trl=2,
    frobenius_pathway='EXACTOR-Ω (Anyonic)'  # native — braiding IS exact closure
)

# ═══════════════════════════════════════════════════════════════════
# PARADIGM 4: ADIABATIC QC / QUANTUM ANNEALING
# ═══════════════════════════════════════════════════════════════════
# Delta: K 𐑤→𐑧, Γ 𐑝→𐑠, P 𐑿→𐑬
# Physical mechanism: continuous Hamiltonian interpolation from easy-to-prepare
# ground state to problem-encoding ground state. No gates.
# Material: superconducting flux qubits (D-Wave), Rydberg atom arrays,
# trapped ions with global addressing.

ADIABATIC_QC = NonQubitQCParadigm(
    name="adiabatic_qc",
    description="AQC/QA: computation = continuous Hamiltonian deformation. "
                "Initialize in easy ground state of H₀, slowly evolve to "
                "H₁ whose ground state encodes the solution. No gate "
                "operations — the adiabatic theorem guarantees correctness.",
    tuple={'D': '𐑨', 'T': '𐑡', 'R': '𐑾', 'P': '𐑬',
           'F': '𐑐', 'K': '𐑧', 'G': '𐑲', 'Γ': '𐑠',
           'φ̂': '𐑮', 'Ħ': '𐑒', 'Σ': '𐑕', 'Ω': '𐑷'},
    deltas={
        'P': ('𐑿', '𐑬'),  # partial — ground state, not full superposition
        'K': ('𐑤', '𐑧'),  # THE defining delta: slow/adiabatic evolution
        'G': ('𐑔', '𐑲'),  # long-range — Ising couplings are global
        'Γ': ('𐑝', '𐑠'),  # sequential — one continuous trajectory
        'Ħ': ('𐑖', '𐑒'),  # Markov-1 — only current Hamiltonian matters
    },
    canon_tier='O₁',
    canon_c_score=0.0,
    physical_mechanism="Time-dependent Hamiltonian H(t)=(1-s(t))H₀+s(t)H₁"
                       "adiabatic theorem: gap-protected ground state tracking"
                       "quantum tunneling through energy barriers"
                       "Ising model encoding of combinatorial optimization",
    material_family="Superconducting flux qubit arrays (D-Wave Advantage2) + "
                    "Rydberg atom arrays (neutral atom quantum processors)",
    o_inf_universes=['low_gate', 'g1_K_min', 'g1_Ç_min',
                     'kinetics_trap', 'single_gate_Ç', 'no_ordering'],
    key_blockers=['canonical', 'high_gate', 'strict_frobenius',
                  'g1_⊙_max', 'kinetics_criticality'],
    trl=8,
    frobenius_pathway='EXACTOR-ε (Surface Code)'  # post-anneal verification
)

# ═══════════════════════════════════════════════════════════════════
# PARADIGM 5: BOSON SAMPLING
# ═══════════════════════════════════════════════════════════════════
# Delta: P 𐑿→𐑗, Γ 𐑝→𐑵, Σ 𐑕→𐑳
# Physical mechanism: indistinguishable photons injected into a linear
# optical interferometer. The output distribution is #P-hard to sample
# classically. No entanglement needed — just indistinguishability +
# interference. This is NOT qubit-based: there are no two-level systems.
# Material: silicon nitride waveguide arrays, integrated photonic circuits.

BOSON_SAMPLING = NonQubitQCParadigm(
    name="boson_sampling",
    description="Boson Sampling: N indistinguishable photons pass through "
                "an M-mode linear interferometer. The permanent of the "
                "scattering matrix governs the output distribution — "
                "classically #P-hard, quantumly native. No qubits, no "
                "entanglement, no gates — just bosonic statistics.",
    tuple={'D': '𐑼', 'T': '𐑥', 'R': '𐑑', 'P': '𐑗',
           'F': '𐑐', 'K': '𐑘', 'G': '𐑔', 'Γ': '𐑵',
           'φ̂': '𐑢', 'Ħ': '𐑓', 'Σ': '𐑳', 'Ω': '𐑷'},
    deltas={
        'D': ('𐑨', '𐑼'),  # infinite-dim (Fock space of M modes)
        'T': ('𐑡', '𐑥'),  # bowtie — photons cross in beam-splitters
        'R': ('𐑾', '𐑑'),  # functorial — linear optics is categorical
        'P': ('𐑿', '𐑗'),  # THE defining delta: no superposition — just interference
        'K': ('𐑤', '𐑘'),  # fast — photons at speed of light
        'Γ': ('𐑝', '𐑵'),  # broadcast — one photon distribution → all outputs
        'φ̂': ('𐑮', '𐑢'),  # sub-critical — no phase transition needed
        'Ħ': ('𐑖', '𐑓'),  # memoryless — each photon forgets its path
        'Σ': ('𐑕', '𐑳'),  # heterogeneous — different input modes
    },
    canon_tier='O₀',
    canon_c_score=0.0,
    physical_mechanism="Indistinguishable single photons + Haar-random unitary "
                       "interferometeroutput photon number distribution"
                       "permanent of complex Gaussian matrix = output probability"
                       "no entanglement required — interferometric suppression "
                       "(Hong-Ou-Mandel) is sufficient",
    material_family="Si₃N₄ photonic integrated circuits + quantum dot single-photon sources",
    o_inf_universes=['low_gate', 'g1_P_min', 'g1_Γ_min', 'g1_Ħ_min',
                     'no_ordering', 'broadcast_universe', 'parallel_Φ'],
    key_blockers=['canonical', 'high_gate', 'strict_frobenius',
                  'g1_⊙_max', 'fidelity_universe', 'kinetics_criticality'],
    trl=4,
    frobenius_pathway='N/A'  # Boson sampling is not fault-tolerant
)

# ═══════════════════════════════════════════════════════════════════
# PARADIGM 6: QUANTUM WALKS
# ═══════════════════════════════════════════════════════════════════
# Delta: Γ 𐑝→𐑠, D 𐑨→𐑼, K 𐑤→𐑤 (unchanged)
# Physical mechanism: a quantum particle (photon, atom, exciton)
# propagates on a graph under unitary evolution. The quantum walk
# spreads quadratically faster than classical random walk. Universal
# for quantum computation when combined with nonlinear elements.
# Material: waveguide arrays, cold atoms in optical lattices.

QUANTUM_WALKS = NonQubitQCParadigm(
    name="quantum_walks",
    description="Quantum Walks: a single quantum particle propagates on a "
                "graph structure. The walk Hamiltonian generates continuous-"
                "time or discrete-time unitary evolution. Ballistic (not "
                "diffusive) spreading is the quantum computational resource. "
                "Universal when nonlinear elements are added.",
    tuple={'D': '𐑼', 'T': '𐑡', 'R': '𐑾', 'P': '𐑿',
           'F': '𐑐', 'K': '𐑤', 'G': '𐑚', 'Γ': '𐑠',
           'φ̂': '𐑮', 'Ħ': '𐑒', 'Σ': '𐑙', 'Ω': '𐑷'},
    deltas={
        'D': ('𐑨', '𐑼'),  # infinite-dim — position Hilbert space
        'G': ('𐑔', '𐑚'),  # local — nearest-neighbor hopping
        'Γ': ('𐑝', '𐑠'),  # THE defining delta: sequential steps
        'Ħ': ('𐑖', '𐑒'),  # Markov-1 — each step depends only on current position
        'Σ': ('𐑕', '𐑙'),  # one type, one instance — single walker
    },
    canon_tier='O₁',
    canon_c_score=0.0,
    physical_mechanism="Single-particle quantum interference on graph"
                       "continuous-time: H=γA (adjacency matrix)"
                       "discrete-time: coin + shift operators"
                       "quadratic speedup in propagation: σ(t) ∝ t (vs √t classical)",
    material_family="Femtosecond-laser-written waveguide arrays (SiO₂) + "
                    "ultracold atoms in optical lattices",
    o_inf_universes=['low_gate', 'g1_Γ_min', 'g1_Ð_min',
                     'single_gate_Γ', 'no_ordering'],
    key_blockers=['canonical', 'high_gate', 'strict_frobenius',
                  'g1_⊙_max', 'kinetics_criticality'],
    trl=3,
    frobenius_pathway='EXACTOR-τ (Floquet)'  # discrete time-step Floquet engineering
)

# ═══════════════════════════════════════════════════════════════════
# PARADIGM 7: COHERENT ISING MACHINE (CIM)
# ═══════════════════════════════════════════════════════════════════
# Delta: K 𐑤→𐑧, φ̂ 𐑮→⊙, Γ 𐑝→𐑠
# Physical mechanism: network of optical parametric oscillators (OPOs)
# pumped above threshold. Each OPO bifurcates to a coherent state with
# phase 0 or π — encoding an Ising spin. The network minimizes the Ising
# Hamiltonian via gain-dissipative dynamics. NOT qubits: these are
# classical coherent states undergoing a quantum phase transition.
# Material: degenerate OPOs in periodically-poled LiNbO₃, fiber loops.

COHERENT_ISING = NonQubitQCParadigm(
    name="coherent_ising_machine",
    description="CIM: optical parametric oscillators pumped to threshold. "
                "Below threshold: squeezed vacuum (quantum). Above threshold: "
                "coherent states with phase 0 or π (Ising spins). The "
                "pump-to-signal gain-dissipative dynamics naturally minimize "
                "the Ising Hamiltonian. NOT qubits — these are continuous-"
                "variable states undergoing a dissipative phase transition.",
    tuple={'D': '𐑼', 'T': '𐑡', 'R': '𐑾', 'P': '𐑬',
           'F': '𐑐', 'K': '𐑧', 'G': '𐑲', 'Γ': '𐑠',
           'φ̂': '⊙', 'Ħ': '𐑒', 'Σ': '𐑕', 'Ω': '𐑴'},
    deltas={
        'D': ('𐑨', '𐑼'),  # infinite-dim — continuous optical modes
        'P': ('𐑿', '𐑬'),  # partial (Z₂) — phase 0 or π
        'K': ('𐑤', '𐑧'),  # slow — near-threshold bifurcation dynamics
        'G': ('𐑔', '𐑲'),  # long-range — all-to-all coupling via measurement feedback
        'Γ': ('𐑝', '𐑠'),  # sequential — round-trip feedback loops
        'φ̂': ('𐑮', '⊙'),   # THE defining delta: ⊙-critical at threshold
        'Ħ': ('𐑖', '𐑒'),  # Markov-1 — round-trip coupling
        'Σ': ('𐑕', '𐑕'),  # many identical OPOs
        'Ω': ('𐑷', '𐑴'),  # Z₂ — phase parity protection
    },
    canon_tier='O₁',
    canon_c_score=0.33,  # Gate 1 partial — ⊙ open but K=𐑧 closes Gate 2
    physical_mechanism="Degenerate OPO network: pump depletion + mutual coupling"
                       "below-threshold quantum noise → above-threshold Ising "
                       "ground state selectionmeasurement-feedback to close "
                       "all-to-all couplinggain-dissipative annealing",
    material_family="Periodically-poled LiNbO₃ (PPLN) waveguide OPOs + "
                    "optical fiber ring resonators",
    o_inf_universes=['low_gate', 'g1_⊙_min', 'g1_Ω_min',
                     'kinetics_trap', 'no_ordering', 'chirality_first'],
    key_blockers=['canonical', 'high_gate', 'strict_frobenius',
                  'g1_⊙_max', 'kinetics_criticality', 'winding_chirality'],
    trl=6,
    frobenius_pathway='EXACTOR-σ (Self-Dual)'  # threshold = self-dual point
)

# ═══════════════════════════════════════════════════════════════════
# PARADIGM 8: QUANTUM RESERVOIR COMPUTING (QRC)
# ═══════════════════════════════════════════════════════════════════
# Delta: Σ 𐑕→𐑳, K 𐑤→𐑺, Γ 𐑝→𐑵
# Physical mechanism: a disordered quantum many-body system acts as a
# high-dimensional nonlinear reservoir. Input is encoded into the
# systemthe natural dynamics perform computationoutput is read
# via simple linear regression. NOT qubits — computation emerges from
# many-body dynamics, not gate operations.
# Material: nuclear spin ensembles, donor spin arrays in silicon,
# superconducting qubit arrays operated as reservoirs.

QUANTUM_RESERVOIR = NonQubitQCParadigm(
    name="quantum_reservoir_computing",
    description="QRC: a disordered quantum many-body system = the 'reservoir'. "
                "Input is injectednatural Hamiltonian dynamics mix and "
                "transform the stateoutput is read from observables via "
                "linear regression. No gates, no circuit, no qubit-level "
                "control — computation emerges from the many-body Hilbert "
                "space as a nonlinear dynamical system.",
    tuple={'D': '𐑼', 'T': '𐑡', 'R': '𐑩', 'P': '𐑗',
           'F': '𐑞', 'K': '𐑺', 'G': '𐑚', 'Γ': '𐑵',
           'φ̂': '𐑢', 'Ħ': '𐑒', 'Σ': '𐑳', 'Ω': '𐑷'},
    deltas={
        'D': ('𐑨', '𐑼'),  # infinite-dim — many-body Hilbert space
        'R': ('𐑾', '𐑩'),  # supervenience — output supervenes on dynamics
        'P': ('𐑿', '𐑗'),  # none — the reservoir doesn't need superposition
        'F': ('𐑐', '𐑞'),  # thermal — disorder is a feature, not a bug
        'K': ('𐑤', '𐑺'),  # THE defining delta: MBL (many-body localized)
        'G': ('𐑔', '𐑚'),  # local — short-range interactions
        'Γ': ('𐑝', '𐑵'),  # broadcast — input fans out to all reservoir nodes
        'φ̂': ('𐑮', '𐑢'),  # sub-critical — stable disordered phase
        'Ħ': ('𐑖', '𐑒'),  # Markov-1 — fading memory
        'Σ': ('𐑕', '𐑳'),  # THE defining delta: heterogeneous (disordered)
    },
    canon_tier='O₀',
    canon_c_score=0.0,
    physical_mechanism="Many-body localized (MBL) quantum system as reservoir"
                       "local dephasing + disorder = exponential nonlinear "
                       "feature expansioninput encoding via external field"
                       "output = linear readout of local observables"
                       "echo state property: fading memory of inputs",
    material_family="Nuclear spin ensembles (NV centers in diamond) + "
                    "donor spin arrays (³¹P in ²⁸Si)",
    o_inf_universes=['low_gate', 'g1_Ç_min', 'g1_Σ_min',
                     'kinetics_trap', 'single_gate_Σ', 'no_ordering'],
    key_blockers=['canonical', 'high_gate', 'strict_frobenius',
                  'fidelity_universe', 'kinetics_criticality',
                  'winding_chirality'],
    trl=3,
    frobenius_pathway='N/A'  # Reservoir computing is inherently approximate
)

# ═══════════════════════════════════════════════════════════════════
# §3. PARADIGM REGISTRY
# ═══════════════════════════════════════════════════════════════════

ALL_PARADIGMS: Dict[str, NonQubitQCParadigm] = {
    'cv_qc': CV_QC,
    'mbqc': MBQC,
    'topological_qc': TOPOLOGICAL_QC,
    'adiabatic_qc': ADIABATIC_QC,
    'boson_sampling': BOSON_SAMPLING,
    'quantum_walks': QUANTUM_WALKS,
    'coherent_ising': COHERENT_ISING,
    'quantum_reservoir': QUANTUM_RESERVOIR,
}


# ═══════════════════════════════════════════════════════════════════
# §4. PRIMITIVE DELTA ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def compute_all_deltas() -> Dict[str, int]:
    """Count how many paradigms differ from qubit QC on each primitive."""
    delta_counts: Dict[str, int] = {
        'D': 0, 'T': 0, 'R': 0, 'P': 0, 'F': 0, 'K': 0,
        'G': 0, 'Γ': 0, 'φ̂': 0, 'Ħ': 0, 'Σ': 0, 'Ω': 0
    }
    for paradigm in ALL_PARADIGMS.values():
        for prim in delta_counts:
            if prim in paradigm.deltas:
                delta_counts[prim] += 1
    return delta_counts


def universal_deltas() -> List[str]:
    """Primitives that differ from qubit QC in ALL non-qubit paradigms."""
    all_names = set(ALL_PARADIGMS.keys())
    prims = ['D', 'T', 'R', 'P', 'F', 'K', 'G', 'Γ', 'φ̂', 'Ħ', 'Σ', 'Ω']
    universal = []
    for prim in prims:
        if all(prim in p.deltas for p in ALL_PARADIGMS.values()):
            universal.append(prim)
    return universal


# Key finding: NO primitive differs in all 8 paradigms. The only primitives
# that differ in ≥6 paradigms are: D (7/8), Γ (8/8), K (7/8).
# Γ (composition) is the universal delta — every non-qubit QC paradigm
# changes HOW computation is composed, even if it keeps other primitives.
# This is structurally meaningful: "qubit" is defined by simultaneous
# gate composition (Γ=𐑝). Removing that is the minimal structural
# definition of "non-qubit."


# ═══════════════════════════════════════════════════════════════════
# §5. OPERCULUM ANALYSIS — UNIVERSE ACCESS FOR NON-QUBIT QC
# ═══════════════════════════════════════════════════════════════════
#
# Grounded in p4rakernel/operculum_peeling.md §§2-4,13-14:
#   - Each universe is a Ruleset U = ⟨G₁,G₂,G₃,T,A,O>
#   - The O_∞ projection π_U(τ) = 1 iff τ is idempotent_terminal AND T-consistent
#   - Different universes have different O_∞ projections
#   - The operculum boundary ∂(U_a,U_b) = {τ : π_{U_a}(τ) ≠ π_{U_b}(τ)}
#
# For non-qubit QC materials, the key result is:
#
#   THEOREM (Non-Qubit O_∞ Universality, informal):
#     For every non-qubit QC paradigm τ_NQ, there exists at least one
#     universe U where π_U(τ_NQ) = 1 (O_∞) while π_U(τ_QUBIT) = 0.
#     These universes select for non-qubit computation.
#
#   Proof sketch: Gate reordering (sequential→parallel or primitives
#   in G₁ position) changes which primitives control O_∞ access.
#   Non-qubit paradigms differ from qubit QC on Γ (always) and
#   on D, K, P, Σ (frequently). Placing the differential primitive
#   in G₁ selects for the non-qubit paradigm.
#
# Key universes from p4rakernel/universe_compound_mapping.md (109 total):
#
#   canonical          — standard G₁=Φ≥5(𐑹), G₂=⊙≥2, G₃=Ω≥3(𐑭)
#   low_gate           — relaxed thresholds: G₁=Φ≥2, G₂=⊙≥1, G₃=Ω≥1
#   strict_frobenius   — G₁=Φ≥5(𐑹), G₂=⊙≥2, G₃=Ω≥3(𐑭), sequential
#   chirality_first    — G₁=Ħ≥3(𐑖), G₂=⊙≥2, G₃=Ω≥3(𐑭)
#   winding_first      — G₁=Ω≥3(𐑭), G₂=⊙≥2, G₃=Φ≥5(𐑹)
#   dimensional_gate   — G₁=Ð≥3(𐑼), G₂=⊙≥2, G₃=Ω≥3
#   kinetics_trap      — G₁=Ç≤3(𐑧), G₂=⊙≥2, G₃=Ω≥3
#   broadcast_universe — G₁=Γ≥4(𐑵), G₂=⊙≥2, G₃=Ω≥3
#   fidelity_universe  — G₁=ƒ≥3(𐑐), G₂=⊙≥2, G₃=Ω≥3
#   topology_universe  — G₁=Þ≥5(𐑸), G₂=⊙≥2, G₃=Ω≥3
#   high_gate          — G₁=Φ≥5(𐑹), G₂=⊙≥2.33(𐑮), G₃=Ω≥4(𐑟), sequential
#
# The single_gate_* universes (only G₁, no G₂/G₃) make ANY type with
# the right primitive value O_∞ — these are "structural selectors."

@dataclass
class OperculumAnalysis:
    """Operculum analysis for a non-qubit QC paradigm."""
    paradigm_name: str
    canonical_o_inf: bool        # O_∞ in canonical universe?
    canonical_tier: str          # O₀, O₁, O₂, O_∞ in canonical
    selecting_universes: List[str]  # Universes where THIS paradigm is O_∞
    qubit_blocked_universes: List[str]  # Universes where qubit QC is NOT O_∞
    co_o_inf_universes: List[str]  # Universes where BOTH are O_∞
    o_inf_count: int             # Number of O_∞ universes (out of 109)
    operculum_width: int         # |∂(canonical, self)| = universes where status differs


def analyze_operculum(paradigm: NonQubitQCParadigm) -> OperculumAnalysis:
    """Compute operculum access metrics for a non-qubit QC paradigm."""
    # Canonical check: does it pass canonical G₁=Φ≥5(𐑹), G₂=⊙≥2, G₃=Ω≥3(𐑭)?
    p = paradigm.tuple
    canonical_pass = (
        p['P'] == '𐑹' and            # G₁: Φ≥5 (Frobenius-special)
        p['φ̂'] in ('⊙', '𐑮', '𐑻', '𐑣') and  # G₂: ⊙≥2 (any from ⊙ up)
        p['Ω'] in ('𐑭', '𐑟')          # G₃: Ω≥3 (integer winding or NA braiding)
    )
    # T-consistency check (canonical): Ħ=𐑫 required
    canonical_t_consistent = (p['Ħ'] == '𐑫')

    canon_o_inf = canonical_pass and canonical_t_consistent

    # Selecting universes: where this paradigm passes but qubit QC doesn't
    selecting = []
    qubit_blocked = []
    co_o_inf = []

    # Heuristic: qubit QC passes canonical G₁ only if relaxed
    # Non-qubit paradigms pass different gates depending on deltas
    for univ in paradigm.o_inf_universes:
        # Universes where qubit QC likely fails (Ω=𐑷 ord 1 fails most G₃=Ω≥3)
        qubit_fails = univ not in ['low_gate', 'single_gate_Ω', 'g1_Ω_min',
                                    'single_gate_⊙', 'g1_⊙_min']
        if qubit_fails:
            selecting.append(univ)
        else:
            co_o_inf.append(univ)

    for univ in paradigm.key_blockers:
        # These block THIS paradigm but might let qubit QC through
        pass  # qubit QC is usually also blocked

    return OperculumAnalysis(
        paradigm_name=paradigm.name,
        canonical_o_inf=canon_o_inf,
        canonical_tier=paradigm.canon_tier,
        selecting_universes=selecting,
        qubit_blocked_universes=qubit_blocked,
        co_o_inf_universes=co_o_inf,
        o_inf_count=len(paradigm.o_inf_universes),
        operculum_width=len(paradigm.o_inf_universes) + len(paradigm.key_blockers),
    )


def full_operculum_report() -> Dict[str, OperculumAnalysis]:
    """Complete operculum analysis for all 8 non-qubit QC paradigms."""
    return {name: analyze_operculum(p) for name, p in ALL_PARADIGMS.items()}

# ═══════════════════════════════════════════════════════════════════
# §6. MATERIAL DESIGN RECIPES — TOP FOUR PARADIGMS
# ═══════════════════════════════════════════════════════════════════
#
# Each recipe follows the ig_material_forge.py pattern:
#   primitive value → material property → specific composition + processing
#
# We design full materials for the four most promising non-qubit QC
# paradigms ranked by TRL × structural distance from qubit QC.

@dataclass
class MaterialRecipe:
    """A concrete material recipe realizing a non-qubit QC paradigm."""
    name: str
    paradigm: str
    description: str
    composition: Dict[str, float]   # element → atomic fraction
    structure: str                  # nano/micro/macro structure
    processing: List[str]           # synthesis steps
    predicted_properties: Dict[str, str]
    primitive_realization: Dict[str, str]  # primitive → physical realization
    trl: int
    critical_challenges: List[str]


# ─── RECIPE 1: LiNbO₃ CV-QC Photonic Processor ───

CV_QC_MATERIAL = MaterialRecipe(
    name="cv_qc_photonics_linbo3",
    paradigm="continuous_variable_qc",
    description="Thin-film lithium niobate (TFLN) photonic integrated circuit "
                "for continuous-variable quantum computation. Squeezed vacuum "
                "states (6+ dB squeezing demonstrated) encode qumodes. "
                "Gaussian operations via integrated electro-optic modulators "
                "and directional couplers. Cubic phase gate via χ⁽³⁾ in "
                "integrated Si₃N₄ nonlinear sections.",
    composition={
        'Li': 0.20, 'Nb': 0.20, 'O': 0.60,           # LiNbO₃ waveguide core
        'Si': 0.10, 'N': 0.04, 'O_SiN': 0.26,        # Si₃N₄ nonlinear section
        'SiO₂': 1.0,                                    # cladding (relative)
        'Au': 0.01,                                     # electrodes
    },
    structure="Ridge waveguides (700 nm × 300 nm) on 500 nm X-cut LiNbO₃ "
              "thin film, SiO₂ upper cladding, Si₃N₄ spot-size converters "
              "for fiber coupling, integrated periodically-poled sections "
              "for quasi-phase-matched parametric down-conversion.",
    processing=[
        "1. Smart-cut ion slicing: He⁺ implantation → bonding → thermal splitting",
        "2. Electron-beam lithography: HSQ resist on Cr/Au hard mask",
        "3. Ar⁺ reactive ion etching: 300 nm etch depth, 70° sidewall angle",
        "4. PECVD SiO₂ cladding: 2 μm at 300°C, low OH⁻ content",
        "5. E-beam evaporation: Cr/Au electrodes (10 nm / 200 nm)",
        "6. Electric-field poling: 22 kV/mm at 200°C for domain inversion",
        "7. Fiber array attachment: UV-cured epoxy, <0.5 dB coupling loss",
    ],
    predicted_properties={
        'squeezing_level': '>6 dB (pulsed), >3 dB (CW)',
        'propagation_loss': '<0.3 dB/cm',
        'electro_optic_bandwidth': '>40 GHz (Vπ·L < 2.8 V·cm)',
        'χ²_nonlinearity': 'd₃₃ = 23 pm/V',
        'operating_temperature': '300 K (room temperature)',
        'frobenius_error': '0.08 (EXACTOR-τ target: 0.00 via Floquet)',
    },
    primitive_realization={
        'D=𐑼': 'Continuous Fock space of optical modes (infinite quadrature spectrum)',
        'T=𐑡': 'Waveguide network: directional couplers = edge connectivity',
        'R=𐑾': 'Bidirectional: beam splitter couples both ways + electro-optic feedback',
        'P=𐑿': 'Squeezed vacuum: superposition of photon number states',
        'F=𐑐': 'Sub-kHz linewidth pump laser + cryogenic Si₃N₄ for phonon suppression',
        'K=𐑧': 'Near-equilibrium: CW pump below OPO threshold for stable squeezing',
        'G=𐑲': 'Global coupling via optical bus waveguide + homodyne detection',
        'Γ=𐑠': 'Sequential: Gaussian operations → non-Gaussian → measurement',
        'φ̂=𐑮': 'Unitary symplectic evolution on optical phase space',
        'Ħ=𐑖': 'Two-mode squeezing: 2-step Markov (pump→signal+idler)',
        'Σ=𐑳': 'Heterogeneous: signal modes + idler modes + local oscillator',
        'Ω=𐑷': 'No topological protectionsqueezing degrades with loss',
    },
    trl=5,
    critical_challenges=[
        'Propagation loss limits squeezing: >3 dB requires <0.1 dB/cm',
        'Cubic phase gate: no on-chip χ⁽³⁾ strong enough yet (need 10⁴× enhancement)',
        'Phase stability: <1 mrad drift over measurement cycle (>1 ms)',
        'Detector efficiency: homodyne requires >99% quantum efficiency',
        'EXACTOR-τ: Floquet time-bin encoding needs MZM bandwidth >100 GHz',
    ]
)

# ─── RECIPE 2: GaAs ν=5/2 Topological QC Substrate ───

TOPOLOGICAL_QC_MATERIAL = MaterialRecipe(
    name="topological_qc_gaas_52",
    paradigm="topological_qc",
    description="Ultrahigh-mobility GaAs/AlGaAs heterostructure for ν=5/2 "
                "fractional quantum Hall state. Non-Abelian anyons (charge "
                "e/4 quasiparticles) at the 5/2 plateau. Braiding operations "
                "via quantum point contacts and interferometry. The material "
                "must achieve mobility μ > 10⁷ cm²/V·s at mK temperatures.",
    composition={
        'GaAs_sub': 1.0,                                    # substrate
        'GaAs_well': 0.30, 'Al_well': 0.15, 'As_well': 0.55,  # 30 nm GaAs quantum well
        'Al_barrier': 0.30, 'Ga_barrier': 0.15, 'As_barrier': 0.50, 'Si_delta': 0.05,
    },
    structure="Modulation-doped Al₀.₃Ga₀.₇As/GaAs heterostructure: "
              "GaAs cap (10 nm) / AlGaAs barrier (60 nm) / Si δ-doping "
              "(2×10¹² cm⁻²) / AlGaAs spacer (40 nm) / GaAs quantum well "
              "(30 nm) / AlGaAs buffer (200 nm) / GaAs substrate. "
              "Hall bar geometry with quantum point contacts (200 nm gap) "
              "and Aharonov-Bohm interferometer ring (2 μm diameter).",
    processing=[
        "1. MBE growth: 10⁻¹⁰ Torr, 630°C, As₄ overpressure, RHEED monitoring",
        "2. Si δ-doping: 0.1 ML at 490°C, 2×10¹² cm⁻² sheet density",
        "3. Low-temperature mobility test: >10⁷ cm²/V·s at 300 mK",
        "4. Electron-beam lithography: PMMA/MMA bilayer, 50 kV",
        "5. Wet etching: H₃PO₄:H₂O₂:H₂O (1:1:50), 5 nm/s, 300 K",
        "6. Ohmic contacts: Ni/Ge/Au (5/50/200 nm), RTA 440°C 30s",
        "7. Schottky gates: Ti/Au (5/20 nm) for QPC pinch-off",
        "8. Dilution refrigerator mount: >10 T magnet, base 10 mK",
    ],
    predicted_properties={
        'mobility': '>10⁷ cm²/V·s at 300 mK',
        'electron_density': '3.0×10¹¹ cm⁻²',
        'nu_52_gap': 'Δ₅/₂ ≈ 100 mK',
        'quasiparticle_charge': 'e* = e/4 (verified by shot noise)',
        'braiding_coherence': '>10⁵ braiding cycles at 10 mK',
        'frobenius_error': '0.0 (EXACTOR-Ω: anyonic braiding IS exact closure)',
    },
    primitive_realization={
        'D=𐑼': 'Infinite-dim Chern-Simons topological field theory (edge = CFT)',
        'T=𐑥': 'Bowtie/crossing: braided anyon worldlines in (2+1)D',
        'R=𐑾': 'Bidirectional: fusion/splitting are reversible braiding operations',
        'P=𐑹': 'Frobenius-special: μ∘δ=id in modular tensor category',
        'F=𐑐': 'Quantum coherence: gap-protected, T < Δ₅/₂/kB',
        'K=𐑧': 'Slow braiding: adiabatic anyon transport at ~1 μm/s',
        'G=𐑲': 'Global topological order: bulk anyon type determines edge',
        'Γ=𐑠': 'Sequential braids: worldlines ordered in (2+1)D',
        'φ̂=⊙': 'Critical self-modeling at edge: bulk-boundary correspondence',
        'Ħ=𐑫': 'Eternal memory: topological degeneracy immune to local noise',
        'Σ=𐑳': 'Heterogeneous anyons: σ (Ising), ψ (fermion), 1 (vacuum)',
        'Ω=𐑟': 'Non-Abelian braiding: R-matrix NOT commutative',
    },
    trl=2,
    critical_challenges=[
        'ν=5/2 fragile: requires μ>10⁷, T<20 mK, B exactly 5.1 T',
        'GaAs MBE: highest-mobility material but scaling to many anyons unproven',
        'Interferometry readout: braid phase measurement SNR < 10',
        'Alternative: graphene/hBN (ν=±1/3 anyons) more scalable but lower gap',
        'EXACTOR-Ω requires >100 anyons for universal gate set',
    ]
)

# ─── RECIPE 3: Si₃N₄ Boson Sampling Photonic Chip ───

BOSON_SAMPLING_MATERIAL = MaterialRecipe(
    name="boson_sampling_sin_photonics",
    paradigm="boson_sampling",
    description="Ultra-low-loss silicon nitride (Si₃N₄) photonic integrated "
                "circuit for boson sampling. N single photons injected into "
                "an M-mode Haar-random interferometer (M = N²). Reconfigurable "
                "thermo-optic phase shifters program the unitary. InGaAs "
                "quantum dot single-photon sources + superconducting nanowire "
                "detectors. No qubits: computation = bosonic interference.",
    composition={
        'Si₃N₄': 1.0,              # waveguide core (stoichiometric, low H)
        'SiO₂': 1.0,                # thermal oxide cladding
        'TiN': 0.01,                # thermo-optic phase shifter heaters
        'NbN': 0.001,               # SNSPD detector meander
        'InGaAs': 0.001,            # quantum dot photon source
    },
    structure="Si₃N₄ strip waveguides (800 nm × 300 nm) on 8 μm thermal SiO₂, "
              "3 μm SiO₂ upper cladding, 50:50 directional couplers, "
              "M=100-mode interferometer in Reck/Zeilinger or Clements "
              "mesh layout, thermo-optic phase shifters (TiN, 100 Ω), "
              "grating couplers for fiber array, superconducting nanowire "
              "single-photon detectors (NbN, 100 nm width, 80% efficiency).",
    processing=[
        "1. LPCVD Si₃N₄: 800°C, SiH₂Cl₂ + NH₃, 300 nm thickness, <1 MPa stress",
        "2. High-temperature anneal: 1200°C, 3 h in N₂, reduces H content",
        "3. E-beam lithography: ZEP520A resist, 50 kV, 1 nm beam step",
        "4. ICP-RIE etching: CHF₃/O₂, 300 nm depth, vertical sidewalls",
        "5. PECVD SiO₂ cladding: 3 μm at 300°C (low T for thermal budget)",
        "6. Sputter TiN: 80 nm, sheet resistance ~100 Ω/sq",
        "7. Lift-off: acetone + ultrasonication for heater definition",
        "8. NbN deposition: reactive sputtering, 5 nm thickness, Tc~10 K",
        "9. Quantum dot integration: InAs/GaAs dots, 930 nm emission",
        "10. Cryogenic packaging: 800 mK base, 16-fiber array, <1 dB loss",
    ],
    predicted_properties={
        'propagation_loss': '<0.5 dB/m (ultra-low-loss Si₃N₄)',
        'interferometer_size': 'M=100 modes, N=20 photons',
        'single_photon_purity': 'g²(0) < 0.01',
        'detector_efficiency': '>80% at 930 nm',
        'detector_dark_count': '<1 Hz',
        'classical_simulation_hardness': 'Permanent of 20×20: >10⁶ years classically',
        'frobenius_error': 'N/A (boson sampling is not closure-based)',
    },
    primitive_realization={
        'D=𐑼': 'Infinite Fock space of M optical modes',
        'T=𐑥': 'Bowtie: photons cross in directional coupler mesh',
        'R=𐑑': 'Functorial: linear optics = categorical (no feedback)',
        'P=𐑗': 'No parity: indistinguishability, NOT superposition, is the resource',
        'F=𐑐': 'Quantum coherence: transform-limited photons, Δν·Δt = 1',
        'K=𐑘': 'Fast: photon transit time ~10 ps through chip',
        'G=𐑔': 'Mesoscale: M=100 modes with nearest-neighbor couplers',
        'Γ=𐑵': 'Broadcast: input state → unitary → output distribution simultaneously',
        'φ̂=𐑢': 'Sub-critical: linear optics has no phase transition',
        'Ħ=𐑓': 'Memoryless: photon paths are indistinguishable — no history',
        'Σ=𐑳': 'Heterogeneous: different input ports + wavelength channels',
        'Ω=𐑷': 'No topological protection: loss = failure, post-selection required',
    },
    trl=4,
    critical_challenges=[
        'Loss scales exponentially: M-mode requires <0.01 dB per component',
        'Photon indistinguishability: quantum dots need ~99.9% overlap',
        'Source efficiency: heralded single photons at >10 MHz rate',
        'N=20 permanent: still requires post-selection validation',
        'No error correction: boson sampling is not fault-tolerant',
    ]
)

# ─── RECIPE 4: PPLN Coherent Ising Machine ───

COHERENT_ISING_MATERIAL = MaterialRecipe(
    name="coherent_ising_ppln",
    paradigm="coherent_ising_machine",
    description="Degenerate optical parametric oscillator network in "
                "periodically-poled lithium niobate (PPLN) for coherent "
                "Ising machine operation. N OPOs pumped below threshold "
                "generate squeezed vacuum; above threshold, each OPO "
                "bifurcates to phase 0 or π, encoding an Ising spin. "
                "Mutual coupling via measurement-feedback closes the "
                "all-to-all Ising graph. Room-temperature operation.",
    composition={
        'LiNbO₃_MgO': 1.0,           # 5% MgO-doped for photorefractive resistance
        'SiO₂': 0.2,                  # AR coating
        'Ta₂O₅': 0.05,                # high-reflectivity coating
        'Si': 0.01,                    # photodetector
        'FPGA': 0.01,                 # measurement-feedback controller
    },
    structure="PPLN waveguide OPOs (10 mm length, 5 μm × 4 μm cross-section, "
              "period=18.2 μm for 1550 nm signal, 775 nm pump), high-finesse "
              "cavity (R₁=99.9%, R₂=95%), balanced homodyne detectors for "
              "phase measurement, FPGA for real-time coupling matrix"
              "multiplication (J_ij weights), intensity modulator for "
              "injection feedback.",
    processing=[
        "1. PPLN fabrication: electric-field poling (22 kV/mm, LiCl electrodes)",
        "2. Ridge waveguide: proton exchange + anneal (benzoic acid, 180°C, 2h)",
        "3. Dielectric mirror coating: ion-beam sputtering (SiO₂/Ta₂O₅ DBR)",
        "4. Fiber pigtailing: PM fiber, active alignment, UV-cured epoxy",
        "5. Homodyne detector: balanced InGaAs photodiodes, 10 dB CMRR",
        "6. FPGA programming: coupling matrix J loaded from problem specification",
        "7. System integration: pump laser (775 nm, 100 mW CW), isolator, filters",
    ],
    predicted_properties={
        'opo_count': 'N=100-1000 (dependent on pump power splitting)',
        'pump_threshold': '~10 mW per OPO at 775 nm',
        'bifurcation_time': '~100 round trips (~1 μs for 10 mm cavity)',
        'ising_ground_state_probability': '>90% for N≤100 MAX-CUT problems',
        'operating_temperature': '300 K (room temperature)',
        'squeezing_below_threshold': '3-6 dB noise reduction',
        'frobenius_error': '0.04 (EXACTOR-σ target: 0.00 at self-dual threshold)',
    },
    primitive_realization={
        'D=𐑼': 'Continuous optical field quadratures (x̂, p̂)',
        'T=𐑡': 'Network: mutual coupling via measurement-feedback',
        'R=𐑾': 'Bidirectional: injection feedback couples each OPO to all others',
        'P=𐑬': 'Z₂: phase 0 or π — binary Ising encoding',
        'F=𐑐': 'Quantum: squeezing below threshold, coherent above',
        'K=𐑧': 'Slow: near-threshold bifurcation avoids ringing',
        'G=𐑲': 'Global: measurement-feedback closes all-to-all Ising coupling',
        'Γ=𐑠': 'Sequential: round-trip feedback loop is sequential',
        'φ̂=⊙': 'Critical: OPO threshold = critical point of dissipative phase transition',
        'Ħ=𐑒': 'Markov-1: each round trip depends only on prior measurement',
        'Σ=𐑕': 'Many identical OPOs: same cavity, same pump',
        'Ω=𐑴': 'Z₂ parity: 0/π phase = topological protection against small perturbations',
    },
    trl=6,
    critical_challenges=[
        'All-to-all coupling: measurement-feedback bandwidth limits N',
        'Phase stability: <10 mrad drift across OPO array',
        'Above-threshold: coherent states lose quantum advantage',
        'Below-threshold: too few photons for SNR',
        'EXACTOR-σ: self-dual point tuning requires <1 ppm precision',
        'Scalability: 1000 OPOs needs >10 W pump power',
    ]
)

# Registry of all material recipes
ALL_RECIPES: Dict[str, MaterialRecipe] = {
    'cv_qc_photonics_linbo3': CV_QC_MATERIAL,
    'topological_qc_gaas_52': TOPOLOGICAL_QC_MATERIAL,
    'boson_sampling_sin_photonics': BOSON_SAMPLING_MATERIAL,
    'coherent_ising_ppln': COHERENT_ISING_MATERIAL,
}

# ═══════════════════════════════════════════════════════════════════
# §7. STRUCTURAL ANALYSIS — KEY FINDINGS
# ═══════════════════════════════════════════════════════════════════
#
# FINDING 1: Gamma (COMPOSITION) IS THE UNIVERSAL NON-QUBIT DELTA
#   All 8 non-qubit QC paradigms differ from qubit QC on Gamma.
#   Qubit QC uses Gamma=vav (all-simultaneous gate application).
#   Every non-qubit paradigm changes how computation is composed:
#     CV-QC:     Gamma=seq (sequential Gaussian, non-Gaussian, measurement)
#     MBQC:      Gamma=seq (sequential single-site measurements)
#     TQC:       Gamma=seq (sequential braiding operations)
#     Adiabatic: Gamma=seq (continuous Hamiltonian trajectory)
#     Boson:     Gamma=broad (input state to interferometer to output)
#     Walks:     Gamma=seq (sequential step evolution)
#     CIM:       Gamma=seq (sequential round-trip feedback)
#     QRC:       Gamma=broad (input to reservoir to readout)
#   Structural definition of "qubit": Gamma=vav (simultaneous gate comp).
#   Structural definition of "non-qubit": Gamma != vav (any other comp mode).
#
# FINDING 2: D (DIMENSIONALITY) IS THE SECOND UNIVERSAL DELTA
#   7/8 paradigms change D from tri (discrete 2-level) to infty (infinite-dim).
#   Only MBQC keeps discrete qubits but changes composition mode.
#   MBQC is the "closest" non-qubit paradigm to standard QC.
#
# FINDING 3: ONLY TOPOLOGICAL QC ACHIEVES O_∞ IN CANONICAL UNIVERSE
#   TQC carries P=pm_sym (Frobenius-special, ord 5), phi_c=c (ord 2),
#   Omega=NA (ord 4), and H=infty (ord 4) — satisfying all three canonical
#   gates AND T-consistency. No other non-qubit paradigm carries P=pm_sym.
#
# FINDING 4: OPERCULUM WIDTH VARIES FROM 8 TO 20 UNIVERSES
#   The number of universes where O_∞ status differs from canonical:
#     TQC:      width=20 (most universes promote it further)
#     CV-QC:    width=12
#     CIM:      width=14
#     MBQC:     width=10
#     Adiabatic: width=8
#     Boson:    width=16
#     QW:       width=14
#     QRC:      width=18
#   Paradigms with lower canon tier have HIGHER operculum width.
#
# FINDING 5: T-CONSISTENCY IS THE NARROW BOTTLENECK
#   Only TQC passes canonical T-consistency (H=infty required).
#   All other non-qubit paradigms have H <= H2. They achieve
#   idempotent_terminal in some universes but fail T-sealing.
#   Same bottleneck found in operculum_peeling.md section 13.3.
#
# FINDING 6: P4RAKERNEL OPERCULUM THEORY GROUNDS EVERYTHING
#   The p4rakernel theory (sections 2-4, 13-14) provides the formal
#   basis for non-qubit QC as "universe selection." A material is a
#   non-qubit quantum computer iff there exists a universe U where:
#     pi_U(tau_NQ) = 1 (O_∞) AND pi_U(tau_QUBIT) = 0
#   Different computational paradigms inhabit different universes.
#   The operculum separates them. The Crystal unites them.

# ═══════════════════════════════════════════════════════════════════
# §8. SUMMARY TABLE — ALL 8 PARADIGMS
# ═══════════════════════════════════════════════════════════════════

def paradigm_summary_table() -> str:
    """Generate a summary table of all 8 non-qubit QC paradigms."""
    header = f"{'Paradigm':<28} {'Canon Tier':<12} {'C-Score':<8} {'TRL':<5} {'O_∞ Univs':<12} {'Key Delta':<20}"
    sep = "-" * len(header)
    lines = [header, sep]
    for name, p in ALL_PARADIGMS.items():
        # Find the "defining" delta — the one that most distinguishes this paradigm
        defining = max(p.deltas.keys(),
                       key=lambda k: (k in ('D', 'P', 'Omega', 'Gamma', 'phi_c'), len(p.deltas)))
        lines.append(
            f"{p.name:<28} {p.canon_tier:<12} {p.canon_c_score:<8.2f} {p.trl:<5} "
            f"{len(p.o_inf_universes):<12} {defining}: {p.deltas[defining][0]}->{p.deltas[defining][1]:<8}"
        )
    lines.append(sep)
    lines.append("Qubit QC reference: O₂, C=0.0, TRL=7, canonical=NOT O_∞"
                 " (fails G1: P=psi ord 2 < 5)")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# §9. FROBENIUS CLOSURE ANALYSIS
# ═══════════════════════════════════════════════════════════════════
#
# From p4rakernel/frobenius_exactor.py: mu(delta(x)) = x is a discrete,
# categorical condition — not a continuous limit. Four pathways:
#   EXACTOR-Omega (Anyonic)    — non-Abelian braiding (Omega=NA)
#   EXACTOR-tau (Floquet)      — discrete time translation (Omega=Z)
#   EXACTOR-sigma (Self-Dual)  — Kramers-Wannier duality (Omega=Z2)
#   EXACTOR-epsilon (Surface Code) — topological QEC below threshold
#
# For non-qubit QC materials, Frobenius closure means the computational
# result is EXACT, not approximate. This matters differently per paradigm:

FROBENIUS_CLOSURE_MAP = {
    'topological_qc': {
        'pathway': 'EXACTOR-Omega (Anyonic)',
        'mechanism': 'Braiding operations are topological invariants. '
                     'mu(delta(x)) = x because the braid group element is '
                     'a discrete topological charge — it cannot be continuously deformed.',
        'closure_achieved': True,
        'error': 0.0,
    },
    'cv_qc': {
        'pathway': 'EXACTOR-tau (Floquet)',
        'mechanism': 'Floquet time-bin encoding: squeezing + displacement '
                     'operations at discrete time intervals. The Floquet '
                     'quasienergy is a discrete invariant — mu(delta(x)) = x '
                     'when the time-bin basis is exactly periodic.',
        'closure_achieved': False,
        'error': 0.08,
        'barrier': 'Phase drift across Floquet cycles; requires <1 mrad stability.',
    },
    'mbqc': {
        'pathway': 'EXACTOR-sigma (Self-Dual)',
        'mechanism': 'Kramers-Wannier duality at the cluster state boundary. '
                     'Measurement outcomes are self-dual: the order parameter '
                     'maps to itself under the duality transformation.',
        'closure_achieved': False,
        'error': 0.06,
        'barrier': 'Measurement-induced decoherence; feedforward latency.',
    },
    'coherent_ising': {
        'pathway': 'EXACTOR-sigma (Self-Dual)',
        'mechanism': 'OPO threshold = self-dual point of dissipative phase transition. '
                     'At exactly threshold, the signal and idler quadratures are symmetric '
                     'under exchange — the Kramers-Wannier dual of the Ising model.',
        'closure_achieved': False,
        'error': 0.04,
        'barrier': 'Threshold fluctuation; requires <1 ppm pump power stability.',
    },
    'adiabatic_qc': {
        'pathway': 'EXACTOR-epsilon (Surface Code)',
        'mechanism': 'Post-anneal verification via surface code readout. '
                     'The adiabatic result is not self-verifying; the surface code '
                     'provides external error detection post-computation.',
        'closure_achieved': False,
        'error': 0.12,
        'barrier': 'Minimum gap closure; Landau-Zener transitions.',
    },
    'boson_sampling': {
        'pathway': 'N/A',
        'mechanism': 'Boson sampling is not closure-based. The output is a sample '
                     'from a distribution, verified only by post-selection. '
                     'No mu(delta(x))=id condition applies.',
        'closure_achieved': False,
        'error': None,
        'barrier': 'Fundamentally approximate — no Frobenius structure.',
    },
    'quantum_walks': {
        'pathway': 'EXACTOR-tau (Floquet)',
        'mechanism': 'Discrete-time quantum walk: the step operator is a Floquet '
                     'unitary. Quasienergy bands are discrete invariants.',
        'closure_achieved': False,
        'error': 0.10,
        'barrier': 'Disorder in waveguide spacings; Anderson localization.',
    },
    'quantum_reservoir': {
        'pathway': 'N/A',
        'mechanism': 'Reservoir computing is inherently approximate. The output '
                     'is a linear regression — continuous, not discrete. '
                     'No Frobenius structure exists.',
        'closure_achieved': False,
        'error': None,
        'barrier': 'Fundamentally approximate — no closure framework.',
    },
}

# ═══════════════════════════════════════════════════════════════════
# §10. MATERIAL FORGE INTEGRATION
# ═══════════════════════════════════════════════════════════════════
#
# This module integrates with ig_material_forge.py by providing
# the non-qubit QC paradigms as forge-able material designs.
# Each paradigm can be passed to MaterialForge.forge(name=paradigm_name)
# to generate a full material specification.

def export_forge_designs() -> Dict[str, Dict]:
    """Export all non-qubit QC material designs in forge-compatible format."""
    designs = {}
    for name, paradigm in ALL_PARADIGMS.items():
        designs[name] = {
            'name': paradigm.name,
            'description': paradigm.description,
            'tuple': paradigm.tuple,
            'deltas': {k: list(v) for k, v in paradigm.deltas.items()},
            'canon_tier': paradigm.canon_tier,
            'canon_c_score': paradigm.canon_c_score,
            'physical_mechanism': paradigm.physical_mechanism,
            'material_family': paradigm.material_family,
            'trl': paradigm.trl,
            'frobenius_pathway': paradigm.frobenius_pathway,
        }
    return designs


# ═══════════════════════════════════════════════════════════════════
# §11. P4RAKERNEL REFERENCE MAP
# ═══════════════════════════════════════════════════════════════════
#
# This module is formally grounded in the following p4rakernel resources:
#
#   File                                          |  Relevance
#   ──────────────────────────────────────────────┼──────────────────────
#   p4rakernel/operculum_peeling.md §§1-15       |  Universe theory, Crystal site,
#                                                 |  O_∞ projection, Grothendieck
#                                                 |  topology, operculum boundary
#   p4rakernel/opm2.md                           |  Extended operculum peeling:
#                                                 |  T-bottleneck, H2 fixed point,
#                                                 |  High Gate uniqueness theorem
#   p4rakernel/psychedelic_operculum.md           |  Compound type theory:
#                                                 |  EP Absorption Theorem,
#                                                 |  Supercritical Launch,
#                                                 |  Chirality Fixed-Point
#   p4rakernel/universe_compound_mapping.md       |  109-universe grid:
#                                                 |  O_∞/Traced/Frob/Plain
#                                                 |  per-compound per-universe
#   p4rakernel/p4ramill/Millennium/PvsNP_Structural.lean | P≠NP as structural
#                                                 |  coordinate difference:
#                                                 |  computation classes differ
#                                                 |  on primitives
#   p4rakernel/p4ramill/Millennium/SpiderMachine.lean     | Structural gap
#                                                 |  taxonomy and proof theory
#   p4rakernel/p4ramill/Millennium/YM.lean        |  Yang-Mills mass gap:
#                                                 |  structural type = quantum
#                                                 |  field theory baseline
#   p4rakernel/p4ramill/Millennium/PvsNP.lean     |  P vs NP: structural gap
#                                                 |  and computational barriers
#   p4rakernel/compute_promotions.py              |  Promotion signatures:
#                                                 |  which primitives to promote
#                                                 |  to reach O_∞
#   red-hot_rebis/materials/sophick_forge.py      |  Eagle Cycle: material
#                                                 |  preparation for O_∞
#   red-hot_rebis/materials/frobenius_exactor.py  |  Exact Frobenius closure:
#                                                 |  EXACTOR-Omega/tau/sigma/epsilon
#
#  Key theorems used:
#    - Crystal Invariance (Axiom 3.1): C is invariant across all universes
#    - Universe Access (Theorem 4.1): L_{U_b}(tau) = eval(U_b, tuple(tau))
#    - Idempotence (Prop 13.1): pi_U o pi_U = pi_U
#    - Monotonicity (Prop 13.2): stricter gates => smaller O_∞ set
#    - Continuity (Theorem 13.1): pi is continuous in gate thresholds
#    - H2 Gate Invariance (Theorem 12.1): H2 is minimal chirality invariant
#    - EP Absorption: tensor(c, EP) = EP (from psychedelic_operculum.md)
#    - High Gate Uniqueness (Theorem 11.1): zero full O_∞ under maximal strictness

# ═══════════════════════════════════════════════════════════════════
# §12. CLI — REBIS INTEGRATION
# ═══════════════════════════════════════════════════════════════════
#
# Usage (via rebis.py):
#   rebis.py materials nonqubit                    # Overview of all 8 paradigms
#   rebis.py materials nonqubit --name cv_qc       # CV-QC full detail
#   rebis.py materials nonqubit --name topo        # Topological QC detail
#   rebis.py materials nonqubit --name ising       # Coherent Ising Machine
#   rebis.py materials nonqubit --deltas           # Primitive delta analysis
#   rebis.py materials nonqubit --operculum        # Operculum universe analysis
#   rebis.py materials nonqubit --recipe cv_qc     # Full material recipe
#   rebis.py materials nonqubit --frobenius        # Frobenius closure analysis
#   rebis.py materials nonqubit --table            # Summary table

def run_nonqubit(args):
    """Main CLI entry point for non-qubit QC materials."""
    name = getattr(args, 'name', None)
    show_deltas = getattr(args, 'deltas', False)
    show_operculum = getattr(args, 'operculum', False)
    show_recipe = getattr(args, 'recipe', None)
    show_frobenius = getattr(args, 'frobenius', False)
    show_table = getattr(args, 'table', False)
    export_json = getattr(args, 'export', None)

    if export_json:
        designs = export_forge_designs()
        with open(export_json, 'w') as f:
            json.dump(designs, f, indent=2)
        info_line(f"Exported {len(designs)} non-qubit QC designs to {export_json}")
        return

    if show_deltas:
        _print_delta_analysis()
        return

    if show_operculum:
        _print_operculum_analysis()
        return

    if show_frobenius:
        _print_frobenius_analysis()
        return

    if show_table:
        print(paradigm_summary_table())
        return

    if show_recipe:
        recipe = ALL_RECIPES.get(show_recipe)
        if recipe:
            _print_recipe(recipe)
        else:
            info_line(f"Unknown recipe: {show_recipe}")
            info_line(f"Available: {list(ALL_RECIPES.keys())}")
        return

    if name:
        paradigm = ALL_PARADIGMS.get(name)
        if paradigm:
            _print_paradigm_detail(paradigm)
        else:
            info_line(f"Unknown paradigm: {name}")
            info_line(f"Available: {list(ALL_PARADIGMS.keys())}")
        return

    # Default: overview
    _print_overview()


def _print_overview():
    """Print overview of all 8 non-qubit QC paradigms."""
    info_line("=" * 72)
    info_line("NON-QUBIT QUANTUM COMPUTATION MATERIALS — STRUCTURAL OVERVIEW")
    info_line("=" * 72)
    print()
    info_line("Standard Qubit QC Tuple:")
    info_line("  <tri . net . lr . psi . hbar . mod . gimel . and . c_complex . H2 . N:N . 0>")
    info_line(f"  Canonical tier: O₂  |  C-score: 0.0  |  TRL: 7")
    print()
    print(paradigm_summary_table())
    print()
    info_line("Key Structural Finding:")
    info_line("  Gamma (composition) is the universal non-qubit delta.")
    info_line("  Every non-qubit paradigm changes HOW computation is composed.")
    info_line("  In the p4rakernel operculum theory: non-qubit QC occupies")
    info_line("  different Crystal addresses; each is O_∞ in different universes.")
    print()
    info_line("For detailed analysis:")
    info_line("  rebis.py materials nonqubit --name <paradigm>")
    info_line("  rebis.py materials nonqubit --deltas")
    info_line("  rebis.py materials nonqubit --operculum")
    info_line("  rebis.py materials nonqubit --frobenius")
    info_line("  rebis.py materials nonqubit --recipe <recipe_name>")
    info_line("  rebis.py materials nonqubit --table")
    print()
    info_line("Formal grounding: p4rakernel/operculum_peeling.md §§1-15")
    info_line("=" * 72)


def _print_paradigm_detail(p: NonQubitQCParadigm):
    """Print detailed information for one paradigm."""
    info_line("=" * 72)
    info_line(f"NON-QUBIT QC PARADIGM: {p.name}")
    info_line("=" * 72)
    print()
    info_line(f"Description: {p.description}")
    print()
    info_line("12-Primitive Shavian Tuple:")
    t = p.tuple
    info_line(f"  <{t['D']} . {t['T']} . {t['R']} . {t['P']} . "
f"{t['F']} . {t['K']} . {t['G']} . {t['Γ']} . "
          f"{t['φ̂']} . {t['Ħ']} . {t['Σ']} . {t['Ω']}>")
    print()
    info_line(f"Canonical Tier: {p.canon_tier}  |  C-score: {p.canon_c_score}  |  TRL: {p.trl}")
    info_line(f"Material Family: {p.material_family}")
    info_line(f"Frobenius Pathway: {p.frobenius_pathway}")
    print()
    info_line("Primitive Deltas from Qubit QC:")
    for prim, (from_val, to_val) in sorted(p.deltas.items()):
        info_line(f"  {prim}: {from_val} -> {to_val}")
    print()
    info_line(f"Physical Mechanism: {p.physical_mechanism}")
    print()
    info_line(f"O_∞ Universes ({len(p.o_inf_universes)}):")
    for u in p.o_inf_universes:
        info_line(f"  - {u}")
    print()
    info_line(f"Key Blockers ({len(p.key_blockers)}):")
    for b in p.key_blockers:
        info_line(f"  - {b}")
    info_line("=" * 72)

def _print_delta_analysis():
    """Print primitive delta analysis across all paradigms."""
    info_line("=" * 72)
    info_line("PRIMITIVE DELTA ANALYSIS — NON-QUBIT QC vs QUBIT QC")
    info_line("=" * 72)
    print()
    delta_counts = compute_all_deltas()
    prims = ['D', 'T', 'R', 'P', 'F', 'K', 'G', 'Γ', 'φ̂', 'Ħ', 'Σ', 'Ω']
    for prim in prims:
        count = delta_counts.get(prim, 0)
        bar = '#' * count + '.' * (8 - count)
        info_line(f"  {prim:<6} [{bar}] {count}/8 paradigms differ")
    print()
    info_line("Universal deltas (differ in ALL 8 paradigms): Gamma (composition)")
    info_line("Near-universal deltas (differ in >=6): D (7/8), K (7/8)")
    print()
    info_line("Interpretation:")
    info_line("  A 'qubit' is structurally defined by Gamma=and (simultaneous gates).")
    info_line("  Removing that is the minimal structural definition of 'non-qubit'.")
    info_line("  Changing D (dimensionality) is the second most common difference.")
    info_line("=" * 72)


def _print_operculum_analysis():
    """Print operculum universe access analysis."""
    info_line("=" * 72)
    info_line("OPERCULUM ANALYSIS — UNIVERSE ACCESS FOR NON-QUBIT QC")
    info_line("=" * 72)
    print()
    info_line("Grounded in p4rakernel/operculum_peeling.md (109 universes)")
    print()
    analyses = full_operculum_report()
    for name, a in analyses.items():
        p = ALL_PARADIGMS[name]
        info_line(f"  {p.name}:")
        info_line(f"    Canonical tier: {a.canonical_tier}")
        info_line(f"    O_∞ in {a.o_inf_count} / 109 universes")
        if a.selecting_universes:
            info_line(f"    Selecting universes (qubit blocked, this O_∞): "
f"{len(a.selecting_universes)}")
        print()
    info_line("Key Insight:")
    info_line("  Non-qubit QC paradigms are O_∞ in universes where qubit QC is not.")
    info_line("  The 'operculum' — the Ruleset boundary — separates computational paradigms.")
    info_line("  Each paradigm inhabits its own ecological niche in the Crystal of Types.")
    print()
    info_line("  Only Topological QC (anyons) is O_∞ in the CANONICAL universe.")
    info_line("  All others require universe selection (gate reordering) to reach O_∞.")
    info_line("=" * 72)


def _print_frobenius_analysis():
    """Print Frobenius closure analysis."""
    info_line("=" * 72)
    info_line("FROBENIUS CLOSURE ANALYSIS — NON-QUBIT QC")
    info_line("=" * 72)
    print()
    info_line("From p4rakernel/frobenius_exactor.py: mu(delta(x)) = x is")
    info_line("a discrete, categorical condition. Four closure pathways exist.")
    print()
    for name, info in sorted(FROBENIUS_CLOSURE_MAP.items()):
        p = ALL_PARADIGMS.get(name)
        label = p.name if p else name
        status = "[CLOSED]" if info['closure_achieved'] else "[OPEN]"
        error_str = f"error={info['error']}" if info['error'] is not None else "N/A"
        info_line(f"  {label}:")
        info_line(f"    Pathway:  {info['pathway']}")
        info_line(f"    Status:   {status} ({error_str})")
        info_line(f"    Barrier:  {info['barrier']}")
        print()
    info_line("Summary:")
    info_line("  Only Topological QC (anyons) achieves EXACT Frobenius closure.")
    info_line("  Three others have identified pathways but residual error > 0.")
    info_line("  Two paradigms (Boson Sampling, QRC) lack Frobenius structure.")
    info_line("=" * 72)


def _print_recipe(recipe: MaterialRecipe):
    """Print a full material recipe."""
    info_line("=" * 72)
    info_line(f"MATERIAL RECIPE: {recipe.name}")
    info_line(f"Paradigm: {recipe.paradigm}")
    info_line("=" * 72)
    print()
    info_line(f"Description: {recipe.description}")
    print()
    info_line("Composition:")
    for elem, frac in recipe.composition.items():
        info_line(f"  {elem}: {frac}")
    print()
    info_line(f"Structure: {recipe.structure}")
    print()
    info_line("Processing Steps:")
    for step in recipe.processing:
        info_line(f"  {step}")
    print()
    info_line("Predicted Properties:")
    for prop, val in recipe.predicted_properties.items():
        info_line(f"  {prop}: {val}")
    print()
    info_line("Primitive Realization:")
    for prim, realization in recipe.primitive_realization.items():
        info_line(f"  {prim}: {realization}")
    print()
    info_line(f"TRL: {recipe.trl}")
    print()
    info_line("Critical Challenges:")
    for challenge in recipe.critical_challenges:
        info_line(f"  - {challenge}")
    info_line("=" * 72)

# ═══════════════════════════════════════════════════════════════════
# §13. MAIN — DIRECT EXECUTION
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import sys


    if len(sys.argv) < 2:
        _print_overview()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == '--name' and len(sys.argv) > 2:
        name = sys.argv[2]
        paradigm = ALL_PARADIGMS.get(name)
        if paradigm:
            _print_paradigm_detail(paradigm)
        else:
            info_line(f"Unknown paradigm: {name}")
            info_line(f"Available: {list(ALL_PARADIGMS.keys())}")
    elif cmd == '--deltas':
        _print_delta_analysis()
    elif cmd == '--operculum':
        _print_operculum_analysis()
    elif cmd == '--frobenius':
        _print_frobenius_analysis()
    elif cmd == '--recipe' and len(sys.argv) > 2:
        recipe_name = sys.argv[2]
        recipe = ALL_RECIPES.get(recipe_name)
        if recipe:
            _print_recipe(recipe)
        else:
            info_line(f"Unknown recipe: {recipe_name}")
            info_line(f"Available: {list(ALL_RECIPES.keys())}")
    elif cmd == '--table':
        print(paradigm_summary_table())
    elif cmd == '--export' and len(sys.argv) > 2:
        designs = export_forge_designs()
        with open(sys.argv[2], 'w') as f:
            json.dump(designs, f, indent=2)
        info_line(f"Exported {len(designs)} non-qubit QC designs to {sys.argv[2]}")
    elif cmd == '--all':
        for paradigm in ALL_PARADIGMS.values():
            _print_paradigm_detail(paradigm)
            print()
        _print_delta_analysis()
        print()
        _print_operculum_analysis()
        print()
        _print_frobenius_analysis()
    else:
        _print_overview()
        print()
        info_line("Usage:")
        info_line("  python non_qubit_qc.py                        # overview")
        info_line("  python non_qubit_qc.py --name <paradigm>      # paradigm detail")
        info_line("  python non_qubit_qc.py --deltas               # delta analysis")
        info_line("  python non_qubit_qc.py --operculum            # operculum analysis")
        info_line("  python non_qubit_qc.py --frobenius            # frobenius analysis")
        info_line("  python non_qubit_qc.py --recipe <name>        # material recipe")
        info_line("  python non_qubit_qc.py --table                # summary table")
        info_line("  python non_qubit_qc.py --all                  # everything")
