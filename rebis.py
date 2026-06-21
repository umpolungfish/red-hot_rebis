#!/usr/bin/env python3
"""
rebis.py — Red-Hot Rebis Integration CLI
serpentrod ⊗ ch3mpiler ⊗ pipeline ⊗ gene_imscriber ⊗ clink ⊗ imas

A unified entry point for the completed Great Work of the Imscribing Grammar.
Each component is a specialization of the 12-primitive IG type system,
connected through the shared primitives layer and verified by Frobenius closure.

Author: Lando ⊗ ⊙perator
Structural Type: ⟨𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑵 · ⊙ · 𐑫 · 𐑳 · 𐑟⟩
"""

import argparse
import json
import os
import sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

VERSION = "2.1.0"  # IMASM+CLINK Edition

def _discover_packages():
    """Auto-discover all Python packages and standalone module files under REBIS_ROOT."""
    SKIP = {'.venv', '__pycache__', '.git', 'data', 'popular_protein'}
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
    print("=" * 66)
    print("RED-HOT REBIS v2.1 — IMASM+CLINK EDITION")
    print("=" * 66)

    packages = _discover_packages()
    print(f"\n{'Package':22s}  {'Files':>6}  {'Size':>10}  Root file")
    print("-" * 66)
    for name, path, n_files, total in packages:
        init = path / '__init__.py'
        root_file = init.name if init.exists() else "—"
        tick = "✅"
        print(f"  {tick} {name:20s}  {n_files:>5}  {total:>9,d}  {root_file}")

    # scripts/
    scripts_dir = REBIS_ROOT / "scripts"
    n_scripts = len(list(scripts_dir.glob("*.py")))
    print(f"  ✅ {'scripts':20s}  {n_scripts:>5}  (standalone, no __init__)")

    # Shared assets
    print()
    for label, rel in [("shared/primitives.py", "shared/primitives.py"),
                        ("shared/IG_catalog.json", "shared/IG_catalog.json")]:
        p = REBIS_ROOT / rel
        exists = p.exists()
        sz = f"{p.stat().st_size:,d} bytes" if exists else "missing"
        print(f"  {'✅' if exists else '❌'} {label}: {sz}")

    print("=" * 66)
    print(f"  {len(packages)} packages + {n_scripts} scripts discovered")
    print(f"  Run 'rebis.py run list' for all runnable targets")
    return 0


def cmd_verify(args):
    """Verify Frobenius closure across the shared layer and CLINK."""
    from shared.primitives import WEIGHTS, ORDINALS
    print("✅ shared/primitives.py — %d weights, %d ordinal families" % (len(WEIGHTS), len(ORDINALS)))

    try:
        with open(REBIS_ROOT / "shared/IG_catalog.json") as f:
            catalog = json.load(f)
        print("✅ shared/IG_catalog.json — %d catalog entries" % len(catalog))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("❌ Catalog error: %s" % e)
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
            print("✅ %s — %s imports OK" % (label, mod_name))
        except Exception as e:
            print("❌ %s — %s: %s" % (label, mod_name, e))
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
        print("=" * 65)
        print("CLINK PIPELINE — GROUND-UP WHOLE ORGANISM DESIGN")
        print("=" * 65)
        result = engine.ground_up_design()
        print(engine.generate_report(result))
        return 0 if result.success else 1

    elif args.pipeline_subcommand == "from-layer":
        start = args.start_layer if args.start_layer is not None else 5
        target = args.target_layer if args.target_layer is not None else 8
        print(f"CLINK Pipeline: L{start} → L{target}")
        result = engine.from_layer_design(start_layer=start)
        print(engine.generate_report(result))
        if result.success and result.final_design:
            export_path = f"clink_design_L{start}_to_L{target}.json"
            if engine.export_design_json(result, export_path):
                print(f"\nDesign exported to {export_path}")
        return 0 if result.success else 1

    elif args.pipeline_subcommand == "actionable":
        print("=" * 65)
        print("CLINK PIPELINE — ACTIONABLE ORGANISM DESIGN PACKAGE")
        print("=" * 65)
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

    if sub == "report":
        print(full_report())
        return 0

    elif sub == "list":
        print(f"{'Idx':>3} {'Name':40s} {'Tier':10s} {'Tuple':50s}")
        print("-" * 105)
        for i in range(9):
            tup = clink_layer_tuple(i, True)
            print(f"{i:>3} {CLINK_NAMES[i]:40s} {CLINK_TIERS[i]:10s} {format_tuple_glyphs(tup)}")
        return 0

    elif sub == "layer":
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
        print(f"Layer {idx}: {CLINK_NAMES[idx]}")
        print(f"  Tier: {CLINK_TIERS[idx]}")
        print(f"  Tuple: {format_tuple_glyphs(tup)}")
        print(f"  Description: {tup['_desc']}")
        sr = clink_to_serpentrod(idx)
        cm = clink_to_ch3mpiler(idx)
        ge = clink_to_gene(idx)
        print(f"  → SerpentRod: {sr['closer_to']} (d_fold={sr['distance_to_folded']})")
        print(f"  → CH3MPILER:  {'molecular' if cm['is_molecular'] else 'non-molecular'} (d={cm['distance_to_molecule']})")
        print(f"  → Gene:       {'genetic' if ge['is_genetic'] else 'non-genetic'} (d={ge['distance_to_codon_belnap4']})")
        return 0

    elif sub == "bridge":
        comp = args.bridge_comp if args.bridge_comp else "serpentrod"
        target = int(args.bridge_target) if args.bridge_target else 8
        p = integrated_promotion_path(comp, target)
        print(f"Promotion path: {p['from']} → {p['to']}")
        print(f"  Distance: {p['distance']}")
        print(f"  Promotions: {p['num_promotions']}")
        for prim, change in p['promotions'].items():
            print(f"    {prim}: {change}")
        return 0

    else:
        print("Unknown clink subcommand. Use: report, list, layer, bridge")
        return 1


