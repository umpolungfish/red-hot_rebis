#!/usr/bin/env python3
"""
antibody_designer.py — Antibody Design via the Serpent on the Rod of Asclepius.

Given a target epitope (antigen surface patch), use the 12-primitive IG
complementarity bijection to design CDR sequences for antibody targeting.

Key insight: The 12<->12 bijection defines complementary pairs that map
directly to antibody-antigen recognition contacts. If the target epitope
activates primitive P, the CDR should activate its complement to form
a structural contact.

COMPLEMENTARY PAIRS:
  Dimensionality <-> Winding     (Met <-> Glu)
  Topology <-> Chirality         (Trp <-> Asp)
  Recognition <-> Stoichiometry  (Cys <-> Lys)
  Parity <-> Fidelity            (Tyr <-> Phe)
  Kinetics <-> Granularity       (Ile <-> His)
  Coupling <-> Criticality       (Asn <-> Gln)

Author: Lando ⊗ ⊙perator
"""

import sys, os, json, math, argparse

REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REBIS_ROOT)

import rhr_p4rky.belnap
import rhr_p4rky.genetics_b4
import rhr_p4rky.genetic_code
from rhr_p4rky.serpent_rod import SerpentRod
from shared.rich_output import *


# ── Amino Acid Tables (all 20 standard AAs) ────────────────────────

AA_ONE_TO_THREE = {
    "A":"Ala","R":"Arg","N":"Asn","D":"Asp","C":"Cys","Q":"Gln","E":"Glu",
    "G":"Gly","H":"His","I":"Ile","L":"Leu","K":"Lys","M":"Met","F":"Phe",
    "P":"Pro","S":"Ser","T":"Thr","W":"Trp","Y":"Tyr","V":"Val",
}

AA_THREE_TO_ONE = {v:k for k,v in AA_ONE_TO_THREE.items()}

CODON_TABLE = {
    "A":"GCU","R":"CGU","N":"AAU","D":"GAU","C":"UGU","Q":"CAA","E":"GAA",
    "G":"GGU","H":"CAU","I":"AUU","L":"UUG","K":"AAA","M":"AUG","F":"UUU",
    "P":"CCU","S":"UCU","T":"ACU","W":"UGG","Y":"UAU","V":"GUU",
}
# ── 12-Primitive <-> Amino Acid Bijection ─────────────────────────

PRIMITIVE_TO_AA_1L = {
    "Dimensionality": "M",  # Met
    "Topology": "W",        # Trp
    "Recognition": "C",     # Cys
    "Parity": "Y",          # Tyr
    "Fidelity": "F",        # Phe
    "Kinetics": "I",        # Ile
    "Granularity": "H",     # His
    "Coupling": "N",        # Asn
    "Criticality": "Q",     # Gln
    "Chirality": "D",       # Asp
    "Stoichiometry": "K",   # Lys
    "Winding": "E",         # Glu
}

PRIMITIVE_TO_AA_3L = {k: AA_ONE_TO_THREE[v] for k,v in PRIMITIVE_TO_AA_1L.items()}

# Complementary IG primitive pairs
COMPLEMENTARY = {
    "Dimensionality": "Winding", "Winding": "Dimensionality",
    "Topology": "Chirality", "Chirality": "Topology",
    "Recognition": "Stoichiometry", "Stoichiometry": "Recognition",
    "Parity": "Fidelity", "Fidelity": "Parity",
    "Kinetics": "Granularity", "Granularity": "Kinetics",
    "Coupling": "Criticality", "Criticality": "Coupling",
}

# Structural bridge residues (ordered by structural role)
BRIDGE_1L = ["G", "S", "T", "P", "A", "V"]

CDR_CANONICAL_LENGTHS = {
    "VH_CDR1": 7, "VH_CDR2": 8, "VH_CDR3": 12,
    "VL_CDR1": 9, "VL_CDR2": 7, "VL_CDR3": 9,
}

