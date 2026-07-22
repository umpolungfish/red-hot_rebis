#!/usr/bin/env python3
"""qp — Quantum Physical Predictor v1.0

Standalone CLI tool for MoDoT-grounded physical property prediction.
Takes any IG structural tuple or catalog name and returns ~30 predicted
physical/chemical/biological properties — from bond energies to band gaps
to enzymatic turnover rates.

Usage:
  qp magnetar                  # Predict from catalog name
  qp <𐑛𐑡𐑽𐑗𐑐𐑧𐑚𐑝𐑢𐑒𐑙𐑷>         # Predict from inline tuple
  qp --list                    # List catalog entries with predictions
  qp --compare magnetar bec    # Compare two systems side by side
  qp --json magnetar           # JSON output for pipeline use
  qp --batch molecules.txt     # Batch predict from file (one entry per line)

All predictions grounded in the 7 verified MoDoT Lean 4 constant modules:
  FineStructureConstant.lean, ProtonElectronMass.lean, LeptonMassRatios.lean,
  BosonMassRatios.lean, GravitationalCoupling.lean, SICFlavorPartition.lean,
  OmegaCorrClosure.lean

Author: Lando⊗⊙perator
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../rhr_p4rky'))

def main():
    parser = argparse.ArgumentParser(
        description='qp — Quantum Physical Predictor (MoDoT-grounded)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  qp magnetar                    # Predict from catalog
  qp '<𐑛𐑡𐑽𐑗𐑐𐑧𐑚𐑝𐑢𐑒𐑙𐑷>'         # Predict from inline tuple
  qp --compare magnetar bec      # Compare two systems
  qp --json magnetar > out.json  # JSON output""")
    
    parser.add_argument('targets', nargs='*', help='Catalog names or IG tuples')
    parser.add_argument('--list', action='store_true', help='List catalog entries with predictions')
    parser.add_argument('--compare', action='store_true', help='Compare multiple targets side by side')
    parser.add_argument('--json', action='store_true', help='JSON output')
    parser.add_argument('--batch', type=str, help='Batch file with one target per line')
    parser.add_argument('--all', action='store_true', help='Predict for ALL catalog entries')
    
    args = parser.parse_args()
    
    # Lazy import
    from rhr_p4rky.physical_predictor import (
        predict_from_name, predict_from_tuple, get_thermochemical_score,
        get_material_quality_score, get_protein_design_score, format_prediction
    )
    from rhr_p4rky.pipeline_integrator import find_best_applications, batch_predict_all
    
    if args.list:
        # List all catalog entries with scores
        results = batch_predict_all()
        print(f"{'Name':<25} {'E_bond':<10} {'E (GPa)':<12} {'E_g (eV)':<10} {'T_melt (K)':<10} {'TC Score':<10} {'Apps':<30}")
        print("-" * 110)
        for name, pred, scores in results:
            apps = ', '.join(pred.applications[:3]) if pred.applications else ''
            print(f"{name:<25} {pred.bond_energy_kJmol:<10.0f} {pred.youngs_modulus_GPa:<12.1f} {pred.band_gap_eV:<10.3f} {pred.melting_temp_K:<10.0f} {scores['thermochemical']:<10.3f} {apps:<30}")
        return
    
    if args.all:
        results = batch_predict_all()
        if args.json:
            data = {}
            for name, pred, scores in results:
                data[name] = {**pred.to_dict(), 'scores': scores}
            print(json.dumps(data, indent=2))
        else:
            for name, pred, scores in results:
                print(f"\n{'='*60}")
                print(f"  {name}")
                print(f"{'='*60}")
                print(format_prediction(pred))
                print(f"  Applications: {', '.join(pred.applications)}")
        return
    
    if args.batch:
        with open(args.batch) as f:
            targets = [line.strip() for line in f if line.strip()]
    else:
        targets = args.targets
    
    if args.compare and len(targets) >= 2:
        # Side-by-side comparison
        preds = []
        for t in targets:
            try:
                preds.append((t, predict_from_name(t)))
            except:
                try:
                    clean = t.replace('<','').replace('>','')
                    chars = [c for c in clean if c.strip()]
                    preds.append((t, predict_from_tuple(t, tuple(chars))))
                except:
                    preds.append((t, None))
        
        if args.json:
            data = {}
            for name, pred in preds:
                if pred:
                    data[name] = {**pred.to_dict(), 'score': get_thermochemical_score(pred)}
                else:
                    data[name] = {'error': 'not found'}
            print(json.dumps(data, indent=2))
        else:
            # Build comparison table
            metrics = [
                ('E_bond (kJ/mol)', 'bond_energy_kJmol', '{:.0f}'),
                ('E (GPa)', 'young_modulus_GPa', '{:.0f}'),
                ('E_g (eV)', 'band_gap_eV', '{:.3f}'),
                ('T_melt (K)', 'melting_temperature_K', '{:.0f}'),
                ('T_D (K)', 'debye_temp_K', '{:.0f}'),
                ('κ (W/mK)', 'thermal_conductivity_WmK', '{:.1f}'),
                ('T_prot (meV)', 'topological_protection_energy_meV', '{:.0f}'),
                ('Enhancement', 'sensitivity_enhancement', '{:.0f}x'),
                ('ΔG_fold (kcal)', 'folding_stability_kcal', '{:.1f}'),
                ('k_cat (s⁻¹)', 'enzymatic_turnover_s', '{:.2e}'),
                ('τ_coh (s)', 'coherence_time_s', '{:.2e}'),
                ('E_qc (eV)', 'quantum_confinement_eV', '{:.3f}'),
            ]
            # Header
            header = f"{'Property':<25}"
            for name, _ in preds:
                header += f"  {name:<22}"
            print(header)
            print("-" * (25 + 24 * len(preds)))
            for label, attr, fmt in metrics:
                row = f"{label:<25}"
                for _, pred in preds:
                    if pred:
                        val = getattr(pred, attr, 0)
                        row += f"  {fmt.format(val):<22}"
                    else:
                        row += f"  {'N/A':<22}"
                print(row)
    else:
        # Single predictions
        if not targets:
            parser.print_help()
            return
        
        for target in targets:
            try:
                # Try catalog name first
                pred = predict_from_name(target)
                if args.json:
                    d = pred.to_dict()
                    d['thermochemical_score'] = get_thermochemical_score(pred)
                    d['material_quality_score'] = get_material_quality_score(pred)
                    d['protein_design_score'] = get_protein_design_score(pred)
                    print(json.dumps(d, indent=2))
                else:
                    print(format_prediction(pred))
                    apps = find_best_applications(target)
                    if apps:
                        print(f"  Best applications: {', '.join(apps[:5])}")
            except Exception as e1:
                try:
                    # Try as inline tuple
                    clean = target.replace('<','').replace('>','')
                    chars = [c for c in clean if c.strip()]
                    if len(chars) == 12:
                        pred = predict_from_tuple(target, tuple(chars))
                        if args.json:
                            print(json.dumps(pred.to_dict(), indent=2))
                        else:
                            print(format_prediction(pred))
                    else:
                        print(f"Error: '{target}' has {len(chars)} primitives (need 12)")
                except Exception as e2:
                    print(f"Error: could not resolve '{target}': {e2}")

if __name__ == '__main__':
    main()
