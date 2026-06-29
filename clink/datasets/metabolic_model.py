#!/usr/bin/env python3
"""
metabolic_model.py — Stoichiometric Metabolic Model with Flux Analysis
=======================================================================
Generates quantitative SBML-style metabolic models with stoichiometric
matrices, flux balance analysis (FBA) parameters, and actionable output.

Key capabilities:
  - Core carbon metabolism (glycolysis, TCA, pentose phosphate)
  - Amino acid biosynthesis pathways
  - Stoichiometric matrix (S · v = 0)
  - Flux bounds and objective functions
  - SBML-compatible output for loading into COBRApy

Author: Lando (R) (O)perator
"""

from __future__ import annotations
import json, math, random, re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
from shared.rich_output import *



@dataclass
class Metabolite:
    """A metabolite in the metabolic model."""
    id: str
    name: str
    formula: str = ""
    compartment: str = "c"
    charge: int = 0

@dataclass
class Reaction:
    """A biochemical reaction with stoichiometry."""
    id: str
    name: str
    equation: str
    stoichiometry: Dict[str, float]
    reversible: bool = False
    lower_bound: float = 0.0
    upper_bound: float = 1000.0
    objective_coeff: float = 0.0
    gene_reaction_rule: str = ""
    subsystem: str = ""
    deltaG_kJ_per_mol: float = 0.0
    ec_number: str = ""
    notes: str = ""

@dataclass
class MetabolicModel:
    """Complete constraint-based metabolic model."""
    id: str = "CLINK_core_model"
    name: str = "CLINK Core Carbon Metabolism"
    metabolites: Dict[str, Metabolite] = field(default_factory=dict)
    reactions: Dict[str, Reaction] = field(default_factory=dict)
    biomass_reaction: str = ""
    compartments: Dict[str, str] = field(default_factory=lambda: {
        "c": "cytosol", "m": "mitochondria", "e": "extracellular",
    })
    notes: List[str] = field(default_factory=list)

