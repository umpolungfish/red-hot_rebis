#!/usr/bin/env python3
"""
_demo_reverse_ligand.py — Demo: Enzyme Active Site → De-Novo Ligand Pipeline.

Demonstrates the complete reverse pipeline workflow:
  1. List the bevy of catalyzing proteins
  2. Generate de-novo ligands for one enzyme (template-based)
  3. Generate de-novo ligands with the improved (RDKit fragment-based) engine
  4. Run on the full bevy
  5. Analyze results

Usage:
  python3 demo_scripts/_demo_reverse_ligand.py          # Full demo (all 10 enzymes)
  python3 demo_scripts/_demo_reverse_ligand.py --quick   # Quick demo (3 enzymes)
  python3 demo_scripts/_demo_reverse_ligand.py --enzyme lysozyme  # Single enzyme

Author: Lando ⊗ ⊙perator
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the pipeline modules
from rhr_p4rky.ligand_from_active_site import (
    CATALYZING_PROTEINS, PROTEIN_LOOKUP, analyze_bevy, 
    analyze_bevy_improved, fmt_tuple
)

# Colors
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

def header(text):
    print(f"\n{BOLD}{CYAN}{'='*70}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'='*70}{RESET}")

def step(text):
    print(f"\n{YELLOW}▶ {text}{RESET}")

def ok(text):
    print(f"  {GREEN}✓ {text}{RESET}")

def run_quick():
    """Quick demo on 3 enzymes."""
    proteins = ["alcohol_dehydrogenase", "urease", "lysozyme"]
    
    header("QUICK DEMO: Reverse Ligand Pipeline (3 Enzymes)")
    
    for pname in proteins:
        p = PROTEIN_LOOKUP[pname]
        step(f"Enzyme: {p['name']} ({p['organism']})")
        print(f"  Active site: {', '.join(p['active_site_residues'])}")
        print(f"  Reaction: {p['reaction']}")
        print(f"  Site type: {fmt_tuple(p.get('structural_type', {}))}")
        
        # Template-based generation
        results = analyze_bevy([pname])
        r = results[0]
        print(f"  Closest bond: {r['closest_bond']} (d={r['bond_distance']})")
        print(f"  Ligand type:  {r['ligand_type_fmt']}")
        
        candidates = r.get("ligand_candidates", [])
        if candidates:
            print(f"  {GREEN}Top candidates:{RESET}")
            for c in candidates[:3]:
                print(f"    {c['smiles']:45s} method={c['method']}")
        print()
    
    # Improved engine
    step("Running IMPROVED engine (RDKit fragment-based) on alcohol dehydrogenase...")
    imp_results = analyze_bevy_improved(["alcohol_dehydrogenase"], max_candidates=5)
    ir = imp_results[0]
    print(f"  Estimated bond: {ir['estimated_bond']}")
    print(f"  Estimated FGs:  {ir['estimated_fgs']}")
    print(f"  Candidates generated: {ir['n_candidates']}")
    for c in ir.get("ligand_candidates", [])[:3]:
        print(f"    {c['smiles']:45s} score={c['composite_score']:.3f}  "
              f"logP={c['logP']:.2f}  MW={c['MW']:.1f}")
    
    header("QUICK DEMO COMPLETE")

def run_full():
    """Full demo on all 10 enzymes with improved engine."""
    header("FULL DEMO: Reverse Ligand Pipeline (10 Enzymes)")
    
    print(f"Bevy of {len(CATALYZING_PROTEINS)} catalyzing proteins:\n")
    for i, p in enumerate(CATALYZING_PROTEINS, 1):
        st = p.get("structural_type", {})
        print(f"  {i:2d}. {p['name']:30s} {fmt_tuple(st)}")
        print(f"      {', '.join(p['active_site_residues'])}")
    
    step("Running IMPROVED engine on all 10 enzymes...")
    start = time.time()
    results = analyze_bevy_improved(max_candidates=10)
    elapsed = time.time() - start
    
    total_candidates = sum(r['n_candidates'] for r in results)
    
    print(f"\n  {GREEN}Results ({total_candidates} candidates across {len(results)} enzymes, "
          f"{elapsed:.1f}s):{RESET}\n")
    print(f"  {'Enzyme':25s} {'Bond':15s} {'Top Ligand':45s} {'Score':8s}")
    print(f"  {'-'*25} {'-'*15} {'-'*45} {'-'*8}")
    
    for r in results:
        top = r.get("ligand_candidates", [{}])
        top_smiles = top[0].get('smiles', '-')[:45] if top else '-'
        top_score = top[0].get('composite_score', 0) if top else 0
        bond = r.get('estimated_bond', '-')
        marker = ""
        if r['protein_name'] == 'alcohol_dehydrogenase' and 'CCO' in top_smiles:
            marker = " ★"
        elif r['protein_name'] == 'urease' and 'NC(=O)NC(N)=O' in top_smiles:
            marker = " ★"
        print(f"  {r['protein_name']:25s} {bond:15s} {top_smiles:45s} {top_score:.3f}{marker}")
    
    ok(f"Total candidates: {total_candidates}")
    
    # Drug-likeness summary
    all_scores = []
    for r in results:
        for c in r.get("ligand_candidates", []):
            all_scores.append({
                'protein': r['protein_name'],
                'smiles': c.get('smiles'),
                'composite': c.get('composite_score', 0),
                'logP': c.get('logP', 0),
                'MW': c.get('MW', 0),
                'HBD': c.get('HBD', 0),
                'HBA': c.get('HBA', 0),
                'TPSA': c.get('TPSA', 0),
            })
    
    lipinski_pass = sum(
        1 for s in all_scores
        if s['MW'] <= 500 and s['logP'] <= 5 and s['HBD'] <= 5 and s['HBA'] <= 10
    )
    
    print(f"\n  Drug-likeness: {lipinski_pass}/{len(all_scores)} Lipinski-compliant "
          f"({100*lipinski_pass/max(len(all_scores),1):.0f}%)")
    
    if all_scores:
        avg_mw = sum(s['MW'] for s in all_scores) / len(all_scores)
        avg_logp = sum(s['logP'] for s in all_scores) / len(all_scores)
        avg_score = sum(s['composite'] for s in all_scores) / len(all_scores)
        print(f"  Average: MW={avg_mw:.0f}, logP={avg_logp:.2f}, score={avg_score:.3f}")
    
    header("FULL DEMO COMPLETE")

def main():
    args = sys.argv[1:]
    
    if '--quick' in args:
        run_quick()
    elif any(a.startswith('--enzyme') for a in args):
        for a in args:
            if a.startswith('--enzyme='):
                pname = a.split('=', 1)[1]
            elif a.startswith('--enzyme') and args.index(a) + 1 < len(args):
                pname = args[args.index(a) + 1]
        
        if pname in PROTEIN_LOOKUP:
            from rhr_p4rky.ligand_from_active_site import analyze_bevy_improved
            header(f"Single Enzyme: {pname}")
            results = analyze_bevy_improved([pname], max_candidates=10)
            r = results[0]
            print(f"  Enzyme:    {r['protein_name']}")
            print(f"  Organism:  {r['organism']}")
            print(f"  Reaction:  {r['reaction']}")
            print(f"  Site type: {r['site_type_fmt']}")
            print(f"  Bond:      {r['estimated_bond']}")
            print(f"  FGs:       {r['estimated_fgs']}")
            print(f"  Ligand type: {r['ligand_type_fmt']}")
            print(f"\n  {GREEN}Top candidates:{RESET}\n")
            print(f"  {'SMILES':50s} {'Score':8s} {'logP':6s} {'MW':7s} {'HBD':4s} {'HBA':4s} {'Method':20s}")
            print(f"  {'-'*50} {'-'*8} {'-'*6} {'-'*7} {'-'*4} {'-'*4} {'-'*20}")
            for c in r.get("ligand_candidates", []):
                print(f"  {c['smiles']:50s} {c['composite_score']:.3f}  "
                      f"{c['logP']:5.2f} {c['MW']:6.1f} {c['HBD']:3d}  {c['HBA']:3d}  "
                      f"{c['method']:20s}")
            
            lipinski = all([
                c['MW'] <= 500 and c['logP'] <= 5 
                and c['HBD'] <= 5 and c['HBA'] <= 10
                for c in r.get("ligand_candidates", [])
            ])
            print(f"\n  Lipinski compliance: {GREEN}✅ {len(r['ligand_candidates'])}/{len(r['ligand_candidates'])}{RESET}" if lipinski else f"\n  Lipinski compliance: ❌")
        else:
            print(f"Unknown enzyme: {pname}")
            print(f"Available: {list(PROTEIN_LOOKUP.keys())}")
            sys.exit(1)
    else:
        run_full()

if __name__ == "__main__":
    main()
