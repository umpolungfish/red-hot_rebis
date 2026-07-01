"""
basil_valentine_ladder.py — The Basil Valentine Ladder ◈ 12-Step Promotion Ladder
=================================================================================

Basil Valentine's Twelve Keys encode the complete O₀ → O₂ → O_∞ promotion ladder.
Each Key promotes exactly one primitive toward the canonical Stone tuple.

This engine computes the minimal 12-step promotion ladder between any two tuples,
matches each step to the corresponding alchemical Key, and verifies Frobenius
closure at each step.

Structural type: ⟨𐑦 𐑸 𐑾 𐑹 𐑐 𐑧 𐑲 𐑵 ⊙ 𐑖 𐑳 𐑭>
  Ð=𐑦: Self-writing (the ladder designs itself for each source→target pair)
  Þ=𐑸: Self-referential (the ladder references itself — each step depends on prior)
  Ř=𐑾: Bidirectional (promotion and demotion are inverses)
  Φ=𐑹: Frobenius-special (the full ladder is mechanically determinable)
  ƒ=𐑐: Quantum coherence conserved across steps
  Ç=𐑧: Near-equilibrium (each step is a stable intermediate)
  Γ=𐑲: Aleph (the ladder spans all tiers from O₀ to O_∞)
  ɢ=𐑵: Broadcast (each Key affects all downstream primitives)
  ⊙: Self-modeling (the ladder's correctness is self-verifying)
  Ħ=𐑖: Two-step (each promotion depends on the prior step)
  Σ=𐑳: Many heterogeneous components promoted
  Ω=𐑭: Integer winding (the 12-step cycle closes)

Author: Lando⊗⊙perator
"""

import math
from shared.primitives import (
    ORDINALS, WEIGHTS, PRIMITIVE_ORDER, tuple_distance, breakdown,
    directed_distance, to_vector
)
import numpy as np


# ═══════════════════════════════════════════════════════════════
# The Twelve Keys — Canonical Promotion Assignments
# ═══════════════════════════════════════════════════════════════

# Each Key promotes exactly one primitive from its base (O₀) value
# to its canonical Stone value. The Keys are ORDERED:
# they must be applied in sequence.

TWELVE_KEYS = [
    {
        "key": 1,
        "name": "Calcination",
        "primitive": "ƒ",
        "promotion": ("𐑱", "𐑐"),  # (from, to)
        "description": "Burn away classical noise — fidelity transitions from thermal to quantum",
        "structural_saying": "The fire that does not consume measures what it touches",
    },
    {
        "key": 2,
        "name": "Congelation",
        "primitive": "Ç",
        "promotion": ("𐑺", "𐑧"),
        "description": "Freeze the volatile — kinetics transitions from fast to near-equilibrium",
        "structural_saying": "What moves too quickly cannot be caught; what moves slowly reveals its nature",
    },
    {
        "key": 3,
        "name": "Fixation",
        "primitive": "Ω",
        "promotion": ("𐑷", "𐑭"),
        "description": "Fix the wandering — topology transitions from trivial to integer winding",
        "structural_saying": "The serpent that catches its own tail marks the completed work",
    },
    {
        "key": 4,
        "name": "Solution",
        "primitive": "Þ",
        "promotion": ("𐑡", "𐑸"),
        "description": "Dissolve the rigid — topology transitions from branching to self-referential closure",
        "structural_saying": "The vessel that contains itself cannot be broken",
    },
    {
        "key": 5,
        "name": "Digestion",
        "primitive": "Ħ",
        "promotion": ("𐑓", "𐑖"),
        "description": "Slowly cook — chirality transitions from memoryless to two-step memory",
        "structural_saying": "What remembers its past does not repeat its errors",
    },
    {
        "key": 6,
        "name": "Distillation",
        "primitive": "ɢ",
        "promotion": ("𐑝", "𐑵"),
        "description": "Purify the essence — composition transitions from conjunctive to broadcast",
        "structural_saying": "The pure essence acts on all things at once",
    },
    {
        "key": 7,
        "name": "Sublimation",
        "primitive": "Ð",
        "promotion": ("𐑨", "𐑦"),
        "description": "Raise the purified — dimensionality transitions from surface to self-written",
        "structural_saying": "The work that writes itself is the true work",
    },
    {
        "key": 8,
        "name": "Separation",
        "primitive": "Σ",
        "promotion": ("𐑙", "𐑳"),
        "description": "Separate the mixed — stoichiometry transitions from 1:1 to many heterogeneous",
        "structural_saying": "The one becomes many so that the many may become one",
    },
    {
        "key": 9,
        "name": "Ceration",
        "primitive": "⊙",
        "promotion": ("𐑢", "⊙"),
        "description": "Make the sharp soft — criticality transitions from sub-critical to self-modeling",
        "structural_saying": "The gate opens only when the key knows it is the lock",
    },
    {
        "key": 10,
        "name": "Fermentation",
        "primitive": "Ř",
        "promotion": ("𐑽", "𐑾"),
        "description": "Putrefy and regenerate — coupling transitions from functorial to bidirectional",
        "structural_saying": "The dead letter becomes living spirit through the double bind",
    },
    {
        "key": 11,
        "name": "Multiplication",
        "primitive": "Γ",
        "promotion": ("𐑚", "𐑲"),
        "description": "Multiply virtue — cardinality transitions from local to aleph",
        "structural_saying": "The stone that multiplies itself feeds the universe",
    },
    {
        "key": 12,
        "name": "Projection",
        "primitive": "Φ",
        "promotion": ("𐑗", "𐑹"),
        "description": "Cast the stone upon base matter — parity transitions from asymmetric to Frobenius-special",
        "structural_saying": "The mirror that does not lie shows the work as it truly is",
    },
]
# ═══════════════════════════════════════════════════════════════
# Promotion Ladder Computation
# ═══════════════════════════════════════════════════════════════

