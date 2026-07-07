"""
rebis.materials — Materials Science & Metamaterial Design (ADVANCED v2)
══════════════════════════════════════════════════════════════════════
Full implementations of:
  - MaterialForge: Forge materials from IG tuples
  - FrobeniusMetamaterial: μ∘δ=id self-verifying metamaterial simulation
  - CriticalMetamaterial: ⊙-sensing critical metamaterial
  - OuroboricAlloy: Topological grain boundary network
  - NonQubitQCParadigm: Non-qubit quantum computing material designs
  - SophickForge, CasimirCavityDesigner, MBNCDesigner, etc.

Callable as a command:
  rebis.materials forge [name] [--tuple TUPLE] [--from-catalog NAME]
  rebis.materials metamaterial [--size 20] [--cycles 20] [--heal-steps 10]
  rebis.materials critical [--size 16] [--kappa 0.2] [--nonlinear 0.1] [--time 60]
  rebis.materials alloy [--n-grains 64]
  rebis.materials nonqubit
  rebis.materials sophick
  rebis.materials casimir [--target-gap 0.1]
  rebis.materials molecule <smiles> [--cas ID] [--name NAME]
  rebis.materials list
  rebis.materials status
"""
import sys, importlib, argparse, json, runpy
from pathlib import Path
from rebis.file_input import parse_with_file

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "materials"),
          str(_REBIS_ROOT / "shared")]:
    if p not in sys.path:
        sys.path.insert(0, p)

__all__ = []

def _lazy(name, module, attr=None):
    try:
        m = importlib.import_module(module)
        globals()[name] = getattr(m, attr or name)
        __all__.append(name)
    except Exception:
        pass

_lazy("CriticalMetamaterial", "materials.critical_metamaterial")
_lazy("ClosureStatus", "materials.frobenius_closure_complete")
_lazy("ClosureDesign", "materials.frobenius_closure_complete")
_lazy("StructuralOpenDiagnosis", "materials.frobenius_closure_complete")
_lazy("complete_closure_table", "materials.frobenius_closure_complete")
_lazy("closure_mechanism_comparison", "materials.frobenius_closure_complete")
_lazy("FrobeniusClosureType", "materials.frobenius_exactor")
_lazy("ClosureObstruction", "materials.frobenius_exactor")
_lazy("ExactFrobeniusState", "materials.frobenius_exactor")
_lazy("ExactorMaterial", "materials.frobenius_exactor")
_lazy("design_exactor_omega", "materials.frobenius_exactor")
_lazy("FrobeniusMetamaterial", "materials.frobenius_metamaterial")
_lazy("FrobeniusMaterialParams", "materials.frobenius_metamaterial")
_lazy("MaterialDesign", "materials.ig_material_forge")
_lazy("MaterialForge", "materials.ig_material_forge")
_lazy("predefined_novel_materials", "materials.ig_material_forge")
_lazy("SophickForge", "materials.sophick_forge")
_lazy("design_sophick_material", "materials.sophick_forge")
_lazy("OuroboricAlloy", "materials.ouroboric_alloy")
_lazy("TripleJunction", "materials.ouroboric_alloy")
_lazy("GrainBoundary", "materials.ouroboric_alloy")
_lazy("TopologicalGrainBoundaryNetwork", "materials.ouroboric_alloy")
_lazy("NonQubitQCParadigm", "materials.non_qubit_qc")
_lazy("compute_all_deltas", "materials.non_qubit_qc")
_lazy("universal_deltas", "materials.non_qubit_qc")
_lazy("OperculumAnalysis", "materials.non_qubit_qc")
_lazy("full_operculum_report", "materials.non_qubit_qc")
_lazy("export_forge_designs", "materials.non_qubit_qc")
_lazy("paradigm_summary_table", "materials.non_qubit_qc")
_lazy("SelfHealingComposite", "materials.gap_closure_module")
_lazy("EternalMemorySim", "materials.gap_closure_module")
_lazy("resolve_molecule", "materials.molecule_material_bridge")
_lazy("molecule_to_material_tuple", "materials.molecule_material_bridge")
_lazy("OrganoidAugmentation", "materials.organoid.organoid_augmentations")
_lazy("design_organoid_augmentation", "materials.organoid.organoid_augmentations")
_lazy("MBNCDesigner", "materials.mycelial_conduit.mbnc_designer")
_lazy("design_mycelial_conduit", "materials.mycelial_conduit.mbnc_designer")
_lazy("CasimirCavityDesigner", "materials.zpe_design.casimir_cavity_design")
_lazy("design_casimir_cavity", "materials.zpe_design.casimir_cavity_design")
_lazy("SophickForgeIntegration", "materials.zpe_design.sophick_forge_integration")
_lazy("ThermalRectifier", "materials.thermal_rectifier")
_lazy("EternalMemorySim", "materials.materials_sim")


