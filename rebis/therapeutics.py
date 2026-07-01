"""
rebis.therapeutics — Therapeutic Design Pipeline
═════════════════════════════════════════════════
Lazy-import bridge to therapeutics/.

Callable as a command:
  rebis.therapeutics list         — List therapeutics tools
  rebis.therapeutics design <tgt> — Design a chemotherapeutic
  rebis.therapeutics sim          — Run ouroboric pill simulation
  rebis.therapeutics neurotrophic — Design neurotrophic factor
  rebis.therapeutics antidote     — Query universal antidote library
  rebis.therapeutics info         — Show available tools
"""
import sys, importlib, argparse, json
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "therapeutics")]:
    if p not in sys.path: sys.path.insert(0, p)
__all__ = []
def _lazy(name, module, attr=None):
    try: m = importlib.import_module(module); globals()[name] = getattr(m, attr or name); __all__.append(name)
    except Exception: pass

_lazy("FrobeniusChemotherapeutic", "therapeutics.frobenius_chemotherapeutic")
_lazy("design_chemotherapeutic", "therapeutics.frobenius_chemotherapeutic")
_lazy("NeurotrophicFactorDesigner", "therapeutics.neurotrophic_factor")
_lazy("design_neurotrophic_factor", "therapeutics.neurotrophic_factor")
_lazy("OuroboricPillSimulation", "therapeutics.ouroboric_pill_sim")
_lazy("simulate_pill_dynamics", "therapeutics.ouroboric_pill_sim")
_lazy("QuantumBiologicPrototype", "therapeutics.quantum_biologic_prototype")
_lazy("design_quantum_biologic", "therapeutics.quantum_biologic_prototype")
_lazy("UniversalAntidoteLibrary", "therapeutics.universal_antidote_library")
_lazy("query_antidote", "therapeutics.universal_antidote_library")


def main():
    """CLI: rebis.therapeutics <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.therapeutics — Therapeutic Design Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: list, design, sim, neurotrophic, antidote, info, help")
    parser.add_argument("args", nargs="*", help="Arguments")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.therapeutics — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd in ("design", "chemotherapeutic"):
        target = args.args[0] if args.args else "default"
        print(f"Designing chemotherapeutic for target: {target}...")
        try:
            result = design_chemotherapeutic(target=target)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Design failed: {e}")
        return 0

    if cmd == "sim":
        print("Running OuroboricPillSimulation...")
        try:
            sim = OuroboricPillSimulation()
            result = sim.run() if hasattr(sim, 'run') else simulate_pill_dynamics()
            print(str(result)[:2000])
        except Exception as e:
            print(f"Simulation failed: {e}")
        return 0

    if cmd in ("neurotrophic", "neuro"):
        target = args.args[0] if args.args else "BDNF"
        print(f"Designing neurotrophic factor: {target}")
        try:
            result = design_neurotrophic_factor(target=target)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Design failed: {e}")
        return 0

    if cmd in ("antidote", "poison"):
        poison = args.args[0] if args.args else "cyanide"
        print(f"Querying antidote for: {poison}")
        try:
            result = query_antidote(poison)
            print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
        except Exception as e:
            print(f"Antidote query failed: {e}")
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())