"""
pipeline_orchestrator.py — Pipeline Engine for CLINK Whole-Organism Design
===========================================================================

Orchestrates the full CLINK chain walk:
  SYNTHESIS (up): lower_layer → higher_layer
  ANALYSIS (down): higher_layer → lower_layer

Modes:
  GROUND_UP:  L0 → L8, designing every layer from scratch
  FROM_LAYER: Start at any layer with existing design data
  FROM_FILE:  Load saved design and walk from there

Every transition tries to bridge to existing tools first,
then falls back to synthetic designers. Missing tools are
created via the ToolForge.

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import json, os, sys, time, hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

from clink.chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS, PORDER,
    clink_layer_index, clink_layer_tuple,
    clink_frobenius_closed, clink_distance,
    format_tuple_glyphs, primitive_deltas,
    verify_all_frobenius_closed,
)
from clink.designers.designer_base import (
    DesignSpec, TransitionResult, LayerDesigner, ToolForge,
    TRANSITION_TOOLS,
)
from clink.designers.layer_designers import (
    DESIGNER_REGISTRY, get_designer, list_available_bridges,
)


@dataclass
class PipelineResult:
    """Complete result of running the CLINK pipeline."""
    success: bool
    entry_mode: str
    start_layer: int
    target_layer: int
    direction: str
    transitions: List[TransitionResult] = field(default_factory=list)
    final_design: Optional[DesignSpec] = None
    total_promotions: int = 0
    total_distance: float = 0.0
    new_tools_created: List[str] = field(default_factory=list)
    bridges_available: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0


class PipelineEngine:
    """Orchestrates the CLINK design pipeline."""
    
    def __init__(self):
        self.tool_forge = ToolForge()
        self.designers: Dict[int, LayerDesigner] = {}
        self.bridges = list_available_bridges()
        self._init_designers()
    
    def _init_designers(self):
        for idx in sorted(DESIGNER_REGISTRY.keys()):
            try:
                self.designers[idx] = get_designer(idx)
            except Exception as e:
                pass
    
    def ground_up_design(self, **kwargs) -> PipelineResult:
        """Design a whole organism from scratch, starting at L0 (quarks).
        
        Walks through ALL 9 layers, calling each designer's design() method
        in sequence, bridging to available tools at each transition.
        """
        return self.run_pipeline(
            start_layer=0, target_layer=8,
            entry_mode="ground_up", **kwargs
        )
    
    def from_layer_design(self, start_layer: int, **kwargs) -> PipelineResult:
        """Design starting from a specific layer with provided data."""
        return self.run_pipeline(
            start_layer=start_layer, target_layer=8,
            entry_mode="from_layer", **kwargs
        )
    
    def run_pipeline(self, start_layer: int = 0, target_layer: int = 8,
                     entry_mode: str = "ground_up",
                     initial_data: Optional[Dict] = None,
                     **kwargs) -> PipelineResult:
        """Main pipeline runner.
        
        Args:
            start_layer: CLINK layer index to start from (0-8)
            target_layer: CLINK layer index to walk to (0-8)
            entry_mode: "ground_up", "from_layer", or "from_file"
            initial_data: Starting design data dict (for from_layer mode)
            **kwargs: Passed to each designer's design() method
        
        Returns:
            PipelineResult with all transitions
        """
        start_time = time.time()
        
        direction = "synthesis" if target_layer > start_layer else "analysis"
        
        result = PipelineResult(
            success=True,
            entry_mode=entry_mode,
            start_layer=start_layer,
            target_layer=target_layer,
            direction=direction,
            bridges_available=dict(self.bridges),
        )
        
        # Determine layer sequence
        if direction == "synthesis":
            layer_seq = list(range(start_layer, target_layer + 1))
        else:
            layer_seq = list(range(start_layer, target_layer - 1, -1))
        
        # Create initial design spec if starting from ground
        current_spec = None
        if entry_mode == "ground_up" and start_layer == 0:
            try:
                d0 = self.designers[0]
                current_spec = d0.design(None, **kwargs)
            except Exception as e:
                result.errors.append(f"Ground-up start failed at L0: {e}")
                result.success = False
                return result
        elif initial_data:
            # Create spec from provided data
            layer_tup = clink_layer_tuple(start_layer)
            current_spec = DesignSpec(
                layer_idx=start_layer,
                layer_name=CLINK_NAMES[start_layer],
                tuple_glyphs=dict(layer_tup),
                design_data=initial_data,
                frobenius_verified=clink_frobenius_closed(start_layer),
            )
        
        # Walk through layers
        for i in range(len(layer_seq) - 1):
            from_idx = layer_seq[i]
            to_idx = layer_seq[i + 1]
            
            trans = self._transition(current_spec, from_idx, to_idx, **kwargs)
            result.transitions.append(trans)
            
            if trans.success and trans.design:
                current_spec = trans.design
            else:
                result.errors.append(
                    f"Transition L{from_idx}→L{to_idx} failed: {trans.error}"
                )
                if direction == "synthesis":
                    break  # Can't continue upward without this layer
        
        result.final_design = current_spec
        result.total_promotions = sum(
            len(t.promotions) for t in result.transitions
        )
        result.total_distance = round(
            sum(t.distance for t in result.transitions), 4
        )
        result.new_tools_created = list(self.tool_forge.created_tools)
        result.duration_seconds = round(time.time() - start_time, 2)
        
        if result.errors:
            result.success = False
        
        return result
    
    def _transition(self, current_spec: Optional[DesignSpec],
                    from_idx: int, to_idx: int,
                    **kwargs) -> TransitionResult:
        """Execute a single layer transition."""
        from_name = CLINK_NAMES[from_idx]
        to_name = CLINK_NAMES[to_idx]
        from_tier = CLINK_TIERS[from_idx]
        to_tier = CLINK_TIERS[to_idx]
        
        # Compute structural gap
        from_tup = clink_layer_tuple(from_idx)
        to_tup = clink_layer_tuple(to_idx)
        dist = clink_distance(from_idx, to_idx)
        deltas = primitive_deltas(from_idx, to_idx)
        
        trans = TransitionResult(
            from_layer=from_idx, to_layer=to_idx,
            from_name=from_name, to_name=to_name,
            from_tier=from_tier, to_tier=to_tier,
            success=False, distance=round(dist, 4),
            promotions=deltas,
        )
        
        # Try to use the target layer's designer
        designer = self.designers.get(to_idx)
        if designer is None:
            # Try to forge one
            tool_path = self.tool_forge.forge_transition(from_idx, to_idx)
            if tool_path:
                trans.new_tools_created.append(tool_path)
                try:
                    designer = get_designer(to_idx)
                    self.designers[to_idx] = designer
                except Exception:
                    pass
        
        if designer is None:
            trans.error = f"No designer available for layer {to_idx}"
            return trans
        
        # Call the designer
        try:
            new_spec = designer.design(current_spec, **kwargs)
            trans.success = True
            trans.design = new_spec
            trans.tool_used = designer.__class__.__name__
            
            # Check Frobenius closure
            if not new_spec.frobenius_verified:
                new_spec.frobenius_verified = clink_frobenius_closed(to_idx)
            
        except Exception as e:
            trans.error = f"Design failed: {e}"
        
        return trans
    
    def generate_report(self, result: PipelineResult) -> str:
        """Generate a human-readable report from pipeline results."""
        lines = []
        lines.append("=" * 65)
        lines.append("CLINK PIPELINE — WHOLE ORGANISM DESIGN REPORT")
        lines.append("=" * 65)
        lines.append(f"Entry mode: {result.entry_mode}")
        lines.append(f"Direction:  {result.direction}")
        lines.append(f"Path:       L{result.start_layer} → L{result.target_layer}")
        lines.append(f"Duration:   {result.duration_seconds}s")
        lines.append(f"Status:     {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        lines.append("")
        
        # Available bridges
        lines.append("Available Bridges:")
        for name, avail in result.bridges_available.items():
            lines.append(f"  {'✅' if avail else '❌'} {name}")
        lines.append("")
        
        # Transitions
        lines.append("Layer Transitions:")
        lines.append(f"  {'From':25s} → {'To':25s} {'d':>6s} {'P':>3s} {'Tool':20s}")
        lines.append("-" * 85)
        
        for t in result.transitions:
            tool_short = t.tool_used[:20] if t.tool_used else "—"
            status = "✅" if t.success else "❌"
            lines.append(f"  {t.from_name:25s} → {t.to_name:25s} "
                         f"{t.distance:>5.2f} {len(t.promotions):>3d} "
                         f"{tool_short:20s} {status}")
        
        lines.append("")
        lines.append(f"Total distance:      {result.total_distance}")
        lines.append(f"Total promotions:    {result.total_promotions}")
        lines.append(f"New tools created:   {len(result.new_tools_created)}")
        
        if result.final_design:
            lines.append("")
            lines.append("Final Design:")
            layer = result.final_design
            lines.append(f"  Layer:  {layer.layer_name} (L{layer.layer_idx})")
            lines.append(f"  Tuple:  {format_tuple_glyphs(layer.tuple_glyphs)}")
            lines.append(f"  Tier:   {CLINK_TIERS[layer.layer_idx]}")
            lines.append(f"  Frobenius: {'✅' if layer.frobenius_verified else '❌'}")
        
        if result.errors:
            lines.append("")
            lines.append("Errors:")
            for e in result.errors:
                lines.append(f"  ❌ {e}")
        
        if result.new_tools_created:
            lines.append("")
            lines.append("New Tools Created:")
            for t in result.new_tools_created:
                lines.append(f"  🔨 {t}")
        
        lines.append("=" * 65)
        return "\n".join(lines)
    
    def export_design_json(self, result: PipelineResult, path: str) -> bool:
        """Export the pipeline design to a JSON file for reload."""
        if not result.final_design:
            return False
        
        export = {
            "clink_pipeline": {
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "entry_mode": result.entry_mode,
                "start_layer": result.start_layer,
                "target_layer": result.target_layer,
                "total_distance": result.total_distance,
                "total_promotions": result.total_promotions,
                "success": result.success,
            },
            "final_design": {
                "layer_idx": result.final_design.layer_idx,
                "layer_name": result.final_design.layer_name,
                "tuple_glyphs": result.final_design.tuple_glyphs,
                "design_data": result.final_design.design_data,
                "frobenius_verified": result.final_design.frobenius_verified,
            },
            "transitions": [
                {
                    "from": t.from_layer,
                    "to": t.to_layer,
                    "distance": t.distance,
                    "promotions": len(t.promotions),
                    "success": t.success,
                    "tool": t.tool_used,
                }
                for t in result.transitions
            ],
            "bridges_available": result.bridges_available,
            "new_tools": result.new_tools_created,
        }
        
        try:
            with open(path, 'w') as f:
                json.dump(export, f, indent=2)
            return True
        except Exception:
            return False
    
    def load_design_json(self, path: str) -> Optional[DesignSpec]:
        """Load a design from JSON file."""
        try:
            with open(path) as f:
                data = json.load(f)
            fd = data["final_design"]
            return DesignSpec(
                layer_idx=fd["layer_idx"],
                layer_name=fd["layer_name"],
                tuple_glyphs=fd["tuple_glyphs"],
                design_data=fd["design_data"],
                frobenius_verified=fd["frobenius_verified"],
            )
        except Exception as e:
            return None
