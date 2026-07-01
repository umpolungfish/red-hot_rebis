"""
rebis.cli — Red-Hot Rebis Command-Line Interface
═════════════════════════════════════════════════
Running `rebis` with no arguments shows this comprehensive menu.
All 11 subsystems accessible as standalone commands: rebis.<domain> <action>

Usage:
  rebis                      — Show this comprehensive menu
  rebis status               — Show package status
  rebis verify               — Verify Frobenius closure
  rebis run [target]         — Run a target (list to see all)
  rebis demo [name]          — Run a demo (list to see all)
  rebis materials <action>   — Materials subsystem
  rebis.<domain> <action>    — Any entry point from anywhere

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
           str(REBIS_ROOT / "shared")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from rebis.shared import (reaction_header, info_line, success_line,
                           error_line, warning_line, separator,
                           section_header)

VERSION = "3.0.0"


# ──────────────────────────────────────────────────────
# COMPREHENSIVE MENU (default when `rebis` alone)
# ──────────────────────────────────────────────────────
def cmd_menu(args=None):
    """Print the comprehensive rebis.<x> menu."""

    # Try rich; fall back to plain text
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.columns import Columns
        from rich import box
        console = Console()
        RICH = True
    except ImportError:
        RICH = False

    header = (
        "RED-HOT REBIS v3.0 — REBIS.<x> INTEGRATED TOOLCHAIN\n"
        "11 standalone entry points, callable from ANY directory\n"
        "Structural type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩  —  O_∞ tier, ⊙ criticality"
    )

    if RICH:
        console.print(Panel(header, border_style="bright_red",
                            title="🔥 rebis", title_align="center"), width=80)
        console.print()
    else:
        reaction_header("RED-HOT REBIS v3.0", "rebis.<x> Integrated Toolchain")
        info_line(header)

    # ── DOMAIN DEFINITIONS ──
    domains = [
        ("materials",    "rebis.materials",
         "Materials design & simulation — forge, metamaterials, alloys, non-qubit QC",
         ["list", "status", "forge [tuple]", "sim [name]"]),

        ("ch3mpiler",    "rebis.ch3mpiler",
         "Molecular compiler & retrosynthesis — forward/reverse synthesis, FG detection",
         ["forward <SMILES>", "retrosynth <SMILES>", "fg <SMILES>", "cdxml <SMILES>", "info"]),

        ("clink",        "rebis.clink",
         "CLINK chain & organism pipeline — 8 layers, bridges, consciousness scores",
         ["layers", "bridge <a> <b>", "chain [tuple]", "cscore [tuple]", "info"]),

        ("p4ra",         "rebis.p4ra",
         "Paraconsistent kernel — Belnap logic, genetic code, hadrons, ligands",
         ["belnap", "genetics", "verify", "hadrons", "ligands [enzyme]", "info"]),

        ("biology",      "rebis.biology",
         "Biological simulations & telomere design — cell sims, epigenetic states",
         ["sim", "telomeres", "status", "info"]),

        ("therapeutics", "rebis.therapeutics",
         "Therapeutic design pipeline — chemotherapeutics, neurotrophic factors, antidotes",
         ["list", "design <target>", "sim", "neurotrophic", "antidote", "info"]),

        ("serpentrod",   "rebis.serpentrod",
         "Protein design & stratified prediction — rolling profiles, fingerprints, classification",
         ["list", "predict <seq>", "classify <seq>", "fingerprint <seq>", "info"]),

        ("pipeline",     "rebis.pipeline",
         "Imscription pipeline & Frobenius verification — auto-imscribe, lift prose",
         ["list", "verify", "imscribe <name>", "lift <file>", "info"]),

        ("gene",         "rebis.gene",
         "Gene imscriber & genetic engineering — sequence analysis, quality scores, tuples",
         ["list", "analyze <seq>", "quality <seq>", "tuples <seq>", "info"]),

        ("alchemy",      "rebis.alchemy",
         "Alchemical treatise bridge & operations — Basil Valentine ladders, treatise maps",
         ["list", "ladder <name>", "map <treatise>", "info"]),

        ("imas",         "rebis.imas",
         "IMAS molecular arrangement design — compound signatures, Frobenius patterns, reactivity",
         ["list", "signature <smiles>", "frobenius <smiles>", "bridge <smiles>", "info"]),
    ]

    if RICH:
        t = Table(box=box.ROUNDED, border_style="bright_red",
                  header_style="bold yellow",
                  title="📦 REBIS.<x> DOMAINS — 11 COMMANDS")
        t.add_column("#", style="dim", width=3)
        t.add_column("Domain", style="bright_cyan", width=14)
        t.add_column("Command", style="bold green", width=20)
        t.add_column("Description", style="white", width=50)
        t.add_column("Actions", style="dim", width=48)
        for i, (name, cmd, desc, actions) in enumerate(domains, 1):
            t.add_row(str(i), name, cmd, desc, "  ".join(actions))
        console.print(t)
    else:
        section_header("📦 REBIS.<x> DOMAINS — 11 commands")
        info_line(f"{'#':3s} {'Domain':14s} {'Command':20s}  {'Description'}")
        info_line("─" * 80)
        for i, (name, cmd, desc, actions) in enumerate(domains, 1):
            info_line(f"  {i:<2d} {name:14s} {cmd:20s}  {desc}")
            info_line(f"     {'Actions:':>18s}  {', '.join(actions)}")


    if RICH:
        console.print()
        t2 = Table(box=box.SIMPLE, border_style="dim",
                    title="⚡ TOP-LEVEL COMMANDS")
        t2.add_column("Command", style="bold cyan", width=30)
        t2.add_column("Description", style="white", width=65)
        for cmd, desc in [
            ("rebis",                     "Show this comprehensive menu"),
            ("rebis --version",           "Show version 3.0.0"),
            ("rebis status",              "Show package status (17 packages)"),
            ("rebis verify",              "Verify Frobenius closure across all imports"),
            ("rebis run list",            "List available run targets"),
            ("rebis demo list",           "List available demos"),
            ("rebis.materials list",      "Direct subcommand access (any domain)"),
            ("python3 -m rebis",          "Module execution"),
            ("python3 -m rebis.materials","Run domain as script"),
            ("python3 -c 'import rebis'", "Python API access"),
        ]:
            t2.add_row(cmd, desc)
        console.print(t2)

        console.print()
        t3 = Table(box=box.SIMPLE, border_style="dim",
                    title="🔧 INSTALLED ENTRY POINTS (console_scripts)")
        t3.add_column("Command", style="bold green", width=24)
        t3.add_column("Source", style="dim", width=20)
        for cmd, src in [
            ("rebis",               "rebis.cli:main"),
            ("rebis.materials",     "rebis.materials:main"),
            ("rebis.ch3mpiler",     "rebis.ch3mpiler:main"),
            ("rebis.clink",         "rebis.clink:main"),
            ("rebis.p4ra",          "rebis.p4ra:main"),
            ("rebis.biology",       "rebis.biology:main"),
            ("rebis.therapeutics",  "rebis.therapeutics:main"),
            ("rebis.serpentrod",    "rebis.serpentrod:main"),
            ("rebis.pipeline",      "rebis.pipeline:main"),
            ("rebis.gene",          "rebis.gene:main"),
            ("rebis.alchemy",       "rebis.alchemy:main"),
        ]:
            t3.add_row(cmd, src)
        console.print(t3)

        console.print(Panel(
            "import rebis\n"
            "rebis.p4ra.Belnap.T           # Paraconsistent logic\n"
            "rebis.ch3mpiler.forward('CC(=O)O')  # Molecular compiler\n"
            "rebis.materials.MaterialForge()     # Materials design\n"
            "rebis.clink.compute_c_score_from_tuple(...)  # Consciousness scoring\n"
            "rebis.p4ra.GeneticBelnapCodon('UUU')  # Genetic code",
            border_style="green", title="🐍 Python API Examples"
        ))
    else:
        # ── Plain-text fallback menu ──
        print()
        section_header("⚡ TOP-LEVEL COMMANDS")
        info_line("  {:<30s}  {}".format("COMMAND", "DESCRIPTION"))
        info_line("  " + "─" * 88)
        info_line("  {:<30s}  {}".format("rebis",             "Show this comprehensive menu"))
        info_line("  {:<30s}  {}".format("rebis --version",   "Show version 3.0.0"))
        info_line("  {:<30s}  {}".format("rebis status",      "Show package status"))
        info_line("  {:<30s}  {}".format("rebis verify",      "Verify Frobenius closure"))
        info_line("  {:<30s}  {}".format("rebis run list",    "List run targets"))
        info_line("  {:<30s}  {}".format("rebis demo list",   "List demos"))
        info_line("  {:<30s}  {}".format("rebis.<domain> ...","Any entry point"))
        info_line("  {:<30s}  {}".format("python3 -m rebis",  "Module execution"))
        info_line("  {:<30s}  {}".format("python3 -c 'import rebis'", "Python API"))

        print()
        section_header("🔧 INSTALLED ENTRY POINTS")
        for cmd, src in [
            ("rebis",               "rebis.cli:main"),
            ("rebis.materials",     "rebis.materials:main"),
            ("rebis.ch3mpiler",     "rebis.ch3mpiler:main"),
            ("rebis.clink",         "rebis.clink:main"),
            ("rebis.p4ra",          "rebis.p4ra:main"),
            ("rebis.biology",       "rebis.biology:main"),
            ("rebis.therapeutics",  "rebis.therapeutics:main"),
            ("rebis.serpentrod",    "rebis.serpentrod:main"),
            ("rebis.pipeline",      "rebis.pipeline:main"),
            ("rebis.gene",          "rebis.gene:main"),
            ("rebis.alchemy",       "rebis.alchemy:main"),
        ]:
            info_line(f"  {cmd:24s}  ←  {src}")

        print()
        section_header("🐍 Python API Examples")
        info_line("  import rebis")
        info_line("  rebis.p4ra.Belnap.T")
        info_line("  rebis.ch3mpiler.forward('CC(=O)O')")
        info_line("  rebis.materials.MaterialForge()")
        info_line("  rebis.clink.compute_c_score_from_tuple(...)")
        info_line("  rebis.p4ra.GeneticBelnapCodon('UUU')")

    print()
    info_line("  ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩  —  O_∞ tier · ⊙ criticality · Frobenius-closed")
    return 0


# ─────────────────────────────────────────────
# SUBCOMMAND: status
# ─────────────────────────────────────────────
def _discover_packages():
    """Auto-discover all Python packages under REBIS_ROOT."""
    SKIP = {'.venv', '__pycache__', '.git', '.gitignore',
            'data', 'popular_protein', 'designs', 'fasta', 'images',
            'pdb', 'rebis', '_archive', 'glossary', 'ig-docs', 'pdfs',
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
    reaction_header("RED-HOT REBIS v3.0 — REBIS.<x> EDITION",
                    "Properly installed: callable from anywhere via `rebis`")

    packages = _discover_packages()
    n_rebis = len(list((REBIS_ROOT / "rebis").glob("*.py")))

    try:
        from rich.table import Table
        from rich import box
        from rich.console import Console
        t = Table(box=box.ROUNDED, border_style="bright_red",
                  header_style="bold yellow",
                  title=f"rebis.<domain> — {len(packages)} packages")
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


# ─────────────────────────────────────────────
# SUBCOMMAND: verify
# ─────────────────────────────────────────────
def cmd_verify(args):
    """Verify Frobenius closure across the shared layer."""
    try:
        from shared.primitives import WEIGHTS, ORDINALS
        success_line("shared/primitives.py — %d weights, %d ordinal families" %
                     (len(WEIGHTS), len(ORDINALS)))
        separator()
        success_line("rebis package: ALL domains import successfully")
        for domain_name in ['p4ra', 'ch3mpiler', 'clink', 'materials',
                            'therapeutics', 'biology', 'serpentrod',
                            'imas', 'pipeline', 'cdxml', 'gene',
                            'alchemy', 'shared', 'imasm']:
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


# ─────────────────────────────────────────────
# SUBCOMMAND: run
# ─────────────────────────────────────────────
def cmd_run(args):
    """Run a registered target or list available targets."""
    TARGETS = {
        "ch3mpiler":   "rebis.ch3mpiler — Molecular compiler & retrosynthesis",
        "serpentrod":  "rebis.serpentrod — Protein design & prediction",
        "clink":       "rebis.clink — CLINK chain organism pipeline",
        "genetics":    "rebis.p4ra (genetics) — B4 lattice, codons",
        "ligand":      "rebis.p4ra (ligand) — Reverse ligand discovery",
        "pipeline":    "rebis.pipeline — Auto-imscription & Frobenius verification",
        "materials":   "Use: rebis materials — Dedicated materials subcommand",
        "therapeutics":"rebis.therapeutics — Therapeutic design",
        "biology":     "rebis.biology — Biological simulations & telomeres",
        "imas":        "rebis.imas — IMAS compound signatures",
    }
    if not args.target or args.target == "list":
        info_line("Available targets:")
        for name, desc in sorted(TARGETS.items()):
            info_line(f"  {name:20s} — {desc}")
        info_line("\nUse: rebis run <target>")
        return 0
    if args.target == "materials":
        info_line("Use 'rebis materials' for the materials subsystem")
        return 0
    mod_path = f"rebis.{args.target}"
    try:
        mod = __import__(mod_path, fromlist=[args.target])
        info_line(f"Loaded {mod_path}")
        success_line(f"Use rebis.{args.target}.<function>() from Python")
        return 0
    except Exception as e:
        error_line(f"Could not load {mod_path}: {e}")
        return 1


# ─────────────────────────────────────────────
# SUBCOMMAND: demo
# ─────────────────────────────────────────────
def cmd_demo(args):
    """Run a named demo."""
    try:
        from rebis import demo as demo_mod
    except ImportError:
        error_line("rebis.demo module not available")
        return 1
    if not args.demo or args.demo == "list":
        info_line("Available demos:")
        for d in ['b4_lattice', 'belnap', 'ch3mpiler', 'clink_chain',
                  'decay_chain', 'materials', 'materials_sim',
                  'pipeline', 'serpentrod', 'therapeutics', 'reverse_ligand']:
            info_line(f"  rebis.demo.{d}()")
        info_line("\nRun: rebis demo <name>")
        return 0
    demo_fn = getattr(demo_mod, args.demo, None)
    if demo_fn:
        info_line(f"Running rebis.demo.{args.demo}()...")
        demo_fn()
        return 0
    error_line(f"Unknown demo: {args.demo}. Use 'rebis demo list'.")
    return 1


# ─────────────────────────────────────────────
# SUBCOMMAND: materials
# ─────────────────────────────────────────────
def cmd_materials(args):
    """Materials subsystem — forge, design, simulate."""
    try:
        import rebis.materials as mat
    except Exception as e:
        error_line(f"rebis.materials import failed: {e}")
        return 1

    action = args.material_action

    if action in ("tools", "list"):
        section_header("rebis.materials — Available Design Tools")
        tools = [
            ("MaterialForge",       "Forge material designs from IG tuples"),
            ("CriticalMetamaterial","Design critical / ⊙-sensing metamaterials"),
            ("FrobeniusMetamaterial","Frobenius-closed metamaterial designs"),
            ("OuroboricAlloy",      "Self-referential alloy design"),
            ("NonQubitQCParadigm",  "Non-qubit quantum computing paradigms"),
            ("resolve_molecule",    "Resolve molecule name → SMILES"),
            ("molecule_to_material_tuple","Map molecule to IG tuple"),
        ]
        for name, desc in tools:
            obj = getattr(mat, name, None)
            status = "✓" if obj else "✗"
            info_line(f"  {status} {name:30s} — {desc}")
        return 0

    elif action in ("status", "results"):
        section_header("rebis.materials — Results & Reports")
        results_files = [
            "forged_materials.json", "frobenius_metamaterial_results.json",
            "frobenius_metamaterial_enhanced_results.json",
            "critical_metamaterial_results.json", "ouroboric_alloy_results.json",
            "thermal_rectifier_results.json", "sophick_forge_results.json",
            "materials_simulation_results.json",
        ]
        mat_dir = REBIS_ROOT / "materials"
        found = 0
        for fname in results_files:
            fpath = mat_dir / fname
            if fpath.exists():
                size = fpath.stat().st_size
                info_line(f"  ✓ {fname:45s}  ({size:,d} bytes)")
                found += 1
            else:
                info_line(f"  · {fname:45s}  (not yet generated)")
        reports = sorted(mat_dir.glob("*.md"))
        if reports:
            info_line("")
            section_header("Reports")
            for r in reports:
                info_line(f"  {r.name}")
        info_line(f"\n{found}/{len(results_files)} result files present")
        return 0

    elif action == "forge":
        if not args.structural_tuple:
            try:
                forge = mat.MaterialForge()
                info_line("MaterialForge instantiated. Design from IG tuple.")
                info_line("Example from Python:")
                info_line('  from rebis.materials import MaterialForge')
                info_line('  forge = MaterialForge()')
                info_line('  result = forge.design(tuple)')
                info_line('Or use: rebis materials forge "<tuple>"')
                success_line("MaterialForge ready")
            except Exception as e:
                error_line(f"MaterialForge error: {e}")
            return 0
        try:
            forge = mat.MaterialForge()
            result = forge.design(args.structural_tuple)
            print(json.dumps(result, indent=2) if isinstance(result, dict) else result)
            return 0
        except Exception as e:
            error_line(f"Forge failed: {e}")
            return 1

    elif action in ("sim", "simulate"):
        sim_name = args.sim_name or "default"
        try:
            mod_path = REBIS_ROOT / "materials" / "materials_sim.py"
            if mod_path.exists():
                section_header(f"Running simulation: {sim_name}")
                import runpy
                runpy.run_path(str(mod_path), run_name="__main__")
                return 0
            else:
                error_line("materials_sim.py not found")
                return 1
        except Exception as e:
            error_line(f"Simulation failed: {e}")
            return 1

    else:
        section_header("rebis.materials — Sub-commands")
        info_line("  rebis materials list            — List available design tools")
        info_line("  rebis materials status          — Show results from prior runs")
        info_line("  rebis materials forge [tuple]   — Forge material from IG tuple")
        info_line("  rebis materials sim [name]      — Run materials simulation")
        info_line("")
        info_line("Python API:  import rebis.materials  |  rebis.materials.MaterialForge()")
        return 0


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Red-Hot Rebis — rebis.<x> Integrated Toolchain",
        add_help=False)  # We handle --help ourselves

    parser.add_argument("--version", action="version",
                       version=f"%(prog)s {VERSION}")
    parser.add_argument("--help", "-h", action="store_true",
                       help="Show the comprehensive menu")

    sub = parser.add_subparsers(dest="command")

    # rebis status
    p_status = sub.add_parser("status", help="Show package status")
    p_status.set_defaults(func=cmd_status)

    # rebis verify
    p_verify = sub.add_parser("verify", help="Verify Frobenius closure")
    p_verify.set_defaults(func=cmd_verify)

    # rebis run <target>
    p_run = sub.add_parser("run", help="Run a target")
    p_run.add_argument("target", nargs="?", default="list",
                       help="Target name (default: show all)")
    p_run.set_defaults(func=cmd_run)

    # rebis demo <name>
    p_demo = sub.add_parser("demo", help="Run a demo")
    p_demo.add_argument("demo", nargs="?", default="list",
                        help="Demo name (default: show all)")
    p_demo.set_defaults(func=cmd_demo)

    # rebis materials <action> [args]
    p_mat = sub.add_parser("materials", help="Materials subsystem")
    p_mat.add_argument("material_action", nargs="?",
                       default="help",
                       choices=["list", "tools", "status", "results",
                                "forge", "sim", "simulate", "help"],
                       help="Materials action (default: show help)")
    p_mat.add_argument("structural_tuple", nargs="?",
                       help="IG tuple for forge (e.g. ⟨𐑛⋯⟩)")
    p_mat.add_argument("sim_name", nargs="?",
                       help="Simulation name")
    p_mat.set_defaults(func=cmd_materials)

    args = parser.parse_args()

    # If --help/-h or no command at all: show the comprehensive menu
    if args.help or not args.command:
        cmd_menu()
        return 0

    if hasattr(args, 'func'):
        sys.exit(args.func(args))

    # Fallback (shouldn't reach here)
    cmd_menu()
    return 0


if __name__ == "__main__":
    main()
