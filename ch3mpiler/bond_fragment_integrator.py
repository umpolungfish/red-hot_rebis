#!/usr/bin/env python3
"""bond_fragment_integrator.py — Bridge between grammar-derived retrosynthesis
and RDKit-based molecular fragmentation.

The ch3mpiler's retrosynthesis engine (compiler.py) computes structural cuts
between functional group pairs using grammar type algebra, but NEVER actually
fragments the molecular graph. Precursor SMILES are generic placeholders.

This module:
  1. Takes a target SMILES (resolved from name, CAS, or direct input)
  2. Uses ScaffoldParser to get real bond-level fragment SMILES
  3. Matches grammar-derived cuts to actual molecule bonds by FG pair + bond type
  4. Returns the REAL fragment SMILES for each cut

Author: Lando\u2297\u2299perator
"""
import sys, os, json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from rdkit import Chem
from rdkit.Chem import AllChem, rdchem

sys.path.insert(0, str(Path(__file__).parent.absolute()))
from scaffold_parser import ScaffoldParser, resolve_name_to_smiles


def resolve_target_smiles(target_name: str = "", smiles: str = "", cas: str = "",
                          cas_cache_path: str = "") -> Optional[str]:
    """Resolve target SMILES from name, direct input, or CAS."""
    if smiles:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            return Chem.MolToSmiles(mol)
        return smiles
    if cas and cas_cache_path:
        try:
            with open(cas_cache_path) as f:
                cache = json.load(f)
            entry = cache.get(cas, {})
            if entry.get("smiles"):
                return entry["smiles"]
        except Exception:
            pass
    if target_name:
        try:
            result = resolve_name_to_smiles(target_name)
            if result:
                return result
        except Exception:
            pass
    return None


