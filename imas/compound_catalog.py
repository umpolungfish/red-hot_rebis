#!/usr/bin/env python3
"""
compound_catalog.py — Compound Catalog Registration Pipeline

Registers chemical compounds in the IG file-based catalog from SMILES,
enabling cross-domain analogy search: which materials, proteins, or
consciousness states share structural type with a given molecule?

Pipeline:
    SMILES → IMASM arrangement → StructuralFingerprint → IG 12-tuple → catalog entry

Then:
    catalog entry → nearest-neighbor search across all 3900+ catalog entries

Author: Lando⊗⊙perator
"""

import json, sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Locate shared catalog
REBIS_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REBIS_ROOT / "shared" / "IG_catalog.json"

# Imports
from imas.compound_imasm import analyze_molecule, format_arrangement, molecule_to_arrangement, TOKEN_NAMES
from imas.arranger import compute_fingerprint, StructuralFingerprint, CANONICAL_FINGERPRINTS
from imas.ig_bridge import fingerprint_to_ig, ig_tuple_str, describe_full, PRIMITIVE_NAMES

# ── Shared compound database ──

COMPOUND_DATABASE = {
    # Pharmaceutically relevant compounds
    "aspirin": {
        "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "description": "Acetylsalicylic acid — NSAID, cyclooxygenase inhibitor, analgesic and anti-inflammatory",
    },
    "paracetamol": {
        "smiles": "CC(=O)NC1=CC=C(C=C1)O",
        "description": "Acetaminophen — analgesic and antipyretic, COX inhibitor in CNS",
    },
    "ibuprofen": {
        "smiles": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        "description": "NSAID, COX-1/COX-2 inhibitor, analgesic and anti-inflammatory",
    },
    "caffeine": {
        "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "description": "Xanthine alkaloid — adenosine receptor antagonist, CNS stimulant",
    },
    "morphine": {
        "smiles": "CN1CC[C@]23C4C1CC5=C2C(=C(C=C5)O)OC3C4O",
        "description": "Opiate alkaloid — mu-opioid receptor agonist, potent analgesic",
    },
    "codeine": {
        "smiles": "CN1CC[C@]23C4C1CC5=C2C(=C(C=C5)OC)OC3C4O",
        "description": "Opiate alkaloid — prodrug of morphine, mild to moderate analgesic",
    },
    "dopamine": {
        "smiles": "C1=CC(=C(C=C1CCN)O)O",
        "description": "Catecholamine neurotransmitter — D1-D5 receptor agonist, reward/motor control",
    },
    "serotonin": {
        "smiles": "C1=CC2=C(C=C1O)C(=CN2)CCN",
        "description": "5-Hydroxytryptamine — neurotransmitter, mood/appetite/sleep regulation",
    },
    "adrenaline": {
        "smiles": "CNCC(C1=CC(=C(C=C1)O)O)O",
        "description": "Epinephrine — adrenergic receptor agonist, fight-or-flight hormone",
    },
    "noradrenaline": {
        "smiles": "NCC(C1=CC(=C(C=C1)O)O)O",
        "description": "Norepinephrine — neurotransmitter, arousal/attention/stress response",
    },
    "benzene": {
        "smiles": "c1ccccc1",
        "description": "Aromatic hydrocarbon — prototypical aromatic ring system",
    },
    "toluene": {
        "smiles": "CC1=CC=CC=C1",
        "description": "Methylbenzene — aromatic solvent, methylated benzene",
    },
    "phenol": {
        "smiles": "C1=CC=C(C=C1)O",
        "description": "Hydroxybenzene — aromatic alcohol, antiseptic and precursor",
    },
    "aniline": {
        "smiles": "C1=CC=C(C=C1)N",
        "description": "Aminobenzene — aromatic amine, dye and pharmaceutical precursor",
    },
    "glucose": {
        "smiles": "C(C1C(C(C(C(O1)O)O)O)O)O",
        "description": "D-Glucose — primary energy source in cellular metabolism",
    },
    "fructose": {
        "smiles": "C(C1C(C(C(O1)O)O)O)O",
        "description": "D-Fructose — monosaccharide, fruit sugar",
    },
    "cholesterol": {
        "smiles": "CC(C)CCCC(C)C1CCC2C1(CCC3C2CC=C4C3(CCC(C4)O)C)C",
        "description": "Steroid — cell membrane component, hormone precursor",
    },
    "estradiol": {
        "smiles": "CC12CCC3C(C1CCC2O)CCC4=C3C=CC(=C4)O",
        "description": "Primary estrogen — steroid hormone, female reproductive system",
    },
    "testosterone": {
        "smiles": "CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34",
        "description": "Androgen — steroid hormone, male reproductive system",
    },
    "cortisol": {
        "smiles": "CC12CCC3C(C1CCC2(C(=O)CO)O)CCC4=CC(=O)CCC34",
        "description": "Hydrocortisone — glucocorticoid hormone, stress response",
    },
    "ethanol": {
        "smiles": "CCO",
        "description": "Ethyl alcohol — simple alcohol, CNS depressant",
    },
    "acetic_acid": {
        "smiles": "CC(=O)O",
        "description": "Ethanoic acid — simple carboxylic acid, vinegar component",
    },
    "ammonia": {
        "smiles": "N",
        "description": "Simple base — nitrogen hydride, metabolic waste product",
    },
    "water": {
        "smiles": "O",
        "description": "Water — universal solvent, essential to all known life",
    },
    "carbon_dioxide": {
        "smiles": "C(=O)=O",
        "description": "Carbon dioxide — respiratory waste, greenhouse gas",
    },
    "lysergic_acid": {
        "smiles": "CN1CC(C=C2C1CC3=CNC4=CC=CC2=C34)C(=O)O",
        "description": "Ergoline alkaloid — precursor to LSD, dopamine/serotonin receptor ligand",
    },
    "tryptamine": {
        "smiles": "C1=CC=C2C(=C1)C(=CN2)CCN",
        "description": "Monoamine alkaloid — serotonin precursor, trace amine-associated receptor agonist",
    },
    "psilocin": {
        "smiles": "CN(C)CCC1=CNC2=C1C=C(C=C2)O",
        "description": "Psilocybin metabolite — 5-HT2A serotonin receptor agonist, psychedelic tryptamine",
    },
    "mescaline": {
        "smiles": "COC1=CC(=CC(=C1OC)OC)CCN",
        "description": "Phenethylamine alkaloid — 5-HT2A agonist, psychedelic, found in peyote cactus",
    },
    "dmt": {
        "smiles": "CN(C)CCC1=CNC2=CC=CC=C12",
        "description": "N,N-Dimethyltryptamine — endogenous psychedelic, 5-HT2A agonist, found in plants and mammals",
    },
    "lsd": {
        "smiles": "CCN(CC)C(=O)C1CN(C2CC3=CNC4=CC=CC2=C34)C1",
        "description": "Lysergic acid diethylamide — potent 5-HT2A agonist, prototypical psychedelic",
    },
    "mdma": {
        "smiles": "CC(NC)CC1=CC2=C(C=C1)OCO2",
        "description": "3,4-Methylenedioxymethamphetamine — empathogen, serotonin/norepinephrine/dopamine releaser",
    },
    "cocaine": {
        "smiles": "CN1C2CCC1C(C(C2)OC(=O)C3=CC=CC=C3)C(=O)OC",
        "description": "Tropane alkaloid — dopamine reuptake inhibitor, stimulant and local anesthetic",
    },
    "nicotine": {
        "smiles": "CN1CCCC1C2=CN=CC=C2",
        "description": "Nicotinic acetylcholine receptor agonist — alkaloid stimulant in tobacco",
    },
    "thc": {
        "smiles": "CCCCCC1=CC(=C2C3C=C(C)CCC3C(O2)C1=O)O",
        "description": "Delta-9-tetrahydrocannabinol — cannabinoid CB1/CB2 receptor partial agonist, psychoactive",
    },
    "cbd": {
        "smiles": "CCCCCC1=CC(=C2C3C=C(C)CCC3C(O2)C1=O)O",
        "description": "Cannabidiol — cannabinoid, non-psychoactive, modulates endocannabinoid system",
    },
    "capsaicin": {
        "smiles": "CC(C)=CCCC(C)C(=O)NCC1=CC(=C(C=C1)O)OC",
        "description": "TRPV1 agonist — vanilloid, pungent principle of chili peppers, analgesic",
    },
    "penicillin_g": {
        "smiles": "CC1(C(N2C(S1)C(C2=O)NC(=O)CC3=CC=CC=C3)C(=O)O)C",
        "description": "Beta-lactam antibiotic — penicillin-binding protein inhibitor, bactericidal",
    },
    "cyclosporine_a": {
        "smiles": "CC[C@H](C)C(=O)N[C@@H]([C@H](C)C)C(=O)N[C@@H](CC(C)C)C(=O)N[C@@H](CC(C)C)C(=O)N[C@@H](CC(C)C)C(=O)N[C@@H](CC(C)C)C(=O)N[C@@H](CCCN)C(=O)N[C@@H](CC(C)C)C(=O)N[C@@H](CC(C)C)C(=O)N[C@@H](CC(C)C)C(=O)N1CCC[C@H]1C(=O)N[C@@H](CC(C)C)C(=O)N[C@@H]([C@H](C)C)C(=O)N[C@@H](CCCN)C(=O)O",
        "description": "Cyclic undecapeptide — calcineurin inhibitor, immunosuppressant",
    },
    "digoxin": {
        "smiles": "CC12CCC3C(C1CCC2C4=CC(=O)OC4)CCC5=CC(=O)OC53",
        "description": "Cardiac glycoside — Na+/K+ ATPase inhibitor, heart failure treatment",
    },
    "taxol": {
        "smiles": "CC(=O)O[C@@H]1[C@@H]2C[C@H](O)[C@]3(C)C(=O)[C@@H]4CC(C)=C4[C@H](OC(C)=O)C[C@H]3[C@@]2(C)[C@@H](OC(=O)c2ccccc2)[C@@H](OC(=O)[C@H](O)[C@@H](NC(=O)c2ccccc2)c2ccccc2)[C@]1(C)O",
        "description": "Paclitaxel — microtubule stabilizer, chemotherapeutic, taxane diterpenoid",
    },
    "warfarin": {
        "smiles": "CC(=O)CC(C1=CC=CC=C1)C2=C(C3=CC=CC=C3OC2=O)O",
        "description": "Vitamin K antagonist — anticoagulant, coumarin derivative",
    },
    "sildenafil": {
        "smiles": "CCCC1=NN(C2=NC(=NC(=C12)S(=O)(=O)N3CCN(CC3)C)C)C4=CC(=C(C=C4)OCC)OC",
        "description": "PDE5 inhibitor — vasodilator, erectile dysfunction treatment",
    },
    "atropine": {
        "smiles": "CN1C2CCC1CC(C2)OC(=O)C(CO)C3=CC=CC=C3",
        "description": "Muscarinic acetylcholine receptor antagonist — anticholinergic, tropane alkaloid",
    },
    "quinine": {
        "smiles": "COC1=CC2=C(C=C1)N=CC=C2C(C3CC4CCN3CC4)O",
        "description": "Cinchona alkaloid — antimalarial, Plasmodium hemoglobin degradation inhibitor",
    },
    "curare": {
        "smiles": "COC1=C(C=C2C(=C1)CC3CC2C4=C(C5=C(C=C4OC)OCO5)CCN3C)O",
        "description": "Tubocurarine — nicotinic acetylcholine receptor antagonist, neuromuscular blocking agent",
    },
    "strychnine": {
        "smiles": "C1CC2CN3CC4=C(C5=CC=CC=C5N4)C3CC2C1",
        "description": "Strychnos alkaloid — glycine receptor antagonist, neurotoxic convulsant",
    },
    "reserpine": {
        "smiles": "COC1=CC(=C(C=C1OC)C(=O)OCC2CC3CC4C5C(C(=O)OC)CCC6C5CC(=O)N6C4CC3N(C2)C)OC",
        "description": "Rauwolfia alkaloid — VMAT2 inhibitor, antihypertensive and antipsychotic",
    },
    "ouabain": {
        "smiles": "CC12CCC3C(C1CCC2C4=CC(=O)OC4)CCC5C3(C(C(C(C5)O)O)O)C",
        "description": "Cardiac glycoside — Na+/K+ ATPase inhibitor, arrow poison, cardiotonic",
    },
    "saxitoxin": {
        "smiles": "C1C(N=C(N1)N)C2(C(N=C(N2)N)C(=O)O)CO",
        "description": "Paralytic shellfish toxin — voltage-gated sodium channel blocker, potent neurotoxin",
    },
    "tetrodotoxin": {
        "smiles": "C1C(C2(C(CC3(C1(N2)O)O)O)C4(C3O4)O)O",
        "description": "Pufferfish toxin — voltage-gated sodium channel blocker, potent neurotoxin",
    },
}

