"""
rebis.clink — CLINK Chain & Organism Pipeline
═══════════════════════════════════════════════
Lazy-import bridge to clink/.

Callable as a command:
  rebis.clink layers              — List CLINK layers
  rebis.clink bridge <a> <b>     — Compute bridge between components
  rebis.clink chain <tuple>      — Compute CLINK chain from tuple
  rebis.clink cscore <tuple>     — Compute consciousness score
  rebis.clink info               — Show available tools
"""

import sys, importlib, argparse, json
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "clink")]:
    if p not in sys.path: sys.path.insert(0, p)

__all__ = []
def _lazy(name, module, attr=None):
    try:
        m = importlib.import_module(module)
        globals()[name] = getattr(m, attr or name)
        __all__.append(name)
    except Exception:
        pass

# chain
_lazy("compute_tier_from_tuple", "clink.chain")
_lazy("compute_c_score_from_tuple", "clink.chain")
_lazy("clink_frobenius_closed", "clink.chain")
_lazy("clink_layer_index", "clink.chain")
_lazy("clink_layer_tuple", "clink.chain")

# bridges
_lazy("BridgeResult", "clink.bridges")
_lazy("protein_to_clink", "clink.bridges")
_lazy("molecule_to_clink", "clink.bridges")
_lazy("gene_to_clink", "clink.bridges")
_lazy("bridge_all_components", "clink.bridges")

# integration
_lazy("IntegratedCLINKResult", "clink.integration")
_lazy("verify_clink_integration", "clink.integration")
_lazy("integrated_promotion_path", "clink.integration")
_lazy("clink_to_serpentrod", "clink.integration")
_lazy("clink_to_ch3mpiler", "clink.integration")

# pipeline_engine
_lazy("PipelineMode", "clink.pipeline_engine")
_lazy("EntryMode", "clink.pipeline_engine")
_lazy("DesignSpec", "clink.pipeline_engine")
_lazy("TransitionResult", "clink.pipeline_engine")
_lazy("PipelineResult", "clink.pipeline_engine")

# structural_algebra
_lazy("meet", "clink.structural_algebra")
_lazy("join", "clink.structural_algebra")
_lazy("ordinal", "clink.structural_algebra")

# designers
_lazy("DesignerBase", "clink.designers.designer_base")
_lazy("LayerDesigner", "clink.designers.layer_designers")
_lazy("design_layer", "clink.designers.layer_designers")
_lazy("ToolForge", "clink.designers.tool_forge")
_lazy("PipelineOrchestrator", "clink.designers.pipeline_orchestrator")
_lazy("DFTBridge", "clink.designers.dft_bridge")


def main():
    """CLI: rebis.clink <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.clink — CLINK Chain & Organism Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: layers, bridge, chain, cscore, info, list, help")
    parser.add_argument("args", nargs="*", help="Arguments for command")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.clink — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd in ("layers", "layer", "chains"):
        print("CLINK Layers (L0–L8):")
        for i in range(9):
            tup = clink_layer_tuple(i)
            tier = compute_tier_from_tuple(tup)
            cscore = compute_c_score_from_tuple(tup)
            print(f"  L{i}: ⟨{''.join(tup.values())}⟩  tier={tier}  C={cscore:.3f}")
        return 0

    if cmd == "bridge":
        cl_args = args.args
        if len(cl_args) < 1:
            print("Usage: rebis.clink bridge <component> [component2]")
            return 1
        try:
            result = bridge_all_components(cl_args)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Bridge failed: {e}")
            return 1
        return 0

    if cmd == "chain":
        if not args.args:
            print("Usage: rebis.clink chain <tuple_encoded_name>")
            return 1
        from clink.pipeline_engine import run_pipeline
        try:
            result = run_pipeline(args.args[0])
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Chain failed: {e}")
            return 1
        return 0

    if cmd in ("cscore", "c-score", "consciousness"):
        if not args.args:
            print("Usage: rebis.clink cscore <tuple_encoded_name>")
            return 1
        try:
            cscore = compute_c_score_from_tuple(args.args[0])
            print(f"C-score: {cscore:.4f}")
        except Exception as e:
            print(f"C-score failed: {e}")
            return 1
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())