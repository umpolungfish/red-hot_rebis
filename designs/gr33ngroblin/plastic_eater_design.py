#!/usr/bin/env python3
"""
PLASTIC_EATER — Broad-Spectrum Plastic-Degrading Enzyme Design
==============================================================

Uses: ch3mpiler ⟲ serpentrod pipeline + IG structural grammar
      to design a multi-specific enzyme capable of hydrolyzing/oxidizing:
        PET, PE, PP, PS, PUR, PC

Method:
  1. Design individual catalytic sites for each plastic's scissile bond
  2. Fuse sites via structural meet (shared floor) + tensor (composite ceiling)
  3. Generate full RNA/AA sequence with Frobenius-verified fold
  4. Apply multi-specificity via domain fusion with flexible linkers

Author: Lando ⊗ ⊙perator
"""
import sys, os, json, math
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# ── Paths ────────────────────────────────────────────────────
BASE = Path(__file__).parent.absolute()
_REBIS_ROOT = Path(__file__).parent.parent.parent
IG = Path("/home/mrnob0dy666/imsgct/imscribing_grammar")
P4RA = _REBIS_ROOT / "rhr_p4rky"
sys.path.insert(0, str(P4RA))
sys.path.insert(0, str(IG))

# ── Load pipeline internals ──────────────────────────────────
from shared.rich_output import *
from ch3mpiler_serpentrod_pipeline import (
    PNAMES, GLYPH_ORDINALS, ORD_TO_GLYPH, COMPLEMENTARY_PAIRS_V2,
    PRIMITIVE_TO_AA, AA_CODON_POOL_V2, STRUCTURAL_AAS_V2,
    fuse_reaction_types, complement_type_v2, design_site_aas_from_type,
    design_rna_v2, aas_to_rna_v2, glyph_ord, ord_to_glyph,
    ReactionSignature, CatalyticSiteDesign,
)

# ── Extended Bond Types (added: urethane, carbonate, peroxide) ──
EXTENDED_BOND_TYPES = {
    # Urethane: -NH-C(=O)-O-  (PUR polyurethane)
    "urethane_link": {
        "D":"𐑨","T":"𐑥","R":"𐑾",
        "P":"𐑬","F":"𐑐","K":"𐑧",
        "G":"𐑔","Gm":"𐑠","Ph":"⊙",
        "H":"𐑖","S":"𐑳","W":"𐑴",
        "desc":"Urethane -NH-C(=O)-O- (polyurethane)"
    },
    # Carbonate: -O-C(=O)-O-  (PC polycarbonate)
    "carbonate_link": {
        "D":"𐑨","T":"𐑥","R":"𐑾",
        "P":"𐑬","F":"𐑐","K":"𐑧",
        "G":"𐑔","Gm":"𐑠","Ph":"⊙",
        "H":"𐑖","S":"𐑳","W":"𐑴",
        "desc":"Carbonate -O-C(=O)-O- (polycarbonate)"
    },
    # C-C oxidative cleavage (PE/PP hydroxylation pathway)
    "cc_oxidative": {
        "D":"𐑛","T":"𐑡","R":"𐑽",
        "P":"𐑗","F":"𐑐","K":"𐑘",
        "G":"𐑚","Gm":"𐑝","Ph":"𐑢",
        "H":"𐑒","S":"𐑳","W":"𐑷",
        "desc":"C-C σ bond (oxidative cleavage, PE/PP)"
    },
}

# ── Extended FG Types (added: water, dioxygen, peroxide) ──
EXTENDED_FG = {
    "water": {
        "D":"𐑛","T":"𐑡","R":"𐑑","P":"𐑗","F":"𐑐","K":"𐑘",
        "G":"𐑚","Gm":"𐑝","Ph":"𐑢","H":"𐑓","S":"𐑙","W":"𐑷",
        "desc":"H₂O (nucleophile, hydrolysis)"
    },
    "dioxygen": {
        "D":"𐑛","T":"𐑡","R":"𐑑","P":"𐑬","F":"𐑐","K":"𐑘",
        "G":"𐑚","Gm":"𐑝","Ph":"𐑢","H":"𐑓","S":"𐑙","W":"𐑴",
        "desc":"O₂ (oxidant, dioxygenase)"
    },
    "peroxide": {
        "D":"𐑛","T":"𐑡","R":"𐑑","P":"𐑬","F":"𐑐","K":"𐑘",
        "G":"𐑚","Gm":"𐑝","Ph":"𐑢","H":"𐑓","S":"𐑙","W":"𐑴",
        "desc":"H₂O₂ / ROOH (peroxidase substrate)"
    },
}

