"""
rebis.alchemy — Alchemical Treatise Bridge & Operations
════════════════════════════════════════════════════════
Lazy-import bridge to alchemical_bridge/.

Callable as a command:
  rebis.alchemy list                — List available tools
  rebis.alchemy ladder <name>       — Compute Basil Valentine ladder
  rebis.alchemy map <treatise>      — Map treatise structure
  rebis.alchemy portico [tuple]     — Check Zosimos portico
  rebis.alchemy info                — Show available tools
"""
import sys, importlib, argparse, json
from rebis.file_input import parse_with_file
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

# Default structural tuples
_PRIMITIVE_ORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]
_DEFAULT_SOURCE = {"Ð": "𐑛", "Þ": "𐑡", "Ř": "𐑩", "Φ": "𐑗", "ƒ": "𐑱", "Ç": "𐑺", "Γ": "𐑲", "ɢ": "𐑝", "⊙": "𐑢", "Ħ": "𐑓", "Σ": "𐑙", "Ω": "𐑷"}
_DEFAULT_TARGET = {"Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹", "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠", "⊙": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑭"}


def _parse_tuple_arg(tup_str, default=None):
    """Parse a tuple argument: either a compact glyph string or return default."""
    if not tup_str and default:
        return dict(default)
    if not tup_str:
        return dict(_DEFAULT_SOURCE)
    # Compact format: 12-char glyph string
    if len(tup_str) == 12:
        return {_PRIMITIVE_ORDER[i]: tup_str[i] for i in range(12)}
    # Try semicolon-separated format
    parts = [p.strip() for p in tup_str.replace("⟨", "").replace("⟩", "").split(";")]
    if len(parts) == 12:
        return {_PRIMITIVE_ORDER[i]: parts[i] for i in range(12)}
    # Unknown format — return default
    return dict(default or _DEFAULT_SOURCE)


def _cmd_ladder(args):
    name = args.name
    print(f"Computing Basil Valentine ladder: {name}")
    try:
        # If name is a compact tuple, use it as source; otherwise use defaults
        if len(name) == 12 and all(ord(c) > 127 for c in name):
            source = _parse_tuple_arg(name)
            target = _DEFAULT_TARGET
        elif name == "all":
            source = _DEFAULT_SOURCE
            target = _DEFAULT_TARGET
        else:
            # Named operation — use defaults
            source = _DEFAULT_SOURCE
            target = _DEFAULT_TARGET
        result = compute_ladder(source, target)
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
    tup_str = args.tuple_str if hasattr(args, 'tuple_str') and args.tuple_str else ""
    print("Checking Zosimos portico...")
    try:
        tup = _parse_tuple_arg(tup_str, _DEFAULT_TARGET)
        result = check_portico(tup)
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
                    "mapped to IG primitive promotions.\n"
                    "Pass 'all' for the full 12-step ladder from O₀ → O_∞.",
        epilog="Examples:  rebis.alchemy ladder\n"
               "           rebis.alchemy ladder all\n"
               "           rebis.alchemy ladder calcination",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_lad.add_argument("name", nargs="?", default="all",
                       help="Operation name, 'all', or compact tuple (default: all)")
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
                    "between alchemical operations and IG primitives.\n"
                    "Optionally pass a compact tuple string to check.",
        epilog="Examples:  rebis.alchemy portico\n"
               "           rebis.alchemy portico ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑙𐑭⟩",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_por.add_argument("tuple_str", nargs="?", default="",
                       help="Optional compact tuple string to check")
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
