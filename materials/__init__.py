"""
red-hot_rebis materials — IG Structural Material Design Suite
=============================================================

Modules:
  ig_material_forge.py      — IG structural type → concrete material design bridge
  frobenius_metamaterial.py — μ∘δ=id self-verifying metamaterial simulation
  ouroboric_alloy.py        — Topological self-healing HEA simulation
  critical_metamaterial.py  — ⊙-critical metamaterial sensor (existing)
  materials_sim.py          — Self-healing composite + eternal memory polymer (existing)
  thermal_rectifier.py      — Topological thermal rectifier / heat diode (existing)

CLI (via rebis.py):
  rebis.py materials forge --all           # Forge all 8 predefined novel materials
  rebis.py materials forge --name <name>   # Forge one material or IMASM canonical
  rebis.py materials report               # Full report on frobenius composite
  rebis.py materials list                 # List all available material names
  rebis.py materials frobenius            # Run Frobenius metamaterial simulation
  rebis.py materials ouroboric            # Run Ouroboric alloy simulation
"""

from materials.ig_material_forge import MaterialForge, MaterialDesign, predefined_novel_materials
from materials.frobenius_metamaterial import FrobeniusMetamaterial, FrobeniusMaterialParams
from materials.ouroboric_alloy import OuroboricAlloy

__all__ = [
    'MaterialForge', 'MaterialDesign', 'predefined_novel_materials',
    'FrobeniusMetamaterial', 'FrobeniusMaterialParams',
    'OuroboricAlloy',
]