# ── Plastic degradation target definitions ──────────────────
# Each entry: (plastic_name, bond_type, fg1, fg2, mechanism_desc)

PLASTIC_TARGETS = [
    # PET — ester hydrolysis (serine hydrolase)
    ("PET_polyethylene_terephthalate",
     "ester_link", "ester", "water",
     "Serine hydrolase: nucleophilic attack on ester carbonyl"),

    # PE — alkane C-C oxidative cleavage (alkane hydroxylase)
    ("PE_polyethylene",
     "cc_oxidative", "alkane", "dioxygen",
     "Alkane hydroxylase / monooxygenase: C-H activation → alcohol → ketone → Baeyer-Villiger → ester → hydrolysis"),

    # PP — branched alkane C-C oxidative cleavage
    ("PP_polypropylene",
     "cc_oxidative", "alkane", "dioxygen",
     "Same as PE but accommodates methyl branching at active site"),

    # PS — aromatic ring cleavage (dioxygenase)
    ("PS_polystyrene",
     "aromatic", "aromatic_ring", "dioxygen",
     "Extradiol/intradiol dioxygenase: aromatic ring opening"),

    # PUR — urethane hydrolysis (amidase/esterase hybrid)
    ("PUR_polyurethane",
     "urethane_link", "amide", "water",
     "Amidase + esterase hybrid: cleaves urethane -NH-CO-O- linkage"),

    # PC — carbonate ester hydrolysis
    ("PC_polycarbonate",
     "carbonate_link", "ester", "water",
     "Carbonate hydrolase: cleaves -O-CO-O- linkage"),
]