class CoreMetabolismBuilder:
    """Builds a stoichiometric model of core carbon metabolism."""

    def build_core_model(self, organism_type: str = "mammalian") -> MetabolicModel:
        """Build core carbon metabolism for the given organism type."""
        model = MetabolicModel(
            id=f"CLINK_{organism_type}_core",
            name=f"CLINK {organism_type.capitalize()} Core Metabolism",
        )
        self._add_metabolites(model)
        self._add_glycolysis(model)
        self._add_tca_cycle(model)
        self._add_pentose_phosphate(model)
        self._add_amino_acid_synthesis(model)
        self._add_biomass_reaction(model, organism_type)
        return model

    def _add_metabolites(self, model: MetabolicModel):
        mets = {
            "glc__D": Metabolite("glc__D", "D-Glucose", "C6H12O6", "e", 0),
            "g6p": Metabolite("g6p", "Glucose-6-phosphate", "C6H13O9P", "c", -2),
            "f6p": Metabolite("f6p", "Fructose-6-phosphate", "C6H13O9P", "c", -2),
            "fdp": Metabolite("fdp", "Fructose-1,6-bisphosphate", "C6H14O12P2", "c", -4),
            "dhap": Metabolite("dhap", "Dihydroxyacetone phosphate", "C3H7O6P", "c", -2),
            "g3p": Metabolite("g3p", "Glyceraldehyde-3-phosphate", "C3H7O6P", "c", -2),
            "13dpg": Metabolite("13dpg", "1,3-Bisphospho-D-glycerate", "C3H8O10P2", "c", -4),
            "3pg": Metabolite("3pg", "3-Phospho-D-glycerate", "C3H7O7P", "c", -3),
            "2pg": Metabolite("2pg", "2-Phospho-D-glycerate", "C3H7O7P", "c", -3),
            "pep": Metabolite("pep", "Phosphoenolpyruvate", "C3H5O6P", "c", -3),
            "pyr": Metabolite("pyr", "Pyruvate", "C3H4O3", "c", -1),
            "lac__D": Metabolite("lac__D", "D-Lactate", "C3H6O3", "c", -1),
            "accoa": Metabolite("accoa", "Acetyl-CoA", "C23H38N7O17P3S", "c", -4),
            "cit": Metabolite("cit", "Citrate", "C6H8O7", "c", -3),
            "icit": Metabolite("icit", "Isocitrate", "C6H8O7", "c", -3),
            "akg": Metabolite("akg", "2-Oxoglutarate", "C5H6O5", "c", -2),
            "succoa": Metabolite("succoa", "Succinyl-CoA", "C25H40N7O19P3S", "c", -5),
            "succ": Metabolite("succ", "Succinate", "C4H6O4", "c", -2),
            "fum": Metabolite("fum", "Fumarate", "C4H4O4", "c", -2),
            "mal__L": Metabolite("mal__L", "L-Malate", "C4H6O5", "c", -2),
            "oaa": Metabolite("oaa", "Oxaloacetate", "C4H4O5", "c", -2),
            "nad": Metabolite("nad", "NAD+", "C21H27N7O14P2", "c", -1),
            "nadh": Metabolite("nadh", "NADH", "C21H29N7O14P2", "c", -2),
            "nadp": Metabolite("nadp", "NADP+", "C21H28N7O17P3", "c", -3),
            "nadph": Metabolite("nadph", "NADPH", "C21H29N7O17P3", "c", -4),
            "atp": Metabolite("atp", "ATP", "C10H16N5O13P3", "c", -4),
            "adp": Metabolite("adp", "ADP", "C10H15N5O10P2", "c", -3),
            "pi": Metabolite("pi", "Phosphate", "HO4P", "c", -2),
            "co2": Metabolite("co2", "CO2", "CO2", "c", 0),
            "h2o": Metabolite("h2o", "H2O", "H2O", "c", 0),
            "h": Metabolite("h", "H+", "H", "c", 1),
            "o2": Metabolite("o2", "O2", "O2", "c", 0),
            "glu__L": Metabolite("glu__L", "L-Glutamate", "C5H9NO4", "c", -1),
            "gln__L": Metabolite("gln__L", "L-Glutamine", "C5H10N2O3", "c", 0),
            "ala__L": Metabolite("ala__L", "L-Alanine", "C3H7NO2", "c", 0),
            "asp__L": Metabolite("asp__L", "L-Aspartate", "C4H7NO4", "c", -1),
            "asn__L": Metabolite("asn__L", "L-Asparagine", "C4H8N2O3", "c", 0),
            "lys__L": Metabolite("lys__L", "L-Lysine", "C6H14N2O2", "c", 0),
            "e4p": Metabolite("e4p", "Erythrose-4-phosphate", "C4H9O7P", "c", -2),
            "r5p": Metabolite("r5p", "Ribose-5-phosphate", "C5H11O8P", "c", -2),
            "ru5p__D": Metabolite("ru5p__D", "D-Ribulose-5-phosphate", "C5H11O8P", "c", -2),
            "xu5p__D": Metabolite("xu5p__D", "D-Xylulose-5-phosphate", "C5H11O8P", "c", -2),
            "s7p": Metabolite("s7p", "Sedoheptulose-7-phosphate", "C7H15O10P", "c", -2),
        }
        model.metabolites = mets

    def _stoich_str(self, r_id: str, stoich: Dict[str, float], reversible: bool = False) -> str:
        """Generate human-readable equation string."""
        left = []
        right = []
        for mid, coeff in stoich.items():
            if coeff < 0:
                left.append(f"{-coeff} {mid}" if coeff < -1 else mid)
            elif coeff > 0:
                right.append(f"{coeff} {mid}" if coeff > 1 else mid)
        arrow = " <-> " if reversible else " -> "
        return " + ".join(left) + arrow + " + ".join(right)

    def _add_reaction(self, model: MetabolicModel, r_id: str, name: str,
                      stoich: Dict[str, float], reversible: bool = False,
                      subsystem: str = "", deltaG: float = 0.0,
                      lb: float = 0.0, ub: float = 1000.0):
        model.reactions[r_id] = Reaction(
            id=r_id, name=name,
            equation=self._stoich_str(r_id, stoich, reversible),
            stoichiometry=stoich, reversible=reversible,
            lower_bound=lb, upper_bound=ub,
            subsystem=subsystem, deltaG_kJ_per_mol=deltaG,
        )

    def _add_glycolysis(self, model: MetabolicModel):
        rxns = {
            "HEX1": ("Hexokinase", {"glc__D": -1, "atp": -1, "g6p": 1, "adp": 1, "h": 1}, False, "Glycolysis", -16.7),
            "PGI": ("Glucose-6-phosphate isomerase", {"g6p": -1, "f6p": 1}, True, "Glycolysis", 1.7),
            "PFK": ("Phosphofructokinase", {"f6p": -1, "atp": -1, "fdp": 1, "adp": 1, "h": 1}, False, "Glycolysis", -14.2),
            "FBA": ("Fructose-bisphosphate aldolase", {"fdp": -1, "dhap": 1, "g3p": 1}, True, "Glycolysis", 23.8),
            "TPI": ("Triose-phosphate isomerase", {"dhap": -1, "g3p": 1}, True, "Glycolysis", 7.5),
            "GAPD": ("Glyceraldehyde-3-phosphate dehydrogenase", {"g3p": -1, "nad": -1, "pi": -1, "13dpg": 1, "nadh": 1, "h": 1}, True, "Glycolysis", 6.3),
            "PGK": ("Phosphoglycerate kinase", {"13dpg": -1, "adp": -1, "3pg": 1, "atp": 1}, True, "Glycolysis", -18.5),
            "PGM": ("Phosphoglycerate mutase", {"3pg": -1, "2pg": 1}, True, "Glycolysis", 4.4),
            "ENO": ("Enolase", {"2pg": -1, "pep": 1, "h2o": 1}, True, "Glycolysis", 1.8),
            "PYK": ("Pyruvate kinase", {"pep": -1, "adp": -1, "pyr": 1, "atp": 1}, False, "Glycolysis", -31.4),
            "LDH": ("Lactate dehydrogenase", {"pyr": -1, "nadh": -1, "h": -1, "lac__D": 1, "nad": 1}, True, "Glycolysis", -25.1),
            "PDH": ("Pyruvate dehydrogenase", {"pyr": -1, "nad": -1, "coa": -1, "accoa": 1, "co2": 1, "nadh": 1}, False, "Glycolysis", -33.4),
        }
        for r_id, (name, stoich, rev, sub, dG) in rxns.items():
            self._add_reaction(model, r_id, name, stoich, rev, sub, dG)

    def _add_tca_cycle(self, model: MetabolicModel):
        rxns = {
            "CS": ("Citrate synthase", {"accoa": -1, "oaa": -1, "h2o": -1, "cit": 1, "coa": 1, "h": 1}, False, "TCA Cycle", -31.5),
            "ACONT": ("Aconitase", {"cit": -1, "icit": 1}, True, "TCA Cycle", 6.7),
            "ICDH": ("Isocitrate dehydrogenase", {"icit": -1, "nadp": -1, "akg": 1, "nadph": 1, "co2": 1}, False, "TCA Cycle", -8.4),
            "AKGD": ("2-Oxoglutarate dehydrogenase", {"akg": -1, "nad": -1, "coa": -1, "succoa": 1, "nadh": 1, "co2": 1, "h": 1}, False, "TCA Cycle", -33.5),
            "SUCOAS": ("Succinyl-CoA synthetase", {"succoa": -1, "adp": -1, "pi": -1, "succ": 1, "atp": 1, "coa": 1}, True, "TCA Cycle", 3.4),
            "SUCDH": ("Succinate dehydrogenase", {"succ": -1, "fad": -1, "fum": 1, "fadh2": 1}, False, "TCA Cycle", 0.0),
            "FUM": ("Fumarase", {"fum": -1, "h2o": -1, "mal__L": 1}, True, "TCA Cycle", -3.8),
            "MDH": ("Malate dehydrogenase", {"mal__L": -1, "nad": -1, "oaa": 1, "nadh": 1, "h": 1}, True, "TCA Cycle", 29.7),
        }
        for r_id, (name, stoich, rev, sub, dG) in rxns.items():
            self._add_reaction(model, r_id, name, stoich, rev, sub, dG)

    def _add_pentose_phosphate(self, model: MetabolicModel):
        rxns = {
            "G6PDH": ("G6PDH", {"g6p": -1, "nadp": -1, "ru5p__D": 1, "nadph": 1, "co2": 1}, False, "PPP", 0.0),
            "RPI": ("RPI", {"ru5p__D": -1, "r5p": 1}, True, "PPP", 0.0),
            "RPE": ("RPE", {"ru5p__D": -1, "xu5p__D": 1}, True, "PPP", 0.0),
            "TKT1": ("TKT1", {"xu5p__D": -1, "r5p": -1, "s7p": 1, "g3p": 1}, True, "PPP", 0.0),
            "TKT2": ("TKT2", {"xu5p__D": -1, "e4p": -1, "f6p": 1, "g3p": 1}, True, "PPP", 0.0),
            "TALA": ("TALA", {"s7p": -1, "g3p": -1, "f6p": 1, "e4p": 1}, True, "PPP", 0.0),
        }
        for r_id, (name, stoich, rev, sub, dG) in rxns.items():
            self._add_reaction(model, r_id, name, stoich, rev, sub, dG)

    def _add_amino_acid_synthesis(self, model: MetabolicModel):
        rxns = {
            "GLNS": ("Glutamine synthetase", {"glu__L": -1, "atp": -1, "nh4": -1, "gln__L": 1, "adp": 1, "pi": 1}, False, "AA Metabolism", 0.0),
            "GLUD": ("Glutamate dehydrogenase", {"akg": -1, "nadph": -1, "nh4": -1, "glu__L": 1, "nadp": 1, "h2o": 1}, True, "AA Metabolism", 0.0),
            "ALAT": ("Alanine transaminase", {"glu__L": -1, "pyr": -1, "akg": 1, "ala__L": 1}, True, "AA Metabolism", 0.0),
            "ASPT": ("Aspartate transaminase", {"glu__L": -1, "oaa": -1, "akg": 1, "asp__L": 1}, True, "AA Metabolism", 0.0),
            "ASNS": ("Asparagine synthetase", {"asp__L": -1, "atp": -1, "gln__L": -1, "asn__L": 1, "amp": 1, "ppi": 1, "glu__L": 1}, False, "AA Metabolism", 0.0),
        }
        for r_id, (name, stoich, rev, sub, dG) in rxns.items():
            self._add_reaction(model, r_id, name, stoich, rev, sub, dG)

    def _add_biomass_reaction(self, model: MetabolicModel, org_type: str):
        if org_type == "mammalian":
            stoich = {
                "atp": -65.0, "glu__L": -0.4, "gln__L": -0.2,
                "ala__L": -0.1, "asp__L": -0.1, "asn__L": -0.05,
                "lys__L": -0.08, "g6p": -0.2, "f6p": -0.05,
                "r5p": -0.1, "accoa": -0.3, "nadph": -10.0,
                "oaa": -0.1, "pep": -0.05, "pyr": -0.1,
                "h2o": -1.0, "h": -1.0, "biomass": 1.0,
            }
        else:
            stoich = {"atp": -40.0, "glu__L": -0.3, "gln__L": -0.1,
                      "ala__L": -0.08, "g6p": -0.2, "r5p": -0.08,
                      "accoa": -0.2, "nadph": -8.0, "oaa": -0.08,
                      "h2o": -1.0, "h": -0.5, "biomass": 1.0}
        model.reactions["BIOMASS"] = Reaction(
            id="BIOMASS", name="Biomass production",
            equation=self._stoich_str("BIOMASS", stoich, False),
            stoichiometry=stoich, reversible=False,
            lower_bound=0, upper_bound=1000,
            subsystem="Biomass", objective_coeff=1.0,
            notes="Biomass objective function"
        )
        model.biomass_reaction = "BIOMASS"

    def export_sbml(self, model: MetabolicModel) -> str:
        """Export model in SBML-compatible format."""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" level="3" version="1">',
            f'  <model id="{model.id}" name="{model.name}">',
            '    <listOfCompartments>',
        ]
        for cid, cname in model.compartments.items():
            lines.append(f'      <compartment id="{cid}" name="{cname}" size="1"/>')
        lines.append('    </listOfCompartments>')
        lines.append('    <listOfSpecies>')
        for mid, met in model.metabolites.items():
            lines.append(f'      <species id="{mid}" name="{met.name}" '
                         f'compartment="{met.compartment}" '
                         f'hasOnlySubstanceUnits="false" boundaryCondition="false"/>')
        lines.append('    </listOfSpecies>')
        lines.append('    <listOfReactions>')
        for r_id, rxn in model.reactions.items():
            lines.append(f'      <reaction id="{r_id}" name="{rxn.name}" '
                         f'reversible="{str(rxn.reversible).lower()}">')
            lines.append('        <listOfReactants>')
            for mid, coeff in rxn.stoichiometry.items():
                if coeff < 0:
                    lines.append(f'          <speciesReference species="{mid}" stoichiometry="{-coeff}"/>')
            lines.append('        </listOfReactants>')
            lines.append('        <listOfProducts>')
            for mid, coeff in rxn.stoichiometry.items():
                if coeff > 0 and mid != "biomass":
                    lines.append(f'          <speciesReference species="{mid}" stoichiometry="{coeff}"/>')
            lines.append('        </listOfProducts>')
            lines.append('      </reaction>')
        lines.append('    </listOfReactions>')
        lines.append('  </model>')
        lines.append('</sbml>')
        return '\n'.join(lines)

    def export_fba_parameters(self, model: MetabolicModel) -> Dict:
        """Export FBA-ready parameter dictionary."""
        return {
            "model_id": model.id,
            "metabolites": len(model.metabolites),
            "reactions": len(model.reactions),
            "biomass_rxn": model.biomass_reaction,
            "objective": model.biomass_reaction,
            "reaction_bounds": {
                r_id: {"lb": rxn.lower_bound, "ub": rxn.upper_bound}
                for r_id, rxn in model.reactions.items()
            },
        }

    def export_stoichiometric_matrix(self, model: MetabolicModel) -> Dict:
        """Export stoichiometric matrix as JSON."""
        met_ids = list(model.metabolites.keys())
        rxn_ids = list(model.reactions.keys())
        matrix = []
        for i, mid in enumerate(met_ids):
            row = []
            for j, r_id in enumerate(rxn_ids):
                coeff = model.reactions[r_id].stoichiometry.get(mid, 0.0)
                row.append(coeff)
            matrix.append(row)
        return {
            "n_metabolites": len(met_ids),
            "n_reactions": len(rxn_ids),
            "metabolites": met_ids,
            "reactions": rxn_ids,
            "matrix": matrix,
        }