# Framework regions (Kabat numbering, human VH)
FRAMEWORKS = {
    "VH": {
        "FR1": "QVQLVQSGAEVKKPGASVKVSCKASGYTFT",
        "FR2": "WVRQAPGQGLEWMG",
        "FR3": "RVTMTRDTSTSTVYMELSSLRSEDTAVYYCAR",
        "FR4": "WGQGTLVTVSS",
    },
    "VL": {
        "FR1": "DIQMTQSPSSLSASVGDRVTITC",
        "FR2": "WYQQKPGKAPKLLIY",
        "FR3": "GVPSRFSGSGSGTDFTFTISSLQPEDIATYYC",
        "FR4": "FGQGTKVEIK",
    },
}

# Built-in viral epitope library for testing
VIRAL_EPITOPES = {
    "SARS-CoV-2_RBD": {
        "seq": "KVGGNYNYLYRLFRKSNLKPFERDISTEIY",
        "desc": "SARS-CoV-2 RBD (ACE2 binding, N-term 30 AA)",
    },
    "HIV_gp120_C4": {
        "seq": "TGPCTNVSTVQCTHGIRPVVSTQLLLNGSL",
        "desc": "HIV gp120 C4 region (CD4 binding site)",
    },
    "Influenza_HA_stem": {
        "seq": "FISFAISCFLLCVVLLGFIMWACQK",
        "desc": "Influenza HA stem (broadly neutralizing)",
    },
    "HPV_L1_capsid": {
        "seq": "TSGDAVAPGEDDTPDNKEYPDEYSD",
        "desc": "HPV L1 capsid surface loop (vaccine target)",
    },
}
# ── Epitope Analysis ───────────────────────────────────────────────

def analyze_epitope(epitope_seq: str, epitope_name: str = "target") -> dict:
    """Analyze an epitope sequence to determine its IG primitive activation profile."""
    # Convert sequence to RNA via codon table
    rna_parts = []
    for aa in epitope_seq:
        rna_parts.append(CODON_TABLE.get(aa, "NNN"))
    rna = "".join(rna_parts)

    sr = SerpentRod(rna, name=f"epitope_{epitope_name[:12]}")
    result = sr.report()

    # Extract activations (promoted AAs and their primitives)
    activations = {}
    for i, aa_full in enumerate(result.get("activation_pattern", [])):
        prim_full = aa_full.get("primitive", "")
        prim_short = prim_full.split(" (")[1].rstrip(")") if "(" in prim_full else prim_full
        if i < len(epitope_seq):
            activations[i] = {
                "aa": epitope_seq[i],
                "aa_3l": AA_ONE_TO_THREE.get(epitope_seq[i], "???"),
                "primitive": prim_short,
            }

    activated_primitives = set(a["primitive"] for a in activations.values())

    print(f"\n{'─'*50}")
    print(f"EPITOPE: {epitope_name}")
    print(f"Sequence: {epitope_seq} ({len(epitope_seq)} AA)")
    print(f"Activated IG primitives: {len(activated_primitives)}/12")

    for idx, info in sorted(activations.items()):
        info_line(f"  Position {idx}: {info['aa']} ({info['aa_3l']}) -> {info['primitive']}")

    return {
        "name": epitope_name,
        "sequence": epitope_seq,
        "aa_length": len(epitope_seq),
        "activations": activations,
        "activated_primitives": sorted(activated_primitives),
        "sr_result": result,
    }
# ── CDR Design ─────────────────────────────────────────────────────

