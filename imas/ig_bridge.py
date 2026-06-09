"""
ig_bridge.py — IMASM Fingerprint → IG Structural Type Bridge
=============================================================
Systematic mapping from IMASM arrangement structural fingerprints to
the 12-primitive Imscribing Grammar (IG) crystal of types.

Each fingerprint field maps deterministically to one IG primitive. The
bridge reveals which IMASM arrangements correspond to which structural
regimes — generic thermal noise, Frobenius-closed verification, ⊙-critical
self-modeling, or pure irreversible recording.

Author: Lando⊗⊙perator
Adapted from: /home/mrnob0dy666/IMSCRIBr/imas_ig_bridge.py
"""

from typing import Tuple, Dict, List
from imas.arranger import (
    StructuralFingerprint, CANONICAL_FINGERPRINTS, CANONICAL_NAMES,
)

# ═══════════════════════════════════════════════════════════════════
# FINGERPRINT → IG MAPPING
# ═══════════════════════════════════════════════════════════════════

def fingerprint_to_ig(fp: StructuralFingerprint) -> Tuple[str, ...]:
    """Map a StructuralFingerprint to a 12-tuple of IG primitive values.

    Each fingerprint field maps to one IG primitive via a deterministic rule.
    The mapping is structural, not definitional — it captures the structural
    essence of the arrangement in the IG primitive language.

    Returns:
        (D, T, R, P, F, K, G, C, Phi, H, S, Omega) as Shavian glyph strings.
    """
    # D (Dimensionality): from token diversity
    d = fp.token_diversity
    D = ('𐑛' if d <= 2 else ('𐑨' if d <= 5 else ('𐑼' if d <= 9 else '𐑦')))

    # T (Topology): from self_ref + period + frobenius_order
    if fp.self_ref:
        T = '𐑸'
    elif fp.period == 1:
        T = '𐑡'
    elif fp.period == 2:
        T = '𐑥'
    elif fp.frobenius_order > 0:
        T = '𐑶'
    else:
        T = '𐑰'

    # R (Coupling): from frobenius_order
    R = ('𐑾' if fp.frobenius_order == 1 else
         ('𐑽' if fp.frobenius_order == 2 else
          ('𐑑' if fp.frobenius_order == 3 else '𐑩')))

    # P (Parity): from frobenius_order + dialetheia_complete
    if fp.frobenius_order == 1:
        P = '𐑹'
    elif fp.frobenius_order == 2:
        P = '𐑯'
    elif fp.frobenius_order == 3:
        P = '𐑬'
    elif fp.dialetheia_complete:
        P = '𐑿'
    else:
        P = '𐑗'

    # F (Fidelity): from dialetheia_complete + period
    if fp.dialetheia_complete:
        F = '𐑐'
    elif fp.period == 1:
        F = '𐑱'
    else:
        F = '𐑞'

    # K (Kinetics): from period + sig_X (IFIX count)
    sx = fp.sig_X
    if sx == 8:
        K = '𐑪'
    elif fp.period == 1:
        K = '𐑧'
    elif fp.period <= 2:
        K = '𐑤'
    elif fp.period <= 4:
        K = '𐑤'
    else:
        K = '𐑘'

    # G (Cardinality): from sig_X + token_diversity
    if sx >= 3:
        G = '𐑲'
    elif sx >= 1:
        G = '𐑔'
    elif fp.token_diversity <= 3:
        G = '𐑚'
    else:
        G = '𐑔'

    # C (Composition): from frobenius_order + period
    if fp.frobenius_order > 0:
        C = '𐑠'
    elif fp.period == 1:
        C = '𐑝'
    elif fp.period == 2:
        C = '𐑜'
    else:
        C = '𐑵'

    # Phi (Criticality): from self_ref + dialetheia_complete + period
    if fp.self_ref and fp.dialetheia_complete:
        Phi = '⊙'
    elif fp.self_ref:
        Phi = '𐑮'
    elif fp.dialetheia_complete:
        Phi = '𐑻'
    elif fp.period == 1:
        Phi = '𐑢'
    else:
        Phi = '𐑣'

    # H (Chirality): from period
    H = ('𐑓' if fp.period == 1 else
         ('𐑒' if fp.period == 2 else
          ('𐑖' if fp.period == 3 else '𐑫')))

    # S (Stoichiometry): from signature non-zero count
    nz = sum(1 for c in fp.signature if c > 0)
    S = ('𐑙' if nz == 1 else ('𐑕' if nz == 2 else '𐑳'))

    # Omega (Winding): from frobenius_order + self_ref + period
    if fp.frobenius_order == 1:
        Omega = '𐑭'
    elif fp.frobenius_order == 2:
        Omega = '𐑴'
    elif fp.self_ref:
        Omega = '𐑭'
    elif fp.period == 2:
        Omega = '𐑴'
    else:
        Omega = '𐑷'

    return (D, T, R, P, F, K, G, C, Phi, H, S, Omega)

