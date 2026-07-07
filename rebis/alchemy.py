"""
rebis.alchemy — Alchemical Treatise Bridge & Operations (ADVANCED v2)
══════════════════════════════════════════════════════════════════════
Full implementations of:
  - BasilValentineLadder: climb_to_stone, full_opus_report, climb_between
  - ZosimosEngine: analyze_structure, perform_stilling, compare_to_zosimos
  - RetrosyntheticStoneEngine: plan_synthesis, grand_sequence
  - GreenFireEngine: analyze_catalyst, screen_library, suggest_optimal_wavelength
  - AlchemicalThirdEngine: compute_binding, suggest_host_for_guest
  - ArtephiusDecoder: decode, decode_molecule, learn, history
  - TreatiseMapper: design_for_tier, design_for_treatise, taxonomy
  - AlchemicalOperations: list_operations, grand_sequence, trace_opus
  - AlchemicalBridge (unified): all of the above in one interface

Callable as a command:
  rebis.alchemy ladder [name|all]          — Basil Valentine ladder
  rebis.alchemy opus                       — Full opus report (12 operations)
  rebis.alchemy stilling <smiles>          — Zosimos stilling analysis
  rebis.alchemy structure <smiles>         — Structural alchemical analysis
  rebis.alchemy retrosynth <smiles>        — Retrosynthetic stone synthesis
  rebis.alchemy grand-seq <smiles>         — Grand alchemical sequence
  rebis.alchemy catalyst <smiles>          — Green fire catalyst analysis
  rebis.alchemy wavelength <smiles>        — Optimal photocatalytic wavelength
  rebis.alchemy screen <smiles>            — Screen catalyst library
  rebis.alchemy binding <host> <guest>     — Third engine binding computation
  rebis.alchemy host <guest>               — Suggest host for guest
  rebis.alchemy decode <text>              — Artephius cryptic decode
  rebis.alchemy decode-mol <smiles>        — Artephius molecule decode
  rebis.alchemy treatise [name]            — Treatise taxonomy / design
  rebis.alchemy operations                 — List 12 alchemical operations
  rebis.alchemy portico [tuple]            — Zosimos portico check
  rebis.alchemy list                       — List available tools
"""
import sys, importlib, argparse, json
from pathlib import Path
from rebis.file_input import parse_with_file

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "alchemical_bridge")]:
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

# --- Lazy imports ---
_lazy("AlchemicalThirdEngine", "alchemical_bridge.alchemical_third_engine")
_lazy("ArtephiusDecoder", "alchemical_bridge.artephius_decoder")
_lazy("BasilValentineLadder", "alchemical_bridge.basil_valentine_ladder")
_lazy("compute_ladder", "alchemical_bridge.basil_valentine_ladder")
_lazy("AlchemicalBridge", "alchemical_bridge.bridge")
_lazy("AlchemicalOperations", "alchemical_bridge.operations")
_lazy("GreenFireEngine", "alchemical_bridge.green_fire_engine")
_lazy("PhotocatalyticCycle", "alchemical_bridge.green_fire_engine")
_lazy("RetrosyntheticStone", "alchemical_bridge.retrosynthetic_stone_engine")
_lazy("RetrosyntheticStoneEngine", "alchemical_bridge.retrosynthetic_stone_engine")
_lazy("TreatiseMapper", "alchemical_bridge.treatise_map")
_lazy("ZosimosEngine", "alchemical_bridge.zosimos_engine")
_lazy("check_portico", "alchemical_bridge.zosimos_engine")

# --- Default structural tuples ---
_PRIMITIVE_ORDER = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]
_DEFAULT_SOURCE = {"Ð": "𐑛", "Þ": "𐑡", "Ř": "𐑩", "Φ": "𐑗", "ƒ": "𐑱", "Ç": "𐑺", "Γ": "𐑲", "ɢ": "𐑝", "⊙": "𐑢", "Ħ": "𐑓", "Σ": "𐑙", "Ω": "𐑷"}
# --- Key mapping: short names → Unicode primitive names ---
_KEY_MAP = {"D": "Ð", "T": "Þ", "R": "Ř", "P": "Φ", "F": "ƒ", "Ç": "Ç",
            "K": "Ç", "G": "Γ", "Gm": "ɢ", "Ph": "⊙", "H": "Ħ", "S": "Σ", "W": "Ω"}

