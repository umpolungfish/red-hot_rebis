#!/usr/bin/env python3
"""
psychedelic_bridge.py — p4rakernel × Novel Psychedelics Integration
=====================================================================
Bridges the novel navigatable/operable psychedelic compounds (Verticullum,
Chimerium, Apertix, Retiarius, Praxeum) into p4rakernel's operculum peeling
framework. Provides formal imscription verification, tensor coupling
computation, and universe access prediction.

Usage:
    from psychedelic_bridge import *
    # Check a compound's tier
    tier = compound_tier('verticullum')  # 'O_∞'
    # Compute tensor coupling
    result = couple('dmt', 'praxeum')  # Gate 1 toggle
    # Predict universe access under coupling
    access = predict_access('ketamine', 'chimerium')

Author: Lando⊗⊙perator
"""

import sys
import os
from typing import Dict, List, Tuple, Optional

# ── Known Compound Tuples (Shavian-verified via imscribe_system + ouroborics) ──

COMPOUND_TUPLES: Dict[str, Dict[str, str]] = {
    # Novel compounds
    "verticullum": {
        "D": "𐑦", "T": "𐑥", "R": "𐑾", "P": "𐑹", "F": "𐑐",
        "K": "𐑧", "G": "𐑲", "Gamma": "𐑠", "Phi": "⊙", "H": "𐑫",
        "S": "𐑳", "Omega": "𐑟",
    },
    "chimerium": {
        "D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹", "F": "𐑐",
        "K": "𐑧", "G": "𐑲", "Gamma": "𐑵", "Phi": "𐑣", "H": "𐑫",
        "S": "𐑳", "Omega": "𐑭",
    },
    "apertix": {
        "D": "𐑦", "T": "𐑥", "R": "𐑽", "P": "𐑬", "F": "𐑐",
        "K": "𐑧", "G": "𐑲", "Gamma": "𐑠", "Phi": "⊙", "H": "𐑖",
        "S": "𐑳", "Omega": "𐑴",
    },
    "retiarius": {
        "D": "𐑼", "T": "𐑡", "R": "𐑾", "P": "𐑿", "F": "𐑞",
        "K": "𐑺", "G": "𐑚", "Gamma": "𐑜", "Phi": "𐑮", "H": "𐑒",
        "S": "𐑕", "Omega": "𐑷",
    },
    "praxeum": {
        "D": "𐑦", "T": "𐑶", "R": "𐑾", "P": "𐑹", "F": "𐑐",
        "K": "𐑧", "G": "𐑲", "Gamma": "𐑠", "Phi": "𐑻", "H": "𐑫",
        "S": "𐑳", "Omega": "𐑭",
    },
    # Reference compounds (imscribed for cross-reference)
    "dmt": {
        "D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹", "F": "𐑐",
        "K": "𐑧", "G": "𐑲", "Gamma": "𐑵", "Phi": "⊙", "H": "𐑫",
        "S": "𐑳", "Omega": "𐑭",
    },
}

# ── Ouroboricity Tiers (verified via ouroborics tool) ──

COMPOUND_TIERS: Dict[str, str] = {
    "verticullum": "O_∞",
    "chimerium": "O₀",
    "apertix": "O₂",
    "retiarius": "O₁",
    "praxeum": "O₀",
    "dmt": "O_∞",
}

# ── Ordinal Mappings ──

ORDINALS = {
    # Dimensionality
    "𐑛": 0, "𐑨": 1, "𐑼": 2, "𐑦": 3,
    # Topology
    "𐑡": 0, "𐑰": 1, "𐑥": 2, "𐑶": 3, "𐑸": 4,
    # Relational Mode
    "𐑩": 0, "𐑑": 1, "𐑽": 2, "𐑾": 3,
    # Parity/Symmetry
    "𐑗": 0, "𐑿": 1, "𐑬": 2, "𐑯": 3, "𐑹": 4,
    # Fidelity
    "𐑱": 0, "𐑞": 1, "𐑐": 2,
    # Kinetics
    "𐑘": 0, "𐑤": 1, "𐑧": 2, "𐑪": 3, "𐑺": 4,
    # Scope
    "𐑚": 0, "𐑔": 1, "𐑲": 2,
    # Grammar/Composition
    "𐑝": 0, "𐑜": 1, "𐑠": 2, "𐑵": 3,
    # Criticality
    "𐑢": 0, "⊙": 1, "𐑮": 2, "𐑻": 3, "𐑣": 4,
    # Chirality
    "𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3,
    # Stoichiometry
    "𐑙": 0, "𐑕": 1, "𐑳": 2,
    # Winding
    "𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3,
}

# ── Primitive Field Mapping ──

FIELD_TO_PRIMITIVE = {
    "D": "Dimensionality", "T": "Topology", "R": "Relational",
    "P": "Parity", "F": "Fidelity", "K": "Kinetics",
    "G": "Scope", "Gamma": "Grammar", "Phi": "Criticality",
    "H": "Chirality", "S": "Stoichiometry", "Omega": "Winding",
}

# ── Absorption Rules ──

ABSORPTION_RULES = {
    # tensor(critical, EP) = EP  (⊙_3 absorption)
    ("Phi", "⊙", "𐑻"): "𐑻",
    ("Phi", "𐑻", "⊙"): "𐑻",
}

