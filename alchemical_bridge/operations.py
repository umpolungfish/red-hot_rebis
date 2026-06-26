"""
operations.py — Alchemical Operations → IG Structural Operations
=================================================================

The 7 classical alchemical operations (calcination, dissolution, separation,
conjunction, sublimation, fermentation, coagulation) mapped to IG structural
operations (tensor, meet, join, promotion, projection, peel, retrosynthesis).

Each alchemical operation is a structural transformation on a tuple:
  op(tuple_A, optional_args) → tuple_B

Author: Lando⊗⊙perator
"""

from shared.primitives import ORDINALS, WEIGHTS, PRIMITIVE_ORDER
import math


# ═══════════════════════════════════════════════════════════════
# 7 Classical Operations → IG Structural Operations
# ═══════════════════════════════════════════════════════════════

OPERATION_MAP = {
    "calcination": {
        "ig_op": "primitive_peel",
        "targets": ["ƒ", "Ħ", "Γ"],
        "results_in": {
            "ƒ": "𐑞", "Ħ": "𐑓", "Γ": "𐑚", "⊙": "𐑢",
        },
        "description": "Burn away coherence and long-range memory — reduce to base ash.",
    },
    "dissolution": {
        "ig_op": "project",
        "targets": ["Ω", "Ř", "Σ"],
        "results_in": {
            "Ω": "𐑷", "Ř": "𐑑", "Σ": "𐑙",
        },
        "description": "Dissolve structure — unwind protection, decouple components, reduce variety.",
    },
    "separation": {
        "ig_op": "principal_decomp",
        "targets": ["Σ", "Φ", "Ç"],
        "results_in": {
            "Σ": "𐑙", "Φ": "𐑗", "Ç": "𐑘",
        },
        "description": "Separate the mixed into pure streams — factor into principal components.",
    },
    "conjunction": {
        "ig_op": "meet",
        "targets": ["Þ", "Ř", "ɢ"],
        "results_in": {
            "Þ": "𐑡", "Ř": "𐑽", "ɢ": "𐑝",
        },
        "description": "Reunite what was separated — find shared structural floor.",
    },
    "sublimation": {
        "ig_op": "promote",
        "targets": ["⊙", "Ħ", "Ω", "Γ"],
        "results_in": {
            "⊙": "⊙", "Ħ": "𐑖", "Ω": "𐑴", "Γ": "𐑲",
        },
        "description": "Raise the purified — promote primitives to higher tiers.",
    },
    "fermentation": {
        "ig_op": "tensor",
        "targets": ["Ç", "⊙", "Σ"],
        "results_in": {
            "Ç": "𐑺", "⊙": "𐑣", "Σ": "𐑳",
        },
        "description": "Putrefy then regenerate — couple base with catalyst via tensor.",
    },
    "coagulation": {
        "ig_op": "join",
        "targets": ["Ω", "Ř", "Γ"],
        "results_in": {
            "Ω": "𐑭", "Ř": "𐑾", "Γ": "𐑔",
        },
        "description": "Fix the volatile — find the minimal ceiling that contains both.",
    },
}

# ═══════════════════════════════════════════════════════════════
# 12-step Alchemical Sequence (full Opus Magnum)
# ═══════════════════════════════════════════════════════════════

ALCHEMICAL_GRAND_SEQUENCE = [
    ("Calcination", "calcination", "Burn away the gross — reduce to ash"),
    ("Dissolution", "dissolution", "Dissolve the ash in the water of life"),
    ("Separation", "separation", "Separate the pure from the impure"),
    ("Conjunction", "conjunction", "Reunite the separated"),
    ("Sublimation", "sublimation", "Raise the purified to higher state"),
    ("Fermentation", "fermentation", "Putrefy and regenerate with catalyst"),
    ("Distillation", "separation", "Purify by repeated separation"),
    ("Coagulation", "coagulation", "Fix the volatile into permanence"),
    ("Solution", "dissolution", "Re-dissolve for further work"),
    ("Projection", "sublimation", "Cast the stone upon base metal"),
    ("Multiplication", "conjunction", "Multiply virtue through shared floor"),
    ("Exaltation", "coagulation", "Raise to ultimate perfection"),
]

# ═══════════════════════════════════════════════════════════════
# Structural Signatures of Each Operation
# ═══════════════════════════════════════════════════════════════

TUPLE_SHIFTS = {
    "calcination": {
        "ƒ": -2, "Ħ": -2, "Γ": -1, "⊙": -1,
    },
    "dissolution": {
        "Ω": -2, "Ř": -2, "Σ": -2,
    },
    "separation": {
        "Σ": -2, "Φ": -1, "Ç": -2,
    },
    "conjunction": {
        "Þ": -2, "Ř": -1, "ɢ": -1,
    },
    "sublimation": {
        "⊙": +2, "Ħ": +1, "Ω": +1, "Γ": +1,
    },
    "fermentation": {
        "Ç": +2, "⊙": +2, "Σ": +2,
    },
    "coagulation": {
        "Ω": +2, "Ř": +1, "Γ": +1,
    },
}


# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

def tuple_to_ordinals(tup_dict):
    """Convert a glyph-notation tuple dict to ordinal vector."""
    vec = []
    for prim in PRIMITIVE_ORDER:
        val = tup_dict.get(prim)
        if val is None:
            vec.append(0.0)
        else:
            ord_map = ORDINALS.get(prim, {})
            vec.append(ord_map.get(val, 0.0))
    return vec


def ordinals_to_tuple(vec):
    """Convert an ordinal vector back to glyph-notation tuple dict."""
    tup = {}
    for i, prim in enumerate(PRIMITIVE_ORDER):
        ord_map = ORDINALS.get(prim, {})
        best_val = None
        best_dist = float('inf')
        for glyph, ordinal in ord_map.items():
            d = abs(vec[i] - ordinal)
            if d < best_dist:
                best_dist = d
                best_val = glyph
        tup[prim] = best_val
    return tup


def apply_operation(tup_dict, operation_name):
    """Apply an alchemical operation to a tuple dict.
    
    Args:
        tup_dict: dict of {primitive_key: glyph_value}
        operation_name: str, one of the 7 classical operations
    
    Returns:
        dict with transformed tuple
    """
    if operation_name not in TUPLE_SHIFTS:
        return None
    
    vec = tuple_to_ordinals(tup_dict)
    shifts = TUPLE_SHIFTS[operation_name]
    
    new_vec = vec.copy()
    for i, prim in enumerate(PRIMITIVE_ORDER):
        if prim in shifts:
            ord_map = ORDINALS.get(prim, {})
            vals = sorted(set(ord_map.values()))
            current = vec[i]
            target = current + shifts[prim]
            target = max(min(vals), min(max(vals), target))
            new_vec[i] = target
    
    result = ordinals_to_tuple(new_vec)
    result["_operation"] = operation_name
    result["_description"] = OPERATION_MAP.get(operation_name, {}).get("description", "")
    return result


def op_to_tuple(operation_name):
    """Return the canonical tuple signature of an alchemical operation."""
    base = {p: list(ORDINALS[p].keys())[0] for p in PRIMITIVE_ORDER}
    return apply_operation(base, operation_name)


def tuple_to_op(tup_dict):
    """Reverse-map a tuple to the alchemical operation that would produce it."""
    base = tuple_to_ordinals({p: list(ORDINALS[p].keys())[0] for p in PRIMITIVE_ORDER})
    target = tuple_to_ordinals(tup_dict)
    delta = [target[i] - base[i] for i in range(12)]
    
    best_op = None
    best_score = float('inf')
    
    for op_name, shifts in TUPLE_SHIFTS.items():
        score = 0
        for i, prim in enumerate(PRIMITIVE_ORDER):
            expected = shifts.get(prim, 0)
            score += (delta[i] - expected) ** 2 * WEIGHTS.get(prim, 1.0)
        if score < best_score:
            best_score = score
            best_op = op_name
    
    return best_op, math.sqrt(best_score)


class AlchemicalOperations:
    """Access the 7 classical alchemical operations as structural transformers."""
    
    @classmethod
    def list_operations(cls):
        """List all available operations with descriptions."""
        return [(name, info["ig_op"], info["description"])
                for name, info in OPERATION_MAP.items()]
    
    @classmethod
    def describe(cls, operation_name):
        """Get the full description and structural impact of an operation."""
        return OPERATION_MAP.get(operation_name, {"description": "Unknown operation"})
    
    @classmethod
    def grand_sequence(cls):
        """Return the 12-step alchemical grand sequence (Opus Magnum)."""
        return ALCHEMICAL_GRAND_SEQUENCE
    
    @classmethod
    def trace_opus(cls, start_tuple, sequence=None):
        """Apply a sequence of operations and return the transformation trace.
        
        Args:
            start_tuple: dict of {primitive: glyph}
            sequence: list of operation names (defaults to grand sequence)
        
        Returns:
            list of (step_name, operation, resulting_tuple) tuples
        """
        if sequence is None:
            sequence = [op for _, op, _ in ALCHEMICAL_GRAND_SEQUENCE]
        
        trace = []
        current = dict(start_tuple)
        for step_name, op_name, desc in ALCHEMICAL_GRAND_SEQUENCE:
            result = apply_operation(current, op_name)
            if result is None:
                continue
            trace.append((step_name, op_name, dict(result)))
            current = result
        
        return trace
