#!/usr/bin/env python3
"""
fg_exhaustive.py — Comprehensive Functional Group SMARTS Library

170+ SMARTS patterns covering all major organic functional groups,
each mapped to its IMASM token role for compound imscription.

Structure:
  SMARTS_PATTERNS: Dict[str, tuple] — (smarts, imasm_token, weight, role_category)
  TOKEN_BY_FG: auto-generated inverse map
  FG_CATEGORIES: functional group taxonomy

Fields per entry:
  smarts: RDKit SMARTS pattern string
  token: IMASM token (0-11)
  weight: importance weight (1-10) for tiebreaking
  category: 'core', 'acid', 'base', 'electrophile', 'nucleophile',
            'leaving', 'linker', 'terminal', 'ambident', 'redox'

Author: Lando⊗⊙perator
"""

from typing import Dict, Tuple, List, Optional

# Token constants
VINIT, TANCH, AFWD, AREV, CLINK = 0, 1, 2, 3, 4
IMSCRIB, FSPLIT, FFUSE = 5, 6, 7
EVALT, EVALF, ENGAGR, IFIX = 8, 9, 10, 11

# Pattern entry: (smarts, token, weight, category)
FGEntry = Tuple[str, int, int, str]

SMARTS_PATTERNS: Dict[str, FGEntry] = {

    # ── CORE SCAFFOLDS (VINIT=0) ──────────────────────────────
    "aromatic_c6":            ("c1ccccc1", VINIT, 8, "core"),
    "aromatic_hetero_5":      ("[a;r5]", VINIT, 7, "core"),
    "aromatic_hetero_6":      ("[a;r6]", VINIT, 7, "core"),
    "spiro_center":           ("[CX4;R2]([R])([R])([R])[R]", VINIT, 6, "core"),
    "bridged_bicyclic":       ("[R;r3]1[R;r3][R;r3]1", VINIT, 5, "core"),
    "cubane_core":            ("[C]12[C]3[C]4[C]1[C]5[C]2[C]3[C]45", VINIT, 3, "core"),
    "adamantane_core":        ("[C]12[C]3[C]4[C]1[C]5[C]2[C]3[C]4[C]5", VINIT, 3, "core"),

    # ── SELF-IMSCRIBING SYSTEMS (IMSCRIB=5) ───────────────────
    "aromatic_ring":          ("a", IMSCRIB, 5, "core"),
    "conjugated_diene":       ("[#6]=[#6]-[#6]=[#6]", IMSCRIB, 4, "core"),
    "conjugated_ene_yn":      ("[#6]=[#6]-[#6]#[#6]", IMSCRIB, 3, "core"),
    "porphyrin_core":         ("c1c2cc3cc4cc5cc6cc1n7c2c8c9c%10c%11c%12c%13c%14c%15c%16c%17c%18c%19c%20c%21c%22c%23c%24c%25c%26c%27c%28c%29c%30c%31c%32c%33c%34c%35c%36c%37c%38c%39c%40c%41c%42c%43c%44c%45c(=[N-]%46)c%47c%48c%49c%50c%51c%52c%53c%54c%55c%56c%57c%58c%59c%60c%61c%62", IMSCRIB, 1, "core"),
    "fullerene_patch":        ("c12c3c4c5c1c6c7c2c8c3c9c%10c4c%11c5c%12c6c%13c7c8c%14c%15c9c%10c%16c%11c%12c%13c%14c%15", IMSCRIB, 1, "core"),
    "annulene":               ("[c;R]1[c;R][c;R][c;R][c;R][c;R]1", IMSCRIB, 3, "core"),

    # ── ACIDIC GROUPS (EVALT=8) ──────────────────────────────
    "carboxylic_acid":        ("[CX3](=O)[OX2H,OX1-]", EVALT, 10, "acid"),
    "sulfonic_acid":          ("[SX4](=O)(=O)[OX2H,OX1-]", EVALT, 9, "acid"),
    "sulfinic_acid":          ("[SX3](=O)[OX2H]", EVALT, 7, "acid"),
    "phosphonic_acid":        ("[PX4](=O)([OX2H])[OX2H]", EVALT, 8, "acid"),
    "phosphoric_acid":        ("[PX4](=[OX1])([OX2H])([OX2H])[OX2H]", EVALT, 7, "acid"),
    "boronic_acid":           ("[BX3]([OX2H])([OX2H])[#6]", EVALT, 7, "acid"),
    "phenol":                 ("[OX2H][c]", EVALT, 6, "acid"),
    "enol":                   ("[#6]([OH1])=[#6]", EVALT, 5, "acid"),
    "imine_acid":             ("[NX3H][CX3](=O)[OX2H]", EVALT, 4, "acid"),
    "thiol":                  ("[SX2H]", EVALT, 5, "acid"),
    "thioic_acid":            ("[CX3](=S)[OX2H]", EVALT, 6, "acid"),
    "alpha_hydroxy_acid":     ("[CX4]([OX2H])[CX3](=O)[OX2H]", EVALT, 5, "acid"),
    "barbituric_acid":        ("[NX3]1[CX3](=[OX1])[NX3][CX3](=[OX1])[CX3](=[OX1])1", EVALT, 4, "acid"),
    "saccharide_oh":          ("[CX4][OX2H]", EVALT, 3, "acid"),  # sugar OH
    "ascorbic_acid":          ("[CX3](=O)[C@@H]([OX2H])[C@H]([OX2H])[CH2][OX2H]", EVALT, 3, "acid"),
    "tetrazole":              ("[n;r5]1[n;r5][n;r5][n;r5][n;r5]1", EVALT, 5, "acid"),
    "imides":                 ("[CX3](=[OX1])[NX3][CX3](=[OX1])", EVALT, 4, "acid"),

    # ── BASIC GROUPS (EVALF=9) ─────────────────────────────────
    "primary_amine":          ("[NX3;H2;!$(N=*)]", EVALF, 9, "base"),
    "secondary_amine":        ("[NX3;H1;!$(N=*)]", EVALF, 8, "base"),
    "tertiary_amine":         ("[NX3;H0;!$(N=*)]", EVALF, 7, "base"),
    "aniline":                ("[NX3;H2,H1][c]", EVALF, 6, "base"),
    "pyridine":               ("[n;r6]", EVALF, 7, "base"),
    "imidazole":              ("[n;r5]1[c;r5][n;r5][c;r5][c;r5]1", EVALF, 6, "base"),
    "guanidine":              ("[NX3][CX3](=[NX2])[NX3]", EVALF, 8, "base"),
    "amidine":                ("[CX3](=[NX2])[NX3]", EVALF, 7, "base"),
    "hydrazine":              ("[NX3][NX3]", EVALF, 5, "base"),
    "hydroxylamine":          ("[NX3][OX2H]", EVALF, 4, "base"),
    "quaternary_ammonium":    ("[N+X4]", EVALF, 3, "base"),
    "pyrimidine":             ("[n;r6]1[c;r6][n;r6][c;r6][c;r6]1", EVALF, 6, "base"),
    "purine":                 ("[n;r5]1[c;r5][n;r5][c;r5]2[c;r6][n;r6][c;r6][n;r6]21", EVALF, 5, "base"),
    "piperidine":             ("[NX3;R;r6]", EVALF, 4, "base"),
    "morpholine":             ("[OX2;R;r6]1[CX4;R;r6][CX4;R;r6][NX3;R;r6][CX4;R;r6][CX4;R;r6]1", EVALF, 4, "base"),
    "piperazine":             ("[NX3;R;r6]1[CX4;R;r6][CX4;R;r6][NX3;R;r6][CX4;R;r6][CX4;R;r6]1", EVALF, 4, "base"),
    "pyrrolidine":            ("[NX3;R;r5]", EVALF, 3, "base"),
    "aziridine":              ("[NX3;R;r3]", EVALF, 2, "base"),
    "diazabicyclooctane":     ("[NX3]12[CX4][CX4][NX3]([CX4][CX4]1)[CX4][CX4]2", EVALF, 3, "base"),
    "histidine_sidechain":    ("[c;r5]1[n;r5][c;r5][n;r5]1", EVALF, 3, "base"),
    "tryptamine_nh":          ("[nH;r5]", EVALF, 4, "base"),

    # ── ELECTROPHILES (AFWD=2) ─────────────────────────────────
    "aldehyde":               ("[CX3H1](=O)[#6]", AFWD, 9, "electrophile"),
    "ketone":                 ("[#6][CX3](=O)[#6]", AFWD, 8, "electrophile"),
    "acyl_chloride":          ("[CX3](=O)[Cl]", AFWD, 9, "electrophile"),
    "acyl_bromide":           ("[CX3](=O)[Br]", AFWD, 8, "electrophile"),
    "acid_anhydride":         ("[CX3](=O)[OX2][CX3](=O)", AFWD, 8, "electrophile"),
    "isocyanate":             ("[NX2]=[C]=[OX1]", AFWD, 7, "electrophile"),
    "isothiocyanate":         ("[NX2]=[C]=[SX1]", AFWD, 6, "electrophile"),
    "epoxide":                ("[C;R;r3]1[OX2][C;R;r3]1", AFWD, 7, "electrophile"),
    "aziridine_electrophile": ("[C;R;r3]1[NX3;R;r3][C;R;r3]1", AFWD, 5, "electrophile"),
    "alkylating_agent":       ("[#6][CH2][Cl,Br,I,OS(=O)(=O)O]", AFWD, 7, "electrophile"),
    "formyl":                 ("[CX3H1](=O)", AFWD, 6, "electrophile"),
    "carbonyl":               ("[CX3]=[OX1]", AFWD, 5, "electrophile"),
    "activated_ester":        ("[CX3](=O)[OX2][c,n;!$([nX3])]", AFWD, 6, "electrophile"),
    "barton_ester":           ("[CX3](=O)[SX2]", AFWD, 4, "electrophile"),
    "weinreb_amide":          ("[CX3](=O)[NX3]([#6])[OX2][#6]", AFWD, 4, "electrophile"),
    "acyl_cyanide":           ("[CX3](=O)[CX2]#[NX1]", AFWD, 5, "electrophile"),
    "imine_electrophile":     ("[CX3](=[NX2])[#6]", AFWD, 5, "electrophile"),
    "oxime":                  ("[CX3](=[NX2][OX2H])[#6]", AFWD, 3, "electrophile"),
    "chloroformate":          ("[Cl]C(=O)[OX2]", AFWD, 6, "electrophile"),
    "sulfonyl_chloride":      ("[SX4](=O)(=O)[Cl]", AFWD, 7, "electrophile"),
    "sulfonyl_fluoride":      ("[SX4](=O)(=O)[F]", AFWD, 7, "electrophile"),
    "sulfate":                ("[SX4](=O)(=O)[OX2][#6]", AFWD, 4, "electrophile"),
    "phosphate_activated":    ("[PX4](=[OX1])([OX2][#6])[OX2][#6]", AFWD, 4, "electrophile"),
    "triflate":               ("[#6][SX4](=O)(=O)[OX2]C(F)(F)F", AFWD, 3, "electrophile"),
    "tosylate":               ("[#6]c1ccc(S(=O)(=O)[OX2])cc1", AFWD, 3, "electrophile"),
    "ms_protected":           ("[SX4](=O)(=O)[OX2]", AFWD, 2, "electrophile"),

    # ── NUCLEOPHILES (AREV=3) ──────────────────────────────────
    "alcohol":                ("[CX4][OX2H]", AREV, 7, "nucleophile"),
    "phenol_nucleophile":     ("[OX2H][c]", AREV, 5, "nucleophile"),
    "thiol_nucleophile":      ("[SX2H]", AREV, 7, "nucleophile"),
    "thiolate":               ("[SX1-]", AREV, 8, "nucleophile"),
    "alkoxide":               ("[OX1-]", AREV, 8, "nucleophile"),
    "primary_amine_nuc":      ("[NX3;H2]", AREV, 7, "nucleophile"),
    "secondary_amine_nuc":    ("[NX3;H1]", AREV, 6, "nucleophile"),
    "azide_nuc":              ("[NX2-]=[NX2+]=[NX1-]", AREV, 6, "nucleophile"),
    "cyanide_nuc":            ("[CX2-]#[NX1+]", AREV, 7, "nucleophile"),
    "enolate":                ("[#6]([OX1-])=[#6]", AREV, 8, "nucleophile"),
    "enamine":                ("[NX3][#6]=[#6]", AREV, 5, "nucleophile"),
    "carbanion":              ("[CX1-,CX2-,CX3-,CX4-]", AREV, 9, "nucleophile"),
    "hydride_donor":          ("[BH4-]", AREV, 4, "nucleophile"),
    "grignard":               ("[Mg][Cl,Br,I]", AREV, 8, "nucleophile"),
    "organolithium":          ("[Li][#6]", AREV, 9, "nucleophile"),
    "organozinc":             ("[Zn][#6]", AREV, 6, "nucleophile"),
    "organocuprate":          ("[Cu][#6]", AREV, 5, "nucleophile"),
    "organoboron":            ("[BX3]([OH])([OH])[#6]", AREV, 5, "nucleophile"),
    "organostannane":         ("[Sn]([#6])([#6])([#6])[#6]", AREV, 4, "nucleophile"),
    "organosilane":           ("[Si]([#6])([#6])([#6])[#6]", AREV, 3, "nucleophile"),
    "ylide":                  ("[#6-][#16+]([#6])([#6])[#6]", AREV, 5, "nucleophile"),
    "phosphine":              ("[PX3;!$(P=*)]", AREV, 5, "nucleophile"),
    "phosphite":              ("[PX3]([OX2][#6])([OX2][#6])[OX2][#6]", AREV, 3, "nucleophile"),
    "sulfide":                ("[SX2;!$(S=O)]", AREV, 4, "nucleophile"),
    "disulfide":              ("[SX2][SX2]", AREV, 2, "nucleophile"),
    "enol_ether":             ("[#6]=[#6][OX2][#6]", AREV, 3, "nucleophile"),
    "diene_nuc":              ("[#6]=[#6]-[#6]=[#6]", AREV, 3, "nucleophile"),
    "indole_nuc":             ("[c;r5]1[c;r5][c;r5]2[c;r6][c;r6][c;r6][c;r6]21", AREV, 3, "nucleophile"),
    "furan_nuc":              ("[o;r5]1[c;r5][c;r5][c;r5]1", AREV, 3, "nucleophile"),
    "thiophene_nuc":          ("[s;r5]1[c;r5][c;r5][c;r5]1", AREV, 2, "nucleophile"),
    "pyrrole_nuc":            ("[nH;r5]1[c;r5][c;r5][c;r5]1", AREV, 3, "nucleophile"),

    # ── LEAVING GROUPS (FSPLIT=6) ──────────────────────────────
    "halide_leaving":         ("[Cl,Br,I][CX4]", FSPLIT, 7, "leaving"),
    "tosylate_leaving":       ("[#6]c1ccc(S(=O)(=O)[OX2])cc1", FSPLIT, 8, "leaving"),
    "triflate_leaving":       ("[OX2]S(=O)(=O)C(F)(F)F", FSPLIT, 9, "leaving"),
    "mesylate_leaving":       ("[OX2]S(=O)(=O)C", FSPLIT, 8, "leaving"),
    "nonaflate_leaving":      ("[OX2]S(=O)(=O)C(F)(F)C(F)(F)C(F)(F)C(F)(F)F", FSPLIT, 6, "leaving"),
    "water_leaving":          ("[OH2]", FSPLIT, 5, "leaving"),
    "dinitrogen":             ("[NX2-]=[NX2+]=[NX1-]", FSPLIT, 7, "leaving"),
    "carbon_dioxide":         ("[OX1]=[CX2]=[OX1]", FSPLIT, 5, "leaving"),
    "acetic_acid_leaving":    ("[CX3](=O)[OX2H]", FSPLIT, 4, "leaving"),
    "phosphate_leaving":      ("[PX4](=[OX1])([OX2H])([OX2H])[OX2H]", FSPLIT, 4, "leaving"),
    "pyrophosphate_leaving":  ("[PX4](=[OX1])([OX2])[OX2][PX4](=[OX1])([OX2])[OX2]", FSPLIT, 3, "leaving"),
    # ── AMBIDENT / RESONANCE (ENGAGR=10) ──────────────────────
    "enolate_ambident":       ("[#6]=[#6][OX1-]", ENGAGR, 7, "ambident"),
    "phenoxide":              ("[OX1-][c]", ENGAGR, 6, "ambident"),
    "carboxylate":            ("[CX3](=O)[OX1-]", ENGAGR, 8, "ambident"),
    "nitronate":              ("[CX3](=[NX2+]([OX1-]))", ENGAGR, 5, "ambident"),
    "enamine_ambident":       ("[NX3][#6]=[#6]", ENGAGR, 4, "ambident"),
    "allyl_ambident":         ("[#6]=[#6]-[#6-]", ENGAGR, 5, "ambident"),
    "diene_ambident":         ("[#6]=[#6]-[#6]=[#6]", ENGAGR, 3, "ambident"),
    "indole_ambident":        ("[nH;r5]", ENGAGR, 3, "ambident"),
    "imidazole_ambident":     ("[n;r5]", ENGAGR, 3, "ambident"),
    "nitro_group":            ("[NX3+](=O)[O-]", ENGAGR, 5, "ambident"),
    "azide_ambident":         ("[NX2-]=[NX2+]=[NX1-]", ENGAGR, 4, "ambident"),
    "diazo":                  ("[NX2+]=[NX2-]", ENGAGR, 5, "ambident"),

    # ── LINKERS / BRIDGES (CLINK=4) ────────────────────────────
    "ether":                  ("[OD2]([#6])[#6]", CLINK, 5, "linker"),
    "thioether":              ("[SD2]([#6])[#6]", CLINK, 4, "linker"),
    "methylene_bridge":       ("[CH2]", CLINK, 4, "linker"),
    "ethylene_bridge":        ("[CH2][CH2]", CLINK, 3, "linker"),
    "ester_link":             ("[#6][CX3](=[OX1])[OX2][#6]", CLINK, 5, "linker"),
    "amide_link":             ("[#6][CX3](=[OX1])[NX3][#6]", CLINK, 5, "linker"),
    "disulfide_bridge":       ("[SX2][SX2]", CLINK, 4, "linker"),
    "acetal":                 ("[OX2][CH]([OX2])[#6]", CLINK, 4, "linker"),
    "hemiacetal":             ("[OX2][CH]([OX2H])[#6]", CLINK, 3, "linker"),
    "glycosidic_bond":        ("[OX2][C@H]1[OX2][C@@H]([#6])[C@H]([OX2H])[C@@H]([OX2H])[C@H]1[OX2H]", CLINK, 3, "linker"),
    "phosphodiester":         ("[PX4](=[OX1])([OX2][#6])[OX2][#6]", CLINK, 4, "linker"),
    "carbonate":              ("[#6][OX2][CX3](=[OX1])[OX2][#6]", CLINK, 3, "linker"),
    "sulfonate_ester":        ("[#6][SX4](=O)(=O)[OX2][#6]", CLINK, 3, "linker"),
    "hydrazone":              ("[CX3]=[NX3][NX3]", CLINK, 3, "linker"),
    "oxime_link":             ("[CX3]=[NX2][OX2]", CLINK, 2, "linker"),
    "peptide_bond":           ("[CX3](=[OX1])[NX3][C@@H]([#6])", CLINK, 4, "linker"),
    "urea_link":              ("[NX3][CX3](=[OX1])[NX3]", CLINK, 3, "linker"),
    "carbamate":              ("[NX3][CX3](=[OX1])[OX2][#6]", CLINK, 3, "linker"),
    "sulfonamide":            ("[#6][SX4](=O)(=O)[NX3]", CLINK, 3, "linker"),

    # ── TERMINAL GROUPS (TANCH=1) ─────────────────────────────
    "methyl":                 ("[CH3]", TANCH, 3, "terminal"),
    "ethyl":                  ("[CH3][CH2]", TANCH, 2, "terminal"),
    "tert_butyl":             ("[CH3][C]([CH3])([CH3])", TANCH, 2, "terminal"),
    "trifluoromethyl":        ("[CF3]", TANCH, 4, "terminal"),
    "trichloromethyl":        ("[CCl3]", TANCH, 3, "terminal"),
    "fluorine_terminal":      ("[F]", TANCH, 3, "terminal"),
    "chlorine_terminal":      ("[Cl]", TANCH, 3, "terminal"),
    "bromine_terminal":       ("[Br]", TANCH, 2, "terminal"),
    "iodine_terminal":        ("[I]", TANCH, 2, "terminal"),
    "nitrile_terminal":       ("[CX2]#[NX1]", TANCH, 3, "terminal"),
    "nitro_terminal":         ("[NX3+](=O)[O-]", TANCH, 2, "terminal"),
    "azide_terminal":         ("[NX2-]=[NX2+]=[NX1-]", TANCH, 2, "terminal"),
    "aldehyde_terminal":      ("[CX3H1](=O)", TANCH, 2, "terminal"),
    "acetyl":                 ("[CH3]C(=O)", TANCH, 2, "terminal"),
    "benzyl":                 ("[c]1[c][c][c][c][c]1[CH2]", TANCH, 2, "terminal"),
    "methoxy":                ("[OX2][CH3]", TANCH, 3, "terminal"),
    "ethoxy":                 ("[OX2][CH3][CH2]", TANCH, 2, "terminal"),
    "dimethylamino":          ("[NX3]([CH3])[CH3]", TANCH, 2, "terminal"),

    # ── BOND-FORMING SITES (FFUSE=7) ──────────────────────────
    "alkene_ffuse":           ("[CX3]=[CX3]", FFUSE, 5, "redox"),
    "alkyne_ffuse":           ("[CX2]#[CX2]", FFUSE, 6, "redox"),
    "diene_ffuse":            ("[#6]=[#6]-[#6]=[#6]", FFUSE, 5, "redox"),
    "allene":                 ("[CX2]=[CX2]=[CX2]", FFUSE, 4, "redox"),
    "aryl_halide_coupling":   ("[Cl,Br,I][c]", FFUSE, 6, "redox"),
    "vinyl_halide":           ("[Cl,Br,I][CX3]=[CX3]", FFUSE, 5, "redox"),
    "boronic_coupling":       ("[BX3]([OH])([OH])[c]", FFUSE, 6, "redox"),
    "stannyl_coupling":       ("[Sn]([#6])([#6])([#6])[c]", FFUSE, 4, "redox"),
    "silyl_coupling":         ("[Si]([#6])([#6])([#6])[c]", FFUSE, 3, "redox"),
    "diazonium_coupling":     ("[NX2+]#[NX1-][c]", FFUSE, 6, "redox"),
    "radical_center":         ("[CH2][CH2]*", FFUSE, 2, "redox"),
    "olefin_metathesis":      ("[CX3]=[CX3]", FFUSE, 4, "redox"),
    "azide_alkyne_click":     ("[NX2-]=[NX2+]=[NX1-].[CX2]#[CX2]", FFUSE, 7, "redox"),

    # ── IRREVERSIBLE / PROTECTING (IFIX=11) ────────────────────
    "silyl_ether":            ("[Si]([#6])([#6])([#6])[OX2]", IFIX, 4, "protecting"),
    "acetal_protecting":      ("[OX2][CH]([OX2])[#6]", IFIX, 4, "protecting"),
    "benzyl_protecting":      ("[c]1[c][c][c][c][c]1[CH2][OX2]", IFIX, 3, "protecting"),
    "boc_protecting":         ("[CX3](=O)[OX2]C(C)(C)C", IFIX, 4, "protecting"),
    "fmoc_protecting":        ("[c]12[c][c][c][c]1[c][c][c][c]2[CH2][OX2]C(=O)", IFIX, 3, "protecting"),
    "cbz_protecting":         ("[c]1[c][c][c][c]c1[CH2][OX2]C(=O)", IFIX, 3, "protecting"),
    "pmb_protecting":         ("[c]1[c][c]([OX2][CH3])[c][c]1[CH2][OX2]", IFIX, 2, "protecting"),
    "tms_protecting":         ("[Si]([CH3])([CH3])[CH3]", IFIX, 3, "protecting"),
    "trityl_protecting":      ("[c]1[c][c][c][c][c]1[C]([c]2[c][c][c][c][c]2)[c]3[c][c][c][c][c]3", IFIX, 2, "protecting"),
}

