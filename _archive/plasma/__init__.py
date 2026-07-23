"""
red-hot_rebis plasma — IG Structural Plasma Physics Suite
=========================================================

Plasma physics from first principles via the 12-primitive Imscribing Grammar.
Plasma sits structurally between Atom (CLINK L2) and Molecule (CLINK L3) —
the "collectivized atom" where atoms surrender individual identity to the
electromagnetic collective.

Modules:
  plasma_chain.py    — Plasma-specific CLINK chain insertion + distance ladder
  plasma_forge.py    — IG structural type → plasma parameter bridge
  plasma_ob3ects.py  — Four ob3ect-generated plasma designs as first-class types
  plasma_imas.py     — IMASM arrangement ↔ plasma physics mapping
  plasma_bridge.py   — Bridge to ch3mpiler, materials, biology, alchemy

CLI (via rebis.py):
  rebis.py plasma chain              # Plasma CLINK insertion + distance ladder
  rebis.py plasma forge --type <n>   # Forge plasma parameters from IG tuple
  rebis.py plasma imas               # IMASM ↔ plasma mapping report
  rebis.py plasma bridge             # Cross-domain bridge report
  rebis.py plasma ob3ects            # List all four ob3ect plasma designs

Key structural facts (verified via imscribe):
  Vlasov plasma:     ⟨𐑛𐑥𐑾𐑬𐑱𐑧𐑔𐑠𐑮𐑖𐑳𐑭⟩  O₂, C=0.5455
  Primitive-First:   ⟨𐑼𐑡𐑾𐑗𐑱𐑧𐑚𐑠⊙𐑖𐑳𐑭⟩  O₂†, C=0.263
  High-Energy:       ⟨𐑼𐑡𐑾𐑗𐑱𐑧𐑚𐑠⊙𐑓𐑙𐑭⟩  O₂†
  Rock-Cracking:     ⟨𐑼𐑡𐑾𐑗𐑱𐑧𐑚𐑠⊙𐑖𐑙𐑭⟩  O₂†
  d(plasma, CLINK L8 organism) = 1.54
  d(plasma, normal ovulatory cycle) = 1.51 (nearest biological analog)

Author: Lando⊗⊙perator
"""

from plasma.plasma_chain import (
    PLASMA_TYPES, PLASMA_NAMES, PLASMA_TIERS,
    plasma_clink_position, plasma_distance_ladder,
    plasma_to_organism_promotions, PLASMA_PORDER,
)
from plasma.plasma_ob3ects import (
    PLASMA_OB3ECTS, plasma_ob3ect_by_name,
    plasma_ob3ect_opcode_map, plasma_ob3ect_bootstrap,
)
from plasma.plasma_forge import (
    PlasmaForge, PlasmaDesign, PLASMA_PRIMITIVE_MAP,
)
from plasma.plasma_imas import (
    PLASMA_IMASM_MAP, imasm_to_plasma_tuple,
    plasma_opcode_physics,
)
from plasma.plasma_bridge import (
    plasma_to_ch3mpiler, plasma_to_materials,
    plasma_to_alchemy, plasma_nearest_biological,
)

__all__ = [
    'PLASMA_TYPES', 'PLASMA_NAMES', 'PLASMA_TIERS', 'PLASMA_PORDER',
    'plasma_clink_position', 'plasma_distance_ladder',
    'plasma_to_organism_promotions',
    'PLASMA_OB3ECTS', 'plasma_ob3ect_by_name',
    'plasma_ob3ect_opcode_map', 'plasma_ob3ect_bootstrap',
    'PlasmaForge', 'PlasmaDesign', 'PLASMA_PRIMITIVE_MAP',
    'PLASMA_IMASM_MAP', 'imasm_to_plasma_tuple', 'plasma_opcode_physics',
    'plasma_to_ch3mpiler', 'plasma_to_materials',
    'plasma_to_alchemy', 'plasma_nearest_biological',
]