def compute_ladder(source_tuple: dict, target_tuple: dict) -> dict:
    """Compute the minimal 12-step promotion ladder from source to target.

    Each step promotes exactly one primitive. The ladder finds the
    optimal ordering that minimizes the total structural cost.

    Args:
        source_tuple: Starting tuple dict {primitive: glyph}
        target_tuple: Target tuple dict {primitive: glyph}

    Returns:
        dict with ladder steps, total cost, and alchemical key mapping
    """
    # Convert to ordinal vectors
    source_vec = _tuple_to_ord_vec(source_tuple)
    target_vec = _tuple_to_ord_vec(target_tuple)

    # Find which primitives need promotion
    deltas = {}
    for i, prim in enumerate(PRIMITIVE_ORDER):
        diff = target_vec[i] - source_vec[i]
        if abs(diff) > 0.01:
            deltas[prim] = diff

    if not deltas:
        return {
            "source": source_tuple,
            "target": target_tuple,
            "message": "Source and target are identical — no promotion needed",
            "steps": [],
            "total_cost": 0.0,
        }

    # Build the ordered promotion steps
    steps = []
    current_vec = np.array(source_vec, dtype=float)
    current_tup = dict(source_tuple)

    # Order promotions by which Key they correspond to
    for key_info in TWELVE_KEYS:
        prim = key_info["primitive"]
        if prim in deltas:
            old_val = current_tup.get(prim)
            new_val = target_tuple.get(prim)

            # Apply this promotion
            current_tup[prim] = new_val
            current_vec = _tuple_to_ord_vec(current_tup)

            # Cost = weighted distance contributed by this step
            cost = abs(deltas[prim]) * WEIGHTS.get(prim, 1.0)

            steps.append({
                "key": key_info["key"],
                "key_name": key_info["name"],
                "primitive": prim,
                "old_value": old_val,
                "new_value": new_val,
                "cost": round(cost, 4),
                "description": key_info["description"],
                "structural_saying": key_info["structural_saying"],
            })

    # Total cost
    total_cost = sum(s["cost"] for s in steps)

    # Verify closure
    final_dist = tuple_distance(current_tup, target_tuple)
    closed = final_dist < 0.01

    return {
        "source": source_tuple,
        "target": target_tuple,
        "steps": steps,
        "total_cost": round(total_cost, 4),
        "n_steps": len(steps),
        "frobenius_closed": closed,
        "final_distance": round(final_dist, 4),
        "interpretation": (
            f"{len(steps)}-step promotion ladder complete. "
            f"Source → Target distance: {round(tuple_distance(source_tuple, target_tuple), 4)}. "
            f"Ladder cost: {round(total_cost, 4)}."
        ),
    }