def smiles_to_ig(smiles: str) -> Tuple[list, StructuralFingerprint, Tuple[str, ...], str]:
    """Full SMILES → IG pipeline.
    
    Returns: (arrangement, fingerprint, ig_tuple, arrangement_str)
    Raises ValueError if SMILES is invalid.
    """
    result = analyze_molecule(smiles)
    arr = result['arrangement']
    arr_str = format_arrangement(arr)
    fp = compute_fingerprint(arr)
    ig = fingerprint_to_ig(fp)
    return arr, fp, ig, arr_str


def build_catalog_entry(name: str, description: str, ig: Tuple[str, ...]) -> Dict:
    """Build a catalog entry dict from an IG tuple.
    
    Catalog format: {name, description, Ð, Þ, Ř, Φ, ƒ, Ç, Γ, ɢ, ⊙, Ħ, Σ, Ω}
    """
    return {
        "name": name,
        "description": description,
        "Ð": ig[0],
        "Þ": ig[1],
        "Ř": ig[2],
        "Φ": ig[3],
        "ƒ": ig[4],
        "Ç": ig[5],
        "Γ": ig[6],
        "ɢ": ig[7],
        "⊙": ig[8],
        "Ħ": ig[9],
        "Σ": ig[10],
        "Ω": ig[11],
    }