def _json_or_str(obj):
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, default=str, ensure_ascii=False)
    if hasattr(obj, '__dict__'):
        try:
            return json.dumps(vars(obj), indent=2, default=str, ensure_ascii=False)
        except Exception:
            return str(obj)
    return str(obj)


def _cmd_forge(args):
    """Forge material from IG tuple or catalog name."""
    name = args.name or "forged_material"
    try:
        from materials.ig_material_forge import MaterialForge, predefined_novel_materials

        if args.from_catalog:
            print(f"═ Forging material from catalog: {args.from_catalog} ═")
            forge = MaterialForge()
            design = forge.forge_from_catalog(args.from_catalog)
            print(_json_or_str(design.to_dict() if hasattr(design, 'to_dict') else design))
            return 0

        if args.tuple:
            print(f"═ Forging material: {name} ═")
            print(f"  IG tuple: {args.tuple}")
            forge = MaterialForge()
            # Parse tuple — accept compact 12-glyph, numerical 12-tuple, or space-separated
            tup = args.tuple
            if isinstance(tup, str):
                # Try numerical 12-tuple first (e.g. "4,5,4,5,3,5,3,4,2,4,3,3")
                try:
                    from rebis.shared import parse_numerical_tuple
                    num_result = parse_numerical_tuple(tup)
                    if num_result is not None:
                        tup = tuple(num_result.values())
                    else:
                        raise ValueError("not numerical")
                except (ValueError, ImportError):
                    if len(tup) == 12:
                        tup = tuple(tup)
                    else:
                        tup = tuple(tup.split())
            design = forge.forge(name, tup)
            print(_json_or_str(design.to_dict() if hasattr(design, 'to_dict') else design))
            return 0

        # No args — list predefined materials and forge the first
        print("═ Predefined Novel Materials ═")
        materials = predefined_novel_materials()
        for mname, mtup in materials.items():
            print(f"  {mname}: {''.join(mtup) if isinstance(mtup, (tuple, list)) else mtup}")

        print(f"\nForging first material: {list(materials.keys())[0]}")
        forge = MaterialForge()
        first_name = list(materials.keys())[0]
        first_tup = materials[first_name]
        design = forge.forge(first_name, first_tup)
        print(_json_or_str(design.to_dict() if hasattr(design, 'to_dict') else design))
    except Exception as e:
        import traceback
        print(f"Forge failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_metamaterial(args):
    """Run FrobeniusMetamaterial simulation."""
    size = args.size
    cycles = args.cycles
    heal_steps = args.heal_steps
    print(f"═ Frobenius Metamaterial Simulation (μ∘δ=id) ═")
    print(f"  Grid: {size}×{size} | Load cycles: {cycles} | Heal steps/cycle: {heal_steps}")
    try:
        from materials.frobenius_metamaterial import FrobeniusMetamaterial
        mat = FrobeniusMetamaterial(size=size)
        print("  Calibrating sensors...")
        mat._calibrate_sensors()
        print(f"  Running {cycles} load-heal cycles...")
        results = mat.run_simulation(
            load_cycles=cycles,
            heal_steps_per_cycle=heal_steps,
        )
        # Compute final Frobenius norm
        fnorm = mat.compute_frobenius_norm()
        output = {
            "grid_size": size,
            "load_cycles": cycles,
            "heal_steps_per_cycle": heal_steps,
            "frobenius_norm": round(float(fnorm), 6),
            "frobenius_closed": float(fnorm) < 0.01,
            "simulation_results": results if isinstance(results, (dict, list)) else str(results),
        }
        print(f"  ✓ Frobenius norm: {fnorm:.6f} ({'CLOSED' if fnorm < 0.01 else 'OPEN'})")
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Metamaterial simulation failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_critical(args):
    """Run CriticalMetamaterial simulation."""
    size = args.size
    kappa = args.kappa
    nonlinear = args.nonlinear
    total_time = args.time
    print(f"═ Critical Metamaterial (⊙-sensing) ═")
    print(f"  Grid: {size}×{size} | κ₀: {kappa} | Nonlinearity: {nonlinear} | Time: {total_time}")
    try:
        from materials.critical_metamaterial import CriticalMetamaterial
        mat = CriticalMetamaterial(size=size, initial_kappa=kappa, nonlinearity=nonlinear)
        print("  Computing susceptibility...")
        susc = mat.compute_susceptibility()
        print(f"  Susceptibility: {susc}")
        print(f"  Running simulation for {total_time} steps...")
        result = mat.run(total_time=total_time)
        output = {
            "grid_size": size,
            "initial_kappa": kappa,
            "nonlinearity": nonlinear,
            "susceptibility": float(susc) if isinstance(susc, (int, float)) else str(susc),
            "simulation_result": result if isinstance(result, (dict, list)) else str(result),
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Critical metamaterial simulation failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_alloy(args):
    """Run OuroboricAlloy topological grain boundary network."""
    n_grains = args.n_grains
    print(f"═ Ouroboric Alloy — Topological Grain Boundary Network ═")
    print(f"  Grains: {n_grains}")
    try:
        from materials.ouroboric_alloy import TopologicalGrainBoundaryNetwork
        network = TopologicalGrainBoundaryNetwork(n_grains=n_grains)
        total_winding = network.total_winding()
        output = {
            "n_grains": n_grains,
            "total_winding": int(total_winding) if isinstance(total_winding, (int, float)) else str(total_winding),
            "n_triple_junctions": len(network.triple_junctions) if hasattr(network, 'triple_junctions') else None,
            "n_grain_boundaries": len(network.boundaries) if hasattr(network, 'boundaries') else None,
        }
        # Compute crack driving force at a junction
        try:
            cdf = network.compute_crack_driving_force(0)
            output["crack_driving_force_junction_0"] = float(cdf) if isinstance(cdf, (int, float)) else str(cdf)
        except Exception:
            pass
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Alloy simulation failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_nonqubit(args):
    """Run NonQubitQCParadigm analysis."""
    print("═ Non-Qubit Quantum Computing Paradigm Analysis ═")
    try:
        from materials.non_qubit_qc import (
            NonQubitQCParadigm, compute_all_deltas, universal_deltas,
            full_operculum_report, paradigm_summary_table, export_forge_designs,
        )
        print("  Computing primitive deltas...")
        deltas = compute_all_deltas()
        print("  Universal deltas:")
        ud = universal_deltas()
        print(f"    {ud}")
        print("  Generating operculum report...")
        operculum = full_operculum_report()
        print("  Generating paradigm summary table...")
        summary = paradigm_summary_table()
        print("  Exporting forge designs...")
        forge_designs = export_forge_designs()
        output = {
            "primitive_deltas": deltas if isinstance(deltas, (dict, list)) else str(deltas),
            "universal_deltas": ud if isinstance(ud, (dict, list)) else str(ud),
            "operculum_report": operculum if isinstance(operculum, (dict, list)) else str(operculum)[:2000],
            "summary_table": str(summary)[:2000],
            "forge_designs": forge_designs if isinstance(forge_designs, (dict, list)) else str(forge_designs)[:2000],
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Non-qubit QC analysis failed: {e}")
        traceback.print_exc()
        return 1
    return 0

def _cmd_sophick(args):
    """Run SophickForge."""
    print("═ Sophick Forge ═")
    try:
        from materials.sophick_forge import SophickForge
        forge = SophickForge()
        result = forge.design() if hasattr(forge, 'design') else str(forge)
        print(_json_or_str(result))
    except Exception as e:
        import traceback
        print(f"Sophick forge failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_casimir(args):
    """Run CasimirCavityDesigner."""
    target_gap = args.target_gap
    print("═ Casimir Cavity Designer (ZPE) ═")
    print(f"  Target gap: {target_gap} µm")
    try:
        from materials.zpe_design.casimir_cavity_design import CasimirCavityDesigner
        designer = CasimirCavityDesigner()
        result = designer.design(target_gap_um=target_gap) if hasattr(designer, 'design') else str(designer)
        print(_json_or_str(result))
    except Exception as e:
        import traceback
        print(f"Casimir cavity design failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_molecule(args):
    """Resolve molecule name/CAS to SMILES and compute IG tuple."""
    smiles = args.smiles
    cas = args.cas
    name = args.name
    print("═ Molecule → Material Bridge ═")
    try:
        from materials.molecule_material_bridge import (
            resolve_molecule, molecule_to_material_tuple)
        mol_data = resolve_molecule(cas=cas, name=name) if (cas or name) else {"smiles": smiles}
        print(f"  Resolved: {mol_data.get('name', 'unknown')}")
        print(f"  SMILES: {mol_data.get('smiles', smiles)}")
        ig_tuple = molecule_to_material_tuple(mol_data)
        output = {
            "input": {"smiles": smiles, "cas": cas, "name": name},
            "resolved": mol_data if isinstance(mol_data, (dict, list)) else str(mol_data),
            "ig_tuple": ig_tuple if isinstance(ig_tuple, (dict, list)) else str(ig_tuple),
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Molecule bridge failed: {e}")
        traceback.print_exc()
        return 1
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
        print("\nReports:")
        for r in reports:
            print(f"  {r.name}")
    print(f"\n{found}/{len(results_files)} result files present")
    return 0


def _cmd_list(args):
    print("rebis.materials — Available Design Tools:")
    tools = [
        ("MaterialForge",         "Forge material designs from IG tuples"),
        ("FrobeniusMetamaterial", "Frobenius-closed metamaterial simulation"),
        ("CriticalMetamaterial",  "⊙-sensing critical metamaterial"),
        ("OuroboricAlloy",        "Topological grain boundary network"),
        ("NonQubitQCParadigm",    "Non-qubit quantum computing paradigms"),
        ("SophickForge",          "Sophick mercury forge"),
        ("CasimirCavityDesigner", "Casimir cavity ZPE designer"),
        ("MBNCDesigner",          "Mycelial bio-nano conduit designer"),
        ("ThermalRectifier",      "Thermal rectifier material"),
        ("resolve_molecule",      "Resolve molecule name → SMILES"),
        ("molecule_to_material_tuple", "Map molecule to IG tuple"),
        ("SelfHealingComposite",  "Self-healing composite simulation"),
        ("EternalMemorySim",      "Eternal polymer memory simulation"),
    ]
    for name, desc in tools:
        obj = globals().get(name)
        status = "✓" if obj is not None else "✗"
        print(f"  {status} {name:30s} — {desc}")
    print("\nCommands:")
    print("  forge [name]          — Forge material from IG tuple or catalog")
    print("  metamaterial          — Frobenius μ∘δ=id metamaterial sim")
    print("  critical              — ⊙-sensing critical metamaterial sim")
    print("  alloy                 — Topological grain boundary network")
    print("  nonqubit              — Non-qubit QC paradigm analysis")
    print("  sophick               — Sophick forge")
    print("  casimir               — Casimir cavity ZPE design")
    print("  molecule <smiles>     — Molecule → IG tuple bridge")
    print("  status                — Show result files")
    print("  list                  — List tools")
    return 0


def main():
    """CLI: rebis.materials <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.materials",
        description="rebis.materials — Materials Science & Metamaterial Design",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    # ── forge ──
    p_forge = sub.add_parser("forge",
        help="Forge material from IG tuple or catalog entry",
        description="Forge a material design from a 12-primitive IG tuple,\n"
                    "a catalog entry name, or list predefined novel materials.",
        epilog="Examples:  rebis.materials forge\n"
               "           rebis.materials forge mymat --tuple 𐑼𐑸𐑾𐑹𐑞𐑧𐑲𐑠⊙𐑫𐑳𐑭\n"
               "           rebis.materials forge --from-catalog magnetar",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_forge.add_argument("name", nargs="?", default="",
                         help="Material name (default: 'forged_material')")
    p_forge.add_argument("--tuple", default="",
                         help="12-glyph IG tuple string")
    p_forge.add_argument("--from-catalog", default="",
                         help="Catalog entry name to forge from")
    p_forge.set_defaults(func=_cmd_forge)

    # ── metamaterial ──
    p_meta = sub.add_parser("metamaterial",
        help="Run Frobenius metamaterial simulation",
        description="FrobeniusMetamaterial — self-verifying material with μ∘δ=id.\n"
                    "Applies load cycles and measures healing recovery.\n"
                    "Frobenius norm → 0 means the material closes the loop.",
        epilog="Example:  rebis.materials metamaterial --size 32 --cycles 30",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_meta.add_argument("--size", type=int, default=20,
                        help="Grid size NxN (default: 20)")
    p_meta.add_argument("--cycles", type=int, default=20,
                        help="Load cycles (default: 20)")
    p_meta.add_argument("--heal-steps", type=int, default=10,
                        help="Heal steps per cycle (default: 10)")
    p_meta.set_defaults(func=_cmd_metamaterial)

    # ── critical ──
    p_crit = sub.add_parser("critical",
        help="Run critical metamaterial simulation",
        description="CriticalMetamaterial — ⊙-sensing material at the\n"
                    "critical point between order and chaos.\n"
                    "Computes susceptibility and runs time evolution.",
        epilog="Example:  rebis.materials critical --size 32 --kappa 0.3",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_crit.add_argument("--size", type=int, default=16,
                        help="Grid size (default: 16)")
    p_crit.add_argument("--kappa", type=float, default=0.2,
                        help="Initial kappa (default: 0.2)")
    p_crit.add_argument("--nonlinear", type=float, default=0.1,
                        help="Nonlinearity (default: 0.1)")
    p_crit.add_argument("--time", type=int, default=60,
                        help="Simulation time steps (default: 60)")
    p_crit.set_defaults(func=_cmd_critical)

    # ── alloy ──
    p_alloy = sub.add_parser("alloy",
        help="Run ouroboric alloy grain boundary analysis",
        description="TopologicalGrainBoundaryNetwork — models grain\n"
                    "boundaries as topological defects with integer winding.\n"
                    "Computes total winding and crack driving force.",
        epilog="Example:  rebis.materials alloy --n-grains 128",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_alloy.add_argument("--n-grains", type=int, default=64,
                         help="Number of grains (default: 64)")
    p_alloy.set_defaults(func=_cmd_alloy)

    # ── nonqubit ──
    p_nq = sub.add_parser("nonqubit",
        help="Run non-qubit quantum computing paradigm analysis",
        description="NonQubitQCParadigm — surveys all non-qubit QC paradigms,\n"
                    "computes primitive deltas, operculum analysis, and forge designs.",
        epilog="Example:  rebis.materials nonqubit",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_nq.set_defaults(func=_cmd_nonqubit)

    # ── sophick ──
    p_soph = sub.add_parser("sophick",
        help="Run Sophick forge",
        description="SophickForge — alchemical mercury-based material synthesis.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_soph.set_defaults(func=_cmd_sophick)

    # ── casimir ──
    p_cas = sub.add_parser("casimir",
        help="Run Casimir cavity ZPE design",
        description="CasimirCavityDesigner — designs zero-point energy\n"
                    "harvesting Casimir cavity structures.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_cas.add_argument("--target-gap", type=float, default=0.1,
                       help="Target cavity gap in µm (default: 0.1)")
    p_cas.set_defaults(func=_cmd_casimir)

    # ── molecule ──
    p_mol = sub.add_parser("molecule",
        help="Resolve molecule to SMILES and compute IG tuple",
        description="MoleculeMaterialBridge — resolve a molecule by SMILES,\n"
                    "CAS number, or name, then compute its IG material tuple.",
        epilog="Examples:  rebis.materials molecule CC(=O)O\n"
               "           rebis.materials molecule --cas 64-19-7\n"
               "           rebis.materials molecule --name aspirin",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_mol.add_argument("smiles", nargs="?", default="",
                       help="SMILES string")
    p_mol.add_argument("--cas", default="",
                       help="CAS registry number")
    p_mol.add_argument("--name", default="",
                       help="Common molecule name")
    p_mol.set_defaults(func=_cmd_molecule)

    # ── status ──
    p_stat = sub.add_parser("status",
        help="Show results and reports",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_stat.set_defaults(func=_cmd_status)

    # ── list / info ──
    p_ls = sub.add_parser("list",
        help="List all design tools",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ls.set_defaults(func=_cmd_list)

    p_inf = sub.add_parser("info",
        help="Show available tools (alias for list)",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_inf.set_defaults(func=_cmd_list)

    sub.add_parser("help",
        help="Show this help message",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    args = parse_with_file(parser)

    if not args.command or args.command == "help":
        parser.print_help()
        return 0

    if hasattr(args, 'func'):
        return args.func(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
