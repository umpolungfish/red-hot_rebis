_HELP_EXAMPLES = """  rebis.py run frob_design"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])
if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
    _doc = __doc__.strip() if __doc__ else "scripts/frob_design.py"
    print(_doc)
    print()
    info_line("Examples:")
    print(_HELP_EXAMPLES)
    print()
    _sys.exit(0)

import sys, os, json, math
from pathlib import Path
_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REBIS_ROOT)
sys.path.insert(0, '/home/mrnob0dy666/imscribing_grammar')
sys.path.insert(0, os.path.join(_REBIS_ROOT, 'rhr_p4rky'))
from ch3mpiler_serpentrod_pipeline import *
sys.path.insert(0, os.path.join(_REBIS_ROOT, 'designs/gr33ngroblin'))
from plastic_eater_design import *
from shared.rich_output import *


def design_site_frobenius_exact(plastic_name, bond_name, fg1_name, fg2_name, mechanism):
    """
    Frobenius-exact catalytic site design.
    
    Strategy: For each complementary pair (A,B), activate the AA for the member
    with the higher ordinal percentile in the site type. This ensures exactly one
    member per pair is activated → 6/6 pair coverage (dominant-member rule).
    
    The site type is computed via v2 complement (structurally correct).
    """
    bond_t = ALL_BOND_TYPES.get(bond_name, {})
    fg1_t = ALL_FG.get(fg1_name, {})
    fg2_t = ALL_FG.get(fg2_name, {})
    bond_type = {p: bond_t.get(p, '?') for p in PNAMES}
    fg1_type = {p: fg1_t.get(p, '?') for p in PNAMES}
    fg2_type = {p: fg2_t.get(p, '?') for p in PNAMES}
    fused = fuse_reaction_types(bond_type, fg1_type, fg2_type)
    site_type = complement_type_v2(fused)  # v2: structurally correct complement
    
    # AA design: dominant-member rule for each complementary pair
    aas = [None] * 12
    activated = set()
    
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        pa_idx = PNAMES.index(pa)
        pb_idx = PNAMES.index(pb)
        pa_o = glyph_ord(pa, site_type.get(pa, '?'))
        pb_o = glyph_ord(pb, site_type.get(pb, '?'))
        pa_max = len(GLYPH_ORDINALS.get(pa, {})) - 1
        pb_max = len(GLYPH_ORDINALS.get(pb, {})) - 1
        pa_pct = pa_o / pa_max if pa_max > 0 else 0
        pb_pct = pb_o / pb_max if pb_max > 0 else 0
        
        # Activate the dominant member (higher percentile)
        if pa_pct >= pb_pct:
            aas[pa_idx] = PRIMITIVE_TO_AA.get(pa)
            activated.add(pa)
            aas[pb_idx] = None  # structural AA placeholder
        else:
            aas[pb_idx] = PRIMITIVE_TO_AA.get(pb)
            activated.add(pb)
            aas[pa_idx] = None
    
    # Fill structural AAs
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
    
    # Pair status
    pair_status = []
    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        pa_o = glyph_ord(pa, site_type.get(pa, '?'))
        pb_o = glyph_ord(pb, site_type.get(pb, '?'))
        pa_max = len(GLYPH_ORDINALS.get(pa, {})) - 1
        pb_max = len(GLYPH_ORDINALS.get(pb, {})) - 1
        pa_pct = pa_o / pa_max if pa_max > 0 else 0
        pb_pct = pb_o / pb_max if pb_max > 0 else 0
        dominant = pa if pa_pct >= pb_pct else pb
        pair_status.append({
            "pair": f"{pa}-{pb}",
            "dominant": dominant,
            "activated": pa if pa in activated else pb,
            "pa_pct": round(pa_pct, 2),
            "pb_pct": round(pb_pct, 2),
        })
    
    return {
        "plastic": plastic_name, "bond": bond_name, "mechanism": mechanism,
        "fg_pair": f"{fg1_name} + {fg2_name}",
        "fused_type": fused, "site_type": site_type,
        "aa_sequence": "".join(final_aas), "rna_sequence": rna,
        "pairs_covered": 6,  # always 6 with dominant-member rule
        "confidence": 1.0,
        "activated": sorted(activated),
        "pair_status": pair_status,
    }

# Run
info_line("=" * 72)
info_line("  v5 FROBENIUS-EXACT: Dominant-Member Rule per Complementary Pair")
info_line("  Every pair has exactly 1 member activated → 6/6 coverage")
info_line("=" * 72)

all_sites = []
for plastic_name, bond_name, fg1_name, fg2_name, mechanism in PLASTIC_TARGETS:
    s = design_site_frobenius_exact(plastic_name, bond_name, fg1_name, fg2_name, mechanism)
    all_sites.append(s)
    info_line(f"\n--- {plastic_name} ---")
    info_line(f"  Bond: {bond_name}")
    info_line(f"  AA:   {s['aa_sequence']}")
    info_line(f"  Activated: {s['activated']}")
    for ps in s['pair_status']:
        info_line(f"    {ps['pair']:8s}  dominant={ps['dominant']:2s}  act={ps['activated']:2s}  pcts=({ps['pa_pct']:.2f},{ps['pb_pct']:.2f})")
    info_line(f"  Site: {json.dumps(s['site_type'])}")

# Diversity
info_line("\n" + "=" * 72)
info_line("  AA SEQUENCE DIVERSITY")
aas_seen = {}
for s in all_sites:
    seq = s['aa_sequence']
    if seq not in aas_seen:
        aas_seen[seq] = []
    aas_seen[seq].append(s['plastic'])
info_line(f"  Unique AA sequences: {len(aas_seen)}/{len(all_sites)}")
for seq, plastics in aas_seen.items():
    info_line(f"  {seq}")
    for p in plastics:
        info_line(f"    <- {p}")

# Clustering suggestion
info_line("\n" + "=" * 72)
info_line("  CLUSTERING FOR SEPARATE CATALYSTS")
# Group by identical site types
groups = {}
for s in all_sites:
    st = json.dumps(s['site_type'], sort_keys=True)
    if st not in groups:
        groups[st] = []
    groups[st].append(s['plastic'])

info_line(f"  Unique site types: {len(groups)}")
for i, (st, plastics) in enumerate(groups.items()):
    info_line(f"  Group {i+1}: {plastics}")
    # Show the site type for the first member
    for s in all_sites:
        if s['plastic'] == plastics[0]:
            info_line(f"    AA: {s['aa_sequence']}")
            break

# Also group by AA sequence
info_line(f"\n  Unique AA sequences: {len(aas_seen)}")
for i, (seq, plastics) in enumerate(aas_seen.items()):
    info_line(f"  Catalyst {i+1}: {plastics}")
    info_line(f"    AA: {seq}")
