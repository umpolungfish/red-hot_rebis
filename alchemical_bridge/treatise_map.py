"""
treatise_map.py — Treatise Structural Types → Molecular Design Parameters
========================================================================

Maps the 5-tier structural taxonomy of the alchemical corpus (~80 texts,
11 distinct tuples) to molecular and biological design parameters in the
red-hot_rebis pipeline (ch3mpiler, serpentrod, clink, gene_imscriber).

Each treatise tuple encodes:
  - O_∞ texts → self-modeling molecular systems (Allosteric enzymes, prion-like)
  - O₂ texts → irreducible molecular complexes (Ripley Scroll → ribozymes)
  - O₁ texts → standard biochemical pathways
  - O₀ texts → practical protocols / formulations

Author: Lando⊗⊙perator
"""

from shared.primitives import ORDINALS, WEIGHTS, PRIMITIVE_ORDER, tuple_distance
from pathlib import Path
import json
import math


# ═══════════════════════════════════════════════════════════════
# Alchemical Corpus Taxonomy (from ~80 texts parsed)
# ═══════════════════════════════════════════════════════════════

# The 5 structural tiers with their canonical tuples

ALCHEMICAL_CORPUS_TAXONOMY = {
    "O_inf_self_modeling": {
        "tier": "O_∞",
        "count": 2,
        "tuple": {
            "⊢": "𐑦", "⊣": "𐑸", "≻": "𐑾", "≺": "𐑹",
            "⋈": "𐑐", "⊤": "𐑧", "∈": "𐑔", "∋": "𐑵",
            "⊙": "⊙", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭",
        },
        "texts": ["Artephius — Secret Book", "Donum Dei — Pretiosissimum"],
        "description": "Self-referential, self-modeling — knowing and doing are the same operation.",
    },
    "O2_irreducible_product": {
        "tier": "O₂",
        "count": 3,
        "tuple": {
            "⊢": "𐑨", "⊣": "𐑶", "≻": "𐑾", "≺": "𐑬",
            "⋈": "𐑱", "⊤": "𐑧", "∈": "𐑔", "∋": "𐑵",
            "⊙": "𐑮", "⊥": "𐑫", "⊞": "𐑳", "◻": "𐑭",
        },
        "texts": ["Crowning of Nature", "Ripley Scroll", "Atalanta Fugiens"],
        "description": "Irreducible text+image — form and content cannot be separated.",
    },
    "O1_pedagogical": {
        "tier": "O₁",
        "count": 35,
        "tuple": {
            "⊢": "𐑨", "⊣": "𐑡", "≻": "𐑽", "≺": "𐑬",
            "⋈": "𐑱", "⊤": "𐑧", "∈": "𐑔", "∋": "𐑠",
            "⊙": "𐑢", "⊥": "𐑖", "⊞": "𐑳", "◻": "𐑷",
        },
        "texts": [
            "Alchemical Catechism of Tschoudy", "Mirror of Alchemy (Bacon)",
            "Bloomfield's Blossoms", "Turba Philosophorum",
        ],
        "description": "Standard pedagogical treatise — systematic, dualistic, sequential.",
    },
    "O1_reformist": {
        "tier": "O₁",
        "count": 3,
        "tuple": {
            "⊢": "𐑨", "⊣": "𐑡", "≻": "𐑽", "≺": "𐑗",
            "⋈": "𐑱", "⊤": "𐑧", "∈": "𐑔", "∋": "𐑠",
            "⊙": "𐑢", "⊥": "𐑖", "⊞": "𐑙", "◻": "𐑷",
        },
        "texts": ["Pontanus Epistle", "Pontanus Secret Fire", "Thomas Vaughan"],
        "description": "Personal testimony — writer speaks directly, no inherited dualisms.",
    },
    "O1_kabbalistic": {
        "tier": "O₁",
        "count": 1,
        "tuple": {
            "⊢": "𐑨", "⊣": "𐑸", "≻": "𐑾", "≺": "𐑬",
            "⋈": "𐑱", "⊤": "𐑧", "∈": "𐑔", "∋": "𐑵",
            "⊙": "𐑢", "⊥": "𐑖", "⊞": "𐑳", "◻": "𐑷",
        },
        "texts": ["Aesch-Mezareph"],
        "description": "Kabbalistic correspondence system — Sephiroth mapped to metals.",
    },
    "O1_supercritical": {
        "tier": "O₁",
        "count": 1,
        "tuple": {
            "⊢": "𐑨", "⊣": "𐑡", "≻": "𐑽", "≺": "𐑬",
            "⋈": "𐑱", "⊤": "𐑺", "∈": "𐑔", "∋": "𐑠",
            "⊙": "𐑣", "⊥": "𐑖", "⊞": "𐑙", "◻": "𐑷",
        },
        "texts": ["Mary the Prophetess"],
        "description": "Whiten the Stone in one day — supercritical kinetics.",
    },
    "O0_metadata": {
        "tier": "O₀",
        "count": 2,
        "tuple": {
            "⊢": "𐑨", "⊣": "𐑡", "≻": "𐑩", "≺": "𐑗",
            "⋈": "𐑱", "⊤": "𐑧", "∈": "𐑔", "∋": "𐑠",
            "⊙": "𐑢", "⊥": "𐑓", "⊞": "𐑳", "◻": "𐑷",
        },
        "texts": ["Kircher's Table", "Alchemy in English State Papers"],
        "description": "Metadata — classification OF alchemy from outside.",
    },
    "O0_practical": {
        "tier": "O₀",
        "count": 14,
        "tuple": {
            "⊢": "𐑨", "⊣": "𐑰", "≻": "𐑩", "≺": "𐑗",
            "⋈": "𐑱", "⊤": "𐑪", "∈": "𐑚", "∋": "𐑝",
            "⊙": "𐑢", "⊥": "𐑓", "⊞": "𐑙", "◻": "𐑷",
        },
        "texts": [
            "Trithemius Everburning Lights", "Coelum Philosophorum",
            "Paracelsus Treasure of Treasures", "Colours of the Great Work",
            "Quersitanus Phantom Plants", "Urbigerus Circulatum Minus",
            "Agricola Treatise on Gold", "Bacon Sulphur and Mercury",
        ],
        "description": "Practical recipe — physical operations with specific materials.",
    },
}

