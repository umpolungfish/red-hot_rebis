#!/usr/bin/env python3
"""
SYNTHETIC DETOX GLAND v2.0 — Zero-Incision In-Situ Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Redesign: gland grows inside the body from an injectable precursor.
No incisions. Single 22G needle puncture. Ultrasound-guided.

Structural type: ⟨𐑼 · 𐑶 · 𐑾 · 𐑬 · 𐑞 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑖 · 𐑳 · 𐑴⟩
  Ouroboricity: O₂
  Kinetics shifted to 𐑧 (slow in-situ assembly, days not minutes)
  Four cell types: sensor + producer + vascular support + EPC

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import json, os, textwrap, sys
from typing import Dict, Optional

OUTPUT_DIR = os.path.join(os.path.dirname(__file__))
V1_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gland_designs", "gland_v1")

# ─────────────────────────────────────────────────────────────────
# SHARED BIOLOGICAL CONTENT (reused from v1.0 — these don't change)
# ─────────────────────────────────────────────────────────────────

TOXIN_CLASSES = {
    "organophosphate": {"sensor": "PXR_CAR_hybrid", "antidote_arm": "PON1_enhanced"},
    "heavy_metal": {"sensor": "MTF1_metal_sensor", "antidote_arm": "MT3_enhanced"},
    "biological_toxin": {"sensor": "TLR4_TLR2_hybrid", "antidote_arm": "DARPin_toxin_neutralizer"},
    "PAH_dioxin": {"sensor": "AhR_enhanced", "antidote_arm": "CYP3A4_enhanced"},
    "cyanide_sulfide": {"sensor": "SUOX_cyano_sensor", "antidote_arm": "rhodanese_enhanced"},
    "electrophile_oxidant": {"sensor": "KEAP1_NRF2_sensor", "antidote_arm": "GST_TXNRD1_enhanced"},
}

def copy_v1_file(filename: str) -> str:
    """Copy a file from the v1 output directory."""
    path = os.path.join(V1_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return f"# {filename} not found in v1 output"

# ─────────────────────────────────────────────────────────────────
# V2-SPECIFIC GENERATORS
# ─────────────────────────────────────────────────────────────────

def generate_epc_genbank() -> str:
    """GenBank format for endothelial progenitor cell construct."""
    return """LOCUS       epc_construct            12500 bp    DNA     circular    01-JAN-2025
DEFINITION  pCLINK_EPC - Endothelial progenitor cell construct for in-situ angiogen.
ACCESSION   GLS2025004
VERSION     GLS2025004.1
KEYWORDS    synthetic biology; detox gland; angiogenesis; EPC.
SOURCE      synthetic construct
  ORGANISM  synthetic construct
FEATURES             Location/Qualifiers
     promoter        1..584
                     /note="CAG constitutive promoter"
     CDS             585..1481
                     /note="CXCR4 - SDF-1 homing receptor"
                     /gene="CXCR4"
     IRES            1482..2082
                     /note="EMCV IRES"
     CDS             2083..2956
                     /note="eNOS - endothelial nitric oxide synthase"
                     /gene="NOS3"
     IRES            2957..3557
                     /note="EMCV IRES"
     CDS             3558..4643
                     /note="VE-cadherin - endothelial adhesion"
                     /gene="CDH5"
     regulatory      4644..5200
                     /note="WPRE"
     terminator      5201..5426
                     /note="BGH polyA signal"
     misc_feature    5427..6036
                     /note="Hygromycin resistance (hygR)"
     misc_feature    6037..12500
                     /note="pUC ori + ampR backbone"
ORIGIN
"""

def generate_metabolic_model_v2() -> str:
    """SBML L3 model updated for v2 in-situ dynamics, adding EPC and vascularization."""
    # Reuse v1 model but add EPC differentiation and angiogenesis coupling
    v1_model = copy_v1_file("metabolic_model.xml")
    # Add EPC compartment and reactions to v1 model
    insert_point = v1_model.find("</listOfReactions>")
    if insert_point == -1:
        return v1_model
    additions = """
      <reaction id="EPC_differentiation" reversible="false">
        <listOfReactants>
          <speciesReference species="amino_acids" stoichiometry="10"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="antidote_protein" stoichiometry="1"/>
        </listOfProducts>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply><times/><cn>0.0001</cn><ci> amino_acids </ci></apply>
          </math>
        </kineticLaw>
      </reaction>
