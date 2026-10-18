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
import importlib as _importlib

_EXPORTS = {'MaterialForge': 'materials.ig_material_forge',
 'MaterialDesign': 'materials.ig_material_forge',
 'predefined_novel_materials': 'materials.ig_material_forge',
 'FrobeniusMetamaterial': 'materials.frobenius_metamaterial',
 'FrobeniusMaterialParams': 'materials.frobenius_metamaterial',
 'OuroboricAlloy': 'materials.ouroboric_alloy'}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(_importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
