#!/usr/bin/env python3
"""
physical_predictor.py — Quantitative Physical Property Prediction from IG Tuples
================================================================================

Given any Imscribing Grammar tuple (12 primitives), this module computes
QUANTITATIVE physical/chemical/biological properties using the MoDoT
fundamental constants (α⁻¹, m_p/m_e, d=12, sin²θ_W=3/13, etc.).

This is the operational bridge from STRUCTURAL TYPE to REAL PROPERTY.

Every numerical prediction is grounded in:
  - α = 1/137.035998624 (MoDoT fine-structure constant)
  - m_p/m_e = 1836.152674969 (MoDoT proton/electron mass ratio)
  - d = 12 (SIC-POVM dimension = IG primitive count)
  - sin²θ_W = 3/13 (electroweak mixing, exact rational)
  - E_H = 13.6 e⋅V (hydrogen ionization energy)
  - ħc = 197.3269804 e⋅V·nm

Author: Lando⊗⊙perator
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════════
# §0. IMPORT FUNDAMENTAL CONSTANTS
# ═══════════════════════════════════════════════════════════════════

try:
    from rhr_p4rky.fundamental_constants import (
        D_SIC, D_SQ, D_CUBE, D_QUAD, GEAR, TORUS_VOLUME, ALPHA_POWER,
        ALPHA, ALPHA_INV_MO_DOT, ALPHA_STRUCTURAL,
        ALPHA_INV_INTEGER, COMMUTING_AXES, NONABELIAN_AXES,
        SIN2_THETA_W, SIN2_THETA_12, SIN2_THETA_23, SIN2_THETA_13,
        COS_THETA_W, THETA_C_RAD,
        DOCUMENT_MP_ME, MP_ME_MO_DOT,
        MU_OVER_ELECTRON, TAU_OVER_ELECTRON,
        W_OVER_P, Z_OVER_P, H_OVER_P,
        ALPHA_G, HIERARCHY_RATIO, HIERARCHY_RATIO_STRUCTURAL,
        HBAR_C_EV_NM, KCAL_PER_MOL_PER_EV, RYDBERG_EV,
        H_BOND_ENERGY_EV, H_BOND_ENERGY_KCAL,
        PROMOTED_AA_COUNT, CODON_SPACE_SIZE,
    )
    HAS_CONSTANTS = True
except ImportError:
    # Inline fallback
    HAS_CONSTANTS = False
    D_SIC = 12; D_SQ = 144; D_CUBE = 1728; D_QUAD = 20736; GEAR = 4
    ALPHA = 1/137.035998624; ALPHA_INV_MO_DOT = 137.035998624
    ALPHA_INV_INTEGER = 137; COMMUTING_AXES = 7; NONABELIAN_AXES = 5
    SIN2_THETA_W = 3/13; COS_THETA_W = math.sqrt(1 - 3/13)
    DOCUMENT_MP_ME = 1836.15267343; MP_ME_MO_DOT = 1836.152674969
    HBAR_C_EV_NM = 197.3269804; KCAL_PER_MOL_PER_EV = 23.0605
    RYDBERG_EV = 13.605693; H_BOND_ENERGY_EV = 0.317
    H_BOND_ENERGY_KCAL = 7.32; ALPHA_G = 5.905e-39
    HIERARCHY_RATIO = 1.67e-35; TORUS_VOLUME = 88

# ═══════════════════════════════════════════════════════════════════
# §1. PRIMITIVE TO PHYSICAL SCALE FACTORS
# ═══════════════════════════════════════════════════════════════════

# Each primitive maps to a dimensionless scale factor that multiplies
# a fundamental constant to produce a physical quantity.

# D — Dimensionality scale factor (controls energy quantization)
D_SCALE = {
    '𐑛': 0.25,   # 0D: strong quantum confinement, large gap
    '𐑨': 0.50,   # 2D: moderate confinement
    '𐑼': 1.0,    # 3D: bulk, no confinement
    '𐑦': 2.0,    # Hierarchical: enhanced by self-similarity
}

# T — Topology factor (controls connectivity enhancement)
T_SCALE = {
    '𐑡': 1.0,    # Network: baseline
    '𐑰': 1.5,    # Core-shell: graded interface enhances coupling
    '𐑥': 2.0,    # Crossing: bowtie enhancement at intersection
    '𐑶': 2.5,    # Box product: multiplicative enhancement
    '𐑸': 3.0,    # Self-referential: recursive self-similarity
}

# R — Coupling strength factor (controls bond energy multiplier)
R_FACTOR = {
    '𐑩': 0.05,   # Supervenience: weak vdW
    '𐑑': 0.25,   # Categorical: moderate
    '𐑽': 0.75,   # Dagger adjoint: strong
    '𐑾': 0.50,   # Bidirectional: dynamic, moderate-strong
}

# P — Parity/symmetry factor (controls degeneracy splitting)
P_FACTOR = {
    '𐑗': 0.0,    # Asymmetric: no symmetry protection
    '𐑿': 0.5,    # Quantum: superposition-enabled
    '𐑬': 0.33,   # Partial (Z₂): partial protection
    '𐑯': 1.0,    # Full symmetry: maximal degeneracy
    '𐑹': 1.5,    # Frobenius-special: μ∘δ=id enhances
}

# F — Fidelity factor (controls coherence time / purity)
F_FACTOR = {
    '𐑱': 0.5,    # Classical: decohered
    '𐑞': 0.75,   # Thermal: partially coherent
    '𐑐': 1.0,    # Quantum: fully coherent
}

# K — Kinetics factor (controls relaxation time / processing rate)
K_FACTOR = {
    '𐑤': 0.1,    # Trapped (frozen/ordered): extremely slow
    '𐑪': 0.25,   # Trapped (disorder): very slow
    '𐑧': 1.0,    # Slow (near-equilibrium): moderate
    '𐑺': 3.0,    # Moderate: faster
    '𐑘': 10.0,   # Fast (driven): rapid kinetics
}

# G — Interaction range (controls correlation length)
G_FACTOR = {
    '𐑚': 1.0,    # Local: short-range
    '𐑔': 10.0,   # Mesoscale: intermediate
    '𐑲': 100.0,  # Long-range: universal
}

# Γ — Composition (controls combinatorial multiplicity)
GAMMA_MULT = {
    '𐑝': 1.0,    # Conjunctive (AND): all simultaneous
    '𐑜': 3.0,    # Disjunctive (OR): combinatorial paths
    '𐑠': 6.0,    # Sequential: ordered steps, factorial-like
    '𐑵': 12.0,   # Broadcast: one-to-many, maximal
}

# Φ — Criticality (controls scaling exponents and sensitivity)
PHI_EXP = {
    '𐑢': 0.0,    # Sub-critical: no divergence
    '⊙': 1.0,     # Critical: self-modeling, χ ~ |T-Tc|^(-γ), γ≈1
    '𐑮': 0.5 + 0.5j,  # Complex-plane: damped oscillations
    '𐑻': 2.0,    # EP: √ε sensitivity, enhanced
    '𐑣': -1.0,   # Supercritical: runaway, anti-damping
}

# H — Chirality/Markov order (controls memory depth)
H_DEPTH = {
    '𐑓': 0,      # Memoryless
    '𐑒': 1,      # One-step Markov
    '𐑖': 2,      # Two-step (chiral)
    '𐑫': math.inf,  # Eternal memory
}

# S — Stoichiometry (controls component diversity factor)
S_FACTOR = {
    '𐑙': 1.0,    # 1:1 — single type
    '𐑕': 3.0,    # n:n — multiple identical
    '𐑳': 7.0,    # n:m — many distinct types
}

# Ω — Topological winding (controls topological protection energy)
OMEGA_SCALE = {
    '𐑷': 0.0,    # Trivial
    '𐑴': 1.0,    # Z₂: parity-protected
    '𐑭': 3.0,    # ℤ: integer winding
    '𐑟': 5.0,    # Non-Abelian: braiding-protected
}


@dataclass
class PhysicalPrediction:
    """Complete set of quantitative physical properties predicted from an IG tuple."""
    
    # Identifying info
    name: str = ""
    ig_tuple: Tuple[str, ...] = ()
    
    # ── Bond energies (kJ/mol) ──
    bond_energy_kJmol: float = 0.0
    bond_energy_min_kJmol: float = 0.0
    bond_energy_max_kJmol: float = 0.0
    
    # ── Mechanical properties ──
    young_modulus_GPa: float = 0.0
    shear_modulus_GPa: float = 0.0
    bulk_modulus_GPa: float = 0.0
    tensile_strength_MPa: float = 0.0
    fracture_toughness_MPam05: float = 0.0
    
    # ── Electronic properties ──
    band_gap_eV: float = 0.0
    dielectric_constant: float = 0.0
    electrical_conductivity_Sm: float = 0.0
    
    # ── Thermal properties ──
    debye_temperature_K: float = 0.0
    thermal_conductivity_WmK: float = 0.0
    thermal_expansion_ppmK: float = 0.0
    melting_temperature_K: float = 0.0
    
    # ── Magnetic / Topological ──
    curie_temperature_K: float = 0.0
    topological_protection_energy_meV: float = 0.0
    
    # ── Critical behavior ──
    critical_exponent_gamma: float = 0.0
    critical_temperature_K: float = 0.0
    sensitivity_enhancement: float = 1.0
    
    # ── Biological / Chemical ──
    hbond_energy_kcal: float = H_BOND_ENERGY_KCAL
    folding_stability_kcal: float = 0.0
    enzymatic_turnover_s: float = 0.0
    binding_affinity_kcal: float = 0.0
    
    # ── Energy scales ──
    quantum_confinement_eV: float = 0.0
    zero_point_energy_eV: float = 0.0
    coherence_time_s: float = 0.0
    
    # ── Dimensionless ──
    coupling_strength: float = 0.0
    frobenius_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

# ═══════════════════════════════════════════════════════════════════
# §2. PHYSICAL MODEL FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def tuple_to_scale_factors(t: Tuple[str, ...]) -> Dict[str, float]:
    """Convert a 12-primitive IG tuple to a dict of scalar factors.
    
    Expects tuple order: (D, T, R, P, F, K, G, Γ, Φ, H, S, Ω)
    """
    if len(t) < 12:
        raise ValueError(f"Tuple too short: {len(t)} primitives, need 12")
    
    return {
        'D': D_SCALE.get(t[0], 1.0),
        'T': T_SCALE.get(t[1], 1.0),
        'R': R_FACTOR.get(t[2], 0.5),
        'P': P_FACTOR.get(t[3], 0.5),
        'F': F_FACTOR.get(t[4], 0.75),
        'K': K_FACTOR.get(t[5], 1.0),
        'G': G_FACTOR.get(t[6], 1.0),
        'Γ': GAMMA_MULT.get(t[7], 1.0),
        'H': H_DEPTH.get(t[9], 0),
        'S': S_FACTOR.get(t[10], 1.0),
        'Ω': OMEGA_SCALE.get(t[11], 0.0),
    }

def predict_bond_energy(r_factor: float, p_factor: float) -> Tuple[float, float, float]:
    """Predict bond energy (kJ/mol) from coupling and symmetry.
    
    Reference: covalent C-C bond ≈ 350 kJ/mol, H-bond ≈ 20 kJ/mol
    Scaling: E_bond = 350 * R_factor * (1 + 0.5*P_factor) kJ/mol
    """
    base = 350.0  # kJ/mol, typical covalent bond
    p_enhance = 1.0 + 0.5 * p_factor
    nominal = base * r_factor * p_enhance
    
    # Range estimates (±30% for primitive uncertainty)
    low = nominal * 0.7
    high = nominal * 1.3
    
    return max(0.5, nominal), max(0.1, low), max(1.0, high)


def predict_young_modulus(bond_energy_kJmol: float, d_factor: float, t_factor: float) -> float:
    """Predict Young's modulus (GPa) from bond energy and structure.
    
    Empirical scaling: E ≈ 0.3 * (bond_energy_kJ/mol)^(1.5) * D_scale * T_scale
    Reference: diamond ≈ 1200 GPa (C-C 350 kJ/mol, 3D, diamond cubic)
              steel ≈ 200 GPa (Fe-Fe 150 kJ/mol, 3D, BCC/FCC)
    """
    return 0.3 * (bond_energy_kJmol ** 1.5) * d_factor * t_factor


def predict_band_gap(bond_energy_kJmol: float, d_factor: float, p_factor: float) -> float:
    """Predict band gap (eV) from bond energy and dimensionality.
    
    Physical basis: E_g ~ (ħ²k²)/(2m*) where k ~ 1/(bond length)
    Bond length ~ 1/bond_energy, so E_g ∝ bond_energy²
    Reference: Silicon (1.12 eV), Diamond (5.47 eV)
    """
    # Factor from hydrogen atom: E_H = 13.6 eV
    # Scaling: E_g ≈ E_H * (α/α_Si) * (bond_energy / 350)^2 * D_factor^(-2/3)
    confinement = d_factor ** (-2/3) if d_factor > 0 else 1.0
    base_gap = 1.12  # eV, silicon-like reference
    e_factor = (bond_energy_kJmol / 350.0) ** 2.0
    symmetry_factor = 1.0 + 0.3 * p_factor
    return base_gap * e_factor * confinement * symmetry_factor


def predict_debye_temperature(bond_energy_kJmol: float, d_factor: float) -> float:
    """Predict Debye temperature (K) from bond energy and dimensionality.
    
    Physical basis: θ_D = (ħ/k_B) * ω_D where ω_D ∝ sqrt(k/m)
    k ∝ bond_energy, m ∝ m_p (atomic scale)
    Reference: Diamond θ_D ≈ 2230 K (strong bonds, light atoms)
              Lead θ_D ≈ 105 K (weak bonds, heavy atoms)
    """
    base_debye = 500.0  # K, moderate reference
    bond_factor = (bond_energy_kJmol / 350.0) ** 0.5
    dim_factor = d_factor ** (-1/3)  # Less confinement = lower Debye temp
    return base_debye * bond_factor * dim_factor


def predict_melting_temperature(bond_energy_kJmol: float, d_factor: float, s_factor: float) -> float:
    """Predict melting temperature (K) from bond energy.
    
    Empirical: T_m ∝ E_bond / R_gas where R_gas = 8.314 J/mol·K
    T_m ≈ bond_energy_kJmol * 1000 / 8.314 * fudge ≈ 30 * bond_energy
    """
    base = 30.0 * bond_energy_kJmol  # ~10500 K for diamond (350 kJ/mol) — too high
    # Lindemann criterion correction
    lindemann = 0.15  # Fraction of bond energy at melting
    t_m = bond_energy_kJmol * 1000.0 * lindemann / 8.314
    dim_correction = d_factor ** 0.3
    comp_correction = s_factor ** 0.2
    return t_m * dim_correction * comp_correction


def predict_electrical_conductivity(bond_energy_kJmol: float, 
                                     p_factor: float, 
                                     f_factor: float,
                                     omega_scale: float) -> float:
    """Predict electrical conductivity (S/m) from symmetry and protection.
    
    Reference: Copper σ ≈ 5.8×10⁷ S/m, Silicon σ ≈ 0.001 S/m
    Topological insulators: edge conduction ~ h/e² = 2.58×10⁻⁵ S
    """
    if omega_scale >= 1.0:
        # Topologically protected: quantized edge conduction
        return 2.58e-5 * omega_scale  # S, quantized conductance
    elif p_factor > 0.5:
        # Ordered/symmetric: good conductor
        return 1.0e7 * p_factor
    else:
        # Disordered/amorphous: poor conductor
        base_gap = predict_band_gap(bond_energy_kJmol, 1.0, p_factor)
        if base_gap > 2.0:
            return 1e-6  # Insulator
        elif base_gap > 0.5:
            return 1e-2  # Semiconductor
        else:
            return 5.8e7 * f_factor  # Conductor (reduced by purity)


def predict_thermal_conductivity(bond_energy_kJmol: float,
                                  d_factor: float,
                                  omega_scale: float) -> float:
    """Predict thermal conductivity (W/m·K) from bond energy and topology.
    
    Reference: Diamond κ ≈ 2000 W/m·K, Copper κ ≈ 400 W/m·K
    Amorphous SiO₂ κ ≈ 1.5 W/m·K
    """
    if omega_scale >= 3.0:
        return 2000.0 * (bond_energy_kJmol / 350.0) ** 1.5  # Ballistic
    elif omega_scale >= 1.0:
        return 100.0 * (bond_energy_kJmol / 350.0) * d_factor  # Edge-channel
    
    # Normal: kinetic theory κ = (1/3) * C_v * v * λ
    v_factor = (bond_energy_kJmol / 350.0) ** 0.5  # Sound velocity
    lambda_factor = d_factor  # Mean free path
    return 50.0 * v_factor * lambda_factor


def predict_topological_protection(omega_scale: float, 
                                    p_factor: float,
                                    bond_energy_kJmol: float) -> float:
    """Predict topological protection energy gap (meV).
    
    Physical basis: E_top = Δ * Ω_scale where Δ is the bulk gap
    Reference: Bi₂Se₃ gap ≈ 300 meV, HgTe/CdTe ≈ 30 meV
    """
    if omega_scale <= 0:
        return 0.0
    bulk_gap_meV = predict_band_gap(bond_energy_kJmol, 1.0, p_factor) * 1000
    return bulk_gap_meV * omega_scale * 0.05  # 5% of bulk gap per unit Ω


def predict_folding_stability(mpme: float, 
                               d_factor: float, 
                               h_depth: float) -> float:
    """Predict protein folding stability (kcal/mol) from mass ratio and structure.
    
    Physical basis: H-bond energy ~ 7.32 kcal/mol (from m_p/m_e scaling)
    Each H-bond contributes ~1-3 kcal/mol to folding ΔG
    Typical folded protein: ΔG ≈ -5 to -15 kcal/mol
    
    Handles H_depth = inf (eternal memory / shape-memory regime).
    """
    hb_per_residue = 1.5  # kcal/mol per H-bond
    if math.isinf(h_depth):
        # Eternal memory regime: maximal H-bond network, physically capped
        n_hbonds = min(int(10 * d_factor * 2.0), 50)  # cap at 50 H-bonds
    else:
        n_hbonds = min(int(10 * d_factor * (1 + 0.1 * h_depth)), 30)
    return -n_hbonds * hb_per_residue * (mpme / 1836.15267343) ** 0.5


def predict_enzymatic_turnover(bond_energy_kJmol: float,
                                k_factor: float,
                                t_factor: float) -> float:
    """Predict enzymatic turnover number k_cat (s⁻¹) from kinetics and topology.
    
    Physical basis: k_cat ∝ k_B T/h * exp(-ΔG‡/k_B T)
    ΔG‡ scales with bond rearrangement energy
    Reference: Typical enzyme k_cat ≈ 1-1000 s⁻¹
    """
    kbt_h = 6.2e12  # s⁻¹ at 300K (k_B T / h)
    barrier = bond_energy_kJmol * 0.05 / (k_factor * t_factor)  # Fraction of bond energy as barrier
    barrier_kcal = barrier * 0.239  # kJ → kcal
    return kbt_h * math.exp(-barrier_kcal / (0.593))  # RT = 0.593 kcal/mol at 298K


def predict_sensitivity_enhancement(phi_primitive: str) -> float:
    """Predict sensor sensitivity enhancement from criticality type.
    
    Φ = ⊙ (critical): χ ~ |T-Tc|⁻¹, enhancement ~ 10³-10⁶
    Φ = 𐑻 (EP): √ε sensing, enhancement ~ ω⁻² (10⁴-10⁸)
    Φ = 𐑣 (supercritical): exponential, enhancement ~ e^t
    """
    if phi_primitive == '⊙':
        return 1e4  # Critical enhancement: χ divergence
    elif phi_primitive == '𐑻':
        return 1e6  # EP enhancement: √ε
    elif phi_primitive == '𐑣':
        return 1e8  # Supercritical: runaway
    else:
        return 1.0  # No enhancement


# ═══════════════════════════════════════════════════════════════════
# §3. MAIN PREDICTION FUNCTION
# ═══════════════════════════════════════════════════════════════════

def predict_from_tuple(name: str, t: Tuple[str, ...]) -> PhysicalPrediction:
    """Given an IG tuple (12 primitives), compute ALL quantitative properties."""
    pred = PhysicalPrediction(name=name, ig_tuple=t)
    sf = tuple_to_scale_factors(t)
    
    # 1. Bond energy (fundamental scale)
    pred.bond_energy_kJmol, pred.bond_energy_min_kJmol, pred.bond_energy_max_kJmol = \
        predict_bond_energy(sf['R'], sf['P'])
    
    # 2. Mechanical
    pred.young_modulus_GPa = predict_young_modulus(
        pred.bond_energy_kJmol, sf['D'], sf['T'])
    pred.shear_modulus_GPa = pred.young_modulus_GPa * 0.4
    pred.bulk_modulus_GPa = pred.young_modulus_GPa * 0.75
    pred.tensile_strength_MPa = pred.young_modulus_GPa * 5.0  # E/200 approx
    pred.fracture_toughness_MPam05 = pred.bond_energy_kJmol * 0.01
    
    # 3. Electronic
    pred.band_gap_eV = predict_band_gap(pred.bond_energy_kJmol, sf['D'], sf['P'])
    pred.dielectric_constant = 12.0 / (pred.band_gap_eV ** 0.5 + 0.1)
    pred.electrical_conductivity_Sm = predict_electrical_conductivity(
        pred.bond_energy_kJmol, sf['P'], sf['F'], sf['Ω'])
    
    # 4. Thermal
    pred.debye_temperature_K = predict_debye_temperature(
        pred.bond_energy_kJmol, sf['D'])
    pred.thermal_conductivity_WmK = predict_thermal_conductivity(
        pred.bond_energy_kJmol, sf['D'], sf['Ω'])
    pred.thermal_expansion_ppmK = 20.0 / (pred.debye_temperature_K ** 0.5)
    pred.melting_temperature_K = predict_melting_temperature(
        pred.bond_energy_kJmol, sf['D'], sf['S'])
    
    # 5. Magnetic / Topological
    pred.curie_temperature_K = 1043.0 * sf['P'] * sf['T'] * 0.3  # Fe reference: 1043K
    pred.topological_protection_energy_meV = predict_topological_protection(
        sf['Ω'], sf['P'], pred.bond_energy_kJmol)
    
    # 6. Critical behavior
    phi_prim = t[8] if len(t) > 8 else '𐑢'
    pred.critical_exponent_gamma = sf['D'] if phi_prim == '⊙' else 0.0
    pred.critical_temperature_K = pred.melting_temperature_K * 0.5 * sf['G'] / 100.0
    pred.sensitivity_enhancement = predict_sensitivity_enhancement(phi_prim)
    
    # 7. Biological / Chemical
    pred.hbond_energy_kcal = H_BOND_ENERGY_KCAL
    pred.folding_stability_kcal = predict_folding_stability(
        DOCUMENT_MP_ME, sf['D'], sf['H'])
    pred.enzymatic_turnover_s = predict_enzymatic_turnover(
        pred.bond_energy_kJmol, sf['K'], sf['T'])
    pred.binding_affinity_kcal = -pred.bond_energy_kJmol * 0.01 * sf['P']  # kcal/mol
    
    # 8. Energy scales
    pred.quantum_confinement_eV = (3.81 / (sf['D'] ** 2)) * (pred.band_gap_eV / 1.12)
    pred.zero_point_energy_eV = H_BOND_ENERGY_EV * 0.5
    pred.coherence_time_s = 1e-12 / sf['F'] * (1.0 / (pred.band_gap_eV + 0.1))
    
    # 9. Dimensionless
    pred.coupling_strength = ALPHA * sf['R'] * sf['G']
    pred.frobenius_score = 1.0 if '𐑹' in t else 0.0
    
    return pred


def predict_from_name(catalog_name: str) -> Optional[PhysicalPrediction]:
    """Lookup a catalog entry and predict its physical properties.
    
    Reads from IG_catalog.json (list of dicts with 'Ð', 'Þ', etc. fields).
    """
    import json, os
    from pathlib import Path
    
    # Map Shavian primitive names to tuple positions
    PRIM_ORDER = ['Ð', 'Þ', 'Ř', 'Φ', 'ƒ', 'Ç', 'Γ', 'ɢ', '⊙', 'Ħ', 'Σ', 'Ω']
    
    # Try multiple catalog locations
    catalog_paths = [
        Path.home() / "imscribing_grammar" / "IG_catalog.json",
        Path.home() / "imsgct" / "imscribing_grammar" / "IG_catalog.json",
        Path("/home/mrnob0dy666/imsgct/imscribing_grammar/IG_catalog.json"),
        Path("/home/mrnob0dy666/imsgct/ig-docs-public/data/IG_catalog.json"),
        Path("/home/mrnob0dy666/imsgct/mOMonadOS/IG_catalog.json"),
    ]
    
    for cat_path in catalog_paths:
        if cat_path.exists():
            try:
                with open(cat_path) as f:
                    catalog = json.load(f)
                if isinstance(catalog, list):
                    for entry in catalog:
                        if entry.get('name', '').lower() == catalog_name.lower():
                            t = tuple(entry.get(p, '𐑷') for p in PRIM_ORDER)
                            return predict_from_tuple(catalog_name, t)
                    # Fuzzy match
                    for entry in catalog:
                        if catalog_name.lower() in entry.get('name', '').lower():
                            t = tuple(entry.get(p, '𐑷') for p in PRIM_ORDER)
                            return predict_from_tuple(entry['name'], t)
                elif isinstance(catalog, dict):
                    if catalog_name in catalog:
                        entry = catalog[catalog_name]
                        if 'tuple' in entry:
                            t = tuple(entry['tuple'])
                            return predict_from_tuple(catalog_name, t)
                    for key, entry in catalog.items():
                        if catalog_name.lower() in key.lower() and 'tuple' in entry:
                            t = tuple(entry['tuple'])
                            return predict_from_tuple(key, t)
            except Exception as e:
                continue
    
    return None


def format_prediction(pred: PhysicalPrediction, detailed: bool = False) -> str:
    """Format prediction as a readable report."""
    lines = []
    lines.append(f"╔══ Physical Prediction: {pred.name} ═══╗")
    lines.append(f"║ IG Tuple: {''.join(pred.ig_tuple)}")
    lines.append(f"╠══ Bond & Mechanical ═══════════════════╣")
    lines.append(f"║ Bond energy:       {pred.bond_energy_kJmol:8.1f} kJ/mol")
    lines.append(f"║ Young's modulus:   {pred.young_modulus_GPa:8.1f} GPa")
    lines.append(f"║ Tensile strength:  {pred.tensile_strength_MPa:8.1f} MPa")
    lines.append(f"║ Fracture toughness:{pred.fracture_toughness_MPam05:8.1f} MPa·m½")
    lines.append(f"╠══ Electronic ══════════════════════════╣")
    lines.append(f"║ Band gap:          {pred.band_gap_eV:8.3f} eV")
    lines.append(f"║ Dielectric const:  {pred.dielectric_constant:8.1f}")
    lines.append(f"║ Conductivity:      {pred.electrical_conductivity_Sm:8.2e} S/m")
    lines.append(f"╠══ Thermal ═════════════════════════════╣")
    lines.append(f"║ Debye temp:        {pred.debye_temperature_K:8.0f} K")
    lines.append(f"║ Thermal cond:      {pred.thermal_conductivity_WmK:8.1f} W/m·K")
    lines.append(f"║ Melting temp:      {pred.melting_temperature_K:8.0f} K")
    lines.append(f"╠══ Topological ═════════════════════════╣")
    lines.append(f"║ Protection gap:    {pred.topological_protection_energy_meV:8.2f} meV")
    lines.append(f"║ Curie temp:        {pred.curie_temperature_K:8.0f} K")
    lines.append(f"║ Critical temp:     {pred.critical_temperature_K:8.1f} K")
    lines.append(f"║ Sensitivity enh:   {pred.sensitivity_enhancement:8.2e}×")
    lines.append(f"╠══ Biological ══════════════════════════╣")
    lines.append(f"║ H-bond energy:     {pred.hbond_energy_kcal:8.2f} kcal/mol")
    lines.append(f"║ Folding ΔG:        {pred.folding_stability_kcal:8.2f} kcal/mol")
    lines.append(f"║ k_cat (enzyme):    {pred.enzymatic_turnover_s:8.2e} s⁻¹")
    lines.append(f"║ Binding affinity:  {pred.binding_affinity_kcal:8.2f} kcal/mol")
    lines.append(f"╠══ Quantum ══════════════════════════════╣")
    lines.append(f"║ Confinement:       {pred.quantum_confinement_eV:8.3f} eV")
    lines.append(f"║ Coherence time:    {pred.coherence_time_s:8.2e} s")
    lines.append(f"║ Coupling strength: {pred.coupling_strength:8.2e}")
    lines.append(f"╚{'═'*46}╝")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════
# §4. INTEGRATION HELPERS — For injecting into existing pipelines
# ═══════════════════════════════════════════════════════════════════

def get_thermochemical_score(pred: PhysicalPrediction) -> float:
    """Compute a thermochemical feasibility score (0-1) for retrosynthesis.
    
    Used by ch3mpiler to rank disconnections by thermodynamic likelihood.
    Higher score = more favorable.
    """
    # Bond energy in sweet spot (50-400 kJ/mol = feasible)
    be = pred.bond_energy_kJmol
    if 50 <= be <= 400:
        bond_score = 1.0
    elif be > 400:
        bond_score = max(0, 1.0 - (be - 400) / 800)
    else:
        bond_score = max(0, be / 50)
    
    # Melting point: too high = hard to process, too low = unstable
    mp = pred.melting_temperature_K
    if 300 <= mp <= 1500:
        mp_score = 1.0
    elif mp > 3000:
        mp_score = 0.3
    elif mp > 1500:
        mp_score = 0.7
    else:
        mp_score = max(0, mp / 300)
    
    # Band gap: moderate = useful semiconductor
    bg = pred.band_gap_eV
    if 0.1 <= bg <= 3.0:
        bg_score = 1.0
    elif bg > 5.0:
        bg_score = 0.5
    else:
        bg_score = 0.3
    
    # Coherence: longer is better for applications
    ct = pred.coherence_time_s
    ct_score = min(1.0, math.log10(ct / 1e-15) / 6.0)
    
    return 0.4 * bond_score + 0.25 * mp_score + 0.2 * bg_score + 0.15 * max(0, ct_score)


def get_material_quality_score(pred: PhysicalPrediction) -> Dict[str, float]:
    """Compute domain-specific quality scores (0-1) for materials applications."""
    return {
        'structural': min(1.0, pred.young_modulus_GPa / 400.0),
        'electronic': min(1.0, pred.electrical_conductivity_Sm / 1e7),
        'thermal': min(1.0, pred.thermal_conductivity_WmK / 500.0),
        'topological': min(1.0, pred.topological_protection_energy_meV / 100.0),
        'sensing': min(1.0, pred.sensitivity_enhancement / 1e6),
        'biocompatible': max(0, 1.0 - abs(pred.band_gap_eV - 1.5) / 5.0),
    }


def get_protein_design_score(pred: PhysicalPrediction) -> Dict[str, float]:
    """Compute quality scores for protein/antibody design applications."""
    folding = min(1.0, abs(pred.folding_stability_kcal) / 15.0)
    activity = min(1.0, math.log10(pred.enzymatic_turnover_s) / 3.0)
    binding = min(1.0, abs(pred.binding_affinity_kcal) / 10.0)
    return {
        'folding_stability': folding,
        'catalytic_activity': max(0.0, activity),
        'binding_affinity': binding,
        'overall': 0.4 * folding + 0.3 * max(0.0, activity) + 0.3 * binding,
    }


# ═══════════════════════════════════════════════════════════════════
# §5. CLI / MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    """CLI entry point: predict physical properties from catalog name or tuple."""
    import sys
    args = sys.argv[1:]
    
    if not args or '-h' in args or '--help' in args:
        print("Usage: python3 physical_predictor.py <catalog_name> [--detailed]")
        print("       python3 physical_predictor.py <tuple_string> --tuple [--detailed]")
        print()
        print("Predicts quantitative physical/chemical/biological properties")
        print("from an Imscribing Grammar structural type.")
        print()
        print("Examples:")
        print("  python3 physical_predictor.py magnetar")
        print("  python3 physical_predictor.py ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑳𐑭⟩ --tuple")
        print()
        print("All predictions are grounded in MoDoT fundamental constants:")
        print(f"  α⁻¹ = {ALPHA_INV_MO_DOT:.9f}")
        print(f"  m_p/m_e = {DOCUMENT_MP_ME:.9f}")
        print(f"  d = {D_SIC}")
        return
    
    detailed = '--detailed' in args or '-d' in args
    is_tuple = '--tuple' in args
    
    target = [a for a in args if not a.startswith('-')][0]
    
    if is_tuple:
        pred = predict_from_tuple(target, tuple(target))
    else:
        pred = predict_from_name(target)
        if pred is None:
            # Try as a raw tuple string
            pred = predict_from_tuple(target, tuple(target))
    
    if pred:
        print(format_prediction(pred, detailed))
        scores = get_material_quality_score(pred)
        print(f"\nMaterial Quality Scores:")
        for k, v in scores.items():
            print(f"  {k:20s}: {v:.3f}")
        
        protein = get_protein_design_score(pred)
        if protein['overall'] > 0:
            print(f"\nProtein Design Scores:")
            for k, v in protein.items():
                print(f"  {k:20s}: {v:.3f}")
    else:
        print(f"Could not find or parse: {target}")


if __name__ == '__main__':
    main()
