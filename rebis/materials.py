"""
rebis.materials — Materials Science & Metamaterial Design
══════════════════════════════════════════════════════════
Lazy-import bridge to materials/.

Callable as a command:
  rebis.materials list            — List design tools
  rebis.materials status          — Show results
  rebis.materials forge [tuple]   — Forge material
  rebis.materials sim [name]      — Run simulation
"""

import sys, importlib, argparse
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "materials")]:
    if p not in sys.path: sys.path.insert(0, p)

__all__ = []

def _lazy(name, module, attr=None):
    try:
        m = importlib.import_module(module)
        globals()[name] = getattr(m, attr or name)
        __all__.append(name)
    except Exception:
        pass

_lazy("CriticalMetamaterial", "materials.critical_metamaterial")
_lazy("ClosureStatus", "materials.critical_metamaterial")
_lazy("ClosureDesign", "materials.critical_metamaterial")
_lazy("FrobeniusClosureType", "materials.frobenius_closure_complete")
_lazy("ClosureObstruction", "materials.frobenius_closure_complete")
_lazy("ExactFrobeniusState", "materials.frobenius_closure_complete")
_lazy("FrobeniusExactor", "materials.frobenius_exactor")
_lazy("FrobeniusMetamaterial", "materials.frobenius_metamaterial")
_lazy("MaterialDesign", "materials.ig_material_forge")
_lazy("MaterialForge", "materials.ig_material_forge")
_lazy("SophickForge", "materials.sophick_forge")
_lazy("design_sophick_material", "materials.sophick_forge")
_lazy("OuroboricAlloy", "materials.ouroboric_alloy")
_lazy("NonQubitQCParadigm", "materials.non_qubit_qc")
_lazy("SelfHealingComposite", "materials.gap_closure_module")
_lazy("EternalMemorySim", "materials.gap_closure_module")
_lazy("EagleMaterial", "materials.thermal_rectifier")
_lazy("resolve_molecule", "materials.molecule_material_bridge")
_lazy("molecule_to_material_tuple", "materials.molecule_material_bridge")
_lazy("OrganoidAugmentation", "materials.organoid.organoid_augmentations")
_lazy("design_organoid_augmentation", "materials.organoid.organoid_augmentations")
_lazy("MBNCDesigner", "materials.mycelial_conduit.mbnc_designer")
_lazy("design_mycelial_conduit", "materials.mycelial_conduit.mbnc_designer")
_lazy("CasimirCavityDesigner", "materials.zpe_design.casimir_cavity_design")
_lazy("design_casimir_cavity", "materials.zpe_design.casimir_cavity_design")
_lazy("SophickForgeIntegration", "materials.zpe_design.sophick_forge_integration")


def main():
    """CLI: rebis.materials <action> [args]"""
    from rebis.cli import cmd_materials

    parser = argparse.ArgumentParser(
        description="rebis.materials — Materials Science & Metamaterial Design")
    parser.add_argument("material_action", nargs="?",
                       default="help",
                       choices=["list", "tools", "status", "results",
                                "forge", "sim", "simulate", "help"],
                       help="Materials action")
    parser.add_argument("structural_tuple", nargs="?",
                       help="IG tuple for forge (e.g. ⟨𐑛𐑨·⟩)")
    parser.add_argument("sim_name", nargs="?",
                       help="Simulation name")
    args = parser.parse_args()
    return cmd_materials(args)


if __name__ == "__main__":
    sys.exit(main())