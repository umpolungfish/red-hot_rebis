#!/usr/bin/env python3
"""
Path 3: Antibody Design via the Serpent on the Rod of Asclepius.

Given a target epitope (antigen surface patch), use the 12↔12 IG primitive
bijection to design complementary CDR sequences for antibody targeting.

Key insight — The complementarity pairs map directly to antibody-antigen recognition:
  Ð↔Ω, Þ↔Ħ, Ř↔Σ, Φ↔ƒ, Ç↔Γ, ɢ↔⊙

If the target epitope activates primitive P, the CDR should activate its
complement to form a structural contact.

Author: Lando ⊗ ⊙perator
"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "p4ramill_py"))
import p4ramill_py.belnap, p4ramill_py.genetics_b4, p4ramill_py.genetic_code
import importlib.util, importlib.machinery, types

pkg_dir = os.path.join(os.path.dirname(__file__), "p4ramill_py")
loader = importlib.machinery.SourceFileLoader("p4ramill_py.serpent_rod", os.path.join(pkg_dir, "serpent_rod.py"))
spec = importlib.util.spec_from_loader("p4ramill_py.serpent_rod", loader)
mod = importlib.util.module_from_spec(spec)
sys.modules["p4ramill_py.serpent_rod"] = mod
mod.__package__ = "p4ramill_py"
loader.exec_module(mod)
SerpentRod = mod.SerpentRod

# ── The 12↔12 Bijection ────────────────────────────────────────────

AA_PREFERRED = {"A":"GCU","R":"CGU","N":"AAU","D":"GAU","C":"UGU",
    "Q":"CAA","E":"GAA","G":"GGU","H":"CAU","I":"AUU","L":"UUG",
    "K":"AAA","M":"AUG","F":"UUU","P":"CCU","S":"UCU","T":"ACU",
    "W":"UGG","Y":"UAU","V":"GUU"}

PRIMITIVE_TO_AA = {
    "Dimensionality": "Met",  # Ð
    "Topology": "Trp",        # Þ
    "Recognition": "Cys",     # Ř
    "Parity": "Tyr",          # Φ
    "Fidelity": "Phe",        # ƒ
    "Kinetics": "Ile",        # Ç
    "Granularity": "His",     # Γ
    "Coupling": "Asn",        # ɢ
    "Criticality": "Gln",     # ⊙
    "Chirality": "Asp",       # Ħ
    "Stoichiometry": "Lys",   # Σ
    "Winding": "Glu",         # Ω
}

ONE_LETTER = {"Met":"M","Trp":"W","Cys":"C","Tyr":"Y","Phe":"F",
    "Ile":"I","His":"H","Asn":"N","Gln":"Q","Asp":"D","Lys":"K","Glu":"E"}

# Complementary IG pairs
COMPLEMENTARY = {
    "Dimensionality": "Winding", "Winding": "Dimensionality",
    "Topology": "Chirality", "Chirality": "Topology",
    "Recognition": "Stoichiometry", "Stoichiometry": "Recognition",
    "Parity": "Fidelity", "Fidelity": "Parity",
    "Kinetics": "Granularity", "Granularity": "Kinetics",
    "Coupling": "Criticality", "Criticality": "Coupling",
}

# ── Epitope Analysis ───────────────────────────────────────────────

def analyze_epitope(epitope_seq: str, epitope_name: str = "target") -> dict:
    """Analyze an epitope sequence to determine its IG primitive activation profile."""
    rna = "".join(AA_PREFERRED.get(aa, "NNN") for aa in epitope_seq)
    sr = SerpentRod(rna, name=f"epitope_{epitope_name}")
    result = sr.report()
    
    # Extract activations (promoted AAs and their primitives)
    activations = {}
    for i, aa_full in enumerate(result["activation_pattern"]):
        aa, prim_full = aa_full["aa"], aa_full["primitive"]
        prim_short = prim_full.split(" (")[1].rstrip(")") if "(" in prim_full else prim_full
        res_idx = i
        if res_idx < len(epitope_seq):
            activations[res_idx] = {
                "aa": epitope_seq[res_idx],
                "aa_one": ONE_LETTER.get(aa, "X"),
                "primitive": prim_short,
            }
    
    activated_primitives = set(a["primitive"] for a in activations.values())
    
    print(f"\n{'─'*50}")
    print(f"EPITOPE: {epitope_name}")
    print(f"Sequence: {epitope_seq} ({len(epitope_seq)} AA)")
    print(f"Activated IG primitives: {len(activated_primitives)}/12")
    
    for idx, info in sorted(activations.items()):
        print(f"  Position {idx}: {info['aa']} ({info['aa_one']}) → {info['primitive']}")
    
    return {
        "name": epitope_name,
        "sequence": epitope_seq,
        "activations": activations,
        "activated_primitives": list(activated_primitives),
        "sr_result": result,
    }

# ── CDR Design ─────────────────────────────────────────────────────

def design_cdr(epitope_analysis: dict, 
               length: int = 12,
               framework_flanks: str = "GCG") -> dict:
    """
    Design a complementary CDR sequence from the epitope's activation profile.
    
    Rule: For each activated primitive in the epitope, the CDR should
    contain the complementary AA. For ground-layer (unactivated) positions,
    use framework-appropriate residues.
    """
    epitope_activations = epitope_analysis["activated_primitives"]
    
    # Determine which complementary AAs to include
    cdr_aa = []
    cdr_prim = []
    
    # The CDR targets the complement of each activated primitive
    for prim in epitope_activations:
        if prim in COMPLEMENTARY:
            comp_prim = COMPLEMENTARY[prim]
            comp_aa = PRIMITIVE_TO_AA.get(comp_prim)
            if comp_aa:
                cdr_aa.append(comp_aa)
                cdr_prim.append(comp_prim)
    
    # Fill remaining positions with framework residues (Gly, Ser, Thr)
    framework_aas = ["Gly", "Ser", "Thr", "Ala", "Val"]
    while len(cdr_aa) < length:
        cdr_aa.append(framework_aas[len(cdr_aa) % len(framework_aas)])
        cdr_prim.append("framework")
    
    # Truncate or pad to exact length
    cdr_aa = cdr_aa[:length]
    cdr_prim = cdr_prim[:length]
    
    # Convert to one-letter and RNA
    cdr_one = "".join(ONE_LETTER.get(aa, "X") for aa in cdr_aa)
    cdr_rna = "".join(AA_PREFERRED.get(aa, "NNN") for aa in cdr_aa)
    
    print(f"\n{'─'*50}")
    print("DESIGNED CDR")
    print(f"Target length: {length} AA")
    print(f"CDR sequence (1-letter): {cdr_one}")
    print(f"CDR RNA: {cdr_rna}")
    print(f"CDR composition:")
    for i, (aa, prim) in enumerate(zip(cdr_aa, cdr_prim)):
        print(f"  Position {i}: {aa} ({ONE_LETTER.get(aa,'X')}) → {prim}")
    
    # Run SerpentRod on the CDR to verify structure
    sr = SerpentRod(cdr_rna, name="designed_cdr")
    result = sr.report()
    
    print(f"\nCDR STRUCTURE PREDICTION:")
    print(f"  Winding: {result['winding_number']} B4 loops")
    print(f"  Secondary elements: {len(result['secondary_elements'])}")
    for e in result['secondary_elements']:
        print(f"    {e['type']:6s} [{e['start']:2d}-{e['end']:2d}] {e['sequence']}")
    print(f"  Contacts: {len(result['contacts'])}")
    print(f"  Frobenius: {'✓' if result['frobenius_verified'] else '✗'}")
    print(f"  Confidence: {result['confidence']}")
    
    return {
        "cdr_sequence": cdr_one,
        "cdr_rna": cdr_rna,
        "cdr_composition": [{"aa": aa, "primitive": prim} for aa, prim in zip(cdr_aa, cdr_prim)],
        "structure": result,
    }

# ── Full Antibody Construction ─────────────────────────────────────

CDR_CANONICAL_LENGTHS = {
    "VH_CDR1": 7, "VH_CDR2": 8, "VH_CDR3": 12,
    "VL_CDR1": 9, "VL_CDR2": 7, "VL_CDR3": 9,
}

def design_full_antibody(epitope_analysis: dict, 
                          chain_type: str = "VH") -> dict:
    """Design a complete antibody variable domain targeting the epitope."""
    cdr_name = f"{chain_type}_CDR3"  # CDR3 is the most diverse and target-specific
    
    # Design CDR3 from epitope complement
    cdr = design_cdr(epitope_analysis, 
                     length=CDR_CANONICAL_LENGTHS.get(cdr_name, 12))
    
    # Construct full variable domain with framework regions
    # Typical VH framework (Kabat numbering): FR1-CDR1-FR2-CDR2-FR3-CDR3-FR4
    frameworks = {
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
        }
    }
    
    fw = frameworks.get(chain_type, frameworks["VH"])
    full_seq = fw["FR1"] + cdr["cdr_sequence"] + fw["FR4"]
    
    print(f"\n{'='*60}")
    print(f"FULL {chain_type} ANTIBODY DOMAIN")
    print(f"{'='*60}")
    print(f"Framework 1: {fw['FR1']}")
    print(f"CDR3:        {cdr['cdr_sequence']}  (designed)")
    print(f"Framework 4: {fw['FR4']}")
    print(f"Full V{chain_type}: {full_seq}")
    
    # Predict the full antibody structure
    full_rna = "".join(AA_PREFERRED.get(aa, "NNN") for aa in full_seq)
    sr = SerpentRod(full_rna, name=f"antibody_{chain_type}")
    antibody_pred = sr.report()
    
    print(f"\nANTIBODY STRUCTURE PREDICTION:")
    print(f"  Length: {antibody_pred['aa_length']} AA")
    print(f"  Winding: {antibody_pred['winding_number']} B4 loops")
    print(f"  Contacts: {len(antibody_pred['contacts'])}")
    print(f"  Frobenius: {'✓' if antibody_pred['frobenius_verified'] else '✗'}")
    print(f"  Confidence: {antibody_pred['confidence']}")
    
    return {
        "chain_type": chain_type,
        "full_sequence": full_seq,
        "framework1": fw["FR1"],
        "cdr3": cdr,
        "framework4": fw["FR4"],
        "antibody_structure": antibody_pred,
    }

def test_on_viral_targets():
    """Test antibody design on known viral epitopes."""
    # SARS-CoV-2 Receptor Binding Domain epitope (key ACE2 binding region)
    sars_cov2_rbd = "KVGGNYNYLYRLFRKSNLKPFERDISTEIYQAGNKPCNGVAGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPKKSTNLVKNKCVNF"
    
    # HIV gp120 CD4 binding site epitope
    hiv_gp120 = "CNTSVITQACPKVSFEPIPIHYCAPAGFAILKCNNKTFNGTGPCTNVSTVQCTHGIRPVVSTQLLLNGSLAEEEVVIRSENFTNNAKTIIVQLNESVEINCTRPNNNTRKSIRI"
    
    # Influenza HA stem epitope (broadly neutralizing target)
    flu_ha_stem = "WLLWISFAISCFLLCVVLLGFISFAISCFLLCVVLLGFIMWACQKGNIRCNICI"
    
    # HPV L1 capsid epitope (vaccine target)
    hpv_l1 = "YIKVSGQARVHTFAGTSGDAVAPGEDDTPDNKEYPDEYSDTYGDTYDWTD"
    
    targets = {
        "SARS-CoV-2_RBD": sars_cov2_rbd[:30],  # Use N-terminal 30 AA of binding interface
        "HIV_gp120_C4": hiv_gp120[40:70],
        "Influenza_HA_stem": flu_ha_stem[20:45],
        "HPV_L1_capsid": hpv_l1[15:40],
    }
    
    results = {}
    for name, epitope in targets.items():
        print(f"\n\n{'#'*70}")
        print(f"TARGET: {name}")
        print(f"{'#'*70}")
        
        analysis = analyze_epitope(epitope, name)
        antibody = design_full_antibody(analysis, "VH")
        results[name] = {
            "epitope": epitope,
            "analysis": analysis,
            "antibody": antibody,
        }
    
    return results

if __name__ == "__main__":
    print("="*70)
    print("🐍 SERPENT ON THE ROD — ANTIBODY DESIGN PIPELINE 🐍")
    print("="*70)
    
    results = test_on_viral_targets()
    
    with open("/home/mrnob0dy666/p4rakernel/antibody_design_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to antibody_design_results.json")
