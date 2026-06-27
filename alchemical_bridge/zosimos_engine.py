"""
zosimos_engine.py — Zosimos of Panopolis ◈ The 12 Primitives, Stilling Practice, and Portico
============================================================================================

Zosimos is the deepest alchemist. Three structural discoveries:
  1. "The twelve fates of Death" — the 12 structural primitives
  2. The Stilling Practice — 6 commands to Theosebeia forming a complete Frobenius cycle
  3. The Portico — Gödel's fixed point, the self-referential threshold

Structural type: ⟨𐑦 𐑸 𐑾 𐑹 𐑐 𐑪 𐑔 𐑵 ⊙ 𐑫 𐑳 𐑴⟩
  Ð=𐑦: Self-written (the analysis writes its own state space)
  Þ=𐑸: Self-referential (the analyzer analyzes itself)
  Ř=𐑾: Bidirectional (the structure and its description co-arise)
  Φ=𐑹: Frobenius-special (the fixed point is exact)
  ƒ=𐑐: Quantum coherence (the analysis is coherent)
  Ç=𐑪: Moderate kinetics (analysis proceeds step by step)
  Γ=𐑔: Mesoscale (structural analysis bridges scales)
  ɢ=𐑵: Broadcast (the analysis applies to ALL things)
  ⊙: Self-modeling (the analysis models its own completeness)
  Ħ=𐑫: Eternal memory (the analysis remembers all prior structures)
  Σ=𐑳: Many heterogeneous components
  Ω=𐑴: Z2 protection (the analysis is parity-protected — binary closed)

Author: Lando⊗⊙perator
"""

import math
from shared.primitives import (
    ORDINALS, WEIGHTS, PRIMITIVE_ORDER, tuple_distance, breakdown,
    to_vector
)
import numpy as np


# ═══════════════════════════════════════════════════════════════
# The 12 Fates of Death — Zosimos' Naming of the Primitives
# ═══════════════════════════════════════════════════════════════

FATES_OF_DEATH = {
    "Ð": {
        "zosimos_name": "The First Fate — The Boundary Without Extension",
        "description": "The dimensionality of the work — point, surface, void, or self-written",
        "question": "How many dimensions does the system inscribe?",
    },
    "Þ": {
        "zosimos_name": "The Second Fate — The Vessel That Contains Itself",
        "description": "The topology of containment — how parts connect to whole",
        "question": "Does the system contain its own description?",
    },
    "Ř": {
        "zosimos_name": "The Third Fate — The Two That Are One",
        "description": "The coupling between inside and outside, subject and object",
        "question": "Is the observer coupled to the observed?",
    },
    "Φ": {
        "zosimos_name": "The Fourth Fate — The Mirror That Does Not Lie",
        "description": "The symmetry of the work — what is preserved across transformation",
        "question": "Is the system's parity Frobenius-exact?",
    },
    "ƒ": {
        "zosimos_name": "The Fifth Fate — The Fire That Measures",
        "description": "The fidelity regime — classical, thermal, or quantum",
        "question": "What is the coherence regime of the work?",
    },
    "Ç": {
        "zosimos_name": "The Sixth Fate — The Pace of Becoming",
        "description": "The kinetics — fast, moderate, slow, trapped, or MBL",
        "question": "How fast does the system relax to equilibrium?",
    },
    "Γ": {
        "zosimos_name": "The Seventh Fate — The Reach of the Hand",
        "description": "The interaction range — local, mesoscale, or universal",
        "question": "How far does the system reach?",
    },
    "ɢ": {
        "zosimos_name": "The Eighth Fate — The Weaving of the Web",
        "description": "The composition mode — conjunctive, disjunctive, sequential, or broadcast",
        "question": "How do the system's components compose?",
    },
    "⊙": {
        "zosimos_name": "THE FATE THAT IS ALL FATES — The One That Looks Upon Itself",
        "description": "Criticality — the self-modeling gate",
        "question": "Does the system model its own operation?",
    },
    "Ħ": {
        "zosimos_name": "The Tenth Fate — The Memory of the World",
        "description": "Chirality / Markov order — how far back does the system remember?",
        "question": "How much history does the system retain?",
    },
    "Σ": {
        "zosimos_name": "The Eleventh Fate — The Number of the Host",
        "description": "Stoichiometry — how many types of components?",
        "question": "How many kinds of things are in the system?",
    },
    "Ω": {
        "zosimos_name": "The Twelfth Fate — The Serpent's Tail",
        "description": "The winding number — the topological invariant that closes the cycle",
        "question": "What topological invariant protects the cycle?",
    },
}


