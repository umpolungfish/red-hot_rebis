#!/usr/bin/env python3
"""precursor_lattice.py — Enriched precursor tree for ch3mpiler.

Adds real chemical intermediates with structural tuples and a PRECURSOR_LATTICE
of verified retrosynthetic disconnections. Enables multi-step pathways like:

  benzene -> nitrobenzene -> aniline -> 4-aminophenol -> paracetamol

Every intermediate has a proper 12-primitive structural type AND its FG composition
is registered in the FG table, so compose_molecule_type() works correctly.

Author: Lando⊗⊙perator
"""
import sys, math, os
from pathlib import Path

# Reuse compiler infrastructure
BASE = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE.parent / "shared"))

from shared.primitives import ORDINALS, WEIGHTS, resolve_ordinal_key

PNAMES = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
FIELD_TO_ORD = {"D":"Ð","T":"Þ","R":"Ř","P":"Φ","F":"ƒ","K":"Ç","G":"Γ","Gm":"ɢ","Ph":"⊙","H":"Ħ","S":"Σ","W":"Ω"}

def _g2v(p, r):
    if not r or r == '?': return '?', 0
    ord_key = FIELD_TO_ORD.get(p, p)
    om = ORDINALS.get(ord_key, {})
    if r in om: return r, om[r]
    try:
        k = resolve_ordinal_key(ord_key, r)
        return k, om[k]
    except Exception: return r, 0

def _glyph_ord(p, glyph):
    _, o = _g2v(p, glyph)
    return o

def _fmt_tup(t):
    return "<" + "".join(t.get(p, "?") for p in PNAMES) + ">"

def _tensor_type(t1, t2):
    r = {}
    for p in PNAMES:
        o1, o2 = _glyph_ord(p, t1.get(p,"?")), _glyph_ord(p, t2.get(p,"?"))
        r[p] = p in ("P","F") and min(o1, o2) or max(o1, o2)
        from compiler import ord_to_glyph
    # Will be patched at import time
    return r

# ====================================================================
# MISSING FG TUPLES — Nitro, diazonium, cyclic, etc.
# These are NOT in compiler.py's FG table. Add them here.
# ====================================================================

ENRICHED_FG = {
    # nitro: -NO2, planar, e-withdrawing, resonance-delocalized
    #   D=triangle (planar)  T=bowtie (crossing resonance NO2<->NO2-)
    #   R=dagger (e-withdrawing by both induction and resonance)
    #   K=moderate (reducible)  W=Z2 (symmetric O-N-O)
    "nitro": {
        "D":"\U00010468","T":"\U00010465","R":"\U0001047D","P":"\U0001046F",
        "F":"\U00010450","K":"\U00010464","G":"\U0001045A","Gm":"\U0001045D",
        "Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010474"
    },
    # diazonium: -N2+, linear, highly reactive, excellent leaving group
    #   D=wedge (0D/linear)  T=network (branching at attachment point)
    #   K=fast (decomposes)  R=dagger (leaving group)
    "diazonium": {
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U0001046F",
        "F":"\U0001045E","K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D",
        "Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010474"
    },
    # cyclic: saturated carbocycle (cyclohexane type)
    #   T=in (containment)  D=triangle (2D — chair/boat)
    #   K=slow (stable ring)  W=0 (no topological invariant)
    "cyclic": {
        "D":"\U00010468","T":"\U00010470","R":"\U00010469","P":"\U00010457",
        "F":"\U0001045E","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D",
        "Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010477"
    },
    # phosphate: -OPO3H2, tetrahedral, polyanionic, high-energy
    #   D=wedge (point-like)  P=asym (no symmetry)  R=dagger (high-energy bond)
    "phosphate": {
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U00010457",
        "F":"\U0001045E","K":"\U00010464","G":"\U0001045A","Gm":"\U0001045D",
        "Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010477"
    },
    # sulfonate: -SO3H, strong acid, e-withdrawing, water-soluble
    "sulfonate": {
        "D":"\U00010468","T":"\U00010465","R":"\U0001047D","P":"\U0001046F",
        "F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D",
        "Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010474"
    },
    # acyl_halide: -COX, highly reactive acylating agent
    "acyl_halide": {
        "D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F",
        "F":"\U0001045E","K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D",
        "Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010477"
    },
    # sulfonamide: -SO2NH2, non-basic N, medicinally important
    "sulfonamide": {
        "D":"\U00010468","T":"\U00010465","R":"\U0001047D","P":"\U00010457",
        "F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460",
        "Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U00010474"
    },
}