def register_compound(name: str, smiles: str, description: str = "",
                      catalog_path: Path = CATALOG_PATH,
                      dry_run: bool = False) -> Dict:
    """Register a compound in the IG catalog from SMILES.
    
    Returns result dict with ig_tuple, arrangement, and status.
    """
    if not description:
        description = f"Compound: {name}"
    
    # Generate IG tuple from SMILES
    arr, fp, ig, arr_str = smiles_to_ig(smiles)
    
    # Build catalog entry
    entry = build_catalog_entry(name, description, ig)
    
    if dry_run:
        return {
            "name": name,
            "ig_tuple_str": ig_tuple_str(ig),
            "arrangement": arr_str,
            "fingerprint": fp,
            "description": description,
            "status": "dry_run",
        }
    
    # Load existing catalog
    if catalog_path.exists():
        with open(catalog_path) as f:
            catalog = json.load(f)
    else:
        catalog = []
    
    # Check for duplicate
    existing = [e for e in catalog if e.get("name") == name]
    if existing:
        return {
            "name": name,
            "ig_tuple_str": ig_tuple_str(existing[0].get_tuple() if hasattr(existing[0], 'get_tuple') else (ig[0],)),
            "status": "already_exists",
            "message": f"Compound '{name}' already in catalog — skipping",
        }
    
    # Append and save
    catalog.append(entry)
    with open(catalog_path, 'w') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    return {
        "name": name,
        "ig_tuple_str": ig_tuple_str(ig),
        "arrangement": arr_str,
        "description": description,
        "status": "registered",
    }


