#!/usr/bin/env python3
"""
pipeline/reaction_pipeline.py — Full recursive retrosynthetic pipeline.

Builds a complete multi-step synthesis tree by recursively decomposing every
intermediate through ch3mpiler's grammar-derived disconnection engine until
commercially available starting materials are reached.

Key difference from v1: uses ch3mpiler's FG-based recursive decomposition
(amine_precursor → amine+amine → hydrogen_bond → ...) for intermediate steps,
then matches REAGENT_DB only at terminal leaves. No premature termination.

Author: Lando⊗⊙perator
"""
import json
import math
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

BASE_DIR = Path(__file__).parent.parent.absolute()
CH3MPILER_DIR = BASE_DIR / "ch3mpiler"
sys.path.insert(0, str(CH3MPILER_DIR))
sys.path.insert(0, str(BASE_DIR))

from compiler import (
    Ch3mpiler, PNAMES, tup_dist, fmt_tup, BOND_TYPES, FG as FG_TYPES,
    find_fgs, get_molecule_type, find_disconnections,
)
from reaction_deriver import (
    ReactionDeriver, DerivedReaction,
    REAGENT_DB, SOLVENT_DB, CATALYST_DB, ACTIVATOR_DB,
    SIMPLE_STARTING_MATERIALS, is_simple_material,
    select_reactants, select_solvent, select_catalyst, select_activator, select_workup,
    meet_type, tensor_type,
    derive_conditions_from_disconnection,
)
from ch3mpiler.scaffold_parser import ScaffoldParser, resolve_name_to_smiles
from shared.rich_output import *

# ── Rich text formatting ──
try:
    STYLED = True
except ImportError:
    STYLED = False




# --- SMILES resolution for tree output ---
_SMILES_CACHE = {}
def _resolve_node_smiles(name):
    """Resolve a molecule/fragment name to SMILES."""
    if not name: return ""
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key in _SMILES_CACHE: return _SMILES_CACHE[key]
    try:
        from ch3mpiler.scaffold_parser import resolve_name_to_smiles as _r
        smi = _r(name)
        if smi: _SMILES_CACHE[key] = smi; return smi
    except: pass
    return ""

def _smiles_formula(smiles: str) -> str:
    """Return Hill-order molecular formula from SMILES (C7H6O style)."""
    if not smiles:
        return ""
    try:
        from rdkit import Chem
        from rdkit.Chem import rdMolDescriptors
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return ""
        return rdMolDescriptors.CalcMolFormula(mol)
    except Exception:
        return ""

def _smi_display(smiles: str) -> str:
    """Return 'SMILES: <smi>  [formula]' or empty string."""
    if not smiles:
        return ""
    formula = _smiles_formula(smiles)
    return f"SMILES: {smiles}" + (f"  [{formula}]" if formula else "")
class RetrosyntheticNode:
    """One node in the recursive retrosynthetic tree."""
    def __init__(self, name: str, level: int = 0):
        self.name = name
        self.level = level
        self.fgs: List[str] = []
        self.mol_type: str = ""
        self.is_terminal: bool = False
        self.is_simple: bool = False
        self.terminal_reason: str = ""
        self.reagent_match: Optional[Dict] = None
        self.smiles: Optional[str] = ""          # full molecule SMILES (set on root, empty on intermediates)
        self.fragment_smiles: Optional[str] = ""  # actual molecular fragment from scaffold cut
        self.routes: List[Dict] = []