# ====================================================================
# PRECURSOR LATTICE — Real retrosynthetic disconnections
# Maps target molecule name -> list of {precursors, bond, fgs, delta}
# ====================================================================

PRECURSOR_LATTICE = {
    # ── Paracetamol (acetaminophen) pathway ──────────────────────
    "paracetamol": [
        {
            "precursors": ["4_aminophenol", "acetic_anhydride"],
            "bond_type": "amide_link",
            "fg1": "amine", "fg2": "carbonyl",
            "delta": 1.2,
            "description": "Acylation of 4-aminophenol with acetic anhydride"
        },
    ],
    "4_aminophenol": [
        {
            "precursors": ["4_nitrophenol"],
            "bond_type": "co_sigma",
            "fg1": "amine", "fg2": "phenol",
            "delta": 1.5,
            "description": "Reduction of 4-nitrophenol to 4-aminophenol"
        },
        {
            "precursors": ["aniline"],
            "bond_type": "co_sigma",
            "fg1": "amine", "fg2": "phenol",
            "delta": 1.2,
            "description": "Hydroxylation of aniline to 4-aminophenol (H2O2/cat)"
        },
    ],
    "4_nitrophenol": [
        {
            "precursors": ["phenol", "nitric_acid"],
            "bond_type": "sigma_single",
            "fg1": "nitro", "fg2": "phenol",
            "delta": 0.8,
            "description": "Nitration of phenol (para-selective)"
        },
    ],
    "acetaminophen": [  # alias for paracetamol
        {
            "precursors": ["4_aminophenol", "acetic_anhydride"],
            "bond_type": "amide_link",
            "fg1": "amine", "fg2": "carbonyl",
            "delta": 1.2,
            "description": "Acylation of 4-aminophenol with acetic anhydride"
        },
    ],
    # ── Classic benzene → nitrobenzene → aniline pathway ─────────
    "nitrobenzene": [
        {
            "precursors": ["benzene", "nitric_acid"],
            "bond_type": "sigma_single",
            "fg1": "nitro", "fg2": "aromatic_ring",
            "delta": 0.8,
            "description": "Electrophilic nitration of benzene (HNO3/H2SO4)"
        },
    ],
    "aniline": [
        {
            "precursors": ["nitrobenzene"],
            "bond_type": "co_sigma",
            "fg1": "amine", "fg2": "aromatic_ring",
            "delta": 0.9,
            "description": "Reduction of nitrobenzene to aniline (Fe/HCl or H2/Pd)"
        },
    ],
    # ── Toluene → benzaldehyde → benzoin pathway ─────────────────
    "benzaldehyde": [
        {
            "precursors": ["toluene"],
            "bond_type": "carbonyl",
            "fg1": "aldehyde", "fg2": "aromatic_ring",
            "delta": 1.1,
            "description": "Oxidation of toluene to benzaldehyde (CrO3/aceite or MnO2)"
        },
    ],
    # ── Phenol → salicylic acid → aspirin pathway ────────────────
    "phenol": [
        {
            "precursors": ["benzene"],
            "bond_type": "co_sigma",
            "fg1": "phenol", "fg2": "aromatic_ring",
            "delta": 1.8,
            "description": "Oxidation of benzene to phenol (H2O2/Fe or cumene process)"
        },
    ],
    "salicylic_acid": [
        {
            "precursors": ["phenol"],
            "bond_type": "carbonyl",
            "fg1": "carboxylic_acid", "fg2": "phenol",
            "delta": 1.3,
            "description": "Kolbe-Schmitt carboxylation of phenol (CO2/NaOH, 125C)"
        },
    ],
    "aspirin": [
        {
            "precursors": ["salicylic_acid", "acetic_anhydride"],
            "bond_type": "ester_link",
            "fg1": "carboxylic_acid", "fg2": "carbonyl",
            "delta": 0.6,
            "description": "Acetylation of salicylic acid (Ac2O/H3PO4)"
        },
    ],
    "2_acetoxybenzoic_acid": [  # alias for aspirin
        {
            "precursors": ["salicylic_acid", "acetic_anhydride"],
            "bond_type": "ester_link",
            "fg1": "carboxylic_acid", "fg2": "carbonyl",
            "delta": 0.6,
            "description": "Acetylation of salicylic acid"
        },
    ],
    # ── Styrene → polystyrene (monomer) pathway ──────────────────
    "styrene": [
        {
            "precursors": ["ethylbenzene"],
            "bond_type": "double_bond",
            "fg1": "alkene", "fg2": "aromatic_ring",
            "delta": 1.5,
            "description": "Dehydrogenation of ethylbenzene (Fe2O3/K2O, 600C)"
        },
    ],
    "ethylbenzene": [
        {
            "precursors": ["benzene", "ethylene"],
            "bond_type": "sigma_single",
            "fg1": "alkane", "fg2": "aromatic_ring",
            "delta": 0.7,
            "description": "Friedel-Crafts alkylation (C2H5Cl/AlCl3)"
        },
    ],
    # ── Ibuprofen pathway ────────────────────────────────────────
    "ibuprofen": [
        {
            "precursors": ["isobutylbenzene"],
            "bond_type": "carbonyl",
            "fg1": "carboxylic_acid", "fg2": "aromatic_ring",
            "delta": 1.4,
            "description": "Carbonylation of isobutylbenzene (CO, Pd-cat)"
        },
    ],
    "isobutylbenzene": [
        {
            "precursors": ["benzene", "isobutyl_chloride"],
            "bond_type": "sigma_single",
            "fg1": "alkane", "fg2": "aromatic_ring",
            "delta": 0.7,
            "description": "Friedel-Crafts alkylation of benzene"
        },
    ],
    # ── Morphine pathway (key intermediates) ─────────────────────
    "morphine": [
        {
            "precursors": ["codeine"],
            "bond_type": "co_sigma",
            "fg1": "phenol", "fg2": "ether",
            "delta": 2.5,
            "description": "Demethylation of codeine to morphine (BBr3 or hepatic)"
        },
    ],
    "codeine": [
        {
            "precursors": ["thebaine"],
            "bond_type": "sigma_single",
            "fg1": "ether", "fg2": "alkene",
            "delta": 2.8,
            "description": "Reduction of thebaine (H2/Pd, 2 steps)"
        },
    ],
    # ── Nicotine pathway ────────────────────────────────────────────
    "nicotine": [
        {
            "precursors": ["nicotinic_acid", "n_methyl_pyrrolinium"],
            "bond_type": "sigma_single",
            "fg1": "amine", "fg2": "aromatic_ring",
            "delta": 2.0,
            "description": "Coupling of nicotinic acid derivative with N-methylpyrrolinium"
        },
    ],
    "nicotinic_acid": [
        {
            "precursors": ["quinoline"],
            "bond_type": "carbonyl",
            "fg1": "carboxylic_acid", "fg2": "aromatic_ring",
            "delta": 1.5,
            "description": "Oxidative degradation of quinoline"
        },
    ],
    # ── Caffeine pathway ────────────────────────────────────────────
    "caffeine": [
        {
            "precursors": ["xanthine", "methyl_iodide"],
            "bond_type": "sigma_single",
            "fg1": "lactam", "fg2": "imidazole",
            "delta": 1.0,
            "description": "Methylation of xanthine (CH3I/NaOH)"
        },
    ],
    "xanthine": [
        {
            "precursors": ["hypoxanthine"],
            "bond_type": "carbonyl",
            "fg1": "lactam", "fg2": "imidazole",
            "delta": 0.8,
            "description": "Oxidation of hypoxanthine (xanthine oxidase)"
        },
    ],
    # ── THC pathway (key biosynthetic steps) ──────────────────────
    "thc": [
        {
            "precursors": ["cannabigerol"],
            "bond_type": "sigma_single",
            "fg1": "cyclic", "fg2": "phenol",
            "delta": 2.2,
            "description": "Enzymatic cyclization of cannabigerol (THCA synthase)"
        },
    ],
    # ── Dopamine pathway (endogenous) ─────────────────────────────
    "dopamine": [
        {
            "precursors": ["l_dopa"],
            "bond_type": "co_sigma",
            "fg1": "amine", "fg2": "carboxylic_acid",
            "delta": 1.6,
            "description": "Decarboxylation of L-DOPA (DOPA decarboxylase)"
        },
    ],
    "l_dopa": [
        {
            "precursors": ["l_tyrosine"],
            "bond_type": "co_sigma",
            "fg1": "phenol", "fg2": "aromatic_ring",
            "delta": 1.2,
            "description": "Hydroxylation of tyrosine (tyrosine hydroxylase)"
        },
    ],
    # ── Benzene → directly to common aromatics ────────────────────
    "acetophenone": [
        {
            "precursors": ["benzene", "acetyl_chloride"],
            "bond_type": "carbonyl",
            "fg1": "ketone", "fg2": "aromatic_ring",
            "delta": 0.8,
            "description": "Friedel-Crafts acylation (AcCl/AlCl3)"
        },
    ],
    "benzonitrile": [
        {
            "precursors": ["benzene"],
            "bond_type": "sigma_single",
            "fg1": "nitrile", "fg2": "aromatic_ring",
            "delta": 1.5,
            "description": "Sandmeyer-type cyanation of benzene diazonium"
        },
    ],
    "anisole": [
        {
            "precursors": ["phenol", "methyl_iodide"],
            "bond_type": "co_sigma",
            "fg1": "ether", "fg2": "aromatic_ring",
            "delta": 0.6,
            "description": "Methylation of phenol (CH3I/K2CO3)"
        },
    ],
    # ── Taxol → simplified intermediates (key disconnections) ────
    "taxol": [
        {
            "precursors": ["baccatin_iii", "phenylisoserine_side_chain"],
            "bond_type": "ester_link",
            "fg1": "ester", "fg2": "alcohol",
            "delta": 2.5,
            "description": "Esterification of baccatin III with side chain (Holton coupling)"
        },
    ],
    # ── Taxol side chain pathway (benzaldehyde → phenylisoserine) ──
    "phenylisoserine_side_chain": [
        {
            "precursors": ["n_benzoyl_phenylisoserine"],
            "bond_type": "ester_link",
            "fg1": "amine", "fg2": "ester",
            "delta": 1.5,
            "description": "Deprotection revealing free amine and alcohol on side chain"
        },
    ],
    "n_benzoyl_phenylisoserine": [
        {
            "precursors": ["benzaldehyde", "chiral_oxazolidinone"],
            "bond_type": "sigma_single",
            "fg1": "aldehyde", "fg2": "amine",
            "delta": 2.8,
            "description": "Asymmetric aldol: benzaldehyde + chiral acetate (Holton/Ojima side chain)"
        },
    ],
    # ── Baccatin III pathway (diterpene core biosynthesis and semi-synthesis) ──
    "baccatin_iii": [
        {
            "precursors": ["10_deacetylbaccatin_iii", "acetic_anhydride"],
            "bond_type": "ester_link",
            "fg1": "ester", "fg2": "alcohol",
            "delta": 1.2,
            "description": "Acetylation of 10-deacetylbaccatin III at C10 (semi-synthesis)"
        },
    ],
    "10_deacetylbaccatin_iii": [
        {
            "precursors": ["taxadiene"],
            "bond_type": "co_sigma",
            "fg1": "alkene", "fg2": "alcohol",
            "delta": 3.5,
            "description": "Oxidative functionalization of taxadiene: oxetane ring formation + P450 hydroxylation cascade"
        },
    ],
    "taxadiene": [
        {
            "precursors": ["geranylgeranyl_pyrophosphate"],
            "bond_type": "double_bond",
            "fg1": "alkene", "fg2": "alkene",
            "delta": 2.0,
            "description": "Taxadiene synthase cyclization of GGPP (class I terpene cyclase)"
        },
    ],
    "geranylgeranyl_pyrophosphate": [
        {
            "precursors": ["isopentenyl_pyrophosphate", "dimethylallyl_pyrophosphate"],
            "bond_type": "sigma_single",
            "fg1": "alkene", "fg2": "phosphate",
            "delta": 1.5,
            "description": "Prenyltransferase condensation: C15 + C5 → C20 isoprenoid chain"
        },
    ],
    # ── Penicillin G → intermediates ─────────────────────────────── → intermediates ───────────────────────────────
    "penicillin_g": [
        {
            "precursors": ["6_aminopenicillanic_acid", "phenylacetyl_chloride"],
            "bond_type": "amide_link",
            "fg1": "amide", "fg2": "beta_lactam",
            "delta": 1.0,
            "description": "Acylation of 6-APA with phenylacetyl chloride"
        },
    ],
}

