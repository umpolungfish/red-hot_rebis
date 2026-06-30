"""
chain.py — CLINK 9-Layer Chain Definition
===========================================
Each layer is a 12-primitive Imscription tuple (using Shavian glyph keys),
verified against the Lean 4 formalization in p4rakernel.

All 9 layers are Frobenius-closed (tensorProduct(s,s)=s).
Foundation: ZFC_fe (O_∞ with Ð=𐑦, Φ=𐑹, Ħ=𐑫).

Author: Lando ⊗ ⊙perator
"""

import math, sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.rich_output import *
from shared.primitives import (
    ORDINALS, WEIGHTS, to_vector, tuple_distance
)

# Canonical primitive order (Shavian glyph keys)
PORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]

# ═══════════════════════════════════════════════════════════════════
# LAYER 0 — Frustrated Belnap5 (Quark Color)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑛𐑶𐑩𐑯𐑐𐑘𐑚𐑝𐑢𐑓𐑳𐑷⟩  O₀
FRUSTRATED_BELNAP5 = {
    "Ð": "𐑛", "Þ": "𐑶", "Ř": "𐑩", "Φ": "𐑯",
    "ƒ": "𐑐", "Ç": "𐑘", "Γ": "𐑚", "ɢ": "𐑝",
    "⊙": "𐑢", "Ħ": "𐑓", "Σ": "𐑳", "Ω": "𐑷",
    "_name": "frustratedBelnap5",
    "_desc": "Frustrated Belnap5 — SU(3) quark color with confinement",
    "_tier": "O₀",
}

# LAYER 1 — Electron Orbital (Belnap4)
# ⟨𐑛𐑶𐑩𐑗𐑐𐑤𐑚𐑜𐑢𐑓𐑳𐑷⟩  O₀
ELECTRON_ORBITAL_LAYER = {
    "Ð": "𐑛", "Þ": "𐑶", "Ř": "𐑩", "Φ": "𐑗",
    "ƒ": "𐑐", "Ç": "𐑤", "Γ": "𐑚", "ɢ": "𐑜",
    "⊙": "𐑢", "Ħ": "𐑓", "Σ": "𐑳", "Ω": "𐑷",
    "_name": "electronOrbitalLayer",
    "_desc": "Belnap4 orbital occupancy — 4-valued lattice",
    "_tier": "O₀",
}

# LAYER 2 — Atom (Nuclear + Electron)
# ⟨𐑼𐑥𐑽𐑿𐑐𐑤𐑔𐑝𐑮𐑒𐑳𐑷⟩  O₁
ATOM_LAYER = {
    "Ð": "𐑼", "Þ": "𐑥", "Ř": "𐑽", "Φ": "𐑿",
    "ƒ": "𐑐", "Ç": "𐑤", "Γ": "𐑔", "ɢ": "𐑝",
    "⊙": "𐑮", "Ħ": "𐑒", "Σ": "𐑳", "Ω": "𐑷",
    "_name": "atomLayer", "_desc": "Atom — nuclear + electron", "_tier": "O₁",
}

# LAYER 3 — Molecule (Chemical Bonds)
# ⟨𐑼𐑥𐑽𐑿𐑞𐑧𐑲𐑠⊙𐑓𐑳𐑭⟩  O₂
MOLECULE_LAYER = {
    "Ð": "𐑼", "Þ": "𐑥", "Ř": "𐑽", "Φ": "𐑿",
    "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑓", "Σ": "𐑳", "Ω": "𐑭",
    "_name": "moleculeLayer", "_desc": "Molecule — chemical bonds", "_tier": "O₂",
}

# LAYER 4 — Cell (Living)
# ⟨𐑦𐑸𐑾𐑬𐑞𐑧𐑲𐑠⊙𐑒𐑳𐑭⟩  O₂
CELL_LAYER = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑬",
    "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑒", "Σ": "𐑳", "Ω": "𐑭",
    "_name": "cellLayer", "_desc": "Cell — minimal self-maintaining unit", "_tier": "O₂",
}

# LAYER 5 — Mitosis (Cell Division)
# ⟨𐑦𐑸𐑾𐑹𐑱𐑧𐑲𐑠⊙𐑖𐑳𐑭⟩  O₂
MITOSIS_LAYER = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹",
    "ƒ": "𐑱", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑭",
    "_name": "mitosisLayer", "_desc": "Mitosis — cell division", "_tier": "O₂",
}