class BondFragmentIntegrator:
    """Bridge between grammar-derived cuts and actual molecular fragments."""

    BOND_TYPE_MAP = {
        "sigma_single": "sigma_single", "pi_bond": "double_bond",
        "double_bond": "double_bond", "triple_bond": "triple_bond",
        "carbonyl": "double_bond", "co_sigma": "sigma_single",
        "cn_sigma": "sigma_single", "amide_link": "amide_link",
        "ester_link": "ester_link", "aromatic": "aromatic",
        "ether_link": "ether_link",
    }

    # Compiler FG names may be broader than pipeline-detected FGs.
    FG_EXPANSION_MAP = {
        "carbonyl": ["carbonyl", "ester", "carboxylic_acid", "ketone", "aldehyde", "amide"],
        "carboxylic_acid": ["carboxylic_acid", "ester"],
        "ester": ["ester", "carboxylic_acid"],
        "amide": ["amide", "carboxylic_acid"],
        "phenol": ["phenol", "aromatic_ring"],
        "aniline": ["aniline", "aromatic_ring"],
        "alkene": ["alkene", "aromatic_ring"],
    }

    def __init__(self, target_smiles: str):
        self.target_smiles = target_smiles
        self._mol = None
        self._decomposer = None
        self._strategic_bonds = []
        self._fragment_map = {}
        if target_smiles:
            self._load()

    def _load(self):
        mol = Chem.MolFromSmiles(self.target_smiles)
        if mol is None:
            return
        self.target_smiles = Chem.MolToSmiles(mol)
        self._mol = mol
        decomposer = ScaffoldParser()
        decomposer.load(self.target_smiles)
        self._decomposer = decomposer
        self._strategic_bonds = decomposer.get_strategic_bonds()
        for bond in self._strategic_bonds:
            btype = bond.get("bond_type", "sigma_single")
            fg1 = bond.get("fg1", "alkane")
            fg2 = bond.get("fg2", "alkane")
            entry = {
                "bond_idx": bond.get("bond_idx"),
                "fragment_smiles_a": bond.get("fragment_smiles_a"),
                "fragment_smiles_b": bond.get("fragment_smiles_b"),
                "in_ring": bond.get("in_ring", False),
            }
            for k in [(btype, fg1, fg2), (btype, fg2, fg1)]:
                self._fragment_map.setdefault(k, []).append(entry)
    def get_fragments_for_cut(self, bond_type: str, fg1: str, fg2: str) -> List[Dict]:
        """Get actual fragment SMILES for a grammar-derived cut using
        FG_EXPANSION_MAP to handle broader/narrower FG name mismatches."""
        if not self._strategic_bonds:
            return []

        fg1_exp = set(self.FG_EXPANSION_MAP.get(fg1, [fg1]))
        fg2_exp = set(self.FG_EXPANSION_MAP.get(fg2, [fg2]))
        mapped_type = self.BOND_TYPE_MAP.get(bond_type, bond_type)
        best_results = []
        best_score = -1

        for bond in self._strategic_bonds:
            b_type = bond.get("bond_type", "")
            b_fg1 = bond.get("fg1", "")
            b_fg2 = bond.get("fg2", "")
            frag_a = bond.get("fragment_smiles_a")
            frag_b = bond.get("fragment_smiles_b")

            # Bond type compatibility
            type_ok = (b_type == mapped_type or b_type == bond_type)
            if not type_ok and bond_type in ("co_sigma", "cn_sigma", "sigma_single"):
                type_ok = b_type in ("sigma_single", "ether_link", "cn_sigma")

            if not type_ok:
                continue

            # Score: 4=perfect, 3=one-side-matches-both, 2=one-side-matches-one, 1=partial
            score = 0
            if b_fg1 in fg1_exp and b_fg2 in fg2_exp:
                score = 4
            elif b_fg2 in fg1_exp and b_fg1 in fg2_exp:
                score = 4
            elif b_fg1 in fg1_exp and b_fg2 in fg1_exp:
                score = 3
            elif b_fg2 in fg1_exp and b_fg1 in fg2_exp:
                score = 3
            elif b_fg1 in fg1_exp or b_fg2 in fg2_exp:
                score = 2
            elif b_fg1 in fg2_exp or b_fg2 in fg1_exp:
                score = 2

            if score <= best_score:
                continue
            best_score = score
            best_results = [{
                "bond_idx": bond.get("bond_idx"), "bond_type": b_type,
                "fg1": b_fg1, "fg2": b_fg2,
                "fragment_smiles_a": frag_a, "fragment_smiles_b": frag_b,
                "in_ring": bond.get("in_ring", False),
            }]

        # Phase 2: absolute fallback — first strategic bond with fragment data
        if not best_results:
            for bond in self._strategic_bonds:
                if bond.get("is_strategic", False) and bond.get("fragment_smiles_a"):
                    best_results.append({
                        "bond_idx": bond.get("bond_idx"), "bond_type": bond.get("bond_type"),
                        "fg1": bond.get("fg1"), "fg2": bond.get("fg2"),
                        "fragment_smiles_a": bond.get("fragment_smiles_a"),
                        "fragment_smiles_b": bond.get("fragment_smiles_b"),
                        "in_ring": bond.get("in_ring", False),
                    })
                    break

        return best_results

    def enrich_retrosynthesis_tree(self, tree: Dict) -> Dict:
        """Enrich a grammar-derived retrosynthesis tree with real fragment SMILES.
        Uses RDKit FG detection on each fragment to assign to the correct precursor."""
        if not self._mol or not self._strategic_bonds:
            return tree

        # Build FG SMARTS matchers for fragment verification
        from rdkit.Chem import MolFromSmarts
        _fg_smarts = {
            "carbonyl": MolFromSmarts("[CX3]=[OX1]"),
            "carboxylic_acid": MolFromSmarts("[CX3](=O)[OX2H]"),
            "ester": MolFromSmarts("[CX3](=O)[OX2][#6]"),
            "aromatic_ring": MolFromSmarts("a"),
            "amine": MolFromSmarts("[NX3;H2,H1;!$(NC=O)]"),
            "alcohol": MolFromSmarts("[OX2H]"),
            "ether": MolFromSmarts("[OX2]([#6])[#6]"),
            "phenol": MolFromSmarts("[OX2H]c"),
            "alkene": MolFromSmarts("[CX3]=[CX3;!a]"),
            "amide": MolFromSmarts("[NX3][CX3](=[OX1])[#6]"),
            "ketone": MolFromSmarts("[#6][CX3](=O)[#6]"),
            "aldehyde": MolFromSmarts("[CX3H1](=O)[#6]"),
        }

        def _fragment_has_fg(frag_smi: str, fg_name: str) -> bool:
            """Check if a fragment SMILES contains a specific FG."""
            if not frag_smi:
                return False
            try:
                mol = Chem.MolFromSmiles(frag_smi)
                if mol is None:
                    return False
                smarts = _fg_smarts.get(fg_name)
                if smarts is None:
                    return False
                return mol.HasSubstructMatch(smarts)
            except Exception:
                return False

        enriched = dict(tree)
        for step in enriched.get("steps", []):
            bond_type = step.get("bond", "")
            fg1 = step.get("fg1", "")
            fg2 = step.get("fg2", "")
            fragments = self.get_fragments_for_cut(bond_type, fg1, fg2)
            if not fragments:
                continue
            frag = fragments[0]
            frag_a = frag.get("fragment_smiles_a", "")
            frag_b = frag.get("fragment_smiles_b", "")
            precs = step.get("precursors", [])

            if len(precs) == 2:
                prec1_fg = precs[0].get("fg_hint", fg1)
                prec2_fg = precs[1].get("fg_hint", fg2)

                # Score each fragment for each FG match
                score_a1 = 1 if _fragment_has_fg(frag_a, prec1_fg) else 0
                score_a2 = 1 if _fragment_has_fg(frag_a, prec2_fg) else 0
                score_b1 = 1 if _fragment_has_fg(frag_b, prec1_fg) else 0
                score_b2 = 1 if _fragment_has_fg(frag_b, prec2_fg) else 0

                # Assign: frag_a goes to precursor whose FG it matches
                if score_a1 > score_a2:
                    precs[0]["smiles"] = frag_a
                    precs[1]["smiles"] = frag_b
                elif score_a2 > score_a1:
                    precs[1]["smiles"] = frag_a
                    precs[0]["smiles"] = frag_b
                else:
                    # Tie — use size heuristic: larger fragment typically has more FG context
                    if len(frag_a) >= len(frag_b):
                        precs[0]["smiles"] = frag_a
                        precs[1]["smiles"] = frag_b
                    else:
                        precs[1]["smiles"] = frag_a
                        precs[0]["smiles"] = frag_b
            elif len(precs) == 1:
                precs[0]["smiles"] = frag_a or frag_b

            step["bond_idx"] = frag.get("bond_idx")
        return enriched