def _smiles_to_tuple(smiles: str) -> dict:
    """Convert SMILES → IG tuple dict with Unicode keys."""
    try:
        import importlib
        m = importlib.import_module("scripts.omonad_bridge")
        short = m.smiles_to_molecule_type(smiles)
    except Exception:
        short = dict(_DEFAULT_SOURCE)
    return {_KEY_MAP.get(k, k): v for k, v in short.items()}

_DEFAULT_TARGET = {"Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹", "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑔", "ɢ": "𐑠", "⊙": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑭"}


def _parse_tuple_arg(tup_str, default=None):
    if not tup_str and default:
        return dict(default)
    if not tup_str:
        return dict(_DEFAULT_SOURCE)
    if len(tup_str) == 12:
        return {_PRIMITIVE_ORDER[i]: tup_str[i] for i in range(12)}
    parts = [p.strip() for p in tup_str.replace("⟨", "").replace("⟩", "").split(";")]
    if len(parts) == 12:
        return {_PRIMITIVE_ORDER[i]: parts[i] for i in range(12)}
    return dict(default or _DEFAULT_SOURCE)


def _json_or_str(obj):
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, default=str, ensure_ascii=False)
    if hasattr(obj, '__dict__'):
        try:
            return json.dumps(vars(obj), indent=2, default=str, ensure_ascii=False)
        except Exception:
            return str(obj)
    return str(obj)


def _try_call(obj, method_name, *args, **kwargs):
    """Safely call a method if it exists, return result or None."""
    if hasattr(obj, method_name):
        return getattr(obj, method_name)(*args, **kwargs)
    return None

# ═══════════════════════════════════════════════════════════════════
# Command handlers
# ═══════════════════════════════════════════════════════════════════

