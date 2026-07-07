"""
rebis.biology — Biological Simulations & Telomere Design (ADVANCED v2)
══════════════════════════════════════════════════════════════════════
Full implementations of:
  - OuroboricCellSim: Frobenius-exact cell evolution (gen 0-500+)
  - TopologicalMorphogenesisSim: Reaction-diffusion tissue patterning
  - Telomere subsystem: Shelterin, ATM, EpigeneticDerepressor, hTERT, Telomerase, GQuadruplex

Callable as a command:
  rebis.biology sim [--generations 500] [--genome-size 531000] [--n-genes 50] ...
  rebis.biology morphogenesis [--steps 1200] [--grid-size 64] [--n-types 5]
  rebis.biology telomeres
  rebis.biology status
  rebis.biology list
"""
import sys, importlib, argparse, json, io
from pathlib import Path
from rebis.file_input import parse_with_file

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "biology"),
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

_lazy("OuroboricCellSim", "biology.biology_sim_frobenius_exact")
_lazy("TopologicalMorphogenesisSim", "biology.biology_sim_frobenius_exact")
_lazy("CellFate", "biology.ouroboric_telomere_expanded")
_lazy("EpigeneticPhase", "biology.ouroboric_telomere_expanded")
_lazy("TelomereState", "biology.ouroboric_telomere_expanded")
_lazy("EpigeneticState", "biology.ouroboric_telomere_expanded")
_lazy("ATMSignalingState", "biology.ouroboric_telomere_expanded")
_lazy("CellState", "biology.ouroboric_telomere_expanded")
_lazy("EndogenousParams", "biology.ouroboric_telomere_expanded")
_lazy("ShelterinSensor", "biology.ouroboric_telomere_expanded")
_lazy("ATMSignaling", "biology.ouroboric_telomere_expanded")
_lazy("EpigeneticDerepressor", "biology.ouroboric_telomere_expanded")
_lazy("hTERTExpression", "biology.ouroboric_telomere_expanded")
_lazy("TelomeraseExtension", "biology.ouroboric_telomere_expanded")
_lazy("GQuadruplexTerminator", "biology.ouroboric_telomere_expanded")


def _json_or_str(obj):
    """Serialize to JSON if possible, else str."""
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, default=str, ensure_ascii=False)
    if hasattr(obj, '__dict__'):
        try:
            return json.dumps(vars(obj), indent=2, default=str, ensure_ascii=False)
        except Exception:
            return str(obj)
    return str(obj)


def _cmd_sim(args):
    """Run OuroboricCellSim + TopologicalMorphogenesisSim."""
    generations = args.generations
    genome_size = args.genome_size
    n_genes = args.n_genes
    n_adaptive = args.n_adaptive
    morph_steps = args.morphogenesis_steps
    grid_size = args.grid_size

    output = {}

    # ── OuroboricCellSim ──
    print(f"═ Ouroboric Cell Simulation (Frobenius-exact v6) ═")
    print(f"  Genome: {genome_size:,} bp | Genes: {n_genes} | Adaptive loci: {n_adaptive}")
    print(f"  Generations: {generations}")
    try:
        from biology.biology_sim_frobenius_exact import OuroboricCellSim
        sim = OuroboricCellSim(
            genome_size_bp=genome_size,
            n_genes=n_genes,
            n_adaptive_loci=n_adaptive,
        )
        print("  Running evolution...")
        sim.run_evolution(generations=generations)
        summary = sim.summarize()
        output["ouroboric_cell_sim"] = {
            "genome_size_bp": genome_size,
            "n_genes": n_genes,
            "n_adaptive_loci": n_adaptive,
            "generations": generations,
            "final_generation": sim.generation,
            "environment_locked": sim.env_locked,
            "environment_signal": round(float(sim.environment_signal), 6),
            "recombinase_efficiency": sim.recombinase_efficiency,
            "editing_events": len(sim.editing_history),
            "summary": summary if isinstance(summary, (dict, list)) else str(summary),
        }
        print(f"  ✓ Evolution complete — {sim.generation} generations, "
              f"{len(sim.editing_history)} edits")
    except Exception as e:
        import traceback
        print(f"  Cell simulation failed: {e}")
        traceback.print_exc()
        output["ouroboric_cell_sim"] = {"error": str(e)}

    # ── TopologicalMorphogenesisSim ──
    print(f"\n═ Topological Morphogenesis (v4) ═")
    print(f"  Grid: {grid_size}×{grid_size} | Steps: {morph_steps}")
    try:
        from biology.biology_sim_frobenius_exact import TopologicalMorphogenesisSim
        morph = TopologicalMorphogenesisSim(grid_size=grid_size)
        print("  Running morphogenesis...")
        morph_result = morph.run(steps=morph_steps)
        # Compute fill fraction
        if hasattr(morph, 'grid'):
            import numpy as np
            total_cells = morph.grid.size
            occupied = int(np.count_nonzero(morph.grid))
            fill_frac = round(occupied / total_cells, 4)
        else:
            fill_frac = None
        output["topological_morphogenesis"] = {
            "grid_size": grid_size,
            "steps": morph_steps,
            "fill_fraction": fill_frac,
            "result": morph_result if isinstance(morph_result, (dict, list)) else str(morph_result),
        }
        if fill_frac is not None:
            print(f"  ✓ Morphogenesis complete — fill: {fill_frac:.1%}")
        else:
            print("  ✓ Morphogenesis complete")
    except Exception as e:
        import traceback
        print(f"  Morphogenesis failed: {e}")
        traceback.print_exc()
        output["topological_morphogenesis"] = {"error": str(e)}

    print()
    print(_json_or_str(output))
    return 0


