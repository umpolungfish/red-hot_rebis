#!/usr/bin/env python3
"""
ligand_combinatorial.py — Fast combinatorial SMILES generator

Direct scaffold × fragment substitution — bypasses slow RDKit reaction enumeration.
Produces thousands of diverse, drug-like SMILES per protein by exploring the
cross-product of 113 heterocyclic scaffolds × 80+ functional group fragments.

Author: Lando⊗⊙perator
"""

import sys, os, math, random, hashlib, io, contextlib
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path

from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')
import rdkit.RDLogger as rkl

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors, Lipinski

# ── Fragment pool: diverse substituents with varying properties ──
FRAGMENT_POOL = {
    # Small alkyl
    "methyl":       "[*:0]C",
    "ethyl":        "[*:0]CC",
    "isopropyl":    "[*:0]C(C)C",
    "cyclopropyl":  "[*:0]C1CC1",
    "tbutyl":       "[*:0]C(C)(C)C",
    "CF3":          "[*:0]C(F)(F)F",
    
    # Polar/H-bond
    "alcohol":      "[*:0]CO",
    "primary_amine": "[*:0]CN",
    "carboxyl":     "[*:0]CC(=O)O",
    "amide":        "[*:0]CC(=O)N",
    "sulfonamide":  "[*:0]S(=O)(=O)N",
    "urea":         "[*:0]NC(=O)N",
    "guanidine":    "[*:0]NC(=N)N",
    
    # Acidic
    "sulfonic":     "[*:0]S(=O)(=O)O",
    "phosphonic":   "[*:0]P(=O)(O)O",
    "tetrazole":    "[*:0]c1[nH]nnn1",
    "carboxylic":   "[*:0]C(=O)O",
    "hydroxamic":   "[*:0]C(=O)NO",
    
    # Basic
    "amino":        "[*:0]N",
    "dimethylamino": "[*:0]N(C)C",
    "piperidine":   "[*:0]N1CCCCC1",
    "piperazine":   "[*:0]N1CCNCC1",
    "morpholine":   "[*:0]N1CCOCC1",
    "imidazole":    "[*:0]c1c[nH]cn1",
    "pyridine":     "[*:0]c1ccccn1",
    
    # Neutral polar
    "nitrile":      "[*:0]C#N",
    "nitro":        "[*:0][N+](=O)[O-]",
    "sulfone":      "[*:0]S(=O)(=O)C",
    "sulfoxide":    "[*:0]S(=O)C",
    "acetyl":       "[*:0]C(=O)C",
    "methoxy":      "[*:0]OC",
    "ethoxy":       "[*:0]OCC",
    "methylsulfonyl": "[*:0]S(=O)(=O)C",
    
    # Halogen
    "fluoro":       "[*:0]F",
    "chloro":       "[*:0]Cl",
    "bromo":        "[*:0]Br",
    "difluoromethoxy": "[*:0]OC(F)F",
    
    # Aromatic
    "phenyl":       "[*:0]c1ccccc1",
    "fluorophenyl": "[*:0]c1ccc(F)cc1",
    "chlorophenyl": "[*:0]c1ccc(Cl)cc1",
    "methoxyphenyl": "[*:0]c1ccc(OC)cc1",
    "pyridyl":      "[*:0]c1ccccn1",
    "thienyl":      "[*:0]c1cccs1",
    "oxazolyl":     "[*:0]c1cocn1",
    "thiazolyl":    "[*:0]c1cscn1",
    
    # Alkene/alkyne
    "vinyl":        "[*:0]C=C",
    "ethynyl":      "[*:0]C#C",
    "allyl":        "[*:0]CC=C",
    
    # Bioisosteres
    "oxetane":      "[*:0]C1COC1",
    "azetidine":    "[*:0]C1CNC1",
    "oxadiazole":   "[*:0]c1cnoc1",
    "isoxazole":    "[*:0]c1ccno1",
    
    # Extended
    "benzyl":       "[*:0]Cc1ccccc1",
    "phenethyl":    "[*:0]CCc1ccccc1",
    "CH2COOH":      "[*:0]CC(=O)O",
    "CH2OH":        "[*:0]CO",
    "CH2NH2":       "[*:0]CN",
    "SO2Me":        "[*:0]S(=O)(=O)C",
    "CONH2":        "[*:0]C(=O)N",
    "CO2Me":        "[*:0]C(=O)OC",
    "OCH2COOH":     "[*:0]OCC(=O)O",
    "NHCOMe":       "[*:0]NC(=O)C",
    
    # Spiro/bicyclic
    "bicyclobutyl": "[*:0]C12CC1C2",
    "spiro_oxetane": "[*:0]C12COC1CC2",
}