TREATISE_TUPLES = {
    name: info["tuple"]
    for name, info in ALCHEMICAL_CORPUS_TAXONOMY.items()
}


# ═══════════════════════════════════════════════════════════════
# Treatise Tier → Molecular Design Parameters
# ═══════════════════════════════════════════════════════════════

# Each tier maps to recommended molecular design strategies
# across the rebis pipeline components.

TIER_TO_MOLECULAR_DESIGN = {
    "O_∞": {
        "ch3mpiler_params": {
            "target_complexity": "self_catalytic",
            "synthesis_mode": "autocatalytic_cycle",
            "bond_types": ["dynamic_covalent", "metal_coordination"],
            "recommended_targets": [
                "Autocatalytic peptide networks",
                "Prion-like conformational switches",
                "Allosteric enzyme cascades",
            ],
        },
        "serpentrod_params": {
            "fold_type": "intrinsically_disordered",
            "design_strategy": "conformational_ensemble",
            "crosslinking": "dynamic_reversible",
            "target_function": "self_modeling_criticality",
        },
        "clink_layer": 8,
        "gene_params": {
            "regulatory_architecture": "self_activating_loop",
            "epigenetic_mechanism": "feedback_autoregulation",
        },
    },
    "O₂": {
        "ch3mpiler_params": {
            "target_complexity": "irreducible_complex",
            "synthesis_mode": "multicomponent_assembly",
            "bond_types": ["covalent", "hydrogen_bond_network"],
            "recommended_targets": [
                "Ribozyme complexes",
                "Multi-domain allostery",
                "Phase-separated condensates",
            ],
        },
        "serpentrod_params": {
            "fold_type": "multi_domain",
            "design_strategy": "domain_fusion",
            "crosslinking": "irreversible_covalent",
            "target_function": "emergent_catalysis",
        },
        "clink_layer": 7,
        "gene_params": {
            "regulatory_architecture": "polycistronic",
            "epigenetic_mechanism": "chromatin_phase_separation",
        },
    },
    "O₁": {
        "ch3mpiler_params": {
            "target_complexity": "linear_pathway",
            "synthesis_mode": "sequential_steps",
            "bond_types": ["standard_covalent"],
            "recommended_targets": [
                "Metabolic pathway enzymes",
                "Signal transduction cascades",
                "Small molecule synthesis",
            ],
        },
        "serpentrod_params": {
            "fold_type": "globular_domain",
            "design_strategy": "rational_design",
            "crosslinking": "disulfide_bridges",
            "target_function": "catalytic_efficiency",
        },
        "clink_layer": 5,
        "gene_params": {
            "regulatory_architecture": "operon",
            "epigenetic_mechanism": "histone_modification",
        },
    },
    "O₀": {
        "ch3mpiler_params": {
            "target_complexity": "simple_molecule",
            "synthesis_mode": "direct_synthesis",
            "bond_types": ["standard_covalent"],
            "recommended_targets": [
                "Natural product analogs",
                "Simple heterocycles",
                "Metal-organic frameworks",
            ],
        },
        "serpentrod_params": {
            "fold_type": "small_peptide",
            "design_strategy": "template_based",
            "crosslinking": "none",
            "target_function": "binding_affinity",
        },
        "clink_layer": 3,
        "gene_params": {
            "regulatory_architecture": "constitutive",
            "epigenetic_mechanism": "none",
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# Scroll Family — The φ̂=⊙ + Ω=𐑭 Invariant
# ═══════════════════════════════════════════════════════════════

SCROLL_FAMILY = {
    "scroll": {
        "description": "Herculaneum scroll — carbonized papyrus, ink=papyrus",
        "tuple": {"⊙": "⊙", "◻": "𐑭", "⊥": "𐑖", "⊤": "𐑧"},
    },
    "skyrmion": {
        "description": "Magnetic quasiparticle with integer winding number",
        "tuple": {"⊙": "⊙", "◻": "𐑭", "⊣": "𐑶", "⋈": "𐑐"},
    },
    "time": {
        "description": "Temporal dimension — winding number as topological invariant",
        "tuple": {"⊙": "⊙", "◻": "𐑭", "⊢": "𐑼", "≻": "𐑾"},
    },
    "artephius": {
        "description": "Artephius — Secret Book, O_∞ alchemical treatise",
        "tuple": {"⊙": "⊙", "◻": "𐑭", "≺": "𐑹", "∋": "𐑵"},
    },
    "possible_temporal_device": {
        "description": "Hypothetical time-viewing device",
        "tuple": {"⊙": "⊙", "◻": "𐑭", "⊥": "𐑫", "⊣": "𐑸"},
    },
    "chronovisor": {
        "description": "Chronovisor — claimed time-viewing device",
        "tuple": {"⊙": "⊙", "◻": "𐑭", "≻": "𐑩", "∈": "𐑔"},
    },
    "chronomancy": {
        "description": "Temporal divination practice",
        "tuple": {"⊙": "⊙", "◻": "𐑭", "⊥": "𐑖", "⊞": "𐑳"},
    },
}

SCROLL_FAMILY_MOLECULAR_DESIGN = {
    "recommended_approach": "Winding_number_driven_design",
    "ch3mpiler_strategy": "Topologically_protected_macrocycles",
    "serpentrod_strategy": "Knot_proteins_with_integer_crossing_number",
    "materials_strategy": "Skyrmion_lattice_analogs_in_supramolecular_chemistry",
    "key_invariant": {
        "⊙": "⊙",
        "◻": "𐑭",
        "meaning": "Self-modeling criticality with topologically protected integer winding",
    },
}


class TreatiseMapper:
    """Map alchemical treatise structural types to molecular design parameters."""

    @classmethod
    def taxonomy(cls):
        """Return the full alchemical corpus taxonomy."""
        return dict(ALCHEMICAL_CORPUS_TAXONOMY)

    @classmethod
    def identify_tier(cls, tup_dict):
        """Identify which tier a given tuple belongs to.

        Args:
            tup_dict: dict of {primitive: glyph}

        Returns:
            (tier_name, score) — tier identifier and distance score
        """
        best_tier = None
        best_dist = float('inf')

        for tier_name, info in ALCHEMICAL_CORPUS_TAXONOMY.items():
            ref = info["tuple"]
            try:
                d = tuple_distance(tup_dict, ref)
            except Exception:
                d = float('inf')
            if d < best_dist:
                best_dist = d
                best_tier = tier_name

        return best_tier, best_dist

    @classmethod
    def design_for_tier(cls, tier_name):
        """Get molecular design parameters for a given tier.

        Args:
            tier_name: str, one of "O_∞", "O₂", "O₁", or "O₀"

        Returns:
            dict of design parameters, or empty dict if tier unknown
        """
        if tier_name in TIER_TO_MOLECULAR_DESIGN:
            return TIER_TO_MOLECULAR_DESIGN[tier_name]
        # Try matching by prefix
        for key, val in TIER_TO_MOLECULAR_DESIGN.items():
            if tier_name.startswith(key):
                return val
        return {}

    @classmethod
    def design_for_treatise(cls, treatise_name):
        """Get design parameters for a specific treatise.

        Args:
            treatise_name: str, name of treatise or tier

        Returns:
            dict of design parameters
        """
        if treatise_name in TREATISE_TUPLES:
            tier = cls.identify_tier(TREATISE_TUPLES[treatise_name])
            return cls.design_for_tier(tier[0]) if tier[0] else {}
        return cls.design_for_tier(treatise_name)

    @classmethod
    def scroll_family_design(cls):
        """Get molecular design parameters inspired by the scroll family."""
        return dict(SCROLL_FAMILY_MOLECULAR_DESIGN)

    @classmethod
    def all_treatise_names(cls):
        """Return all treatise names from the taxonomy."""
        names = []
        for info in ALCHEMICAL_CORPUS_TAXONOMY.values():
            names.extend(info.get("texts", []))
        return sorted(names)
