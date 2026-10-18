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
from rebis.file_input import parse_with_file
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "ch3mpiler"),
          str(_REBIS_ROOT / "rhr_p4rky")]:
    if p not in sys.path: sys.path.insert(0, p)

_EXPORTS = {'Ch3mpiler': ('rhr_p4rky.ch3mpiler_bridge', 'Ch3mpiler'), 'analyze': ('rhr_p4rky.ch3mpiler_bridge', 'analyze'), 'retrosynthesis': ('rhr_p4rky.ch3mpiler_bridge', 'retrosynthesis'), 'forward': ('rhr_p4rky.ch3mpiler_bridge', 'forward'), 'fg_info': ('rhr_p4rky.ch3mpiler_bridge', 'fg_info'), 'rxn_info': ('rhr_p4rky.ch3mpiler_bridge', 'rxn_info'), 'Ch3mpilerCore': ('ch3mpiler.compiler', 'Ch3mpiler'), 'CASResolver': ('ch3mpiler.compiler', 'CASResolver'), 'tensor_type': ('ch3mpiler.compiler', 'tensor_type'), 'join_type': ('ch3mpiler.compiler', 'join_type'), 'meet_type': ('ch3mpiler.compiler', 'meet_type'), 'bond_product_type': ('ch3mpiler.compiler', 'bond_product_type'), 'compose_molecule_type': ('ch3mpiler.compiler', 'compose_molecule_type'), 'get_molecule_type': ('ch3mpiler.compiler', 'get_molecule_type'), 'find_fgs': ('ch3mpiler.compiler', 'find_fgs'), 'find_fgs_from_smiles': ('ch3mpiler.compiler', 'find_fgs_from_smiles'), 'find_disconnections': ('ch3mpiler.compiler', 'find_disconnections'), 'fmt_tup': ('ch3mpiler.compiler', 'fmt_tup'), 'tup_dist': ('ch3mpiler.compiler', 'tup_dist'), 'tup_to_ords': ('ch3mpiler.compiler', 'tup_to_ords'), 'is_bond_compatible': ('ch3mpiler.compiler', 'is_bond_compatible'), 'print_retrosynthesis': ('ch3mpiler.compiler', 'print_retrosynthesis'), 'detect_functional_groups': ('ch3mpiler.fg_exhaustive', 'detect_functional_groups'), 'ScaffoldParser': ('ch3mpiler.scaffold_parser', 'ScaffoldParser'), 'resolve_name_to_smiles': ('ch3mpiler.scaffold_parser', 'resolve_name_to_smiles'), 'mol_to_cdxml': ('ch3mpiler.smiles_to_cdxml', 'mol_to_cdxml'), 'validate_cdxml': ('ch3mpiler.smiles_to_cdxml', 'validate_cdxml')}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, attribute = _EXPORTS[name]
    value = getattr(importlib.import_module(module), attribute)
    globals()[name] = value
    return value


def _cmd_forward(args):
    if not args.smiles:
        print("Error: SMILES string required.")
        print("Example:  rebis.ch3mpiler forward CC(=O)O")
        return 1
    try:
        result = __getattr__("forward")([args.smiles])
        print(json.dumps(result, indent=2, ensure_ascii=False) if isinstance(result, (dict, list)) else result)
        if isinstance(result, dict) and result.get("error"):
            return 1
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
        result = __getattr__("retrosynthesis")(args.smiles)
        print(json.dumps(result, indent=2, ensure_ascii=False) if isinstance(result, (dict, list)) else result)
        if isinstance(result, dict) and result.get("error"):
            return 1
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
        from ch3mpiler.smiles_to_cdxml import mol_to_cdxml
        from rdkit import Chem
        mol = Chem.MolFromSmiles(args.smiles)
        if mol is None:
            print(f'Invalid SMILES: {args.smiles}')
            return 1
        cdx = mol_to_cdxml(mol, name=args.smiles)
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
        result = __getattr__("analyze")(args.smiles)
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
