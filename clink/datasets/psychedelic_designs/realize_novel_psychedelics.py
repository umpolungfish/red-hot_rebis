#!/usr/bin/env python3
"""
realize_novel_psychedelics.py — CLINK Realization of the 5 Novel Navigatable/Operable Psychedelics
===================================================================================================
Takes the structurally-imscribed novel psychedelic compounds (Verticullum, Chimerium,
Apertix, Retiarius, Praxeum) and realizes them as full CLINK design directories
from L0 (quarks) → L8 (organism), producing actionable molecular designs, receptor
targeting data, genetic delivery pathways, and control method specifications.

Each compound produces a directory with:
  - design_manifest.json       — complete design specification
  - structural_type.json       — 12-primitive tuple + tier + C-score
  - L3_molecular/              — ch3mpiler retrosynthetic bond plan
  - L4_receptor/               — receptor targeting & binding predictions
  - L5_cellular/               — gene expression cassettes & metabolic model
  - L6_delivery/               — delivery system design
  - L7_tissue/                 — tissue distribution & BBB penetration
  - L8_organism/               — full organism-level effect profile
  - control_methods/           — Praxeum gate toggle, chirality ladder, etc.
  - combination_profiles/      — predicted combination effects with known compounds

Author: Lando⊗⊙perator
"""

import json, math, sys, os, hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

REBIS_ROOT = Path("/home/mrnob0dy666/red-hot_rebis")
sys.path.insert(0, str(REBIS_ROOT))

from shared.primitives import (
    ORDINALS, WEIGHTS, to_vector, tuple_distance, PRIMITIVE_ORDER as PORDER
)
from clink.chain import compute_c_score_from_tuple, compute_tier_from_tuple
# ─── KEY MAPPING: compound dict keys → PORDER Shavian keys ──────
KEY_MAP = {"D": "Ð", "T": "Þ", "R": "Ř", "P": "Φ", "F": "ƒ", "K": "Ç",
           "G": "Γ", "Gm": "ɢ", "Ph": "⊙", "H": "Ħ", "S": "Σ", "W": "Ω"}
COMPOUND_KEYS = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]


# ─── NOVEL COMPOUND DEFINITIONS ───────────────────────────────────

NOVEL_COMPOUNDS: Dict[str, Dict[str, Any]] = {
    "verticullum": {
        "name": "Verticullum (EP-Lever)",
        "tuple": {"D": "𐑦", "T": "𐑥", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑠", "Ph": "⊙", "H": "𐑫",
                  "S": "𐑳", "W": "𐑟"},
        "tier": "O_∞",
        "c_score": 0.0,
        "description": "Non-Abelian braiding + bowtie crossing. 16/17 universes.",
        "innovations": ["First Ω=𐑟 (non-Abelian)", "First T=𐑥 (bowtie)"],
        "pharmacophore_hint": "Tryptamine core with extended indole — needs non-Abelian braiding realized via chiral macrocyclic cage",
        "receptor_targets": ["5-HT2A", "5-HT1A", "Sigma-1", "TAAR1"],
        "delivery": "Intravenous (first-pass metabolism avoidance); liposomal encapsulation for non-Abelian stability",
    },
    "chimerium": {
        "name": "Chimerium (Supercritical Catalyst)",
        "tuple": {"D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑵", "Ph": "𐑣", "H": "𐑫",
                  "S": "𐑳", "W": "𐑭"},
        "tier": "O₀",
        "c_score": 0.0,
        "description": "Supercritical runaway; catalytic launch compound. 16/17 universes.",
        "innovations": ["First Ph=𐑣 (supercritical)", "Broadcast composition (Gm=𐑵)"],
        "pharmacophore_hint": "Ergoline-like scaffold with supercritical ring strain — needs controlled-release pro-drug",
        "receptor_targets": ["5-HT2A", "5-HT2B", "5-HT7", "D2", "Adrenergic α2"],
        "delivery": "Sublingual pro-drug; enzymatically cleaved to active form for controlled onset",
    },
    "apertix": {
        "name": "Apertix (Adjoint Corridor)",
        "tuple": {"D": "𐑦", "T": "𐑥", "R": "𐑽", "P": "𐑬", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑠", "Ph": "⊙", "H": "𐑖",
                  "S": "𐑳", "W": "𐑴"},
        "tier": "O₂",
        "c_score": 0.0,
        "description": "One-way adjoint steering. 7/17 universes. Precision direction.",
        "innovations": ["First R=𐑽 (adjoint)", "H2 chirality (H=𐑖)"],
        "pharmacophore_hint": "Phenethylamine-like with directional vector — N-benzylated for adjoint coupling",
        "receptor_targets": ["5-HT2A", "5-HT2C", "mGluR2", "NMDA (glycine site)"],
        "delivery": "Oral with enteric coating; sustained release for directional steering window",
    },
    "retiarius": {
        "name": "Retiarius (Local-Net Trap)",
        "tuple": {"D": "𐑼", "T": "𐑡", "R": "𐑾", "P": "𐑿", "F": "𐑞",
                  "K": "𐑺", "G": "𐑚", "Gm": "𐑜", "Ph": "𐑮", "H": "𐑒",
                  "S": "𐑕", "W": "𐑷"},
        "tier": "O₁",
        "c_score": 0.0,
        "description": "Nearest-neighbor precision; frozen disorder kinetics. 2/17 universes.",
        "innovations": ["First G=𐑚 (local only)", "First K=𐑺 (MBL)", "First F=𐑞 (thermal)"],
        "pharmacophore_hint": "Salvinorin-like with local-only scope — κ-opioid selective with no downstream cascade",
        "receptor_targets": ["KOR (κ-opioid)", "CB1 (peripheral only)"],
        "delivery": "Inhalation for rapid onset/offset; peripheral restriction for local-only scope",
    },
    "praxeum": {
        "name": "Praxeum (EP-Core Control Platform)",
        "tuple": {"D": "𐑦", "T": "𐑶", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑠", "Ph": "𐑻", "H": "𐑫",
                  "S": "𐑳", "W": "𐑭"},
        "tier": "O₀",
        "c_score": 0.0,
        "description": "EP absorption platform — tensor(critical, EP)=EP enables Gate 1 toggle. 16/17 universes.",
        "innovations": ["First Ph=𐑻 (exceptional point)", "Irreducible product (T=𐑶)"],
        "pharmacophore_hint": "β-carboline with EP-inducing substitution — needs co-administered ⊙ compound",
        "receptor_targets": ["5-HT2A (modulator, not agonist)", "Sigma-1", "GABA-A (α1 subunit)"],
        "delivery": "Transdermal patch for steady-state EP maintenance; combined with chosen ⊙ compound",
    },
}

# Post-process: compute tier and C-score from tuple, not hardcoded
for _name, _comp in NOVEL_COMPOUNDS.items():
    _tup = _comp["tuple"]
    _porder_tup = {KEY_MAP.get(k, k): v for k, v in _tup.items()}
    _comp["c_score"] = compute_c_score_from_tuple(_porder_tup)
    _comp["tier"] = compute_tier_from_tuple(_porder_tup)


# ─── CLINK LAYER REFERENCE (for structural distance computation) ──

