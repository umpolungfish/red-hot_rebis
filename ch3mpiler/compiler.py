#!/usr/bin/env python3
"""ch3mpiler - IG-grounded retrosynthetic compiler using grammar-derived rules
of bond formation — NO named reactions.

Bond formation is modeled as: product_type = join(tensor(FG1, FG2), bond)
  - tensor: max on union primitives (D,T,R,K,G,Gm,Ph,H,S,W), min on P,F
  - join with bond: max on all primitives (bond provides a structural floor)
Disconnections are ranked by distance between predicted product type and
the molecule's catalog-verified type (or FG-composed type as fallback).

Author: Lando \u2297 \u2299perator
"""
import argparse, json, math, os, re, sys, urllib.request, urllib.error, time
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).parent.absolute()
CATALOG_PATH = BASE.parent / "shared" / "IG_catalog.json"
CAS_CACHE_PATH = BASE / "CAS_cache.json"
sys.path.insert(0, str(BASE.parent))

from shared.primitives import ORDINALS, WEIGHTS, resolve_ordinal_key
from shared.rich_output import *

# ── Exhaustive functional group database (SMARTS-based) ──
try:
    from fg_exhaustive import SMARTS_PATTERNS, FG_TUPLES as EXHAUSTIVE_FG_TUPLES, detect_functional_groups
    HAS_EXHAUSTIVE_FG = True
except ImportError:
    HAS_EXHAUSTIVE_FG = False
    EXHAUSTIVE_FG_TUPLES = {}

# ── CDXML generation (optional) ──
try:
    from cdxml_generator import generate_reaction_cdxml, nucleophilicity_score, electrophilicity_score
    HAS_CDXML = True
except ImportError:
    HAS_CDXML = False

# ── RDKit-based bond fragment integrator (real SMILES from bond cuts) ──
try:
    from bond_fragment_integrator import BondFragmentIntegrator, resolve_target_smiles
    HAS_FRAGMENT_INTEGRATOR = True
except ImportError:
    HAS_FRAGMENT_INTEGRATOR = False
    BondFragmentIntegrator = None
    resolve_target_smiles = lambda *a, **kw: None

# ── SMILES lookup for known molecules ──
SMILES_LOOKUP = {
    "benzaldehyde": "C1=CC=C(C=C1)C=O",
    "taxol": "CC1=C2C(C(=O)C3(C(CC4C(C3C(C(C2(C)C)(CC1OC(=O)C(C(C5=CC=CC=C5)NC(=O)C6=CC=CC=C6)O)O)OC(=O)C7=CC=CC=C7)(CO4)OC(=O)C)O)C)OC(=O)C",
    "baccatin_iii": "CC1=C2C(C(=O)C3(C(CC4C(C3C(C(C2(C)C)(CC1O)O)OC(=O)C5=CC=CC=C5)(CO4)OC(=O)C)O)C)OC(=O)C",
    "n_benzoyl_phenylisoserine": "C1=CC=C(C=C1)C(C(=O)O)NC(=O)C2=CC=CC=C2",
    "phenylisoserine_side_chain": "C1=CC=C(C=C1)C(C(=O)O)N",
    "acetic_acid": "CC(=O)O",
    "chiral_acetate": "CC(=O)[O-]",
    "benzophenone": "C1=CC=C(C=C1)C(=O)C2=CC=CC=C2",
    "acetophenone": "CC(=O)C1=CC=CC=C1",
    "methanol": "CO",
    "ethanol": "CCO",
    "water": "O",
    "phenol": "C1=CC=C(C=C1)O",
    "paracetamol": "CC(=O)NC1=CC=C(C=C1)O",
    "4_nitrophenol": "C1=CC(=CC=C1O)[N+](=O)[O-]",
    "4_aminophenol": "C1=CC(=CC=C1O)N",
    "toluene": "CC1=CC=CC=C1",
    "ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
    "isobutylbenzene": "CC(C)CC1=CC=CC=C1",
    "carboxylic_acid": "CC(=O)O",
    "benzene": "C1=CC=CC=C1",
    "aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "salicylic_acid": "C1=CC=C(C=C1)C(=O)O",
    "styrene": "C=CC1=CC=CC=C1",
    "ethylene": "C=C",
    "propene": "CC=C",
    "benzyl_alcohol": "C1=CC=C(C=C1)CO",
    "benzoic_acid": "C1=CC=C(C=C1)C(=O)O",
    "aniline": "C1=CC=C(C=C1)N",
    "nitrobenzene": "C1=CC=C(C=C1)[N+](=O)[O-]",
    "acetaminophen": "CC(=O)NC1=CC=C(C=C1)O",
    "resveratrol": "C1=CC(=CC=C1C=CC2=CC(=CC(=C2)O)O)O",
    "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
}

# ── Rich text formatting ──
try:
    STYLED = True
except ImportError:
    STYLED = False


def cascade_smiles(path, start_smi, smi_lookup):
    '''Cascade SMILES through multi-step paths: each product becomes next reactant.'''
    steps = []
    prev_smi = start_smi
    for i, step in enumerate(path):
        prod_name = step.get("product", "").lower().replace(" ", "_").replace("-", "_")
        prod_smi = smi_lookup.get(prod_name, "")
        steps.append({
            "step": step.get("step", i+1),
            "bond": step.get("bond", ""),
            "reaction": step.get("reaction", ""),
            "fg1": step.get("fg1", ""),
            "fg2": step.get("fg2", ""),
            "product": step.get("product", ""),
            "smiles_reactant": prev_smi,
            "smiles_product": prod_smi,
        })
        if prod_smi:
            prev_smi = prod_smi
    return steps



PNAMES = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
PFIELDS = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
FIELD_TO_ORD = {
    "D":"\u00D0", "T":"\u00de", "R":"\u0158", "P":"\u03a6", "F":"\u0192",
    "K":"\u00c7", "G":"\u0393", "Gm":"\u0262", "Ph":"\u2299", "H":"\u0126",
    "S":"\u03a3", "W":"\u03a9"
}

def g2v(p, r):
    """Primitive glyph → ordinal value."""
    if not r or r == '?':
        return '?', 0
    ord_key = FIELD_TO_ORD.get(p, p)
    om = ORDINALS.get(ord_key, {})
    if r in om:
        return r, om[r]
    try:
        k = resolve_ordinal_key(ord_key, r)
        return k, om[k]
    except Exception:
        return r, 0
def glyph_ord(p, glyph):
    _, o = g2v(p, glyph)
    return o

def ord_to_glyph(p, o):
    ord_key = FIELD_TO_ORD.get(p, p)
    om = ORDINALS.get(ord_key, {})
    rev = {v:k for k,v in om.items()}
    return rev.get(o, '?')

def fmt_tup(t):
    gs = []
    for p in PNAMES:
        v = t.get(p, "?")
        gs.append(v)
    return "<" + "; ".join(gs) + ">"

def tup_to_ords(t):
    """Convert glyph tuple dict to ordinal dict."""
    return {p: glyph_ord(p, t.get(p, "?")) for p in PNAMES}

def tup_dist(t1, t2):
    """Weighted Euclidean distance between two structural type dictionaries."""
    sq = 0.0; cf = []
    for p in PNAMES:
        v1 = t1.get(p, ""); v2 = t2.get(p, "")
        o1 = glyph_ord(p, v1); o2 = glyph_ord(p, v2)
        w = WEIGHTS.get(FIELD_TO_ORD.get(p, p), 1.0)
        d = (o1 - o2) * w; sq += d * d
        if o1 != o2:
            cf.append({"p": p, "a": v1, "b": v2, "d": o1 - o2})
    return math.sqrt(sq), cf

def tensor_type(t1, t2):
    """Grammar tensor: max on union primitives, min on P and F."""
    r = {}
    for p in PNAMES:
        o1, o2 = glyph_ord(p, t1.get(p,"?")), glyph_ord(p, t2.get(p,"?"))
        if p in ("P", "F"):
            r[p] = ord_to_glyph(p, min(o1, o2))
        else:
            r[p] = ord_to_glyph(p, max(o1, o2))
    return r

def join_type(t1, t2):
    """Grammar join: max on all primitives."""
    r = {}
    for p in PNAMES:
        o1, o2 = glyph_ord(p, t1.get(p,"?")), glyph_ord(p, t2.get(p,"?"))
        r[p] = ord_to_glyph(p, max(o1, o2))
    return r

def bond_product_type(fg1_type, fg2_type, bond_type):
    """Product type when FG1 and FG2 are connected by bond B.
    Formula: product = join(tensor(FG1, FG2), bond)
    """
    t = tensor_type(fg1_type, fg2_type)
    return join_type(t, bond_type)
# ====================================================================
# GLYPH REFERENCE MAP
# ====================================================================
GLYPH_MAP = {
    "\U0001045B": ("D",1), "\U00010468": ("D",2),
    "\U00010461": ("T",1), "\U00010470": ("T",2), "\U00010465": ("T",3), "\U00010478": ("T",5),
    "\U00010469": ("R",1), "\U00010451": ("R",2), "\U0001047D": ("R",3), "\U0001047E": ("R",4),
    "\U00010457": ("P",1), "\U0001047F": ("P",2), "\U0001046C": ("P",3), "\U0001046F": ("P",4), "\U00010479": ("P",5),
    "\U00010450": ("F",3), "\U0001045E": ("F",2), "\U00010471": ("F",1),
    "\U00010458": ("K",1), "\U00010464": ("K",2), "\U00010467": ("K",3), "\U0001047A": ("K",4), "\U0001046A": ("K",5),
    "\U0001045A": ("G",1), "\U00010454": ("G",2), "\U00010472": ("G",3),
    "\U0001045D": ("Ga",1), "\U0001045C": ("Ga",2), "\U00010460": ("Ga",3), "\U00010475": ("Ga",4),
    "\U00010462": ("Ph",1), "\u2299": ("Ph",2), "\U0001046E": ("Ph",3), "\U0001047B": ("Ph",4), "\U00010463": ("Ph",5),
    "\U00010452": ("H",2), "\U00010456": ("H",3), "\U00010453": ("H",1), "\U0001046B": ("H",4),
    "\U00010459": ("S",1), "\U00010455": ("S",2), "\U00010473": ("S",3),
    "\U00010477": ("W",1), "\U00010474": ("W",2), "\U0001046D": ("W",3), "\U0001045F": ("W",4),
}

# ====================================================================
# GRAMMAR-DERIVED BOND TYPES
# Each bond type encodes a DISTINCTIVE structural signature.
# The bond provides a FLOOR for the product type via join.
# Higher primitive values = more structural character added by the bond.
# ====================================================================