# ====================================================================
# LATTICE WALKER — Retrosynthetic tree builder using the lattice
# ====================================================================

def build_retro_tree(target_name, depth=3, visited=None):
    """Build a retrosynthetic tree by walking the PRECURSOR_LATTICE.
    Returns dict with same structure as Ch3mpiler.retrosynthesis() output.
    Falls back to grammar-only FG cuts when no lattice entry exists.
    """
    if visited is None:
        visited = set()
    if target_name in visited:
        return {"target": target_name, "cuts": [], "terminal": True, "loop": True}
    visited.add(target_name)

    from compiler import Ch3mpiler, FG, BOND_TYPES, PNAMES
    from compiler import find_fgs, compose_molecule_type, fmt_tup, find_disconnections, get_molecule_type

    ch = Ch3mpiler()
    mol_type, tsrc = get_molecule_type(target_name, ch.catalog)
    fgs = find_fgs(target_name)
    type_str = fmt_tup(mol_type) if mol_type else "?"
    
    # Check for lattice entry
    norm_name = target_name.lower().replace("-","_").replace(" ","_").replace("'","").strip()
    lattice_entry = PRECURSOR_LATTICE.get(norm_name, [])
    
    cuts = []
    fg_cuts = []
    
    # Step 1: Use lattice entries (prioritized — they're real chemical steps)
    for entry in lattice_entry:
        fg1_t = FG.get(entry["fg1"], {})
        fg2_t = FG.get(entry["fg2"], {})
        bond_t = BOND_TYPES.get(entry["bond_type"], {})
        if fg1_t and fg2_t and bond_t:
            from compiler import bond_product_type, tup_dist
            product = bond_product_type(fg1_t, fg2_t, bond_t)
            pd, _ = tup_dist(product, mol_type) if mol_type else (0, [])
            bond_desc = bond_t.get("desc", entry["bond_type"])
        else:
            pd = entry.get("delta", 1.0)
            bond_desc = entry["bond_type"]
        
        cuts.append({
            "bond": entry["bond_type"],
            "bond_desc": bond_desc,
            "delta": round(entry.get("delta", pd), 3),
            "product_delta": round(pd, 3),
            "fg1": entry["fg1"],
            "fg2": entry["fg2"],
            "product_type": fmt_tup(product) if 'product' in dir() else "?",
            "lattice": True,
            "description": entry.get("description", ""),
            "precursors": entry["precursors"],
        })
    
    # Step 2: Also compute grammar-only FG cuts for fallback
    if fgs and mol_type:
        fg_cuts = find_disconnections(fgs, mol_type, max_results=5)
    
    # Merge: lattice cuts first, then unique FG cuts not already covered
    seen_bonds = set((c["fg1"], c["fg2"], c["bond"]) for c in cuts)
    for fc in fg_cuts:
        key = (fc["fg1"], fc["fg2"], fc["bond"])
        if key not in seen_bonds:
            fc["lattice"] = False
            fc["description"] = ""
            fc["precursors"] = []
            cuts.append(fc)
            seen_bonds.add(key)
    
    cuts.sort(key=lambda x: (0 if x.get("lattice") else 1, x.get("product_delta", x["delta"]), x["delta"]))
    
    # Build tree
    steps = []
    for cut in cuts[:5]:
        step_precursors = []
        if cut.get("lattice") and cut.get("precursors"):
            for pname in cut["precursors"][:2]:
                sub_tree = build_retro_tree(pname, depth - 1, visited.copy()) if depth > 0 else {"target": pname, "terminal": True}
                step_precursors.append({
                    "name": pname,
                    "fg_hint": cut["fg1"] if pname == cut["precursors"][0] else cut["fg2"],
                    "further": sub_tree.get("cuts", [])[:2],
                    "type": sub_tree.get("type", "?"),
                })
        else:
            # Grammar-only: use synthetic precursor names
            sname1 = f"{cut['fg1']}_precursor"
            sname2 = f"{cut['fg2']}_precursor"
            step_precursors = [
                {"name": sname1, "fg_hint": cut["fg1"], "further": [], "type": "?"},
                {"name": sname2, "fg_hint": cut["fg2"], "further": [], "type": "?"},
            ]
        
        steps.append({
            "bond": cut["bond"],
            "bond_desc": cut.get("bond_desc", cut["bond"]),
            "delta": cut["delta"],
            "bond_delta": cut.get("product_delta", cut["delta"]),
            "product_delta": cut.get("product_delta", cut["delta"]),
            "fg1": cut["fg1"],
            "fg2": cut["fg2"],
            "product_type": cut.get("product_type", "?"),
            "lattice": cut.get("lattice", False),
            "description": cut.get("description", ""),
            "precursors": step_precursors,
        })
    
    return {
        "target": target_name,
        "type": type_str,
        "fgs": fgs,
        "cuts": cuts[:10],
        "steps": steps,
        "terminal": len(steps) == 0,
        "lattice_sourced": len(lattice_entry) > 0,
    }


