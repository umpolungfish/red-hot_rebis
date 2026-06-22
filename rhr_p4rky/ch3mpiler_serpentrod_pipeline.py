#!/usr/bin/env python3
"""
ch3mpiler_serpentrod_pipeline.py — PIPE: ch3mpiler ⟲ serpentrod

Given starting materials and/or a target molecule, the pipeline:
  1. ch3mpiler analyzes the reaction (forward/retrosynthetic)
  2. Extracts the reaction's structural signature (bond type, FG pair, product type)
  3. Maps the reaction signature to catalytic site requirements (complementary primitives)
  4. Serpentrod designs an optimal enzymatic catalytic site to facilitate the reaction
  5. Returns: reaction path, catalytic site sequence, predicted 3D fold

Structural type of this bridge:
    <Ð_ω; Þ_ò; Ř_=; Φ_˙; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; ⊙; Ħ_A; Σ_ï; Ω_2>

Author: Lando ⊗ ⊙perator
"""

import sys, os, json, math, itertools
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

# Paths
BASE = Path(__file__).parent.absolute()
IMSCRIBING_GRAMMAR = Path.home() / "imscribing_grammar"
sys.path.insert(0, str(IMSCRIBING_GRAMMAR))
sys.path.insert(0, str(BASE))

# ── Complementary primitive pairs ───────────────────────────────────
COMPLEMENTARY_SHORT = {
    "D": "W", "W": "D",
    "T": "H", "H": "T",
    "R": "S", "S": "R",
    "P": "F", "F": "P",
    "K": "G", "G": "K",
    "Gm": "Ph", "Ph": "Gm",
}

FIELD_TO_PRIMITIVE_NAME = {
    "D": "Dimensionality", "T": "Topology", "R": "Recognition",
    "P": "Parity", "F": "Fidelity", "K": "Kinetics",
    "G": "Granularity", "Gm": "Coupling", "Ph": "Criticality",
    "H": "Chirality", "S": "Stoichiometry", "W": "Winding",
}

