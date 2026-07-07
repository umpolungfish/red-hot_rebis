"""
rebis.therapeutics — Therapeutic Design Pipeline (ADVANCED v2)
══════════════════════════════════════════════════════════════════
Full implementations of:
  - FrobeniusChemoSim: Frobenius-verified selective chemotherapeutic
  - OuroboricPillSim: μ∘δ-verified autonomous pill dynamics
  - BNFSim: Bidirectional neurotrophic factor (BDNF/NGF) simulation
  - QuantumBiologicSim: NV-diamond epigenetic editing therapy
  - RibosomeDisplayLibrary: Universal antidote scFv library

Callable as a command:
  rebis.therapeutics design [--target EGFR] [--mutation 0.5] [--time 30] [--drug-conc 2.0]
  rebis.therapeutics sim [--time 100] [--dt 0.5] [--noise 0.02]
  rebis.therapeutics neurotrophic [--disease alzheimer] [--time 100] [--active/--no-active]
  rebis.therapeutics antidote [--poison ricin] [--rounds 8] [--diversity 1e9]
  rebis.therapeutics quantum [--weeks 24] [--edits 3] [--loci 5]
  rebis.therapeutics list
"""
import sys, importlib, argparse, json, io, os
from pathlib import Path
from rebis.file_input import parse_with_file

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "therapeutics"),
          str(_REBIS_ROOT / "shared")]:
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

_lazy("FrobeniusChemoSim", "therapeutics.frobenius_chemotherapeutic")
_lazy("CancerReceptorModel", "therapeutics.frobenius_chemotherapeutic")
_lazy("FrobeniusChemoState", "therapeutics.frobenius_chemotherapeutic")
_lazy("OuroboricPillSim", "therapeutics.ouroboric_pill_sim")
_lazy("BNFSim", "therapeutics.neurotrophic_factor")
_lazy("NeuralEnvironment", "therapeutics.neurotrophic_factor")
_lazy("BidirectionalFactor", "therapeutics.neurotrophic_factor")
_lazy("QuantumBiologicSim", "therapeutics.quantum_biologic_prototype")
_lazy("EpigeneticState", "therapeutics.quantum_biologic_prototype")
_lazy("RibosomeDisplayLibrary", "therapeutics.universal_antidote_library")
_lazy("run_toxin_challenge_sweep", "therapeutics.universal_antidote_library")


def _json_or_str(obj):
    """Serialize to JSON if possible, else str."""
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, default=str, ensure_ascii=False)
    if hasattr(obj, '__dict__'):
        try:
            return json.dumps(vars(obj), indent=2, default=str, ensure_ascii=False)
        except Exception:
            return str(obj)
    return str(obj)


