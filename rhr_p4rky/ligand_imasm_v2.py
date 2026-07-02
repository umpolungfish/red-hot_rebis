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

    # D: Dimensionality — catalytic complexity
    D = ('𐑛' if d == 1 else ('𐑨' if d == 2 else ('𐑼' if d <= 4 else '𐑦')))

    # T: Topology — enzyme IS identity (always self-ref in mechanism flow)
    # Use fam_adj to add order sensitivity when self_ref is constant
    if fp.self_ref:
        # Self-ref with order variants
        T = ('𐑸' if fam_disc <= 1 else '𐑥')
    else:
        T = ('𐑡' if fam_disc <= 1 else '𐑰')

    # R: Coupling — Frobenius pair (FSPLIT + FFUSE both present)
    has_fsplit_token = bool(token_mask & (1 << 6))
    has_ffuse_token = bool(token_mask & (1 << 7))
    if has_fsplit_token and has_ffuse_token:
        R = ('𐑾' if fp.frobenius_order == 1 else
             ('𐑽' if fp.frobenius_order == 2 else '𐑾'))
    elif has_fsplit_token:
        R = '𐑽'  # Only split, no fuse (attack without release)
    elif has_ffuse_token:
        R = '𐑑'  # Only fuse, no split
    else:
        R = '𐑩'  # Neither — pure binding site

    # P: Parity — acid+base both present
    has_evalt = bool(token_mask & (1 << 8))
    has_evalf = bool(token_mask & (1 << 9))
    if has_evalt and has_evalf:
        P = '𐑬'
    elif has_evalt or has_evalf:
        # Use order sensitivity: EVALF-first vs EVALT-first
        if has_evalf and fam_disc >= 2:
            P = '𐑿'  # Base-dominant
        elif has_evalf:
            P = '𐑹'  # Base-prominent (Frobenius-special sense)
        else:
            P = '𐑿'
    else:
        P = '𐑗'

    # F: Fidelity — nucleophile present
    has_nucleophile = bool(token_mask & (1 << 6))
    if has_nucleophile and has_evalf:
        F = '𐑐'  # Nucleophile + base = quantum
    elif has_nucleophile:
        F = '𐑞'  # Nucleophile only = thermal
    else:
        F = '𐑱'  # No nucleophile = classical

    # K: Kinetics — role diversity
    if d >= 5:
        K = '𐑧'
    elif d >= 3:
        K = '𐑪'
    elif d == 2:
        K = '𐑘'
    else:
        K = '𐑤'

    # G: Cardinality — filled positions
    G = ('𐑚' if d <= 2 else ('𐑔' if d <= 4 else '𐑲'))

    # Gm: Composition — order-sensitive
    if fp.frobenius_order > 0:
        Gm = '𐑠'
    elif fam_disc >= 3:
        Gm = '𐑵'  # Complex transitions
    elif fam_disc >= 1:
        Gm = '𐑜'  # Some structure
    else:
        Gm = '𐑝'  # All same family

    # Ph: Criticality — paradox handling
    has_engagr = bool(token_mask & (1 << 10))
    if fp.self_ref and has_engagr:
        Ph = '⊙'
    elif has_engagr:
        Ph = '𐑻'
    elif fp.self_ref:
        Ph = '𐑮'
    elif d <= 2:
        Ph = '𐑢'
    else:
        Ph = ('𐑣' if fam_disc <= 1 else '𐑻')

    # H: Chirality — signature spread + order
    if nz >= 4:
        H = '𐑫'
    elif nz == 3:
        H = '𐑖'
    elif nz == 2:
        H = ('𐑒' if fam_disc >= 2 else '𐑓')
    else:
        H = '𐑓'

    # S: Stoichiometry — unique roles
    S = ('𐑙' if d == 1 else ('𐑕' if d <= 3 else '𐑳'))

    # W: Winding — catalytic cycle completion
    if has_fsplit_token and has_ffuse_token:
        W = '𐑭'
    elif fp.self_ref:
        W = '𐑴'
    else:
        W = '𐑷'

    return (D, T, R, P, F, K, G, Gm, Ph, H, S, W)
