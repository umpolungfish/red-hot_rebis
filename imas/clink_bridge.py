"""
clink_bridge.py — IMASM Arrangement → CLINK Biological Layer Bridge
====================================================================
Novel structural bridge connecting the IMASM token arrangement space
(computational/programmatic scale) to the CLINK biological scale chain
(physical scale, 9 layers, quark→organism).

This bridge reveals:
  - Which canonical arrangement types are structurally proximal to which
    biological layers
  - The "computational cost" of each CLINK layer in IMASM token operations
  - The structural distance between arrangement-space programs and
    biological-scale structures
  - Paths to synthesize (via arrangement programming) specific biological
    structural types

Key Discovery: The CLINK chain's biological progression (O₀→O_∞) is mirrored
in the IMASM canonical progression from Generic Mass (O₀) to Dialetheic
Bootstrap (⊙, O_∞), but via different primitive paths — the biological
chain promotes D, T, H, Ω while the IMASM chain promotes R, P, C, Φ.

Author: Lando⊗⊙perator
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import sys
from pathlib import Path

# Bridge to CLINK
sys.path.insert(0, str(Path(__file__).parent.parent))

from imas.arranger import (
    CANONICAL_ARRANGEMENTS, CANONICAL_FINGERPRINTS, CANONICAL_NAMES,
    CANONICAL_DESCRIPTIONS, StructuralFingerprint, compute_fingerprint,
)
from shared.rich_output import *
from imas.ig_bridge import (

    fingerprint_to_ig, canonical_ig_types, distinct_canonical_ig_types,
    ig_distance, ig_tuple_str, describe_ig, describe_full,
)

# ═══════════════════════════════════════════════════════════════════
# CLINK LAYER TUPLES (mirrored from clink/chain.py for self-containment)
# ═══════════════════════════════════════════════════════════════════

CLINK_LAYER_TUPLES = {
    "L0_FrustratedBelnap5": ('𐑛', '𐑶', '𐑩', '𐑯', '𐑐', '𐑘', '𐑚', '𐑝', '𐑢', '𐑓', '𐑳', '𐑷'),
    "L1_ElectronOrbital":   ('𐑛', '𐑶', '𐑩', '𐑗', '𐑐', '𐑤', '𐑚', '𐑜', '𐑢', '𐑓', '𐑳', '𐑷'),
    "L2_Atom":              ('𐑼', '𐑥', '𐑽', '𐑿', '𐑐', '𐑤', '𐑔', '𐑝', '𐑮', '𐑒', '𐑳', '𐑷'),
    "L3_Molecule":          ('𐑼', '𐑥', '𐑽', '𐑿', '𐑞', '𐑧', '𐑲', '𐑠', '⊙', '𐑓', '𐑳', '𐑭'),
    "L4_Cell":              ('𐑦', '𐑸', '𐑾', '𐑬', '𐑞', '𐑧', '𐑲', '𐑠', '⊙', '𐑒', '𐑳', '𐑭'),
    "L5_Mitosis":           ('𐑦', '𐑸', '𐑾', '𐑹', '𐑱', '𐑧', '𐑲', '𐑠', '⊙', '𐑖', '𐑳', '𐑭'),
    "L6_Meiosis":           ('𐑦', '𐑸', '𐑽', '𐑿', '𐑱', '𐑧', '𐑲', '𐑠', '⊙', '𐑖', '𐑳', '𐑭'),
    "L7_Tissue":            ('𐑦', '𐑸', '𐑾', '𐑬', '𐑞', '𐑧', '𐑲', '𐑵', '⊙', '𐑖', '𐑳', '𐑭'),
    "L8_Organism":          ('𐑦', '𐑸', '𐑾', '𐑹', '𐑐', '𐑧', '𐑲', '𐑵', '⊙', '𐑫', '𐑳', '𐑟'),
}

CLINK_LAYER_NAMES = [
    "L0_FrustratedBelnap5", "L1_ElectronOrbital", "L2_Atom",
    "L3_Molecule", "L4_Cell", "L5_Mitosis",
    "L6_Meiosis", "L7_Tissue", "L8_Organism",
]

CLINK_TIERS = {
    "L0": "O₀", "L1": "O₀", "L2": "O₁", "L3": "O₂",
    "L4": "O₂", "L5": "O₂", "L6": "O₂", "L7": "O₂", "L8": "O_∞",
}


# ═══════════════════════════════════════════════════════════════════
# IMASM → CLINK BRIDGE
# ═══════════════════════════════════════════════════════════════════

@dataclass
class IMASM_CLINK_Link:
    """A structural link between an IMASM canonical and a CLINK layer."""
    canonical: str
    clink_layer: str
    ig_distance: int
    shared_primitives: List[str]
    differing_primitives: List[str]
    interpretation: str


def imasm_to_clink(canonical_name: str) -> List[IMASM_CLINK_Link]:
    """Find the nearest CLINK layers for a canonical arrangement.

    Returns all CLINK layers sorted by IG distance (nearest first).
    """
    ig = fingerprint_to_ig(CANONICAL_FINGERPRINTS[canonical_name])
    links = []
    for layer_name, layer_ig in CLINK_LAYER_TUPLES.items():
        d = ig_distance(ig, layer_ig)
        shared = []
        diffs = []
        for i, prim_name in enumerate(['D','T','R','P','F','K','G','C','Φ','H','S','Ω']):
            if ig[i] == layer_ig[i]:
                shared.append(f"{prim_name}={ig[i]}")
            else:
                diffs.append(f"{prim_name}: {ig[i]}→{layer_ig[i]}")
        links.append(IMASM_CLINK_Link(
            canonical=canonical_name,
            clink_layer=layer_name,
            ig_distance=d,
            shared_primitives=shared,
            differing_primitives=diffs,
            interpretation=_interpret_link(canonical_name, layer_name, d, diffs),
        ))
    links.sort(key=lambda x: x.ig_distance)
    return links


def _interpret_link(canonical: str, layer: str, dist: int,
                    diffs: List[str]) -> str:
    """Generate a human-readable interpretation of the IMASM-CLINK link."""
    if dist <= 2:
        return f"Near-isomorphic: {canonical} structurally mirrors {layer}"
    elif dist <= 4:
        return f"Structurally adjacent: {canonical} and {layer} share core primitives, differ in {'; '.join(diffs[:3])}"
    elif dist <= 7:
        return f"Different regime: {canonical} requires {len(diffs)} promotions to reach {layer}"
    else:
        return f"Structurally remote: {canonical} and {layer} occupy different sectors of the crystal"

# ═══════════════════════════════════════════════════════════════════
# CANONICAL → CLINK FULL MAPPING
# ═══════════════════════════════════════════════════════════════════

def canonical_clink_map() -> Dict[str, Dict]:
    """Full mapping of all 12 canonicals to their nearest CLINK layers.

    Returns a dict: canonical_name → {
        'ig': ...,
        'nearest_layer': ...,
        'distance': ...,
        'all_layers': [(layer, dist), ...],
    }
    """
    result = {}
    for name in CANONICAL_NAMES:
        ig = fingerprint_to_ig(CANONICAL_FINGERPRINTS[name])
        layer_dists = [(ln, ig_distance(ig, lt))
                       for ln, lt in CLINK_LAYER_TUPLES.items()]
        layer_dists.sort(key=lambda x: x[1])
        nearest = layer_dists[0]
        result[name] = {
            'ig': ig,
            'ig_str': ig_tuple_str(ig),
            'description': describe_ig(ig),
            'canonical_desc': CANONICAL_DESCRIPTIONS[name],
            'nearest_layer': nearest[0],
            'nearest_distance': nearest[1],
            'all_layers': layer_dists,
        }
    return result


# ═══════════════════════════════════════════════════════════════════
# STRUCTURAL ACTIVATION ENERGY
# ═══════════════════════════════════════════════════════════════════

def structural_activation_energy(
    source_ig: Tuple[str, ...],
    target_layer: str,
) -> Dict:
    """Compute the 'structural activation energy' to lift an IG type to a CLINK layer.

    This measures how many primitive promotions are needed, which primitives
    must change, and the weighted cost of the transition. This operationalizes
    Discovery 2 (Generic Mass) and Discovery 3 (Zero Frobenius Pairs) — the
    combinatorial suppression of structured types.

    Returns:
        dict with: distance, promotions, weighted_cost, tier_gap, feasible
    """
    target_ig = CLINK_LAYER_TUPLES[target_layer]
    dist = ig_distance(source_ig, target_ig)

    promotions = []
    for i, name in enumerate(['D','T','R','P','F','K','G','C','Φ','H','S','Ω']):
        if source_ig[i] != target_ig[i]:
            promotions.append(f"{name}: {source_ig[i]} → {target_ig[i]}")

    # Weighted cost: primitives with higher cardinalities cost more to promote
    cardinalities = {'D': 4, 'T': 5, 'R': 4, 'P': 5, 'F': 3, 'K': 5,
                     'G': 3, 'C': 4, 'Φ': 5, 'H': 4, 'S': 3, 'Ω': 4}
    weighted = sum(
        cardinalities[name] / (cardinalities[name] - 1)
        for i, name in enumerate(['D','T','R','P','F','K','G','C','Φ','H','S','Ω'])
        if source_ig[i] != target_ig[i]
    )

    # Tier gap
    source_tier = _estimate_tier(source_ig)
    target_tier_name = target_layer.split('_')[0]
    target_tier = CLINK_TIERS.get(target_tier_name, "O_?")

    return {
        'distance': dist,
        'promotions': promotions,
        'weighted_cost': round(weighted, 2),
        'tier_gap': f"{source_tier} → {target_tier}",
        'feasible': dist <= 8,
    }


def _estimate_tier(ig: Tuple[str, ...]) -> str:
    """Rough tier estimate from IG primitives."""
    if ig[8] == '⊙' and ig[3] in ('𐑹', '𐑯') and ig[11] in ('𐑭', '𐑟'):
        return 'O_∞'
    elif ig[8] == '⊙' and ig[0] in ('𐑦', '𐑼'):
        return 'O₂'
    elif ig[0] in ('𐑼',):
        return 'O₁'
    else:
        return 'O₀'


# ═══════════════════════════════════════════════════════════════════
# ARRANGEMENT → BIOLOGICAL SCALE BRIDGE TABLE
# ═══════════════════════════════════════════════════════════════════

def build_bridge_table() -> str:
    """Generate a formatted bridge table: IMASM canonical → nearest CLINK layer."""
    mapping = canonical_clink_map()
    lines = []
    lines.append("| Canonical | IG Tier | Nearest CLINK Layer | CLINK Tier | d | Key Deltas |")
    lines.append("|-----------|---------|---------------------|------------|---|------------|")
    for name in CANONICAL_NAMES:
        m = mapping[name]
        short = name.split('_', 1)[1]
        tier = _estimate_tier(m['ig'])
        lname = m['nearest_layer'].replace('_', ' ')
        ltier = CLINK_TIERS.get(m['nearest_layer'].split('_')[0], '?')
        d = m['nearest_distance']
        # Find key deltas
        ig = m['ig']
        target = CLINK_LAYER_TUPLES[m['nearest_layer']]
        key_deltas = []
        for i, pn in enumerate(['D','T','R','P','F','K','G','C','Φ','H','S','Ω']):
            if ig[i] != target[i]:
                key_deltas.append(f"{pn}")
        lines.append(
            f"| {short:25s} | {tier:6s} | {lname:20s} | {ltier:6s} | {d} | {', '.join(key_deltas[:4])} |"
        )
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════
# PRE-COMPUTED BRIDGE TABLE
# ═══════════════════════════════════════════════════════════════════

IMASM_CLINK_BRIDGE_TABLE = build_bridge_table()


# ═══════════════════════════════════════════════════════════════════
# FROBENIUS PATHWAY SYNTHESIS
# ═══════════════════════════════════════════════════════════════════

def frobenius_pathway_to_layer(target_layer: str) -> Dict:
    """What would it take to synthesize a Frobenius-closed arrangement
    that structurally matches a CLINK layer?

    This combines the Frobenius rarity discovery (0 in 10M random) with
    the CLINK bridge to answer: how hard is it to program a Frobenius-closed
    system at each biological scale?
    """
    target_ig = CLINK_LAYER_TUPLES[target_layer]
    # Find which canonicals (if any) are closest
    mapping = canonical_clink_map()
    nearest_canonical = None
    nearest_dist = 13
    for name, m in mapping.items():
        if m['nearest_layer'] == target_layer:
            if m['nearest_distance'] < nearest_dist:
                nearest_dist = m['nearest_distance']
                nearest_canonical = name

    # Does target_layer already have Frobenius signature?
    frob_in_target = target_ig[3] == '𐑹'  # P = Frobenius-special

    return {
        'target_layer': target_layer,
        'target_ig_str': ig_tuple_str(target_ig),
        'has_frobenius_parity': frob_in_target,
        'nearest_canonical': nearest_canonical,
        'nearest_canonical_dist': nearest_dist,
        'frobenius_closed_layers': [
            ln for ln, lt in CLINK_LAYER_TUPLES.items()
            if lt[3] == '𐑹'
        ],
    }


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    info_line("=" * 72)
    info_line("IMASM → CLINK BRIDGE")
    info_line("=" * 72)
    print()
    print(build_bridge_table())
    print()
    info_line("=" * 72)
    info_line("FROBENIUS PATHWAY SYNTHESIS")
    info_line("=" * 72)
    for layer in CLINK_LAYER_NAMES:
        fp = frobenius_pathway_to_layer(layer)
        status = "✓ Frobenius-special" if fp['has_frobenius_parity'] else "— not Frobenius"
        info_line(f"  {layer}: {status}")
        if fp['nearest_canonical']:
            info_line(f"    Nearest canonical: {fp['nearest_canonical']} (d={fp['nearest_canonical_dist']})")
