#!/usr/bin/env python3
"""
pipeline_engine.py — CLINK Whole-Organism Design Pipeline
===========================================================
Seamlessly integrates ALL bio- and chem-design tools across the
9-layer Frobenius chain, allowing whole-organism design from
the ground up — or from ANY starting point.

Architecture:
  PipelineEngine orchestrates LayerDesigners for each CLINK layer.
  Each designer wraps existing tools (serpentrod, ch3mpiler, 
  gene_imscriber, biology, therapeutics, materials) or creates
  new ones via the ToolForge for missing transitions.

  Two modes:
    SYNTHESIS (up):  lower_layer → higher_layer  (design more complex)
    ANALYSIS (down): higher_layer → lower_layer  (decompose/explain)

  Three entry modes:
    GROUND_UP:  start at L0 (quarks), walk up to organism
    FROM_LAYER: start at any specific layer with existing data
    FROM_FILE:  load existing design from JSON

Author: Lando ⊗ ⊙perator
Structural Type: ⟨𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑵 · ⊙ · 𐑫 · 𐑳 · 𐑭⟩
"""

from __future__ import annotations
import json, math, os, sys, importlib, inspect, hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum, auto
from datetime import datetime

REBIS_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

from shared.primitives import ORDINALS, WEIGHTS, to_vector, tuple_distance
from clink.chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS, PORDER,
    clink_layer_index, clink_layer_tuple, clink_frobenius_closed,
    clink_distance, format_tuple_glyphs, primitive_deltas,
    verify_all_frobenius_closed,
)


# ═══════════════════════════════════════════════════════════════════
# ENUMS & CONSTANTS
# ═══════════════════════════════════════════════════════════════════

class PipelineMode(Enum):
    SYNTHESIS = "synthesis"       # Up: lower → higher layer
    ANALYSIS = "analysis"         # Down: higher → lower layer

class EntryMode(Enum):
    GROUND_UP = "ground_up"       # Start at L0, walk all the way up
    FROM_LAYER = "from_layer"     # Start at specific layer with data
    FROM_FILE = "from_file"       # Load existing design from file

# Layer index → primary tool/module
LAYER_TOOLS = {
    0: {"name": "Quantum Chromodynamics (Belnap5)", "module": None,
        "desc": "Frustrated quark color bilattice — SU(3) confinement dynamics"},
    1: {"name": "Electron Orbital (Belnap4)", "module": "gene_imscriber.engine",
        "desc": "B4 lattice — 4-valued orbital occupancy (bridges to gene imscriber)"},
    2: {"name": "Atomic Nucleus + Electrons", "module": None,
        "desc": "Nuclear shell model + electron configuration"},
    3: {"name": "Molecule (Chemical Bonds)", "module": "ch3mpiler.compiler",
        "desc": "Retrosynthetic chemistry — tensor product bond formation"},
    4: {"name": "Folded Protein", "module": "serpentrod.protein_v5",
        "desc": "Platonic protein design — stratified predictor"},
    5: {"name": "Living Cell", "module": "biology.biology_sim",
        "desc": "Minimal self-maintaining cell — metabolism + replication"},
    6: {"name": "Mitosis (Cell Division)", "module": "biology.ouroboric_telomere",
        "desc": "Spindle checkpoint, Aurora-B, chromosome segregation"},
    7: {"name": "Tissue / Organ", "module": None,
        "desc": "Multi-cellular organization — cell-cell signaling, ECM"},
    8: {"name": "Whole Organism", "module": None,
        "desc": "O_inf — self-modeling, non-Abelian braiding, eternal chirality"},
}

