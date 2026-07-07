"""
rebis.serpentrod — Protein Design & Stratified Prediction
══════════════════════════════════════════════════════════
Lazy-import bridge to serpentrod/ + rhr_p4rky serpent.

Callable as a command:
  rebis.serpentrod list               — List available tools
  rebis.serpentrod predict <sequence> — Predict protein features
  rebis.serpentrod classify <sequence> — Classify module type
  rebis.serpentrod finger <sequence>  — Match protein fingerprint
  rebis.serpentrod info               — Show available tools
"""
import sys, importlib, argparse, json
from rebis.file_input import parse_with_file
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "serpentrod"), str(_REBIS_ROOT / "rhr_p4rky")]:
    if p not in sys.path: sys.path.insert(0, p)
__all__ = []
def _lazy(name, module, attr=None):
    try: m = importlib.import_module(module); globals()[name] = getattr(m, attr or name); __all__.append(name)
    except Exception: pass

_lazy("RollingProfile", "serpentrod.protein_v5")
_lazy("CleavageSite", "serpentrod.protein_v5")
_lazy("MatureProduct", "serpentrod.protein_v5")
_lazy("improved_signal_peptide_detection", "serpentrod.protein_v5")
_lazy("classify_module_rich", "serpentrod.protein_v5")
_lazy("match_fingerprint", "serpentrod.protein_v5")
_lazy("identify_fragment", "serpentrod.protein_v5")
_lazy("FINGERPRINTS", "serpentrod.protein_v5")
_lazy("ProteinStratifiedPredictor", "serpentrod.stratified_predictor")
_lazy("SerpentRod", "rhr_p4rky.serpent_rod")
_lazy("SerpentRodV2", "rhr_p4rky.serpent_rod_v2")


def _cmd_predict(args):
    if not args.sequence:
        print("Error: protein sequence required.")
        print("Example:  rebis.serpentrod predict MVSKGEELFTGVVPILVELDGDVNGHKFS")
        return 1
    print(f"Predicting features for sequence ({len(args.sequence)} aa)...")
    try:
        predictor = ProteinStratifiedPredictor()
        result = predictor.run_full_pipeline(sequence=args.sequence)
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Prediction failed: {e}")
    return 0


def _cmd_classify(args):
    if not args.sequence:
        print("Error: protein sequence required.")
        print("Example:  rebis.serpentrod classify MVSKGEELFTGVVPILVELDGDVNGHKFS")
        return 1
    try:
        result = classify_module_rich(args.sequence)
        print(result)
    except Exception as e:
        print(f"Classification failed: {e}")
    return 0


def _cmd_finger(args):
    if not args.sequence:
        print("Error: protein sequence required.")
        print("Example:  rebis.serpentrod finger MVSKGEELFTGVVPILVELDGDVNGHKFS")
        return 1
    try:
        # Build combined fingerprint list from FINGERPRINTS dict
        fingerprints = []
        for name, patterns in FINGERPRINTS.items():
            fingerprints.extend(patterns)
        matched = match_fingerprint(args.sequence, fingerprints)
        if matched:
            # Find which fingerprint matched
            for name, patterns in FINGERPRINTS.items():
                if match_fingerprint(args.sequence, patterns):
                    print(f"  ✓ Matched: {name}")
        else:
            print(f"  No fingerprint match — novel sequence")
        print(f"  Match result: {matched}")
    except Exception as e:
        print(f"Fingerprint match failed: {e}")
    return 0


def _cmd_list(args):
    print("rebis.serpentrod — Exports:")
    for name in sorted(__all__):
        print(f"  {name}")
    return 0


def main():
    """CLI: rebis.serpentrod <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.serpentrod",
        description="rebis.serpentrod — Protein Design & Stratified Prediction",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_pred = sub.add_parser("predict",
        help="Predict protein features from amino acid sequence",
        description="Predict protein structural features — secondary structure,\n"
                    "solvent accessibility, disordered regions, signal peptide,\n"
                    "transmembrane helices — via stratified rolling profiles.",
        epilog="Example:  rebis.serpentrod predict MVSKGEELFTGVVPILVELDGDVNGHKFS",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_pred.add_argument("sequence", nargs="?", default="",
                        help="Amino acid sequence (single-letter codes)")
    p_pred.set_defaults(func=_cmd_predict)

    p_cls = sub.add_parser("classify",
        help="Classify protein module type from sequence",
        description="Classify a protein sequence into its module type\n"
                    "(e.g. enzyme, receptor, transporter, structural)\n"
                    "using IG-guided stratified classification.",
        epilog="Example:  rebis.serpentrod classify MVSKGEELFTGVVPILVELDGDVNGHKFS",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_cls.add_argument("sequence", nargs="?", default="",
                       help="Amino acid sequence")
    p_cls.set_defaults(func=_cmd_classify)

    p_fin = sub.add_parser("finger",
        help="Match protein fingerprint from sequence",
        description="Match a protein sequence against the structural fingerprint\n"
                    "database — returns closest known protein family and\n"
                    "IG tuple distance.",
        epilog="Example:  rebis.serpentrod finger MVSKGEELFTGVVPILVELDGDVNGHKFS",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_fin.add_argument("sequence", nargs="?", default="",
                       help="Amino acid sequence")
    p_fin.set_defaults(func=_cmd_finger)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
        epilog="Example:  rebis.serpentrod list",
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