# ── Inverse mapping: token → list of FG names ──
FG_BY_TOKEN: Dict[int, List[str]] = {}
for fg_name, (_, token, _, _) in SMARTS_PATTERNS.items():
    FG_BY_TOKEN.setdefault(token, []).append(fg_name)

# ── FG by category ──
FG_BY_CATEGORY: Dict[str, List[str]] = {}
for fg_name, (_, _, _, cat) in SMARTS_PATTERNS.items():
    FG_BY_CATEGORY.setdefault(cat, []).append(fg_name)

# ── Convenience access ──
def get_smarts(fg_name: str) -> Optional[str]:
    """Get SMARTS for a functional group name."""
    entry = SMARTS_PATTERNS.get(fg_name)
    return entry[0] if entry else None

def get_token(fg_name: str) -> Optional[int]:
    """Get IMASM token for a functional group name."""
    entry = SMARTS_PATTERNS.get(fg_name)
    return entry[1] if entry else None

def list_by_token(token: int) -> List[str]:
    """List all FGs mapping to a given IMASM token."""
    return FG_BY_TOKEN.get(token, [])

def list_by_category(category: str) -> List[str]:
    """List all FGs in a given category."""
    return FG_BY_CATEGORY.get(category, [])

def total_patterns() -> int:
    """Total number of functional group SMARTS patterns."""
    return len(SMARTS_PATTERNS)

def token_counts() -> Dict[str, int]:
    """Count of FGs per token name."""
    from collections import Counter
    cnt = Counter()
    token_names = {
        0: "VINIT", 1: "TANCH", 2: "AFWD", 3: "AREV",
        4: "CLINK", 5: "IMSCRIB", 6: "FSPLIT", 7: "FFUSE",
        8: "EVALT", 9: "EVALF", 10: "ENGAGR", 11: "IFIX",
    }
    for _, (_, tok, _, _) in SMARTS_PATTERNS.items():
        cnt[token_names.get(tok, str(tok))] += 1
    return dict(cnt)
