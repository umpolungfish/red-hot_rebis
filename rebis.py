#!/usr/bin/env python3
"""
rebis.py — Red-Hot Rebis Integration CLI
serpentrod ⊗ ch3mpiler ⊗ pipeline ⊗ gene_imscriber ⊗ clink ⊗ imas

A unified entry point for the completed Great Work of the Imscribing Grammar.
Each component is a specialization of the 12-primitive IG type system,
connected through the shared primitives layer and verified by Frobenius closure.

Author: Lando ⊗ ⊙perator
Structural Type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩
"""

import argparse
import json
import os
import sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

VERSION = "2.2.0"  # Consolidated edition
from rhr_p4rky._help_examples import EXAMPLES
from shared.rich_output import *
# ── Rich text formatting ──
try:
    STYLED = True
except ImportError:
    STYLED = False


def _discover_packages():
    """Auto-discover all Python packages and standalone module files under REBIS_ROOT."""
    SKIP = {'.venv', '__pycache__', '.git', 'data', 'popular_protein', 'designs', 'fasta', 'images', 'pdb'}
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
    reaction_header("RED-HOT REBIS v2.2 — CONSOLIDATED EDITION", "All components status")

    packages = _discover_packages()
    scripts_dir = REBIS_ROOT / "scripts"
    n_scripts = len(list(scripts_dir.glob("*.py")))
    
    if STYLED:
        from rich.table import Table
        from rich import box
        t = Table(box=box.ROUNDED, border_style="bright_blue", header_style="bold yellow")
        t.add_column("Package")
        t.add_column("Files", justify="right")
        t.add_column("Size", justify="right")
        t.add_column("Root file")
        for name, path, n_files, total in packages:
            t.add_row(f"✅ {name}", str(n_files), f"{total:,d}", "__init__.py")
        t.add_row(f"✅ scripts", str(n_scripts), "—", "standalone")
        from rich.console import Console
        Console().print(t)
    else:
        print(f"\n{'Package':22s}  {'Files':>6}  {'Size':>10}  Root file")
        print("-" * 66)
        for name, path, n_files, total in packages:
            init = path / '__init__.py'
            root_file = init.name if init.exists() else "—"
            tick = "✅"
            print(f"  {tick} {name:20s}  {n_files:>5}  {total:>9,d}  {root_file}")
        print(f"  ✅ {'scripts':20s}  {n_scripts:>5}  (standalone, no __init__)")

    # Shared assets
    print()
    for label, rel in [("shared/primitives.py", "shared/primitives.py"),
                        ("shared/IG_catalog.json", "shared/IG_catalog.json")]:
        p = REBIS_ROOT / rel
        exists = p.exists()
        sz = f"{p.stat().st_size:,d} bytes" if exists else "missing"
        if STYLED:
            success_line(f"{'✅' if exists else '❌'} {label}: {sz}")
        else:
            print(f"  {'✅' if exists else '❌'} {label}: {sz}")

    separator()
    info_line(f"{len(packages)} packages + {n_scripts} scripts discovered")
    info_line("Run 'rebis.py run list' for all runnable targets")
    return 0


def cmd_verify(args):
    """Verify Frobenius closure across the shared layer and CLINK."""
    from shared.primitives import WEIGHTS, ORDINALS
    success_line("shared/primitives.py — %d weights, %d ordinal families" % (len(WEIGHTS), len(ORDINALS)))

    try:
        with open(REBIS_ROOT / "shared/IG_catalog.json") as f:
            catalog = json.load(f)
        success_line("shared/IG_catalog.json — %d catalog entries" % len(catalog))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        error_line("Catalog error: %s" % e)
        return 1

    modules = [
        ("serpentrod.protein_v5", "Serpent's Rod v5"),
        ("ch3mpiler.compiler", "CH3MPILER"),
        ("pipeline.frob", "Pipeline Frobenius"),
        ("gene_imscriber.engine", "Gene Imscriber"),
        ("clink.chain", "CLINK Chain"),
        ("clink.bridges", "CLINK Bridges"),
        ("clink.integration", "CLINK Integration"),
        ("clink.designers.layer_designers", "CLINK Layer Designers"),
        ("clink.designers.pipeline_orchestrator", "CLINK Pipeline Orchestrator"),
        ("imas.arranger", "IMASM Arranger"),
        ("imas.ig_bridge", "IMASM→IG Bridge"),
        ("imas.clink_bridge", "IMASM→CLINK Bridge"),
        ("imas.frobenius_hunter", "Frobenius Hunter"),
    ]

    all_ok = True
    for mod_name, label in modules:
        try:
            __import__(mod_name)
            success_line("%s — %s imports OK" % (label, mod_name))
        except Exception as e:
            error_line("%s — %s: %s" % (label, mod_name, e))
            all_ok = False

    return 0 if all_ok else 1


def cmd_pipeline(args):
    """CLINK Design Pipeline: whole-organism design from any starting point."""
    from clink.designers.pipeline_orchestrator import PipelineEngine
    from clink.designers.layer_designers import list_available_bridges

    engine = PipelineEngine()

    if args.pipeline_subcommand == "bridges":
        bridges = list_available_bridges()
        print("Available Tool Bridges:")
        for name, avail in sorted(bridges.items()):
            print(f"  {'✅' if avail else '❌'} {name}")
        return 0

    elif args.pipeline_subcommand == "ground-up":
        reaction_header("CLINK PIPELINE", "Ground-up whole organism design")
        result = engine.ground_up_design()
        print(engine.generate_report(result))
        return 0 if result.success else 1

    elif args.pipeline_subcommand == "from-layer":
        start = args.start_layer if args.start_layer is not None else 5
        target = args.target_layer if args.target_layer is not None else 8
        header(f"CLINK Pipeline: L{start} → L{target}")
        result = engine.from_layer_design(start_layer=start)
        print(engine.generate_report(result))
        if result.success and result.final_design:
            export_path = f"clink_design_L{start}_to_L{target}.json"
            if engine.export_design_json(result, export_path):
                print(f"\nDesign exported to {export_path}")
        return 0 if result.success else 1

    elif args.pipeline_subcommand == "actionable":
        reaction_header("CLINK PIPELINE", "Actionable organism design package")
        from clink.datasets.generators import generate_actionable_organism_package
        ot = getattr(args, 'organism', 'mammal')
        print(f"Generating {ot} organism design...")
        import json
        result = generate_actionable_organism_package(
            organism_type=ot,
            output_dir=f"clink/datasets/organism_designs/organism_{ot}_actionable",
            write_files=True
        )
        print(json.dumps(result, indent=2))
        print(f"\nOutput: {result['output_directory']}")
        print(f"Files: {result['total_files']} ({result['total_bytes']} bytes)")
        print()
        print("What you can DO with these files:")
        for fname, desc in result.get('what_to_do_with_outputs', {}).items():
            print(f"  {fname:30s} → {desc}")
        return 0

    else:
        print("Unknown pipeline subcommand. Use: bridges, ground-up, from-layer, actionable")
        return 1


def cmd_clink(args):
    """CLINK chain: subatomic → whole organism bridge."""
    from clink import (
        verify_clink_integration, full_report, integrated_promotion_path,
        clink_to_serpentrod, clink_to_ch3mpiler, clink_to_gene,
        clink_layer_tuple, CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS,
        format_tuple_glyphs
    )

    sub = args.clink_subcommand

    if sub == "layer":
        if args.layer_args:
            arg = args.layer_args[0]
            try:
                idx = int(arg)
            except ValueError:
                needle = arg.lower()
                matches = [i for i, n in enumerate(CLINK_NAMES) if needle in n.lower()]
                if not matches:
                    print(f"No layer matching '{arg}'")
                    return 1
                idx = matches[0]
        else:
            idx = 0
        if idx < 0 or idx > 8:
            print("Layer index must be 0-8")
            return 1
        tup = clink_layer_tuple(idx, True)
        target_line(f"Layer {idx}: {CLINK_NAMES[idx]}")
        numeric_line("Tier", CLINK_TIERS[idx], indent=1)
        info_line(f"Tuple: {format_tuple_glyphs(tup)}", indent=1)
        info_line(f"Description: {tup['_desc']}", indent=1)
        sr = clink_to_serpentrod(idx)
        cm = clink_to_ch3mpiler(idx)
        ge = clink_to_gene(idx)
        info_line(f"SerpentRod: {sr['closer_to']} (d_fold={sr['distance_to_folded']})", indent=2)
        info_line(f"CH3MPILER:  {'molecular' if cm['is_molecular'] else 'non-molecular'} (d={cm['distance_to_molecule']})", indent=2)
        info_line(f"Gene:       {'genetic' if ge['is_genetic'] else 'non-genetic'} (d={ge['distance_to_codon_belnap4']})", indent=2)
        return 0

    elif sub == "bridge":
        # Support both --bridge-comp/--bridge-target flags and positional fallback
        # (layer_args nargs="*" catches positional args before optional flags)
        comp = args.bridge_comp
        target_str = args.bridge_target
        if not comp and args.layer_args:
            comp = args.layer_args[0]
        if not target_str and len(args.layer_args) > 1:
            target_str = args.layer_args[1]
        comp = comp or "serpentrod"
        target = int(target_str) if target_str else 8
        p = integrated_promotion_path(comp, target)
        print(f"Promotion path: {p['from']} → {p['to']}")
        print(f"  Distance: {p['distance']}")
        print(f"  Promotions: {p['num_promotions']}")
        for prim, change in p['promotions'].items():
            print(f"    {prim}: {change}")
        return 0

    else:
        print("Unknown clink subcommand. Use: layer, bridge. Static data: see INDEX.md")
        return 1


