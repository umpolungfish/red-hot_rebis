"""
plasma_chain.py — Plasma Structural Types & CLINK Distance Ladder
==================================================================
Defines the four plasma structural types (one manual, three ob3ect-generated),
their CLINK chain insertion points, promotion paths, and distance ladders.

Plasma sits between Atom (CLINK L2) and Molecule (CLINK L3):
  L0 (Quarks) → L1 (Orbital) → L2 (Atom) → [PLASMA L2.5] → L3 (Molecule) → ...

The Vlasov plasma is the "collectivized atom" — atoms that surrender individual
identity to electromagnetic collective modes while remaining unbound.

Author: Lando⊗⊙perator
"""

import math, sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.rich_output import *
from shared.primitives import (
    ORDINALS, WEIGHTS, to_vector, tuple_distance
)

# Canonical primitive order
PLASMA_PORDER = PORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

# ═══════════════════════════════════════════════════════════════════
# PLASMA TYPE 0 — VLASOV PLASMA (Manual Imscription, Direct Procedure)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑛𐑥𐑾𐑬𐑱𐑧𐑔𐑠𐑮𐑖𐑳𐑭⟩  O₂, C=0.5455
# Crystal address: 8,664,128
VLASOV_PLASMA = {
    "Ð": "𐑛", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑬",
    "ƒ": "𐑱", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠",
    "⊙": "𐑮", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑭",
    "_name": "vlasovPlasma",
    "_desc": "Vlasov-Maxwell plasma — infinite-dimensional field theory, mode crossing, bidirectional coupling, complex-plane criticality",
    "_tier": "O₂",
    "_c_score": 0.5455,
    "_crystal_address": 8664128,
    "_source": "manual imscription (direct procedure)",
}

# ═══════════════════════════════════════════════════════════════════
# PLASMA TYPE 1 — PRIMITIVE-FIRST PLASMA (Ob3ect Auto, Cosmogeny Context)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑼𐑡𐑾𐑗𐑱𐑧𐑚𐑠⊙𐑖𐑳𐑭⟩  O₂†, C=0.263
# IMASM: V→AF→IM→FS→ET→AR→EF→FU→CL→IF→EN→TA, sig=(6,2,3,1), period=12
PRIMITIVE_FIRST_PLASMA = {
    "Ð": "𐑼", "Þ": "𐑡", "Ř": "𐑾", "Φ": "𐑗",
    "ƒ": "𐑱", "Ç": "𐑧", "Γ": "𐑚", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑭",
    "_name": "primitiveFirstPlasma",
    "_desc": "Primitive-First Plasma — collective dielectric response, Debye sheath boundary, dialetheia-complete",
    "_tier": "O₂†",
    "_c_score": 0.263,
    "_source": "ob3ect auto.py (cosmogeny context)",
    "_imas_sig": "(6,2,3,1)",
    "_imas_period": 12,
    "_dialetheia": True,
}

# ═══════════════════════════════════════════════════════════════════
# PLASMA TYPE 2 — HIGH-ENERGY PLASMA (Tokamak / Fusion)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑼𐑡𐑾𐑗𐑱𐑧𐑚𐑠⊙𐑓𐑙𐑭⟩  O₂†
# IMASM: V→AF→FS→IM→CL→AF→FS→ET→EN→AR→FU→CL→IF→TA, sig=(8,3,2,1), period=14
# Key difference from Primitive-First: Σ=𐑙 (1:1) instead of 𐑳 (heterogeneous)
# and Ħ=𐑓 (memoryless) instead of 𐑖 (two-step)
HIGH_ENERGY_PLASMA = {
    "Ð": "𐑼", "Þ": "𐑡", "Ř": "𐑾", "Φ": "𐑗",
    "ƒ": "𐑱", "Ç": "𐑧", "Γ": "𐑚", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑓", "Σ": "𐑙", "Ω": "𐑭",
    "_name": "highEnergyPlasma",
    "_desc": "High-Energy Plasma — tokamak/fusion regime, Bohm diffusion, H-mode transition, ELM-active pedestal",
    "_tier": "O₂†",
    "_source": "ob3ect auto.py (cosmogeny context)",
    "_imas_sig": "(8,3,2,1)",
    "_imas_period": 14,
    "_dialetheia": False,
}