class ReactionPipeline:
    """Full ch3mpiler pipeline with deep recursive retrosynthesis.

    Recursively decomposes target molecules through FG-based disconnection
    trees, deriving reaction conditions at each step, until commercially
    available starting materials are reached.
    """

    def __init__(self, max_depth: int = 6):
        self.compiler = Ch3mpiler()
        self.deriver = ReactionDeriver()
        self.max_depth = max_depth
        self._visited: Set[str] = set()
        self._scaffold_map = {}  # Pass 1 scaffold decomposition
        self._target_smiles = ""

    def _decompose_single_fg(self, fg_name: str, mol_type: Dict,
                            target: str, depth: int) -> Optional[List[Dict]]:
        """Decompose a single-FG precursor by enumerating ALL FG types.

        When a precursor has only one FG (e.g., amine_precursor), the standard
        disconnection engine can't find meaningful cuts (it would pair the FG
        with itself, producing nonsense). Instead, we enumerate every known FG
        type as a potential co-precursor and find the best (other_fg, bond)
        pair whose product type matches the target FG's structural type.

        Returns a list of route dicts (same format as the multi-FG path),
        or None if no chemically reasonable disconnection exists.
        """
        from compiler import evaluate_disconnection

        fg_type = FG_TYPES.get(fg_name, {})
        if not fg_type:
            return None

        candidates = []
        for other_fg in sorted(FG_TYPES.keys()):
            if other_fg == fg_name:
                continue
            for bond_name in BOND_TYPES:
                result = evaluate_disconnection(fg_name, other_fg, bond_name, fg_type)
                if result and result.get("compatible", True):
                    candidates.append(result)

        if not candidates:
            return None

        # Sort by product_delta (lower = better match to target FG type)
        candidates.sort(key=lambda c: c.get("product_delta", 999))

        # Only accept if the best disconnection is chemically reasonable
        best = candidates[0]
        if best.get("product_delta", 999) > 2.5:
            return None  # No chemically meaningful decomposition

        # Build routes (up to 3, skip candidates with product_delta > 3.0)
        routes = []
        for i, cut in enumerate(candidates[:3]):
            if cut.get("product_delta", 999) > 3.0:
                break
            route = {
                "index": i + 1,
                "fg1": cut["fg1"],
                "fg2": cut["fg2"],
                "bond": cut["bond"],
                "bond_desc": cut.get("bond_desc", cut["bond"]),
                "product_delta": cut.get("product_delta", 0),
                "bond_delta": cut.get("bond_delta", 0),
                "product_type": cut.get("product_type", "?"),
            }

            # Derive reaction conditions
            rxn = self.deriver.derive(cut)
            if rxn:
                route["reaction"] = rxn.to_dict()

            if i == 0:
                # Best cut: full recursive decomposition
                # ── Compute fragment SMILES FIRST, then pass INTO recursion ──
                frag_a, frag_b = self._get_fragment_smiles_for_cut(
                    cut["fg1"], cut["fg2"], cut["bond"])
                route["child_a"] = self.deep_retrosynthesis(
                    f"{cut['fg1']}_precursor", depth + 1, fg_hint=cut["fg1"],
                    fragment_smiles=frag_a)
                route["child_b"] = self.deep_retrosynthesis(
                    f"{cut['fg2']}_precursor", depth + 1, fg_hint=cut["fg2"],
                    fragment_smiles=frag_b)
            else:
                # Alternative cuts: terminal reagent matches only
                def _make_terminal(fg):
                    n = RetrosyntheticNode(f"{fg}_precursor", depth + 1)
                    n.fgs = [fg]
                    n.is_terminal = True
                    match = self._match_reagent(fg)
                    if match:
                        n.is_simple = True
                        n.reagent_match = match
                        n.terminal_reason = f"alt_single_fg, reagent: {match['name']}"
                    else:
                        n.terminal_reason = "alt_single_fg_no_reagent"
                    return n
                route["child_a"] = _make_terminal(cut["fg1"])
                route["child_b"] = _make_terminal(cut["fg2"])

            routes.append(route)

        return routes

    def _match_reagent(self, fg_name: str) -> Optional[Dict]:
        """Find the best REAGENT_DB match for a functional group type.

        Prefers reagents that supply ONLY the target FG (fewest extras),
        then breaks ties by structural distance.
        """
        fg_type = FG_TYPES.get(fg_name, {})
        candidates = []
        for name, rinfo in REAGENT_DB.items():
            supplies = rinfo.get("supplies", [])
            if fg_name in supplies or any(s in fg_name for s in supplies):
                ct = {p: rinfo.get(p, "?") for p in PNAMES}
                d, _ = tup_dist(fg_type, ct) if fg_type else (3.0, [])
                extra = [s for s in supplies if s != fg_name]
                candidates.append({
                    "name": name, "smiles": rinfo["smiles"],
                    "distance": round(d, 3), "supplies": supplies,
                    "extra_count": len(extra), "extra": extra,
                })
        if not candidates:
            return None
        # Sort by extra_count first, then by distance
        candidates.sort(key=lambda c: (c["extra_count"], c["distance"]))
        best = candidates[0]
        return {"name": best["name"], "smiles": best["smiles"],
                "distance": best["distance"], "supplies": best["supplies"]}

    def _get_fragment_smiles_for_cut(self, fg1: str, fg2: str, bond_type: str) -> tuple:
        """Pass 2: Look up fragment SMILES for a specific FG-pair cut.
        
        When the scaffold map has multiple bonds for the same FG pair,
        picks the BEST bond (most sensible retrosynthetic cut), not the
        first one. Prefers real functional group links and sigma_single
        bonds over C=O double bonds.
        
        Returns (frag_a, frag_b) or (None, None).
        """
        pair = tuple(sorted([fg1, fg2]))
        bonds = self._scaffold_map.get(pair, [])
        if not bonds:
            return None, None
        
        # Bond type ranking: lower score = better cut
        BOND_RANK = {
            "ether_link": 0,     # C-O-C ether — real FG link
            "ester_link": 0,     # C(=O)-O ester — real FG link
            "amide_link": 0,     # C(=O)-N amide — real FG link
            "sigma_single": 1,   # C-C single bond — good
            "co_sigma": 2,       # C-O sigma
            "cn_sigma": 2,       # C-N sigma
            "pi_bond": 3,        # pi bond
            "carbonyl": 3,       # C=O
            "hydrogen_bond": 4,  # H-bond
            "double_bond": 5,    # C=C
            "triple_bond": 5,    # C#C
        }
        
        def _frag_quality(b):
            """Score a bond: lower = better. Higher = worse."""
            bt = b.get("bond_type", "")
            fa = b.get("fragment_smiles_a", "")
            fb = b.get("fragment_smiles_b", "")
            
            # Bond type rank (0 = best, 5+ = worst)
            rank = BOND_RANK.get(bt, 3)
            
            # Count heavy atoms in fragments
            from rdkit import Chem
            def _heavy(smi):
                if not smi or smi in ('?', '', 'H', '[H]'):
                    return 0
                try:
                    mol = Chem.MolFromSmiles(smi)
                    if mol is None:
                        return 0
                    return sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() > 1)
                except:
                    return 0
            
            ha = _heavy(fa)
            hb = _heavy(fb)
            
            # Penalize single-atom fragments heavily
            atom_penalty = 0
            if ha < 2:
                atom_penalty += 10
            if hb < 2:
                atom_penalty += 10
            
            # Prefer balanced fragments (both sides have meaningful size)
            if ha >= 2 and hb >= 2:
                atom_penalty -= 2  # Bonus for balanced
            
            return rank + atom_penalty
        
        # Sort by bond quality, pick best
        best = min(bonds, key=_frag_quality)
        frag_a = best.get("fragment_smiles_a")
        frag_b = best.get("fragment_smiles_b")
        
        # Verify: the scaffold bond's (fg1, fg2) may not match the caller's (fg1, fg2)
        # because the pair is sorted. If they're reversed, swap the fragments.
        bond_fg1 = best.get("fg1", "")
        bond_fg2 = best.get("fg2", "")
        if fg1 == bond_fg2 and fg2 == bond_fg1:
            # Caller's order is reversed from bond's atom order → swap
            frag_a, frag_b = frag_b, frag_a
        
        return frag_a, frag_b

    def _parse_smiles_to_scaffold_map(self, smiles: str) -> dict:
        """Parse a SMILES string into a sub-scaffold map for recursive decomposition.
        
        Used at every tree level: when a node has a real fragment SMILES from
        its parent cut, this parses THAT fragment to find its own strategic
        bonds. Each bond carries the sub-fragment SMILES for the next level.
        
        Returns dict mapping FG-pair tuples to lists of bond info dicts,
        or empty dict on failure.
        """
        if not smiles or smiles in ('?', '', 'H', '[H]'):
            return {}
        try:
            from ch3mpiler.scaffold_parser import ScaffoldParser
            parser = ScaffoldParser()
            parser.load(smiles, name="_sub")
            decomp = parser.get_full_scaffold_decomposition()
            
            sub_map = {}
            for pair_str, bonds in decomp.get("fg_pair_bonds", {}).items():
                import ast
                pair = ast.literal_eval(pair_str)
                pair_key = tuple(sorted(pair))
                if pair_key not in sub_map:
                    sub_map[pair_key] = []
                sub_map[pair_key].extend(bonds)
            return sub_map
        except Exception:
            return {}

    def _is_sensible_cut(self, bond_info: dict) -> bool:
        """Check if a scaffold bond is a sensible retrosynthetic disconnection.
        
        Rules for sensible cuts:
        1. Bond must be between DIFFERENT FG types (cutting within same FG is wrong)
        2. Must NOT be a C=O double bond (breaking carbonyl = useless)
        3. Both fragments must have >1 heavy atom (no single-atom fragments)
        4. Prefer sigma_single, ester_link, amide_link bonds
        
        Args:
            bond_info: dict from scaffold parser with bond type and fragment SMILES
        Returns:
            bool: True if this is a sensible disconnection
        """
        from rdkit import Chem
        fg1 = bond_info.get("fg1", "")
        fg2 = bond_info.get("fg2", "")
        bond_type = bond_info.get("bond_type", "")
        frag_a = bond_info.get("fragment_smiles_a", "")
        frag_b = bond_info.get("fragment_smiles_b", "")
        
        # Rule: must be different FG types
        if fg1 == fg2:
            return False
        
        # Rule: C=O double bond — not a useful disconnection
        if bond_type == "double_bond" and ("carboxylic_acid" in (fg1, fg2) or "carbonyl" in (fg1, fg2)):
            return False
        
        # Rule: both fragments must have >1 heavy atom (no single-atom fragments)
        def _heavy_count(smi):
            if not smi or smi in ('?', '', 'H', '[H]'):
                return 0
            # Count non-H atoms in SMILES
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                return 0
            return sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() > 1)
        
        ha = _heavy_count(frag_a)
        hb = _heavy_count(frag_b)
        if ha < 2 or hb < 2:
            return False
        
        return True

    def _build_scaffold_routes(self, bonds: list, depth: int, 
                               parent_fragment_smiles: str = None) -> list:
        """Build retrosynthetic route dicts from actual scaffold bond cuts.
        
        Unlike _decompose_single_fg which GUESSES abstract FG co-precursors,
        this uses the REAL bond cuts from the scaffold parser. Each bond
        carries actual fragment SMILES for both sides.
        
        Only sensible disconnections are included (see _is_sensible_cut).
        
        Args:
            bonds: list of bond info dicts from scaffold parser
            depth: current recursion depth
            parent_fragment_smiles: the SMILES of the parent fragment
        """
        # Filter to only sensible cuts
        sensible = [b for b in bonds if self._is_sensible_cut(b)]
        if not sensible:
            return []  # No sensible cuts → will fall back to reagent matching
        
        from rdkit import Chem
        
        routes = []
        for i, bond_info in enumerate(sensible[:5]):
            fg1 = bond_info["fg1"]
            fg2 = bond_info["fg2"]
            bond_type = bond_info.get("bond_type", "sigma_single")
            frag_a = bond_info.get("fragment_smiles_a")
            frag_b = bond_info.get("fragment_smiles_b")
            
            cut = {"fg1": fg1, "fg2": fg2, "bond": bond_type,
                   "bond_desc": bond_type, "product_delta": 1.0,
                   "bond_delta": 0, "product_type": "?"}
            
            route = {
                "index": i + 1,
                "fg1": fg1, "fg2": fg2,
                "bond": bond_type,
                "bond_desc": bond_type,
                "product_delta": 1.0,
                "bond_delta": 0,
                "product_type": "?",
            }
            
            rxn = self.deriver.derive(cut)
            if rxn:
                route["reaction"] = rxn.to_dict()
            
            if i == 0:
                # Best cut: pass sub-fragment SMILES recursively
                route["child_a"] = self.deep_retrosynthesis(
                    f"{fg1}_precursor", depth + 1, fg_hint=fg1,
                    fragment_smiles=frag_a)
                route["child_b"] = self.deep_retrosynthesis(
                    f"{fg2}_precursor", depth + 1, fg_hint=fg2,
                    fragment_smiles=frag_b)
            else:
                # Alternative cuts: terminal
                def _make_terminal(fg):
                    n = RetrosyntheticNode(f"{fg}_precursor", depth + 1)
                    n.fgs = [fg]
                    n.is_terminal = True
                    match = self._match_reagent(fg)
                    if match:
                        n.is_simple = True
                        n.reagent_match = match
                        n.terminal_reason = f"alt_scaffold, reagent: {match['name']}"
                    else:
                        n.terminal_reason = "alt_scaffold_no_reagent"
                    return n
                route["child_a"] = _make_terminal(fg1)
                route["child_b"] = _make_terminal(fg2)
            
            routes.append(route)
        
        return routes

    def resolve_and_parse_scaffold(self, target: str, smiles: str = "") -> bool:
        """Pass 1: Resolve target to SMILES and parse scaffold decomposition.
        
        Builds the scaffold map that maps FG-pair cuts to actual
        fragment SMILES from the target molecule.
        """
        if not smiles:
            smiles = resolve_name_to_smiles(target)
        
        if not smiles:
            print(f"  [scaffold] WARNING: Could not resolve '{target}' to SMILES. "
                  f"Using FG-only decomposition (no fragment structures).")
            return False
        
        try:
            parser = ScaffoldParser()
            parser.load(smiles, name=target)
            decomp = parser.get_full_scaffold_decomposition()
            
            self._scaffold_map = {}
            for pair_str, bonds in decomp.get("fg_pair_bonds", {}).items():
                import ast
                pair = ast.literal_eval(pair_str)
                pair_key = tuple(sorted(pair))
                if pair_key not in self._scaffold_map:
                    self._scaffold_map[pair_key] = []
                self._scaffold_map[pair_key].extend(bonds)
            
            self._target_smiles = smiles
            n_bonds = sum(len(v) for v in self._scaffold_map.values())
            
            info_line(f"  [scaffold] Pass 1: Parsed {target} [{smiles}]")
            print(f"  [scaffold]   {decomp['num_atoms']} atoms, {decomp['num_bonds']} bonds, "
                  f"{len(decomp['fgs'])} FGs: {', '.join(decomp['fgs'])}")
            print(f"  [scaffold]   {n_bonds} strategic disconnections across "
                  f"{len(self._scaffold_map)} FG-pair types")
            for pair, bonds in sorted(self._scaffold_map.items()):
                info_line(f"  [scaffold]     {pair[0]} + {pair[1]}: {len(bonds)} bond(s)")
            return True
            
        except Exception as e:
            error_line(f"  [scaffold] ERROR parsing scaffold: {e}")
            return False

    def _is_truly_simple(self, name: str) -> Tuple[bool, str]:
        """Check if a molecule is a genuine simple starting material.
        
        Uses ONLY the SIMPLE_STARTING_MATERIALS set + REAGENT_DB.
        Does NOT use the len(fgs)<=1 heuristic — that incorrectly marks
        complex single-FG molecules (indole, benzene, etc.) as simple.
        """
        name_lower = name.lower().replace(" ", "_").replace("-", "_")
        if name_lower in SIMPLE_STARTING_MATERIALS or name in SIMPLE_STARTING_MATERIALS:
            return True, "commercially_available"
        if name_lower in REAGENT_DB:
            return True, "in_reagent_db"
        return False, ""

    def deep_retrosynthesis(self, target: str, depth: int = 0,
                            fg_hint: Optional[str] = None,
                            fragment_smiles: Optional[str] = None) -> RetrosyntheticNode:
        """Full recursive retrosynthetic tree.

        Uses ch3mpiler's FG-based decomposition logic for intermediate steps.
        At terminal nodes (max depth, cycles, or no disconnections),
        matches against REAGENT_DB for concrete starting materials.

        Args:
            target: molecule name or FG-precursor name
            depth: current recursion depth
            fg_hint: if this precursor came from a disconnection, the FG it supplies
        """
        # ── Pass 1: Scaffold parsing (only at root, depth=0) ──
        if depth == 0 and not fg_hint:
            if hasattr(self, '_target_smiles') and self._target_smiles:
                self.resolve_and_parse_scaffold(target, self._target_smiles)
            else:
                self.resolve_and_parse_scaffold(target)

        node = RetrosyntheticNode(target, depth)
        if fragment_smiles:
            node.fragment_smiles = fragment_smiles

        # ── Attach scaffold decomposition data to root node ──
        if depth == 0 and not fg_hint and hasattr(self, '_scaffold_map'):
            # Collect all strategic bonds from scaffold map
            all_bonds = []
            for pair, bonds in self._scaffold_map.items():
                all_bonds.extend(bonds)
            node.strategic_bonds = all_bonds
            node.fg_pair_bonds = self._scaffold_map
            node.smiles = getattr(self, '_target_smiles', '')
            node.fragment_smiles = node.smiles or node.fragment_smiles

        # ── Terminal: max depth ──
        if depth >= self.max_depth:
            node.is_terminal = True
            match = self._match_reagent(fg_hint) if fg_hint else None
            if match:
                node.is_simple = True
                node.reagent_match = match
                node.terminal_reason = f"max_depth, reagent: {match['name']}"
            else:
                node.terminal_reason = f"max_depth={self.max_depth}"
            return node

        # ── Terminal: cycle detection ──
        name_key = (fg_hint or target).lower().replace(" ", "_").replace("-", "_")
        if name_key in self._visited:
            node.is_terminal = True
            match = self._match_reagent(fg_hint) if fg_hint else None
            if match:
                node.is_simple = True
                node.reagent_match = match
                node.terminal_reason = f"cycle, reagent: {match['name']}"
            else:
                node.terminal_reason = "cycle_detected"
            return node
        self._visited.add(name_key)

        # ── Determine FGs and type ──
        if fg_hint:
            # Use the FG hint directly — find_fgs can miss tokens like "aromatic_ring"
            fgs = [fg_hint]
            mol_type = FG_TYPES.get(fg_hint, {})
            type_src = "fg_hint"
        else:
            fgs = find_fgs(target)
            if not fgs:
                # Try token-based: strip "_precursor" suffix
                clean = target.replace("_precursor", "")
                fgs = find_fgs(clean)
            mol_type, type_src = get_molecule_type(target, self.compiler.catalog)
            if not mol_type and fgs:
                mol_type = FG_TYPES.get(fgs[0], {})

        node.fgs = fgs
        node.mol_type = fmt_tup(mol_type) if mol_type else "?"

        # ── Depth-0 SMILES target: name-based FG lookup fails for raw SMILES.
        # When scaffold map is populated but FG detection returned nothing,
        # extract FGs from the scaffold bond pairs and build routes directly.
        if depth == 0 and not fg_hint and not fgs and self._scaffold_map:
            all_bonds = []
            for bonds in self._scaffold_map.values():
                all_bonds.extend(bonds)
            if all_bonds:
                routes = self._build_scaffold_routes(all_bonds, depth)
                if routes:
                    fgs_set: set = set()
                    for pair in self._scaffold_map.keys():
                        fgs_set.update(pair)
                    node.fgs = sorted(fgs_set)
                    node.routes = routes
                    return node

        # ── Single FG: enumerate ALL FG types as co-precursors ──
        # Instead of terminating, find the best retrosynthetic disconnection
        # to form this FG from simpler precursors via exhaustive FG-pair search.
        if len(fgs) == 1 or (len(fgs) > 1 and len(set(fgs)) == 1):
            # ── RECURSIVE SCAFFOLD PATH: If we have a real fragment SMILES,
            # parse THAT fragment to find its actual bond cuts instead of
            # guessing abstract FG co-precursors. This is the key fix: every
            # tree level uses real structural decomposition, not FG guessing.
            if fragment_smiles and depth > 0:
                sub_map = self._parse_smiles_to_scaffold_map(fragment_smiles)
                if sub_map:
                    all_bonds = []
                    for pair in sorted(sub_map.keys()):
                        all_bonds.extend(sub_map[pair])
                    if all_bonds:
                        routes = self._build_scaffold_routes(all_bonds, depth, fragment_smiles)
                        if routes:
                            node.routes = routes
                            return node
            
            # ── FALLBACK: Abstract FG guessing (only when no fragment SMILES) ──
            routes = self._decompose_single_fg(fgs[0], mol_type, target, depth)
            if routes:
                node.routes = routes
                return node
            # No valid retrosynthetic disconnection → fall back to reagent matching
            node.is_terminal = True
            match = self._match_reagent(fgs[0])
            if match:
                node.is_simple = True
                node.reagent_match = match
                node.terminal_reason = f"single_fg_no_decomp, reagent: {match['name']}"
            else:
                nk = target.lower().replace(" ", "_").replace("-", "_")
                if nk in REAGENT_DB:
                    node.is_simple = True
                    node.reagent_match = {"name": target, "smiles": REAGENT_DB[nk]["smiles"],
                                          "distance": 0.0}
                    node.terminal_reason = "direct_reagent_match"
                else:
                    node.terminal_reason = "single_fg_no_decomp_no_reagent"
            return node

        # ── Terminal: no FGs, no type ──
        if not fgs or not mol_type:
            node.is_terminal = True
            match = self._match_reagent(fg_hint) if fg_hint else None
            if match:
                node.is_simple = True
                node.reagent_match = match
                node.terminal_reason = f"no_fgs, reagent: {match['name']}"
            else:
                # Try direct REAGENT_DB lookup by name
                nk = target.lower().replace(" ", "_").replace("-", "_")
                if nk in REAGENT_DB:
                    node.is_simple = True
                    node.reagent_match = {"name": target, "smiles": REAGENT_DB[nk]["smiles"],
                                          "distance": 0.0}
                    node.terminal_reason = "direct_reagent_match"
                else:
                    node.terminal_reason = "no_functional_groups"
            return node

        # ── Find disconnections ──
        cuts = find_disconnections(fgs, mol_type, max_results=5)

        # ── Terminal: no disconnections found ──
        if not cuts:
            node.is_terminal = True
            match = self._match_reagent(fgs[0]) if fgs else None
            if match:
                node.is_simple = True
                node.reagent_match = match
                node.terminal_reason = f"no_cuts, reagent: {match['name']}"
            else:
                # Try REAGENT_DB by name
                nk = target.lower().replace(" ", "_").replace("-", "_")
                if nk in REAGENT_DB:
                    node.is_simple = True
                    node.reagent_match = {"name": target, "smiles": REAGENT_DB[nk]["smiles"],
                                          "distance": 0.0}
                    node.terminal_reason = "direct_reagent_match"
                else:
                    node.terminal_reason = "no_viable_disconnections"
            return node

        # ── Recursive decomposition ──
        # Best cut gets full recursive decomposition.
        # Alternative cuts get route info only (terminal reagent matches for children).
        for i, cut in enumerate(cuts[:5]):
            route = {
                "index": i + 1,
                "fg1": cut["fg1"],
                "fg2": cut["fg2"],
                "bond": cut["bond"],
                "bond_desc": cut.get("bond_desc", cut["bond"]),
                "product_delta": cut.get("product_delta", cut.get("delta", 0)),
                "bond_delta": cut.get("bond_delta", 0),
                "product_type": cut.get("product_type", "?"),
            }

            # Derive reaction conditions for this disconnection
            rxn = self.deriver.derive(cut)
            if rxn:
                route["reaction"] = rxn.to_dict()

            if i == 0:
                # Best cut: full recursive decomposition
                # ── Compute fragment SMILES FIRST, then pass INTO recursion ──
                frag_a, frag_b = self._get_fragment_smiles_for_cut(
                    cut["fg1"], cut["fg2"], cut["bond"])
                route["child_a"] = self.deep_retrosynthesis(
                    f"{cut['fg1']}_precursor", depth + 1, fg_hint=cut["fg1"],
                    fragment_smiles=frag_a)
                route["child_b"] = self.deep_retrosynthesis(
                    f"{cut['fg2']}_precursor", depth + 1, fg_hint=cut["fg2"],
                    fragment_smiles=frag_b)
            else:
                # Alternative cuts: terminal reagent matches only (no recursion)
                def _make_terminal(fg_name):
                    n = RetrosyntheticNode(f"{fg_name}_precursor", depth + 1)
                    n.fgs = [fg_name]
                    n.is_terminal = True
                    match = self._match_reagent(fg_name)
                    if match:
                        n.is_simple = True
                        n.reagent_match = match
                        n.terminal_reason = f"alt_route, reagent: {match['name']}"
                    else:
                        n.terminal_reason = "alt_route_no_reagent"
                    return n
                route["child_a"] = _make_terminal(cut["fg1"])
                route["child_b"] = _make_terminal(cut["fg2"])

            node.routes.append(route)

        return node

    def _tree_to_dict(self, node: RetrosyntheticNode) -> Dict:
        """Convert a RetrosyntheticNode tree to a plain dict (for JSON output)."""
        result = {
            "name": node.name,
            "level": node.level,
            "fgs": node.fgs,
            "type": node.mol_type,
            "is_terminal": node.is_terminal,
            "is_simple": node.is_simple,
            "terminal_reason": node.terminal_reason,
        }
        if node.fragment_smiles:
            result["fragment_smiles"] = node.fragment_smiles
        if node.reagent_match:
            result["reagent_match"] = node.reagent_match
        if node.routes:
            result["routes"] = []
            for r in node.routes:
                rd = {
                    "index": r["index"],
                    "fg1": r["fg1"], "fg2": r["fg2"],
                    "bond": r["bond"], "bond_desc": r["bond_desc"],
                    "product_delta": r["product_delta"],
                    "reaction": r.get("reaction"),
                    "child_a": self._tree_to_dict(r["child_a"]),
                    "child_b": self._tree_to_dict(r["child_b"]),
                }
                result["routes"].append(rd)
        return result

    # ── Tree Printing ──

    def print_tree(self, node, prefix="", is_last=True, show_all_routes=False):
        """Pretty-print the retrosynthetic tree with rich text formatting."""
        if prefix == "":
            reaction_header(f"RETROSYNTHETIC TREE: {node.name}")
            if node.fgs:
                fg_line(f"FGs: {node.fgs}")
            if node.mol_type and node.mol_type != "?":
                numeric_line("Type", node.mol_type)
            separator()

        connector = "└── " if is_last else "├── "

        node_smi = node.smiles or node.fragment_smiles or _resolve_node_smiles(node.name)
        node_smi_str = f"  {_smi_display(node_smi)}" if node_smi else ""
        if node.is_terminal and node.is_simple:
            tag = "SIMPLE ✓"
            if node.reagent_match:
                rsmi = node.reagent_match['smiles']
                rform = _smiles_formula(rsmi)
                rform_str = f" [{rform}]" if rform else ""
                tag = f"{node.reagent_match['name']} [{rsmi}]{rform_str} (reagent)"
            elif node.fgs:
                tag += f" [{', '.join(node.fgs[:3])}]"
            if STYLED:
                success_line(f"{prefix}{connector}{node.name}  {node_smi_str}  -- {tag}")
            else:
                info_line(f"{prefix}{connector}{node.name}  {node_smi_str}  -- {tag}")
        elif node.is_terminal:
            if STYLED:
                error_line(f"{prefix}{connector}{node.name}  {node_smi_str}  -- TERMINAL ({node.terminal_reason})")
            else:
                info_line(f"{prefix}{connector}{node.name}  {node_smi_str}  -- TERMINAL ({node.terminal_reason})")
        else:
            n_routes = len(node.routes)
            if n_routes == 0:
                if STYLED:
                    error_line(f"{prefix}{connector}{node.name}  {node_smi_str}  -- NO ROUTES")
                else:
                    info_line(f"{prefix}{connector}{node.name}  {node_smi_str}  -- NO ROUTES")
                return

            best = node.routes[0]
            delta_str = ""
            if best.get("product_delta", 0) > 0:
                delta_str = f" (D={best['product_delta']:.3f})"
            # target_line already prepends "SMILES:" internally; pass smi+formula only
            _formula = _smiles_formula(node_smi) if node_smi else ""
            node_smi_for_target = (f"{node_smi}  [{_formula}]" if _formula else node_smi) if node_smi else ""
            if STYLED:
                target_line(f"{prefix}{connector}{node.name}", node_smi_for_target, indent=0)
                if delta_str:
                    info_line(f"{'':>{len(prefix)+4}}via {best['fg1']} + {best['fg2']} -> {best['bond']}{delta_str}")
            else:
                info_line(f"{prefix}{connector}{node.name}  {node_smi_str}  via {best['fg1']} + {best['fg2']} -> {best['bond']}{delta_str}")

            rxn = best.get("reaction", {})
            ext = "    " if is_last else "|   "
            if rxn:
                T_info = rxn.get("temperature", {})
                if T_info:
                    lo, hi = T_info.get("T_C", (20, 30))
                    regime = T_info.get("regime", "?")
                    info_line(f"{prefix}{ext}  Temp: ({lo}, {hi}) C [{regime}]")
                solv = rxn.get("solvent", {})
                if solv:
                    info_line(f"{prefix}{ext}  Solvent: {solv.get('name', '?')} (bp {solv.get('bp_C', '?')} C)")
                cat = rxn.get("catalyst")
                if cat:
                    info_line(f"{prefix}{ext}  Catalyst: {cat.get('name', '?')}")
                act = rxn.get("activator")
                if act:
                    info_line(f"{prefix}{ext}  Activator: {act.get('name', '?')}")
                wu = rxn.get("workup", {})
                if wu:
                    info_line(f"{prefix}{ext}  Workup: {wu.get('description', '?')}")

            ext_cont = "    " if is_last else "|   "
            child_a = best.get("child_a")
            child_b = best.get("child_b")

            if child_a and child_b:
                a_is_last = child_b.is_terminal
                self.print_tree(child_a, prefix + ext_cont, is_last=a_is_last)
                self.print_tree(child_b, prefix + ext_cont, is_last=True)
            elif child_a:
                self.print_tree(child_a, prefix + ext_cont, is_last=True)

            if show_all_routes and n_routes > 1:
                for r in node.routes[1:]:
                    pd = r.get("product_delta", 0)
                    info_line(f"{prefix}    [Alt] {r['fg1']} + {r['fg2']} -> {r['bond']} (D={pd:.3f})")

    def derive_reactions(self, target: str, max_cuts: int = 5) -> Dict:
        """Single-level pipeline: target -> disconnections -> reactions (no recursion)."""
        analysis = self.compiler.analyze(target)
        cuts = analysis.get("cuts", [])
        if not cuts:
            return {
                "target": target, "type": analysis.get("type", "?"),
                "fgs": analysis.get("fgs", []),
                "error": "No viable disconnections found", "reactions": [],
            }
        reactions = []
        for cut in cuts[:max_cuts]:
            rxn = self.deriver.derive(cut)
            if rxn:
                reactions.append(rxn.to_dict())
        return {
            "target": target, "type": analysis.get("type", "?"),
            "type_source": analysis.get("type_source", "?"),
            "fgs": analysis.get("fgs", []),
            "num_disconnections": len(cuts),
            "reactions_derived": len(reactions),
            "reactions": reactions,
            "structural_analogs": analysis.get("analogs", []),
        }

    def cas_pipeline(self, cas_number: str, max_cuts: int = 5) -> Dict:
        """CAS number -> resolve -> analyze -> derive reactions."""
        info = self.compiler.resolve_and_analyze(cas_number)
        name = info.get("cas_info", {}).get("name", cas_number)
        cuts = info.get("cuts", [])
        reactions = []
        for cut in cuts[:max_cuts]:
            rxn = self.deriver.derive(cut)
            if rxn:
                reactions.append(rxn.to_dict())
        return {
            "cas": cas_number, "name": name,
            "formula": info.get("cas_info", {}).get("formula", ""),
            "type": info.get("type", "?"), "fgs": info.get("fgs", []),
            "reactions": reactions,
        }

    def retrosynthetic_pipeline(self, target: str, depth: int = 2, max_cuts: int = 3) -> Dict:
        """DEPRECATED: Use deep_retrosynthesis() + print_tree() instead."""
        self._visited.clear()
        old_max = self.max_depth
        self.max_depth = min(depth, 6)
        tree = self.deep_retrosynthesis(target, depth=0)
        self.max_depth = old_max
        return self._tree_to_dict(tree)

    def print_synthesis(self, spec):
        """Pretty-print a single-level synthesis specification (rich formatted)."""
        tgt_smi = _resolve_node_smiles(spec['target'])
        reaction_header(f"SYNTHESIS: {spec['target']}", f"SMILES: {tgt_smi}" if tgt_smi else "")
        info_line(f"Type: {spec.get('type', '?')} [{spec.get('type_source', '?')}]")
        if spec.get('fgs'):
            fg_line(f"FGs: {spec.get('fgs', [])}")
        separator()
        reactions = spec.get('reactions', [])
        if not reactions:
            info_line("No reactions derived.")
            return
        for i, rxn in enumerate(reactions):
            disc = rxn.get('disconnection', f"Reaction {i+1}")
            subheader(f"ROUTE {i+1}: {disc}")
            numeric_line("Structural delta", rxn.get('structural_delta', '?'), indent=1)
            T = rxn.get('temperature', {})
            if T:
                info_line(f"Temperature: {T.get('T_C', (20,30))} C [{T.get('regime','?')}]", indent=1)
            solv = rxn.get('solvent', {})
            if solv:
                info_line(f"Solvent: {solv.get('name','?')} (bp {solv.get('bp_C','?')} C, d={solv.get('distance','?')})", indent=1)
            cat = rxn.get('catalyst')
            if cat:
                info_line(f"Catalyst: {cat.get('name','?')} ({cat.get('type','?')})", indent=1)
            act = rxn.get('activator')
            if act:
                info_line(f"Activator: {act.get('name','?')} ({act.get('type','?')})", indent=1)
            reacts = rxn.get('reactants', {})
            fg1r = reacts.get('fg1_reactants', [])
            fg2r = reacts.get('fg2_reactants', [])
            if fg1r:
                best = fg1r[0]
                info_line(f"Reactant 1: {best['name']} [{best['smiles']}] (d={best['distance']})", indent=1)
            if fg2r:
                best = fg2r[0]
                info_line(f"Reactant 2: {best['name']} [{best['smiles']}] (d={best['distance']})", indent=1)
            wu = rxn.get('workup', {})
            if wu:
                info_line(f"Workup: {wu.get('description','?')}", indent=1)

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="ch3mpiler reaction pipeline -- deep recursive retrosynthetic tree (grammar-first)")
    parser.add_argument("--smiles", help="Target SMILES (bypasses name-to-SMILES resolution)")
    parser.add_argument("--target", help="Molecule name")
    parser.add_argument("--cas", help="CAS Registry Number")
    parser.add_argument("--shallow", action="store_true", help="Single-level only (no recursion)")
    parser.add_argument("--depth", type=int, default=6, help="Max recursion depth (default: 6)")
    parser.add_argument("--max-cuts", type=int, default=5, help="Max disconnections per level")
    parser.add_argument("--all-routes", action="store_true", help="Show all alternative routes")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--cdxml", action="store_true", help="Export intermediates as CDXML")
    parser.add_argument("--cdxml-dir", type=str, default="cdxml_output",
                        help="Directory for CDXML exports (default: cdxml_output)")
    args = parser.parse_args()

    pipeline = ReactionPipeline(max_depth=args.depth)

    if args.demo:
        reaction_header("ch3mpiler Deep Retrosynthetic Pipeline", "Grammar-First — Decomposing until simple starting materials are reached")

        demos = [
            "benzaldehyde",
            "aspirin",
            "4-Methyl-5-phenyl-4,5-dihydro-1,3-oxazol-2-amine",
            "(Ra)-perdeutero-pentacyclo-1H-indole-3-ethanamine",
        ]
        for d in demos:
            pipeline._target_smiles = args.smiles or ""
            info_line(f"\n--- DEMO: {d} ---")
            pipeline._visited.clear()
            tree = pipeline.deep_retrosynthesis(d)
            pipeline.print_tree(tree)
            if args.cdxml:
                from cdxml.pipeline_hook import export_tree_to_cdxml
                result = export_tree_to_cdxml(tree, args.cdxml_dir, prefix=f"demo_{d}_", verbose=True)
                info_line(f"  >> CDXML: {result['generated']} files written to {args.cdxml_dir}/")
        return

    if args.cas:
        info = pipeline.compiler.resolve_and_analyze(args.cas)
        name = info.get("cas_info", {}).get("name", args.cas)
        if args.shallow:
            spec = pipeline.cas_pipeline(args.cas, max_cuts=args.max_cuts)
            if args.json:
                print(json.dumps(spec, indent=2, ensure_ascii=False))
            else:
                info_line(f"Target: {name}")
                info_line(f"Formula: {info.get('cas_info', {}).get('formula', '')}")
                pipeline.print_synthesis(spec)
        else:
            pipeline._target_smiles = info.get("cas_info", {}).get("smiles", "") or args.smiles or ""
            pipeline._visited.clear()
            tree = pipeline.deep_retrosynthesis(name)
            if args.json:
                print(json.dumps(pipeline._tree_to_dict(tree), indent=2, ensure_ascii=False))
            else:
                pipeline.print_tree(tree, show_all_routes=args.all_routes)
                if args.cdxml:
                    from cdxml.pipeline_hook import export_tree_to_cdxml
                    result = export_tree_to_cdxml(tree, args.cdxml_dir, verbose=True)
                    info_line(f"  >> CDXML: {result['generated']} files written to {args.cdxml_dir}/")
                    if result['failed']:
                        error_line(f"  >> Failed: {result['failed']}")
        return

    if args.target:
        if args.shallow:
            spec = pipeline.derive_reactions(args.target, max_cuts=args.max_cuts)
            if args.json:
                print(json.dumps(spec, indent=2, ensure_ascii=False))
            else:
                pipeline.print_synthesis(spec)
        else:
            pipeline._target_smiles = args.smiles or ""
            pipeline._visited.clear()
            tree = pipeline.deep_retrosynthesis(args.target)
            if args.json:
                print(json.dumps(pipeline._tree_to_dict(tree), indent=2, ensure_ascii=False))
            else:
                pipeline.print_tree(tree, show_all_routes=args.all_routes)
                if args.cdxml:
                    from cdxml.pipeline_hook import export_tree_to_cdxml
                    result = export_tree_to_cdxml(tree, args.cdxml_dir, verbose=True)
                    info_line(f"  >> CDXML: {result['generated']} files written to {args.cdxml_dir}/")
                    if result['failed']:
                        error_line(f"  >> Failed: {result['failed']}")
        return

    # Default: --smiles target if provided, else demo benzaldehyde
    info_line("=" * 72)
    info_line("  ch3mpiler Deep Retrosynthetic Pipeline -- Grammar-First Synthesis")
    info_line("  Use --target <molecule> for deep retrosynthetic tree")
    info_line("  Use --target <molecule> --shallow for single-level only")
    info_line("  Use --demo to see examples")
    info_line("=" * 72)
    print()
    pipeline._visited.clear()
    if args.smiles:
        pipeline._target_smiles = args.smiles
        tree = pipeline.deep_retrosynthesis(args.smiles)
    else:
        tree = pipeline.deep_retrosynthesis("benzaldehyde")
    pipeline.print_tree(tree)
    if args.cdxml:
        from cdxml.pipeline_hook import export_tree_to_cdxml
        result = export_tree_to_cdxml(tree, args.cdxml_dir, verbose=True)
        info_line(f"  >> CDXML: {result['generated']} files written to {args.cdxml_dir}/")


if __name__ == "__main__":
    main()
