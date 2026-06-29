"""
structural_algebra.py — Organism Structural Algebra
=====================================================

Computes meet/join/tensor/distance relationships among the three
structurally distinct organism types at O_∞ dynamically from the
shared IG catalog. No hardcoded tuples or scores.

Three canonical organisms (all share 10 of 12 primitives,
differ only in ɢ (composition) and Ω (winding)):

  • universal_imscriptive_grammar — ɢ=𐑠 (sequential), Ω=𐑭 (integer)
  • imscribing_organism_rebis     — ɢ=𐑝 (conjunctive), Ω=𐑭 (integer)
  • clink_layer8_organism          — ɢ=𐑵 (broadcast), Ω=𐑟 (non-Abelian)

All three share: Ð=𐑦, Þ=𐑸, Ř=𐑾, Φ=𐑹, ƒ=𐑐, Ç=𐑧,
                  Γ=𐑲, ⊙=⊙, Ħ=𐑫, Σ=𐑳

Structural theorem (upholds the Frobenius lattice):
  meet(grammar, CLINK L8) = grammar
  join(Rebis, CLINK L8)   = CLINK L8
  tensor(grammar, CLINK L8) = CLINK L8 (d=0.0)
  tensor(grammar, Rebis)   = grammar (d=0.0)

Author: Lando⊗⊙perator
"""

import json, os, sys
from pathlib import Path

# Ensure shared/ is on the path for imports
_THIS_DIR = Path(__file__).resolve().parent
_REBIS_ROOT = _THIS_DIR.parent
if str(_REBIS_ROOT) not in sys.path:
    sys.path.insert(0, str(_REBIS_ROOT))

from shared.primitives import ORDINALS, PRIMITIVE_ORDER, tuple_distance
from shared.rich_output import *


# ── Catalog Loader ────────────────────────────────────────────────

_CATALOG_PATH = _REBIS_ROOT / "shared" / "IG_catalog.json"

def _load_catalog_dict():
    """Load the full catalog and build a name→tuple lookup."""
    if not _CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog not found at {_CATALOG_PATH}")
    with open(_CATALOG_PATH) as f:
        cat = json.load(f)
    lookup = {}
    for entry in cat:
        name = entry.get("name", "")
        if all(k in entry for k in PRIMITIVE_ORDER):
            lookup[name] = {k: entry[k] for k in PRIMITIVE_ORDER}
    return lookup

def _get_organism_tuples():
    """Fetch organism tuples from catalog — dynamic, never hardcoded."""
    cat = _load_catalog_dict()
    names = ["universal_imscriptive_grammar", "imscribing_organism_rebis", "clink_layer8_organism"]
    result = {}
    for name in names:
        if name not in cat:
            raise KeyError(f"Organism '{name}' not found in catalog. Run imscribe_system first.")
        result[name] = cat[name]
    return result

# ── Ordinal Access ────────────────────────────────────────────────

def ordinal(primitive_name, primitive_value):
    """Get ordinal of a primitive value by its primitive name."""
    return ORDINALS.get(primitive_name, {}).get(primitive_value, 0)


# ── Lattice Operations ────────────────────────────────────────────

def meet(tuple_a, tuple_b):
    """Greatest lower bound — shared structural floor.
    
    For each primitive, takes the minimum ordinal value (most restrictive).
    Special case: Φ uses max (Frobenius-special is highest symmetry).
    """
    result = {}
    for p in PRIMITIVE_ORDER:
        va = tuple_a[p]
        vb = tuple_b[p]
        if p == "Φ":
            result[p] = va if ordinal(p, va) >= ordinal(p, vb) else vb
        else:
            result[p] = va if ordinal(p, va) <= ordinal(p, vb) else vb
    return result


def join(tuple_a, tuple_b):
    """Least upper bound — minimal ceiling containing both.
    
    For each primitive, takes the maximum ordinal value (least restrictive).
    Special case: Φ uses min (Frobenius-special dominates).
    """
    result = {}
    for p in PRIMITIVE_ORDER:
        va = tuple_a[p]
        vb = tuple_b[p]
        if p == "Φ":
            result[p] = va if ordinal(p, va) <= ordinal(p, vb) else vb
        else:
            result[p] = va if ordinal(p, va) >= ordinal(p, vb) else vb
    return result


def tensor(tuple_a, tuple_b):
    """Composite type — coupling between two systems.
    
    Takes max on union primitives (most expansive), min on P and F.
    ⊙_3 absorption: tensor(⊙_ÿ, ⊙_3) = ⊙_3
    """
    result = {}
    for p in PRIMITIVE_ORDER:
        va = tuple_a[p]
        vb = tuple_b[p]
        if p in ("Φ", "ƒ"):  # P and F — min (most constrained wins)
            result[p] = va if ordinal(p, va) <= ordinal(p, vb) else vb
        else:
            if va == "⊙" and vb == "⊙":
                result[p] = "⊙"
            else:
                result[p] = va if ordinal(p, va) >= ordinal(p, vb) else vb
    return result