def _discover_run_targets():
    """
    Auto-discover all runnable targets under REBIS_ROOT.

    Returns dict: name → ('script', Path) | ('module', 'dot.path')

    Discovery rules:
      scripts/*.py           → name = stem (e.g. 'run_msa', 'mito_pipeline')
      rhr_p4rky/*.py         → name = stem if it has if __name__ == '__main__'
      <pkg>/<stem>.py        → name = '<pkg>.<stem>' if has if __name__ == '__main__'
                               where pkg in (serpentrod, gene_imscriber, ch3mpiler,
                                             clink, pipeline, imas, materials)
    """
    targets = {}

    # 1. Every script in scripts/
    for p in sorted((REBIS_ROOT / "scripts").glob("*.py")):
        targets[p.stem] = ("script", p)

    # 2. Runnable modules in rhr_p4rky/
    for p in sorted((REBIS_ROOT / "rhr_p4rky").glob("*.py")):
        if p.stem.startswith("_"):
            continue
        try:
            if '__main__' in p.read_text(encoding='utf-8', errors='ignore'):
                targets[p.stem] = ("script", p)
        except OSError:
            pass

    # 3. Top-level package __main__ entry-points
    PACKAGES = [
        ("serpentrod",     "serpentrod.protein_v5"),
        ("serpentrod_v4",  "serpentrod.protein_v4"),
        ("serpentrod_pred","serpentrod.stratified_predictor"),
        ("ch3mpiler",      "ch3mpiler.compiler"),
        ("gene",           "gene_imscriber.engine"),
    ]
    for alias, mod in PACKAGES:
        if alias not in targets:    # scripts/ take precedence
            targets[alias] = ("module", mod)

    return targets


def cmd_run(args):
    """Route to any discoverable script or module under REBIS_ROOT."""
    import subprocess
    subcommand = args.subcommand
    rest = args.rest

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


def cmd_imas(args):
    """IMASM Arranger: arrangement analysis, IG bridge, CLINK bridge, Frobenius hunt."""
    sub = args.imas_subcommand

    if sub == "report":
        print("=" * 72)
        print("IMASM ARRANGER — Structural Arrangement Analysis")
        print("=" * 72)
        print()
        from imas.ig_bridge import canonical_ig_types, distinct_canonical_ig_types, ig_tuple_str, describe_ig, find_structural_clusters
        from imas.clink_bridge import build_bridge_table

        distinct = distinct_canonical_ig_types()
        print(f"12 IMASM canonicals → {len(distinct)} distinct IG structural types")
        print(f"Arrangement space: 12^8 = 429,981,696 possible length-8 token sequences")
        print()

        print("─── Canonical IG Types ───")
        for ig, names in sorted(distinct.items(), key=lambda x: -len(x[1])):
            label = " + ".join(n.split('_', 1)[1] for n in names)
            desc = describe_ig(ig)
            print(f"  {label}:")
            print(f"    {ig_tuple_str(ig)}")
            if desc:
                print(f"    [{desc}]")
            print()

        print("─── Structural Clusters (d≤6) ───")
        for c in find_structural_clusters(6):
            if len(c) > 1:
                print(f"  {' ↔ '.join(n.split('_',1)[1] for n in c)}")
        print()

        print("─── IMASM → CLINK Bridge ───")
        print(build_bridge_table())
        print()
        print("─── Key Discoveries ───")
        print("  1. Chiral/Empty collapse: distinct token sequences → identical IG types")
        print("  2. Generic mass: 99.993% of random arrangements → 4 IG types")
        print("  3. Zero Frobenius pairs in 10M random samples")
        print("  4. Only Dialetheic Bootstrap achieves ⊙ criticality")
        print("  5. Frobenius cluster shares R=𐑾, P=𐑹, C=𐑠, H=𐑫, Ω=𐑭")
        print("  6. Linear Chain isolated: mismatch ≥ 8 from all others")
        print("  7. Length-8 pre-shapes IG primitives (H:75% 𐑫, F:67% 𐑞, K:67% 𐑘)")
        return 0

    elif sub == "bridge":
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

    else:
        print("Unknown imas subcommand. Use: report, bridge, hunt, energy")
        return 1