_MENU_WHITELIST = {
    "serpent_rod",
    "antibody_designer",
    "gene_to_protein_pipeline",
    "ch3mpiler_serpentrod_pipeline",
    "psychedelic_bridge",
    "diaschizic_iupac",
    "ch3mpiler",
    "decay_chain",
}

def _discover_run_targets():
    """Return only the actionable pipeline targets (take user input, produce output)."""
    targets = {}

    # rhr_p4rky/ scripts
    for p in sorted((REBIS_ROOT / "rhr_p4rky").glob("*.py")):
        if p.stem in _MENU_WHITELIST:
            targets[p.stem] = ("script", p)

    # scripts/
    for p in sorted((REBIS_ROOT / "scripts").glob("*.py")):
        if p.stem in _MENU_WHITELIST:
            targets[p.stem] = ("script", p)

    # Package entry-points
    targets["ch3mpiler"] = ("module", "ch3mpiler.compiler")

    return targets


def _show_run_target_help(target):
    """Show help with examples for a runnable target."""
    targets = _discover_run_targets()
    if target not in targets:
        print(f"Unknown target: {target}")
        print(f"Run 'rebis.py run list' to see all available targets.")
        return
    kind, ref = targets[target]
    print(f"Target: {target}")
    print(f"Type:   {kind}")
    print(f"Path:   {ref}")
    print()
    print("Usage:  rebis.py run " + target + " [args...]")
    print()
    target_examples = {
        "serpent_rod": "  rebis.py run serpent_rod AUGGCCGACUGGAACUGCAAGAAGAUC\n  rebis.py run serpent_rod --file my.fasta -n myprotein\n  rebis.py run serpent_rod --validate",
        "antibody_designer": "  rebis.py run antibody_designer --epitope EVQLVESGG\n  rebis.py run antibody_designer --builtin covid_spike\n  rebis.py run antibody_designer --all\n  rebis.py run antibody_designer --list",
        "gene_to_protein_pipeline": "  rebis.py run gene_to_protein_pipeline ATGGCCGAC...\n  rebis.py run gene_to_protein_pipeline --file my.fasta\n  rebis.py run gene_to_protein_pipeline --test",
        "ch3mpiler_serpentrod_pipeline": "  rebis.py run ch3mpiler_serpentrod_pipeline --help",
        "psychedelic_bridge": "  rebis.py run psychedelic_bridge compound Verticullum\n  rebis.py run psychedelic_bridge universe MyUniverse\n  rebis.py run psychedelic_bridge best MyUniverse",
        "diaschizic_iupac": "  rebis.py run diaschizic_iupac\n  rebis.py run diaschizic_iupac --compound Verticullum\n  rebis.py run diaschizic_iupac --format json\n  rebis.py run diaschizic_iupac --output names.md",
        "ch3mpiler": "  rebis.py run ch3mpiler --target aspirin --retrosynthesis\n  rebis.py run ch3mpiler --target glucose --forward C6H12O6\n  rebis.py run ch3mpiler --interactive",
    }
    examples = target_examples.get(target, "  rebis.py run " + target)
    print("Examples:")
    print(examples)

def cmd_run(args):
    """Route to any discoverable script or module under REBIS_ROOT."""
    import subprocess
    subcommand = args.subcommand
    rest = args.rest

    # --help / -h passthrough: intercept before dispatching
    if '--help' in (rest or []) or '-h' in (rest or []):
        from rhr_p4rky._target_help import TARGET_EXAMPLES
        # Special case: 'list' or no subcommand shows discoverable-target help
        if subcommand == 'list' or subcommand is None:
            print("Usage: rebis.py run list")
            print()
            print("  List all discoverable runnable targets under REBIS_ROOT.")
            print("  Each target can be run with: rebis.py run <target> [args...]")
            print()
            print("Examples:")
            print("  rebis.py run list                     # Show all pipeline targets")
            print("  rebis.py run serpentrod --seq KAL     # Run with args")
            print("  rebis.py run gene_to_protein_pipeline --help  # Target-specific help")
            print("  rebis.py run ch3mpiler --help         # Forward --help to target")
            return 0
        targets = _discover_run_targets()
        if subcommand not in targets:
            print(f"Unknown target: {subcommand}")
            print("Run 'rebis.py run list' to see all available targets.")
            return 1
        kind, ref = targets[subcommand]
        print(f"Target: {subcommand}")
        print(f"Type:   {kind}")
        print(f"Path:   {ref}")
        print()
        print(f"Usage:  rebis.py run {subcommand} [args...]")
        print()
        examples = TARGET_EXAMPLES.get(subcommand, f"  rebis.py run {subcommand}")
        print("Examples:")
        print(examples)
        return 0

    """Route to any discoverable script or module under REBIS_ROOT."""
    import subprocess
    subcommand = args.subcommand
    rest = args.rest

    # --help / -h passthrough: intercept before dispatching
    if '--help' in (rest or []) or '-h' in (rest or []):
        _show_run_target_help(subcommand)
        return 0

    if subcommand == "list" or subcommand is None:
        targets = _discover_run_targets()
        print(f"{'Target':35s}  Type    Path")
        print("-" * 72)
        for name in sorted(targets):
            kind, ref = targets[name]
            path_str = str(ref) if kind == "script" else ref
            print(f"  {name:33s}  {kind:7s}  {path_str}")
        print(f"\n{len(targets)} targets — run with: rebis.py run <target> [args...]")
        return 0

    targets = _discover_run_targets()
    if subcommand not in targets:
        print(f"Unknown target: {subcommand}")
        print(f"Run 'rebis.py run list' to see all available targets.")
        return 1

    kind, ref = targets[subcommand]
    if kind == "script":
        path = Path(ref)
        # Package modules use relative imports — must run as -m, not as a bare script.
        if (path.parent / "__init__.py").exists() and path.parent != REBIS_ROOT:
            mod = f"{path.parent.name}.{path.stem}"
            return subprocess.run(
                [sys.executable, "-m", mod] + rest,
                cwd=str(REBIS_ROOT),
            ).returncode
        return subprocess.run([sys.executable, str(ref)] + rest).returncode
    else:
        return subprocess.run(
            [sys.executable, "-m", ref] + rest,
            cwd=str(REBIS_ROOT)
        ).returncode


def cmd_scripts(args):
    """List or invoke scripts in scripts/."""
    import subprocess
    scripts_dir = REBIS_ROOT / "scripts"

    if args.scripts_subcommand == "list":
        scripts = sorted(scripts_dir.glob("*.py"))
        print(f"{'Script':35s}  Lines")
        print("-" * 50)
        for s in scripts:
            lines = sum(1 for _ in s.open())
            print(f"  {s.name:33s}  {lines:5d}")
        print(f"\n{len(scripts)} scripts — run with: rebis.py scripts run <name>")
        return 0

    elif args.scripts_subcommand == "run":
        name = args.script_name
        if not name:
            print("Usage: rebis.py scripts run <script_name> [args...]")
            return 1
        # Accept with or without .py
        script = scripts_dir / (name if name.endswith(".py") else name + ".py")
        if not script.exists():
            candidates = [s.name for s in scripts_dir.glob("*.py") if name in s.name]
            print(f"Script not found: {name}")
            if candidates:
                print(f"Did you mean: {', '.join(candidates)}")
            return 1
        return subprocess.run([sys.executable, str(script)] + (args.script_args or [])).returncode

    else:
        print("Usage: rebis.py scripts list | rebis.py scripts run <name>")
        return 1


