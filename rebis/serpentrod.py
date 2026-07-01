"""
rebis.serpentrod — Protein Design & Stratified Prediction
══════════════════════════════════════════════════════════
Lazy-import bridge to serpentrod/ + rhr_p4rky serpent.

Callable as a command:
  rebis.serpentrod list              — List available tools
  rebis.serpentrod predict <seq>     — Predict protein features
  rebis.serpentrod classify <seq>    — Classify module type
  rebis.serpentrod finger <seq>      — Match protein fingerprint
  rebis.serpentrod info              — Show available tools
"""
import sys, importlib, argparse, json
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
_lazy("ProteinStratifiedPredictor", "serpentrod.stratified_predictor")
_lazy("SerpentRod", "rhr_p4rky.serpent_rod")
_lazy("SerpentRodV2", "rhr_p4rky.serpent_rod_v2")


def main():
    """CLI: rebis.serpentrod <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.serpentrod — Protein Design & Stratified Prediction",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: predict, classify, finger, list, info, help")
    parser.add_argument("seq", nargs="?", default="",
                       help="Protein sequence or fragment name")
    parser.add_argument("args", nargs="*", help="Additional arguments")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.serpentrod — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd in ("predict", "profile"):
        if not args.seq:
            print("Usage: rebis.serpentrod predict <sequence>")
            return 1
        print(f"Predicting features for sequence ({len(args.seq)} aa)...")
        try:
            predictor = ProteinStratifiedPredictor()
            result = predictor.predict(args.seq)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Prediction failed: {e}")
        return 0

    if cmd in ("classify", "class"):
        if not args.seq:
            print("Usage: rebis.serpentrod classify <sequence>")
            return 1
        try:
            result = classify_module_rich(args.seq)
            print(result)
        except Exception as e:
            print(f"Classification failed: {e}")
        return 0

    if cmd in ("finger", "fingerprint"):
        if not args.seq:
            print("Usage: rebis.serpentrod finger <sequence>")
            return 1
        try:
            result = match_fingerprint(args.seq)
            print(result)
        except Exception as e:
            print(f"Fingerprint match failed: {e}")
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())