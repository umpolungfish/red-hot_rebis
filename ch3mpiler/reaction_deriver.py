#!/usr/bin/env python3
"""reaction_deriver.py — Grammar-first reaction condition deriver for ch3mpiler.

Given a disconnection (FG1, FG2, bond_type), derives reactants, conditions,
solvents, catalysts, and workup procedures from the Imscribing Grammar's
12-primitive structural algebra — ZERO appeal to named reactions or convention.

Core algorithm:
  1. Compute delta_vector = primitive-wise distance(bond, meet(FG1, FG2))
  2. Map each non-zero delta to a physical reaction parameter
  3. Select reactants from grammar-typed reagent database by FG compatibility
  4. Select solvent by structural proximity to meet(FG1, FG2)
  5. Derive workup from product–reactant structural gap

Author: Lando⊗⊙perator
"""
import math
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

BASE = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE.parent))
from shared.primitives import ORDINALS, WEIGHTS, resolve_ordinal_key
from shared.rich_output import *

PNAMES = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]
PFIELDS = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]
FIELD_TO_ORD = {
    "D": "Ð", "T": "Þ", "R": "Ř", "P": "Φ", "F": "ƒ",
    "K": "Ç", "G": "Γ", "Gm": "ɢ", "Ph": "⊙", "H": "Ħ",
    "S": "Σ", "W": "Ω"
}

def glyph_ord(p, glyph):
    if not glyph or glyph == '?':
        return 0
    ord_key = FIELD_TO_ORD.get(p, p)
    om = ORDINALS.get(ord_key, {})
    if glyph in om:
        return om[glyph]
    try:
        k = resolve_ordinal_key(ord_key, glyph)
        return om.get(k, 0)
    except (KeyError, Exception):
        return 0

def ord_to_glyph(p, o):
    ord_key = FIELD_TO_ORD.get(p, p)
    om = ORDINALS.get(ord_key, {})
    rev = {v: k for k, v in om.items()}
    return rev.get(o, '?')

def fmt_tup(t):
    gs = [t.get(p, "?") for p in PNAMES]
    return "<" + "".join(gs) + ">"

def tup_dist(t1, t2):
    sq = 0.0
    cf = []
    for p in PNAMES:
        v1 = t1.get(p, "")
        v2 = t2.get(p, "")
        o1 = glyph_ord(p, v1)
        o2 = glyph_ord(p, v2)
        w = WEIGHTS.get(FIELD_TO_ORD.get(p, p), 1.0)
        d = (o1 - o2) * w
        sq += d * d
        if o1 != o2:
            cf.append({"p": p, "a": v1, "b": v2, "d": o1 - o2})
    return math.sqrt(sq), cf

def meet_type(t1, t2):
    r = {}
    for p in PNAMES:
        o1 = glyph_ord(p, t1.get(p, "?"))
        o2 = glyph_ord(p, t2.get(p, "?"))
        r[p] = ord_to_glyph(p, min(o1, o2))
    return r

def tensor_type(t1, t2):
    r = {}
    for p in PNAMES:
        o1 = glyph_ord(p, t1.get(p, "?"))
        o2 = glyph_ord(p, t2.get(p, "?"))
        if p in ("P", "F"):
            r[p] = ord_to_glyph(p, min(o1, o2))
        else:
            r[p] = ord_to_glyph(p, max(o1, o2))
    return r

# ====================================================================
# PRIMITIVE-TO-CONDITION MAPPING
# Each primitive delta maps to a physical reaction parameter.
# Higher delta = more "structural tension" to overcome.
# ====================================================================

# Canonical ordinal ranges for each primitive (from shared/primitives.py)
# D: 1-4, T: 1-5, R: 1-4, P: 1-5, F: 1-3, K: 1-4.5
# G: 1-3, Gm: 1-4, Ph: 1-3, H: 1-4, S: 1-3, W: 1-4