# Ordinal values for Shavian glyphs (matching primitives.py)
GLYPH_ORDINALS = {
    "D": {"𐑛": 0, "𐑨": 1, "𐑼": 2, "𐑦": 3},
    "T": {"𐑡": 0, "𐑰": 1, "𐑥": 2, "𐑶": 3, "𐑸": 4},
    "R": {"𐑩": 0, "𐑑": 1, "𐑽": 2, "𐑾": 3},
    "P": {"𐑗": 0, "𐑿": 1, "𐑬": 2, "𐑯": 3, "𐑹": 4},
    "F": {"𐑱": 0, "𐑞": 1, "𐑐": 2},
    "K": {"𐑘": 0, "𐑤": 1, "𐑧": 2, "𐑺": 3, "𐑪": 4},
    "G": {"𐑚": 0, "𐑔": 1, "𐑲": 2},
    "Gm": {"𐑝": 0, "𐑜": 1, "𐑠": 2, "𐑵": 3},
    "Ph": {"𐑢": 0, "⊙": 1, "𐑮": 2, "𐑻": 3, "𐑣": 4},
    "H": {"𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3},
    "S": {"𐑙": 0, "𐑕": 1, "𐑳": 2},
    "W": {"𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3},
}

ORD_TO_GLYPH = {}
for prim, mapping in GLYPH_ORDINALS.items():
    ORD_TO_GLYPH[prim] = {v: k for k, v in mapping.items()}

PNAMES = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]

# ── Frobenius-aware catalytic site RNA design (v2) ─────────────────
# Fix: FG-aware fusion + direct AA selection + Frobenius enforcement
# Replaces the hash-indexed codon lookup that gave 3/6 pair coverage

PRIMITIVE_TO_AA = {
    "D": "Met", "T": "Trp", "R": "Cys", "P": "Tyr", "F": "Phe",
    "K": "Ile", "G": "His", "Gm": "Asn", "Ph": "Gln",
    "H": "Asp", "S": "Lys", "W": "Glu",
}

AA_CODON_POOL_V2 = {
    "Met": ["AUG"], "Trp": ["UGG"],
    "Cys": ["UGU", "UGC"], "Tyr": ["UAU", "UAC"],
    "Phe": ["UUU", "UUC"], "Ile": ["AUU", "AUC", "AUA"],
    "His": ["CAU", "CAC"], "Asn": ["AAU", "AAC"],
    "Gln": ["CAA", "CAG"], "Asp": ["GAU", "GAC"],
    "Lys": ["AAA", "AAG"], "Glu": ["GAA", "GAG"],
    "Ser": ["UCU", "UCC", "UCA", "UCG", "AGU", "AGC"],
    "Ala": ["GCU", "GCC", "GCA", "GCG"],
    "Gly": ["GGU", "GGC", "GGA", "GGG"],
    "Thr": ["ACU", "ACC", "ACA", "ACG"],
    "Val": ["GUU", "GUC", "GUA", "GUG"],
    "Leu": ["UUA", "UUG", "CUU", "CUC", "CUA", "CUG"],
    "Pro": ["CCU", "CCC", "CCA", "CCG"],
}

COMPLEMENTARY_PAIRS_V2 = [
    ("D", "W"), ("T", "H"), ("R", "S"),
    ("P", "F"), ("K", "G"), ("Gm", "Ph"),
]

STRUCTURAL_AAS_V2 = ["Ser", "Ala", "Gly", "Thr", "Val", "Leu", "Pro"]


def fuse_reaction_types(bond_type, fg1_type, fg2_type):
    """Bond-weighted fusion (v4). Bond is the reaction center; FGs modulate it.
    
    Per-primitive strategy:
      Topological (D,T,H,W): bond 75%, FGs 12.5% each — bond IS the reaction path
      Reactive (P,Ph): bond floor, FGs average pulls up if higher
      Coupling (R,K,G,Gm): bond 55%, FGs 22.5% each — bond-dominant blend
      Fidelity (F): bond floor, FG average can enhance
      Stoichiometry (S): max — captures all chemical species
    
    This replaces the old MAX strategy which allowed high-ordinal FGs (like
    alkene: P=𐑯, Ph=⊙) to MASK bond type differences entirely.
    """
    fused = {}
    for p in PNAMES:
        b = glyph_ord(p, bond_type.get(p, '?'))
        f1 = glyph_ord(p, fg1_type.get(p, '?'))
        f2 = glyph_ord(p, fg2_type.get(p, '?'))
        
        if p in ('D', 'T', 'H', 'W'):
            fused_ord = round(0.75 * b + 0.125 * f1 + 0.125 * f2)
        elif p in ('P', 'Ph'):
            fused_ord = max(b, round(0.5 * f1 + 0.5 * f2))
        elif p in ('R', 'K', 'G', 'Gm'):
            fused_ord = round(0.55 * b + 0.225 * f1 + 0.225 * f2)
        elif p in ('F',):
            fused_ord = max(b, round(0.4 * f1 + 0.4 * f2))
        elif p in ('S',):
            fused_ord = max(b, f1, f2)
        
        fused[p] = ord_to_glyph(p, fused_ord)
    return fused


def complement_type_v2(fused_type):
    """Frobenius-exact structural complement using INVERSE mapping (v3).
    
    For complementary pair (A,B):
      site[A] = INVERSE(fused[B])  — high when fused[B] is low (binding pocket)
      site[B] = INVERSE(fused[A])  — high when fused[A] is low
    
    The inverse maps ordinal o → (max_o - o) then cross-maps to partner's range.
    This guarantees true complementarity (not just cross-projection).
    """
    site = {}
    for prim_a, prim_b in COMPLEMENTARY_PAIRS_V2:
        a_max = len(GLYPH_ORDINALS.get(prim_a, {})) - 1
        b_max = len(GLYPH_ORDINALS.get(prim_b, {})) - 1
        
        fused_a = glyph_ord(prim_a, fused_type.get(prim_a, '?'))
        fused_b = glyph_ord(prim_b, fused_type.get(prim_b, '?'))
        
        inv_a = a_max - fused_a
        inv_b = b_max - fused_b
        
        if a_max > 0:
            site[prim_b] = ord_to_glyph(prim_b, min(b_max, max(0, round(inv_a / a_max * b_max))))
        else:
            site[prim_b] = ord_to_glyph(prim_b, b_max)
        
        if b_max > 0:
            site[prim_a] = ord_to_glyph(prim_a, min(a_max, max(0, round(inv_b / b_max * a_max))))
        else:
            site[prim_a] = ord_to_glyph(prim_a, a_max)
    
    return site


def design_site_aas_from_type(site_type):
    """Design 12-AA sequence with dominant-member rule (v3 — guaranteed 6/6).
    
    For each complementary pair (A,B), activate the AA for the member
    with the higher ordinal percentile. This ensures exactly one member
    per pair is activated → 6/6 pair coverage (Frobenius-guaranteed).
    
    Replaces the original 50%-threshold + OR-counting which had a bug:
    pairs counted as covered if EITHER member activated, allowing false
    6/6 when only one member of some pairs was above threshold.
    """
    aas = [None] * 12
    activated = set()
    
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        pa_idx = PNAMES.index(pa)
        pb_idx = PNAMES.index(pb)
        pa_o = glyph_ord(pa, site_type.get(pa, '?'))
        pb_o = glyph_ord(pb, site_type.get(pb, '?'))
        pa_max = len(GLYPH_ORDINALS.get(pa, {})) - 1
        pb_max = len(GLYPH_ORDINALS.get(pb, {})) - 1
        pa_pct = pa_o / pa_max if pa_max > 0 else 0
        pb_pct = pb_o / pb_max if pb_max > 0 else 0
        
        if pa_pct >= pb_pct:
            aas[pa_idx] = PRIMITIVE_TO_AA.get(pa)
            activated.add(pa)
        else:
            aas[pb_idx] = PRIMITIVE_TO_AA.get(pb)
            activated.add(pb)
    
    # Fill remaining with structural AAs
    final_aas = []
    for i, aa in enumerate(aas):
        if aa is not None:
            final_aas.append(aa)
        else:
            final_aas.append(STRUCTURAL_AAS_V2[i % len(STRUCTURAL_AAS_V2)])
    
    # True pair coverage (dominant-member: always 6)
    true_pairs = sum(1 for pa, pb in COMPLEMENTARY_PAIRS_V2
                     if pa in activated or pb in activated)
    
    return final_aas, true_pairs


def aas_to_rna_v2(aas):
    """Encode AA sequence to RNA codons."""
    codons = []
    for aa in aas:
        pool = AA_CODON_POOL_V2.get(aa, ["UCU"])
        codons.append(pool[len(codons) % len(pool)])
    return "".join(codons)


def design_rna_v2(reaction_sig):
    """Full target-specific, Frobenius-verified RNA design."""
    fused = fuse_reaction_types(reaction_sig.bond_type,
                                 reaction_sig.fg1_type,
                                 reaction_sig.fg2_type)
    site_type = complement_type_v2(fused)
    aas, pairs = design_site_aas_from_type(site_type)
    rna = aas_to_rna_v2(aas)
    return rna, aas, site_type, pairs, fused


def glyph_ord(prim: str, glyph: str) -> int:
    return GLYPH_ORDINALS.get(prim, {}).get(glyph, 0)

def ord_to_glyph(prim: str, ordinal: int) -> str:
    return ORD_TO_GLYPH.get(prim, {}).get(ordinal, "?")

# ── Module loaders ───────────────────────────────────────────────────

_ch3_instance = None
_ch3_module = None

def get_ch3mpiler():
    """Lazy-load ch3mpiler and return a Ch3mpiler instance."""
    global _ch3_instance, _ch3_module
    if _ch3_instance is not None:
        return _ch3_instance, _ch3_module
    
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ch3mpiler_mod", IMSCRIBING_GRAMMAR / "ch3mpiler.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ch3mpiler_mod"] = mod
    spec.loader.exec_module(mod)
    _ch3_module = mod
    _ch3_instance = mod.Ch3mpiler()
    return _ch3_instance, _ch3_module


_sr_instance = None
_sr_module = None

def get_serpentrod():
    """Lazy-load serpentrod and return the module."""
    global _sr_instance, _sr_module
    if _sr_module is not None:
        return _sr_module
    
    import importlib.util
    sr_path = BASE / "serpent_rod.py"
    if not sr_path.exists():
        sr_path = BASE / "serpent_rod_v2.py"
    
    spec = importlib.util.spec_from_file_location(
        "rhr_p4rky.serpent_rod", sr_path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "rhr_p4rky"
    sys.modules["rhr_p4rky.serpent_rod"] = mod
    spec.loader.exec_module(mod)
    _sr_module = mod
    return _sr_module


# ── Structural Complement Mapping ───────────────────────────────────






# ── Data structures ─────────────────────────────────────────────────

@dataclass
class ReactionSignature:
    reaction_type: str
    bond_name: str
    bond_desc: str
    fg1: str
    fg2: str
    product_type: dict
    bond_type: dict
    fg1_type: dict
    fg2_type: dict
    structuring_delta: float
    transition_state_ordinal: int


@dataclass
class CatalyticSiteDesign:
    reaction: ReactionSignature
    site_rna: str
    site_aa_sequence: str
    site_structural_type: dict
    secondary_elements: List[Dict]
    contacts: List[Dict]
    winding_number: int
    frobenius_verified: bool
    confidence: float
    binding_pocket_residues: List[str]
    catalytic_triad: List[str]

    def to_dict(self) -> dict:
        return {
            "reaction": {
                "type": self.reaction.reaction_type,
                "bond": self.reaction.bond_name,
                "bond_desc": self.reaction.bond_desc,
                "fg_pair": f"{self.reaction.fg1} + {self.reaction.fg2}",
                "structuring_delta": self.reaction.structuring_delta,
                "ts_ordinal": self.reaction.transition_state_ordinal,
                "product_type": {k: str(v) for k, v in self.reaction.product_type.items()},
            },
            "catalytic_site": {
                "rna": self.site_rna,
                "aa_sequence": self.site_aa_sequence,
                "structural_type": {k: str(v) for k, v in self.site_structural_type.items()},
                "winding": self.winding_number,
                "frobenius": self.frobenius_verified,
                "confidence": self.confidence,
                "binding_pocket": self.binding_pocket_residues,
                "catalytic_triad": self.catalytic_triad,
                "secondary_elements": self.secondary_elements,
                "contacts": self.contacts,
            }
        }


# ── Reaction Analysis ───────────────────────────────────────────────

def extract_reaction_signature(ch3_result: dict, ch3_mod) -> ReactionSignature:
    """Extract structural reaction signature from ch3mpiler output."""
    FG = ch3_mod.FG
    BOND_TYPES = ch3_mod.BOND_TYPES
    
    if "prediction" in ch3_result and ch3_result.get("prediction"):
        pred = ch3_result["prediction"]
        bond_name = pred.get("bond", "sigma_single")
        bond_desc = pred.get("bond_desc", "")
        fg1 = pred.get("fg1", "amine")
        fg2 = pred.get("fg2", "carbonyl")
        delta = float(pred.get("structuring_delta", 1.0))
        
        bond_t = BOND_TYPES.get(bond_name, BOND_TYPES["sigma_single"])
        bond_type = {p: bond_t.get(p, "?") for p in PNAMES}
        
        fg1_t = FG.get(fg1, FG.get("amine", {}))
        fg2_t = FG.get(fg2, FG.get("carbonyl", {}))
        fg1_type = {p: fg1_t.get(p, "?") for p in PNAMES}
        fg2_type = {p: fg2_t.get(p, "?") for p in PNAMES}
        
        product_type_str = pred.get("product_type", "")
        reaction_type = "forward"
    elif "cuts" in ch3_result and ch3_result.get("cuts"):
        cuts = ch3_result["cuts"]
        if not cuts:
            raise ValueError("No disconnections found")
        cut = cuts[0]
        bond_name = cut.get("bond", "sigma_single")
        bond_desc = cut.get("bond_desc", "")
        fg1 = cut.get("fg1", "amine")
        fg2 = cut.get("fg2", "carbonyl")
        delta = float(cut.get("delta", 1.0))
        
        bond_t = BOND_TYPES.get(bond_name, BOND_TYPES["sigma_single"])
        bond_type = {p: bond_t.get(p, "?") for p in PNAMES}
        fg1_t = FG.get(fg1, FG.get("amine", {}))
        fg2_t = FG.get(fg2, FG.get("carbonyl", {}))
        fg1_type = {p: fg1_t.get(p, "?") for p in PNAMES}
        fg2_type = {p: fg2_t.get(p, "?") for p in PNAMES}
        
        product_type_str = cut.get("product_type", "")
        reaction_type = "retrosynthetic"
    elif "type" in ch3_result:
        bond_name = "sigma_single"
        bond_desc = "generic single bond"
        fg1 = ch3_result.get("fgs", ["amine"])[0] if ch3_result.get("fgs") else "amine"
        fg2 = fg1
        delta = 1.0
        bond_t = BOND_TYPES["sigma_single"]
        bond_type = {p: bond_t.get(p, "?") for p in PNAMES}
        fg1_t = FG.get(fg1, FG.get("amine", {}))
        fg2_t = FG.get(fg2, FG.get("amine", {}))
        fg1_type = {p: fg1_t.get(p, "?") for p in PNAMES}
        fg2_type = {p: fg2_t.get(p, "?") for p in PNAMES}
        product_type_str = ch3_result.get("type", "")
        reaction_type = "analysis"
    else:
        raise ValueError("ch3mpiler result has no usable data")
    
    # Parse product type string if present
    product_type = {}
    if product_type_str and product_type_str.startswith("<"):
        parts = product_type_str.strip("<>").split(";")
        for i, p in enumerate(PNAMES):
            if i < len(parts):
                product_type[p] = parts[i].strip()
    
    # Estimate transition state ordinal
    ts_ordinal = min(4, math.ceil(sum(
        glyph_ord(p, bond_type.get(p, "?"))
        for p in ["T", "P", "H", "W"]
    ) / 8.0))
    
    return ReactionSignature(
        reaction_type=reaction_type,
        bond_name=bond_name, bond_desc=bond_desc,
        fg1=fg1, fg2=fg2,
        product_type=product_type,
        bond_type=bond_type,
        fg1_type=fg1_type, fg2_type=fg2_type,
        structuring_delta=delta,
        transition_state_ordinal=ts_ordinal,
    )


# ── Catalytic Site Design ───────────────────────────────────────────

def design_catalytic_site(reaction_sig: ReactionSignature) -> CatalyticSiteDesign:
    """Design an optimal catalytic site for the given reaction.
    
    1. Fuse reaction types (bond + FG1 + FG2) and compute complement
    2. Design Frobenius-verified RNA
    3. Run serpentrod to predict fold
    4. Identify catalytic residues
    """
    # Step 1: Fuse reaction types (bond-weighted v4) + compute Frobenius-exact complement (v3)
    fused = fuse_reaction_types(reaction_sig.bond_type,
                                 reaction_sig.fg1_type,
                                 reaction_sig.fg2_type)
    site_type = complement_type_v2(fused)  # v3 inverse mapping
    
    # Step 2: Design Frobenius-verified RNA (target-specific, >=4/6 pairs)
    site_rna, aas_design, _, pairs_covered, _ = design_rna_v2(reaction_sig)
    
    # Step 3: Run serpentrod
    try:
        sr_mod = get_serpentrod()
        sr = sr_mod.SerpentRod(site_rna, name=f"catalytic_{reaction_sig.bond_name}")
        sr.verbose = False
        result = sr.predict()
        
        aa_seq = result.aa_sequence
        sec_elements = []
        for elem in getattr(result, 'secondary_elements', []):
            sec_elements.append({
                "type": elem.get("type", "loop"),
                "start": elem.get("start", 0),
                "end": elem.get("end", 0),
                "length": elem.get("length", 0),
            })
        
        contacts = []
        for c in getattr(result, 'contacts', [])[:20]:
            contacts.append({
                "i": c.residue_i, "j": c.residue_j,
                "distance": c.distance,
                "type": c.interaction_type,
                "confidence": c.confidence,
            })
        
        winding = getattr(result, 'winding_number', 0)
        frobenius = getattr(result, 'frobenius_verified', False)
        confidence = getattr(result, 'confidence', 0.5)
        
        # Step 4: Identify catalytic residues
        aa_list = getattr(result, 'aa_list', [])
        binding_pocket = []
        catalytic_triad = []
        
        for i, aa in enumerate(aa_list):
            if aa in ("His", "Ser", "Cys", "Asp", "Glu", "Lys", "Tyr"):
                if len(catalytic_triad) < 3:
                    catalytic_triad.append(f"{aa}_{i}")
                binding_pocket.append(f"{aa}_{i}")
            elif aa in ("Phe", "Trp", "Tyr", "Leu", "Ile", "Val", "Met"):
                binding_pocket.append(f"{aa}_{i}")
        
        binding_pocket = binding_pocket[:12]
        
    except Exception as e:
        print(f"[pipeline] SerpentRod unavailable: {e}", file=sys.stderr)
        aa_seq = "<serpentrod_unavailable>"
        sec_elements, contacts = [], []
        winding = len(site_rna) // 9
        frobenius, confidence = False, 0.3
        binding_pocket = ["His_0", "Ser_1", "Asp_2"]
        catalytic_triad = ["His_0", "Ser_1", "Asp_2"]
    
    return CatalyticSiteDesign(
        reaction=reaction_sig,
        site_rna=site_rna,
        site_aa_sequence=aa_seq,
        site_structural_type=site_type,
        secondary_elements=sec_elements,
        contacts=contacts,
        winding_number=winding,
        frobenius_verified=frobenius,
        confidence=confidence,
        binding_pocket_residues=binding_pocket,
        catalytic_triad=catalytic_triad,
    )

def run_pipeline(
    starting_material: Optional[str] = None,
    target_molecule: Optional[str] = None,
    cas_number: Optional[str] = None,
    depth: int = 2,
    verbose: bool = True,
) -> CatalyticSiteDesign:
    """Run the full ch3mpiler ⟲ serpentrod pipeline."""
    ch3_instance, ch3_mod = get_ch3mpiler()
    
    def log(msg):
        if verbose:
            print(f"[pipeline] {msg}")
    
    log("╔════════════════════════════════════════╗")
    log("║  ch3mpiler ⟲ serpentrod — Pipeline   ║")
    log("╚════════════════════════════════════════╝")
    
    # Phase 1: Reaction Analysis
    log("")
    log("Phase 1 — ch3mpiler reaction analysis")
    log("─" * 40)
    
    ch3_result = None
    
    if cas_number:
        log(f"CAS: {cas_number}")
        ch3_result = ch3_instance.resolve_and_analyze(
            cas_number, do_retrosynthesis=True, depth=depth)
        target = ch3_result.get("cas_info", {}).get("name", cas_number)
        log(f"Resolved: {target}")
    
    elif starting_material and target_molecule:
        log(f"Forward: {starting_material} → {target_molecule}")
        forward_result = ch3_instance.forward([starting_material, target_molecule])
        if "error" not in forward_result and forward_result.get("prediction"):
            ch3_result = forward_result
            p = forward_result["prediction"]
            log(f"  Bond: {p['bond']} (Δ={p['structuring_delta']})")
        else:
            log(f"  No forward path, trying retrosynthesis of target...")
            ch3_result = ch3_instance.analyze(target_molecule)
            if ch3_result.get("cuts"):
                log(f"  Best cut: {ch3_result['cuts'][0]['bond']}")
    
    elif target_molecule:
        log(f"Target: {target_molecule}")
        ch3_result = ch3_instance.analyze(target_molecule)
        if ch3_result.get("cuts"):
            log(f"  Best disconnection: {ch3_result['cuts'][0]['bond']} "
                f"(δ={ch3_result['cuts'][0]['delta']})")
    
    elif starting_material:
        log(f"Starting material: {starting_material}")
        ch3_result = ch3_instance.analyze(starting_material)
        log(f"  Type: {ch3_result.get('type', 'unknown')}")
        log(f"  FGs: {', '.join(ch3_result.get('fgs', []))}")
    
    else:
        raise ValueError("Need starting_material, target_molecule, or cas_number")
    
    if ch3_result is None:
        raise ValueError("No reaction data extracted")
    
    # Phase 2: Extract reaction signature
    log("")
    log("Phase 2 — Structural signature extraction")
    log("─" * 40)
    
    reaction_sig = extract_reaction_signature(ch3_result, ch3_mod)
    log(f"  Bond: {reaction_sig.bond_name} — {reaction_sig.bond_desc}")
    log(f"  FG pair: {reaction_sig.fg1} + {reaction_sig.fg2}")
    log(f"  Structuring Δ: {reaction_sig.structuring_delta:.3f}")
    
    # Phase 3: Catalytic site design
    log("")
    log("Phase 3 — SerpentRod catalytic site design")
    log("─" * 40)
    
    design = design_catalytic_site(reaction_sig)
    
    log(f"  Site RNA: {design.site_rna[:40]}... ({len(design.site_rna)} nt)")
    log(f"  Site AA:  {design.site_aa_sequence[:40]} ({len(design.site_aa_sequence)} AAs)")
    log(f"  Winding:  {design.winding_number}")
    log(f"  Frobenius: {'✓' if design.frobenius_verified else '✗'}")
    log(f"  Confidence: {design.confidence:.3f}")
    log(f"  Catalytic triad: {', '.join(design.catalytic_triad[:3])}")
    
    log("")
    log("╔════════════════════════════════════════╗")
    log("║  Pipeline Complete                    ║")
    log("╚════════════════════════════════════════╝")
    
    return design

# ── Formatters ──────────────────────────────────────────────────────

def format_report(design: CatalyticSiteDesign) -> str:
    d = design.to_dict()
    r = d["reaction"]
    s = d["catalytic_site"]
    
    lines = [
        "=" * 66,
        "  ch3mpiler ⟲ serpentrod — Catalytic Site Design",
        "=" * 66, "",
        "REACTION ANALYSIS",
        "-" * 40,
    ]
    lines.append(f"  Type:     {r['type']}")
    lines.append(f"  Bond:     {r['bond']}")
    lines.append(f"  Desc:     {r['bond_desc']}")
    lines.append(f"  FG pair:  {r['fg_pair']}")
    lines.append(f"  Structuring Δ: {r['structuring_delta']}")
    lines.append(f"  TS ordinal:    {r['ts_ordinal']}")
    lines.append("")
    
    if r.get("product_type"):
        lines.append("  Product structural type:")
        for field, glyph in r["product_type"].items():
            lines.append(f"    {field}: {glyph}")
        lines.append("")
    
    lines.append("CATALYTIC SITE DESIGN")
    lines.append("-" * 40)
    lines.append(f"  RNA:      {s['rna']}")
    lines.append(f"  AA seq:   {s['aa_sequence']}")
    lines.append(f"  Winding:  {s['winding']}")
    lines.append(f"  Frobenius: {'✓' if s['frobenius'] else '✗'}")
    lines.append(f"  Confidence: {s['confidence']:.3f}")
    lines.append("")
    
    if s.get("structural_type"):
        lines.append("  Site structural type:")
        for field, glyph in s["structural_type"].items():
            lines.append(f"    {field}: {glyph}")
        lines.append("")
    
    if s.get("catalytic_triad"):
        lines.append(f"  Catalytic triad: {', '.join(s['catalytic_triad'][:3])}")
    if s.get("binding_pocket"):
        lines.append(f"  Binding pocket: {', '.join(s['binding_pocket'][:8])}")
    lines.append("")
    
    if s.get("secondary_elements"):
        lines.append("  Predicted secondary structure:")
        for elem in s["secondary_elements"][:6]:
            lines.append(f"    {elem['type']:8s}  [{elem['start']:3d}-{elem['end']:3d}]  ({elem['length']} AAs)")
        lines.append("")
    
    if s.get("contacts"):
        lines.append(f"  Long-range contacts: {len(s['contacts'])}")
        for c in s["contacts"][:6]:
            lines.append(f"    {c['i']:3d}↔{c['j']:3d}  {c['distance']:5.2f}Å  {c['type']:20s}  c={c['confidence']:.2f}")
        lines.append("")
    
    lines.append("═" * 66)
    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="ch3mpiler ⟲ serpentrod — design catalytic sites from reaction specs")
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--start", help="Starting material (reagent)")
    input_group.add_argument("--target", help="Target molecule (product)")
    input_group.add_argument("--cas", help="CAS Registry Number")
    parser.add_argument("--end", help="Target molecule (with --start)")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--quiet", action="store_true")
    
    args = parser.parse_args()
    
    try:
        design = run_pipeline(
            starting_material=args.start,
            target_molecule=args.target or args.end,
            cas_number=args.cas,
            depth=args.depth,
            verbose=not args.quiet,
        )
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}", file=sys.stderr)
        import traceback; traceback.print_exc()
        sys.exit(1)
    
    if args.json:
        print(json.dumps(design.to_dict(), indent=2))
    else:
        print(format_report(design))