# ═══════════════════════════════════════════════════════════════════
# CANONICAL IG TYPES
# ═══════════════════════════════════════════════════════════════════

def canonical_ig_types() -> Dict[str, Tuple[str, ...]]:
    """Return all IG types for the 12 canonical arrangements.

    Note: IX_Chiral_Pairs and VI_Empty_Bootstrap map to the same IG type.
    """
    return {name: fingerprint_to_ig(fp)
            for name, fp in CANONICAL_FINGERPRINTS.items()}

def distinct_canonical_ig_types() -> Dict[Tuple[str, ...], List[str]]:
    """Return distinct IG types and which canonicals map to them."""
    groups = {}
    for name, fp in CANONICAL_FINGERPRINTS.items():
        ig = fingerprint_to_ig(fp)
        groups.setdefault(ig, []).append(name)
    return dict(groups)


# ═══════════════════════════════════════════════════════════════════
# DISTANCE & COMPARISON
# ═══════════════════════════════════════════════════════════════════

def ig_distance(ig_a: Tuple[str, ...], ig_b: Tuple[str, ...]) -> int:
    """Count of primitive mismatches between two IG tuples."""
    return sum(1 for a, b in zip(ig_a, ig_b) if a != b)

def ig_distance_matrix(
    ig_types: Dict[str, Tuple[str, ...]]
) -> Dict[str, Dict[str, int]]:
    """Compute pairwise distance matrix for a set of IG types."""
    names = sorted(ig_types.keys())
    return {na: {nb: ig_distance(ig_types[na], ig_types[nb])
                  for nb in names}
            for na in names}


# ═══════════════════════════════════════════════════════════════════
# DISPLAY & DESCRIPTION
# ═══════════════════════════════════════════════════════════════════

PRIMITIVE_NAMES = ['D', 'T', 'R', 'P', 'F', 'K', 'G', 'C', 'Φ', 'H', 'S', 'Ω']

def ig_tuple_str(ig: Tuple[str, ...]) -> str:
    """Format an IG tuple for display: ⟨D · T · R · P · F · K · G · C · Φ · H · S · Ω⟩"""
    return '⟨' + ' · '.join(ig) + '⟩'

def describe_ig(ig: Tuple[str, ...]) -> str:
    """Return a one-line description of an IG tuple's key structural features."""
    parts = []
    if ig[8] == '⊙':
        parts.append('⊙-critical (self-modeling)')
    elif ig[8] == '𐑮':
        parts.append('self-reflective')
    elif ig[8] == '𐑻':
        parts.append('EP (paradox-capable)')
    if ig[3] == '𐑹':
        parts.append('Frobenius-special')
    elif ig[3] == '𐑯':
        parts.append('inverted-Frobenius')
    if ig[0] == '𐑛':
        parts.append('point-like')
    elif ig[0] == '𐑦':
        parts.append('holographic')
    return ', '.join(parts) if parts else 'generic'