PRIMITIVE_TO_CONDITION = {
    "D": {
        "name": "molecularity",
        "delta_map": {
            # delta=0: bond matches FG dimensionality — no activation
            (0, 0.5): {"molecularity": "spontaneous", "activation": "none"},
            # delta=1: bond adds 1D (wedge->triangle) — needs thermal activation
            (0.5, 1.5): {"molecularity": "bimolecular", "activation": "thermal"},
            # delta=2: bond adds 2D — needs high-energy activation
            (1.5, 2.5): {"molecularity": "termolecular", "activation": "photochemical_or_thermal_high"},
            # delta>2.5: bond restructures dimensionality completely
            (2.5, 5):   {"molecularity": "surface-mediated", "activation": "catalytic_harsh"},
        }
    },
    "T": {
        "name": "topology_control",
        "delta_map": {
            (0, 0.5):  {"steric": "none", "orientation": "no_preference"},
            (0.5, 1.5): {"steric": "moderate", "orientation": "facially_selective"},
            (1.5, 2.5): {"steric": "high", "orientation": "regioselective_catalyst"},
            (2.5, 5):   {"steric": "extreme", "orientation": "templated_synthesis"},
        }
    },
    "R": {
        "name": "coupling_mode",
        "delta_map": {
            (0, 0.5):  {"mode": "direct_combination", "activator": "none"},
            (0.5, 1.5): {"mode": "acid_or_base_catalyzed", "activator": "proton_transfer"},
            (1.5, 2.5): {"mode": "coupling_agent_required", "activator": "DCC_or_EDC_type"},
            (2.5, 5):   {"mode": "electrochemical_or_photoredox", "activator": "single_electron_transfer"},
        }
    },
    "P": {
        "name": "stereochemistry",
        "delta_map": {
            (0, 0.5):  {"stereo": "racemic_OK", "ee_requirement": 0},
            (0.5, 1.5): {"stereo": "diastereoselective", "ee_requirement": 70},
            (1.5, 3):   {"stereo": "enantioselective", "ee_requirement": 90},
            (3, 5):     {"stereo": "enantiospecific", "ee_requirement": 99},
        }
    },
    "F": {
        "name": "fidelity_regime",
        "delta_map": {
            (0, 0.5):  {"regime": "classical", "solvent_polarity": "any"},
            (0.5, 1.5): {"regime": "semiclassical", "solvent_polarity": "moderate"},
            (1.5, 3):   {"regime": "quantum_coherent", "solvent_polarity": "precise_dielectric"},
        }
    },
    "K": {
        "name": "temperature",
        "delta_map": {
            (0, 0.5):   {"T_C": (0, 30), "regime": "ambient"},
            (0.5, 1.5): {"T_C": (30, 80), "regime": "gentle_warming"},
            (1.5, 2.5): {"T_C": (80, 150), "regime": "reflux"},
            (2.5, 4.5): {"T_C": (150, 300), "regime": "sealed_tube"},
        }
    },
    "G": {
        "name": "concentration",
        "delta_map": {
            (0, 0.5):  {"conc_M": (0.5, 2.0), "regime": "standard"},
            (0.5, 1.5): {"conc_M": (0.01, 0.5), "regime": "dilute"},
            (1.5, 3):   {"conc_M": (2.0, 10.0), "regime": "high_concentration_or_neat"},
        }
    },
    "Gm": {
        "name": "addition_order",
        "delta_map": {
            (0, 0.5):  {"order": "all_at_once", "timing": "single_portion"},
            (0.5, 1.5): {"order": "sequential", "timing": "dropwise_over_time"},
            (1.5, 3):   {"order": "inverse_addition", "timing": "slow_reverse"},
            (3, 4):     {"order": "telescoped", "timing": "multiple_quenches"},
        }
    },
    "Ph": {
        "name": "catalyst",
        "delta_map": {
            (0, 0.3):  {"catalyst": "none", "reason": "bond_at_or_below_critical"},
            (0.3, 0.8): {"catalyst": "lewis_acid", "reason": "polarization_needed"},
            (0.8, 1.5): {"catalyst": "transition_metal", "reason": "orbital_symmetry_breaking"},
            (1.5, 3):   {"catalyst": "organocatalyst_or_enzyme", "reason": "highly_specific_activation"},
        }
    },
    "H": {
        "name": "chiral_induction",
        "delta_map": {
            (0, 0.5):  {"chiral": "none", "auxiliary": "not_needed"},
            (0.5, 1.5): {"chiral": "chiral_pool", "auxiliary": "substrate_control"},
            (1.5, 2.5): {"chiral": "chiral_auxiliary", "auxiliary": "evans_oxazolidinone_type"},
            (2.5, 4):   {"chiral": "chiral_catalyst", "auxiliary": "proline_or_binap_type"},
        }
    },
    "S": {
        "name": "stoichiometry",
        "delta_map": {
            (0, 0.5):  {"ratio": "1:1", "excess": 0},
            (0.5, 1.5): {"ratio": "1:1.2_to_1:3", "excess": 20},
            (1.5, 3):   {"ratio": "1:5_to_1:20", "excess": 100},
        }
    },
    "W": {
        "name": "protecting_groups",
        "delta_map": {
            (0, 0.5):  {"protect": "none", "strategy": "open_air_OK"},
            (0.5, 1.5): {"protect": "simple", "strategy": "acid_labile_group"},
            (1.5, 2.5): {"protect": "orthogonal", "strategy": "two_orthogonal_groups"},
            (2.5, 4):   {"protect": "full_orchestration", "strategy": "three_or_more_orthogonal"},
        }
    },
}

# ====================================================================
# GRAMMAR-TYPED REAGENT DATABASE
# Each reagent carries a full 12-primitive structural type, SMILES,
# and the functional groups it can supply.
# ====================================================================

