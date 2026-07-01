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


def main():
    """CLI: rebis.pipeline <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.pipeline — Imscription Pipeline & Frobenius Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: verify, imscribe, lift, list, info, help")
    parser.add_argument("args", nargs="*", help="Arguments")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.pipeline — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd == "verify":
        print("Running Frobenius verification...")
        try:
            result = verify_frobenius()
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Verification failed: {e}")
        return 0

    if cmd == "imscribe":
        name = args.args[0] if args.args else "test"
        print(f"Running auto-imscription for: {name}")
        try:
            imscriber = AutoImscriber()
            result = imscriber.imscribe(name) if hasattr(imscriber, 'imscribe') else str(imscriber)
            print(result[:2000] if isinstance(result, str) else json.dumps(result, indent=2))
        except Exception as e:
            print(f"Imscription failed: {e}")
        return 0

    if cmd == "lift":
        fname = args.args[0] if args.args else ""
        if not fname:
            print("Usage: rebis.pipeline lift <filepath>")
            return 1
        print(f"Lifting prose in: {fname}")
        try:
            result = lift_text(fname)
            print(result[:2000] if isinstance(result, str) else json.dumps(result, indent=2))
        except Exception as e:
            print(f"Lift failed: {e}")
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())