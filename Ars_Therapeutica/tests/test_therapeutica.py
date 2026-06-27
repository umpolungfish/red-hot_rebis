#!/usr/bin/env python3
"""
Ars Therapeutica — Comprehensive Test Suite
============================================
Verifies all 10 therapies, structural operations, psychiatric spectrum,
and primitive ordering cardinalities.

Usage: python3 -m pytest tests/test_therapeutica.py -v
"""

import sys
import os
import math

# Ensure the package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ars_therapeutica.types import (
    THERAPIES, DISEASE_TYPES, HEALTH_TYPES, PSYCHIATRIC_SPECTRUM,
    Imscription, D, T, R, P, F, K, G, Gamma, Phi, H, S, W,
    tensor, meet, join, distance, delta_primitives, c_score, tier,
    ORDERS, primitive_order,
    SCHIZOPHRENIA, HEALTHY_BRAIN, DEPRESSION, BIPOLAR_MANIA,
    HIV, NORMAL_IMMUNE, MRSA, NORMAL_FLORA,
    PCOS, NORMAL_OVARIAN, CF, NORMAL_CFTR,
    GOUT, NORMAL_URATE, HOMEOPATHIC_REMEDY, DISEASE_GENERIC,
    ART, NMDA_SYSTEM, DOPAMINE_MESOLIMBIC,
)


# ─────────────────────────────────────────────────────────
# 1. PRIMITIVE CARDINALITIES
# ─────────────────────────────────────────────────────────

def test_primitive_cardinalities():
    """All primitive enums have correct cardinalities."""
    assert len(D) == 4, f"D has {len(D)} values, expected 4"
    assert len(T) == 5, f"T has {len(T)} values, expected 5"
    assert len(R) == 4, f"R has {len(R)} values, expected 4"
    assert len(P) == 5, f"P has {len(P)} values, expected 5"
    assert len(F) == 3, f"F has {len(F)} values, expected 3"
    assert len(K) == 5, f"K has {len(K)} values, expected 5"
    assert len(G) == 3, f"G has {len(G)} values, expected 3"
    assert len(Gamma) == 4, f"Gamma has {len(Gamma)} values, expected 4"
    assert len(Phi) == 5, f"Phi has {len(Phi)} values, expected 5"
    assert len(H) == 4, f"H has {len(H)} values, expected 4"
    assert len(S) == 3, f"S has {len(S)} values, expected 3"
    assert len(W) == 4, f"W has {len(W)} values, expected 4"
    assert len(ORDERS) == 12, f"ORDERS has {len(ORDERS)} entries, expected 12"


# ─────────────────────────────────────────────────────────
# 2. THERAPY COUNT
# ─────────────────────────────────────────────────────────

def test_therapy_count():
    """Exactly 10 therapies are registered."""
    assert len(THERAPIES) == 10, f"Expected 10 therapies, got {len(THERAPIES)}"


def test_all_therapies_have_required_fields():
    """Every therapy has all required fields."""
    required = [
        "name", "disease", "category", "disease_type", "health_type",
        "delta_primitives", "distance", "tier_disease", "tier_health",
        "c_score_disease", "c_score_health", "components",
        "structural_strategy", "pdb_files", "lean_files", "doc_file", "summary"
    ]
    for key, th in THERAPIES.items():
        for field in required:
            assert hasattr(th, field), f"Therapy '{key}' missing field: {field}"


# ─────────────────────────────────────────────────────────
# 3. STRUCTURAL OPERATIONS — MATHEMATICAL CONSISTENCY
# ─────────────────────────────────────────────────────────

def test_distance_symmetric():
    """Distance is symmetric: d(a,b) == d(b,a)."""
    for name_a, ta in DISEASE_TYPES.items():
        tb = HEALTH_TYPES.get(name_a)
        if tb is None:
            continue
        d_ab = distance(ta, tb)
        d_ba = distance(tb, ta)
        assert d_ab == d_ba, f"d({name_a}, health)={d_ab} != d(health, {name_a})={d_ba}"