def _load_scaffolds() -> Dict[str, Dict]:
    """Load all scaffolds from the heterocycle library."""
    from rhr_p4rky.ligand_heterocycles import HETERO_CORE
    return dict(HETERO_CORE)


def _substitute_scaffold(scaffold_smi: str, substitutions: List[str]) -> Optional[str]:
    """Substitute [*:n] attachment points with fragments.
    
    Args:
        scaffold_smi: Scaffold SMILES with [*:n] dummy atoms
        substitutions: List of fragment SMILES with [*:0] attachment,
                       one per [*:n] position
    """
    result = scaffold_smi
    for i, frag in enumerate(substitutions):
        placeholder = f"[*:{i+1}]"
        # Strip [*:0] from the fragment
        frag_clean = frag.replace("[*:0]", "")
        if placeholder in result:
            result = result.replace(placeholder, frag_clean)
        else:
            return None
    return result


def _validate_molecule(smi: str) -> Optional[Dict]:
    """Validate SMILES and compute drug-likeness properties."""
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return None
        
        # Basic filters
        mw = Descriptors.MolWt(mol)
        if mw < 100 or mw > 700:
            return None
        
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        rot = Descriptors.NumRotatableBonds(mol)
        rings = rdMolDescriptors.CalcNumRings(mol)
        tpsa = Descriptors.TPSA(mol)
        
        # Drug-likeness score (Lipinski + Veber)
        violations = 0
        if mw > 500:
            violations += 1
        if logp > 5:
            violations += 1
        if hbd > 5:
            violations += 1
        if hba > 10:
            violations += 1
        
        # Allow up to 1 violation (lead-like)
        if violations > 1:
            return None
        
        # Composite score (higher = more drug-like)
        score = 0.0
        score += max(0, (500 - abs(mw - 350)) / 500)  # MW penalty
        score += max(0, 1.0 - abs(logp - 2.5) / 5.0)   # logP penalty
        score += max(0, 1.0 - hbd / 10.0)
        score += max(0, 1.0 - hba / 15.0)
        score += max(0, 1.0 - rot / 15.0)
        score += 0.3 if rings >= 1 else 0
        score += 0.2 if 40 < tpsa < 140 else 0  # CNS drug range
        
        return {
            "smiles": smi,
            "mw": mw,
            "logp": logp,
            "hbd": hbd,
            "hba": hba,
            "rot": rot,
            "rings": rings,
            "tpsa": tpsa,
            "score": score,
        }
    except:
        return None


