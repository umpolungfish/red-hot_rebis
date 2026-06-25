#!/usr/bin/env python3
"""
scaffold_parser.py — Two-pass scaffold-aware retrosynthetic decomposition.

Pass 1: Parse target molecule SMILES → identify all disconnection sites
with bond types, ring systems, stereocenters, and FG locations.
For each strategic cut, generate actual fragment SMILES with proper valences.

Pass 2: Map retrosynthetic cuts back onto the scaffold. Each intermediate
carries its real fragment SMILES for CDXML output — NOT generic reagent matches.

Key feature: FG detection outputs pipeline-standard names so fragment SMILES
from scaffold cuts match the retrosynthetic disconnections.

Author: Lando⊗⊙perator
"""
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolDescriptors, rdchem

PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound"


def resolve_name_to_smiles(name: str) -> Optional[str]:
    """Resolve a chemical name to SMILES deterministically via OPSIN,
    with PubChem as fallback for names OPSIN cannot parse.

    OPSIN (Open Parser for Systematic IUPAC Nomenclature) is a Java library
    for deterministic IUPAC name -> SMILES conversion — no web dependency.
    PubChem fallback handles trivial names and very complex nomenclature."""
    # Phase 1: OPSIN (deterministic, local)
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    try:
        from iupac_resolver import iupac_to_smiles
        result = iupac_to_smiles(name)
        if result:
            return result
    except Exception:
        pass

    # Phase 2: PubChem web API (fallback)
    import urllib.parse
    encoded = urllib.parse.quote(name)
    url = f"{PUBCHEM_BASE}/name/{encoded}/property/CanonicalSMILES/JSON"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ch3mpiler/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            props = data["PropertyTable"]["Properties"][0]
        return props.get("CanonicalSMILES", "") or props.get("ConnectivitySMILES", "") or None
    except Exception:
        return None


# === Pipeline-standard FG name detection via SMARTS ===
# Maps pipeline FG names to SMARTS patterns for structural detection.
# Priority-ordered: first match wins (most specific first).
FG_SMARTS_PATTERNS = [
    # Ring systems
    ("aromatic_ring", "a"),                 # any aromatic atom
    ("spirocycle", None),                   # special: atom in 2+ rings (detected structurally)
    ("cyclic", None),                       # special: atom in any ring (detected structurally)
    # Oxygen FGs
    ("alcohol", "[OX2H]"),                  # O-H (not carbonyl)
    ("phenol", "[OX2H]c"),                  # O-H on aromatic ring
    ("carbonyl", "[CX3]=[OX1]"),            # C=O
    ("carboxylic_acid", "[CX3](=O)[OX2H]"), # C(=O)OH
    ("ester", "[CX3](=O)[OX2][#6]"),        # C(=O)OC
    ("ether", "[OX2]([#6])[#6]"),           # C-O-C (not carbonyl, not ester)
    ("ketone", "[#6][CX3](=O)[#6]"),        # C-C(=O)-C
    ("aldehyde", "[CX3H1](=O)[#6]"),        # HC(=O)-
    # Nitrogen FGs
    ("amine", "[NX3;H2,H1;!$(NC=O)]"),     # NH2/NH (not amide)
    ("amide", "[NX3][CX3](=[OX1])[#6]"),    # N-C(=O)-C
    ("nitrile", "[NX1]#[CX2]"),             # C#N
    ("aniline", "[NX3;H2,H1]c"),           # NH2 attached to aromatic
    ("aziridine", "[N]1[C][C]1"),          # 3-membered N ring
    ("imidazole", "c1[nH]cnc1"),           # imidazole ring
    # Halogens
    ("halide", "[F,Cl,Br,I]"),             # Any halogen
    # Other
    ("thiol", "[SX2H]"),                    # S-H
    ("sulfide", "[SX2]([#6])[#6]"),        # C-S-C
    ("alkene", "[CX3]=[CX3;!a]"),             # C=C
    ("alkyne", "[CX2]#[CX2]"),             # C#C
]
FG_SMARTS_PATTERNS_LIST = [(name, Chem.MolFromSmarts(sm) if sm else None) for name, sm in FG_SMARTS_PATTERNS]

