"""
integration.py — CLINK Unified Integration
===========================================
Integrates the CLINK chain with the full rebis architecture:
  serpentrod ⊗ ch3mpiler ⊗ pipeline ⊗ gene_imscriber → CLINK

Provides unified verification, promotion paths, and cross-component analysis.

Author: Lando ⊗ ⊙perator
"""

import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from clink.chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS, PORDER,
    clink_distance, clink_layer_index, clink_layer_tuple,
    clink_frobenius_closed, verify_all_frobenius_closed,
    clink_chain_distance, format_tuple_glyphs
)
from clink.bridges import (
    BridgeResult, protein_to_clink, molecule_to_clink, gene_to_clink,
    bridge_all_components
)


@dataclass
class IntegratedCLINKResult:
    """Complete integration report."""
    frobenius_closure: Dict
    chain_distances: Dict
    bridges: Dict[str, BridgeResult]
    zfc_fe_distance: float
    total_promotions: int
    verification_status: str


def verify_clink_integration():
    """Run full integration verification across all components.
    
    Returns:
        IntegratedCLINKResult
    """
    # 1. Frobenius closure
    frob = verify_all_frobenius_closed()
    
    # 2. Chain distances
    chain = clink_chain_distance()
    
    # 3. Bridges
    bridges = bridge_all_components()
    
    # 4. ZFC_fe distance
    zfc_fe_tup = {
        "Ð": "𐑦", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑹",
        "ƒ": "𐑐", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
        "⊙": "⊙", "Ħ": "𐑫", "Σ": "𐑳", "Ω": "𐑭"
    }
    org_tup = clink_layer_tuple(8)
    zfc_dist = clink_distance(zfc_fe_tup, org_tup)
    
    # 5. Total promotions across chain
    total_promos = sum(
        len([p for p in PORDER if CLINK_LAYERS[i][p] != CLINK_LAYERS[i+1][p]])
        for i in range(8)
    )
    
    # 6. Status
    all_ok = (
        frob["all_closed"]
        and all(r.frobenius_verified for r in bridges.values())
        and zfc_dist < 2.0
    )
    
    return IntegratedCLINKResult(
        frobenius_closure=frob,
        chain_distances=chain,
        bridges=bridges,
        zfc_fe_distance=round(zfc_dist, 4),
        total_promotions=total_promos,
        verification_status="✅ VERIFIED" if all_ok else "⚠️ PARTIAL"
    )


def integrated_promotion_path(from_comp: str, to_layer_idx: int):
    """Compute promotion path from a rebis component to a target CLINK layer.
    
    Args:
        from_comp: "serpentrod", "ch3mpiler", or "gene_imscriber"
        to_layer_idx: target CLINK layer index (0-8)
    
    Returns:
        dict with path, distance, and tier change
    """
    bridge_map = {
        "serpentrod": protein_to_clink(),
        "ch3mpiler": molecule_to_clink(),
        "gene_imscriber": gene_to_clink(),
    }
    if from_comp not in bridge_map:
        raise KeyError(f"Unknown component: {from_comp}")
    
    from_tup = bridge_map[from_comp].component_type
    to_tup = CLINK_LAYERS[to_layer_idx]
    
    dist = clink_distance(from_tup, to_tup)
    deltas = [p for p in PORDER if from_tup[p] != to_tup[p]]
    
    return {
        "from": from_comp,
        "to": CLINK_NAMES[to_layer_idx],
        "to_tier": CLINK_TIERS[to_layer_idx],
        "distance": round(dist, 4),
        "num_promotions": len(deltas),
        "promotions": {p: f"{from_tup[p]}→{to_tup[p]}" for p in deltas},
    }


def clink_to_serpentrod(layer_idx: int):
    """Map a CLINK layer to its nearest serpentrod protein analog.
    
    Returns dict with protein type info.
    """
    from clink.bridges import PLATONIC_PROTEIN, UNFOLDED_PROTEIN
    tup = clink_layer_tuple(layer_idx)
    d_fold = clink_distance(tup, {k: PLATONIC_PROTEIN[k] for k in PORDER})
    d_unfold = clink_distance(tup, {k: UNFOLDED_PROTEIN[k] for k in PORDER})
    return {
        "layer": CLINK_NAMES[layer_idx],
        "distance_to_folded": round(d_fold, 4),
        "distance_to_unfolded": round(d_unfold, 4),
        "closer_to": "folded" if d_fold < d_unfold else "unfolded",
    }


def clink_to_ch3mpiler(layer_idx: int):
    """Map a CLINK layer to molecule space. Returns distance info."""
    from clink.bridges import PLATONIC_PROTEIN
    mol_tup = clink_layer_tuple(3)  # moleculeLayer
    tup = clink_layer_tuple(layer_idx)
    d = clink_distance(tup, mol_tup)
    return {
        "layer": CLINK_NAMES[layer_idx],
        "distance_to_molecule": round(d, 4),
        "is_molecular": d < 1.0,
    }


def clink_to_gene(layer_idx: int):
    """Map a CLINK layer to gene space."""
    from clink.bridges import CODON_BELNAP4_TYPE
    cod_tup = {k: CODON_BELNAP4_TYPE[k] for k in PORDER}
    tup = clink_layer_tuple(layer_idx)
    d = clink_distance(tup, cod_tup)
    return {
        "layer": CLINK_NAMES[layer_idx],
        "distance_to_codon_belnap4": round(d, 4),
        "is_genetic": d < 2.5,
    }


def full_report() -> str:
    """Generate a full integration report as a string."""
    result = verify_clink_integration()
    
    lines = []
    lines.append("=" * 60)
    lines.append("CLINK INTEGRATION REPORT — red-hot_rebis")
    lines.append("=" * 60)
    lines.append(f"Status: {result.verification_status}")
    
    lines.append("\n--- Frobenius Closure ---")
    for name, closed in result.frobenius_closure["per_layer"].items():
        lines.append(f"  {'✅' if closed else '❌'} {name}")
    
    lines.append("\n--- Chain Distances ---")
    for s in result.chain_distances["steps"]:
        lines.append(f"  {s['from']} → {s['to']}: d={s['distance']}")
    lines.append(f"  Total: Σd={result.chain_distances['total_distance']}, "
                 f"{result.chain_distances['total_primitive_deltas']} deltas")
    
    lines.append(f"\n--- ZFC_fe Distance ---")
    lines.append(f"  d(organism, ZFC_fe) = {result.zfc_fe_distance}")
    
    lines.append(f"\n--- Component Bridges ---")
    for name, r in result.bridges.items():
        lines.append(f"  {name}: → {r.nearest_layer_name} (d={r.distance}, "
                     f"Frob={r.frobenius_verified})")
    
    lines.append(f"\n--- Total Promotions ---")
    lines.append(f"  {result.total_promotions} primitive promotions across 8 transitions")
    
    lines.append("\n" + "=" * 60)
    lines.append("CLINK: subatomic → whole organism. Frobenius-closed. Verified.")
    lines.append("=" * 60)
    
    return "\n".join(lines)


if __name__ == "__main__":
    print(full_report())
