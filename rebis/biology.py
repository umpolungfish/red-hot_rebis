"""
rebis.biology — Biological Simulations & Telomere Design
═════════════════════════════════════════════════════════
Lazy-import bridge to biology/.

Callable as a command:
  rebis.biology sim               — Run biological simulation
  rebis.biology telomeres         — Show telomere/epigenetic states
  rebis.biology status            — Show simulation results
  rebis.biology info              — Show available tools
"""
import sys, importlib, argparse, json
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "biology")]:
    if p not in sys.path: sys.path.insert(0, p)
__all__ = []
def _lazy(name, module, attr=None):
    try: m = importlib.import_module(module); globals()[name] = getattr(m, attr or name); __all__.append(name)
    except Exception: pass

_lazy("OuroboricCellSim", "biology.biology_sim_frobenius_exact")
_lazy("TopologicalMorphogenesisSim", "biology.biology_sim_frobenius_exact")
_lazy("CellFate", "biology.ouroboric_telomere_expanded")
_lazy("EpigeneticPhase", "biology.ouroboric_telomere_expanded")
_lazy("TelomereState", "biology.ouroboric_telomere_expanded")
_lazy("EpigeneticState", "biology.ouroboric_telomere_expanded")


def main():
    """CLI: rebis.biology <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.biology — Biological Simulations & Telomere Design",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: sim, telomeres, status, info, help")
    parser.add_argument("args", nargs="*", help="Arguments")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.biology — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd == "sim":
        print("Running OuroboricCellSim...")
        try:
            sim = OuroboricCellSim()
            result = sim.run() if hasattr(sim, 'run') else str(sim)
            print(result if isinstance(result, str) else json.dumps(result, indent=2))
        except Exception as e:
            print(f"Simulation failed: {e}")
        return 0

    if cmd in ("telomeres", "telomere", "epigenetics"):
        print("Telomere / Epigenetic States:")
        for cls_name in ["CellFate", "EpigeneticPhase", "TelomereState", "EpigeneticState"]:
            cls = globals().get(cls_name)
            if cls:
                members = [m for m in dir(cls) if not m.startswith('_')]
                print(f"  {cls_name}: {', '.join(members[:6])}")
        return 0

    if cmd in ("status", "results"):
        bio_dir = _REBIS_ROOT / "biology"
        results = list(bio_dir.glob("*.json")) + list(bio_dir.glob("*.md"))
        if results:
            print("Biology results:")
            for r in results:
                print(f"  {r.name} ({r.stat().st_size:,d} bytes)")
        else:
            print("No results files found in biology/")
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())