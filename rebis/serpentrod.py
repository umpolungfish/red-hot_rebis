"""
rebis.serpentrod — Protein Design & Stratified Prediction (ADVANCED v2)
══════════════════════════════════════════════════════════════════════
Full implementations of:
  - ProteinStratifiedPredictor: Full pipeline (signal peptide, cleavage, fragments)
  - EnhancedPredictorV5: POMC processing, monobasic cleavage, fragment classification
  - SerpentRod: RNA→protein folding with winding number + Frobenius closure
  - SerpentRodV2: Backbone model with energy minimization + contact prediction

Callable as a command:
  rebis.serpentrod predict <sequence> [--name NAME]
  rebis.serpentrod classify <sequence>
  rebis.serpentrod finger <sequence>
  rebis.serpentrod process <sequence> [--name NAME]
  rebis.serpentrod fold <rna> [--name NAME]
  rebis.serpentrod foldv2 <rna> [--name NAME]
  rebis.serpentrod spectrum <sequence>
  rebis.serpentrod list
"""
import sys, importlib, argparse, json
from pathlib import Path
from rebis.file_input import parse_with_file

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "serpentrod"),
          str(_REBIS_ROOT / "rhr_p4rky"), str(_REBIS_ROOT / "shared")]:
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

# protein_v5 — enhanced predictor
_lazy("RollingProfile", "serpentrod.protein_v5")
_lazy("CleavageSite", "serpentrod.protein_v5")
_lazy("MatureProduct", "serpentrod.protein_v5")
_lazy("ProcessingPrediction", "serpentrod.protein_v5")
_lazy("EnhancedPredictorV5", "serpentrod.protein_v5")
_lazy("improved_signal_peptide_detection", "serpentrod.protein_v5")
_lazy("classify_module_rich", "serpentrod.protein_v5")
_lazy("match_fingerprint", "serpentrod.protein_v5")
_lazy("identify_fragment", "serpentrod.protein_v5")
_lazy("FINGERPRINTS", "serpentrod.protein_v5")
_lazy("detect_monobasic_sites", "serpentrod.protein_v5")
_lazy("should_merge_fragments", "serpentrod.protein_v5")
_lazy("translate_dna", "serpentrod.protein_v5")
_lazy("reverse_translate", "serpentrod.protein_v5")

# stratified_predictor
_lazy("ProteinStratifiedPredictor", "serpentrod.stratified_predictor")
_lazy("classify_module", "serpentrod.stratified_predictor")
_lazy("predict_processing", "serpentrod.stratified_predictor")
_lazy("analyze_spectrum", "serpentrod.stratified_predictor")
_lazy("compare_spectra", "serpentrod.stratified_predictor")
_lazy("PRIMITIVE_MAP", "serpentrod.stratified_predictor")
_lazy("PRIMITIVE_ORDERS", "serpentrod.stratified_predictor")
_lazy("HYDROPATHY", "serpentrod.stratified_predictor")

# serpent_rod (v1 + v2)
_lazy("SerpentRod", "rhr_p4rky.serpent_rod")
_lazy("FoldedProtein", "rhr_p4rky.serpent_rod")
_lazy("SerpentRodV2", "rhr_p4rky.serpent_rod_v2")
_lazy("Gen2Result", "rhr_p4rky.serpent_rod_v2")
_lazy("frobenius_verified_v2", "rhr_p4rky.serpent_rod_v2")


def _json_or_str(obj):
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, default=str)
    if hasattr(obj, '__dict__'):
        try:
            return json.dumps(vars(obj), indent=2, default=str)
        except Exception:
            return str(obj)
    return str(obj)


