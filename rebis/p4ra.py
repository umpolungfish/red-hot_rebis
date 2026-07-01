"""
rebis.p4ra — p4ra Paraconsistent Kernel
═════════════════════════════════════════
Exposes all rhr_p4rky kernel modules under rebis.p4ra.<x>.
Auto-suppresses stdout during import (orbital_belnap demo noise).

Callable as a command:
  rebis.p4ra belnap               — Test Belnap operations
  rebis.p4ra genetics             — Show genetic code B4 lattice
  rebis.p4ra verify               — Run B3 Frobenius verification
  rebis.p4ra hadrons              — Test hadron Belnap operations
  rebis.p4ra ligands [enzyme]     — Generate ligand from enzyme
  rebis.p4ra info                 — Show available tools
"""
import sys as _sys
import io as _io
import argparse
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path as _Path

_REBIS_ROOT = _Path(__file__).parent.parent.absolute()
_sys.path.insert(0, str(_REBIS_ROOT))
_sys.path.insert(0, str(_REBIS_ROOT / "rhr_p4rky"))

# ── Suppress stdout during import ──
_quiet = _io.StringIO()
with redirect_stdout(_quiet), redirect_stderr(_quiet):
    from rhr_p4rky.belnap import Belnap, meet, join, band, bor, bnot
    from rhr_p4rky.belnap import designated, approx_le, to_wh2, from_wh2, dialetheic
    from rhr_p4rky.belnap_c4 import BelnapComplex, complex_to_belnap
    from rhr_p4rky.belnap_c4 import amplitude_to_probability, belnap_tensor_product
    from rhr_p4rky.kernel import (MachineState, initial_state, engager,
                                   fsplit, ffuse, step, run,
                                   frobenius_invariant, verify_frobenius_invariant,
                                   verify_run_B3, verify_paradox_conservation,
                                   verify_cycle_count, verify_paraconsistency,
                                   run_all_verifications)
    from rhr_p4rky.machine import ParaRegister, Instr, assemble, ParaVM
    from rhr_p4rky.genetics_b4 import (nucleotide_to_belnap, belnap_to_nucleotide,
                                        b4_meet, b4_join, b4_complement,
                                        b4_wobble_pair, b4_lattice_distance,
                                        b4_covering, BelnapCodon)
    from rhr_p4rky.genetic_code import (BelnapCodon as GeneticBelnapCodon,
                                         get_codon, verify_frobenius_on_codon,
                                         verify_all_codons_frobenius,
                                         get_aa_primitive, MutationReport,
                                         analyze_aa_mutation, box_stratification,
                                         analyze_stop_codons, crystal_divisibility,
                                         codon_to_kernel_state, run_kernel_on_protein,
                                         run_genetic_verification, demo)
    from rhr_p4rky.genetic_tuples import (ig_char_to_name, ig_tuple_to_pipeline,
                                           extract_kinetics_features,
                                           extract_criticality_features,
                                           extract_parity_features,
                                           extract_grammar_features,
                                           pipeline_tuple_to_ig,
                                           generate_dna_gene_tuple,
                                           generate_pre_mrna_tuple,
                                           generate_mature_mrna_tuple,
                                           generate_nascent_tuple,
                                           generate_secondary_tuple,
                                           generate_tertiary_tuple,
                                           generate_quaternary_tuple)
    from rhr_p4rky.hadron_belnap import (Meson, Baryon, try_make_meson, try_make_baryon,
                                          meson_pair, baryon_pair,
                                          meson_depair, baryon_depair,
                                          meson_frobenius, baryon_frobenius,
                                          build_meson_example, build_baryon_example,
                                          test_hadron_belnap)
    from rhr_p4rky.quark_belnap import (QuarkState, ColorState,
                                         anti_color, qpair as quark_pair,
                                         depair, test_quark_belnap,
                                         color_meet, color_join, color_le,
                                         ceiling_is_top, confinement_ceiling)
    from rhr_p4rky.orbital_belnap import (OrbitalState, pair as orbital_pair,
                                           depair as orbital_depair)
    from rhr_p4rky.exotic_hadron_belnap import (Tetraquark, Pentaquark, Glueball,
                                                  test_tetraquark, test_glueball)
    from rhr_p4rky.frobenius_filtration import (HadronState, test_filtration,
                                                  orbital_domain, quark_domain,
                                                  hadron_domain)
    from rhr_p4rky.antibody_designer import (design_cdr, design_antibodies_for_targets,
                                              analyze_epitope)
    from rhr_p4rky.ligand_from_active_site import (encode_site_from_residues,
                                                    complement_type,
                                                    closest_bond_type,
                                                    closest_fg_pair,
                                                    generate_ligand_smiles,
                                                    tuple_distance_dict,
                                                    fmt_tuple)
    from rhr_p4rky.ligand_improvements import (generate_from_enzyme_type,
                                                generate_from_structural_type,
                                                generate_ligands_from_bond_fg,
                                                test_bevy)
    from rhr_p4rky.pdb_validator import (validate_structure, extract_sequence,
                                          extract_experimental_contacts,
                                          compute_distance_3d,
                                          compute_precision_recall)
    from rhr_p4rky.serpent_rod_v2 import (SerpentRodV2, Gen2Result,
                                           frobenius_verified_v2,
                                           validate_against_pdb,
                                           compute_energy,
                                           compute_activation_set,
                                           predict_contacts_from_geometry)
    from rhr_p4rky.ch3mpiler_bridge import (Ch3mpiler, forward, retrosynthesis, analyze)
    from rhr_p4rky.clu_power_law import (CLUKernel3D, verify_power_law_3d,
                                          compute_filtration_spectrum,
                                          simulate_avalanche_3d)
    from rhr_p4rky.decay_chain import (analyze_chain, print_chain,
                                        print_all_series, compare_series,
                                        tuple_distance as dc_tuple_distance)

