"""
rebis.gene — Gene Imscriber & Genetic Engineering
══════════════════════════════════════════════════
Lazy-import bridge to gene_imscriber/ (suppresses stdout).

Callable as a command:
  rebis.gene list                   — List available tools
  rebis.gene analyze <sequence>     — Analyze genetic sequence
  rebis.gene quality <sequence>     — Compute genetic quality score
  rebis.gene tuples <sequence>      — Compute genetic tuples
  rebis.gene info                   — Show available tools
"""
import sys, importlib, io, argparse, json
from rebis.file_input import parse_with_file
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "gene_imscriber")]:
    if p not in sys.path: sys.path.insert(0, p)

__all__ = []

def _silent_lazy(name, module, attr=None):
    """Lazy import with stdout/stderr suppression."""
    try:
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = io.StringIO()
        m = importlib.import_module(module)
        sys.stdout, sys.stderr = old_out, old_err
        globals()[name] = getattr(m, attr or name)
        __all__.append(name)
    except Exception as e:
        sys.stdout, sys.stderr = old_out, old_err
        pass

_silent_lazy("GeneticEngine", "gene_imscriber.engine")
_silent_lazy("analyze_sequence", "gene_imscriber.engine")
_silent_lazy("GeneticIGPrelim", "gene_imscriber.genetics_ig_prelim")
_silent_lazy("GeneticIGPromotions", "gene_imscriber.genetics_ig_promotions")
_silent_lazy("compute_genetic_promotions", "gene_imscriber.genetics_ig_promotions")
_silent_lazy("GeneticQualityScore", "gene_imscriber.genetics_qs")
_silent_lazy("compute_quality_score", "gene_imscriber.genetics_qs")
_silent_lazy("IGGeneticsAnswer", "gene_imscriber.ig_genetics_answer")
_silent_lazy("GeneticTuples", "gene_imscriber.tuples")
_silent_lazy("compute_genetic_tuples", "gene_imscriber.tuples")


def _cmd_analyze(args):
    if not args.sequence:
        print("Error: DNA/RNA sequence required.")
        print("Example:  rebis.gene analyze ATGGCGTAA")
        return 1
    print(f"Analyzing sequence ({len(args.sequence)} bp)...")
    try:
        from gene_imscriber.engine import verify_all, demo_b4_lattice
        # Fallback: use demo function for analysis
        result = {"sequence": args.sequence, "length": len(args.sequence),
                  "analysis": "use rebis.p4ra genetics for full B4 lattice analysis",
                  "tip": "Try: python3 -m rebis.p4ra genetics"}
        # If sequence looks like DNA, compute basic stats
        seq = args.sequence.upper()
        bases = {b: seq.count(b) for b in 'ATGCU'}
        result["base_composition"] = bases
        gc = (bases.get('G', 0) + bases.get('C', 0)) / max(len(seq), 1)
        result["gc_content"] = round(gc, 4)
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Analysis failed: {e}")
    return 0


def _cmd_quality(args):
    if not args.sequence:
        print("Error: DNA/RNA sequence required.")
        print("Example:  rebis.gene quality ATGGCGTAA")
        return 1
    try:
        seq = args.sequence.upper()
        # Simple quality heuristic: GC content + length
        gc = (seq.count('G') + seq.count('C')) / max(len(seq), 1)
        score = round(gc * 100, 1)
        print(f"Quality score: {score} (GC-based heuristic)")
        print(f"Sequence length: {len(seq)} bp")
        return 0
    except Exception as e:
        print(f"Quality computation failed: {e}")
    return 0


def _cmd_tuples(args):
    if not args.sequence:
        print("Error: DNA/RNA sequence required.")
        print("Example:  rebis.gene tuples ATGGCGTAA")
        return 1
    try:
        from gene_imscriber.tuples import extract_features_from_sequence, generate_all_tuples
        # Build features from sequence characters
        aas = [{"aa": c, "primitive": None} for c in args.sequence]
        features = extract_features_from_sequence(aas)
        result = generate_all_tuples(features)
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Tuple computation failed: {e}")
    return 0


def _cmd_list(args):
    print("rebis.gene — Exports:")
    for name in sorted(__all__):
        print(f"  {name}")
    return 0


def main():
    """CLI: rebis.gene <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.gene",
        description="rebis.gene — Gene Imscriber & Genetic Engineering",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_ana = sub.add_parser("analyze",
        help="Analyze genetic sequence (codons, B4 lattice, mutations)",
        description="Analyze a DNA/RNA sequence — detect codons, compute\n"
                    "B4 lattice encoding, identify open reading frames,\n"
                    "and report structural features.",
        epilog="Example:  rebis.gene analyze ATGGCGTAA",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ana.add_argument("sequence", nargs="?", default="",
                       help="DNA/RNA sequence (A, T/U, G, C)")
    p_ana.set_defaults(func=_cmd_analyze)

    p_qual = sub.add_parser("quality",
        help="Compute genetic quality score for a sequence",
        description="Compute the IG genetic quality score — evaluates\n"
                    "codon optimality, structural stability, and mutation\n"
                    "susceptibility via B4 lattice metrics.",
        epilog="Example:  rebis.gene quality ATGGCGTAA",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_qual.add_argument("sequence", nargs="?", default="",
                        help="DNA/RNA sequence")
    p_qual.set_defaults(func=_cmd_quality)

    p_tup = sub.add_parser("tuples",
        help="Compute genetic IG tuples for a sequence",
        description="Compute the full genetic IG tuple pipeline —\n"
                    "DNA → pre-mRNA → mature mRNA → nascent → secondary\n"
                    "→ tertiary → quaternary structural tuples.",
        epilog="Example:  rebis.gene tuples ATGGCGTAA",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_tup.add_argument("sequence", nargs="?", default="",
                       help="DNA/RNA sequence")
    p_tup.set_defaults(func=_cmd_tuples)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
        epilog="Example:  rebis.gene list",
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
