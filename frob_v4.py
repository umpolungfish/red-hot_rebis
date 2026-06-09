import sys, json, math
from pathlib import Path
sys.path.insert(0, '/home/mrnob0dy666/p4rakernel/p4ramill_py')
sys.path.insert(0, '/home/mrnob0dy666/imscribing_grammar')
from ch3mpiler_serpentrod_pipeline import *
from plastic_eater_design import *

def complement_v4(fused):
    """v2 complement then Frobenius boost: for each pair, ensure
    both members reach >=50% by raising the lower to the higher's level."""
    # Step 1: v2 complement
    site = {}
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        a_max = len(GLYPH_ORDINALS.get(pa, {})) - 1
        b_max = len(GLYPH_ORDINALS.get(pb, {})) - 1
        src_a = glyph_ord(pa, fused.get(pa, '?'))
        src_b = glyph_ord(pb, fused.get(pb, '?'))
        cross_a = min(a_max, round(src_b / b_max * a_max)) if b_max > 0 else 0
        cross_b = min(b_max, round(src_a / a_max * b_max)) if a_max > 0 else 0
        site[pa] = ord_to_glyph(pa, cross_a)
        site[pb] = ord_to_glyph(pb, cross_b)
    
    # Step 2: Frobenius boost — for each pair, raise lower to match higher's percentile
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        a_max = len(GLYPH_ORDINALS.get(pa, {})) - 1
        b_max = len(GLYPH_ORDINALS.get(pb, {})) - 1
        a_o = glyph_ord(pa, site.get(pa, '?'))
        b_o = glyph_ord(pb, site.get(pb, '?'))
        a_pct = a_o / a_max if a_max > 0 else 1.0
        b_pct = b_o / b_max if b_max > 0 else 1.0
        target_pct = max(a_pct, b_pct, 0.5)
        if a_pct < target_pct:
            new_a = min(a_max, max(0, round(target_pct * a_max)))
            site[pa] = ord_to_glyph(pa, new_a)
        if b_pct < target_pct:
            new_b = min(b_max, max(0, round(target_pct * b_max)))
            site[pb] = ord_to_glyph(pb, new_b)
    return site

def design_site_v4(plastic_name, bond_name, fg1_name, fg2_name, mechanism):
    bond_t = ALL_BOND_TYPES.get(bond_name, {})
    fg1_t = ALL_FG.get(fg1_name, {})
    fg2_t = ALL_FG.get(fg2_name, {})
    bond_type = {p: bond_t.get(p, '?') for p in PNAMES}
    fg1_type = {p: fg1_t.get(p, '?') for p in PNAMES}
    fg2_type = {p: fg2_t.get(p, '?') for p in PNAMES}
    fused = fuse_reaction_types(bond_type, fg1_type, fg2_type)
    
    # v4 complement
    site_type = complement_v4(fused)
    
    # AA design with AND logic enforcement
    aas = [None] * 12
    activated = set()
    for i, prim in enumerate(PNAMES):
        o = glyph_ord(prim, site_type.get(prim, '?'))
        max_o = len(GLYPH_ORDINALS.get(prim, {})) - 1
        if max_o > 0 and o / max_o >= 0.5:
            aa = PRIMITIVE_TO_AA.get(prim)
            if aa:
                aas[i] = aa
                activated.add(prim)
    
    # Force both members of incomplete pairs
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        if pa in activated and pb in activated:
            continue
        pa_idx = PNAMES.index(pa)
        pb_idx = PNAMES.index(pb)
        if pa not in activated and aas[pa_idx] is None:
            aas[pa_idx] = PRIMITIVE_TO_AA.get(pa)
            activated.add(pa)
        if pb not in activated and aas[pb_idx] is None:
            aas[pb_idx] = PRIMITIVE_TO_AA.get(pb)
            activated.add(pb)
    
    true_pairs = sum(1 for pa, pb in COMPLEMENTARY_PAIRS_V2 if pa in activated and pb in activated)
    
    final_aas = []
    for i, aa in enumerate(aas):
        if aa is not None:
            final_aas.append(aa)
        else:
            final_aas.append(STRUCTURAL_AAS_V2[i % len(STRUCTURAL_AAS_V2)])
    
    # RNA
    codons = []
    for aa in final_aas:
        pool = AA_CODON_POOL_V2.get(aa, ["UCU"])
        codons.append(pool[len(codons) % len(pool)])
    rna = "".join(codons)
    
    # Categorize which were boosted
    v2_site = complement_type_v2(fused)
    boosted = []
    for prim in PNAMES:
        v2_o = glyph_ord(prim, v2_site.get(prim, '?'))
        v4_o = glyph_ord(prim, site_type.get(prim, '?'))
        if v4_o > v2_o:
            boosted.append(f"{prim}:{ord_to_glyph(prim,v2_o)}->{ord_to_glyph(prim,v4_o)}")
    
    return {
        "plastic": plastic_name, "bond": bond_name, "mechanism": mechanism,
        "fg_pair": f"{fg1_name} + {fg2_name}",
        "fused_type": fused, "site_type": site_type,
        "aa_sequence": "".join(final_aas), "rna_sequence": rna,
        "pairs_covered": true_pairs, "confidence": min(1.0, true_pairs / 6.0),
        "boosted": boosted,
    }

# Run all
print("=" * 72)
print("  v4 FROBENIUS-EXACT DESIGN (v2 complement + minimal boost)")
print("=" * 72)
all_sites = []
for plastic_name, bond_name, fg1_name, fg2_name, mechanism in PLASTIC_TARGETS:
    s = design_site_v4(plastic_name, bond_name, fg1_name, fg2_name, mechanism)
    all_sites.append(s)
    print(f"\n--- {plastic_name} ---")
    print(f"  Bond: {bond_name}")
    print(f"  Pairs: {s['pairs_covered']}/6  Boosted: {s['boosted']}")
    print(f"  AA: {s['aa_sequence']}")
    print(f"  Site: {json.dumps(s['site_type'])}")

# Show AA diversity
print("\n" + "=" * 72)
print("  AA SEQUENCE DIVERSITY")
aas_seen = set()
for s in all_sites:
    aas_seen.add(s['aa_sequence'])
print(f"  Unique AA sequences: {len(aas_seen)}/{len(all_sites)}")
for s in all_sites:
    print(f"  {s['plastic'][:25]:25s}  {s['aa_sequence']}")

# Distances
print("\n  SITE TYPE DISTANCES:")
for i, s1 in enumerate(all_sites):
    for j, s2 in enumerate(all_sites):
        if i >= j: continue
        d = math.sqrt(sum(((glyph_ord(p, s1['site_type'].get(p,'?')) - glyph_ord(p, s2['site_type'].get(p,'?'))) / max(1, len(GLYPH_ORDINALS.get(p,{}))-1))**2 for p in PNAMES))
        print(f"    {s1['plastic'][:20]:20s} <-> {s2['plastic'][:20]:20s}  d={d:.3f}")
