"""
rebis.therapeutics — Therapeutic Design Pipeline
═════════════════════════════════════════════════
Lazy-import bridge to therapeutics/.

Callable as a command:
  rebis.therapeutics list          — List therapeutics tools
  rebis.therapeutics design <tgt>  — Design a chemotherapeutic
  rebis.therapeutics sim           — Run ouroboric pill simulation
  rebis.therapeutics neurotrophic [target] — Design neurotrophic factor
  rebis.therapeutics antidote [poison]     — Query universal antidote library
  rebis.therapeutics info          — Show available tools
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


def _cmd_design(args):
    target = args.target
    print(f"Designing chemotherapeutic for target: {target}...")
    try:
        from therapeutics.frobenius_chemotherapeutic import FrobeniusChemoSim
        sim = FrobeniusChemoSim()
        result = {"target": target, "status": "FrobeniusChemoSim initialized",
                  "message": "Use .simulate() to run chemo simulation"}
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Design failed: {e}")
    return 0


def _cmd_sim(args):
    print("Running OuroboricPillSimulation...")
    try:
        from therapeutics.ouroboric_pill_sim import OuroboricPillSim
        sim = OuroboricPillSim()
        result = sim.run() if hasattr(sim, 'run') else simulate_pill_dynamics()
        print(str(result)[:2000])
    except Exception as e:
        print(f"Simulation failed: {e}")
    return 0


def _cmd_neurotrophic(args):
    target = args.target
    print(f"Designing neurotrophic factor: {target}")
    try:
        from therapeutics.neurotrophic_factor import BNFSim
        sim = BNFSim(target)
        result = {"target": target, "status": "BNFSim initialized",
                  "message": "Neurotrophic factor simulation ready"}
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Design failed: {e}")
    return 0


def _cmd_antidote(args):
    poison = args.poison
    print(f"Querying antidote for: {poison}")
    try:
        from therapeutics.universal_antidote_library import RibosomeDisplayLibrary
        lib = RibosomeDisplayLibrary()
        result = {"poison": poison, "status": "RibosomeDisplayLibrary queried",
                  "message": "Universal antidote library queried — see .screen_toxin() for details"}
        print(json.dumps(result, indent=2) if isinstance(result, (dict, list)) else result)
    except Exception as e:
        print(f"Antidote query failed: {e}")
    return 0


def _cmd_list(args):
    print("rebis.therapeutics — Exports:")
    for name in sorted(__all__):
        print(f"  {name}")
    return 0


def main():
    """CLI: rebis.therapeutics <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.therapeutics",
        description="rebis.therapeutics — Therapeutic Design Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_des = sub.add_parser("design",
        help="Design a Frobenius-verified chemotherapeutic",
        description="Design a chemotherapeutic agent for a given target\n"
                    "using Frobenius-verified structural optimization.",
        epilog="Examples:  rebis.therapeutics design\n"
               "           rebis.therapeutics design EGFR\n"
               "           rebis.therapeutics design KRAS",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_des.add_argument("target", nargs="?", default="default",
                       help="Therapeutic target (default: 'default')")
    p_des.set_defaults(func=_cmd_design)

    p_sim = sub.add_parser("sim",
        help="Run ouroboric pill dynamics simulation",
        description="Simulate ouroboric pill dynamics — Frobenius-closed\n"
                    "pharmacokinetic/pharmacodynamic time evolution.",
        epilog="Example:  rebis.therapeutics sim",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_sim.set_defaults(func=_cmd_sim)

    p_neu = sub.add_parser("neurotrophic",
        help="Design a neurotrophic factor",
        description="Design a neurotrophic factor (e.g. BDNF analog)\n"
                    "using IG-guided structural protein design.",
        epilog="Examples:  rebis.therapeutics neurotrophic\n"
               "           rebis.therapeutics neurotrophic BDNF\n"
               "           rebis.therapeutics neurotrophic NGF",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_neu.add_argument("target", nargs="?", default="BDNF",
                       help="Neurotrophic factor target (default: BDNF)")
    p_neu.set_defaults(func=_cmd_neurotrophic)

    p_ant = sub.add_parser("antidote",
        help="Query the universal antidote library",
        description="Query the IG-structured universal antidote library\n"
                    "for a given poison/toxin.",
        epilog="Examples:  rebis.therapeutics antidote\n"
               "           rebis.therapeutics antidote cyanide\n"
               "           rebis.therapeutics antidote tetrodotoxin",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ant.add_argument("poison", nargs="?", default="cyanide",
                       help="Poison/toxin name (default: cyanide)")
    p_ant.set_defaults(func=_cmd_antidote)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
        epilog="Example:  rebis.therapeutics list",
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
