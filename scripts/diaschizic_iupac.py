#!/usr/bin/env python3
"""
diaschizic_iupac.py — IUPAC Systematic Name Generator for Diaschizics
======================================================================
Takes the 11 diaschizic compounds (5 first-generation + 6 second-generation)
and generates systematic IUPAC-style chemical names based on:
  - Pharmacophore scaffold (derived from structural primitives)
  - Primitive-to-substituent mapping (12-primitive tuple → IUPAC features)
  - Stereochemical descriptors (R/S, E/Z, atropisomer)
  - Topological descriptors (catenane, rotaxane, spiro, bridged)

The mapping is principled: each primitive value constrains a specific
aspect of the IUPAC name following the structural logic of diaschizics_design.md.

Author: Lando⊗⊙perator
"""

import json, math, sys, os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# ─── PRIMITIVE ORDINALS (from shared/primitives.py) ──────────────

ORDINALS = {
    "Ð": {"𐑛": 0, "𐑨": 1, "𐑼": 2, "𐑦": 3},
    "Þ": {"𐑡": 0, "𐑰": 1, "𐑥": 2, "𐑶": 3, "𐑸": 4},
    "Ř": {"𐑩": 0, "𐑑": 1, "𐑽": 2, "𐑾": 3},
    "Φ": {"𐑗": 0, "𐑿": 1, "𐑬": 2, "𐑯": 3, "𐑹": 4},
    "ƒ": {"𐑱": 0, "𐑞": 1, "𐑐": 2},
    "Ç": {"𐑺": 0, "𐑪": 1, "𐑧": 2, "𐑤": 3, "𐑘": 4},
    "Γ": {"𐑚": 0, "𐑔": 1, "𐑲": 2},
    "ɢ": {"𐑝": 0, "𐑜": 1, "𐑠": 2, "𐑵": 3},
    "⊙": {"𐑢": 0, "⊙": 1, "𐑮": 2, "𐑻": 3, "𐑣": 4},
    "Ħ": {"𐑓": 0, "𐑒": 1, "𐑖": 2, "𐑫": 3},
    "Σ": {"𐑙": 0, "𐑕": 1, "𐑳": 2},
    "Ω": {"𐑷": 0, "𐑴": 1, "𐑭": 2, "𐑟": 3},
}

# Shavian keys for compound dict → ORDINALS
PKEY_MAP = {"D": "Ð", "T": "Þ", "R": "Ř", "P": "Φ", "F": "ƒ",
            "K": "Ç", "G": "Γ", "Gm": "ɢ", "Ph": "⊙", "H": "Ħ",
            "S": "Σ", "W": "Ω"}
COMPOUND_KEYS = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]

def glyph_ord(prim: str, glyph: str) -> int:
    mapped = PKEY_MAP.get(prim, prim)
    return ORDINALS.get(mapped, {}).get(glyph, 0)

def format_tuple(t: Dict) -> str:
    glyphs = [t.get(p, "?") for p in COMPOUND_KEYS]
    return "⟨" + "".join(glyphs) + "⟩"


# ═══════════════════════════════════════════════════════════════════
# ALL 11 DIASCHIZICS — complete structural definitions
# ═══════════════════════════════════════════════════════════════════

