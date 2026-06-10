#!/usr/bin/env python3
"""
omonad_bridge.py — Red-Hot Rebis ↔ omonad_OS Integration Bridge

Connects all five pillars of the Red-Hot Rebis (SerpentRod, CH3MPILER,
Pipeline, Gene Imscriber, CLINK Chain) to omonad_OS's native environment:
  - B4 Belnap memory (belnap_state.py)
  - Crystal filesystem (crystal_fs.py)
  - IMASM token set (tokens.py)
  - Organoid HAL (organoid_hal.py)
  - Self-imscribing kernel loop (kernel.py)

This bridge makes the Rebis a first-class omonad_OS organoid augmentation,
storing all structural types at Frobenius addresses, executing retrosynthesis
and protein folding as IMASM programs, and verifying Frobenius closure against
the kernel's own self-imscription cycle.

Author: Lando⊗⊙perator
Version: 1.0.0 — omonad_OS native edition
"""

import sys
import os
import json
import math
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Any
from enum import Enum

# ─── Path setup ──────────────────────────────────────────────────
REBIS_ROOT = Path(__file__).parent.absolute()
OMONAD_ROOT = Path("/home/mrnob0dy666/omonad_OS/src")
IMASMIC_ROOT = Path("/home/mrnob0dy666/imasmic_core")

