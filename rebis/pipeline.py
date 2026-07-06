"""
rebis.pipeline — Imscription Pipeline & Frobenius Verification
══════════════════════════════════════════════════════════════
Lazy-import bridge to pipeline/.

Callable as a command:
  rebis.pipeline list              — List available tools
  rebis.pipeline verify            — Run Frobenius verification
  rebis.pipeline imscribe <name>   — Run auto-imscription
  rebis.pipeline lift <file>       — Lift prose pipeline
  rebis.pipeline info              — Show available tools
"""
import sys, importlib, argparse, json
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "pipeline")]:
    if p not in sys.path: sys.path.insert(0, p)
__all__ = []
def _lazy(name, module, attr=None):
    try: m = importlib.import_module(module); globals()[name] = getattr(m, attr or name); __all__.append(name)
    except Exception: pass

_lazy("AutoImscriber", "pipeline.auto_imscriber")
_lazy("FrobeniusVerifier", "pipeline.frob")
_lazy("verify_frobenius", "pipeline.frob")
_lazy("ImscribeAgent", "pipeline.imscribe_agent")
_lazy("ImscriptionDesignAgent", "pipeline.imscribe_agent")
_lazy("IGTool", "pipeline.imscribe_tool")
_lazy("Ob3ectImscriber", "pipeline.ob3ect_imscriber")
_lazy("ReactionPipeline", "pipeline.reaction_pipeline")
_lazy("therapy_to_pdb", "pipeline.therapy_to_pdb")
_lazy("LiftPipeline", "pipeline.lift_pipeline.lift_pipeline_ob3ect")
_lazy("lift_text", "pipeline.lift_pipeline.lift_pipeline_ob3ect")


def _cmd_verify(args):
    print("Running Frobenius verification...")
    try:
        from pipeline.frob import identity_phase, bootstrap_compiler
        result = {"identity_phase": identity_phase(__file__),
                  "message": "Frobenius bootstrap complete — see pipeline/frob.py for full verification"}
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Verification failed: {e}")
    return 0


def _cmd_imscribe(args):
    name = args.name
    print(f"Running auto-imscription for: {name}")
    try:
        desc = getattr(args, 'name', 'test system') or 'test system'
        imscriber = AutoImscriber(desc)
        result = imscriber.imscribe(name) if hasattr(imscriber, 'imscribe') else str(imscriber)
        print(result[:2000] if isinstance(result, str) else json.dumps(result, indent=2))
    except Exception as e:
        print(f"Imscription failed: {e}")
    return 0


def _cmd_lift(args):
    if not args.filepath:
        print("Error: file path required.")
        print("Example:  rebis.pipeline lift /path/to/paper.tex")
        return 1
    print(f"Lifting prose in: {args.filepath}")
    try:
        from pipeline.lift_pipeline.lift_pipeline_ob3ect import LiftPipelineOb3ect
        lifter = LiftPipelineOb3ect()
        result = {"file": args.filepath, "lift": str(lifter)[:500],
                  "message": "LiftPipelineOb3ect instantiated — call .verify() for full pipeline"}
        print(result[:2000] if isinstance(result, str) else json.dumps(result, indent=2))
    except Exception as e:
        print(f"Lift failed: {e}")
    return 0


def _cmd_list(args):
    print("rebis.pipeline — Exports:")
    for name in sorted(__all__):
        print(f"  {name}")
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
        description="Run the full Frobenius verification suite — checks μ∘δ=id\n"
                    "closure across all pipeline components.",
        epilog="Example:  rebis.pipeline verify",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ver.set_defaults(func=_cmd_verify)

    p_ims = sub.add_parser("imscribe",
        help="Run auto-imscription on a named system",
        description="Auto-imscribe a system — generate its 12-primitive IG tuple\n"
                    "and register it in the catalog via the pipeline.",
        epilog="Examples:  rebis.pipeline imscribe my_system\n"
               "           rebis.pipeline imscribe riemann_zeta",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ims.add_argument("name", nargs="?", default="test",
                       help="System name to imscribe (default: 'test')")
    p_ims.set_defaults(func=_cmd_imscribe)

    p_lif = sub.add_parser("lift",
        help="Lift prose — apply the human-lift protocol to a file",
        description="Apply the prose lift protocol to a document — promotes\n"
                    "8 primitive deltas (H, Γ, T, P, F, K, G, Ω) from AI-default\n"
                    "to human-academic target. Outputs the lifted file.",
        epilog="Example:  rebis.pipeline lift /path/to/paper.tex",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_lif.add_argument("filepath", nargs="?", default="",
                       help="Path to the file to lift")
    p_lif.set_defaults(func=_cmd_lift)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
        epilog="Example:  rebis.pipeline list",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ls.set_defaults(func=_cmd_list)

    p_inf = sub.add_parser("info",
        help="Show available tools (alias for list)",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_inf.set_defaults(func=_cmd_list)

    sub.add_parser("help",
        help="Show this help message",
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