DIASCHIZICS: Dict[str, Dict] = {

    # ─── FIRST GENERATION (original 5) ─────────────────────────

    "verticullum": {
        "name": "Verticullum",
        "generation": 1,
        "epithet": "EP-Lever",
        "tuple": {"D": "𐑦", "T": "𐑥", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑠", "Ph": "⊙", "H": "𐑫",
                  "S": "𐑳", "W": "𐑟"},
        "tier": "O_∞",
        "pharmacophore_hint": "Tryptamine core with extended indole — needs non-Abelian braiding realized via chiral macrocyclic cage",
        "predicted_scaffold": "Bridged bicyclic with crossing point — tropane-like or morphinan-like",
        "innovations": ["First Ω=𐑟 (non-Abelian)", "First T=𐑥 (bowtie)"],
    },

    "chimerium": {
        "name": "Chimerium",
        "generation": 1,
        "epithet": "Supercritical Catalyst",
        "tuple": {"D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑵", "Ph": "𐑣", "H": "𐑫",
                  "S": "𐑳", "W": "𐑭"},
        "tier": "O₀",
        "pharmacophore_hint": "Ergoline-like scaffold with supercritical ring strain — needs controlled-release pro-drug",
        "predicted_scaffold": "Indole-based (tryptamine core) — self-referential closure topology",
        "innovations": ["First Ph=𐑣 (supercritical)", "Broadcast composition (Gm=𐑵)"],
    },

    "apertix": {
        "name": "Apertix",
        "generation": 1,
        "epithet": "Adjoint Corridor",
        "tuple": {"D": "𐑦", "T": "𐑥", "R": "𐑽", "P": "𐑬", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑠", "Ph": "⊙", "H": "𐑖",
                  "S": "𐑳", "W": "𐑴"},
        "tier": "O₂",
        "pharmacophore_hint": "Phenethylamine-like with directional vector — N-benzylated for adjoint coupling",
        "predicted_scaffold": "Bridged bicyclic with crossing point — tropane-like or morphinan-like",
        "innovations": ["First R=𐑽 (adjoint)", "H2 chirality (H=𐑖)"],
    },

    "retiarius": {
        "name": "Retiarius",
        "generation": 1,
        "epithet": "Local-Net Trap",
        "tuple": {"D": "𐑼", "T": "𐑡", "R": "𐑾", "P": "𐑿", "F": "𐑞",
                  "K": "𐑺", "G": "𐑚", "Gm": "𐑜", "Ph": "𐑮", "H": "𐑒",
                  "S": "𐑕", "W": "𐑷"},
        "tier": "O₁",
        "pharmacophore_hint": "Salvinorin-like with local-only scope — κ-opioid selective with no downstream cascade",
        "predicted_scaffold": "Flexible chain with branching — phenethylamine scaffold",
        "innovations": ["First G=𐑚 (local only)", "First K=𐑺 (MBL)", "First F=𐑞 (thermal)"],
    },

    "praxeum": {
        "name": "Praxeum",
        "generation": 1,
        "epithet": "EP-Core Control Platform",
        "tuple": {"D": "𐑦", "T": "𐑶", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑠", "Ph": "𐑻", "H": "𐑫",
                  "S": "𐑳", "W": "𐑭"},
        "tier": "O₀",
        "pharmacophore_hint": "β-carboline with EP-inducing substitution — needs co-administered ⊙ compound",
        "predicted_scaffold": "Non-factorizable cage — cubane or adamantane derivative",
        "innovations": ["First Ph=𐑻 (exceptional point)", "Irreducible product (T=𐑶)"],
    },

    # ─── SECOND GENERATION (6 new) ──────────────────────────────

    "frigorix": {
        "name": "Frigorix",
        "generation": 2,
        "epithet": "The MBL Key",
        "tuple": {"D": "𐑦", "T": "𐑶", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑺", "G": "𐑲", "Gm": "𐑠", "Ph": "⊙", "H": "𐑒",
                  "S": "𐑳", "W": "𐑷"},
        "tier": "O₀",
        "pharmacophore_hint": "Tryptamine core with MBL-frozen disorder — l-bit eigenstate scaffold requiring rigid aromatic cage with frozen conformational disorder",
        "predicted_scaffold": "Rigid aromatic cage with frozen disorder — triarylamine or hexaarylbenzene core",
        "innovations": ["K=𐑺 with ⊙ frozen — MBL-keyed gate access"],
    },

    "bifrons": {
        "name": "Bifrons",
        "generation": 2,
        "epithet": "The Disjunctive Self-Modeler",
        "tuple": {"D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑜", "Ph": "⊙", "H": "𐑖",
                  "S": "𐑳", "W": "𐑭"},
        "tier": "O₂",
        "pharmacophore_hint": "Bis-tryptamine dimer with disjunctive coupling — two parallel indole cores linked by a cleavable disulfide or photochromic bridge",
        "predicted_scaffold": "Bis-indole dimer with disjunctive linker — photochromic azobenzene bridge",
        "innovations": ["C=𐑜 (disjunctive composition)", "Two parallel self-models"],
    },

    "punctum": {
        "name": "Punctum",
        "generation": 2,
        "epithet": "The Absolute Point",
        "tuple": {"D": "𐑛", "T": "𐑡", "R": "𐑩", "P": "𐑗", "F": "𐑱",
                  "K": "𐑪", "G": "𐑚", "Gm": "𐑝", "Ph": "𐑢", "H": "𐑓",
                  "S": "𐑙", "W": "𐑷"},
        "tier": "O₀",
        "pharmacophore_hint": "Single-atom-like precision — xenon or noble-gas clathrate with zero conformational freedom, absolute point-localization",
        "predicted_scaffold": "Monoatomic or clathrate — adamantane-like single-point cage with encapsulated xenon",
        "innovations": ["D=𐑛 (0d point)", "K=𐑪 (trapped ordered)", "Six new primitive values"],
    },

    "syndexios": {
        "name": "Syndexios",
        "generation": 2,
        "epithet": "The Perfect Mirror",
        "tuple": {"D": "𐑼", "T": "𐑶", "R": "𐑾", "P": "𐑯", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑠", "Ph": "⊙", "H": "𐑫",
                  "S": "𐑳", "W": "𐑭"},
        "tier": "O_∞",
        "pharmacophore_hint": "Fully symmetric meso compound — all stereocenters paired as internal compensation, no net chirality despite multiple centers; cryptophane or carcerand cage",
        "predicted_scaffold": "Meso-cryptophane with full symmetry — octahedral coordination cage or carcerand",
        "innovations": ["P=𐑯 (full symmetry)", "All symmetries unbroken"],
    },

    "katachthon": {
        "name": "Katachthon",
        "generation": 2,
        "epithet": "The Deep-Structure Resonator",
        "tuple": {"D": "𐑦", "T": "𐑥", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑔", "Gm": "𐑠", "Ph": "𐑮", "H": "𐑖",
                  "S": "𐑳", "W": "𐑴"},
        "tier": "O₂",
        "pharmacophore_hint": "Tryptamine with mesoscale-extended conjugation — phenanthrene-fused indole core with Z2-parity-protected resonance",
        "predicted_scaffold": "Phenanthrene-fused tryptamine — extended aromatic with mesoscale conjugation length",
        "innovations": ["G=𐑔 (mesoscale)", "Φ=𐑮 (complex critical)"],
    },

    "diabaton": {
        "name": "Diabaton",
        "generation": 2,
        "epithet": "The Threshold-Crosser",
        "tuple": {"D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹", "F": "𐑐",
                  "K": "𐑧", "G": "𐑲", "Gm": "𐑠", "Ph": "⊙", "H": "𐑖",
                  "S": "𐑳", "W": "𐑭"},
        "tier": "O₂†",
        "pharmacophore_hint": "Tryptamine with self-referential topology — macrocyclic tryptamine dimer with integer-winding topology, the threshold between O₂ and O_∞",
        "predicted_scaffold": "Macrocyclic bis-tryptamine — cyclophane with integer winding and self-referential topology",
        "innovations": ["O₂† tier", "T=𐑸 + H=𐑖 + Ω=𐑭 threshold"],
    },
}