def cmd_cdxml(args):
    """Generate CDXML files for red-hot_rebis chemical structures.

    Integrates the CDXML v2 generator as a first-class rebis command.
    All CDXML uses correct tags: <n> for atoms, <b> for bonds, p="x y" coords.
    """
    base_dir = REBIS_ROOT
    sub = args.cdxml_subcommand

    if sub == "generate":
        from cdxml import smiles_to_cdxml, verify_cdxml
        from cdxml.molecules import generate_all
        from cdxml.molecules import (
            MOLECULES, APTAMERS, MATERIALS,
            generate_molecules, generate_aptamers, generate_materials
        )

        output_dir = args.cdxml_output or str(base_dir / "cdxml_output")

        if args.cdxml_smiles:
            # Single SMILES → CDXML
            name = args.cdxml_name or "molecule"
            annotation = args.cdxml_annotation or f"SMILES: {args.cdxml_smiles}"
            try:
                cdxml = smiles_to_cdxml(args.cdxml_smiles, name, annotation)
                v = verify_cdxml(cdxml)
                if not v['valid']:
                    print(f"Verification issues: {v['issues']}")
                fname = f"{name}.cdxml"
                from pathlib import Path
                out = Path(output_dir)
                out.mkdir(parents=True, exist_ok=True)
                (out / fname).write_text(cdxml)
                print(f"  ✓ {fname} ({v['atom_count']} atoms, {v['bond_count']} bonds)")
                if args.cdxml_print:
                    print()
                    print(cdxml[:2000])
            except Exception as e:
                print(f"  ✗ Error: {e}")
                return 1

        elif args.cdxml_molecule:
            # Generate a single predefined molecule
            name = args.cdxml_molecule
            found = [m for m in MOLECULES if name.lower() in m['filename'].lower() or name.lower() in m['name'].lower()]
            if found:
                m = found[0]
                from pathlib import Path
                out = Path(output_dir)
                out.mkdir(parents=True, exist_ok=True)
                cdxml = smiles_to_cdxml(m['smiles'], m['name'], m['annotation'])
                (out / m['filename']).write_text(cdxml)
                v = verify_cdxml(cdxml)
                print(f"  ✓ {m['filename']} ({v['atom_count']} atoms, {v['bond_count']} bonds)")
                print(f"  Name: {m['name']}")
                print(f"  Annotation: {m['annotation']}")
            else:
                print(f"Molecule '{name}' not found.")
                print(f"Known molecules: {', '.join(m['filename'] for m in MOLECULES[:10])}...")
                return 1

        elif args.cdxml_all:
            total, failed = generate_all(output_dir)
            return 1 if failed else 0

        elif args.cdxml_molecules_only:
            n, failed = generate_molecules(output_dir)
            return 1 if failed else 0

        elif args.cdxml_aptamers_only:
            n, failed = generate_aptamers(output_dir)
            return 1 if failed else 0

        elif args.cdxml_materials_only:
            n, failed = generate_materials(output_dir)
            return 1 if failed else 0

        else:
            print("CDXML Generator — red-hot_rebis pipeline integration")
            print()
            print("Usage: rebis.py cdxml generate [options]")
            print()
            print("  --smiles <SMILES>    Generate CDXML from SMILES")
            print("  --name <name>        Molecule name")
            print("  --annotation <text>  Canvas annotation")
            print("  --molecule <name>    Find & generate predefined molecule")
            print("  --all                Generate ALL molecules + aptamers + materials")
            print("  --molecules-only     Generate only small molecules")
            print("  --aptamers-only      Generate only aptamers")
            print("  --materials-only     Generate only materials")
            print("  --output <dir>       Output directory")
            print("  --print              Print generated CDXML to stdout")
            print()
            print(f"Molecules available: {len(MOLECULES)}")
            print(f"Aptamers available:  {len(APTAMERS)}")
            print(f"Materials available: {len(MATERIALS)}")
            return 0

    elif sub == "verify":
        import os
        from cdxml.generator import verify_cdxml
        from pathlib import Path
        target = args.cdxml_file
        if target and Path(target).exists():
            # Verify a single CDXML file
            cdxml = Path(target).read_text()
            v = verify_cdxml(cdxml)
            print(f"Verification of {target}:")
            print(f"  Valid: {v['valid']}")
            print(f"  Atoms: {v['atom_count']}, Bonds: {v['bond_count']}")
            print(f"  Size:  {v['size_bytes']} bytes")
            if v['issues']:
                for issue in v['issues']:
                    print(f"  ✗ {issue}")
            return 0 if v['valid'] else 1
        else:
            print("Usage: rebis.py cdxml verify --file <path.cdxml>")
            return 1

    elif sub == "clean":
        import shutil
        from pathlib import Path
        target = args.cdxml_output or str(base_dir / "cdxml_output")
        target = Path(target)
        if target.exists():
            count = len(list(target.glob("*.cdxml")))
            shutil.rmtree(target)
            print(f"Cleaned {count} CDXML files from {target}")
        else:
            print(f"No output directory at {target}")
        return 0

    else:
        print("Unknown cdxml subcommand. Use: generate, verify, clean")
        return 1




