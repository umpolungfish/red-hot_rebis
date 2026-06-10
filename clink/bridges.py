"""
bridges.py — CLINK Bridges to Rebis Pillars
============================================
Maps between CLINK layers and the three primary rebis components:
  serpentrod   — platonic proteins bridge to moleculeLayer (L3) / cellLayer (L4)
  ch3mpiler    — retrosynthetic compiler bridge to moleculeLayer (L3)
  gene_imscriber — codon editing bridge to electronOrbitalLayer (L1)

Each bridge takes a component's output type and returns the nearest CLINK
layer(s), promotion path, and Frobenius verification status.

Author: Lando ⊗ ⊙perator
"""

from dataclasses import dataclass, field
from typing import List, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from clink.chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS, PORDER,
    clink_distance, clink_layer_index, clink_frobenius_closed,
    format_tuple_glyphs
)


@dataclass
class BridgeResult:
    """Result of bridging a component type to the CLINK chain."""
    component: str              # e.g., "serpentrod", "ch3mpiler", "gene_imscriber"
    component_type: dict        # The 12-primitive tuple from the component
    nearest_layer_idx: int      # Index of nearest CLINK layer (0-8)
    nearest_layer_name: str     # Name of nearest CLINK layer
    distance: float             # Distance to nearest layer
    promotion_path: List[str]   # Primitives needing promotion
    frobenius_verified: bool    # Whether component is Frobenius-closed
    notes: str = ""             # Additional commentary


# ═══════════════════════════════════════════════════════════════════
# SERPENTROD BRIDGE — Protein layer ↔ moleculeLayer / cellLayer
# ═══════════════════════════════════════════════════════════════════
# 
# SerpentRod produces "platonic protein" tuples — the structural type
# of a folded protein. These sit between moleculeLayer (L3) and 
# cellLayer (L4) because proteins are:
#   - Molecular: chemical bonds, thermal fidelity, catalysis (L3)
#   - Pre-cellular: self-organization, folding topology, allostery (L4)
#
# The protein's tuple is derived from its amino acid sequence via
# the stratified_predictor's PRIMITIVE_MAP.

# Canonical structural type for a folded protein (platonic protein)
PLATONIC_PROTEIN = {
    "Ð": "𐑦", "Þ": "𐑥", "Ř": "𐑾", "Φ": "𐑬",
    "ƒ": "𐑞", "Ç": "𐑧", "Γ": "𐑲", "ɢ": "𐑠",
    "⊙": "⊙", "Ħ": "𐑒", "Σ": "𐑳", "Ω": "𐑭",
    "_name": "platonicProtein",
    "_desc": "Folded protein — between molecule and cell",
    "_tier": "O₂",
}

# Canonical structural type for unfolded/random coil protein
UNFOLDED_PROTEIN = {
    "Ð": "𐑼", "Þ": "𐑡", "Ř": "𐑑", "Φ": "𐑿",
    "ƒ": "𐑱", "Ç": "𐑤", "Γ": "𐑔", "ɢ": "𐑜",
    "⊙": "𐑢", "Ħ": "𐑓", "Σ": "𐑕", "Ω": "𐑷",
    "_name": "unfoldedProtein",
    "_desc": "Unfolded/random coil protein chain",
    "_tier": "O₀",
}

def protein_to_clink(protein_tuple=None):
    """Bridge a serpentrod protein type to the nearest CLINK layer.
    
    Args:
        protein_tuple: dict with 12 primitives (keys in PORDER or ch3mpiler style).
                       If None, uses the canonical PLATONIC_PROTEIN.
    
    Returns:
        BridgeResult
    """
    if protein_tuple is None:
        tup = {k: PLATONIC_PROTEIN[k] for k in PORDER}
    else:
        # Normalize to PORDER keys if needed
        ch3_to_porder = {"D":"Ð","T":"Þ","R":"Ř","P":"Φ","F":"ƒ",
                         "K":"Ç","G":"Γ","Gm":"ɢ","Ph":"⊙","H":"Ħ","S":"Σ","W":"Ω"}
        if all(k in ch3_to_porder for k in protein_tuple):
            tup = {ch3_to_porder[k]: v for k, v in protein_tuple.items()}
        else:
            tup = {k: protein_tuple[k] for k in PORDER}
    
    # Find nearest layer
    distances = [(i, clink_distance(tup, i)) for i in range(9)]
    nearest = min(distances, key=lambda x: x[1])
    idx, dist = nearest
    
    # Compute promotion path
    nearest_tup = CLINK_LAYERS[idx]
    promos = [f"{p}: {tup[p]}→{nearest_tup[p]}" for p in PORDER if tup[p] != nearest_tup[p]]
    
    return BridgeResult(
        component="serpentrod",
        component_type=tup,
        nearest_layer_idx=idx,
        nearest_layer_name=CLINK_NAMES[idx],
        distance=round(dist, 4),
        promotion_path=promos,
        frobenius_verified=clink_frobenius_closed(tup),
        notes="Proteins bridge molecule→cell. Folded proteins approach cellLayer (self-organization)."
    )


# ═══════════════════════════════════════════════════════════════════
# CH3MPILER BRIDGE — Molecule ↔ moleculeLayer (L3)
# ═══════════════════════════════════════════════════════════════════
#
# ch3mpiler compiles retrosynthetic disconnections based on the
# structural distance between product and FG type compositions.
# Molecules map naturally to moleculeLayer (L3).

