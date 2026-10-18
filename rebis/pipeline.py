"""
rebis.pipeline — Imscription Pipeline & Frobenius Verification (ADVANCED v2)
════════════════════════════════════════════════════════════════════════════
Full implementations of:
  - Frobenius verification (identity_phase, bootstrap_compiler)
  - AutoImscriber (auto-imscription generation)
  - ImscriptionDesignAgent (LLM-driven design iteration)
  - ReactionPipeline (retrosynthetic analysis)
  - therapy_to_pdb (full therapy→PDB pipeline)
  - LiftPipeline (prose lift)

Callable as a command:
  rebis.pipeline verify [--source PATH]
  rebis.pipeline imscribe <name> [--description DESC]
  rebis.pipeline retro <smiles> [--depth 6]
  rebis.pipeline therapy <key> [--skip-ch3mpile] [--skip-serpentrod]
  rebis.pipeline therapy-all [--skip-ch3mpile] [--skip-serpentrod]
  rebis.pipeline lift <filepath>
  rebis.pipeline list
"""
import sys, importlib, argparse, json, ast
from pathlib import Path
from rebis.file_input import parse_with_file

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "pipeline"),
          str(_REBIS_ROOT / "shared")]:
    if p not in sys.path:
        sys.path.insert(0, p)

_EXPORTS = {'AutoImscriber': 'pipeline.auto_imscriber', 'identity_phase': 'pipeline.frob', 'bootstrap_compiler': 'pipeline.frob', 'VINIT': 'pipeline.frob', 'TANCH': 'pipeline.frob', 'AREV': 'pipeline.frob', 'AFWD': 'pipeline.frob', 'FFUSE': 'pipeline.frob', 'CLINK': 'pipeline.frob', 'IFIX': 'pipeline.frob', 'ISCRIB': 'pipeline.frob', 'EVALT': 'pipeline.frob', 'EVALF': 'pipeline.frob', 'ImscriptionDesignAgent': 'pipeline.imscribe_agent', 'IGTool': 'pipeline.imscribe_tool', 'ToolResponse': 'pipeline.imscribe_tool', 'ReactionPipeline': 'pipeline.reaction_pipeline', 'RetrosyntheticNode': 'pipeline.reaction_pipeline', 'PipelineReport': 'pipeline.therapy_to_pdb', 'run_pipeline': 'pipeline.therapy_to_pdb', 'run_all_therapies': 'pipeline.therapy_to_pdb', 'generate_summary_report': 'pipeline.therapy_to_pdb', 'stage_load': 'pipeline.therapy_to_pdb', 'stage_analyze': 'pipeline.therapy_to_pdb', 'stage_ch3mpile': 'pipeline.therapy_to_pdb', 'stage_serpentrod': 'pipeline.therapy_to_pdb', 'stage_pdb_validate': 'pipeline.therapy_to_pdb', 'stage_frobenius': 'pipeline.therapy_to_pdb', 'LiftPipelineOb3ect': 'pipeline.lift_pipeline.lift_pipeline_ob3ect'}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value


def _json_or_str(obj):
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, default=str, ensure_ascii=False)
    if hasattr(obj, '__dict__'):
        try:
            return json.dumps(vars(obj), indent=2, default=str, ensure_ascii=False)
        except Exception:
            return str(obj)
    return str(obj)


def _cmd_verify(args):
    """Run Frobenius verification — identity_phase + bootstrap_compiler."""
    print("═ Frobenius Verification (μ∘δ=id) ═")
    from pipeline import frob
    filepath = args.source or frob.__file__
    try:
        from pipeline.frob import identity_phase, bootstrap_compiler, VINIT, TANCH, AREV, AFWD, FFUSE, CLINK, IFIX, EVALT, EVALF
        print(f"  Source: {filepath}")

        # AREV reads a path and returns the source; every operator below takes
        # the source text, not the path.
        source = AREV(filepath)
        print("  [1] Semantic identity phase (AST → source → AST)...")
        identity_ok = identity_phase(source)
        print(f"      {'✓ PASS' if identity_ok else '✗ FAIL'}")

        # Phase 2: IMASM bootstrap sequence
        print("  [2] IMASM bootstrap sequence:")
        vinit_result = VINIT()
        print(f"      VINIT: {vinit_result}")
        tanch_result = TANCH(source)
        print(f"      TANCH: {'✓' if tanch_result else '✗'}")
        arev_result = source
        print(f"      AREV: {arev_result[:60]}...")
        afwd_result = AFWD(tanch_result) if tanch_result else None
        print(f"      AFWD: {'✓' if afwd_result else '✗'}")
        ffuse_result = FFUSE(tanch_result, source) if tanch_result else None
        print(f"      FFUSE: {'✓' if ffuse_result else '✗'}")
        # Exercise file emission on a local copy, preserving the input source.
        import tempfile
        work_root = _REBIS_ROOT / "measurements" / "script_review"
        work_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="verify-", dir=work_root) as work:
            emitted = Path(work) / "emitted.py"
            CLINK(source, str(emitted))
            written = emitted.read_text(encoding="utf-8")
            clink_ok = ast.dump(ast.parse(written)) == ast.dump(ast.parse(source))
            print(f"      CLINK: {'✓' if clink_ok else '✗'}")
            IFIX(str(emitted))
        print("      IFIX: ✓")

        # Phase 3: Bootstrap compiler
        print("  [3] Bootstrap compiler...")
        bootstrap_result = bootstrap_compiler(filepath)
        print(f"      {'✓ PASS' if bootstrap_result else '✗ FAIL'}")

        output = {
            "source": filepath,
            "identity_phase": identity_ok,
            "bootstrap_compiler": bootstrap_result,
            "imasm_sequence": {
                "VINIT": str(vinit_result)[:200],
                "TANCH": bool(tanch_result),
                "AREV": str(arev_result)[:200],
                "AFWD": bool(afwd_result),
                "FFUSE": bool(ffuse_result),
                "CLINK": clink_ok,
                "IFIX": True,
            },
            "frobenius_closed": bool(identity_ok and ffuse_result and clink_ok and bootstrap_result),
        }
        print()
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Verification failed: {e}")
        traceback.print_exc()
        return 1
    return int(not output["frobenius_closed"])