def register_all_compounds(dry_run: bool = False) -> List[Dict]:
    """Register all compounds in COMPOUND_DATABASE."""
    results = []
    for name, info in COMPOUND_DATABASE.items():
        try:
            result = register_compound(
                name=name,
                smiles=info["smiles"],
                description=info["description"],
                dry_run=dry_run,
            )
            results.append(result)
        except Exception as e:
            results.append({
                "name": name,
                "status": "error",
                "error": str(e),
            })
    return results


# ── Cross-domain analogy search ──

def ig_distance(ig_a: Tuple[str, ...], ig_b: Tuple[str, ...]) -> int:
    """Hamming distance between two IG tuples (primitive mismatch count)."""
    return sum(1 for a, b in zip(ig_a, ig_b) if a != b)


def load_catalog(catalog_path: Path = CATALOG_PATH) -> List[Dict]:
    """Load the IG catalog."""
    if catalog_path.exists():
        with open(catalog_path) as f:
            return json.load(f)
    return []


def entry_to_ig(entry: Dict) -> Optional[Tuple[str, ...]]:
    """Extract IG tuple from a catalog entry."""
    try:
        return (
            entry["Ð"], entry["Þ"], entry["Ř"], entry["Φ"],
            entry["ƒ"], entry["Ç"], entry["Γ"], entry["ɢ"],
            entry["⊙"], entry["Ħ"], entry["Σ"], entry["Ω"],
        )
    except KeyError:
        return None


