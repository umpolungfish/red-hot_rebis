"""
designer_base.py — Base classes for CLINK Layer Designers & ToolForge

LayerDesigner: abstract base for all 9 layer-specific designers
ToolForge: creates new transition tools for missing steps via ob3ect

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import json, os, sys, importlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

from shared.primitives import ORDINALS, WEIGHTS, to_vector, tuple_distance
from clink.chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS, PORDER,
    clink_layer_index, clink_layer_tuple,
    clink_frobenius_closed, clink_distance,
    format_tuple_glyphs, primitive_deltas,
    verify_all_frobenius_closed,
)


@dataclass
class DesignSpec:
    """A design specification at a given CLINK layer."""
    layer_idx: int
    layer_name: str
    tuple_glyphs: Dict[str, str]
    design_data: Dict[str, Any]
    frobenius_verified: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    parent_spec: Optional[str] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class TransitionResult:
    """Result of transitioning between CLINK layers."""
    from_layer: int
    to_layer: int
    from_name: str
    to_name: str
    from_tier: str
    to_tier: str
    success: bool
    design: Optional[DesignSpec] = None
    promotions: List[Dict] = field(default_factory=list)
    distance: float = 0.0
    tool_used: str = ""
    error: Optional[str] = None
    new_tools_created: List[str] = field(default_factory=list)


TRANSITION_TOOLS = {
    (0, 1): {"quantum_field": "QCD → orbital: hadronization & electron capture"},
    (1, 2): {"nuclear_physics": "Electron config → atom: nuclear shell model + shielding"},
    (2, 3): {"chemistry": "Atoms → molecules: valence bond theory → ch3mpiler"},
    (3, 4): {"protein_folding": "Molecules → proteins: amino acid sequence → serpentrod"},
    (4, 5): {"cell_assembly": "Proteins → cell: metabolism, gene regulation → gene_imscriber"},
    (5, 6): {"cell_division": "Cell → mitosis: spindle, kinetochore, Aurora-B checkpoint"},
    (6, 7): {"tissue_morphogenesis": "Mitosis → tissue: differentiation, ECM, cell-cell junctions"},
    (7, 8): {"organism_integration": "Tissues → organism: organ systems, homeostasis, neuroendocrine"},
}


class LayerDesigner:
    """Base class for CLINK layer designers."""
    
    layer_idx: int = -1
    
    def __init__(self):
        self.clink_tuple = clink_layer_tuple(self.layer_idx, include_meta=False)
        self.clink_meta = clink_layer_tuple(self.layer_idx, include_meta=True)
    
    def design(self, lower_spec: DesignSpec, **kwargs) -> DesignSpec:
        raise NotImplementedError(f"Designer L{self.layer_idx} must implement design()")
    
    def analyze(self, upper_spec: DesignSpec, **kwargs) -> DesignSpec:
        raise NotImplementedError(f"Designer L{self.layer_idx} must implement analyze()")
    
    def verify_frobenius(self, design_data: Dict) -> bool:
        if "tuple" in design_data:
            return clink_frobenius_closed(design_data["tuple"])
        return clink_frobenius_closed(self.layer_idx)
    
    def compute_promotions(self, from_tuple: Dict, to_tuple: Optional[Dict] = None) -> List[Dict]:
        target = to_tuple or self.clink_tuple
        return [{"primitive": p, "from": from_tuple.get(p, "?"), "to": target.get(p, "?")}
                for p in PORDER if from_tuple.get(p) != target.get(p)]


class ToolForge:
    """Creates new design tools for layer transitions where none exists."""
    
    def __init__(self):
        self.created_tools: List[str] = []
    
    def forge_transition(self, from_layer: int, to_layer: int) -> Optional[str]:
        key = (from_layer, to_layer)
        if key not in TRANSITION_TOOLS:
            return None
        
        description = list(TRANSITION_TOOLS[key].values())[0]
        
        # Check if designer exists
        try:
            mod = importlib.import_module("clink.designers.layer_designers")
            designer_name = f"Layer{to_layer}Designer"
            if hasattr(mod, designer_name):
                return f"clink.designers.layer_designers.{designer_name}"
        except (ImportError, AttributeError):
            pass
        
        # Generate synthetic designer
        out_dir = Path(__file__).parent / "generated"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        from_tup = clink_layer_tuple(from_layer)
        to_tup = clink_layer_tuple(to_layer)
        deltas = [p for p in PORDER if from_tup[p] != to_tup[p]]
        
        safe_name = f"transition_{from_layer}_to_{to_layer}"
        module_path = out_dir / f"{safe_name}.py"
        
        deltas_code = "\n".join(
            f'    "{p}": {{"from": "{from_tup[p]}", "to": "{to_tup[p]}"}}'
            for p in deltas
        )
        
        code = f'''"""
{safe_name}.py — Auto-generated transition tool
{description}

Primitive promotions:
{deltas_code}
Generated by CLINK ToolForge
"""
from typing import Dict, List, Any

PORDER = {PORDER!r}

TRANSITION_MAP = {{
{deltas_code}
}}

def compute_promotions(source_tuple: Dict[str, str]) -> List[Dict]:
    return [{{"primitive": p, "from": source_tuple.get(p,"?"), "to": TRANSITION_MAP[p]["to"]}}
            for p in TRANSITION_MAP]

def bridge_structural(source_tuple: Dict[str, str],
                      target_tuple: Dict[str, str]) -> Dict:
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