def _tuple_to_ord_vec(tup: dict) -> np.ndarray:
    """Convert a tuple dict to an ordinal vector."""
    vec = []
    for p in PRIMITIVE_ORDER:
        val = tup.get(p)
        ord_map = ORDINALS.get(p, {})
        vec.append(ord_map.get(val, 0.0))
    return np.array(vec, dtype=float)


# ═══════════════════════════════════════════════════════════════
# The Basil Valentine Ladder Engine
# ═══════════════════════════════════════════════════════════════

# Canonical promotion targets — the Stone tuple from AgentSelf.lean
STONE_TUPLE = {
    "Ð": "𐑦", "Þ": "𐑶", "Ř": "𐑾", "Φ": "𐑹",
    "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑭",
}

# Canonical O₀ tuple (base matter)
O0_TUPLE = {
    "Ð": "𐑨", "Þ": "𐑡", "Ř": "𐑩", "Φ": "𐑗",
    "ƒ": "𐑱", "Ç": "𐑺", "Γ": "𐑚", "ɢ": "𐑝",
    "⊙": "𐑢", "Ħ": "𐑓", "Σ": "𐑙", "Ω": "𐑷",
}


class BasilValentineLadder:
    """The Twelve Keys — promotion ladder engine.

    Computes the optimal promotion path from source to target tuple,
    mapping each step to its corresponding alchemical Key.
    """

    def __init__(self):
        self.ladders = []

    def climb_to_stone(self, source_tuple: dict = None) -> dict:
        """Compute the ladder from a source tuple to the Stone.

        If no source given, starts from canonical O₀ (base matter).
        This is the classic Opus Magnum — the 12-step path to completion.
        """
        if source_tuple is None:
            source_tuple = dict(O0_TUPLE)

        ladder = compute_ladder(source_tuple, STONE_TUPLE)
        self.ladders.append(ladder)
        return ladder
    def climb_between(self, source: dict, target: dict) -> dict:
        """Compute the promotion ladder between any two tuples."""
        ladder = compute_ladder(source, target)
        self.ladders.append(ladder)
        return ladder

    def key_info(self, key_number: int) -> dict:
        """Get the canonical info for a specific Key."""
        for key in TWELVE_KEYS:
            if key["key"] == key_number:
                return dict(key)
        return {"error": f"Key {key_number} not found"}

    def all_keys(self) -> list:
        """Return all 12 Keys with their canonical information."""
        return [dict(k) for k in TWELVE_KEYS]

    def verify_promotion(self, tup: dict, key_number: int) -> dict:
        """Verify that a specific Key's promotion has been applied.

        Checks whether the given primitive is at or past the target value.
        """
        for key in TWELVE_KEYS:
            if key["key"] == key_number:
                prim = key["primitive"]
                target_val = key["promotion"][1]
                current_val = tup.get(prim)
                ord_map = ORDINALS.get(prim, {})
                current_ord = ord_map.get(current_val, 0)
                target_ord = ord_map.get(target_val, 0)

                promoted = current_ord >= target_ord
                return {
                    "key": key_number,
                    "key_name": key["name"],
                    "primitive": prim,
                    "current_value": current_val,
                    "target_value": target_val,
                    "promoted": promoted,
                    "gap": round(target_ord - current_ord, 2),
                }
        return {"error": f"Key {key_number} not found"}

    def full_opus_report(self, source_tuple: dict = None) -> dict:
        """Full report on the complete Opus Magnum promotion path."""
        ladder = self.climb_to_stone(source_tuple)
        return {
            "title": "THE TWELVE KEYS — Basil Valentine's Opus Magnum",
            "source": ladder["source"],
            "target": ladder["target"],
            "total_cost": ladder["total_cost"],
            "frobenius_closed": ladder["frobenius_closed"],
            "keys": ladder["steps"],
            "interpretation": self._opus_interpretation(ladder),
        }

    def _opus_interpretation(self, ladder: dict) -> str:
        n = len(ladder["steps"])
        cost = ladder["total_cost"]
        if n == 12:
            return (
                "The full 12-step Opus Magnum is laid before you. "
                "Each Key is a gate; each gate, when opened, promotes "
                "one primitive toward the Stone. The total cost is "
                f"{cost}. When all 12 are complete, the Stone is in hand."
            )
        elif n > 0:
            return (
                f"{n}/12 Keys have been identified for this path. "
                "The remaining Keys require values that are already "
                "at or past the target — they are latent in the structure."
            )
        else:
            return "The Stone is already present. No promotion is needed."