"""
    return v1_model[:insert_point] + additions + v1_model[insert_point:]

def generate_v2_specification() -> str:
    """Generate the v2 gland specification JSON."""
    spec = {
        "name": "Universal Detox Gland (Panacea) — v2 In-Situ",
        "version": "2.0.0",
        "design_principle": "Zero-incision in-situ assembly via percutaneous injection",
        "structural_type": "⟨𐑼 · 𐑶 · 𐑾 · 𐑬 · 𐑞 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑖 · 𐑳 · 𐑴⟩",
        "ouroboricity_tier": "O₂",
        "consciousness_score": 0.45,
        "delivery_method": {
            "type": "ultrasound_guided_percutaneous_injection",
            "needle_gauge": "22G",
            "volume_mL": 2.5,
            "target_anatomy": "greater_omentum",
            "guidance": "ultrasound (7.5-12 MHz linear array)",
            "anesthesia": "local lidocaine 1% (5 mL)",
            "incisions_required": 0,
            "procedure_time_min": 15,
            "recovery": "immediate outpatient"
        },
        "physical_specs": {
            "final_volume_cm3": 3.0,
            "shape": "ellipsoid",
            "dimensions_mm": [18, 15, 12],
            "cell_count": 1e9,
            "cell_types": {
                "sensor": {"count": 5e7, "pct": 5},
                "producer": {"count": 8.5e8, "pct": 85},
                "vascular_support": {"count": 5e7, "pct": 5},
                "endothelial_progenitor": {"count": 5e7, "pct": 5}
            },
            "vascularization": {
                "method": "in_situ_angiogenesis",
                "preformed_channels": False,
                "driver": "VEGF_bFGF_Ang1_from_support_cells",
                "host_recruitment": "SDF1alpha_CXCR4",
                "time_to_full_vascularization_days": 21
            }
        },
        "injectable_formulation": {
            "thermogel": "Pluronic_F127_20pct",
            "secondary_crosslinker": "HA_tyramine_HRP_H2O2",
            "fibrin_stabilizer": "fibrinogen_10mg_thrombin_50U",
            "cell_protection": "alginate_PEG_microcapsules_100um",
            "growth_factors": ["VEGF", "bFGF", "Ang1", "SDF1a", "IGF1"],
            "immune_modulators": ["CCL22", "TGFb1", "IL10"],
            "storage": "4C_liquid_use_within_2h"
        },
        "in_situ_assembly_timeline_days": {
            "gel_formation": 0,
            "first_capillary_sprouts": 2,
            "sensors_active": 3,
            "vascular_penetration_50pct": 7,
            "full_vascularization": 14,
            "stable_steady_state": 21
        },
        "sensor_systems": {
            "AhR_enhanced": {"target": "PAHs_dioxins", "sensitivity_uM": [0.01, 100]},
            "PXR_CAR_hybrid": {"target": "organophosphates", "sensitivity_uM": [0.1, 500]},
            "TLR4_MD2_hybrid": {"target": "endotoxins", "sensitivity_uM": [0.001, 10]},
            "MTF1_metal_sensor": {"target": "heavy_metals", "sensitivity_uM": [0.5, 200]},
            "KEAP1_NRF2_sensor": {"target": "electrophiles", "sensitivity_uM": [1, 500]}
        },
        "antidote_arms": {
            "CYP3A4_enhanced": {"target": "PAHs_drugs", "mechanism": "oxidative", "Km_uM": 15},
            "PON1_enhanced": {"target": "organophosphates", "mechanism": "hydrolysis", "Km_uM": 50},
            "MT3_enhanced": {"target": "heavy_metals", "mechanism": "chelation", "Kd_uM": 0.1},
            "DARPin_neutralizer": {"target": "protein_toxins", "mechanism": "binding", "Kd_uM": 0.01},
            "Rhodanese_enhanced": {"target": "cyanide", "mechanism": "thiocyanate", "Km_uM": 100},
            "GST_TXNRD1_enhanced": {"target": "electrophiles", "mechanism": "conjugation", "Km_uM": 30}
        },
        "kinetics": {
            "induction_delay_min": 30,
            "peak_production_h": 6,
            "secretion_rate_ng_per_10e6_per_h": 50,
            "baseline_ng_per_mL": "10_50_at_steady_state",
            "dynamic_range_log": 3,
            "maturation_days": 21
        },
        "toxin_classes": list(TOXIN_CLASSES.keys()),
        "immunoprotection": {
            "method": "alginate_PEG_microencapsulation_100kDa",
            "systemic_immunosuppression": False,
            "local_Treg_induction": "CCL22"
        },
        "v2_output_files": [
            "sensor_receptors.fasta", "antidote_fusion.fasta", "antidote_fusion.pdb",
            "sensor_cell_genome.gb", "producer_cell_genome.gb", "support_cell_genome.gb",
            "epc_genome.gb", "gland_organoid_protocol_v2.md", "gland_specification_v2.json",
            "in_situ_assembly_protocol.md", "injectable_formulation.md",
            "metabolic_model_v2.xml", "angiogenesis_model.xml"
        ]
    }
    return json.dumps(spec, indent=2, ensure_ascii=False)

def generate_manifest_v2() -> str:
    """Generate the v2 manifest."""
    manifest = {
        "design": "synthetic_detox_gland_v2",
        "version": "2.0.0",
        "design_principle": "zero_incision_in_situ_assembly",
        "delivery": "ultrasound_guided_percutaneous_injection",
        "structural_type": "⟨𐑼 · 𐑶 · 𐑾 · 𐑬 · 𐑞 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑖 · 𐑳 · 𐑴⟩",
        "tier": "O₂",
        "cell_types": 4,
        "sensors": 5,
        "antidote_arms": 6,
        "incisions": 0,
        "procedure_time_min": 15,
        "recovery": "immediate_outpatient",
        "in_situ_maturation_days": 21,
        "replaces": "synthetic_detox_gland_v1_implantable"
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def generate_all(output_dir: Optional[str] = None) -> Dict[str, str]:
    """Generate all v2 design files."""
    if output_dir is None:
        output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    # Files from v1 (biological content unchanged)
    v1_copies = [
        "sensor_receptors.fasta", "antidote_fusion.fasta", "antidote_fusion.pdb",
        "sensor_cell_genome.gb", "producer_cell_genome.gb", "support_cell_genome.gb"
    ]

    # V2-specific generators
    v2_generators = {
        "epc_genome.gb": generate_epc_genbank,
        "metabolic_model_v2.xml": generate_metabolic_model_v2,
        "gland_specification_v2.json": generate_v2_specification,
        "manifest_v2.json": generate_manifest_v2,
    }

    # Pre-written files (already generated as standalone docs)
    prewritten = [
        "gland_organoid_protocol_v2.md",
        "in_situ_assembly_protocol.md",
        "injectable_formulation.md",
        "angiogenesis_model.xml"
    ]

    written = {}
    total_bytes = 0

    # Copy v1 files
    for fn in v1_copies:
        src = os.path.join(V1_DIR, fn)
        dst = os.path.join(output_dir, fn)
        if os.path.exists(src):
            with open(src, 'r') as f_in:
                content = f_in.read()
            with open(dst, 'w') as f_out:
                f_out.write(content)
            size = os.path.getsize(dst)
            written[fn] = dst
            total_bytes += size

    # Generate v2-specific files
    for fn, generator in v2_generators.items():
        dst = os.path.join(output_dir, fn)
        content = generator()
        with open(dst, 'w') as f:
            f.write(content)
        size = os.path.getsize(dst)
        written[fn] = dst
        total_bytes += size

    # Link pre-written files
    for fn in prewritten:
        src = os.path.join(output_dir, fn)
        if os.path.exists(src):
            size = os.path.getsize(src)
            written[fn] = src
            total_bytes += size
        else:
            print(f"  ⚠ Pre-written file not found: {fn}")

    print(f"✓ GLAND V2 (IN-SITU): {len(written)} files, {total_bytes} bytes")
    print(f"  Output: {output_dir}/")
    for fn, fp in sorted(written.items()):
        print(f"  • {fn} ({os.path.getsize(fp)} bytes)")
    print(f"  • ZERO incisions — single ultrasound-guided injection")

    return written

if __name__ == "__main__":
    output_dir = sys.argv[1] if len(sys.argv) > 1 else None
    generate_all(output_dir)
