"""
rebis.clink — CLINK Chain & Organism Pipeline (ADVANCED v2)
══════════════════════════════════════════════════════════════
Full implementations of:
  - CLINK layers L0–L8 with tier and C-score
  - Structural algebra (meet, join, tensor, distance)
  - Component bridges (protein, molecule, gene → CLINK)
  - Integrated promotion paths
  - Pipeline engine (design, analyze, verify)
  - DFT bridge (energy estimates)

Callable as a command:
  rebis.clink layers
  rebis.clink chain <name-or-tuple>
  rebis.clink cscore <name-or-tuple>
  rebis.clink bridge [--protein] [--molecule] [--gene]
  rebis.clink algebra <a> <b> [--op meet|join|tensor|distance]
  rebis.clink integrate <component> <layer>
  rebis.clink energy [--layer N]
  rebis.clink list
"""
import sys, importlib, argparse, json
from pathlib import Path
from rebis.file_input import parse_with_file

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "clink"),
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

# chain
_lazy("compute_tier_from_tuple", "clink.chain")
_lazy("compute_c_score_from_tuple", "clink.chain")
_lazy("clink_frobenius_closed", "clink.chain")
_lazy("clink_layer_index", "clink.chain")
_lazy("clink_layer_tuple", "clink.chain")
_lazy("clink_distance", "clink.chain")
_lazy("primitive_deltas", "clink.chain")
_lazy("primitive_mismatch_count", "clink.chain")
_lazy("verify_all_frobenius_closed", "clink.chain")
_lazy("clink_chain_distance", "clink.chain")
_lazy("format_tuple_glyphs", "clink.chain")

# bridges
_lazy("BridgeResult", "clink.bridges")
_lazy("protein_to_clink", "clink.bridges")
_lazy("molecule_to_clink", "clink.bridges")
_lazy("gene_to_clink", "clink.bridges")
_lazy("bridge_all_components", "clink.bridges")

# integration
_lazy("IntegratedCLINKResult", "clink.integration")
_lazy("verify_clink_integration", "clink.integration")
_lazy("integrated_promotion_path", "clink.integration")
_lazy("clink_to_serpentrod", "clink.integration")
_lazy("clink_to_ch3mpiler", "clink.integration")
_lazy("clink_to_gene", "clink.integration")
_lazy("full_report", "clink.integration")

# pipeline_engine
_lazy("PipelineMode", "clink.pipeline_engine")
_lazy("EntryMode", "clink.pipeline_engine")
_lazy("DesignSpec", "clink.pipeline_engine")
_lazy("TransitionResult", "clink.pipeline_engine")
_lazy("PipelineResult", "clink.pipeline_engine")

# structural_algebra
_lazy("meet", "clink.structural_algebra")
_lazy("join", "clink.structural_algebra")
_lazy("tensor", "clink.structural_algebra")
_lazy("structural_distance", "clink.structural_algebra")
_lazy("ordinal", "clink.structural_algebra")
_lazy("compute_all_algebra", "clink.structural_algebra")
_lazy("clink_chain_table", "clink.structural_algebra")

# designers
_lazy("LayerDesigner", "clink.designers.designer_base")
_lazy("DesignSpec", "clink.designers.designer_base")
_lazy("TransitionResult", "clink.designers.designer_base")
_lazy("ToolForge", "clink.designers.designer_base")
_lazy("compute_promotions", "clink.designers.designer_base")
_lazy("bridge_structural", "clink.designers.designer_base")

_lazy("Layer0Designer", "clink.designers.layer_designers")
_lazy("design_layer", "clink.designers.layer_designers")

_lazy("DFTBridge", "clink.designers.dft_bridge")
_lazy("DFTEngine", "clink.designers.dft_bridge")
_lazy("detect_available_engines", "clink.designers.dft_bridge")
_lazy("compute_full_energy_ladder", "clink.designers.dft_bridge")
_lazy("energy_ladder_summary", "clink.designers.dft_bridge")
_lazy("estimate_small_molecule_energy", "clink.designers.dft_bridge")

