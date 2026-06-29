#!/usr/bin/env python3
"""
MOLECULE → MATERIAL BRIDGE
Takes a CAS number or molecule name and produces a complete material design.
Integrates ch3mpiler (reaction analysis) + IG Material Forge (structural type → composition).

Usage:
  python3 molecule_material_bridge.py --cas 58-08-2
  python3 molecule_material_bridge.py --name caffeine
  python3 molecule_material_bridge.py --cas 58-08-2 --forge

Author: Lando⊗⊙perator
"""

import sys, os, json, argparse
from pathlib import Path
from shared.rich_output import *

BASE = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "rhr_p4rky"))

IMSCRIBING_GRAMMAR = Path.home() / "imsgct" / "imscribing_grammar"


def resolve_molecule(cas=None, name=None):
    """Resolve a molecule via ch3mpiler and extract its structural type."""
    sys.path.insert(0, str(IMSCRIBING_GRAMMAR))
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "ch3mpiler_mod", IMSCRIBING_GRAMMAR / "ch3mpiler.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ch3mpiler_mod"] = mod
    spec.loader.exec_module(mod)
    ch3 = mod.Ch3mpiler()
    
    if cas:
        result = ch3.resolve_and_analyze(cas, do_retrosynthesis=True, depth=1)
        mol_name = result.get("cas_info", {}).get("name", cas)
        print(f"[bridge] Resolved CAS {cas} → {mol_name}")
    else:
        result = ch3.analyze(name)
        mol_name = name
    
    # Extract structural type
    fgs = result.get("fgs", [])
    mol_type_str = result.get("type", "")
    
    # Parse structural type
    product_type = {}
    if mol_type_str and "<" in mol_type_str:
        parts = mol_type_str.strip("<>").split(";")
        pnames = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]
        for i, p in enumerate(pnames):
            if i < len(parts):
                product_type[p] = parts[i].strip()
    
    # Get bond and FG types from ch3mpiler data
    bond_types = mod.BOND_TYPES
    fg_types = mod.FG
    
    # Use the best available disconnection or prediction
    cuts = result.get("cuts", [])
    pred = result.get("prediction", {})
    
    if cuts and len(cuts) > 0:
        cut = cuts[0]
        bond_name = cut.get("bond", "sigma_single")
        fg1_name = cut.get("fg1", "amine")
        fg2_name = cut.get("fg2", "carbonyl")
    elif pred:
        bond_name = pred.get("bond", "sigma_single")
        fg1_name = pred.get("fg1", "amine")
        fg2_name = pred.get("fg2", "carbonyl")
    else:
        bond_name = "sigma_single"
        fg1_name = fgs[0] if fgs else "amine"
        fg2_name = fgs[1] if len(fgs) > 1 else fg1_name
    
    print(f"[bridge] Bond: {bond_name}, FGs: {fg1_name} + {fg2_name}")
    print(f"[bridge] FGs detected: {fgs}")
    
    return {
        "name": mol_name,
        "cas": cas,
        "fgs": fgs,
        "bond": bond_name,
        "bond_type": bond_types.get(bond_name, bond_types.get("sigma_single", {})),
        "fg1": fg1_name,
        "fg1_type": fg_types.get(fg1_name, fg_types.get("amine", {})),
        "fg2": fg2_name,
        "fg2_type": fg_types.get(fg2_name, fg_types.get("carbonyl", {})),
        "product_type": product_type,
    }