# ═══════════════════════════════════════════════════════════════════
# SCAFFOLD → IUPAC PARENT HYDRIDE MAPPING
# ═══════════════════════════════════════════════════════════════════

# Each pharmacophore hint maps to a parent hydride (IUPAC Blue Book)
SCAFFOLD_PARENT = {
    "tryptamine": {
        "parent": "1H-indole-3-ethanamine",
        "formula": "C₁₀H₁₂N₂",
        "mw": 160.22,
        "ring_system": "indole",
    },
    "ergoline": {
        "parent": "ergoline",
        "formula": "C₁₄H₁₆N₂",
        "mw": 212.30,
        "ring_system": "ergoline (tetracyclic)",
        "iupac": "(6aR,9R)-7-methyl-4,6,6a,7,8,9-hexahydroindolo[4,3-fg]quinoline",
    },
    "phenethylamine": {
        "parent": "benzeneethanamine",
        "formula": "C₈H₁₁N",
        "mw": 121.18,
        "ring_system": "benzene",
    },
    "beta-carboline": {
        "parent": "9H-pyrido[3,4-b]indole",
        "formula": "C₁₁H₈N₂",
        "mw": 168.20,
        "ring_system": "β-carboline (tricyclic)",
    },
    "salvinorin": {
        "parent": "neoclerodane",
        "formula": "C₂₀H₂₈",
        "mw": 268.44,
        "ring_system": "neoclerodane diterpenoid",
        "iupac": "methyl (2S,4aR,6aR,7R,9S,10aS,10bR)-2-(furan-3-yl)-6a,10b-dimethyl-4,10-dioxo-2,4a,5,6,7,8,9,10a-octahydro-1H-benzo[f]isochromene-7-carboxylate",
    },
    "tropane": {
        "parent": "8-azabicyclo[3.2.1]octane",
        "formula": "C₇H₁₃N",
        "mw": 111.19,
        "ring_system": "tropane (bicyclic bridged)",
    },
    "morphinan": {
        "parent": "morphinan",
        "formula": "C₁₆H₂₁N",
        "mw": 227.35,
        "ring_system": "morphinan (tetracyclic bridged)",
    },
    "cubane": {
        "parent": "pentacyclo[4.2.0.0²·⁵.0³·⁸.0⁴·⁷]octane",
        "formula": "C₈H₈",
        "mw": 104.15,
        "ring_system": "cubane (pentacyclic cage)",
    },
    "adamantane": {
        "parent": "tricyclo[3.3.1.1³·⁷]decane",
        "formula": "C₁₀H₁₆",
        "mw": 136.24,
        "ring_system": "adamantane (tricyclic cage)",
    },
    "triarylamine": {
        "parent": "N,N-diarylaniline",
        "formula": "C₁₈H₁₅N",
        "mw": 245.32,
        "ring_system": "triarylamine",
    },
    "hexaarylbenzene": {
        "parent": "hexaphenylbenzene",
        "formula": "C₄₂H₃₀",
        "mw": 534.70,
        "ring_system": "hexaarylbenzene",
    },
    "cryptophane": {
        "parent": "cryptophane",
        "formula": "C₅₄H₅₄O₁₂",
        "mw": 895.01,
        "ring_system": "cryptophane (cage)",
    },
    "carcerand": {
        "parent": "carcerand",
        "formula": "variable",
        "mw": ">1000",
        "ring_system": "carcerand (hemicarcerand cage)",
    },
    "cyclophane": {
        "parent": "cyclophane",
        "formula": "variable",
        "mw": "variable",
        "ring_system": "cyclophane (bridged aromatic)",
    },
    "azobenzene": {
        "parent": "(E)-diphenyldiazene",
        "formula": "C₁₂H₁₀N₂",
        "mw": 182.23,
        "ring_system": "azobenzene (photochromic)",
    },
    "phenanthrene": {
        "parent": "phenanthrene",
        "formula": "C₁₄H₁₀",
        "mw": 178.23,
        "ring_system": "phenanthrene (tricyclic aromatic)",
    },
    "xenon_clathrate": {
        "parent": "xenon hydrate",
        "formula": "Xe·nH₂O",
        "mw": "variable",
        "ring_system": "clathrate cage",
        "iupac": "xenon—clathrate hydrate",
    },
    "bis_indole": {
        "parent": "3,3'-di(1H-indole)",
        "formula": "C₁₆H₁₂N₂",
        "mw": 232.29,
        "ring_system": "bis-indole",
        "iupac": "3,3'-(diazene-1,2-diyl)bis(1H-indole-3-ethanamine)",
    },
    "coordination_cage": {
        "parent": "coordination cage",
        "formula": "variable",
        "mw": ">800",
        "ring_system": "octahedral M₄L₆ cage",
    },
}



# ═══════════════════════════════════════════════════════════════════
# PRIMITIVE → IUPAC SUBSTITUENT MAPPING
# ═══════════════════════════════════════════════════════════════════
# Each primitive value contributes specific IUPAC substituent prefixes,
# suffixes, or stereodescriptors based on the structural logic.