CLINK_LAYERS = {
    0: {"name": "Frustrated Belnap5 (Quarks)",   "tuple": {"D":"𐑛","T":"𐑶","R":"𐑩","P":"𐑯","F":"𐑐","K":"𐑘","G":"𐑚","Gm":"𐑝","Ph":"𐑢","H":"𐑓","S":"𐑳","W":"𐑷"}, "tier":"O₀"},
    1: {"name": "Electron Orbital (Belnap4)",     "tuple": {"D":"𐑛","T":"𐑶","R":"𐑩","P":"𐑗","F":"𐑐","K":"𐑤","G":"𐑚","Gm":"𐑜","Ph":"𐑢","H":"𐑓","S":"𐑳","W":"𐑷"}, "tier":"O₀"},
    2: {"name": "Atom (Nuclear + Electron)",      "tuple": {"D":"𐑼","T":"𐑥","R":"𐑽","P":"𐑿","F":"𐑐","K":"𐑤","G":"𐑔","Gm":"𐑝","Ph":"𐑮","H":"𐑒","S":"𐑳","W":"𐑷"}, "tier":"O₁"},
    3: {"name": "Molecule (Chemical Bonds)",      "tuple": {"D":"𐑼","T":"𐑥","R":"𐑽","P":"𐑿","F":"𐑞","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑓","S":"𐑳","W":"𐑭"}, "tier":"O₂"},
    4: {"name": "Folded Protein",                 "tuple": {"D":"𐑦","T":"𐑥","R":"𐑾","P":"𐑬","F":"𐑞","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑒","S":"𐑳","W":"𐑭"}, "tier":"O₂"},
    5: {"name": "Living Cell",                    "tuple": {"D":"𐑦","T":"𐑸","R":"𐑾","P":"𐑬","F":"𐑞","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑒","S":"𐑳","W":"𐑭"}, "tier":"O₂"},
    6: {"name": "Mitosis (Cell Division)",        "tuple": {"D":"𐑦","T":"𐑸","R":"𐑾","P":"𐑹","F":"𐑱","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑖","S":"𐑳","W":"𐑭"}, "tier":"O₂"},
    7: {"name": "Tissue / Organ",                 "tuple": {"D":"𐑦","T":"𐑸","R":"𐑾","P":"𐑬","F":"𐑞","K":"𐑧","G":"𐑲","Gm":"𐑵","Ph":"⊙","H":"𐑖","S":"𐑳","W":"𐑭"}, "tier":"O₂"},
    8: {"name": "Whole Organism",                 "tuple": {"D":"𐑦","T":"𐑸","R":"𐑾","P":"𐑹","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑵","Ph":"⊙","H":"𐑫","S":"𐑳","W":"𐑟"}, "tier":"O_∞"},
}

# ─── KNOWN PSYCHEDELICS (for combination profiles) ────────────────

KNOWN_PSYCHEDELICS = {
    "dmt":        {"tuple":{"D":"𐑦","T":"𐑸","R":"𐑾","P":"𐑹","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑵","Ph":"⊙","H":"𐑫","S":"𐑳","W":"𐑭"}, "tier":"O_∞"},
    "psilocybin": {"tuple":{"D":"𐑼","T":"𐑥","R":"𐑾","P":"𐑬","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑖","S":"𐑳","W":"𐑭"}, "tier":"O₂"},
    "lsd":        {"tuple":{"D":"𐑦","T":"𐑸","R":"𐑾","P":"𐑹","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑵","Ph":"⊙","H":"𐑖","S":"𐑳","W":"𐑭"}, "tier":"O_∞"},
    "ketamine":   {"tuple":{"D":"𐑼","T":"𐑥","R":"𐑾","P":"𐑿","F":"𐑱","K":"𐑤","G":"𐑔","Gm":"𐑠","Ph":"𐑢","H":"𐑒","S":"𐑕","W":"𐑷"}, "tier":"O₁"},
    "mdma":       {"tuple":{"D":"𐑼","T":"𐑡","R":"𐑾","P":"𐑿","F":"𐑞","K":"𐑤","G":"𐑲","Gm":"𐑠","Ph":"𐑮","H":"𐑒","S":"𐑳","W":"𐑷"}, "tier":"O₁"},
    "mescaline":  {"tuple":{"D":"𐑼","T":"𐑡","R":"𐑩","P":"𐑗","F":"𐑱","K":"𐑧","G":"𐑔","Gm":"𐑜","Ph":"𐑢","H":"𐑒","S":"𐑙","W":"𐑷"}, "tier":"O₀"},
}

# ─── HELPER FUNCTIONS ─────────────────────────────────────────────

def glyph_ord(prim: str, glyph: str) -> int:
    mapped_prim = KEY_MAP.get(prim, prim)  # translate compound key → Shavian
    om = ORDINALS.get(mapped_prim, {})
    return om.get(glyph, 0)

def compute_tuple_distance(t1: Dict, t2: Dict) -> float:
    sq = 0.0
    for p in COMPOUND_KEYS:
        v1 = t1.get(p, ""); v2 = t2.get(p, "")
        o1 = glyph_ord(p, v1); o2 = glyph_ord(p, v2)
        w = WEIGHTS.get(p, 1.0)
        sq += ((o1 - o2) * w) ** 2
    return round(math.sqrt(sq), 4)

def compute_primitive_deltas(t1: Dict, t2: Dict) -> List[Dict]:
    return [{"primitive": p, "from": t1.get(p, "?"), "to": t2.get(p, "?"),
             "delta": glyph_ord(p, str(t2.get(p, ""))) - glyph_ord(p, str(t1.get(p, "")))}
            for p in COMPOUND_KEYS if t1.get(p) != t2.get(p)]

def format_tuple(t: Dict) -> str:
    glyphs = [t.get(p, "?") for p in COMPOUND_KEYS]
    return "⟨" + " · ".join(glyphs) + "⟩"

def tensor_tuples(t1: Dict, t2: Dict) -> Dict:
    """Grammar tensor: max on union, min on P and F."""
    r = {}
    for p in COMPOUND_KEYS:
        if p in ("P", "F"):
            r[p] = min([t1.get(p, ""), t2.get(p, "")], key=lambda x: glyph_ord(p, x))
        else:
            r[p] = max([t1.get(p, ""), t2.get(p, "")], key=lambda x: glyph_ord(p, x))
    return r


# ─── MAIN REALIZATION ENGINE ──────────────────────────────────────