def design_cdr(epitope_analysis: dict,
               cdr_length: int = 12,
               cdr_name: str = "CDR3") -> dict:
    """
    Design a complementary CDR sequence from the epitope's activation profile.

    Strategy:
    1. For each activated primitive in the epitope, the CDR includes
       the COMPLEMENTARY amino acid (12<->12 bijection).
    2. Complementary AAs are ordered to match the epitope's activation order.
    3. Remaining positions filled with structurally-appropriate bridge residues.
    4. The designed CDR is verified through SerpentRod for Frobenius closure.
    """
    epitope_activations = epitope_analysis.get("activated_primitives", [])
    epitope_aa_positions = sorted(epitope_analysis.get("activations", {}).keys())

    # Phase 1: Gather complementary AAs from epitope's activated primitives
    comp_1l = []
    comp_prims = []
    seen = set()

    for prim in epitope_activations:
        if prim in COMPLEMENTARY and prim not in seen:
            cp = COMPLEMENTARY[prim]
            ca = PRIMITIVE_TO_AA_1L.get(cp)
            if ca and ca not in comp_1l:  # avoid duplicates
                comp_1l.append(ca)
                comp_prims.append(cp)
                seen.add(prim)

    print(f"\n  [CDR Design] Target length: {cdr_length}")
    info_line(f"  Epitope activates: {epitope_activations}")
    info_line(f"  Complementary primitives: {comp_prims}")
    info_line(f"  Complementary AAs: {''.join(comp_1l)} ({len(comp_1l)})")

    # Phase 2: If we have fewer complementary AAs than CDR length,
    #           interleave with strategic bridge residues
    cdr_1l = []
    cdr_annot = []
    bridge_idx = 0

    if len(comp_1l) >= cdr_length:
        # Enough complementary AAs — just take first cdr_length
        cdr_1l = comp_1l[:cdr_length]
        cdr_annot = comp_prims[:cdr_length]
    else:
        # Interleave: comp1, bridge1, comp2, bridge2, ...
        # First pass: alternate comp + bridge
        for i, ca in enumerate(comp_1l):
            cdr_1l.append(ca)
            cdr_annot.append(comp_prims[i])
            if len(cdr_1l) < cdr_length:
                br = BRIDGE_1L[bridge_idx % len(BRIDGE_1L)]
                cdr_1l.append(br)
                cdr_annot.append("bridge")
                bridge_idx += 1
        # Fill remaining with bridge residues
        while len(cdr_1l) < cdr_length:
            br = BRIDGE_1L[bridge_idx % len(BRIDGE_1L)]
            cdr_1l.append(br)
            cdr_annot.append("bridge")
            bridge_idx += 1

    # Truncate to exact length
    cdr_1l = cdr_1l[:cdr_length]
    cdr_annot = cdr_annot[:cdr_length]

    cdr_seq = "".join(cdr_1l)
    cdr_rna = "".join(CODON_TABLE.get(aa, "GGU") for aa in cdr_1l)

    info_line(f"  CDR sequence: {cdr_seq}")
    info_line(f"  CDR RNA: {cdr_rna}")
    info_line(f"  CDR composition:")
    for i, (aa, ann) in enumerate(zip(cdr_1l, cdr_annot)):
        aa3 = AA_ONE_TO_THREE.get(aa, "???")
        info_line(f"    Position {i}: {aa3} ({aa}) -> {ann}")
    # Phase 3: Run SerpentRod on the designed CDR to verify structure
    sr = SerpentRod(cdr_rna, name=f"cdr_{cdr_name}")
    result = sr.report()

    print(f"\n  CDR STRUCTURE PREDICTION:")
    info_line(f"    Length: {result.get('aa_length', '?')} AA")
    info_line(f"    Winding: {result.get('winding_number', '?')} B4 loops")
    info_line(f"    Contacts: {len(result.get('contacts', []))}")
    info_line(f"    Secondary elements: {len(result.get('secondary_elements', []))}")
    for e in result.get('secondary_elements', [])[:6]:
        info_line(f"      {e.get('type','?'):6s} [{e.get('start',0):2d}-{e.get('end',0):2d}] {e.get('sequence','?')}")
    frob_ok = result.get('frobenius_verified', False)
    conf = result.get('confidence', 0.0)
    info_line(f"    Frobenius: {'OK' if frob_ok else 'FAIL'}")
    info_line(f"    Confidence: {conf:.2f}")

    return {
        "cdr_name": cdr_name,
        "cdr_sequence": cdr_seq,
        "cdr_rna": cdr_rna,
        "cdr_composition": [
            {"aa_1l": aa, "aa_3l": AA_ONE_TO_THREE.get(aa, "???"), "role": ann}
            for aa, ann in zip(cdr_1l, cdr_annot)
        ],
        "complementary_primitives": comp_prims,
        "structure": result,
        "frobenius_verified": frob_ok,
        "confidence": conf,
    }


