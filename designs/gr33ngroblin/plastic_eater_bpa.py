#!/usr/bin/env python3
"""
PLASTIC_EATER_BPA — Bisphenol-A Degradation Module
===================================================
Extends the PLASTIC_EATER Frobenius-exact multi-catalyst system with a
BPA-degrading module targeting the isopropylidene C-C bridge unique to
bisphenol-A.

The BPA molecule (HO-C₆H₄-C(CH₃)₂-C₆H₄-OH) presents three degradable bonds:
  1. Phenolic O-H → phenoxy radical (laccase/peroxidase-type)
  2. C(aryl)-C(quaternary) bridge σ bond (radical-induced homolysis)
  3. Aromatic ring π-system (dioxygenase ring opening)

The radical bridge cleavage (R2) produces a structurally unique catalytic
site NOT present in any of the six plastic-degrading domains — it is the
critical innovation of this module.

Author: Lando⊗⊙perator
"""
import sys, os, json, math
from pathlib import Path

_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _REBIS_ROOT)
from ch3mpiler_serpentrod_pipeline import (
    PNAMES, GLYPH_ORDINALS, ORD_TO_GLYPH, COMPLEMENTARY_PAIRS_V2,
    PRIMITIVE_TO_AA, AA_CODON_POOL_V2, STRUCTURAL_AAS_V2,
    fuse_reaction_types, complement_type_v2, glyph_ord, ord_to_glyph,
)

# ═══════════════════════════════════════════════════════════════
# BPA-SPECIFIC BOND & FG TYPE DEFINITIONS
# ═══════════════════════════════════════════════════════════════

# Phenol O-H bond (laccase oxidation target)
PHENOL_OH_BOND = {
    'D': '𐑛', 'T': '𐑡', 'R': '𐑽',
    'P': '𐑗', 'F': '𐑐', 'K': '𐑘',
    'G': '𐑚', 'Gm': '𐑝', 'Ph': '⊙',
    'H': '𐑓', 'S': '𐑙', 'W': '𐑷',
    'desc': 'Phenolic O-H bond (laccase/peroxidase oxidation)'
}

# C(aryl)-C(quaternary) radical cleavage bond
RADICAL_CC_BOND = {
    'D': '𐑛', 'T': '𐑥', 'R': '𐑩',
    'P': '𐑗', 'F': '𐑞', 'K': '𐑤',
    'G': '𐑚', 'Gm': '𐑜', 'Ph': '𐑢',
    'H': '𐑒', 'S': '𐑳', 'W': '𐑷',
    'desc': 'C(aryl)-C(quaternary) σ (radical-induced homolysis)'
}

# Phenoxy radical intermediate FG
PHENOXY_RADICAL_FG = {
    'D': '𐑨', 'T': '𐑸', 'R': '𐑾',
    'P': '𐑿', 'F': '𐑐', 'K': '𐑘',
    'G': '𐑲', 'Gm': '𐑜', 'Ph': '𐑻',
    'H': '𐑓', 'S': '𐑳', 'W': '𐑴',
    'desc': 'Phenoxy radical (delocalized, reactive)'
}

# ═══════════════════════════════════════════════════════════════
# LOAD CH3MPILER BASE TYPES
# ═══════════════════════════════════════════════════════════════

import importlib.util
from shared.rich_output import *