# D (Dimensionality) → scaffold rigidity descriptors
D_IUPAC = {
    "𐑛": {"prefix": "", "descriptor": "clathrate", "note": "0d point — monoatomic or clathrate cage"},
    "𐑨": {"prefix": "", "descriptor": "spiro", "note": "2d surface — spiro junction"},
    "𐑼": {"prefix": "", "descriptor": "cyclo", "note": "∞-dim field-theoretic — flexible chain"},
    "𐑦": {"prefix": "seco-", "descriptor": "macrocyclo", "note": "self-written — macrocyclic cage"},
}

# T (Topology) → ring system descriptors
T_IUPAC = {
    "𐑡": {"prefix": "", "descriptor": "", "note": "network/branching — linear or branched"},
    "𐑰": {"prefix": "", "descriptor": "cyclo", "note": "containment — monocyclic"},
    "𐑥": {"prefix": "", "descriptor": "bicyclo", "note": "bowtie crossing — bridged bicyclic"},
    "𐑶": {"prefix": "", "descriptor": "pentacyclo", "note": "irreducible product — cage (cubane/adamantane)"},
    "𐑸": {"prefix": "", "descriptor": "spiro", "note": "self-ref closure — spiro-linked macrocycle"},
}

# R (Coupling) → linking functional groups
R_IUPAC = {
    "𐑩": {"prefix": "", "suffix": "", "note": "supervenience — no reactive handles"},
    "𐑑": {"prefix": "", "suffix": "-amide", "note": "functorial — amide coupling"},
    "𐑽": {"prefix": "N-", "suffix": "-amine", "note": "adjoint — directed N-substitution"},
    "𐑾": {"prefix": "bis-", "suffix": "", "note": "bidirectional — two identical handles"},
}

# P (Symmetry) → stereochemical descriptors
P_IUPAC = {
    "𐑗": {"stereo": "", "note": "asymmetric — no symmetry constraints"},
    "𐑿": {"stereo": "(R)- or (S)-", "note": "quantum superposition — single stereocenter"},
    "𐑬": {"stereo": "(R,R)- or (S,S)-", "note": "Z₂ symmetry — two centers, same handedness"},
    "𐑯": {"stereo": "meso-", "note": "full symmetry — meso compound, internal compensation"},
    "𐑹": {"stereo": "(Rₐ)- or (Sₐ)-", "note": "Frobenius-special — atropisomerism (axial chirality)"},
}

# F (Fidelity) — physical state / quantum character
F_IUPAC = {
    "𐑱": {"descriptor": "", "note": "classical — no special quantum character"},
    "𐑞": {"descriptor": "", "note": "thermal/noisy — dynamic ensemble, no fixed conformation"},
    "𐑐": {"descriptor": "", "note": "quantum-coherent — H-bond network, deuterated analog possible"},
}

# K (Kinetics) — substituent bulk / kinetic stability
K_IUPAC = {
    "𐑺": {"prefix": "per(fluoro)-", "descriptor": "frozen", "note": "MBL frozen-disorder — perfluorinated or perdeuterated"},
    "𐑪": {"prefix": "", "descriptor": "clathro-", "note": "trapped ordered — encapsulated / clathrate"},
    "𐑧": {"prefix": "tert-", "descriptor": "", "note": "slow — bulky tert-substituents, slow kinetics"},
    "𐑤": {"prefix": "", "descriptor": "", "note": "moderate — standard kinetics"},
    "𐑘": {"prefix": "", "descriptor": "", "note": "fast/driven — small, reactive substituents"},
}

# G (Range) — conjugation length / scope
G_IUPAC = {
    "𐑚": {"descriptor": "", "note": "local — isolated, no extended conjugation"},
    "𐑔": {"descriptor": "", "note": "mesoscale — phenanthrene or extended aromatic, 3-5 fused rings"},
    "𐑲": {"descriptor": "", "note": "long-range — full conjugation or macrocyclic delocalization"},
}

# Gm/ɢ (Composition) — bond formation order / assembly logic
Gm_IUPAC = {
    "𐑝": {"note": "all-simultaneous — convergent synthesis"},
    "𐑜": {"descriptor": "bis-", "note": "disjunctive — cleavable dimer, two parallel units"},
    "𐑠": {"note": "sequential — linear synthesis, stepwise assembly"},
    "𐑵": {"note": "broadcast — one-to-all, dendrimeric or star-shaped"},
}

# Ph/⊙ (Criticality) — ring strain / electronic character
Ph_IUPAC = {
    "𐑢": {"note": "sub-critical — no special electronic character"},
    "⊙": {"note": "critical — H-bond network at self-modeling threshold; deuteration-sensitive"},
    "𐑮": {"descriptor": "complex-", "note": "complex-plane critical — metal coordination complex"},
    "𐑻": {"suffix": "-N-oxide", "note": "exceptional point — N-oxide or zwitterionic; co-administered ⊙ compound required"},
    "𐑣": {"descriptor": "cyclo[prop/lact]", "note": "supercritical — strained ring (cyclopropyl, β-lactam)"},
}

# H (Chirality) — number of stereocenters / Markov order
H_IUPAC = {
    "𐑓": {"descriptor": "", "note": "memoryless — achiral, no stereocenters"},
    "𐑒": {"descriptor": "(R)- or (S)-", "note": "1-step — single stereocenter"},
    "𐑖": {"descriptor": "(R,R)-, (R,S)-, etc.", "note": "2-step — two stereocenters, diastereomers possible"},
    "𐑫": {"descriptor": "(Rₐ)- or (Sₐ)-", "note": "eternal — atropisomerism, axial chirality only"},
}

