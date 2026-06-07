"""
tool_forge.py — Tool creation for missing CLINK transitions
Creates new ob3ects and transition tools for layer gaps.

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import os, sys, json
from pathlib import Path
from typing import Dict, List, Optional, Any

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

from clink.chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS, PORDER,
    clink_layer_tuple, clink_frobenius_closed, clink_distance,
    format_tuple_glyphs, primitive_deltas,
)


def generate_transition_tool(from_layer: int, to_layer: int,
                              description: str) -> Optional[str]:
    """Generate a transition tool via the ob3ect system.
    
    Creates a self-verifying ob3ect that bridges two CLINK layers.
    
    Returns:
        Module path string, or None if generation fails.
    """
    from_tup = clink_layer_tuple(from_layer)
    to_tup = clink_layer_tuple(to_layer)
    deltas = [p for p in PORDER if from_tup[p] != to_tup[p]]
    
    delta_str = "; ".join(f"{p}:{from_tup[p]}->{to_tup[p]}" for p in deltas)
    
    # Try using the ob3ect system
    try:
        from ob3ect import auto
        ob3ect_desc = (
            f"CLINK transition tool: {CLINK_NAMES[from_layer]} → "
            f"{CLINK_NAMES[to_layer]}. "
            f"Primitive promotions: {delta_str}. "
            f"Structural distance: d={clink_distance(from_layer, to_layer):.2f}. "
            f"Frobenius closure required."
        )
        result = auto.generate_ob3ect(
            description=ob3ect_desc,
            domain="computational",
            run=True
        )
        # ob3ect/auto generates and places the file
        return "ob3ect.digital." + result.get("slug", f"clink_tool_{from_layer}_{to_layer}")
    except Exception as e:
        pass
    
    # Fallback: generate the synthetic tool ourselves
    out_dir = Path(__file__).parent / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = f"clink_transition_{from_layer}_to_{to_layer}"
    module_path = out_dir / f"{safe_name}.py"
    
    deltas_code = "\n".join(
        f'    "{p}": {{"from": "{from_tup[p]}", "to": "{to_tup[p]}"}}'
        for p in deltas
    )
    
    code = f'''\"\"\"
{safe_name}.py — CLINK Transition Tool (auto-generated)
{description}

From: {CLINK_NAMES[from_layer]} (L{from_layer})
To:   {CLINK_NAMES[to_layer]} (L{to_layer})
Tier: {CLINK_TIERS[from_layer]} → {CLINK_TIERS[to_layer]}

Primitive promotions:
{deltas_code}

Structural distance: d={clink_distance(from_layer, to_layer):.4f}
\"\"\"

from typing import Dict, List, Any

PORDER = {PORDER!r}

TRANSITION_MAP = {{
{deltas_code}
}}

FROM_TUPLE = {from_tup!r}
TO_TUPLE = {to_tup!r}


def compute_promotions(source_tuple: Dict[str, str]) -> List[Dict]:
    \"\"\"Return promotions needed to reach target layer from source.\"\"\"
    return [{{"primitive": p, "from": source_tuple.get(p, "?"), "to": TRANSITION_MAP[p]["to"]}}
            for p in TRANSITION_MAP]


def bridge(source_tuple: Dict[str, str],
           target_tuple: Dict[str, str]) -> Dict:
    \"\"\"Compute structural bridge between two tuples.\"\"\"
    from shared.primitives import tuple_distance
    d = tuple_distance(source_tuple, target_tuple)
    promotions = [{{"primitive": p, "from": source_tuple[p], "to": target_tuple[p]}}
                  for p in PORDER if source_tuple.get(p) != target_tuple.get(p)]
    return {{
        "distance": round(d, 4),
        "promotions": promotions,
        "count": len(promotions),
        "frobenius_closed": all(
            source_tuple.get(p) == target_tuple.get(p)
            for p in PORDER if source_tuple.get(p) != target_tuple.get(p)
        ) if False else False,
    }}
'''
    
    with open(module_path, 'w') as f:
        f.write(code)
    
    return str(module_path.relative_to(REBIS_ROOT))