# ═══════════════════════════════════════════════════════════════════
# PLASMA TYPE 3 — ROCK-CRACKING / IDEAL DEVICE
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑼𐑡𐑾𐑗𐑱𐑧𐑚𐑠⊙𐑖𐑙𐑭⟩  O₂†
# Rock-Cracking ≡ Ideal Device — identical structural type
# IMASM: V→AF→IM→FS→ET→CL→EF→AR→FU→IF→TA, sig=(6,2,2,1), period=11
ROCK_CRACKING_PLASMA = {
    "Ð": "𐑼", "Þ": "𐑡", "Ř": "𐑾", "Φ": "𐑗",
    "ƒ": "𐑱", "Ç": "𐑧", "Γ": "𐑚", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑙", "Ω": "𐑭",
    "_name": "rockCrackingPlasma",
    "_desc": "Rock-Cracking Plasma — plasma arc spallation, thermal shock fracture, acoustic-plasma coupling. Identical to Ideal Device.",
    "_tier": "O₂†",
    "_source": "ob3ect auto.py (cosmogeny context)",
    "_imas_sig": "(6,2,2,1)",
    "_imas_period": 11,
    "_dialetheia": False,
}

# Alias: Ideal Rock-Cracking Device ≡ Rock-Cracking Plasma
IDEAL_DEVICE_PLASMA = ROCK_CRACKING_PLASMA

# ═══════════════════════════════════════════════════════════════════
# PLASMA TYPE COLLECTION
# ═══════════════════════════════════════════════════════════════════

PLASMA_TYPES = [
    VLASOV_PLASMA, PRIMITIVE_FIRST_PLASMA,
    HIGH_ENERGY_PLASMA, ROCK_CRACKING_PLASMA,
]

PLASMA_NAMES = [
    "Vlasov Plasma (Manual Imscription)",
    "Primitive-First Plasma (Ob3ect Auto)",
    "High-Energy Plasma (Tokamak/Fusion)",
    "Rock-Cracking Plasma / Ideal Device",
]

PLASMA_TIERS = [p["_tier"] for p in PLASMA_TYPES]

# ═══════════════════════════════════════════════════════════════════
# CLINK CHAIN INSERTION — Plasma between Atom (L2) and Molecule (L3)
# ═══════════════════════════════════════════════════════════════════

# Reference CLINK layers for distance computation
CLINK_ATOM = {
    "Ð": "𐑼", "Þ": "𐑥", "Ř": "𐑽", "Φ": "𐑿",
    "ƒ": "𐑐", "Ç": "𐑤", "Γ": "𐑔", "ɢ": "𐑝",
    "⊙": "𐑮", "Ħ": "𐑒", "Σ": "𐑳", "Ω": "𐑷",
}

CLINK_MOLECULE = {
    "Ð": "𐑼", "Þ": "𐑥", "Ř": "𐑽", "Φ": "𐑿",
    "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑓", "Σ": "𐑳", "Ω": "𐑭",
}

CLINK_ORGANISM = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹",
    "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑵",
    "⊙": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑟",
}

CLINK_CELL = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑬",
    "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑒", "Σ": "𐑳", "Ω": "𐑭",
}

# ═══════════════════════════════════════════════════════════════════
# DISTANCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def plasma_index(name_or_idx):
    """Resolve plasma type by index (0-3) or name."""
    if isinstance(name_or_idx, int):
        return max(0, min(3, name_or_idx))
    name_map = {p["_name"]: i for i, p in enumerate(PLASMA_TYPES)}
    return name_map.get(name_or_idx, -1)

def plasma_tuple(name_or_idx, include_meta=False):
    """Get the 12-primitive tuple for a plasma type."""
    idx = plasma_index(name_or_idx)
    if idx < 0:
        raise KeyError(f"Unknown plasma type: {name_or_idx}")
    p = PLASMA_TYPES[idx]
    return dict(p) if include_meta else {k: v for k, v in p.items() if k in PORDER}