def _cmd_predict(args):
    """Run full ProteinStratifiedPredictor pipeline."""
    if not args.sequence:
        print("Error: protein sequence required.")
        return 1
    name = args.name or "protein"
    print(f"═ Protein Prediction Pipeline ═")
    print(f"  Sequence: {args.sequence[:50]}{'...' if len(args.sequence) > 50 else ''}")
    print(f"  Length: {len(args.sequence)} aa | Name: {name}")
    try:
        from serpentrod.stratified_predictor import ProteinStratifiedPredictor
        predictor = ProteinStratifiedPredictor(sequence=args.sequence, name=name)
        result = predictor.run_full_pipeline()
        # Also generate narrative
        try:
            narrative = predictor.generate_narrative(result)
        except Exception:
            narrative = None
        try:
            json_report = predictor.generate_json_report(result)
        except Exception:
            json_report = None

        output = {
            "name": name,
            "sequence": args.sequence,
            "length": len(args.sequence),
            "pipeline_result": result if isinstance(result, (dict, list)) else str(result),
            "narrative": narrative if isinstance(narrative, str) else str(narrative) if narrative else None,
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Prediction failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_classify(args):
    """Classify protein module type."""
    if not args.sequence:
        print("Error: protein sequence required.")
        return 1
    print(f"═ Module Classification ═")
    print(f"  Length: {len(args.sequence)} aa")
    try:
        from serpentrod.protein_v5 import classify_module_rich
        result = classify_module_rich(args.sequence)
        print(_json_or_str(result))
    except Exception as e:
        # Fallback to basic classifier
        try:
            from serpentrod.stratified_predictor import classify_module
            result = classify_module(args.sequence)
            output = {"sequence_length": len(args.sequence), "module_type": result}
            print(_json_or_str(output))
        except Exception as e2:
            print(f"Classification failed: {e2}")
            return 1
    return 0


def _cmd_finger(args):
    """Match protein fingerprint."""
    if not args.sequence:
        print("Error: protein sequence required.")
        return 1
    print(f"═ Fingerprint Matching ═")
    try:
        from serpentrod.protein_v5 import FINGERPRINTS, match_fingerprint
        all_matches = []
        for fname, patterns in FINGERPRINTS.items():
            if match_fingerprint(args.sequence, patterns):
                all_matches.append(fname)
        output = {
            "sequence_length": len(args.sequence),
            "matched_fingerprints": all_matches,
            "n_matches": len(all_matches),
            "novel": len(all_matches) == 0,
        }
        if all_matches:
            print(f"  ✓ Matched: {', '.join(all_matches)}")
        else:
            print("  Novel sequence — no fingerprint match")
        print(_json_or_str(output))
    except Exception as e:
        print(f"Fingerprint match failed: {e}")
        return 1
    return 0


def _cmd_process(args):
    """Run EnhancedPredictorV5 — full protein processing prediction."""
    if not args.sequence:
        print("Error: protein sequence required.")
        return 1
    name = args.name or "protein"
    print(f"═ Enhanced Processing Prediction (v5) ═")
    print(f"  Sequence: {args.sequence[:50]}{'...' if len(args.sequence) > 50 else ''}")
    print(f"  Length: {len(args.sequence)} aa | Name: {name}")
    try:
        from serpentrod.protein_v5 import EnhancedPredictorV5
        predictor = EnhancedPredictorV5()
        result = predictor.predict(args.sequence, name=name)
        try:
            narrative = predictor.narrative(result) if hasattr(predictor, 'narrative') else None
        except Exception:
            narrative = None
        output = {
            "name": name,
            "length": len(args.sequence),
            "processing_result": result if isinstance(result, (dict, list)) else str(result),
            "narrative": narrative,
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Processing prediction failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_fold(args):
    """Run SerpentRod v1 — RNA→protein folding."""
    if not args.rna:
        print("Error: RNA sequence required.")
        return 1
    name = args.name or "serpent"
    print(f"═ SerpentRod Folding (v1) ═")
    print(f"  RNA: {args.rna[:50]}{'...' if len(args.rna) > 50 else ''}")
    print(f"  Length: {len(args.rna)} nt | Name: {name}")
    try:
        from rhr_p4rky.serpent_rod import SerpentRod
        sr = SerpentRod(rna_sequence=args.rna, name=name)
        result = sr.predict()
        report = sr.report()
        output = {
            "name": name,
            "rna": args.rna,
            "winding_number": result.winding_number if hasattr(result, 'winding_number') else None,
            "folded_report": report if isinstance(report, (dict, list)) else str(report),
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Folding failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_foldv2(args):
    """Run SerpentRodV2 — backbone model with energy."""
    if not args.rna:
        print("Error: RNA sequence required.")
        return 1
    name = args.name or "serpent_v2"
    print(f"═ SerpentRod Folding (v2 — backbone + energy) ═")
    print(f"  RNA: {args.rna[:50]}{'...' if len(args.rna) > 50 else ''}")
    print(f"  Length: {len(args.rna)} nt | Name: {name}")
    try:
        from rhr_p4rky.serpent_rod_v2 import SerpentRodV2
        sr = SerpentRodV2(rna_sequence=args.rna, name=name)
        result = sr.predict()
        output = {
            "name": name,
            "rna": args.rna,
            "result": result if isinstance(result, (dict, list)) else str(result),
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Folding v2 failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_spectrum(args):
    """Analyze primitive activation spectrum."""
    if not args.sequence:
        print("Error: protein sequence required.")
        return 1
    print(f"═ Primitive Activation Spectrum ═")
    print(f"  Length: {len(args.sequence)} aa")
    try:
        from serpentrod.stratified_predictor import analyze_spectrum, compare_spectra
        spectrum = analyze_spectrum(args.sequence)
        output = {
            "sequence": args.sequence,
            "length": len(args.sequence),
            "spectrum": spectrum if isinstance(spectrum, (dict, list)) else str(spectrum),
        }
        print(_json_or_str(output))
    except Exception as e:
        print(f"Spectrum analysis failed: {e}")
        return 1
    return 0

def _cmd_list(args):
    """List available serpent rod tools and capabilities."""
    tools = {
        "predict": "ProteinStratifiedPredictor — full pipeline (signal peptide, cleavage, fragments)",
        "classify": "Module type classification (rich + basic fallback)",
        "finger": "Fingerprint matching against known protein patterns",
        "process": "EnhancedPredictorV5 — POMC processing, monobasic cleavage, fragment classification",
        "fold": "SerpentRod v1 — RNA→protein folding with winding number",
        "foldv2": "SerpentRod v2 — backbone model with energy minimization",
        "spectrum": "Primitive activation spectrum analysis",
    }
    print("═ Serpent Rod Tools ═")
    for cmd, desc in tools.items():
        print(f"  {cmd:12s} — {desc}")
    print(_json_or_str({"tools": tools, "count": len(tools)}))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="rebis.serpentrod",
        description="Protein design & stratified prediction (advanced v2)",
    )
    sub = parser.add_subparsers(dest="command")

    # predict
    p = sub.add_parser("predict", help="Full stratified prediction pipeline")
    p.add_argument("sequence", nargs="?", help="Protein sequence (1-letter aa)")
    p.add_argument("--name", default=None, help="Protein name")
    p.set_defaults(func=_cmd_predict)

    # classify
    p = sub.add_parser("classify", help="Classify module type")
    p.add_argument("sequence", nargs="?", help="Protein sequence")
    p.set_defaults(func=_cmd_classify)

    # finger
    p = sub.add_parser("finger", help="Match protein fingerprint")
    p.add_argument("sequence", nargs="?", help="Protein sequence")
    p.set_defaults(func=_cmd_finger)

    # process
    p = sub.add_parser("process", help="Enhanced processing prediction (v5)")
    p.add_argument("sequence", nargs="?", help="Protein sequence")
    p.add_argument("--name", default=None, help="Protein name")
    p.set_defaults(func=_cmd_process)

    # fold
    p = sub.add_parser("fold", help="SerpentRod v1 RNA→protein folding")
    p.add_argument("rna", nargs="?", help="RNA sequence")
    p.add_argument("--name", default=None, help="Protein name")
    p.set_defaults(func=_cmd_fold)

    # foldv2
    p = sub.add_parser("foldv2", help="SerpentRod v2 backbone + energy")
    p.add_argument("rna", nargs="?", help="RNA sequence")
    p.add_argument("--name", default=None, help="Protein name")
    p.set_defaults(func=_cmd_foldv2)

    # spectrum
    p = sub.add_parser("spectrum", help="Primitive activation spectrum")
    p.add_argument("sequence", nargs="?", help="Protein sequence")
    p.set_defaults(func=_cmd_spectrum)

    # list
    sub.add_parser("list", help="List available tools").set_defaults(func=_cmd_list)

    return parser


def main():
    parser = build_parser()
    args = parse_with_file(parser)
    if not args.command:
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