def find_analogies(name_or_smiles: str, limit: int = 10,
                   catalog_path: Path = CATALOG_PATH) -> List[Dict]:
    """Find nearest structural neighbors in the catalog.
    
    Accepts either a catalog entry name or a SMILES string.
    Returns ranked list of {name, description, distance, mismatches}.
    """
    catalog = load_catalog(catalog_path)
    
    # Resolve query tuple
    query_ig = None
    query_name = name_or_smiles
    
    # Try SMILES first (if it looks like one)
    if any(c in name_or_smiles for c in "CcNOSPFBrI=#()[]"):
        try:
            _, _, query_ig, _ = smiles_to_ig(name_or_smiles)
        except Exception:
            pass
    
    # Try catalog lookup
    if query_ig is None:
        for entry in catalog:
            if entry.get("name") == name_or_smiles:
                query_ig = entry_to_ig(entry)
                query_name = entry.get("name", name_or_smiles)
                break
    
    if query_ig is None:
        raise ValueError(f"Could not resolve '{name_or_smiles}' as SMILES or catalog name")
    
    # Compute distances
    scored = []
    for entry in catalog:
        name = entry.get("name", "???")
        if name == query_name:
            continue
        entry_ig = entry_to_ig(entry)
        if entry_ig is None:
            continue
        d = ig_distance(query_ig, entry_ig)
        mismatches = []
        for i, (a, b) in enumerate(zip(query_ig, entry_ig)):
            if a != b:
                mismatches.append({
                    "primitive": PRIMITIVE_NAMES[i],
                    "query": a,
                    "entry": b,
                })
        scored.append({
            "name": name,
            "description": entry.get("description", ""),
            "distance": d,
            "mismatches": mismatches,
        })
    
    # Sort by distance (ascending)
    scored.sort(key=lambda x: x["distance"])
    return scored[:limit]


def describe_analogies(results: List[Dict], query_name: str = "query") -> str:
    """Format analogy results as a readable string."""
    lines = [f"Nearest structural neighbors to '{query_name}':\n"]
    for r in results:
        d = r["distance"]
        bar = "█" * (12 - d) + "░" * d
        lines.append(f"  d={d:2d}  {bar}  {r['name']}")
        lines.append(f"        {r['description'][:100]}")
        if d > 0 and d <= 4:
            for m in r["mismatches"]:
                lines.append(f"        Δ {m['primitive']}: {m['query']} → {m['entry']}")
        lines.append("")
    return '\n'.join(lines)


# ── CLI ──