# S/Σ (Stoichiometry) — substituent multiplicity
S_IUPAC = {
    "𐑙": {"prefix": "", "note": "1:1 — single substituent type, single instance"},
    "𐑕": {"prefix": "poly-", "note": "many identical — polymeric or oligomeric repeat"},
    "𐑳": {"prefix": "", "suffix": "", "note": "heterogeneous — multiple substituent types"},
}

# W/Ω (Winding) — topological protection descriptors
W_IUPAC = {
    "𐑷": {"note": "trivial — no topological protection"},
    "𐑴": {"descriptor": "homodimer", "note": "Z₂ parity — homodimer, disulfide-linked"},
    "𐑭": {"descriptor": "cyclo[n]-", "note": "integer winding — [n]cyclophane or macrocyclic lactam"},
    "𐑟": {"descriptor": "[2]catenane", "note": "non-Abelian — mechanically interlocked catenane/rotaxane"},
}



# ═══════════════════════════════════════════════════════════════════
# SCAFFOLD IDENTIFICATION — map pharmacophore hint to parent hydride
# ═══════════════════════════════════════════════════════════════════

def identify_scaffold(hint: str) -> str:
    """Identify the parent scaffold from pharmacophore hint text."""
    hint_lower = hint.lower()
    # Order matters: more specific matches first
    scaffolds = [
        ("xenon_clathrate", ["xenon", "clathrate", "monoatomic", "noble-gas"]),
        ("coordination_cage", ["coordination cage", "octahedral", "cryptophane", "carcerand"]),
        ("bis_indole", ["bis-indole", "bis-tryptamine"]),
        ("azobenzene", ["azobenzene", "photochromic"]),
        ("salvinorin", ["salvinorin", "neoclerodane"]),
        ("beta-carboline", ["carboline", "β-carboline"]),
        ("ergoline", ["ergoline", "ergot"]),
        ("cubane", ["cubane"]),
        ("adamantane", ["adamantane"]),
        ("triarylamine", ["triarylamine", "hexaarylbenzene", "triaryl"]),
        ("phenanthrene", ["phenanthrene"]),
        ("tropane", ["tropane", "tropane-like"]),
        ("morphinan", ["morphinan"]),
        ("cyclophane", ["cyclophane"]),
        ("phenethylamine", ["phenethylamine", "phenethyl"]),
        ("tryptamine", ["tryptamine", "indole"]),
    ]
    for scaffold, keywords in scaffolds:
        if any(kw in hint_lower for kw in keywords):
            return scaffold
    return "tryptamine"  # default


# ═══════════════════════════════════════════════════════════════════
# IUPAC NAME GENERATOR
# ═══════════════════════════════════════════════════════════════════

