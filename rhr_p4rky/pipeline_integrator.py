#!/usr/bin/env python3
"""
pipeline_integrator.py — Unified Pipeline Integration for Physical Predictor
=============================================================================

Bridges the MoDoT-grounded physical_predictor into ALL red-hot_rebis pipelines:

  1. material_forge  → adds quantitative properties to MaterialDesign
  2. ch3mpiler       → adds thermochemical scoring to retrosynthesis ranking
  3. serpent_rod     → adds folding stability & binding affinity to protein designs
  4. sophick_forge   → adds energetics to alchemical transformations
  5. antibody_designer → adds binding thermodynamics to antibody designs

Every prediction is grounded in the 7 verified MoDoT constant modules
(*.lean) from p4rakernel — not fitted parameters.

Author: Lando⊗⊙perator
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
import json, math, sys
from pathlib import Path
from dataclasses import dataclass, field

# ═══════════════════════════════════════════════════════════════════
# §0. IMPORTS
# ═══════════════════════════════════════════════════════════════════

try:
    from rhr_p4rky.physical_predictor import (
        predict_from_tuple, predict_from_name, format_prediction,
        get_thermochemical_score, get_material_quality_score,
        get_protein_design_score, PhysicalPrediction,
    )
    HAS_PREDICTOR = True
except ImportError:
    HAS_PREDICTOR = False

try:
    from shared.primitives import ORDINALS, WEIGHTS, CATALOG
    HAS_CATALOG = True
except ImportError:
    HAS_CATALOG = False


# ═══════════════════════════════════════════════════════════════════
# §1. MATERIAL FORGE INTEGRATOR
# ═══════════════════════════════════════════════════════════════════

def augment_material_design(name: str, ig_tuple: Tuple[str, ...]) -> Dict[str, Any]:
    """Compute full quantitative physical properties for a material design.
    
    Returns a dict with computed values that can be merged into 
    MaterialDesign.predicted_properties.
    """
    if not HAS_PREDICTOR:
        return {'error': 'physical_predictor not available'}
    
    pred = predict_from_tuple(name, ig_tuple)
    scores = get_material_quality_score(pred)
    
    return {
        '_quantitative': pred.to_dict(),
        '_quality_scores': scores,
        'Young_modulus_GPa': round(pred.young_modulus_GPa, 1),
        'Shear_modulus_GPa': round(pred.shear_modulus_GPa, 1),
        'Bulk_modulus_GPa': round(pred.bulk_modulus_GPa, 1),
        'Tensile_strength_MPa': round(pred.tensile_strength_MPa, 1),
        'Fracture_toughness_MPam05': round(pred.fracture_toughness_MPam05, 2),
        'Band_gap_eV': round(pred.band_gap_eV, 3),
        'Dielectric_constant': round(pred.dielectric_constant, 1),
        'Electrical_conductivity_Sm': pred.electrical_conductivity_Sm,
        'Debye_temperature_K': round(pred.debye_temperature_K, 0),
        'Thermal_conductivity_WmK': round(pred.thermal_conductivity_WmK, 1),
        'Melting_temperature_K': round(pred.melting_temperature_K, 0),
        'Topological_gap_meV': round(pred.topological_protection_energy_meV, 2),
        'Sensitivity_enhancement': pred.sensitivity_enhancement,
        'Curie_temperature_K': round(pred.curie_temperature_K, 0),
        'Thermochemical_score': round(get_thermochemical_score(pred), 3),
    }


# ═══════════════════════════════════════════════════════════════════
# §2. CH3MPILER INTEGRATOR
# ═══════════════════════════════════════════════════════════════════

def get_disconnection_thermochemistry(product_tuple: Tuple[str, ...]) -> Dict[str, float]:
    """Compute thermochemical properties for a retrosynthetic disconnection product.
    
    Returns dict with:
      - thermochemical_score: 0-1 feasibility
      - bond_energy_kJmol: predicted bond strength
      - band_gap_eV: electronic properties of product
      - melting_temp_K: processing temperature
      - folding_stability: for protein/peptide targets
    """
    if not HAS_PREDICTOR or len(product_tuple) < 12:
        return {'thermochemical_score': 0.5}
    
    pred = predict_from_tuple('disconnection_product', product_tuple)
    return {
        'thermochemical_score': round(get_thermochemical_score(pred), 3),
        'bond_energy_kJmol': round(pred.bond_energy_kJmol, 1),
        'band_gap_eV': round(pred.band_gap_eV, 3),
        'melting_temp_K': round(pred.melting_temperature_K, 0),
        'folding_stability_kcal': round(pred.folding_stability_kcal, 2),
    }


# ═══════════════════════════════════════════════════════════════════
# §3. SERPENT ROD INTEGRATOR
# ═══════════════════════════════════════════════════════════════════

def get_protein_physical_properties(sequence: str) -> Dict[str, Any]:
    """Compute folding and binding properties from an amino acid sequence.
    
    Uses the 12-primitive amino acid encoding to construct an IG tuple
    from the sequence, then predicts physical properties.
    
    This lets ANY sequence get a quantitative folding stability prediction
    without running expensive molecular dynamics.
    """
    if not HAS_PREDICTOR:
        return {'error': 'predictor unavailable'}
    
    # Map sequence to 12-primitive tuple by counting AA primitive activations
    aa_to_prim = {
        'M': '𐐦', 'W': '𐐸', 'C': '𐐾',
        'Y': '𐐿', 'F': '𐐐', 'I': '𐐧',
        'H': '𐐲', 'N': '𐐠', 'Q': '⊙',
        'D': '𐐖', 'K': '𐐙', 'E': '𐐭',
    }
    prim_order = ['𐐦', '𐐸', '𐐾', '𐐿',
                  '𐐐', '𐐧', '𐐲', '𐐠',
                  '⊙', '𐐖', '𐐙', '𐐭']
    
    # Count primitives in the sequence
    from collections import Counter
    prim_counts = Counter()
    for aa in sequence.upper():
        if aa in aa_to_prim:
            prim_counts[aa_to_prim[aa]] += 1
    
    # Build tuple: choose dominant primitive for each position
    # (simplified: for now, just take the mode from the sequence)
    if not prim_counts:
        return {'error': 'no activated AAs in sequence'}
    
    return _compute_protein_from_tuple(prim_counts, len(sequence))


def _compute_protein_from_tuple(prim_counts, seq_len):
    """Helper: build tuple from primitive counts and predict."""
    # Build a representative tuple from the primitives present
    tup = (
        '𐐦' if '𐐦' in prim_counts else '𐐪',  # D
        '𐐸' if '𐐸' in prim_counts else '𐐡',  # T  
        '𐐾' if '𐐾' in prim_counts else '𐐩',  # R
        '𐐿' if '𐐿' in prim_counts else '𐐗',  # P
        '𐐐' if '𐐐' in prim_counts else '𐐱',  # F
        '𐐧' if '𐐧' in prim_counts else '𐐺',  # K
        '𐐲' if '𐐲' in prim_counts else '𐐚',  # G
        '𐐠' if '𐐠' in prim_counts else '𐐝',  # Gamma
        '⊙' if '⊙' in prim_counts else '𐐢',          # Phi
        '𐐖' if '𐐖' in prim_counts else '𐐓',  # H
        '𐐙' if '𐐙' in prim_counts else '𐐕',  # S
        '𐐭' if '𐐭' in prim_counts else '𐐷',  # Omega
    )
    
    pred = predict_from_tuple('protein_' + str(seq_len), tup)
    return {
        'folding_stability_kcal': round(pred.folding_stability_kcal, 2),
        'binding_affinity_kcal': round(pred.binding_affinity_kcal, 2),
        'enzymatic_turnover_s': pred.enzymatic_turnover_s,
        'thermochemical_score': round(get_thermochemical_score(pred), 3),
        'protein_design_score': get_protein_design_score(pred),
        'sequence_length': seq_len,
        'activated_primitive_count': len(prim_counts),
    }


# ═══════════════════════════════════════════════════════════════════
# §4. CATALOG BATCH PREDICTOR
# ═══════════════════════════════════════════════════════════════════

def batch_predict_all() -> Dict[str, Dict[str, Any]]:
    """Predict physical properties for ALL catalog entries."""
    results = {}
    if not HAS_CATALOG:
        return {'error': 'catalog not available'}
    
    for name, entry in CATALOG.items():
        if 'tuple' in entry:
            try:
                t = tuple(entry['tuple'])
                aug = augment_material_design(name, t)
                results[name] = aug
            except Exception as e:
                results[name] = {'error': str(e)}
    return results


# ═══════════════════════════════════════════════════════════════════
# §5. APPLICATION FINDER
# ═══════════════════════════════════════════════════════════════════

def find_best_applications(name: str, ig_tuple: Tuple[str, ...]) -> List[str]:
    """Find best real-world applications for a structural type based on 
    its quantitative physical properties."""
    if not HAS_PREDICTOR:
        return ['physical_predictor not available']
    
    pred = predict_from_tuple(name, ig_tuple)
    scores = get_material_quality_score(pred)
    apps = []
    
    if scores['structural'] > 0.7:
        apps.append(f'High-strength structural material ({pred.young_modulus_GPa:.0f} GPa)')
    if scores['electronic'] > 0.5:
        apps.append(f'Conductive electrode (σ={pred.electrical_conductivity_Sm:.2e} S/m)')
    if scores['topological'] > 0.3:
        apps.append(f'Topological quantum device (gap={pred.topological_protection_energy_meV:.1f} meV)')
    if scores['sensing'] > 0.1:
        apps.append(f'Ultra-sensitive sensor ({pred.sensitivity_enhancement:.1e}x enhancement)')
    if 0.5 < pred.band_gap_eV < 3.0:
        apps.append(f'Semiconductor (E_g={pred.band_gap_eV:.2f} eV)')
    if pred.band_gap_eV > 3.0:
        apps.append(f'Wide-bandgap insulator/UV optoelectronics (E_g={pred.band_gap_eV:.2f} eV)')
    if pred.thermal_conductivity_WmK > 100:
        apps.append(f'Thermal management (κ={pred.thermal_conductivity_WmK:.0f} W/m·K)')
    if pred.topological_protection_energy_meV > 50:
        apps.append('Quantum computing (Majorana qubit host)')
    if abs(pred.folding_stability_kcal) > 10:
        apps.append(f'Stable protein scaffold (ΔG={pred.folding_stability_kcal:.1f} kcal/mol)')
    
    return apps if apps else ['General purpose material']