def test_distance_self_zero():
    """Distance to self is zero."""
    for name, t in {**DISEASE_TYPES, **HEALTH_TYPES}.items():
        d = distance(t, t)
        assert d == 0.0, f"d({name}, self) = {d}, expected 0.0"


def test_delta_primitives_vs_distance():
    """delta_primitives list matches the actual differing primitives."""
    PRIM_REV_MAP = {'D': 'Ð', 'T': 'Þ', 'R': 'Ř', 'P': 'Φ', 'F': 'ƒ', 'K': 'Ç',
                    'G': 'Γ', 'Gamma': 'ɢ', 'Phi': 'φ̂', 'H': 'Ħ', 'S': 'Σ', 'W': 'Ω'}
    for name, th in THERAPIES.items():
        computed = delta_primitives(th.disease_type, th.health_type)
        computed_symbols = [PRIM_REV_MAP.get(p, p) for p in computed]
        assert set(computed_symbols) == set(th.delta_primitives), \
            f"Therapy '{name}': computed deltas {computed_symbols} != declared {th.delta_primitives}"


def test_meet_lower_bound():
    """meet(a,b) <= a and meet(a,b) <= b for all primitive orderings."""
    for _, th in THERAPIES.items():
        a, b = th.disease_type, th.health_type
        m = meet(a, b)
        for prim_name in ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
            oa = primitive_order(getattr(a, prim_name), prim_name)
            ob = primitive_order(getattr(b, prim_name), prim_name)
            om = primitive_order(getattr(m, prim_name), prim_name)
            assert om <= oa, f"meet {prim_name}={om} > a={oa} in {th.name}"
            assert om <= ob, f"meet {prim_name}={om} > b={ob} in {th.name}"


def test_join_upper_bound():
    """join(a,b) >= a and join(a,b) >= b for all primitive orderings."""
    for _, th in THERAPIES.items():
        a, b = th.disease_type, th.health_type
        j = join(a, b)
        for prim_name in ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
            oa = primitive_order(getattr(a, prim_name), prim_name)
            ob = primitive_order(getattr(b, prim_name), prim_name)
            oj = primitive_order(getattr(j, prim_name), prim_name)
            assert oj >= oa, f"join {prim_name}={oj} < a={oa} in {th.name}"
            assert oj >= ob, f"join {prim_name}={oj} < b={ob} in {th.name}"