def cmd_imas(args):
    """IMASM Arranger: arrangement analysis, IG bridge, CLINK bridge, Frobenius hunt."""
    sub = args.imas_subcommand

    if sub == "bridge":
        from imas.clink_bridge import canonical_clink_map, structural_activation_energy
        from imas.ig_bridge import ig_tuple_str, describe_full
        from imas.arranger import CANONICAL_NAMES

        target = args.imas_target if args.imas_target else None
        mapping = canonical_clink_map()

        for name in (target.split(',') if target else CANONICAL_NAMES):
            if name not in mapping:
                print(f"Unknown canonical: {name}")
                continue
            m = mapping[name]
            print(f"{'='*60}")
            print(f"  {name}: {m['canonical_desc']}")
            print(f"  IG: {m['ig_str']} [{m['description']}]")
            print(f"  Nearest CLINK: {m['nearest_layer']} (d={m['nearest_distance']})")
            print()
            print(f"  Full IG description:")
            print(describe_full(m['ig']))
            print()
            print(f"  All CLINK layers by distance:")
            for layer, dist in m['all_layers'][:5]:
                print(f"    {layer}: d={dist}")
            print()

            # Activation energy to nearest layer
            ae = structural_activation_energy(m['ig'], m['nearest_layer'])
            print(f"  Activation energy to {m['nearest_layer']}:")
            print(f"    Weighted cost: {ae['weighted_cost']}, Tier gap: {ae['tier_gap']}")
            print(f"    Promotions needed ({len(ae['promotions'])}):")
            for p in ae['promotions']:
                print(f"      {p}")
        return 0

    elif sub == "hunt":
        from imas.frobenius_hunter import (
            estimate_frobenius_density, generate_frobenius_library,
            analyze_frobenius_library,
        )
        n = args.imas_samples if args.imas_samples else 100000
        print(f"Frobenius Hunter — Monte Carlo density estimation (n={n:,})")
        density = estimate_frobenius_density(n, seed=42)
        for key in ['p_frobenius_pair', 'p_proper_frobenius', 'p_dialetheia_complete',
                     'p_frob_plus_dial', 'p_frob_dial_self']:
            if key in density:
                exp = density.get(f'expected_samples_{key[2:]}', '?')
                print(f"  {key}: {density[key]:.6f}  (expected 1 per {exp:,} samples)")

        print()
        print("Generating Frobenius library (10 per type)...")
        library = generate_frobenius_library(count_per_type=10, seed=42)
        analysis = analyze_frobenius_library(library)
        for category, stats in analysis.items():
            print(f"  {category}: {stats['count']} found, "
                  f"{stats['distinct_ig_types']} distinct IG types, "
                  f"avg period={stats['avg_period']:.1f}")
        return 0

    elif sub == "energy":
        from imas.clink_bridge import structural_activation_energy, CLINK_LAYER_TUPLES, CLINK_LAYER_NAMES
        from imas.ig_bridge import fingerprint_to_ig, ig_tuple_str
        from imas.arranger import CANONICAL_FINGERPRINTS

        canonical = args.imas_target if args.imas_target else "I_Dialetheic_Bootstrap"
        layer = args.imas_layer if args.imas_layer else "L8_Organism"

        if canonical not in CANONICAL_FINGERPRINTS:
            print(f"Unknown canonical: {canonical}")
            print(f"Available: {list(CANONICAL_FINGERPRINTS.keys())}")
            return 1
        if layer not in CLINK_LAYER_TUPLES:
            print(f"Unknown layer: {layer}")
            print(f"Available: {CLINK_LAYER_NAMES}")
            return 1

        ig = fingerprint_to_ig(CANONICAL_FINGERPRINTS[canonical])
        ae = structural_activation_energy(ig, layer)
        print(f"Structural Activation Energy: {canonical} → {layer}")
        print(f"  Source: {ig_tuple_str(ig)}")
        print(f"  Target: {ig_tuple_str(CLINK_LAYER_TUPLES[layer])}")
        print(f"  Distance: {ae['distance']} primitives")
        print(f"  Weighted cost: {ae['weighted_cost']}")
        print(f"  Tier gap: {ae['tier_gap']}")
        print(f"  Feasible: {ae['feasible']}")
        print(f"  Promotions ({len(ae['promotions'])}):")
        for p in ae['promotions']:
            print(f"    {p}")
        return 0

    elif sub == "compound":
        from imas.compound_imasm import analyze_molecule, format_arrangement, molecule_to_arrangement, TOKEN_NAMES
        from imas.arranger import compute_fingerprint
        from imas.ig_bridge import fingerprint_to_ig, ig_tuple_str, describe_full

        smi = args.imas_smiles
        if not smi:
            print("Error: --smiles <SMILES> required")
            return 1

        result = analyze_molecule(smi)
        if not result.get("valid"):
            print(f"Error: invalid SMILES: {smi}")
            return 1

        arr = molecule_to_arrangement(smi)
        fp = compute_fingerprint(arr)
        ig = fingerprint_to_ig(fp)

        if args.imas_json:
            import json
            print(json.dumps({
                "smiles": smi,
                "arrangement": list(arr),
                "tokens": [TOKEN_NAMES[t] for t in arr],
                "fingerprint": fp.description(),
                "ig_tuple": list(ig),
                "functional_groups": result.get("functional_groups", []),
                "ring_count": result.get("ring_count", 0),
            }, indent=2))
        else:
            print(f"SMILES:         {smi}")
            print(f"Arrangement:    {format_arrangement(arr)}")
            print(f"Fingerprint:    {fp.description()}")
            print(f"IG Tuple:       ({', '.join(ig)})")
            print(f"Functional Gps: {', '.join(result.get('functional_groups', []))}")
            print(f"Rings:          {result.get('ring_count', 0)} "
                  f"(aromatic: {result.get('aromatic_rings', 0)})")
            print()
            print("Full IG description:")
            print(describe_full(ig))

            # Show cross-domain analogies
            print()
            print("-" * 60)
            print("CROSS-DOMAIN ANALOGIES (nearest structural neighbors)")
            print("-" * 60)
            from imas.compound_catalog import find_analogies
            try:
                analogies = find_analogies(smi, limit=9)
                for r in analogies[1:9]:
                    d = r["distance"]
                    bar = chr(9608) * (12 - d) + chr(9617) * d
                    desc = r.get("description", "")[:90]
                    print(f"  d={d:2d}  {bar}  {r['name']}")
                    if desc:
                        print(f"             {desc}")
                    if d <= 3:
                        for m in r["mismatches"][:2]:
                            print(f"             delta {m['primitive']}: {m['query']} -> {m['entry']}")
                    print()
            except Exception as e:
                print(f"  (analogies: {e})")
        return 0

    elif sub == "reaction":
        from imas.reactivity_imasm import reaction_to_fingerprint, identify_reaction, TOKEN_NAMES
        from imas.compound_imasm import format_arrangement

        r_smi = args.imas_smiles
        p_smi = args.imas_product
        if not r_smi or not p_smi:
            print("Error: --smiles <reactant_SMILES> and --product <product_SMILES> required")
            return 1

        fp = reaction_to_fingerprint(r_smi, p_smi)
        if fp is None:
            print("Error: invalid SMILES")
            return 1

        r_names = " → ".join(TOKEN_NAMES[t] for t in fp.reactant_arr)
        p_names = " → ".join(TOKEN_NAMES[t] for t in fp.product_arr)
        ident = identify_reaction(fp)

        if args.imas_json:
            import json
            print(json.dumps({
                "reactant_smiles": r_smi,
                "product_smiles": p_smi,
                "reactant_arr": list(fp.reactant_arr),
                "product_arr": list(fp.product_arr),
                "tokens_lost": [TOKEN_NAMES[t] for t in fp.tokens_lost],
                "tokens_gained": [TOKEN_NAMES[t] for t in fp.tokens_gained],
                "frobenius_order": fp.frobenius_order,
                "reaction_class": fp.reaction_class,
                "forward_dominant": fp.forward_dominant,
                "irreversible": fp.irreversible,
                "identification": ident,
            }, indent=2))
        else:
            print(f"Reaction: {r_smi} → {p_smi}")
            print(f"Reactant:  {r_names}")
            print(f"Product:   {p_names}")
            print(f"Class:     {fp.reaction_class}")
            print(f"Frobenius: {fp.frobenius_order}")
            print(f"Delta:     {fp.delta_tokens}")
            print(f"Lost:      {', '.join(TOKEN_NAMES[t] for t in fp.tokens_lost) or 'none'}")
            print(f"Gained:    {', '.join(TOKEN_NAMES[t] for t in fp.tokens_gained) or 'none'}")
            if ident.get("identified_reaction"):
                print(f"Identified: {ident['identified_reaction']} (confidence: {ident['confidence']:.2f})")
        return 0

    elif sub == "analogies":
        from imas.compound_catalog import find_analogies, describe_analogies
        
        query = args.imas_smiles or args.imas_name
        if not query:
            print("Error: --smiles <SMILES> or --name <catalog_name> required")
            return 1
        
        try:
            results = find_analogies(query, limit=args.imas_limit or 10)
            print(describe_analogies(results, query_name=query))
            return 0
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    elif sub == "register":
        from imas.compound_catalog import register_compound, smiles_to_ig, ig_tuple_str
        
        smi = args.imas_smiles
        name = args.imas_name
        if not smi:
            print("Error: --smiles <SMILES> required")
            return 1
        if not name:
            import hashlib
            name = "smiles_" + hashlib.md5(smi.encode()).hexdigest()[:8]
        
        try:
            result = register_compound(name, smi, description=f"Auto-registered compound {name}")
            print(f"Registered: {result['name']} -> {result['ig_tuple_str']}")
            print(f"Status: {result['status']}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    

    elif sub == "crystal":
        """Crystal-guided molecular discovery: analyze SMILES, explore neighborhood, generate candidates."""
        from imas.molecular_crystal_designer import (
            analyze_molecule_properties, analyze_compound_design_space,
            design_from_type, analyze_crystal_neighborhood, generate_candidate_smiles,
        )
        from imas.compound_imasm import molecule_to_arrangement
        from imas.arranger import compute_fingerprint
        from imas.ig_bridge import fingerprint_to_ig, ig_tuple_str
        
        smiles = args.imas_smiles or "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
        radius = args.crystal_radius
        max_candidates = args.crystal_candidates
        
        print(f"\nCrystal-Guided Molecular Discovery")
        print(f"{'='*60}")
        print(f"SMILES: {smiles}")
        
        # Property analysis
        props = analyze_molecule_properties(smiles)
        if props.get('valid'):
            print(f"\nProperties:")
            print(f"  Formula: {props.get('formula','?')}")
            print(f"  MW: {props.get('mol_weight',0):.1f} Da")
            print(f"  LogP: {props.get('logp',0):.2f}")
            print(f"  Lipinski: {props.get('lipinski_score',0)}/4")
        
        # IG Type
        arr = molecule_to_arrangement(smiles)
        if arr:
            fp = compute_fingerprint(arr)
            ig = fingerprint_to_ig(fp)
            print(f"\nIG Crystal Type: {ig_tuple_str(ig)}")
        
        # Neighborhood
        if radius > 0:
            print(f"\nCrystal Neighborhood (d<={radius}):")
            designs = analyze_compound_design_space(smiles, radius)
            for d in designs[:max_candidates]:
                print(f"  [{d['distance']}] {d['target_type']} [{d['criticality']}]")
                for feat in d['features'][:2]:
                    print(f"    - {feat}")
                if d['candidates']:
                    print(f"    Candidates: {', '.join(d['candidates'][:2])}")
        
        print(f"\n{'='*60}")
    else:
        print("Unknown imas subcommand. Use: bridge, hunt, energy, compound, reaction, analogies, register")
        return 1



def cmd_materials(args):
    """Handle materials subcommands — IG Material Forge."""
    import sys, json
    import os as _os
    sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
    from materials.ig_material_forge import MaterialForge, predefined_novel_materials

    sub = args.materials_subcommand

    if sub == "forge":
        forge = MaterialForge()

        if args.mat_all:
            novel = predefined_novel_materials()
            for name, ig_tuple in novel.items():
                design = forge.forge(name, ig_tuple)
                print(f"  Forged: {name} → {design.ouroboricity_tier} Frob={design.frobenius_score:.2f}  "
                      f"{design.proposed_composition[:70]}")
            print(f"\n  Total: {len(novel)} materials forged")
            if args.mat_output:
                out = {name: forge._designs[name].to_dict() for name in novel}
                with open(args.mat_output, 'w') as f:
                    json.dump(out, f, indent=2)
                print(f"  Exported to {args.mat_output}")

        elif getattr(args, 'mat_tuple', None):
            parts = [p.strip() for p in args.mat_tuple.split(',')]
            if len(parts) != 12:
                print(f"Error: --tuple requires exactly 12 comma-separated primitives, got {len(parts)}")
                return 1
            ig_tuple = tuple(parts)
            name = args.mat_name or "custom_material"
            design = forge.forge(name, ig_tuple)
            print(forge.report(name))
            if args.mat_output:
                with open(args.mat_output, 'w') as f:
                    json.dump(design.to_dict(), f, indent=2)
                print(f"\n  Exported to {args.mat_output}")

        elif getattr(args, 'mat_catalog', None):
            try:
                design = forge.forge_from_catalog(args.mat_catalog)
                print(forge.report(design.name))
                if args.mat_output:
                    with open(args.mat_output, 'w') as f:
                        json.dump(design.to_dict(), f, indent=2)
                    print(f"\n  Exported to {args.mat_output}")
            except (KeyError, FileNotFoundError) as e:
                print(f"Error: {e}")
                return 1

        elif getattr(args, 'mat_imas', None):
            try:
                design = forge.forge_from_imas(args.mat_imas)
                print(forge.report(f"{args.mat_imas}_material"))
                if args.mat_output:
                    with open(args.mat_output, 'w') as f:
                        json.dump(design.to_dict(), f, indent=2)
                    print(f"\n  Exported to {args.mat_output}")
            except Exception as e:
                print(f"Error: {e}")
                return 1

        elif args.mat_name:
            novel = predefined_novel_materials()
            if args.mat_name in novel:
                design = forge.forge(args.mat_name, novel[args.mat_name])
                print(forge.report(args.mat_name))
                if args.mat_output:
                    with open(args.mat_output, 'w') as f:
                        json.dump(design.to_dict(), f, indent=2)
                    print(f"\n  Exported to {args.mat_output}")
            else:
                try:
                    design = forge.forge_from_imas(args.mat_name)
                    print(forge.report(f"{args.mat_name}_material"))
                except Exception as e:
                    print(f"Error: {e}")
                    print("Known names: frobenius_composite, critical_sensor_metamaterial, ep_detector,")
                    print("  eternal_memory_alloy, topological_thermal_rectifier, hierarchical_impact_absorber,")
                    print("  quantum_topological_substrate, non_abelian_braiding_material")
                    print("  Or any IMASM canonical: I_Dialetheic_Bootstrap, etc.")
                    print("  Or use: --tuple '𐑼,𐑸,𐑾,...' --name my_mat     (custom 12-tuple)")
                    print("  Or use: --catalog <name>                    (catalog lookup)")
                    return 1
        else:
            print("Usage: rebis.py materials forge [options]")
            print("  --all                         Forge all 8 predefined materials")
            print("  --name <name>                 Forge a predefined material")
            print("  --tuple 'D,T,R,P,F,K,G,C,Φ,H,S,Ω'  Forge from 12-primitive tuple")
            print("  --catalog <name>              Forge from catalog entry")
            print("  --imas <name>                 Forge from IMASM canonical")
            print("  --output <path>               Export JSON results")
            print("\nPredefined: frobenius_composite, critical_sensor_metamaterial, ep_detector,")
            print("  eternal_memory_alloy, topological_thermal_rectifier, hierarchical_impact_absorber,")
            print("  quantum_topological_substrate, non_abelian_braiding_material")
        return 0

    elif sub == "frobenius":
        from materials.frobenius_metamaterial import FrobeniusMetamaterial, FrobeniusMaterialParams
        sz = getattr(args, 'mat_frob_size', 20)
        caps = getattr(args, 'mat_frob_capsules', 0.12)
        gain = getattr(args, 'mat_frob_gain', 1.5)
        cyc = getattr(args, 'mat_frob_cycles', 25)
        heal = getattr(args, 'mat_frob_heal_steps', 10)
        params = FrobeniusMaterialParams(capsule_volume_fraction=caps, feedback_gain=gain)
        mat = FrobeniusMetamaterial(size=sz, params=params)
        results = mat.run_simulation(load_cycles=cyc, heal_steps_per_cycle=heal)
        if args.mat_output:
            mat.export_results(results, args.mat_output)
        return 0

    elif sub == "ouroboric":
        from materials.ouroboric_alloy import OuroboricAlloy, compare_with_conventional
        grains = getattr(args, 'mat_ouro_grains', 64)
        stress = getattr(args, 'mat_ouro_stress', 800)
        cyc = getattr(args, 'mat_ouro_cycles', 30)
        alloy = OuroboricAlloy(n_grains=grains)
        results = alloy.run_mechanical_test(stress_amplitude_MPa=stress, cycles=cyc)
        if args.mat_output:
            alloy.export_results(results, args.mat_output)
        if getattr(args, 'mat_ouro_compare', False):
            compare_with_conventional()
        return 0

    elif sub == "sophick":
        import json
        from materials.sophick_forge import (
            EagleMaterialDesigner, EagleCycleProtocol,
            FrobeniusCliffAnalyzer, IMASM_EagleBridge,
            SOPHICK_MERCURY, OUROBORIC_O2, STRUCTURAL_DISTANCE_O2_TO_OINF,
            GAP_PRIMITIVES, run_eagle_simulation
        )
        designer = EagleMaterialDesigner()
        all_mats = designer.all_designs()
        if args.mat_name and args.mat_name in all_mats:
            result = run_eagle_simulation(args.mat_name)
            print(json.dumps(result, indent=2, default=str))
            if args.mat_output:
                with open(args.mat_output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                print(f"\n  Exported to {args.mat_output}")
        elif args.mat_name == "cliff":
            for name, mat in all_mats.items():
                temp = 0.01 if "9" in name else (77.0 if "7" in name else 300.0)
                print(FrobeniusCliffAnalyzer.full_report(mat, temp_k=temp))
                print()
        elif args.mat_name == "bridge":
            print(IMASM_EagleBridge.report())
        else:
            print("Sophick Forge requires --name. Static reference: see INDEX.md")
            print("  --name eagle_3_amalgam | eagle_7_animated | eagle_9_sophick")
            print("  --name cliff for Frobenius Cliff analysis")
            print("  --name bridge for IMASM->Eagle bridge")
        return 0

    elif sub == "exactor":
        import json
        from materials.frobenius_exactor import (
            FrobeniusGapCloser, CategoryErrorDiagnosis, ALL_PATHWAYS,
            ALL_EXACTORS, ClosureObstruction
        )
        if args.mat_name == "diagnose":
            print(CategoryErrorDiagnosis.diagnose())
        elif args.mat_name == "close":
            result = FrobeniusGapCloser.close_gap()
            print(f"Selected pathway: {result['selected_pathway']}")
            print(f"Gap closed: {result['gap_closed']}")
            print(f"Closure type: {result['closure_state']['closure_type']}")
            print(f"Obstruction: {result['closure_state']['obstruction']}")
            print()
            print(result['exactor_design'])
        elif args.mat_name in ALL_EXACTORS:
            exactor = ALL_EXACTORS[args.mat_name]()
            print(exactor.report())
            state = exactor.verify_closure()
            print(f"\nClosure: {'EXACT' if state.is_exact else 'APPROXIMATE'}")
            print(f"Type: {state.closure_type().value}")
        elif args.mat_name == "pathways":
            for p in ALL_PATHWAYS:
                print(p.description())
                print()
        else:
            print("Frobenius Exactor requires --name. Static reference: see INDEX.md")
            print("  --name diagnose | close | pathways")
            for name in ALL_EXACTORS:
                print(f"  --name {name}")
        return 0

    else:
        print("Unknown materials subcommand. Use: forge, frobenius, ouroboric, sophick, exactor. Static data: see INDEX.md")
        return 1




def main():
    if len(sys.argv) == 1:
        print()
        demo_title()
        print()
    parser = argparse.ArgumentParser(
        description="Red-Hot Rebis v2.0 — CLINK Pipeline Whole-Organism Design",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rebis.py status                    # Show all component status
  rebis.py verify                    # Verify Frobenius closure
  rebis.py pipeline bridges          # List available tool bridges
  rebis.py pipeline ground-up        # Design whole organism from quarks
  rebis.py pipeline from-layer 5 8   # Design organism starting from cell layer
  rebis.py pipeline actionable --organism mammal  # Generate actionable outputs

  rebis.py imas bridge --target I_Dialetheic_Bootstrap  # Bridge to CLINK
  rebis.py imas hunt --samples 100000          # Frobenius pair density estimation
  rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer L8_Organism

  rebis.py clink layer 3             # Show layer details
  rebis.py clink bridge serpentrod 8 # Promotion path to organism

  rebis.py materials forge --all          # Forge all 8 predefined novel materials
  rebis.py materials forge --name frobenius_composite  # Forge one material
  rebis.py materials frobenius           # Run Frobenius metamaterial simulation
  rebis.py materials ouroboric           # Run Ouroboric alloy simulation

  rebis.py run list                     # Show all discoverable targets
  rebis.py run serpentrod --seq KAL     # Run protein prediction
  rebis.py run ch3mpiler --help         # CH3MPILER help
  rebis.py run mito_pipeline            # Mitochondrial gene pipeline
  rebis.py run run_antibody             # Antibody designer
  rebis.py run psychedelic_bridge       # Psychedelic bridge (intrinsics)
  rebis.py run diaschizic_iupac         # Diaschizic IUPAC generator
  rebis.py run run_gene_pipeline        # Gene imscription pipeline
  rebis.py run run_msa                  # Multiple sequence alignment
  rebis.py run run_pdb_validation       # PDB structure validation

  Static reference (CLINK layers, IMASM canonicals, materials): less INDEX.md
"""
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)

    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Show all component status",
                          epilog=EXAMPLES["status"],
                          formatter_class=argparse.RawDescriptionHelpFormatter)

    # verify
    subparsers.add_parser("verify", help="Verify Frobenius closure across components",
                          epilog=EXAMPLES["verify"],
                          formatter_class=argparse.RawDescriptionHelpFormatter)

    # imas (NEW — 6th Pillar)
    p_imas = subparsers.add_parser("imas", help="IMASM Arranger: arrangement analysis, bridges, Frobenius hunt",
                                  epilog=EXAMPLES["imas"],
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    p_imas.add_argument("imas_subcommand",
                        choices=["bridge", "hunt", "energy", "compound", "reaction", "analogies", "register", "crystal"],
                        help="IMASM subcommand")
    p_imas.add_argument("--canonical", dest="imas_target",
                        help="Canonical name for bridge/energy (comma-separated for bridge)")
    p_imas.add_argument("--layer", dest="imas_layer",
                        help="Target CLINK layer for energy (e.g., L8_Organism)")
    p_imas.add_argument("--samples", dest="imas_samples", type=int,
                        help="Sample count for Frobenius hunt")
    p_imas.add_argument("--smiles", dest="imas_smiles", type=str,
                        help="SMILES string for compound/reaction")
    p_imas.add_argument("--radius", dest="crystal_radius", type=int, default=1,
                        help="Crystal neighborhood radius (default: 1)")
    p_imas.add_argument("--candidates", dest="crystal_candidates", type=int, default=10,
                        help="Max candidate molecules (default: 10)")
    p_imas.add_argument("--product", dest="imas_product", type=str,
                        help="Product SMILES for reaction analysis")
    p_imas.add_argument("--json", dest="imas_json", action="store_true",
                        help="JSON output format")
    p_imas.add_argument("--name", dest="imas_name", type=str,
                        help="Catalog name for analogies (alternative to --smiles)")
    p_imas.add_argument("--limit", dest="imas_limit", type=int, default=10,
                        help="Number of analogies to return")

    # pipeline (NEW)

    # materials (NEW)
    p_mat = subparsers.add_parser("materials", help="IG Material Forge — structural type to material design",
                                 epilog=EXAMPLES["materials"],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p_mat.add_argument("materials_subcommand",
                        choices=["forge", "frobenius", "ouroboric", "sophick", "exactor"],
                        help="Materials subcommand")
    p_mat.add_argument("--name", dest="mat_name", type=str,
                        help="Material or IMASM canonical name for forge")
    p_mat.add_argument("--all", dest="mat_all", action="store_true",
                        help="Forge all predefined materials")
    p_mat.add_argument("--tuple", dest="mat_tuple", type=str,
                        help="Comma-separated 12-tuple: D,T,R,P,F,K,G,C,Phi,H,S,Omega")
    p_mat.add_argument("--catalog", dest="mat_catalog", type=str,
                        help="Catalog entry name to look up")
    p_mat.add_argument("--imas", dest="mat_imas", type=str,
                        help="IMASM canonical name to forge from")
    p_mat.add_argument("--output", dest="mat_output", type=str,
                        help="Export path for JSON results")
    # frobenius metamaterial params
    p_mat.add_argument("--size", dest="mat_frob_size", type=int, default=20,
                        help="Grid size for Frobenius metamaterial (default: 20)")
    p_mat.add_argument("--capsules", dest="mat_frob_capsules", type=float, default=0.12,
                        help="Capsule volume fraction (default: 0.12)")
    p_mat.add_argument("--gain", dest="mat_frob_gain", type=float, default=1.5,
                        help="Feedback gain (default: 1.5)")
    p_mat.add_argument("--cycles", dest="mat_frob_cycles", type=int, default=25,
                        help="Load cycles for Frobenius / Ouroboric (default: 25/30)")
    p_mat.add_argument("--heal-steps", dest="mat_frob_heal_steps", type=int, default=10,
                        help="Heal steps per cycle (default: 10)")
    # ouroboric alloy params
    p_mat.add_argument("--grains", dest="mat_ouro_grains", type=int, default=64,
                        help="Number of grains for Ouroboric alloy (default: 64)")
    p_mat.add_argument("--stress", dest="mat_ouro_stress", type=float, default=800.0,
                        help="Stress amplitude in MPa (default: 800)")
    p_mat.add_argument("--compare", dest="mat_ouro_compare", action="store_true",
                        help="Run comparative analysis for Ouroboric alloy")

    # cdxml — Chemical CDXML generation
    p_cdxml = subparsers.add_parser("cdxml", help="CDXML chemical structure generation (v2-correct format)",
                                    epilog=EXAMPLES.get("cdxml", "Generate CDXML for molecules, aptamers, and materials"),
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    p_cdxml.add_argument("cdxml_subcommand", choices=["generate", "verify", "clean"],
                          help="cdxml subcommand")
    p_cdxml.add_argument("--smiles", dest="cdxml_smiles", type=str,
                          help="SMILES string to convert")
    p_cdxml.add_argument("--name", dest="cdxml_name", type=str,
                          help="Molecule name for CDXML header")
    p_cdxml.add_argument("--annotation", dest="cdxml_annotation", type=str,
                          help="Annotation text on CDXML canvas")
    p_cdxml.add_argument("--molecule", dest="cdxml_molecule", type=str,
                          help="Generate a predefined molecule by name/filename")
    p_cdxml.add_argument("--all", dest="cdxml_all", action="store_true",
                          help="Generate ALL CDXML files (molecules + aptamers + materials)")
    p_cdxml.add_argument("--molecules-only", dest="cdxml_molecules_only", action="store_true",
                          help="Generate only small molecule CDXML")
    p_cdxml.add_argument("--aptamers-only", dest="cdxml_aptamers_only", action="store_true",
                          help="Generate only aptamer CDXML")
    p_cdxml.add_argument("--materials-only", dest="cdxml_materials_only", action="store_true",
                          help="Generate only material CDXML")
    p_cdxml.add_argument("--output", "-o", dest="cdxml_output", type=str,
                          help="Output directory for CDXML files")
    p_cdxml.add_argument("--file", dest="cdxml_file", type=str,
                          help="CDXML file path for verify")
    p_cdxml.add_argument("--print", dest="cdxml_print", action="store_true",
                          help="Print generated CDXML to stdout")

    p_pipe = subparsers.add_parser("pipeline", help="CLINK Design Pipeline",
                                  epilog=EXAMPLES["pipeline"],
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    p_pipe.add_argument("pipeline_subcommand",
                        choices=["bridges", "ground-up", "from-layer", "actionable"],
                        help="Pipeline subcommand")
    p_pipe.add_argument("start_layer", nargs="?", type=int, default=None,
                        help="Start layer index for from-layer mode")
    p_pipe.add_argument("--organism", type=str, default="mammal",
                        help="Organism type for actionable mode")
    p_pipe.add_argument("target_layer", nargs="?", type=int, default=None,
                        help="Target layer index for from-layer mode")

    # clink
    p_clink = subparsers.add_parser("clink", help="CLINK chain: subatomic to whole organism",
                                   epilog=EXAMPLES["clink"],
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
    p_clink.add_argument("clink_subcommand",
                         choices=["layer", "bridge"],
                         help="CLINK subcommand")
    p_clink.add_argument("layer_args", nargs="*", help="Layer index for 'layer'")

    # alchemy (NEW)
    p_alc = subparsers.add_parser("alchemy", help="Alchemical Bridge — map alchemical treatises to molecular designs",
                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                  epilog="""Examples:
  rebis.py alchemy report                  # Full bridge report
  rebis.py alchemy tier O_inf_self_modeling # Analyze a tier
  rebis.py alchemy scroll-family           # Scroll family (phi=odot, Omega=Z)
  rebis.py alchemy suggest O1_pedagogical   # Suggest molecular designs from tier
  rebis.py alchemy trace O_inf_self_modeling # Trace grand sequence on treatise tuple
  rebis.py alchemy operate --tuple D,T,R,P,F,K,G,C,Phi,H,S,Omega --operation calcination
""")
    p_alc.add_argument("alchemy_subcommand",
                        choices=["report", "tier", "scroll-family", "suggest", "trace", "operate", "greenfire", "wavelength", "host", "bind", "retro", "grand-sequence", "decode", "learn", "alchemical-mol", "zosimos", "portico", "stilling", "ladder", "key", "opus"],
                        help="Alchemical bridge subcommand")
    p_alc.add_argument("alchemy_treatise", nargs="?", default=None,
                        help="Treatise name or tier identifier")
    p_alc.add_argument("--tuple", dest="alchemy_tuple", type=str,
                        help="Comma-separated 12-tuple for 'operate'")
    p_alc.add_argument("--operation", dest="alchemy_operation", type=str,
                        help="Alchemical operation for 'operate'")
    p_alc.add_argument("--guest", dest="guest_smiles", type=str,
                        help="Guest SMILES for 'bind'")
    p_alc.add_argument("--modern", dest="modern_term", type=str,
                        help="Modern scientific term for 'learn'")
    p_alc.add_argument("--key-number", dest="key_number", type=int,
                        help="Key number (1-12) for 'key'")
    p_alc.add_argument("--substrate", dest="substrate", type=str,
                        help="Substrate SMILES for 'greenfire'")


    p_clink.add_argument("--bridge-comp", dest="bridge_comp",
                         help="Component for 'bridge' (serpentrod/ch3mpiler/gene_imscriber)")
    p_clink.add_argument("--bridge-target", dest="bridge_target",
                         help="Target layer index for 'bridge' (0-8)")

    # run
    p_run = subparsers.add_parser("run", help="Run any discoverable script or module (use 'run list' to see all)",
                                 epilog=EXAMPLES["run"],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p_run.add_argument("subcommand", nargs="?", default="list",
                       help="Target name, or 'list' to show all available targets")
    p_run.add_argument("rest", nargs=argparse.REMAINDER,
                       help="Arguments to pass to the target")

    # scripts
    p_scr = subparsers.add_parser("scripts", help="List or invoke scripts in scripts/",
                                 epilog=EXAMPLES["scripts"],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p_scr.add_argument("scripts_subcommand", choices=["list", "run"],
                       help="list — show all scripts; run — invoke one")
    p_scr.add_argument("script_name", nargs="?", help="Script name for 'run'")
    p_scr.add_argument("script_args", nargs=argparse.REMAINDER,
                       help="Arguments forwarded to the script")

    # at — Ars Therapeutica
    p_at = subparsers.add_parser("at", help="Ars Therapeutica — structural therapy navigator",
                                 epilog=EXAMPLES.get("at", "Grammar-derived optimal therapy design and structural diagnosis"),
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p_at.add_argument("at_subcommand",
                      choices=["list", "diagnose", "therapy", "compare", "tensor", "meet", "spectrum", "operate"],
                      help="at subcommand: list therapies, diagnose a disease, show therapy protocol, compare types, compute tensor/meet, show psychiatric spectrum, or run structural operations")
    p_at.add_argument("at_args", nargs="*", help="Arguments for the subcommand (disease name, type names)")

    args = parser.parse_args()

    if args.command == "status":
        return cmd_status(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "pipeline":
        return cmd_pipeline(args)
    elif args.command == "clink":
        return cmd_clink(args)
    elif args.command == "materials":
        return cmd_materials(args)
    elif args.command == "imas":
        return cmd_imas(args)
    elif args.command == "cdxml":
        return cmd_cdxml(args)
    elif args.command == "run":
        return cmd_run(args)
    elif args.command == "scripts":
        return cmd_scripts(args)
    elif args.command == "at":
        return cmd_at(args)
    elif args.command == "alchemy":
        return cmd_alchemy(args)
    else:
        parser.print_help()
        return 1


def cmd_at(args):
    """Ars Therapeutica — structural therapy navigator."""
    from Ars_Therapeutica.ars_therapeutica.cli import main as at_main
    import sys
    # Build argv from parsed args
    argv = ["at"] + [args.at_subcommand] + list(args.at_args)
    # Redirect sys.argv temporarily for the existing CLI
    old_argv = sys.argv
    sys.argv = argv
    try:
        at_main()
    finally:
        sys.argv = old_argv
    return 0


def cmd_alchemy(args):
    """Alchemy Bridge — map alchemical treatise types to molecular designs.
    
    Includes 6 fully functional computational engines:
      greenfire — Photocatalytic cycle discovery (Secret Fire)
      third — Supramolecular cavity/void design (Salt)
      retro — Solve et Coagula retrosynthesis
      decode — Cryptic alchemical → modern science co-type matching
      zosimos — 12-primitive structural analysis + Stilling Practice
      ladder — 12-step promotion ladder (Basil Valentine's Twelve Keys)
    """
    from alchemical_bridge import AlchemicalBridge
    from alchemical_bridge.operations import AlchemicalOperations, apply_operation
    
    bridge = AlchemicalBridge()
    sub = args.alchemy_subcommand
    
    if sub == "report":
        print(bridge.full_report())
        return 0

    # ── Original subcommands ──────────────────────────────────
    elif sub == "tier":
        tname = args.alchemy_treatise
        if tname:
            import json
            analysis = bridge.analyze_treatise(tname)
            print(json.dumps(analysis, indent=2))
        else:
            print("Usage: rebis.py alchemy tier <treatise_name>")
            print("Available tiers: O_inf_self_modeling, O2_irreducible_product, O1_pedagogical, O1_reformist, O1_kabbalistic, O1_supercritical, O0_metadata, O0_practical")
            return 1
        return 0
    elif sub == "scroll-family":
        import json
        fam = bridge.analyze_scroll_family()
        print(json.dumps(fam, indent=2))
        return 0
    elif sub == "suggest":
        import json
        result = bridge.suggest_design(args.alchemy_treatise)
        print(json.dumps(result, indent=2))
        return 0
    elif sub == "trace":
        import json
        trace = bridge.trace_opus_on_treatise(args.alchemy_treatise)
        print(json.dumps(trace, indent=2, default=str))
        return 0
    elif sub == "operate":
        tup_str = args.alchemy_tuple
        op_name = args.alchemy_operation
        if not tup_str or not op_name:
            print("Usage: rebis.py alchemy operate --tuple D,T,R,P,F,K,G,C,Phi,H,S,Omega --operation <name>")
            ops = [n for n, _, _ in AlchemicalOperations.list_operations()]
            print("Operations:", ", ".join(ops))
            return 1
        parts = tup_str.split(",")
        if len(parts) != 12:
            print("Tuple must have exactly 12 comma-separated values")
            return 1
        from shared.primitives import ORDINALS, PRIMITIVE_ORDER
        tup_dict = {}
        for i, prim in enumerate(PRIMITIVE_ORDER):
            glyph = parts[i].strip()
            ord_map = ORDINALS.get(prim, {})
            rev_map = {str(v): k for k, v in ord_map.items()}
            resolved = rev_map.get(glyph) or glyph
            tup_dict[prim] = resolved
        result = apply_operation(tup_dict, op_name)
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    # ── NEW: Green Fire Engine ────────────────────────────────
    elif sub == "greenfire":
        smiles = args.alchemy_treatise
        if not smiles:
            print("Usage: rebis.py alchemy greenfire <catalyst_SMILES>")
            return 1
        result = bridge.analyze_photocatalyst(smiles, getattr(args, 'substrate', None))
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    elif sub == "wavelength":
        smiles = args.alchemy_treatise
        if not smiles:
            print("Usage: rebis.py alchemy wavelength <catalyst_SMILES>")
            return 1
        result = bridge.suggest_wavelength(smiles)
        import json
        print(json.dumps(result, indent=2))
        return 0

    # ── NEW: Alchemical Third Engine ──────────────────────────
    elif sub == "host":
        smiles = args.alchemy_treatise
        if not smiles:
            print("Usage: rebis.py alchemy host <host_SMILES>")
            return 1
        result = bridge.analyze_host(smiles)
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    elif sub == "bind":
        host = args.alchemy_treatise
        guest = args.guest_smiles if hasattr(args, 'guest_smiles') else None
        if not host or not guest:
            print("Usage: rebis.py alchemy bind <host_SMILES> --guest <guest_SMILES>")
            return 1
        result = bridge.compute_binding(host, guest)
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    # ── NEW: Retrosynthetic Stone Engine ──────────────────────
    elif sub == "retro":
        smiles = args.alchemy_treatise
        if not smiles:
            print("Usage: rebis.py alchemy retro <target_SMILES>")
            return 1
        result = bridge.plan_synthesis(smiles)
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    elif sub == "grand-sequence":
        smiles = args.alchemy_treatise
        if not smiles:
            print("Usage: rebis.py alchemy grand-sequence <target_SMILES>")
            return 1
        result = bridge.grand_sequence_synthesis(smiles)
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    # ── NEW: Artephius Decoder ────────────────────────────────
    elif sub == "decode":
        phrase = args.alchemy_treatise
        if not phrase:
            print("Usage: rebis.py alchemy decode '<cryptic_phrase>'")
            return 1
        result = bridge.decode_cryptic(phrase)
        import json
        print(json.dumps(result, indent=2))
        return 0

    elif sub == "learn":
        cryptic = args.alchemy_treatise
        modern = args.modern_term if hasattr(args, 'modern_term') else None
        if not cryptic or not modern:
            print("Usage: rebis.py alchemy learn '<cryptic>' --modern '<modern>'")
            return 1
        result = bridge.learn_decoding(cryptic, modern, "user_discovery", 0.8, "user")
        import json
        print(json.dumps(result, indent=2))
        return 0

    elif sub == "alchemical-mol":
        smiles = args.alchemy_treatise
        if not smiles:
            print("Usage: rebis.py alchemy alchemical-mol <SMILES>")
            return 1
        result = bridge.decode_molecule(smiles)
        import json
        print(json.dumps(result, indent=2))
        return 0

    # ── NEW: Zosimos Engine ───────────────────────────────────
    elif sub == "zosimos":
        tup_str = args.alchemy_tuple
        if not tup_str:
            print("Usage: rebis.py alchemy zosimos --tuple D,T,R,P,F,K,G,C,Phi,H,S,Omega")
            return 1
        parts = tup_str.split(",")
        if len(parts) != 12:
            print("Tuple must have exactly 12 comma-separated values")
            return 1
        from shared.primitives import ORDINALS, PRIMITIVE_ORDER
        tup_dict = {}
        for i, prim in enumerate(PRIMITIVE_ORDER):
            glyph = parts[i].strip()
            ord_map = ORDINALS.get(prim, {})
            rev_map = {str(v): k for k, v in ord_map.items()}
            resolved = rev_map.get(glyph) or glyph
            tup_dict[prim] = resolved
        result = bridge.analyze_structure("user_system", tup_dict)
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    elif sub == "portico":
        tup_str = args.alchemy_tuple
        if not tup_str:
            print("Usage: rebis.py alchemy portico --tuple D,T,R,P,F,K,G,C,Phi,H,S,Omega")
            return 1
        parts = tup_str.split(",")
        if len(parts) != 12:
            print("Tuple must have exactly 12 comma-separated values")
            return 1
        from shared.primitives import ORDINALS, PRIMITIVE_ORDER
        tup_dict = {}
        for i, prim in enumerate(PRIMITIVE_ORDER):
            glyph = parts[i].strip()
            ord_map = ORDINALS.get(prim, {})
            rev_map = {str(v): k for k, v in ord_map.items()}
            resolved = rev_map.get(glyph) or glyph
            tup_dict[prim] = resolved
        result = bridge.check_portico(tup_dict)
        import json
        print(json.dumps(result, indent=2))
        return 0

    elif sub == "stilling":
        tup_str = args.alchemy_tuple
        if not tup_str:
            print("Usage: rebis.py alchemy stilling --tuple D,T,R,P,F,K,G,C,Phi,H,S,Omega")
            return 1
        parts = tup_str.split(",")
        if len(parts) != 12:
            print("Tuple must have exactly 12 comma-separated values")
            return 1
        from shared.primitives import ORDINALS, PRIMITIVE_ORDER
        tup_dict = {}
        for i, prim in enumerate(PRIMITIVE_ORDER):
            glyph = parts[i].strip()
            ord_map = ORDINALS.get(prim, {})
            rev_map = {str(v): k for k, v in ord_map.items()}
            resolved = rev_map.get(glyph) or glyph
            tup_dict[prim] = resolved
        result = bridge.perform_stilling(tup_dict)
        import json
        print(json.dumps(result, indent=2))
        return 0

    # ── NEW: Basil Valentine Ladder ───────────────────────────
    elif sub == "ladder":
        tup_str = args.alchemy_tuple
        if not tup_str:
            # Default: climb from O₀ to Stone
            result = bridge.full_opus_report()
        else:
            parts = tup_str.split(",")
            if len(parts) != 12:
                print("Tuple must have exactly 12 comma-separated values")
                return 1
            from shared.primitives import ORDINALS, PRIMITIVE_ORDER
            tup_dict = {}
            for i, prim in enumerate(PRIMITIVE_ORDER):
                glyph = parts[i].strip()
                ord_map = ORDINALS.get(prim, {})
                rev_map = {str(v): k for k, v in ord_map.items()}
                resolved = rev_map.get(glyph) or glyph
                tup_dict[prim] = resolved
            result = bridge.climb_to_stone(tup_dict)
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    elif sub == "key":
        key_num = args.key_number if hasattr(args, 'key_number') else None
        if key_num is None:
            print("Usage: rebis.py alchemy key <1-12>")
            return 1
        result = bridge.key_info(int(key_num))
        import json
        print(json.dumps(result, indent=2))
        return 0

    elif sub == "opus":
        result = bridge.full_opus_report()
        import json
        print(json.dumps(result, indent=2, default=str))
        return 0

    else:
        print("Unknown subcommand. Use:")
        print("  report, tier, scroll-family, suggest, trace, operate")
        print("  greenfire, wavelength, host, bind")
        print("  retro, grand-sequence")
        print("  decode, learn, alchemical-mol")
        print("  zosimos, portico, stilling")
        print("  ladder, key, opus")
        return 1

if __name__ == "__main__":
    sys.exit(main())