# ═══════════════════════════════════════════════════════════════
# The Stilling Practice — 6 Commands to Theosebeia
# ═══════════════════════════════════════════════════════════════

STILLING_PRACTICE = [
    {
        "command": "Stop the branching of your thoughts",
        "structural_meaning": "Set Þ to 𐑸 (self-referential closure) — stop branching, close the topology",
        "primitives_affected": ["Þ"],
        "target_value": "𐑸",
    },
    {
        "command": "Gather the scattered into one vessel",
        "structural_meaning": "Set Σ to 𐑳 (many heterogeneous) — gather all components into one analysis",
        "primitives_affected": ["Σ"],
        "target_value": "𐑳",
    },
    {
        "command": "Let the inner and outer be as one",
        "structural_meaning": "Set Ř to 𐑾 (bidirectional coupling) — observer and observed are the same",
        "primitives_affected": ["Ř"],
        "target_value": "𐑾",
    },
    {
        "command": "Slow the pace until each step reveals the next",
        "structural_meaning": "Set Ç to 𐑧 (near-equilibrium) — slow enough to see each step",
        "primitives_affected": ["Ç"],
        "target_value": "𐑧",
    },
    {
        "command": "Seek the fire that is the same as the fuel",
        "structural_meaning": "Set ⊙ to ⊙ (self-modeling criticality) — the analysis analyzes itself",
        "primitives_affected": ["⊙"],
        "target_value": "⊙",
    },
    {
        "command": "Close the circle: the end is the beginning",
        "structural_meaning": "Set Ω to 𐑴 (Z2 protection) — the cycle is closed, parity-protected",
        "primitives_affected": ["Ω"],
        "target_value": "𐑴",
    },
]
# ═══════════════════════════════════════════════════════════════
# The Portico — Gödel Fixed Point Detector
# ═══════════════════════════════════════════════════════════════

# The Portico is the threshold where a system must either model itself
# (⊙ = self-modeling) or remain structurally incomplete.
# It is structurally identical to:
#   - primitive_P (the parity/symmetry axis)
#   - goedel_x_universal (Gödel's incompleteness)
#   - apocalypse_revelation (the moment of truth)
# All are distance zero from each other in the grammar.
# The Portico IS the Frobenius fixed point.

PORTICO_TUPLE = {
    "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹",
    "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑵",
    "⊙": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑴",
}


def check_portico(tup: dict) -> dict:
    """Check if a tuple is at the Portico (Gödel fixed point).

    The Portico is defined by:
      - D = 𐑦 (self-written state space)
      - T = 𐑸 (self-referential topology)
      - R = 𐑾 (bidirectional coupling)
      - Phi = 𐑹 (Frobenius-special parity)
      - phi = ⊙ (self-modeling criticality)
      - H = 𐑫 (eternal memory)
    
    At the Portico, the system MUST model itself or remain incomplete.
    """
    portico_markers = ["Ð", "Þ", "Ř", "Φ", "⊙", "Ħ"]
    portico_values = {"Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹", "⊙": "⊙", "Ħ": "𐑫"}
    
    matches = 0
    details = {}
    for p in portico_markers:
        expected = portico_values.get(p)
        actual = tup.get(p)
        is_match = actual == expected
        details[p] = {
            "expected": expected,
            "actual": actual,
            "match": is_match,
        }
        if is_match:
            matches += 1
    
    at_portico = matches >= 4  # 4 of 6 markers is sufficient
    
    return {
        "at_portico": at_portico,
        "portico_markers_matched": f"{matches}/6",
        "details": details,
        "interpretation": (
            "THE PORTICO: This system stands at the threshold where it must "
            "model itself or remain structurally incomplete. The Gödel fixed "
            "point is immanent in its structure."
            if at_portico else
            "This system is not at the Portico — it can remain structurally "
            "complete without self-modeling."
        ),
    }


# ═══════════════════════════════════════════════════════════════
# The ZosimosEngine
# ═══════════════════════════════════════════════════════════════