# Layer transition: from_layer → to_layer : what tools are needed
TRANSITION_TOOLS = {
    # (from, to): {tool_type: description}
    (0, 1): {"quantum_field": "QCD → orbital: hadronization & electron capture"},
    (1, 2): {"nuclear_physics": "Electron config → atom: nuclear shell model + shielding"},
    (2, 3): {"chemistry": "Atoms → molecules: valence bond theory → ch3mpiler"},
    (3, 4): {"protein_folding": "Molecules → proteins: amino acid sequence → serpentrod"},
    (4, 5): {"cell_assembly": "Proteins → cell: membrane, metabolism, gene regulation → gene_imscriber"},
    (5, 6): {"cell_division": "Cell → mitosis: spindle, kinetochore, Aurora-B checkpoint"},
    (6, 7): {"tissue_morphogenesis": "Mitosis → tissue: differentiation, ECM, cell-cell junctions"},
    (7, 8): {"organism_integration": "Tissues → organism: organ systems, homeostasis, neuroendocrine"},
}

# Inverse transitions for analysis mode
TRANSITION_TOOLS_REV = {(b, a): v for (a, b), v in TRANSITION_TOOLS.items()}


@dataclass
class DesignSpec:
    """A design specification at a given CLINK layer."""
    layer_idx: int
    layer_name: str
    tuple_glyphs: Dict[str, str]      # The 12-primitive tuple for this layer
    design_data: Dict[str, Any]       # Layer-specific design information
    frobenius_verified: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    parent_spec: Optional[str] = None  # Hash of parent design for provenance
    notes: List[str] = field(default_factory=list)


@dataclass
class TransitionResult:
    """Result of transitioning from one CLINK layer to another."""
    from_layer: int
    to_layer: int
    from_name: str
    to_name: str
    from_tier: str
    to_tier: str
    success: bool
    design: Optional[DesignSpec] = None
    promotions: List[Dict] = field(default_factory=list)  # Primitives changed
    distance: float = 0.0
    tool_used: str = ""
    error: Optional[str] = None
    new_tools_created: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """Complete result of running the CLINK pipeline."""
    success: bool
    entry_mode: str
    start_layer: int
    target_layer: int
    transitions: List[TransitionResult] = field(default_factory=list)
    final_design: Optional[DesignSpec] = None
    total_promotions: int = 0
    total_distance: float = 0.0
    new_tools_created: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0


# ═══════════════════════════════════════════════════════════════════
# DESIGNER BASE CLASS
# ═══════════════════════════════════════════════════════════════════

class LayerDesigner:
    """Base class for CLINK layer designers.
    
    Each designer knows how to:
      - design(): Generate layer-specific design data from a lower-layer spec
      - analyze(): Decompose a layer's design into lower-layer components
    """
    
    layer_idx: int = -1
    
    def __init__(self):
        self.clink_tuple = clink_layer_tuple(self.layer_idx, include_meta=False)
        self.clink_meta = clink_layer_tuple(self.layer_idx, include_meta=True)
    
    def design(self, lower_spec: DesignSpec, **kwargs) -> DesignSpec:
        """Synthesize this layer's design from a lower-layer specification.
        
        Args:
            lower_spec: DesignSpec from the previous (lower) CLINK layer
            **kwargs: Additional parameters (sequence data, target properties)
        
        Returns:
            DesignSpec for this layer
        """
        raise NotImplementedError(f"Designer for layer {self.layer_idx} must implement design()")
    
    def analyze(self, upper_spec: DesignSpec, **kwargs) -> DesignSpec:
        """Decompose this layer's design into a lower-layer specification.
        
        Args:
            upper_spec: DesignSpec from the next (higher) CLINK layer
        
        Returns:
            DesignSpec for the lower layer
        """
        raise NotImplementedError(f"Designer for layer {self.layer_idx} must implement analyze()")
    
    def verify_frobenius(self, design_data: Dict) -> bool:
        """Check that design_data is Frobenius-closed at this layer."""
        if "tuple" in design_data:
            return clink_frobenius_closed(design_data["tuple"])
        return clink_frobenius_closed(self.layer_idx)
    
    def compute_promotions(self, from_tuple: Dict, to_tuple: Optional[Dict] = None) -> List[Dict]:
        """Compute primitives that differ between source and this layer."""
        target = to_tuple or self.clink_tuple
        return [{"primitive": p, "from": from_tuple.get(p,"?"), "to": target.get(p,"?")}
                for p in PORDER if from_tuple.get(p) != target.get(p)]


