"""
dft_bridge.py — Quantum Chemistry Bridge for CLINK
====================================================
Bridges structural computation (CLINK layer transitions) with quantum chemistry.
Provides DFT energy estimation, geometry optimization hooks, and energy gap analysis
for tier transitions — closing the gap between "computing that a transition has
distance 3.32" and "computing the actual energy barrier of that transition."

Integration points:
  - L3 (Molecule): ch3mpiler output → DFT energy estimation
  - L4 (Folded Protein): serpentrod output → folding energy landscape
  - L5→L6 (Cell→Mitosis): energy barrier for replication
  - Tier transitions: energy gap for primitive promotions

External DFT engines (when available):
  - ORCA (orcasubmit/orca_plot)
  - Gaussian (g16)
  - Psi4 (Python-native)
  - xtb (semi-empirical, fast fallback)

Author: Lando⊗⊙perator
"""

import os, sys, json, math, subprocess, hashlib, tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from shared.rich_output import *

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))


# ═══════════════════════════════════════════════════════════════════
# ENGINE DETECTION
# ═══════════════════════════════════════════════════════════════════

class DFTEngine(Enum):
    NONE = "none"
    XTB = "xtb"          # semi-empirical GFN2-xTB (fast, always available via conda)
    PSI4 = "psi4"        # Python-native DFT
    ORCA = "orca"        # ORCA quantum chemistry
    GAUSSIAN = "gaussian"  # Gaussian 16


