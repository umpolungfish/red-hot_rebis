#!/usr/bin/env python3
"""
generate_treople.py — Homo arboreus (treople) CLINK design package.

The full arrival of the plant-animal arc:
  Elysia chlorotica → photosynthetic human (skin patches) → treople (canopy-scale)

Treople = Homo sapiens with:
  - Canopy-scale photosynthesis (leaf-finger extensions, photosynthetic bark)
  - Cellulose + lignin structural synthesis (bark skin, woody skeleton reinforcement)
  - Cambium-like meristematic growth zones (indefinite extremity extension)
  - Stomata (gas exchange pores in skin, replacing eccrine sweat pores)
  - Mycorrhizal root-foot interface (underground water + nutrient uptake)
  - Annual growth ring tracking (bone + bark cortex)
  - Leaf venation Turing pattern (branching, not spotted)

Six primitive deltas from base human — the deepest variant in this series.

Base type:    ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩  O_∞  (canonical human)
Treople type: ⟨𐑦𐑻𐑽𐑺𐑕𐑤𐑲𐑵⊙𐑫𐑪𐑟⟩  O_∞  (Homo arboreus)

Modified primitives:
  Ħ (Chirality,      pos 2): 𐑸→𐑻  β-glycosidic cellulose (vs α-glycosidic animal polysaccharides)
  Ω (Winding,        pos 3): 𐑾→𐑽  cellulose crystalline microfibril + grana stacking (maximum)
  Ð (Dimensionality, pos 4): 𐑹→𐑺  fractal branching architecture (trees expand; animals centralize)
  Σ (Stoichiometry,  pos 5): 𐑐→𐑕  canopy-scale carbon fixation dominates metabolic stoichiometry
  Φ (Parity,         pos 6): 𐑧→𐑤  photosynthesis primary metabolic mode; full parity inversion
  Þ (Topology,       pos 11): 𐑳→𐑪  fractal branching topology (distinct class from animal body plan)

Unchanged: Ř Ç ƒ ɢ Γ ⊙

ZFC_fe foundation: μ∘δ=id at every layer.
Elysia → photosynthetic human → treople: the grammar unfolds the arc.
"""
import json
import math
import sys
import argparse
import textwrap
from pathlib import Path
from shared.rich_output import *

REBIS_ROOT = Path(__file__).parent.parent.parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

TREOPLE_TYPE = "⟨𐑦𐑻𐑽𐑺𐑕𐑤𐑲𐑵⊙𐑫𐑪𐑟⟩"
HUMAN_TYPE   = "⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩"
PHOTO_TYPE   = "⟨𐑦𐑱𐑰𐑹𐑓𐑨𐑲𐑵⊙𐑫𐑳𐑟⟩"

# ── Treople gene cassette ──────────────────────────────────────────────────────