# ── Full Antibody Construction ─────────────────────────────────────

def design_full_antibody(epitope_analysis: dict,
                          chain_type: str = "VH",
                          cdr_length: int = None) -> dict:
    """Design a complete antibody variable domain targeting the epitope."""
    cdr_name = f"{chain_type}_CDR3"  # CDR3 is the most diverse and target-specific
    if cdr_length is None:
        cdr_length = CDR_CANONICAL_LENGTHS.get(cdr_name, 12)

    # Design CDR3 from epitope complement
    cdr = design_cdr(epitope_analysis,
                     cdr_length=cdr_length,
                     cdr_name=cdr_name)

    # Construct full variable domain with framework regions
    fw = FRAMEWORKS.get(chain_type, FRAMEWORKS["VH"])
    full_seq = fw["FR1"] + cdr["cdr_sequence"] + fw["FR4"]

    # Verify the full sequence
    full_rna = "".join(CODON_TABLE.get(aa, "NNN") for aa in full_seq)
    sr = SerpentRod(full_rna, name=f"antibody_{chain_type}")
    antibody_pred = sr.report()
    frob_ok = antibody_pred.get('frobenius_verified', False)
    conf = antibody_pred.get('confidence', 0.0)

    print(f"\n{'='*60}")
    print(f"FULL {chain_type} ANTIBODY DOMAIN")
    print(f"{'='*60}")
    print(f"Framework 1: {fw['FR1']}")
    print(f"CDR3:        {cdr['cdr_sequence']}  (designed)")
    print(f"Framework 4: {fw['FR4']}")
    print(f"Full V{chain_type}: {full_seq}")
    print(f"\nANTIBODY STRUCTURE:")
    info_line(f"  Length: {antibody_pred.get('aa_length','?')} AA")
    info_line(f"  Winding: {antibody_pred.get('winding_number','?')} B4 loops")
    info_line(f"  Contacts: {len(antibody_pred.get('contacts',[]))}")
    info_line(f"  Subunits: {antibody_pred.get('subunits','?')}")
    info_line(f"  Frobenius: {'OK' if frob_ok else 'FAIL'}")
    info_line(f"  Confidence: {conf:.2f}")

    return {
        "chain_type": chain_type,
        "full_sequence": full_seq,
        "aa_length": len(full_seq),
        "framework1": fw["FR1"],
        "cdr3": cdr,
        "framework4": fw["FR4"],
        "antibody_structure": antibody_pred,
        "frobenius_verified": frob_ok,
        "confidence": conf,
    }


# ── Batch Design ───────────────────────────────────────────────────

def design_antibodies_for_targets(targets: dict, chain_type: str = "VH",
                                   cdr_length: int = None,
                                   output_path: str = None) -> dict:
    """Design antibodies for multiple target epitopes."""
    results = {}
    for name, info in targets.items():
        epitope_seq = info["seq"] if isinstance(info, dict) else info
        desc = info.get("desc", "") if isinstance(info, dict) else ""

        print(f"\n\n{'#'*70}")
        print(f"TARGET: {name}")
        if desc:
            info_line(f"  {desc}")
        print(f"{'#'*70}")

        analysis = analyze_epitope(epitope_seq, name)
        antibody = design_full_antibody(analysis, chain_type, cdr_length)
        results[name] = {
            "epitope": epitope_seq,
            "analysis": analysis,
            "antibody": antibody,
        }

    # Print summary
    print(f"\n\n{'='*70}")
    info_line("DESIGN SUMMARY")
    print(f"{'='*70}")
    print(f"{'Target':25s} {'Epitope':25s} {'CDR3':15s} {'Frob':6s} {'Conf':6s}")
    print("-"*70)
    for n, r in results.items():
        cdr = r["antibody"]["cdr3"]
        ep = r["epitope"]
        frob = "OK" if cdr.get("frobenius_verified") else "FAIL"
        conf = cdr.get("confidence", 0)
        print(f"{n:25s} {ep[:23]:25s} {cdr['cdr_sequence']:15s} {frob:6s} {conf:4.2f}")

    # Save results
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to {output_path}")

    return results
