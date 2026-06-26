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

__all__ = [
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
]