REAGENT_DB = {
    # ── Carbon Nucleophiles ──
    "methyl_iodide": {
        "smiles": "CI", "role": "electrophile",
        "supplies": ["alkane"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U0001045E",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "ethyl_bromide": {
        "smiles": "CCBr", "role": "electrophile",
        "supplies": ["alkane"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U0001045E",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "benzyl_bromide": {
        "smiles": "BrCc1ccccc1", "role": "electrophile",
        "supplies": ["aromatic_ring"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },
    "benzene": {
        "smiles": "c1ccccc1", "role": "solvent/reagent",
        "supplies": ["aromatic_ring"],
        "D":"𐑨","T":"𐑸","R":"𐑾","P":"𐑯","F":"𐑐",
        "K":"𐑧","G":"𐑲","Gm":"𐑠","Ph":"⊙",
        "H":"𐑖","S":"𐑙","W":"𐑷",
    },

    "acetyl_chloride": {
        "smiles": "CC(=O)Cl", "role": "acylating_agent",
        "supplies": ["carbonyl", "halide"],
        "D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "benzoyl_chloride": {
        "smiles": "ClC(=O)c1ccccc1", "role": "acylating_agent",
        "supplies": ["carbonyl", "aromatic_ring", "halide"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "acetic_anhydride": {
        "smiles": "CC(=O)OC(C)=O", "role": "acylating_agent",
        "supplies": ["carbonyl", "ester"],
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047D","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010473","W":"\U00010477",
    },
    "formaldehyde": {
        "smiles": "C=O", "role": "electrophile",
        "supplies": ["aldehyde"],
        "D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "benzaldehyde": {
        "smiles": "O=Cc1ccccc1", "role": "electrophile",
        "supplies": ["aldehyde", "aromatic_ring"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "acetone": {
        "smiles": "CC(=O)C", "role": "electrophile",
        "supplies": ["ketone"],
        "D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },

    # ── Nitrogen Nucleophiles ──
    "ammonia": {
        "smiles": "N", "role": "nucleophile",
        "supplies": ["amine"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "methylamine": {
        "smiles": "CN", "role": "nucleophile",
        "supplies": ["amine"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "aniline": {
        "smiles": "Nc1ccccc1", "role": "nucleophile",
        "supplies": ["amine", "aromatic_ring"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "sodium_azide": {
        "smiles": "[N-]=[N+]=[N-].[Na+]", "role": "nucleophile",
        "supplies": ["amine", "nitrile"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },

    # ── Oxygen Nucleophiles ──
    "water": {
        "smiles": "O", "role": "nucleophile",
        "supplies": ["alcohol"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U0001045E",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
    },
    "methanol": {
        "smiles": "CO", "role": "nucleophile",
        "supplies": ["alcohol", "ether"],
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U00010457","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "ethanol": {
        "smiles": "CCO", "role": "nucleophile",
        "supplies": ["alcohol", "ether"],
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U00010457","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "phenol": {
        "smiles": "Oc1ccccc1", "role": "nucleophile",
        "supplies": ["phenol", "aromatic_ring"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "sodium_hydroxide": {
        "smiles": "[OH-].[Na+]", "role": "base",
        "supplies": ["alcohol"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U0001045E",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
    },
    "potassium_carbonate": {
        "smiles": "[K+].[K+].[O-]C([O-])=O", "role": "base",
        "supplies": [],  # inorganic base — supplies no organic FG
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U0001045E",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
    },

    # ── Reducing Agents ──
    "sodium_borohydride": {
        "smiles": "[BH4-].[Na+]", "role": "reducing_agent",
        "supplies": ["alcohol"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "lithium_aluminum_hydride": {
        "smiles": "[Li+].[AlH4-]", "role": "strong_reducing_agent",
        "supplies": ["alcohol", "amine"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U00010472","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },

    # ── Oxidizing Agents ──
    "potassium_permanganate": {
        "smiles": "[K+].[O-][Mn](=O)(=O)=O", "role": "oxidizing_agent",
        "supplies": ["carboxylic_acid", "ketone"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010458","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },
    "pyridinium_chlorochromate": {
        "smiles": "C1=CC=[NH+]C=C1.[O-][Cr](Cl)(=O)=O", "role": "oxidizing_agent",
        "supplies": ["aldehyde", "ketone"],
        "D":"\U0001045B","T":"\U00010465","R":"\U00010451","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },

    # ── Indole / Tryptamine precursors ──
    "tryptamine": {
        "smiles": "NCCc1c[nH]c2ccccc12", "role": "nucleophile",
        "supplies": ["amine", "aromatic_ring", "cyclic"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "indole": {
        "smiles": "c1ccc2[nH]ccc2c1", "role": "nucleophile",
        "supplies": ["aromatic_ring", "cyclic"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U00010479","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "gramine": {
        "smiles": "CN(C)Cc1c[nH]c2ccccc12", "role": "electrophile",
        "supplies": ["amine", "aromatic_ring", "cyclic"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046C","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "indole_3_acetaldehyde": {
        "smiles": "O=CCc1c[nH]c2ccccc12", "role": "electrophile",
        "supplies": ["aldehyde", "aromatic_ring", "cyclic"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "skatole": {
        "smiles": "Cc1c[nH]c2ccccc12", "role": "nucleophile",
        "supplies": ["aromatic_ring", "cyclic", "alkane"],
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U00010479","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    # ── Polycyclic framework precursors ──
    "cyclopentadiene": {
        "smiles": "C1C=CC=C1", "role": "diene",
        "supplies": ["cyclic", "alkene"],
        "D":"\U0001045B","T":"\U00010470","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010464","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },
    "maleic_anhydride": {
        "smiles": "O=C1OC(=O)C=C1", "role": "dienophile",
        "supplies": ["carbonyl", "alkene", "cyclic"],
        "D":"\U00010468","T":"\U00010470","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },
    "benzoquinone": {
        "smiles": "O=C1C=CC(=O)C=C1", "role": "dienophile",
        "supplies": ["ketone", "alkene", "cyclic"],
        "D":"\U00010468","T":"\U00010465","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },
    # ── Deuteration agents ──
    "deuterium_oxide": {
        "smiles": "[2H]O[2H]", "role": "deuterating_agent",
        "supplies": ["alcohol"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
    },
    "lithium_aluminum_deuteride": {
        "smiles": "[Li+].[Al]([2H])([2H])([2H])[2H-]", "role": "deuterating_reducing_agent",
        "supplies": ["alcohol", "amine"],
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U00010472","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },

    # ── Amide suppliers ──
    "acetamide": {
        "smiles": "CC(=O)N", "role": "amide_source",
        "supplies": ["amide", "carbonyl"],
    },
    "formamide": {
        "smiles": "O=CN", "role": "amide_source",
        "supplies": ["amide", "aldehyde"],
    },
    # ── Nitrile suppliers ──
    "acetonitrile": {
        "smiles": "CC#N", "role": "nitrile_source",
        "supplies": ["nitrile"],
    },
    # ── Halide suppliers ──
    "thionyl_chloride": {
        "smiles": "ClS(Cl)=O", "role": "halogenating_agent",
        "supplies": ["halide"],
    },
    "phosphorus_tribromide": {
        "smiles": "BrP(Br)Br", "role": "halogenating_agent",
        "supplies": ["halide"],
    },
    # ── Carboxylic acid suppliers ──
    "acetic_acid": {
        "smiles": "CC(=O)O", "role": "acid_source",
        "supplies": ["carboxylic_acid"],
    },
    "benzoic_acid": {
        "smiles": "O=C(O)c1ccccc1", "role": "acid_source",
        "supplies": ["carboxylic_acid", "aromatic_ring"],
    },
    # ── Ether suppliers ──
    "diethyl_ether": {
        "smiles": "CCOCC", "role": "ether_source",
        "supplies": ["ether"],
    },
    # ── Nitro suppliers ──
    "nitric_acid": {
        "smiles": "O[N+](=O)[O-]", "role": "nitrating_agent",
        "supplies": ["nitro"],
    },
    # ── Epoxide suppliers ──
    "ethylene_oxide": {
        "smiles": "C1CO1", "role": "epoxide_source",
        "supplies": ["epoxide"],
    },
    # ── Diazonium suppliers ──
    "sodium_nitrite": {
        "smiles": "[Na+].[O-]N=O", "role": "diazotizing_agent",
        "supplies": ["diazonium"],
    },
    # ── Sulfur/thiol suppliers ──
    "hydrogen_sulfide": {
        "smiles": "S", "role": "thiol_source",
        "supplies": ["thiol"],
    },
}

# ====================================================================
# GRAMMAR-TYPED SOLVENT DATABASE
# Each solvent carries a 12-primitive structural type.
# Solvents are selected by structural proximity to meet(FG1, FG2).
# ====================================================================

SOLVENT_DB = {
    "water": {
        "bp_C": 100, "polarity": "protic_polar", "dielectric": 80.0,
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U0001045E",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
    },
    "methanol": {
        "bp_C": 65, "polarity": "protic_polar", "dielectric": 33.0,
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U00010457","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "ethanol": {
        "bp_C": 78, "polarity": "protic_polar", "dielectric": 24.5,
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U00010457","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "dichloromethane": {
        "bp_C": 40, "polarity": "aprotic_polar", "dielectric": 9.1,
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "acetonitrile": {
        "bp_C": 82, "polarity": "aprotic_polar", "dielectric": 37.5,
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },
    "tetrahydrofuran": {
        "bp_C": 66, "polarity": "aprotic_polar", "dielectric": 7.5,
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "diethyl_ether": {
        "bp_C": 35, "polarity": "aprotic_nonpolar", "dielectric": 4.3,
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
    },
    "toluene": {
        "bp_C": 111, "polarity": "aprotic_nonpolar", "dielectric": 2.4,
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U00010479","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "dimethylformamide": {
        "bp_C": 153, "polarity": "aprotic_polar", "dielectric": 36.7,
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047D","P":"\U0001046C","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U00010474",
    },
    "dimethyl_sulfoxide": {
        "bp_C": 189, "polarity": "aprotic_polar", "dielectric": 46.7,
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047D","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010473","W":"\U00010474",
    },
    "hexane": {
        "bp_C": 69, "polarity": "nonpolar", "dielectric": 1.9,
        "D":"\U0001045B","T":"\U00010461","R":"\U00010451","P":"\U00010457","F":"\U0001045E",
        "K":"\U00010464","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "ethyl_acetate": {
        "bp_C": 77, "polarity": "aprotic_moderate", "dielectric": 6.0,
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047D","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010473","W":"\U00010477",
    },
}

# ====================================================================
# GRAMMAR-TYPED CATALYST DATABASE
# Catalysts are selected based on the Ph (criticality) delta.
# ====================================================================

CATALYST_DB = {
    # Lewis acids
    "aluminum_trichloride": {
        "type": "lewis_acid", "smiles": "Cl[Al](Cl)Cl",
        "Ph_bridge": (0.3, 0.8),
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "boron_trifluoride": {
        "type": "lewis_acid", "smiles": "FB(F)F",
        "Ph_bridge": (0.3, 0.8),
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "zinc_chloride": {
        "type": "lewis_acid", "smiles": "Cl[Zn]Cl",
        "Ph_bridge": (0.3, 0.8),
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    # Transition metal
    "palladium_on_carbon": {
        "type": "transition_metal", "smiles": "[Pd]",
        "Ph_bridge": (0.8, 1.5),
        "D":"\U00010468","T":"\U00010470","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },
    "tetrakis_triphenylphosphine_palladium": {
        "type": "transition_metal", "smiles": "[Pd](P(c1ccccc1)(c2ccccc2)c3ccccc3)(P(c4ccccc4)(c5ccccc5)c6ccccc6)(P(c7ccccc7)(c8ccccc8)c9ccccc9)P(c%10ccccc%10)(c%11ccccc%11)c%12ccccc%12",
        "Ph_bridge": (0.8, 1.5),
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U00010479","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
    "copper_iodide": {
        "type": "transition_metal", "smiles": "[Cu]I",
        "Ph_bridge": (0.8, 1.5),
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    # Organocatalysts
    "L_proline": {
        "type": "organocatalyst", "smiles": "OC(=O)[C@@H]1CCCN1",
        "Ph_bridge": (1.5, 3.0),
        "D":"\U0001045B","T":"\U00010465","R":"\U0001047E","P":"\U0001046C","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U00010474",
    },
    "DMAP": {
        "type": "organocatalyst", "smiles": "CN(C)c1ccncc1",
        "Ph_bridge": (1.5, 3.0),
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010456","S":"\U00010473","W":"\U0001046D",
    },
}

# ====================================================================
# GRAMMAR-TYPED ACTIVATING AGENTS (coupling reagents)
# ====================================================================

ACTIVATOR_DB = {
    "DCC": {
        "smiles": "C1CCC(CC1)N=C=NC2CCCCC2", "type": "carbodiimide",
        "R_bridge": (1.5, 2.5),
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U0001046C","F":"\U00010450",
        "K":"\U00010467","G":"\U00010472","Gm":"\U00010460","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010473","W":"\U00010474",
    },
    "EDC": {
        "smiles": "CCN=C=NCCCN(C)C", "type": "carbodiimide",
        "R_bridge": (1.5, 2.5),
        "D":"\U0001045B","T":"\U00010461","R":"\U0001047D","P":"\U0001046C","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "HOBt": {
        "smiles": "O=N1C=CC=C1", "type": "additive",
        "R_bridge": (1.5, 2.5),
        "D":"\U00010468","T":"\U00010478","R":"\U0001047E","P":"\U0001046F","F":"\U00010450",
        "K":"\U00010467","G":"\U0001045A","Gm":"\U0001045D","Ph":"\u2299",
        "H":"\U00010452","S":"\U00010459","W":"\U00010474",
    },
    "sodium_ethoxide": {
        "smiles": "CC[O-].[Na+]", "type": "alkoxide_base",
        "R_bridge": (0.5, 1.5),
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U00010450",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010452","S":"\U00010459","W":"\U00010477",
    },
    "sodium_hydride": {
        "smiles": "[H-].[Na+]", "type": "strong_base",
        "R_bridge": (0.5, 1.5),
        "D":"\U0001045B","T":"\U00010461","R":"\U00010469","P":"\U00010457","F":"\U0001045E",
        "K":"\U00010458","G":"\U0001045A","Gm":"\U0001045D","Ph":"\U00010462",
        "H":"\U00010453","S":"\U00010459","W":"\U00010477",
    },
}

# ====================================================================
# WORKUP DATABASE — derived from product/reactant structural gap
# ====================================================================

WORKUP_STRATEGIES = {
    # By structural gap magnitude
    "minimal": {
        "description": "Concentration in vacuo, direct use or recrystallization",
        "steps": ["concentrate under reduced pressure", "recrystallize from appropriate solvent"]
    },
    "standard": {
        "description": "Aqueous quench + organic extraction",
        "steps": ["quench with water or saturated NH4Cl", "extract with organic solvent (3x)", "dry over MgSO4 or Na2SO4", "filter and concentrate"]
    },
    "intensive": {
        "description": "Multiple washes + chromatography",
        "steps": ["quench carefully", "extract", "wash with brine, water, saturated NaHCO3", "dry, filter, concentrate", "purify by flash column chromatography"]
    },
    "complex": {
        "description": "Full separation cascade",
        "steps": ["quench with controlled pH", "extract with specified solvent", "sequential washes (acid, base, neutral)", "dry, filter, concentrate", "column chromatography", "optional: HPLC or recrystallization"]
    },
}

# ====================================================================
# SIMPLE STARTING MATERIALS — molecules considered commercially available.
# These are reagent names that do NOT need further retrosynthetic decomposition.
# ====================================================================

# Every reagent in REAGENT_DB is considered a commercially available building block.
# Additional materials below are common solvents/inorganics that may appear as reactants.
SIMPLE_STARTING_MATERIALS = set(REAGENT_DB.keys()) | {
    "water", "oxygen", "hydrogen", "nitrogen", "carbon_dioxide",
    "sodium_chloride", "sodium_sulfate", "magnesium_sulfate",
    "hydrochloric_acid", "sulfuric_acid", "nitric_acid", "phosphoric_acid",
    "sodium_bicarbonate", "ammonium_chloride", "sodium_nitrite",
    "hydrogen_peroxide", "acetic_acid", "formic_acid",
    "ethylene", "propylene", "butadiene", "isoprene",
    "carbon_monoxide", "sulfur", "iodine", "bromine", "chlorine",
    "lithium", "sodium", "potassium", "magnesium", "zinc", "iron",
    "calcium_hydroxide", "sodium_carbonate", "potassium_hydroxide",
    "sodium_cyanoborohydride", "sodium_triacetoxyborohydride",
    "borane", "diborane", "dimethyl_sulfide", "trimethylamine",
    "triethylamine", "pyridine", "lutidine", "DBU", "DIPEA",
    "diethyl_ether", "hexane", "pentane", "heptane",
    "ethyl_acetate", "acetone", "acetonitrile", "dichloromethane",
    "chloroform", "methanol", "ethanol", "isopropanol", "butanol",
    "tetrahydrofuran", "dimethylformamide", "dimethyl_sulfoxide",
    "toluene", "benzene", "xylene", "dioxane", "NMP",
}

# Reagents that ARE simple (in REAGENT_DB) are already included above.
# But we also want to recognize reagent names that might come back as
# sub-target analysis results (like "indole" -> find_fgs -> ["aromatic_ring", "cyclic"]).
# Those ARE in REAGENT_DB already, so they're covered.

def is_simple_material(name, compiler=None):
    """Check if a molecule name corresponds to a simple, commercially available starting material.
    
    Returns True if:
      1. Exact name match in SIMPLE_STARTING_MATERIALS, OR
      2. REAGENT_DB has an entry for it, OR  
      3. Molecule has <= 1 functional group (too simple to disconnect), OR
      4. No viable disconnections found (cannot be further decomposed)
    """
    name_lower = name.lower().replace(" ", "_").replace("-", "_")
    
    # Direct match
    if name_lower in SIMPLE_STARTING_MATERIALS:
        return True
    if name in SIMPLE_STARTING_MATERIALS:
        return True
    if name_lower in REAGENT_DB:
        return True
    
    # If compiler is available, check if the molecule can be further decomposed
    if compiler is not None:
        try:
            fgs = compiler.find_fgs_direct(name) if hasattr(compiler, 'find_fgs_direct') else []
            if not fgs:
                from compiler import find_fgs
                fgs = find_fgs(name)
            # Single FG = too simple for further disconnection
            if len(fgs) <= 1:
                return True
            # Try to find disconnections; if none, it's terminal
            mol_type, source = compiler.get_molecule_type_direct(name) if hasattr(compiler, 'get_molecule_type_direct') else (None, None)
            if mol_type is None:
                from compiler import get_molecule_type
                mol_type, source = get_molecule_type(name, compiler.catalog)
            if mol_type:
                from compiler import find_disconnections
                cuts = find_disconnections(fgs, mol_type, max_results=3)
                if not cuts:
                    return True  # No disconnections → terminal
        except Exception:
            pass
    
    return False


# ====================================================================
# DERIVATION ENGINE
# ====================================================================

def per_primitive_delta(bond_type, meet_type_dict):
    """Compute the primitive-wise delta between bond and meet(FG1, FG2).
    Returns dict of {primitive_name: (delta_value, bond_glyph, meet_glyph)}.
    """
    deltas = {}
    for p in PNAMES:
        bo = glyph_ord(p, bond_type.get(p, "?"))
        mo = glyph_ord(p, meet_type_dict.get(p, "?"))
        d = bo - mo
        if d > 0.001:
            deltas[p] = {"delta": round(d, 3), "bond": bond_type.get(p, "?"), "meet": meet_type_dict.get(p, "?")}
    return deltas


def map_delta_to_condition(primitive, delta_val):
    """Map a single primitive delta value to its physical condition."""
    mapping = PRIMITIVE_TO_CONDITION.get(primitive, {})
    delta_map = mapping.get("delta_map", {})
    for (lo, hi), conditions in delta_map.items():
        if lo <= delta_val < hi:
            return {"primitive": primitive, "name": mapping.get("name", primitive), **conditions}
    # Fallback: return last range
    if delta_map:
        last_range = list(delta_map.values())[-1]
        return {"primitive": primitive, "name": mapping.get("name", primitive), **last_range}
    return {"primitive": primitive, "name": mapping.get("name", "unknown"), "value": delta_val}


def derive_conditions_from_disconnection(fg1_type, fg2_type, bond_type):
    """Core derivation: given FG structural types and bond type, derive ALL reaction conditions.

    Returns a dict with: temperature, pressure, solvent, catalyst, activator,
    addition_order, stoichiometry, protecting_groups, stereochemistry, workup.
    """
    face = meet_type(fg1_type, fg2_type)
    deltas = per_primitive_delta(bond_type, face)

    conditions = {}
    conditions["delta_summary"] = {}
    for p, dinfo in sorted(deltas.items()):
        cond = map_delta_to_condition(p, dinfo["delta"])
        conditions["delta_summary"][p] = cond
        conditions[p] = cond

    return conditions, deltas, face


def select_solvent(face_type):
    """Select the best solvent by minimal structural distance to the FG meet type."""
    best = None
    best_dist = float("inf")
    for name, sinfo in SOLVENT_DB.items():
        st = {p: sinfo.get(p, "?") for p in PNAMES}
        d, _ = tup_dist(face_type, st)
        if d < best_dist:
            best_dist = d
            best = {"name": name, "distance": round(d, 3), **sinfo}
    return best


def select_catalyst(ph_delta):
    """Select catalyst based on criticality delta magnitude."""
    best = None
    for name, cinfo in CATALYST_DB.items():
        lo, hi = cinfo.get("Ph_bridge", (0, 0))
        if lo <= ph_delta < hi:
            if best is None or abs(ph_delta - (lo + hi) / 2) < abs(ph_delta - sum(best.get("Ph_bridge", (0, 0))) / 2):
                best = {"name": name, **cinfo}
    return best


def select_activator(r_delta):
    """Select coupling activator based on R delta."""
    best = None
    for name, ainfo in ACTIVATOR_DB.items():
        lo, hi = ainfo.get("R_bridge", (0, 0))
        if lo <= r_delta < hi:
            return {"name": name, **ainfo}
    return None


def select_reactants(fg1_name, fg2_name, bond_name):
    """Select concrete reactants from the reagent DB by FG supply compatibility."""
    candidates_1 = []
    candidates_2 = []
    for name, rinfo in REAGENT_DB.items():
        supplies = rinfo.get("supplies", [])
        # Reactant supplies the FG (or a precursor to it)
        if fg1_name in supplies or any(s in fg1_name for s in supplies):
            candidates_1.append({"name": name, **rinfo})
        if fg2_name in supplies or any(s in fg2_name for s in supplies):
            candidates_2.append({"name": name, **rinfo})

    # Rank by structural distance to the FG type
    # (Use FG types from the compiler module)
    from compiler import FG as FG_TYPES
    fg1_t = FG_TYPES.get(fg1_name, {})
    fg2_t = FG_TYPES.get(fg2_name, {})

    def rank(candidates, fg_type):
        ranked = []
        for c in candidates:
            ct = {p: c.get(p, "?") for p in PNAMES}
            d, _ = tup_dist(fg_type, ct)
            ranked.append({"name": c["name"], "smiles": c["smiles"],
                           "role": c["role"], "distance": round(d, 3)})
        ranked.sort(key=lambda x: x["distance"])
        return ranked

    return {
        "fg1_reactants": rank(candidates_1, fg1_t),
        "fg2_reactants": rank(candidates_2, fg2_t),
    }


def select_workup(total_delta):
    """Select workup strategy based on total structural gap magnitude."""
    if total_delta < 1.0:
        return WORKUP_STRATEGIES["minimal"]
    elif total_delta < 2.5:
        return WORKUP_STRATEGIES["standard"]
    elif total_delta < 5.0:
        return WORKUP_STRATEGIES["intensive"]
    else:
        return WORKUP_STRATEGIES["complex"]


def derive_temperature(k_delta):
    """Derive temperature from K (kinetics) delta."""
    mapping = PRIMITIVE_TO_CONDITION["K"]["delta_map"]
    for (lo, hi), cond in mapping.items():
        if lo <= k_delta < hi:
            return cond
    return {"T_C": (20, 30), "regime": "ambient"}

# ====================================================================
# REACTION DERIVER — Main Class
# ====================================================================

# ====================================================================
# DEFAULT CONDITIONS (applied when primitive has zero delta)
# ====================================================================

DEFAULT_CONDITIONS = {
    "D": {"molecularity": "bimolecular", "activation": "thermal"},
    "T": {"steric": "none", "orientation": "no_preference"},
    "R": {"mode": "direct_combination", "activator": "none"},
    "P": {"stereo": "racemic_OK", "ee_requirement": 0},
    "F": {"regime": "classical", "solvent_polarity": "any"},
    "K": {"T_C": (20, 30), "regime": "ambient"},
    "G": {"conc_M": (0.5, 2.0), "regime": "standard"},
    "Gm": {"order": "all_at_once", "timing": "single_portion"},
    "Ph": {"catalyst": "none", "reason": "below_critical"},
    "H": {"chiral": "none", "auxiliary": "not_needed"},
    "S": {"ratio": "1:1", "excess": 0},
    "W": {"protect": "none", "strategy": "open_air_OK"},
}

@dataclass
class DerivedReaction:
    """Complete derived reaction specification for one disconnection."""
    fg1: str
    fg2: str
    bond: str
    bond_desc: str
    structural_delta: float

    # Derived conditions (per-primitive)
    temperature: Dict = field(default_factory=dict)
    solvent: Dict = field(default_factory=dict)
    catalyst: Optional[Dict] = None
    activator: Optional[Dict] = None
    addition_order: Dict = field(default_factory=dict)
    stoichiometry: Dict = field(default_factory=dict)
    stereochemistry: Dict = field(default_factory=dict)
    protecting_groups: Dict = field(default_factory=dict)
    concentration: Dict = field(default_factory=dict)
    molecularity: Dict = field(default_factory=dict)
    chiral_induction: Dict = field(default_factory=dict)
    fidelity_regime: Dict = field(default_factory=dict)

    # Reactants
    reactants: Dict = field(default_factory=dict)

    # Workup
    workup: Dict = field(default_factory=dict)

    # Raw deltas
    deltas: Dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "disconnection": f"{self.fg1} + {self.fg2} via {self.bond}",
            "bond_description": self.bond_desc,
            "structural_delta": self.structural_delta,
            "temperature": self.temperature,
            "solvent": self.solvent,
            "catalyst": self.catalyst,
            "activator": self.activator,
            "addition_order": self.addition_order,
            "stoichiometry": self.stoichiometry,
            "stereochemistry": self.stereochemistry,
            "protecting_groups": self.protecting_groups,
            "concentration": self.concentration,
            "molecularity": self.molecularity,
            "chiral_induction": self.chiral_induction,
            "fidelity_regime": self.fidelity_regime,
            "reactants": self.reactants,
            "workup": self.workup,
            "primitive_deltas": self.deltas,
        }

    def print_procedure(self):
        """Print a human-readable reaction procedure derived from grammar."""
        info_line(f"\n{'='*70}")
        info_line(f"  REACTION: {self.fg1} + {self.fg2}  via  {self.bond}")
        info_line(f"  Bond: {self.bond_desc}")
        info_line(f"  Structural Delta: {self.structural_delta:.3f}")
        info_line(f"{'='*70}")

        # Mechanism class
        mol = self.molecularity.get("molecularity", "unknown")
        act = self.molecularity.get("activation", "unknown")
        info_line(f"\n  Mechanism Class: {mol} ({act})")

        # Reactants
        info_line(f"\n  ── REACTANTS ──")
        fg1r = self.reactants.get("fg1_reactants", [])
        fg2r = self.reactants.get("fg2_reactants", [])
        if fg1r:
            best1 = fg1r[0]
            info_line(f"  [{self.fg1}] Best: {best1['name']}  (d={best1['distance']:.3f})  [{best1['smiles']}]")
            if len(fg1r) > 1:
                info_line(f"           Alternatives: {', '.join(r['name'] for r in fg1r[1:4])}")
        if fg2r:
            best2 = fg2r[0]
            info_line(f"  [{self.fg2}] Best: {best2['name']}  (d={best2['distance']:.3f})  [{best2['smiles']}]")
            if len(fg2r) > 1:
                info_line(f"           Alternatives: {', '.join(r['name'] for r in fg2r[1:4])}")

        # Solvent
        if self.solvent:
            s = self.solvent
            info_line(f"\n  ── SOLVENT ──")
            info_line(f"  {s['name']}  (bp {s.get('bp_C','?')} °C, d={s.get('distance','?')}, {s.get('polarity','?')})")

        # Conditions
        info_line(f"\n  ── CONDITIONS ──")
        T = self.temperature
        info_line(f"  Temperature: {T.get('T_C', (20,30))} °C  [{T.get('regime','?')}]")
        conc = self.concentration
        info_line(f"  Concentration: {conc.get('conc_M', (0.5,2.0))} M  [{conc.get('regime','?')}]")
        ao = self.addition_order
        info_line(f"  Addition: {ao.get('order','?')} ({ao.get('timing','?')})")
        stoich = self.stoichiometry
        info_line(f"  Stoichiometry: {stoich.get('ratio','1:1')}")

        # Catalyst / Activator
        if self.catalyst:
            c = self.catalyst
            info_line(f"\n  ── CATALYST ──")
            info_line(f"  {c['name']} ({c['type']})  [{c['smiles']}]")
            info_line(f"  Reason: {c.get('Ph_bridge','?')}")
        if self.activator:
            a = self.activator
            info_line(f"\n  ── ACTIVATOR ──")
            info_line(f"  {a['name']} ({a['type']})  [{a['smiles']}]")

        # Stereo
        stereo = self.stereochemistry
        if stereo.get("ee_requirement", 0) > 0:
            info_line(f"\n  ── STEREOCHEMISTRY ──")
            info_line(f"  {stereo.get('stereo','?')}  (ee > {stereo.get('ee_requirement',0)}%)")

        # Chirality
        chiral = self.chiral_induction
        if chiral.get("chiral", "none") != "none":
            info_line(f"\n  ── CHIRAL INDUCTION ──")
            info_line(f"  Strategy: {chiral.get('chiral','?')}  [{chiral.get('auxiliary','?')}]")

        # Protecting groups
        pg = self.protecting_groups
        if pg.get("protect", "none") != "none":
            info_line(f"\n  ── PROTECTING GROUPS ──")
            info_line(f"  Level: {pg.get('protect','?')}  [{pg.get('strategy','?')}]")

        # Workup
        wu = self.workup
        info_line(f"\n  ── WORKUP ──")
        info_line(f"  Strategy: {wu.get('description','?')}")
        for i, step in enumerate(wu.get("steps", []), 1):
            info_line(f"    {i}. {step}")

        # Primitive deltas (diagnostic)
        if self.deltas:
            info_line(f"\n  ── PRIMITIVE DELTAS (bond - meet) ──")
            for p in PNAMES:
                if p in self.deltas:
                    d = self.deltas[p]
                    info_line(f"  {p}: Δ={d['delta']:.3f}  (bond={d['bond']}, meet={d['meet']})")


class ReactionDeriver:
    """Grammar-first reaction condition deriver.

    Takes a ch3mpiler disconnection and derives complete reaction specifications
    from the 12-primitive structural algebra — NO named reactions, NO convention.
    """
    def __init__(self):
        self.fg_types = None  # loaded from compiler on first use

    def _load_fg_types(self):
        if self.fg_types is not None:
            return
        try:
            from compiler import FG as FG_TYPES
            self.fg_types = FG_TYPES
        except ImportError:
            # Fallback: load ch3mpiler directly
            sys.path.insert(0, str(BASE.parent.parent / "imscribing_grammar"))
            try:
                from ch3mpiler import FG as FG_TYPES
                self.fg_types = FG_TYPES
            except ImportError:
                info_line("Warning: Could not load FG type definitions")
                self.fg_types = {}

    def derive(self, disconnection):
        """Derive complete reaction conditions for one disconnection.

        Args:
            disconnection: dict with keys fg1, fg2, bond, bond_desc, delta
                          (as returned by ch3mpiler's evaluate_disconnection/find_disconnections)

        Returns:
            DerivedReaction with all conditions filled in.
        """
        self._load_fg_types()

        fg1_name = disconnection["fg1"]
        fg2_name = disconnection["fg2"]
        bond_name = disconnection["bond"]

        # Get structural types
        fg1_type = self.fg_types.get(fg1_name, {})
        fg2_type = self.fg_types.get(fg2_name, {})

        # Bond type from compiler
        try:
            from compiler import BOND_TYPES
        except ImportError:
            sys.path.insert(0, str(BASE.parent.parent / "imscribing_grammar"))
            from ch3mpiler import BOND_TYPES

        bond_type = BOND_TYPES.get(bond_name, {})

        if not fg1_type or not fg2_type or not bond_type:
            return None

        # Compute per-primitive deltas
        conditions, deltas, face = derive_conditions_from_disconnection(
            fg1_type, fg2_type, bond_type
        )

        # Extract per-primitive conditions
        k_delta = deltas.get("K", {}).get("delta", 0)
        ph_delta = deltas.get("Ph", {}).get("delta", 0)
        r_delta = deltas.get("R", {}).get("delta", 0)
        total_delta = disconnection.get("delta", sum(d["delta"] for d in deltas.values()))

        rxn = DerivedReaction(
            fg1=fg1_name,
            fg2=fg2_name,
            bond=bond_name,
            bond_desc=disconnection.get("bond_desc", bond_name),
            structural_delta=disconnection.get("delta", 0.0),
            deltas=deltas,
        )

        # Fill in conditions from primitive deltas
        if "D" in conditions:
            rxn.molecularity = conditions["D"]
        if "K" in conditions:
            rxn.temperature = conditions["K"]
        if "G" in conditions:
            rxn.concentration = conditions["G"]
        if "Gm" in conditions:
            rxn.addition_order = conditions["Gm"]
        if "P" in conditions:
            rxn.stereochemistry = conditions["P"]
        if "W" in conditions:
            rxn.protecting_groups = conditions["W"]
        if "H" in conditions:
            rxn.chiral_induction = conditions["H"]
        if "F" in conditions:
            rxn.fidelity_regime = conditions["F"]
        if "S" in conditions:
            rxn.stoichiometry = conditions["S"]

        # Apply defaults for any un-set condition fields
        if not rxn.temperature:
            rxn.temperature = DEFAULT_CONDITIONS["K"]
        if not rxn.concentration:
            rxn.concentration = DEFAULT_CONDITIONS["G"]
        if not rxn.addition_order:
            rxn.addition_order = DEFAULT_CONDITIONS["Gm"]
        if not rxn.stereochemistry:
            rxn.stereochemistry = DEFAULT_CONDITIONS["P"]
        if not rxn.protecting_groups:
            rxn.protecting_groups = DEFAULT_CONDITIONS["W"]
        if not rxn.chiral_induction:
            rxn.chiral_induction = DEFAULT_CONDITIONS["H"]
        if not rxn.fidelity_regime:
            rxn.fidelity_regime = DEFAULT_CONDITIONS["F"]
        if not rxn.molecularity:
            rxn.molecularity = DEFAULT_CONDITIONS["D"]
        if not rxn.stoichiometry:
            rxn.stoichiometry = DEFAULT_CONDITIONS["S"]

        # Solvent
        rxn.solvent = select_solvent(face)

        # Catalyst
        if ph_delta > 0.3:
            rxn.catalyst = select_catalyst(ph_delta)

        # Activator (coupling agent)
        if r_delta > 0.5:
            rxn.activator = select_activator(r_delta)

        # Reactants
        rxn.reactants = select_reactants(fg1_name, fg2_name, bond_name)

        # Workup
        rxn.workup = select_workup(total_delta)

        return rxn

    def derive_all(self, disconnections, limit=5):
        """Derive reactions for a list of disconnections."""
        results = []
        for i, disc in enumerate(disconnections[:limit]):
            rxn = self.derive(disc)
            if rxn:
                results.append(rxn)
        return results

    def derive_from_ch3mpiler_result(self, ch3mpiler_result):
        """Take a full ch3mpiler analyze() result and derive reactions for all cuts."""
        cuts = ch3mpiler_result.get("cuts", [])
        return self.derive_all(cuts)

    def print_all(self, reactions):
        """Print all derived reactions."""
        for i, rxn in enumerate(reactions):
            rxn.print_procedure()

    def to_procedure_document(self, target_name, reactions):
        """Generate a complete reaction procedure document as a dict."""
        doc = {
            "target": target_name,
            "generated_by": "reaction_deriver.py (grammar-first, no named reactions)",
            "num_disconnections": len(reactions),
            "reactions": [r.to_dict() for r in reactions],
        }
        return doc

# ====================================================================
# CLI
# ====================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="reaction_deriver — Grammar-first reaction condition derivation (no named reactions)")
    parser.add_argument("--target", help="Molecule name (same as ch3mpiler --target)")
    parser.add_argument("--cas", help="CAS Registry Number")
    parser.add_argument("--disconnection", nargs=3,
                        metavar=("FG1", "FG2", "BOND"),
                        help="Manual: FG1 FG2 bond_type (e.g. alcohol amine amide_link)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--limit", type=int, default=5, help="Max disconnections to process")
    parser.add_argument("--list-solvents", action="store_true")
    parser.add_argument("--list-catalysts", action="store_true")
    parser.add_argument("--list-activators", action="store_true")
    parser.add_argument("--list-reagents", action="store_true")
    parser.add_argument("--list-bonds", action="store_true")
    args = parser.parse_args()

    deriver = ReactionDeriver()

    if args.list_solvents:
        info_line("Grammar-typed Solvents:")
        for name, s in sorted(SOLVENT_DB.items()):
            t = {p: s.get(p, "?") for p in PNAMES}
            info_line(f"  {name:25s}  bp={s['bp_C']:4d} C  pol={s['polarity']:20s}  {fmt_tup(t)}")
        return

    if args.list_catalysts:
        info_line("Grammar-typed Catalysts:")
        for name, c in sorted(CATALYST_DB.items()):
            info_line(f"  {name:40s}  {c['type']:20s}  Ph_bridge={c['Ph_bridge']}")
        return

    if args.list_activators:
        info_line("Grammar-typed Activators:")
        for name, a in sorted(ACTIVATOR_DB.items()):
            info_line(f"  {name:25s}  {a['type']:20s}  R_bridge={a['R_bridge']}")
        return

    if args.list_reagents:
        info_line("Grammar-typed Reagents:")
        for name, r in sorted(REAGENT_DB.items()):
            info_line(f"  {name:30s}  {r['role']:20s}  supplies={r['supplies']}  {r['smiles']}")
        return

    if args.list_bonds:
        info_line("Use ch3mpiler --list-bonds for bond types")
        return

    # Manual disconnection
    if args.disconnection:
        fg1, fg2, bond = args.disconnection
        disc = {"fg1": fg1, "fg2": fg2, "bond": bond, "bond_desc": bond, "delta": 0.0}
        rxn = deriver.derive(disc)
        if rxn:
            if args.json:
                import json
                print(json.dumps(rxn.to_dict(), indent=2, ensure_ascii=False))
            else:
                rxn.print_procedure()
        else:
            error_line(f"ERROR: Could not derive reaction for {fg1} + {fg2} via {bond}")
            info_line("Check that FGs and bond are defined in ch3mpiler's FG/BOND_TYPES dictionaries")
        return

    # CAS-based
    if args.cas:
        sys.path.insert(0, str(BASE))
        from compiler import Ch3mpiler
        ch = Ch3mpiler()
        result = ch.resolve_and_analyze(args.cas)
        name = result.get("cas_info", {}).get("name", args.cas)
        info_line(f"Target: {name}")
        info_line(f"Type: {result.get('type', '?')}")
        info_line(f"FGs: {result.get('fgs', [])}")

        cuts = result.get("cuts", [])
        if not cuts:
            info_line("No disconnections found.")
            return

        reactions = deriver.derive_all(cuts, limit=args.limit)
        if args.json:
            import json
            doc = deriver.to_procedure_document(name, reactions)
            print(json.dumps(doc, indent=2, ensure_ascii=False))
        else:
            deriver.print_all(reactions)
        return

    # Target molecule
    if args.target:
        sys.path.insert(0, str(BASE))
        from compiler import Ch3mpiler
        ch = Ch3mpiler()
        result = ch.analyze(args.target)
        info_line(f"Target: {result['target']}")
        info_line(f"Type: {result['type']} [{result.get('type_source', '?')}]")
        info_line(f"FGs: {result.get('fgs', [])}")

        cuts = result.get("cuts", [])
        if not cuts:
            info_line("No disconnections found.")
            return

        reactions = deriver.derive_all(cuts, limit=args.limit)
        if args.json:
            import json

            doc = deriver.to_procedure_document(args.target, reactions)
            print(json.dumps(doc, indent=2, ensure_ascii=False))
        else:
            deriver.print_all(reactions)
        return

    # Default: demo
    info_line("=" * 70)
    info_line("  reaction_deriver — Grammar-First Reaction Condition Derivation")
    info_line("  No named reactions — conditions derived from 12-primitive algebra")
    info_line("=" * 70)
    print()
    info_line("Demo: benzaldehyde + amine via amide_link")
    info_line("(First, forming an imine with aniline)")
    disc = {"fg1": "amine", "fg2": "aldehyde", "bond": "cn_sigma",
            "bond_desc": "C-N sigma bond (imine formation)", "delta": 1.5}
    rxn = deriver.derive(disc)
    if rxn:
        rxn.print_procedure()
    print()
    info_line("Try: python reaction_deriver.py --target benzaldehyde")
    info_line("     python reaction_deriver.py --target aspirin")
    info_line("     python reaction_deriver.py --disconnection alcohol acid ester_link")


if __name__ == "__main__":
    main()