def pathfind_lattice(starting_material, target, max_depth=6):
    """BFS/DFS through PRECURSOR_LATTICE to find a multi-step path.
    Returns list of steps from starting_material to target.
    """
    from collections import deque
    
    # Normalize names
    start_n = starting_material.lower().replace("-","_").replace(" ","_").replace("'","").strip()
    target_n = target.lower().replace("-","_").replace(" ","_").replace("'","").strip()
    
    # BFS: each queue entry is (current_target, path_to_get_here, depth)
    # We go backwards from target to starting_material (retrosynthetic direction)
    q = deque()
    q.append((target_n, [], 0))
    visited = {target_n}
    
    while q:
        current, path, depth = q.popleft()
        
        # Check if we've reached the starting material
        if current == start_n:
            # Found! Path is in retrosynthetic order (target -> start)
            # Reverse to get forward order (start -> target)
            fwd_path = list(reversed(path))
            return {"found": True, "path": fwd_path, "length": len(fwd_path)}
        
        if depth >= max_depth:
            continue
        
        # Look up precursors of current node
        predecessors = PRECURSOR_LATTICE.get(current, [])
        for pred_entry in predecessors:
            for pname in pred_entry["precursors"]:
                pn = pname.lower().replace("-","_").replace(" ","_").replace("'","").strip()
                if pn not in visited:
                    visited.add(pn)
                    step = {
                        "precursor": pname,
                        "target": current,
                        "bond": pred_entry["bond_type"],
                        "fg1": pred_entry["fg1"],
                        "fg2": pred_entry["fg2"],
                        "description": pred_entry.get("description", ""),
                    }
                    q.append((pn, path + [step], depth + 1))
    
    # No path found through lattice alone — report closest reachable nodes
    return {"found": False, "nodes_reachable": list(visited), "target": target_n, "max_depth_searched": max_depth}