def _cmd_morphogenesis(args):
    """Run only TopologicalMorphogenesisSim."""
    steps = args.steps
    grid_size = args.grid_size
    n_types = args.n_types
    print(f"═ Topological Morphogenesis (v4) ═")
    print(f"  Grid: {grid_size}×{grid_size} | Cell types: {n_types} | Steps: {steps}")
    try:
        from biology.biology_sim_frobenius_exact import TopologicalMorphogenesisSim
        morph = TopologicalMorphogenesisSim(grid_size=grid_size, n_cell_types=n_types)
        print("  Running...")
        result = morph.run(steps=steps)
        if hasattr(morph, 'grid'):
            import numpy as np
            occupied = int(np.count_nonzero(morph.grid))
            total = morph.grid.size
            fill = round(occupied / total, 4)
        else:
            fill = None
        output = {
            "grid_size": grid_size,
            "n_cell_types": n_types,
            "steps": steps,
            "fill_fraction": fill,
            "result": result if isinstance(result, (dict, list)) else str(result),
        }
        if fill is not None:
            print(f"  ✓ Fill: {fill:.1%}")
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Morphogenesis failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_telomeres(args):
    """Show full telomere subsystem state."""
    print("═ Telomere & Epigenetic State Analysis ═")
    output = {}
    try:
        from biology.ouroboric_telomere_expanded import (
            CellFate, EpigeneticPhase, TelomereState, EpigeneticState,
            ATMSignalingState, CellState, EndogenousParams,
            ShelterinSensor, ATMSignaling, EpigeneticDerepressor,
            hTERTExpression, TelomeraseExtension, GQuadruplexTerminator,
        )

        # Enumerations
        output["cell_fates"] = [f.name for f in CellFate]
        output["epigenetic_phases"] = [p.name for p in EpigeneticPhase]

        # Default parameters
        params = EndogenousParams()
        params_dict = {}
        if hasattr(params, '__dict__'):
            for k, v in vars(params).items():
                try:
                    params_dict[k] = float(v)
                except (ValueError, TypeError):
                    params_dict[k] = str(v)
        output["endogenous_params"] = params_dict

        # Initialize a baseline cell state
        telomere = TelomereState()
        epi = EpigeneticState()
        cell = CellState()

        # Shelterin sensor
        shelterin = ShelterinSensor(params)
        try:
            trf2_occ, pot1_occ = shelterin.compute_occupancy(telomere)
            below = shelterin.is_below_threshold(trf2_occ, pot1_occ)
            output["shelterin_sensor"] = {
                "trf2_occupancy": round(float(trf2_occ), 6),
                "pot1_occupancy": round(float(pot1_occ), 6),
                "below_threshold": bool(below),
            }
        except Exception as e:
            output["shelterin_sensor"] = {"error": str(e)}

        # ATM signaling
        atm = ATMSignaling(params)
        try:
            atm_state = atm.compute_signal(cell)
            atm_dict = {}
            if hasattr(atm_state, '__dict__'):
                for k, v in vars(atm_state).items():
                    try:
                        atm_dict[k] = float(v)
                    except (ValueError, TypeError):
                        atm_dict[k] = str(v)
            else:
                atm_dict = str(atm_state)
            output["atm_signaling"] = atm_dict
        except Exception as e:
            output["atm_signaling"] = {"error": str(e)}

        # Epigenetic derepressor
        derep = EpigeneticDerepressor(params)
        try:
            derep.step(cell, dt=1.0)
            derep_dict = {}
            if hasattr(cell, '__dict__'):
                for k, v in vars(cell).items():
                    try:
                        derep_dict[k] = float(v)
                    except (ValueError, TypeError):
                        try:
                            derep_dict[k] = str(v)
                        except:
                            derep_dict[k] = "<non-serializable>"
            output["epigenetic_derepressor"] = {
                "cell_state_after_step": derep_dict,
            }
        except Exception as e:
            output["epigenetic_derepressor"] = {"error": str(e)}

        # hTERT expression
        htert = hTERTExpression(params)
        try:
            expr_level = htert.compute_expression(cell)
            output["htert_expression"] = {
                "expression_level": round(float(expr_level), 6),
            }
        except Exception as e:
            output["htert_expression"] = {"error": str(e)}

        # Telomerase extension
        telomerase = TelomeraseExtension(params)
        try:
            extension = telomerase.extend(telomere, htert_level=0.5)
            output["telomerase_extension"] = {
                "bp_extended": int(extension) if isinstance(extension, (int, float)) else str(extension),
            }
        except Exception as e:
            output["telomerase_extension"] = {"error": str(e)}

        # G-Quadruplex terminator
        gquad = GQuadruplexTerminator()
        gquad_methods = [m for m in dir(gquad) if not m.startswith('_')]
        output["g_quadruplex_terminator"] = {
            "available_methods": gquad_methods,
        }

        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Telomere analysis failed: {e}")
        traceback.print_exc()
        return 1
    return 0