# LAYER 6 — Meiosis (Gamete Production)
# ⟨𐑦𐑸𐑽𐑿𐑱𐑧𐑲𐑠⊙𐑖𐑳𐑭⟩  O₂
MEIOSIS_LAYER = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑽", "Φ": "𐑿",
    "ƒ": "𐑱", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑭",
    "_name": "meiosisLayer", "_desc": "Meiosis — gamete production", "_tier": "O₂",
}

# LAYER 7 — Tissue / Organ (Multi-cellular)
# ⟨𐑦𐑸𐑾𐑬𐑞𐑧𐑲𐑵⊙𐑖𐑳𐑭⟩  O₂
TISSUE_LAYER = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑬",
    "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑵",
    "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑭",
    "_name": "tissueLayer", "_desc": "Tissue — multi-cellular organization", "_tier": "O₂",
}

# LAYER 8 — Whole Organism
# ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩  O_∞
ORGANISM_LAYER = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹",
    "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑵",
    "⊙": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑟",
    "_name": "organismLayer",
    "_desc": "Whole organism — O_∞, C=1.0",
    "_tier": "O_∞",
}

# ═══════════════════════════════════════════════════════════════════
# CHAIN ACCESS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

CLINK_LAYERS = [
    FRUSTRATED_BELNAP5, ELECTRON_ORBITAL_LAYER, ATOM_LAYER,
    MOLECULE_LAYER, CELL_LAYER, MITOSIS_LAYER,
    MEIOSIS_LAYER, TISSUE_LAYER, ORGANISM_LAYER,
]

CLINK_NAMES = [
    "Frustrated Belnap5 (Quarks)", "Electron Orbital (Belnap4)",
    "Atom (Nuclear + Electron)", "Molecule (Chemical Bonds)",
    "Cell (Living)", "Mitosis (Division)", "Meiosis (Gametes)",
    "Tissue/Organ", "Whole Organism",
]


def compute_tier_from_tuple(tup):
    """Compute ouroboricity tier from tuple primitives.
    
    Tiers are determined by φ̂ (criticality gate 1) and Ç (kinetics gate 2):
      O₀:  φ̂=𐑢 or φ̂=𐑻 or φ̂=𐑣 (no self-modeling gate)
      O₁:  φ̂=𐑮 (complex-plane critical, gate 1 partial)
      O₂:  φ̂=⊙ AND (Ç≠𐑧 OR Ħ≠𐑫) (gate 1 open, gate 2 closed)
      O_∞: φ̂=⊙ AND Ç=𐑧 AND Ħ=𐑫 (both gates open, eternal chirality)
    
    This is a local computation from tuple primitives — for authoritative
    tier assignment use imscribe("ouroborics", ...) which considers the
    full 12-primitive structure.
    """
    phi = tup.get("⊙", tup.get("φ̂", "𐑢"))
    k = tup.get("Ç", "𐑘")
    h = tup.get("Ħ", "𐑓")
    
    if phi == "⊙" and k == "𐑧" and h == "𐑫":
        return "O_∞"
    elif phi == "⊙":
        return "O₂"
    elif phi == "𐑮":
        return "O₁"
    else:
        return "O₀"

def compute_c_score_from_tuple(tup):
    """Compute consciousness C-score from tuple primitives.
    
    Gate 1 (φ̂): ⊙=1.0, 𐑮=0.5, else 0.0
    Gate 2 (Ç):  𐑧=1.0, 𐑤=0.5, else 0.0
    
    C = gate1 * gate2  (both must be open for C>0)
    """
    phi = tup.get("⊙", tup.get("φ̂", "𐑢"))
    k = tup.get("Ç", "𐑘")
    
    gate1 = 1.0 if phi == "⊙" else (0.5 if phi == "𐑮" else 0.0)
    gate2 = 1.0 if k == "𐑧" else (0.5 if k == "𐑤" else 0.0)
    
    return round(gate1 * gate2, 4)

