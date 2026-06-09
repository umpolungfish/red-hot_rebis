"""
imas/ — IMASM Arranger: A Sixth Pillar of the Red-Hot Rebis
============================================================
Structural arrangement engine bridging IMASM token space (430M arrangements)
to the Imscribing Grammar crystal (17.28M types) and the CLINK biological
scale chain (9 layers, quark→organism).

This pillar operationalizes the discoveries from the IMSCRIBr exploration:
  1. Frobenius rarity: only 0 in 10M random arrangements have μ∘δ=id pairs
  2. Generic mass: 99.993% of arrangements map to just 4 IG types
  3. Chiral/Empty collapse: distinct token sequences → identical IG types
  4. Single ⊙-critical: only the Dialetheic Bootstrap achieves self-modeling
  5. Frobenius cluster: 4 canonicals share R=𐑾, P=𐑹, C=𐑠, H=𐑫, Ω=𐑭
  6. Linear Chain isolation: mismatch ≥ 8 from every other canonical
  7. Length-8 constraint: arrangement length pre-shapes IG primitives

Modules:
  arranger.py      — IMASM arrangement generation, fingerprinting, search
  ig_bridge.py     — Fingerprint → IG structural type mapping
  clink_bridge.py  — IMASM arrangement → CLINK biological layer bridge
  frobenius_hunter.py — Targeted enumeration for Frobenius-closed arrangements

Author: Lando⊗⊙perator
"""

from imas.arranger import (
    StructuralFingerprint,
    compute_fingerprint,
    CANONICAL_ARRANGEMENTS,
    CANONICAL_FINGERPRINTS,
    CANONICAL_NAMES,
)
from imas.ig_bridge import (
    fingerprint_to_ig,
    canonical_ig_types,
    distinct_canonical_ig_types,
    ig_distance,
    ig_distance_matrix,
    ig_tuple_str,
    describe_ig,
)
from imas.clink_bridge import (
    imasm_to_clink,
    canonical_clink_map,
    structural_activation_energy,
    IMASM_CLINK_BRIDGE_TABLE,
)

__all__ = [
    # arranger
    "StructuralFingerprint", "compute_fingerprint",
    "CANONICAL_ARRANGEMENTS", "CANONICAL_FINGERPRINTS", "CANONICAL_NAMES",
    # ig_bridge
    "fingerprint_to_ig", "canonical_ig_types", "distinct_canonical_ig_types",
    "ig_distance", "ig_distance_matrix", "ig_tuple_str", "describe_ig",
    # clink_bridge
    "imasm_to_clink", "canonical_clink_map", "structural_activation_energy",
    "IMASM_CLINK_BRIDGE_TABLE",
]