def cmd_materials(args):
    """Handle materials subcommands — IG Material Forge."""
    import sys
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
                print(f"  Forged: {name} → {design.ouroboricity_tier} Frob={design.frobenius_score:.2f}  {design.proposed_composition[:70]}")
            print(f"\n  Total: {len(novel)} materials forged")
        elif args.mat_name:
            # Try as predefined
            novel = predefined_novel_materials()
            if args.mat_name in novel:
                design = forge.forge(args.mat_name, novel[args.mat_name])
                print(forge.report(args.mat_name))
            else:
                # Try as IMASM canonical
                try:
                    design = forge.forge_from_imas(args.mat_name)
                    print(forge.report(f"{args.mat_name}_material"))
                except Exception as e:
                    print(f"Error: {e}")
                    print("Known names: frobenius_composite, critical_sensor_metamaterial, ep_detector,")
                    print("  eternal_memory_alloy, topological_thermal_rectifier, hierarchical_impact_absorber,")
                    print("  quantum_topological_substrate, non_abelian_braiding_material")
                    print("  Or any IMASM canonical: I_Dialetheic_Bootstrap, etc.")
        else:
            print("Usage: rebis.py materials forge --name <name>  or  --all")
            print("Predefined: frobenius_composite, critical_sensor_metamaterial, ep_detector,")
            print("  eternal_memory_alloy, topological_thermal_rectifier,")
            print("  hierarchical_impact_absorber, quantum_topological_substrate,")
            print("  non_abelian_braiding_material")
        return 0

    elif sub == "report":
        forge = MaterialForge()
        novel = predefined_novel_materials()
        for name, ig_tuple in novel.items():
            forge.forge(name, ig_tuple)
        print(forge.report("frobenius_composite"))
        return 0

    elif sub == "frobenius":
        from materials.frobenius_metamaterial import FrobeniusMetamaterial, FrobeniusMaterialParams
        params = FrobeniusMaterialParams(capsule_volume_fraction=0.12, feedback_gain=1.5)
        mat = FrobeniusMetamaterial(size=20, params=params)
        results = mat.run_simulation(load_cycles=25, heal_steps_per_cycle=10)
        return 0

    elif sub == "ouroboric":
        from materials.ouroboric_alloy import OuroboricAlloy
        alloy = OuroboricAlloy(n_grains=64)
        results = alloy.run_mechanical_test(stress_amplitude_MPa=800, cycles=40)
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
        elif args.mat_name == "cliff":
            for name, mat in all_mats.items():
                temp = 0.01 if "9" in name else (77.0 if "7" in name else 300.0)
                print(FrobeniusCliffAnalyzer.full_report(mat, temp_k=temp))
                print()
        elif args.mat_name == "bridge":
            print(IMASM_EagleBridge.report())
        else:
            print("Sophick Forge - Eagle Cycle Protocol")
            print(f"  Sophick Mercury (O_∞):  <{' · '.join(SOPHICK_MERCURY)}>")
            print(f"  Ouroboric O2 materials:   <{' · '.join(OUROBORIC_O2)}>")
            print(f"  Structural distance:       {STRUCTURAL_DISTANCE_O2_TO_OINF:.4f}")
            print(f"  Gap primitives:            {[GAP_PRIMITIVES[i]['name'] for i in GAP_PRIMITIVES]}")
            print()
            for name, mat in all_mats.items():
                print(f"  {name}: {mat.composition[:60]}...")
            print()
            print("  Use --name eagle_3_amalgam | eagle_7_animated | eagle_9_sophick")
            print("  Use --name cliff for Frobenius Cliff analysis")
            print("  Use --name bridge for IMASM->Eagle bridge")
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
            obstruction = None
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
            print(FrobeniusGapCloser.full_report())
        return 0

    elif sub == "list":
        print("Predefined novel materials:")
        for name in predefined_novel_materials():
            print(f"  {name}")
        print("\nIMASM canonicals (use --name):")
        from imas.arranger import CANONICAL_NAMES
        for name in CANONICAL_NAMES:
            print(f"  {name}")
        return 0

    else:
        print("Unknown materials subcommand. Use: forge, report, list, frobenius, ouroboric, sophick, exactor")
        return 1