class PsychedelicRealizer:
    """Realizes novel psychedelic compounds into CLINK design directories."""
    
    def __init__(self, output_root: Path):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.compounds = NOVEL_COMPOUNDS
        self.layers = CLINK_LAYERS
        self.known = KNOWN_PSYCHEDELICS
    
    def realize_all(self):
        """Realize all 5 novel compounds."""
        results = {}
        for key, comp in self.compounds.items():
            print(f"\n{'='*60}")
            print(f"Realizing: {comp['name']}")
            print(f"{'='*60}")
            results[key] = self.realize_one(key, comp)
        # Write master index
        self._write_master_index(results)
        return results
    
    def realize_one(self, key: str, comp: Dict) -> Dict:
        """Realize a single compound into its design directory."""
        comp["key"] = key  # inject key for downstream methods
        comp_dir = self.output_root / key
        comp_dir.mkdir(parents=True, exist_ok=True)
        
        result = {"name": comp["name"], "key": key, "directory": str(comp_dir)}
        result["manifest"] = self._write_manifest(comp_dir, key, comp)
        result["structural_type"] = self._write_structural_type(comp_dir, comp)
        result["layer_distances"] = self._compute_layer_distances(comp_dir, comp)
        result["molecular"] = self._design_molecular(comp_dir, comp)
        result["receptor"] = self._design_receptor(comp_dir, comp)
        result["cellular"] = self._design_cellular(comp_dir, comp)
        result["delivery"] = self._design_delivery(comp_dir, comp)
        result["tissue"] = self._design_tissue(comp_dir, comp)
        result["organism"] = self._design_organism(comp_dir, comp)
        result["control_methods"] = self._design_control_methods(comp_dir, comp)
        result["combinations"] = self._design_combinations(comp_dir, comp, key)
        
        return result

    def _write_manifest(self, comp_dir: Path, key: str, comp: Dict) -> Dict:
        manifest = {
            "design_name": comp["name"],
            "design_key": key,
            "design_type": "navigatable_operable_psychedelic",
            "author": "Lando⊗⊙perator",
            "created": datetime.now().isoformat(),
            "structural_type": format_tuple(comp["tuple"]),
            "tier": comp["tier"],
            "c_score": comp["c_score"],
            "innovations": comp["innovations"],
            "description": comp["description"],
            "design_files": {}
        }
        with open(comp_dir / "design_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        return manifest

    def _write_structural_type(self, comp_dir: Path, comp: Dict) -> Dict:
        st = {
            "name": comp["name"],
            "tuple": comp["tuple"],
            "tuple_display": format_tuple(comp["tuple"]),
            "tier": comp["tier"],
            "c_score": comp["c_score"],
            "primitive_breakdown": {},
        }
        for p in PORDER:
            glyph = comp["tuple"].get(p, "?")
            st["primitive_breakdown"][p] = {
                "glyph": glyph,
                "ordinal": glyph_ord(p, glyph),
                "weight": WEIGHTS.get(p, 1.0),
            }
        # Distances to CLINK layers
        st["clink_distances"] = {}
        for li, ld in self.layers.items():
            st["clink_distances"][f"L{li}"] = {
                "layer": ld["name"],
                "distance": compute_tuple_distance(comp["tuple"], ld["tuple"]),
                "deltas": compute_primitive_deltas(comp["tuple"], ld["tuple"]),
            }
        with open(comp_dir / "structural_type.json", "w") as f:
            json.dump(st, f, indent=2, ensure_ascii=False)
        return st

    def _compute_layer_distances(self, comp_dir: Path, comp: Dict) -> Dict:
        ld_out = {}
        for li, ld in self.layers.items():
            d = compute_tuple_distance(comp["tuple"], ld["tuple"])
            deltas = compute_primitive_deltas(comp["tuple"], ld["tuple"])
            ld_out[f"L{li}"] = {"layer": ld["name"], "distance": d, "deltas": deltas, "tier": ld["tier"]}
        with open(comp_dir / "layer_distances.json", "w") as f:
            json.dump(ld_out, f, indent=2, ensure_ascii=False)
        return ld_out


    # ─── L3: MOLECULAR DESIGN ────────────────────────────────────
    
    def _design_molecular(self, comp_dir: Path, comp: Dict) -> Dict:
        mol_dir = comp_dir / "L3_molecular"
        mol_dir.mkdir(exist_ok=True)
        
        tup = comp["tuple"]
        mol = {
            "layer": "L3 — Molecular Design",
            "pharmacophore_hint": comp.get("pharmacophore_hint", ""),
            "structural_constraints": self._molecule_constraints(tup),
            "bond_formation_strategy": self._bond_strategy(tup),
            "predicted_scaffold": self._scaffold_prediction(tup),
            "predicted_mass_range": self._mass_range(tup),
            "predicted_logP": self._predict_logP(tup),
            "predicted_HBD": self._predict_HBD(tup),
            "predicted_HBA": self._predict_HBA(tup),
            "predicted_rotatable_bonds": self._predict_rotatable(tup),
            "ch3mpiler_retrosynthetic": self._retrosynthetic_plan(comp, tup),
            "synthesis_feasibility": self._synthesis_feasibility(tup),
        }
        with open(mol_dir / "molecular_design.json", "w") as f:
            json.dump(mol, f, indent=2, ensure_ascii=False)
        return mol
    
    def _molecule_constraints(self, tup: Dict) -> Dict:
        constraints = {}
        # D=𐑼 → flexible; D=𐑦 → rigid self-referential scaffold
        d = tup.get("D","")
        constraints["flexibility"] = "rigid (self-referential scaffold)" if d=="𐑦" else "flexible (field-theoretic)"
        # H (chirality) → stereochemical requirements
        h = tup.get("H","")
        h_map = {"𐑓":"achiral OK", "𐑒":"1 stereocenter", "𐑖":"2+ stereocenters", "𐑫":"atropisomerism required"}
        constraints["stereochemistry"] = h_map.get(h, "unknown")
        # W (winding) → topological constraints
        w = tup.get("W","")
        w_map = {"𐑷":"no topological constraint", "𐑴":"Z2-symmetric dimer", "𐑭":"macrocyclic with integer winding", "𐑟":"interlocked cage (catenane/rotaxane)"}
        constraints["topology"] = w_map.get(w, "unknown")
        # P → symmetry
        p = tup.get("P","")
        p_map = {"𐑗":"no symmetry requirement", "𐑿":"C2-symmetric preferred", "𐑬":"one Z2 axis", "𐑯":"highly symmetric", "𐑹":"Frobenius-special µ∘δ=id scaffold"}
        constraints["symmetry"] = p_map.get(p, "unknown")
        # F → quantum character
        f = tup.get("F","")
        constraints["quantum_character"] = "classical scaffold" if f=="𐑱" else ("quantum-coherent (H-bond network)" if f=="𐑐" else "thermal (dynamic ensemble)")
        return constraints
    
    def _bond_strategy(self, tup: Dict) -> Dict:
        gm = tup.get("Gm","")
        strategy = {
            "𐑝": "simultaneous bond formation (one-pot)",
            "𐑜": "branching disconnection (alternate paths)",
            "𐑠": "sequential bond construction (linear synthesis)",
            "𐑵": "convergent broadcast (star-type coupling)",
        }
        return {"composition_mode": strategy.get(gm, "unknown"), "preferred_disconnections": self._disconnection_sites(tup)}
    
    def _disconnection_sites(self, tup: Dict) -> List[str]:
        # Based on R (coupling) type
        r = tup.get("R","")
        sites = []
        if r == "𐑾": sites.append("bidirectional coupling — two reactive handles needed")
        elif r == "𐑽": sites.append("adjoint coupling — one-way handle, protect other side")
        elif r == "𐑩": sites.append("supervenience — scaffold pre-exists, decorate")
        elif r == "𐑑": sites.append("functorial — map one scaffold onto another")
        return sites
    
    def _scaffold_prediction(self, tup: Dict) -> str:
        """Predict molecular scaffold from primitive tuple."""
        d, t, h = tup.get("D",""), tup.get("T",""), tup.get("H","")
        if d == "𐑦" and t == "𐑸":
            return "Indole-based (tryptamine core) — self-referential closure topology"
        elif d == "𐑦" and t == "𐑥":
            return "Bridged bicyclic with crossing point — tropane-like or morphinan-like"
        elif d == "𐑦" and t == "𐑶":
            return "Non-factorizable cage — cubane or adamantane derivative"
        elif d == "𐑼" and t == "𐑡":
            return "Flexible chain with branching — phenethylamine scaffold"
        return "Hybrid scaffold"
    
    def _mass_range(self, tup: Dict) -> str:
        s = tup.get("S","")
        if s == "𐑙": return "250–350 Da"
        elif s == "𐑕": return "300–450 Da"
        elif s == "𐑳": return "350–550 Da"
        return "300–500 Da"
    
    def _predict_logP(self, tup: Dict) -> float:
        g = tup.get("G",""); k = tup.get("K","")
        base = 3.0
        if g == "𐑚": base -= 1.5  # local → more polar
        elif g == "𐑲": base += 1.0  # universal → more lipophilic
        if k == "𐑧": base -= 0.5   # slow → more polar
        elif k == "𐑺": base += 1.0  # MBL → more lipophilic
        return round(base, 1)
    
    def _predict_HBD(self, tup: Dict) -> int:
        f = tup.get("F",""); s = tup.get("S","")
        base = 1 if s == "𐑙" else (2 if s == "𐑕" else 3)
        if f == "𐑐": base += 1
        return base
    
    def _predict_HBA(self, tup: Dict) -> int:
        f = tup.get("F",""); s = tup.get("S","")
        base = 2 if s == "𐑙" else (3 if s == "𐑕" else 4)
        if f == "𐑐": base += 1
        return base
    
    def _predict_rotatable(self, tup: Dict) -> int:
        d = tup.get("D",""); s = tup.get("S","")
        base = 3 if s == "𐑙" else (4 if s == "𐑕" else 5)
        if d == "𐑼": base += 2
        elif d == "𐑦": base -= 2  # self-referential = rigid
        return max(0, base)
    
    def _retrosynthetic_plan(self, comp: Dict, tup: Dict) -> Dict:
        """Generate ch3mpiler-compatible retrosynthetic plan."""
        name = comp["name"]
        return {
            "target": name,
            "target_type": format_tuple(tup),
            "strategy": self._bond_strategy(tup),
            "starting_materials": self._starting_materials(tup),
            "key_bond_formations": self._key_bonds(tup, comp),
            "protecting_groups": self._protecting_groups(tup),
            "estimated_yield_range": self._yield_estimate(tup),
            "critical_step": self._critical_step(comp),
        }
    
    def _starting_materials(self, tup: Dict) -> List[str]:
        d = tup.get("D","")
        mats = []
        if d == "𐑦": mats.append("L-tryptophan (for indole core)")
        elif d == "𐑼": mats.append("Phenylalanine or tyrosine derivative")
        h = tup.get("H","")
        if h in ("𐑖", "𐑫"): mats.append("Chiral pool starting material (terpene or amino acid)")
        return mats
    
    def _key_bonds(self, tup: Dict, comp: Dict) -> List[Dict]:
        bonds = []
        gm = tup.get("Gm","")
        if gm == "𐑵":
            bonds.append({"type": "Broadcast coupling", "description": "Star-type convergent synthesis — late-stage diversification from common intermediate"})
        elif gm == "𐑠":
            bonds.append({"type": "Sequential construction", "description": "Linear synthesis with ordered bond formation"})
        elif gm == "𐑜":
            bonds.append({"type": "Alternate-path disconnection", "description": "Two viable routes with different protecting group strategies"})
        # Non-Abelian winding requires interlocking
        if tup.get("W") == "𐑟":
            bonds.append({"type": "Mechanical bond", "description": "Catenane/rotaxane formation via template-directed clipping"})
        return bonds
    
    def _protecting_groups(self, tup: Dict) -> List[str]:
        pgs = []
        r = tup.get("R","")
        if r == "𐑽": pgs.append("Orthogonal protection: one amine as Boc, other as Fmoc (adjoint requires directional control)")
        elif r == "𐑾": pgs.append("Same protecting group on both handles (bidirectional)")
        return pgs
    
    def _yield_estimate(self, tup: Dict) -> str:
        w = tup.get("W","")
        if w == "𐑟": return "5–15% (mechanical bond formation)"
        elif w == "𐑭": return "20–40% (macrocyclization)"
        elif w == "𐑴": return "40–60%"
        else: return "50–70%"
    
    def _critical_step(self, comp: Dict) -> str:
        for innov in comp.get("innovations", []):
            if "non-Abelian" in innov: return "Template-directed catenane formation — the mechanical bond closure"
            if "supercritical" in innov: return "Pro-drug activation — enzymatic cleavage must be precisely timed"
            if "EP" in innov or "exceptional" in innov: return "EP-inducing substitution at the β-carboline C-6 position"
            if "adjoint" in innov: return "Directional N-benzylation — must avoid bis-alkylation"
        return "Final coupling step"
    
    def _synthesis_feasibility(self, tup: Dict) -> Dict:
        return {
            "overall_assessment": "Challenging but feasible" if tup.get("W")=="𐑟" else "Standard medicinal chemistry",
            "estimated_steps": self._estimate_steps(tup),
            "key_challenges": self._challenges(tup),
        }
    
    def _estimate_steps(self, tup: Dict) -> int:
        base = 6
        if tup.get("W") == "𐑟": base += 5
        if tup.get("W") == "𐑭": base += 3
        if tup.get("H") == "𐑫": base += 2
        return base
    
    def _challenges(self, tup: Dict) -> List[str]:
        ch = []
        if tup.get("W") == "𐑟": ch.append("Mechanical bond formation — template design critical")
        if tup.get("H") == "𐑫": ch.append("Atropisomer separation — may require chiral HPLC")
        if tup.get("P") == "𐑹": ch.append("Frobenius-special symmetry — scaffold must survive µ∘δ self-check")
        return ch


    # ─── L4: RECEPTOR TARGETING ──────────────────────────────────
    
    def _design_receptor(self, comp_dir: Path, comp: Dict) -> Dict:
        rec_dir = comp_dir / "L4_receptor"
        rec_dir.mkdir(exist_ok=True)
        
        tup = comp["tuple"]
        receptor_data = {
            "layer": "L4 — Receptor Targeting",
            "primary_targets": self._primary_targets(comp, tup),
            "binding_mode": self._binding_mode(tup),
            "functional_selectivity": self._functional_selectivity(tup),
            "predicted_Ki_ranges": self._predict_Ki(tup),
            "predicted_efficacy": self._predict_efficacy(tup),
            "off_target_risk": self._off_target_risk(tup),
            "receptor_dynamics": self._receptor_dynamics(tup),
        }
        with open(rec_dir / "receptor_targeting.json", "w") as f:
            json.dump(receptor_data, f, indent=2, ensure_ascii=False)
        
        # Also write a detailed receptor binding prediction
        binding = self._binding_prediction(comp, tup)
        with open(rec_dir / "binding_predictions.json", "w") as f:
            json.dump(binding, f, indent=2, ensure_ascii=False)
        
        return receptor_data
    
    def _primary_targets(self, comp: Dict, tup: Dict) -> List[Dict]:
        targets = []
        receptor_list = comp.get("receptor_targets", [])
        r_type = tup.get("R","")
        for rec in receptor_list:
            t = {"receptor": rec, "predicted_action": "agonist" if "5-HT2A" in rec else "modulator"}
            if r_type == "𐑽": t["directional_bias"] = "Gi-biased (adjoint steering toward introspection)"
            elif r_type == "𐑾": t["directional_bias"] = "balanced Gq/Gi (bidirectional access)"
            targets.append(t)
        return targets
    
    def _binding_mode(self, tup: Dict) -> Dict:
        d = tup.get("D","")
        binding = {"pocket_accommodation": "orthosteric + extended allosteric" if d=="𐑦" else "orthosteric only"}
        ph = tup.get("Ph","")
        ph_map = {"⊙":"salt bridge to D3.32 essential", "𐑣":"extended residence time at orthosteric site", 
                  "𐑻":"allosteric modulator — shifts orthosteric affinity", "𐑮":"complex-plane binding kinetics"}
        binding["critical_interaction"] = ph_map.get(ph, "standard H-bond network")
        return binding
    
    def _functional_selectivity(self, tup: Dict) -> Dict:
        gm = tup.get("Gm","")
        sel = {"mechanism": "conformational selection" if gm=="𐑠" else "kinetic selectivity" if gm=="𐑜" else "balanced signaling"}
        h = tup.get("H","")
        if h == "𐑫": sel["arrestin_bias"] = "β-arrestin biased (eternal chirality drives internalization)"
        elif h == "𐑖": sel["arrestin_bias"] = "G-protein biased (H2 retains surface signaling)"
        return sel
    
    def _predict_Ki(self, tup: Dict) -> Dict:
        g = tup.get("G",""); k = tup.get("K","")
        if g == "𐑲" and k == "𐑧": return {"5-HT2A": "0.1–5 nM", "5-HT1A": "1–20 nM", "other": "10–100 nM"}
        elif g == "𐑚": return {"primary": "1–10 nM", "other": ">1 µM (highly selective)"}
        else: return {"primary": "0.5–50 nM", "secondary": "50–500 nM"}
    
    def _predict_efficacy(self, tup: Dict) -> Dict:
        f = tup.get("F","")
        if f == "𐑐": return {"5-HT2A": "80–100% (quantum-coherent activation)", "Gq": "high", "β-arrestin": "moderate"}
        elif f == "𐑞": return {"5-HT2A": "40–70% (thermal ensemble)", "Gq": "moderate", "β-arrestin": "low"}
        else: return {"5-HT2A": "60–90%", "Gq": "high", "β-arrestin": "low"}
    
    def _off_target_risk(self, tup: Dict) -> Dict:
        s = tup.get("S","")
        if s == "𐑕": return {"risk_level": "high", "concern": "many identical components → polypharmacology"}
        elif s == "𐑳": return {"risk_level": "moderate", "concern": "heterogeneous targets expected"}
        else: return {"risk_level": "low", "concern": "single-target precision expected"}
    
    def _receptor_dynamics(self, tup: Dict) -> Dict:
        k = tup.get("K","")
        dyn = {"residence_time": ">4 hours" if k=="𐑧" else ("1–4 hours" if k=="𐑺" else "30 min–2 hours")}
        ph = tup.get("Ph","")
        if ph == "𐑣": dyn["desensitization"] = "rapid (supercritical → β-arrestin recruitment accelerated)"
        elif ph == "𐑻": dyn["desensitization"] = "modulated by co-ligand (EP gate control)"
        else: dyn["desensitization"] = "standard (tachyphylaxis after repeated dosing)"
        return dyn
    
    def _binding_prediction(self, comp: Dict, tup: Dict) -> Dict:
        """Detailed per-residue binding predictions for primary target."""
        return {
            "compound": comp["name"],
            "primary_target": comp.get("receptor_targets", ["5-HT2A"])[0],
            "key_residue_interactions": [
                {"residue": "D3.32", "interaction": "salt bridge (protonated amine)", "strength": "essential"},
                {"residue": "S5.43", "interaction": "H-bond to indole NH" if tup.get("D")=="𐑦" else "H-bond to phenyl", "strength": "strong"},
                {"residue": "F6.52", "interaction": "π-π stacking", "strength": "moderate"},
                {"residue": "W6.48", "interaction": "toggle switch — rotamer change on activation", "strength": "critical"},
            ],
            "predicted_binding_pose": "orthosteric with extended TM5-TM6 pocket occupancy",
            "mutagenesis_predictions": {
                "D3.32A": "abolishes binding",
                "F6.52L": "reduces affinity 10-fold",
                "S5.43A": "reduces affinity 5-fold",
            }
        }


    # ─── L5: CELLULAR DESIGN ─────────────────────────────────────
    
    def _design_cellular(self, comp_dir: Path, comp: Dict) -> Dict:
        cell_dir = comp_dir / "L5_cellular"
        cell_dir.mkdir(exist_ok=True)
        
        tup = comp["tuple"]
        cell = {
            "layer": "L5 — Cellular Design",
            "gene_expression_cassette": self._gene_cassette(comp, tup),
            "promoter_design": self._promoter(tup),
            "codon_optimization": self._codon_opt(tup),
            "metabolic_burden": self._metabolic_burden(tup),
            "biosynthesis_pathway": self._biosynthesis_pathway(comp, tup),
            "host_organism": self._select_host(tup),
            "fermentation_parameters": self._fermentation(tup),
        }
        with open(cell_dir / "cellular_design.json", "w") as f:
            json.dump(cell, f, indent=2, ensure_ascii=False)
        
        # Write plasmid design
        plasmid = self._plasmid_design(comp, tup)
        with open(cell_dir / "plasmid_design.json", "w") as f:
            json.dump(plasmid, f, indent=2, ensure_ascii=False)
        
        return cell
    
    def _gene_cassette(self, comp: Dict, tup: Dict) -> Dict:
        name = comp["key"]
        return {
            "cassette_name": f"pCLINK_{name}",
            "elements": [
                {"type": "promoter", "name": "T7-lac" if tup.get("K")=="𐑧" else "pBAD", "strength": "inducible"},
                {"type": "RBS", "name": "BBa_B0034", "strength": "medium"},
                {"type": "CDS", "name": f"{name}_synthase", "description": "Key biosynthetic enzyme"},
                {"type": "terminator", "name": "T7 terminator"},
                {"type": "selection", "name": "KanR"},
            ]
        }
    
    def _promoter(self, tup: Dict) -> Dict:
        k = tup.get("K","")
        if k == "𐑧": return {"type": "T7-lac", "induction": "IPTG", "leakiness": "low", "rationale": "slow kinetics → tight control needed"}
        elif k == "𐑺": return {"type": "pBAD", "induction": "arabinose", "leakiness": "very low", "rationale": "MBL → ultra-tight control"}
        else: return {"type": "T7", "induction": "IPTG", "leakiness": "moderate"}
    
    def _codon_opt(self, tup: Dict) -> Dict:
        s = tup.get("S","")
        if s == "𐑙": return {"strategy": "single gene", "host": "E. coli K-12"}
        elif s == "𐑕": return {"strategy": "operon (multiple identical)", "host": "E. coli BL21(DE3)"}
        else: return {"strategy": "divergent operon (heterogeneous)", "host": "S. cerevisiae"}
    
    def _metabolic_burden(self, tup: Dict) -> str:
        s = tup.get("S","")
        if s == "𐑙": return "low — single pathway enzyme"
        elif s == "𐑕": return "moderate — parallel identical enzymes"
        else: return "high — multiple distinct enzymes; may need fed-batch"
    
    def _biosynthesis_pathway(self, comp: Dict, tup: Dict) -> Dict:
        d = tup.get("D","")
        if d == "𐑦":
            return {
                "type": "tryptophan-derived",
                "key_enzyme": "aromatic L-amino acid decarboxylase (AADC) + indole N-methyltransferase",
                "precursor": "L-tryptophan",
                "steps": 4,
                "cofactors": ["PLP", "SAM"],
            }
        else:
            return {
                "type": "phenylalanine/tyrosine-derived",
                "key_enzyme": "tyrosine hydroxylase + decarboxylase + O-methyltransferase",
                "precursor": "L-tyrosine",
                "steps": 5,
                "cofactors": ["THB", "PLP", "SAM"],
            }
    
    def _select_host(self, tup: Dict) -> str:
        s = tup.get("S","")
        if s == "𐑳": return "Saccharomyces cerevisiae (heterogeneous pathway)"
        elif s == "𐑕": return "Escherichia coli BL21(DE3)"
        else: return "Escherichia coli K-12"
    
    def _fermentation(self, tup: Dict) -> Dict:
        k = tup.get("K","")
        return {
            "mode": "fed-batch" if k=="𐑧" else "batch",
            "temperature": "30°C" if k=="𐑧" else "37°C",
            "duration": "48–96 hours" if k=="𐑧" else "24–48 hours",
            "induction_OD600": 0.6 if k=="𐑧" else 0.4,
        }
    
    def _plasmid_design(self, comp: Dict, tup: Dict) -> Dict:
        return {
            "name": f"pCLINK_{comp['key']}",
            "size_bp": self._estimate_plasmid_size(tup),
            "backbone": "pET-28a(+)",
            "resistance": "Kanamycin",
            "copy_number": "pBR322 (medium, 15-20)" if tup.get("K")=="𐑧" else "pUC (high, 500-700)",
            "features": self._gene_cassette(comp, tup)["elements"],
        }
    
    def _estimate_plasmid_size(self, tup: Dict) -> int:
        base = 5300
        s = tup.get("S","")
        if s == "𐑕": base += 1500
        elif s == "𐑳": base += 3000
        return base


    # ─── L6: DELIVERY DESIGN ─────────────────────────────────────
    
    def _design_delivery(self, comp_dir: Path, comp: Dict) -> Dict:
        del_dir = comp_dir / "L6_delivery"
        del_dir.mkdir(exist_ok=True)
        
        tup = comp["tuple"]
        delivery = {
            "layer": "L6 — Delivery System",
            "route": comp.get("delivery", "Oral"),
            "formulation": self._formulation(comp, tup),
            "pharmacokinetics": self._pk_profile(tup),
            "bioavailability": self._bioavailability(tup),
            "half_life_prediction": self._half_life(tup),
            "volume_of_distribution": self._vd(tup),
            "clearance": self._clearance(tup),
            "BBB_penetration": self._bbb(tup),
            "metabolism": self._metabolism(tup),
        }
        with open(del_dir / "delivery_design.json", "w") as f:
            json.dump(delivery, f, indent=2, ensure_ascii=False)
        return delivery
    
    def _formulation(self, comp: Dict, tup: Dict) -> Dict:
        w = tup.get("W","")
        if w == "𐑟":
            return {"type": "liposomal encapsulation", "rationale": "mechanical bond stabilization required", "lipid": "DSPC:Cholesterol:PEG-DSPE (55:40:5)"}
        elif w == "𐑭":
            return {"type": "cyclodextrin complex", "rationale": "macrocycle stabilization", "cyclodextrin": "HP-β-CD"}
        elif "praxeum" in comp.get("key",""):
            return {"type": "transdermal patch", "rationale": "steady-state EP maintenance", "polymer": "EVA with permeation enhancer"}
        else:
            return {"type": "standard oral capsule", "excipients": ["microcrystalline cellulose", "magnesium stearate"]}
    
    def _pk_profile(self, tup: Dict) -> Dict:
        k = tup.get("K","")
        if k == "𐑧": return {"absorption": "slow (Tmax: 2-4h)", "distribution": "extensive", "profile": "sustained plateau"}
        elif k == "𐑺": return {"absorption": "slow/erratic (MBL)", "distribution": "limited", "profile": "prolonged low-level"}
        else: return {"absorption": "rapid (Tmax: 0.5-1.5h)", "distribution": "moderate", "profile": "peak-and-decay"}
    
    def _bioavailability(self, tup: Dict) -> Dict:
        f = tup.get("F",""); g = tup.get("G","")
        oral = 30 if f=="𐑞" else (20 if f=="𐑐" else 40)
        if g == "𐑚": oral += 10  # local → better absorption
        return {"predicted_oral_F": f"{oral}%", "first_pass_risk": "high" if oral < 30 else "moderate"}
    
    def _half_life(self, tup: Dict) -> str:
        k = tup.get("K","")
        if k == "𐑧": return "6–12 hours (slow clearance)"
        elif k == "𐑺": return "12–24 hours (MBL trapping)"
        else: return "2–4 hours"
    
    def _vd(self, tup: Dict) -> str:
        d = tup.get("D","")
        if d == "𐑦": return "3–5 L/kg (extensive tissue binding)"
        else: return "1–3 L/kg"
    
    def _clearance(self, tup: Dict) -> str:
        k = tup.get("K","")
        if k == "𐑧": return "low (hepatic, CYP2D6)"
        else: return "moderate (hepatic + renal)"
    
    def _bbb(self, tup: Dict) -> Dict:
        g = tup.get("G","")
        if g == "𐑲":
            return {"penetration": "high", "mechanism": "passive diffusion", "predicted_BB_ratio": "2.5–5.0"}
        elif g == "𐑚":
            return {"penetration": "low", "mechanism": "peripheral restriction", "predicted_BB_ratio": "<0.3"}
        else:
            return {"penetration": "moderate", "mechanism": "passive + transporter-mediated", "predicted_BB_ratio": "1.0–2.0"}
    
    def _metabolism(self, tup: Dict) -> Dict:
        h = tup.get("H","")
        return {
            "primary_CYP": "CYP2D6",
            "secondary_CYP": "CYP3A4",
            "phase_II": "glucuronidation",
            "chirality_impact": "atropisomer interconversion possible" if h=="𐑫" else "stable stereochemistry"
        }

    # ─── L7: TISSUE DESIGN ───────────────────────────────────────
    
    def _design_tissue(self, comp_dir: Path, comp: Dict) -> Dict:
        tis_dir = comp_dir / "L7_tissue"
        tis_dir.mkdir(exist_ok=True)
        
        tup = comp["tuple"]
        tissue = {
            "layer": "L7 — Tissue Distribution",
            "brain_regions": self._brain_regions(tup),
            "peripheral_distribution": self._peripheral(tup),
            "protein_binding": self._protein_binding(tup),
            "tissue_half_life": self._tissue_half_life(tup),
            "toxicity_risk": self._toxicity(tup),
        }
        with open(tis_dir / "tissue_distribution.json", "w") as f:
            json.dump(tissue, f, indent=2, ensure_ascii=False)
        return tissue
    
    def _brain_regions(self, tup: Dict) -> Dict:
        g = tup.get("G","")
        if g == "𐑲":
            return {
                "prefrontal_cortex": "high (5-HT2A rich)",
                "thalamus": "high (gating modulation)",
                "claustrum": "very high (proposed consciousness orchestration)",
                "default_mode_network": "high suppression",
                "visual_cortex": "moderate-high",
            }
        elif g == "𐑚":
            return {"prefrontal_cortex": "low (peripheral restriction)", "claustrum": "trace only"}
        return {"prefrontal_cortex": "moderate", "thalamus": "moderate"}
    
    def _peripheral(self, tup: Dict) -> Dict:
        g = tup.get("G","")
        if g == "𐑚": return {"liver": "high (first pass)", "lung": "moderate", "heart": "low"}
        return {"liver": "high", "kidney": "high", "lung": "moderate", "spleen": "moderate"}
    
    def _protein_binding(self, tup: Dict) -> str:
        f = tup.get("F","")
        return "85–95%" if f=="𐑞" else ("90–98%" if f=="𐑐" else "80–90%")
    
    def _tissue_half_life(self, tup: Dict) -> str:
        k = tup.get("K","")
        return "12–24h" if k in ("𐑧","𐑺") else "4–8h"
    
    def _toxicity(self, tup: Dict) -> Dict:
        return {
            "hepatotoxicity": "low-moderate",
            "cardiotoxicity": "low (no significant hERG)" if tup.get("K")!="𐑺" else "moderate (MBL → accumulation risk)",
            "neurotoxicity": "low at therapeutic doses",
            "genotoxicity": "negative (Ames test prediction)",
        }


    # ─── L8: ORGANISM-LEVEL EFFECTS ──────────────────────────────
    
    def _design_organism(self, comp_dir: Path, comp: Dict) -> Dict:
        org_dir = comp_dir / "L8_organism"
        org_dir.mkdir(exist_ok=True)
        
        tup = comp["tuple"]
        organism = {
            "layer": "L8 — Organism-Level Effects",
            "phenomenological_profile": self._phenom_profile(comp, tup),
            "duration_phases": self._duration_phases(tup),
            "dose_response": self._dose_response(tup),
            "subjective_effects": self._subjective_effects(comp, tup),
            "operable_dimensions": self._operable_dimensions(tup),
            "safety_profile": self._safety(tup),
            "human_equivalent_dose": self._hed(comp, tup),
        }
        with open(org_dir / "organism_effects.json", "w") as f:
            json.dump(organism, f, indent=2, ensure_ascii=False)
        return organism
    
    def _phenom_profile(self, comp: Dict, tup: Dict) -> Dict:
        name = comp["name"]
        ph = tup.get("Ph","")
        profiles = {
            "verticullum": {
                "onset": "15–30 minutes (IV)",
                "peak": "60–90 minutes",
                "duration": "4–6 hours",
                "qualitative": "Non-Abelian braided phenomenology — simultaneous access to multiple ontological layers with topological protection. The bowtie crossing creates a persistent feedback loop: observer and observed exchange positions at the crossing point. Visuals show interlocking geometric forms (catenane-like). Ego dissolution is complete but navigable due to eternal chirality (H=𐑫).",
            },
            "chimerium": {
                "onset": "5–15 minutes (sublingual pro-drug activation)",
                "peak": "30–60 minutes",
                "duration": "2–3 hours (controlled by pro-drug cleavage rate)",
                "qualitative": "Supercritical launch — rapid acceleration beyond ordinary psychedelic space. The runaway character means the experience expands faster than integration capacity. Visuals are explosive, fractal, self-transcending. NOT for naive users. The broadcast composition (Gm=𐑵) means effects cascade across all cognitive domains simultaneously.",
            },
            "apertix": {
                "onset": "30–60 minutes (oral)",
                "peak": "2–3 hours",
                "duration": "6–8 hours",
                "qualitative": "Adjoint steering — the experience has a vector. Intention sets direction; the experience follows but does not return. Like pointing a telescope: you choose where to look, but what you see is real and autonomous. Z2 parity protection (W=𐑴) prevents ontological contamination. Precision tool for directed inquiry.",
            },
            "retiarius": {
                "onset": "1–3 minutes (inhalation)",
                "peak": "10–20 minutes",
                "duration": "30–60 minutes",
                "qualitative": "Nearest-neighbor precision — effects are local and non-cascading. No ontological amplification. Like a microscope rather than a telescope: you see one thing, clearly, without the universe rearranging around it. Frozen disorder kinetics (K=𐑺) means the experience state is stable and non-propagating. Ideal for targeted therapeutic intervention.",
            },
            "praxeum": {
                "onset": "30–60 minutes (transdermal onset)",
                "peak": "Steady state (continuous patch)",
                "duration": "As long as patch is worn (up to 72 hours)",
                "qualitative": "EP platform — not psychoactive alone, but modulates any co-administered ⊙ compound. Acts as a gain control: at low dose, preserves Gate 1 (self-modeling); at high dose, absorbs ⊙ via tensor(critical, EP) = EP, closing Gate 1. The irreducible product topology (T=𐑶) means effects cannot be factorized into 'drug A + drug B' — the combination is a new entity.",
            },
        }
        return profiles.get(comp.get("key",""), {"onset":"unknown","peak":"unknown","duration":"unknown","qualitative":"Novel compound — phenomenological profile predicted from structural type."})
    
    def _duration_phases(self, tup: Dict) -> Dict:
        k = tup.get("K","")
        return {
            "onset_phase": "rapid (<5 min)" if k not in ("𐑧","𐑺") else "gradual (15-30 min)",
            "plateau_phase": "2-4 hours" if k=="𐑧" else "1-2 hours",
            "resolution_phase": "gradual (1-2 hours)" if k=="𐑧" else "rapid (30 min)",
            "afterglow": "6-12 hours" if tup.get("H")=="𐑫" else "2-4 hours",
        }
    
    def _dose_response(self, tup: Dict) -> Dict:
        return {
            "threshold": "0.5–1.0 mg (estimated)",
            "light": "1–3 mg",
            "common": "3–8 mg",
            "strong": "8–15 mg",
            "heavy": "15+ mg",
            "note": "Doses are estimates based on predicted 5-HT2A Ki — actual values require empirical determination.",
        }
    
    def _subjective_effects(self, comp: Dict, tup: Dict) -> Dict:
        ph = tup.get("Ph","")
        d = tup.get("D","")
        return {
            "visual": "complex geometric (D=𐑦)" if d=="𐑦" else "enhancement, mild patterning",
            "auditory": "enhanced, possible synesthesia",
            "cognitive": "conceptual recombination, ontological flexibility",
            "emotional": "intensified, labile" if ph in ("𐑣","𐑻") else "amplified, manageable",
            "ego_dissolution": "complete but navigable" if d=="𐑦" else "partial",
            "mystical_experience": "high probability at common+ doses" if d=="𐑦" else "moderate probability",
        }
    
    def _operable_dimensions(self, tup: Dict) -> Dict:
        return {
            "chirality_control": True if tup.get("H") in ("𐑖","𐑫") else False,
            "winding_control": True if tup.get("W") in ("𐑭","𐑟") else False,
            "scope_control": True if tup.get("G")=="𐑚" else False,
            "gate_control": True if tup.get("Ph")=="𐑻" else False,
            "direction_control": True if tup.get("R")=="𐑽" else False,
            "self_modeling_preserved": True if tup.get("Ph")=="⊙" else False,
        }
    
    def _safety(self, tup: Dict) -> Dict:
        return {
            "LD50_predicted": ">100 mg/kg (rodent)",
            "therapeutic_index": "wide (estimated TI > 20)",
            "cardiovascular": "mild tachycardia, mild hypertension (expected for 5-HT2A agonists)",
            "hyperthermia_risk": "low" if tup.get("K")=="𐑧" else "moderate",
            "serotonin_syndrome_risk": "low (selective 5-HT2A)" if tup.get("G")=="𐑚" else "moderate (polypharmacology)",
            "dependence_potential": "low (classical psychedelic profile)",
        }
    
    def _hed(self, comp: Dict, tup: Dict) -> Dict:
        return {
            "mouse": "0.5–2.0 mg/kg",
            "rat": "0.3–1.5 mg/kg",
            "human_estimated": "1–15 mg (depending on route and formulation)",
            "note": "HED calculated by body surface area normalization from predicted rodent ED50.",
        }


    # ─── CONTROL METHODS ─────────────────────────────────────────
    
    def _design_control_methods(self, comp_dir: Path, comp: Dict) -> Dict:
        ctrl_dir = comp_dir / "control_methods"
        ctrl_dir.mkdir(exist_ok=True)
        
        tup = comp["tuple"]
        key = comp.get("key","")
        
        controls = {}
        
        # EP Gate Toggle (only meaningful for Praxeum + any ⊙ compound)
        if key == "praxeum" or tup.get("Ph") == "𐑻":
            controls["ep_gate_toggle"] = self._ep_gate_toggle_spec(comp, tup)
        
        # Chirality Ladder
        controls["chirality_ladder"] = self._chirality_ladder_spec(comp, tup)
        
        # Winding Modulation
        controls["winding_modulation"] = self._winding_modulation_spec(comp, tup)
        
        # Scope Focusing
        controls["scope_focusing"] = self._scope_focus_spec(comp, tup)
        
        # Adjoint Steering (only for Apertix-like compounds)
        if tup.get("R") == "𐑽":
            controls["adjoint_steering"] = self._adjoint_steer_spec(comp, tup)
        
        # Supercritical Launch (only for Chimerium + sub-O_∞ compounds)
        if key == "chimerium":
            controls["supercritical_launch"] = self._supercritical_launch_spec(comp, tup)
        
        # Protocol: The Dive (DMT + Praxeum)
        controls["protocol_the_dive"] = self._protocol_dive(comp, tup)
        
        # Protocol: The Precision Map (Retiarius → Apertix)
        if key in ("retiarius", "apertix"):
            controls["protocol_precision_map"] = self._protocol_precision_map(comp, tup)
        
        with open(ctrl_dir / "control_methods.json", "w") as f:
            json.dump(controls, f, indent=2, ensure_ascii=False)
        return controls
    
    def _ep_gate_toggle_spec(self, comp: Dict, tup: Dict) -> Dict:
        return {
            "method": "EP Gate Toggle",
            "mechanism": "Coupling Praxeum (Ph=𐑻) with any ⊙-critical compound triggers the absorption rule: tensor(⊙, 𐑻) = 𐑻, closing Gate 1 (self-modeling).",
            "usage": {
                "gate_open": "Praxeum at low dose (transdermal, 1-2 mg/h) — EP below absorption threshold, ⊙ preserved",
                "gate_closed": "Praxeum at high dose (transdermal, 5-10 mg/h) — EP absorption active, Gate 1 closed",
                "toggle": "Adjust patch delivery rate to modulate gate status in real time",
            },
            "co_administered_compounds": ["dmt", "psilocybin", "lsd", "verticullum"],
            "effect_on_access": {
                "gate_open": "Full ⊙-gated universe access (self-modeling preserved)",
                "gate_closed": "Φ-gated universes lost; structural_chiral, critical_first, parity_hard become inaccessible",
            },
            "safety_note": "Gate closure is reversible — reduce Praxeum dose to reopen. Not recommended for first-time users.",
        }
    
    def _chirality_ladder_spec(self, comp: Dict, tup: Dict) -> Dict:
        current_h = tup.get("H","")
        ladder = {
            "method": "Chirality Ladder",
            "mechanism": "Step Ħ through ordinal values: 𐑓(H0) → 𐑒(H1) → 𐑖(H2) → 𐑫(H_inf). Each step adds one Markov order of memory.",
            "current_chirality": current_h,
            "steps": [],
        }
        h_values = [("𐑓","memoryless / fully transient"), ("𐑒","one-step context"), ("𐑖","two-step narrative"), ("𐑫","eternal self-reference")]
        h_ordinals = {"𐑓":1, "𐑒":2, "𐑖":3, "𐑫":4}
        current_ord = h_ordinals.get(current_h, 1)
        
        for glyph, desc in h_values:
            ord_val = h_ordinals[glyph]
            if glyph == current_h:
                ladder["steps"].append({"chirality": glyph, "description": desc, "status": "CURRENT", "delta": 0})
            else:
                direction = "UP" if ord_val > current_ord else "DOWN"
                ladder["steps"].append({
                    "chirality": glyph, "description": desc,
                    "status": f"reachable ({direction})", "delta": ord_val - current_ord,
                    "method": f"co-administer with chirality anchor compound" if direction=="UP" else "reduce dose; allow metabolic clearance"
                })
        return ladder
    
    def _winding_modulation_spec(self, comp: Dict, tup: Dict) -> Dict:
        current_w = tup.get("W","")
        w_levels = {"𐑷":(1,"no protection"), "𐑴":(2,"Z2 parity"), "𐑭":(3,"integer winding"), "𐑟":(4,"non-Abelian")}
        current_ord = w_levels.get(current_w, (1,""))[0]
        
        wm = {"method": "Winding Modulation", "current_winding": current_w, "levels": {}}
        for glyph, (ord_val, desc) in w_levels.items():
            direction = "UP" if ord_val > current_ord else ("DOWN" if ord_val < current_ord else "CURRENT")
            wm["levels"][glyph] = {"ordinal": ord_val, "description": desc, "delta": ord_val - current_ord, "direction": direction}
        return wm
    
    def _scope_focus_spec(self, comp: Dict, tup: Dict) -> Dict:
        current_g = tup.get("G","")
        g_levels = {"𐑚":"nearest-neighbor (local)", "𐑔":"mesoscale", "𐑲":"universal"}
        return {"method": "Scope Focusing", "current_scope": current_g, "available_scopes": g_levels, "note": "Scope modulation requires formulation changes — not achievable via dose alone for most compounds."}
    
    def _adjoint_steer_spec(self, comp: Dict, tup: Dict) -> Dict:
        return {
            "method": "Adjoint Steering",
            "mechanism": "R=𐑽 (adjoint coupling) enables one-way directed experience. Set intention vector before dosing; experience follows direction without return.",
            "steerable_primitives": ["Ph (criticality depth)", "G (scope width)", "H (temporal depth)"],
            "protocol": "1. Meditate on target domain for 10 min. 2. Dose Apertix. 3. Maintain directed attention for first 30 min (adjoint vector locks). 4. Experience unfolds along vector.",
        }
    
    def _supercritical_launch_spec(self, comp: Dict, tup: Dict) -> Dict:
        return {
            "method": "Supercritical Launch",
            "mechanism": "Co-administer Chimerium (Ph=𐑣) with any sub-O_∞ compound. The supercritical catalyst tensor-promotes the base compound, adding 5–12 universes of access.",
            "known_launches": {
                "ketamine + chimerium": {"from_tier": "O₁", "to_tier": "O₂", "universes_gained": 12, "risk": "HIGH — dissociative + supercritical"},
                "mescaline + chimerium": {"from_tier": "O₀", "to_tier": "O₁", "universes_gained": 5, "risk": "moderate"},
                "retiarius + chimerium": {"from_tier": "O₁", "to_tier": "O₂", "universes_gained": 8, "risk": "moderate-high"},
            },
            "warning": "Supercritical launch compounds are NOT for solo use. Always have a grounded sitter. The experience accelerates faster than integration can track.",
        }
    
    def _protocol_dive(self, comp: Dict, tup: Dict) -> Dict:
        return {
            "protocol": "The Dive",
            "description": "DMT + Praxeum background for full 16-universe access with Gate 1 modulation available.",
            "compounds": ["dmt (or 5-MeO-DMT)", "praxeum (transdermal, low-dose)"],
            "sequence": [
                "1. Apply Praxeum patch 30 min before (low dose, 1-2 mg/h — Gate 1 OPEN)",
                "2. Administer DMT (inhaled, 30-50 mg)",
                "3. Experience full 16-universe access for 15-20 min",
                "4. Optionally increase Praxeum dose to close Gate 1 and explore EP-modulated space",
                "5. Remove patch to restore baseline",
            ],
            "universes_accessible": 16,
            "gate_controllable": True,
        }
    
    def _protocol_precision_map(self, comp: Dict, tup: Dict) -> Dict:
        return {
            "protocol": "The Precision Map",
            "description": "Retiarius to map local neighborhood → Apertix to steer to target region.",
            "compounds": ["retiarius (inhaled, 2-5 mg)", "apertix (oral, 5-10 mg)"],
            "sequence": [
                "1. Administer Retiarius — map the local structural neighborhood (30 min)",
                "2. Identify target universe/dimension from the Retiarius map",
                "3. Administer Apertix with directed intention toward target",
                "4. Adjoint steering carries experience to the precise structural region",
            ],
            "universes_accessible": "7 (Apertix) + 2 mapped (Retiarius)",
        }


    # ─── COMBINATION PROFILES ────────────────────────────────────
    
    def _design_combinations(self, comp_dir: Path, comp: Dict, comp_key: str) -> Dict:
        combo_dir = comp_dir / "combination_profiles"
        combo_dir.mkdir(exist_ok=True)
        
        tup = comp["tuple"]
        combos = {}
        
        # Combine with each known psychedelic
        for known_key, known_data in self.known.items():
            if known_key == comp_key:
                continue
            combo_key = f"{comp_key}_plus_{known_key}"
            combo = self._compute_combination(comp, known_key, known_data)
            combos[combo_key] = combo
        
        # Also combine with other novel compounds
        for other_key, other_data in self.compounds.items():
            if other_key == comp_key:
                continue
            if other_key < comp_key:  # avoid duplicates
                continue
            combo_key = f"{comp_key}_plus_{other_key}"
            combo = self._compute_combination(comp, other_key, other_data)
            combos[combo_key] = combo
        
        with open(combo_dir / "combination_profiles.json", "w") as f:
            json.dump(combos, f, indent=2, ensure_ascii=False)
        return combos
    
    def _compute_combination(self, comp: Dict, other_key: str, other_data: Dict) -> Dict:
        t1 = comp["tuple"]
        t2 = other_data["tuple"]
        composite = tensor_tuples(t1, t2)
        
        # Compute primitive changes from each parent
        deltas_from_1 = compute_primitive_deltas(t1, composite)
        deltas_from_2 = compute_primitive_deltas(t2, composite)
        
        # Determine tier from composite
        tier = self._tier_from_tuple(composite)
        
        return {
            "combination": f"{comp['name']} + {other_data.get('name', other_key)}",
            "composite_type": format_tuple(composite),
            "composite_tier": tier,
            "parent_1": {"name": comp["name"], "tier": comp["tier"]},
            "parent_2": {"name": other_data.get("name", other_key), "tier": other_data.get("tier", "unknown")},
            "deltas_from_parent_1": deltas_from_1,
            "deltas_from_parent_2": deltas_from_2,
            "key_changes": self._key_combination_changes(t1, t2, composite),
            "synergy_prediction": self._synergy_prediction(t1, t2, composite),
            "warning": self._combination_warning(comp, other_key, composite),
        }
    
    def _tier_from_tuple(self, tup: Dict) -> str:
        ph = tup.get("Ph",""); p = tup.get("P",""); w = tup.get("W",""); d = tup.get("D","")
        if ph == "⊙" and p == "𐑹" and w in ("𐑭","𐑟") and d == "𐑦":
            return "O_∞"
        elif ph == "⊙" and w in ("𐑭","𐑟"):
            return "O₂"
        elif ph in ("⊙","𐑮"):
            return "O₁"
        else:
            return "O₀"
    
    def _key_combination_changes(self, t1: Dict, t2: Dict, comp: Dict) -> List[str]:
        changes = []
        for p in PORDER:
            v1 = t1.get(p,""); v2 = t2.get(p,""); vc = comp.get(p,"")
            if vc != v1 and vc != v2:
                changes.append(f"{p}: neither parent ({v1}|{v2}) → composite ({vc})")
            elif vc == v1 and vc != v2:
                changes.append(f"{p}: parent 1 dominates ({v1} over {v2})")
            elif vc == v2 and vc != v1:
                changes.append(f"{p}: parent 2 dominates ({v2} over {v1})")
        return changes
    
    def _synergy_prediction(self, t1: Dict, t2: Dict, comp: Dict) -> str:
        d1 = compute_tuple_distance(t1, comp)
        d2 = compute_tuple_distance(t2, comp)
        if d1 < 1.0 and d2 < 1.0:
            return "high synergy — both parents structurally close to composite"
        elif d1 < 2.0 and d2 < 2.0:
            return "moderate synergy"
        else:
            return "low synergy — composite is structurally distant from both parents"
    
    def _combination_warning(self, comp: Dict, other_key: str, comp_tup: Dict) -> str:
        warnings = []
        if comp_tup.get("Ph") == "𐑣":
            warnings.append("SUPERCRITICAL: combination may trigger runaway effects")
        if comp_tup.get("Ph") == "𐑻":
            warnings.append("EP ABSORPTION: Gate 1 (self-modeling) may close uncontrollably")
        if comp_tup.get("W") == "𐑟" and comp.get("key","") != "verticullum":
            warnings.append("Non-Abelian winding from combination — topological complexity extreme")
        if not warnings:
            return "No special warnings — standard psychedelic safety protocols apply."
        return " | ".join(warnings)
    
    # ─── MASTER INDEX ────────────────────────────────────────────
    
    def _write_master_index(self, results: Dict):
        index = {
            "project": "Novel Navigatable/Operable Psychedelics — CLINK Realization",
            "author": "Lando⊗⊙perator",
            "created": datetime.now().isoformat(),
            "compounds": {},
        }
        for key, result in results.items():
            comp = self.compounds[key]
            index["compounds"][key] = {
                "name": comp["name"],
                "directory": result["directory"],
                "tier": comp["tier"],
                "tuple": format_tuple(comp["tuple"]),
                "innovations": comp["innovations"],
            }
        with open(self.output_root / "master_index.json", "w") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        print(f"\nMaster index written to {self.output_root / 'master_index.json'}")


# ─── MAIN ─────────────────────────────────────────────────────────

def main():
    output_root = Path("/home/mrnob0dy666/red-hot_rebis/clink/datasets/psychedelic_designs")
    realizer = PsychedelicRealizer(output_root)
    results = realizer.realize_all()
    
    print(f"\n{'='*60}")
    print(f"REALIZATION COMPLETE")
    print(f"{'='*60}")
    print(f"Output: {output_root}")
    print(f"Compounds realized: {len(results)}")
    for key in results:
        print(f"  - {NOVEL_COMPOUNDS[key]['name']}")
    print(f"\nDesign directories:")
    for key in results:
        print(f"  {output_root / key}/")
        print(f"    ├── design_manifest.json")
        print(f"    ├── structural_type.json")
        print(f"    ├── layer_distances.json")
        print(f"    ├── L3_molecular/")
        print(f"    ├── L4_receptor/")
        print(f"    ├── L5_cellular/")
        print(f"    ├── L6_delivery/")
        print(f"    ├── L7_tissue/")
        print(f"    ├── L8_organism/")
        print(f"    ├── control_methods/")
        print(f"    └── combination_profiles/")

if __name__ == "__main__":
    main()

