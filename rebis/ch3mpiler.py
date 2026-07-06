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


def _cmd_forward(args):
    if not args.smiles:
        print("Error: SMILES string required.")
        print("Example:  rebis.ch3mpiler forward CC(=O)O")
        return 1
    try:
        result = forward(args.smiles)
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Forward synthesis failed: {e}")
        return 1
    return 0


def _cmd_retrosynth(args):
    if not args.smiles:
        print("Error: SMILES string required.")
        print("Example:  rebis.ch3mpiler retrosynth c1ccccc1")
        return 1
    try:
        result = retrosynthesis(args.smiles)
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Retrosynthesis failed: {e}")
        return 1
    return 0


def _cmd_fg(args):
    if not args.smiles:
        print("Error: SMILES string required.")
        print("Example:  rebis.ch3mpiler fg CC(=O)O")
        return 1
    try:
        import importlib, pathlib
        _fg_path = pathlib.Path(__file__).parent.parent / 'ch3mpiler' / 'fg_exhaustive.py'
        _spec = importlib.util.spec_from_file_location('fg_exhaustive', str(_fg_path))
        _fg_mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_fg_mod)
        fgs = _fg_mod.detect_functional_groups(args.smiles)
        for fg in fgs:
            print(f"  {fg}")
    except Exception as e:
        print(f"FG detection failed: {e}")
        return 1
    return 0


def _cmd_cdxml(args):
    if not args.smiles:
        print("Error: SMILES string required.")
        print("Example:  rebis.ch3mpiler cdxml CC(=O)O")
        return 1
    try:
        import importlib, pathlib
        _cdx_path = pathlib.Path(__file__).parent.parent / 'ch3mpiler' / 'smiles_to_cdxml.py'
        _cdx_spec = importlib.util.spec_from_file_location('smiles_to_cdxml', str(_cdx_path))
        _cdx_mod = importlib.util.module_from_spec(_cdx_spec)
        _cdx_spec.loader.exec_module(_cdx_mod)
        from rdkit import Chem
        mol = Chem.MolFromSmiles(args.smiles)
        if mol is None:
            print(f'Invalid SMILES: {args.smiles}')
            return 1
        cdx = _cdx_mod.mol_to_cdxml(mol)
        if args.smiles:
            cdx = cdx.replace('<s name="molecule"', f'<s name="{args.smiles}"')
        print(cdx)
    except Exception as e:
        print(f"CDXML conversion failed: {e}")
        return 1
    return 0


def _cmd_analyze(args):
    if not args.smiles:
        print("Error: SMILES string required.")
        print("Example:  rebis.ch3mpiler analyze CC(=O)O")
        return 1
    try:
        result = analyze(args.smiles)
        print(result)
    except Exception as e:
        print(f"Analysis failed: {e}")
        return 1
    return 0


def _cmd_list(args):
    print("rebis.ch3mpiler — Exports:")
    for name in sorted(__all__):
        print(f"  {name}")
    return 0


def main():
    """CLI: rebis.ch3mpiler <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.ch3mpiler",
        description="rebis.ch3mpiler — Molecular Compiler & Retrosynthesis",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    # ── forward ──
    p_fwd = sub.add_parser("forward",
        help="Forward synthesis from SMILES",
        description="Run forward molecular synthesis — compose a molecule from\n"
                    "its SMILES string and compute its structural IG tuple.",
        epilog="Example:  rebis.ch3mpiler forward CC(=O)O",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_fwd.add_argument("smiles", nargs="?", default="",
                       help="SMILES string (e.g. CC(=O)O for acetic acid)")
    p_fwd.set_defaults(func=_cmd_forward)

    # ── retrosynth ──
    p_ret = sub.add_parser("retrosynth",
        help="Retrosynthetic analysis from SMILES",
        description="Run retrosynthetic analysis — decompose a molecule into\n"
                    "functional groups, identify disconnection sites, and compute\n"
                    "synthetic accessibility via IG lattice operations.",
        epilog="Example:  rebis.ch3mpiler retrosynth c1ccccc1",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ret.add_argument("smiles", nargs="?", default="",
                       help="SMILES string (e.g. c1ccccc1 for benzene)")
    p_ret.set_defaults(func=_cmd_retrosynth)

    # ── fg ──
    p_fg = sub.add_parser("fg",
        help="Detect functional groups in SMILES",
        description="Detect all functional groups present in a molecule\n"
                    "by exhaustive pattern matching against known FG templates.",
        epilog="Example:  rebis.ch3mpiler fg CC(=O)O",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_fg.add_argument("smiles", nargs="?", default="",
                      help="SMILES string (e.g. CC(=O)O)")
    p_fg.set_defaults(func=_cmd_fg)

    # ── cdxml ──
    p_cdx = sub.add_parser("cdxml",
        help="Convert SMILES to CDXML format",
        description="Convert a SMILES string to ChemDraw CDXML format\n"
                    "for structural diagram rendering.",
        epilog="Example:  rebis.ch3mpiler cdxml CC(=O)O",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_cdx.add_argument("smiles", nargs="?", default="",
                       help="SMILES string")
    p_cdx.set_defaults(func=_cmd_cdxml)

    # ── analyze ──
    p_ana = sub.add_parser("analyze",
        help="Full molecular analysis (forward + retrosynth + FG)",
        description="Run complete molecular analysis — forward synthesis,\n"
                    "retrosynthetic decomposition, and functional group detection.",
        epilog="Example:  rebis.ch3mpiler analyze CC(=O)O",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ana.add_argument("smiles", nargs="?", default="",
                       help="SMILES string")
    p_ana.set_defaults(func=_cmd_analyze)

    # ── list ──
    p_list = sub.add_parser("list",
        help="List all exported symbols",
        description="List all symbols available via `rebis.ch3mpiler.<name>`.",
        epilog="Example:  rebis.ch3mpiler list",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_list.set_defaults(func=_cmd_list)

    # ── info (alias) ──
    p_info = sub.add_parser("info",
        help="Show available tools (alias for list)",
        epilog="Example:  rebis.ch3mpiler info",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_info.set_defaults(func=_cmd_list)

    # ── help ──
    sub.add_parser("help",
        help="Show this help message",
        epilog="Example:  rebis.ch3mpiler help",
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
