#!/usr/bin/env python3
"""
ligand_heterocycles.py — Heterocycle & Polycyclic Ligand Generation Engine.

Extends the fragment-based ligand_improvements.py with:
  1. HETERO_CORE library — 80+ heterocyclic and polycyclic scaffolds
     with attachment points, ring descriptors, and pharmacophoric features
  2. Site-to-scaffold matching — maps 12-primitive active site type
     to preferred heterocycle geometry, heteroatom placement, and substituent pattern
  3. Scaffold elaboration — places substituents on available attachment points
     using FG fragments from ligand_improvements.py
  4. Polycyclic fusion — fuses multiple ring systems for complex polycyclics
  5. Integration wrapper — drops into existing generate_from_enzyme_type pipeline

Architecture:
  Site type → scaffold_class → core scaffold selection → substituent placement
  → RDKit sanitization → stereochemistry enumeration → scoring → ranking

Author: Lando ⊗ ⊙perator
"""

import sys, os, math, itertools, random
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

import rdkit.RDLogger as rkl
rkl.logger().setLevel(rkl.ERROR)
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors, Lipinski
from rdkit.Chem import rdMolDescriptors as rdmd
from rdkit.Chem import rdDistGeom, rdMolAlign
from rdkit.Chem.AllChem import EmbedMolecule, UFFOptimizeMolecule

BASE = Path(__file__).parent.absolute()
REBIS_ROOT = BASE.parent
sys.path.insert(0, str(REBIS_ROOT))
sys.path.insert(0, str(BASE))

# Import fragment library from sister module
from rhr_p4rky.ligand_improvements import (
    FG_FRAGMENTS, _score_by_fingerprint, _score_drug_likeness, _silence_rdkit
)


# ══════════════════════════════════════════════════════════════════════
# HETEROCYCLE SCAFFOLD LIBRARY
# ══════════════════════════════════════════════════════════════════════
# Each scaffold entry:
#   smiles   — core SMILES with [*:n] attachment points (n=1,2,...)
#   rings    — (n_rings, ring_sizes tuple)
#   het_atoms — list of heteroatom symbols
#   hbd      — number of H-bond donors in core
#   hba      — number of H-bond acceptors in core
#   aromatic — bool, fully aromatic?
#   saturated — bool, fully saturated?
#   family   — scaffold family for matching
#   priority — substituent attachment positions (indices of [*:n])