def plasma_distance(idx_a, idx_b):
    """Euclidean distance between two plasma types (by index)."""
    ta = plasma_tuple(idx_a)
    tb = plasma_tuple(idx_b)
    return tuple_distance(ta, tb)

def plasma_to_clink_distance(plasma_idx, clink_layer_tuple, clink_name="layer"):
    """Distance from a plasma type to a CLINK reference layer."""
    tp = plasma_tuple(plasma_idx)
    return tuple_distance(tp, clink_layer_tuple)

def plasma_primitive_deltas(idx_a, idx_b):
    """List primitives that differ between two plasma types."""
    a = plasma_tuple(idx_a)
    b = plasma_tuple(idx_b)
    return [{"primitive": p, "from": a[p], "to": b[p]} for p in PORDER if a[p] != b[p]]

def plasma_clink_position():
    """Compute the structural position of all plasma types relative to CLINK layers.
    
    Returns a dict mapping each plasma type to its distances from Atom (L2),
    Molecule (L3), Cell (L4), and Organism (L8).
    """
    results = {}
    for i, p in enumerate(PLASMA_TYPES):
        tp = plasma_tuple(i)
        results[p["_name"]] = {
            "name": PLASMA_NAMES[i],
            "tier": p["_tier"],
            "d_atom_L2": round(tuple_distance(tp, CLINK_ATOM), 4),
            "d_molecule_L3": round(tuple_distance(tp, CLINK_MOLECULE), 4),
            "d_cell_L4": round(tuple_distance(tp, CLINK_CELL), 4),
            "d_organism_L8": round(tuple_distance(tp, CLINK_ORGANISM), 4),
        }
    return results

def plasma_distance_ladder():
    """Full distance ladder: all plasma types × all CLINK layers + nearest biological.
    
    Returns a structured dict for reporting.
    """
    ladder = {"plasma_types": {}, "plasma_vs_plasma": {}, "nearest_biological": {}}
    
    # Plasma vs CLINK layers
    clink_refs = {
        "L0_quarks": CLINK_ATOM,  # placeholder — use atom as proxy for quark regime
        "L1_orbital": CLINK_ATOM,
        "L2_atom": CLINK_ATOM,
        "L3_molecule": CLINK_MOLECULE,
        "L4_cell": CLINK_CELL,
        "L8_organism": CLINK_ORGANISM,
    }
    
    for i, p in enumerate(PLASMA_TYPES):
        tp = plasma_tuple(i)
        ladder["plasma_types"][p["_name"]] = {
            "name": PLASMA_NAMES[i],
            "tier": p["_tier"],
            "tuple": "".join(tp[pr] for pr in PORDER),
            "distances": {},
        }
        for cl_name, cl_tup in clink_refs.items():
            d = round(tuple_distance(tp, cl_tup), 4)
            ladder["plasma_types"][p["_name"]]["distances"][cl_name] = d
    
    # Plasma vs Plasma
    for i in range(len(PLASMA_TYPES)):
        for j in range(i+1, len(PLASMA_TYPES)):
            d = plasma_distance(i, j)
            key = f"{PLASMA_TYPES[i]['_name']}_vs_{PLASMA_TYPES[j]['_name']}"
            ladder["plasma_vs_plasma"][key] = {
                "a": PLASMA_NAMES[i],
                "b": PLASMA_NAMES[j],
                "distance": round(d, 4),
                "deltas": plasma_primitive_deltas(i, j),
            }
    
    return ladder