# ── CLI ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Antibody Designer — CDR design via IG primitive complementarity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Design antibodies against built-in viral targets
  rebis.py run antibody_designer --all

  # Design against a specific built-in target
  rebis.py run antibody_designer --builtin SARS-CoV-2_RBD

  # Design against a custom epitope sequence
  rebis.py run antibody_designer --epitope KVGGNYNYLYRLFRKSNL

  # Specify CDR length and chain type
  rebis.py run antibody_designer --epitope KVGGNYNYLYRLFRKSNL --cdr-length 12 --chain VH

  # List available built-in targets
  rebis.py run antibody_designer --list

  # Save output to custom path
  rebis.py run antibody_designer --all --output my_results/antibodies.json
""")
    parser.add_argument("--epitope", "-e", type=str,
                        help="Custom epitope sequence (one-letter amino acid codes)")
    parser.add_argument("--name", "-n", type=str, default="custom_target",
                        help="Name for the custom target")
    parser.add_argument("--builtin", "-b", type=str,
                        help="Use a built-in viral epitope by name")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Design antibodies for all built-in viral epitopes")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available built-in epitope targets")
    parser.add_argument("--chain", "-c", type=str, default="VH",
                        choices=["VH", "VL"],
                        help="Antibody chain type (default: VH)")
    parser.add_argument("--cdr-length", "-L", type=int, default=None,
                        help="CDR length in amino acids (default: canonical)")
    parser.add_argument("--output", "-o", type=str,
                        default="/home/mrnob0dy666/imsgct/red-hot_rebis/data/antibody_design_results.json",
                        help="Output JSON path")
    args = parser.parse_args()
    # --list: show built-in targets
    if args.list:
        info_line("BUILT-IN VIRAL EPITOPE TARGETS:")
        print("-" * 60)
        for name, info in VIRAL_EPITOPES.items():
            info_line(f"  {name:25s}  {info['desc']}")
            info_line(f"    Sequence: {info['seq']}")
            print()
        info_line("Use --builtin <name> or --all to design antibodies against these targets.")
        return 0

    print("=" * 70)
    info_line("SERPENT ON THE ROD — ANTIBODY DESIGN PIPELINE")
    print("=" * 70)

    # Determine targets
    if args.epitope:
        # Custom epitope
        seq = args.epitope.upper().strip()
        # Validate amino acid codes
        valid_aas = set("ACDEFGHIKLMNPQRSTVWY")
        invalid = set(seq) - valid_aas
        if invalid:
            print(f"WARNING: Non-standard amino acid codes: {invalid}")
            print(f"Continuing anyway — positions with unknown codes will use NNN codons.")

        targets = {args.name: {"seq": seq, "desc": "User-specified epitope"}}
        print(f"\nCustom target: {args.name}")
        print(f"Epitope: {seq}")

    elif args.builtin:
        # Specific built-in target
        if args.builtin not in VIRAL_EPITOPES:
            print(f"Unknown built-in target: {args.builtin}")
            print(f"Available: {list(VIRAL_EPITOPES.keys())}")
            info_line("Use --list to see all built-in targets with descriptions.")
            return 1
        targets = {args.builtin: VIRAL_EPITOPES[args.builtin]}

    elif args.all:
        # All built-in targets
        targets = VIRAL_EPITOPES
        print(f"Designing antibodies for {len(targets)} viral targets...")

    else:
        # Default: run all built-in targets
        info_line("No target specified. Running all built-in viral epitopes.")
        info_line("Use --epitope <SEQ> for a custom target, --builtin <NAME> for one, or --list to browse.")
        targets = VIRAL_EPITOPES

    # Design antibodies
    results = design_antibodies_for_targets(
        targets,
        chain_type=args.chain,
        cdr_length=args.cdr_length,
        output_path=args.output,
    )

    # Quick summary
    frob_all = all(r["antibody"].get("frobenius_verified", False) for r in results.values())
    print(f"\nOverall Frobenius: {'ALL OK' if frob_all else 'SOME FAILURES'}")
    return 0 if frob_all else 1


if __name__ == "__main__":
    sys.exit(main())
