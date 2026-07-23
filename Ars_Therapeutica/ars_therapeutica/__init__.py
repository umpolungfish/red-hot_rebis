"""
Ars Therapeutica — Structural grammar-derived optimal therapies.

A pip-installable CLI that operationalizes the 12-primitive Imscribing Grammar
for disease diagnosis, therapy navigation, and structural computation.

Usage:
    at list              — list all therapies
    at diagnose <name>   — structural diagnosis
    at therapy <name>    — full therapy protocol
    at spectrum          — psychiatric φ̂ spectrum
    at compare <a> <b>   — side-by-side comparison
    at tensor <a> <b>    — tensor product
    at meet <a> <b>       — meet (greatest lower bound)
"""

from .types import (
    Imscription, Therapy, THERAPIES, DISEASE_TYPES, HEALTH_TYPES,
    D, T, R, P, F, K, G, Gamma, Phi, H, S, W,
    tensor, meet, join, distance, delta_primitives, c_score, tier,
    SCHIZOPHRENIA, HEALTHY_BRAIN, DEPRESSION, BIPOLAR_MANIA,
    HIV, NORMAL_IMMUNE, MRSA, NORMAL_FLORA,
    PCOS, NORMAL_OVARIAN, CF, NORMAL_CFTR,
    GOUT, NORMAL_URATE,
)

__version__ = "1.0.0"
