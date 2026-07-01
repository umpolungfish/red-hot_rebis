"""
rebis.alchemy — Alchemical Treatise Bridge & Operations
════════════════════════════════════════════════════════
Lazy-import bridge to alchemical_bridge/.

Callable as a command:
  rebis.alchemy list               — List available tools
  rebis.alchemy ladder <name>      — Compute Basil Valentine ladder
  rebis.alchemy map <treatise>     — Map treatise structure
  rebis.alchemy info               — Show available tools
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


def main():
    """CLI: rebis.alchemy <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.alchemy — Alchemical Treatise Bridge & Operations",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: ladder, map, list, info, help")
    parser.add_argument("args", nargs="*", help="Arguments")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.alchemy — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd in ("ladder", "basil"):
        name = args.args[0] if args.args else "all"
        print(f"Computing Basil Valentine ladder: {name}")
        try:
            result = compute_ladder(name)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Ladder failed: {e}")
        return 0

    if cmd == "map":
        treatise = args.args[0] if args.args else "Emerald Tablet"
        print(f"Mapping treatise: {treatise}")
        try:
            mapper = TreatiseMapper()
            result = mapper.map(treatise) if hasattr(mapper, 'map') else str(mapper)
            print(result[:2000])
        except Exception as e:
            print(f"Mapping failed: {e}")
        return 0

    if cmd == "portico":
        print("Checking Zosimos portico...")
        try:
            result = check_portico()
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Portico check failed: {e}")
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())