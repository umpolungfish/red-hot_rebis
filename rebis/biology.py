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


def _cmd_sim(args):
    print("Running OuroboricCellSim...")
    try:
        sim = OuroboricCellSim()
        result = sim.run() if hasattr(sim, 'run') else str(sim)
        print(result if isinstance(result, str) else json.dumps(result, indent=2))
    except Exception as e:
        print(f"Simulation failed: {e}")
    return 0


def _cmd_telomeres(args):
    print("Telomere / Epigenetic States:")
    for cls_name in ["CellFate", "EpigeneticPhase", "TelomereState", "EpigeneticState"]:
        cls = globals().get(cls_name)
        if cls:
            members = [m for m in dir(cls) if not m.startswith('_')]
            print(f"  {cls_name}: {', '.join(members[:6])}")
    return 0


def _cmd_status(args):
    bio_dir = _REBIS_ROOT / "biology"
    results = list(bio_dir.glob("*.json")) + list(bio_dir.glob("*.md"))
    if results:
        print("Biology results:")
        for r in results:
            print(f"  {r.name} ({r.stat().st_size:,d} bytes)")
    else:
        print("No results files found in biology/")
    return 0


def _cmd_list(args):
    print("rebis.biology — Exports:")
    for name in sorted(__all__):
        print(f"  {name}")
    return 0


def main():
    """CLI: rebis.biology <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.biology",
        description="rebis.biology — Biological Simulations & Telomere Design",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_sim = sub.add_parser("sim",
        help="Run OuroboricCellSim (Frobenius-exact cell simulation)",
        description="Run the Frobenius-exact ouroboric cell simulation —\n"
                    "topological morphogenesis, cell fate determination,\n"
                    "and epigenetic state transitions.",
        epilog="Example:  rebis.biology sim",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_sim.set_defaults(func=_cmd_sim)

    p_tel = sub.add_parser("telomeres",
        help="Show telomere and epigenetic states",
        description="Display available telomere states, epigenetic phases,\n"
                    "and cell fate enumerations from the ouroboric telomere model.",
        epilog="Example:  rebis.biology telomeres",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_tel.set_defaults(func=_cmd_telomeres)

    p_stat = sub.add_parser("status",
        help="Show simulation results and reports",
        description="List all result files (JSON, Markdown) in the biology/\n"
                    "output directory with file sizes.",
        epilog="Example:  rebis.biology status",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_stat.set_defaults(func=_cmd_status)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
        epilog="Example:  rebis.biology list",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ls.set_defaults(func=_cmd_list)

    p_inf = sub.add_parser("info",
        help="Show available tools (alias for list)",
        epilog="Example:  rebis.biology info",
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