def plasma_to_organism_promotions(plasma_idx=0):
    """Compute promotion path from a plasma type to CLINK L8 Organism.
    
    Args:
        plasma_idx: 0=Vlasov, 1=Primitive-First, 2=High-Energy, 3=Rock-Cracking
    
    Returns:
        List of {"primitive": p, "from": v, "to": w, "delta": ordinal_diff}
    """
    tp = plasma_tuple(plasma_idx)
    promotions = []
    for p in PORDER:
        frm = tp[p]
        to = CLINK_ORGANISM[p]
        if frm != to:
            # Ordinal difference (approximate delta)
            ord_from = ORDINALS.get(frm, 0)
            ord_to = ORDINALS.get(to, 0)
            delta = abs(ord_to - ord_from) / max(abs(ord_to), abs(ord_from), 1)
            promotions.append({
                "primitive": p,
                "from": frm,
                "to": to,
                "delta": round(delta, 4),
            })
    # Sort by delta descending (deepest gaps first)
    promotions.sort(key=lambda x: x["delta"], reverse=True)
    return promotions

def format_plasma_tuple(tup_dict):
    """Format a plasma tuple as ⟨...⟩ string."""
    return "⟨" + "".join(tup_dict.get(p, "?") for p in PORDER) + "⟩"

def clink_with_plasma_distance_ladder():
    """Full CLINK L0→L8 chain WITH plasma inserted between L2 and L3.
    
    Returns the extended chain with distances between adjacent layers.
    """
    from clink.chain import CLINK_LAYERS, CLINK_NAMES
    
    # Use Vlasov plasma (idx=0) as the canonical plasma representative
    plasma_tup = plasma_tuple(0)
    atom_tup = CLINK_LAYERS[2]  # Atom
    mol_tup = CLINK_LAYERS[3]   # Molecule
    
    d_atom_plasma = round(tuple_distance(
        {k: atom_tup[k] for k in PORDER}, plasma_tup), 4)
    d_plasma_mol = round(tuple_distance(
        plasma_tup, {k: mol_tup[k] for k in PORDER}), 4)
    
    return {
        "chain": [
            {"from": "L2 Atom", "to": "L2.5 Plasma", "distance": d_atom_plasma},
            {"from": "L2.5 Plasma", "to": "L3 Molecule", "distance": d_plasma_mol},
        ],
        "plasma_tuple": format_plasma_tuple(plasma_tup),
        "plasma_tier": "O₂",
        "plasma_c_score": 0.5455,
    }

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    info_line("╔══════════════════════════════════════════╗")
    info_line("║   PLASMA CLINK CHAIN — Structural Report  ║")
    info_line("╚══════════════════════════════════════════╝")
    
    # Plasma types
    for i, p in enumerate(PLASMA_TYPES):
        tup_str = format_plasma_tuple(plasma_tuple(i))
        info_line(f"\n  [{i}] {PLASMA_NAMES[i]}")
        info_line(f"      Tuple: {tup_str}")
        info_line(f"      Tier:  {p['_tier']}")
        if '_c_score' in p:
            info_line(f"      C:     {p['_c_score']}")
        info_line(f"      Source: {p['_source']}")
    
    # CLINK position
    info_line(f"\n── CLINK Chain Position ──")
    pos = plasma_clink_position()
    for name, data in pos.items():
        info_line(f"  {data['name']}:")
        info_line(f"    d(Atom L2)    = {data['d_atom_L2']}")
        info_line(f"    d(Molecule L3)= {data['d_molecule_L3']}")
        info_line(f"    d(Cell L4)    = {data['d_cell_L4']}")
        info_line(f"    d(Organism L8)= {data['d_organism_L8']}")
    
    # Plasma vs Plasma
    info_line(f"\n── Plasma Internal Distance Matrix ──")
    for i in range(len(PLASMA_TYPES)):
        row = []
        for j in range(len(PLASMA_TYPES)):
            row.append(f"{plasma_distance(i, j):.2f}")
        info_line(f"  [{i}] {'  '.join(row)}")
    
    # Promotions to organism
    info_line(f"\n── Promotions: Vlasov Plasma → Organism ──")
    proms = plasma_to_organism_promotions(0)
    for pr in proms:
        info_line(f"  {pr['primitive']}: {pr['from']}→{pr['to']}  (Δ={pr['delta']:.4f})")