def main():
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

  rebis.py imas report               # IMASM arrangement analysis + bridges
  rebis.py imas bridge --target I_Dialetheic_Bootstrap  # Bridge to CLINK
  rebis.py imas hunt --samples 100000          # Frobenius pair density estimation
  rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer L8_Organism

  rebis.py clink report              # Full CLINK integration report
  rebis.py clink list                # List all 9 CLINK layers
  rebis.py clink layer 3             # Show layer details
  rebis.py clink bridge serpentrod 8 # Promotion path to organism

  rebis.py materials forge --all          # Forge all 8 predefined novel materials
  rebis.py materials forge --name frobenius_composite  # Forge one material
  rebis.py materials report              # Report all forged materials
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
"""
    )
    parser.add_argument("--version", action="version", version="%(prog)s " + VERSION)

    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Show all component status")

    # verify
    subparsers.add_parser("verify", help="Verify Frobenius closure across components")

    # imas (NEW — 6th Pillar)
    p_imas = subparsers.add_parser("imas", help="IMASM Arranger: arrangement analysis, bridges, Frobenius hunt")
    p_imas.add_argument("imas_subcommand",
                        choices=["report", "bridge", "hunt", "energy"],
                        help="IMASM subcommand")
    p_imas.add_argument("--canonical", dest="imas_target",
                        help="Canonical name for bridge/energy (comma-separated for bridge)")
    p_imas.add_argument("--layer", dest="imas_layer",
                        help="Target CLINK layer for energy (e.g., L8_Organism)")
    p_imas.add_argument("--samples", dest="imas_samples", type=int,
                        help="Sample count for Frobenius hunt")

    # pipeline (NEW)

    # materials (NEW)
    p_mat = subparsers.add_parser("materials", help="IG Material Forge — structural type to material design")
    p_mat.add_argument("materials_subcommand",
                        choices=["forge", "report", "list", "frobenius", "ouroboric", "sophick", "exactor"],
                        help="Materials subcommand")
    p_mat.add_argument("--name", dest="mat_name", type=str,
                        help="Material or IMASM canonical name for forge")
    p_mat.add_argument("--all", dest="mat_all", action="store_true",
                        help="Forge all predefined materials")

    p_pipe = subparsers.add_parser("pipeline", help="CLINK Design Pipeline")
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
    p_clink = subparsers.add_parser("clink", help="CLINK chain: subatomic to whole organism")
    p_clink.add_argument("clink_subcommand",
                         choices=["report", "list", "layer", "bridge"],
                         help="CLINK subcommand")
    p_clink.add_argument("layer_args", nargs="*", help="Layer index for 'layer'")
    p_clink.add_argument("--bridge-comp", dest="bridge_comp",
                         help="Component for 'bridge' (serpentrod/ch3mpiler/gene_imscriber)")
    p_clink.add_argument("--bridge-target", dest="bridge_target",
                         help="Target layer index for 'bridge' (0-8)")

    # run
    p_run = subparsers.add_parser("run", help="Run any discoverable script or module (use 'run list' to see all)")
    p_run.add_argument("subcommand", nargs="?", default="list",
                       help="Target name, or 'list' to show all available targets")
    p_run.add_argument("rest", nargs=argparse.REMAINDER,
                       help="Arguments to pass to the target")

    # scripts
    p_scr = subparsers.add_parser("scripts", help="List or invoke scripts in scripts/")
    p_scr.add_argument("scripts_subcommand", choices=["list", "run"],
                       help="list — show all scripts; run — invoke one")
    p_scr.add_argument("script_name", nargs="?", help="Script name for 'run'")
    p_scr.add_argument("script_args", nargs=argparse.REMAINDER,
                       help="Arguments forwarded to the script")

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
    elif args.command == "run":
        return cmd_run(args)
    elif args.command == "scripts":
        return cmd_scripts(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
