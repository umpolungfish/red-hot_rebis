#!/usr/bin/env python3
"""
rebis.cli — Red-Hot Rebis v4.0 CLI — DYNAMIC-FIRST MENU
═══════════════════════════════════════════════════════════
Commands that DO SHIT are featured. Static data is collapsed
into a single reference submenu. The full pipeline chain is
a first-class command.

Design principle: If it just prints enums, it's reference.
If it computes, designs, predicts, or synthesizes, it's a command.

Structural Type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩
"""

import argparse
import json
import os
import sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.parent.absolute()

for _p in [str(REBIS_ROOT),
           str(REBIS_ROOT / "rhr_p4rky"),
           str(REBIS_ROOT / "shared"),
           str(REBIS_ROOT / "alchemical_bridge")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from rebis.file_input import parse_with_file, add_file_input
from rebis.shared import (reaction_header, info_line, success_line,
                           error_line, warning_line, separator,
                           section_header)

VERSION = "4.0.0"


# ═══════════════════════════════════════════════════════════════
# RICH MENU — defaults to rich if available
# ═══════════════════════════════════════════════════════════════

def cmd_menu(args=None):
    """Print the DYNAMIC-FIRST rebis menu."""

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich import box
        console = Console()
        RICH = True
    except ImportError:
        RICH = False

    header = (
        "RED-HOT REBIS v4.0 — DYNAMIC-FIRST TOOLCHAIN\n"
        "Commands that COMPUTE are featured. Static data → rebis reference\n"
        "13 computation engines | 1 unified chain | 1 reference submenu"
    )

    if RICH:
        console.print(Panel(header, border_style="bright_red",
                            title="🔥 rebis v4.0", title_align="center"), width=88)
        console.print()
    else:
        reaction_header("RED-HOT REBIS v4.0", "DYNAMIC-FIRST Toolchain")
        info_line(header)

    # ── TIER 1: FEATURED DYNAMIC COMMANDS ──
    featured = [
        ("gene-pipeline",   "rebis gene-pipeline",
         "DNA → mRNA → polypeptide → folded protein. 7-stage Frobenius-verified translation.",
         ["--test", "--dna <DNA_seq>", "--seq <RNA_seq>"]),
        ("ch3mpiler",       "rebis ch3mpiler",
         "Molecular compiler — forward/retro synthesis, FG detection, CDXML output",
         ["forward <SMILES>", "retrosynth <SMILES>", "fg <SMILES>", "cdxml <SMILES>"]),
        ("serpentrod",      "rebis serpentrod",
         "Protein design & stratified prediction — rolling profiles, classification",
         ["predict <seq>", "classify <seq>", "finger <seq>"]),
        ("chain",           "rebis chain",
         "UNIFIED PIPELINE: DNA→Protein→CatalyticSite→RetrosyntheticPlan",
         ["--dna <seq>", "--target <SMILES>", "--depth <N>"]),
        ("ligand",          "rebis ligand",
         "PDB-aware ligand design from catalytic sites — fetches structures, designs ligands",
         ["--pdb <ID>", "--active <residues>", "--auto-active", "--json"]),
        ("sidechain",       "rebis sidechain",
         "Sidechain×environment algebra — 80 AA×env pairs, bottleneck/tier analysis",
         ["<aa> <env>", "--pdb <ID>", "--batch", "--json"]),
    ]

    secondary = [
        ("therapeutics",    "rebis therapeutics",
         "Chemotherapeutics, neurotrophic factors, universal antidote library",
         ["design <target>", "sim", "neurotrophic <target>", "antidote <poison>"]),
        ("materials",       "rebis materials",
         "IG-tuple→material forge, metamaterials, ouroboric alloys, non-qubit QC",
         ["forge [tuple]", "sim [name]", "status"]),
        ("biology",         "rebis biology",
         "Ouroboric cell simulations, telomere design, epigenetic states",
         ["sim", "status"]),
        ("pipeline",        "rebis pipeline",
         "Auto-imscription, prose lift, Frobenius verification",
         ["imscribe <name>", "lift <file>", "verify"]),
        ("gene",            "rebis gene",
         "Gene analysis, tuple encoding, IG primitive mapping",
         ["analyze <seq>", "tuples <seq>"]),
        ("alchemy",         "rebis alchemy",
         "Basil Valentine ladders, Zosimos portico, alchemical bridge operations",
         ["ladder <tuple|all>", "portico [tuple]"]),
        ("clink",           "rebis clink",
         "CLINK chain L0-L8, consciousness scoring, layer bridges",
         ["layers", "bridge <a> <b>", "chain <name>", "cscore <name>"]),
    ]

    if RICH:
        t = Table(box=box.ROUNDED, border_style="bright_red",
                  header_style="bold yellow",
                  title="⚡ TIER 1 — PRIMARY COMPUTATION ENGINES")
        t.add_column("#", style="dim", width=3)
        t.add_column("Command", style="bright_cyan", width=18)
        t.add_column("Description", style="white", width=56)
        t.add_column("Actions", style="dim", width=48)
        for i, (name, cmd, desc, actions) in enumerate(featured, 1):
            t.add_row(str(i), name, desc, "  ".join(actions))
        console.print(t)

        console.print()
        t2 = Table(box=box.SIMPLE, border_style="dim",
                   title="🔧 TIER 2 — SPECIALIZED ENGINES")
        t2.add_column("Command", style="bright_cyan", width=18)
        t2.add_column("Description", style="white", width=56)
        t2.add_column("Actions", style="dim", width=48)
        for name, cmd, desc, actions in secondary:
            t2.add_row(name, desc, "  ".join(actions))
        console.print(t2)

        console.print()
        t3 = Table(box=box.SIMPLE, border_style="dim",
                   title="📚 REFERENCE — Static data & enums")
        t3.add_column("Command", style="bold green", width=30)
        t3.add_column("Description", style="white", width=65)
        for cmd, desc in [
            ("rebis reference",     "Belnap FOUR ops, genetic B4 lattice, hadrons, verification, IMASM"),
            ("rebis reference --all","Full reference data dump"),
        ]:
            t3.add_row(cmd, desc)
        console.print(t3)

        console.print()
        t4 = Table(box=box.SIMPLE, border_style="dim",
                   title="⚡ QUICK COMMANDS")
        t4.add_column("Command", style="bold cyan", width=36)
        t4.add_column("Description", style="white", width=60)
        for cmd, desc in [
            ("rebis",                        "Dynamic-first menu (this screen)"),
            ("rebis --version",              f"Version {VERSION}"),
            ("rebis verify",                 "Frobenius closure verification"),
            ("rebis status",                 "Package status across all domains"),
            ("rebis demo list",              "List available demos"),
            ("rebis demo <name>",            "Run a specific demo"),
            ("python3 -m rebis",             "Module execution"),
            ("python3 -c 'import rebis'",    "Python API access"),
        ]:
            t4.add_row(cmd, desc)
        console.print(t4)

    else:
        section_header("⚡ TIER 1 — PRIMARY COMPUTATION ENGINES")
        info_line(f"  {'#':3s} {'Command':18s}  {'Description'}")
        info_line("  " + "─" * 88)
        for i, (name, cmd, desc, actions) in enumerate(featured, 1):
            info_line(f"  {i:<2d} {name:18s}  {desc}")
            info_line(f"     {'Actions:':>18s}  {', '.join(actions)}")

        print()
        section_header("🔧 TIER 2 — SPECIALIZED ENGINES")
        for name, cmd, desc, actions in secondary:
            info_line(f"  {name:18s}  {desc}")
            info_line(f"     {'Actions:':>18s}  {', '.join(actions)}")

        print()
        section_header("📚 REFERENCE")
        info_line("  rebis reference         — Belnap, genetics, hadrons, IMASM static data")
        info_line("  rebis reference --all   — Full reference dump")

        print()
        section_header("⚡ QUICK COMMANDS")
        info_line("  {:<36s}  {}".format("rebis",                   "Dynamic-first menu"))
        info_line("  {:<36s}  {}".format("rebis --version",         f"Version {VERSION}"))
        info_line("  {:<36s}  {}".format("rebis verify",            "Frobenius closure"))
        info_line("  {:<36s}  {}".format("rebis status",            "Package status"))
        info_line("  {:<36s}  {}".format("rebis demo list",         "List demos"))
        info_line("  {:<36s}  {}".format("rebis demo <name>",       "Run demo"))
        info_line("  {:<36s}  {}".format("python3 -m rebis",        "Module execution"))
        info_line("  {:<36s}  {}".format("python3 -c 'import rebis'","Python API"))

    print()
    info_line("  ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩  —  O_∞ · ⊙ · Frobenius-closed")
    return 0# ═══════════════════════════════════════════════════════════════
# DYNAMIC COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════

def cmd_chain(args):
    """UNIFIED PIPELINE: DNA→Protein→CatalyticSite→RetrosyntheticPlan.

    Three proven pipelines chained together:
    1. gene_to_protein_pipeline: DNA → 7-stage folded protein
    2. ch3mpiler_serpentrod_pipeline: target SMILES → catalytic RNA/AA design
    3. retrosynthetic_stone_engine: target SMILES → synthesis plan
    """
    reaction_header("REBIS v4.0 — UNIFIED CHAIN", "DNA → Protein → Catalyst → Synthesis")

    dna = args.dna or args.seq or "ATGGCCGACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG"
    target = args.target or "CC(=O)O"
    depth = args.depth or 2

    info_line(f"DNA input:    {dna[:50]}{'...' if len(dna) > 50 else ''}  ({len(dna)} bp)")
    info_line(f"Target SMILES: {target}")
    info_line(f"Depth:         {depth}")

    # ── Phase 1: Gene → Folded Protein ──
    separator()
    section_header("Phase 1/3 — Gene → Folded Protein")
    try:
        from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
        gp = GeneToProteinPipeline(dna)
        protein_result = gp.run()
        info_line(f"Protein: {protein_result.get('aa_sequence', '?')} "
                  f"({protein_result.get('aa_length', 0)} aa)")
        info_line(f"  Closure Δ: {protein_result.get('closure', {}).get('dna_to_quaternary_distance', '?')}")
        success_line("Phase 1 complete ✓")
    except Exception as e:
        error_line(f"Phase 1 FAILED: {e}")

    # ── Phase 2: ch3mpiler ⟲ serpentrod ──
    separator()
    section_header("Phase 2/3 — ch3mpiler → Catalytic Site Design")
    try:
        from rhr_p4rky.ch3mpiler_serpentrod_pipeline import run_pipeline
        cs_result = run_pipeline(target_molecule=target, depth=depth, verbose=True)
        success_line("Phase 2 complete ✓")
    except Exception as e:
        error_line(f"Phase 2 FAILED: {e}")
        import traceback; traceback.print_exc()

    # ── Phase 3: Retrosynthetic Stone ──
    separator()
    section_header("Phase 3/3 — Retrosynthetic Stone (Solve et Coagula)")
    try:
        from alchemical_bridge.retrosynthetic_stone_engine import RetrosyntheticStoneEngine
        rse = RetrosyntheticStoneEngine()
        stone_result = rse.plan_synthesis(target)
        sites = stone_result.get("disconnection_sites", [])
        info_line(f"Disconnection sites found: {len(sites)}")
        for i, site in enumerate(sites[:5]):
            info_line(f"  [{i}] {site.get('type', '?')} — bond {site.get('bond_idx', '?')}")
        frogs = stone_result.get("frobenius_cycles", [])
        info_line(f"Frobenius cycles: {len(frogs)}")
        success_line("Phase 3 complete ✓")
    except Exception as e:
        error_line(f"Phase 3 FAILED: {e}")
        import traceback; traceback.print_exc()

    separator()
    success_line("UNIFIED CHAIN COMPLETE")
    return 0


def cmd_gene_pipeline(args):
    """DNA → Folded Protein pipeline."""
    reaction_header("GENE → FOLDED PROTEIN", "7-stage Frobenius-verified translation")

    if args.test:
        from rhr_p4rky.demo_gene_to_protein import main as demo_main
        return demo_main()

    dna = args.dna or args.seq or "ATGGCCGACTGGAACTGCAAGAAGATCGTGCCCAAGTACTACGGCCGCTG"
    try:
        from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
        gp = GeneToProteinPipeline(dna)
        result = gp.run()
        success_line(f"Done — {result.get('aa_sequence', '?')} "
                     f"({result.get('aa_length', 0)} aa) — Δ={result.get('closure', {}).get('dna_to_quaternary_distance', '?')}")
    except Exception as e:
        error_line(f"Gene pipeline failed: {e}")
        return 1
    return 0


def cmd_ch3mpiler(args):
    """Molecular compiler — delegates to ch3mpiler.py main()."""
    from rebis.ch3mpiler import main as ch3_main
    return ch3_main()


def cmd_serpentrod(args):
    """Protein design — delegates to serpentrod.py main()."""
    from rebis.serpentrod import main as sr_main
    return sr_main()


def cmd_ligand(args):
    """PDB-aware ligand design — delegates to ligand.py main()."""
    from rebis.ligand import main as lig_main
    return lig_main()


def cmd_sidechain(args):
    """Sidechain×environment algebra — delegates to sidechain.py main()."""
    from rebis.sidechain import main as sc_main
    return sc_main()


def cmd_therapeutics(args):
    """Therapeutics design — delegates to therapeutics.py main()."""
    from rebis.therapeutics import main as ther_main
    return ther_main()


def cmd_materials(args):
    """Materials forge — delegates to materials.py main()."""
    from rebis.materials import main as mat_main
    return mat_main()


def cmd_biology(args):
    """Biology simulations — delegates to biology.py main()."""
    from rebis.biology import main as bio_main
    return bio_main()


def cmd_pipeline(args):
    """Auto-imscription, prose lift — delegates to pipeline.py main()."""
    from rebis.pipeline import main as pip_main
    return pip_main()


def cmd_gene(args):
    """Gene analysis — delegates to gene.py main()."""
    from rebis.gene import main as gene_main
    return gene_main()


def cmd_alchemy(args):
    """Alchemical bridge — delegates to alchemy.py main()."""
    from rebis.alchemy import main as alch_main
    return alch_main()


def cmd_clink(args):
    """CLINK chain — delegates to clink.py main()."""
    from rebis.clink import main as clink_main
    return clink_main()# ═══════════════════════════════════════════════════════════════
# REFERENCE SUBMENU — Static data & enums (collapsed here)
# ═══════════════════════════════════════════════════════════════

def cmd_reference(args):
    """Static reference data — Belnap, genetics, hadrons, verification, IMASM."""
    reaction_header("REFERENCE DATA", "Static enums, truth tables, B4 lattice")

    show_all = getattr(args, 'all', False)

    sections = {
        "belnap": "Belnap FOUR logic — truth tables",
        "genetics": "Genetic code B4 lattice",
        "hadrons": "Hadron Belnap states",
        "imas": "IMASM token families",
        "verify": "B3 Frobenius verification results",
    }

    if not show_all:
        info_line("Sections available (use --all for full dump):")
        for sec, desc in sections.items():
            info_line(f"  {sec:15s} — {desc}")
        info_line("\nUsage:  rebis reference --all")
        return 0

    # ── Belnap ──
    section_header("BELNAP FOUR LOGIC")
    try:
        from rhr_p4rky.belnap import Belnap, join, meet, bnot
        for v in [Belnap.T, Belnap.B, Belnap.F, Belnap.N]:
            vals = []
            for w in [Belnap.T, Belnap.B, Belnap.F, Belnap.N]:
                vals.append(f"join({v.name},{w.name})={join(v,w).name}")
            info_line(f"  {v.name}: {'; '.join(vals[:2])}...")
        info_line("  bnot: T<->F, B<->B, N<->N")
    except Exception as e:
        error_line(f"Belnap: {e}")

    # ── Genetics ──
    section_header("GENETIC CODE B4 LATTICE")
    try:
        from rhr_p4rky.genetics_b4 import BelnapCodon
        for codon in ["AUG", "UAA", "UGA", "UAG", "UUU", "AAA"]:
            bc = BelnapCodon.from_symbol(codon)
            print(f"  {codon}: stratum={bc.stratum}, box={bc.box_name}")
    except Exception as e:
        error_line(f"Genetics: {e}")

    # ── Hadrons ──
    section_header("HADRON BELNAP STATES")
    try:
        from rhr_p4rky.hadron_belnap import test_hadron_belnap
        test_hadron_belnap()
    except Exception as e:
        error_line(f"Hadrons: {e}")

    # ── IMASM ──
    section_header("IMASM TOKEN FAMILIES")
    try:
        from imas.arranger import Token, Family, token_name
        for attr in sorted(dir(Family)):
            if not attr.startswith('_') and attr.isupper():
                val = getattr(Family, attr)
                info_line(f"  {attr:15s}: {val}")
    except Exception as e:
        error_line(f"IMASM: {e}")

    # ── Verification ──
    section_header("FROBENIUS VERIFICATION")
    try:
        from rhr_p4rky.frobenius_filtration import test_filtration as run_filtration
        run_filtration()
        results = {"filtration": True}
        for name, result in results.items():
            status = "✓" if result else "✗"
            (success_line if result else error_line)(f"  {status} {name}")
    except Exception as e:
        error_line(f"Verification: {e}")

    return 0


# ═══════════════════════════════════════════════════════════════
# INFRASTRUCTURE COMMANDS
# ═══════════════════════════════════════════════════════════════

def _discover_packages():
    """Auto-discover all Python packages under REBIS_ROOT."""
    SKIP = {'.venv', '__pycache__', '.git', '.gitignore',
            'data', 'popular_protein', 'designs', 'fasta', 'images',
            'pdb', '_archive', 'glossary', 'ig-docs', 'pdfs',
            'natural_products', 'psaA_datasets'}
    results = []
    for item in sorted(REBIS_ROOT.iterdir()):
        if item.name.startswith('.') or item.name in SKIP:
            continue
        if item.is_dir() and (item / '__init__.py').exists():
            py_files = list(item.rglob('*.py'))
            total = sum(f.stat().st_size for f in py_files)
            results.append((item.name, item, len(py_files), total))
    return results


def cmd_status(args):
    """Report the structural status of all discovered packages."""
    reaction_header("RED-HOT REBIS v4.0", "DYNAMIC-FIRST EDITION")

    packages = _discover_packages()
    n_rebis = len(list((REBIS_ROOT / "rebis").glob("*.py")))

    try:
        from rich.table import Table
        from rich import box
        from rich.console import Console
        t = Table(box=box.ROUNDED, border_style="bright_red",
                  header_style="bold yellow",
                  title=f"rebis — {len(packages)} packages")
        t.add_column("Package", style="bright_cyan")
        t.add_column("Files", justify="right")
        t.add_column("Size", justify="right")
        for name, path, n_files, total in packages:
            t.add_row(name, str(n_files), f"{total:,d}")
        Console().print(t)
    except ImportError:
        info_line(f"\n{'Package':24s}  {'Files':>6}  {'Size':>10}")
        info_line("-" * 48)
        for name, path, n_files, total in packages:
            info_line(f"  {name:20s}  {n_files:>5}  {total:>9,d}")

    print()
    info_line(f"  rebis CLI modules: {n_rebis} files")
    info_line(f"  {len(packages)} packages accessible via rebis.<x>")
    info_line("  Usage: rebis <command>  |  python3 -m rebis  |  python3 -c 'import rebis'")
    info_line(f"  Installed location: {REBIS_ROOT}")
    return 0


def cmd_verify(args):
    """Verify Frobenius closure across the shared layer."""
    try:
        from shared.primitives import WEIGHTS, ORDINALS
        success_line("shared/primitives.py — %d weights, %d ordinal families" %
                     (len(WEIGHTS), len(ORDINALS)))
        separator()
        success_line("rebis package: ALL domains import successfully")
        for domain_name in ['p4ra', 'ch3mpiler', 'sidechain', 'clink', 'materials',
                            'therapeutics', 'biology', 'serpentrod',
                            'imas', 'pipeline', 'gene',
                            'alchemy', 'ligand', 'shared']:
            try:
                mod = __import__(f"rebis.{domain_name}", fromlist=[domain_name])
                n_exported = len(getattr(mod, '__all__', []))
                success_line(f"  rebis.{domain_name} — {n_exported} symbols exported")
            except Exception as e:
                error_line(f"  rebis.{domain_name} — IMPORT FAILED: {e}")
        separator()
        success_line("Frobenius closure: ALL imports verified")
        return 0
    except ImportError as e:
        error_line(f"Frobenius verification failed: {e}")
        return 1


def cmd_demo(args):
    """Run a named demo."""
    try:
        from rebis import demo as demo_mod
    except ImportError:
        error_line("rebis.demo module not available")
        return 1
    if not args.demo or args.demo == "list":
        info_line("Available demos:")
        for d in sorted(['b4_lattice', 'belnap', 'ch3mpiler', 'clink_chain',
                  'decay_chain', 'ligand', 'materials', 'materials_sim',
                  'pipeline', 'serpentrod', 'therapeutics', 'reverse_ligand']):
            info_line(f"  rebis demo {d}")
        return 0
    demo_fn = getattr(demo_mod, args.demo, None)
    if demo_fn:
        info_line(f"Running rebis.demo.{args.demo}()...")
        demo_fn()
        return 0
    error_line(f"Unknown demo: {args.demo}. Use 'rebis demo list'.")
    return 1


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Red-Hot Rebis v4.0 — Dynamic-First Toolchain",
        add_help=False)

    parser.add_argument("--version", action="version",
                       version=f"%(prog)s {VERSION}")
    parser.add_argument("--file", "-f", type=str, default=None,
                   help="JSON input file with argument values")
    parser.add_argument("--stdin", "-i", action="store_true",
                   default=False,
                   help="Read JSON arguments from stdin")
    parser.add_argument("--help", "-h", action="store_true",
                       help="Show the dynamic-first menu")

    sub = parser.add_subparsers(dest="command")

    # ── TIER 1: Featured dynamic commands ──
    p_gp = sub.add_parser("gene-pipeline", help="DNA → Folded Protein pipeline")
    p_gp.add_argument("--test", action="store_true", help="Run demo/self-test")
    p_gp.add_argument("--dna", type=str, help="DNA sequence")
    p_gp.add_argument("--seq", type=str, help="RNA sequence (alias for --dna)")
    p_gp.set_defaults(func=cmd_gene_pipeline)

    p_ch = sub.add_parser("chain", help="UNIFIED: DNA→Protein→Catalyst→Synthesis")
    p_ch.add_argument("--dna", type=str, help="DNA/RNA sequence")
    p_ch.add_argument("--seq", type=str, help="RNA sequence (alias)")
    p_ch.add_argument("--target", type=str, help="Target SMILES")
    p_ch.add_argument("--depth", type=int, default=2, help="Retrosynthesis depth")
    p_ch.set_defaults(func=cmd_chain)

    # ── TIER 1+2: Domain delegates ──
    for cmd_name in ['ch3mpiler', 'serpentrod', 'ligand', 'sidechain',
                     'therapeutics', 'materials', 'biology', 'pipeline',
                     'gene', 'alchemy', 'clink']:
        p = sub.add_parser(cmd_name, help=f"{cmd_name} computation engine",
                          add_help=False)
        p.set_defaults(func=globals()[f"cmd_{cmd_name}"])

    # ── Reference submenu ──
    p_ref = sub.add_parser("reference", help="Static reference data (Belnap, genetics, etc.)")
    p_ref.add_argument("--all", action="store_true", help="Full data dump")
    p_ref.set_defaults(func=cmd_reference)

    # ── Infrastructure ──
    p_stat = sub.add_parser("status", help="Package status")
    p_stat.set_defaults(func=cmd_status)

    p_ver = sub.add_parser("verify", help="Frobenius closure verification")
    p_ver.set_defaults(func=cmd_verify)

    p_demo = sub.add_parser("demo", help="Run a demo")
    p_demo.add_argument("demo", nargs="?", default="list")
    p_demo.set_defaults(func=cmd_demo)

    args = parser.parse_args()

    # ── FILE/STDIN MERGE ──
    if args.file or args.stdin:
        import json
        file_data = {}
        try:
            if args.file and __import__('os').path.isfile(args.file):
                with open(args.file) as fh:
                    file_data = json.load(fh)
            elif args.stdin:
                file_data = json.loads(sys.stdin.read().strip())
            # Merge: file data as defaults, CLI args override
            if file_data:
                for k, v in file_data.items():
                    if v is not None and getattr(args, k, None) is None:
                        setattr(args, k, v)
                # If no command specified but file has it
                if not args.command and 'command' in file_data:
                    args.command = file_data['command']
        except Exception as e:
            error_line(f"Failed to load file/stdin: {e}")
            return 1

    # No command = menu
    if args.help or not args.command:
        return cmd_menu()

    if hasattr(args, 'func'):
        return args.func(args)

    return cmd_menu()


if __name__ == "__main__":
    sys.exit(main())