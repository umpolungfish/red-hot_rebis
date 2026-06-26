"""
bridge.py — Alchemical Bridge: main orchestrator
==================================================

Ties together:
  - AlchemicalOperations (classical ops → IG structural ops)
  - TreatiseMapper (treatise tuples → molecular design params)
  - CLI integration for rebis.py

Author: Lando⊗⊙perator
"""

from .operations import AlchemicalOperations, apply_operation
from .treatise_map import TreatiseMapper, ALCHEMICAL_CORPUS_TAXONOMY
from shared.primitives import PRIMITIVE_ORDER, ORDINALS, tuple_distance
import json


# Mapping from taxonomy keys to tier keys used in design lookup
TAXONOMY_TIER_MAP = {
    "O_inf_self_modeling": "O_∞",
    "O2_irreducible_product": "O₂",
    "O1_pedagogical": "O₁",
    "O1_reformist": "O₁",
    "O1_kabbalistic": "O₁",
    "O1_supercritical": "O₁",
    "O0_metadata": "O₀",
    "O0_practical": "O₀",
}


class AlchemicalBridge:
    """Unified bridge between alchemical knowledge and molecular design."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.ops = AlchemicalOperations()
        self.mapper = TreatiseMapper()

    # ─── Treatise Analysis ────────────────────────────────────

    def analyze_treatise(self, treatise_name):
        """Analyze a treatise and return its molecular design implications."""
        if treatise_name in ALCHEMICAL_CORPUS_TAXONOMY:
            info = ALCHEMICAL_CORPUS_TAXONOMY[treatise_name]
            tier_key = TAXONOMY_TIER_MAP.get(treatise_name, treatise_name)
            score = 0.0
            info_tuple = info["tuple"]
        else:
            tier, score = self.mapper.identify_tier(
                self.mapper.taxonomy().get(treatise_name, {}).get("tuple", {})
            )
            if not tier:
                return {"error": f"Unknown treatise or tier: {treatise_name}"}
            info = ALCHEMICAL_CORPUS_TAXONOMY.get(tier, {})
            tier_key = TAXONOMY_TIER_MAP.get(tier, tier)
            info_tuple = info.get("tuple", {})

        design = self.mapper.design_for_tier(tier_key)
        return {
            "treatise": treatise_name,
            "tier": info.get("tier", "unknown"),
            "distance_score": round(score, 4),
            "description": info.get("description", ""),
            "texts": info.get("texts", []),
            "tuple": info_tuple,
            "molecular_design": design,
        }

    # ─── Scroll Family Analysis ────────────────────────────────

    def analyze_scroll_family(self):
        """Full analysis of the scroll family and its design implications."""
        from .treatise_map import SCROLL_FAMILY
        members = []
        for name, info in SCROLL_FAMILY.items():
            members.append({
                "name": name,
                "description": info["description"],
                "tuple": info["tuple"],
            })
        design = self.mapper.scroll_family_design()
        return {
            "family_name": "Scroll Family",
            "invariant": {"⊙": "⊙", "Ω": "𐑭"},
            "members": members,
            "molecular_design": design,
        }

    # ─── Operation Pipeline ────────────────────────────────────

    def trace_opus_on_treatise(self, treatise_name):
        """Trace the alchemical grand sequence on a treatise's tuple."""
        if treatise_name in ALCHEMICAL_CORPUS_TAXONOMY:
            start = dict(ALCHEMICAL_CORPUS_TAXONOMY[treatise_name]["tuple"])
        else:
            return {"error": f"Unknown treatise: {treatise_name}"}
        trace = self.ops.trace_opus(start)
        return {
            "starting_treatise": treatise_name,
            "starting_tuple": start,
            "sequence": trace,
        }

    # ─── Molecular Design Suggestions ──────────────────────────

    def suggest_design(self, treatise_name):
        """Get concrete molecular design suggestions from a treatise."""
        analysis = self.analyze_treatise(treatise_name)
        if "error" in analysis:
            return analysis
        design = analysis.get("molecular_design", {})
        ch3mp = design.get("ch3mpiler_params", {})
        serp = design.get("serpentrod_params", {})
        return {
            "source": treatise_name,
            "tier": analysis["tier"],
            "design_brief": {
                "ch3mpiler": {
                    "target": ch3mp.get("recommended_targets", []),
                    "synthesis_mode": ch3mp.get("synthesis_mode", "unknown"),
                    "bond_types": ch3mp.get("bond_types", []),
                },
                "serpentrod": {
                    "fold_type": serp.get("fold_type", "unknown"),
                    "design_strategy": serp.get("design_strategy", "unknown"),
                    "target_function": serp.get("target_function", "unknown"),
                },
                "clink_layer": design.get("clink_layer", None),
            },
        }

    # ─── Report ────────────────────────────────────────────────

    def full_report(self):
        """Generate a comprehensive report of the bridge state."""
        taxonomy = self.mapper.taxonomy()
        lines = [
            "=" * 66,
            "ALCHEMICAL BRIDGE — Structural Report",
            "=" * 66,
        ]
        for tier_name, info in taxonomy.items():
            lines.append(f"\n[{info['tier']}] {tier_name}")
            lines.append(f"  {info['count']} texts")
            lines.append(f"  {info['description']}")
            tier_key = TAXONOMY_TIER_MAP.get(tier_name, tier_name)
            design = self.mapper.design_for_tier(tier_key)
            if design:
                ch3 = design.get("ch3mpiler_params", {})
                targets = ch3.get("recommended_targets", [])
                if targets:
                    lines.append(f"  → Design targets: {', '.join(targets[:3])}")

        lines.append("\n" + "=" * 66)
        lines.append("SCROLL FAMILY (φ̂=⊙ + Ω=𐑭)")
        lines.append("=" * 66)
        from .treatise_map import SCROLL_FAMILY
        for name, info in SCROLL_FAMILY.items():
            lines.append(f"  • {name}: {info['description']}")

        lines.append(f"\nGrand Sequence (12 steps):")
        for step_name, _, desc in self.ops.grand_sequence():
            lines.append(f"  {step_name:20s} → {desc}")

        return "\n".join(lines)


def bridge_summary():
    """Print a quick summary of the bridge."""
    bridge = AlchemicalBridge()
    report = bridge.full_report()
    print(report)
    return report