def _cmd_imscribe(args):
    """Run auto-imscription."""
    name = args.name
    desc = args.description or f"Auto-imscribed system: {name}"
    print(f"═ Auto-Imscription ═")
    print(f"  Name: {name}")
    print(f"  Description: {desc}")
    try:
        from pipeline.auto_imscriber import AutoImscriber
        imscriber = AutoImscriber(desc)
        result = imscriber.generate() if hasattr(imscriber, 'generate') else str(imscriber)
        print(_json_or_str(result))
    except Exception as e:
        import traceback
        print(f"Imscription failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_retro(args):
    """Run retrosynthetic analysis via ReactionPipeline."""
    smiles = args.smiles
    depth = args.depth
    if not smiles or depth < 0:
        print("A target SMILES and nonnegative depth are required.")
        return 1
    print(f"═ Retrosynthetic Analysis ═")
    print(f"  Target SMILES: {smiles}")
    print(f"  Max depth: {depth}")
    try:
        from pipeline.reaction_pipeline import ReactionPipeline
        pipeline = ReactionPipeline(max_depth=depth)
        pipeline._target_smiles = smiles
        result = pipeline.deep_retrosynthesis(smiles)
        pipeline.print_tree(result)
    except Exception as e:
        import traceback
        print(f"Retrosynthesis failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _report_failed(report):
    """Inspect stage execution status without collapsing scientific readings."""
    stages = report.stages
    return not stages or any(
        getattr(stage.status, "value", stage.status) in ("failed", "pending", "running")
        or bool(stage.errors) for stage in stages)


def _cmd_therapy(args):
    """Run therapy→PDB pipeline for a single therapy."""
    key = args.key
    print(f"═ Therapy → PDB Pipeline ═")
    print(f"  Therapy key: {key}")
    try:
        from pipeline.therapy_to_pdb import run_pipeline
        report = run_pipeline(
            key,
            skip_ch3mpile=args.skip_ch3mpile,
            skip_serpentrod=args.skip_serpentrod,
        )
        output = {
            "therapy_key": key,
            "skip_ch3mpile": args.skip_ch3mpile,
            "skip_serpentrod": args.skip_serpentrod,
            "report": report.summary() if hasattr(report, 'summary') else str(report),
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Therapy pipeline failed: {e}")
        traceback.print_exc()
        return 1
    return int(_report_failed(report))


def _cmd_therapy_all(args):
    """Run therapy→PDB pipeline for ALL therapies."""
    print(f"═ All Therapies → PDB Pipeline ═")
    try:
        from pipeline.therapy_to_pdb import run_all_therapies, generate_summary_report, THERAPIES
        print("  Running all therapies (this may take a while)...")
        reports = run_all_therapies(
            skip_ch3mpile=args.skip_ch3mpile,
            skip_serpentrod=args.skip_serpentrod,
        )
        summary = generate_summary_report(reports)
        print(_json_or_str(summary))
    except Exception as e:
        import traceback
        print(f"Therapy pipeline failed: {e}")
        traceback.print_exc()
        return 1
    return int(not reports or len(reports) != len(THERAPIES)
               or {r.therapy_key for r in reports} != set(THERAPIES)
               or any(_report_failed(report) for report in reports))


def _cmd_lift(args):
    """Run prose lift pipeline."""
    if not args.filepath:
        print("Error: file path required.")
        print("Example:  rebis.pipeline lift /path/to/paper.tex")
        return 1
    print(f"═ Prose Lift Pipeline ═")
    print(f"  File: {args.filepath}")
    try:
        from pipeline.lift_pipeline.lift_pipeline_ob3ect import LiftPipelineOb3ect
        lifter = LiftPipelineOb3ect()
        result = lifter.analyze_document(Path(args.filepath).read_text(encoding="utf-8"))
        output = {
            "file": args.filepath,
            "result": result if isinstance(result, (dict, list)) else str(result)[:2000],
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Lift failed: {e}")
        traceback.print_exc()
        return 1
    return 0

def _cmd_list(args):
    print("rebis.pipeline — Exports:")
    for name in sorted(__all__):
        print(f"  {name} ({_EXPORTS[name]}; resolved on access)")
    print("\nCommands:")
    print("  verify [--source PATH]    — Frobenius μ∘δ=id verification")
    print("  imscribe <name>         — Auto-imscription generation")
    print("  retro <smiles>          — Retrosynthetic analysis")
    print("  therapy <key>           — Therapy→PDB pipeline")
    print("  therapy-all             — All therapies→PDB")
    print("  lift <file>             — Prose lift pipeline")
    print("  list                    — List exports")
    return 0


def main():
    """CLI: rebis.pipeline <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.pipeline",
        description="rebis.pipeline — Imscription Pipeline & Frobenius Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_ver = sub.add_parser("verify",
        help="Run Frobenius verification across all pipeline modules",
        description="Run the full Frobenius verification suite:\n"
                    "  1. Semantic identity phase (AST→source→AST roundtrip)\n"
                    "  2. IMASM bootstrap sequence (VINIT→TANCH→AREV→AFWD→FFUSE→CLINK→IFIX→EVALT)\n"
                    "  3. Bootstrap compiler (self-verifying compilation)",
        epilog="Examples:  rebis.pipeline verify\n"
               "           rebis.pipeline verify --source /path/to/module.py",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ver.add_argument("--source", default="",
                       help="Python source to verify (default: pipeline/frob.py); --file loads command configuration")
    p_ver.set_defaults(func=_cmd_verify)

    p_ims = sub.add_parser("imscribe",
        help="Run auto-imscription on a named system",
        description="Auto-imscribe a system — generate its 12-primitive IG tuple\n"
                    "and structural characterization via the AutoImscriber pipeline.",
        epilog="Examples:  rebis.pipeline imscribe my_system\n"
               "           rebis.pipeline imscribe riemann_zeta --description 'zeta function'",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ims.add_argument("name", nargs="?", default="test",
                       help="System name to imscribe (default: 'test')")
    p_ims.add_argument("--description", default="",
                       help="System description for imscription")
    p_ims.set_defaults(func=_cmd_imscribe)

    p_ret = sub.add_parser("retro",
        help="Run retrosynthetic analysis",
        description="Run retrosynthetic analysis on a target molecule.\n"
                    "Uses ReactionPipeline — decomposes the molecule into\n"
                    "synthons via functional group disconnections.",
        epilog="Example:  rebis.pipeline retro c1ccccc1 --depth 4",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ret.add_argument("smiles", nargs="?", default="",
                       help="Target molecule SMILES")
    p_ret.add_argument("--depth", type=int, default=6,
                       help="Max retrosynthesis depth (default: 6)")
    p_ret.set_defaults(func=_cmd_retro)

    p_the = sub.add_parser("therapy",
        help="Run therapy→PDB pipeline for a single therapy",
        description="Full therapy→PDB pipeline:\n"
                    "  load → analyze → ch3mpile → serpentrod → PDB validate → Frobenius\n"
                    "Generates a structural design report for the specified therapy.",
        epilog="Example:  rebis.pipeline therapy schizophrenia",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # The therapies are named in the pipeline itself, so the choices come from
    # there and an omitted key runs the first rather than failing on an empty one.
    try:
        from pipeline.therapy_to_pdb import THERAPIES as _THERAPIES
        _keys = list(_THERAPIES)
    except Exception:
        _keys = []
    p_the.add_argument("key", nargs="?", default=(_keys[0] if _keys else ""),
                       choices=(_keys or None),
                       help="Therapy key" + (f" ({', '.join(_keys)})" if _keys else ""))
    p_the.add_argument("--skip-ch3mpile", action="store_true",
                       help="Skip ch3mpiler stage")
    p_the.add_argument("--skip-serpentrod", action="store_true",
                       help="Skip serpentrod stage")
    p_the.set_defaults(func=_cmd_therapy)

    p_all = sub.add_parser("therapy-all",
        help="Run therapy→PDB pipeline for ALL therapies",
        description="Run the full therapy→PDB pipeline for all registered\n"
                    "therapies and generate a summary report.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_all.add_argument("--skip-ch3mpile", action="store_true",
                       help="Skip ch3mpiler stage")
    p_all.add_argument("--skip-serpentrod", action="store_true",
                       help="Skip serpentrod stage")
    p_all.set_defaults(func=_cmd_therapy_all)

    p_lif = sub.add_parser("lift",
        help="Lift prose — apply the human-lift protocol to a file",
        description="Apply the prose lift protocol to a document — promotes\n"
                    "8 primitive deltas from AI-default to human-academic target.",
        epilog="Example:  rebis.pipeline lift /path/to/paper.tex",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_lif.add_argument("filepath", nargs="?", default="",
                       help="Path to the file to lift")
    p_lif.set_defaults(func=_cmd_lift)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
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