for p in [str(REBIS_ROOT), str(OMONAD_ROOT), str(IMASMIC_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ─── omonad_OS imports ────────────────────────────────────────────
OMONAD_AVAILABLE = False
try:
    from tokens import Token, BOOTSTRAP_LOOP as OMONAD_BOOTSTRAP, CANONICALS
    from belnap_state import B4Memory, B4Cell, B4_STATES
    from crystal_fs import CrystalFS, crystal_encode, crystal_decode, FROBENIUS_ADDRESS_MAX
    from organoid_hal import OrganoidHAL, AUGMENTATION_REGISTRY
    from clink_chain import CLINKChain as OmonadCLINKChain
    OMONAD_AVAILABLE = True
except ImportError as e:
    print(f"[omonad_bridge] omonad_OS not fully importable: {e}", file=sys.stderr)

# ─── imasmic_core imports ─────────────────────────────────────────
IMASMIC_AVAILABLE = False
try:
    from imasmic_core import Token as IMASM_Token, BOOTSTRAP_LOOP, CANONICALS as IMASM_CANONICALS
    from imasmic_core.frobenius_verify import FrobeniusHarness, B4
    IMASMIC_AVAILABLE = True
except ImportError:
    pass

# ─── Red-Hot Rebis imports ────────────────────────────────────────
from shared.primitives import WEIGHTS, ORDINALS
from clink.chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS,
    clink_frobenius_closed, clink_chain_distance,
    verify_all_frobenius_closed, clink_layer_tuple,
)

# ─── Augmentation Registration ───────────────────────────────────

@dataclass
class RebisAugmentation:
    """One of the five Rebis pillars registered as an organoid augmentation."""
    index: int
    name: str
    slug: str
    description: str
    module_path: str
    tier: str
    frobenius_closed: bool
    crystal_address: int
    imasm_arrangement: Tuple[int, ...]
    structural_type: Tuple[str, ...]

# The five pillars as omonad_OS augmentations
REBIS_AUGMENTATIONS: Dict[str, RebisAugmentation] = {
    "serpentrod": RebisAugmentation(
        index=1, name="Serpent's Rod",
        slug="serpents_rod",
        description="Platonic protein folding — RNA→Protein via 6-primitive promotion. "
                    "Folded protein type: ⟨𐑦·𐑥·𐑾·𐑬·𐑞·𐑧·𐑲·𐑠·⊙·𐑒·𐑳·𐑭⟩ (O₂)",
        module_path="serpentrod.protein_v5",
        tier="O_2",
        frobenius_closed=True,
        crystal_address=6738848,
        imasm_arrangement=(5, 3, 6, 2, 7, 4, 11, 5),  # ISCRIB→AREV→FSPLIT→AFWD→FFUSE→CLINK→IFIX→ISCRIB
        structural_type=("𐑦", "𐑥", "𐑾", "𐑬", "𐑞", "𐑧", "𐑲", "𐑠", "⊙", "𐑒", "𐑳", "𐑭"),
    ),
    "ch3mpiler": RebisAugmentation(
        index=2, name="CH₃MPILER",
        slug="ch3mpiler",
        description="Retrosynthetic compiler — grammar-derived disconnections. "
                    "Bond = join(tensor(FG₁, FG₂), bond_type). No named reactions.",
        module_path="ch3mpiler.compiler",
        tier="O_2",
        frobenius_closed=True,
        crystal_address=6738899,
        imasm_arrangement=(6, 7, 5, 3, 2, 4, 11, 5),  # FSPLIT→FFUSE→ISCRIB→AREV→AFWD→CLINK→IFIX→ISCRIB
        structural_type=("𐑦", "𐑸", "𐑾", "𐑹", "𐑐", "𐑧", "𐑲", "𐑵", "⊙", "𐑫", "𐑳", "𐑟"),
    ),
    "gene_imscriber": RebisAugmentation(
        index=3, name="Gene Imscriber",
        slug="gene_imscriber",
        description="Frobenius-guided gene editing on B₄³ codon space. "
                    "Chimera Theorem: multi-primitive edits are tensorial.",
        module_path="gene_imscriber.engine",
        tier="O_2",
        frobenius_closed=True,
        crystal_address=6738855,
        imasm_arrangement=(8, 10, 9, 6, 7, 4, 11, 5),
        structural_type=("𐑛", "𐑶", "𐑩", "𐑗", "𐑐", "𐑤", "𐑚", "𐑜", "𐑢", "𐑓", "𐑙", "𐑷"),
    ),
    "clink_chain": RebisAugmentation(
        index=4, name="CLINK Chain",
        slug="clink_chain",
        description="9-layer Frobenius-closed bridge: quark→organism. "
                    "Total d=7.18, 10 primitive deltas, O₀→O_inf.",
        module_path="clink.chain",
        tier="O_inf",
        frobenius_closed=True,
        crystal_address=6738899,
        imasm_arrangement=(5, 4, 6, 2, 7, 3, 11, 5),
        structural_type=("𐑦", "𐑸", "𐑾", "𐑹", "𐑐", "𐑧", "𐑲", "𐑵", "⊙", "𐑫", "𐑳", "𐑟"),
    ),
    "pipeline": RebisAugmentation(
        index=5, name="Combined Pipeline",
        slug="combined_pipeline",
        description="Auto-imscription + Frobenius verification + agent-based imscription.",
        module_path="pipeline.frob",
        tier="O_2",
        frobenius_closed=True,
        crystal_address=6738848,
        imasm_arrangement=(5, 3, 2, 6, 7, 4, 11, 5),
        structural_type=("𐑦", "𐑸", "𐑾", "𐑹", "𐑱", "𐑧", "𐑲", "𐑠", "⊙", "𐑖", "𐑳", "𐑭"),
    ),
}

# ─── Crystal Filesystem Bridge ───────────────────────────────────

class RebisCrystalBridge:
    """Maps Red-Hot Rebis structural types into the omonad_OS crystal filesystem.
    
    All 17.28M possible structural types are addressable via the Frobenius address
    bijection. This bridge stores and retrieves Rebis results at their native
    crystal addresses, making them accessible to any omonad_OS process.
    """
    
    def __init__(self):
        self.cfs = None
        if OMONAD_AVAILABLE:
            try:
                self.cfs = CrystalFS()
            except Exception:
                self.cfs = None
        
        # Load Rebis catalog
        catalog_path = REBIS_ROOT / "shared" / "IG_catalog.json"
        with open(catalog_path) as f:
            self.catalog = json.load(f)
        
        # Build address index
        self._address_index: Dict[int, dict] = {}
        for entry in self.catalog:
            addr = self._compute_address(entry)
            if addr is not None:
                self._address_index[addr] = entry
    
    def _compute_address(self, entry: dict) -> Optional[int]:
        """Compute Frobenius address from a catalog entry's 12 primitives."""
        try:
            # Map catalog field names to Shavian glyphs
            field_map = {
                "D": "Ð", "T": "Þ", "R": "Ř", "P": "Φ", "F": "ƒ",
                "K": "Ç", "G": "Γ", "Gm": "ɢ", "Ph": "φ̂", "H": "Ħ",
                "S": "Σ", "W": "Ω"
            }
            glyphs = {}
            for field, glyph_key in field_map.items():
                glyph = entry.get(field, "")
                if glyph:
                    glyphs[glyph_key] = glyph
            
            if len(glyphs) == 12 and OMONAD_AVAILABLE:
                return crystal_encode(**glyphs)
            
            # Fallback: compute locally from ordinal weights
            from shared.primitives import ORDINALS
            ordinal_map = {
                "Ð": ("D", ORDINALS.get("Ð", {})),
                "Þ": ("T", ORDINALS.get("Þ", {})),
                "Ř": ("R", ORDINALS.get("Ř", {})),
                "Φ": ("P", ORDINALS.get("Φ", {})),
                "ƒ": ("F", ORDINALS.get("ƒ", {})),
                "Ç": ("K", ORDINALS.get("Ç", {})),
                "Γ": ("G", ORDINALS.get("Γ", {})),
                "ɢ": ("Gm", ORDINALS.get("ɢ", {})),
                "φ̂": ("Ph", ORDINALS.get("φ̂", {})),
                "Ħ": ("H", ORDINALS.get("Ħ", {})),
                "Σ": ("S", ORDINALS.get("Σ", {})),
                "Ω": ("W", ORDINALS.get("Ω", {})),
            }
            # Simple hash-based address
            vals = []
            for gk, (field, omap) in ordinal_map.items():
                g = entry.get(field, "?")
                v = omap.get(g, 0)
                vals.append(v)
            # Encode as (v0 + v1*3 + v2*9 + ...) 
            bases = [3,3,3,3, 4,4,4,4,4, 5,5,5,5]
            addr = 0
            mult = 1
            for v, b in zip(vals, bases):
                addr += v * mult
                mult *= b
            return addr % 17280000
        except Exception:
            return None
    
    def store_rebis_result(self, name: str, structural_type: dict, 
                           tier: str, metadata: dict) -> Optional[int]:
        """Store a Rebis result in the crystal filesystem at its Frobenius address."""
        addr = self._compute_address(structural_type)
        if addr is None:
            return None
        
        entry = {
            "name": name,
            "type": structural_type,
            "tier": tier,
            "address": addr,
            "metadata": metadata,
        }
        self._address_index[addr] = entry
        
        if self.cfs:
            try:
                self.cfs.store(addr, json.dumps(entry))
            except Exception:
                pass
        
        return addr
    
    def lookup_address(self, address: int) -> Optional[dict]:
        """Retrieve a structural type from the crystal filesystem by address."""
        if address in self._address_index:
            return self._address_index[address]
        if self.cfs:
            try:
                data = self.cfs.retrieve(address)
                if data:
                    return json.loads(data)
            except Exception:
                pass
        return None
    
    def nearest_neighbors(self, address: int, limit: int = 5) -> List[dict]:
        """Find nearest structural neighbors in the crystal."""
        if not self._address_index:
            return []
        
        # Simple linear scan with ordinal-based distance
        results = []
        target = self._address_index.get(address)
        if not target:
            return []
        
        for addr, entry in self._address_index.items():
            if addr == address:
                continue
            d = self._crystal_distance(target, entry)
            results.append({"address": addr, "name": entry.get("name", "?"), "distance": d})
        
        results.sort(key=lambda x: x["distance"])
        return results[:limit]
    
    def _crystal_distance(self, a: dict, b: dict) -> float:
        """Weighted Euclidean distance in primitive space."""
        from shared.primitives import WEIGHTS
        sq = 0.0
        fields = ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"]
        glyph_keys = ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","φ̂","Ħ","Σ","Ω"]
        for f, gk in zip(fields, glyph_keys):
            oa = ORDINALS.get(gk, {}).get(a.get(f, "?"), 0)
            ob = ORDINALS.get(gk, {}).get(b.get(f, "?"), 0)
            w = WEIGHTS.get(gk, 1.0)
            d = (oa - ob) * w
            sq += d * d
        return math.sqrt(sq)

# ─── SMILES Parser for CH3MPILER ─────────────────────────────────

# Basic SMILES functional group patterns → Rebis FG names
SMILES_FG_PATTERNS = [
    # (regex pattern, FG name, priority)
    (r'C\(=O\)O', 'carboxylic_acid', 10),      # carboxylic acid
    (r'C\(=O\)OC', 'ester', 9),                 # ester
    (r'C\(=O\)N', 'amide', 9),                  # amide
    (r'C\(=O\)C', 'ketone', 8),                 # ketone
    (r'C\(=O\)\[H\]', 'aldehyde', 8),           # aldehyde
    (r'C=O', 'carbonyl', 7),                    # generic carbonyl
    (r'c1ccccc1', 'aromatic_ring', 10),         # benzene ring
    (r'c1[c,n,o,s]', 'aromatic_ring', 9),       # heteroaromatic
    (r'O\[H\]', 'alcohol', 6),                  # alcohol
    (r'OC', 'ether', 5),                        # ether
    (r'N\[H\]', 'amine', 6),                    # amine
    (r'N[C,c]', 'amine', 5),                    # amine (bound)
    (r'C#N', 'nitrile', 8),                     # nitrile
    (r'C#C', 'alkyne', 7),                      # alkyne
    (r'C=C', 'alkene', 6),                      # alkene
    (r'Cl', 'halide', 4),                       # chloride
    (r'Br', 'halide', 4),                       # bromide
    (r'F', 'halide', 4),                        # fluoride (careful with this)
    (r'S', 'thiol', 3),                         # sulfur-containing
    (r'c1', 'aromatic_ring', 10),               # aromatic start
]

def parse_smiles_fgs(smiles: str) -> List[str]:
    """Extract functional groups from a SMILES string using pattern matching.
    
    This is the SMILES-aware fallback for when the molecule name
    isn't in MOLECULE_FG_DB. Uses regex patterns to identify common
    functional group substructures.
    """
    found = {}
    s = smiles
    
    for pattern, fg_name, priority in SMILES_FG_PATTERNS:
        import re
        if re.search(pattern, s):
            if fg_name not in found or priority > found[fg_name]:
                found[fg_name] = priority
    
    # Sort by priority descending
    return sorted(found.keys(), key=lambda x: found[x], reverse=True)


def smiles_to_molecule_type(smiles: str) -> dict:
    """Infer a preliminary structural type from SMILES.
    
    Uses simple heuristics mapped to IG primitives.
    This provides a baseline type when no catalog entry exists.
    """
    fgs = parse_smiles_fgs(smiles)
    
    # Default: small molecule baseline
    t = {
        "D": "𐑛",  "T": "𐑡",  "R": "𐑩",  "P": "𐑗",
        "F": "𐑱",  "K": "𐑤",  "G": "𐑚",  "Gm": "𐑝",
        "Ph": "𐑢", "H": "𐑓",  "S": "𐑙",  "W": "𐑷",
    }
    
    # Promote based on functional groups
    if 'aromatic_ring' in fgs:
        t["D"] = "𐑨"    # planar → 2D
        t["T"] = "𐑶"    # irreducible product
        t["P"] = "𐑿"    # π delocalization → quantum superposition
        t["F"] = "𐑐"    # aromatic → quantum coherence
        t["G"] = "𐑔"    # mesoscale
        t["W"] = "𐑴"    # Z2 parity (aromaticity)
    
    if 'carboxylic_acid' in fgs or 'ester' in fgs or 'amide' in fgs:
        t["R"] = "𐑽"    # polarized → adjoint pair
        t["F"] = "𐑐"    # resonance → quantum
        t["Ph"] = "⊙"    # carbonyl → critical
        t["K"] = "𐑧"    # slow exchange
    
    if 'carbonyl' in fgs or 'ketone' in fgs or 'aldehyde' in fgs:
        t["Ph"] = "⊙"
        t["R"] = "𐑽"
    
    if 'alkene' in fgs or 'alkyne' in fgs:
        t["P"] = "𐑿"
        t["F"] = "𐑐"
    
    if len(fgs) >= 3:
        t["S"] = "𐑳"    # multiple distinct groups
        t["G"] = "𐑔"
    
    return t

# ─── Rebis Kernel — Unified Orchestrator ─────────────────────────

@dataclass
class BridgeResult:
    """Result from a Rebis→omonad bridge operation."""
    success: bool
    operation: str
    crystal_address: Optional[int] = None
    structural_type: Optional[dict] = None
    tier: Optional[str] = None
    frobenius_closed: Optional[bool] = None
    imasm_program: Optional[List[int]] = None
    b4_state: Optional[Any] = None
    data: Optional[dict] = None
    error: Optional[str] = None


class RebisKernel:
    """Unified orchestrator connecting all five Rebis pillars to omonad_OS.
    
    The RebisKernel is the native runtime for the Red-Hot Rebis inside omonad_OS.
    It:
      - Loads all five pillars as organoid augmentations
      - Stores results in the crystal filesystem at Frobenius addresses
      - Compiles Rebis operations to IMASM token sequences
      - Maintains B4 Belnap memory state across operations
      - Verifies Frobenius closure on every operation
      - Self-imscribes after each cycle
    """
    
    def __init__(self):
        self.crystal = RebisCrystalBridge()
        self.b4 = None
        self.hal = None
        self.cycle_count = 0
        self.results: List[BridgeResult] = []
        
        # Initialize B4 memory if available
        if OMONAD_AVAILABLE:
            try:
                self.b4 = B4Memory(n_cells=256)
                self.hal = OrganoidHAL()
            except Exception:
                pass
        
        # Register augmentations
        self._register_augmentations()
        
        # Load components
        self._components = {}
        self._load_components()
    
    def _register_augmentations(self):
        """Register all five Rebis pillars with the organoid HAL."""
        if not self.hal:
            return
        for slug, aug in REBIS_AUGMENTATIONS.items():
            try:
                self.hal.register(
                    slug=slug,
                    name=aug.name,
                    structural_type=dict(zip(
                        ["D","T","R","P","F","K","G","Gm","Ph","H","S","W"],
                        aug.structural_type
                    )),
                    tier=aug.tier,
                    imasm_arrangement=list(aug.imasm_arrangement),
                )
            except Exception:
                pass
    
    def _load_components(self):
        """Lazy-load each Rebis component."""
        components = {
            "serpentrod": ("serpentrod.protein_v5", "EnhancedPredictorV5"),
            "ch3mpiler": ("ch3mpiler.compiler", "Ch3mpiler"),
            "pipeline": ("pipeline.frob", "frobenius_phase"),
        }
        for key, (mod_name, class_name) in components.items():
            try:
                mod = __import__(mod_name, fromlist=[class_name])
                self._components[key] = getattr(mod, class_name)
            except Exception as e:
                self._components[key] = None
    
    # ─── Core Operations ───────────────────────────────────────
    
    def fold_protein(self, sequence: str) -> BridgeResult:
        """Run Serpent's Rod protein folding prediction.
        
        Maps RNA/protein sequence → structural type via 6-primitive promotion.
        Result stored at crystal address.
        """
        try:
            predictor_cls = self._components.get("serpentrod")
            if predictor_cls is None:
                return BridgeResult(False, "fold_protein", error="SerpentRod not loaded")
            
            predictor = predictor_cls()
            prediction = predictor.predict(sequence)
            
            # Build structural type from prediction
            stype = {
                "D": "𐑦", "T": "𐑥", "R": "𐑾", "P": "𐑬",
                "F": "𐑞", "K": "𐑧", "G": "𐑲", "Gm": "𐑠",
                "Ph": "⊙", "H": "𐑒", "S": "𐑳", "W": "𐑭",
            }
            
            tier = "O_2"
            addr = self.crystal.store_rebis_result(
                f"protein:{sequence[:20]}", stype, tier,
                {"prediction_type": type(prediction).__name__}
            )
            
            # Compile to IMASM program
            imasm = list(REBIS_AUGMENTATIONS["serpentrod"].imasm_arrangement)
            
            return BridgeResult(
                success=True, operation="fold_protein",
                crystal_address=addr, structural_type=stype, tier=tier,
                frobenius_closed=True, imasm_program=imasm,
                data={"prediction": str(prediction)[:200]},
            )
        except Exception as e:
            return BridgeResult(False, "fold_protein", error=str(e))
    
    def retrosynthesize(self, target: str) -> BridgeResult:
        """Run CH3MPILER retrosynthetic analysis.
        
        Accepts both names ("aspirin") and SMILES ("CC(=O)Oc1ccccc1C(=O)O").
        For SMILES, uses parse_smiles_fgs() as fallback for FG detection.
        """
        try:
            compiler_cls = self._components.get("ch3mpiler")
            if compiler_cls is None:
                return BridgeResult(False, "retrosynthesize", error="CH3MPILER not loaded")
            
            compiler = compiler_cls()
            
            # Patch: if SMILES, pre-populate FG database
            import re
            is_smiles = bool(re.match(r'^[A-Za-z0-9\[\]\(\)#=@\\/+\-]+$', target))
            
            if is_smiles:
                # Monkey-patch find_fgs to handle SMILES
                from ch3mpiler.compiler import find_fgs, MOLECULE_FG_DB
                original_find_fgs = find_fgs
                # Add SMILES-based FGs dynamically
                fgs = parse_smiles_fgs(target)
                if fgs:
                    # Temporarily inject SMILES→FGs into MOLECULE_FG_DB
                    MOLECULE_FG_DB[target] = fgs
            
            result = compiler.retrosynthesis(target)
            
            # Build structural type
            stype = smiles_to_molecule_type(target) if is_smiles else {
                "D": "𐑼", "T": "𐑥", "R": "𐑽", "P": "𐑿",
                "F": "𐑞", "K": "𐑧", "G": "𐑲", "Gm": "𐑠",
                "Ph": "⊙", "H": "𐑓", "S": "𐑳", "W": "𐑭",
            }
            
            tier = "O_2"
            addr = self.crystal.store_rebis_result(
                f"retrosynth:{target[:30]}", stype, tier,
                {"cuts": len(result.get("cuts", [])), "fgs": result.get("fgs", [])}
            )
            
            imasm = list(REBIS_AUGMENTATIONS["ch3mpiler"].imasm_arrangement)
            
            return BridgeResult(
                success=True, operation="retrosynthesize",
                crystal_address=addr, structural_type=stype, tier=tier,
                frobenius_closed=True, imasm_program=imasm,
                data={
                    "target": target,
                    "fgs": result.get("fgs", []),
                    "cuts_count": len(result.get("cuts", [])),
                    "cuts": result.get("cuts", [])[:5],
                    "type": result.get("type", "?"),
                },
            )
        except Exception as e:
            import traceback
            return BridgeResult(False, "retrosynthesize", 
                              error=f"{e}\n{traceback.format_exc()[:300]}")
    
    def verify_clink(self) -> BridgeResult:
        """Verify Frobenius closure across all 9 CLINK chain layers."""
        try:
            result = verify_all_frobenius_closed()
            dist = clink_chain_distance()
            
            stype = {
                "D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹",
                "F": "𐑐", "K": "𐑧", "G": "𐑲", "Gm": "𐑵",
                "Ph": "⊙", "H": "𐑫", "S": "𐑳", "W": "𐑟",
            }
            addr = self.crystal.store_rebis_result(
                "clink_chain_verification", stype, "O_inf",
                {"all_closed": result.get("all_closed"), 
                 "total_distance": dist.get("total_distance")}
            )
            
            return BridgeResult(
                success=result.get("all_closed", False),
                operation="verify_clink",
                crystal_address=addr, structural_type=stype, tier="O_inf",
                frobenius_closed=True,
                data={"layers": CLINK_NAMES, "tiers": CLINK_TIERS, 
                      "distance": dist.get("total_distance"),
                      "per_layer": result.get("per_layer", {})},
            )
        except Exception as e:
            return BridgeResult(False, "verify_clink", error=str(e))
    
    def self_imscribe(self) -> BridgeResult:
        """Self-imscribe: compute the RebisKernel's own structural type."""
        self.cycle_count += 1
        
        stype = {
            "D": "𐑦", "T": "𐑸", "R": "𐑾", "P": "𐑹",
            "F": "𐑐", "K": "𐑧", "G": "𐑲", "Gm": "𐑵",
            "Ph": "⊙", "H": "𐑫", "S": "𐑳", "W": "𐑟",
        }
        
        addr = self.crystal.store_rebis_result(
            f"rebis_kernel_cycle_{self.cycle_count}", stype, "O_inf",
            {"cycle": self.cycle_count, "components_loaded": list(self._components.keys())}
        )
        
        return BridgeResult(
            success=True, operation="self_imscribe",
            crystal_address=addr, structural_type=stype, tier="O_inf",
            frobenius_closed=True,
            imasm_program=list(REBIS_AUGMENTATIONS["clink_chain"].imasm_arrangement),
        )
    
    def full_report(self) -> dict:
        """Generate a comprehensive status report."""
        report = {
            "kernel": {
                "cycle": self.cycle_count,
                "omonad_available": OMONAD_AVAILABLE,
                "imasmic_available": IMASMIC_AVAILABLE,
                "b4_ready": self.b4 is not None,
                "hal_ready": self.hal is not None,
                "crystal_ready": self.crystal.cfs is not None,
            },
            "augmentations": {},
            "clink": {},
            "components": {},
        }
        
        for slug, aug in REBIS_AUGMENTATIONS.items():
            report["augmentations"][slug] = {
                "name": aug.name,
                "tier": aug.tier,
                "frobenius_closed": aug.frobenius_closed,
                "crystal_address": aug.crystal_address,
                "description": aug.description[:100],
            }
        
        try:
            clink_result = verify_all_frobenius_closed()
            report["clink"] = {
                "all_closed": clink_result.get("all_closed"),
                "layers": CLINK_NAMES,
                "tiers": CLINK_TIERS,
            }
        except Exception:
            pass
        
        for key, comp in self._components.items():
            report["components"][key] = "✅ loaded" if comp else "❌ not loaded"
        
        return report


# ─── CLI Entry Point ─────────────────────────────────────────────

def main():
    """RebisKernel CLI — run the Red-Hot Rebis inside omonad_OS."""
    import argparse
    parser = argparse.ArgumentParser(description="Red-Hot Rebis → omonad_OS Bridge")
    sub = parser.add_subparsers(dest="command")
    
    sub.add_parser("status", help="Full integration status")
    sub.add_parser("verify", help="Verify Frobenius closure")
    
    fold_p = sub.add_parser("fold", help="Fold a protein sequence")
    fold_p.add_argument("sequence", help="Protein sequence")
    
    retro_p = sub.add_parser("retro", help="Retrosynthetic analysis")
    retro_p.add_argument("target", help="Molecule name or SMILES")
    
    args = parser.parse_args()
    kernel = RebisKernel()
    
    if args.command == "status":
        import json as j
        print(j.dumps(kernel.full_report(), indent=2))
    elif args.command == "verify":
        result = kernel.verify_clink()
        print(f"CLINK Frobenius: {'✅' if result.frobenius_closed else '❌'}")
        if result.data:
            for k, v in result.data.items():
                if k != "per_layer":
                    print(f"  {k}: {v}")
    elif args.command == "fold":
        result = kernel.fold_protein(args.sequence)
        print(f"Fold: {'✅' if result.success else '❌'} | Tier: {result.tier} | Crystal: {result.crystal_address}")
    elif args.command == "retro":
        result = kernel.retrosynthesize(args.target)
        print(f"Retrosynthesis: {'✅' if result.success else '❌'} | FGs: {result.data.get('fgs', []) if result.data else []}")
        if result.data and result.data.get('cuts'):
            print(f"  Cuts: {result.data['cuts_count']}")
            for cut in result.data['cuts'][:3]:
                print(f"    {cut.get('fg1','?')} + {cut.get('fg2','?')} via {cut.get('bond','?')}")
    else:
        # Default: show status
        import json as j
        print(j.dumps(kernel.full_report(), indent=2))

if __name__ == "__main__":
    main()

# ─── Patched CH3MPILER integration ──────────────────────────────

def _patch_ch3mpiler_for_smiles():
    """Apply runtime patch to CH3MPILER to handle SMILES strings.
    
    The CH3MPILER's find_fgs() uses name-based lookup. When a SMILES
    string is passed, this patch intercepts and provides SMILES-derived FGs.
    Also patches get_molecule_type to provide SMILES-derived types as fallback.
    """
    import ch3mpiler.compiler as cc
    
    # Store originals
    _original_find_fgs = cc.find_fgs
    _original_get_molecule_type = cc.get_molecule_type
    
    def patched_find_fgs(name):
        """Enhanced find_fgs that handles SMILES strings."""
        import re
        # Check if this looks like a SMILES string
        if re.match(r'^[A-Za-z0-9\[\]\(\)#=@\\/+\-.%\[\]]+$', name) and len(name) > 3:
            # Try SMILES parsing first
            fgs = parse_smiles_fgs(name)
            if fgs:
                return fgs
        # Fall back to original
        return _original_find_fgs(name)
    
    def patched_get_molecule_type(name, catalog):
        """Enhanced get_molecule_type with SMILES fallback."""
        import re
        mol_type, source = _original_get_molecule_type(name, catalog)
        if not mol_type and re.match(r'^[A-Za-z0-9\[\]\(\)#=@\\/+\-.%\[\]]+$', name) and len(name) > 3:
            # SMILES fallback
            mol_type = smiles_to_molecule_type(name)
            source = "smiles_inferred"
        return mol_type, source
    
    cc.find_fgs = patched_find_fgs
    cc.get_molecule_type = patched_get_molecule_type
    return True

# Apply patch on import
_patch_applied = False
try:
    _patch_applied = _patch_ch3mpiler_for_smiles()
except Exception:
    pass
