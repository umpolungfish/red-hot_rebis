#!/usr/bin/env python3
"""
Compute primitive mismatches between each Millennium Problem's
PrimitiveBridge.lean encoding and the O_∞ target (6,734,591).
"""
_HELP_EXAMPLES = """  rebis.py run compute_promotions"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "scripts/compute_promotions.py"
    print(_doc)
    print()
    info_line("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import json
from shared.rich_output import *


# O_∞ target from crystal_decode(6,734,591)
# ⟨Ð_ωÞ_OŘ_ýΦ_}ƒ^żÇ^@Γ_ʔɢ^Ş⊙_ÿĦ_!Σ_ïΩ_z>
O_INF = {
    "D": "Ð_ω", "T": "Þ_O", "R": "Ř_ý", "P": "Φ_}", "F": "ƒ^ż", "K": "Ç^@",
    "G": "Γ_ʔ", "Gamma": "ɢ^Ş", "Phi": "⊙_ÿ", "H": "Ħ_!", "S": "Σ_ï", "Omega": "Ω_z"
}

# PrimitiveBridge.lean encodings (from file_read above)
# Field mapping: D=dim, T=top, R=rel, P=pol, F=fid, K=kin, G=gran, Gamma=gram, 
#                 Phi=crit, H=chir, S=stoi, Omega=prot

PROBLEMS = {
    "YM Classical": {
        "D": "Ð_ß", "T": "Þ_6", "R": "Ř_¯", "P": "Φ_˙", "F": "ƒ_ì", "K": "Ç_-",
        "G": "Γ_β", "Gamma": "ɢ_Ş", "Phi": "φ̂_ž", "H": "Ħ_£", "S": "Σ_ő", "Omega": "Ω_z"
    },
    "YM Quantum Target": {
        "D": "Ð_ß", "T": "Þ_6", "R": "Ř_¯", "P": "Φ_˙", "F": "ƒ_ż", "K": "Ç_Ù",
        "G": "Γ_ʔ", "Gamma": "ɢ_Ş", "Phi": "φ̂_ÿ", "H": "Ħ_£", "S": "Σ_ő", "Omega": "Ω_z"
    },
    "RH": {
        "D": "Ð_C", "T": "Þ_6", "R": "Ř_↑", "P": "Φ_υ", "F": "ƒ_ż", "K": "Ç_@",
        "G": "Γ_ʔ", "Gamma": "ɢ_Ş", "Phi": "φ̂_Æ", "H": "Ħ_Ñ", "S": "Σ_ő", "Omega": "Ω_Å"
    },
    "NS": {
        "D": "Ð_ß", "T": "Þ_6", "R": "Ř_¯", "P": "Φ_υ", "F": "ƒ_ì", "K": "Ç_-",
        "G": "Γ_β", "Gamma": "ɢ_Ş", "Phi": "φ̂_ž", "H": "Ħ_Ñ", "S": "Σ_ï", "Omega": "Ω_Å"
    },
    "OPN": {
        "D": "Ð_;", "T": "Þ_K", "R": "Ř_↑", "P": "Φ_∅", "F": "ƒ_ℓ", "K": "Ç_Ù",
        "G": "Γ_ʔ", "Gamma": "ɢ_Ş", "Phi": "φ̂_ÿ", "H": "Ħ_Ñ", "S": "Σ_1", "Omega": "Ω_Å"
    },
    "Hodge": {
        "D": "Ð_ω", "T": "Þ_O", "R": "Ř_↑", "P": "Φ_υ", "F": "ƒ_ż", "K": "Ç_@",
        "G": "Γ_ʔ", "Gamma": "ɢ_Ş", "Phi": "φ̂_ÿ", "H": "Ħ_Ñ", "S": "Σ_ï", "Omega": "Ω_Å"
    },
    "BSD": {
        "D": "Ð_ω", "T": "Þ_¨", "R": "Ř_↑", "P": "Φ_υ", "F": "ƒ_ì", "K": "Ç_@",
        "G": "Γ_ʔ", "Gamma": "ɢ_Ş", "Phi": "φ̂_ÿ", "H": "Ħ_Ñ", "S": "Σ_ï", "Omega": "Ω_z"
    },
    "PvsNP": {
        "D": "Ð_;", "T": "Þ_6", "R": "Ř_↑", "P": "Φ_∅", "F": "ƒ_ℓ", "K": "Ç_-",
        "G": "Γ_β", "Gamma": "ɢ_Ş", "Phi": "φ̂_ž", "H": "Ħ_Ñ", "S": "Σ_1", "Omega": "Ω_Å"
    }
}

# Ordinal mappings for comparison
PRIMITIVE_ORDINALS = {
    "D": {"Ð_;": 1, "Ð_C": 2, "Ð_ß": 3, "Ð_ω": 4},
    "T": {"Þ_6": 1, "Þ_K": 2, "Þ_¨": 3, "Þ_ò": 4, "Þ_O": 5},
    "R": {"Ř_↑": 1, "Ř_¯": 2, "Ř_†": 3, "Ř_ý": 4},
    "P": {"Φ_∅": 1, "Φ_ψ": 2, "Φ_˙": 3, "Φ_υ": 4, "Φ_}": 5},
    "F": {"ƒ_ℓ": 1, "ƒ_ì": 2, "ƒ_ż": 3},
    "K": {"Ç_-": 1, "Ç_W": 2, "Ç_@": 3, "Ç_Ù": 4, "Ç_λ": 5},
    "G": {"Γ_β": 1, "Γ_γ": 2, "Γ_ʔ": 3},
    "Gamma": {"ɢ_Ş": 1, "ɢ_˝": 2, "ɢ_ˌ": 3, "ɢ_^": 4},
    "Phi": {"φ̂_ž": 1, "φ̂_ÿ": 2, "φ̂_Æ": 3, "φ̂_3": 4, "φ̂_Ţ": 5},
    "H": {"Ħ_Ñ": 1, "Ħ_£": 2, "Ħ_A": 3, "Ħ_!": 4},
    "S": {"Σ_1": 1, "Σ_ő": 2, "Σ_ï": 3},
    "Omega": {"Ω_Å": 1, "Ω_2": 2, "Ω_z": 3, "Ω_5": 4}
}

PRIMITIVE_NAMES = {
    "D": "Dimensionality", "T": "Topology", "R": "Relational", "P": "Parity",
    "F": "Fidelity", "K": "Kinetics", "G": "Granularity", "Gamma": "Interaction",
    "Phi": "Criticality", "H": "Chirality", "S": "Stoichiometry", "Omega": "Winding"
}

def distance(a, b):
    """Weighted Euclidean distance between two tuples."""
    total = 0.0
    conflicts = []
    for prim in PRIMITIVE_ORDINALS:
        o_a = PRIMITIVE_ORDINALS[prim].get(a[prim], 0)
        o_b = PRIMITIVE_ORDINALS[prim].get(b[prim], 0)
        if o_a != o_b:
            conflicts.append({"primitive": prim, "a": a[prim], "b": b[prim]})
            delta = abs(o_a - o_b)
            total += delta * delta
    return total**0.5, conflicts

def count_mismatches(source, target):
    """Count primitives that differ between source and target."""
    mismatches = []
    for prim in PRIMITIVE_ORDINALS:
        if source[prim] != target[prim]:
            mismatches.append(prim)
    return len(mismatches), mismatches

def classify(source, target):
    """Classify each primitive as promotion (source<target), demotion (source>target), or same."""
    result = {"promotions": [], "demotions": [], "same": []}
    for prim in PRIMITIVE_ORDINALS:
        o_s = PRIMITIVE_ORDINALS[prim].get(source[prim], 0)
        o_t = PRIMITIVE_ORDINALS[prim].get(target[prim], 0)
        if o_s < o_t:
            result["promotions"].append((prim, source[prim], target[prim], o_t - o_s))
        elif o_s > o_t:
            result["demotions"].append((prim, source[prim], target[prim], o_s - o_t))
        else:
            result["same"].append(prim)
    return result

info_line("=" * 90)
info_line(f"{'Problem':25s} {'Promos':8s} {'Demos':8s} {'Changes':8s} {'Distance':10s} {'Bottlenecks'}")
info_line("=" * 90)

results = []
for name, source in PROBLEMS.items():
    d, _ = distance(source, O_INF)
    n_promos, _ = count_mismatches(source, O_INF)  # simple count
    c = classify(source, O_INF)
    n_promos = len(c["promotions"])
    n_demos = len(c["demotions"])
    total = n_promos + n_demos
    bottlenecks = ", ".join([f"{p}({s}→{t})" for p, s, t, _ in c["promotions"]])
    info_line(f"{name:25s} {str(n_promos):8s} {str(n_demos):8s} {str(total):8s} {f'{d:.2f}':10s} {bottlenecks[:60]}")
    results.append((name, n_promos, n_demos, total, d, c))

print()
info_line("=" * 90)
info_line("DETAILED PER-PRIMITIVE COMPARISON")
info_line("=" * 90)
for name, source in PROBLEMS.items():
    info_line(f"\n--- {name} ---")
    c = classify(source, O_INF)
    for p, s, t, delta in c["promotions"]:
        info_line(f"  ↑ {p:8s}: {s:12s} → {t:12s}  Δ={delta}")
    for p, s, t, delta in c["demotions"]:
        info_line(f"  ↓ {p:8s}: {s:12s} → {t:12s}  Δ={delta}")
    for p in c["same"]:
        info_line(f"  = {p:8s}: {source[p]:12s}  (unchanged)")
