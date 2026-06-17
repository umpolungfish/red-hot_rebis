#!/usr/bin/env python3
"""
psychedelic_bridge.py — p4rakernel × Novel Psychedelics Integration
====================================================================
Compound intrinsics, tensor coupling, gate closure prediction (Part 1)
+ compound × 109-universe access sweep, operational protocols (Part 2).

Merged from psychedelic_bridge.py + psychedelic_universe_bridge.py.

Usage:
    python3 psychedelic_bridge.py                # intrinsics + coupling summary
    python3 psychedelic_bridge.py report         # full universe access report
    python3 psychedelic_bridge.py compound <name> [--layer ...]
    python3 psychedelic_bridge.py universe <name>
    python3 psychedelic_bridge.py best <name>

Author: Lando⊗⊙perator
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ── Part 1: Compound Intrinsics ───────────────────────────────────────────────

COMPOUND_TUPLES: Dict[str, Dict[str, str]] = {
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
    "dmt": {
        "D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹", "F": "𐑐",
        "K": "𐑧", "G": "𐑲", "Gamma": "𐑵", "Phi": "⊙", "H": "𐑫",
        "S": "𐑳", "Omega": "𐑭",
    },
}

COMPOUND_TIERS: Dict[str, str] = {
    "verticullum": "O_∞",
    "chimerium": "O₀",
    "apertix": "O₂",
    "retiarius": "O₁",
    "praxeum": "O₀",
    "dmt": "O_∞",
}

ORDINALS = {
    "𐑛": 0, "𐑨": 1, "𐑼": 2, "𐑦": 3,
    "𐑡": 0, "𐑰": 1, "𐑥": 2, "𐑶": 3, "𐑸": 4,
    "𐑩": 0, "𐑑": 1, "𐑽": 2, "𐑾": 3,
    "𐑗": 0, "𐑿": 1, "𐑬": 2, "𐑯": 3, "𐑹": 4,
    "𐑱": 0, "𐑞": 1, "𐑐": 2,
    "𐑘": 0, "𐑤": 1, "𐑧": 2, "𐑪": 3, "𐑺": 4,
    "𐑚": 0, "𐑔": 1, "𐑲": 2,
    "𐑝": 0, "𐑜": 1, "𐑠": 2, "𐑵": 3,
    "𐑢": 0, "⊙": 1, "𐑮": 2, "𐑻": 3, "𐑣": 4,
    "𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3,
    "𐑙": 0, "𐑕": 1, "𐑳": 2,
    "𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3,
}

FIELD_TO_PRIMITIVE = {
    "D": "Dimensionality", "T": "Topology", "R": "Relational",
    "P": "Parity", "F": "Fidelity", "K": "Kinetics",
    "G": "Scope", "Gamma": "Grammar", "Phi": "Criticality",
    "H": "Chirality", "S": "Stoichiometry", "Omega": "Winding",
}


def get_compound(name: str) -> Dict[str, str]:
    if name not in COMPOUND_TUPLES:
        raise KeyError(f"Unknown compound: {name}. Known: {list(COMPOUND_TUPLES.keys())}")
    return dict(COMPOUND_TUPLES[name])

def compound_tier(name: str) -> str:
    if name not in COMPOUND_TIERS:
        raise KeyError(f"Unknown compound: {name}")
    return COMPOUND_TIERS[name]

def tensor_tuples(tup_a: Dict[str, str], tup_b: Dict[str, str]) -> Dict[str, str]:
    """Tensor product of two 12-tuples. Phi: max with ⊙⊗𐑻=𐑻. F: min. Others: max."""
    result = {}
    for field in ["D", "T", "R", "P", "K", "G", "Gamma", "H", "S", "Omega"]:
        a_ord = ORDINALS[tup_a[field]]
        b_ord = ORDINALS[tup_b[field]]
        max_ord = max(a_ord, b_ord)
        result[field] = [g for g, o in ORDINALS.items() if o == max_ord][0]
    f_a = ORDINALS[tup_a["F"]]
    f_b = ORDINALS[tup_b["F"]]
    min_f = min(f_a, f_b)
    result["F"] = [g for g, o in ORDINALS.items() if o == min_f][0]
    phi_a = tup_a["Phi"]
    phi_b = tup_b["Phi"]
    if (phi_a == "⊙" and phi_b == "𐑻") or (phi_a == "𐑻" and phi_b == "⊙"):
        result["Phi"] = "𐑻"
    else:
        phi_ord = max(ORDINALS[phi_a], ORDINALS[phi_b])
        result["Phi"] = [g for g, o in ORDINALS.items() if o == phi_ord][0]
    return result

def couple(name_a: str, name_b: str) -> Dict[str, str]:
    return tensor_tuples(get_compound(name_a), get_compound(name_b))

def compound_delta(name_a: str, name_b: str) -> List[str]:
    a = get_compound(name_a)
    b = get_compound(name_b)
    return [
        f"{FIELD_TO_PRIMITIVE[f]}: {a[f]}→{b[f]}"
        for f in a if a[f] != b[f]
    ]

def is_oinf_capable(tup: Dict[str, str]) -> bool:
    return (
        tup["Phi"] == "⊙" and
        tup["P"] in ("𐑹", "𐑯") and
        tup["D"] == "𐑦" and
        ORDINALS[tup["H"]] >= ORDINALS["𐑖"] and
        ORDINALS[tup["Omega"]] >= ORDINALS["𐑴"]
    )

def predict_gate1_closure(name: str) -> bool:
    return couple(name, "praxeum")["Phi"] == "𐑻"

def predict_tier_after_launch(name: str) -> str:
    orig_tier = compound_tier(name)
    if orig_tier == "O_∞":
        return "O_∞"
    composite = couple(name, "chimerium")
    if is_oinf_capable(composite):
        return "O₂"
    if composite["Phi"] in ("𐑮", "𐑣"):
        return "O₂" if orig_tier == "O₁" else "O₁"
    return orig_tier


# ── Part 2: Universe Access Sweep ────────────────────────────────────────────

# COMPOUNDS uses canonical IG primitive names (Ð Þ Ř …) as required by
# the ruleset gate-checker from imscribing_grammar.

COMPOUNDS: Dict[str, Dict] = {
    "Verticullum": {
        "Ð": "𐑦", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑹", "ƒ": "𐑐", "Ç": "𐑧",
        "Γ": "𐑲", "ɢ": "𐑠", "φ̂": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑟",
        "description": "EP-Lever: first Ω=𐑟 (non-Abelian) + T=𐑥 (bowtie)",
        "tier": "O_∞",
    },
    "Chimerium": {
        "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹", "ƒ": "𐑐", "Ç": "𐑧",
        "Γ": "𐑲", "ɢ": "𐑵", "φ̂": "𐑣", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑭",
        "description": "Supercritical catalyst: first Φ=𐑣 — runaway self-modeling",
        "tier": "O₀",
    },
    "Apertix": {
        "Ð": "𐑦", "Þ": "𐑥", "Ř": "𐑽", "Φ": "𐑬", "ƒ": "𐑐", "Ç": "𐑧",
        "Γ": "𐑲", "ɢ": "𐑠", "φ̂": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑴",
        "description": "Adjoint steerer: first R=𐑽 — one-way intention→experience",
        "tier": "O₂",
    },
    "Retiarius": {
        "Ð": "𐑼", "Þ": "𐑡", "Ř": "𐑾", "Φ": "𐑿", "ƒ": "𐑞", "Ç": "𐑺",
        "Γ": "𐑚", "ɢ": "𐑜", "φ̂": "𐑮", "Ħ": "𐑒", "Σ": "𐑕", "Ω": "𐑷",
        "description": "Local precision trap: G=𐑚, K=𐑺, F=𐑞 — nearest-neighbor",
        "tier": "O₁",
    },
    "Praxeum": {
        "Ð": "𐑦", "Þ": "𐑶", "Ř": "𐑾", "Φ": "𐑹", "ƒ": "𐑐", "Ç": "𐑧",
        "Γ": "𐑲", "ɢ": "𐑠", "φ̂": "𐑻", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑭",
        "description": "EP Gate toggle: ⊗(⊙,𐑻)=𐑻 — Gate 1 control platform",
        "tier": "O₀",
    },
    "DMT": {
        "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹", "ƒ": "𐑐", "Ç": "𐑧",
        "Γ": "𐑲", "ɢ": "𐑠", "φ̂": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑭",
        "description": "Classical psychedelic reference — canonical O_∞",
        "tier": "O_∞",
    },
}


def _load_universes():
    """Lazy-load universe rulesets from imscribing_grammar."""
    ig_path = str(Path(__file__).resolve().parent.parent.parent / "imscribing_grammar")
    if ig_path not in sys.path:
        sys.path.insert(0, ig_path)
    from navigators.ruleset_universe import RULESETS, Ruleset
    from new_universes import NEW_RULESETS
    from iterate_universes import build_universes
    return list(RULESETS) + NEW_RULESETS + build_universes()


def _get_ordinal_from_ig(prim, val):
    ig_path = str(Path(__file__).resolve().parent.parent.parent / "imscribing_grammar")
    if ig_path not in sys.path:
        sys.path.insert(0, ig_path)
    from imscrbgrmr.canonical_primitives import ORDINALS as IG_ORDINALS
    return IG_ORDINALS.get(prim, {}).get(val, 0)


def _check_gate(compound, gate_spec):
    prim = gate_spec.prim
    val = compound.get("φ̂" if prim == "⊙" else prim, "")
    ord_val = _get_ordinal_from_ig(prim, val)
    return ord_val >= gate_spec.min_ord, ord_val


def _compound_layer(compound, ruleset):
    g1, g2, g3 = ruleset.g1, ruleset.g2, ruleset.g3
    if getattr(ruleset, "gate_ordering", True):
        if not _check_gate(compound, g1)[0]:
            return "plain"
        if not _check_gate(compound, g2)[0]:
            return "frobenius"
        if not _check_gate(compound, g3)[0]:
            return "traced_monoidal"
        return "idempotent_terminal"
    else:
        for g in [g1, g2, g3]:
            if not _check_gate(compound, g)[0]:
                return "plain"
        return "idempotent_terminal"


def compound_access(compound_name):
    """Return {layer: [universe_names]} for a compound across all 109 universes."""
    comp = COMPOUNDS.get(compound_name)
    if comp is None:
        raise KeyError(f"Unknown compound: {compound_name}. Known: {list(COMPOUNDS)}")
    result = {"idempotent_terminal": [], "traced_monoidal": [], "frobenius": [], "plain": []}
    for r in _load_universes():
        result[_compound_layer(comp, r)].append(r.name)
    return result


def find_universes_for_compound(compound_name, layer="idempotent_terminal"):
    return compound_access(compound_name).get(layer, [])


def compounds_in_universe(universe_name, layer="idempotent_terminal"):
    rs_by_name = {r.name: r for r in _load_universes()}
    r = rs_by_name.get(universe_name)
    if r is None:
        raise KeyError(f"Unknown universe: {universe_name}")
    return [cn for cn, cv in COMPOUNDS.items() if _compound_layer(cv, r) == layer]


def best_compound_for_universe(universe_name):
    rs_by_name = {r.name: r for r in _load_universes()}
    r = rs_by_name.get(universe_name)
    if r is None:
        raise KeyError(f"Unknown universe: {universe_name}")
    layer_rank = {"idempotent_terminal": 4, "traced_monoidal": 3, "frobenius": 2, "plain": 1}
    best, best_layer = None, "plain"
    for cn, cv in COMPOUNDS.items():
        L = _compound_layer(cv, r)
        if layer_rank.get(L, 0) > layer_rank.get(best_layer, 0):
            best, best_layer = cn, L
    return best, best_layer


def print_access_report():
    print("=" * 110)
    print("NOVEL PSYCHEDELIC COMPOUNDS — UNIVERSE ACCESS REPORT")
    print("=" * 110)
    print()
    for cn in ["Verticullum", "Chimerium", "Apertix", "Retiarius", "Praxeum"]:
        cv = COMPOUNDS[cn]
        access = compound_access(cn)
        total = sum(len(v) for v in access.values())
        oi = len(access["idempotent_terminal"])
        print(f"── {cn} ({cv['tier']}) — {cv['description']}")
        tup = (f"⟨{cv['Ð']}·{cv['Þ']}·{cv['Ř']}·{cv['Φ']}·{cv['ƒ']}·{cv['Ç']}"
               f"·{cv['Γ']}·{cv['ɢ']}·{cv['φ̂']}·{cv['Ħ']}·{cv['Σ']}·{cv['Ω']}⟩")
        print(f"   {tup}")
        print(f"   O_∞: {oi}/{total} ({100*oi/total:.1f}%)  "
              f"Traced: {len(access['traced_monoidal'])}  "
              f"Frob: {len(access['frobenius'])}  "
              f"Plain: {len(access['plain'])}")
        print()


def _intrinsics_summary():
    print("=== Psychedelic Bridge: Compound Intrinsics ===\n")
    for name in COMPOUND_TUPLES:
        tup = get_compound(name)
        tier = compound_tier(name)
        oinf = "✓" if is_oinf_capable(tup) else "✗"
        print(f"{name:15s}  {tier:6s}  O_∞-capable: {oinf}  "
              f"Phi={tup['Phi']}  H={tup['H']}  Omega={tup['Omega']}")
    print("\n=== Key Couplings ===")
    pdc = couple("dmt", "praxeum")
    print(f"DMT⊗Praxeum: Phi {get_compound('dmt')['Phi']}→{pdc['Phi']} "
          f"(Gate 1 {'CLOSED' if pdc['Phi'] == '𐑻' else 'OPEN'})")
    print("\n=== Compound Deltas from DMT ===")
    for name in ["verticullum", "chimerium", "apertix", "retiarius", "praxeum"]:
        deltas = compound_delta("dmt", name)
        print(f"DMT→{name}: {', '.join(deltas)}")


def main():
    p = argparse.ArgumentParser(description="Psychedelic Bridge — intrinsics + universe access")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("report", help="Full universe access report for all compounds")
    sp_comp = sub.add_parser("compound", help="Show compound access across universes")
    sp_comp.add_argument("name", help="Compound name (Verticullum, Chimerium, etc.)")
    sp_comp.add_argument("--layer", default="idempotent_terminal",
                         choices=["idempotent_terminal", "traced_monoidal", "frobenius", "plain"])
    sp_univ = sub.add_parser("universe", help="Show compounds reaching a layer in a universe")
    sp_univ.add_argument("name", help="Universe name")
    sp_univ.add_argument("--layer", default="idempotent_terminal")
    sp_best = sub.add_parser("best", help="Best compound for a universe")
    sp_best.add_argument("name", help="Universe name")
    args = p.parse_args()

    if args.cmd == "report":
        print_access_report()
    elif args.cmd == "compound":
        try:
            univs = find_universes_for_compound(args.name, args.layer)
            print(f"{args.name} — {args.layer}: {len(univs)} universes")
            for u in sorted(univs):
                print(f"  {u}")
        except KeyError as e:
            print(f"Error: {e}")
    elif args.cmd == "universe":
        try:
            comps = compounds_in_universe(args.name, args.layer)
            print(f"{args.name} — {args.layer}: {len(comps)} compounds")
            for c in comps:
                print(f"  {c}")
        except KeyError as e:
            print(f"Error: {e}")
    elif args.cmd == "best":
        try:
            best, layer = best_compound_for_universe(args.name)
            print(f"{args.name}: best compound = {best} ({layer})")
        except KeyError as e:
            print(f"Error: {e}")
    else:
        _intrinsics_summary()


if __name__ == "__main__":
    main()