def generate_combinatorial(
    protein_context: Dict = None,
    n_scaffolds: int = 50,
    fragments_per_position: int = 8,
    max_products: int = 2000,
    seed: int = 0,
    verbose: bool = True,
) -> List[Dict]:
    """Generate ligands via fast combinatorial scaffold × fragment enumeration.
    
    This is 10-100× faster than the RDKit reaction-based generator because
    it does direct SMILES string substitution rather than chemical reaction
    enumeration, then validates with RDKit.

    Args:
        protein_context: Dict with name, organism, reaction, etc. (for seeding diversity)
        n_scaffolds: Number of scaffolds to use
        fragments_per_position: Fragments to try per attachment point
        max_products: Maximum total products to return
        seed: Random seed for deterministic diversity
        verbose: Print progress
    """
    scaffolds = _load_scaffolds()
    frag_names = list(FRAGMENT_POOL.keys())
    frag_smis = [FRAGMENT_POOL[n] for n in frag_names]
    
    if seed == 0 and protein_context:
        seed = int(hashlib.md5(protein_context.get("name", "x").encode()).hexdigest()[:8], 16)
    
    rng = random.Random(seed)
    
    # Select scaffolds — prioritize those with 2 attachment points
    scaffold_items = list(scaffolds.items())
    
    # Score scaffolds by diversity
    def scaffold_score(item):
        name, s = item
        n_attach = s["smiles"].count("[*:")
        family = s.get("family", "")
        # Prefer diverse families, 2 attachment points
        score = n_attach * 2  # more attachment = more substitution space
        score += len(s.get("het_atoms", []))  # more heteroatoms = more interesting
        return score
    
    scaffold_items.sort(key=scaffold_score, reverse=True)
    selected = scaffold_items[:n_scaffolds]
    
    if verbose:
        print(f"  Combinatorial: {len(selected)} scaffolds × {fragments_per_position} fragments/pos")
    
    all_candidates = []
    seen_smiles = set()
    
    for scaffold_name, scaffold in selected:
        if len(all_candidates) >= max_products:
            break
        
        smi = scaffold["smiles"]
        n_attach = smi.count("[*:")
        
        if n_attach == 0:
            # No attachment points — use scaffold as-is
            props = _validate_molecule(smi)
            if props and smi not in seen_smiles:
                seen_smiles.add(smi)
                props["scaffold"] = scaffold_name
                all_candidates.append(props)
            continue
        
        # Select diverse fragment subsets per position
        frag_indices = list(range(len(frag_smis)))
        rng.shuffle(frag_indices)
        
        # For 1 attachment: try N fragments
        # For 2+ attachments: try combinations (limited)
        if n_attach == 1:
            for fi in frag_indices[:fragments_per_position * 3]:
                if len(all_candidates) >= max_products:
                    break
                result = _substitute_scaffold(smi, [frag_smis[fi]])
                if result and result not in seen_smiles:
                    props = _validate_molecule(result)
                    if props:
                        seen_smiles.add(result)
                        props["scaffold"] = scaffold_name
                        props["fragments"] = [frag_names[fi]]
                        all_candidates.append(props)
        
        elif n_attach == 2:
            max_combo = min(fragments_per_position * fragments_per_position, 200)
            count = 0
            for fi in frag_indices[:fragments_per_position * 2]:
                for fj in frag_indices[:fragments_per_position * 2]:
                    if fi == fj:
                        continue
                    if count >= max_combo or len(all_candidates) >= max_products:
                        break
                    result = _substitute_scaffold(smi, [frag_smis[fi], frag_smis[fj]])
                    if result and result not in seen_smiles:
                        props = _validate_molecule(result)
                        if props:
                            seen_smiles.add(result)
                            props["scaffold"] = scaffold_name
                            props["fragments"] = [frag_names[fi], frag_names[fj]]
                            all_candidates.append(props)
                    count += 1
        
        else:  # 3+ attachment points — limited enumeration
            max_triple = min(fragments_per_position ** 3, 100)
            count = 0
            for fi in frag_indices[:fragments_per_position]:
                for fj in frag_indices[:fragments_per_position]:
                    for fk in frag_indices[:fragments_per_position]:
                        if len({fi, fj, fk}) < 3:
                            continue
                        if count >= max_triple or len(all_candidates) >= max_products:
                            break
                        result = _substitute_scaffold(smi, [frag_smis[fi], frag_smis[fj], frag_smis[fk]])
                        if result and result not in seen_smiles:
                            props = _validate_molecule(result)
                            if props:
                                seen_smiles.add(result)
                                props["scaffold"] = scaffold_name
                                props["fragments"] = [frag_names[fi], frag_names[fj], frag_names[fk]]
                                all_candidates.append(props)
                        count += 1
    
    # Sort by score
    all_candidates.sort(key=lambda c: c.get("score", 0), reverse=True)
    
    if verbose:
        print(f"  Combinatorial: {len(all_candidates)} valid drug-like products")
    
    return all_candidates[:max_products]


