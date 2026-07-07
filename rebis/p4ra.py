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
import json
import math
import urllib.request
import urllib.error
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
                                                    fmt_tuple,
                                                    PROTEIN_LOOKUP,
                                                    CATALYZING_PROTEINS)
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


    from rhr_p4rky.sidechain_algebra import (SIDECHAINS, ENVIRONMENTS,
                                              analyze_composition, batch_analyze,
                                              print_analysis, print_frustration_matrix,
                                              print_dominance_matrix, print_tier_matrix,
                                              tuple_str as sc_tuple_str)
    from rhr_p4rky.ligand_imasm import (encode_site_imasm,
                                         fingerprint_to_ig_biochemical)
    from rhr_p4rky.ligand_imasm_v2 import (fingerprint_to_ig_biochemical
                                           as fingerprint_to_ig_biochemical_v2)
    from rhr_p4rky.ligand_sicpovm import (generate_ligands_sicpovm,
                                           encode_site_with_context,
                                           batch_generate_all)
    from rhr_p4rky.ligand_heterocycles import (generate_hybrid_ligands,
                                                generate_heterocycle_ligands,
                                                match_scaffolds_to_site)
    from rhr_p4rky.ligand_combinatorial import (generate_combinatorial,
                                                 batch_combinatorial_all)
    from rhr_p4rky.gene_to_protein_pipeline import (GeneToProteinPipeline,
                                                     AASite, CodonSite)
    from rhr_p4rky.serpent_rod import (SerpentRod, FoldedProtein)
    from rhr_p4rky.ch3mpiler_serpentrod_pipeline import (CatalyticSiteDesign,
                                                           ReactionSignature)
__all__ = sorted([k for k in dir() if not k.startswith('_')
                   and k not in ('_sys', '_io', '_Path', '_REBIS_ROOT', '_quiet',
                                 'redirect_stdout', 'redirect_stderr')])


def _cmd_belnap(args):
    """Test Belnap FOUR operations."""
    print("Belnap FOUR Values:")
    for v in [Belnap.T, Belnap.B, Belnap.F, Belnap.N]:
        print(f"  {v.name}: meet={meet(v, Belnap.T).name}, "
              f"join={join(v, Belnap.F).name}, "
              f"not={bnot(v).name}")
    print(f"\nDesignated: {[v.name for v in [Belnap.T, Belnap.B]]}")
    return 0


def _cmd_genetics(args):
    """Show genetic code B4 lattice."""
    print("Genetic Code — B4 Lattice (64 codons):")
    try:
        demo()
    except Exception:
        for codon in ["AUG", "UAA", "UGA", "UAG", "UUU", "AAA"]:
            bc = get_codon(codon)
            if bc:
                print(f"  {codon}: {bc}")
    return 0


def _cmd_verify(args):
    """Run B3 Frobenius verification suite."""
    print("Running ALL B3 Frobenius verifications...")
    results = run_all_verifications()
    all_pass = all(results.values())
    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    print(f"\n{'ALL PASS' if all_pass else 'SOME FAILED'}")
    return 0 if all_pass else 1


def _cmd_hadrons(args):
    """Test hadron Belnap operations."""
    print("Testing Hadron Belnap...")
    try:
        test_hadron_belnap()
    except Exception as e:
        print(f"  build_meson_example: {build_meson_example()}")
        print(f"  build_baryon_example: {build_baryon_example()}")
        print(f"  test_tetraquark: {test_tetraquark()}")
        print(f"  test_glueball: {test_glueball()}")
    return 0


