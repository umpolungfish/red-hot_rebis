"""
rebis.ch3mpiler — Molecular Compiler & Retrosynthesis
═══════════════════════════════════════════════════════
Lazy-import bridge to ch3mpiler + p4ra ch3mpiler_bridge.

Callable as a command:
  rebis.ch3mpiler forward <SMILES>    — Forward synthesis
  rebis.ch3mpiler retrosynth <SMILES> — Retrosynthetic analysis
  rebis.ch3mpiler fg <SMILES>         — Detect functional groups
  rebis.ch3mpiler cdxml <SMILES>      — Convert to CDXML
  rebis.ch3mpiler info                — Show available tools
  rebis.ch3mpiler list                — List exported symbols
"""

import sys, importlib, argparse, json
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "ch3mpiler"),
          str(_REBIS_ROOT / "rhr_p4rky")]:
    if p not in sys.path: sys.path.insert(0, p)

__all__ = []

def _lazy(name, module, attr=None):
    try:
        m = importlib.import_module(module)
        globals()[name] = getattr(m, attr or name)
        __all__.append(name)
    except Exception:
        pass

# p4ra bridge
_lazy("Ch3mpiler", "rhr_p4rky.ch3mpiler_bridge")
_lazy("analyze", "rhr_p4rky.ch3mpiler_bridge")
_lazy("retrosynthesis", "rhr_p4rky.ch3mpiler_bridge")
_lazy("forward", "rhr_p4rky.ch3mpiler_bridge")
_lazy("fg_info", "rhr_p4rky.ch3mpiler_bridge")
_lazy("rxn_info", "rhr_p4rky.ch3mpiler_bridge")

# Direct ch3mpiler
_lazy("Ch3mpilerCore", "ch3mpiler.compiler", "Ch3mpiler")
_lazy("CASResolver", "ch3mpiler.compiler")
_lazy("tensor_type", "ch3mpiler.compiler")
_lazy("join_type", "ch3mpiler.compiler")
_lazy("meet_type", "ch3mpiler.compiler")
_lazy("bond_product_type", "ch3mpiler.compiler")
_lazy("compose_molecule_type", "ch3mpiler.compiler")
_lazy("get_molecule_type", "ch3mpiler.compiler")
_lazy("find_fgs", "ch3mpiler.compiler")
_lazy("find_fgs_from_smiles", "ch3mpiler.compiler")
_lazy("find_disconnections", "ch3mpiler.compiler")
_lazy("fmt_tup", "ch3mpiler.compiler")
_lazy("tup_dist", "ch3mpiler.compiler")
_lazy("tup_to_ords", "ch3mpiler.compiler")
_lazy("is_bond_compatible", "ch3mpiler.compiler")
_lazy("print_retrosynthesis", "ch3mpiler.compiler")
_lazy("detect_functional_groups", "ch3mpiler.fg_exhaustive")
_lazy("parse_scaffold", "ch3mpiler.scaffold_parser")
_lazy("scaffold_library", "ch3mpiler.scaffold_parser")
_lazy("smiles_to_cdxml", "ch3mpiler.smiles_to_cdxml")
_lazy("smiles_to_cdxml_file", "ch3mpiler.smiles_to_cdxml")
_lazy("fix_cas_smiles", "ch3mpiler.cas_smiles_fix")
_lazy("validate_smiles", "ch3mpiler.cas_smiles_fix")


def main():
    """CLI: rebis.ch3mpiler <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.ch3mpiler — Molecular Compiler & Retrosynthesis",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: forward, retrosynth, fg, cdxml, info, list, help")
    parser.add_argument("smiles", nargs="?", default="",
                       help="SMILES string or compound name")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.ch3mpiler — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd == "forward":
        if not args.smiles:
            print("Usage: rebis.ch3mpiler forward <SMILES>")
            return 1
        try:
            result = forward(args.smiles)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Forward synthesis failed: {e}")
            return 1
        return 0

    if cmd in ("retrosynth", "retro", "retrosynthesis"):
        if not args.smiles:
            print("Usage: rebis.ch3mpiler retrosynth <SMILES>")
            return 1
        try:
            result = retrosynthesis(args.smiles)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Retrosynthesis failed: {e}")
            return 1
        return 0

    if cmd in ("fg", "functional-groups", "funcgroups"):
        if not args.smiles:
            print("Usage: rebis.ch3mpiler fg <SMILES>")
            return 1
        try:
            fgs = detect_functional_groups(args.smiles)
            for fg in fgs:
                print(f"  {fg}")
        except Exception as e:
            print(f"FG detection failed: {e}")
            return 1
        return 0

    if cmd in ("cdxml", "cdx"):
        if not args.smiles:
            print("Usage: rebis.ch3mpiler cdxml <SMILES>")
            return 1
        try:
            cdx = smiles_to_cdxml(args.smiles)
            print(cdx)
        except Exception as e:
            print(f"CDXML conversion failed: {e}")
            return 1
        return 0

    if cmd == "analyze":
        if not args.smiles:
            print("Usage: rebis.ch3mpiler analyze <SMILES>")
            return 1
        try:
            result = analyze(args.smiles)
            print(result)
        except Exception as e:
            print(f"Analysis failed: {e}")
            return 1
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())