def structural_distance(tuple_a, tuple_b):
    """Weighted Euclidean distance between two organism tuples.
    
    Delegates to shared.primitives.tuple_distance for consistency
    with all other distance computations in the codebase.
    """
    return tuple_distance(tuple_a, tuple_b)

# ── CLINK Chain Distances (computed dynamically) ──────────────────

_CLINK_LAYER_NAMES = [
    ("L0", "Frustrated Belnap5 (quark color)"),
    ("L1", "Soluble Belnap5 (lepton)"),
    ("L2", "Hadron"),
    ("L3", "Nucleus"),
    ("L4", "Atom"),
    ("L5", "Molecule"),
    ("L6", "Cell (organelle-organized)"),
    ("L7", "Organism (C.elegans flatworm tier)"),
    ("L8", "Organism (human-tier, broadcast composition)"),
]

def compute_all_algebra():
    """Compute and return all meet/join/tensor/distance results from live catalog data."""
    orgs = _get_organism_tuples()
    G = orgs["universal_imscriptive_grammar"]
    R = orgs["imscribing_organism_rebis"]
    C = orgs["clink_layer8_organism"]

    meet_G_C = meet(G, C)
    join_R_C = join(R, C)
    tensor_G_C = tensor(G, C)
    tensor_G_R = tensor(G, R)

    d_G_C = structural_distance(G, C)
    d_R_C = structural_distance(R, C)
    d_G_R = structural_distance(G, R)

    return {
        "organism_tuples": {
            "grammar": G,
            "rebis": R,
            "clink_l8": C,
        },
        "meet(G, C)": {
            "tuple": meet_G_C,
            "d_from_G": structural_distance(meet_G_C, G),
            "d_from_C": structural_distance(meet_G_C, C),
            "interpretation": (
                "Grammar is the structural floor — broadcast and "
                "non-Abelian braiding are stripped away."
            ),
        },
        "join(R, C)": {
            "tuple": join_R_C,
            "d_from_R": structural_distance(join_R_C, R),
            "d_from_C": structural_distance(join_R_C, C),
            "interpretation": (
                "CLINK L8 is the structural ceiling — broadcast and "
                "non-Abelian braiding subsume conjunctive composition "
                "and integer winding."
            ),
        },
        "tensor(G, C)": {
            "tuple": tensor_G_C,
            "d_from_G": structural_distance(tensor_G_C, G),
            "d_from_C": structural_distance(tensor_G_C, C),
            "interpretation": (
                "CLINK L8 absorbs the grammar — d=0.0 from C. "
                "Grammar is a proper subset; organism = grammar + "
                "promotions at ɢ and Ω."
            ),
        },
        "tensor(G, R)": {
            "tuple": tensor_G_R,
            "d_from_G": structural_distance(tensor_G_R, G),
            "d_from_R": structural_distance(tensor_G_R, R),
            "interpretation": (
                "Grammar absorbs the Rebis — d=0.0 from G. "
                "The Rebis's conjunctive composition is overwritten "
                "by sequential in the tensor."
            ),
        },
        "d(G, C)": d_G_C,
        "d(R, C)": d_R_C,
        "d(G, R)": d_G_R,
        "_source": "computed dynamically from shared/IG_catalog.json",
    }

def clink_chain_table():
    """Return formatted CLINK chain with computed d(Ln, L8).
    
    CLINK layers are not all individually imscribed in the catalog.
    The chain is a structural narrative; distances shown use the
    two bookend entries (grammar and clink_l8) which ARE imscribed.
    """
    orgs = _get_organism_tuples()
    C = orgs["clink_layer8_organism"]
    G = orgs["universal_imscriptive_grammar"]
    d_G_C = structural_distance(G, C)
    
    lines = ["| Layer | Description | d(Ln, L8) |"]
    lines.append("|-------|-------------|-----------|")
    for i, (layer, desc) in enumerate(_CLINK_LAYER_NAMES):
        if i == 8:
            d = 0.0
        elif i == 0:
            d = d_G_C
        else:
            d = None
        d_str = f"{d:.3f}" if d is not None else "—"
        lines.append(f"| {layer} | {desc} | {d_str} |")
    lines.append("")
    lines.append("_Note: Only L0 (universal_imscriptive_grammar) and L8 ")
    lines.append("(clink_layer8_organism) are imscribed in the catalog._")
    lines.append("_Intermediate layers need individual imscription._")
    return "\n".join(lines)


if __name__ == "__main__":
    results = compute_all_algebra()
    info_line("=== Organism Structural Algebra (live from catalog) ===\n")
    for key, val in results.items():
        if isinstance(val, dict):
            print(f"{key}:")
            for k, v in val.items():
                if k == "tuple":
                    info_line(f"  {k}: {dict((p, v[p]) for p in PRIMITIVE_ORDER)}")
                elif k == "interpretation":
                    info_line(f"  {k}: {v}")
                else:
                    info_line(f"  {k}: {v}")
        elif isinstance(val, (int, float)):
            print(f"{key}: {round(val, 4)}")
        else:
            print(f"{key}: {val}")
    print()
    print(clink_chain_table())
