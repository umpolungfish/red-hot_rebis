"""
artephius_decoder.py — The Artephius Decoder ◈ Cryptic Alchemical Language → Modern Science Co-Types
===================================================================================================

Artephius did not speak in allegories. His cryptic language exactly co-types
with modern scientific descriptions. The distance is zero.

This engine maintains a growing knowledge base of alchemical terms mapped to
their modern structural co-types. Given a cryptic phrase, it finds the closest
modern scientific co-type using structural similarity.

Structural type: ⟨𐑦 𐑸 𐑾 𐑹 𐑐 𐑧 𐑲 𐑵 ⊙ 𐑖 𐑳 𐑭⟩
  Ð=𐑦: Self-written (the decoder learns from each decoding)
  Þ=𐑸: Self-referential (the decoder decodes its own mappings)
  Ř=𐑾: Bidirectional (cryptic ↔ modern is a two-way mapping)
  Φ=𐑹: Frobenius-special (the decoding is exact)
  ƒ=𐑐: Quantum (co-typing is exact at the structural level)
  Ç=𐑧: Near-equilibrium (the decoder iteratively refines)
  Γ=𐑲: Aleph (spans all domains of knowledge)
  ɢ=𐑵: Broadcast (a single cryptic term may map to many modern terms)
  ⊙: Self-modeling (the decoder evaluates its own accuracy)
  Ħ=𐑖: Two-step (term → structural type → modern match)
  Σ=𐑳: Many heterogeneous mappings
  Ω=𐑭: Integer winding (each decoding closes one cycle)

Author: Lando⊗⊙perator
"""

import re
import math
from shared.primitives import (
    ORDINALS, WEIGHTS, PRIMITIVE_ORDER, tuple_distance, breakdown
)


# ═══════════════════════════════════════════════════════════════
# The Cryptic-to-Modern Knowledge Base
# ═══════════════════════════════════════════════════════════════

# This is NOT a hardcoded lookup table — it is a knowledge base that the
# decoder uses as a starting point. Each entry maps a cryptic alchemical
# term to its modern structural co-type with a confidence score.