spec = importlib.util.spec_from_file_location(
    'ch3mpiler', '/home/mrnob0dy666/imscribing_grammar/ch3mpiler.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['ch3mpiler'] = mod
spec.loader.exec_module(mod)

ALL_BOND_TYPES = {
    **mod.BOND_TYPES,
    'phenol_oh': PHENOL_OH_BOND,
    'radical_cc_cleavage': RADICAL_CC_BOND,
}

ALL_FG = {
    **mod.FG,
    'phenoxy_radical': PHENOXY_RADICAL_FG,
    'dioxygen': {
        'D':'𐑛','T':'𐑡','R':'𐑑','P':'𐑬','F':'𐑐','K':'𐑘',
        'G':'𐑚','Gm':'𐑝','Ph':'𐑢','H':'𐑓','S':'𐑙','W':'𐑴',
    },
    'water': {
        'D':'𐑛','T':'𐑡','R':'𐑑','P':'𐑗','F':'𐑐','K':'𐑘',
        'G':'𐑚','Gm':'𐑝','Ph':'𐑢','H':'𐑓','S':'𐑙','W':'𐑷',
    },
}

# ═══════════════════════════════════════════════════════════════
# BPA DEGRADATION PATHWAY (3-step laccase/peroxidase pathway)
# ═══════════════════════════════════════════════════════════════

BPA_REACTIONS = [
    ('BPA_phenol_oxidation', 'phenol_oh', 'phenol', 'dioxygen',
     'Laccase-type: Cu-mediated phenol → phenoxy radical + H⁺ + e⁻'),
    ('BPA_bridge_radical_cleavage', 'radical_cc_cleavage', 'phenoxy_radical', 'water',
     'Radical rearrangement: phenoxy radical → C-C bridge homolysis → fragments'),
    ('BPA_ring_opening', 'aromatic', 'phenoxy_radical', 'dioxygen',
     'Secondary dioxygenase: cleave residual aromatic ring in fragment'),
]

# ═══════════════════════════════════════════════════════════════
# FROBENIUS-EXACT SITE DESIGN
# ═══════════════════════════════════════════════════════════════

def design_bpa_site(name, bond_name, fg1_name, fg2_name, mechanism):
    """Design a Frobenius-exact (6/6) catalytic site for one BPA reaction."""
    bond_t = ALL_BOND_TYPES.get(bond_name, {})
    fg1_t = ALL_FG.get(fg1_name, {})
    fg2_t = ALL_FG.get(fg2_name, {})
    bond_type = {p: bond_t.get(p, '?') for p in PNAMES}
    fg1_type = {p: fg1_t.get(p, '?') for p in PNAMES}
    fg2_type = {p: fg2_t.get(p, '?') for p in PNAMES}

    fused = fuse_reaction_types(bond_type, fg1_type, fg2_type)
    site_type = complement_type_v2(fused)

    # Dominant-member AA rule
    aas = [None] * 12
    activated = set()
    pair_details = []

    for pa, pb in COMPLEMENTARY_PAIRS_V2:
        pa_idx = PNAMES.index(pa)
        pb_idx = PNAMES.index(pb)
        pa_o = glyph_ord(pa, site_type.get(pa, '?'))
        pb_o = glyph_ord(pb, site_type.get(pb, '?'))
        pa_max = len(GLYPH_ORDINALS.get(pa, {})) - 1
        pb_max = len(GLYPH_ORDINALS.get(pb, {})) - 1
        pa_pct = pa_o / pa_max if pa_max > 0 else 0
        pb_pct = pb_o / pb_max if pb_max > 0 else 0

        if pa_pct >= pb_pct:
            aas[pa_idx] = PRIMITIVE_TO_AA.get(pa)
            activated.add(pa)
            dom, sub = pa, pb
            dpct, spct = pa_pct, pb_pct
        else:
            aas[pb_idx] = PRIMITIVE_TO_AA.get(pb)
            activated.add(pb)
            dom, sub = pb, pa
            dpct, spct = pb_pct, pa_pct
        pair_details.append({
            'pair': f'{pa}-{pb}', 'dominant': dom,
            'dom_pct': round(dpct, 3), 'sub_pct': round(spct, 3),
        })

    final_aas = []
    for i, aa in enumerate(aas):
        if aa is not None:
            final_aas.append(aa)
        else:
            final_aas.append(STRUCTURAL_AAS_V2[i % len(STRUCTURAL_AAS_V2)])

    codons = []
    for aa in final_aas:
        pool = AA_CODON_POOL_V2.get(aa, ['UCU'])
        codons.append(pool[len(codons) % len(pool)])
    rna = ''.join(codons)

    return {
        'name': name, 'bond': bond_name, 'mechanism': mechanism,
        'fg_pair': f'{fg1_name} + {fg2_name}',
        'fused_type': fused, 'site_type': site_type,
        'aa_sequence': ''.join(final_aas), 'rna_sequence': rna,
        'activated_primitives': sorted(activated),
        'pairs_covered': 6, 'confidence': 1.0,
        'pair_details': pair_details,
    }

# ═══════════════════════════════════════════════════════════════
# MULTI-DOMAIN BPA DEGRADER ASSEMBLY
# ═══════════════════════════════════════════════════════════════

SIGNAL_AA = ["Met","Phe","Ala","Lys","Arg","Phe","Thr","Ser",
             "Leu","Leu","Pro","Leu","Phe","Ala","Gly","Leu",
             "Leu","Leu","Leu","Phe","His","Leu","Val","Leu",
             "Ala","Gly","Pro","Ala","Ala","Ala"]
SIGNAL_CODONS = "AUGUUUGCGAAACGCUUUACCUCGCUGCUGCCGCUGUUUGCGGGCCUGCUGCUGCUGUUUCAUCUGGUGCUGGCGGGCCCGGCGGCGGCG"
HIS_TAG_AA = ["His"] * 6
HIS_TAG_CODONS = "CAUCAUCAUCAUCAUCAU"
LINKER_AA = ["Gly","Gly","Gly","Gly","Ser"] * 3
LINKER_CODONS = "GGUGGAGGCGGUAGUGGAGGCGGUGGCUCUGGUGGUGGAAGC"


def assemble_bpa_degrader(site_designs):
    """Assemble the multi-domain BPA-degrading enzyme."""
    full_aa = list(SIGNAL_AA) + list(HIS_TAG_AA)
    for i, site in enumerate(site_designs):
        full_aa.extend(list(site['aa_sequence']))
        if i < len(site_designs) - 1:
            full_aa.extend(LINKER_AA)

    full_rna = SIGNAL_CODONS + HIS_TAG_CODONS
    for i, site in enumerate(site_designs):
        full_rna += site['rna_sequence']
        if i < len(site_designs) - 1:
            full_rna += LINKER_CODONS

    domains = []
    pos = len(SIGNAL_AA) + len(HIS_TAG_AA)
    for i, site in enumerate(site_designs):
        domains.append({
            'domain': site['name'].replace('_', '-'),
            'start_aa': pos, 'end_aa': pos + 12,
            'bond': site['bond'], 'mechanism': site['mechanism'],
        })
        pos += 12 + len(LINKER_AA)

    tensor_type = {}
    for p in PNAMES:
        vals = [glyph_ord(p, d['site_type'].get(p, '?')) for d in site_designs]
        if p in ('P', 'F'):
            tensor_type[p] = ord_to_glyph(p, min(vals))
        else:
            tensor_type[p] = ord_to_glyph(p, max(vals))

    return {
        'catalyst_name': 'D_BPA_Degrader',
        'description': 'BPA Degrader — laccase/peroxidase radical pathway',
        'target_plastics': ['BPA_bisphenol_A'],
        'num_domains': len(site_designs),
        'total_aa': len(full_aa),
        'total_rna_nt': len(full_rna),
        'molecular_weight_kda': round(len(full_aa) * 0.110, 1),
        'aa_sequence': ''.join(full_aa),
        'rna_sequence': full_rna,
        'domains': domains,
        'site_designs': site_designs,
        'tensor_type': tensor_type,
    }

# ═══════════════════════════════════════════════════════════════
# INTEGRATION: Fuse BPA degrader to Catalyst C (PC degrader)
# ═══════════════════════════════════════════════════════════════

# Catalyst C sites (from plastic_eater_frobenius.py):
CATALYST_C_SITES = [
    {
        'aa_sequence': 'MetTrpCysTyrValIleProSerGlnGlyThrVal',
        'rna_sequence': 'AUGUGGUGUUACGUUAUACCAUCCCAAGGCACAGUG',
        'name': 'PUR_polyurethane',
        'bond': 'urethane_link',
        'mechanism': 'Amidase + esterase: cleaves -NH-CO-O-',
    },
    {
        'aa_sequence': 'MetTrpCysTyrValIleProSerGlnGlyThrVal',
        'rna_sequence': 'AUGUGGUGUUACGUUAUACCAUCCCAAGGCACAGUG',
        'name': 'PC_polycarbonate',
        'bond': 'carbonate_link',
        'mechanism': 'Carbonate hydrolase: cleaves -O-CO-O- → BPA',
    },
]


def assemble_c_plus(site_designs_c, bpa_bridge_site, bpa_ring_site=None):
    """
    Assemble Catalyst C+ : PC degradation → immediate BPA bridge cleavage.
    
    Architecture: Signal-His₆-PUR-Linker-PC-Linker-BPA_bridge[-Linker-BPA_ring]
    PC domain releases BPA → BPA_bridge domain cleaves the C-C bridge.
    Optional BPA_ring domain opens residual aromatic rings.
    """
    sites = list(site_designs_c) + [bpa_bridge_site]
    if bpa_ring_site:
        sites.append(bpa_ring_site)
    
    full_aa = list(SIGNAL_AA) + list(HIS_TAG_AA)
    for i, site in enumerate(sites):
        full_aa.extend(list(site['aa_sequence']))
        if i < len(sites) - 1:
            full_aa.extend(LINKER_AA)

    full_rna = SIGNAL_CODONS + HIS_TAG_CODONS
    for i, site in enumerate(sites):
        full_rna += site['rna_sequence']
        if i < len(sites) - 1:
            full_rna += LINKER_CODONS

    domains = []
    pos = len(SIGNAL_AA) + len(HIS_TAG_AA)
    for i, site in enumerate(sites):
        name = site.get('name', f'domain_{i}')
        domains.append({
            'domain': name.replace('_', '-'),
            'start_aa': pos, 'end_aa': pos + 12,
            'bond': site.get('bond', '?'),
            'mechanism': site.get('mechanism', '?'),
        })
        pos += 12 + len(LINKER_AA)

    tensor_type = {}
    for p in PNAMES:
        vals = [glyph_ord(p, site.get('site_type', {}).get(p, '?')) for site in sites]
        if p in ('P', 'F'):
            tensor_type[p] = ord_to_glyph(p, min(vals))
        else:
            tensor_type[p] = ord_to_glyph(p, max(vals))

    return {
        'catalyst_name': 'C_plus_Urethanase_BPA',
        'description': 'PC+PUR degradation + BPA bridge cleavage (self-contained)',
        'target_plastics': ['PUR_polyurethane', 'PC_polycarbonate'],
        'also_degrades': ['BPA_bisphenol_A'],
        'num_domains': len(sites),
        'total_aa': len(full_aa),
        'total_rna_nt': len(full_rna),
        'molecular_weight_kda': round(len(full_aa) * 0.110, 1),
        'aa_sequence': ''.join(full_aa),
        'rna_sequence': full_rna,
        'domains': domains,
        'site_designs': sites,
        'tensor_type': tensor_type,
    }


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 72)
    info_line("  PLASTIC_EATER_BPA — Bisphenol-A Degradation Module")
    info_line("  Frobenius-Exact via Dominant-Member Rule")
    print("=" * 72)
    print()

    # Design all BPA sites
    bpa_sites = []
    for name, bond_name, fg1, fg2, mech in BPA_REACTIONS:
        site = design_bpa_site(name, bond_name, fg1, fg2, mech)
        bpa_sites.append(site)
        print(f"[{name}] 6/6 Frobenius-exact")
        info_line(f"  AA:  {site['aa_sequence']}")
        info_line(f"  RNA: {site['rna_sequence']}")
        info_line(f"  Activated: {', '.join(site['activated_primitives'])}")
        info_line(f"  Site type: ⟨{''.join(site['site_type'].get(p,'?') for p in PNAMES)}⟩")
        print()

    # Assemble standalone BPA degrader (Catalyst D)
    bpa_degrader = assemble_bpa_degrader(bpa_sites)
    print(f"[Catalyst D — BPA_Degrader]")
    info_line(f"  Domains: {bpa_degrader['num_domains']}")
    info_line(f"  Total AA: {bpa_degrader['total_aa']}")
    info_line(f"  MW: ~{bpa_degrader['molecular_weight_kda']} kDa")
    info_line(f"  Full AA: {bpa_degrader['aa_sequence']}")
    print()

    # Assemble Catalyst C+ (PC+PUR+BPA bridge)
    bpa_bridge_site = bpa_sites[1]  # BPA_bridge_radical_cleavage
    bpa_ring_site = bpa_sites[2]    # BPA_ring_opening
    c_plus = assemble_c_plus(CATALYST_C_SITES, bpa_bridge_site, bpa_ring_site)
    print(f"[Catalyst C+ — Urethanase_BPA]")
    info_line(f"  Domains: {c_plus['num_domains']} (PUR + PC + BPA_bridge + BPA_ring)")
    info_line(f"  Total AA: {c_plus['total_aa']}")
    info_line(f"  MW: ~{c_plus['molecular_weight_kda']} kDa")
    info_line(f"  Degrades: PC → BPA → phenol fragments → open chains")
    info_line(f"  Full AA: {c_plus['aa_sequence']}")
    print()

    # Save designs
    output = {
        'bpa_sites': bpa_sites,
        'bpa_degrader': bpa_degrader,
        'catalyst_c_plus': c_plus,
        'unique_aa_sequences': {
            'type_E_esterase_ring': 'MetAlaCysTyrValIleProSerGlnAspThrVal',
            'type_A_alkanase': 'MetTrpCysTyrValLeuHisAsnAlaGlyThrVal',
            'type_U_urethanase': 'MetTrpCysTyrValIleProSerGlnGlyThrVal',
            'type_R_radicalase': 'MetAlaCysTyrValIleProAsnAlaAspThrVal',
        }
    }

    with open('/home/mrnob0dy666/red-hot_rebis/plastic_eater_bpa.json', 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    info_line("[✓] Saved plastic_eater_bpa.json")