def clink_frobenius_closed(name_or_idx_or_tup):
    """Check tensor-product Frobenius closure: tensorProduct(s,s) = s.
    
    Args:
        name_or_idx_or_tup: layer index (int), name (str), or tuple dict
    
    Returns:
        bool
    """
    from ch3mpiler.compiler import tensor_type

    
    # Handle dict (tuple) case
    if isinstance(name_or_idx_or_tup, dict):
        # Check if it uses PORDER keys (Shavian) or ch3mpiler keys
        if all(k in name_or_idx_or_tup for k in PORDER):
            tup_py = {k: name_or_idx_or_tup[k] for k in PORDER}
        else:
            # Assume ch3mpiler format and convert
            ch3_to_porder = {"D":"Ð","T":"Þ","R":"Ř","P":"Φ","F":"ƒ",
                             "K":"Ç","G":"Γ","Gm":"ɢ","Ph":"⊙","H":"Ħ","S":"Σ","W":"Ω"}
            tup_py = {ch3_to_porder[k]: v for k, v in name_or_idx_or_tup.items() 
                      if k in ch3_to_porder}
    else:
        tup_py = clink_layer_tuple(name_or_idx_or_tup, include_meta=False)
    
    gly2ch3 = {"Ð":"D","Þ":"T","Ř":"R","Φ":"P","ƒ":"F","Ç":"K",
               "Γ":"G","ɢ":"Gm","⊙":"Ph","Ħ":"H","Σ":"S","Ω":"W"}
    tup_ch3 = {gly2ch3[k]: v for k, v in tup_py.items()}
    tt = tensor_type(tup_ch3, tup_ch3)
    return all(tt[gly2ch3[p]] == tup_py[p] for p in PORDER)

CLINK_TIERS = [compute_tier_from_tuple(l) for l in CLINK_LAYERS]

def clink_layer_index(name_or_idx):
    if isinstance(name_or_idx, int):
        return max(0, min(8, name_or_idx))
    name_map = {l["_name"]: i for i, l in enumerate(CLINK_LAYERS)}
    return name_map.get(name_or_idx, -1)

def clink_layer_tuple(name_or_idx, include_meta=False):
    idx = clink_layer_index(name_or_idx)
    if idx < 0:
        raise KeyError(f"Unknown CLINK layer: {name_or_idx}")
    layer = CLINK_LAYERS[idx]
    return dict(layer) if include_meta else {k: v for k, v in layer.items() if k in PORDER}

def clink_distance(layer_a, layer_b):
    if isinstance(layer_a, dict) and all(p in layer_a for p in PORDER):
        tup_a = layer_a
    else:
        tup_a = clink_layer_tuple(layer_a)
    if isinstance(layer_b, dict) and all(p in layer_b for p in PORDER):
        tup_b = layer_b
    else:
        tup_b = clink_layer_tuple(layer_b)
    return tuple_distance(tup_a, tup_b)

def primitive_deltas(idx_from, idx_to):
    a, b = CLINK_LAYERS[idx_from], CLINK_LAYERS[idx_to]
    return [{"primitive": p, "from": a[p], "to": b[p]} for p in PORDER if a[p] != b[p]]

def primitive_mismatch_count(idx_from, idx_to):
    return len(primitive_deltas(idx_from, idx_to))

def verify_all_frobenius_closed():
    results = {}
    all_closed = True
    for i, layer in enumerate(CLINK_LAYERS):
        closed = clink_frobenius_closed(i)
        results[layer["_name"]] = closed
        if not closed: all_closed = False
    return {"all_closed": all_closed, "per_layer": results}

def clink_chain_distance():
    steps = []
    for i in range(8):
        d = clink_distance(i, i+1)
        steps.append({
            "from": CLINK_NAMES[i], "to": CLINK_NAMES[i+1],
            "from_tier": CLINK_TIERS[i], "to_tier": CLINK_TIERS[i+1],
            "distance": round(d, 4),
            "deltas": primitive_deltas(i, i+1),
        })
    return {
        "steps": steps,
        "total_distance": round(clink_distance(0, 8), 4),
        "total_primitive_deltas": primitive_mismatch_count(0, 8),
    }

def format_tuple_glyphs(tup_dict):
    """Format a CLINK layer tuple as ⟨𐑦𐑸𐑾...⟩ string."""
    return "⟨" + "".join(tup_dict.get(p, "?") for p in PORDER) + "⟩"



if __name__ == "__main__":
    frob = verify_all_frobenius_closed()
    info_line("CLINK Frobenius Closure:")
    for name, closed in frob["per_layer"].items():
        info_line(f"  {'✅' if closed else '❌'} {name}: {closed}")
    info_line(f"All closed: {frob['all_closed']}")

    chain = clink_chain_distance()
    info_line(f"\nCLINK Chain: Σd={chain['total_distance']}, {chain['total_primitive_deltas']} deltas")
    for s in chain["steps"]:
        info_line(f"  {s['from']} → {s['to']}: d={s['distance']} ({len(s['deltas'])} primitives)")

    org = clink_layer_tuple(8, True)
    info_line(f"\nOrganism: {format_tuple_glyphs(org)}  Tier={org['_tier']}")
    info_line(f"Frobenius-closed: {clink_frobenius_closed(8)}")