# FG specificity priority: when multiple FGs are detected at one atom,
# the MOST specific FG wins. Used by get_strategic_bonds.
# Ordered from most specific to most generic.
FG_PRIORITY = [
    # Structural atom types first (these describe the atom itself)
    # Aromatic ring carbons should be classified as aromatic_ring,
    # not as ester/amide/etc. from extended SMARTS group matches.
    "spirocycle", "aromatic_ring", "cyclic",
    # Specific functional groups (substituent atoms, not the ring)
    "carboxylic_acid", "ester", "amide", "aniline", "phenol",
    "aldehyde", "ketone", "nitrile", "aziridine", "imidazole",
    "alcohol", "amine", "ether", "halide",
    "thiol", "sulfide", "alkene", "alkyne",
    # Generic fallback
    "alkane",
]


def detect_pipeline_fgs(mol, atom_idx: int) -> List[str]:
    """Detect pipeline-standard FG names at a given atom using SMARTS.
    
    Returns sorted list of pipeline FG names (from FG_TYPES keys).
    Uses SMARTS substructure matching, ring analysis, and element analysis.
    """
    if mol is None:
        return ["alkane"]
    atom = mol.GetAtomWithIdx(atom_idx)
    atomic_num = atom.GetAtomicNum()
    found = set()
    
    # 1. Ring membership (detected structurally, not via SMARTS)
    if atom.IsInRing():
        found.add("cyclic")
        # Spiro: atom in 2+ rings
        ri = mol.GetRingInfo()
        ring_count = sum(1 for r in ri.AtomRings() if atom_idx in r)
        if ring_count >= 2:
            found.add("spirocycle")
        # Check ring size for special types
        ring_sizes = set()
        for r in ri.AtomRings():
            if atom_idx in r:
                ring_sizes.add(len(r))
        if 3 in ring_sizes and atomic_num == 7:
            found.add("aziridine")
        if 3 in ring_sizes and atomic_num == 8:
            found.add("oxetane")  # 3-membered O ring = epoxide, 4 = oxetane
    
    # 2. Aromatic detection
    if atom.GetIsAromatic():
        found.add("aromatic_ring")
    
    # 3. SMARTS-based FG detection
    for fg_name, pattern in FG_SMARTS_PATTERNS_LIST:
        if pattern is None:
            continue  # handled structurally above
        matches = mol.GetSubstructMatches(pattern)
        for m in matches:
            # PHASE A: Primary-atom-only SMARTS matching
            # Only tag atom if it's the FIRST atom in the SMARTS match.
            # This prevents e.g. amide SMARTS [NX3][CX3](=[OX1])[#6]
            # from classifying the methyl carbon (position 3) as "amide".
            if len(m) > 0 and m[0] == atom_idx:
                found.add(fg_name)
                break

    # PHASE B: For O, N, S and halogen atoms, also accept any-position
    # matches so e.g. carbonyl oxygen retains "carbonyl" classification.
    if atomic_num in (8, 7, 16, 9, 17, 35, 53):
        for fg_name, pattern in FG_SMARTS_PATTERNS_LIST:
            if pattern is None:
                continue
            if fg_name in found:
                continue
            matches = mol.GetSubstructMatches(pattern)
            for m in matches:
                if atom_idx in m:
                    found.add(fg_name)
                    break
    
    # 4. Element-specific refinements (catches cases SMARTS misses)
    if atomic_num == 6 and not found:
        # Plain carbon: alkane by default
        found.add("alkane")
    elif atomic_num == 6 and "alkane" not in found and "aromatic_ring" not in found:
        found.add("alkane")
    
    # 5. Refinements: remove conflicting overlaps
    # Phenol subsumes alcohol
    if "phenol" in found and "alcohol" in found:
        found.discard("alcohol")
    # Ester subsumes carbonyl + ether
    if "ester" in found:
        found.discard("carbonyl")
    # Carboxylic acid subsumes carbonyl
    if "carboxylic_acid" in found:
        found.discard("carbonyl")
    # Amide subsumes carbonyl
    if "amide" in found and "carbonyl" in found:
        found.discard("carbonyl")
    # Aniline subsumes amine
    if "aniline" in found and "amine" in found:
        found.discard("amine")
    # Carboxylic acid subsumes alcohol (OH is part of COOH)
    if "carboxylic_acid" in found and "alcohol" in found:
        found.discard("alcohol")
    # Ester subsumes ether (ester O is not an ether)
    if "ester" in found and "ether" in found:
        found.discard("ether")
    # Cyclic subsumes alkene (ring C=C is not alkene FG)
    if "cyclic" in found and "alkene" in found:
        found.discard("alkene")
    # Aromatic ring subsumes alkene (kekulized double bonds)
    if "aromatic_ring" in found and "alkene" in found:
        found.discard("alkene")
    
    return sorted(found) if found else ["alkane"]

