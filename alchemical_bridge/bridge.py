"""
bridge.py — Alchemical Bridge: main orchestrator
==================================================

Ties together:
  - AlchemicalOperations (classical ops → IG structural ops)
  - TreatiseMapper (treatise tuples → molecular design params)
  - **6 new computational engines** integrated as live methods
  - CLI integration for rebis.py

Author: Lando⊗⊙perator
"""

from .operations import AlchemicalOperations, apply_operation
from .treatise_map import TreatiseMapper, ALCHEMICAL_CORPUS_TAXONOMY
from shared.primitives import PRIMITIVE_ORDER, ORDINALS, tuple_distance
import json
from shared.rich_output import *


# Mapping from taxonomy keys to tier keys
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
    """Unified bridge between alchemical knowledge and molecular design.

    Integrates all 6 computational engines:
      • GreenFireEngine     — photocatalytic cycle discovery
      • AlchemicalThirdEngine — supramolecular cavity/void design
      • RetrosyntheticStoneEngine — retrosynthesis as Solve et Coagula
      • ZosimosEngine       — 12-primitive structural analysis
      • ArtephiusDecoder    — cryptic → modern co-type matching
      • BasilValentineLadder — 12-step promotion ladder
    """

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.ops = AlchemicalOperations()
        self.mapper = TreatiseMapper()

        # Initialize the 6 engines (lazy — imported only when first used)
        self._green_fire = None
        self._alchemical_third = None
        self._retro_stone = None
        self._zosimos = None
        self._artephius = None
        self._basil_valentine = None

    # ── Lazy Engine Accessors ──────────────────────────────────

    @property
    def green_fire(self):
        if self._green_fire is None:
            from .green_fire_engine import GreenFireEngine
            self._green_fire = GreenFireEngine()
        return self._green_fire

    @property
    def alchemical_third(self):
        if self._alchemical_third is None:
            from .alchemical_third_engine import AlchemicalThirdEngine
            self._alchemical_third = AlchemicalThirdEngine()
        return self._alchemical_third

    @property
    def retro_stone(self):
        if self._retro_stone is None:
            from .retrosynthetic_stone_engine import RetrosyntheticStoneEngine
            self._retro_stone = RetrosyntheticStoneEngine()
        return self._retro_stone

    @property
    def zosimos(self):
        if self._zosimos is None:
            from .zosimos_engine import ZosimosEngine
            self._zosimos = ZosimosEngine()
        return self._zosimos

    @property
    def artephius(self):
        if self._artephius is None:
            from .artephius_decoder import ArtephiusDecoder
            self._artephius = ArtephiusDecoder()
        return self._artephius

    @property
    def basil_valentine(self):
        if self._basil_valentine is None:
            from .basil_valentine_ladder import BasilValentineLadder
            self._basil_valentine = BasilValentineLadder()
        return self._basil_valentine
    # ── Original methods ──────────────────────────────────────

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
    # ── NEW: Green Fire Engine Methods ──────────────────────────

    def analyze_photocatalyst(self, catalyst_smiles: str, substrate_smiles: str = None) -> dict:
        """Analyze a molecule's photocatalytic potential (Green Fire)."""
        return self.green_fire.analyze_catalyst(catalyst_smiles, substrate_smiles)

    def suggest_wavelength(self, catalyst_smiles: str) -> dict:
        """Suggest optimal excitation wavelength for a catalyst."""
        return self.green_fire.suggest_optimal_wavelength(catalyst_smiles)

    # ── NEW: Alchemical Third Engine Methods ────────────────────

    def analyze_host(self, host_smiles: str) -> dict:
        """Analyze a host molecule's cavity/void properties (Salt)."""
        return self.alchemical_third.analyze_host(host_smiles)

    def compute_binding(self, host_smiles: str, guest_smiles: str) -> dict:
        """Compute host-guest binding compatibility."""
        return self.alchemical_third.compute_binding(host_smiles, guest_smiles)

    def screen_hosts(self, guest_smiles: str, library: list = None) -> list:
        """Screen host library against a guest."""
        return self.alchemical_third.suggest_host_for_guest(guest_smiles, library)

    # ── NEW: Retrosynthetic Stone Engine Methods ────────────────

    def plan_synthesis(self, target_smiles: str) -> dict:
        """Plan a retrosynthetic route (Solve et Coagula)."""
        return self.retro_stone.plan_synthesis(target_smiles)

    def grand_sequence_synthesis(self, target_smiles: str) -> dict:
        """Full 12-step grand sequence for a target molecule."""
        return self.retro_stone.grand_sequence(target_smiles)

    # ── NEW: Zosimos Engine Methods ─────────────────────────────

    def analyze_structure(self, name: str, tuple_dict: dict) -> dict:
        """Analyze a structural type through Zosimos' lens."""
        return self.zosimos.analyze_structure(name, tuple_dict)

    def check_portico(self, tuple_dict: dict) -> dict:
        """Check if a tuple is at the Portico (Gödel fixed point)."""
        from .zosimos_engine import check_portico
        return check_portico(tuple_dict)

    def perform_stilling(self, tuple_dict: dict) -> dict:
        """Perform the Stilling Practice on a tuple."""
        return self.zosimos.perform_stilling(tuple_dict)

    # ── NEW: Artephius Decoder Methods ──────────────────────────

    def decode_cryptic(self, cryptic_phrase: str) -> dict:
        """Decode a cryptic alchemical phrase into modern science."""
        return self.artephius.decode(cryptic_phrase)

    def learn_decoding(self, cryptic: str, modern: str, stype: str,
                        confidence: float, source: str = "decoder") -> dict:
        """Teach the decoder a new cryptic→modern mapping."""
        return self.artephius.learn(cryptic, modern, stype, confidence, source)

    def decode_molecule(self, smiles: str, context: str = None) -> dict:
        """Get the alchemical interpretation of a molecule."""
        return self.artephius.decode_molecule(smiles, context)

    # ── NEW: Basil Valentine Ladder Methods ─────────────────────

    def climb_to_stone(self, source_tuple: dict = None) -> dict:
        """Compute the 12-step promotion ladder to the Stone."""
        return self.basil_valentine.climb_to_stone(source_tuple)

    def climb_between(self, source: dict, target: dict) -> dict:
        """Compute promotion ladder between any two tuples."""
        return self.basil_valentine.climb_between(source, target)

    def key_info(self, key_number: int) -> dict:
        """Get canonical info about a specific Key."""
        return self.basil_valentine.key_info(key_number)

    def full_opus_report(self, source_tuple: dict = None) -> dict:
        """Full Opus Magnum report with all 12 Keys."""
        return self.basil_valentine.full_opus_report(source_tuple)
    # ── Report ──────────────────────────────────────────────────

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
                    lines.append(f"  \u2192 Design targets: {', '.join(targets[:3])}")

        lines.append("\n" + "=" * 66)
        lines.append("SCROLL FAMILY (\u03c6\u0302=\u2299 + \u03a9=\U0001046D)")
        lines.append("=" * 66)
        from .treatise_map import SCROLL_FAMILY

        for name, info in SCROLL_FAMILY.items():
            lines.append(f"  \u2022 {name}: {info['description']}")

        lines.append(f"\nGrand Sequence (12 steps):")
        for step_name, _, desc in self.ops.grand_sequence():
            lines.append(f"  {step_name:20s} \u2192 {desc}")

        lines.append("\n" + "=" * 66)
        lines.append("6 COMPUTATIONAL ENGINES (fully functional)")
        lines.append("=" * 66)
        lines.append("  \u2022 GreenFireEngine         \u2014 Photocatalytic cycle discovery (Secret Fire)")
        lines.append("  \u2022 AlchemicalThirdEngine    \u2014 Supramolecular cavity/void design (Salt)")
        lines.append("  \u2022 RetrosyntheticStoneEngine \u2014 Solve et Coagula retrosynthesis")
        lines.append("  \u2022 ZosimosEngine            \u2014 12-primitive structural analysis")
        lines.append("  \u2022 ArtephiusDecoder         \u2014 Cryptic \u2192 modern co-type matching")
        lines.append("  \u2022 BasilValentineLadder     \u2014 12-step promotion ladder")

        return "\n".join(lines)


def bridge_summary():
    """Print a quick summary of the bridge."""
    bridge = AlchemicalBridge()
    report = bridge.full_report()
    print(report)
    return report