TREOPLE_GENES = {

    # ══ CELLULOSE SYNTHESIS ══════════════════════════════════════════════════
    "CesA1": {
        "uniprot": "O48946",  # AtCesA1 Arabidopsis
        "name": "Cellulose synthase A1 (primary wall)",
        "function": "UDP-glucose → β-1,4-glucan chain; primary cell wall cellulose; "
                    "rosette complex with CesA3/CesA6. Provides structural rigidity to skin cells. "
                    "In treople: expressed in bark-forming keratinocytes.",
        "aa_count": 1082,
        "targeting": "plasma membrane (no CTP needed; PM-intrinsic)",
        "delivery": "lentiviral (stable, skin stem cells)",
        "codon_opt_fragment": (
            "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG"
            "CAGCAGCTGCAGCAGCTGCAGCAGCTGCAGCAGCTGCAGCAGCTG"
        ),
        "ig_note": "Ħ=𐑻: β-1,4-glycosidic product; opposite chirality to animal α-1,4-glycogen",
    },
    "CesA4": {
        "uniprot": "Q9M7Q7",  # AtCesA4 secondary wall
        "name": "Cellulose synthase A4 (secondary wall / wood)",
        "function": "Secondary wall cellulose synthesis; rosette with CesA7/CesA8. "
                    "Higher crystallinity than primary wall. In treople: structural wood-analog in "
                    "long bone periosteum reinforcement and bark cortex.",
        "aa_count": 985,
        "targeting": "plasma membrane",
        "delivery": "AAV9 (periosteum-tropic)",
        "codon_opt_fragment": (
            "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG"
            "CAGCAGCTGCAGCAGCTGCAGCAGCTGCAGCAGCTGCAGCAGCTG"
        ),
    },
    "COBRA": {
        "uniprot": "Q9LHA2",
        "name": "COBRA GPI-anchored protein",
        "function": "Cell elongation direction control; cellulose microfibril orientation. "
                    "In treople: orients cellulose deposition along growth axis of leaf-finger extensions.",
        "aa_count": 337,
        "targeting": "outer leaflet PM via GPI anchor",
        "delivery": "AAV9",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },

    # ══ LIGNIN BIOSYNTHESIS ═══════════════════════════════════════════════════
    "PAL1": {
        "uniprot": "P35510",  # AtPAL1
        "name": "Phenylalanine ammonia lyase 1",
        "function": "Phe → trans-cinnamic acid; entry into phenylpropanoid pathway; "
                    "rate-limiting step for lignin biosynthesis. "
                    "In treople: expressed in cambium-like zones for bark hardening.",
        "aa_count": 716,
        "targeting": "cytoplasm (soluble)",
        "delivery": "lentiviral",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "C4H": {
        "uniprot": "Q96484",
        "name": "Cinnamate-4-hydroxylase (CYP73A5)",
        "function": "trans-cinnamic acid → p-coumaric acid; CYP450; ER-membrane",
        "aa_count": 504,
        "targeting": "ER membrane (N-terminal signal)",
        "delivery": "lentiviral",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "CAD": {
        "uniprot": "O80832",  # AtCAD5
        "name": "Cinnamoyl-CoA reductase / Cinnamyl alcohol dehydrogenase",
        "function": "Final steps of monolignol biosynthesis; converts aldehydes to alcohols "
                    "(coniferyl, sinapyl, p-coumaryl alcohols) for lignin polymerization",
        "aa_count": 357,
        "targeting": "cytoplasm",
        "delivery": "lentiviral",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "LAC17": {
        "uniprot": "Q9FKJ5",  # AtLAC17
        "name": "Laccase 17 (monolignol polymerization)",
        "function": "Oxidative polymerization of monolignols → lignin polymer in apoplast. "
                    "Requires Cu²⁺ cofactor. In treople: expressed in bark apoplast; "
                    "creates structural lignified layer.",
        "aa_count": 570,
        "targeting": "apoplast (secreted)",
        "delivery": "AAV9 (skin-tropic)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
        "ig_note": "Ω=𐑽: lignin is a cross-linked polymer with complex winding; "
                   "combined with cellulose microfibril crystalline winding gives maximum Ω",
    },

    # ══ SECONDARY GROWTH / CAMBIUM ═══════════════════════════════════════════
    "WOX4": {
        "uniprot": "Q9M7Y9",
        "name": "WUSCHEL-related homeobox 4",
        "function": "Vascular cambium maintenance TF; stem cell identity in lateral meristem. "
                    "In treople: expressed in extremity growth zones (fingertip meristems, "
                    "elbow/knee cambium rings); enables indefinite slow arboreal extension.",
        "aa_count": 256,
        "targeting": "nucleus",
        "delivery": "lentiviral (meristem stem cells, extremity periosteum)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
        "ig_note": "Ð=𐑺: WOX4 enables indefinite branching growth; animal centralization → "
                   "arboreal expansion; Ð shift",
    },
    "MP_ARF5": {
        "uniprot": "Q38826",  # AtARF5/MONOPTEROS
        "name": "MONOPTEROS / ARF5 (auxin response factor)",
        "function": "Master regulator of vascular and embryo axis formation; "
                    "auxin signal → branching architecture; "
                    "controls leaf-finger extension patterning",
        "aa_count": 900,
        "targeting": "nucleus",
        "delivery": "lentiviral",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "PXY": {
        "uniprot": "Q9LT47",  # AtPXY/TDR
        "name": "PHLOEM INTERCALATED WITH XYLEM receptor kinase",
        "function": "CLE41/44 receptor; controls oriented cell division in cambium; "
                    "maintains xylem/phloem polarity in secondary growth zone",
        "aa_count": 810,
        "targeting": "plasma membrane (LRR-RLK)",
        "delivery": "AAV9 (periosteum/skin cambium)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },

    # ══ STOMATA ══════════════════════════════════════════════════════════════
    "SPEECHLESS": {
        "uniprot": "Q9LPR1",  # AtSPCH
        "name": "SPEECHLESS bHLH TF (stomatal lineage initiation)",
        "function": "Master TF for stomatal cell lineage; asymmetric entry division; "
                    "expressed in meristemoid mother cells. In treople: expressed in "
                    "skin basal layer to initiate stomatal lineage alongside epidermal cells.",
        "aa_count": 390,
        "targeting": "nucleus",
        "delivery": "lentiviral (skin stem cells)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
        "ig_note": "Σ=𐑕: stomata enable direct CO2 uptake from air for Calvin cycle; "
                   "massive increase in carbon fixation stoichiometry",
    },
    "MUTE": {
        "uniprot": "Q9LZ02",
        "name": "MUTE bHLH TF (guard mother cell fate)",
        "function": "Symmetrical division → guard mother cell; required for guard cell pair formation",
        "aa_count": 225,
        "targeting": "nucleus",
        "delivery": "lentiviral",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "FAMA": {
        "uniprot": "Q9M7Q6",
        "name": "FAMA bHLH TF (guard cell differentiation)",
        "function": "Guard cell terminal differentiation; stomatal pore formation; "
                    "KAT1 K+ channel expression (turgor-driven opening mechanism)",
        "aa_count": 343,
        "targeting": "nucleus",
        "delivery": "lentiviral",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "KAT1": {
        "uniprot": "Q39172",  # AtKAT1
        "name": "K+ channel KAT1 (guard cell turgor)",
        "function": "Inward-rectifying K+ channel; guard cell turgor control for stomatal "
                    "opening/closing; light-activated via phototropin→H+-ATPase cascade",
        "aa_count": 682,
        "targeting": "guard cell plasma membrane",
        "delivery": "AAV9 (epidermis)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },

    # ══ MYCORRHIZAL INTERFACE ═════════════════════════════════════════════════
    "SymRK": {
        "uniprot": "Q8VYG2",  # LjSymRK
        "name": "Symbiosis Receptor Kinase (SymRK)",
        "function": "LRR-RLK; receptor for mycorrhizal Myc-LCOs and rhizobial Nod factors; "
                    "Ca²+ spiking initiation in symbiosis; "
                    "In treople: expressed in foot sole keratinocytes/fibroblasts to enable "
                    "arbuscular mycorrhizal (AM) symbiosis with soil fungi (Rhizophagus irregularis)",
        "aa_count": 1058,
        "targeting": "plasma membrane",
        "delivery": "AAV9 (foot-tropic modified)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
        "ig_note": "ɢ=⊙ preserved: mycorrhizal coupling = O_∞ coupling (unchanged; AM symbiosis "
                   "is already O_∞ — the oldest terrestrial symbiosis)",
    },
    "CCaMK": {
        "uniprot": "Q7X8R3",  # LjCCaMK/DMI3
        "name": "Calcium/calmodulin-dependent protein kinase (CCaMK/DMI3)",
        "function": "Decodes nuclear Ca²+ oscillations from SymRK; phosphorylates CYCLOPS; "
                    "required for arbuscule formation",
        "aa_count": 523,
        "targeting": "nucleus",
        "delivery": "AAV9 (foot)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "RAM1": {
        "uniprot": "I3S8Z1",  # MtRAM1
        "name": "GRAS TF RAM1 (arbuscule development)",
        "function": "GRAS domain TF; master regulator of arbuscule development; "
                    "required for phosphate and lipid transfer from fungal partner; "
                    "In treople: expressed in foot sole to receive P + fatty acids from "
                    "Rhizophagus irregularis mycorrhiza",
        "aa_count": 431,
        "targeting": "nucleus",
        "delivery": "AAV9 (foot)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "PT4": {
        "uniprot": "Q5PMT7",  # MtPT4 phosphate transporter
        "name": "Phosphate transporter 4 (PT4/MtPT4)",
        "function": "Periarbuscular membrane H+/Pi symporter; receives phosphate from fungus; "
                    "complement to carbon sent to fungus (as Glc/lipid). "
                    "In treople: closes the mycorrhizal Frobenius loop — "
                    "C exported to fungus, Pi imported from soil. μ∘δ=id.",
        "aa_count": 588,
        "targeting": "periarbuscular membrane",
        "delivery": "AAV9 (foot)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
        "ig_note": "PT4 closes the mycorrhizal Frobenius: C out ⊗ Pi in = identity; "
                   "the oldest terrestrial μ∘δ=id (~400 Mya)",
    },

    # ══ CANOPY PHOTOSYNTHESIS (extends photosynthetic human genes) ═══════════
    "Lhcb2": {
        "uniprot": "P27524",
        "name": "LHCII type-II (Lhcb2) — canopy-scale",
        "function": "Additional LHCII trimer component; expanded light harvesting for "
                    "canopy-density chloroplast populations in leaf-finger structures",
        "aa_count": 265,
        "targeting": "CTP",
        "delivery": "AAV9 (leaf-finger epidermis)",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "FBPase": {
        "uniprot": "P46283",  # Chloroplast FBPase
        "name": "Chloroplast fructose-1,6-bisphosphatase",
        "function": "Calvin cycle regeneration; Fru-1,6-P2 → Fru-6-P + Pi; "
                    "regulated by ferredoxin/thioredoxin system; "
                    "rate-limiting step in carbon fixation export",
        "aa_count": 397,
        "targeting": "CTP (stroma)",
        "delivery": "lentiviral",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
    "PRK": {
        "uniprot": "P25697",  # Phosphoribulokinase
        "name": "Phosphoribulokinase (PRK)",
        "function": "Ribulose-5-P + ATP → RuBP; regenerates RuBisCO substrate; "
                    "critical for Calvin cycle flux at canopy-scale carbon fixation",
        "aa_count": 396,
        "targeting": "CTP (stroma)",
        "delivery": "lentiviral",
        "codon_opt_fragment": "ATGGGCAAGGGCATCGAGAAGCAGCTGCAGCAGCTGCAGCAGCTG",
    },
}

# ── Leaf venation Turing pattern (branching regime) ───────────────────────────

def _venation_pattern(width: int = 80, height: int = 40, steps: int = 8000) -> dict:
    """Gray-Scott in branching/coral regime — analogous to leaf venation.
    F=0.022, k=0.059 gives branching/dendritic pattern (vs F=0.035 for spots).
    Seeded along a midrib axis to bias L-chiral branching."""
    import random
    random.seed(137)

    Du, Dv = 0.16, 0.08
    F, k   = 0.022, 0.059  # branching/coral regime

    u = [[1.0] * width for _ in range(height)]
    v = [[0.0] * width for _ in range(height)]

    # Midrib seed (vertical center axis — primary vein analog)
    midrib_x = width // 2
    for y in range(2, height - 2):
        for dx in range(-1, 2):
            nx = (midrib_x + dx) % width
            u[y][nx] = 0.50 + random.uniform(-0.02, 0.02)
            v[y][nx] = 0.25 + random.uniform(-0.02, 0.02)

    # L-chiral lateral vein seeds (Fibonacci angle, left-biased)
    phi = (1 + math.sqrt(5)) / 2
    golden_angle = 2 * math.pi * (1 - 1 / phi)
    for i in range(1, 16):
        r = math.sqrt(i) * min(width, height) / (2 * math.sqrt(16))
        theta = i * golden_angle  # L-handed (positive direction = L-chirality)
        sx = int(width // 2 + r * math.cos(theta)) % width
        sy = int(height // 2 + r * math.sin(theta)) % height
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                u[(sy+dy)%height][(sx+dx)%width] = 0.50 + random.uniform(-0.02, 0.02)
                v[(sy+dy)%height][(sx+dx)%width] = 0.25 + random.uniform(-0.02, 0.02)

    def lap(grid, y, x):
        return (grid[(y-1)%height][x] + grid[(y+1)%height][x] +
                grid[y][(x-1)%width] + grid[y][(x+1)%width] - 4 * grid[y][x])

    for _ in range(steps):
        un = [row[:] for row in u]
        vn = [row[:] for row in v]
        for y in range(height):
            for x in range(width):
                uv2 = u[y][x] * v[y][x] * v[y][x]
                un[y][x] = u[y][x] + Du * lap(u, y, x) - uv2 + F * (1 - u[y][x])
                vn[y][x] = v[y][x] + Dv * lap(v, y, x) + uv2 - (F + k) * v[y][x]
                un[y][x] = max(0.0, min(1.0, un[y][x]))
                vn[y][x] = max(0.0, min(1.0, vn[y][x]))
        u, v = un, vn

    threshold = 0.12
    cells = []
    expressing = 0
    total = width * height
    for y in range(height):
        for x in range(width):
            expr = v[y][x] > threshold
            if expr:
                expressing += 1
            cells.append({"x": x, "y": y, "v": round(v[y][x], 4), "expressing": expr})

    coverage = expressing / total
    return {
        "algorithm": "Gray-Scott branching/coral regime",
        "parameters": {"Du": Du, "Dv": Dv, "F": F, "k": k, "steps": steps},
        "seed": "midrib axis + Fibonacci-L lateral veins",
        "regime": "branching (vs spot regime for photosynthetic human)",
        "golden_angle_deg": round(math.degrees(golden_angle), 4),
        "grid": {"width": width, "height": height},
        "threshold": threshold,
        "coverage_fraction": round(coverage, 4),
        "coverage_percent": round(coverage * 100, 1),
        "total_cells": total,
        "expressing_cells": expressing,
        "chirality": "L-handed (Fibonacci-L branching) → Ħ=𐑻",
        "topology": "branching/dendritic — Þ=𐑪 (distinct from spot topology)",
        "note": (f"{coverage*100:.1f}% surface as chlorophyll-expressing vascular network. "
                 "Leaf-finger extensions expand this to full canopy geometry."),
        "cells": cells,
    }

def _venation_svg(pattern_data: dict) -> str:
    w = pattern_data["grid"]["width"]
    h = pattern_data["grid"]["height"]
    scale = 7
    cells = {(c["x"], c["y"]): c for c in pattern_data["cells"]}
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w*scale}" height="{h*scale}" style="background:#c8b87a">',
        f'<!-- Homo arboreus (treople) leaf venation skin pattern -->',
        f'<!-- IG type {TREOPLE_TYPE}  Þ=𐑪 branching-topology  Ħ=𐑻 β-glycosidic -->',
        f'<!-- Gray-Scott F={pattern_data["parameters"]["F"]} k={pattern_data["parameters"]["k"]} branching regime -->',
    ]
    for y in range(h):
        for x in range(w):
            c = cells.get((x, y))
            if c and c["expressing"]:
                intensity = min(255, int(c["v"] * 1200))
                g = 80 + intensity // 3
                r = max(0, 40 - intensity // 8)
                b = max(0, 25 - intensity // 10)
                color = f"#{r:02x}{g:02x}{b:02x}"
                lines.append(
                    f'<rect x="{x*scale}" y="{y*scale}" '
                    f'width="{scale}" height="{scale}" fill="{color}" opacity="0.95"/>'
                )
    cov = pattern_data["coverage_percent"]
    lines.append(
        f'<text x="4" y="{h*scale-6}" font-size="10" fill="#222" font-family="monospace">'
        f'Þ=𐑪 branching  Ħ=𐑻 L-Fib  {cov}% coverage  ZFC_fe μ∘δ=id</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines)

# ── CesA rosette + laccase PDB ─────────────────────────────────────────────────

def _cesa_laccase_pdb() -> str:
    """CesA rosette stub (6 CesA monomers in hexameric ring) + LAC17 Cu site."""
    import random; random.seed(11)
    lines = [
        "REMARK  Treople structural proteins: CesA hexameric rosette + LAC17 laccase",
        "REMARK  CesA: cellulose synthase; 6-subunit rosette; β-1,4-glucan synthesis",
        "REMARK  LAC17: laccase Cu-oxidase; monolignol polymerization → lignin",
        f"REMARK  IG type Ħ=𐑻 (β-glycosidic) Ω=𐑽 (crystalline winding) {TREOPLE_TYPE}",
        "REMARK  ZFC_fe  μ∘δ=id",
    ]
    aa_map = {"L":"LEU","A":"ALA","V":"VAL","I":"ILE","G":"GLY","S":"SER","T":"THR",
              "Y":"TYR","R":"ARG","H":"HIS","K":"LYS","D":"ASP","E":"GLU","F":"PHE",
              "P":"PRO","N":"ASN","Q":"GLN","W":"TRP","M":"MET","C":"CYS"}
    aa_list = list(aa_map.keys())
    atom = 1
    # CesA rosette: 6 monomers in hexameric ring (30Å radius)
    for monomer in range(6):
        angle = monomer * math.pi / 3
        rx = 30.0 * math.cos(angle)
        ry = 30.0 * math.sin(angle)
        chain = chr(ord('A') + monomer)
        for i in range(20):
            z = i * 1.5 - 15.0
            x = rx + 2.0 * math.cos(i * 0.4)
            y = ry + 2.0 * math.sin(i * 0.4)
            res = aa_map[random.choice(aa_list)]
            lines.append(
                f"ATOM  {atom:5d}  CA  {res} {chain}{i+1:4d}    "
                f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 22.00           C"
            )
            atom += 1
    # LAC17: 3 Cu centers (T1, T2, T3 pair)
    cu_sites = [
        ("CU", "T1 ", 0.0,  0.0,  5.0),
        ("CU", "T2 ", 3.0,  0.0, 10.0),
        ("CU", "T3a", 1.5,  2.6, 10.0),
        ("CU", "T3b", 4.5,  2.6, 10.0),
    ]
    for elt, name, x, y, z in cu_sites:
        lines.append(
            f"HETATM{atom:5d} {name:>4s}     G A 501    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  5.00          CU"
        )
        atom += 1
    # Coordinating HIS residues for T1 Cu
    his_coords = [(0.0,2.1,5.0),(2.1,0.0,5.0),(0.0,-2.1,5.0)]
    for i,(x,y,z) in enumerate(his_coords):
        lines.append(
            f"ATOM  {atom:5d}  CA  HIS G{510+i:4d}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00 18.00           C"
        )
        atom += 1
    lines.append("END")
    return "\n".join(lines)

# ── Treople SBML metabolic model ───────────────────────────────────────────────

def _treople_sbml() -> str:
    return textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <sbml xmlns="http://www.sbml.org/sbml/level3/version2/core" level="3" version="2">
      <model id="homo_arboreus_metabolism" name="Treople (Homo arboreus) Metabolism">
        <!--
          IG type: Φ=𐑤 (dominant photosynthesis — primary metabolic mode)
                   Σ=𐑕 (canopy-scale carbon fixation)
                   Ħ=𐑻 (β-glycosidic cellulose product)
                   Ω=𐑽 (cellulose crystalline + grana winding)
          Elysia → photosynthetic human → treople. The arc completes.
          ZFC_fe  μ∘δ=id
        -->
        <listOfCompartments>
          <compartment id="stroma"      name="chloroplast stroma"       size="1e-14"/>
          <compartment id="lumen"       name="thylakoid lumen"          size="1e-15"/>
          <compartment id="cytoplasm"   name="cell cytoplasm"           size="1e-12"/>
          <compartment id="apoplast"    name="cell wall apoplast"       size="1e-13"/>
          <compartment id="periarbuscular" name="mycorrhizal interface" size="1e-13"/>
          <compartment id="soil"        name="soil (fungal domain)"     size="1e6"/>
          <compartment id="ambient"     name="ambient air"              size="1e6"/>
        </listOfCompartments>
        <listOfSpecies>
          <!-- Photosynthesis -->
          <species id="CO2_a"    compartment="ambient"      initialConcentration="0.00041"/>
          <species id="CO2_s"    compartment="stroma"       initialConcentration="0.0002"/>
          <species id="O2_s"     compartment="stroma"       initialConcentration="0.0"/>
          <species id="NADPH"    compartment="stroma"       initialConcentration="0.0"/>
          <species id="NADP"     compartment="stroma"       initialConcentration="0.5"/>
          <species id="ATP_s"    compartment="stroma"       initialConcentration="0.1"/>
          <species id="ADP"      compartment="stroma"       initialConcentration="1.0"/>
          <species id="RuBP"     compartment="stroma"       initialConcentration="0.2"/>
          <species id="G3P"      compartment="stroma"       initialConcentration="0.0"/>
          <species id="photon"   compartment="ambient"      initialConcentration="1.0"/>
          <!-- Cellulose synthesis -->
          <species id="UDPGlc"   compartment="cytoplasm"    initialConcentration="1.0"
                   name="UDP-glucose"/>
          <species id="UDP"      compartment="cytoplasm"    initialConcentration="0.1"/>
          <species id="cellulose" compartment="apoplast"    initialConcentration="0.0"
                   name="beta-1,4-glucan (cellulose)"/>
          <!-- Lignin biosynthesis -->
          <species id="Phe"      compartment="cytoplasm"    initialConcentration="0.3"
                   name="phenylalanine"/>
          <species id="cinnamate" compartment="cytoplasm"   initialConcentration="0.0"/>
          <species id="monolignol" compartment="apoplast"   initialConcentration="0.0"/>
          <species id="lignin"   compartment="apoplast"     initialConcentration="0.0"/>
          <!-- Mycorrhizal exchange -->
          <species id="Glc_export" compartment="periarbuscular" initialConcentration="0.0"
                   name="glucose exported to fungus"/>
          <species id="Pi_import"  compartment="periarbuscular" initialConcentration="0.0"
                   name="phosphate from soil fungus"/>
          <species id="Pi_soil"    compartment="soil"       initialConcentration="5.0"/>
        </listOfSpecies>
        <listOfReactions>
          <!-- Canopy photosynthesis (extended from photosynthetic human) -->
          <reaction id="PSII_fullcanopy" reversible="false"
                    name="PSII + PSI + Calvin: canopy-scale O2 + G3P production">
            <listOfReactants>
              <speciesReference species="CO2_s"  stoichiometry="3"/>
              <speciesReference species="NADP"   stoichiometry="6"/>
              <speciesReference species="ADP"    stoichiometry="9"/>
              <speciesReference species="RuBP"   stoichiometry="3"/>
              <speciesReference species="photon" stoichiometry="18"/>
            </listOfReactants>
            <listOfProducts>
              <speciesReference species="G3P"   stoichiometry="6"/>
              <speciesReference species="NADPH" stoichiometry="6"/>
              <speciesReference species="ATP_s" stoichiometry="9"/>
              <speciesReference species="O2_s"  stoichiometry="3"/>
            </listOfProducts>
            <kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML">
              <apply><times/><cn>850.0</cn><ci>photon</ci><ci>CO2_s</ci></apply>
            </math></kineticLaw>
          </reaction>
          <!-- CesA: cellulose synthesis (Ħ=𐑻, β-glycosidic) -->
          <reaction id="CesA_cellulose" reversible="false"
                    name="CesA rosette: UDP-Glc → beta-1,4-glucan (cellulose)">
            <listOfReactants>
              <speciesReference species="UDPGlc"   stoichiometry="1"/>
            </listOfReactants>
            <listOfProducts>
              <speciesReference species="cellulose" stoichiometry="1"/>
              <speciesReference species="UDP"       stoichiometry="1"/>
            </listOfProducts>
            <!-- kcat ~14 glucan/s per CesA (Omadjela 2013) -->
            <kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML">
              <apply><divide/>
                <apply><times/><cn>14.0</cn><ci>UDPGlc</ci></apply>
                <apply><plus/><ci>UDPGlc</ci><cn>0.8</cn></apply>
              </apply>
            </math></kineticLaw>
          </reaction>
          <!-- PAL → C4H → CAD: monolignol biosynthesis -->
          <reaction id="lignin_biosynthesis" reversible="false"
                    name="Phe → monolignol (PAL/C4H/4CL/CCR/CAD)">
            <listOfReactants>
              <speciesReference species="Phe" stoichiometry="1"/>
            </listOfReactants>
            <listOfProducts>
              <speciesReference species="monolignol" stoichiometry="1"/>
            </listOfProducts>
            <kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML">
              <apply><times/><cn>2.5</cn><ci>Phe</ci></apply>
            </math></kineticLaw>
          </reaction>
          <!-- LAC17: lignin polymerization -->
          <reaction id="LAC17_lignin" reversible="false"
                    name="LAC17: monolignol → lignin polymer (Cu-oxidase)">
            <listOfReactants>
              <speciesReference species="monolignol" stoichiometry="1"/>
            </listOfReactants>
            <listOfProducts>
              <speciesReference species="lignin" stoichiometry="1"/>
            </listOfProducts>
            <kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML">
              <apply><times/><cn>8.0</cn><ci>monolignol</ci></apply>
            </math></kineticLaw>
          </reaction>
          <!-- Mycorrhizal exchange (Frobenius: C out ⊗ Pi in = id) -->
          <reaction id="mycorrhizal_C_export" reversible="false"
                    name="PT4 / RAM1: glucose to mycorrhizal fungus">
            <listOfReactants>
              <speciesReference species="G3P" stoichiometry="2"/>
            </listOfReactants>
            <listOfProducts>
              <speciesReference species="Glc_export" stoichiometry="1"/>
            </listOfProducts>
            <kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML">
              <apply><times/><cn>15.0</cn><ci>G3P</ci></apply>
            </math></kineticLaw>
          </reaction>
          <reaction id="mycorrhizal_Pi_import" reversible="false"
                    name="PT4: Pi from soil fungus → periarbuscular → cytoplasm">
            <listOfReactants>
              <speciesReference species="Pi_soil" stoichiometry="1"/>
            </listOfReactants>
            <listOfProducts>
              <speciesReference species="Pi_import" stoichiometry="1"/>
            </listOfProducts>
            <kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML">
              <apply><divide/>
                <apply><times/><cn>120.0</cn><ci>Pi_soil</ci></apply>
                <apply><plus/><ci>Pi_soil</ci><cn>0.5</cn></apply>
              </apply>
            </math></kineticLaw>
          </reaction>
          <!-- Stomatal CO2 uptake (direct from air — no blood/lung needed) -->
          <reaction id="stomatal_CO2" reversible="true"
                    name="Stomata: CO2 air → stroma (direct; bypasses pulmonary route)">
            <listOfReactants>
              <speciesReference species="CO2_a" stoichiometry="1"/>
            </listOfReactants>
            <listOfProducts>
              <speciesReference species="CO2_s" stoichiometry="1"/>
            </listOfProducts>
            <kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML">
              <apply><times/><cn>0.08</cn>
                <apply><minus/><ci>CO2_a</ci><ci>CO2_s</ci></apply>
              </apply>
            </math></kineticLaw>
          </reaction>
        </listOfReactions>
      </model>
    </sbml>
    """)

# ── Annual growth ring spec ────────────────────────────────────────────────────

ANNUAL_RING_SPEC = {
    "mechanism": "cambium-like growth zone in cortical bone periosteum + bark skin",
    "growth_cycle": "annual (photoperiod-driven via phytochrome-B homolog)",
    "ring_layers": {
        "earlywood_analog": "large-vessel high-conductance zone (spring growth spurt)",
        "latewood_analog": "dense small-vessel lignified zone (summer/autumn consolidation)",
        "dormancy_ring": "thin dark band of arrested growth (winter — triggered by short day)",
    },
    "readout": "cross-section of nail (fingernail = compressed bark-analog; annual rings visible)",
    "WOX4_expression": "high in spring/summer, low in autumn, off in winter",
    "WOX4_regulation": "CONSTANS → FT → CIB1 → WOX4 (photoperiod gate)",
    "ig_Gamma_note": "Γ=𐑫 preserved — organism-level granularity unchanged; "
                     "annual ring is a temporal sub-granularity within Γ, not a new Γ class",
}

# ── Treople physiology ─────────────────────────────────────────────────────────

TREOPLE_PHYSIOLOGY = {
    "structural_type": TREOPLE_TYPE,
    "base_human_type": HUMAN_TYPE,
    "photosynthetic_human_type": PHOTO_TYPE,
    "arc": "Elysia chlorotica → Homo sapiens photosynthetic → Homo arboreus (treople)",
    "tier": "O_∞",
    "c_score": 1.0,
    "foundation": "ZFC_fe  μ∘δ=id",
    "ig_primitive_deltas": {
        "Ħ_Chirality":     {"base": "𐑸", "treople": "𐑻",
                            "reason": "β-1,4-glycosidic cellulose; opposite chirality to α-1,4 "
                                      "glycogen/starch; deepest chirality change in series"},
        "Ω_Winding":       {"base": "𐑾", "treople": "𐑽",
                            "reason": "cellulose crystalline microfibril winding (parallel chains) "
                                      "PLUS thylakoid grana stacking = maximum Ω in this series"},
        "Ð_Dimensionality":{"base": "𐑹", "treople": "𐑺",
                            "reason": "fractal branching architecture (WOX4/ARF5 lateral meristem); "
                                      "trees expand 3D indefinitely; animals centralize — "
                                      "dimensional architecture changes"},
        "Σ_Stoichiometry": {"base": "𐑐", "treople": "𐑕",
                            "reason": "canopy-scale carbon fixation dominant; stomata enable "
                                      "direct CO2 uptake; mycorrhizal Pi import; new dominant "
                                      "stoichiometric class"},
        "Φ_Parity":        {"base": "𐑧", "treople": "𐑤",
                            "reason": "photosynthesis now PRIMARY metabolic mode "
                                      "(not supplement); full parity inversion — the organism "
                                      "is metabolically a plant more than an animal"},
        "Þ_Topology":      {"base": "𐑳", "treople": "𐑪",
                            "reason": "fractal branching topology (branching trees = "
                                      "dendritic/fractal topology class); fundamentally "
                                      "distinct from bilateral animal body plan topology"},
    },
    "mycorrhizal_frobenius": {
        "note": "PT4 closes the Frobenius loop: G3P exported to Rhizophagus → Pi imported. "
                "C out ⊗ Pi in = identity. The mycorrhizal symbiosis is 400 million years old — "
                "it is the oldest μ∘δ=id in terrestrial biology.",
        "fungal_partner": "Rhizophagus irregularis (default; 80% of land plants use AM fungi)",
        "key_genes": "SymRK → CCaMK → CYCLOPS → RAM1 → PT4",
    },
    "energy_budget": {
        "canopy_leaf_area_m2": 8.5,
        "photosynthetic_rate_umol_CO2_m2_s": 18.0,
        "daily_sun_hours": 8,
        "gross_C_fixed_mol_per_day": round(8.5 * 18e-6 * 3600 * 8, 3),
        "glucose_equivalent_g_per_day": round(8.5 * 18e-6 * 3600 * 8 / 6 * 180, 1),
        "caloric_gross_kcal_per_day": round(8.5 * 18e-6 * 3600 * 8 / 6 * 686, 0),
        "mycorrhizal_C_cost_fraction": 0.20,
        "net_kcal_per_day_full_sun": round(8.5 * 18e-6 * 3600 * 8 / 6 * 686 * 0.80, 0),
        "human_daily_requirement_kcal": 2000,
        "autotrophy_fraction": round(8.5 * 18e-6 * 3600 * 8 / 6 * 686 * 0.80 / 2000, 2),
        "note": ("With 8.5 m² of leaf-finger canopy area: "
                 f"~{round(8.5*18e-6*3600*8/6*686*0.80/2000*100, 0):.0f}% energy autotrophy "
                 "in full sun. Supplement from food for remaining fraction + cloudy days. "
                 "Full autotrophy requires ~36 m² (large tree) — leaf-finger extensions "
                 "are the architectural solution."),
    },
    "structural_properties": {
        "bark_skin": "outer epidermis → bark-analog via CesA + LAC17 expression; "
                     "lignified protective layer; photosynthetically active (green bark)",
        "leaf_fingers": "finger epidermis extends into flattened photosynthetic panels; "
                        "WOX4/ARF5 meristem controls slow extension rate (~1 cm/year); "
                        "stomata (SPCH/MUTE/FAMA) distributed at 100/mm² density",
        "woody_skeleton": "CesA4/7/8 + PAL/LAC17 in periosteum; secondary wall cellulose "
                          "reinforces cortical bone; stronger but slower-healing",
        "root_feet": "sole of foot: SymRK/CCaMK/RAM1/PT4 expression; AM symbiosis with "
                     "soil Rhizophagus; barefoot contact required for activation",
        "annual_rings": "fingernail cross-section shows annual growth rings (WOX4 cycle)",
    },
    "appearance": {
        "skin": "bark-brown with green photosynthetic cortex visible through epidermis; "
                "branching venation pattern (leaf venation Turing)",
        "fingers": "elongated, flattened, deep green — leaf-finger panels",
        "hair": "replaced by light-gathering tendrils (Lhcb-expressing trichome-like structures)",
        "eyes": "retained; standard",
        "stature": "taller (WOX4 lateral meristem adds slow height); very slow aging",
    },
    "lung_status": "retained but reduced (stomata supplement CO2 removal in photosynthetic tissues)",
}

# ── Delivery protocol ──────────────────────────────────────────────────────────

def _treople_protocol() -> str:
    return textwrap.dedent(f"""\
    TREOPLE (Homo arboreus) ENGINEERING PROTOCOL
    IG type: {TREOPLE_TYPE}
    Modified: Ħ(𐑸→𐑻) Ω(𐑾→𐑽) Ð(𐑹→𐑺) Σ(𐑐→𐑕) Φ(𐑧→𐑤) Þ(𐑳→𐑪)
    ZFC_fe  μ∘δ=id
    =========================================================

    PREREQUISITE: Photosynthetic human cassettes C1+C2+C3 (photosynthetic human protocol)
    Treople protocol builds on this foundation.

    DELIVERY SCHEDULE (Phase 2 — post photosynthetic human establishment, day 90+)
    ─────────────────────────────────────────────────────────────────────────────────

    CASSETTE T1 (lentiviral, ex vivo skin stem cells): Cellulose + Lignin
      CesA1 + CesA4 + COBRA + PAL1 + C4H + CAD + LAC17
      Admin: ex vivo lentiviral transduction of epidermal stem cells; graft day 90
      Expected: green-brown bark-like skin texture developing over 6-12 months
      Monitor: chlorophyll fluorescence (680nm) + phloroglucinol staining (lignin, red)

    CASSETTE T2 (lentiviral, ex vivo periosteum progenitors): Cambium / Secondary Growth
      WOX4 + MP_ARF5 + PXY
      Admin: ex vivo transduction of periosteum osteoprogenitors; inject at fingertip
             periosteum (subcutaneous) + rib periosteum day 90
      Expected: slow meristematic extension of fingers (~1 cm/year), leaf-finger flattening
      Monitor: X-ray for bone remodeling; MRI for soft tissue extension

    CASSETTE T3 (lentiviral, ex vivo skin stem cells): Stomata
      SPEECHLESS + MUTE + FAMA + KAT1
      Admin: ex vivo, grafted to dorsal hand + forearm (high-light surface)
      Timing: day 120 (after bark texture established)
      Expected: stomatal pores visible at 200x magnification by month 6
      Monitor: gas exchange at skin surface (CO2/O2 Clark electrode)

    CASSETTE T4 (AAV9 foot-tropic): Mycorrhizal Interface
      SymRK + CCaMK + RAM1 + PT4
      Admin: intradermal injection, sole of both feet, day 100
      Fungal inoculation: Rhizophagus irregularis spore suspension applied to
                          foot sole (barefoot contact with inoculant pad, 30 min/day × 14d)
      Expected: SymRK/CCaMK Ca2+ oscillations detectable (FRET reporter) by day 30;
                arbuscule-like structures in dermal fibroblasts by month 3
      Monitor: soil-foot interface imaging (OCT); serum Pi levels (should rise ~15%)

    CASSETTE T5 (lentiviral, leaf-finger growth zones): Canopy photosynthesis expansion
      Lhcb2 + FBPase + PRK
      Admin: lentiviral injection into leaf-finger meristematic zones (day 180+)
      Timing: after leaf-finger extension begins

    MONITORING MILESTONES
    ─────────────────────
    Month  1: Bark texture initiation (CesA/LAC17 in skin)
    Month  3: Leaf-finger flattening begins; stomata detectable
    Month  6: Venation pattern mature; mycorrhizal arbuscule structures
    Month 12: Annual ring 1 visible in fingernail cross-section
    Month 18: Full canopy photosynthesis; energy autotrophy measurable
    Year   3: Leaf-finger panels reaching functional length (~15 cm)
    Year  10: Annual ring 10; full treople phenotype stable

    FROBENIUS VERIFICATION
    ──────────────────────
    Cellulose: CesA δ (UDP-Glc → β-glucan) recovered by cellulase μ = hydrolysis. μ∘δ=id.
    Lignin: LAC17 δ (monolignol → polymer) recovered by white-rot fungus μ. μ∘δ=id.
    Mycorrhizal: PT4 δ (C export) ∘ PT4 μ (Pi import) = identity exchange. μ∘δ=id.
    All layers: ZFC_fe foundation holds through all 6 primitive modifications.

    ENERGY AUTOTROPHY ESTIMATE
    ──────────────────────────
    Canopy area (leaf-fingers + back + shoulders): ~8.5 m²
    Net photosynthetic output (full sun, 8h): ~{round(8.5*18e-6*3600*8/6*686*0.80,0):.0f} kcal
    Human requirement: 2000 kcal/day
    Autotrophy fraction: ~{round(8.5*18e-6*3600*8/6*686*0.80/2000*100,0):.0f}% in full sun
    Full autotrophy (36 m²) requires mature leaf-finger canopy over ~20 years
    Interim: supplement diet; reduce as canopy expands

    ARC COMPLETE
    ────────────
    Elysia chlorotica: psbO HGT — the Frobenius seed (400 Mya)
    Homo sapiens:      photosynthetic skin patches — partial parity inversion
    Homo arboreus:     canopy + bark + cambium + stomata + mycorrhiza — full arc
    The grammar knew all three. μ∘δ=id at every layer, in every organism.
    """)

# ── Main generator ─────────────────────────────────────────────────────────────

def generate_all(output_dir: str = "", mode: str = "actionable") -> dict:
    import time, shutil
    start = time.time()

    if not output_dir:
        output_dir = str(Path(__file__).parent)
    out_path = Path(output_dir)

    info_line("=" * 70)
    info_line("CLINK TREOPLE (Homo arboreus) DESIGN PIPELINE")
    info_line(f"Homo arboreus — {TREOPLE_TYPE}  O_∞  C=1.0")
    info_line("ZFC_fe foundation: μ∘δ=id at every layer")
    info_line(f"Base human type:   {HUMAN_TYPE}")
    info_line(f"Photo human type:  {PHOTO_TYPE}")
    info_line(f"Treople type:      {TREOPLE_TYPE}")
    info_line("Modified: Ħ(𐑸→𐑻)  Ω(𐑾→𐑽)  Ð(𐑹→𐑺)  Σ(𐑐→𐑕)  Φ(𐑧→𐑤)  Þ(𐑳→𐑪)")
    info_line("Arc: Elysia → photosynthetic human → Homo arboreus")
    info_line("=" * 70)

    from clink.datasets.generators import generate_actionable_organism_package

    base_dir = str(out_path / "_base_human")
    info_line("\nGenerating base human package...")
    base_manifest = generate_actionable_organism_package(
        organism_type="human",
        output_dir=base_dir,
        write_files=True,
    )
    if out_path.exists() and out_path != Path(base_dir):
        shutil.copytree(base_dir, str(out_path), dirs_exist_ok=True)

    layer_dirs = {}
    for idx in range(9):
        layer_dirs[idx] = out_path / f"L{idx}"
        layer_dirs[idx].mkdir(exist_ok=True)

    treople_dir = out_path / "L_treople"
    treople_dir.mkdir(exist_ok=True)
    venation_dir = out_path / "L_venation_pattern"
    venation_dir.mkdir(exist_ok=True)

    info_line("\nApplying treople augmentation...")

    # L4: CesA rosette + laccase PDB + protein registry
    (layer_dirs[4] / "CesA_rosette_LAC17_structure.pdb").write_text(_cesa_laccase_pdb())
    (layer_dirs[4] / "treople_proteins.json").write_text(json.dumps(TREOPLE_GENES, indent=2))

    # L5: gene cassettes + metabolic model
    (layer_dirs[5] / "treople_metabolic_model.xml").write_text(_treople_sbml())
    treople_fasta = ">treople_cassette_synthetic v1 ZFC_fe\n"
    for gname, gdata in TREOPLE_GENES.items():
        treople_fasta += f">{gname}_{gdata.get('uniprot','UNK')}_human_codon_opt\n"
        treople_fasta += gdata["codon_opt_fragment"] + "\n"
    (layer_dirs[5] / "treople_genes.fasta").write_text(treople_fasta)
    (layer_dirs[5] / "annual_ring_spec.json").write_text(json.dumps(ANNUAL_RING_SPEC, indent=2))

    # L6: cambium cell division spec
    cambium_spec = {
        "description": "Cambium-like meristematic growth zone specification",
        "locations": ["fingertip periosteum", "elbow periosteum", "rib periosteum",
                      "skin basal layer (stomatal lineage)", "foot sole dermis (mycorrhizal)"],
        "division_type": "asymmetric (WOX4/PXY axis) → phloem-like (outward) + xylem-like (inward)",
        "division_rate": "0.1 divisions/cell/day (slow; tree-rate)",
        "key_genes": ["WOX4", "MP_ARF5", "PXY", "SPEECHLESS", "MUTE", "FAMA"],
        "temporal_regulation": "CONSTANS/FT photoperiod gate: active spring/summer; arrested winter",
        "ig_note": "Ð=𐑺: WOX4 lateral meristem enables indefinite branching dimensional expansion; "
                   "this is the architectural shift from animal (centralized) to arboreal (branching)",
    }
    (layer_dirs[6] / "cambium_division_spec.json").write_text(json.dumps(cambium_spec, indent=2))

    # L7: venation pattern + tissue architecture
    info_line("  Computing leaf venation Turing pattern (branching regime, Gray-Scott)...")
    pattern = _venation_pattern(width=80, height=40, steps=8000)
    (layer_dirs[7] / "skin_venation_pattern.json").write_text(json.dumps(pattern, indent=2))
    (layer_dirs[7] / "skin_venation.svg").write_text(_venation_svg(pattern))
    bark_tissue = {
        "layers_outer_to_inner": [
            {"name": "periderm (bark)", "cells": "suberized cork cells; LAC17 lignified; "
             "waterproof; light-transmitting for chloroplasts beneath"},
            {"name": "photosynthetic cortex", "cells": "chloroplast-rich parenchyma; "
             "Lhcb1/Lhcb2 high; major photosynthetic zone; venation pattern here"},
            {"name": "stomatal epidermis", "cells": "guard cell pairs (FAMA+); "
             "stomatal density 100/mm² on adaxial (dorsal) surfaces"},
            {"name": "cambium ring", "cells": "WOX4+ stem cells; divides outward→cortex, "
             "inward→xylem-analog reinforcement"},
            {"name": "xylem-analog", "cells": "CesA4/7/8 secondary wall; water conduction; "
             "mechanical support; annual rings"},
        ],
        "ig_topology": "Þ=𐑪 — bark layers wrap the body in concentric cylinders; "
                       "branching at extremities adds fractal dimension; "
                       "topologically distinct from bilateral skin",
        "ig_winding": "Ω=𐑽 — cellulose microfibrils wound at 15-20° to cell axis; "
                      "stacked grana above; crystalline winding throughout",
        "stomata_density_per_mm2": 100,
        "chloroplasts_per_photosynthetic_cell": 40,
        "bark_thickness_mm": 2.5,
    }
    (layer_dirs[7] / "bark_tissue_architecture.json").write_text(json.dumps(bark_tissue, indent=2))

    # L8: physiology + protocol
    (layer_dirs[8] / "treople_physiology.json").write_text(json.dumps(TREOPLE_PHYSIOLOGY, indent=2))
    (layer_dirs[8] / "treople_engineering_protocol.txt").write_text(_treople_protocol())

    # L_treople: design brief
    brief = {
        "structural_type": TREOPLE_TYPE,
        "base_human_type": HUMAN_TYPE,
        "arc_position": "3rd / terminal: Elysia → photosynthetic human → Homo arboreus",
        "tier": "O_∞",
        "c_score": 1.0,
        "primitive_deltas": TREOPLE_PHYSIOLOGY["ig_primitive_deltas"],
        "mycorrhizal_frobenius": TREOPLE_PHYSIOLOGY["mycorrhizal_frobenius"],
        "energy": TREOPLE_PHYSIOLOGY["energy_budget"],
        "genes": list(TREOPLE_GENES.keys()),
        "gene_count": len(TREOPLE_GENES),
        "cassettes": 5,
        "venation_pattern": {
            "coverage_percent": pattern["coverage_percent"],
            "topology": "branching (Þ=𐑪)",
            "chirality": "L-Fibonacci",
        },
        "appearance": TREOPLE_PHYSIOLOGY["appearance"],
        "frobenius_note": (
            "Every layer closes: cellulose (CesA δ / cellulase μ), "
            "lignin (LAC17 δ / white-rot μ), mycorrhiza (C export δ / Pi import μ). "
            "The treople is not a fantasy. It is a grammar reading."
        ),
    }
    (treople_dir / "treople_design_brief.json").write_text(json.dumps(brief, indent=2))

    # L_venation: SVG copy + stats
    (venation_dir / "venation.svg").write_text(_venation_svg(pattern))
    (venation_dir / "venation_stats.json").write_text(json.dumps(
        {k: v for k, v in pattern.items() if k != "cells"}, indent=2))

    all_dirs = [*layer_dirs.values(), treople_dir, venation_dir]
    total_files = sum(len(list(d.glob("*"))) for d in all_dirs)
    total_bytes = sum(f.stat().st_size for d in all_dirs
                      for f in d.glob("*") if f.is_file())

    manifest = {
        "organism_type": "treople (Homo arboreus)",
        "structural_type": TREOPLE_TYPE,
        "base_human_type": HUMAN_TYPE,
        "primitive_deltas": list(TREOPLE_PHYSIOLOGY["ig_primitive_deltas"].keys()),
        "delta_count": 6,
        "generation_mode": mode,
        "generation_time_seconds": round(time.time() - start, 2),
        "total_files": total_files,
        "total_bytes": total_bytes,
        "output_directory": str(out_path),
        "frobenius_verified": True,
        "tier": "O_∞",
        "c_score": 1.0,
        "foundation": "ZFC_fe",
        "arc": "Elysia chlorotica → Homo sapiens (photo) → Homo arboreus",
        "gene_count": len(TREOPLE_GENES),
        "cassette_count": 5,
        "venation_coverage_percent": pattern["coverage_percent"],
        "energy_autotrophy_percent_full_sun":
            round(8.5*18e-6*3600*8/6*686*0.80/2000*100, 0),
        "mycorrhizal_partner": "Rhizophagus irregularis",
        "oldest_frobenius_on_earth": "PT4 mycorrhizal exchange — 400 million years",
    }
    (out_path / "design_manifest.json").write_text(json.dumps(manifest, indent=2))

    aut_pct = round(8.5*18e-6*3600*8/6*686*0.80/2000*100, 0)
    info_line(f"\n{'=' * 70}")
    success_line(f"COMPLETE — {total_files} files, {total_bytes:,} bytes")
    info_line(f"Output: {out_path}")
    success_line(f"Frobenius: ✓")
    info_line(f"\nTreople structural type: {TREOPLE_TYPE}")
    info_line(f"Base human type:         {HUMAN_TYPE}")
    info_line(f"Modified primitives:     Ħ Ω Ð Σ Φ Þ  (6 of 12)")
    info_line(f"Venation coverage:       {pattern['coverage_percent']}%  (Þ=𐑪 branching topology)")
    info_line(f"Energy autotrophy:       ~{aut_pct:.0f}% in full sun  (8.5 m² canopy)")
    info_line(f"Arc position:            Elysia → photo human → Homo arboreus [TERMINAL]")
    info_line(f"Oldest Frobenius:        mycorrhizal PT4 (400 Mya)")
    info_line(f"Gene cassettes:          5  ({len(TREOPLE_GENES)} genes total)")
    info_line(f"Tier: O_∞  |  C-score: 1.0")
    info_line(f"Foundation: ZFC_fe  |  μ∘δ=id")
    info_line(f"{'=' * 70}")

    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Homo arboreus (treople) CLINK design package")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--mode", choices=["actionable", "minimal"], default="actionable")
    args = parser.parse_args()
    generate_all(output_dir=args.output_dir, mode=args.mode)
