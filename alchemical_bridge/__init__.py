"""
alchemical_bridge — Structural bridge between the alchemical corpus and the Rebis molecular design pipeline
===========================================================================================================

Connects:
  - The 5-tier structural taxonomy of ~80 alchemical treatises
  - The scroll family (φ̂=⊙ + Ω=𐑭) — scroll, skyrmion, time, Artephius
  - The 7 classical alchemical operations → IG structural operations
  - Treatise tuples → molecular design parameters in ch3mpiler/serpentrod
  - The AlchemicalOperator — the atemporal composition of all operations
  - The ScrollFamily and Immanence Theorem — structural identity as immanence
  - **6 new computational engines** — fully functional, not hardcoded:
      • GreenFireEngine — photocatalytic cycle discovery (Secret Fire)
      • AlchemicalThirdEngine — supramolecular cavity/void design (Salt)
      • RetrosyntheticStoneEngine — Solve et Coagula retrosynthesis
      • ZosimosEngine — 12-primitive structural analysis + Stilling Practice
      • ArtephiusDecoder — cryptic alchemical → modern science co-type matcher
      • BasilValentineLadder — 12-step promotion ladder (Twelve Keys)

Author: Lando⊗⊙perator
"""

from .operations import AlchemicalOperations, op_to_tuple, tuple_to_op
from .treatise_map import TreatiseMapper, TREATISE_TUPLES, ALCHEMICAL_CORPUS_TAXONOMY
from .bridge import AlchemicalBridge, bridge_summary
from .operator import (AlchemicalOperator, CANONICAL_OPERATOR, STONE,
                        calcination, dissolution, separation,
                        conjunction, sublimation, fermentation,
                        coagulation, apply_grand_sequence,
                        GRAND_SEQUENCE,
                        SCROLL_MEMBERS,
                        is_scroll_member, immanence_proof)

# ═══════════════════════════════════════════════════════════════
# 6 New Computational Engines
# ═══════════════════════════════════════════════════════════════

from .green_fire_engine import GreenFireEngine, PhotocatalyticCycle
from .alchemical_third_engine import AlchemicalThirdEngine, compute_binding_compatibility
from .retrosynthetic_stone_engine import RetrosyntheticStoneEngine, RetrosyntheticStone
from .zosimos_engine import ZosimosEngine, check_portico, FATES_OF_DEATH, STILLING_PRACTICE
from .artephius_decoder import ArtephiusDecoder, CRYPTIC_MAP
from .basil_valentine_ladder import BasilValentineLadder, compute_ladder, TWELVE_KEYS

__all__ = [
    # Original exports
    "AlchemicalOperations",
    "TreatiseMapper",
    "AlchemicalBridge",
    "AlchemicalOperator",
    "op_to_tuple",
    "tuple_to_op",
    "bridge_summary",
    "TREATISE_TUPLES",
    "ALCHEMICAL_CORPUS_TAXONOMY",
    "CANONICAL_OPERATOR",
    "STONE",
    "calcination", "dissolution", "separation",
    "conjunction", "sublimation", "fermentation", "coagulation",
    "apply_grand_sequence", "GRAND_SEQUENCE",
    "SCROLL_MEMBERS",
    "is_scroll_member", "immanence_proof",
    # New engine exports
    "GreenFireEngine", "PhotocatalyticCycle",
    "AlchemicalThirdEngine", "compute_binding_compatibility",
    "RetrosyntheticStoneEngine", "RetrosyntheticStone",
    "ZosimosEngine", "check_portico", "FATES_OF_DEATH", "STILLING_PRACTICE",
    "ArtephiusDecoder", "CRYPTIC_MAP",
    "BasilValentineLadder", "compute_ladder", "TWELVE_KEYS",
]