HETERO_CORE = {
    # ── 5-Membered Monocyclic Heterocycles ──
    "pyrrole_25": {
        "smiles": "[*:1]c1ccc([*:2])[nH]1",
        "rings": (1, (5,)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": True, "saturated": False, "family": "5het_1N",
        "priority": [1, 2],
    },
    "furan_25": {
        "smiles": "[*:1]c1cc([*:2])co1",
        "rings": (1, (5,)), "het_atoms": ["O"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "5het_1O",
        "priority": [1, 2],
    },
    "thiophene_25": {
        "smiles": "[*:1]c1cc([*:2])cs1",
        "rings": (1, (5,)), "het_atoms": ["S"], "hbd": 0, "hba": 0,
        "aromatic": True, "saturated": False, "family": "5het_1S",
        "priority": [1, 2],
    },
    "imidazole_14": {
        "smiles": "[*:1]c1cn([*:2])cn1",
        "rings": (1, (5,)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "5het_2N",
        "priority": [1, 2],
    },
    "imidazole_45": {
        "smiles": "[*:1]c1nc([*:2])[nH]c1",
        "rings": (1, (5,)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": True, "saturated": False, "family": "5het_2N",
        "priority": [1, 2],
    },
    "pyrazole_13": {
        "smiles": "[*:1]c1cc([*:2])n[nH]1",
        "rings": (1, (5,)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 1,
        "aromatic": True, "saturated": False, "family": "5het_2N",
        "priority": [1, 2],
    },
    "oxazole_24": {
        "smiles": "[*:1]c1nc([*:2])co1",
        "rings": (1, (5,)), "het_atoms": ["O", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "5het_ON",
        "priority": [1, 2],
    },
    "isoxazole_35": {
        "smiles": "[*:1]c1cc([*:2])no1",
        "rings": (1, (5,)), "het_atoms": ["O", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "5het_ON",
        "priority": [1, 2],
    },
    "thiazole_24": {
        "smiles": "[*:1]c1nc([*:2])cs1",
        "rings": (1, (5,)), "het_atoms": ["S", "N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "5het_SN",
        "priority": [1, 2],
    },
    "isothiazole_35": {
        "smiles": "[*:1]c1cc([*:2])ns1",
        "rings": (1, (5,)), "het_atoms": ["S", "N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "5het_SN",
        "priority": [1, 2],
    },
    "123_triazole_14": {
        "smiles": "[*:1]c1cn([*:2])nn1",
        "rings": (1, (5,)), "het_atoms": ["N", "N", "N"], "hbd": 0, "hba": 3,
        "aromatic": True, "saturated": False, "family": "5het_3N",
        "priority": [1, 2],
    },
    "124_triazole_13": {
        "smiles": "[*:1]c1nc([*:2])n[nH]1",
        "rings": (1, (5,)), "het_atoms": ["N", "N", "N"], "hbd": 1, "hba": 3,
        "aromatic": True, "saturated": False, "family": "5het_3N",
        "priority": [1, 2],
    },
    "tetrazole_15": {
        "smiles": "[*:1]c1nnn([*:2])n1",
        "rings": (1, (5,)), "het_atoms": ["N", "N", "N", "N"], "hbd": 0, "hba": 4,
        "aromatic": True, "saturated": False, "family": "5het_4N",
        "priority": [1, 2],
    },
    "124_oxadiazole_35": {
        "smiles": "[*:1]c1noc([*:2])n1",
        "rings": (1, (5,)), "het_atoms": ["O", "N", "N"], "hbd": 0, "hba": 3,
        "aromatic": True, "saturated": False, "family": "5het_ON2",
        "priority": [1, 2],
    },
    "134_oxadiazole_25": {
        "smiles": "[*:1]c1nnc([*:2])o1",
        "rings": (1, (5,)), "het_atoms": ["O", "N", "N"], "hbd": 0, "hba": 3,
        "aromatic": True, "saturated": False, "family": "5het_ON2",
        "priority": [1, 2],
    },
    "134_thiadiazole_25": {
        "smiles": "[*:1]c1nnc([*:2])s1",
        "rings": (1, (5,)), "het_atoms": ["S", "N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "5het_SN2",
        "priority": [1, 2],
    },

    # ── 6-Membered Monocyclic Heterocycles ──
    "pyridine_26": {
        "smiles": "[*:1]c1cc([*:2])ccn1",
        "rings": (1, (6,)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "6het_1N",
        "priority": [1, 2],
    },
    "pyridine_35": {
        "smiles": "[*:1]c1cncc([*:2])c1",
        "rings": (1, (6,)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "6het_1N",
        "priority": [1, 2],
    },
    "pyrimidine_24": {
        "smiles": "[*:1]c1nc([*:2])ccn1",
        "rings": (1, (6,)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "6het_2N",
        "priority": [1, 2],
    },
    "pyrimidine_46": {
        "smiles": "[*:1]c1cc([*:2])ncn1",
        "rings": (1, (6,)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "6het_2N",
        "priority": [1, 2],
    },
    "pyrazine_25": {
        "smiles": "[*:1]c1nc([*:2])cnc1",
        "rings": (1, (6,)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "6het_2N",
        "priority": [1, 2],
    },
    "pyridazine_34": {
        "smiles": "[*:1]c1cc([*:2])nnc1",
        "rings": (1, (6,)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "6het_2N",
        "priority": [1, 2],
    },
    "123_triazine_45": {
        "smiles": "[*:1]c1cc([*:2])nnn1",
        "rings": (1, (6,)), "het_atoms": ["N", "N", "N"], "hbd": 0, "hba": 3,
        "aromatic": True, "saturated": False, "family": "6het_3N",
        "priority": [1, 2],
    },
    "135_triazine_24": {
        "smiles": "[*:1]c1nc([*:2])ncn1",
        "rings": (1, (6,)), "het_atoms": ["N", "N", "N"], "hbd": 0, "hba": 3,
        "aromatic": True, "saturated": False, "family": "6het_3N",
        "priority": [1, 2],
    },
    "pyran_2H": {
        "smiles": "[*:1]C1=CC([*:2])=CCO1",
        "rings": (1, (6,)), "het_atoms": ["O"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": False, "family": "6het_1O",
        "priority": [1, 2],
    },
    "thiopyran_2H": {
        "smiles": "[*:1]C1=CC([*:2])=CCS1",
        "rings": (1, (6,)), "het_atoms": ["S"], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": False, "family": "6het_1S",
        "priority": [1, 2],
    },

    # ── Saturated Heterocycles ──
    "pyrrolidine": {
        "smiles": "[*:1]C1CC([*:2])CN1",
        "rings": (1, (5,)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "sat_5_N",
        "priority": [1, 2],
    },
    "pyrrolidine_Nsub": {
        "smiles": "[*:1]C1CCN([*:2])C1",
        "rings": (1, (5,)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "sat_5_N",
        "priority": [1, 2],
    },
    "tetrahydrofuran": {
        "smiles": "[*:1]C1CC([*:2])CO1",
        "rings": (1, (5,)), "het_atoms": ["O"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "sat_5_O",
        "priority": [1, 2],
    },
    "tetrahydrothiophene": {
        "smiles": "[*:1]C1CCSC([*:2])C1",
        "rings": (1, (5,)), "het_atoms": ["S"], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "sat_5_S",
        "priority": [1, 2],
    },
    "piperidine": {
        "smiles": "[*:1]C1CCC([*:2])CN1",
        "rings": (1, (6,)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "sat_6_N",
        "priority": [1, 2],
    },
    "piperidine_Nsub": {
        "smiles": "[*:1]C1CCN([*:2])CC1",
        "rings": (1, (6,)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "sat_6_N",
        "priority": [1, 2],
    },
    "piperazine": {
        "smiles": "[*:1]N1CCN([*:2])CC1",
        "rings": (1, (6,)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": True, "family": "sat_6_2N",
        "priority": [1, 2],
    },
    "morpholine": {
        "smiles": "[*:1]N1CCOC([*:2])C1",
        "rings": (1, (6,)), "het_atoms": ["O", "N"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": True, "family": "sat_6_ON",
        "priority": [1, 2],
    },
    "thiomorpholine": {
        "smiles": "[*:1]N1CCSC([*:2])C1",
        "rings": (1, (6,)), "het_atoms": ["S", "N"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "sat_6_SN",
        "priority": [1, 2],
    },
    "azepane": {
        "smiles": "[*:1]C1CCCC([*:2])CN1",
        "rings": (1, (7,)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "sat_7_N",
        "priority": [1, 2],
    },

    # ── Fused Bicyclic Heterocycles (5,6-systems) ──
    "indole_23": {
        "smiles": "[*:1]c1c([*:2])c2ccccc2[nH]1",
        "rings": (2, (5,6)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_56_1N",
        "priority": [1, 2],
    },
    "indole_3sub": {
        "smiles": "[*:1]c1c[nH]c2c([*:2])cccc12",
        "rings": (2, (5,6)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_56_1N",
        "priority": [1, 2],
    },
    "benzofuran_23": {
        "smiles": "[*:1]c1c([*:2])c2ccccc2o1",
        "rings": (2, (5,6)), "het_atoms": ["O"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_56_1O",
        "priority": [1, 2],
    },
    "benzothiophene_23": {
        "smiles": "[*:1]c1c([*:2])c2ccccc2s1",
        "rings": (2, (5,6)), "het_atoms": ["S"], "hbd": 0, "hba": 0,
        "aromatic": True, "saturated": False, "family": "fused_56_1S",
        "priority": [1, 2],
    },
    "benzimidazole_2sub": {
        "smiles": "[*:1]c1nc2cc([*:2])ccc2[nH]1",
        "rings": (2, (5,6)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_56_2N",
        "priority": [1, 2],
    },
    "benzothiazole_2sub": {
        "smiles": "[*:1]c1nc2cc([*:2])ccc2s1",
        "rings": (2, (5,6)), "het_atoms": ["S", "N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_56_SN",
        "priority": [1, 2],
    },
    "benzoxazole_2sub": {
        "smiles": "[*:1]c1nc2cc([*:2])ccc2o1",
        "rings": (2, (5,6)), "het_atoms": ["O", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_56_ON",
        "priority": [1, 2],
    },

    # ── Fused Bicyclic Heterocycles (6,6-systems) ──
    "quinoline_23": {
        "smiles": "[*:1]c1cc2cc([*:2])ccc2nc1",
        "rings": (2, (6,6)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_66_1N",
        "priority": [1, 2],
    },
    "quinoline_58": {
        "smiles": "[*:1]c1ccc2c([*:2])ccnc2c1",
        "rings": (2, (6,6)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_66_1N",
        "priority": [1, 2],
    },
    "isoquinoline_14": {
        "smiles": "[*:1]c1nccc2cc([*:2])ccc12",
        "rings": (2, (6,6)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_66_1N",
        "priority": [1, 2],
    },
    "quinazoline_24": {
        "smiles": "[*:1]c1nc2cc([*:2])ccc2cn1",
        "rings": (2, (6,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_66_2N",
        "priority": [1, 2],
    },
    "quinoxaline_23": {
        "smiles": "[*:1]c1nc2cc([*:2])ccc2nc1",
        "rings": (2, (6,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_66_2N",
        "priority": [1, 2],
    },
    "cinnoline_34": {
        "smiles": "[*:1]c1cc2cc([*:2])ccc2nn1",
        "rings": (2, (6,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_66_2N",
        "priority": [1, 2],
    },
    "purine_26": {
        "smiles": "[*:1]c1nc2nc([*:2])ncc2[nH]1",
        "rings": (2, (5,6)), "het_atoms": ["N", "N", "N", "N"], "hbd": 1, "hba": 4,
        "aromatic": True, "saturated": False, "family": "fused_56_4N",
        "priority": [1, 2],
    },
    "pteridine_24": {
        "smiles": "[*:1]c1nc2nc([*:2])cnc2cn1",
        "rings": (2, (6,6)), "het_atoms": ["N", "N", "N", "N"], "hbd": 0, "hba": 4,
        "aromatic": True, "saturated": False, "family": "fused_66_4N",
        "priority": [1, 2],
    },
    "naphthyridine_15": {
        "smiles": "[*:1]c1cc2c([*:2])ccnc2cn1",
        "rings": (2, (6,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_66_2N",
        "priority": [1, 2],
    },
    "chromone_23": {
        "smiles": "[*:1]c1coc2cc([*:2])ccc2c1=O",
        "rings": (2, (6,6)), "het_atoms": ["O"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": False, "family": "fused_66_1O_carb",
        "priority": [1, 2],
    },
    "coumarin_34": {
        "smiles": "[*:1]c1cc(=O)oc2cc([*:2])ccc12",
        "rings": (2, (6,6)), "het_atoms": ["O", "O"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": False, "family": "fused_66_2O",
        "priority": [1, 2],
    },

    # ── Tricyclic / Polycyclic Heterocycles ──
    "acridine_29": {
        "smiles": "[*:1]c1ccc2cc3cc([*:2])ccc3nc2c1",
        "rings": (3, (6,6,6)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_666_1N",
        "priority": [1, 2],
    },
    "phenazine_29": {
        "smiles": "[*:1]c1ccc2nc3cc([*:2])ccc3nc2c1",
        "rings": (3, (6,6,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_666_2N",
        "priority": [1, 2],
    },
    "phenothiazine": {
        "smiles": "[*:1]c1ccc2Sc3cc([*:2])ccc3Nc2c1",
        "rings": (3, (6,6,6)), "het_atoms": ["S", "N"], "hbd": 1, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_666_SN",
        "priority": [1, 2],
    },
    "carbazole_36": {
        "smiles": "[*:1]c1ccc2c(c1)[nH]c1cc([*:2])ccc12",
        "rings": (3, (5,6,6)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_566_1N",
        "priority": [1, 2],
    },
    "dibenzofuran": {
        "smiles": "[*:1]c1ccc2oc3cc([*:2])ccc3c2c1",
        "rings": (3, (5,6,6)), "het_atoms": ["O"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_566_1O",
        "priority": [1, 2],
    },
    "dibenzothiophene": {
        "smiles": "[*:1]c1ccc2sc3cc([*:2])ccc3c2c1",
        "rings": (3, (5,6,6)), "het_atoms": ["S"], "hbd": 0, "hba": 0,
        "aromatic": True, "saturated": False, "family": "fused_566_1S",
        "priority": [1, 2],
    },
    "xanthone": {
        "smiles": "[*:1]c1ccc2c(c1)C(=O)c1cc([*:2])ccc1O2",
        "rings": (3, (6,6,6)), "het_atoms": ["O", "O"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": False, "family": "fused_666_2O_carb",
        "priority": [1, 2],
    },

    # ── Spiro and Bridged Heterocycles ──
    "spiro_piperidine_oxetane": {
        "smiles": "[*:1]C1CCC2(CC1)COC([*:2])C2",
        "rings": (2, (6,4)), "het_atoms": ["N", "O"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": True, "family": "spiro_NO",
        "priority": [1, 2],
    },
    "spiro_indoline_pyrrolidine": {
        "smiles": "[*:1]c1ccc2c(c1)CC1(CCCN1[*:2])N2",
        "rings": (3, (5,5,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": True, "family": "spiro_2N",
        "priority": [1, 2],
    },
    "tropane": {
        "smiles": "[*:1]C1CC2CCC([*:2])(C1)N2C",
        "rings": (2, (6,5)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_N",
        "priority": [1, 2],
    },
    "quinuclidine": {
        "smiles": "[*:1]C1CN2CCC1([*:2])CC2",
        "rings": (3, (6,6,6)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_3ring_N",
        "priority": [1, 2],
    },
    "diazabicyclo_222_octane": {
        "smiles": "[*:1]N1CC2CCN(CC1[*:2])C2",
        "rings": (3, (6,6,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_2N",
        "priority": [1, 2],
    },
    "hexahydro_25_methanopyrrolo_isoquinoline": {
        "smiles": "[*:1]c1ccc2c(c1)C1CC3CCCN3C([*:2])C1N2",
        "rings": (4, (5,6,6,6)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_poly_N",
        "priority": [1, 2],
    },
# ════════════════════════════════════════════════════════════════
    # EXPANDED: Bridged Bicyclic Carbocyclic Systems
    # ════════════════════════════════════════════════════════════════

    "norbornane_27": {
        "smiles": "[*:1]C1CC2CCC1([*:2])C2",
        "rings": (2, (5,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "bridged_carbo",
        "priority": [1, 2],
    },
    "norbornene_25": {
        "smiles": "[*:1]C1CC2C=CC1([*:2])C2",
        "rings": (2, (5,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": False, "family": "bridged_carbo_unsat",
        "priority": [1, 2],
    },
    "bicyclo_222_octane": {
        "smiles": "[*:1]C1CC2CCC1([*:2])CC2",
        "rings": (2, (6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "bridged_carbo",
        "priority": [1, 2],
    },
    "bicyclo_321_octane": {
        "smiles": "[*:1]C1CC2CCCC1([*:2])C2",
        "rings": (2, (5,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "bridged_carbo",
        "priority": [1, 2],
    },
    "bicyclo_331_nonane": {
        "smiles": "[*:1]C1CC2CCCC1([*:2])CC2",
        "rings": (2, (6,7)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "bridged_carbo_large",
        "priority": [1, 2],
    },
    "bicyclo_440_decane_cis": {
        "smiles": "[*:1]C1CCC2CCCCC2C1[*:2]",
        "rings": (2, (6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "fused_carbo",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Bridged Heterocycles (N-containing)
    # ════════════════════════════════════════════════════════════════

    "7_azabicyclo_221_heptane": {
        "smiles": "[*:1]C1CC2CCC1([*:2])N2",
        "rings": (2, (5,6)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_1N",
        "priority": [1, 2],
    },
    "2_azabicyclo_222_octane": {
        "smiles": "[*:1]C1CC2CCC1([*:2])CN2",
        "rings": (2, (6,6)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_1N",
        "priority": [1, 2],
    },
    "3_azabicyclo_321_octane": {
        "smiles": "[*:1]C1CC2CNCC1([*:2])C2",
        "rings": (2, (5,6)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_1N",
        "priority": [1, 2],
    },
    "8_azabicyclo_321_octane": {
        "smiles": "[*:1]C1CC2CCC1([*:2])CN2",
        "rings": (2, (5,6)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_1N",
        "priority": [1, 2],
    },
    "9_azabicyclo_331_nonane": {
        "smiles": "[*:1]C1CC2CCCN([*:2])C1C2",
        "rings": (2, (6,7)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_1N_large",
        "priority": [1, 2],
    },
    "2_azabicyclo_310_hexane": {
        "smiles": "[*:1]C1CC2CC1([*:2])N2",
        "rings": (2, (4,5)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_1N_small",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Bridged Heterocycles (N,N-diaza)
    # ════════════════════════════════════════════════════════════════

    "37_diazabicyclo_331_nonane": {
        "smiles": "[*:1]N1CC2CC(C1)CN([*:2])C2",
        "rings": (2, (6,7)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_2N",
        "priority": [1, 2],
    },
    "39_diazabicyclo_331_nonane": {
        "smiles": "[*:1]N1CCCN2CCC1([*:2])C2",
        "rings": (2, (6,7)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_2N",
        "priority": [1, 2],
    },
    "28_diazabicyclo_321_octane": {
        "smiles": "[*:1]C1CC2CNC1([*:2])CN2",
        "rings": (2, (5,6)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_2N",
        "priority": [1, 2],
    },
    "26_diazabicyclo_222_octane": {
        "smiles": "[*:1]C1CN2CCC1([*:2])CN2",
        "rings": (2, (6,6)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_2N",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Bridged Heterocycles (O-containing)
    # ════════════════════════════════════════════════════════════════

    "7_oxabicyclo_221_heptane": {
        "smiles": "[*:1]C1CC2CCC1([*:2])O2",
        "rings": (2, (5,6)), "het_atoms": ["O"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_1O",
        "priority": [1, 2],
    },
    "8_oxabicyclo_321_octane": {
        "smiles": "[*:1]C1CC2CCC1([*:2])CO2",
        "rings": (2, (5,6)), "het_atoms": ["O"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_1O",
        "priority": [1, 2],
    },
    "2_oxa_5_azabicyclo_221_heptane": {
        "smiles": "[*:1]C1CC2COC1([*:2])N2",
        "rings": (2, (5,6)), "het_atoms": ["O", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_ON",
        "priority": [1, 2],
    },
    "3_oxa_7_azabicyclo_331_nonane": {
        "smiles": "[*:1]C1CC2COCC1([*:2])CN2",
        "rings": (2, (6,7)), "het_atoms": ["O", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_ON_large",
        "priority": [1, 2],
    },
    "8_oxa_3_azabicyclo_321_octane": {
        "smiles": "[*:1]C1CC2COC1([*:2])CN2",
        "rings": (2, (5,6)), "het_atoms": ["O", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "bridged_ON",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Bridged Heterocycles (S-containing)
    # ════════════════════════════════════════════════════════════════

    "7_thiabicyclo_221_heptane": {
        "smiles": "[*:1]C1CC2CCC1([*:2])S2",
        "rings": (2, (5,6)), "het_atoms": ["S"], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "bridged_1S",
        "priority": [1, 2],
    },
    "8_thiabicyclo_321_octane": {
        "smiles": "[*:1]C1CC2CCC1([*:2])CS2",
        "rings": (2, (5,6)), "het_atoms": ["S"], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "bridged_1S",
        "priority": [1, 2],
    },
    "3_thia_7_azabicyclo_331_nonane": {
        "smiles": "[*:1]C1CC2CSCC1([*:2])CN2",
        "rings": (2, (6,7)), "het_atoms": ["S", "N"], "hbd": 1, "hba": 1,
        "aromatic": False, "saturated": True, "family": "bridged_SN",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Tricyclic & Cage Carbocyclic Systems
    # ════════════════════════════════════════════════════════════════

    "adamantane": {
        "smiles": "[*:1]C1C2CC3CC1CC([*:2])(C2)C3",
        "rings": (3, (6,6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "cage_carbo",
        "priority": [1, 2],
    },
    "twistane": {
        "smiles": "[*:1]C1CC2CC3CCC1([*:2])CC2C3",
        "rings": (3, (6,6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "cage_carbo",
        "priority": [1, 2],
    },
    "noradamantane": {
        "smiles": "[*:1]C1C2CC3CC1([*:2])CC2C3",
        "rings": (3, (5,6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "cage_carbo_small",
        "priority": [1, 2],
    },
    "tricyclo_331_137_decane": {
        "smiles": "[*:1]C1CC2CC3CCC1([*:2])CC2C3",
        "rings": (3, (6,6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": False, "saturated": True, "family": "cage_carbo",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Cage Heterocycles (aza-adamantanes)
    # ════════════════════════════════════════════════════════════════

    "1_azaadamantane": {
        "smiles": "[*:1]C1C2CN3CC1CC([*:2])(C2)C3",
        "rings": (3, (6,6,6)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "cage_1N",
        "priority": [1, 2],
    },
    "2_azaadamantane": {
        "smiles": "[*:1]C1C2CC3CN1CC([*:2])(C2)C3",
        "rings": (3, (6,6,6)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "cage_1N",
        "priority": [1, 2],
    },
    "hexamine_cage": {
        "smiles": "[*:1]C1N2CN3CN1CN([*:2])C2C3",
        "rings": (4, (6,6,6,6)), "het_atoms": ["N", "N", "N", "N"], "hbd": 0, "hba": 4,
        "aromatic": False, "saturated": True, "family": "cage_polyN",
        "priority": [1, 2],
    },
    "14_diazaadamantane": {
        "smiles": "[*:1]C1C2CN3CCN1CC([*:2])(C2)C3",
        "rings": (3, (6,6,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": True, "family": "cage_2N",
        "priority": [1, 2],
    },
    "oxaadamantane": {
        "smiles": "[*:1]C1C2CC3CC1CC([*:2])(C2)O3",
        "rings": (3, (6,6,6)), "het_atoms": ["O"], "hbd": 0, "hba": 1,
        "aromatic": False, "saturated": True, "family": "cage_1O",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Fused Polycyclic (3+ rings) All-Carbon
    # ════════════════════════════════════════════════════════════════

    "phenanthrene_29": {
        "smiles": "[*:1]c1ccc2c(c1)ccc1cc([*:2])ccc21",
        "rings": (3, (6,6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": True, "saturated": False, "family": "polyarom",
        "priority": [1, 2],
    },
    "pyrene_16": {
        "smiles": "[*:1]c1cc2ccc3cccc4ccc1c2c34[*:2]",
        "rings": (4, (6,6,6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": True, "saturated": False, "family": "polyarom",
        "priority": [1, 2],
    },
    "chrysene_612": {
        "smiles": "[*:1]c1ccc2c(c1)ccc1c3ccccc3cc([*:2])c21",
        "rings": (4, (6,6,6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": True, "saturated": False, "family": "polyarom",
        "priority": [1, 2],
    },
    "fluoranthene_38": {
        "smiles": "[*:1]c1ccc2c3c1cccc3c1cccc2c1[*:2]",
        "rings": (4, (5,6,6,6)), "het_atoms": [], "hbd": 0, "hba": 0,
        "aromatic": True, "saturated": False, "family": "polyarom",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Tricyclic Heterocycles (fused)
    # ════════════════════════════════════════════════════════════════

    "phenanthridine_56": {
        "smiles": "[*:1]c1ccc2c(c1)cnc1cc([*:2])ccc21",
        "rings": (3, (6,6,6)), "het_atoms": ["N"], "hbd": 0, "hba": 1,
        "aromatic": True, "saturated": False, "family": "fused_666_1N",
        "priority": [1, 2],
    },
    "benzo_c_cinnoline": {
        "smiles": "[*:1]c1ccc2c(c1)nnc1cc([*:2])ccc21",
        "rings": (3, (6,6,6)), "het_atoms": ["N", "N"], "hbd": 0, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_666_2N",
        "priority": [1, 2],
    },
    "phenoxazine_310": {
        "smiles": "[*:1]c1ccc2Nc3cc([*:2])ccc3Oc2c1",
        "rings": (3, (6,6,6)), "het_atoms": ["O", "N"], "hbd": 1, "hba": 2,
        "aromatic": True, "saturated": False, "family": "fused_666_ON",
        "priority": [1, 2],
    },
    "benzocarbazole": {
        "smiles": "[*:1]c1ccc2c(c1)c1cc3cc([*:2])ccc3nc1c1ccccc21",
        "rings": (4, (5,6,6,6)), "het_atoms": ["N"], "hbd": 1, "hba": 1,
        "aromatic": True, "saturated": False, "family": "polyarom_1N",
        "priority": [1, 2],
    },

    # ════════════════════════════════════════════════════════════════
    # EXPANDED: Spiro Polycyclic Heterocycles
    # ════════════════════════════════════════════════════════════════

    "spiro_pyrrolidine_piperidine": {
        "smiles": "[*:1]C1CCCN2CCCC12[*:2]",
        "rings": (2, (5,6)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "spiro_2N",
        "priority": [1, 2],
    },
    "spiro_piperidine_tetrahydrofuran": {
        "smiles": "[*:1]C1CCCOC12CCN([*:2])CC2",
        "rings": (2, (5,6)), "het_atoms": ["O", "N"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": True, "family": "spiro_ON",
        "priority": [1, 2],
    },
    "spiro_chroman_piperidine": {
        "smiles": "[*:1]N1CCC2(CC1)COc1ccc([*:2])cc21",
        "rings": (3, (6,6,6)), "het_atoms": ["O", "N"], "hbd": 0, "hba": 2,
        "aromatic": False, "saturated": False, "family": "spiro_ON_arom",
        "priority": [1, 2],
    },
    "dispiro_piperazine": {
        "smiles": "[*:1]C1CC23CCN(CC2)CC3N([*:2])C1",
        "rings": (3, (6,6,6)), "het_atoms": ["N", "N"], "hbd": 1, "hba": 2,
        "aromatic": False, "saturated": True, "family": "dispiro_2N",
        "priority": [1, 2],
    },
}


# ══════════════════════════════════════════════════════════════════════
# SITE-TO-SCAFFOLD MATCHING ENGINE
# ══════════════════════════════════════════════════════════════════════

def _get_site_ordinals(site_type: Dict[str, str]) -> Dict[str, int]:
    """Convert glyph site type to ordinal dict."""
    from rhr_p4rky.ligand_from_active_site import GLYPH_ORDINALS
    ords = {}
    for pn in ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]:
        g = site_type.get(pn, "?")
        ords[pn] = GLYPH_ORDINALS.get(pn, {}).get(g, -1)
    return ords


def match_scaffolds_to_site(site_type: Dict[str, str], n_top: int = 25) -> List[str]:
    """Match heterocycle scaffolds to an active site structural type.

    Maps the 12-primitive site type to preferred scaffold families,
    then scores all scaffolds against the site profile.

    Returns list of scaffold names, best match first.
    """
    o = _get_site_ordinals(site_type)

    # ── Determine preferred scaffold properties from site type ──
    # T (topology): ring count preference
    t_val = o["T"]
    if t_val >= 4:   # odot closure
        target_rings = (3, 4)       # polycyclic
        target_saturation = False    # aromatic preferred
    elif t_val >= 3:  # boxtimes
        target_rings = (2, 3)
        target_saturation = False
    elif t_val >= 2:  # bowtie
        target_rings = (2, 2)
        target_saturation = None     # either
    elif t_val >= 1:  # in
        target_rings = (1, 2)
        target_saturation = None
    else:              # net
        target_rings = (1, 1)
        target_saturation = True     # saturated preferred

    # R (coupling): heteroatom complexity
    r_val = o["R"]
    if r_val >= 3:   # lr bidirectional
        target_het_count = (3, 6)
    elif r_val >= 2:  # dagger adjoint
        target_het_count = (2, 4)
    elif r_val >= 1:  # cat functorial
        target_het_count = (1, 3)
    else:              # super
        target_het_count = (1, 2)

    # K (kinetics): saturated vs aromatic
    k_val = o["K"]
    if k_val <= 1:  # MBL or trap
        target_saturation = True
    elif k_val >= 3:  # fast
        target_saturation = False
    # else: keep from T determination

    # Ph (criticality): electron richness
    ph_val = o["Ph"]
    if ph_val >= 4:  # supercritical
        prefer_e_rich = True
    elif ph_val >= 2:  # c_complex
        prefer_e_rich = False      # electron-poor preferred
    else:
        prefer_e_rich = None

    # H (chirality): stereochemical complexity
    h_val = o["H"]
    if h_val >= 3:  # eternal
        target_chiral = True
    elif h_val >= 2:  # two
        target_chiral = True
    else:
        target_chiral = False

    # ── Score all scaffolds ──
    scores = {}
    for name, sc in HETERO_CORE.items():
        score = 0.0

        # Ring count match
        n_rings = sc["rings"][0]
        if target_rings[0] <= n_rings <= target_rings[1]:
            score += 3.0
        elif abs(n_rings - target_rings[0]) == 1:
            score += 1.0

        # Heteroatom count match
        n_het = len(sc["het_atoms"])
        if target_het_count[0] <= n_het <= target_het_count[1]:
            score += 2.0
        elif abs(n_het - target_het_count[0]) == 1:
            score += 0.5

        # Saturation match
        if target_saturation is not None:
            if sc["saturated"] == target_saturation:
                score += 2.0
            elif target_saturation is False and not sc["aromatic"]:
                score += 0.5

        # Electron richness preference
        if prefer_e_rich is True:
            # e-rich: S, O heterocycles, pyrrole-type N
            if "O" in sc["het_atoms"] or "S" in sc["het_atoms"]:
                score += 1.0
            if sc.get("hbd", 0) > 0:  # N-H donors = e-rich
                score += 0.5
        elif prefer_e_rich is False:
            # e-poor: pyridine-type N, multiple N
            if sc["het_atoms"].count("N") >= 2:
                score += 1.0
            if sc.get("hbd", 0) == 0 and sc.get("hba", 0) >= 2:
                score += 0.5

        # Chirality potential
        if target_chiral and sc["saturated"]:
            score += 1.5

        # H-bond complement: match site HBD/HBA profile
        site_hbd = o["K"]  # K proxies for H-bond donor capacity
        if site_hbd <= 1 and sc.get("hba", 0) >= 2:
            score += 0.5
        if site_hbd >= 3 and sc.get("hbd", 0) >= 1:
            score += 0.5

        
        # ── Bridged carbocyclic bonus ──
        if "bridged" in sc.get("family", ""):
            if t_val >= 3:
                score += 2.0
            elif t_val >= 2:
                score += 1.0
            if target_chiral:
                score += 1.0
            if sc["saturated"] and target_saturation is False:
                score += 0.5

        # ── Cage system bonus ──
        if "cage" in sc.get("family", ""):
            if t_val >= 4:
                score += 3.0
            elif t_val >= 3:
                score += 1.5
            if sc["saturated"]:
                score += 0.5
            if len(sc["het_atoms"]) >= 2:
                score += 1.0

        # ── Polyaromatic bonus ──
        if "polyarom" in sc.get("family", ""):
            if sc["aromatic"] and target_saturation is False:
                score += 1.5
            if ph_val >= 2:
                score += 1.0
            if n_rings >= 4:
                score += 1.5

        # ── Spiro/dispiro bonus ──
        if "spiro" in sc.get("family", "") or "dispiro" in sc.get("family", ""):
            if target_chiral:
                score += 1.5
            if t_val >= 2:
                score += 0.5
            if len(sc["het_atoms"]) >= 2:
                score += 0.5


# Sulfur complement: W (winding) high → S-containing scaffolds
        if o["W"] >= 2 and "S" in sc["het_atoms"]:
            score += 1.0

        # P/F complement — high P + high F = demand complex aromatic polycyclics
        p_val = o["P"]
        f_val = o["F"]
        if p_val >= 3 and f_val >= 2:
            # Frobenius-special parity + quantum fidelity → polycyclic aromatics
            if n_rings >= 3:
                score += 2.5
            elif n_rings >= 2:
                score += 1.5
            if sc["aromatic"] and n_het >= 2:
                score += 1.5
            if n_het >= 3:
                score += 1.0
        elif p_val >= 3:
            # High symmetry → multi-ring
            if n_rings >= 2:
                score += 1.0
            if sc["aromatic"]:
                score += 0.5
        elif f_val >= 2:
            # Quantum fidelity → aromatic
            if sc["aromatic"]:
                score += 1.0
            if n_rings >= 2:
                score += 0.5

        # S (stoichiometry) complement
        s_val = o["S"]
        if s_val >= 2:  # heterogeneous → diverse heteroatoms
            if len(set(sc["het_atoms"])) >= 3:
                score += 1.0
            elif len(set(sc["het_atoms"])) >= 2:
                score += 0.5

        scores[name] = score

    # Sort by score, take top N
    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return [name for name, score in ranked[:n_top]]


# ══════════════════════════════════════════════════════════════════════
# SCAFFOLD ELABORATION — Substituent Placement
# ══════════════════════════════════════════════════════════════════════

def _get_fg_smiles_list(fg_names: List[str], max_per_fg: int = 2) -> List[str]:
    """Get SMILES fragments for a list of FG names."""
    frags = []
    for fg in fg_names:
        if fg in FG_FRAGMENTS:
            frags.extend(FG_FRAGMENTS[fg][:max_per_fg])
    return frags


def elaborate_scaffold(
    scaffold_name: str,
    fg_names: List[str],
    site_type: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Elaborate a heterocycle scaffold with substituent fragments.

    Uses RDKit RWMol for proper atom-by-atom fragment attachment
    rather than naive string replacement. This ensures chemically
    valid connections at all attachment points.

    Returns list of (method_tag, SMILES) tuples.
    """
    if scaffold_name not in HETERO_CORE:
        return []

    sc = HETERO_CORE[scaffold_name]
    core_smi = sc["smiles"]
    frag_smis = _get_fg_smiles_list(fg_names, max_per_fg=2)

    if not frag_smis:
        frag_smis = ["C", "N", "O", "C(=O)O", "C(=O)N"]

    molecules = []

    # Parse core scaffold with RDKit to find dummy atom positions
    try:
        core_mol = Chem.MolFromSmiles(core_smi)
        if core_mol is None:
            # Fall back to string-based for unparseable scaffolds
            return _elaborate_by_string(core_smi, frag_smis, sc)
    except:
        return _elaborate_by_string(core_smi, frag_smis, sc)

    # Find dummy atoms [*:1] and [*:2]
    dummy_atoms = []
    for atom in core_mol.GetAtoms():
        if atom.GetSymbol() == '*' and atom.HasProp('molAtomMapNumber'):
            dummy_atoms.append(atom)

    if len(dummy_atoms) < 2:
        return _elaborate_by_string(core_smi, frag_smis, sc)

    # Sort by atom map number
    dummy_atoms.sort(key=lambda a: int(a.GetProp('molAtomMapNumber')))
    d1, d2 = dummy_atoms[0], dummy_atoms[1]

    # Get the neighbors of each dummy atom (the actual attachment points)
    nbr1 = [a for a in d1.GetNeighbors()][0] if d1.GetNeighbors() else None
    nbr2 = [a for a in d2.GetNeighbors()][0] if d2.GetNeighbors() else None

    # Strategy: Use SMILES with explicit attachment via carbon linker
    # Replace dummy atoms with CH2 groups first, then swap CH2->FG
    def _attach_fg_at_position(core_mol, dummy_atom, fg_smi, keep_other_dummy=True):
        """Attach FG at dummy position. Other dummy stays as CH3."""
        try:
            rw = Chem.RWMol(core_mol)
            dummy_idx = dummy_atom.GetIdx()
            nbr = [a for a in dummy_atom.GetNeighbors()]
            if not nbr:
                return None
            nbr_idx = nbr[0].GetIdx()

            # Remove dummy atom and its neighbor's bond
            rw.RemoveAtom(dummy_idx)

            # Parse FG fragment
            fg_mol = Chem.MolFromSmiles(fg_smi)
            if fg_mol is None:
                return None

            # Combine core + FG, create bond between nbr and first carbon of FG
            combined = Chem.CombineMols(rw.GetMol(), fg_mol)
            rw2 = Chem.RWMol(combined)
            nbr_new_idx = nbr_idx if nbr_idx < dummy_idx else nbr_idx - 1
            fg_start = rw.GetMol().GetNumAtoms()
            rw2.AddBond(nbr_new_idx, fg_start, Chem.BondType.SINGLE)

            mol = rw2.GetMol()
            with _silence_rdkit():
                Chem.SanitizeMol(mol)
            return Chem.MolToSmiles(mol)
        except:
            return None

    # Strategy 1: Attach FG1 at position 1, leave position 2 as H
    for f1 in frag_smis:
        result = _attach_fg_at_position(core_mol, d1, f1)
        if result:
            # Remove other dummy
            try:
                mol = Chem.MolFromSmiles(result)
                if mol:
                    dummies_left = [a for a in mol.GetAtoms() if a.GetSymbol() == '*']
                    if dummies_left:
                        rw = Chem.RWMol(mol)
                        for da in sorted(dummies_left, key=lambda a: a.GetIdx(), reverse=True):
                            rw.RemoveAtom(da.GetIdx())
                        mol = rw.GetMol()
                        with _silence_rdkit():
                            Chem.SanitizeMol(mol)
                        molecules.append(("mono_1", Chem.MolToSmiles(mol)))
            except:
                molecules.append(("mono_1_str", result))

    # Strategy 2: Attach FG2 at position 2
    for f2 in frag_smis:
        result = _attach_fg_at_position(core_mol, d2, f2)
        if result:
            try:
                mol = Chem.MolFromSmiles(result)
                if mol:
                    dummies_left = [a for a in mol.GetAtoms() if a.GetSymbol() == '*']
                    if dummies_left:
                        rw = Chem.RWMol(mol)
                        for da in sorted(dummies_left, key=lambda a: a.GetIdx(), reverse=True):
                            rw.RemoveAtom(da.GetIdx())
                        mol = rw.GetMol()
                        with _silence_rdkit():
                            Chem.SanitizeMol(mol)
                        molecules.append(("mono_2", Chem.MolToSmiles(mol)))
            except:
                molecules.append(("mono_2_str", result))

    # If RDKit-based assembly failed, fall back to string-based
    if len(molecules) < 2:
        molecules.extend(_elaborate_by_string(core_smi, frag_smis, sc))

    return molecules


def _elaborate_by_string(core_smi: str, frag_smis: List[str],
                         sc: Dict) -> List[Tuple[str, str]]:
    """Fallback SMILES string-based elaboration."""
    molecules = []
    # Ensure all FGs start with carbon for clean connection
    frag_smis_clean = []
    for f in frag_smis:
        # If FG starts with a heteroatom, prepend a CH2 linker
        first_char = f[0]
        if first_char in 'NOSPFClBrI[cnos]':
            f = 'C' + f
        frag_smis_clean.append(f)

    for f1 in frag_smis_clean:
        smi = core_smi.replace("[*:1]", f1).replace("[*:2]", "")
        smi = smi.replace("-)", ")").replace("(-", "(").replace("--", "-")
        molecules.append(("mono_1", smi))

    for f2 in frag_smis_clean:
        smi = core_smi.replace("[*:2]", f2).replace("[*:1]", "")
        smi = smi.replace("-)", ")").replace("(-", "(").replace("--", "-")
        molecules.append(("mono_2", smi))

    for fg in frag_smis_clean:
        smi = core_smi.replace("[*:1]", fg).replace("[*:2]", fg)
        smi = smi.replace("-)", ")").replace("(-", "(").replace("--", "-")
        molecules.append(("bis_same", smi))

    for f1 in frag_smis_clean:
        for f2 in frag_smis_clean:
            if f1 == f2:
                continue
            smi = core_smi.replace("[*:1]", f1).replace("[*:2]", f2)
            smi = smi.replace("-)", ")").replace("(-", "(").replace("--", "-")
            molecules.append(("bis_diff", smi))

    return molecules


# ══════════════════════════════════════════════════════════════════════
# VALIDATION & SCORING
# ══════════════════════════════════════════════════════════════════════

def _validate_and_score_smiles(
    smi: str,
    method: str,
    site_type: Optional[Dict[str, str]],
    target_mol: Optional[Chem.Mol],
    scaffold_info: Optional[Dict] = None,
) -> Optional[Dict]:
    """Validate a SMILES, compute properties, and return scored candidate.

    CHEMICAL SPACE: Unbounded. The only hard gate is MolFromSmiles
    (can RDKit parse the connectivity?). Sanitization failures (kekulization,
    valence rules) are NOT rejections — they're flags for exotic chemistry.
    Property filters are wide to admit strained, unusual, and non-drug-like
    molecules that conventional pipelines would discard.
    """
    sanitized = True
    try:
        with _silence_rdkit():
            mol = Chem.MolFromSmiles(smi)
        if mol is None:
            return None
        with _silence_rdkit():
            Chem.SanitizeMol(mol)
        canon = Chem.MolToSmiles(mol)
    except:
        # Sanitization failed — molecule is exotic but structurally valid.
        # Rebuild from SMILES without sanitization for property computation.
        sanitized = False
        try:
            with _silence_rdkit():
                mol = Chem.MolFromSmiles(smi, sanitize=False)
            if mol is None:
                return None
            # Try partial sanitization: update property cache only
            try:
                mol.UpdatePropertyCache(strict=False)
            except:
                pass
            canon = smi  # Keep original SMILES for exotic molecules
        except:
            return None

    # --- Property computation (best-effort) ---
    try:
        mw = Descriptors.MolWt(mol)
        heavy = mol.GetNumHeavyAtoms()
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
    except:
        mw, heavy, hbd, hba = 0, 0, 0, 0
    try:
        logp = Descriptors.MolLogP(mol)
    except:
        logp = 0.0
    try:
        n_rings = Lipinski.RingCount(mol)
        n_rot = Descriptors.NumRotatableBonds(mol)
        n_arom = Lipinski.NumAromaticRings(mol)
        tpsa = Descriptors.TPSA(mol)
    except:
        n_rings, n_rot, n_arom, tpsa = 0, 0, 0, 0.0

    # Property filters — WIDE gates (unbounded chemical space).
    # Only reject physically impossible cases (e.g. zero atoms).
    if heavy < 3:
        return None
    # MW: allow up to 1200 Da (peptides, macrocycles, organometallics)
    if mw > 1200:
        return None
    # logP: allow -10 to +15 (exotic but physically realizable)
    if logp < -10 or logp > 15:
        return None

    # Exotic bonus: molecules that fail RDKit sanitization are often
    # the most interesting — unusual valences, strained rings, radical species.
    exotic_bonus = 0.10 if not sanitized else 0.0

    # Fingerprint similarity (skip if unsanitized — fingerprint may be unreliable)
    fp_score = _score_by_fingerprint(mol, target_mol) if sanitized else 0.5

    # Drug-likeness (skip if unsanitized — descriptors may be unstable)
    drug_score = _score_drug_likeness(mol) if sanitized else 0.5

    # Structural complement score — multi-factor
    struct_score = _score_structural_complement(mol, site_type, scaffold_info) if site_type else 0.5

    # Heterocycle bonus: if the molecule contains heteroatoms beyond C,H
    het_types = set()
    for atom in mol.GetAtoms():
        sym = atom.GetSymbol()
        if sym not in ("C", "H"):
            het_types.add(sym)
    het_bonus = min(0.15, len(het_types) * 0.04)

    composite = round(
        0.40 * struct_score + 0.20 * drug_score + 0.20 * fp_score
        + het_bonus + exotic_bonus + 0.05, 3
    )

    return {
        "smiles": canon,
        "method": method,
        "fp_score": round(fp_score, 3),
        "drug_score": round(drug_score, 3),
        "struct_score": round(struct_score, 3),
        "composite_score": composite,
        "logP": round(logp, 2),
        "MW": round(mw, 1),
        "heavy_atoms": heavy,
        "HBD": hbd,
        "HBA": hba,
        "rings": n_rings,
        "aromatic_rings": n_arom,
        "rotatable": n_rot,
        "TPSA": round(tpsa, 1),
        "heteroatoms": sorted(het_types),
        "sanitized": sanitized,
        "valid": True,
    }


# ══════════════════════════════════════════════════════════════════════
# MAIN GENERATION FUNCTION — Heterocycle Ligand Generation
# ══════════════════════════════════════════════════════════════════════

def generate_heterocycle_ligands(
    site_type: Dict[str, str],
    fg_names: Optional[List[str]] = None,
    substrate_hint: str = "",
    max_candidates: int = 30,
    n_scaffolds: int = 25,
) -> List[Dict]:
    """Generate de-novo heterocyclic/polycyclic ligands from an active site type.

    Pipeline:
      1. Match scaffolds to site type → get top N scaffold names
      2. If fg_names not provided, estimate from site type
      3. For each scaffold + FG combination, elaborate with substituents
      4. Validate all SMILES via RDKit
      5. Score against drug-likeness, structural complement, fingerprint
      6. Rank by composite score and return top candidates

    Args:
        site_type: 12-primitive dict of the enzyme active site
        fg_names: Optional list of FG names (auto-estimated if None)
        substrate_hint: Optional known substrate SMILES for fingerprint scoring
        max_candidates: Max candidates to return
        n_scaffolds: Number of top scaffolds to use

    Returns:
        List of scored candidate dicts
    """
    # Import bond/FG estimators from sister module
    from rhr_p4rky.ligand_improvements import (
        _estimate_bond_from_site_type, _estimate_fgs_from_site_type
    )

    if fg_names is None:
        # First estimate bond type from site
        bond_name = _estimate_bond_from_site_type(site_type)
        fg_names = _estimate_fgs_from_site_type(site_type, bond_name)

    print(f"    Bond: {bond_name if 'bond_name' in locals() else 'auto'}, FGs: {fg_names}")

    # Match scaffolds
    scaffold_names = match_scaffolds_to_site(site_type, n_top=n_scaffolds)
    print(f"    Matched {len(scaffold_names)} scaffolds: {', '.join(scaffold_names[:6])}...")

    # Parse substrate hint
    target_mol = None
    if substrate_hint:
        try:
            target_mol = Chem.MolFromSmiles(substrate_hint)
        except:
            pass

    # Generate and score candidates
    candidates = []
    seen_smiles = set()

    for sc_name in scaffold_names:
        sc_info = HETERO_CORE[sc_name]
        elaborated = elaborate_scaffold(sc_name, fg_names, site_type)

        for method_tag, raw_smi in elaborated:
            result = _validate_and_score_smiles(
                raw_smi,
                method=f"het_{sc_name}_{method_tag}",
                site_type=site_type,
                target_mol=target_mol,
                scaffold_info=sc_info,
            )
            if result and result["smiles"] not in seen_smiles:
                seen_smiles.add(result["smiles"])
                candidates.append(result)

    # Also generate the parent scaffold alone (no substituents except H)
    for sc_name in scaffold_names[:5]:
        sc_info = HETERO_CORE[sc_name]
        # Strip dummy atoms to get bare scaffold
        bare_smi = sc_info["smiles"]
        bare_smi = bare_smi.replace("[*:1]", "").replace("[*:2]", "")
        bare_smi = bare_smi.replace("-)", ")").replace("(-", "(").replace("--", "-")
        result = _validate_and_score_smiles(
            bare_smi,
            method=f"core_{sc_name}",
            site_type=site_type,
            target_mol=target_mol,
            scaffold_info=sc_info,
        )
        if result and result["smiles"] not in seen_smiles:
            seen_smiles.add(result["smiles"])
            candidates.append(result)

    # ── Sort by composite score ──
    candidates.sort(key=lambda x: x["composite_score"], reverse=True)
    return candidates[:max_candidates]


# ══════════════════════════════════════════════════════════════════════
# HYBRID GENERATION — Heterocycles + Fragment-Based Combined
# ══════════════════════════════════════════════════════════════════════

def generate_hybrid_ligands(
    site_type: Dict[str, str],
    substrate_hint: str = "",
    max_candidates: int = 30,
    heterocycle_fraction: float = 0.6,
) -> List[Dict]:
    """Generate ligands combining heterocycle-based and fragment-based methods.

    Args:
        site_type: Active site 12-primitive type
        substrate_hint: Known substrate SMILES
        max_candidates: Total candidates to return
        heterocycle_fraction: Fraction of candidates from heterocycle generation

    Returns:
        Combined and ranked list of candidate dicts
    """
    from rhr_p4rky.ligand_improvements import (
        generate_from_enzyme_type as generate_fragment,
    )

    n_het = int(max_candidates * heterocycle_fraction)
    n_frag = max_candidates - n_het

    # Heterocycle generation
    het_candidates = generate_heterocycle_ligands(
        site_type=site_type,
        fg_names=None,
        substrate_hint=substrate_hint,
        max_candidates=n_het,
        n_scaffolds=25,
    )

    # Fragment-based generation (existing method)
    frag_candidates = generate_fragment(
        site_type=site_type,
        substrate_hint=substrate_hint,
        max_candidates=n_frag,
    )

    # Combine, deduplicate by SMILES, rank
    seen = set()
    combined = []
    for c in het_candidates + frag_candidates:
        if c["smiles"] not in seen:
            seen.add(c["smiles"])
            combined.append(c)

    combined.sort(key=lambda x: x["composite_score"], reverse=True)
    return combined[:max_candidates]


# ══════════════════════════════════════════════════════════════════════
# TEST / DEMO
# ══════════════════════════════════════════════════════════════════════

def test_on_enzyme(pdb_id: str, residues: List[str]) -> None:
    """Test heterocycle generation on a specific enzyme."""
    from rhr_p4rky.ligand_from_active_site import encode_site_from_residues, fmt_tuple

    print(f"\n{'='*72}")
    print(f"  HETEROCYCLE LIGAND GENERATION — {pdb_id}")
    print(f"  Residues: {', '.join(residues)}")
    print(f"{'='*72}")

    site_type = encode_site_from_residues(residues)
    print(f"  Site type: {fmt_tuple(site_type)}")

    candidates = generate_hybrid_ligands(site_type, max_candidates=20)

    print(f"\n  Generated {len(candidates)} unique candidates:\n")
    print(f"  {'#':3s}  {'Method':35s}  {'SMILES':40s}  {'Score':6s}  {'logP':6s}  {'MW':7s}  {'Rings':5s}  {'Het':10s}")
    print(f"  {'-'*3}  {'-'*35}  {'-'*40}  {'-'*6}  {'-'*6}  {'-'*7}  {'-'*5}  {'-'*10}")

    for i, c in enumerate(candidates):
        het_str = ','.join(c.get('heteroatoms', []))
        print(f"  {i+1:3d}  {c['method'][:35]:35s}  {c['smiles'][:40]:40s}  "
              f"{c['composite_score']:6.3f}  {c['logP']:6.2f}  {c['MW']:7.1f}  "
              f"{c['rings']:5d}  {het_str:10s}")


def test_three_enzymes():
    """Test on the three PDB enzymes from the original report."""
    enzymes = {
        "10BM": ["ARG105","ARG113","ARG118","ARG159","ARG169","ARG171","ARG177","ARG193"],
        "4XRY": ["ARG101","ARG115","ARG123","ARG129","ARG132","ARG133","ARG140","ARG170"],
        "11BA": ["ARG10","ARG33","ARG80","ARG85","ASP121","ASP14","ASP53","ASP83"],
    }
    for pdb, residues in enzymes.items():
        test_on_enzyme(pdb, residues)



# ══════════════════════════════════════════════════════════════════════
# IMPROVED SCORING — Multi-factor structural complement
# ══════════════════════════════════════════════════════════════════════

def _score_structural_complement(
    mol: Chem.Mol,
    site_type: Dict[str, str],
    scaffold_info: Optional[Dict] = None,
) -> float:
    """Score how well a molecule complements the active site structurally.

    Returns score in [0, 1].
    """
    o = _get_site_ordinals(site_type)
    score = 0.0
    total_weight = 0.0

    try:
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        n_rings = Lipinski.RingCount(mol)
        n_arom = Lipinski.NumAromaticRings(mol)
        n_rot = Descriptors.NumRotatableBonds(mol)
        n_heavy = mol.GetNumHeavyAtoms()
        tpsa = Descriptors.TPSA(mol)
    except:
        return 0.3

    # ── Ring complexity matching (weight: 0.25) ──
    t_val = o["T"]
    ring_target = {0: 0.0, 1: 1.0, 2: 2.0, 3: 2.5, 4: 3.0}.get(t_val, 0.0)
    ring_score = 1.0 - min(1.0, abs(n_rings - ring_target) / 3.0)
    score += 0.25 * ring_score
    total_weight += 0.25

    # ── Hydrogen bond complement (weight: 0.25) ──
    # K proxies for site H-bond character
    k_val = o["K"]
    if k_val <= 1:  # frozen/disordered — want many H-bond points
        hb_target_hba = 6
        hb_target_hbd = 3
    elif k_val >= 3:  # fast — fewer H-bond points
        hb_target_hba = 2
        hb_target_hbd = 1
    else:  # moderate
        hb_target_hba = 4
        hb_target_hbd = 2

    hba_score = 1.0 - min(1.0, abs(hba - hb_target_hba) / 8.0)
    hbd_score = 1.0 - min(1.0, abs(hbd - hb_target_hbd) / 4.0)
    score += 0.25 * (hba_score + hbd_score) / 2
    total_weight += 0.25

    # ── Size complement (weight: 0.20) ──
    g_val = o["G"]
    size_targets = {0: 120, 1: 250, 2: 400}
    target_mw = size_targets.get(g_val, 250)
    size_score = 1.0 - min(1.0, abs(mw - target_mw) / 350.0)
    score += 0.20 * size_score
    total_weight += 0.20

    # ── Aromatic character complement (weight: 0.15) ──
    ph_val = o["Ph"]
    if ph_val >= 2:  # critical or above — want aromatic
        arom_score = min(1.0, n_arom / 3.0)
    elif ph_val >= 1:
        arom_score = 1.0 - abs(n_arom - 1.0) / 2.0
    else:
        arom_score = 1.0 - min(1.0, n_arom / 2.0)
    score += 0.15 * arom_score
    total_weight += 0.15

    # ── Flexibility complement (weight: 0.15) ──
    h_val = o["H"]
    if h_val >= 3:  # eternal — want rigid
        flex_target = 2
    elif h_val >= 1:
        flex_target = 4
    else:
        flex_target = 6
    flex_score = 1.0 - min(1.0, abs(n_rot - flex_target) / 8.0)
    score += 0.15 * flex_score
    total_weight += 0.15

    # ── Heteroatom diversity bonus ──
    het_types = set()
    for atom in mol.GetAtoms():
        sym = atom.GetSymbol()
        if sym not in ("C", "H"):
            het_types.add(sym)
    het_bonus = min(0.10, len(het_types) * 0.03)
    score += het_bonus

    # ── Drug-likeness penalty ──
    if mw < 100 or mw > 600:
        score -= 0.15
    if logp < -2 or logp > 6:
        score -= 0.10
    if tpsa > 200:
        score -= 0.05

    return max(0.0, min(1.0, score))

if __name__ == '__main__':
    test_three_enzymes()