class ScaffoldParser:
    """Parse a target molecule and identify all disconnection sites.
    
    For each bond that could be a retrosynthetic disconnection:
    - Generate the fragment SMILES for both sides (with radical caps)
    - Identify the pipeline-standard FG type at each cut site
    - Record bond type, stereochemistry, ring context
    """
    
    def __init__(self):
        self._mol = None
        self._smiles = ""
        self._name = ""
    
    def load(self, smiles: str, name: str = ""):
        """Load a molecule from SMILES."""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")
        AllChem.Compute2DCoords(mol)
        self._mol = mol
        self._smiles = smiles
        self._name = name or smiles
    
    def _get_fg_at_atom(self, atom_idx: int) -> List[str]:
        """Identify pipeline-standard FG names at a specific atom.
        
        Uses SMARTS patterns + structural analysis to detect FGs.
        Returns sorted list of pipeline FG names.
        """
        return detect_pipeline_fgs(self._mol, atom_idx)
    
    def _is_carbonyl_oxygen(self, o_idx: int) -> bool:
        """Check if an oxygen atom is double-bonded to carbon (carbonyl)."""
        if self._mol is None:
            return False
        atom = self._mol.GetAtomWithIdx(o_idx)
        if not atom.GetNeighbors():
            return False
        neighbor = atom.GetNeighbors()[0]
        bond = self._mol.GetBondBetweenAtoms(o_idx, neighbor.GetIdx())
        return bond is not None and bond.GetBondType() == rdchem.BondType.DOUBLE
    
    def _is_amide_nitrogen(self, n_idx: int) -> bool:
        """Check if a nitrogen is adjacent to a carbonyl carbon."""
        if self._mol is None:
            return False
        atom = self._mol.GetAtomWithIdx(n_idx)
        for neighbor in atom.GetNeighbors():
            if neighbor.GetAtomicNum() == 6:  # Carbon
                for nn in neighbor.GetNeighbors():
                    if nn.GetAtomicNum() == 8 and self._is_carbonyl_oxygen(nn.GetIdx()):
                        return True
        return False
    
    def get_strategic_bonds(self) -> List[Dict]:
        """Identify all strategic disconnection sites on the scaffold.
        
        Returns a list of disconnection candidates, each with:
        - bond_idx: index of the bond to cut
        - bond_type: sigma_single, amide_link, ester_link, etc.
        - fg1, fg2: pipeline-standard FG names on each side
        - fragment_smiles_a, fragment_smiles_b: actual fragment SMILES after cutting
        - ring_context: whether the bond is in a ring
        """
        if self._mol is None:
            return []
        
        mol = self._mol
        results = []
        ring_info = mol.GetRingInfo()
        ring_bonds = set()
        for ring in ring_info.BondRings():
            for b in ring:
                ring_bonds.add(b)
        
        for bond in mol.GetBonds():
            bi = bond.GetIdx()
            btype = bond.GetBondType()
            a1 = bond.GetBeginAtomIdx()
            a2 = bond.GetEndAtomIdx()
            
            # Determine bond type (pipeline-standard names)
            if btype == rdchem.BondType.SINGLE:
                bond_type = "sigma_single"
            elif btype == rdchem.BondType.DOUBLE:
                bond_type = "double_bond"
            elif btype == rdchem.BondType.TRIPLE:
                bond_type = "triple_bond"
            elif btype == rdchem.BondType.AROMATIC:
                bond_type = "aromatic"
            else:
                bond_type = "sigma_single"
            
            # Special bond type detection using SMARTS
            if bond_type == "sigma_single":
                n1 = mol.GetAtomWithIdx(a1)
                n2 = mol.GetAtomWithIdx(a2)
                # Amide bond: C(=O)-N
                if (n1.GetAtomicNum() == 6 and n2.GetAtomicNum() == 7 and
                    self._is_amide_nitrogen(a2)):
                    bond_type = "amide_link"
                elif (n1.GetAtomicNum() == 7 and n2.GetAtomicNum() == 6 and
                      self._is_amide_nitrogen(a1)):
                    bond_type = "amide_link"
                # Ester bond: C(=O)-O
                elif n1.GetAtomicNum() == 8 and n2.GetAtomicNum() == 6:
                    # Check if the carbon has a carbonyl oxygen
                    for nn in n2.GetNeighbors():
                        if nn.GetAtomicNum() == 8 and nn.GetIdx() != a1:
                            bond = mol.GetBondBetweenAtoms(n2.GetIdx(), nn.GetIdx())
                            if bond and bond.GetBondType() == rdchem.BondType.DOUBLE:
                                bond_type = "ester_link"
                                break
                elif n2.GetAtomicNum() == 8 and n1.GetAtomicNum() == 6:
                    for nn in n1.GetNeighbors():
                        if nn.GetAtomicNum() == 8 and nn.GetIdx() != a2:
                            bond = mol.GetBondBetweenAtoms(n1.GetIdx(), nn.GetIdx())
                            if bond and bond.GetBondType() == rdchem.BondType.DOUBLE:
                                bond_type = "ester_link"
                                break            # Ether bond: C-O-C (not ester)
            if bond_type == "sigma_single":
                n1 = mol.GetAtomWithIdx(a1)
                n2 = mol.GetAtomWithIdx(a2)
                if n1.GetAtomicNum() == 8 and n2.GetAtomicNum() == 6:
                    bond_type = "ether_link"
                elif n2.GetAtomicNum() == 8 and n1.GetAtomicNum() == 6:
                    bond_type = "ether_link"
                # Hydrogen bond: O-H or N-H
                if (n1.GetAtomicNum() == 1 and n2.GetAtomicNum() in (7, 8)):
                    bond_type = "hydrogen_bond"
                elif (n2.GetAtomicNum() == 1 and n1.GetAtomicNum() in (7, 8)):
                    bond_type = "hydrogen_bond"
            
            # Get pipeline-standard FGs on each side
            fg1 = self._get_fg_at_atom(a1)
            fg2 = self._get_fg_at_atom(a2)
            
            # Generate fragment SMILES by cutting this bond (keyed to atoms)
            frag_a, frag_b = self._cut_bond_keyed(bi, a1, a2)
            
            # Check if this is a strategic disconnection
            is_strategic = (
                not bi in ring_bonds and  # Don't cut rings
                len(fg1) > 0 and len(fg2) > 0 and
                not (set(fg1) == {"alkane"} and set(fg2) == {"alkane"})  # At least one FG
            )
            
            best_fg1 = next((f for f in FG_PRIORITY if f in fg1), fg1[0] if fg1 else "alkane")
            best_fg2 = next((f for f in FG_PRIORITY if f in fg2), fg2[0] if fg2 else "alkane")
            
            results.append({
                "bond_idx": int(bi),
                "atom_a": int(a1),
                "atom_b": int(a2),
                "bond_type": bond_type,
                "fg1": best_fg1,
                "fg2": best_fg2,
                "fg_list_a": fg1,
                "fg_list_b": fg2,
                "fragment_smiles_a": frag_a,
                "fragment_smiles_b": frag_b,
                "in_ring": bi in ring_bonds,
                "is_rotatable": not bi in ring_bonds,
                "is_strategic": is_strategic,
            })
        
        return results
    
    def _cut_bond_keyed(self, bond_idx: int, atom_a_idx: int, atom_b_idx: int) -> Tuple[Optional[str], Optional[str]]:
        """Cut a bond and return fragment SMILES keyed to (atom_a, atom_b).
        
        Returns (fragment_containing_atom_a, fragment_containing_atom_b).
        Uses GetMolFrags with atom index lists to determine which fragment
        contains which original atom.
        
        Uses RDKit's FragmentOnBonds with dummy labeling to cap the broken
        valence with hydrogen atoms. Falls back to RemoveBond + GetMolFrags.
        """
        mol = self._mol
        if mol is None:
            return None, None
        
        def _get_keyed_frags(frag_mol):
            """Extract SMILES keyed to (frag_a, frag_b) from fragmented molecule."""
            # Get fragments both as molecules and as atom index lists
            frag_atom_lists = Chem.GetMolFrags(frag_mol, asMols=False, sanitizeFrags=False)
            frag_mols = Chem.GetMolFrags(frag_mol, asMols=True, sanitizeFrags=False)
            
            if len(frag_mols) < 2:
                return None, None
            
            # Determine which fragment list contains atom_a_idx
            a_in_frag0 = atom_a_idx in frag_atom_lists[0]
            a_in_frag1 = atom_a_idx in frag_atom_lists[1]
            
            # Convert to SMILES
            smis = []
            for m in frag_mols:
                try:
                    smi = Chem.MolToSmiles(m)
                except:
                    smi = Chem.MolToSmiles(m, kekuleSmiles=True)
                smis.append(smi)
            
            if a_in_frag0:
                return smis[0], smis[1]  # frag0=atom_a, frag1=atom_b
            elif a_in_frag1:
                return smis[1], smis[0]  # frag1=atom_a, frag0=atom_b
            else:
                # Fallback: neither found (shouldn't happen). Return size-ordered.
                sorted_mols = sorted(frag_mols, key=lambda m: m.GetNumAtoms(), reverse=True)
                try:
                    return Chem.MolToSmiles(sorted_mols[0]), Chem.MolToSmiles(sorted_mols[1])
                except:
                    return Chem.MolToSmiles(sorted_mols[0], kekuleSmiles=True),                            Chem.MolToSmiles(sorted_mols[1], kekuleSmiles=True)
        
        try:
            # Method 1: FragmentOnBonds
            frag_mol = Chem.FragmentOnBonds(
                mol, [bond_idx], addDummies=False
            )
            result = _get_keyed_frags(frag_mol)
            if result[0] is not None:
                return result
        except Exception:
            pass
        
        # Method 2: Fallback — RemoveBond
        try:
            emol = Chem.RWMol(mol)
            emol.RemoveBond(atom_a_idx, atom_b_idx)
            result = _get_keyed_frags(emol)
            if result[0] is not None:
                return result
        except Exception:
            pass
        
        return None, None
    def get_full_scaffold_decomposition(self) -> Dict:
        """Full Pass 1 decomposition: scaffold analysis with all cuts mapped.
        
        Returns dict with:
        - smiles, name, num_atoms, num_bonds
        - fgs: all pipeline-standard FGs present in the molecule
        - fg_locations: atom indices per FG
        - strategic_bonds: all rotatable disconnection sites
        - all_bonds: all bonds with FG assignments
        - fg_pair_bonds: grouped by FG pair (pipeline-standard names)
          For easy lookup by the pipeline's _get_fragment_smiles_for_cut
        """
        bonds = self.get_strategic_bonds()
        
        # Identify all pipeline-standard FGs present
        all_fgs = set()
        fg_locations = {}
        for b in bonds:
            for fg in b.get("fg_list_a", []):
                all_fgs.add(fg)
                fg_locations.setdefault(fg, set()).add(b["atom_a"])
            for fg in b.get("fg_list_b", []):
                all_fgs.add(fg)
                fg_locations.setdefault(fg, set()).add(b["atom_b"])
        
        # Group bonds by FG pair (sorted for consistent lookup)
        # Only include strategic (non-ring, non-aromatic) bonds
        fg_pair_bonds = {}
        for b in bonds:
            if not b.get("is_strategic", False):
                continue  # skip ring bonds — can't cut rings into separate fragments
            pair = tuple(sorted([b["fg1"], b["fg2"]]))
            fg_pair_bonds.setdefault(pair, []).append(b)
        
        return {
            "smiles": self._smiles,
            "name": self._name,
            "num_atoms": self._mol.GetNumAtoms() if self._mol else 0,
            "num_bonds": self._mol.GetNumBonds() if self._mol else 0,
            "fgs": sorted(all_fgs),
            "fg_locations": {k: sorted(v) for k, v in fg_locations.items()},
            "strategic_bonds": [b for b in bonds if b["is_strategic"]],
            "all_bonds": bonds,
            "fg_pair_bonds": {
                str(k): [
                    {
                        "bond_idx": b["bond_idx"],
                        "bond_type": b["bond_type"],
                        "fg1": b["fg1"],
                        "fg2": b["fg2"],
                        "atom_a": b["atom_a"],
                        "atom_b": b["atom_b"],
                        "fragment_smiles_a": b["fragment_smiles_a"],
                        "fragment_smiles_b": b["fragment_smiles_b"],
                        "in_ring": b["in_ring"],
                        "is_strategic": b["is_strategic"],
                    }
                    for b in v
                ]
                for k, v in fg_pair_bonds.items()
            },
        }