def _cmd_ladder(args):
    """Basil Valentine ladder — climb_to_stone or full climb_between."""
    name = args.name or "all"
    print(f"═ Basil Valentine Alchemical Ladder ═")
    print(f"  Operation: {name}")
    try:
        ladder = BasilValentineLadder()
        if name == "all":
            result = ladder.full_opus_report()
        elif name == "stone":
            result = ladder.climb_to_stone()
        elif len(name) == 12 and all(ord(c) > 127 for c in name):
            source = _parse_tuple_arg(name)
            result = ladder.climb_between(source, _DEFAULT_TARGET)
        else:
            result = ladder.key_info(name) if hasattr(ladder, 'key_info') else ladder.full_opus_report()
        print(_json_or_str(result))
    except Exception as e:
        import traceback
        print(f"Ladder failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_opus(args):
    """Full 12-operation opus report."""
    print("═ Full Alchemical Opus Report (12 Operations) ═")
    try:
        ladder = BasilValentineLadder()
        result = ladder.full_opus_report()
        print(_json_or_str(result))
    except Exception as e:
        print(f"Opus report failed: {e}")
        return 1
    return 0


def _cmd_stilling(args):
    """Zosimos stilling — perform_stilling on a molecule."""
    if not args.smiles:
        print("Error: SMILES string required.")
        return 1
    print(f"═ Zosimos Stilling ═")
    print(f"  Molecule: {args.smiles}")
    try:
        tuple_dict = _smiles_to_tuple(args.smiles)
        engine = ZosimosEngine()
        result = engine.perform_stilling(tuple_dict)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Stilling failed: {e}")
        return 1
    return 0


def _cmd_structure(args):
    """Zosimos structural analysis."""
    if not args.smiles:
        print("Error: SMILES string required.")
        return 1
    print(f"═ Alchemical Structural Analysis ═")
    print(f"  Molecule: {args.smiles}")
    try:
        tuple_dict = _smiles_to_tuple(args.smiles)
        engine = ZosimosEngine()
        result = engine.analyze_structure(args.smiles, tuple_dict)
        print(_json_or_str(result))
        # Also compare to zosimos
        try:
            comparison = engine.compare_to_zosimos(tuple_dict)
            print("\n─ Comparison to Zosimos ─")
            print(_json_or_str(comparison))
        except Exception:
            pass
    except Exception as e:
        print(f"Structural analysis failed: {e}")
        return 1
    return 0


def _cmd_retrosynth(args):
    """Retrosynthetic stone engine — plan synthesis."""
    if not args.smiles:
        print("Error: SMILES string required.")
        return 1
    print(f"═ Retrosynthetic Stone Synthesis ═")
    print(f"  Target: {args.smiles}")
    try:
        engine = RetrosyntheticStoneEngine()
        result = engine.plan_synthesis(args.smiles)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Retrosynthetic planning failed: {e}")
        return 1
    return 0


def _cmd_grand_seq(args):
    """Grand alchemical sequence for a molecule."""
    if not args.smiles:
        print("Error: SMILES string required.")
        return 1
    print(f"═ Grand Alchemical Sequence ═")
    print(f"  Target: {args.smiles}")
    try:
        engine = RetrosyntheticStoneEngine()
        result = engine.grand_sequence(args.smiles)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Grand sequence failed: {e}")
        return 1
    return 0


def _cmd_catalyst(args):
    """Green fire catalyst analysis."""
    if not args.smiles:
        print("Error: SMILES string required.")
        return 1
    print(f"═ Green Fire Catalyst Analysis ═")
    print(f"  Catalyst: {args.smiles}")
    try:
        engine = GreenFireEngine()
        result = engine.analyze_catalyst(args.smiles)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Catalyst analysis failed: {e}")
        return 1
    return 0


def _cmd_wavelength(args):
    """Suggest optimal photocatalytic wavelength."""
    if not args.smiles:
        print("Error: SMILES string required.")
        return 1
    print(f"═ Optimal Photocatalytic Wavelength ═")
    print(f"  Molecule: {args.smiles}")
    try:
        engine = GreenFireEngine()
        result = engine.suggest_optimal_wavelength(args.smiles)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Wavelength suggestion failed: {e}")
        return 1
    return 0


def _cmd_screen(args):
    """Screen catalyst library against a target."""
    if not args.smiles:
        print("Error: SMILES string required.")
        return 1
    print(f"═ Catalyst Library Screening ═")
    print(f"  Target: {args.smiles}")
    try:
        engine = GreenFireEngine()
        result = engine.screen_library(args.smiles)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Screening failed: {e}")
        return 1
    return 0


def _cmd_binding(args):
    """Alchemical Third Engine — compute host-guest binding."""
    if not args.host or not args.guest:
        print("Error: host and guest SMILES required.")
        return 1
    print(f"═ Third Engine Binding Computation ═")
    print(f"  Host: {args.host}")
    print(f"  Guest: {args.guest}")
    try:
        engine = AlchemicalThirdEngine()
        result = engine.compute_binding(args.host, args.guest)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Binding computation failed: {e}")
        return 1
    return 0


def _cmd_host(args):
    """Suggest host for a guest molecule."""
    if not args.guest:
        print("Error: guest SMILES required.")
        return 1
    print(f"═ Host Suggestion for Guest ═")
    print(f"  Guest: {args.guest}")
    try:
        engine = AlchemicalThirdEngine()
        result = engine.suggest_host_for_guest(args.guest)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Host suggestion failed: {e}")
        return 1
    return 0


def _cmd_decode(args):
    """Artephius cryptic text decode."""
    if not args.text:
        print("Error: text to decode required.")
        return 1
    print(f"═ Artephius Cryptic Decode ═")
    print(f"  Input: {args.text[:80]}{'...' if len(args.text) > 80 else ''}")
    try:
        decoder = ArtephiusDecoder()
        result = decoder.decode(args.text)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Decode failed: {e}")
        return 1
    return 0


def _cmd_decode_mol(args):
    """Artephius molecule decode."""
    if not args.smiles:
        print("Error: SMILES string required.")
        return 1
    print(f"═ Artephius Molecule Decode ═")
    print(f"  Molecule: {args.smiles}")
    try:
        decoder = ArtephiusDecoder()
        result = decoder.decode_molecule(args.smiles)
        print(_json_or_str(result))
    except Exception as e:
        print(f"Molecule decode failed: {e}")
        return 1
    return 0


def _cmd_treatise(args):
    """Treatise taxonomy / design for tier."""
    name = args.treatise or "all"
    print(f"═ Alchemical Treatise Map ═")
    print(f"  Treatise: {name}")
    try:
        mapper = TreatiseMapper()
        if name == "all":
            result = mapper.taxonomy() if hasattr(mapper, 'taxonomy') else mapper.all_treatise_names()
        elif name.startswith("--tier=") or args.tier:
            tier_name = args.tier if args.tier else name.split("=", 1)[1]
            result = mapper.design_for_tier(tier_name) if hasattr(mapper, 'design_for_tier') else {"error": "design_for_tier not available"}
        else:
            result = mapper.design_for_treatise(name) if hasattr(mapper, 'design_for_treatise') else {"error": "design_for_treatise not available"}
        print(_json_or_str(result))
    except Exception as e:
        print(f"Treatise mapping failed: {e}")
        return 1
    return 0


def _cmd_operations(args):
    """List 12 alchemical operations."""
    print("═ 12 Alchemical Operations ═")
    try:
        ops = AlchemicalOperations()
        result = ops.list_operations()
        print(_json_or_str(result))
        # Also show grand sequence
        try:
            grand = ops.grand_sequence()
            print("\n─ Grand Sequence ─")
            print(_json_or_str(grand))
        except Exception:
            pass
    except Exception as e:
        # Fallback: list from module-level
        try:
            from alchemical_bridge.operations import tuple_to_op, op_to_tuple
            ops_list = []
            for i in range(12):
                tup = _parse_tuple_arg(None)
                ordinals = list(tup.values())
                for j, v in enumerate(ordinals):
                    ordinals[j] = j
                ops_list.append({"index": i, "operation": tuple_to_op(i) if callable(tuple_to_op) else f"op_{i}"})
            print(_json_or_str({"operations": ops_list}))
        except Exception:
            print(f"Operations listing failed: {e}")
            return 1
    return 0


def _cmd_portico(args):
    """Zosimos portico consistency check."""
    tup_str = args.tuple_str if hasattr(args, 'tuple_str') and args.tuple_str else ""
    print("═ Zosimos Portico Check ═")
    try:
        tup = _parse_tuple_arg(tup_str, _DEFAULT_TARGET)
        result = check_portico(tup)
        print(_json_or_str(result))
        # Also get the portico speech
        try:
            engine = ZosimosEngine()
            speech = engine.the_portico_speaks() if hasattr(engine, 'the_portico_speaks') else None
            if speech:
                print("\n─ The Portico Speaks ─")
                print(_json_or_str(speech))
        except Exception:
            pass
    except Exception as e:
        print(f"Portico check failed: {e}")
        return 1
    return 0

def _cmd_list(args):
    """List available alchemy tools."""
    tools = {
        "ladder": "Basil Valentine ladder (climb_to_stone, full_opus_report, climb_between)",
        "opus": "Full 12-operation opus report",
        "stilling": "Zosimos stilling — perform_stilling(molecule)",
        "structure": "Structural alchemical analysis — analyze_structure + compare_to_zosimos",
        "retrosynth": "Retrosynthetic stone synthesis — plan_synthesis(target)",
        "grand-seq": "Grand alchemical sequence — grand_sequence(target)",
        "catalyst": "Green fire catalyst analysis — analyze_catalyst(smiles)",
        "wavelength": "Optimal photocatalytic wavelength — suggest_optimal_wavelength(smiles)",
        "screen": "Screen catalyst library — screen_library(target)",
        "binding": "Third engine binding — compute_binding(host, guest)",
        "host": "Suggest host for guest — suggest_host_for_guest(guest)",
        "decode": "Artephius cryptic text decode — decode(text)",
        "decode-mol": "Artephius molecule decode — decode_molecule(smiles)",
        "treatise": "Treatise taxonomy / design — taxonomy, design_for_tier, design_for_treatise",
        "operations": "List 12 alchemical operations + grand sequence",
        "portico": "Zosimos portico consistency check",
    }
    print("═ Alchemical Tools ═")
    for cmd, desc in tools.items():
        print(f"  {cmd:14s} — {desc}")
    print(_json_or_str({"tools": tools, "count": len(tools)}))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="rebis.alchemy",
        description="Alchemical Treatise Bridge & Operations (advanced v2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ladder
    p = sub.add_parser("ladder", help="Basil Valentine alchemical ladder")
    p.add_argument("name", nargs="?", default="all", help="Operation name, 'all', 'stone', or compact tuple")
    p.set_defaults(func=_cmd_ladder)

    # opus
    sub.add_parser("opus", help="Full 12-operation opus report").set_defaults(func=_cmd_opus)

    # stilling
    p = sub.add_parser("stilling", help="Zosimos stilling analysis")
    p.add_argument("smiles", nargs="?", help="Molecule SMILES")
    p.set_defaults(func=_cmd_stilling)

    # structure
    p = sub.add_parser("structure", help="Alchemical structural analysis")
    p.add_argument("smiles", nargs="?", help="Molecule SMILES")
    p.set_defaults(func=_cmd_structure)

    # retrosynth
    p = sub.add_parser("retrosynth", help="Retrosynthetic stone synthesis")
    p.add_argument("smiles", nargs="?", help="Target molecule SMILES")
    p.set_defaults(func=_cmd_retrosynth)

    # grand-seq
    p = sub.add_parser("grand-seq", help="Grand alchemical sequence")
    p.add_argument("smiles", nargs="?", help="Target molecule SMILES")
    p.set_defaults(func=_cmd_grand_seq)

    # catalyst
    p = sub.add_parser("catalyst", help="Green fire catalyst analysis")
    p.add_argument("smiles", nargs="?", help="Catalyst SMILES")
    p.set_defaults(func=_cmd_catalyst)

    # wavelength
    p = sub.add_parser("wavelength", help="Optimal photocatalytic wavelength")
    p.add_argument("smiles", nargs="?", help="Molecule SMILES")
    p.set_defaults(func=_cmd_wavelength)

    # screen
    p = sub.add_parser("screen", help="Screen catalyst library")
    p.add_argument("smiles", nargs="?", help="Target molecule SMILES")
    p.set_defaults(func=_cmd_screen)

    # binding
    p = sub.add_parser("binding", help="Third engine binding computation")
    p.add_argument("host", nargs="?", help="Host molecule SMILES")
    p.add_argument("guest", nargs="?", help="Guest molecule SMILES")
    p.set_defaults(func=_cmd_binding)

    # host
    p = sub.add_parser("host", help="Suggest host for guest")
    p.add_argument("guest", nargs="?", help="Guest molecule SMILES")
    p.set_defaults(func=_cmd_host)

    # decode
    p = sub.add_parser("decode", help="Artephius cryptic text decode")
    p.add_argument("text", nargs="?", help="Text to decode")
    p.set_defaults(func=_cmd_decode)

    # decode-mol
    p = sub.add_parser("decode-mol", help="Artephius molecule decode")
    p.add_argument("smiles", nargs="?", help="Molecule SMILES")
    p.set_defaults(func=_cmd_decode_mol)

    # treatise
    p = sub.add_parser("treatise", help="Treatise taxonomy / design")
    p.add_argument("treatise", nargs="?", default="all", help="Treatise name or 'all'")
    p.add_argument("--tier", default=None, help="Design for specific tier")
    p.set_defaults(func=_cmd_treatise)

    # operations
    sub.add_parser("operations", help="List 12 alchemical operations").set_defaults(func=_cmd_operations)

    # portico
    p = sub.add_parser("portico", help="Zosimos portico consistency check")
    p.add_argument("tuple_str", nargs="?", default="", help="Optional compact tuple string")
    p.set_defaults(func=_cmd_portico)

    # list
    sub.add_parser("list", help="List available tools").set_defaults(func=_cmd_list)

    # info (alias for list)
    sub.add_parser("info", help="Show available tools (alias for list)").set_defaults(func=_cmd_list)

    return parser


def main():
    """CLI: rebis.alchemy <command> [args]"""
    parser = build_parser()
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