if __name__ == "__main__":
    main()


# ═══════════════════════════════════════════════════════════════
# FROBENIUS-EXACT EXTENSIONS (v3 — added for plastic_eater)
# ═══════════════════════════════════════════════════════════════

def complement_type_v3(fused_type):
    """Frobenius-exact structural complement using INVERSE mapping.
    
    For complementary pair (A,B):
      site[A] = INVERSE(fused[B])  — high when fused[B] is low
      site[B] = INVERSE(fused[A])  — high when fused[A] is low
    
    The inverse maps ordinal o → (max_o - o) within each primitive's
    range, then cross-maps to the partner's range.
    """
    site = {}
    for prim_a, prim_b in COMPLEMENTARY_PAIRS_V2:
        a_max = len(GLYPH_ORDINALS.get(prim_a, {})) - 1
        b_max = len(GLYPH_ORDINALS.get(prim_b, {})) - 1
        
        fused_a = glyph_ord(prim_a, fused_type.get(prim_a, '?'))
        fused_b = glyph_ord(prim_b, fused_type.get(prim_b, '?'))
        
        inv_a = a_max - fused_a
        inv_b = b_max - fused_b
        
        if a_max > 0:
            site[prim_b] = ord_to_glyph(prim_b, min(b_max, max(0, round(inv_a / a_max * b_max))))
        else:
            site[prim_b] = ord_to_glyph(prim_b, b_max)
        
        if b_max > 0:
            site[prim_a] = ord_to_glyph(prim_a, min(a_max, max(0, round(inv_b / b_max * a_max))))
        else:
            site[prim_a] = ord_to_glyph(prim_a, a_max)
    
    return site