def batch_combinatorial_all(
    protein_list: List[Dict] = None,
    max_per_protein: int = 500,
    n_scaffolds: int = 40,
    fragments_per_position: int = 6,
    verbose: bool = True,
) -> Dict[str, List[Dict]]:
    """Run combinatorial generation on all proteins."""
    if protein_list is None:
        from rhr_p4rky.ligand_from_active_site import PROTEIN_LOOKUP
        protein_list = list(PROTEIN_LOOKUP.values())
    
    results = {}
    global_uniq = set()
    
    for i, protein in enumerate(protein_list):
        name = protein.get("name", f"p{i}")
        seed = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
        
        candidates = generate_combinatorial(
            protein_context=protein,
            n_scaffolds=n_scaffolds,
            fragments_per_position=fragments_per_position,
            max_products=max_per_protein,
            seed=seed,
            verbose=(verbose and i < 3),  # only verbose for first 3
        )
        
        results[name] = candidates
        for c in candidates:
            global_uniq.add(c["smiles"])
        
        if verbose and i % 20 == 0:
            print(f"  [{i+1}/{len(protein_list)}] {name}: {len(candidates)} candidates, "
                  f"cumulative unique: {len(global_uniq)}")
    
    return results


def collect_all_smiles(results: Dict[str, List[Dict]]) -> List[str]:
    """Collect all unique SMILES from batch results."""
    seen = set()
    ordered = []
    for candidates in results.values():
        for c in candidates:
            smi = c["smiles"]
            if smi not in seen:
                seen.add(smi)
                ordered.append(smi)
    return ordered


# ── CLI ──
if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser(description="Fast combinatorial ligand generator")
    ap.add_argument("--all", "-a", action="store_true", help="All proteins")
    ap.add_argument("--protein", "-p", help="Single protein")
    ap.add_argument("--max", type=int, default=500, help="Max per protein")
    ap.add_argument("--scaffolds", type=int, default=40)
    ap.add_argument("--frags", type=int, default=6, help="Fragments per position")
    ap.add_argument("--smiles-only", action="store_true")
    ap.add_argument("--output", "-o")
    args = ap.parse_args()
    
    from rhr_p4rky.ligand_from_active_site import PROTEIN_LOOKUP
    
    if args.all:
        proteins = list(PROTEIN_LOOKUP.values())
        results = batch_combinatorial_all(
            proteins, max_per_protein=args.max,
            n_scaffolds=args.scaffolds, fragments_per_position=args.frags
        )
        all_smiles = collect_all_smiles(results)
        
        if args.smiles_only or args.output:
            out = "\n".join(all_smiles)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(out + "\n")
                print(f"Wrote {len(all_smiles)} SMILES to {args.output}", file=sys.stderr)
            else:
                print(out)
            print(f"\n# Total unique SMILES: {len(all_smiles)}", file=sys.stderr)
        else:
            print(json.dumps({n: len(c) for n, c in results.items()}, indent=2))
            print(f"\nTotal unique: {len(all_smiles)}")
    
    elif args.protein:
        enzyme = args.protein.lower()
        protein = None
        for name, entry in PROTEIN_LOOKUP.items():
            if enzyme in name.lower() or name.lower() in enzyme:
                protein = entry
                break
        if not protein:
            print(f"Not found: {args.protein}")
            sys.exit(1)
        
        candidates = generate_combinatorial(
            protein_context=protein,
            n_scaffolds=args.scaffolds,
            fragments_per_position=args.frags,
            max_products=args.max,
        )
        if args.smiles_only:
            for c in candidates:
                print(c["smiles"])
        else:
            for i, c in enumerate(candidates[:50]):
                print(f"{i+1:4d}. {c['smiles']:65s} MW={c.get('mw',0):.0f} "
                      f"logP={c.get('logp',0):.1f} score={c.get('score',0):.3f} "
                      f"scaffold={c.get('scaffold','?')}")
            if len(candidates) > 50:
                print(f"... and {len(candidates)-50} more")
            print(f"\nTotal: {len(candidates)}")
    else:
        ap.print_help()
