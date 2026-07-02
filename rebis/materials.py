"""
rebis.materials — Materials Science & Metamaterial Design
══════════════════════════════════════════════════════════
Lazy-import bridge to materials/.

Callable as a command:
  rebis.materials list             — List design tools
  rebis.materials status           — Show results
  rebis.materials forge [tuple]    — Forge material
  rebis.materials sim [name]       — Run simulation
"""

import sys, importlib, argparse, json, runpy
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


def _cmd_list(args):
    """List all available design tools."""
    import rebis.materials as mat
    tools = [
        ("MaterialForge",         "Forge material designs from IG tuples"),
        ("CriticalMetamaterial",  "Design critical / ⊙-sensing metamaterials"),
        ("FrobeniusMetamaterial", "Frobenius-closed metamaterial designs"),
        ("OuroboricAlloy",        "Self-referential alloy design"),
        ("NonQubitQCParadigm",    "Non-qubit quantum computing paradigms"),
        ("SophickForge",          "Sophick mercury forge"),
        ("MBNCDesigner",          "Mycelial bio-nano conduit designer"),
        ("CasimirCavityDesigner", "Casimir cavity ZPE designer"),
        ("resolve_molecule",      "Resolve molecule name → SMILES"),
        ("molecule_to_material_tuple", "Map molecule to IG tuple"),
    ]
    print("rebis.materials — Available Design Tools:")
    for name, desc in tools:
        obj = getattr(mat, name, None)
        status = "✓" if obj else "✗"
        print(f"  {status} {name:30s} — {desc}")
    return 0


def _cmd_status(args):
    """Show results and reports."""
    mat_dir = _REBIS_ROOT / "materials"
    results_files = [
        "forged_materials.json", "frobenius_metamaterial_results.json",
        "frobenius_metamaterial_enhanced_results.json",
        "critical_metamaterial_results.json", "ouroboric_alloy_results.json",
        "thermal_rectifier_results.json", "sophick_forge_results.json",
        "materials_simulation_results.json",
    ]
    print("rebis.materials — Results & Reports:")
    found = 0
    for fname in results_files:
        fpath = mat_dir / fname
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"  ✓ {fname:45s}  ({size:,d} bytes)")
            found += 1
        else:
            print(f"  · {fname:45s}  (not yet generated)")
    reports = sorted(mat_dir.glob("*.md"))
    if reports:
        print()
        print("Reports:")
        for r in reports:
            print(f"  {r.name}")
    print(f"\n{found}/{len(results_files)} result files present")
    return 0


def _cmd_forge(args):
    """Forge material from IG tuple."""
    import rebis.materials as mat
    if not args.structural_tuple:
        try:
            forge = mat.MaterialForge()
            print("MaterialForge instantiated. Design from IG tuple.")
            print("Example from Python:")
            print('  from rebis.materials import MaterialForge')
            print('  forge = MaterialForge()')
            print('  result = forge.design(tuple)')
            print('Or use: rebis.materials forge "<tuple>"')
        except Exception as e:
            print(f"MaterialForge error: {e}")
        return 0
    try:
        forge = mat.MaterialForge()
        result = forge.design(args.structural_tuple)
        print(json.dumps(result, indent=2) if isinstance(result, dict) else result)
    except Exception as e:
        print(f"Forge failed: {e}")
        return 1
    return 0


def _cmd_sim(args):
    """Run a materials simulation."""
    sim_name = args.sim_name or "default"
    mod_path = _REBIS_ROOT / "materials" / "materials_sim.py"
    if mod_path.exists():
        print(f"Running simulation: {sim_name}")
        try:
            runpy.run_path(str(mod_path), run_name="__main__")
            return 0
        except Exception as e:
            print(f"Simulation failed: {e}")
            return 1
    else:
        print("materials_sim.py not found")
        return 1


def main():
    """CLI: rebis.materials <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.materials",
        description="rebis.materials — Materials Science & Metamaterial Design",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_ls = sub.add_parser("list",
        help="List available design tools",
        description="List all materials design tools with availability status.",
        epilog="Example:  rebis.materials list",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ls.set_defaults(func=_cmd_list)

    p_stat = sub.add_parser("status",
        help="Show results and report files",
        description="Display generated result JSON files and Markdown reports\n"
                    "in the materials/ output directory.",
        epilog="Example:  rebis.materials status",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_stat.set_defaults(func=_cmd_status)

    p_for = sub.add_parser("forge",
        help="Forge material from IG structural tuple",
        description="Forge a material design from a 12-primitive IG structural\n"
                    "tuple. Without arguments, shows Python API usage.",
        epilog="Examples:  rebis.materials forge\n"
               "           rebis.materials forge '⟨𐑛𐑨𐑑𐑬𐑞𐑺𐑲𐑝𐑢𐑓𐑕𐑷⟩'",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_for.add_argument("structural_tuple", nargs="?", default="",
                       help="IG tuple string (e.g. ⟨𐑛𐑨𐑑𐑬𐑞𐑺𐑲𐑝𐑢𐑓𐑕𐑷⟩)")
    p_for.set_defaults(func=_cmd_forge)

    p_sim = sub.add_parser("sim",
        help="Run materials simulation",
        description="Run the materials simulation suite (materials_sim.py).",
        epilog="Examples:  rebis.materials sim\n"
               "           rebis.materials sim metamaterial",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_sim.add_argument("sim_name", nargs="?", default="",
                       help="Simulation name (default: 'default')")
    p_sim.set_defaults(func=_cmd_sim)

    sub.add_parser("help",
        help="Show this help message",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    args = parser.parse_args()

    if not args.command or args.command == "help":
        parser.print_help()
        return 0

    if hasattr(args, 'func'):
        return args.func(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