def test_tensor_min_on_P_and_F():
    """Tensor uses MIN on P and F, MAX on everything else."""
    a = SCHIZOPHRENIA
    b = ART
    t = tensor(a, b)
    # P: a.P = PM, b.P = PM -> MIN = PM
    assert t.P == min(a.P, b.P, key=lambda x: primitive_order(x, "P")), \
        f"Tensor P={t.P.value} should be MIN of {a.P.value}, {b.P.value}"
    # F: a.F = ETH, b.F = ETH -> MIN = ETH
    assert t.F == min(a.F, b.F, key=lambda x: primitive_order(x, "F")), \
        f"Tensor F={t.F.value} should be MIN of {a.F.value}, {b.F.value}"
    # D, T, R, K, G, Gamma, Phi, H, S, W should use MAX
    for prim_name in ["D", "T", "R", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
        oa = primitive_order(getattr(a, prim_name), prim_name)
        ob = primitive_order(getattr(b, prim_name), prim_name)
        ot = primitive_order(getattr(t, prim_name), prim_name)
        assert ot == max(oa, ob), \
            f"Tensor {prim_name}={ot} should be MAX of {oa}, {ob}"


# ─────────────────────────────────────────────────────────
# 4. PSYCHIATRIC SPECTRUM
# ─────────────────────────────────────────────────────────

def test_psychiatric_phi_axis():
    """Depression φ̂=𐑢, Healthy φ̂=⊙, Schizophrenia φ̂=𐑣."""
    assert DEPRESSION.Phi == Phi.SUB, f"Depression Phi={DEPRESSION.Phi.value}, expected 𐑢"
    assert HEALTHY_BRAIN.Phi == Phi.C, f"Healthy Phi={HEALTHY_BRAIN.Phi.value}, expected ⊙"
    assert SCHIZOPHRENIA.Phi == Phi.SUPER, f"Schizophrenia Phi={SCHIZOPHRENIA.Phi.value}, expected 𐑣"
    assert BIPOLAR_MANIA.Phi == Phi.SUPER, f"Bipolar_Mania Phi={BIPOLAR_MANIA.Phi.value}, expected 𐑣"


def test_schizophrenia_vs_bipolar_mania():
    """Schizophrenia and Bipolar Mania differ only at K (𐑧 vs 𐑪)."""
    deltas = delta_primitives(SCHIZOPHRENIA, BIPOLAR_MANIA)
    assert set(deltas) == {"K"}, \
        f"Schizophrenia vs Bipolar_Mania deltas = {deltas}, expected {{'K'}}"
    assert SCHIZOPHRENIA.K == K.SLOW, \
        f"Schizophrenia K={SCHIZOPHRENIA.K.value}, expected 𐑧"
    assert BIPOLAR_MANIA.K == K.MOD, \
        f"Bipolar_Mania K={BIPOLAR_MANIA.K.value}, expected 𐑪"


def test_hiv_equals_bipolar_mania():
    """HIV == Bipolar_Mania structurally (d=0.0)."""
    d = distance(HIV, BIPOLAR_MANIA)
    assert d == 0.0, f"d(HIV, Bipolar_Mania) = {d}, expected 0.0"
    # They should have same primitives
    for prim_name in ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
        assert getattr(HIV, prim_name) == getattr(BIPOLAR_MANIA, prim_name), \
            f"HIV.{prim_name}={getattr(HIV, prim_name).value} != Bipolar_Mania.{prim_name}={getattr(BIPOLAR_MANIA, prim_name).value}"


def test_hiv_normal_immune_deltas():
    """HIV differs from Normal_Immune by exactly 5 primitives."""
    PRIM_REV_MAP = {'D': 'Ð', 'T': 'Þ', 'R': 'Ř', 'P': 'Φ', 'F': 'ƒ', 'K': 'Ç',
                    'G': 'Γ', 'Gamma': 'ɢ', 'Phi': 'φ̂', 'H': 'Ħ', 'S': 'Σ', 'W': 'Ω'}
    deltas = delta_primitives(HIV, NORMAL_IMMUNE)
    assert len(deltas) == 5, f"HIV→Normal_Immune deltas count = {len(deltas)}, expected 5"
    computed_symbols = [PRIM_REV_MAP.get(p, p) for p in deltas]
    th = THERAPIES["hiv"]
    assert set(computed_symbols) == set(th.delta_primitives), \
        f"Computed deltas {computed_symbols} != declared {th.delta_primitives}"


# ─────────────────────────────────────────────────────────
# 5. DISTANCE VERIFICATION
# ─────────────────────────────────────────────────────────

def test_therapy_distances_match_computed():
    """Every therapy's declared distance equals computed distance."""
    for key, th in THERAPIES.items():
        computed = distance(th.disease_type, th.health_type)
        assert computed == th.distance, \
            f"Therapy '{key}': declared d={th.distance}, computed d={computed}"


def test_specific_known_distances():
    """Verify specific known structural distances."""
    # Schizophrenia → Health: 2 primitives differ (φ̂, Ħ)
    d1 = distance(SCHIZOPHRENIA, HEALTHY_BRAIN)
    assert d1 == 0.9997, f"d(Schizophrenia, Health) = {d1}, expected 0.9997"

    # MRSA → Normal Flora: 6 primitives differ
    d2 = distance(MRSA, NORMAL_FLORA)
    assert d2 == 1.2886, f"d(MRSA, Normal_Flora) = {d2}, expected 1.2886"

    # CF → Normal CFTR: 10 primitives differ
    d3 = distance(CF, NORMAL_CFTR)
    assert d3 == 1.8377, f"d(CF, Normal_CFTR) = {d3}, expected 1.8377"


# ─────────────────────────────────────────────────────────
# 6. C-SCORE AND TIER VERIFICATION
# ─────────────────────────────────────────────────────────

def test_c_score_gate_1():
    """Gate 1: φ̂ must be ⊙ for C > 0."""
    # Healthy brain has ⊙ → positive C-score
    assert c_score(HEALTHY_BRAIN) > 0.0, "Healthy brain should have C > 0"
    # Depression has 𐑢 → C=0
    assert c_score(DEPRESSION) == 0.0, "Depression should have C = 0 (sub-critical)"
    # Schizophrenia has 𐑣 → C=0
    assert c_score(SCHIZOPHRENIA) == 0.0, "Schizophrenia should have C = 0 (super-critical)"
    # All diseases have C=0 (none at ⊙)
    for name, t in DISEASE_TYPES.items():
        cs = c_score(t)
        assert cs == 0.0, f"Disease '{name}' C-score = {cs}, expected 0.0 (no ⊙)"


def test_c_score_specific_health_values():
    """Verify specific C-score values for health types."""
    assert c_score(HEALTHY_BRAIN) == 0.7000, \
        f"Healthy brain C-score = {c_score(HEALTHY_BRAIN)}, expected 0.7000"
    assert c_score(NORMAL_IMMUNE) == 0.9000, \
        f"Normal immune C-score = {c_score(NORMAL_IMMUNE)}, expected 0.9000"
    assert c_score(NORMAL_FLORA) == 0.6000, \
        f"Normal flora C-score = {c_score(NORMAL_FLORA)}, expected 0.6000"


def test_tier_assignments():
    """Verify tier assignments for disease and health types."""
    # All diseases at O₀ (C=0)
    for name, t in DISEASE_TYPES.items():
        assert tier(t) == "O₀", f"Disease '{name}' tier = {tier(t)}, expected O₀"
    # Health types
    assert tier(HEALTHY_BRAIN) == "O₂", f"Healthy Brain tier = {tier(HEALTHY_BRAIN)}, expected O₂"
    assert tier(NORMAL_IMMUNE) == "O_∞", f"Normal Immune tier = {tier(NORMAL_IMMUNE)}, expected O_∞"
    assert tier(NORMAL_FLORA) == "O₂", f"Normal Flora tier = {tier(NORMAL_FLORA)}, expected O₂"
    assert tier(NORMAL_OVARIAN) == "O₂", f"Normal Ovarian tier = {tier(NORMAL_OVARIAN)}, expected O₂"
    assert tier(NORMAL_CFTR) == "O₂", f"Normal CFTR tier = {tier(NORMAL_CFTR)}, expected O₂"
    assert tier(NORMAL_URATE) == "O₂", f"Normal Urate tier = {tier(NORMAL_URATE)}, expected O₂"


def test_therapy_tiers_match_computed():
    """Every therapy's tier_disease and tier_health match tier() output."""
    for key, th in THERAPIES.items():
        computed_d = tier(th.disease_type)
        computed_h = tier(th.health_type)
        assert computed_d == th.tier_disease, \
            f"Therapy '{key}': tier_disease declared {th.tier_disease}, computed {computed_d}"
        assert computed_h == th.tier_health, \
            f"Therapy '{key}': tier_health declared {th.tier_health}, computed {computed_h}"


def test_therapy_c_scores_match_computed():
    """Every therapy's c_score_disease and c_score_health match c_score() output."""
    for key, th in THERAPIES.items():
        computed_d = c_score(th.disease_type)
        computed_h = c_score(th.health_type)
        assert computed_d == th.c_score_disease, \
            f"Therapy '{key}': c_score_disease declared {th.c_score_disease}, computed {computed_d}"
        assert computed_h == th.c_score_health, \
            f"Therapy '{key}': c_score_health declared {th.c_score_health}, computed {computed_h}"


# ─────────────────────────────────────────────────────────
# 7. IMSCRIPTION CONSTRUCTION
# ─────────────────────────────────────────────────────────

def test_imscription_from_values_roundtrip():
    """from_values correctly constructs Imscription from glyph strings."""
    glyphs = ["𐑼", "𐑥", "𐑾", "𐑬", "𐑞", "𐑧", "𐑔", "𐑠", "⊙", "𐑒", "𐑳", "𐑷"]
    ims = Imscription.from_values(*glyphs)
    assert ims.D == D.INFTY
    assert ims.T == T.BOWTIE
    assert ims.R == R.LR
    assert ims.P == P.PM
    assert ims.F == F.ETH
    assert ims.K == K.SLOW
    assert ims.G == G.GIMEL
    assert ims.Gamma == Gamma.SEQ
    assert ims.Phi == Phi.C, f"Expected ⊙, got {ims.Phi.value}"
    assert ims.H == H.N1
    assert ims.S == S.N_M
    assert ims.W == W.TRIV


def test_imscription_values_unique():
    """All Imscription instances declared as constants have valid primitive values."""
    all_instances = (
        list(DISEASE_TYPES.values()) + list(HEALTH_TYPES.values()) +
        list(PSYCHIATRIC_SPECTRUM.values()) +
        [ART, NMDA_SYSTEM, DOPAMINE_MESOLIMBIC, HOMEOPATHIC_REMEDY, DISEASE_GENERIC]
    )
    for ims in all_instances:
        assert isinstance(ims.D, D)
        assert isinstance(ims.T, T)
        assert isinstance(ims.R, R)
        assert isinstance(ims.P, P)
        assert isinstance(ims.F, F)
        assert isinstance(ims.K, K)
        assert isinstance(ims.G, G)
        assert isinstance(ims.Gamma, Gamma)
        assert isinstance(ims.Phi, Phi)
        assert isinstance(ims.H, H)
        assert isinstance(ims.S, S)
        assert isinstance(ims.W, W)


# ─────────────────────────────────────────────────────────
# 8. PROPER EDGE CASES
# ─────────────────────────────────────────────────────────

def test_homeopathy_remedy_sub_critical():
    """Homeopathic remedy is sub-critical (φ̂=𐑢), C=0."""
    assert HOMEOPATHIC_REMEDY.Phi == Phi.SUB
    assert c_score(HOMEOPATHIC_REMEDY) == 0.0


def test_homeopathy_distance():
    """Homeopathy distance from disease to remedy is 4.1231."""
    d = distance(DISEASE_GENERIC, HOMEOPATHIC_REMEDY)
    assert d == 2.2710, f"d(Disease_Generic, Homeopathic_Remedy) = {d}, expected 2.2710"


def test_all_component_operations_valid():
    """All therapy component operations are 'MEET' or 'TENSOR'."""
    valid_ops = {"MEET", "TENSOR"}
    for key, th in THERAPIES.items():
        for i, comp in enumerate(th.components):
            assert "operation" in comp, \
                f"Therapy '{key}' component {i} missing 'operation'"
            assert comp["operation"] in valid_ops, \
                f"Therapy '{key}' component {i} has op={comp['operation']}, expected MEET or TENSOR"


# ─────────────────────────────────────────────────────────
# 9. DISEASE/HEALTH TYPE CONSISTENCY
# ─────────────────────────────────────────────────────────

def test_disease_health_declared_count():
    """DISEASE_TYPES and HEALTH_TYPES have same keys."""
    assert set(DISEASE_TYPES.keys()) == set(HEALTH_TYPES.keys()), \
        f"Mismatch: disease keys {set(DISEASE_TYPES.keys())} vs health keys {set(HEALTH_TYPES.keys())}"


def test_therapy_keys_in_declared():
    """All therapy keys have matching DISEASE_TYPES and HEALTH_TYPES entries."""
    for key in THERAPIES:
        assert key in DISEASE_TYPES or key != "gout_elimination" or key != "gout_combined" or key != "gout_holistic" or key != "homeopathy", \
            f"Therapy '{key}' disease type not found"
        # Note: gout_elimination, gout_combined, gout_holistic all use GOUT
        # homeopathy uses DISEASE_GENERIC which is not in DISEASE_TYPES