def _cmd_status(args):
    """Show simulation results and reports."""
    bio_dir = _REBIS_ROOT / "biology"
    results = list(bio_dir.glob("*.json")) + list(bio_dir.glob("*.md"))
    if results:
        print("Biology results:")
        for r in results:
            print(f"  {r.name} ({r.stat().st_size:,d} bytes)")
    else:
        print("No results files found in biology/")
    return 0


def _cmd_list(args):
    print("rebis.biology — Exports:")
    for name in sorted(__all__):
        obj = globals().get(name)
        status = "✓" if obj is not None else "✗"
        print(f"  {status} {name}")
    print("\nCommands:")
    print("  sim            — OuroboricCellSim + TopologicalMorphogenesisSim")
    print("  morphogenesis  — TopologicalMorphogenesisSim only")
    print("  telomeres      — Full telomere subsystem (Shelterin, ATM, hTERT, ...)")
    print("  status         — Show result files")
    print("  list           — List exports")
    return 0


def main():
    """CLI: rebis.biology <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.biology",
        description="rebis.biology — Biological Simulations & Telomere Design",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    # ── sim ──
    p_sim = sub.add_parser("sim",
        help="Run OuroboricCellSim + TopologicalMorphogenesisSim",
        description="Run BOTH simulations:\n"
                    "  1. OuroboricCellSim — Frobenius-exact cell evolution\n"
                    "     (genome adaptation, environment locking, fitness)\n"
                    "  2. TopologicalMorphogenesisSim — reaction-diffusion\n"
                    "     tissue patterning (Wnt source, deterministic colonization)",
        epilog="Example:  rebis.biology sim --generations 300 --grid-size 32",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_sim.add_argument("--generations", type=int, default=500,
                       help="Evolution generations (default: 500)")
    p_sim.add_argument("--genome-size", type=int, default=531000,
                       help="Genome size in bp (default: 531000)")
    p_sim.add_argument("--n-genes", type=int, default=50,
                       help="Number of genes (default: 50)")
    p_sim.add_argument("--n-adaptive", type=int, default=20,
                       help="Adaptive loci (default: 20)")
    p_sim.add_argument("--morphogenesis-steps", type=int, default=1200,
                       help="Morphogenesis steps (default: 1200)")
    p_sim.add_argument("--grid-size", type=int, default=64,
                       help="Morphogenesis grid size (default: 64)")
    p_sim.set_defaults(func=_cmd_sim)

    # ── morphogenesis ──
    p_mor = sub.add_parser("morphogenesis",
        help="Run TopologicalMorphogenesisSim only",
        description="Run the reaction-diffusion tissue patterning simulation.\n"
                    "Models Wnt-source maturation and deterministic colonization\n"
                    "with proven 100% fill.",
        epilog="Example:  rebis.biology morphogenesis --steps 600 --grid-size 32",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_mor.add_argument("--steps", type=int, default=1200,
                       help="Number of steps (default: 1200)")
    p_mor.add_argument("--grid-size", type=int, default=64,
                       help="Grid size NxN (default: 64)")
    p_mor.add_argument("--n-types", type=int, default=5,
                       help="Number of cell types (default: 5)")
    p_mor.set_defaults(func=_cmd_morphogenesis)

    # ── telomeres ──
    p_tel = sub.add_parser("telomeres",
        help="Show full telomere subsystem state",
        description="Display computed values from all telomere subsystems:\n"
                    "  ShelterinSensor (TRF2/POT1 occupancy)\n"
                    "  ATMSignaling (damage response)\n"
                    "  EpigeneticDerepressor (passive dilution)\n"
                    "  hTERTExpression (telomerase reverse transcriptase)\n"
                    "  TelomeraseExtension (bp added)\n"
                    "  GQuadruplexTerminator (termination machinery)",
        epilog="Example:  rebis.biology telomeres",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_tel.set_defaults(func=_cmd_telomeres)

    # ── status ──
    p_stat = sub.add_parser("status",
        help="Show simulation results and reports",
        description="List all result files (JSON, Markdown) in the biology/\n"
                    "output directory with file sizes.",
        epilog="Example:  rebis.biology status",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_stat.set_defaults(func=_cmd_status)

    # ── list / info ──
    p_ls = sub.add_parser("list",
        help="List all exported symbols",
        epilog="Example:  rebis.biology list",
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
