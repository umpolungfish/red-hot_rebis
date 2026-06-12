#!/usr/bin/env python3
"""psychedelic_universe_bridge.py — Map novel psychedelic compounds to alternate universes.

Connects the five novel psychedelic compounds to the 109 alternate universes
defined in new_universes.py and iterate_universes.py.

Usage:
    from psychedelic_universe_bridge import (
        COMPOUNDS, all_universes, compound_access, universe_grid,
        print_access_report, find_universes_for_compound,
        compounds_in_universe, best_compound_for_universe
    )
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "imscribing_grammar"))

from navigators.ruleset_universe import RULESETS, Ruleset
from new_universes import NEW_RULESETS
from iterate_universes import build_universes
from imscrbgrmr.canonical_primitives import ORDINALS

# ── Five Novel Psychedelic Compounds ──────────────────────────

COMPOUNDS = {
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
}

# Also include DMT for reference
COMPOUNDS["DMT"] = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹", "ƒ": "𐑐", "Ç": "𐑧",
    "Γ": "𐑲", "ɢ": "𐑠", "φ̂": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑭",
    "description": "Classical psychedelic reference — canonical O_∞",
    "tier": "O_∞",
}

# ── All universes ─────────────────────────────────────────────

def all_universes():
    """Return list of all 109 alternate universes."""
    return list(RULESETS) + NEW_RULESETS + build_universes()

# ── Gate checking ─────────────────────────────────────────────

def get_ordinal(prim, val):
    return ORDINALS.get(prim, {}).get(val, 0)

def check_gate(compound, gate_spec):
    """Check if compound passes a single gate. Returns (passed, ordinal)."""
    prim = gate_spec.prim
    val = compound.get("φ̂" if prim == "⊙" else prim, "")
    return get_ordinal(prim, val) >= gate_spec.min_ord, get_ordinal(prim, val)

def compound_layer(compound, ruleset):
    """Determine which closure layer the compound reaches in this universe.

    Returns one of: 'idempotent_terminal', 'traced_monoidal', 'frobenius', 'plain'
    """
    g1, g2, g3 = ruleset.g1, ruleset.g2, ruleset.g3
    if ruleset.gate_ordering:
        if not check_gate(compound, g1)[0]:
            return "plain"
        if not check_gate(compound, g2)[0]:
            return "frobenius"
        if not check_gate(compound, g3)[0]:
            return "traced_monoidal"
        return "idempotent_terminal"
    else:
        for g in [g1, g2, g3]:
            if not check_gate(compound, g)[0]:
                return "plain"
        return "idempotent_terminal"

# ── Access analysis ───────────────────────────────────────────

def compound_access(compound_name):
    """Return {layer: count, layer: [universe_names]} for a compound."""
    comp = COMPOUNDS.get(compound_name)
    if comp is None:
        raise KeyError(f"Unknown compound: {compound_name}")
    result = {"idempotent_terminal": [], "traced_monoidal": [],
              "frobenius": [], "plain": []}
    for r in all_universes():
        layer = compound_layer(comp, r)
        result[layer].append(r.name)
    return result

def universe_grid(universes=None):
    """Return a dict mapping universe_name → {compound_name: layer}."""
    if universes is None:
        universes = all_universes()
    grid = {}
    for r in universes:
        grid[r.name] = {}
        for cn, cv in COMPOUNDS.items():
            grid[r.name][cn] = compound_layer(cv, r)
    return grid

def find_universes_for_compound(compound_name, layer="idempotent_terminal"):
    """Return list of universe names where compound reaches specified layer."""
    access = compound_access(compound_name)
    return access.get(layer, [])

def compounds_in_universe(universe_name, layer="idempotent_terminal"):
    """Return list of compound names that reach specified layer in this universe."""
    rs_by_name = {r.name: r for r in all_universes()}
    r = rs_by_name.get(universe_name)
    if r is None:
        raise KeyError(f"Unknown universe: {universe_name}")
    result = []
    for cn, cv in COMPOUNDS.items():
        if compound_layer(cv, r) == layer:
            result.append(cn)
    return result

def best_compound_for_universe(universe_name):
    """Return the compound with the highest closure layer in this universe."""
    rs_by_name = {r.name: r for r in all_universes()}
    r = rs_by_name.get(universe_name)
    if r is None:
        raise KeyError(f"Unknown universe: {universe_name}")
    layer_rank = {"idempotent_terminal": 4, "traced_monoidal": 3,
                  "frobenius": 2, "plain": 1}
    best = None
    best_layer = "plain"
    for cn, cv in COMPOUNDS.items():
        L = compound_layer(cv, r)
        if layer_rank.get(L, 0) > layer_rank.get(best_layer, 0):
            best = cn
            best_layer = L
    return best, best_layer

# ── Reporting ─────────────────────────────────────────────────

def print_access_report():
    """Print a full access report for all compounds."""
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
        tup = f"⟨{cv['Ð']}·{cv['Þ']}·{cv['Ř']}·{cv['Φ']}·{cv['ƒ']}·{cv['Ç']}·{cv['Γ']}·{cv['ɢ']}·{cv['φ̂']}·{cv['Ħ']}·{cv['Σ']}·{cv['Ω']}⟩"
        print(f"   {tup}")
        print(f"   O_∞: {oi}/{total} ({100*oi/total:.1f}%)  "
              f"Traced: {len(access['traced_monoidal'])}  "
              f"Frob: {len(access['frobenius'])}  "
              f"Plain: {len(access['plain'])}")
        print()

    print("── OPERATIONAL SUMMARY ──")
    print(f"  Broadest access:  Chimerium   ({len(compound_access('Chimerium')['idempotent_terminal'])}/109)")
    print(f"  Widest O_∞:     Verticullum ({len(compound_access('Verticullum')['idempotent_terminal'])}/109)")
    print(f"  Control platform: Praxeum     ({len(compound_access('Praxeum')['idempotent_terminal'])}/109)")
    print(f"  Precision:        Apertix     ({len(compound_access('Apertix')['idempotent_terminal'])}/109)")
    print(f"  Local trap:       Retiarius   ({len(compound_access('Retiarius')['idempotent_terminal'])}/109)")


# ── CLI ────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser(description="Psychedelic-Universe Bridge")
    sub = p.add_subparsers(dest="cmd")

    sp_report = sub.add_parser("report", help="Full access report")
    sp_comp = sub.add_parser("compound", help="Show compound access")
    sp_comp.add_argument("name", help="Compound name")
    sp_comp.add_argument("--layer", default="idempotent_terminal",
                         help="Layer: idempotent_terminal, traced_monoidal, frobenius, plain")
    sp_univ = sub.add_parser("universe", help="Show compounds in a universe")
    sp_univ.add_argument("name", help="Universe name")
    sp_univ.add_argument("--layer", default="idempotent_terminal",
                         help="Layer filter")
    sp_best = sub.add_parser("best", help="Best compound for a universe")
    sp_best.add_argument("name", help="Universe name")

    args = p.parse_args()

    if args.cmd == "report" or args.cmd is None:
        print_access_report()
    elif args.cmd == "compound":
        try:
            univs = find_universes_for_compound(args.name, args.layer)
            print(f"{args.name} — {args.layer}: {len(univs)} universes")
            for u in sorted(univs):
                print(f"  {u}")
        except KeyError as e:
            print(f"Error: {e}")
            print(f"Available: {list(COMPOUNDS.keys())}")
    elif args.cmd == "universe":
        try:
            comps = compounds_in_universe(args.name, args.layer)
            print(f"{args.name} — {args.layer}: {len(comps)} compounds")
            for c in comps:
                print(f"  {c}")
        except KeyError as e:
            print(f"Error: {e}")
            rs_names = [r.name for r in all_universes()]
            print(f"Available universes: {len(rs_names)}. Use 'report' for full listing.")
    elif args.cmd == "best":
        try:
            best, layer = best_compound_for_universe(args.name)
            print(f"{args.name}: best compound = {best} ({layer})")
        except KeyError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