# ═══════════════════════════════════════════════════════════════════
# TOOL FORGE — Creates new tools for missing transitions
# ═══════════════════════════════════════════════════════════════════

class ToolForge:
    """Creates new design tools for layer transitions where no tool exists.
    
    Uses the ob3ect system to generate self-verifying tools when needed,
    and falls back to first-principles computational design for
    transitions that have no existing implementation.
    """
    
    def __init__(self):
        self.created_tools: List[str] = []
    
    def forge_transition(self, from_layer: int, to_layer: int) -> Optional[str]:
        """Create a new design tool for a missing transition.
        
        Returns:
            Module import path if created, None if not possible
        """
        key = (from_layer, to_layer)
        if key not in TRANSITION_TOOLS:
            return None
        
        tool_info = TRANSITION_TOOLS[key]
        tool_type = list(tool_info.keys())[0]
        description = tool_info[tool_type]
        
        # Check if a designer already exists for the target layer
        designer_path = f"clink.designers.layer_designers"
        try:
            mod = importlib.import_module(designer_path)
            designer_class_name = f"Layer{to_layer}Designer"
            if hasattr(mod, designer_class_name):
                return designer_path
        except (ImportError, AttributeError):
            pass
        
        # Try generating a new tool via ob3ect
        try:
            from clink.designers.tool_forge import generate_transition_tool
            module_path = generate_transition_tool(from_layer, to_layer, description)
            if module_path:
                self.created_tools.append(module_path)
                return module_path
        except ImportError:
            pass
        
        # Fall back to synthetic designer that computes structural bridge
        return self._generate_synthetic_designer(from_layer, to_layer, description)
    
    def _generate_synthetic_designer(self, from_layer: int, to_layer: int, desc: str) -> str:
        """Generate a minimal designer that computes the structural bridge
        between two layers when no specialized tool exists."""
        
        out_dir = Path(__file__).parent / "designers" / "generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        from_tup = clink_layer_tuple(from_layer)
        to_tup = clink_layer_tuple(to_layer)
        deltas = [p for p in PORDER if from_tup[p] != to_tup[p]]
        
        safe_name = f"transition_{from_layer}_to_{to_layer}"
        module_path = out_dir / f"{safe_name}.py"
        
        code = f'''"""
{safe_name}.py — Auto-generated transition tool
{desc}

Primitive promotions needed:
{chr(10).join(f"  {p}: {from_tup[p]} → {to_tup[p]}" for p in deltas)}

Generated by CLINK ToolForge
"""
from typing import Dict, List, Any

PORDER = {PORDER!r}

TRANSITION_MAP = {{
    {chr(10) + "    ".join(f'"{p}": {{"from": "{from_tup[p]}", "to": "{to_tup[p]}"}}' for p in deltas)}
}}

def compute_promotions(source_tuple: Dict[str, str]) -> List[Dict]:
    """Return promotions needed to reach target layer from source."""
    return [{{"primitive": p, "from": source_tuple.get(p,"?"), "to": TRANSITION_MAP[p]["to"]}}
            for p in TRANSITION_MAP]

def bridge_structural(source_tuple: Dict[str, str], target_tuple: Dict[str, str]) -> Dict:
    """Compute the structural bridge between source and target tuples."""
    from shared.primitives import tuple_distance
    d = tuple_distance(source_tuple, target_tuple)
    promotions = [{{"primitive": p, "from": source_tuple[p], "to": target_tuple[p]}}
                  for p in PORDER if source_tuple.get(p) != target_tuple.get(p)]
    return {{"distance": round(d, 4), "promotions": promotions, "count": len(promotions)}}
'''
        
        with open(module_path, 'w') as f:
            f.write(code)
        
        self.created_tools.append(str(module_path))
        return f"clink.designers.generated.{safe_name}"