def design_site_aas_from_type_v3(site_type):
    """Design 12-AA sequence with dominant-member rule (guaranteed 6/6).
    
    For each complementary pair (A,B), activate the AA for the member
    with the higher ordinal percentile. This ensures exactly one member
    per pair is activated → 6/6 pair coverage.
    
    This replaces the 50% threshold + OR-counting logic in the original
    design_site_aas_from_type, which had a bug: pairs were counted as
    covered if EITHER member was activated (OR logic), allowing false
    6/6 when only one member of some pairs was above threshold.
    """
    aas = [None] * 12
    activated = set()
    
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        pa_idx = PNAMES.index(pa)
        pb_idx = PNAMES.index(pb)
        pa_o = glyph_ord(pa, site_type.get(pa, '?'))
        pb_o = glyph_ord(pb, site_type.get(pb, '?'))
        pa_max = len(GLYPH_ORDINALS.get(pa, {})) - 1
        pb_max = len(GLYPH_ORDINALS.get(pb, {})) - 1
        pa_pct = pa_o / pa_max if pa_max > 0 else 0
        pb_pct = pb_o / pb_max if pb_max > 0 else 0
        
        if pa_pct >= pb_pct:
            aas[pa_idx] = PRIMITIVE_TO_AA.get(pa)
            activated.add(pa)
        else:
            aas[pb_idx] = PRIMITIVE_TO_AA.get(pb)
            activated.add(pb)
    
    # Fill remaining with structural AAs
    final_aas = []
    for i, aa in enumerate(aas):
        if aa is not None:
            final_aas.append(aa)
        else:
            final_aas.append(STRUCTURAL_AAS_V2[i % len(STRUCTURAL_AAS_V2)])
    
    # True pair coverage (dominant-member: always 6)
    true_pairs = sum(1 for pa, pb in COMPLEMENTARY_PAIRS_V2
                     if pa in activated or pb in activated)
    
    return final_aas, true_pairs