def molecule_to_clink(molecule_tuple=None):
    """Bridge a ch3mpiler molecule type to the nearest CLINK layer.
    
    Args:
        molecule_tuple: dict with 12 primitives. If None, uses MOLECULE_LAYER.
    
    Returns:
        BridgeResult
    """
    if molecule_tuple is None:
        tup = {k: CLINK_LAYERS[3][k] for k in PORDER}
    else:
        ch3_to_porder = {"D":"Ð","T":"Þ","R":"Ř","P":"Φ","F":"ƒ",
                         "K":"Ç","G":"Γ","Gm":"ɢ","Ph":"⊙","H":"Ħ","S":"Σ","W":"Ω"}
        if all(k in ch3_to_porder for k in molecule_tuple):
            tup = {ch3_to_porder[k]: v for k, v in molecule_tuple.items()}
        else:
            tup = {k: molecule_tuple[k] for k in PORDER}
    
    distances = [(i, clink_distance(tup, i)) for i in range(9)]
    nearest = min(distances, key=lambda x: x[1])
    idx, dist = nearest
    
    nearest_tup = CLINK_LAYERS[idx]
    promos = [f"{p}: {tup[p]}→{nearest_tup[p]}" for p in PORDER if tup[p] != nearest_tup[p]]
    
    return BridgeResult(
        component="ch3mpiler",
        component_type=tup,
        nearest_layer_idx=idx,
        nearest_layer_name=CLINK_NAMES[idx],
        distance=round(dist, 4),
        promotion_path=promos,
        frobenius_verified=clink_frobenius_closed(tup),
        notes="Molecules map to moleculeLayer (L3). Complex molecules may approach cellLayer."
    )


# ═══════════════════════════════════════════════════════════════════
# GENE IMSCRIBER BRIDGE — Codon space ↔ electronOrbitalLayer (L1)
# ═══════════════════════════════════════════════════════════════════
#
# The gene_imscriber maps codon space onto the Belnap B4 lattice,
# which corresponds to electronOrbitalLayer (Layer 1) — both use
# 4-valued paraconsistent logic for occupancy states.

# Canonical structural type for a codon in the Belnap4 lattice
CODON_BELNAP4_TYPE = {
    "Ð": "𐑛", "Þ": "𐑶", "Ř": "𐑩", "Φ": "𐑗",
    "ƒ": "𐑐", "Ç": "𐑤", "Γ": "𐑚", "ɢ": "𐑜",
    "⊙": "𐑢", "Ħ": "𐑓", "Σ": "𐑙", "Ω": "𐑷",
    "_name": "codonBelnap4",
    "_desc": "Codon in Belnap4 lattice — 4-valued paraconsistent",
    "_tier": "O₀",
}

def gene_to_clink(gene_tuple=None):
    """Bridge a gene_imscriber type to the nearest CLINK layer.
    
    Args:
        gene_tuple: dict with 12 primitives. If None, uses CODON_BELNAP4_TYPE.
    
    Returns:
        BridgeResult
    """
    if gene_tuple is None:
        tup = {k: CODON_BELNAP4_TYPE[k] for k in PORDER}
    else:
        ch3_to_porder = {"D":"Ð","T":"Þ","R":"Ř","P":"Φ","F":"ƒ",
                         "K":"Ç","G":"Γ","Gm":"ɢ","Ph":"⊙","H":"Ħ","S":"Σ","W":"Ω"}
        if all(k in ch3_to_porder for k in gene_tuple):
            tup = {ch3_to_porder[k]: v for k, v in gene_tuple.items()}
        else:
            tup = {k: gene_tuple[k] for k in PORDER}
    
    distances = [(i, clink_distance(tup, i)) for i in range(9)]
    nearest = min(distances, key=lambda x: x[1])
    idx, dist = nearest
    
    nearest_tup = CLINK_LAYERS[idx]
    promos = [f"{p}: {tup[p]}→{nearest_tup[p]}" for p in PORDER if tup[p] != nearest_tup[p]]
    
    return BridgeResult(
        component="gene_imscriber",
        component_type=tup,
        nearest_layer_idx=idx,
        nearest_layer_name=CLINK_NAMES[idx],
        distance=round(dist, 4),
        promotion_path=promos,
        frobenius_verified=clink_frobenius_closed(tup),
        notes="Gene imscriber Belnap4 maps to electronOrbitalLayer (L1). Both use 4-valued paraconsistent logic."
    )


def bridge_all_components():
    """Run all bridges and return results as a dict."""
    return {
        "serpentrod": protein_to_clink(),
        "serpentrod_unfolded": protein_to_clink(UNFOLDED_PROTEIN),
        "ch3mpiler": molecule_to_clink(),
        "gene_imscriber": gene_to_clink(),
    }


if __name__ == "__main__":
    results = bridge_all_components()
    print("CLINK Bridges to Rebis Components")
    print("=" * 60)
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Nearest layer: {result.nearest_layer_name} (idx={result.nearest_layer_idx})")
        print(f"  Distance: {result.distance}")
        print(f"  Frobenius-verified: {result.frobenius_verified}")
        print(f"  Promotion path: {result.promotion_path}")
        print(f"  Notes: {result.notes}")
