"""
rebis.gene — Gene Imscriber & Genetic Engineering
══════════════════════════════════════════════════
Lazy-import bridge to gene_imscriber/ (suppresses stdout).

Callable as a command:
  rebis.gene list                  — List available tools
  rebis.gene analyze <seq>         — Analyze genetic sequence
  rebis.gene quality <seq>         — Compute genetic quality score
  rebis.gene tuples <seq>          — Compute genetic tuples
  rebis.gene info                  — Show available tools
"""
import sys, importlib, io, argparse, json
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


def main():
    """CLI: rebis.gene <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.gene — Gene Imscriber & Genetic Engineering",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: analyze, quality, tuples, list, info, help")
    parser.add_argument("seq", nargs="?", default="",
                       help="DNA/RNA sequence or gene name")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.gene — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd == "analyze":
        if not args.seq:
            print("Usage: rebis.gene analyze <sequence>")
            return 1
        print(f"Analyzing sequence ({len(args.seq)} bp)...")
        try:
            result = analyze_sequence(args.seq)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Analysis failed: {e}")
        return 0

    if cmd == "quality":
        if not args.seq:
            print("Usage: rebis.gene quality <sequence>")
            return 1
        try:
            score = compute_quality_score(args.seq)
            print(f"Quality score: {score}")
        except Exception as e:
            print(f"Quality computation failed: {e}")
        return 0

    if cmd == "tuples":
        if not args.seq:
            print("Usage: rebis.gene tuples <sequence>")
            return 1
        try:
            result = compute_genetic_tuples(args.seq)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Tuple computation failed: {e}")
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())