def describe_full(ig: Tuple[str, ...]) -> str:
    """Full structural description of an IG tuple."""
    maps = {
        'D': {'𐑛': 'point-like (0d)', '𐑨': 'triangle (2d)',
              '𐑼': 'infinite-dim field', '𐑦': 'self-written holographic'},
        'T': {'𐑡': 'network branching', '𐑰': 'containment',
              '𐑥': 'crossing/bowtie', '𐑶': 'irreducible product',
              '𐑸': 'self-referential topology'},
        'R': {'𐑩': 'supervenience', '𐑑': 'functorial',
              '𐑽': 'adjoint/dagger', '𐑾': 'bidirectional feedback'},
        'P': {'𐑗': 'no symmetry', '𐑿': 'quantum superposition',
              '𐑬': 'partial Z2', '𐑯': 'full symmetry',
              '𐑹': 'Frobenius-special (μ∘δ=id)'},
        'F': {'𐑱': 'classical', '𐑞': 'thermal/noisy', '𐑐': 'quantum coherent'},
        'K': {'𐑘': 'driven/fast', '𐑤': 'moderate', '𐑧': 'slow/near-eq',
              '𐑪': 'trapped-ordered', '𐑺': 'trapped-disorder'},
        'G': {'𐑚': 'local/nearest-neighbor', '𐑔': 'mesoscale',
              '𐑲': 'universal/long-range'},
        'C': {'𐑝': 'all-simultaneous', '𐑜': 'alternate paths',
              '𐑠': 'ordered steps/sequential', '𐑵': 'broadcast/one-to-all'},
        'Φ': {'𐑢': 'sub-critical', '⊙': 'critical/self-modeling',
              '𐑮': 'complex-plane critical', '𐑻': 'exceptional point',
              '𐑣': 'supercritical/runaway'},
        'H': {'𐑓': 'memoryless (M0)', '𐑒': 'one-step (M1)',
              '𐑖': 'two-step (M2)', '𐑫': 'eternal (no finite n)'},
        'S': {'𐑙': '1:1 single type', '𐑕': 'many identical',
              '𐑳': 'multiple distinct types'},
        'Ω': {'𐑷': 'trivial', '𐑴': 'Z2 parity-protected',
              '𐑭': 'integer winding', '𐑟': 'non-Abelian braiding'},
    }
    lines = []
    for i, name in enumerate(PRIMITIVE_NAMES):
        val = ig[i]
        desc = maps.get(name, {}).get(val, '???')
        lines.append(f"  {name}: {val} — {desc}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════
# STRUCTURAL CLUSTERING
# ═══════════════════════════════════════════════════════════════════

def find_structural_clusters(max_dist: int = 6) -> List[List[str]]:
    """Cluster the 12 canonicals by IG distance ≤ max_dist."""
    igs = canonical_ig_types()
    names = CANONICAL_NAMES
    # Simple connected-component clustering
    adj = {n: set() for n in names}
    for i, ni in enumerate(names):
        for j, nj in enumerate(names):
            if i < j and ig_distance(igs[ni], igs[nj]) <= max_dist:
                adj[ni].add(nj)
                adj[nj].add(ni)
    visited = set()
    clusters = []
    for name in names:
        if name not in visited:
            stack = [name]
            cluster = []
            while stack:
                n = stack.pop()
                if n not in visited:
                    visited.add(n)
                    cluster.append(n)
                    stack.extend(adj[n] - visited)
            clusters.append(sorted(cluster))
    return clusters


# ═══════════════════════════════════════════════════════════════════
# GENERIC MASS DETECTION
# ═══════════════════════════════════════════════════════════════════

GENERIC_IG_TYPES = [
    ('𐑼', '𐑰', '𐑩', '𐑗', '𐑞', '𐑘', '𐑔', '𐑵', '𐑣', '𐑫', '𐑳', '𐑷'),
    ('𐑨', '𐑰', '𐑩', '𐑗', '𐑞', '𐑘', '𐑔', '𐑵', '𐑣', '𐑫', '𐑳', '𐑷'),
    ('𐑼', '𐑸', '𐑩', '𐑗', '𐑞', '𐑘', '𐑔', '𐑵', '𐑮', '𐑫', '𐑳', '𐑭'),
    ('𐑨', '𐑸', '𐑩', '𐑗', '𐑞', '𐑘', '𐑔', '𐑵', '𐑮', '𐑫', '𐑳', '𐑭'),
]

def is_generic_mass(ig: Tuple[str, ...]) -> bool:
    """Check if an IG type belongs to the 99.993% generic mass."""
    return ig in GENERIC_IG_TYPES

def structural_signal_score(ig: Tuple[str, ...]) -> float:
    """How structurally 'interesting' is this IG type? 0=generic mass, 1=⊙-critical.

    Measures distance from the four generic-mass types, normalized by max possible.
    """
    if ig in GENERIC_IG_TYPES:
        return 0.0
    min_dist = min(ig_distance(ig, g) for g in GENERIC_IG_TYPES)
    return min_dist / 12.0


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 72)
    print("IMASM → IG STRUCTURAL BRIDGE")
    print("=" * 72)

    distinct = distinct_canonical_ig_types()
    print(f"\n12 canonicals → {len(distinct)} distinct IG types\n")

    for ig, names in sorted(distinct.items(), key=lambda x: -len(x[1])):
        label = " + ".join(n.split('_', 1)[1] for n in names)
        print(f"  {label}:")
        print(f"    {ig_tuple_str(ig)}")
        desc = describe_ig(ig)
        if desc:
            print(f"    [{desc}]")
        print()

    # Clusters
    for max_d in [4, 6, 8]:
        clusters = find_structural_clusters(max_d)
        print(f"Clusters at d≤{max_d}: {len(clusters)}")
        for c in clusters:
            if len(c) > 1:
                print(f"  {' ↔ '.join(n.split('_',1)[1] for n in c)}")