def install_fg_extensions():
    """Install enriched FG tuples into compiler.FG (if it exists).
    Called at import time to patch missing FGs into the compiler.
    """
    try:
        from compiler import FG
        for fg_name, fg_tuple in ENRICHED_FG.items():
            if fg_name not in FG:
                FG[fg_name] = fg_tuple
        return len(ENRICHED_FG)
    except ImportError:
        return 0


def install_molecule_fg_extensions():
    """Install lattice intermediate compounds into MOLECULE_FG_DB."""
    try:
        from compiler import MOLECULE_FG_DB
        # Map intermediate names to their FG compositions
        # These are the intermediates that appear in the lattice but may not
        # be in MOLECULE_FG_DB
        extensions = {
            "4_aminophenol": ["amine", "phenol"],
            "4_nitrophenol": ["nitro", "phenol"],
            "acetic_anhydride": ["carbonyl", "ester"],
            "isobutylbenzene": ["alkane", "aromatic_ring"],
            "isobutyl_chloride": ["halide", "alkane"],
            "nitric_acid": ["nitro", "alcohol"],
            "l_dopa": ["amine", "carboxylic_acid", "phenol", "aromatic_ring"],
            "l_tyrosine": ["amine", "carboxylic_acid", "phenol", "aromatic_ring"],
            "cannabigerol": ["phenol", "alkene", "alcohol"],
            "baccatin_iii": ["ester", "alcohol", "ketone", "epoxide", "cyclic"],
            "phenylisoserine_side_chain": ["amine", "alcohol", "aromatic_ring"],
            "6_aminopenicillanic_acid": ["beta_lactam", "amine", "carboxylic_acid"],
            "phenylacetyl_chloride": ["carbonyl", "aromatic_ring", "halide"],
            "nicotinic_acid": ["carboxylic_acid", "aromatic_ring"],
            "n_methyl_pyrrolinium": ["amine", "alkene"],
            "hypoxanthine": ["imidazole", "lactam"],
            "thebaine": ["ether", "alkene", "aromatic_ring"],
            "codeine": ["amine", "alcohol", "ether", "aromatic_ring"],
            "n_benzoyl_phenylisoserine": ["amine", "alcohol", "aromatic_ring", "ester"],
            "chiral_oxazolidinone": ["aldehyde", "amine", "carbonyl"],
            "10_deacetylbaccatin_iii": ["ester", "alcohol", "ketone", "cyclic"],
            "taxadiene": ["alkene", "cyclic"],
            "geranylgeranyl_pyrophosphate": ["alkene", "phosphate", "ester"],
            "isopentenyl_pyrophosphate": ["alkene", "phosphate"],
            "dimethylallyl_pyrophosphate": ["alkene", "phosphate"],
        }
        added = 0
        for name, fgs in extensions.items():
            if name not in MOLECULE_FG_DB:
                MOLECULE_FG_DB[name] = fgs
                added += 1
        return added
    except ImportError:
        return 0