_lazy("PipelineOrchestrator", "clink.designers.pipeline_orchestrator")


def _json_or_str(obj):
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, default=str, ensure_ascii=False)
    if hasattr(obj, '__dict__'):
        try:
            return json.dumps(vars(obj), indent=2, default=str, ensure_ascii=False)
        except Exception:
            return str(obj)
    return str(obj)


def _parse_tuple_input(tup_str):
    """Parse a compact 12-glyph tuple string or a named system."""
    if not tup_str:
        return None
    if len(tup_str) == 12 and all(ord(c) > 127 for c in tup_str):
        try:
            from clink.chain import PORDER
            return {PORDER[i]: tup_str[i] for i in range(12)}
        except Exception:
            return None
    return tup_str  # return as-is for name lookup


def _cmd_layers(args):
    """List CLINK layers L0–L8 with tier and C-score."""
    print("═ CLINK Layers (L0–L8) ═")
    try:
        from clink.chain import clink_layer_tuple, compute_tier_from_tuple, compute_c_score_from_tuple, clink_distance
        layers = []
        for i in range(9):
            tup = clink_layer_tuple(i)
            tier = compute_tier_from_tuple(tup)
            cscore = compute_c_score_from_tuple(tup)
            dist_to_l8 = clink_distance(i, 8) if i < 8 else 0.0
            tup_str = ''.join(tup.values()) if isinstance(tup, dict) else str(tup)
            print(f"  L{i}: ⟨{tup_str}⟩  tier={tier}  C={cscore:.4f}  d(L8)={dist_to_l8:.4f}")
            layers.append({
                "layer": i,
                "tuple": tup_str,
                "tier": tier,
                "c_score": round(float(cscore), 4),
                "distance_to_L8": round(float(dist_to_l8), 4),
            })
        print()
        print(_json_or_str(layers))
    except Exception as e:
        import traceback
        print(f"Layers failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_chain(args):
    """Compute CLINK chain from tuple or name."""
    if not args.tuple_name:
        print("Error: tuple name or compact glyph string required.")
        print("Example:  rebis.clink chain my_system")
        print("          rebis.clink chain 𐑼𐑡𐑩𐑗𐑱𐑺𐑲𐑝𐑢𐑓𐑙𐑷")
        return 1
    try:
        from clink.chain import clink_layer_tuple, clink_distance, clink_layer_index, compute_tier_from_tuple, compute_c_score_from_tuple
        tup_input = _parse_tuple_input(args.tuple_name)

        if isinstance(tup_input, dict):
            # Compact tuple
            tup = tup_input
            tier = compute_tier_from_tuple(tup)
            cscore = compute_c_score_from_tuple(tup)
            tup_str = ''.join(tup.values())
            result = {
                "input": args.tuple_name,
                "tuple": tup_str,
                "tier": tier,
                "c_score": round(float(cscore), 4),
            }
        else:
            # Named lookup
            try:
                idx = clink_layer_index(args.tuple_name)
                tup = clink_layer_tuple(idx)
                tier = compute_tier_from_tuple(tup)
                cscore = compute_c_score_from_tuple(tup)
                dist = clink_distance(idx, 8)
                tup_str = ''.join(tup.values()) if isinstance(tup, dict) else str(tup)
                result = {
                    "input": args.tuple_name,
                    "layer_index": idx,
                    "tuple": tup_str,
                    "tier": tier,
                    "c_score": round(float(cscore), 4),
                    "distance_to_L8": round(float(dist), 4),
                }
            except (KeyError, ValueError, TypeError):
                result = {"input": args.tuple_name, "error": "Could not resolve as layer name or tuple"}

        # Full chain distance
        try:
            chain_dist = clink_chain_distance()
            result["total_chain_distance"] = round(float(chain_dist), 4)
        except Exception:
            pass

        # Verify Frobenius closure
        try:
            frob_closed = clink_frobenius_closed(args.tuple_name)
            result["frobenius_closed"] = bool(frob_closed)
        except Exception:
            pass

        print(_json_or_str(result))
    except Exception as e:
        import traceback
        print(f"Chain failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_cscore(args):
    """Compute consciousness score from tuple or name."""
    if not args.tuple_name:
        print("Error: tuple name or compact glyph string required.")
        return 1
    try:
        from clink.chain import compute_c_score_from_tuple, compute_tier_from_tuple
        tup_input = _parse_tuple_input(args.tuple_name)

        if isinstance(tup_input, dict):
            tup = tup_input
        else:
            from clink.chain import clink_layer_tuple
            try:
                tup = clink_layer_tuple(args.tuple_name)
            except (KeyError, ValueError):
                tup = {"⊙": "⊙", "Ç": "𐑧", "Ħ": "𐑫"}

        cscore = compute_c_score_from_tuple(tup)
        tier = compute_tier_from_tuple(tup)
        tup_str = ''.join(tup.values()) if isinstance(tup, dict) else str(tup)
        output = {
            "input": args.tuple_name,
            "tuple": tup_str,
            "c_score": round(float(cscore), 6),
            "tier": tier,
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"C-score failed: {e}")
        traceback.print_exc()
        return 1
    return 0

def _cmd_bridge(args):
    """Compute bridges between components (protein, molecule, gene)."""
    print("═ CLINK Component Bridges ═")
    output = {"components": args.components}
    try:
        from clink.bridges import (
            protein_to_clink, molecule_to_clink, gene_to_clink,
            bridge_all_components, BridgeResult)

        if args.protein:
            print("  Bridging protein → CLINK...")
            result = protein_to_clink()
            output["protein_bridge"] = _json_or_str(result) if not isinstance(result, (dict, list)) else result

        if args.molecule:
            print("  Bridging molecule → CLINK...")
            result = molecule_to_clink()
            output["molecule_bridge"] = _json_or_str(result) if not isinstance(result, (dict, list)) else result

        if args.gene:
            print("  Bridging gene → CLINK...")
            result = gene_to_clink()
            output["gene_bridge"] = _json_or_str(result) if not isinstance(result, (dict, list)) else result

        if not (args.protein or args.molecule or args.gene):
            print("  Bridging ALL components...")
            result = bridge_all_components()
            output["all_bridges"] = result if isinstance(result, (dict, list)) else str(result)

        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Bridge failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_algebra(args):
    """Run structural algebra operations (meet, join, tensor, distance)."""
    a = args.a
    b = args.b
    op = args.op
    print(f"═ Structural Algebra: {op}({a}, {b}) ═")
    try:
        from clink.structural_algebra import meet, join, tensor, structural_distance

        tup_a = _parse_tuple_input(a)
        tup_b = _parse_tuple_input(b)

        if not isinstance(tup_a, dict) or not isinstance(tup_b, dict):
            print("  Error: both arguments must be 12-glyph compact tuple strings.")
            print("  Example: rebis.clink algebra 𐑼𐑡𐑩𐑗𐑱𐑺𐑲𐑝𐑢𐑓𐑙𐑷 𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑫𐑳𐑭 --op distance")
            return 1

        if op == "meet":
            result = meet(tup_a, tup_b)
            print(f"  meet = {''.join(result.values()) if isinstance(result, dict) else result}")
        elif op == "join":
            result = join(tup_a, tup_b)
            print(f"  join = {''.join(result.values()) if isinstance(result, dict) else result}")
        elif op == "tensor":
            result = tensor(tup_a, tup_b)
            print(f"  tensor = {''.join(result.values()) if isinstance(result, dict) else result}")
        elif op == "distance":
            result = structural_distance(tup_a, tup_b)
            print(f"  distance = {result}")

        output = {
            "a": a,
            "b": b,
            "op": op,
            "result": result if isinstance(result, (dict, list, int, float)) else str(result),
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Algebra failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_integrate(args):
    """Compute integrated promotion path from component to CLINK layer."""
    component = args.component
    layer = args.layer
    print(f"═ Integrated Promotion Path ═")
    print(f"  Component: {component} → Layer: L{layer}")
    try:
        from clink.integration import (
            integrated_promotion_path, verify_clink_integration,
            clink_to_serpentrod, clink_to_ch3mpiler, clink_to_gene,
            full_report)

        # Promotion path
        print("  Computing promotion path...")
        path = integrated_promotion_path(component, layer)
        print(f"  Path: {path}")

        # Verify integration
        print("  Verifying CLINK integration...")
        verification = verify_clink_integration()
        print(f"  Integration verified: {verification}")

        output = {
            "component": component,
            "target_layer": layer,
            "promotion_path": path if isinstance(path, (dict, list)) else str(path),
            "integration_verified": verification if isinstance(verification, (dict, list, bool)) else str(verification),
        }

        # Component-specific bridge
        if component == "serpentrod":
            result = clink_to_serpentrod(layer)
            output["serpentrod_bridge"] = result if isinstance(result, (dict, list)) else str(result)
        elif component == "ch3mpiler":
            result = clink_to_ch3mpiler(layer)
            output["ch3mpiler_bridge"] = result if isinstance(result, (dict, list)) else str(result)
        elif component == "gene":
            result = clink_to_gene(layer)
            output["gene_bridge"] = result if isinstance(result, (dict, list)) else str(result)

        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Integration failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_energy(args):
    """Compute DFT energy ladder for CLINK layers."""
    print("═ DFT Energy Ladder ═")
    try:
        from clink.designers.dft_bridge import (
            compute_full_energy_ladder, energy_ladder_summary,
            detect_available_engines, DFTEngine)

        if args.layer is not None:
            from clink.designers.dft_bridge import compute_layer_energy_profile
            print(f"  Computing energy profile for layer L{args.layer}...")
            profile = compute_layer_energy_profile(args.layer)
            output = {
                "layer": args.layer,
                "energy_profile": profile if isinstance(profile, (dict, list)) else str(profile),
            }
        else:
            print("  Detecting available DFT engines...")
            engines = detect_available_engines()
            print(f"  Available: {[e.name for e in engines] if engines else 'none'}")

            print("  Computing full energy ladder (L0→L8)...")
            ladder = compute_full_energy_ladder()

            print("  Generating summary...")
            summary = energy_ladder_summary(ladder)

            output = {
                "available_engines": [e.name for e in engines] if engines else [],
                "energy_ladder": ladder if isinstance(ladder, (dict, list)) else str(ladder),
                "summary": str(summary)[:2000],
            }

        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Energy computation failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_list(args):
    print("rebis.clink — Exports:")
    for name in sorted(__all__):
        obj = globals().get(name)
        status = "✓" if obj is not None else "✗"
        print(f"  {status} {name}")
    print("\nCommands:")
    print("  layers                    — List CLINK L0–L8 with tier/C-score")
    print("  chain <name|tuple>        — CLINK chain analysis")
    print("  cscore <name|tuple>       — Consciousness score")
    print("  bridge [--protein] [--molecule] [--gene] — Component bridges")
    print("  algebra <a> <b> --op OP   — meet/join/tensor/distance")
    print("  integrate <component> <layer> — Promotion path")
    print("  energy [--layer N]        — DFT energy ladder")
    print("  list                      — List exports")
    return 0


def main():
    """CLI: rebis.clink <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.clink",
        description="rebis.clink — CLINK Chain & Organism Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_lay = sub.add_parser("layers",
        help="List CLINK layers L0–L8 with tier and C-score",
        description="Display all 9 CLINK layers (L0 through L8)\n"
                    "with structural tuple, ouroboricity tier,\n"
                    "consciousness score, and distance to L8.",
        epilog="Example:  rebis.clink layers",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_lay.set_defaults(func=_cmd_layers)

    p_ch = sub.add_parser("chain",
        help="Compute CLINK chain from tuple or name",
        description="Analyze a structural tuple or named system in the\n"
                    "CLINK chain — compute layer index, tier, C-score,\n"
                    "distance to L8, and Frobenius closure status.",
        epilog="Examples:  rebis.clink chain human_consciousness\n"
               "           rebis.clink chain 𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑫𐑳𐑭",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ch.add_argument("tuple_name", nargs="?", default="",
                      help="Named system or 12-glyph tuple string")
    p_ch.set_defaults(func=_cmd_chain)

    p_cs = sub.add_parser("cscore",
        help="Compute consciousness score from tuple or name",
        description="Compute the IG consciousness score (0-1) for a\n"
                    "structural tuple or named CLINK layer.",
        epilog="Example:  rebis.clink cscore human_consciousness",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_cs.add_argument("tuple_name", nargs="?", default="",
                      help="Named system or 12-glyph tuple string")
    p_cs.set_defaults(func=_cmd_cscore)

    p_br = sub.add_parser("bridge",
        help="Compute bridges between components",
        description="Compute structural bridges from protein, molecule,\n"
                    "or gene components to the CLINK chain. Run with no\n"
                    "flags to bridge all components simultaneously.",
        epilog="Examples:  rebis.clink bridge\n"
               "           rebis.clink bridge --protein --molecule",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_br.add_argument("components", nargs="*", default=[],
                      help="Components to bridge (optional)")
    p_br.add_argument("--protein", action="store_true",
                      help="Bridge protein → CLINK")
    p_br.add_argument("--molecule", action="store_true",
                      help="Bridge molecule → CLINK")
    p_br.add_argument("--gene", action="store_true",
                      help="Bridge gene → CLINK")
    p_br.set_defaults(func=_cmd_bridge)

    p_alg = sub.add_parser("algebra",
        help="Run structural algebra (meet/join/tensor/distance)",
        description="Apply lattice operations on two structural tuples:\n"
                    "  meet     — greatest lower bound (shared floor)\n"
                    "  join     — least upper bound (minimal ceiling)\n"
                    "  tensor   — composite type\n"
                    "  distance — weighted Euclidean distance",
        epilog="Example:  rebis.clink algebra 𐑼𐑡𐑩𐑗𐑱𐑺𐑲𐑝𐑢𐑓𐑙𐑷 𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑫𐑳𐑭 --op distance",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_alg.add_argument("a", nargs="?", default="",
                       help="First tuple (12-glyph string)")
    p_alg.add_argument("b", nargs="?", default="",
                       help="Second tuple (12-glyph string)")
    p_alg.add_argument("--op", choices=["meet", "join", "tensor", "distance"],
                       default="distance", help="Operation (default: distance)")
    p_alg.set_defaults(func=_cmd_algebra)

    p_int = sub.add_parser("integrate",
        help="Compute integrated promotion path",
        description="Compute the integrated promotion path from a component\n"
                    "(serpentrod, ch3mpiler, gene) to a target CLINK layer.\n"
                    "Verifies CLINK integration and generates bridges.",
        epilog="Example:  rebis.clink integrate serpentrod 4",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_int.add_argument("component", nargs="?", default="serpentrod",
                        help="Component name (serpentrod|ch3mpiler|gene)")
    p_int.add_argument("layer", nargs="?", type=int, default=4,
                       help="Target CLINK layer (default: 4)")
    p_int.set_defaults(func=_cmd_integrate)

    p_eng = sub.add_parser("energy",
        help="Compute DFT energy ladder",
        description="Compute the DFT energy profile across CLINK layers.\n"
                    "Detects available DFT engines and estimates energies\n"
                    "for structural transitions.",
        epilog="Examples:  rebis.clink energy\n"
               "           rebis.clink energy --layer 3",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_eng.add_argument("--layer", type=int, default=None,
                       help="Compute energy for a specific layer (default: all)")
    p_eng.set_defaults(func=_cmd_energy)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
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