def main():
    """CLI entry point: register compounds and find analogies."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Compound Catalog — register molecules & find cross-domain analogies"
    )
    sub = parser.add_subparsers(dest="command")
    
    # register
    reg = sub.add_parser("register", help="Register compounds in catalog")
    reg.add_argument("--smiles", type=str, help="Single SMILES to register")
    reg.add_argument("--name", type=str, help="Name for the compound")
    reg.add_argument("--all", action="store_true", help="Register all compounds in database")
    reg.add_argument("--dry-run", action="store_true", help="Preview without writing")
    
    # analogies
    ana = sub.add_parser("analogies", help="Find cross-domain structural analogies")
    ana.add_argument("query", type=str, nargs="?", help="SMILES or catalog name")
    ana.add_argument("--limit", type=int, default=10, help="Number of results")
    ana.add_argument("--name", type=str, help="Catalog name (alternative to SMILES)")
    
    # show
    show = sub.add_parser("show", help="Show a compound's structural type")
    show.add_argument("query", type=str, nargs="?", help="SMILES or catalog name")
    
    # catalog query
    catq = sub.add_parser("query", help="Query catalog by structural constraints")
    catq.add_argument("--name", type=str, help="Catalog entry name")
    catq.add_argument("--ig", type=str, help="IG tuple as raw string")
    
    args = parser.parse_args()
    
    if args.command == "register":
        if args.all:
            results = register_all_compounds(dry_run=args.dry_run)
            n_ok = sum(1 for r in results if r.get("status") in ("registered", "already_exists"))
            n_err = sum(1 for r in results if r.get("status") == "error")
            print(f"Registered {n_ok}/{len(results)} compounds ({n_err} errors)")
            for r in results:
                status = r.get("status", "?")
                if status == "error":
                    print(f"  ❌ {r['name']}: {r.get('error', 'unknown error')}")
                elif status == "already_exists":
                    print(f"  ⏭️  {r['name']}: {r['ig_tuple_str']} (already exists)")
                elif status == "dry_run":
                    print(f"  🔍 {r['name']}: {r['ig_tuple_str']} (dry run)")
                else:
                    print(f"  ✅ {r['name']}: {r['ig_tuple_str']}")
        elif args.smiles:
            result = register_compound(args.smiles, args.name or "unknown",
                                       dry_run=args.dry_run)
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()
    
    elif args.command == "analogies":
        query = args.query or args.name
        if not query:
            parser.print_help()
            return
        try:
            results = find_analogies(query, limit=args.limit)
            print(describe_analogies(results, query_name=query))
        except ValueError as e:
            print(f"Error: {e}")
    
    elif args.command == "show":
        query = args.query
        if not query:
            parser.print_help()
            return
        # Try SMILES first
        try:
            _, _, ig, arr_str = smiles_to_ig(query)
            print(f"SMILES: {query}")
            print(f"Arrangement: {arr_str}")
            print(f"IG Tuple: {ig_tuple_str(ig)}")
            print(describe_full(ig))
        except Exception:
            # Try catalog lookup
            catalog = load_catalog()
            for entry in catalog:
                if entry.get("name") == query:
                    ig = entry_to_ig(entry)
                    if ig:
                        print(f"Name: {query}")
                        print(f"Description: {entry.get('description', '')}")
                        print(f"IG Tuple: {ig_tuple_str(ig)}")
                        print(describe_full(ig))
                        break
            else:
                print(f"Could not resolve '{query
    # ★⊙ DMT-⊙: autocatalytic DMT analog (self-modeling criticality)
    "5-nitro-bufotenin": {
        "smiles": "CN(C)CCC1=CNC2=CC=C(O)C([N+](=O)[O-])=C12",
        "category": "autocatalytic_tryptamine",
        "properties": {"criticality": "⊙-self_modeling",
                        "discovery": "Crystal-navigated: single primitive 𐑮→⊙ promotion from DMT"}
    },
    "5-nitro-serotonin": {
        "smiles": "NCCC1=CNC2=CC=C(O)C([N+](=O)[O-])=C12",
        "category": "autocatalytic_serotonin",
        "properties": {"criticality": "⊙-self_modeling",
                        "discovery": "Crystal-navigated: single primitive 𐑮→⊙ promotion from serotonin"}
    },
}' as SMILES or catalog name")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