BOND_TYPES = {
    # σ single bond: simple localized connection between sp³ centers
    # Low values — doesn't add structure beyond connectivity
    "sigma_single": {
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
        "desc":"σ single bond (localized, sp³-sp³)"
    },
    # π bond: p-orbital overlap, adds 2D character and quantum coherence
    "pi_bond": {
        "D":"\U00010468","T":"\U00010470","R":"\U0001047D",
        "P":"\U0001046F","F":"\U00010471","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
        "desc":"π bond (p-orbital overlap, quantum coherent)"
    },
    # C=C double bond: σ+π, adds planarity and restricted rotation
    "double_bond": {
        "D":"\U00010468","T":"\U00010465","R":"\U0001047E",
        "P":"\U0001046F","F":"\U00010450","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
        "desc":"C=C double bond (planar, σ+π)"
    },
    # C≡C triple bond: σ+2π, linear geometry
    "triple_bond": {
        "D":"\U00010468","T":"\U00010470","R":"\U0001047E",
        "P":"\U0001046F","F":"\U00010471","K":"\U00010458",
        "G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
        "desc":"C≡C triple bond (linear, σ+2π)"
    },
    # Carbonyl C=O: polarized, reaction hub, critical
    "carbonyl": {
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047D",
        "P":"\U0001046F","F":"\U00010450","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
        "desc":"C=O carbonyl (polarized, reaction hub)"
    },
    # C-O single bond: polar, lower symmetry
    "co_sigma": {
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
        "desc":"C-O σ bond (polar, ether/alcohol)"
    },
    # C-N single bond: polar, nitrogen lone pair
    "cn_sigma": {
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010458",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
        "desc":"C-N σ bond (polar, amine)"
    },
    # Amide: conjugated, planar, high chirality
    "amide_link": {
        "D":"\U00010468","T":"\U00010465","R":"\U0001047E",
        "P":"\U0001046C","F":"\U00010450","K":"\U00010467",
        "G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U00010474",
        "desc":"Amide C(=O)-N (conjugated, planar)"
    },
    # Ester: polarized, resonance-stabilized
    "ester_link": {
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047D",
        "P":"\U0001046F","F":"\U00010450","K":"\U00010467",
        "G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010473","W":"\U00010474",
        "desc":"Ester C(=O)-O (resonance-stabilized)"
    },
    # Aromatic: delocalized, high symmetry, topological
    "aromatic": {
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E",
        "P":"\U00010479","F":"\U00010450","K":"\U00010467",
        "G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
        "desc":"Aromatic delocalized (cyclic π, Z₃)"
    },
    # Hydrogen bond: intermolecular, weak
    "hydrogen_bond": {
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010458",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
        "desc":"H-bond (intermolecular, electrostatic)"
    },
    # Ether C-O-C: bent, polar
    "ether_link": {
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451",
        "P":"\U00010457","F":"\U0001045E","K":"\U00010464",
        "G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
        "desc":"C-O-C ether (bent, polar)"
    },
    # Strain-release: ring-opening of strained 3/4-membered ring
    # High T (strain topology) + max K (strain energy drives opening)
    "strain_release": {
        "D":"𐑛","T":"𐑶","R":"𐑑",
        "P":"𐑿","F":"𐑐","K":"𐑺",
        "G":"𐑚","Gm":"𐑝","Ph":"⊙",
        "H":"𐑒","S":"𐑳","W":"𐑭",
        "desc":"Strain-release ring opening (3/4-membered)"
    },
    # Cage C-C: bridged polycyclic σ bond (adamantane/cubane/norbornane)
    # Matches cage_alkane exactly: H=𐑓 (achiral cage vertex), W=𐑟 (fully wound)
    "cage_bond": {
        "D":"𐑨","T":"𐑸","R":"𐑾",
        "P":"𐑯","F":"𐑐","K":"𐑧",
        "G":"𐑲","Gm":"𐑠","Ph":"⊙",
        "H":"𐑓","S":"𐑳","W":"𐑟",
        "desc":"Cage C-C bond (bridged polycyclic, sp3)"
    },
    # Dative/coordinate bond: metal-ligand η coordination
    # D=𐑦 (full 3D), Gm=𐑵 (maximum coupling), Ph=𐑣 (maximum criticality)
    "dative_bond": {
        "D":"𐑦","T":"𐑸","R":"𐑾",
        "P":"𐑯","F":"𐑐","K":"𐑤",
        "G":"𐑲","Gm":"𐑵","Ph":"𐑣",
        "H":"𐑓","S":"𐑳","W":"𐑟",
        "desc":"Dative/coordinate bond (metal-ligand η)"
    },
}
# ====================================================================
# FUNCTIONAL GROUP TYPES (IG structural encodings)
# ====================================================================
FG = {
    "alcohol": {"D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U00010457","F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "carbonyl": {"D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "aldehyde": {"D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "ketone": {"D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "carboxylic_acid": {"D":"\U0001045B","T":"\U00010465","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010452","S":"\U00010473","W":"\U00010477"},
    "ester": {"D":"\U0001045B","T":"\U00010465","R":"\U0001047D","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010452","S":"\U00010473","W":"\U00010477"},
    "amide": {"D":"\U0001045B","T":"\U00010465","R":"\U0001047D","P":"\U0001046C","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U00010474"},
        "alkane": {"D":"𐑛","T":"𐑡","R":"𐑑","P":"𐑗","F":"𐑐","K":"𐑧","G":"𐑚","Gm":"𐑝","Ph":"𐑢","H":"𐑒","S":"𐑳","W":"𐑷"},
    "amine": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450","K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    "aniline": {"D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U0001046D"},
    "ether": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010453","S":"\U00010459","W":"\U00010477"},
    "nitrile": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010474"},
    "halide": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450","K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010453","S":"\U00010459","W":"\U00010477"},
    "alkene": {"D":"\U0001045B","T":"\U00010461","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010464","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010474"},
    "alkyne": {"D":"\U0001045B","T":"\U00010461","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010474"},
    "aromatic_ring": {"D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U00010479","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U0001046D"},
    "phenol": {"D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450","K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299","H":"\U00010456","S":"\U00010473","W":"\U0001046D"},
    "epoxide": {"D":"\U00010468","T":"\U00010470","R":"\U00010451","P":"\U0001046F","F":"\U00010450","K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299","H":"\U00010452","S":"\U00010459","W":"\U00010474"},
    "thiol": {"D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U0001045E","K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462","H":"\U00010452","S":"\U00010459","W":"\U00010477"},
    # ── Fused N-heterocycle primitives ──────────────────────────────────────
    # imidazole: 5-membered aromatic N-heterocycle with N-H tautomerism
    #   T=𐑥 fused/heterocyclic topology  R=𐑾 bidirectional (N1-H↔N3-H tautomers)
    #   P=𐑗 minimal (odd-electron heterocycle)  W=𐑴 partial winding
    "imidazole": {"D":"𐑛","T":"𐑥","R":"𐑾","P":"𐑗","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑖","S":"𐑳","W":"𐑴"},
    # lactam: cyclic amide (N-containing ring closed by C=O)
    #   T=𐑥 fused topology  R=𐑽 recognition (ring-constrained, not full tautomeric)
    #   P=𐑗 minimal parity  W=𐑴 partial winding
    "lactam": {"D":"𐑛","T":"𐑥","R":"𐑽","P":"𐑗","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑖","S":"𐑳","W":"𐑴"},
    # ── Strained small rings ────────────────────────────────────────────────
    # aziridine: 3-membered N-ring (angle strain + nucleophilic N, SN2 opening)
    #   T=𐑶 strain topology  K=𐑺 max kinetics (strain-driven)
    #   H=𐑒 chirality at N  W=𐑭 wound by ring closure
    "aziridine": {"D":"𐑛","T":"𐑶","R":"𐑑","P":"𐑿","F":"𐑐","K":"𐑺","G":"𐑚","Gm":"𐑝","Ph":"⊙","H":"𐑒","S":"𐑳","W":"𐑭"},
    # beta_lactam: 4-membered cyclic amide (antibiotic pharmacophore)
    #   T=𐑶 4-ring strain  K=𐑺 max kinetics (acylation of β-lactamase)
    #   H=𐑖 chirality at C4  R=𐑽 constrained β-lactamase recognition
    "beta_lactam": {"D":"𐑛","T":"𐑶","R":"𐑽","P":"𐑿","F":"𐑐","K":"𐑺","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑖","S":"𐑳","W":"𐑭"},
    # cyclopropane: 3-membered C-ring (bent bonds / Walsh orbitals)
    #   T=𐑶 strain topology  R=𐑾 Walsh orbitals = bidirectional e- donation
    #   K=𐑧 moderate (activation needed for strain release)  W=𐑭 wound
    "cyclopropane": {"D":"𐑛","T":"𐑶","R":"𐑾","P":"𐑗","F":"𐑐","K":"𐑧","G":"𐑚","Gm":"𐑝","Ph":"⊙","H":"𐑓","S":"𐑙","W":"𐑭"},
    # oxetane: 4-membered O-ring (ring strain + ether-like reactivity)
    #   T=𐑶 4-ring topology  K=𐑪 reactive (acid-catalyzed opening)
    "oxetane": {"D":"𐑛","T":"𐑶","R":"𐑑","P":"𐑿","F":"𐑐","K":"𐑪","G":"𐑚","Gm":"𐑝","Ph":"⊙","H":"𐑓","S":"𐑕","W":"𐑭"},
    # ── Cage and polyhedral carbons ─────────────────────────────────────────
    # cage_alkane: bridged polycyclic cage (adamantane/norbornane/cubane family)
    #   T=𐑸 maximum cage topology  P=𐑯 high symmetry/parity
    #   R=𐑾 bidirectional (cage bonds equivalent by symmetry)  W=𐑟 fully wound
    "cage_alkane": {"D":"𐑨","T":"𐑸","R":"𐑾","P":"𐑯","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑓","S":"𐑳","W":"𐑟"},
    # ── Axial chirality / cumulated bonds ───────────────────────────────────
    # allene: cumulated C=C=C (axial chirality, linear sp carbon center)
    #   H=𐑫 MAXIMUM chirality (axial)  R=𐑾 cumulated π = bidirectional
    #   K=𐑪 reactive toward cycloaddition  W=𐑴 partial winding
    "allene": {"D":"𐑨","T":"𐑡","R":"𐑾","P":"𐑿","F":"𐑐","K":"𐑪","G":"𐑚","Gm":"𐑝","Ph":"⊙","H":"𐑫","S":"𐑙","W":"𐑴"},
    # ── Organometallic ──────────────────────────────────────────────────────
    # metallocene: sandwich η5 complex (ferrocene, Cp2M)
    #   D=𐑦 full 3D dimensionality  T=𐑸 maximum sandwich topology
    #   Gm=𐑵 maximum coupling (metal-π)  Ph=𐑣 maximum criticality
    "metallocene": {"D":"𐑦","T":"𐑸","R":"𐑾","P":"𐑯","F":"𐑐","K":"𐑤","G":"𐑲","Gm":"𐑵","Ph":"𐑣","H":"𐑓","S":"𐑳","W":"𐑟"},
    # ── Spherical carbon ────────────────────────────────────────────────────
    # fullerene: spherical all-carbon cage (C60/C70)
    #   P=𐑹 MAXIMUM parity (icosahedral Oh symmetry)  K=𐑺 strong e- acceptor
    #   Ph=𐑣 maximum criticality  Gm=𐑵 maximum π coupling
    "fullerene": {"D":"𐑨","T":"𐑸","R":"𐑾","P":"𐑹","F":"𐑐","K":"𐑺","G":"𐑲","Gm":"𐑵","Ph":"𐑣","H":"𐑓","S":"𐑳","W":"𐑟"},
    # ── Spirocyclic ─────────────────────────────────────────────────────────
    # spirocycle: two rings sharing one spiro carbon (orthogonal ring planes)
    #   H=𐑖 chirality at spiro center  R=𐑽 constrained recognition
    "spirocycle": {"D":"𐑛","T":"𐑥","R":"𐑽","P":"𐑿","F":"𐑐","K":"𐑧","G":"𐑚","Gm":"𐑜","Ph":"⊙","H":"𐑖","S":"𐑕","W":"𐑭"},
    # ── Macrocyclic ─────────────────────────────────────────────────────────
    # macrolide: large ring lactone (>8-membered, macrolide antibiotics)
    #   D=𐑨 extended chain  R=𐑾 conformational flexibility = bidirectional recognition
    #   P=𐑗 minimal (flexible, no rigid parity)  W=𐑭 wound by macrocycle
    "macrolide": {"D":"𐑨","T":"𐑥","R":"𐑾","P":"𐑗","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑒","S":"𐑳","W":"𐑭"},
    # ── Non-benzenoid aromatics ─────────────────────────────────────────────
    # tropolone: 7-membered aromatic ring with C=O and enol tautomerism
    #   T=𐑸 max topology (non-benzenoid aromatic, unusual ring size)
    #   R=𐑾 bidirectional (C-OH ↔ C=O tautomeric exchange)  P=𐑯 unusual parity
    "tropolone": {"D":"𐑛","T":"𐑸","R":"𐑾","P":"𐑯","F":"𐑐","K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙","H":"𐑒","S":"𐑳","W":"𐑭"},
}


# Auto-extend FG table with exhaustive SMARTS-based FGs
if HAS_EXHAUSTIVE_FG:
    FG.update(EXHAUSTIVE_FG_TUPLES)
    FG_detect = staticmethod(detect_functional_groups)

FG_TOKENS = {
    # ── Heterocycles (BEFORE short tokens — length-prioritized) ──
    "dihydroimidazol":"aromatic_ring", "imidazolidin":"aromatic_ring",
    "dihydrooxazol":"aromatic_ring", "oxazolidin":"aromatic_ring",
    "dihydrothiazol":"aromatic_ring", "thiazolidin":"aromatic_ring",
    "tetrahydroisoquinolin":"aromatic_ring", "tetrahydroquinolin":"aromatic_ring",
    "dihydroindol":"aromatic_ring",
    "isoquinolin":"aromatic_ring", "quinazolin":"aromatic_ring",
    "quinoxalin":"aromatic_ring", "cinnolin":"aromatic_ring",
    "phthalazin":"aromatic_ring", "quinolin":"aromatic_ring",
    "benzimidazol":"aromatic_ring", "benzothiazol":"aromatic_ring",
    "benzoxazol":"aromatic_ring", "benzofuran":"aromatic_ring",
    "benzothiophen":"aromatic_ring", "carbazol":"aromatic_ring",
    "acridin":"aromatic_ring", "phenanthridin":"aromatic_ring",
    "phenazin":"aromatic_ring", "phenothiazin":"aromatic_ring",
    "phenoxazin":"aromatic_ring",
    "indolizin":"aromatic_ring", "indol":"aromatic_ring",
    "pyrrolizin":"aromatic_ring", "pyrrol":"aromatic_ring",
    "imidazol":"aromatic_ring", "pyrazol":"aromatic_ring",
    "triazol":"aromatic_ring", "tetrazol":"aromatic_ring",
    "thiazol":"aromatic_ring", "oxazol":"aromatic_ring",
    "isoxazol":"aromatic_ring", "isothiazol":"aromatic_ring",
    "oxadiazol":"aromatic_ring", "thiadiazol":"aromatic_ring",
    "pyridin":"aromatic_ring", "pyrimidin":"aromatic_ring",
    "pyrazin":"aromatic_ring", "pyridazin":"aromatic_ring",
    "triazin":"aromatic_ring", "tetrazin":"aromatic_ring",
    "thiophen":"aromatic_ring", "furan":"aromatic_ring",
    "selenophen":"aromatic_ring", "tellurophen":"aromatic_ring",
    "purin":"aromatic_ring", "pteridin":"aromatic_ring",
    "flavin":"aromatic_ring", "phenanthrolin":"aromatic_ring",
    "naphthyridin":"aromatic_ring", "chromen":"aromatic_ring",
    "coumarin":"aromatic_ring", "flavon":"aromatic_ring",
    "xanthen":"aromatic_ring", "acridon":"aromatic_ring",
    "porphyrin":"aromatic_ring", "chlorin":"aromatic_ring",
    "corrin":"aromatic_ring", "phthalocyanin":"aromatic_ring",
    # ── Amine side chains ──
    "ethanamine":"amine", "ethylamine":"amine",
    "propanamine":"amine", "propylamine":"amine",
    "butanamine":"amine", "butylamine":"amine",
    "pentanamine":"amine", "pentylamine":"amine",
    "hexanamine":"amine", "hexylamine":"amine",
    "methanamine":"amine", "methylamine":"amine",
    "tryptamine":"amine",
    "phenethylamine":"amine",
    # ── Common aromatic names (prevent "ene"→alkene misfire) ──
    "naphthalene":"aromatic_ring", "anthracene":"aromatic_ring",
    "phenanthrene":"aromatic_ring", "pyrene":"aromatic_ring",
    "chrysene":"aromatic_ring", "tetracene":"aromatic_ring",
    "pentacene":"aromatic_ring", "coronene":"aromatic_ring",
    "perylene":"aromatic_ring", "triphenylene":"aromatic_ring",
    "fluoranthene":"aromatic_ring", "benzene":"aromatic_ring",
    "toluene":"aromatic_ring", "xylene":"aromatic_ring",
    "mesitylene":"aromatic_ring", "styrene":"aromatic_ring",
    "azulene":"aromatic_ring", "fulvene":"aromatic_ring",
    "biphenylene":"aromatic_ring", "acenaphthene":"aromatic_ring",
    "fluorene":"aromatic_ring", "indene":"aromatic_ring",
    "thiophene":"aromatic_ring", "selenophene":"aromatic_ring",
    "tellurophene":"aromatic_ring", "furan":"aromatic_ring",
    "dibenzofuran":"aromatic_ring", "dibenzothiophene":"aromatic_ring",
    "carbazole":"aromatic_ring", "dibenzopyrrole":"aromatic_ring",
    "acridine":"aromatic_ring", "phenazine":"aromatic_ring",
    "phenoxazine":"aromatic_ring", "phenothiazine":"aromatic_ring",
    # ── Standard tokens (kept from original) ──
    "alcohol":"alcohol","ol":"alcohol","hydroxy":"alcohol","hydroxyl":"alcohol",
    "carbonyl":"carbonyl","oxo":"carbonyl",
    "aldehyde":"aldehyde","al":"aldehyde",
    "ketone":"ketone","one":"ketone","keto":"ketone",
    "acid":"carboxylic_acid","carboxy":"carboxylic_acid","oic":"carboxylic_acid","oate":"carboxylic_acid",
    "ester":"ester",
    "amide":"amide","amido":"amide",
    "amine":"amine","amino":"amine","aza":"amine",
    "ether":"ether","oxy":"ether","methoxy":"ether","ethoxy":"ether",
    "nitrile":"nitrile","cyano":"nitrile",
    "halide":"halide","chloro":"halide","bromo":"halide","fluoro":"halide","iodo":"halide",
    "alkene":"alkene","ene":"alkene","vinyl":"alkene",
    "alkane":"alkane","ane":"alkane",
    "alkyne":"alkyne","yne":"alkyne","acetylene":"alkyne",
    "benz":"aromatic_ring","phenyl":"aromatic_ring","aryl":"aromatic_ring",
    "phenol":"phenol","hydroxybenz":"phenol",
    "diazonium":"diazonium","diazo":"diazonium",
    "nitro":"nitro","nitroso":"nitro",
    "epoxide":"epoxide","oxirane":"epoxide",
    "thiol":"thiol","sulfanyl":"thiol",
    "cyclo":"cyclic","cyclohex":"cyclic","cyclopent":"cyclic",
    # ── Fused N-heterocycles ─────────────────────────────────────────────
    "lactam":"lactam","pyrrolidinon":"lactam","piperidinon":"lactam",
    "caprolactam":"lactam","valerolactam":"lactam","butyrolactam":"lactam",
    "imidazole":"imidazole","imidazolin":"imidazole",
    # ── Strained ring tokens ─────────────────────────────────────────────
    "aziridine":"aziridine","aziridin":"aziridine","ethyleneimine":"aziridine",
    "beta_lactam":"beta_lactam","betalactam":"beta_lactam",
    "azetidinon":"beta_lactam","penam":"beta_lactam",
    "penicill":"beta_lactam","cephalospor":"beta_lactam",
    "cyclopropane":"cyclopropane","cyclopropyl":"cyclopropane",
    "cyclopropan":"cyclopropane",
    "oxetane":"oxetane","oxetan":"oxetane",
    # ── Cage alkane tokens ───────────────────────────────────────────────
    "adamantane":"cage_alkane","adamantyl":"cage_alkane",
    "norbornane":"cage_alkane","norbornyl":"cage_alkane","norbornan":"cage_alkane",
    "cubane":"cage_alkane","cubyl":"cage_alkane",
    "diamondoid":"cage_alkane","twistan":"cage_alkane",
    # ── Allene / axial chirality ─────────────────────────────────────────
    "allene":"allene","allenyl":"allene","cumulene":"allene",
    "propadiene":"allene",
    # ── Organometallic ───────────────────────────────────────────────────
    "ferrocene":"metallocene","metallocen":"metallocene",
    "ruthenocene":"metallocene","osmocene":"metallocene",
    "titanocene":"metallocene","zirconocene":"metallocene",
    # ── Fullerene ────────────────────────────────────────────────────────
    "fullerene":"fullerene","buckminster":"fullerene","buckyball":"fullerene",
    # ── Spirocycle ───────────────────────────────────────────────────────
    "spirocycl":"spirocycle","spiro[":"spirocycle",
    # ── Macrolide ────────────────────────────────────────────────────────
    "macrolide":"macrolide","erythromycin":"macrolide",
    "azithromycin":"macrolide","rapamycin":"macrolide","sirolimus":"macrolide",
    # ── Tropolone / non-benzenoid ────────────────────────────────────────
    "tropolone":"tropolone","tropone":"tropolone","colchicin":"tropolone",
    "thujaplicin":"tropolone","hinokitiol":"tropolone",
}

# ====================================================================
# GRAMMAR-DERIVED DISCONNECTION ENGINE
# Product type = join(tensor(FG1, FG2), bond_type)
# Disconnection delta = distance(molecule_type, product_type)
# ====================================================================

def compose_molecule_type(fg_names):
    """Compose molecule type from its functional groups via tensor product."""
    result = None
    for fg in sorted(fg_names):
        fg_t = FG.get(fg, {})
        if not fg_t:
            continue
        if result is None:
            result = dict(fg_t)
        else:
            result = tensor_type(result, fg_t)
    return result if result else {}

def get_molecule_type(name, catalog):
    """Get molecule type: from catalog if available, else compose from FGs."""
    for e in catalog:
        if e.get("name", "").lower() == name.lower():
            t = {}
            for pn, pf in zip(PNAMES, PFIELDS):
                v = e.get(pf, "")
                if v:
                    t[pn] = v
            if len(t) == 12:
                return t, "catalog"
    # Fallback: use find_fgs which checks MOLECULE_FG_DB first, then FG_TOKENS
    fgs_found = find_fgs(name)
    if fgs_found:
        return compose_molecule_type(fgs_found), "composed"
    return {}, "none"

# Name-to-FG lookup from molecule database (built from local CAS DB + catalog)
# Name-to-FG lookup — direct mapping from molecule names to functional groups
MOLECULE_FG_DB = {
    "aspirin": ["ester", "carboxylic_acid", "aromatic_ring"],
    "paracetamol": ["amide", "phenol"],
    "acetaminophen": ["amide", "phenol"],
    "thc": ["phenol", "alkene", "ether", "cyclic"],
    "cannabidiol": ["phenol", "alkene", "cyclic"],
    "caffeine": ["imidazole", "lactam"],
    "theophylline": ["imidazole", "lactam"],
    "theobromine": ["imidazole", "lactam"],
    "xanthine": ["imidazole", "lactam"],
    "hypoxanthine": ["imidazole", "lactam"],
    "adenine": ["imidazole", "lactam"],
    "guanine": ["imidazole", "lactam"],
    "uric_acid": ["imidazole", "lactam"],
    "ibuprofen": ["carboxylic_acid", "aromatic_ring"],
    "naproxen": ["carboxylic_acid", "ether", "aromatic_ring"],
    "morphine": ["amine", "alcohol", "ether", "aromatic_ring"],
    "codeine": ["amine", "alcohol", "ether", "aromatic_ring"],
    "nicotine": ["amine", "cyclic", "aromatic_ring"],
    "glucose": ["alcohol", "ether", "aldehyde"],
    "fructose": ["alcohol", "ether", "ketone"],
    "sucrose": ["alcohol", "ether"],
    "benzaldehyde": ["aldehyde", "aromatic_ring"],
    "aniline": ["amine", "aromatic_ring"],
    "toluene": ["aromatic_ring"],
    "nitrobenzene": ["nitro", "aromatic_ring"],
    "chlorobenzene": ["halide", "aromatic_ring"],
    "acetophenone": ["ketone", "aromatic_ring"],
    "benzonitrile": ["nitrile", "aromatic_ring"],
    "anisole": ["ether", "aromatic_ring"],
    "styrene": ["alkene", "aromatic_ring"],
    "acrylonitrile": ["alkene", "nitrile"],
    "ethylene": ["alkene"],
    "acetylene": ["alkyne"],
    "cyclohexane": ["cyclic"],
    "phenol": ["phenol"],
    "benzene": ["aromatic_ring"],
    "ethylbenzene": ["aromatic_ring"],
    "triethylamine": ["amine"],
    "propionic acid": ["carboxylic_acid"],
    "acetic acid": ["carboxylic_acid"],
    "salicylic acid": ["carboxylic_acid", "phenol"],
    "picric acid": ["phenol", "nitro"],
    "2-acetoxybenzoic acid": ["ester", "carboxylic_acid", "aromatic_ring"],
    "11-hydroxy-δ9-tetrahydrocannabinol": ["phenol", "alcohol", "alkene", "ether", "cyclic"],
    "4-methyl-5-phenyl-4,5-dihydro-1,3-oxazol-2-amine": ["amine", "aromatic_ring", "ether", "cyclic"],
    "tryptamine": ["amine", "aromatic_ring", "cyclic"],
    "dimethyltryptamine": ["amine", "aromatic_ring", "cyclic"],
    "5-methoxy-dimethyltryptamine": ["amine", "aromatic_ring", "ether", "cyclic"],
    "serotonin": ["amine", "phenol", "aromatic_ring", "cyclic"],
    "melatonin": ["amide", "ether", "aromatic_ring", "cyclic"],
    "psilocybin": ["amine", "phosphate", "aromatic_ring", "cyclic"],
    "psilocin": ["amine", "phenol", "aromatic_ring", "cyclic"],
    "ibogaine": ["amine", "ether", "aromatic_ring", "cyclic"],
    "harmaline": ["amine", "ether", "aromatic_ring", "cyclic"],
    "harmine": ["amine", "ether", "aromatic_ring", "cyclic"],
    "yohimbine": ["amine", "ester", "aromatic_ring", "cyclic"],
    "reserpine": ["amine", "ester", "ether", "aromatic_ring", "cyclic"],
    "quinine": ["amine", "alcohol", "ether", "aromatic_ring", "cyclic"],
    "quinidine": ["amine", "alcohol", "ether", "aromatic_ring", "cyclic"],
    "strychnine": ["amine", "amide", "ether", "aromatic_ring", "cyclic"],
    "brucine": ["amine", "amide", "ether", "aromatic_ring", "cyclic"],
    "lysergic_acid": ["amine", "carboxylic_acid", "aromatic_ring", "cyclic"],
    "lsd": ["amine", "amide", "aromatic_ring", "cyclic"],
    "cocaine": ["amine", "ester", "aromatic_ring", "cyclic"],
    "heroin": ["amine", "ester", "ether", "aromatic_ring", "cyclic"],
    "dopamine": ["amine", "phenol", "aromatic_ring"],
    "norepinephrine": ["amine", "alcohol", "phenol", "aromatic_ring"],
    "epinephrine": ["amine", "alcohol", "phenol", "aromatic_ring"],
    "histamine": ["amine", "aromatic_ring"],
    "gramine": ["amine", "aromatic_ring", "cyclic"],
    "bufotenin": ["amine", "phenol", "aromatic_ring", "cyclic"],
    "cubane": ["cage_alkane"],
    "pentacyclo": ["cage_alkane"],
    # ── Strained small rings ──────────────────────────────────────────────
    "aziridine": ["aziridine"],
    "ethyleneimine": ["aziridine"],
    "2_methylaziridine": ["aziridine"],
    "oxetane": ["oxetane"],
    "beta_propiolactone": ["oxetane", "ester"],
    "beta_lactam": ["beta_lactam"],
    "penicillin_g": ["beta_lactam", "thiol", "amide", "carboxylic_acid"],
    "ampicillin": ["beta_lactam", "amine", "amide", "carboxylic_acid"],
    "amoxicillin": ["beta_lactam", "amine", "amide", "carboxylic_acid", "phenol"],
    "cephalosporin_c": ["beta_lactam", "amide", "carboxylic_acid", "alkene"],
    # ── Strained C3 ───────────────────────────────────────────────────────
    "cyclopropane": ["cyclopropane"],
    "cyclopropanol": ["cyclopropane", "alcohol"],
    "cyclopropanone": ["cyclopropane", "ketone"],
    "chrysanthemum_acid": ["cyclopropane", "alkene", "carboxylic_acid"],
    "permethrin": ["cyclopropane", "ester", "halide", "aromatic_ring"],
    # ── Cage/bridged ──────────────────────────────────────────────────────
    "adamantane": ["cage_alkane"],
    "norbornane": ["cage_alkane"],
    "norbornene": ["cage_alkane", "alkene"],
    "bicyclo_1_1_1_pentane": ["cage_alkane", "cyclopropane"],
    "bcp": ["cage_alkane", "cyclopropane"],
    "diamondoid": ["cage_alkane"],
    # ── Allene / axial chirality ──────────────────────────────────────────
    "allene": ["allene"],
    "propadiene": ["allene"],
    "spiropentane": ["spirocycle", "cyclopropane"],
    # ── Organometallic ────────────────────────────────────────────────────
    "ferrocene": ["metallocene", "aromatic_ring"],
    "ruthenocene": ["metallocene", "aromatic_ring"],
    "osmocene": ["metallocene", "aromatic_ring"],
    "decamethylferrocene": ["metallocene", "aromatic_ring"],
    "ferricinium": ["metallocene", "aromatic_ring"],
    # ── Fullerene ─────────────────────────────────────────────────────────
    "buckminsterfullerene": ["fullerene"],
    "c60": ["fullerene"],
    "c70": ["fullerene"],
    "fullerene": ["fullerene"],
    "pcbm": ["fullerene", "ester", "aromatic_ring"],
    # ── Spirocyclic ───────────────────────────────────────────────────────
    "spiro_4_5_decane": ["spirocycle"],
    "griseofulvin": ["spirocycle", "ether", "ketone", "aromatic_ring"],
    "2_oxa_6_azaspiro_3_3_heptane": ["spirocycle", "aziridine", "oxetane"],
    # ── Macrolide antibiotics ─────────────────────────────────────────────
    "erythromycin": ["macrolide", "ether", "amine", "alcohol"],
    "azithromycin": ["macrolide", "ether", "amine", "alcohol"],
    "rapamycin": ["macrolide", "ether", "amide", "alkene"],
    "sirolimus": ["macrolide", "ether", "amide", "alkene"],
    "cyclosporin": ["macrolide", "amide"],
    "epothilone": ["macrolide", "ester", "alkene", "epoxide"],
    # ── Tropolone / non-benzenoid aromatics ───────────────────────────────
    "tropolone": ["tropolone"],
    "colchicine": ["tropolone", "amide", "ether"],
    "hinokitiol": ["tropolone", "alcohol"],
    "beta_thujaplicin": ["tropolone", "alcohol"],
    "p-phenylenediamine": ["amine", "aromatic_ring"],
    "3,4-dichloroaniline": ["halide", "amine", "aromatic_ring"],
}

def find_fgs(name):
    """Extract functional groups from molecule name.
    
    Collects ALL functional groups from ALL matching sources.
    Priority order (all sources contribute; tokens collected cumulatively):
    1. Molecule name lookup (MOLECULE_FG_DB) — exact or substring
    2. Substring token matching (FG_TOKENS)
    
    Returns UNION of all matched FGs, deduplicated and sorted.
    """
    name_lower = name.lower().replace("_", " ").replace("-", " ").strip()
    found = set()
    
    # Build normalized DB for hyphen-insensitive lookup
    _norm = lambda s: s.lower().replace('_',' ').replace('-',' ').strip()
    _norm_db = {_norm(k): v for k, v in MOLECULE_FG_DB.items()}

    # Step 1: Exact match in molecule name DB (hyphen-insensitive)
    if name_lower in _norm_db:
        found.update(_norm_db[name_lower])
        # Still fall through to token matching to catch additional FGs
        # that might not be in the DB entry

    # Step 2: Collect ALL matching DB entries (not just first)
    # Sort by length descending but collect ALL matches
    for db_name in sorted(_norm_db.keys(), key=len, reverse=True):
        if db_name in name_lower:
            found.update(_norm_db[db_name])
    
    # Step 3: Token matching — collect ALL matching tokens
    # Use word-aware matching: a token only matches if it appears
    # as a whole-word fragment, avoiding spurious substring matches
    # like "ol" in "indole" being misread as alcohol.
    matched_tokens = set()
    for token in sorted(FG_TOKENS.keys(), key=len, reverse=True):
        if token in name_lower:
            # For short tokens (<=3 chars), require word-boundary context
            # to avoid spurious matches like "ol" in "indole"
            if len(token) <= 3:
                # Check that token appears at a word boundary.
                # Primary check: token must END at a word boundary (after_ok).
                # Secondary (subsumption): don't match if a longer token already
                # covered this position (e.g. "indol" already matched → skip "ol").
                idx = name_lower.find(token)
                while idx != -1:
                    # Check character after (or end of string) — token must end at boundary
                    after_ok = (idx + len(token) == len(name_lower) or
                               name_lower[idx + len(token)] in ' ()[]{}.,;:-' or
                               name_lower[idx + len(token)].isdigit())
                    if after_ok:
                        # Check: is this token already subsumed by a longer
                        # token that matched? E.g. "indole" already matched, so
                        # don't also match "ol" -> "alcohol" for the same position
                        subsumed = False
                        for longer in matched_tokens:
                            if len(longer) > len(token) and token in longer:
                                # Check if the longer match overlaps this position
                                longer_idx = name_lower.find(longer)
                                if longer_idx <= idx <= longer_idx + len(longer):
                                    subsumed = True
                                    break
                        if not subsumed:
                            found.add(FG_TOKENS[token])
                        break
                    idx = name_lower.find(token, idx + 1)
            else:
                found.add(FG_TOKENS[token])
                matched_tokens.add(token)
    
    return sorted(found)


# ── RDKit-based FG detection from SMILES (fallback when name doesn't resolve) ──
RDKIT_FG_SMARTS = [
    ("aromatic_ring", "[a]"),
    ("alcohol", "[OX2H]"),
    ("phenol", "[OX2H]c"),
    ("carbonyl", "[CX3]=[OX1]"),
    ("carboxylic_acid", "[CX3](=O)[OX2H]"),
    ("ester", "[CX3](=O)[OX2][#6]"),
    ("ether", "[OX2]([#6])[#6]"),
    ("ketone", "[#6][CX3](=O)[#6]"),
    ("aldehyde", "[CX3H1](=O)[#6]"),
    ("amine", "[NX3;H2,H1;!$(NC=O)]"),
    ("amide", "[NX3][CX3](=[OX1])[#6]"),
    ("nitrile", "[NX1]#[CX2]"),
    ("aniline", "[NX3;H2,H1]c"),
    ("halide", "[F,Cl,Br,I]"),
    ("thiol", "[SX2H]"),
    ("alkene", "[CX3]=[CX3;!a]"),
    ("alkyne", "[CX2]#[CX2]"),
]
RDKIT_FG_COMPILED = {}
for fg_name, smarts_str in RDKIT_FG_SMARTS:
    try:
        from rdkit import Chem
        pat = Chem.MolFromSmarts(smarts_str)
        if pat:
            RDKIT_FG_COMPILED[fg_name] = pat
    except ImportError:
        pass

def find_fgs_from_smiles(smiles: str) -> list:
    """Detect functional groups from a SMILES string using RDKit SMARTS."""
    if not HAS_FRAGMENT_INTEGRATOR or not RDKIT_FG_COMPILED:
        return []
    try:
        from rdkit import Chem
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return []
        found = set()
        for fg_name, pat in RDKIT_FG_COMPILED.items():
            if mol.HasSubstructMatch(pat):
                found.add(fg_name)
        return sorted(found)
    except Exception:
        return []
def get_fg_type(fg_name):
    return FG.get(fg_name, {})

def meet_type(t1, t2):
    """Meet: min on all primitives — shared structural floor."""
    r = {}
    for p in PNAMES:
        o1, o2 = glyph_ord(p, t1.get(p,"?")), glyph_ord(p, t2.get(p,"?"))
        r[p] = ord_to_glyph(p, min(o1, o2))
    return r

def is_bond_compatible(bond, fg1, fg2):
    """Check if bond type is structurally compatible with FGs.
    For union primitives: bond value <= max(FG1, FG2)
    For intersection primitives (P, F): bond value <= min(FG1, FG2)
    """
    reasons = []
    for p in PNAMES:
        bo = glyph_ord(p, bond.get(p,"?"))
        if p in ("P", "F"):
            fo = min(glyph_ord(p, fg1.get(p,"?")), glyph_ord(p, fg2.get(p,"?")))
        else:
            fo = max(glyph_ord(p, fg1.get(p,"?")), glyph_ord(p, fg2.get(p,"?")))
        if bo > fo:
            reasons.append(f"{p}: bond={bo} > FG={fo}")
    return len(reasons) == 0, reasons

def evaluate_disconnection(fg1_name, fg2_name, bond_name, molecule_type):
    """Evaluate a disconnection using grammar-derived rules.
    
    Two deltas are computed:
      - bond_delta  = distance(bond_type, meet(FG1, FG2)) — bond-to-interface fit
      - product_delta = distance(product_type, molecule_type) — product-to-target match
    
    Product delta is the PRIMARY ranking criterion — it measures whether
    the disconnection actually produces the target's structural type.
    Bond delta is a secondary diagnostic.
    
    Compatibility = whether bond primitives are within FG capacity.
    """
    fg1 = FG.get(fg1_name, {}); fg2 = FG.get(fg2_name, {})
    bond = BOND_TYPES.get(bond_name, {})
    if not fg1 or not fg2 or not bond:
        return None
    
    interface = meet_type(fg1, fg2)
    bond_delta, bond_conflicts = tup_dist(bond, interface)
    compatible, reasons = is_bond_compatible(bond, fg1, fg2)
    
    product = bond_product_type(fg1, fg2, bond)
    
    # PRIMARY: distance from product type to target molecule type
    product_delta, product_conflicts = tup_dist(product, molecule_type)
    
    return {
        "fg1": fg1_name, "fg2": fg2_name,
        "bond": bond_name,
        "bond_desc": bond.get("desc", bond_name),
        "bond_delta": round(bond_delta, 3),       # bond-to-interface fit
        "product_delta": round(product_delta, 3),  # product-to-target match (PRIMARY)
        "delta": round(product_delta, 3),          # legacy alias = product_delta
        "compatible": compatible,
        "incompatible_reasons": reasons,
        "bond_conflicts": len(bond_conflicts),
        "product_conflicts": len(product_conflicts),
        "product_type": fmt_tup(product),
    }

def find_disconnections(fg_names, molecule_type, max_results=None):
    """Find all viable disconnections via grammar-derived rules.
    For each pair of FGs and each bond type, compute structural delta.
    Incompatible bonds are filtered out. 
    Ranked by product_delta (product-to-target match) then bond_delta (bond-to-interface fit).
    """
    results = []
    for i, fg1 in enumerate(fg_names):
        for fg2 in fg_names[i:]:
            for bname in BOND_TYPES:
                ev = evaluate_disconnection(fg1, fg2, bname, molecule_type)
                if ev and ev["compatible"]:
                    results.append(ev)
    results.sort(key=lambda x: (x["product_delta"], x["bond_delta"]))
    return results[:max_results]

# CAS RESOLVER
# ====================================================================
class CASResolver:
    def __init__(self):
        self._cache = self._load_cache()
        self._local = self._load_local()

    def _load_cache(self):
        try:
            with open(CAS_CACHE_PATH) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self):
        try:
            with open(CAS_CACHE_PATH, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception:
            pass

    def _load_local(self):
        return {
            "50-78-2": {"name": "2-acetoxybenzoic acid", "formula": "C9H8O4", "type_hint": "ester carboxylic_acid aromatic_ring", "smiles": "CC(=O)Oc1ccccc1C(=O)O"},
            "103-90-2": {"name": "acetaminophen", "formula": "C8H9NO2", "type_hint": "amide phenol", "smiles": "CC(=O)Nc1ccc(O)cc1"},
            "69-72-7": {"name": "salicylic acid", "formula": "C7H6O3", "type_hint": "carboxylic_acid phenol", "smiles": "O=C(O)c1ccccc1O"},
            "79-09-4": {"name": "propionic acid", "formula": "C3H6O2", "type_hint": "carboxylic_acid", "smiles": "CCC(=O)O"},
            "64-19-7": {"name": "acetic acid", "formula": "C2H4O2", "type_hint": "carboxylic_acid", "smiles": "CC(=O)O"},
            "67-64-1": {"name": "acetone", "formula": "C3H6O", "type_hint": "ketone", "smiles": "CC(=O)C"},
            "67-56-1": {"name": "methanol", "formula": "CH4O", "type_hint": "alcohol", "smiles": "CO"},
            "64-17-5": {"name": "ethanol", "formula": "C2H6O", "type_hint": "alcohol", "smiles": "CCO"},
            "71-23-8": {"name": "propanol", "formula": "C3H8O", "type_hint": "alcohol", "smiles": "CCCO"},
            "75-07-0": {"name": "acetaldehyde", "formula": "C2H4O", "type_hint": "aldehyde", "smiles": "CC=O"},
            "100-52-7": {"name": "benzaldehyde", "formula": "C7H6O", "type_hint": "aldehyde aromatic_ring", "smiles": "C1=CC=C(C=C1)C=O"},
            "100-66-3": {"name": "anisole", "formula": "C7H8O", "type_hint": "ether aromatic_ring", "smiles": "COc1ccccc1"},
            "108-95-2": {"name": "phenol", "formula": "C6H6O", "type_hint": "phenol", "smiles": "Oc1ccccc1"},
            "71-43-2": {"name": "benzene", "formula": "C6H6", "type_hint": "aromatic_ring", "smiles": "c1ccccc1"},
            "100-42-5": {"name": "styrene", "formula": "C8H8", "type_hint": "alkene aromatic_ring", "smiles": "C=Cc1ccccc1"},
            "121-44-8": {"name": "triethylamine", "formula": "C6H15N", "type_hint": "amine", "smiles": "CCN(CC)CC"},
            "62-53-3": {"name": "aniline", "formula": "C6H7N", "type_hint": "aniline", "smiles": "Nc1ccccc1"},
            "75-05-8": {"name": "acetonitrile", "formula": "C2H3N", "type_hint": "nitrile", "smiles": "CC#N"},
            "67-66-3": {"name": "chloroform", "formula": "CHCl3", "type_hint": "halide", "smiles": "C(Cl)(Cl)Cl"},
            "75-09-2": {"name": "dichloromethane", "formula": "CH2Cl2", "type_hint": "halide", "smiles": "C(Cl)Cl"},
            "107-13-1": {"name": "acrylonitrile", "formula": "C3H3N", "type_hint": "alkene nitrile", "smiles": "C=CC#N"},
            "74-85-1": {"name": "ethylene", "formula": "C2H4", "type_hint": "alkene", "smiles": "C=C"},
            "74-86-2": {"name": "acetylene", "formula": "C2H2", "type_hint": "alkyne", "smiles": "C#C"},
            "106-97-8": {"name": "butane", "formula": "C4H10", "type_hint": "alkene", "smiles": "CCCC"},
            "110-82-7": {"name": "cyclohexane", "formula": "C6H12", "type_hint": "cyclic", "smiles": "C1CCCCC1"},
            "108-88-3": {"name": "toluene", "formula": "C7H8", "type_hint": "aromatic_ring", "smiles": "Cc1ccccc1"},
            "100-41-4": {"name": "ethylbenzene", "formula": "C8H10", "type_hint": "aromatic_ring", "smiles": "CCc1ccccc1"},
            "98-86-2": {"name": "acetophenone", "formula": "C8H8O", "type_hint": "ketone aromatic_ring", "smiles": "CC(=O)c1ccccc1"},
            "98-95-3": {"name": "nitrobenzene", "formula": "C6H5NO2", "type_hint": "nitro aromatic_ring", "smiles": "O=N(=O)c1ccccc1"},
            "100-47-0": {"name": "benzonitrile", "formula": "C7H5N", "type_hint": "nitrile aromatic_ring", "smiles": "N#Cc1ccccc1"},
            "88-89-1": {"name": "picric acid", "formula": "C6H3N3O7", "type_hint": "phenol nitro", "smiles": "O=[N+]([O-])c1c(O)c([N+](=O)[O-])cc1[N+]([O-])=O"},
            "106-50-3": {"name": "p-phenylenediamine", "formula": "C6H8N2", "type_hint": "amine aromatic_ring", "smiles": "Nc1ccc(N)cc1"},
            "95-76-1": {"name": "3,4-dichloroaniline", "formula": "C6H5Cl2N", "type_hint": "halide aniline", "smiles": "Nc1cc(Cl)c(Cl)cc1"},
            "3568-94-3": {"name": "4-methyl-5-phenyl-4,5-dihydro-1,3-oxazol-2-amine", "formula": "C10H12N2O", "type_hint": "amine aromatic_ring ether cyclic", "smiles": "CC1=NC(=NO1)c2ccccc2N"},
            "1972-08-3": {"name": "11-hydroxy-Δ9-tetrahydrocannabinol", "formula": "C21H30O3", "type_hint": "phenol alcohol alkene ether cyclic", "smiles": "CC1(OC2=CC(CCCC(C)(O)C)=CC(=C2C1)C)C"},
            "7704-34-9": {"name": "sulfur", "formula": "S8", "type_hint": "thiol", "smiles": "S1SSSSSSS1"},
        }

    def resolve(self, cas_number):
        cas = cas_number.strip()
        if cas in self._local:
            entry = dict(self._local[cas])
            entry["cas"] = cas; entry["source"] = "local_db"
            return entry
        if cas in self._cache:
            entry = dict(self._cache[cas])
            entry["cas"] = cas; entry["source"] = "cache"
            return entry
        try:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/property/CanonicalSMILES,MolecularFormula,IUPACName/JSON"
            req = urllib.request.Request(url, headers={"User-Agent": "ch3mpiler/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            props = data.get("PropertyTable", {}).get("Properties", [{}])[0]
            name = props.get("IUPACName", props.get("MolecularFormula", cas))
            formula = props.get("MolecularFormula", "")
            smiles = props.get("CanonicalSMILES", "") or props.get("ConnectivitySMILES", "")
            entry = {"cas": cas, "name": name, "formula": formula, "smiles": smiles, "source": "pubchem", "type_hint": ""}
            self._cache[cas] = entry
            self._save_cache()
            return entry
        except Exception as e:
            return {"cas": cas, "name": f"CAS-{cas}", "formula": "", "source": "unresolved", "type_hint": "", "error": str(e)}


# ====================================================================
# CH3MPILER - Main Class
# ====================================================================
class Ch3mpiler:
    def __init__(self):
        self.catalog = self._load_catalog()
        self.cas_resolver = CASResolver()

    def _load_catalog(self):
        try:
            with open(CATALOG_PATH) as f:
                return json.load(f)
        except Exception:
            return []

    def analyze(self, target):
        """Analyze molecule: type, FGs, grammar-derived disconnections."""
        mol_type, source = get_molecule_type(target, self.catalog)
        fgs = find_fgs(target)
        
        cuts = []
        if fgs and mol_type:
            cuts = find_disconnections(fgs, mol_type)
        
        # Find analogs from catalog
        analogs = []
        for e in self.catalog[:500]:
            et = {}
            for pn, pf in zip(PNAMES, PFIELDS):
                v = e.get(pf, ""); 
                if v: et[pn] = v
            if len(et) == 12:
                d, _ = tup_dist(mol_type, et)
                if d < 3.5 and d > 0:
                    analogs.append({"n": e.get("name",""), "d": round(d, 3)})
        analogs.sort(key=lambda x: x["d"])
        
        return {"target": target, "type": fmt_tup(mol_type),
                "type_source": source, "fgs": fgs,
                "cuts": cuts, "analogs": analogs[:8]}

    def retrosynthesis(self, target, depth=2):
        """Full retrosynthetic tree using grammar-derived rules."""
        base = self.analyze(target)
        tree = {"target": target, "type": base["type"],
                "fgs": base["fgs"], "cuts": base["cuts"],
                "analogs": base["analogs"], "steps": []}
        
        if depth > 0:
            for idx, cut in enumerate(base["cuts"][:3]):
                sname1 = f"{cut['fg1']}_precursor"
                sname2 = f"{cut['fg2']}_precursor"
                sub1 = self.retrosynthesis(sname1, depth-1)
                sub2 = self.retrosynthesis(sname2, depth-1)
                tree["steps"].append({
                    "bond": cut["bond"],
                    "bond_desc": cut["bond_desc"],
                    "delta": cut["delta"],
                    "bond_delta": cut.get("bond_delta", cut.get("delta", 0)),
                    "product_delta": cut.get("product_delta", cut.get("delta", 0)),
                    "fg1": cut["fg1"], "fg2": cut["fg2"],
                    "product_type": cut["product_type"],
                    "precursors": [
                        {"name": sname1, "fg_hint": cut["fg1"], "type": sub1["type"],
                         "further": sub1["cuts"][:2] if depth > 1 else []},
                        {"name": sname2, "fg_hint": cut["fg2"], "type": sub2["type"],
                         "further": sub2["cuts"][:2] if depth > 1 else []},
                    ]
                })
        return tree

    def path_to_target(self, starting_material, target, depth=4):
        """Find retrosynthetic path from target to starting material."""
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

        try:
            from reaction_deriver import is_simple_material
            start_is_simple = is_simple_material(starting_material, self)
        except Exception:
            start_is_simple = False

        retro_tree = self.retrosynthesis(target, depth=depth)
        found_paths = []

        def _walk_tree(node, current_path, current_depth):
            steps = node.get("steps", [])
            if not steps:
                node_name = node.get("target", "")
                node_fgs = node.get("fgs", [])
                node_type = node.get("type", "")
                nm = (node_name.lower() == starting_material.lower() or
                      node_name.lower().replace("_"," ").strip() ==
                      starting_material.lower().replace("_"," ").strip())
                start_fgs = start_analysis.get("fgs", [])
                fg_overlap = len(set(node_fgs) & set(start_fgs))
                fgm = (fg_overlap >= min(len(node_fgs), len(start_fgs)) * 0.5
                       if node_fgs and start_fgs else False)
                found_paths.append({
                    "node_name": node_name, "node_type": node_type,
                    "node_fgs": node_fgs, "path": list(current_path),
                    "path_length": len(current_path),
                    "name_match": nm, "fg_match": fgm, "depth": current_depth
                })
                return
            for idx, step in enumerate(steps):
                se = {"bond": step.get("bond",""), "bond_desc": step.get("bond_desc",""),
                      "delta": step.get("delta",0), "fg1": step.get("fg1",""),
                      "fg2": step.get("fg2",""),
                      "product_type": step.get("product_type",""),
                      "target_at_this_level": node.get("target", target)}
                new_path = current_path + [se]
                for prec in step.get("precursors", []):
                    prec_name = prec.get("name", "")
                    prec_type = prec.get("type", "")
                    prec_fgs = []
                    # Use fg_hint from precursor data (most reliable)
                    fg_hint = prec.get("fg_hint", "")
                    if fg_hint and fg_hint in FG:
                        prec_fgs = [fg_hint]
                    else:
                        # Fallback: try analyzing the stripped name
                        stripped = prec_name.replace("_precursor","").replace("_"," ")
                        try:
                            pa = self.analyze(stripped)
                            prec_fgs = pa.get("fgs", [])
                        except Exception:
                            pass
                        # If still empty, check if stripped name IS a known FG
                        if not prec_fgs and stripped in FG:
                            prec_fgs = [stripped]
                    nm = (prec_name.lower() == starting_material.lower() or
                          prec_name.lower().replace("_"," ").strip() ==
                          starting_material.lower().replace("_"," ").strip())
                    start_fgs = start_analysis.get("fgs", [])
                    fg_overlap = len(set(prec_fgs) & set(start_fgs))
                    fgm = (fg_overlap >= min(len(prec_fgs), len(start_fgs)) * 0.5
                           if prec_fgs and start_fgs else False)
                    found_paths.append({
                        "node_name": prec_name, "node_type": prec_type,
                        "node_fgs": prec_fgs, "path": list(new_path),
                        "path_length": len(new_path),
                        "name_match": nm, "fg_match": fgm, "depth": current_depth + 1
                    })
                    further = prec.get("further", [])
                    if further:
                        sub = {"target": prec_name, "type": prec_type, "fgs": prec_fgs,
                               "steps": [{"bond": f.get("bond",""), "bond_desc": f.get("bond_desc",""),
                                          "delta": f.get("delta",0), "fg1": f.get("fg1",""),
                                          "fg2": f.get("fg2",""), "product_type": f.get("product_type",""),
                                          "precursors": []} for f in further]}
                        _walk_tree(sub, new_path, current_depth + 1)

        root_node = {"target": target, "type": retro_tree.get("type",""),
                     "fgs": target_analysis.get("fgs", []),
                     "steps": retro_tree.get("steps", [])}
        _walk_tree(root_node, [], 0)

        name_matches = [p for p in found_paths if p["name_match"]]
        fg_matches = [p for p in found_paths if p["fg_match"] and not p["name_match"]]
        name_matches.sort(key=lambda x: (x["path_length"], x["depth"]))
        fg_matches.sort(key=lambda x: (x["path_length"], x["depth"]))

        result = {"target": target, "starting_material": starting_material,
                  "direct_structural_distance": round(direct_dist, 4),
                  "direct_conflicts": direct_conflicts[:6],
                  "start_is_simple": start_is_simple,
                  "retro_depth_searched": depth,
                  "total_nodes_searched": len(found_paths),
                  "exact_name_matches": len(name_matches),
                  "fg_signature_matches": len(fg_matches)}

        if name_matches:
            best = name_matches[0]
            fwd_path = []
            for step in best["path"]:
                fwd_path.append({"step": len(fwd_path)+1, "operation": "Coagula (mu)",
                    "bond": step.get("bond",""), "reaction": step.get("bond_desc",""),
                    "delta": step.get("delta",0), "fg1": step.get("fg1",""), "fg2": step.get("fg2",""),
                    "product": step.get("target_at_this_level", target)})
            result["found"] = True
            result["path"] = fwd_path
            result["path_length"] = best["path_length"]
            result["match_type"] = "exact_name"
            result["terminal_node_name"] = best["node_name"]
        elif fg_matches:
            best = fg_matches[0]
            fwd_path = []
            for step in best["path"]:
                fwd_path.append({"step": len(fwd_path)+1, "operation": "Coagula (mu)",
                    "bond": step.get("bond",""), "reaction": step.get("bond_desc",""),
                    "delta": step.get("delta",0), "fg1": step.get("fg1",""), "fg2": step.get("fg2",""),
                    "product": step.get("target_at_this_level", target)})
            result["found"] = True
            result["path"] = fwd_path
            result["path_length"] = best["path_length"]
            result["match_type"] = "fg_signature"
            result["terminal_node_name"] = best["node_name"]
            result["nearest_match"] = {"name": best["node_name"],
                "type": best["node_type"], "fgs": best["node_fgs"]}
        else:
            result["found"] = False
            best_node = None
            best_dist = float("inf")
            for p in found_paths:
                nts = p.get("node_type", "")
                if nts and nts.startswith("<"):
                    vals = [v.strip() for v in nts[1:-1].split(";")]
                    no = {}
                    for i, pn in enumerate(PNAMES):
                        if i < len(vals):
                            _, o = g2v(pn, vals[i])
                            no[pn] = o
                    if no and src_ords:
                        sq = 0.0
                        for pn in PNAMES:
                            o1 = src_ords.get(pn, 0)
                            o2 = no.get(pn, 0)
                            w = WEIGHTS.get(pn, 1.0)
                            d = (o1 - o2) * w
                            sq += d * d
                        d = math.sqrt(sq)
                        if d < best_dist:
                            best_dist = d
                            best_node = p
            if best_node:
                result["nearest_match"] = {"name": best_node["node_name"],
                    "type": best_node["node_type"], "fgs": best_node["node_fgs"],
                    "structural_distance": round(best_dist, 4),
                    "path_to_nearest": best_node["path_length"]}
        return result

    def forward(self, reagents):
        """Predict forward reaction: find most compatible bond between reagent FGs."""
        all_fgs = set()
        for r in reagents:
            all_fgs.update(find_fgs(r))
        if not all_fgs:
            return {"reagents": reagents, "error": "no FGs identified"}
        
        # Find best bond between any pair of identified FGs
        best = None
        for fg1 in sorted(all_fgs):
            for fg2 in sorted(all_fgs):
                for bname in BOND_TYPES:
                    fg1_t = FG.get(fg1, {}); fg2_t = FG.get(fg2, {})
                    bond = BOND_TYPES.get(bname, {})
                    if fg1_t and fg2_t and bond:
                        product = bond_product_type(fg1_t, fg2_t, bond)
                        # Lower tensor-to-product delta = bond is more structuring
                        tensor = tensor_type(fg1_t, fg2_t)
                        d, _ = tup_dist(product, tensor)
                        if best is None or d < best["structuring_delta"]:
                            best = {"fg1": fg1, "fg2": fg2, "bond": bname,
                                    "bond_desc": bond.get("desc",""),
                                    "structuring_delta": round(d, 3),
                                    "product_type": fmt_tup(product)}
        return {"reagents": reagents, "fgs": sorted(all_fgs),
                "prediction": best} if best else {"reagents": reagents, "fgs": sorted(all_fgs), "error": "no compatible bond"}

    def resolve_cas(self, cas_number):
        return self.cas_resolver.resolve(cas_number)

    def resolve_and_analyze(self, cas_number, do_retrosynthesis=False, depth=2):
        info = self.resolve_cas(cas_number)
        name = info.get("name", cas_number)
        if do_retrosynthesis:
            tree = self.retrosynthesis(name, depth=depth)
            tree["cas_info"] = info
            return tree
        result = self.analyze(name)
        result["cas_info"] = info
        return result

# Patch Ch3mpiler with enriched precursor lattice
try:
    from . import precursor_lattice
except ImportError:
    import precursor_lattice
precursor_lattice.patch_ch3mpiler(Ch3mpiler)
# ====================================================================

# --- SMILES resolution for print functions ---
_SMILES_CACHE = {}
def _resolve_smiles(name):
    if not name: return ""
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key in SMILES_LOOKUP:
        _SMILES_CACHE[key] = SMILES_LOOKUP[key]
        return _SMILES_CACHE[key]
    if key in _SMILES_CACHE:
        return _SMILES_CACHE[key]
    try:
        from scaffold_parser import resolve_name_to_smiles as _r
        smi = _r(name)
        if smi: _SMILES_CACHE[key] = smi; return smi
    except: pass
    return ""

# OUTPUT FORMATTERS
# ====================================================================
def print_retrosynthesis(tree, indent=0):
    pad = "  " * indent
    target = tree["target"]
    ttype = tree["type"]
    
    if "cas_info" in tree:
        ci = tree["cas_info"]
        src = ci.get("source", "")
def print_retrosynthesis(tree, indent=0):
    pad = "  " * indent
    target = tree["target"]
    ttype = tree["type"]
    
    if "cas_info" in tree:
        ci = tree["cas_info"]
        src = ci.get("source", "")
        cas = ci.get("cas", "")
        formula = ci.get("formula", "")
        if src != "unresolved":
            info_line(f"CAS: {cas}  ({src})", indent=indent)
            if formula:
                info_line(f"Formula: {formula}", indent=indent)
    
    target_smi = _resolve_smiles(target)
    target_line(target, target_smi, indent=indent)
    numeric_line("Type", ttype, indent=indent+1)
    
    fgs = tree.get("fgs", [])
    if fgs:
        fg_line(f"FGs: {', '.join(fgs)}", indent=indent+1)
    
    subheader("Grammar-derived disconnections (no named reactions)")
    steps = tree.get("steps", [])
    if not steps:
        info_line("(terminal)", indent=indent+1)
        return
    
    for idx, step in enumerate(steps):
        bd = step.get('bond_delta', '?')
        bond_line(f"── Cut {idx+1}: {step['bond']} (δ={step['delta']}, binding={bd}) ──", indent=indent+1)
        step_detail("Description", step['bond_desc'], indent=indent+2)
        step_detail("Between", f"{step['fg1']} + {step['fg2']}", indent=indent+2)
        step_detail("Product type", step['product_type'], indent=indent+2)
        
        for pidx, prec in enumerate(step.get("precursors", [])):
            prec_name = prec['name']
            # Use enriched fragment SMILES when available (from BondFragmentIntegrator)
            # Only show SMILES if real fragmentation happened (_resolved_smiles present)
            # or if the precursor name actually resolves to a real molecule
            if tree.get('_resolved_smiles'):
                prec_smi = prec.get('smiles', '') or _resolve_smiles(prec_name)
            else:
                prec_smi = prec.get('smiles', '')
            # Also show further sub-cut fragment info
            further_frags = ''
            f_list = prec.get("further", [])
            if f_list:
                frag_smis = []
                for fc in f_list[:2]:
                    fa = fc.get('fragment_smiles_a', '')
                    fb = fc.get('fragment_smiles_b', '')
                    if fa or fb:
                        frag_smis.append(f'{fc["bond"]}: {fa} + {fb}')
                if frag_smis:
                    further_frags = '  [' + ', '.join(frag_smis) + ']'
            precursor_line(f"Precursor {pidx+1}", prec_name, prec.get('fg_hint',''), prec_smi, indent=indent+2)
            if further_frags:
                info_line(further_frags, indent=indent+3)
            f_list = prec.get("further", [])
            if f_list:
                for fc in f_list[:2]:
                    info_line(f"  └ {fc['bond']} (δ={fc['delta']})", indent=indent+2)



def print_analysis(result):
    target = result['target']
    target_smi = _resolve_smiles(target)
    target_line(target, target_smi)
    numeric_line("Type", f"{result['type']}  [{result.get('type_source','?')}]")
    fgs = result.get("fgs", [])
    if fgs:
        fg_line(f"FGs: {', '.join(fgs)}")
    
    cuts = result.get("cuts", [])
    if cuts:
        subheader("Grammar-derived disconnections (ranked by δ, lower=better)")
        info_line("δ = product-to-target distance")
        headers = ["Bond", "δ", "Binding", "Between", "Product Type"]
        rows = []
        for c in cuts:
            between = f"{c['fg1']}+{c['fg2']}"
            bd = c.get('bond_delta', '?')
            pd = c.get('product_delta', c.get('delta', 0))
            rows.append([c['bond'], f"{pd:.3f}", f"{bd:.3f}", between, c['product_type']])
        table(headers, rows)
    else:
        info_line("No disconnections found.")
    
    analogs = result.get("analogs", [])
    if analogs:
        subheader("Structural analogs")
        for a in analogs[:5]:
            a_smi = _resolve_smiles(a['n'])
            analog_line(a['n'], a['d'], a_smi)



    print("=" * 66)
def print_path(result):
    """Print the synthetic path from starting material to target (rich formatted)."""
    target = result.get("target", "?")
    start = result.get("starting_material", "?")
    direct_dist = result.get("direct_structural_distance", "?")
    
    header(f"ch3mpiler — Synthetic Path: {start} → {target}")
    start_smi = _resolve_smiles(start)
    target_smi = _resolve_smiles(target)
    if start_smi: success_line(f"STARTING MATERIAL SMILES: {start_smi}")
    if target_smi: success_line(f"TARGET SMILES:            {target_smi}")
    numeric_line("Direct structural distance", direct_dist)
    info_line(f"Starting material is simple: {result.get('start_is_simple', '?')}")
    info_line(f"Retro depth searched: {result.get('retro_depth_searched', '?')}")
    info_line(f"Total nodes searched: {result.get('total_nodes_searched', '?')}")
    print()
    
    if result.get("found"):
        match_type = result.get("match_type", "?")
        path_len = result.get("path_length", 0)
        term_node = result.get("terminal_node_name", "?")
        
        success_line(f"PATH FOUND (match: {match_type})")
        info_line(f"Terminal node: {term_node}")
        numeric_line("Path length", f"{path_len} steps")
        print()
        
        path = result.get("path", [])
        subheader(f"Forward synthetic route ({start} → {target})")
        print()
        
        for i, step in enumerate(path):
            step_num = step.get("step", i+1)
            bond = step.get("bond", "?")
            reaction = step.get("reaction", "?")
            delta = step.get("delta", 0)
            fg1 = step.get("fg1", "?")
            fg2 = step.get("fg2", "?")
            product = step.get("product", "?")
            
            path_step(step_num)
            step_detail("Bond", f"{bond} ({reaction})")
            numeric_line("Delta", delta, indent=2)
            step_detail("Between", f"{fg1} + {fg2}", indent=2)
            product_smi = _resolve_smiles(product)
            step_product_line(product, product_smi, indent=2)
            print()
        
        separator(50)
        final_smi = _resolve_smiles(target)
        success_line(f"FINAL: {target}  SMILES: {final_smi}" if final_smi else f"FINAL: {target}")
    else:
        error_line("NO EXACT PATH FOUND")
        nearest = result.get("nearest_match")
        if nearest:
            info_line(f"Nearest tree node: {nearest.get('name', '?')}")
            numeric_line("Structural distance", nearest.get('structural_distance', '?'), indent=1)
            info_line(f"Node type: {nearest.get('type', '?')}")
            info_line(f"Node FGs: {nearest.get('fgs', [])}")
            info_line(f"Path steps to nearest: {nearest.get('path_to_nearest', '?')}")
        print()
        info_line("The starting material cannot be reached from this target")
        info_line("within the searched depth. Try --depth N for deeper search.")
    
    conflicts = result.get("direct_conflicts", [])
    if conflicts:
        subheader(f"Structural conflicts ({len(conflicts)})")
        for c in conflicts[:5]:
            conflict_line(c['p'], c['tgt'], c['src'])



        print(f"  Structural conflicts ({len(conflicts)}):")
        for c in conflicts[:5]:
            print(f"    {c['p']}: target={c['tgt']} vs start={c['src']}")

# MAIN CLI

# ====================================================================
def main():
    _dash_map = str.maketrans({chr(c): '-' for c in [0x2212, 0x2013, 0x2014, 0x2015, 0xff0d, 0xfe63]})
    sys.argv = [s.translate(_dash_map) for s in sys.argv]
    
    parser = argparse.ArgumentParser(
        description="ch3mpiler - Grammar-derived retrosynthetic compiler (no named reactions)")
    parser.add_argument("--target", help="Molecule name")
    parser.add_argument("--smiles", help="Direct SMILES input (will be canonicalized)")
    parser.add_argument("--retrosynthesis", action="store_true", help="Full retrosynthetic tree")
    parser.add_argument("--cas", help="CAS Registry Number")
    parser.add_argument("--depth", type=int, default=2, help="Retrosynthetic depth")
    parser.add_argument("--forward", nargs="+", help="Reagents for forward prediction")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--fg", help="Analyze functional group")
    parser.add_argument("--list-fgs", action="store_true", help="List FGs")
    parser.add_argument("--list-bonds", action="store_true", help="List bond types")
    parser.add_argument("--show-cas-cache", action="store_true", help="Show CAS cache")
    parser.add_argument("--cdxml", help="Generate CDXML reaction scheme (path to .cdxml output file)")
    parser.add_argument("--starting-material", help="Starting material name (used with --target for pathfinding)")
    parser.add_argument("--path", action="store_true", help="Find synthetic path between --starting-material and --target")
    
    args = parser.parse_args()
    ch = Ch3mpiler()
    
    if args.cas and not args.starting_material:
        # Plain CAS mode (no --starting-material)
        if args.retrosynthesis:
            tree = ch.resolve_and_analyze(args.cas, do_retrosynthesis=True, depth=args.depth)
            print("=" * 66)
            print("  ch3mpiler — Retrosynthetic Analysis (grammar-derived)")
            print("=" * 66)
            print_retrosynthesis(tree)
        else:
            r = ch.resolve_and_analyze(args.cas)
            info = r.get("cas_info", {})
            print(f"CAS: {info.get('cas', args.cas)}")
            print(f"Name: {info.get('name', 'unknown')}  ({info.get('source', '')})")
            if info.get("formula"): print(f"Formula: {info['formula']}")
            if info.get("smiles"): print(f"SMILES: {info['smiles']}")
            print_analysis(r)
        return
    elif args.cas and args.starting_material:
        # Handled below by the starting_material handler
        pass
    
    if args.list_fgs:
        print("Functional Groups:")
        for fg_name in sorted(FG.keys()):
            t = {p: FG[fg_name].get(p, "?") for p in PNAMES}
            print(f"  {fg_name:30s}  {fmt_tup(t)}")
        return
    
    if args.list_bonds:
        print("Grammar-derived bond types:")
        for bname in sorted(BOND_TYPES.keys()):
            b = BOND_TYPES[bname]
            t = {p: b.get(p, "?") for p in PNAMES}
            print(f"  {bname:20s}  {b.get('desc',''):45s}  {fmt_tup(t)}")
        return
    
    if args.show_cas_cache:
        cache = ch.cas_resolver._cache
        if not cache:
            print("CAS cache is empty.")
        else:
            print(f"Cached CAS ({len(cache)}):")
            for cas, entry in sorted(cache.items()):
                print(f"  {cas:15s}  {entry.get('name','?'):40s}  [{entry.get('source','?')}]")
        return
    
    if args.fg:
        if args.fg in FG:
            t = {p: FG[args.fg].get(p, "?") for p in PNAMES}
            print(f"FG: {args.fg}")
            print(f"Type: {fmt_tup(t)}")
        else:
            print(f"Unknown FG: {args.fg}")
            print(f"Known: {', '.join(sorted(FG.keys()))}")
        return
    
    if args.starting_material:
        # Pathfinding mode: resolve target from --target or --cas
        target_name = args.target
        if args.cas and not target_name:
            # Resolve CAS to name first
            cas_info = ch.resolve_cas(args.cas)
            target_name = cas_info.get("name", "")
            if not target_name or target_name == args.cas:
                print(f"Could not resolve CAS {args.cas} to a known molecule name.")
                return
        if target_name:
            result = ch.path_to_target(args.starting_material, target_name, depth=args.depth)
            print_path(result)
            
            # Generate CDXML if requested
            if args.cdxml and HAS_CDXML:
                try:
                    from cdxml_generator import generate_reaction_cdxml
                    
                    # Build SMILES for each step with cascading intermediates
                    start_name = args.starting_material.lower().replace(" ", "_")
                    target_name_lower = target_name.lower().replace(" ", "_")
                    
                    start_smi = SMILES_LOOKUP.get(start_name, "")
                    target_smi = SMILES_LOOKUP.get(target_name_lower, "")
                    
                    # Cascade SMILES: product of step n is reactant of step n+1
                    steps_for_cdxml = []
                    prev_smi = start_smi
                    for step in result.get("path", []):
                        fg1_name = step.get("fg1", "")
                        fg2_name = step.get("fg2", "")
                        fg1_tup = FG.get(fg1_name, {})
                        fg2_tup = FG.get(fg2_name, {})
                        
                        prod_name = step.get("product", "")
                        prod_smi = SMILES_LOOKUP.get(prod_name.lower().replace(" ", "_").replace("-", "_"), "")
                        
                        steps_for_cdxml.append({
                            "step": step.get("step", 0),
                            "bond": step.get("bond", ""),
                            "reaction": step.get("reaction", ""),
                            "fg1": fg1_name,
                            "fg2": fg2_name,
                            "product": prod_name,
                            "smiles_reactant": prev_smi,
                            "smiles_product": prod_smi or target_smi,
                            "fg1_tuple": fg1_tup,
                            "fg2_tuple": fg2_tup,
                        })
                        if prod_smi:
                            prev_smi = prod_smi
                    
                    out_path = args.cdxml
                    print(f"\n  [Generating CDXML: {out_path}]")
                    generate_reaction_cdxml(steps_for_cdxml, out_path=out_path,
                                             title=f"{args.starting_material} \u2192 {target_name}")
                except Exception as e:
                    import traceback
                    print(f"  [CDXML ERROR: {e}]")
                    traceback.print_exc()
            
            return
        # If only --starting-material without --target or --cas, fall through
    
    if args.target or args.smiles:
        target_name = args.target or ''
        direct_smiles = args.smiles or ''
        
        if args.retrosynthesis:
            # If direct SMILES provided and no target name, build a fake analyze() result
            if direct_smiles and not target_name:
                # Detect FGs from SMILES using RDKit
                smi_fgs = find_fgs_from_smiles(direct_smiles)
                if smi_fgs:
                    mol_type = compose_molecule_type(smi_fgs)
                    cuts = find_disconnections(smi_fgs, mol_type)
                    tree = {"target": f"SMILES:{direct_smiles[:40]}...", "type": fmt_tup(mol_type),
                            "fgs": smi_fgs, "cuts": cuts, "steps": []}
                    for idx, cut in enumerate(cuts[:3]):
                        sname1 = f"{cut['fg1']}_precursor"
                        sname2 = f"{cut['fg2']}_precursor"
                        tree["steps"].append({
                            "bond": cut["bond"], "bond_desc": cut["bond_desc"],
                            "delta": cut["delta"], "bond_delta": cut.get("bond_delta", cut.get("delta", 0)),
                            "product_delta": cut.get("product_delta", cut.get("delta", 0)),
                            "fg1": cut["fg1"], "fg2": cut["fg2"],
                            "product_type": cut["product_type"],
                            "precursors": [
                                {"name": sname1, "fg_hint": cut["fg1"], "type": "", "further": []},
                                {"name": sname2, "fg_hint": cut["fg2"], "type": "", "further": []},
                            ]
                        })
                else:
                    # Absolute fallback: single empty tree
                    tree = {"target": f"SMILES:{direct_smiles[:40]}...", "type": "?", "fgs": [], "cuts": [], "steps": []}
            else:
                tree = ch.retrosynthesis(target_name, depth=args.depth)
            
            # Enrich with real fragment SMILES if possible
            if HAS_FRAGMENT_INTEGRATOR:
                resolved_smi = resolve_target_smiles(
                    target_name=target_name,
                    smiles=direct_smiles,
                    cas=args.cas if hasattr(args, 'cas') else '',
                    cas_cache_path=str(Path(__file__).parent / 'CAS_cache.json')
                )
                if resolved_smi:
                    integrator = BondFragmentIntegrator(resolved_smi)
                    tree = integrator.enrich_retrosynthesis_tree(tree)
                    tree['_resolved_smiles'] = resolved_smi
                elif target_name:
                    # Name resolution failed — show clear warning
                    tree['_smiles_unresolved'] = True
            
            print("=" * 66)
            print("  ch3mpiler — Retrosynthetic Analysis (grammar-derived)")
            print("=" * 66)
            if tree.get('_resolved_smiles'):
                success_line(f"Target SMILES: {tree['_resolved_smiles']}")
            if tree.get('_smiles_unresolved'):
                error_line("Target name could not be resolved to SMILES - intermediate SMILES are placeholders. Use --smiles to provide exact SMILES.")
            print_retrosynthesis(tree)
        else:
            r = ch.analyze(args.target)
            print_analysis(r)
        return
    
    if args.forward:
        r = ch.forward(args.forward)
        print(f"Reagents: {', '.join(r['reagents'])}")
        if "error" in r:
            print(f"  {r['error']}")
        else:
            p = r.get("prediction", {})
            print(f"FGs: {', '.join(r.get('fgs',[]))}")
            print(f"Best bond: {p.get('bond','?')} ({p.get('bond_desc','')})")
            print(f"  Between: {p.get('fg1','?')} + {p.get('fg2','?')}")
            print(f"  Structuring Δ: {p.get('structuring_delta','?')}")
            print(f"  Product: {p.get('product_type','?')}")
        return
    
    if args.interactive:
        print("ch3mpiler interactive — grammar-derived bond rules")
        print("Commands: <name>, retro:<name>, cas:<n>, cas-retro:<n>,")
        print("          fwd:r1,r2, fg:<n>, fgs, bonds, quit")
        while True:
            try:
                c = input(">>> ").strip()
                if c in ("quit","q","exit"): break
                if c == "fgs":
                    for f in sorted(FG.keys()): print(f"  {f}")
                elif c == "bonds":
                    for b in sorted(BOND_TYPES.keys()):
                        print(f"  {b:20s}  {BOND_TYPES[b].get('desc','')}")
                elif c.startswith("fg:"):
                    fg = c[3:]
                    if fg in FG:
                        t = {p: FG[fg].get(p,"?") for p in PNAMES}
                        print(f"FG {fg}: {fmt_tup(t)}")
                    else: print(f"Unknown FG: {fg}")
                elif c.startswith("retro:"):
                    print_retrosynthesis(ch.retrosynthesis(c[6:], depth=2))
                elif c.startswith("cas:"):
                    r = ch.resolve_and_analyze(c[4:])
                    info = r.get("cas_info",{})
                    print(f"CAS: {info.get('cas','')} Name: {info.get('name','')}")
                    print_analysis(r)
                elif c.startswith("cas-retro:"):
                    print_retrosynthesis(ch.resolve_and_analyze(c[10:], do_retrosynthesis=True, depth=2))
                elif c.startswith("fwd:"):
                    r = ch.forward(c[4:].split(","))
                    print(f"Reagents: {', '.join(r['reagents'])}")
                    if "error" not in r:
                        p = r.get("prediction",{})
                        print(f"  -> {p.get('bond','?')} ({p.get('bond_desc','')})")
                    else: print(f"  {r['error']}")
                else:
                    r = ch.analyze(c)
                    print_analysis(r)
            except (EOFError, KeyboardInterrupt): break
        return
    
    # Default demo
    demo_title()
    print("Demo: benzaldehyde")
    r = ch.analyze("benzaldehyde")
    print_analysis(r)
    print()
    print("Try: ch3mpiler --cas 3568-94-3 --retrosynthesis")

if __name__ == "__main__":
    main()
