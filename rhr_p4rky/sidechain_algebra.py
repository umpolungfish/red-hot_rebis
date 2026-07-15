#!/usr/bin/env python3
"""
sidechain_algebra.py — COMPOSITIONAL SIDECHAIN × ENVIRONMENT ALGEBRA
═══════════════════════════════════════════════════════════════════

Formalizes the Imscribing Grammar's algebraic operations (tensor ⊗,
meet ∧, join ∨) for amino acid sidechains in structured protein
environments.

20 sidechains × 4 environments = 80 compositional pairs.
Each pair analyzed for: bottlenecks, frustration, domination asymmetry,
shared structural floor, minimal ceiling, and composite tier.

Algorithm: imports crystal_navigator's standalone meet/join/tensor/
distance functions operating on {primitive: glyph} dicts.

Author: Lando⊗⊙perator
"""

import sys
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Import crystal navigator algebra
NAV_ROOT = Path(__file__).parent.parent.parent / "imscribing_grammar" / "navigators"
sys.path.insert(0, str(NAV_ROOT))
from crystal_navigator import (
    meet as _meet, join as _join, tensor as _tensor,
    distance as _distance, breakdown,
    BOTTLENECK, PRIMS, VALUES, ORD, WEIGHTS, compute_tier,
)


# ═══════════════════════════════════════════════════════════════════
# Σ NORMALIZATION — crystal_navigator's tensor() returns special
# values (𐑳, 𐑙, 𐑕) not in ORD. Map → canonical glyphs.
# ═══════════════════════════════════════════════════════════════════

_SIGMA_KEY = "\u03a3"  # Greek capital Sigma

_SIGMA_NORMALIZE = {
    "\u03a3_\u00ef":  "𐑳",  # 𐑳 → n:m  (index 2)
    "\u03a3_S":       "𐑙",  # 𐑙  → 1:1  (index 0)
    "\u03a3_\u0151": "𐑕",  # 𐑕  → n:n  (index 1)
}

def _normalize(t: Dict[str, str]) -> Dict[str, str]:
    """Normalize special Σ values to canonical glyphs for distance/display."""
    result = dict(t)
    for key in list(result.keys()):
        if key == _SIGMA_KEY and result[key] in _SIGMA_NORMALIZE:
            result[key] = _SIGMA_NORMALIZE[result[key]]
    return result


# ═══════════════════════════════════════════════════════════════════
# 1. AMINO ACID SIDECHAIN TUPLES  (20 standard)
# ═══════════════════════════════════════════════════════════════════