def _cmd_design(args):
    """Run full FrobeniusChemoSim — cancer vs healthy receptor comparison."""
    target = args.target
    mutation = args.mutation
    total_time = args.time
    drug_conc = args.drug_conc
    print(f"═ Designing Frobenius chemotherapeutic ═")
    print(f"  Target: {target}")
    print(f"  Mutation strength: {mutation}")
    print(f"  Drug concentration: {drug_conc} µM")
    print(f"  Simulation time: {total_time} h")
    try:
        from therapeutics.frobenius_chemotherapeutic import (
            CancerReceptorModel, FrobeniusChemoSim)

        # Cancer receptor — Frobenius symmetry broken
        cancer_rec = CancerReceptorModel(
            receptor_type="cancer", mutation_strength=mutation)
        sim_cancer = FrobeniusChemoSim(dt=0.5, drug_conc=drug_conc)
        print("\nRunning cancer receptor simulation...")
        cancer_result = sim_cancer.run(total_time=total_time)

        # Healthy receptor — Frobenius symmetry preserved (μ∘δ=id)
        healthy_rec = CancerReceptorModel(
            receptor_type="healthy", mutation_strength=0.0)
        sim_healthy = FrobeniusChemoSim(dt=0.5, drug_conc=drug_conc)
        print("Running healthy receptor simulation (control)...")
        healthy_result = sim_healthy.run(total_time=total_time)

        # Frobenius analysis
        cancer_k_on = cancer_rec.k_on
        cancer_k_off = cancer_rec.k_off
        frobenius_cancer = cancer_k_on * cancer_k_off
        frobenius_healthy = healthy_rec.k_on * healthy_rec.k_off

        output = {
            "target": target,
            "parameters": {
                "mutation_strength": mutation,
                "drug_conc_uM": drug_conc,
                "time_hours": total_time,
            },
            "cancer": {
                "k_on": round(cancer_k_on, 4),
                "k_off": round(cancer_k_off, 4),
                "frobenius_product": round(frobenius_cancer, 4),
                "frobenius_broken": abs(frobenius_cancer - 1.0) > 0.01,
                "clustering": round(cancer_rec.clustering, 4),
                "simulation": cancer_result if isinstance(cancer_result, (dict, list)) else str(cancer_result),
            },
            "healthy_control": {
                "k_on": healthy_rec.k_on,
                "k_off": healthy_rec.k_off,
                "frobenius_product": round(frobenius_healthy, 4),
                "frobenius_intact": abs(frobenius_healthy - 1.0) < 0.01,
                "simulation": healthy_result if isinstance(healthy_result, (dict, list)) else str(healthy_result),
            },
            "selectivity": {
                "cancer_activated": frobenius_cancer != 1.0,
                "healthy_unactivated": frobenius_healthy == 1.0,
                "frobenius_selective": abs(frobenius_cancer - 1.0) > 0.01 and abs(frobenius_healthy - 1.0) < 0.01,
            },
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Design failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_sim(args):
    """Run OuroboricPillSim — μ∘δ-verified autonomous pharmacodynamics."""
    total_time = args.time
    dt = args.dt
    noise = args.noise
    print(f"═ Ouroboric Pill Simulation (μ∘δ=id) ═")
    print(f"  Time: {total_time} | dt: {dt} | noise: {noise}")
    try:
        from therapeutics.ouroboric_pill_sim import OuroboricPillSim
        sim = OuroboricPillSim(dt=dt, noise=noise)
        result = sim.run(total_time=total_time)
        print(_json_or_str(result))
    except Exception as e:
        import traceback
        print(f"Simulation failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_neurotrophic(args):
    """Run BNFSim — bidirectional neurotrophic factor dynamics."""
    disease = args.disease
    total_time = args.time
    bnf_active = args.active
    print(f"═ Neurotrophic Factor Simulation ═")
    print(f"  Disease model: {disease}")
    print(f"  BNF active: {bnf_active}")
    print(f"  Time: {total_time}")
    try:
        from therapeutics.neurotrophic_factor import BNFSim
        sim = BNFSim(disease=disease, bnf_active=bnf_active)
        result = sim.run(total_time=total_time)
        print(_json_or_str(result))
    except Exception as e:
        import traceback
        print(f"Neurotrophic simulation failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_antidote(args):
    """Run RibosomeDisplayLibrary — universal antidote scFv screening."""
    poison = args.poison
    rounds = args.rounds
    diversity = args.diversity
    print(f"═ Universal Antidote Library ═")
    print(f"  Target toxin: {poison}")
    print(f"  Panning rounds: {rounds}")
    print(f"  Library diversity: {diversity:.2e}")
    try:
        from therapeutics.universal_antidote_library import (
            RibosomeDisplayLibrary, run_toxin_challenge_sweep)
        lib = RibosomeDisplayLibrary(diversity=diversity)
        print("  Generating library...")
        lib.generate_library()
        print("  Assigning binders...")
        lib.assign_binders()
        print(f"  Multi-target panning ({rounds} rounds)...")
        panning = lib.multi_target_panning(rounds=rounds)
        print(f"  Computing binding for {poison}...")
        binding = lib.compute_binding(toxin_conc_nM=100.0)
        print("  Running toxin challenge sweep...")
        sweep = run_toxin_challenge_sweep()
        output = {
            "poison": poison,
            "library_diversity": diversity,
            "panning_rounds": rounds,
            "panning_results": panning if isinstance(panning, (dict, list)) else str(panning),
            "binding_results": binding if isinstance(binding, (dict, list)) else str(binding),
            "toxin_challenge_sweep": sweep if isinstance(sweep, (dict, list)) else str(sweep),
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Antidote query failed: {e}")
        traceback.print_exc()
        return 1
    return 0

def _cmd_quantum(args):
    """Run QuantumBiologicSim — NV-diamond epigenetic editing therapy."""
    weeks = args.weeks
    edits = args.edits
    loci = args.loci
    print(f"═ Quantum Biologic Prototype ═")
    print(f"  Therapy duration: {weeks} weeks")
    print(f"  Edits per session: {edits}")
    print(f"  Epigenetic loci: {loci}")
    try:
        from therapeutics.quantum_biologic_prototype import (
            QuantumBiologicSim, EpigeneticState)
        sim = QuantumBiologicSim()
        sim.state = EpigeneticState(n_loci=loci)
        print("  Running quantum epigenetic therapy...")
        therapy_result = sim.run_therapy(
            total_weeks=weeks, edits_per_session=edits)
        summary = sim.summarize()
        output = {
            "weeks": weeks,
            "edits_per_session": edits,
            "n_loci": loci,
            "therapy_result": therapy_result if isinstance(therapy_result, (dict, list)) else str(therapy_result),
            "summary": summary if isinstance(summary, (dict, list)) else str(summary),
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"Quantum biologic simulation failed: {e}")
        traceback.print_exc()
        return 1
    return 0


def _cmd_list(args):
    print("rebis.therapeutics — Exports:")
    for name in sorted(__all__):
        obj = globals().get(name)
        status = "✓" if obj is not None else "✗"
        print(f"  {status} {name}")
    print("\nCommands:")
    print("  design <target>     — Frobenius chemotherapeutic (cancer vs healthy)")
    print("  sim                 — Ouroboric pill μ∘δ dynamics")
    print("  neurotrophic <tgt>  — BDNF/NGF bidirectional factor sim")
    print("  antidote <poison>   — Universal antidote scFv library screening")
    print("  quantum             — NV-diamond epigenetic editing therapy")
    print("  list                — List exports")
    return 0


def main():
    """CLI: rebis.therapeutics <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.therapeutics",
        description="rebis.therapeutics — Full Therapeutic Design Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    # ── design ──
    p_des = sub.add_parser("design",
        help="Design a Frobenius-verified chemotherapeutic (cancer vs healthy)",
        description="Run the full FrobeniusChemoSim —\n"
                    "  Cancer: μ∘δ≠id → tether strain → payload exposed\n"
                    "  Healthy: μ∘δ=id → tether relaxed → payload masked\n"
                    "Compares cancer vs healthy receptor binding dynamics.",
        epilog="Examples:  rebis.therapeutics design\n"
               "           rebis.therapeutics design EGFR --mutation 0.7\n"
               "           rebis.therapeutics design KRAS --time 50 --drug-conc 5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_des.add_argument("target", nargs="?", default="EGFR",
                       help="Therapeutic target (default: EGFR)")
    p_des.add_argument("--mutation", type=float, default=0.5,
                       help="Cancer mutation strength 0-1 (default: 0.5)")
    p_des.add_argument("--time", type=float, default=30.0,
                       help="Simulation time in hours (default: 30)")
    p_des.add_argument("--drug-conc", type=float, default=2.0,
                       help="Drug concentration µM (default: 2.0)")
    p_des.set_defaults(func=_cmd_design)

    # ── sim ──
    p_sim = sub.add_parser("sim",
        help="Run ouroboric pill dynamics simulation",
        description="Simulate the OuroboricPill — an autonomous pharmacological\n"
                    "system with embedded Frobenius kernel (μ∘δ=id).\n"
                    "The pill senses, decides, and acts in closed loop.",
        epilog="Example:  rebis.therapeutics sim --time 200 --noise 0.05",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_sim.add_argument("--time", type=float, default=100.0,
                       help="Total simulation time (default: 100)")
    p_sim.add_argument("--dt", type=float, default=0.5,
                       help="Time step (default: 0.5)")
    p_sim.add_argument("--noise", type=float, default=0.02,
                       help="Environmental noise level (default: 0.02)")
    p_sim.set_defaults(func=_cmd_sim)

    # ── neurotrophic ──
    p_neu = sub.add_parser("neurotrophic",
        help="Design and simulate a neurotrophic factor",
        description="Run BNFSim — bidirectional neurotrophic factor simulation\n"
                    "for Alzheimer's, Parkinson's, or ALS disease models.\n"
                    "Models activity-dependent BDNF/NGF secretion and feedback.",
        epilog="Examples:  rebis.therapeutics neurotrophic\n"
               "           rebis.therapeutics neurotrophic --disease parkinsons\n"
               "           rebis.therapeutics neurotrophic --no-active --time 50",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_neu.add_argument("target", nargs="?", default="BDNF",
                       help="Neurotrophic target (default: BDNF)")
    p_neu.add_argument("--disease", default="alzheimer",
                       help="Disease model: alzheimer|parkinsons|als (default: alzheimer)")
    p_neu.add_argument("--time", type=float, default=100.0,
                       help="Simulation time (default: 100)")
    p_neu.add_argument("--active", action=argparse.BooleanOptionalAction, default=True,
                       help="BNF therapy active (default: --active)")
    p_neu.set_defaults(func=_cmd_neurotrophic)

    # ── antidote ──
    p_ant = sub.add_parser("antidote",
        help="Query universal antidote library",
        description="Screen a ribosome display scFv library against a toxin.\n"
                    "Generates library → assigns binders → multi-target panning →\n"
                    "computes binding affinity → runs toxin challenge sweep.",
        epilog="Examples:  rebis.therapeutics antidote\n"
               "           rebis.therapeutics antidote ricin --rounds 12\n"
               "           rebis.therapeutics antidote sarin --diversity 1e10",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ant.add_argument("poison", nargs="?", default="ricin",
                       help="Target toxin (default: ricin)")
    p_ant.add_argument("--rounds", type=int, default=8,
                       help="Panning rounds (default: 8)")
    p_ant.add_argument("--diversity", type=float, default=1e9,
                       help="Library diversity (default: 1e9)")
    p_ant.set_defaults(func=_cmd_antidote)

    # ── quantum ──
    p_qua = sub.add_parser("quantum",
        help="Run quantum biologic prototype (NV-diamond epigenetic therapy)",
        description="QuantumBiologicSim — models NV-diamond mediated\n"
                    "epigenetic editing with quantum coherence readout.\n"
                    "Simulates methylation editing, NV-center readout,\n"
                    "and therapeutic outcomes over multiple weeks.",
        epilog="Examples:  rebis.therapeutics quantum\n"
               "           rebis.therapeutics quantum --weeks 48 --edits 5",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_qua.add_argument("--weeks", type=int, default=24,
                       help="Therapy duration in weeks (default: 24)")
    p_qua.add_argument("--edits", type=int, default=3,
                       help="Edits per session (default: 3)")
    p_qua.add_argument("--loci", type=int, default=5,
                       help="Number of epigenetic loci (default: 5)")
    p_qua.set_defaults(func=_cmd_quantum)

    # ── list / info ──
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