class IUPACGenerator:
    """Generate systematic IUPAC-style names for diaschizic compounds."""

    def __init__(self):
        self.compounds = DIASCHIZICS

    def generate_all(self) -> Dict[str, Dict]:
        """Generate IUPAC names for all 11 diaschizics."""
        results = {}
        for key, comp in self.compounds.items():
            results[key] = self.generate_one(key, comp)
        return results

    def generate_one(self, key: str, comp: Dict) -> Dict:
        """Generate IUPAC name for a single diaschizic compound."""
        tup = comp["tuple"]
        scaffold = identify_scaffold(comp.get("pharmacophore_hint", ""))

        # Build IUPAC name components
        stereodescriptors = self._build_stereo(tup)
        substituents = self._build_substituents(tup)
        parent = self._build_parent(tup, scaffold)
        suffix = self._build_suffix(tup)
        topological = self._build_topological(tup)

        # Assemble full IUPAC name
        iupac_name = self._assemble_name(
            stereodescriptors, substituents, parent, suffix, topological
        )

        # Build the name decomposition (human-readable breakdown)
        decomposition = self._build_decomposition(
            key, comp, stereodescriptors, substituents, parent, suffix, topological
        )

        return {
            "compound": comp["name"],
            "epithet": comp.get("epithet", ""),
            "generation": comp["generation"],
            "tier": comp["tier"],
            "tuple_display": format_tuple(tup),
            "scaffold_class": scaffold,
            "iupac_name": iupac_name,
            "decomposition": decomposition,
        }

    def _build_stereo(self, tup: Dict) -> str:
        """Build stereochemical descriptors from P (symmetry) and H (chirality)."""
        p_val = tup.get("P", "")
        h_val = tup.get("H", "")

        # P=𐑯 (full symmetry) → meso- overrides everything
        if p_val == "𐑯":
            return "meso-"

        # P=𐑹 (Frobenius) → atropisomerism via axial chirality
        if p_val == "𐑹":
            if h_val == "𐑫":
                return "(Rₐ)-"
            elif h_val == "𐑖":
                return "(Rₐ,Rₐ)-"
            elif h_val == "𐑒":
                return "(Rₐ)-"
            else:
                return "(Rₐ)-"

        # P=𐑬 (partial/Z2) → two centers
        if p_val == "𐑬":
            if h_val == "𐑖":
                return "(2R,5R)-"
            elif h_val == "𐑒":
                return "(R)-"
            else:
                return ""

        # P=𐑿 (quantum) → single center
        if p_val == "𐑿":
            return "(R)-"

        # Otherwise use H-based stereochemistry
        if h_val == "𐑒":
            return "(R)-"
        elif h_val == "𐑖":
            return "(2R,5R)-"
        elif h_val == "𐑫":
            return ""  # atropisomerism handled by P
        else:
            return ""

    def _build_substituents(self, tup: Dict) -> str:
        """Build substituent prefixes from kinetics (K) and coupling (R) primitives."""
        parts = []

        k_val = tup.get("K", "")
        r_val = tup.get("R", "")
        s_val = tup.get("S", "")
        gm_val = tup.get("Gm", "")

        # K-driven substituents — only one K prefix
        k_info = K_IUPAC.get(k_val, {})
        if k_val == "𐑧":
            parts.append("tert-butyl-")
        elif k_val == "𐑺":
            # MBL frozen: perdeutero- (not per(fluoro) for diaschizics — that's for actual MBL materials)
            parts.append("perdeutero-")
        elif k_info.get("prefix"):
            parts.append(k_info["prefix"])

        # R-driven: N- for adjoint (𐑽)
        if r_val == "𐑽":
            parts.append("N-")
        elif r_val == "𐑾":
            # bidirectional — bis- prefix for two handles, unless Gm already provides it
            pass

        # Gm-driven: bis- for disjunctive
        if gm_val == "𐑜":
            parts.append("bis-")

        # S-driven multiplicity: poly- only for S=𐑕
        if s_val == "𐑕":
            parts.append("poly-")

        if not parts:
            return ""

        return "".join(parts)

    def _build_parent(self, tup: Dict, scaffold: str) -> str:
        """Build the parent hydride name incorporating topology and dimensionality."""
        t_val = tup.get("T", "")
        d_val = tup.get("D", "")
        g_val = tup.get("G", "")
        ph_val = tup.get("Ph", "")

        parent_info = SCAFFOLD_PARENT.get(scaffold, SCAFFOLD_PARENT["tryptamine"])
        base = parent_info.get("iupac", parent_info["parent"])

        # T-driven ring system prefix
        t_desc = T_IUPAC.get(t_val, {}).get("descriptor", "")

        # Build topological prefix based on T and D
        topo_prefix = ""
        if t_val == "𐑶":
            topo_prefix = "pentacyclo"  # cubane/adamantane type
        elif t_val == "𐑥":
            if d_val == "𐑦":
                topo_prefix = ""  # bridged bicyclic is inherent in morphinan/tropane
            else:
                topo_prefix = "bicyclo"
        elif t_val == "𐑸":
            topo_prefix = ""  # spiro — handled differently for macrocycles

        # G-driven conjugation extension
        if g_val == "𐑔":
            # mesoscale → phenanthrene-fused
            if "indole" in base.lower():
                base = base.replace("indole", "phenanthro[9,10-b]indole")

        # Ph-driven modifications
        if ph_val == "𐑣":
            # supercritical → add cyclopropyl descriptor
            if topo_prefix:
                topo_prefix = "cyclopropyl-" + topo_prefix
            else:
                topo_prefix = "cyclopropyl-"
        elif ph_val == "𐑮":
            # complex critical → metal coordination
            if topo_prefix:
                topo_prefix = "complex-" + topo_prefix
            else:
                topo_prefix = "complex-"

        # Assemble — ensure clean hyphenation
        if topo_prefix:
            topo_prefix = topo_prefix.rstrip("-") + "-"
            # Check if base already contains the topological info
            if topo_prefix.rstrip("-") not in base:
                base = topo_prefix + base

        return base

    def _build_suffix(self, tup: Dict) -> str:
        """Build suffix (functional group endings) from coupling and criticality."""
        parts = []

        r_val = tup.get("R", "")
        r_info = R_IUPAC.get(r_val, {})
        if r_info.get("suffix"):
            parts.append(r_info["suffix"])

        ph_val = tup.get("Ph", "")
        ph_info = Ph_IUPAC.get(ph_val, {})
        if ph_info.get("suffix"):
            parts.append(ph_info["suffix"])

        return "".join(parts)

    def _build_topological(self, tup: Dict) -> str:
        """Build topological descriptor from winding (Ω)."""
        w_val = tup.get("W", "")
        w_info = W_IUPAC.get(w_val, {})

        if w_val == "𐑟":
            return "[2]catenane"
        elif w_val == "𐑭":
            return "cyclophane"
        elif w_val == "𐑴":
            return "disulfide-linked homodimer"
        else:
            return ""

    def _assemble_name(self, stereo: str, substituents: str,
                        parent: str, suffix: str, topological: str) -> str:
        """Assemble IUPAC name from components following Blue Book ordering."""
        # Build core name: [stereo][substituents][parent][suffix]
        core_parts = []
        if stereo:
            core_parts.append(stereo)
        if substituents:
            # Clean up substituent string: remove double hyphens, trailing hyphens
            subs = substituents.strip("-")
            # Remove doubled hyphens
            while "--" in subs:
                subs = subs.replace("--", "-")
            if subs:
                core_parts.append(subs)
        
        # Clean parent: remove [...] placeholders
        parent_clean = parent
        if "[...]" in parent_clean:
            # Try to infer a better parent name
            parent_clean = parent_clean.replace("[...]", "")
            parent_clean = parent_clean.strip("-")
        
        core_parts.append(parent_clean)
        
        if suffix:
            # Attach suffix to parent (last element)
            core_parts[-1] = core_parts[-1] + suffix
        
        core_name = "-".join(p for p in core_parts if p)
        
        # Clean up: remove any double hyphens, trailing/leading hyphens
        while "--" in core_name:
            core_name = core_name.replace("--", "-")
        core_name = core_name.strip("-")
        
        # Apply topological wrapper
        if topological:
            if "catenane" in topological.lower():
                return f"{topological} of ({core_name})"
            elif "dimer" in topological.lower():
                return f"{topological}: ({core_name})"
            elif "cyclophane" in topological.lower():
                return f"[n]{topological} ({core_name})"
        
        return core_name

    def _build_decomposition(self, key: str, comp: Dict,
                              stereo: str, substituents: str,
                              parent: str, suffix: str,
                              topological: str) -> Dict:
        """Build a human-readable decomposition of the IUPAC name."""
        tup = comp["tuple"]
        return {
            "compound": comp["name"],
            "key": key,
            "generation": comp["generation"],
            "epithet": comp.get("epithet", ""),
            "tier": comp["tier"],
            "tuple": format_tuple(tup),
            "scaffold": identify_scaffold(comp.get("pharmacophore_hint", "")),
            "parent_hydride": SCAFFOLD_PARENT.get(
                identify_scaffold(comp.get("pharmacophore_hint", "")),
                {}
            ).get("parent", "unknown"),
            "iupac_components": {
                "stereodescriptors": stereo,
                "substituent_prefixes": substituents,
                "parent_hydride": parent,
                "functional_suffix": suffix,
                "topological_descriptor": topological,
            },
            "primitive_contributions": {
                "D_dimensionality": D_IUPAC.get(tup.get("D", ""), {}).get("note", ""),
                "T_topology": T_IUPAC.get(tup.get("T", ""), {}).get("note", ""),
                "R_coupling": R_IUPAC.get(tup.get("R", ""), {}).get("note", ""),
                "P_symmetry": P_IUPAC.get(tup.get("P", ""), {}).get("note", ""),
                "F_fidelity": F_IUPAC.get(tup.get("F", ""), {}).get("note", ""),
                "K_kinetics": K_IUPAC.get(tup.get("K", ""), {}).get("note", ""),
                "G_range": G_IUPAC.get(tup.get("G", ""), {}).get("note", ""),
                "Gm_composition": Gm_IUPAC.get(tup.get("Gm", ""), {}).get("note", ""),
                "Ph_criticality": Ph_IUPAC.get(tup.get("Ph", ""), {}).get("note", ""),
                "H_chirality": H_IUPAC.get(tup.get("H", ""), {}).get("note", ""),
                "S_stoichiometry": S_IUPAC.get(tup.get("S", ""), {}).get("note", ""),
                "W_winding": W_IUPAC.get(tup.get("W", ""), {}).get("note", ""),
            },
            "pharmacophore_hint": comp.get("pharmacophore_hint", ""),
            "predicted_scaffold": comp.get("predicted_scaffold", ""),
        }