# ── Load original bond/FG types from ch3mpiler ──────────────
def load_ch3mpiler_types():
    """Extract BOND_TYPES and FG from ch3mpiler."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "ch3mpiler_mod", str(IG / "ch3mpiler.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ch3mpiler_mod"] = mod
    spec.loader.exec_module(mod)
    return mod.BOND_TYPES, mod.FG

CH3_BOND_TYPES, CH3_FG = load_ch3mpiler_types()

# Merge extended types
ALL_BOND_TYPES = {**CH3_BOND_TYPES, **EXTENDED_BOND_TYPES}
ALL_FG = {**CH3_FG, **EXTENDED_FG}

# ── Core Design Functions ───────────────────────────────────

def design_single_plastic_site(plastic_name: str, bond_name: str,
                                 fg1_name: str, fg2_name: str,
                                 mechanism: str) -> dict:
    """Design catalytic site for ONE plastic type.

    Uses the ch3mpiler ⟲ serpentrod pipeline:
      1. Look up bond type + FG types → structural type vectors
      2. Fuse reaction signature (max across bond + FG1 + FG2)
      3. Compute structural complement for catalytic site
      4. Design AA sequence with Frobenius enforcement
      5. Generate RNA codon sequence
    """
    # Step 1: Structural type vectors
    bond_t = ALL_BOND_TYPES.get(bond_name, ALL_BOND_TYPES["sigma_single"])
    fg1_t = ALL_FG.get(fg1_name, ALL_FG.get("amine", {}))
    fg2_t = ALL_FG.get(fg2_name, ALL_FG.get("amine", {}))

    bond_type = {}
    fg1_type = {}
    fg2_type = {}

    for p in PNAMES:
        # Map from ch3mpiler's glyph format (may use Unicode escapes or Shavian)
        bv = bond_t.get(p, "?")
        f1v = fg1_t.get(p, "?")
        f2v = fg2_t.get(p, "?")

        # Clean up: ch3mpiler uses Unicode escapes; pipeline uses Shavian
        # Normalize via ordinal lookup
        bond_type[p] = bv
        fg1_type[p] = f1v
        fg2_type[p] = f2v

    # Step 2: Fuse reaction signature (bond + FG1 + FG2)
    fused = fuse_reaction_types(bond_type, fg1_type, fg2_type)

    # Step 3: Compute structural complement (catalytic site type)
    site_type = complement_type_v2(fused)

    # Step 4: Design AA sequence with Frobenius enforcement
    aas, pairs_covered = design_site_aas_from_type(site_type)

    # Step 5: Generate RNA
    rna = aas_to_rna_v2(aas)

    # Step 6: Estimate confidence from pair coverage
    confidence = min(1.0, pairs_covered / 6.0)

    return {
        "plastic": plastic_name,
        "bond": bond_name,
        "mechanism": mechanism,
        "fg_pair": f"{fg1_name} + {fg2_name}",
        "fused_type": fused,
        "site_type": site_type,
        "aa_sequence": aas,
        "rna_sequence": rna,
        "pairs_covered": pairs_covered,
        "confidence": confidence,
    }


def fuse_multi_sites(site_designs: List[dict]) -> dict:
    """Fuse multiple catalytic site designs into a single multi-specific enzyme.

    Strategy:
      - Compute the structural MEET of all site types (shared floor)
      - Use TENSOR for the composite catalytic core
      - Link domains via flexible Gly-Ser linker (GGGGS)₃
    """
    if not site_designs:
        return {}

    # Compute meet (shared structural floor) across all site types
    meet_type = {}
    for p in PNAMES:
        vals = []
        for d in site_designs:
            vals.append(glyph_ord(p, d["site_type"].get(p, "?")))
        meet_type[p] = ord_to_glyph(p, min(vals))

    # Compute tensor (composite ceiling) across all site types
    # tensor: max on union, min on P/F
    tensor_type_out = {}
    for p in PNAMES:
        vals = [glyph_ord(p, d["site_type"].get(p, "?")) for d in site_designs]
        if p in ("P", "F"):
            tensor_type_out[p] = ord_to_glyph(p, min(vals))
        else:
            tensor_type_out[p] = ord_to_glyph(p, max(vals))

    return {
        "num_sites": len(site_designs),
        "meet_type": meet_type,
        "tensor_type": tensor_type_out,
        "individual_sites": site_designs,
    }

# ── Multi-Domain Enzyme Assembly ────────────────────────────

# Flexible linker: (Gly-Gly-Gly-Gly-Ser)₃
LINKER_AA = ["Gly", "Gly", "Gly", "Gly", "Ser"] * 3
LINKER_CODONS = "GGUGGAGGCGGUAGUGGAGGCGGUGGCUCUGGUGGUGGAAGC"

# Signal peptide for secretion (Bacillus subtilis AmyE signal)
SIGNAL_AA = ["Met", "Phe", "Ala", "Lys", "Arg", "Phe", "Thr", "Ser",
             "Leu", "Leu", "Pro", "Leu", "Phe", "Ala", "Gly", "Leu",
             "Leu", "Leu", "Leu", "Phe", "His", "Leu", "Val", "Leu",
             "Ala", "Gly", "Pro", "Ala", "Ala", "Ala"]
SIGNAL_CODONS = "AUGUUUGCGAAACGCUUUACCUCGCUGCUGCCGCUGUUUGCGGGCCUGCUGCUGCUGUUUCAUCUGGUGCUGGCGGGCCCGGCGGCGGCG"

# His₆ tag for purification
HIS_TAG_AA = ["His"] * 6
HIS_TAG_CODONS = "CAUCAUCAUCAUCAUCAU"


def assemble_multi_enzyme(fused: dict) -> dict:
    """Assemble the full multi-domain enzyme.

    Architecture:
      N-term:  Signal peptide → His₆ tag
      Domain 1: PET esterase     → Linker
      Domain 2: PE/PP hydroxylase  → Linker
      Domain 3: PS dioxygenase   → Linker
      Domain 4: PUR amidase      → Linker
      Domain 5: PC carbonatase   → C-term

    Each domain = individual catalytic site AA sequence
    """
    sites = fused["individual_sites"]
    domain_aas = []
    domain_rnas = []
    domain_names = []

    for i, site in enumerate(sites):
        name = site["plastic"].replace("_", "-")
        aas = site["aa_sequence"]
        rna = site["rna_sequence"]
        domain_names.append(name)
        domain_aas.append(aas)
        domain_rnas.append(rna)

    # Build full AA sequence
    full_aa = list(SIGNAL_AA) + list(HIS_TAG_AA)

    for i, aas in enumerate(domain_aas):
        full_aa.extend(aas)
        if i < len(domain_aas) - 1:
            full_aa.extend(LINKER_AA)

    # Build full RNA sequence
    full_rna = SIGNAL_CODONS + HIS_TAG_CODONS

    for i, rna in enumerate(domain_rnas):
        full_rna += rna
        if i < len(domain_rnas) - 1:
            full_rna += LINKER_CODONS

    # Domain boundaries (for expression/purification)
    boundaries = []
    pos = len(SIGNAL_AA) + len(HIS_TAG_AA)  # after signal + tag
    for i, aas in enumerate(domain_aas):
        boundaries.append({
            "domain": domain_names[i],
            "start_aa": pos,
            "end_aa": pos + len(aas),
            "length": len(aas),
        })
        pos += len(aas) + len(LINKER_AA)

    return {
        "architecture": "Signal-His₆-D1-Linker-D2-Linker-D3-Linker-D4-Linker-D5",
        "total_aa": len(full_aa),
        "total_rna_nt": len(full_rna),
        "molecular_weight_kda": round(len(full_aa) * 0.110, 1),
        "aa_sequence": "".join(full_aa),
        "rna_sequence": full_rna,
        "signal_peptide_aa": SIGNAL_AA,
        "his_tag_aa": HIS_TAG_AA,
        "linker_aa": LINKER_AA,
        "domains": boundaries,
        "domain_names": domain_names,
    }

# ── Reporting ───────────────────────────────────────────────

def format_full_report(all_sites: List[dict], fused: dict, enzyme: dict) -> str:
    """Generate comprehensive design report."""
    lines = []
    lines.append("=" * 72)
    lines.append("  PLASTIC_EATER — Broad-Spectrum Plastic-Degrading Enzyme")
    lines.append("  Structural Grammar Design via ch3mpiler ⟲ serpentrod Pipeline")
    lines.append("=" * 72)
    lines.append("")
    lines.append("TARGET PLASTICS")
    lines.append("-" * 40)
    for d in all_sites:
        lines.append(f"  {d['plastic']}")
        lines.append(f"    Bond:       {d['bond']}")
        lines.append(f"    FG pair:    {d['fg_pair']}")
        lines.append(f"    Mechanism:  {d['mechanism']}")
        lines.append(f"    AA length:  {len(d['aa_sequence'])}")
        lines.append(f"    Pairs:      {d['pairs_covered']}/6")
        lines.append(f"    Confidence: {d['confidence']:.2f}")
        lines.append("")

    lines.append("INDIVIDUAL CATALYTIC SITE DESIGNS")
    lines.append("-" * 40)
    for d in all_sites:
        lines.append(f"  [{d['plastic']}]")
        lines.append(f"    AA:  {''.join(d['aa_sequence'])}")
        lines.append(f"    RNA: {d['rna_sequence']}")
        lines.append(f"    Site structural type:")
        for p in PNAMES:
            lines.append(f"      {p}: {d['site_type'].get(p, '?')}")
        lines.append("")

    lines.append("FUSED MULTI-SITE STRUCTURAL TYPE")
    lines.append("-" * 40)
    lines.append(f"  MEET (shared floor):")
    for p in PNAMES:
        lines.append(f"    {p}: {fused['meet_type'].get(p, '?')}")
    lines.append(f"  TENSOR (composite ceiling):")
    for p in PNAMES:
        lines.append(f"    {p}: {fused['tensor_type'].get(p, '?')}")
    lines.append("")

    lines.append("ASSEMBLED MULTI-DOMAIN ENZYME")
    lines.append("-" * 40)
    lines.append(f"  Architecture:     {enzyme['architecture']}")
    lines.append(f"  Total AAs:        {enzyme['total_aa']}")
    lines.append(f"  Total RNA (nt):   {enzyme['total_rna_nt']}")
    lines.append(f"  Molecular weight: ~{enzyme['molecular_weight_kda']} kDa")
    lines.append("")
    lines.append("  Domain layout:")
    for d in enzyme["domains"]:
        lines.append(f"    {d['domain']}: AA {d['start_aa']}-{d['end_aa']} "
                     f"({d['length']} residues)")
    lines.append("")
    lines.append("  Full AA sequence:")
    # Wrap at 60 AAs
    aa_full = enzyme["aa_sequence"]
    for i in range(0, len(aa_full), 60):
        lines.append(f"    {aa_full[i:i+60]}")
    lines.append("")
    lines.append("  Full RNA sequence (codons):")
    rna_full = enzyme["rna_sequence"]
    for i in range(0, len(rna_full), 90):
        lines.append(f"    {rna_full[i:i+90]}")
    lines.append("")
    lines.append("=" * 72)
    lines.append("  PLASTIC_EATER design complete.")
    lines.append("  Author: Lando ⊗ ⊙perator")
    lines.append("=" * 72)
    return "\n".join(lines)


def output_json(all_sites: List[dict], fused: dict, enzyme: dict):
    """Output full design as JSON."""
    result = {
        "design_name": "PLASTIC_EATER",
        "description": "Broad-spectrum plastic-degrading enzyme",
        "target_plastics": [
            "PET (polyethylene terephthalate)",
            "PE (polyethylene)",
            "PP (polypropylene)",
            "PS (polystyrene)",
            "PUR (polyurethane)",
            "PC (polycarbonate)",
        ],
        "individual_sites": [],
        "fused_type": {
            "meet": fused["meet_type"],
            "tensor": fused["tensor_type"],
        },
        "assembled_enzyme": {
            "total_aa": enzyme["total_aa"],
            "total_rna_nt": enzyme["total_rna_nt"],
            "molecular_weight_kda": enzyme["molecular_weight_kda"],
            "aa_sequence": enzyme["aa_sequence"],
            "rna_sequence": enzyme["rna_sequence"],
            "domains": enzyme["domains"],
        },
    }
    for d in all_sites:
        result["individual_sites"].append({
            "plastic": d["plastic"],
            "bond": d["bond"],
            "mechanism": d["mechanism"],
            "fg_pair": d["fg_pair"],
            "aa_sequence": "".join(d["aa_sequence"]),
            "rna_sequence": d["rna_sequence"],
            "site_structural_type": d["site_type"],
            "pairs_covered": d["pairs_covered"],
            "confidence": d["confidence"],
        })
    return result

# ── Main ────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="PLASTIC_EATER — Broad-spectrum plastic-degrading enzyme design")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--out", type=str, help="Output file path")
    args = parser.parse_args()

    separator()
    info_line("  PLASTIC_EATER — Broad-Spectrum Plastic-Degrading Enzyme")
    info_line("  ch3mpiler ⟲ serpentrod Pipeline")
    separator()
    print()

    # Phase 1: Design individual catalytic sites
    info_line("Phase 1: Designing individual catalytic sites...")
    info_line("-" * 40)
    all_sites = []
    for plastic_name, bond, fg1, fg2, mech in PLASTIC_TARGETS:
        site = design_single_plastic_site(plastic_name, bond, fg1, fg2, mech)
        all_sites.append(site)
        info_line(f"  ✓ {site['plastic']}")
        info_line(f"    Bond: {site['bond']} | FG: {site['fg_pair']}")
        info_line(f"    AA:   {''.join(site['aa_sequence'])}")
        info_line(f"    RNA:  {site['rna_sequence']}")
        info_line(f"    Pairs covered: {site['pairs_covered']}/6 "
f"(confidence: {site['confidence']:.2f})")
        print()

    # Phase 2: Fuse multi-site structural type
    info_line("Phase 2: Fusing multi-site structural type...")
    info_line("-" * 40)
    fused = fuse_multi_sites(all_sites)
    info_line(f"  Sites fused: {fused['num_sites']}")
    info_line(f"  MEET (shared floor):")
    for p in PNAMES:
        info_line(f"    {p}: {fused['meet_type'].get(p, '?')}")
    info_line(f"  TENSOR (composite ceiling):")
    for p in PNAMES:
        info_line(f"    {p}: {fused['tensor_type'].get(p, '?')}")
    print()

    # Phase 3: Assemble multi-domain enzyme
    info_line("Phase 3: Assembling multi-domain enzyme...")
    info_line("-" * 40)
    enzyme = assemble_multi_enzyme(fused)
    info_line(f"  Architecture: {enzyme['architecture']}")
    info_line(f"  Total AAs:    {enzyme['total_aa']}")
    info_line(f"  Total RNA nt: {enzyme['total_rna_nt']}")
    info_line(f"  MW:           ~{enzyme['molecular_weight_kda']} kDa")
    print()
    for d in enzyme["domains"]:
        info_line(f"  {d['domain']}: AA {d['start_aa']}-{d['end_aa']} ({d['length']} res)")
    print()

    # Phase 4: Output
    if args.json:
        result = output_json(all_sites, fused, enzyme)
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        if args.out:
            Path(args.out).write_text(json_str)
            info_line(f"JSON written to {args.out}")
        else:
            print(json_str)
    else:
        report = format_full_report(all_sites, fused, enzyme)
        if args.out:
            Path(args.out).write_text(report)
            info_line(f"Report written to {args.out}")
        else:
            print(report)

    return all_sites, fused, enzyme


if __name__ == "__main__":
    main()