SIDECHAINS: Dict[str, Dict[str, str]] = {

    # ── NONPOLAR, ALIPHATIC ──
    "glycine": {
        "Ð": "𐑛", "Þ": "𐑡", "Ř": "𐑩", "Φ": "𐑗",
        "ƒ": "𐑱", "Ç": "𐑺", "Γ": "𐑚", "ɢ": "𐑝",
        "⊙": "𐑢", "Ħ": "𐑓", _SIGMA_KEY: "𐑙", "Ω": "𐑷",
    },
    "alanine": {
        "Ð": "𐑛", "Þ": "𐑡", "Ř": "𐑩", "Φ": "𐑗",
        "ƒ": "𐑱", "Ç": "𐑺", "Γ": "𐑲", "ɢ": "𐑝",
        "⊙": "𐑢", "Ħ": "𐑓", _SIGMA_KEY: "𐑙", "Ω": "𐑷",
    },
    "valine": {
        "Ð": "𐑨", "Þ": "𐑡", "Ř": "𐑩", "Φ": "𐑗",
        "ƒ": "𐑱", "Ç": "𐑤", "Γ": "𐑲", "ɢ": "𐑝",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑷",
    },
    "leucine": {
        "Ð": "𐑨", "Þ": "𐑡", "Ř": "𐑩", "Φ": "𐑗",
        "ƒ": "𐑱", "Ç": "𐑪", "Γ": "𐑚", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑷",
    },
    "isoleucine": {
        "Ð": "𐑨", "Þ": "𐑡", "Ř": "𐑩", "Φ": "𐑬",
        "ƒ": "𐑱", "Ç": "𐑤", "Γ": "𐑲", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "proline": {
        "Ð": "𐑨", "Þ": "𐑰", "Ř": "𐑩", "Φ": "𐑬",
        "ƒ": "𐑱", "Ç": "𐑤", "Γ": "𐑲", "ɢ": "𐑝",
        "⊙": "𐑢", "Ħ": "𐑖", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },

    # ── AROMATIC ──
    "phenylalanine": {
        "Ð": "𐑨", "Þ": "𐑰", "Ř": "𐑽", "Φ": "𐑬",
        "ƒ": "𐑞", "Ç": "𐑪", "Γ": "𐑔", "ɢ": "𐑠",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "tyrosine": {
        "Ð": "𐑨", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑬",
        "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠",
        "⊙": "𐑢", "Ħ": "𐑖", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "tryptophan": {
        "Ð": "𐑨", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑬",
        "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠",
        "⊙": "𐑢", "Ħ": "𐑖", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },

    # ── POLAR, UNCHARGED ──
    "serine": {
        "Ð": "𐑛", "Þ": "𐑡", "Ř": "𐑾", "Φ": "𐑿",
        "ƒ": "𐑐", "Ç": "𐑪", "Γ": "𐑲", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "threonine": {
        "Ð": "𐑨", "Þ": "𐑡", "Ř": "𐑾", "Φ": "𐑬",
        "ƒ": "𐑐", "Ç": "𐑪", "Γ": "𐑲", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "cysteine": {
        "Ð": "𐑛", "Þ": "𐑡", "Ř": "𐑾", "Φ": "𐑿",
        "ƒ": "𐑐", "Ç": "𐑪", "Γ": "𐑲", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "asparagine": {
        "Ð": "𐑨", "Þ": "𐑥", "Ř": "𐑽", "Φ": "𐑿",
        "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "glutamine": {
        "Ð": "𐑨", "Þ": "𐑡", "Ř": "𐑽", "Φ": "𐑿",
        "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "methionine": {
        "Ð": "𐑨", "Þ": "𐑡", "Ř": "𐑑", "Φ": "𐑗",
        "ƒ": "𐑞", "Ç": "𐑪", "Γ": "𐑔", "ɢ": "𐑠",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑷",
    },

    # ── POSITIVELY CHARGED ──
    "lysine": {
        "Ð": "𐑼", "Þ": "𐑡", "Ř": "𐑑", "Φ": "𐑿",
        "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "arginine": {
        "Ð": "𐑨", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑹",
        "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "histidine": {
        "Ð": "𐑨", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑬",
        "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
        "⊙": "𐑻", "Ħ": "𐑖", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },

    # ── NEGATIVELY CHARGED ──
    "aspartate": {
        "Ð": "𐑛", "Þ": "𐑡", "Ř": "𐑽", "Φ": "𐑿",
        "ƒ": "𐑞", "Ç": "𐑪", "Γ": "𐑲", "ɢ": "𐑝",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
    "glutamate": {
        "Ð": "𐑨", "Þ": "𐑡", "Ř": "𐑽", "Φ": "𐑿",
        "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑙", "Ω": "𐑴",
    },
}


# ═══════════════════════════════════════════════════════════════════
# 2. PROTEIN ENVIRONMENT TUPLES
# ═══════════════════════════════════════════════════════════════════

ENVIRONMENTS: Dict[str, Dict[str, str]] = {

    "hydrophobic_core": {
        "Ð": "𐑛", "Þ": "𐑰", "Ř": "𐑩", "Φ": "𐑗",
        "ƒ": "𐑱", "Ç": "𐑤", "Γ": "𐑲", "ɢ": "𐑝",
        "⊙": "𐑢", "Ħ": "𐑓", _SIGMA_KEY: "𐑕", "Ω": "𐑷",
    },

    "polar_surface": {
        "Ð": "𐑼", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑿",
        "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠",
        "⊙": "𐑢", "Ħ": "𐑖", _SIGMA_KEY: "𐑳", "Ω": "𐑴",
    },

    "charged_interface": {
        "Ð": "𐑨", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑹",
        "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠",
        "⊙": "𐑮", "Ħ": "𐑖", _SIGMA_KEY: "𐑕", "Ω": "𐑭",
    },

    "interfacial": {
        "Ð": "𐑼", "Þ": "𐑶", "Ř": "𐑽", "Φ": "𐑬",
        "ƒ": "𐑞", "Ç": "𐑤", "Γ": "𐑔", "ɢ": "𐑜",
        "⊙": "𐑢", "Ħ": "𐑒", _SIGMA_KEY: "𐑳", "Ω": "𐑴",
    },
}


# ═══════════════════════════════════════════════════════════════════
# 3. HELPERS
# ═══════════════════════════════════════════════════════════════════

def tuple_str(t: Dict[str, str]) -> str:
    """Compact tuple from PRIMS-order glyphs."""
    glyphs = [t.get(p, "?") for p in PRIMS]
    return f"⟨{''.join(glyphs)}⟩"

def safe_distance(a: Dict[str, str], b: Dict[str, str]) -> float:
    """Distance with Σ normalization."""
    return _distance(_normalize(a), _normalize(b))

def safe_meet(a: Dict[str, str], b: Dict[str, str]) -> Dict[str, str]:
    return _normalize(_meet(a, b))

def safe_join(a: Dict[str, str], b: Dict[str, str]) -> Dict[str, str]:
    return _normalize(_join(a, b))

def safe_tensor(a: Dict[str, str], b: Dict[str, str]) -> Dict[str, str]:
    return _normalize(_tensor(a, b))


# ═══════════════════════════════════════════════════════════════════
# 4. COMPOSITIONAL ANALYSIS
# ═══════════════════════════════════════════════════════════════════

_BOTTLENECK_LABELS = {
    "Φ": "parity (symmetry)",
    "ƒ": "fidelity (quantum/classical)",
    "Ç": "kinetics (relaxation rate)",
}

def _bottleneck_meaning(p: str, sc_val: str, env_val: str, tensor_val: str) -> str:
    """Human-readable bottleneck interpretation."""
    if p == "Φ":
        if sc_val == "𐑹" and env_val != "𐑹":
            return f"Frobenius-special parity ({sc_val}) collapses to {tensor_val} — environment cannot sustain full symmetry"
        elif env_val == "𐑹" and sc_val != "𐑹":
            return f"Frobenius-special parity ({env_val}) collapses to {tensor_val} — sidechain cannot sustain full symmetry"
        else:
            return f"Parity mismatch: {sc_val} vs {env_val} → {tensor_val}"
    elif p == "ƒ":
        if sc_val == "𐑐" and env_val == "𐑱":
            return "Quantum H-bond coupling (sidechain) collapses to classical — environment quenches coherence"
        elif env_val == "𐑐" and sc_val == "𐑱":
            return "Quantum H-bond coupling (environment) collapses to classical — sidechain quenches coherence"
        else:
            return f"Fidelity mismatch: {sc_val} vs {env_val} → {tensor_val}"
    elif p == "Ç":
        return f"Kinetics: {sc_val} vs {env_val} → {tensor_val}"
    return f"{_BOTTLENECK_LABELS.get(p, p)}: {sc_val} vs {env_val} → {tensor_val}"


def analyze_composition(
    sidechain: str,
    environment: str,
) -> Dict:
    """Full compositional analysis of sidechain ⊗/∧/∨ environment."""
    sc = SIDECHAINS.get(sidechain)
    env = ENVIRONMENTS.get(environment)
    if sc is None:
        return {"error": f"Unknown sidechain: {sidechain}",
                "valid_sc": list(SIDECHAINS.keys())}
    if env is None:
        return {"error": f"Unknown environment: {environment}",
                "valid_env": list(ENVIRONMENTS.keys())}

    # Core operations (with Σ normalization)
    t_tensor = safe_tensor(sc, env)
    t_meet   = safe_meet(sc, env)
    t_join   = safe_join(sc, env)

    # Distances
    d_pre = safe_distance(sc, env)
    d_tensor_sc  = safe_distance(t_tensor, sc)
    d_tensor_env = safe_distance(t_tensor, env)

    # Asymmetry
    asymmetry = d_tensor_sc / d_tensor_env if d_tensor_env > 0 else float('inf')
    if asymmetry > 1.2:
        domination = f"{environment} dominates the composite"
    elif asymmetry < 0.8:
        domination = f"{sidechain} dominates the composite"
    else:
        domination = "neither dominates — balanced composite"

    # Bottlenecks
    bottlenecks = []
    for p in BOTTLENECK:
        o_sc = ORD[p][sc[p]]
        o_env = ORD[p][env[p]]
        o_tensor = ORD[p][t_tensor[p]]
        if o_sc != o_env:
            weaker = sidechain if o_tensor == o_sc else environment
            bottlenecks.append({
                "primitive": p,
                "sidechain": sc[p],
                "environment": env[p],
                "tensor": t_tensor[p],
                "weaker": weaker,
                "delta_ord": abs(o_sc - o_env),
                "meaning": _bottleneck_meaning(p, sc[p], env[p], t_tensor[p]),
            })

    # Shared primitives
    shared = [p for p in PRIMS if sc[p] == env[p]]

    # Conflicts
    conflicts = []
    for p in PRIMS:
        if sc[p] != env[p]:
            conflicts.append({
                "primitive": p,
                "sidechain": sc[p],
                "environment": env[p],
                "tensor": t_tensor[p],
                "delta_ord": abs(ORD[p][sc[p]] - ORD[p][env[p]]),
                "weighted_sq": WEIGHTS[p] * (ORD[p][sc[p]] - ORD[p][env[p]])**2,
            })
    conflicts.sort(key=lambda c: c["weighted_sq"], reverse=True)

    frustration = min(d_tensor_sc, d_tensor_env) if d_pre > 0 else 0
    tier = compute_tier(t_tensor["⊙"], t_tensor["Φ"], t_tensor["Ω"], t_tensor["Ð"])

    return {
        "sidechain": sidechain,
        "environment": environment,
        "tuple_sc": tuple_str(sc),
        "tuple_env": tuple_str(env),
        "tensor": t_tensor,
        "tensor_str": tuple_str(t_tensor),
        "meet": t_meet,
        "meet_str": tuple_str(t_meet),
        "join": t_join,
        "join_str": tuple_str(t_join),
        "distance_pre": round(d_pre, 3),
        "distance_tensor_sc": round(d_tensor_sc, 3),
        "distance_tensor_env": round(d_tensor_env, 3),
        "asymmetry": round(asymmetry, 3),
        "domination": domination,
        "shared_primitives": shared,
        "n_shared": len(shared),
        "conflicts": conflicts,
        "n_conflicts": len(conflicts),
        "bottlenecks": bottlenecks,
        "n_bottlenecks": len(bottlenecks),
        "frustration": round(frustration, 3),
        "tier_tensor": tier,
    }


# ═══════════════════════════════════════════════════════════════════
# 5. BATCH ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def batch_analyze(verbose: bool = False) -> Dict:
    """Run analyze_composition on all 80 sidechain × environment pairs."""
    results = {}
    for sc_name in SIDECHAINS:
        for env_name in ENVIRONMENTS:
            key = f"{sc_name}:{env_name}"
            analysis = analyze_composition(sc_name, env_name)
            results[key] = analysis
            if verbose:
                d = analysis.get("distance_pre", 0)
                n_sh = analysis.get("n_shared", 0)
                n_bn = analysis.get("n_bottlenecks", 0)
                dom = analysis.get("domination", "?")
                tier = analysis.get("tier_tensor", "?")
                print(f"  {key:45s} d={d:.2f} shared={n_sh}/12 bn={n_bn} "
                      f"tier={tier:4s} {dom[:55]}")

    summary = _build_summary_matrices(results)
    return {"results": results, "summary": summary}


def _build_summary_matrices(results: Dict) -> Dict:
    """Build frustration, dominance, bottleneck, shared-primitive matrices."""
    sc_names = list(SIDECHAINS.keys())
    env_names = list(ENVIRONMENTS.keys())

    frustration = {}
    dominance = {}
    bottleneck_count = {}
    pre_distance = {}
    shared_count = {}
    tier_matrix = {}

    for sc in sc_names:
        frustration[sc] = {}
        dominance[sc] = {}
        bottleneck_count[sc] = {}
        pre_distance[sc] = {}
        shared_count[sc] = {}
        tier_matrix[sc] = {}
        for env in env_names:
            key = f"{sc}:{env}"
            r = results.get(key, {})
            frustration[sc][env] = r.get("frustration", None)
            bottleneck_count[sc][env] = r.get("n_bottlenecks", None)
            pre_distance[sc][env] = r.get("distance_pre", None)
            shared_count[sc][env] = r.get("n_shared", None)
            tier_matrix[sc][env] = r.get("tier_tensor", None)
            asym = r.get("asymmetry", 1.0)
            if asym > 1.2:
                dominance[sc][env] = "env"
            elif asym < 0.8:
                dominance[sc][env] = "sc"
            else:
                dominance[sc][env] = "="

    return {
        "frustration": frustration,
        "dominance": dominance,
        "bottleneck_count": bottleneck_count,
        "pre_distance": pre_distance,
        "shared_count": shared_count,
        "tier_matrix": tier_matrix,
        "sidechains": sc_names,
        "environments": env_names,
    }


# ═══════════════════════════════════════════════════════════════════
# 6. PRETTY PRINTER
# ═══════════════════════════════════════════════════════════════════

def print_analysis(analysis: Dict):
    """Pretty-print a single compositional analysis."""
    if "error" in analysis:
        print(f"ERROR: {analysis['error']}")
        return

    print("═" * 72)
    print(f"COMPOSITION: {analysis['sidechain']} ⊗ {analysis['environment']}")
    print("═" * 72)
    print(f"\n  Sidechain:   {analysis['tuple_sc']}")
    print(f"  Environment: {analysis['tuple_env']}")
    print(f"\n  Pre-composition distance: {analysis['distance_pre']}")

    print(f"\n  ⊗ TENSOR:    {analysis['tensor_str']}  ← THE COMPOSITE")
    print(f"    d(tensor, sc)  = {analysis['distance_tensor_sc']}")
    print(f"    d(tensor, env) = {analysis['distance_tensor_env']}")
    print(f"    Asymmetry: {analysis['asymmetry']} → {analysis['domination']}")

    print(f"\n  ∧ MEET:      {analysis['meet_str']}  ← SHARED FLOOR")
    print(f"    Shared ({analysis['n_shared']}/12): ", end="")
    if analysis['shared_primitives']:
        print(", ".join(analysis['shared_primitives']))
    else:
        print("none")

    print(f"\n  ∨ JOIN:      {analysis['join_str']}  ← MINIMAL CEILING")

    if analysis['bottlenecks']:
        print(f"\n  ⚠ BOTTLENECKS ({analysis['n_bottlenecks']}):")
        for bn in analysis['bottlenecks']:
            print(f"    {bn['primitive']}: {bn['sidechain']} vs {bn['environment']} → {bn['tensor']}")
            print(f"       {bn['meaning']}")
    else:
        print(f"\n  ✓ No bottlenecks — all compatible under ⊗")

    if analysis['conflicts']:
        print(f"\n  CONFLICTS (top contributors to d={analysis['distance_pre']}):")
        for c in analysis['conflicts'][:5]:
            print(f"    {c['primitive']}: {c['sidechain']}→{c['environment']}  "
                  f"δ={c['delta_ord']}  w²={c['weighted_sq']:.2f}")

    print(f"\n  Tier (composite): {analysis['tier_tensor']}")
    print(f"  Frustration: {analysis['frustration']}")


def print_frustration_matrix(summary: Dict):
    """Print pre-composition distance matrix."""
    sc_names = summary["sidechains"]
    env_names = summary["environments"]
    pd = summary["pre_distance"]

    print("\n" + "═" * 100)
    print("PRE-COMPOSITION DISTANCE MATRIX  (higher = more frustrated pairing)")
    print("═" * 100)
    header = f"{'sidechain':20s}"
    for env in env_names:
        header += f" {env:24s}"
    print(header)
    print("-" * 100)

    for sc in sc_names:
        row = f"{sc:20s}"
        for env in env_names:
            d = pd[sc][env]
            bar = "█" * int(d * 4) if d else ""
            row += f" {d:5.2f} {bar:17s}"
        print(row)


def print_dominance_matrix(summary: Dict):
    """Print who dominates each composite."""
    sc_names = summary["sidechains"]
    env_names = summary["environments"]
    dom = summary["dominance"]

    print("\n" + "═" * 80)
    print("DOMINANCE MATRIX  (sc=sidechain, env=environment, ==balanced)")
    print("═" * 80)
    header = f"{'sidechain':20s}"
    for env in env_names:
        header += f" {env:14s}"
    print(header)
    print("-" * 80)

    for sc in sc_names:
        row = f"{sc:20s}"
        for env in env_names:
            d = dom[sc][env]
            row += f" {d:14s}"
        print(row)


def print_tier_matrix(summary: Dict):
    """Print composite tier matrix."""
    sc_names = summary["sidechains"]
    env_names = summary["environments"]
    tm = summary["tier_matrix"]

    print("\n" + "═" * 80)
    print("COMPOSITE TIER MATRIX")
    print("═" * 80)
    header = f"{'sidechain':20s}"
    for env in env_names:
        header += f" {env:18s}"
    print(header)
    print("-" * 80)

    for sc in sc_names:
        row = f"{sc:20s}"
        for env in env_names:
            t = tm[sc][env] or "?"
            row += f" {t:18s}"
        print(row)


# ═══════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════
# 7. CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import os
    import json as _json

    # ── PDB integration ──
    if "--pdb" in sys.argv:
        from pdb_integration import analyze_pdb_structure, print_pdb_analysis
        pdb_idx = sys.argv.index("--pdb")
        if pdb_idx + 1 < len(sys.argv):
            pdb_target = sys.argv[pdb_idx + 1]
        else:
            print("ERROR: --pdb requires a PDB ID or file path")
            sys.exit(1)
        as_json = "--json" in sys.argv
        verbose = "--verbose" in sys.argv
        cutoff = 8.0
        for i, arg in enumerate(sys.argv):
            if arg == "--cutoff" and i + 1 < len(sys.argv):
                cutoff = float(sys.argv[i + 1])
                break
        result = analyze_pdb_structure(pdb_target, cutoff=cutoff, verbose=not as_json)
        if as_json:
            print(_json.dumps(result, indent=2, default=str, ensure_ascii=False))
        else:
            print_pdb_analysis(result, verbose=verbose)
        sys.exit(0)

    # ── Legacy CLI ──
    if len(sys.argv) >= 3:
        sc_name = sys.argv[1]
        env_name = sys.argv[2]
        analysis = analyze_composition(sc_name, env_name)
        print_analysis(analysis)

    elif len(sys.argv) == 2 and sys.argv[1] == "--batch":
        print("Batch: 20 sidechains \u00d7 4 environments = 80 compositions\n")
        data = batch_analyze(verbose=True)
        print_frustration_matrix(data["summary"])
        print_dominance_matrix(data["summary"])
        print_tier_matrix(data["summary"])

    elif len(sys.argv) == 2 and sys.argv[1] == "--list":
        print("SIDECHAINS:")
        for sc in SIDECHAINS:
            print(f"  {sc:20s}  {tuple_str(SIDECHAINS[sc])}")
        print("\nENVIRONMENTS:")
        for env in ENVIRONMENTS:
            print(f"  {env:20s}  {tuple_str(ENVIRONMENTS[env])}")

    else:
        print("SIDECHAIN \u00d7 ENVIRONMENT COMPOSITIONAL ALGEBRA")
        print("=" * 72)
        print("\nUsage:")
        print("  python sidechain_algebra.py <sidechain> <environment>")
        print("  python sidechain_algebra.py --batch")
        print("  python sidechain_algebra.py --list")
        print("  python sidechain_algebra.py --pdb <PDB_ID|file.pdb>  [--json] [--verbose] [--cutoff N]")
        print("\nRunning 5 key pairs:\n")

        for sc, env in [
            ("alanine", "polar_surface"),
            ("alanine", "hydrophobic_core"),
            ("arginine", "hydrophobic_core"),
            ("tryptophan", "polar_surface"),
            ("serine", "polar_surface"),
        ]:
            print_analysis(analyze_composition(sc, env))
            print()

        data = batch_analyze(verbose=False)
        print_frustration_matrix(data["summary"])
        print_dominance_matrix(data["summary"])