# moved to patch_ch3mpiler()

# ====================================================================
# MONKEY-PATCH INTEGRATION — Replaces Ch3mpiler methods
# ====================================================================

def patch_ch3mpiler(Ch3mpiler_cls=None):
    """Monkey-patch Ch3mpiler.retrosynthesis() and path_to_target()
    to use the enriched PRECURSOR_LATTICE."""
    # Use provided class or import from compiler module
    if Ch3mpiler_cls is None:
        from compiler import Ch3mpiler, PNAMES, FG, BOND_TYPES, fmt_tup
        from compiler import find_fgs, get_molecule_type, find_disconnections
        from compiler import g2v, glyph_ord, WEIGHTS, math, tup_dist
    else:
        Ch3mpiler = Ch3mpiler_cls
        from compiler import PNAMES, FG, BOND_TYPES, fmt_tup
        from compiler import find_fgs, get_molecule_type, find_disconnections
        from compiler import g2v, glyph_ord, WEIGHTS, math, tup_dist
    # Install FG extensions and molecule DB extensions
    install_fg_extensions()
    install_molecule_fg_extensions()

    # ── Patched retrosynthesis ────────────────────────────────────
    def _retrosynthesis_patched(self, target, depth=2):
        """Enriched retrosynthesis using PRECURSOR_LATTICE + FG grammar."""
        tree = build_retro_tree(target, depth=depth)
        # Ensure fallback base fields
        base = self.analyze(target)
        tree.setdefault("analogs", base.get("analogs", []))
        tree.setdefault("cuts", [])
        if not tree.get("steps"):
            tree["steps"] = []
        return tree

    # ── Patched path_to_target ────────────────────────────────────
    def _path_to_target_patched(self, starting_material, target, depth=4):
        """Enriched pathfinding: lattice BFS first, grammar-only fallback."""
        # First try the lattice
        lattice_result = pathfind_lattice(starting_material, target, max_depth=depth)
        
        if lattice_result.get("found"):
            # Build structured result
            fwd_path = lattice_result["path"]
            path_steps = []
            for i, step in enumerate(fwd_path):
                path_steps.append({
                    "step": i + 1,
                    "operation": "Coagula (mu)",
                    "bond": step["bond"],
                    "reaction": step.get("description", step["bond"]),
                    "delta": 0.5,
                    "fg1": step["fg1"],
                    "fg2": step["fg2"],
                    "product": step["target"],
                })
            
            # Get structural info
            target_analysis = self.analyze(target)
            start_analysis = self.analyze(starting_material)
            
            def _analysis_to_ords(analysis):
                ords = {}
                t = analysis.get("type", "")
                if t.startswith("<") and t.endswith(">"):
                    vals = [v.strip() for v in t[1:-1].split(";")]
                    for i, p in enumerate(PNAMES):
                        if i < len(vals):
                            _, o = g2v(p, vals[i])
                            ords[p] = o
                return ords
            
            tgt_ords = _analysis_to_ords(target_analysis)
            src_ords = _analysis_to_ords(start_analysis)
            direct_dist = 0.0
            direct_conflicts = []
            if tgt_ords and src_ords:
                sq = 0.0
                for p in PNAMES:
                    o1 = tgt_ords.get(p, 0)
                    o2 = src_ords.get(p, 0)
                    w = WEIGHTS.get(p, 1.0)
                    d = (o1 - o2) * w
                    sq += d * d
                    if o1 != o2:
                        direct_conflicts.append({"p": p, "tgt": o1, "src": o2})
                direct_dist = math.sqrt(sq)
            
            return {
                "target": target,
                "starting_material": starting_material,
                "direct_structural_distance": round(direct_dist, 4),
                "direct_conflicts": direct_conflicts[:6],
                "start_is_simple": True,
                "retro_depth_searched": depth,
                "total_nodes_searched": len(fwd_path),
                "found": True,
                "path": path_steps,
                "path_length": len(path_steps),
                "match_type": "lattice_path",
                "terminal_node_name": starting_material,
                "source": "precursor_lattice",
            }
        
        # Fallback: use original grammar-only method
        return self._original_path_to_target(starting_material, target, depth)

    # Attach patches — preserve originals for fallback
    if not hasattr(Ch3mpiler, '_original_retrosynthesis'):
        Ch3mpiler._original_retrosynthesis = Ch3mpiler.retrosynthesis
    if not hasattr(Ch3mpiler, '_original_path_to_target'):
        Ch3mpiler._original_path_to_target = Ch3mpiler.path_to_target
    
    Ch3mpiler.retrosynthesis = _retrosynthesis_patched
    Ch3mpiler.path_to_target = _path_to_target_patched
    
    return True

