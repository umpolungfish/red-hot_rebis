#!/usr/bin/env python3
"""
Frobenius-Exact Plastic-Degrading Enzyme Design
================================================
Fixes the complement and AA design to achieve true 6/6 (AND logic) 
Frobenius pair coverage. Creates 2-3 separate catalysts as needed.

Key fixes:
  1. complement_type_v3: Inverse mapping (low→high, high→low) 
     instead of proportional cross-mapping
  2. design_site_aas_from_type_v3: AND logic for pair counting,
     force both members of each incomplete pair
  3. Cluster plastics by structural compatibility
"""

import sys, json, math
from pathlib import Path

_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REBIS_ROOT)
sys.path.insert(0, '/home/mrnob0dy666/imscribing_grammar')

from ch3mpiler_serpentrod_pipeline import (
    PNAMES, GLYPH_ORDINALS, ORD_TO_GLYPH, COMPLEMENTARY_PAIRS_V2,
    PRIMITIVE_TO_AA, AA_CODON_POOL_V2, STRUCTURAL_AAS_V2,
    fuse_reaction_types, glyph_ord, ord_to_glyph,
)

from plastic_eater_design import (
    ALL_BOND_TYPES, ALL_FG, PLASTIC_TARGETS,
    LINKER_AA, LINKER_CODONS, SIGNAL_AA, SIGNAL_CODONS,
    HIS_TAG_AA, HIS_TAG_CODONS,
)

# ═══════════════════════════════════════════════════════════════
# FIX 1: Inverse complement — Frobenius-exact mapping
# ═══════════════════════════════════════════════════════════════

def complement_type_v3(fused_type):
    """Frobenius-exact structural complement using INVERSE mapping.
    
    For complementary pair (A,B):
      site[A] = INVERSE(fused[B])  — high when fused[B] is low
      site[B] = INVERSE(fused[A])  — high when fused[A] is low
    
    The inverse maps ordinal o → (max_o - o) within each primitive's
    range, then cross-maps to the partner's range.
    """
    site = {}
    for prim_a, prim_b in COMPLEMENTARY_PAIRS_V2:
        a_max = len(GLYPH_ORDINALS.get(prim_a, {})) - 1
        b_max = len(GLYPH_ORDINALS.get(prim_b, {})) - 1
        
        # Get fused ordinals
        fused_a = glyph_ord(prim_a, fused_type.get(prim_a, '?'))
        fused_b = glyph_ord(prim_b, fused_type.get(prim_b, '?'))
        
        # INVERSE within own range, then cross-map to partner's range
        # inv_a = a_max - fused_a  (low→high, high→low within A)
        # site[prim_b] = round(inv_a / a_max * b_max)  mapped to B's range
        inv_a = a_max - fused_a
        inv_b = b_max - fused_b
        
        if a_max > 0:
            site[prim_b] = ord_to_glyph(prim_b, min(b_max, max(0, round(inv_a / a_max * b_max))))
        else:
            site[prim_b] = ord_to_glyph(prim_b, b_max)
        
        if b_max > 0:
            site[prim_a] = ord_to_glyph(prim_a, min(a_max, max(0, round(inv_b / b_max * a_max))))
        else:
            site[prim_a] = ord_to_glyph(prim_a, a_max)
    
    return site


# ═══════════════════════════════════════════════════════════════
# FIX 2: True AND-logic pair enforcement for AA design
# ═══════════════════════════════════════════════════════════════