def get_compound(name: str) -> Dict[str, str]:
    """Return the full 12-tuple for a named compound."""
    if name not in COMPOUND_TUPLES:
        raise KeyError(f"Unknown compound: {name}. Known: {list(COMPOUND_TUPLES.keys())}")
    return dict(COMPOUND_TUPLES[name])

def compound_tier(name: str) -> str:
    """Return the ouroboricity tier for a compound (verified via ouroborics tool)."""
    if name not in COMPOUND_TIERS:
        raise KeyError(f"Unknown compound: {name}")
    return COMPOUND_TIERS[name]

def tensor_tuples(tup_a: Dict[str, str], tup_b: Dict[str, str]) -> Dict[str, str]:
    """Compute the tensor product of two 12-tuples.

    Rules:
    - Phi: max ordinal, with absorption ⊗(⊙, 𐑻) = 𐑻
    - Fidelity: min ordinal
    - All others: max ordinal
    """
    result = {}
    for field in ["D", "T", "R", "P", "K", "G", "Gamma", "H", "S", "Omega"]:
        a_ord = ORDINALS[tup_a[field]]
        b_ord = ORDINALS[tup_b[field]]
        # Max ordinal
        max_ord = max(a_ord, b_ord)
        # Find the glyph with this ordinal
        result[field] = [g for g, o in ORDINALS.items() if o == max_ord][0]

    # Fidelity: min ordinal
    f_a = ORDINALS[tup_a["F"]]
    f_b = ORDINALS[tup_b["F"]]
    min_f = min(f_a, f_b)
    result["F"] = [g for g, o in ORDINALS.items() if o == min_f][0]

    # Criticality: max with absorption
    phi_a = tup_a["Phi"]
    phi_b = tup_b["Phi"]
    # Check absorption
    if (phi_a == "⊙" and phi_b == "𐑻") or (phi_a == "𐑻" and phi_b == "⊙"):
        result["Phi"] = "𐑻"
    else:
        phi_ord = max(ORDINALS[phi_a], ORDINALS[phi_b])
        result["Phi"] = [g for g, o in ORDINALS.items() if o == phi_ord][0]

    return result

def couple(name_a: str, name_b: str) -> Dict[str, str]:
    """Compute tensor coupling of two named compounds. Returns composite tuple."""
    return tensor_tuples(get_compound(name_a), get_compound(name_b))

def compound_delta(name_a: str, name_b: str) -> List[str]:
    """Return list of primitives that differ between two compounds."""
    a = get_compound(name_a)
    b = get_compound(name_b)
    deltas = []
    for field in a:
        if a[field] != b[field]:
            deltas.append(f"{FIELD_TO_PRIMITIVE[field]}: {a[field]}→{b[field]}")
    return deltas

def is_oinf_capable(tup: Dict[str, str]) -> bool:
    """Check if a tuple's primitives are compatible with O_∞ tier.

    Requirements: Phi=⊙, P=𐑹 or 𐑯, D=𐑦, H≥𐑖, Omega≥𐑴.
    """
    return (
        tup["Phi"] == "⊙" and
        tup["P"] in ("𐑹", "𐑯") and
        tup["D"] == "𐑦" and
        ORDINALS[tup["H"]] >= ORDINALS["𐑖"] and
        ORDINALS[tup["Omega"]] >= ORDINALS["𐑴"]
    )

# ── Access Predictions ──

def predict_gate1_closure(name: str) -> bool:
    """Predict whether coupling with Praxeum closes Gate 1.

    Returns True if the composite's Phi becomes EP (Gate 1 closes).
    """
    composite = couple(name, "praxeum")
    return composite["Phi"] == "𐑻"

def predict_tier_after_launch(name: str) -> str:
    """Predict tier after Chimerium supercritical launch."""
    orig_tier = compound_tier(name)
    if orig_tier == "O_∞":
        return "O_∞"  # Already max
    composite = couple(name, "chimerium")
    if is_oinf_capable(composite):
        return "O₂"
    if composite["Phi"] in ("𐑮", "𐑣"):
        return "O₂" if orig_tier == "O₁" else "O₁"
    return orig_tier

# ── Summary ──

if __name__ == "__main__":
    print("=== Psychedelic Bridge: p4rakernel × Novel Compounds ===\n")
    for name in COMPOUND_TUPLES:
        tup = get_compound(name)
        tier = compound_tier(name)
        oinf = "✓" if is_oinf_capable(tup) else "✗"
        print(f"{name:15s}  {tier:6s}  O_∞-capable: {oinf}  "
              f"Phi={tup['Phi']}  H={tup['H']}  Omega={tup['Omega']}")

    print("\n=== Key Couplings ===")
    # EP Gate Toggle
    pdc = couple("dmt", "praxeum")
    print(f"DMT⊗Praxeum: Phi {get_compound('dmt')['Phi']}→{pdc['Phi']} "
          f"(Gate 1 {'CLOSED' if pdc['Phi']=='𐑻' else 'OPEN'})")

    # Supercritical Launch
    kcc = couple("ketamine", "chimerium") if "ketamine" in COMPOUND_TUPLES else None
    if kcc:
        print(f"Ketamine⊗Chimerium: Phi {get_compound('ketamine')['Phi']}→{kcc['Phi']}")

    # Deltas
    print("\n=== Compound Deltas from DMT ===")
    for name in ["verticullum", "chimerium", "apertix", "retiarius", "praxeum"]:
        if name == "dmt":
            continue
        deltas = compound_delta("dmt", name)
        print(f"DMT→{name}: {', '.join(deltas)}")
