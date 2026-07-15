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
# ⟨𐑦𐑸𐑑𐑹ƒ^żÇ^@𐑲ɢ^Ş⊙𐑫𐑳𐑭>
O_INF = {
    "D": "𐑦", "T": "𐑸", "R": "𐑑", "P": "𐑹", "F": "ƒ^ż", "K": "Ç^@",
    "G": "𐑲", "Gamma": "ɢ^Ş", "Phi": "⊙", "H": "𐑫", "S": "𐑳", "Omega": "𐑭"
}

# PrimitiveBridge.lean encodings (from file_read above)
# Field mapping: D=dim, T=top, R=rel, P=pol, F=fid, K=kin, G=gran, Gamma=gram, 
#                 Phi=crit, H=chir, S=stoi, Omega=prot

PROBLEMS = {
    "YM Classical": {
        "D": "𐑛", "T": "𐑡", "R": "𐑩", "P": "𐑯", "F": "𐑱", "K": "𐑘",
        "G": "𐑚", "Gamma": "𐑵", "Phi": "φ̂_ž", "H": "𐑒", "S": "𐑕", "Omega": "𐑭"
    },
    "YM Quantum Target": {
        "D": "𐑛", "T": "𐑡", "R": "𐑩", "P": "𐑯", "F": "𐑐", "K": "𐑪",
        "G": "𐑲", "Gamma": "𐑵", "Phi": "φ̂_ÿ", "H": "𐑒", "S": "𐑕", "Omega": "𐑭"
    },
    "RH": {
        "D": "𐑨", "T": "𐑡", "R": "Ř_↑", "P": "𐑿", "F": "𐑐", "K": "𐑧",
        "G": "𐑲", "Gamma": "𐑵", "Phi": "φ̂_Æ", "H": "𐑓", "S": "𐑕", "Omega": "𐑷"
    },
    "NS": {
        "D": "𐑛", "T": "𐑡", "R": "𐑩", "P": "𐑿", "F": "𐑱", "K": "𐑘",
        "G": "𐑚", "Gamma": "𐑵", "Phi": "φ̂_ž", "H": "𐑓", "S": "𐑳", "Omega": "𐑷"
    },
    "OPN": {
        "D": "𐑼", "T": "𐑰", "R": "Ř_↑", "P": "Φ_∅", "F": "ƒ_ℓ", "K": "𐑪",
        "G": "𐑲", "Gamma": "𐑵", "Phi": "φ̂_ÿ", "H": "𐑓", "S": "Σ_1", "Omega": "𐑷"
    },
    "Hodge": {
        "D": "𐑦", "T": "𐑸", "R": "Ř_↑", "P": "𐑿", "F": "𐑐", "K": "𐑧",
        "G": "𐑲", "Gamma": "𐑵", "Phi": "φ̂_ÿ", "H": "𐑓", "S": "𐑳", "Omega": "𐑷"
    },
    "BSD": {
        "D": "𐑦", "T": "𐑶", "R": "Ř_↑", "P": "𐑿", "F": "𐑱", "K": "𐑧",
        "G": "𐑲", "Gamma": "𐑵", "Phi": "φ̂_ÿ", "H": "𐑓", "S": "𐑳", "Omega": "𐑭"
    },
    "PvsNP": {
        "D": "𐑼", "T": "𐑡", "R": "Ř_↑", "P": "Φ_∅", "F": "ƒ_ℓ", "K": "𐑘",
        "G": "𐑚", "Gamma": "𐑵", "Phi": "φ̂_ž", "H": "𐑓", "S": "Σ_1", "Omega": "𐑷"
    }
}

# Ordinal mappings for comparison
PRIMITIVE_ORDINALS = {
    "D": {"𐑼": 1, "𐑨": 2, "𐑛": 3, "𐑦": 4},
    "T": {"𐑡": 1, "𐑰": 2, "𐑶": 3, "𐑥": 4, "𐑸": 5},
    "R": {"Ř_↑": 1, "𐑩": 2, "Ř_†": 3, "𐑑": 4},
    "P": {"Φ_∅": 1, "Φ_ψ": 2, "𐑯": 3, "𐑿": 4, "𐑹": 5},
    "F": {"ƒ_ℓ": 1, "𐑱": 2, "𐑐": 3},
    "K": {"𐑘": 1, "𐑤": 2, "𐑧": 3, "𐑪": 4, "𐑺": 5},
    "G": {"𐑚": 1, "𐑔": 2, "𐑲": 3},
    "Gamma": {"𐑵": 1, "𐑜": 2, "𐑠": 3, "𐑝": 4},
    "Phi": {"φ̂_ž": 1, "φ̂_ÿ": 2, "φ̂_Æ": 3, "φ̂_3": 4, "φ̂_Ţ": 5},
    "H": {"𐑓": 1, "𐑒": 2, "𐑖": 3, "𐑫": 4},
    "S": {"Σ_1": 1, "𐑕": 2, "𐑳": 3},
    "Omega": {"𐑷": 1, "𐑴": 2, "𐑭": 3, "𐑟": 4}
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