# ═══════════════════════════════════════════════════════════════════
# OUTPUT FORMATTERS
# ═══════════════════════════════════════════════════════════════════

def format_markdown(results: Dict[str, Dict]) -> str:
    """Format all IUPAC names as a markdown document."""
    lines = []
    lines.append("# Diaschizics — IUPAC Systematic Names")
    lines.append("")
    lines.append("**Author:** Lando⊗⊙perator")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append("The 11 diaschizic compounds are assigned systematic IUPAC-style chemical names")
    lines.append("derived from their 12-primitive structural types. Each name component maps to a")
    lines.append("specific primitive value, following the structural logic of `diaschizics_design.md`.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    gen1 = [(k, v) for k, v in results.items() if v["generation"] == 1]
    gen2 = [(k, v) for k, v in results.items() if v["generation"] == 2]
    lines.append("### First Generation (Original 5)")
    for k, v in gen1:
        lines.append(f"- [{v['compound']}](#{v['compound'].lower()}) — {v['epithet']} ({v['tier']})")
    lines.append("")
    lines.append("### Second Generation (6 New)")
    for k, v in gen2:
        lines.append(f"- [{v['compound']}](#{v['compound'].lower()}) — {v['epithet']} ({v['tier']})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Mapping legend
    lines.append("## Primitive → IUPAC Mapping Legend")
    lines.append("")
    lines.append("| Primitive | IUPAC Feature | Example Values |")
    lines.append("|-----------|---------------|----------------|")
    lines.append("| D (Dimensionality) | Scaffold rigidity | 𐑦→macrocyclic cage, 𐑼→flexible chain, 𐑛→clathrate |")
    lines.append("| T (Topology) | Ring system descriptor | 𐑥→bicyclo (bridged), 𐑶→pentacyclo (cage), 𐑸→spiro |")
    lines.append("| R (Coupling) | Linking group / suffix | 𐑽→N-substituted, 𐑾→bis- (bidirectional) |")
    lines.append("| P (Symmetry) | Stereodescriptor | 𐑹→atropisomer (Rₐ), 𐑯→meso, 𐑬→(R,R) |")
    lines.append("| F (Fidelity) | Physical state note | 𐑐→quantum-coherent (H-bond network) |")
    lines.append("| K (Kinetics) | Substituent bulk | 𐑺→perdeutero- (frozen), 𐑧→tert-butyl (slow), 𐑪→clathro- |")
    lines.append("| G (Range) | Conjugation scope | 𐑲→global, 𐑔→mesoscale (phenanthrene-fused), 𐑚→local |")
    lines.append("| Gm (Composition) | Assembly logic | 𐑜→bis- (disjunctive dimer), 𐑠→linear, 𐑵→dendrimeric |")
    lines.append("| Ph (Criticality) | Electronic descriptor | ⊙→H-bond network, 𐑣→strained ring, 𐑻→N-oxide |")
    lines.append("| H (Chirality) | Stereocenter count | 𐑒→1 center, 𐑖→2 centers, 𐑫→atropisomerism |")
    lines.append("| S (Stoichiometry) | Multiplicity prefix | 𐑳→heterogeneous, 𐑕→poly-, 𐑙→single |")
    lines.append("| W (Winding) | Topological descriptor | 𐑟→[2]catenane, 𐑭→cyclophane, 𐑴→homodimer |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Individual compound entries
    for key, result in sorted(results.items(), key=lambda x: (x[1]["generation"], x[0])):
        comp = result
        dec = comp["decomposition"]
        comps = dec["iupac_components"]

        lines.append(f"## {comp['compound']} — *{comp['epithet']}*")
        lines.append("")
        lines.append(f"- **Generation:** {comp['generation']}")
        lines.append(f"- **Tier:** {comp['tier']}")
        lines.append(f"- **Tuple:** {comp['tuple_display']}")
        lines.append(f"- **Scaffold class:** {dec['scaffold']}")
        lines.append(f"- **Parent hydride:** {dec['parent_hydride']}")
        lines.append("")
        lines.append(f"### IUPAC Name")
        lines.append("")
        lines.append(f"> **{comp['iupac_name']}**")
        lines.append("")
        lines.append("### Name Decomposition")
        lines.append("")
        lines.append("| Component | Value |")
        lines.append("|-----------|-------|")
        lines.append(f"| Stereodescriptors | `{comps['stereodescriptors']}` |")
        lines.append(f"| Substituent prefixes | `{comps['substituent_prefixes']}` |")
        lines.append(f"| Parent hydride | `{comps['parent_hydride']}` |")
        lines.append(f"| Functional suffix | `{comps['functional_suffix']}` |")
        lines.append(f"| Topological descriptor | `{comps['topological_descriptor']}` |")
        lines.append("")
        lines.append("### Primitive Contributions")
        lines.append("")
        lines.append("| Primitive | Contribution |")
        lines.append("|-----------|-------------|")
        for prim_label, note in dec["primitive_contributions"].items():
            prim_short = prim_label.split("_")[0]
            lines.append(f"| {prim_short} | {note} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def format_json(results: Dict[str, Dict]) -> str:
    """Format results as JSON."""
    output = []
    for key, result in sorted(results.items()):
        output.append({
            "key": key,
            "compound": result["compound"],
            "epithet": result["epithet"],
            "generation": result["generation"],
            "tier": result["tier"],
            "tuple": result["tuple_display"],
            "iupac_name": result["iupac_name"],
            "scaffold_class": result["scaffold_class"],
        })
    return json.dumps(output, indent=2, ensure_ascii=False)


def format_tsv(results: Dict[str, Dict]) -> str:
    """Format results as TSV."""
    lines = ["compound\tepithet\tgeneration\ttier\tiupac_name\tscaffold_class\ttuple"]
    for key, result in sorted(results.items(), key=lambda x: (x[1]["generation"], x[0])):
        lines.append(
            f"{result['compound']}\t{result['epithet']}\t{result['generation']}"
            f"\t{result['tier']}\t{result['iupac_name']}\t{result['scaffold_class']}"
            f"\t{result['tuple_display']}"
        )
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate IUPAC systematic names for diaschizic compounds"
    )
    parser.add_argument("--format", choices=["md", "json", "tsv", "all"], default="md",
                        help="Output format (default: md)")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output file path (default: stdout)")
    parser.add_argument("--compound", "-c", type=str, default=None,
                        help="Generate for a single compound (key name)")
    args = parser.parse_args()

    gen = IUPACGenerator()

    if args.compound:
        if args.compound not in DIASCHIZICS:
            print(f"Unknown compound: {args.compound}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(DIASCHIZICS.keys()))}", file=sys.stderr)
            sys.exit(1)
        comp = DIASCHIZICS[args.compound]
        result = gen.generate_one(args.compound, comp)
        results = {args.compound: result}
    else:
        results = gen.generate_all()

    if args.format == "md" or args.format == "all":
        md = format_markdown(results)
        if args.format == "all":
            out_path = args.output or "diaschizics_iupac.md"
            with open(out_path, "w") as f:
                f.write(md)
            print(f"Markdown written to {out_path}")
        elif args.output:
            with open(args.output, "w") as f:
                f.write(md)
            print(f"Written to {args.output}")
        else:
            print(md)

    if args.format == "json" or args.format == "all":
        js = format_json(results)
        if args.format == "all":
            out_path = args.output.replace(".md", ".json") if args.output else "diaschizics_iupac.json"
            with open(out_path, "w") as f:
                f.write(js)
            print(f"JSON written to {out_path}")
        elif args.output:
            with open(args.output, "w") as f:
                f.write(js)
            print(f"Written to {args.output}")
        else:
            print(js)

    if args.format == "tsv" or args.format == "all":
        tsv = format_tsv(results)
        if args.format == "all":
            out_path = args.output.replace(".md", ".tsv") if args.output else "diaschizics_iupac.tsv"
            with open(out_path, "w") as f:
                f.write(tsv)
            print(f"TSV written to {out_path}")
        elif args.output:
            with open(args.output, "w") as f:
                f.write(tsv)
            print(f"Written to {args.output}")
        else:
            print(tsv)

    # Summary statistics
    print(f"\nGenerated IUPAC names for {len(results)} diaschizic compounds.", file=sys.stderr)
    gen1_count = sum(1 for r in results.values() if r["generation"] == 1)
    gen2_count = sum(1 for r in results.values() if r["generation"] == 2)
    print(f"  Generation 1: {gen1_count} compounds", file=sys.stderr)
    print(f"  Generation 2: {gen2_count} compounds", file=sys.stderr)


if __name__ == "__main__":
    main()