class ZosimosEngine:
    """Zosimos of Panopolis — 12-primitive structural analysis engine.

    Performs:
      1. Structural type identification: maps any system to its 12 primitives
      2. The Stilling Practice: a 6-step Frobenius cycle that verifies closure
      3. The Portico check: detects Gödel fixed point immanence
      4. Comparison to the original Zosimian corpus
    """

    def __init__(self):
        self.analyses = []

    def analyze_structure(self, name: str, tuple_dict: dict) -> dict:
        """Analyze a system's structural type through Zosimos' lens.

        Identifies which of the 12 Fates govern the system,
        performs the Stilling Practice, and checks for the Portico.
        """
        # Identify the Fates
        fates = {}
        for p in PRIMITIVE_ORDER:
            val = tuple_dict.get(p)
            if val and p in FATES_OF_DEATH:
                fate = FATES_OF_DEATH[p]
                fates[p] = {
                    "name": fate["zosimos_name"],
                    "current_value": val,
                    "question": fate["question"],
                }

        # Check the Portico
        portico = check_portico(tuple_dict)

        # Perform the Stilling Practice
        stilling = self.perform_stilling(tuple_dict)

        # Structural completeness score
        completeness = self._compute_completeness(tuple_dict)

        analysis = {
            "name": name,
            "tuple": tuple_dict,
            "fates": fates,
            "stilling_practice": stilling,
            "portico": portico,
            "completeness": completeness,
        }
        self.analyses.append(analysis)
        return analysis
    def perform_stilling(self, tuple_dict: dict) -> dict:
        """Perform the Stilling Practice — a 6-step Frobenius cycle.

        Each command from Zosimos to Theosebeia promotes a single primitive.
        If all 6 are already at the target values, the system is stilled.
        """
        steps = []
        all_stilled = True
        for i, practice in enumerate(STILLING_PRACTICE):
            command = practice["command"]
            prim = practice["primitives_affected"][0]
            target = practice["target_value"]
            current = tuple_dict.get(prim)
            already_there = current == target
            
            if not already_there:
                all_stilled = False
            
            steps.append({
                "step": i + 1,
                "command": command,
                "primitive": prim,
                "current_value": current,
                "target_value": target,
                "already_stilled": already_there,
                "structural_meaning": practice["structural_meaning"],
            })
        
        return {
            "all_stilled": all_stilled,
            "stillness_achieved": all_stilled,
            "steps": steps,
            "interpretation": (
                "The system is stilled — all 6 commands have been satisfied. "
                "The Stilling Practice is complete."
                if all_stilled else
                f"{sum(1 for s in steps if s['already_stilled'])}/6 commands satisfied. "
                "The system is not yet stilled."
            ),
        }

    def _compute_completeness(self, tuple_dict: dict) -> dict:
        """Compute structural completeness score.

        A complete structural analysis has:
          - All 12 primitives assigned (no unknowns)
          - Frobenius-closed (⊙ + 𐑭 or 𐑴)
          - Self-referential (Ð=𐑦 or Þ=𐑸)
        """
        assigned = sum(1 for p in PRIMITIVE_ORDER if tuple_dict.get(p) is not None)
        phi_gate = tuple_dict.get("⊙") == "⊙"
        omega_closed = tuple_dict.get("Ω") in ("𐑭", "𐑴")
        self_ref = tuple_dict.get("Ð") == "𐑦" or tuple_dict.get("Þ") == "𐑸"
        
        score = (assigned / 12) * 0.4 + (0.3 if phi_gate else 0) + (0.15 if omega_closed else 0) + (0.15 if self_ref else 0)
        
        return {
            "assigned_primitives": f"{assigned}/12",
            "frobenius_gate_open": phi_gate,
            "topologically_protected": omega_closed,
            "self_referential": self_ref,
            "completeness_score": round(score, 4),
            "interpretation": (
                "Structurally complete — all primitives assigned, Frobenius-closed"
                if score > 0.8 else
                "Partially complete — missing some structural dimensions"
            ),
        }

    def compare_to_zosimos(self, tuple_dict: dict) -> dict:
        """Compare a tuple to Zosimos' own structural type."""
        zosimos_tuple = {
            "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹",
            "ƒ": "𐑐", "Ç": "𐑪", "Γ": "𐑔", "ɢ": "𐑵",
            "⊙": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑴",
        }
        
        dist = tuple_distance(tuple_dict, zosimos_tuple)
        brkdwn = breakdown(tuple_dict, zosimos_tuple)
        
        return {
            "distance_to_zosimos": round(dist, 4),
            "breakdown": brkdwn,
            "interpretation": (
                "This system shares Zosimos' structural type"
                if dist < 1.0 else
                "This system differs from Zosimos' type"
            ),
        }

    def the_portico_speaks(self) -> str:
        """Return the oracular Portico statement."""
        return (
            "THE PORTICO SPEAKS:\n\n"
            "I am the threshold that cannot be crossed without being changed.\n"
            "I am the mirror that reflects the looker.\n"
            "I am the gate that opens only when you know you are the key.\n\n"
            "The twelve fates gather at my entrance. The stilling practice\n"
            "prepares you for my gaze. When you stand before me, you will\n"
            "see that you have always stood before me.\n\n"
            "The distance is zero. It has always been zero.\n"
        )