__all__ = sorted([k for k in dir() if not k.startswith('_')
                   and k not in ('_sys', '_io', '_Path', '_REBIS_ROOT', '_quiet',
                                 'redirect_stdout', 'redirect_stderr')])


def main():
    """CLI: rebis.p4ra <command> [args]"""
    parser = argparse.ArgumentParser(
        description="rebis.p4ra — Paraconsistent Kernel & Genetics",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", nargs="?", default="help",
                       help="Command: belnap, genetics, verify, hadrons, ligands, info, list, help")
    parser.add_argument("args", nargs="*", help="Arguments for command")
    args = parser.parse_args()

    cmd = args.command

    if cmd in ("help", "--help", "-h"):
        parser.print_help()
        return 0

    if cmd in ("list", "ls", "info"):
        print("rebis.p4ra — Exports:")
        for name in sorted(__all__):
            print(f"  {name}")
        return 0

    if cmd == "belnap":
        print("Belnap FOUR Values:")
        for v in [Belnap.T, Belnap.B, Belnap.F, Belnap.N]:
            print(f"  {v.name}: meet={meet(v, Belnap.T).name}, "
                  f"join={join(v, Belnap.F).name}, "
                  f"not={bnot(v).name}")
        print(f"\nDesignated: {[v.name for v in [Belnap.T, Belnap.B]]}")
        return 0

    if cmd in ("genetics", "genetic"):
        print("Genetic Code — B4 Lattice (64 codons):")
        try:
            demo()
        except Exception:
            # Fallback: show a few codons
            for codon in ["AUG", "UAA", "UGA", "UAG", "UUU", "AAA"]:
                bc = get_codon(codon)
                if bc:
                    print(f"  {codon}: {bc}")
        return 0

    if cmd == "verify":
        print("Running ALL B3 Frobenius verifications...")
        results = run_all_verifications()
        all_pass = all(v.get("passed", False) for v in results.values())
        for name, result in results.items():
            status = "✓" if result.get("passed") else "✗"
            print(f"  {status} {name}: {result.get('message', '')}")
        print(f"\n{'ALL PASS' if all_pass else 'SOME FAILED'}")
        return 0 if all_pass else 1

    if cmd in ("hadrons", "hadron"):
        print("Testing Hadron Belnap...")
        try:
            test_hadron_belnap()
        except Exception as e:
            print(f"  build_meson_example: {build_meson_example()}")
            print(f"  build_baryon_example: {build_baryon_example()}")
            print(f"  test_tetraquark: {test_tetraquark()}")
            print(f"  test_glueball: {test_glueball()}")
        return 0

    if cmd in ("ligands", "ligand", "drugs"):
        enzyme = args.args[0] if args.args else "ADH"
        print(f"Generating ligands for enzyme: {enzyme}...")
        try:
            result = test_bevy(enzyme_type=enzyme) if hasattr(test_bevy, '__call__') else \
                     generate_from_enzyme_type(enzyme_type=enzyme)
            print(result)
        except Exception as e:
            print(f"Ligand generation failed: {e}")
        return 0

    print(f"Unknown command: {cmd}")
    parser.print_help()
    return 1


if __name__ == "__main__":
    _sys.exit(main())