def molecule_to_material_tuple(mol_data, ch3mpiler_mod=None):
    """Convert molecule structural data to a 12-tuple material IG type.
    
    Strategy: The molecule's reactive primitives (bond-breaking requirements)
    map to material properties. A molecule that requires breaking a strong
    C-N bond needs a material with high interfacial strength (R↑) and
    near-equilibrium processing (K=slow). A molecule with many functional
    groups needs a heterogeneous material (S=multi).
    """
    fgs = mol_data.get("fgs", [])
    bond = mol_data.get("bond", "sigma_single")
    n_fgs = len(fgs)
    
    # D: More FGs → need hierarchical material
    D = '𐑦' if n_fgs >= 5 else ('𐑼' if n_fgs >= 3 else '𐑨')
    
    # T: Complex FG topology → self-referential or network
    if n_fgs >= 5:
        T = '𐑸'
    elif n_fgs >= 3:
        T = '𐑥'
    else:
        T = '𐑡'
    
    # R: Bond strength maps to interface strength
    strong_bonds = {'amide_link', 'cn_sigma', 'ester_link', 'disulfide', 'peptide_bond'}
    weak_bonds = {'hydrogen_bond', 'pi_stacking', 'van_der_waals'}
    if bond in strong_bonds:
        R = '𐑾'  # dynamic/self-healing interface
    elif bond in weak_bonds:
        R = '𐑩'  # weak vdW interface
    else:
        R = '𐑑'  # moderate
    
    # P: Multiple FGs → partially ordered
    P = '𐑹' if n_fgs >= 4 else ('𐑬' if n_fgs >= 2 else '𐑗')
    
    # F: Strong bonds need quantum coherence for catalysis
    F = '𐑐' if bond in strong_bonds else '𐑞'
    
    # K: Strong bonds → near-equilibrium processing
    K = '𐑧' if bond in strong_bonds else '𐑤'
    
    # G: More FGs → longer-range interactions
    G = '𐑲' if n_fgs >= 5 else ('𐑔' if n_fgs >= 3 else '𐑚')
    
    # Gm: Sequential processing for complex molecules
    Gm = '𐑠' if n_fgs >= 3 else '𐑝'
    
    # Ph: Multiple FGs → critical self-modeling
    Ph = '⊙' if n_fgs >= 4 else ('𐑮' if n_fgs >= 2 else '𐑢')
    
    # H: Permanent memory for complex targets
    H = '𐑫' if n_fgs >= 4 else ('𐑖' if n_fgs >= 2 else '𐑒')
    
    # S: More FGs → more components
    S = '𐑳' if n_fgs >= 4 else ('𐑕' if n_fgs >= 2 else '𐑙')
    
    # Omega: Topological protection for strong bonds
    Omega = '𐑭' if bond in strong_bonds else ('𐑴' if bond in weak_bonds else '𐑷')
    
    return (D, T, R, P, F, K, G, Gm, Ph, H, S, Omega)


def main():
    parser = argparse.ArgumentParser(description="Molecule → Material Bridge")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--cas", help="CAS Registry Number")
    input_group.add_argument("--name", help="Molecule name")
    parser.add_argument("--forge", action="store_true", help="Forge full material design")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    # Step 1: Resolve molecule
    mol_data = resolve_molecule(cas=args.cas, name=args.name)
    
    # Step 2: Convert to material IG tuple
    ig_tuple = molecule_to_material_tuple(mol_data)
    
    print(f"\n{'='*60}")
    info_line(f"  MOLECULE → MATERIAL BRIDGE")
    print(f"{'='*60}")
    info_line(f"  Molecule: {mol_data['name']}")
    info_line(f"  CAS: {mol_data.get('cas', 'N/A')}")
    info_line(f"  Bond: {mol_data['bond']}")
    info_line(f"  FGs ({len(mol_data['fgs'])}): {', '.join(mol_data['fgs'])}")
    print(f"\n  Material IG Tuple:")
    pnames = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]
    for i, p in enumerate(pnames):
        info_line(f"    {p}: {ig_tuple[i]}")
    
    # Step 3: Forge material design
    if args.forge:
        from materials.ig_material_forge import MaterialForge

        mf = MaterialForge()
        safe_name = mol_data['name'].replace(' ', '_').replace('-', '_').replace(',', '')[:50]
        design = mf.forge(safe_name, ig_tuple)
        print(f"\n{'-'*60}")
        info_line(f"  FORGED MATERIAL DESIGN")
        print(f"{'-'*60}")
        info_line(f"  Tier: {design.ouroboricity_tier}")
        info_line(f"  Frobenius Score: {design.frobenius_score:.2f}")
        info_line(f"  Composition: {design.proposed_composition}")
        info_line(f"  Processing: {design.proposed_processing}")
        info_line(f"  Properties: {design.predicted_properties}")
        info_line(f"  Applications: {design.proposed_applications}")
    
    if args.json:
        output = {
            "molecule": mol_data["name"],
            "cas": mol_data.get("cas"),
            "material_tuple": list(ig_tuple),
        }
        if args.forge:
            output["design"] = {
                "tier": design.ouroboricity_tier,
                "frobenius_score": design.frobenius_score,
                "composition": design.proposed_composition,
                "processing": design.proposed_processing,
                "properties": design.predicted_properties,
                "applications": design.proposed_applications,
            }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