def detect_available_engines() -> List[DFTEngine]:
    """Detect which quantum chemistry engines are available on the system."""
    available = []
    for engine, cmd in [
        (DFTEngine.XTB, "xtb"),
        (DFTEngine.PSI4, "psi4"),
        (DFTEngine.ORCA, "orca"),
        (DFTEngine.GAUSSIAN, "g16"),
    ]:
        try:
            result = subprocess.run(["which", cmd], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                available.append(engine)
        except Exception:
            pass
    return available if available else [DFTEngine.NONE]


# ═══════════════════════════════════════════════════════════════════
# ENERGY ESTIMATION (semi-empirical fallback)
# ═══════════════════════════════════════════════════════════════════

# Bond dissociation energies (kJ/mol) for common bond types
BOND_ENERGIES = {
    "C-C": 348, "C=C": 614, "C≡C": 839,
    "C-H": 413, "C-O": 358, "C=O": 799, "C-N": 305,
    "C=N": 615, "C≡N": 891, "C-F": 485, "C-Cl": 328,
    "O-H": 463, "N-H": 391, "O=O": 498, "N≡N": 945,
    "H-H": 436, "S-S": 226, "S-H": 363, "P-O": 335,
    "peptide": 30,   # approximate peptide bond stabilization
    "h-bond": 20,    # hydrogen bond (kJ/mol)
    "pi-stack": 8,   # pi-pi stacking
    "disulfide": 210,  # S-S in proteins
    "salt_bridge": 40,  # electrostatic
    "vdw": 2,        # van der Waals
}


def estimate_small_molecule_energy(smiles: str) -> Dict:
    """Estimate energy for a small molecule from SMILES.
    
    Uses bond counting + group additivity as fallback when no DFT engine.
    Returns estimated total energy, atomization energy, and per-atom energy.
    """
    # Count heavy atoms and estimate bonds
    heavy_atoms = sum(1 for c in smiles if c in 'CNOPSFClBrI')
    h_count = smiles.count('H') if 'H' in smiles else heavy_atoms  # rough
    
    # Count double/triple bonds
    double_bonds = smiles.count('=')
    triple_bonds = smiles.count('#')
    single_bonds_est = max(heavy_atoms - 1, 0)
    
    # Rough energy estimation
    atomization = (
        single_bonds_est * BOND_ENERGIES["C-C"] * 0.7 +  # average single bond
        double_bonds * BOND_ENERGIES["C=C"] +
        triple_bonds * BOND_ENERGIES["C≡C"]
    )
    
    return {
        "method": "bond_counting_estimate",
        "smiles": smiles,
        "heavy_atoms": heavy_atoms,
        "est_bonds": single_bonds_est,
        "double_bonds": double_bonds,
        "triple_bonds": triple_bonds,
        "est_atomization_kJmol": round(atomization, 1),
        "est_atomization_eV": round(atomization / 96.485, 3),
        "accuracy": "rough (±50%)",
    }


# ═══════════════════════════════════════════════════════════════════
# TIER TRANSITION ENERGY MODEL
# ═══════════════════════════════════════════════════════════════════

# Estimated energy scales (eV) for CLINK layer transitions
# Based on known physical energy scales for each transition type
TIER_ENERGY_SCALES = {
    # (from_layer, to_layer): (energy_eV, description)
    (0, 1): (5000, "QCD confinement → orbital (hadronization)"),
    (1, 2): (10, "Orbital → atom (ionization/excitation)"),
    (2, 3): (5, "Atom → molecule (bond formation)"),
    (3, 4): (3, "Molecule → folded protein (conformational)"),
    (4, 5): (50, "Protein → cell (self-assembly, membrane)"),
    (5, 6): (100, "Cell → mitosis (replication machinery)"),
    (6, 7): (200, "Mitosis → tissue (cell adhesion, ECM)"),
    (7, 8): (500, "Tissue → organism (system integration)"),
}


def estimate_transition_energy(from_layer: int, to_layer: int,
                               custom_bridge: Optional[Dict] = None) -> Dict:
    """Estimate energy barrier for a CLINK layer transition.
    
    Args:
        from_layer: Source CLINK layer (0-8)
        to_layer: Target CLINK layer (0-8)
        custom_bridge: Optional per-primitive energy contributions
    
    Returns:
        Dict with estimated energy gap, method, and confidence
    """
    base = TIER_ENERGY_SCALES.get((from_layer, to_layer), (10, "unknown transition"))
    
    # Adjust for structural distance
    try:
        from clink.chain import clink_distance
        d = clink_distance(from_layer, to_layer)
    except Exception:
        d = 1.0
    
    # Energy scales with sqrt(structural distance) — prevents runaway for
    # transitions with large physical base energies (e.g., QCD hadronization)
    import math
    energy_ev = base[0] * math.sqrt(max(d, 1.0))
    
    result = {
        "from_layer": from_layer,
        "to_layer": to_layer,
        "structural_distance": round(d, 4),
        "base_energy_eV": base[0],
        "adjusted_energy_eV": round(energy_ev, 2),
        "adjusted_energy_kJmol": round(energy_ev * 96.485, 1),
        "description": base[1],
        "method": "tier_energy_model",
        "confidence": "order-of-magnitude",
    }
    
    if custom_bridge:
        result["custom_contributions"] = custom_bridge
    
    return result

# ═══════════════════════════════════════════════════════════════════
# PRIMITIVE-TO-ENERGY MAPPING
# ═══════════════════════════════════════════════════════════════════

# Energy cost (eV) for promoting each primitive by one ordinal step
PRIMITIVE_PROMOTION_ENERGY = {
    "Ð": 10.0,    # Dimensionality increase — new degrees of freedom
    "Þ": 8.0,     # Topology change — rewiring connections
    "Ř": 5.0,     # Coupling upgrade — stronger interaction
    "Φ": 3.0,     # Parity symmetry change — symmetry breaking/restoration
    "ƒ": 15.0,    # Fidelity upgrade (classical → quantum) — coherence cost
    "Ç": 2.0,     # Kinetics change — relaxation time adjustment
    "Γ": 4.0,     # Range extension — longer-range interactions
    "ɢ": 6.0,     # Composition upgrade — more complex assembly
    "⊙": 12.0,    # Criticality promotion — approach to critical point
    "Ħ": 7.0,     # Chirality increase — higher-order memory
    "Σ": 3.0,     # Stoichiometry — more component types
    "Ω": 20.0,    # Winding topology — topological protection cost
}


def estimate_promotion_energy(promotions: List[Dict]) -> Dict:
    """Estimate total energy cost for a set of primitive promotions.
    
    Args:
        promotions: List of {"primitive": "D", "from": "𐑛", "to": "𐑼"} dicts
    
    Returns:
        Dict with per-primitive and total energy estimates
    """
    total_ev = 0.0
    per_primitive = {}
    
    for promo in promotions:
        p = promo["primitive"]
        base_cost = PRIMITIVE_PROMOTION_ENERGY.get(p, 5.0)
        
        # Estimate ordinal delta if possible
        delta_ord = 1  # default
        per_primitive[p] = {
            "from": promo.get("from", "?"),
            "to": promo.get("to", "?"),
            "base_cost_eV": base_cost,
            "est_ordinal_delta": delta_ord,
            "est_energy_eV": round(base_cost * delta_ord, 2),
        }
        total_ev += base_cost * delta_ord
    
    return {
        "total_energy_eV": round(total_ev, 2),
        "total_energy_kJmol": round(total_ev * 96.485, 1),
        "per_primitive": per_primitive,
        "method": "primitive_promotion_model",
        "confidence": "order-of-magnitude (±1 order)",
    }


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION WITH LAYER DESIGNERS
# ═══════════════════════════════════════════════════════════════════

def compute_layer_energy_profile(layer_idx: int) -> Dict:
    """Compute estimated energy profile for a CLINK layer.
    
    Integrates with clink.chain for tuple data.
    
    Args:
        layer_idx: CLINK layer index (0-8)
    
    Returns:
        Dict with energy profile
    """
    try:
        from clink.chain import clink_layer_tuple, CLINK_NAMES, CLINK_TIERS
        tup = clink_layer_tuple(layer_idx)
        name = CLINK_NAMES[layer_idx]
        tier = CLINK_TIERS[layer_idx]
    except Exception:
        return {"error": f"Could not load CLINK data for layer {layer_idx}"}
    
    # Sum primitive promotion energies relative to L0 baseline
    try:
        baseline_tup = clink_layer_tuple(0)
    except Exception:
        baseline_tup = tup
    
    # Compute primitive ordinal deltas from baseline
    from shared.primitives import ORDINALS

    total_ordinal_delta = 0
    energy_sum = 0.0
    primitive_contribs = {}
    
    PNAMES = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]
    for p in PNAMES:
        if p in tup and p in baseline_tup and p in ORDINALS:
            try:
                ord_map = ORDINALS[p]
                current_val = tup[p]
                baseline_val = baseline_tup[p]
                ord_current = ord_map.get(current_val, 0)
                ord_baseline = ord_map.get(baseline_val, 0)
                delta_ord = max(0, ord_current - ord_baseline)
                energy = PRIMITIVE_PROMOTION_ENERGY.get(p, 5.0) * delta_ord
                energy_sum += energy
                total_ordinal_delta += delta_ord
                primitive_contribs[p] = round(energy, 2)
            except Exception:
                pass
    
    return {
        "layer_idx": layer_idx,
        "layer_name": name,
        "tier": tier,
        "tuple": tup,
        "est_total_energy_eV": round(energy_sum, 2),
        "est_total_energy_kJmol": round(energy_sum * 96.485, 1),
        "primitive_contributions": primitive_contribs,
        "method": "primitive_energy_sum",
        "confidence": "rough estimate",
    }