def design_site_aas_from_type_v3(site_type):
    """Design 12-AA sequence with TRUE Frobenius enforcement (AND logic).
    
    Step 1: Activate primitives with ordinal >= 50% of max
    Step 2: Count pairs where BOTH members are activated
    Step 3: Force-activate BOTH members of any incomplete pair
    Step 4: Fill remaining with structural AAs
    """
    aas = [None] * 12
    activated = set()
    
    # Step 1: Natural activation (>= 50% ordinal)
    for i, prim in enumerate(PNAMES):
        o = glyph_ord(prim, site_type.get(prim, '?'))
        max_o = len(GLYPH_ORDINALS.get(prim, {})) - 1
        if max_o > 0 and o / max_o >= 0.5:
            aa = PRIMITIVE_TO_AA.get(prim)
            if aa:
                aas[i] = aa
                activated.add(prim)
    
    # Step 2: Count true pairs (AND logic)
    def count_true_pairs(act_set):
        return sum(1 for pa, pb in COMPLEMENTARY_PAIRS_V2 
                   if pa in act_set and pb in act_set)
    
    true_pairs = count_true_pairs(activated)
    
    # Step 3: Force both members of incomplete pairs
    # Priority: activate the member with higher site ordinal first
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        if pa in activated and pb in activated:
            continue  # pair already complete
        
        # Find positions and ordinals
        pa_idx = PNAMES.index(pa)
        pb_idx = PNAMES.index(pb)
        pa_o = glyph_ord(pa, site_type.get(pa, '?'))
        pb_o = glyph_ord(pb, site_type.get(pb, '?'))
        pa_max = len(GLYPH_ORDINALS.get(pa, {})) - 1
        pb_max = len(GLYPH_ORDINALS.get(pb, {})) - 1
        pa_pct = pa_o / pa_max if pa_max > 0 else 0
        pb_pct = pb_o / pb_max if pb_max > 0 else 0
        
        # Activate the one with higher percentile (more natural fit)
        # But if neither is activated, activate both
        candidates = []
        if pa not in activated:
            candidates.append((pa_pct, pa, pa_idx))
        if pb not in activated:
            candidates.append((pb_pct, pb, pb_idx))
        
        for _, prim, idx in sorted(candidates, reverse=True):
            if aas[idx] is None:
                aas[idx] = PRIMITIVE_TO_AA.get(prim)
                activated.add(prim)
    
    true_pairs = count_true_pairs(activated)
    
    # Step 4: Fill remaining slots with structural AAs
    final_aas = []
    for i, aa in enumerate(aas):
        if aa is not None:
            final_aas.append(aa)
        else:
            final_aas.append(STRUCTURAL_AAS_V2[i % len(STRUCTURAL_AAS_V2)])
    
    return final_aas, true_pairs


def aas_to_rna_v3(aas):
    """Encode AA sequence to RNA codons (same as v2)."""
    codons = []
    for aa in aas:
        pool = AA_CODON_POOL_V2.get(aa, ["UCU"])
        codons.append(pool[len(codons) % len(pool)])
    return "".join(codons)


# ═══════════════════════════════════════════════════════════════
# Design single site with v3 functions
# ═══════════════════════════════════════════════════════════════

def design_single_site_v3(plastic_name, bond_name, fg1_name, fg2_name, mechanism):
    """Design a Frobenius-exact catalytic site for one plastic."""
    bond_t = ALL_BOND_TYPES.get(bond_name, {})
    fg1_t = ALL_FG.get(fg1_name, {})
    fg2_t = ALL_FG.get(fg2_name, {})
    
    bond_type = {p: bond_t.get(p, '?') for p in PNAMES}
    fg1_type = {p: fg1_t.get(p, '?') for p in PNAMES}
    fg2_type = {p: fg2_t.get(p, '?') for p in PNAMES}
    
    fused = fuse_reaction_types(bond_type, fg1_type, fg2_type)
    site_type = complement_type_v3(fused)
    aas, pairs = design_site_aas_from_type_v3(site_type)
    rna = aas_to_rna_v3(aas)
    
    # Show which primitives are activated
    activated = set()
    for i, prim in enumerate(PNAMES):
        o = glyph_ord(prim, site_type.get(prim, '?'))
        max_o = len(GLYPH_ORDINALS.get(prim, {})) - 1
        if max_o > 0 and o / max_o >= 0.5:
            activated.add(prim)
    
    # Also show force-activated ones
    force_activated = []
    for i, prim in enumerate(PNAMES):
        o = glyph_ord(prim, site_type.get(prim, '?'))
        max_o = len(GLYPH_ORDINALS.get(prim, {})) - 1
        naturally = (max_o > 0 and o / max_o >= 0.5)
        if prim in activated and not naturally:
            force_activated.append(prim)
    
    return {
        "plastic": plastic_name,
        "bond": bond_name,
        "mechanism": mechanism,
        "fg_pair": f"{fg1_name} + {fg2_name}",
        "fused_type": fused,
        "site_type": site_type,
        "aa_sequence": aas,
        "rna_sequence": rna,
        "pairs_covered": pairs,
        "confidence": min(1.0, pairs / 6.0),
        "naturally_activated": sorted([p for p in PNAMES if p in activated and p not in force_activated]),
        "force_activated": sorted(force_activated),
    }