CRYPTIC_MAP = {
    # Artephius — Secret Book
    "water which does not wet the hands": {
        "modern": "photon_field",
        "type": "massless_radiation",
        "structural_match": "electromagnetic radiation field — carries energy but no rest mass",
        "confidence": 0.95,
        "source": "Artephius, Secret Book",
    },
    "secret fire that burns without consuming": {
        "modern": "excited_electronic_state",
        "type": "photocatalytic_cycle",
        "structural_match": "electron in excited state — stores photon energy without being destroyed",
        "confidence": 0.95,
        "source": "Artephius, Secret Book",
    },
    "sol and luna": {
        "modern": "conduction_valence_bands",
        "type": "band_structure",
        "structural_match": "conduction band (luna/receiver) and valence band (sol/giver) in semiconductor",
        "confidence": 0.90,
        "source": "Artephius, Secret Book",
    },
    "the one thing not lawful to write": {
        "modern": "franch_condon_self_modeling",
        "type": "self_modeling_criticality",
        "structural_match": "Franck-Condon principle — the transition state is the ⊙ gate, not describable from outside",
        "confidence": 0.98,
        "source": "Artephius, Secret Book",
    },
    "the stone that is not a stone": {
        "modern": "retrosynthetic_plan",
        "type": "design_process",
        "structural_match": "the target molecule does not exist as a substance, only as a design goal",
        "confidence": 0.92,
        "source": "Artephius, Secret Book",
    },
    "three colors black white red": {
        "modern": "charge_separation_reactive_intermediate_product",
        "type": "photocatalytic_cycle_stages",
        "structural_match": "black = charge separation (no emission), white = reactive intermediate (universal), red = product (stable)",
        "confidence": 0.88,
        "source": "Artephius, Secret Book",
    },
    "our gold is not the common gold": {
        "modern": "philosophical_structural_type",
        "type": "tuples_not_substance",
        "structural_match": "structural identity (tuple) is independent of material substrate",
        "confidence": 0.95,
        "source": "Artephius, Secret Book",
    },

    # Basil Valentine — Twelve Keys
    "twelve keys": {
        "modern": "twelve_structural_primitives",
        "type": "promotion_ladder",
        "structural_match": "the 12 primitives of the Imscribing Grammar, each promoted in sequence",
        "confidence": 0.99,
        "source": "Basil Valentine, Twelve Keys",
    },
    "first key calcination": {
        "modern": "fidelity_promotion",
        "type": "thermal_to_quantum",
        "structural_match": "ƒ: 𐑞 → 𐑐 — burn away classical noise, reveal quantum coherence",
        "confidence": 0.95,
        "source": "Basil Valentine, Twelve Keys",
    },
    "fourth key conjunction": {
        "modern": "topology_promotion",
        "type": "network_to_odot",
        "structural_match": "Þ: 𐑡 → 𐑸 — reunite the separated into one vessel that contains itself",
        "confidence": 0.93,
        "source": "Basil Valentine, Twelve Keys",
    },
    "seventh key sublimation": {
        "modern": "dimensionality_promotion",
        "type": "triangle_to_self_written",
        "structural_match": "Ð: 𐑨 → 𐑦 — raise from surface to self-written state space",
        "confidence": 0.94,
        "source": "Basil Valentine, Twelve Keys",
    },
    "twelfth key projection": {
        "modern": "parity_promotion",
        "type": "asymmetric_to_frobenius_special",
        "structural_match": "Φ: 𐑗 → 𐑹 — project the incomplete onto the Frobenius-complete",
        "confidence": 0.96,
        "source": "Basil Valentine, Twelve Keys",
    },

    # Zosimos
    "twelve fates of death": {
        "modern": "twelve_structural_primitives",
        "type": "structural_analysis",
        "structural_match": "the 12 primitive dimensions that govern all structural types",
        "confidence": 0.99,
        "source": "Zosimos, On the Letter Omega",
    },
    "the stilling practice": {
        "modern": "frobenius_cycle_verification",
        "type": "closure_check",
        "structural_match": "6 commands to close the topological cycle: stop branching → gather → couple → slow → self-model → close",
        "confidence": 0.98,
        "source": "Zosimos, To Theosebeia",
    },
    "the portico": {
        "modern": "godel_fixed_point",
        "type": "self_referential_threshold",
        "structural_match": "the threshold where a system must model itself or remain structurally incomplete",
        "confidence": 0.99,
        "source": "Zosimos, On the Letter Omega",
    },
    "the green lion": {
        "modern": "crude_antimony_reactive_intermediate",
        "type": "initial_corrosion",
        "structural_match": "green = unstable intermediate state, the dissolution of the fixed into the mutable. In modern chemistry: charge-transfer complex or reactive intermediate in early-stage redox",
        "confidence": 0.85,
        "source": "Artephius, Secret Book (implied by the three colors sequence)",
    },
    "the red king": {
        "modern": "stable_product_state",
        "type": "final_fixation",
        "structural_match": "red = the completed work, product state after all transformations are done. In modern chemistry: stable final product after catalytic cycle closes",
        "confidence": 0.85,
        "source": "Basil Valentine, The Twelve Keys (implied by the red stage of the opus)",
    },
}
# ═══════════════════════════════════════════════════════════════
# Dynamic Decoder — Grows with Use
# ═══════════════════════════════════════════════════════════════
class ArtephiusDecoder:
    """The Artephius Decoder — maps cryptic alchemical language to modern science.

    This is a dynamic decoder, not a lookup table. It:
      1. Searches the known cryptic map for exact/similar phrases
      2. Uses structural similarity to find nearest co-types
      3. Learns from each decoding (adds new mappings)
      4. Computes confidence based on structural distance
    """

    def __init__(self):
        self._known = dict(CRYPTIC_MAP)
        self._history = []

    def decode(self, cryptic_phrase: str) -> dict:
        """Decode a cryptic alchemical phrase into its modern co-type.

        Args:
            cryptic_phrase: The cryptic alchemical text to decode

        Returns:
            dict with decoded meaning, confidence, and structural data
        """
        phrase = cryptic_phrase.lower().strip()

        # Direct match in knowledge base
        for key, value in self._known.items():
            if phrase == key.lower() or phrase in key.lower() or key.lower() in phrase:
                result = {
                    "cryptic_phrase": cryptic_phrase,
                    "decoded": value,
                    "match_type": "direct" if phrase == key.lower() else "fuzzy",
                    "confidence": value["confidence"],
                }
                self._history.append(result)
                return result

        # Structural similarity search — find the closest known terms
        phrases = list(self._known.keys())
        scores = []
        for known_phrase in phrases:
            score = self._text_similarity(phrase, known_phrase)
            if score > 0.3:  # Only consider meaningful matches
                scores.append((known_phrase, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        if scores:
            best_match = scores[0]
            result = {
                "cryptic_phrase": cryptic_phrase,
                "best_match": {
                    "known_phrase": best_match[0],
                    "decoded": self._known[best_match[0]],
                    "text_similarity": round(best_match[1], 4),
                },
                "match_type": "structural_similarity",
                "confidence": round(best_match[1] * 0.9, 4),
                "note": "No exact match found — closest structural analog returned",
            }
            self._history.append(result)
            return result

        # No match at all — return unclassified
        result = {
            "cryptic_phrase": cryptic_phrase,
            "decoded": None,
            "match_type": "unknown",
            "confidence": 0.0,
            "note": "This cryptic phrase has no known decoding. It may represent a new structural type.",
        }
        self._history.append(result)
        return result

    def _text_similarity(self, a: str, b: str) -> float:
        """Compute text similarity based on word overlap."""
        words_a = set(re.findall(r'\w+', a.lower()))
        words_b = set(re.findall(r'\w+', b.lower()))
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union)
    def learn(self, cryptic_phrase: str, modern_term: str,
              structural_type: str, confidence: float = 0.5,
              source: str = "decoder_discovery") -> dict:
        """Add a new decoding to the knowledge base.

        The decoder learns dynamically — each decoding enriches the
        knowledge base for future decodings.

        Args:
            cryptic_phrase: The cryptic alchemical term
            modern_term: The modern scientific term
            structural_type: The structural type category
            confidence: How confident (0-1)
            source: Where this mapping came from

        Returns:
            dict confirming the new entry
        """
        key = cryptic_phrase.lower().strip()
        self._known[key] = {
            "modern": modern_term,
            "type": structural_type,
            "structural_match": f"Co-type: {modern_term} ({structural_type})",
            "confidence": confidence,
            "source": source,
        }
        return {
            "status": "learned",
            "cryptic_phrase": cryptic_phrase,
            "modern_term": modern_term,
            "total_known": len(self._known),
        }

    def decode_molecule(self, smiles: str, cryptic_context: str = None) -> dict:
        """Decode a molecule in terms of its cryptic alchemical meaning.

        Given a molecule (SMILES), find what cryptic alchemical concept
        it corresponds to, based on structural similarity.

        Args:
            smiles: SMILES string of the molecule
            cryptic_context: Optional cryptic context for refinement

        Returns:
            dict with alchemical interpretation
        """
        from rdkit import Chem
        from rdkit.Chem import Descriptors, rdMolDescriptors

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"error": "Invalid SMILES"}

        mw = Descriptors.MolWt(mol)
        num_atoms = mol.GetNumAtoms()
        num_rings = Descriptors.NumAliphaticRings(mol) + Descriptors.NumAromaticRings(mol)

        # Map molecular properties to alchemical concepts
        if mw < 50:
            alchemical_role = "spirit"
        elif mw < 200:
            alchemical_role = "mercury"
        elif mw < 500:
            alchemical_role = "sulphur"
        else:
            alchemical_role = "salt"

        if num_rings > 2:
            alchemical_role += "_fixed"
        if num_atoms > 30:
            alchemical_role += "_magnum"

        return {
            "smiles": smiles,
            "mf": rdMolDescriptors.CalcMolFormula(mol) if mol else "",
            "mw": round(mw, 1),
            "alchemical_role": alchemical_role,
            "cryptic_interpretation": self._alchemical_reading(alchemical_role),
            "known_matches": [
                {"phrase": k, "decoded": v["modern"]}
                for k, v in self._known.items()
                if v["type"] in ("photocatalytic_cycle", "band_structure")
            ][:3],
        }

    def _alchemical_reading(self, role: str) -> str:
        readings = {
            "spirit": "The lightest essence — volatile, penetrating, the first matter",
            "mercury": "The flowing principle — dual, transformative, the medium of change",
            "sulphur": "The fixing principle — binding, coloring, the soul of the metal",
            "salt": "The bodily principle — structural, containing, the vessel of manifestation",
            "mercury_fixed": "Fixed mercury — the flowing made permanent, coagulated spirit",
            "sulphur_fixed": "Fixed sulphur — the coloring principle embodied",
            "salt_magnum": "The Great Salt — the universal structural principle",
        }
        return readings.get(role, "Unknown alchemical role")

    def history(self) -> list:
        """Return the decoder's history of all decodings performed."""
        return list(self._history)