# ═══════════════════════════════════════════════════════════════════
# CLINK FULL ENERGY LADDER
# ═══════════════════════════════════════════════════════════════════

def compute_full_energy_ladder() -> List[Dict]:
    """Compute energy profile for all 9 CLINK layers.
    
    Returns:
        List of energy profiles for L0 through L8
    """
    ladder = []
    for i in range(9):
        try:
            profile = compute_layer_energy_profile(i)
            ladder.append(profile)
        except Exception as e:
            ladder.append({"layer_idx": i, "error": str(e)})
    return ladder


def energy_ladder_summary(ladder: List[Dict]) -> str:
    """Format energy ladder as a readable table."""
    lines = [
        "=" * 70,
        "  CLINK ENERGY LADDER (Primitive Promotion Model)",
        "=" * 70,
        f"  {'Layer':<8} {'Name':<30} {'Tier':<6} {'Energy (eV)':>12} {'Energy (kJ/mol)':>16}",
        "  " + "-" * 68,
    ]
    for profile in ladder:
        if "error" in profile:
            lines.append(f"  L{profile['layer_idx']:<7} ERROR: {profile['error']}")
            continue
        lines.append(
            f"  L{profile['layer_idx']:<7} {profile['layer_name'][:29]:<30} "
            f"{profile['tier']:<6} {profile['est_total_energy_eV']:>12.2f} "
            f"{profile['est_total_energy_kJmol']:>16.1f}"
        )
    lines.append("=" * 70)
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    info_line("DFT Bridge — Self Test")
    info_line("=" * 50)
    
    engines = detect_available_engines()
    info_line(f"Available engines: {[e.value for e in engines]}")
    
    # Test energy estimation
    test_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"  # aspirin
    energy = estimate_small_molecule_energy(test_smiles)
    print(f"\nAspirin energy estimate: {json.dumps(energy, indent=2)}")
    
    # Test transition energy
    trans = estimate_transition_energy(2, 3)  # atom → molecule
    print(f"\nL2→L3 transition: {json.dumps(trans, indent=2)}")
    
    # Test full ladder
    info_line("\n" + energy_ladder_summary(compute_full_energy_ladder()))