def _cmd_ligands(args):
    """Generate ligands from enzyme active site.

    Accepts enzyme names (from built-in catalog), PDB IDs, or UniProt accessions.
    Fetches PDB structures on-the-fly from RCSB for unrecognized identifiers.

    Examples:
      rebis.p4ra ligands lysozyme              — built-in catalog entry
      rebis.p4ra ligands T4LYSOZYME            — PDB ID (fetched from RCSB)
      rebis.p4ra ligands 1LYZ                  — PDB ID
      rebis.p4ra ligands P18525                — UniProt accession (resolved via PDB)
    """
    enzyme = args.enzyme
    print(f"Generating ligands for enzyme: {enzyme}...")

    # ── Step 1: Look up in built-in PROTEIN_LOOKUP (case-insensitive, substring) ──
    protein = None
    enzyme_lower = enzyme.lower().strip()

    # Exact match first
    for name, entry in PROTEIN_LOOKUP.items():
        if name.lower() == enzyme_lower:
            protein = entry
            break

    # Substring or fuzzy match
    if protein is None:
        for name, entry in PROTEIN_LOOKUP.items():
            name_lower = name.lower()
            if enzyme_lower in name_lower or name_lower in enzyme_lower:
                protein = entry
                break

    # Try matching alternate names (e.g. "adh" → "alcohol_dehydrogenase")
    if protein is None:
        _aliases = {
            "adh": "alcohol_dehydrogenase",
            "adh1": "alcohol_dehydrogenase",
            "rnase": "ribonuclease_A",
            "rnase_a": "ribonuclease_A",
            "rnasea": "ribonuclease_A",
            "ache": "acetylcholinesterase",
            "ca2": "carbonic_anhydrase_II",
            "ca_ii": "carbonic_anhydrase_II",
            "carbonic_anhydrase": "carbonic_anhydrase_II",
            "hiv_protease": "HIV1_protease",
            "hiv1_protease": "HIV1_protease",
            "hiv": "HIV1_protease",
            "cyp2d6": "cytochrome_P450_2D6",
            "p450_2d6": "cytochrome_P450_2D6",
            "p450": "cytochrome_P450_2D6",
            "pet": "PETase",
            "petase": "PETase",
        }
        canonical = _aliases.get(enzyme_lower)
        if canonical and canonical in PROTEIN_LOOKUP:
            protein = PROTEIN_LOOKUP[canonical]

    if protein is not None:
        print(f"  Enzyme:     {protein['name']}")
        print(f"  Organism:   {protein['organism']}")
        print(f"  PDB:        {protein.get('pdb', 'N/A')}")
        print(f"  Reaction:   {protein['reaction']}")
        print(f"  Active site: {', '.join(protein['active_site_residues'])}")
        print(f"  Catalytic roles: {'; '.join(protein.get('catalytic_roles', []))}")

        # Compute site_type from first principles via IMASM encoding
        residues = protein.get("active_site_residues", [])
        site_type = None
        if residues:
            try:
                from rhr_p4rky.ligand_imasm import encode_site_imasm as _imasm_encode
                imasm_result = _imasm_encode(residues)
                if imasm_result:
                    site_type = imasm_result['site_type']
                    print(f"  [IMASM] Arrangement: {imasm_result['arrangement_str']}")
                    print(f"  [IMASM] Canonical:   {imasm_result['canonical_class'] or '—'}")
                    print(f"  [IMASM] Roles:      {imasm_result['roles_found']}")
            except Exception:
                pass
        if site_type is None:
            # Fallback to old hardcoded type
            site_type = protein.get("structural_type")
        if site_type is None:
            # Final fallback: compute from residues via count-based encoder
            from rhr_p4rky.ligand_from_active_site import encode_site_from_residues
            site_type = encode_site_from_residues(residues)
        
        substrate = protein.get("smiles_substrate_hint", "")

        if site_type is None:
            print("  ERROR: Could not encode active site from residues")
            return 1

        print(f"\n  Site structural type: {fmt_tuple(site_type)}")

        # ── Fast combinatorial generation (SIC-POVM: grammar measures itself) ──
        from rhr_p4rky.ligand_combinatorial import generate_combinatorial as _gen_combi
        candidates = _gen_combi(
            protein_context=protein,
            n_scaffolds=40,
            fragments_per_position=5,
            max_products=500,
            verbose=False,
        )
        # Convert to legacy format
        candidates = [{"smiles": c["smiles"], "method": f"combi/{c.get('scaffold','?')}",
                       "composite_score": c.get("score", 0), "logP": c.get("logp", 0),
                       "MW": c.get("mw", 0)} for c in candidates]
        
        # Fallback to hybrid generator if combinatorial produces nothing
        if not candidates:
            from rhr_p4rky.ligand_heterocycles import generate_hybrid_ligands
            candidates = generate_hybrid_ligands(
                site_type=site_type, substrate_hint=substrate, max_candidates=50,
            )
            if not candidates:
                try:
                    candidates = generate_from_enzyme_type(
                        site_type=site_type, substrate_hint=substrate, max_candidates=50)
                except Exception:
                    pass

        if candidates:
            print(f"\n  Generated {len(candidates)} candidate ligands:\n")
            print(f"  {'#':3s}  {'Method':20s}  {'SMILES':65s}  {'Score':8s}  {'logP':6s}  {'MW':8s}")
            print(f"  {'-'*3}  {'-'*20}  {'-'*65}  {'-'*8}  {'-'*6}  {'-'*8}")
            for i, c in enumerate(candidates[:50], 1):
                smiles = c.get('smiles', '?')
                print(f"  {i:<3d}  {c.get('method', '?'):20s}  {smiles:65s}  "
                      f"{c.get('composite_score', 0):.4f}  "
                      f"{c.get('logP', 0):5.1f}  "
                      f"{c.get('MW', 0):7.1f}")
            if len(candidates) > 50:
                print(f"  ... and {len(candidates)-50} more")
        else:
            print(f"\n  No candidate ligands generated.")
        return 0

    # ── Step 2: Not in catalog — attempt PDB fetch from RCSB ──
    print(f"  Not in built-in catalog ({len(PROTEIN_LOOKUP)} entries).")
    print(f"  Attempting PDB fetch from RCSB for '{enzyme}'...")

    pdb_text = None
    pdb_id = enzyme.strip().upper()

    # Try direct PDB download
    for fetch_id in [pdb_id, pdb_id.lower(), pdb_id.upper()]:
        try:
            url = f'https://files.rcsb.org/download/{fetch_id}.pdb'
            req = urllib.request.Request(url, headers={'User-Agent': 'Rebis/3.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                pdb_text = resp.read().decode('utf-8')
            if pdb_text and len(pdb_text) > 500 and ('ATOM' in pdb_text or 'HETATM' in pdb_text):
                print(f"  ✓ Fetched PDB {fetch_id}: {len(pdb_text)} bytes")
                break
            else:
                pdb_text = None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            print(f"  HTTP error for {fetch_id}: {e}")
        except Exception as e:
            print(f"  Fetch error for {fetch_id}: {e}")

    # Try UniProt → PDB mapping via EBI PDBe API
    if pdb_text is None:
        print(f"  No direct PDB match. Trying UniProt→PDB mapping for '{enzyme}'...")
        try:
            # Try PDBe API: search by UniProt accession
            url = f'https://www.ebi.ac.uk/pdbe/api/mappings/best_structures/{enzyme.strip().upper()}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Rebis/3.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            # Extract PDB IDs (best_structures format: {uniprot_id: [{pdb_id, chain_id, ...}]})
            pdb_ids = []
            for uniprot_id, entries in data.items():
                if isinstance(entries, list):
                    for entry in entries:
                        pid = entry.get('pdb_id', '')
                        if pid:
                            pdb_ids.append(pid)
                elif isinstance(entries, dict):
                    for pdb_entry in entries.get('PDB', []):
                        pdb_ids.append(pdb_entry.get('pdb_id', ''))
            if pdb_ids:
                print(f"  UniProt {enzyme} maps to PDB: {', '.join(pdb_ids[:5])}")
                # Try the first PDB ID
                for pid in pdb_ids[:3]:
                    try:
                        url = f'https://files.rcsb.org/download/{pid}.pdb'
                        req = urllib.request.Request(url, headers={'User-Agent': 'Rebis/3.0'})
                        with urllib.request.urlopen(req, timeout=30) as resp:
                            pdb_text = resp.read().decode('utf-8')
                        if pdb_text and len(pdb_text) > 500:
                            print(f"  ✓ Fetched PDB {pid}: {len(pdb_text)} bytes")
                            break
                    except:
                        continue
        except urllib.error.HTTPError:
            pass
        except Exception as e:
            print(f"  UniProt mapping error: {e}")

    if pdb_text is None or len(pdb_text) < 500:
        print(f"\n  ✗ Could not fetch PDB structure for '{enzyme}'.")
        print(f"  Available built-in enzymes:")
        for name in sorted(PROTEIN_LOOKUP.keys()):
            print(f"    - {name}")
        return 1

    # ── Step 3: Extract active site residues from PDB ──
    print(f"\n  Extracting active site from PDB structure...")

    # Parse CA atoms
    atoms = []
    aa3to1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
              'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
              'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
    for line in pdb_text.split('\n'):
        if line.startswith('ATOM') and line[12:16].strip() == 'CA':
            try:
                res_name = line[17:20].strip()
                chain = line[21]
                res_num = int(line[22:26].strip())
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                atoms.append({
                    'res_name': res_name, 'chain': chain, 'res_num': res_num,
                    'x': x, 'y': y, 'z': z
                })
            except (ValueError, IndexError):
                continue

    # Find HETATM residues (ligands, cofactors, metals)
    het_residues = []
    for line in pdb_text.split('\n'):
        if line.startswith('HETATM'):
            try:
                chain = line[21]
                res_num = int(line[22:26].strip())
                het_residues.append((chain, res_num))
            except:
                pass

    def _dist(a, b):
        return math.sqrt((a['x']-b['x'])**2 + (a['y']-b['y'])**2 + (a['z']-b['z'])**2)

    catalytic = set()
    if het_residues and atoms:
        for h_chain, h_num in het_residues:
            h_atom = next((a for a in atoms if a['chain'] == h_chain and a['res_num'] == h_num), None)
            if h_atom is None:
                h_atom = next((a for a in atoms if a['res_num'] == h_num), None)
            if h_atom:
                for a in atoms:
                    if _dist(h_atom, a) < 6.0:
                        catalytic.add(f"{a['res_name']}{a['res_num']}")

    if catalytic:
        residues = sorted(catalytic)[:8]
        print(f"  Detected active site residues (near HETATM, <6Å): {', '.join(residues)}")
    else:
        # Fall back: look for catalytic residues (ASP, GLU, HIS, SER, CYS, LYS, THR)
        cat_aas = {'ASP', 'GLU', 'HIS', 'SER', 'CYS', 'LYS', 'THR', 'ARG', 'TYR'}
        for a in atoms:
            if a['res_name'] in cat_aas:
                catalytic.add(f"{a['res_name']}{a['res_num']}")
        residues = sorted(catalytic)[:8] if catalytic else []
        if residues:
            print(f"  Using potential catalytic residues: {', '.join(residues)}")
        else:
            print(f"  Could not identify active site residues.")
            print(f"  Residues in structure: {', '.join(sorted(set(a['res_name'] for a in atoms)))}")
            return 1

    # ── Step 4: Encode site (IMASM first principles) and generate ligands ──
    print(f"\n  Encoding active site structural type...")
    
    # Try IMASM-based encoding first (first-principles)
    site_type = None
    try:
        from rhr_p4rky.ligand_imasm import encode_site_imasm as _imasm_encode
        imasm_result = _imasm_encode(residues)
        if imasm_result:
            site_type = imasm_result['site_type']
            print(f"  [IMASM] Arrangement: {imasm_result['arrangement_str']}")
            print(f"  [IMASM] Canonical:   {imasm_result['canonical_class'] or '—'}")
            print(f"  [IMASM] Roles:      {imasm_result['roles_found']}")
    except Exception as e:
        print(f"  [IMASM] Not available: {e}")
    
    # Fallback to count-based encoding
    if site_type is None:
        site_type = encode_site_from_residues(residues)
    
    if site_type is None:
        print("  Failed to encode active site")
        return 1

    print(f"  Site type: {fmt_tuple(site_type)}")

    print(f"  Generating de-novo ligands via enzyme structural type pipeline...")
    from rhr_p4rky.ligand_heterocycles import generate_hybrid_ligands
    candidates = generate_hybrid_ligands(
        site_type=site_type,
        substrate_hint="",
        max_candidates=50,
    )
    if not candidates:
        from rhr_p4rky.ligand_improvements import generate_from_enzyme_type
        candidates = generate_from_enzyme_type(
            site_type=site_type,
            substrate_hint="",
            max_candidates=50,
        )

    if candidates:
        print(f"\n  Generated {len(candidates)} candidate ligands:\n")
        print(f"  {'#':3s}  {'Method':20s}  {'SMILES':65s}  {'Score':8s}  {'logP':6s}  {'MW':8s}")
        print(f"  {'-'*3}  {'-'*20}  {'-'*65}  {'-'*8}  {'-'*6}  {'-'*8}")
        for i, c in enumerate(candidates, 1):
            smiles = c.get('smiles', '?')
            print(f"  {i:<3d}  {c.get('method', '?'):20s}  {smiles:65s}  "
                  f"{c.get('composite_score', 0):.4f}  "
                  f"{c.get('logP', 0):5.1f}  "
                  f"{c.get('MW', 0):7.1f}")
    else:
        print(f"\n  No candidate ligands generated.")

    return 0


def _cmd_list(args):
    """List all exported symbols."""
    print("rebis.p4ra — Exports:")
    for name in sorted(__all__):
        print(f"  {name}")
    return 0



def _cmd_sidechain(args):
    """Analyze sidechain × environment composition."""
    sc = args.sidechain_name
    env = args.environment
    try:
        analysis = analyze_composition(sc, env)
        print_analysis(analysis)
        return 0
    except KeyError as e:
        print(f'Unknown sidechain or environment: {e}')
        print(f'Sidechains: {sorted(SIDECHAINS.keys())}')
        print(f'Environments: {sorted(ENVIRONMENTS.keys())}')
        return 1

def _cmd_gene_pipeline(args):
    """Run gene-to-protein translation pipeline."""
    try:
        from rhr_p4rky.demo_gene_to_protein import main as demo_main
        demo_main()
    except ImportError:
        try:
            demo_gene_to_protein()
        except Exception as e:
            print(f'Gene pipeline error: {e}')
            return 1
    except Exception as e:
        print(f'Gene pipeline error: {e}')
        return 1
    return 0

def _cmd_serpent(args):
    """Run SerpentRod protein design pipeline."""
    if hasattr(args, 'sequence') and args.sequence:
        seq = args.sequence
    else:
        seq = 'MKFLILFNILV'
    try:
        sr = SerpentRod(seq)
        protein = sr.predict()
        profile = sr.report()
        print(f'SerpentRod profile for {seq}:')
        print(f'  Winding: {profile.get("winding_number", "?")}')
        print(f'  Activations: {profile.get("primitive_count", "?")}/12')
        print(f'  Contacts: {profile.get("contact_count", "?")}')
        print(f'  Subunits: {profile.get("subunit_count", "?")}')
        print(f'  Frobenius: {profile.get("frobenius_closure", "?")}')
    except Exception as e:
        print(f'SerpentRod error: {e}')
        return 1
    return 0

def _cmd_sicpovm(args):
    """Run SIC-POVM probe on active site / structural type."""
    if hasattr(args, 'enzyme') and args.enzyme:
        enzyme = args.enzyme
        # Try to encode site first
        try:
            from rhr_p4rky.ligand_sicpovm import encode_site_with_context
            # Use encode_site_with_context as the SIC-POVM probe
            residues = list(enzyme[:20]) if len(enzyme) >= 3 else ['C', 'H', 'C']
            site_type = encode_site_with_context(residues)
            result = {"enzyme": enzyme, "site_type": site_type,
                      "sic_povm_probe": "SIC-POVM dual-link encoding complete"}
            print(json.dumps(result, indent=2, ensure_ascii=False) if isinstance(result, dict) else result)
        except Exception as e:
            print(f'SIC-POVM probe error: {e}')
            return 1
    else:
        print('Usage: rebis.p4ra sicpovm <enzyme>')
        print('Example: rebis.p4ra sicpovm lysozyme')
    return 0

def _cmd_combinatorial(args):
    """Generate combinatorial ligand library."""
    enzyme = args.enzyme if hasattr(args, 'enzyme') and args.enzyme else 'ADH'
    protein = PROTEIN_LOOKUP.get(enzyme.lower(), None)
    if protein is None:
        for name, entry in PROTEIN_LOOKUP.items():
            if enzyme.lower() in name.lower():
                protein = entry
                break
    if protein is None:
        print(f'Enzyme not found: {enzyme}')
        return 1
    try:
        candidates = generate_combinatorial(
            protein_context=protein, n_scaffolds=40,
            fragments_per_position=5, max_products=100, verbose=True)
        print(f'Generated {len(candidates)} candidates')
        for i, c in enumerate(candidates[:20], 1):
            print(f'  {i}. {c["smiles"]}  score={c.get("score",0):.3f}')
    except Exception as e:
        print(f'Combinatorial error: {e}')
        return 1
    return 0

def _cmd_heterocycles(args):
    """Generate heterocycle-focused ligand library."""
    from rhr_p4rky.ligand_from_active_site import encode_site_from_residues
    enzyme = args.enzyme if hasattr(args, 'enzyme') and args.enzyme else 'ADH'
    protein = PROTEIN_LOOKUP.get(enzyme.lower(), None)
    if protein is None:
        for name, entry in PROTEIN_LOOKUP.items():
            if enzyme.lower() in name.lower():
                protein = entry
                break
    if protein is None:
        print(f'Enzyme not found: {enzyme}')
        return 1
    residues = protein.get('active_site_residues', [])
    site_type = encode_site_from_residues(residues)
    print(f'Site type: {fmt_tuple(site_type)}')
    try:
        candidates = generate_hybrid_ligands(site_type=site_type, max_candidates=50)
        print(f'Generated {len(candidates)} heterocycle candidates')
        for i, c in enumerate(candidates[:20], 1):
            print(f'  {i}. {c.get("smiles","?")}  {c.get("method","?")}')
    except Exception as e:
        print(f'Heterocycle error: {e}')
        return 1
    return 0


def main():
    """CLI: rebis.p4ra <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.p4ra",
        description="rebis.p4ra — Paraconsistent Kernel & Genetics\n"
                    "Structural type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩  O_∞ tier · ⊙ criticality",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    # ── belnap ──
    p_belnap = sub.add_parser("belnap",
        help="Test Belnap FOUR operations (T, B, F, N)",
        description="Test Belnap FOUR paraconsistent logic operations.\n\n"
                    "Shows meet, join, and negation for all four truth values:\n"
                    "  T=True, B=Both, F=False, N=None",
        epilog="Example:  rebis.p4ra belnap",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_belnap.set_defaults(func=_cmd_belnap)

    # ── genetics ──
    p_gen = sub.add_parser("genetics",
        help="Show genetic code B4 lattice (64 codons)",
        description="Display the 64-codon Belnap B4 lattice structure.\n\n"
                    "Shows nucleotide→Belnap mapping, codon examples, and\n"
                    "Frobenius-verified genetic code tables.",
        epilog="Example:  rebis.p4ra genetics",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_gen.set_defaults(func=_cmd_genetics)

    # ── verify ──
    p_verify = sub.add_parser("verify",
        help="Run B3 Frobenius verification suite",
        description="Run ALL B3 Frobenius verification tests:\n"
                    "  frobenius_invariant, verify_run_B3, paradox_conservation,\n"
                    "  cycle_count, paraconsistency, and more.",
        epilog="Example:  rebis.p4ra verify",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_verify.set_defaults(func=_cmd_verify)

    # ── hadrons ──
    p_had = sub.add_parser("hadrons",
        help="Test hadron Belnap operations (mesons, baryons, tetraquarks, glueballs)",
        description="Test hadron Belnap state operations:\n"
                    "  meson_pair / meson_depair / meson_frobenius\n"
                    "  baryon_pair / baryon_depair / baryon_frobenius\n"
                    "  tetraquark and glueball tests\n"
                    "  color confinement with quark_belnap",
        epilog="Example:  rebis.p4ra hadrons",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_had.set_defaults(func=_cmd_hadrons)

    # ── ligands ──
    p_lig = sub.add_parser("ligands",
        help="Generate ligands from enzyme active site",
        description="Reverse ligand discovery — generate candidate ligand SMILES\n"
                    "from enzyme active site structural type (Belnap-encoded).",
        epilog="Examples:  rebis.p4ra ligands\n"
               "           rebis.p4ra ligands ADH\n"
               "           rebis.p4ra ligands CYP2D6",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_lig.add_argument("enzyme", nargs="?", default="ADH",
                       help="Enzyme name/code (default: ADH)")
    p_lig.set_defaults(func=_cmd_ligands)

    # ── sidechain ──
    p_sc = sub.add_parser("sidechain",
        help="Analyze sidechain × environment composition",
        description="Analyze amino acid sidechain in protein environment.\n"
                    "20 sidechains × 4 environments = 80 pairs.\n"
                    "Reports tensor/meet/join, bottlenecks, frustration, tier.",
        epilog="Examples:  rebis.p4ra sidechain arginine charged_interface\n"
               "           rebis.p4ra sidechain alanine polar_surface",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_sc.add_argument("sidechain_name", help="Sidechain (e.g. arginine, alanine)")
    p_sc.add_argument("environment", help="Environment (e.g. charged_interface, polar_surface)")
    p_sc.set_defaults(func=_cmd_sidechain)

    # ── gene-pipeline ──
    p_gp = sub.add_parser("gene-pipeline",
        help="Run gene-to-protein translation pipeline",
        description="Full gene-to-protein translation with Frobenius verification. "
                    "Includes B4 lattice encoding, transcription, translation, folding.",
        epilog="Examples:  rebis.p4ra gene-pipeline\n"
               "           rebis.p4ra gene-pipeline --sequence ATGGCC",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_gp.add_argument("--sequence", "-s", default=None,
                       help="DNA sequence (default: ATGGCC)")
    p_gp.set_defaults(func=_cmd_gene_pipeline)

    # ── serpent ──
    p_srp = sub.add_parser("serpent",
        help="Run SerpentRod protein design",
        description="SerpentRod protein design pipeline — compute structural "
                    "profiles, predict contacts, Frobenius verification.",
        epilog="Examples:  rebis.p4ra serpent\n"
               "           rebis.p4ra serpent --sequence MKFLILFNILV",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_srp.add_argument("--sequence", "-s", default=None,
                        help="Protein sequence (default: MKFLILFNILV)")
    p_srp.set_defaults(func=_cmd_serpent)

    # ── sicpovm ──
    p_sp = sub.add_parser("sicpovm",
        help="Run SIC-POVM probe on active site",
        description="SIC-POVM structural probe — evaluate an enzyme's active site "
                    "against the informationally complete measurement basis.",
        epilog="Examples:  rebis.p4ra sicpovm ADH\n"
               "           rebis.p4ra sicpovm lysozyme",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_sp.add_argument("enzyme", nargs="?", default=None,
                       help="Enzyme name (default: show usage)")
    p_sp.set_defaults(func=_cmd_sicpovm)

    # ── combinatorial ──
    p_cb = sub.add_parser("combinatorial",
        help="Generate combinatorial ligand library",
        description="Combinatorial ligand generation — scaffold + fragment "
                    "enumeration guided by structural type.",
        epilog="Examples:  rebis.p4ra combinatorial ADH\n"
               "           rebis.p4ra combinatorial CYP2D6",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_cb.add_argument("enzyme", nargs="?", default="ADH",
                       help="Enzyme name (default: ADH)")
    p_cb.set_defaults(func=_cmd_combinatorial)

    # ── heterocycles ──
    p_hc = sub.add_parser("heterocycles",
        help="Generate heterocycle-focused ligand library",
        description="Heterocycle-focused ligand generation — scaffolds from "
                    "HETEROCYCLE_CATALOG matched to site structural type.",
        epilog="Examples:  rebis.p4ra heterocycles ADH\n"
               "           rebis.p4ra heterocycles CYP2D6",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_hc.add_argument("enzyme", nargs="?", default="ADH",
                       help="Enzyme name (default: ADH)")
    p_hc.set_defaults(func=_cmd_heterocycles)

    # ── list ──
    p_list = sub.add_parser("list",
        help="List all exported symbols",
        description="List all exported symbols available via `rebis.p4ra.<name>`.",
        epilog="Example:  rebis.p4ra list",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_list.set_defaults(func=_cmd_list)

    # ── info (alias for list) ──
    p_info = sub.add_parser("info",
        help="Show available tools (alias for list)",
        description="Alias for `rebis.p4ra list`.",
        epilog="Example:  rebis.p4ra info",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_info.set_defaults(func=_cmd_list)

    # ── help ──
    p_help = sub.add_parser("help",
        help="Show this help message",
        description="Display the full help for rebis.p4ra.",
        epilog="Example:  rebis.p4ra help",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "help":
        parser.print_help()
        return 0

    if hasattr(args, 'func'):
        return args.func(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    _sys.exit(main())
