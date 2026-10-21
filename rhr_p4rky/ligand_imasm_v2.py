#!/usr/bin/env python3
"""Biochemistry-sensitive fingerprint→IG mapping with order sensitivity."""
from typing import Tuple


def _fam_adj_discriminator(fp) -> int:
    """Extract a 0-3 discriminator from family adjacency mask to
    distinguish same-token-set arrangements with different orderings."""
    mask = fp.fam_adj_mask
    # Count distinct family→family transitions
    bits = bin(mask).count('1')
    # Use the mask itself modulo 4 as a discriminator
    return (mask ^ (mask >> 4)) & 0x3


def fingerprint_to_ig_biochemical(fp) -> Tuple[str, ...]:
    """Map StructuralFingerprint → 12-primitive IG tuple (biochemical semantics).

    Each primitive is determined by structural fingerprint properties
    interpreted in the context of enzyme catalysis.
    Uses family adjacency mask for order sensitivity when token sets collide.
    """
    d = fp.token_diversity
    sig = fp.signature  # (L, F, D, X)
    nz = sum(1 for c in sig if c > 0)
    token_mask = fp.token_mask
    fam_disc = _fam_adj_discriminator(fp)

    # ⊢: Dimensionality — catalytic complexity
    dimensionality = ('𐑛' if d == 1 else ('𐑨' if d == 2 else ('𐑼' if d <= 4 else '𐑦')))

    # ⊣: Topology — enzyme IS identity (always self-ref in mechanism flow)
    # Use fam_adj to add order sensitivity when self_ref is constant
    if fp.self_ref:
        # Self-ref with order variants
        topology = ('𐑸' if fam_disc <= 1 else '𐑥')
    else:
        topology = ('𐑡' if fam_disc <= 1 else '𐑰')

    # ≻: Coupling — Frobenius pair (FSPLIT + FFUSE both present)
    has_fsplit_token = bool(token_mask & (1 << 6))
    has_ffuse_token = bool(token_mask & (1 << 7))
    if has_fsplit_token and has_ffuse_token:
        coupling = ('𐑾' if fp.frobenius_order == 1 else
             ('𐑽' if fp.frobenius_order == 2 else '𐑾'))
    elif has_fsplit_token:
        coupling = '𐑽'  # Only split, no fuse (attack without release)
    elif has_ffuse_token:
        coupling = '𐑑'  # Only fuse, no split
    else:
        coupling = '𐑩'  # Neither — pure binding site

    # ≺: Parity — acid+base both present
    has_evalt = bool(token_mask & (1 << 8))
    has_evalf = bool(token_mask & (1 << 9))
    if has_evalt and has_evalf:
        parity = '𐑬'
    elif has_evalt or has_evalf:
        # Use order sensitivity: EVALF-first vs EVALT-first
        if has_evalf and fam_disc >= 2:
            parity = '𐑿'  # Base-dominant
        elif has_evalf:
            parity = '𐑹'  # Base-prominent (Frobenius-special sense)
        else:
            parity = '𐑿'
    else:
        parity = '𐑗'

    # ⋈: Fidelity — nucleophile present
    has_nucleophile = bool(token_mask & (1 << 6))
    if has_nucleophile and has_evalf:
        fidelity = '𐑐'  # Nucleophile + base = quantum
    elif has_nucleophile:
        fidelity = '𐑞'  # Nucleophile only = thermal
    else:
        fidelity = '𐑱'  # No nucleophile = classical

    # ⊤: Kinetics — role diversity
    if d >= 5:
        kinetics = '𐑧'
    elif d >= 3:
        kinetics = '𐑪'
    elif d == 2:
        kinetics = '𐑘'
    else:
        kinetics = '𐑤'

    # ∈: Cardinality — filled positions
    cardinality = ('𐑚' if d <= 2 else ('𐑔' if d <= 4 else '𐑲'))

    # ∋: Composition — order-sensitive
    if fp.frobenius_order > 0:
        composition = '𐑠'
    elif fam_disc >= 3:
        composition = '𐑵'  # Complex transitions
    elif fam_disc >= 1:
        composition = '𐑜'  # Some structure
    else:
        composition = '𐑝'  # All same family

    # ⊙: Criticality — paradox handling
    has_engagr = bool(token_mask & (1 << 10))
    if fp.self_ref and has_engagr:
        criticality = '⊙'
    elif has_engagr:
        criticality = '𐑻'
    elif fp.self_ref:
        criticality = '𐑮'
    elif d <= 2:
        criticality = '𐑢'
    else:
        criticality = ('𐑣' if fam_disc <= 1 else '𐑻')

    # ⊥: Chirality — signature spread + order
    if nz >= 4:
        chirality = '𐑫'
    elif nz == 3:
        chirality = '𐑖'
    elif nz == 2:
        chirality = ('𐑒' if fam_disc >= 2 else '𐑓')
    else:
        chirality = '𐑓'

    # ⊞: Stoichiometry — unique roles
    stoichiometry = ('𐑙' if d == 1 else ('𐑕' if d <= 3 else '𐑳'))

    # ⊡: Winding — catalytic cycle completion
    if has_fsplit_token and has_ffuse_token:
        winding = '𐑭'
    elif fp.self_ref:
        winding = '𐑴'
    else:
        winding = '𐑷'

    return (dimensionality, topology, coupling, parity, fidelity, kinetics, cardinality, composition, criticality, chirality, stoichiometry, winding)