# ═══════════════════════════════════════════════════════════════
# MAIN: Test v3 on all plastics
# ═══════════════════════════════════════════════════════════════

print("=" * 72)
print("  FROBENIUS-EXACT DESIGN (v3 — Inverse Complement + AND Logic)")
print("=" * 72)
print()

all_sites = []
for plastic_name, bond_name, fg1_name, fg2_name, mechanism in PLASTIC_TARGETS:
    site = design_single_site_v3(plastic_name, bond_name, fg1_name, fg2_name, mechanism)
    all_sites.append(site)
    
    print(f"--- {plastic_name} ---")
    print(f"  Bond: {bond_name}  FG: {fg1_name}+{fg2_name}")
    print(f"  Pairs covered (AND): {site['pairs_covered']}/6")
    print(f"  Natural activation: {site['naturally_activated']}")
    print(f"  Force activation:   {site['force_activated']}")
    
    # Per-pair detail
    activated_set = set(site['naturally_activated'] + site['force_activated'])
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        a_act = pa in activated_set
        b_act = pb in activated_set
        status = "OK" if (a_act and b_act) else "FAIL"
        a_sym = "Y" if a_act else "N"
        b_sym = "Y" if b_act else "N"
        print(f"    {pa}-{pb}: {pa}={a_sym} {pb}={b_sym}  [{status}]")
    
    print(f"  Site type: {json.dumps(site['site_type'])}")
    print(f"  AA: {''.join(site['aa_sequence'])}")
    print()

print()
print("=" * 72)
print("  CLUSTERING ANALYSIS")
print("=" * 72)

# Group plastics by structural compatibility (shared failure patterns)
# If all achieve 6/6 individually, 1 catalyst may suffice
# If not, group by which pairs need force-activation

achieved_6 = [s for s in all_sites if s['pairs_covered'] == 6]
not_6 = [s for s in all_sites if s['pairs_covered'] < 6]

print(f"\nAchieved 6/6: {len(achieved_6)}/{len(all_sites)}")
for s in achieved_6:
    print(f"  {s['plastic']}: force={s['force_activated']}")

if not_6:
    print(f"\nDid NOT achieve 6/6: {len(not_6)}")
    for s in not_6:
        print(f"  {s['plastic']}: pairs={s['pairs_covered']}/6")

# For clustering: compute site type distances between all pairs
print("\nSite type distances (ordinal Euclidean):")
for i, s1 in enumerate(all_sites):
    for j, s2 in enumerate(all_sites):
        if i >= j:
            continue
        dist = 0
        for prim in PNAMES:
            o1 = glyph_ord(prim, s1['site_type'].get(prim, '?'))
            o2 = glyph_ord(prim, s2['site_type'].get(prim, '?'))
            max_o = len(GLYPH_ORDINALS.get(prim, {})) - 1
            if max_o > 0:
                dist += ((o1 - o2) / max_o) ** 2
        dist = math.sqrt(dist)
        print(f"  {s1['plastic'][:20]:20s} <-> {s2['plastic'][:20]:20s}  d={dist:.3f}")
