"""
rebis.alchemy — Alchemical Treatise Bridge & Operations
════════════════════════════════════════════════════════
Lazy-import bridge to alchemical_bridge/.

Callable as a command:
  rebis.alchemy list                — List available tools
  rebis.alchemy ladder <name>       — Compute Basil Valentine ladder
  rebis.alchemy map <treatise>      — Map treatise structure
  rebis.alchemy portico             — Check Zosimos portico
  rebis.alchemy info                — Show available tools
"""
import sys, importlib, argparse, json
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "alchemical_bridge")]:
    if p not in sys.path: sys.path.insert(0, p)
__all__ = []
def _lazy(name, module, attr=None):
    try: m = importlib.import_module(module); globals()[name] = getattr(m, attr or name); __all__.append(name)
    except Exception: pass

_lazy("AlchemicalThirdEngine", "alchemical_bridge.alchemical_third_engine")
_lazy("ArtephiusDecoder", "alchemical_bridge.artephius_decoder")
_lazy("BasilValentineLadder", "alchemical_bridge.basil_valentine_ladder")
_lazy("compute_ladder", "alchemical_bridge.basil_valentine_ladder")
_lazy("AlchemicalBridge", "alchemical_bridge.bridge")
_lazy("GreenFireEngine", "alchemical_bridge.green_fire_engine")
_lazy("PhotocatalyticCycle", "alchemical_bridge.green_fire_engine")
_lazy("AlchemicalOperation", "alchemical_bridge.operations")
_lazy("tuple_to_ordinals", "alchemical_bridge.operations")
_lazy("apply_operation", "alchemical_bridge.operations")
_lazy("AlchemicalOperator", "alchemical_bridge.operator")
_lazy("RetrosyntheticStone", "alchemical_bridge.retrosynthetic_stone_engine")
_lazy("RetrosyntheticStoneEngine", "alchemical_bridge.retrosynthetic_stone_engine")
_lazy("TreatiseMapper", "alchemical_bridge.treatise_map")
_lazy("ZosimosEngine", "alchemical_bridge.zosimos_engine")
_lazy("check_portico", "alchemical_bridge.zosimos_engine")


def _cmd_ladder(args):
    name = args.name
    print(f"Computing Basil Valentine ladder: {name}")
    try:
        result = compute_ladder(name)
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Ladder failed: {e}")
    return 0


def _cmd_map(args):
    treatise = args.treatise
    print(f"Mapping treatise: {treatise}")
    try:
        mapper = TreatiseMapper()
        result = mapper.map(treatise) if hasattr(mapper, 'map') else str(mapper)
        print(result[:2000])
    except Exception as e:
        print(f"Mapping failed: {e}")
    return 0


def _cmd_portico(args):
    print("Checking Zosimos portico...")
    try:
        result = check_portico()
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Portico check failed: {e}")
    return 0


def _cmd_list(args):
    print("rebis.alchemy — Exports:")
    for name in sorted(__all__):
        print(f"  {name}")
    return 0


def main():
    """CLI: rebis.alchemy <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.alchemy",
        description="rebis.alchemy — Alchemical Treatise Bridge & Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_lad = sub.add_parser("ladder",
        help="Compute Basil Valentine alchemical ladder",
        description="Compute the Basil Valentine alchemical operation ladder —\n"
                    "structural progression through the 12 alchemical operations\n"
                    "(calcination, dissolution, separation, conjunction, etc.)\n"
                    "mapped to IG primitive promotions.",
        epilog="Examples:  rebis.alchemy ladder\n"
               "           rebis.alchemy ladder all\n"
               "           rebis.alchemy ladder calcination",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_lad.add_argument("name", nargs="?", default="all",
                       help="Operation name or 'all' (default: all)")
    p_lad.set_defaults(func=_cmd_ladder)

    p_map = sub.add_parser("map",
        help="Map alchemical treatise structure",
        description="Map the structure of an alchemical treatise — extract\n"
                    "operations, phases, and correspondences as IG tuple sequences.",
        epilog="Examples:  rebis.alchemy map\n"
               "           rebis.alchemy map \"Emerald Tablet\"\n"
               "           rebis.alchemy map \"Mutus Liber\"",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_map.add_argument("treatise", nargs="?", default="Emerald Tablet",
                       help="Treatise name (default: 'Emerald Tablet')")
    p_map.set_defaults(func=_cmd_map)

    p_por = sub.add_parser("portico",
        help="Check Zosimos portico consistency",
        description="Verify the Zosimos portico — the structural bridge\n"
                    "between alchemical operations and IG primitives.",
        epilog="Example:  rebis.alchemy portico",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_por.set_defaults(func=_cmd_portico)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
        epilog="Example:  rebis.alchemy list",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ls.set_defaults(func=_cmd_list)

    p_inf = sub.add_parser("info",
        help="Show available tools (alias for list)",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_inf.set_defaults(func=_cmd_list)

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
