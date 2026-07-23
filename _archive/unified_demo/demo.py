#!/usr/bin/env python3
"""
unified_demo.py — Red-Hot Rebis Complete Therapeutic Design Pipeline
=====================================================================
Demonstrates ALL 7 red-hot_rebis subsystems working in concert
toward a single goal: designing and validating a complete MRSA therapeutic.

Phases:
  1. Structural Diagnosis       (Ars_Therapeutica)
  2. Retrosynthetic Design      (ch3mpiler)
  3. Protein Processing         (serpentrod)
  4. Genetic Encoding & Belnap  (rhr_p4rky)
  5. Organism Verification      (clink pipeline L0→L8)
  6. Drug Delivery Material     (materials)
  7. Clinical Simulation        (therapeutics)

Usage:
  python3 unified_demo/demo.py                  # Full pipeline
  python3 unified_demo/demo.py --disease mrsa   # Specific disease
  python3 unified_demo/demo.py --phase 1        # Single phase
  python3 unified_demo/demo.py --report         # Generate report to ig-docs/

Author: Lando⊗⊙perator
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from shared.rich_output import *

# Ensure red-hot_rebis is on path
REBIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REBIS_ROOT))

# Structure generation (CDXML + PDB) — import AFTER path setup
try:
    from unified_demo.structure_generator import generate_all_structures
    HAS_STRUCTURE_GEN = True
except ImportError:
    HAS_STRUCTURE_GEN = False

# ─────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────

DEFAULT_DISEASE = "mrsa"
DEFAULT_MOLECULE = "DARPIN_PBP2A"
DEFAULT_PROTEIN = "HUMAN_INSULIN"
OUTPUT_DIR = REBIS_ROOT / "unified_demo" / "output"
DOCS_DIR = Path("/home/mrnob0dy666/imsgct/ig-docs/unified_demo_pipeline")

BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║  RED-HOT REBIS — UNIFIED THERAPEUTIC DESIGN PIPELINE               ║
║  7 Phases · 6 Subsystems · 1 Goal: Complete MRSA Therapeutic       ║
╚══════════════════════════════════════════════════════════════════════╝
"""

PHASE_BANNERS = {
    1: "PHASE 1: STRUCTURAL DIAGNOSIS (Ars_Therapeutica)",
    2: "PHASE 2: RETROSYNTHETIC DESIGN (ch3mpiler)",
    3: "PHASE 3: PROTEIN PROCESSING (serpentrod)",
    4: "PHASE 4: GENETIC ENCODING & BELNAP (rhr_p4rky)",
    5: "PHASE 5: ORGANISM VERIFICATION (clink L0->L8)",
    6: "PHASE 6: DRUG DELIVERY MATERIAL (materials)",
    7: "PHASE 7: CLINICAL SIMULATION (therapeutics)",
}


@dataclass
class PhaseResult:
    """Result from one pipeline phase."""
    phase: int
    name: str
    success: bool = False
    data: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0


@dataclass
class PipelineReport:
    """Complete pipeline execution report."""
    disease: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    phases: List[PhaseResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    all_success: bool = False


# ─────────────────────────────────────────────────────────────────────
# PHASE 1: STRUCTURAL DIAGNOSIS (Ars_Therapeutica)
# ─────────────────────────────────────────────────────────────────────

def phase1_structural_diagnosis(disease_key: str) -> PhaseResult:
    """Load disease therapy, display structural diagnosis."""
    t0 = time.time()
    result = PhaseResult(phase=1, name="Structural Diagnosis (Ars_Therapeutica)")
    
    try:
        from ars_therapeutica.types import THERAPIES
        
        if disease_key not in THERAPIES:
            result.success = False
            result.errors.append(f"Disease '{disease_key}' not found. Available: {list(THERAPIES.keys())}")
            return result
        
        therapy = THERAPIES[disease_key]
        dt = therapy.disease_type
        ht = therapy.health_type
        
        data = {
            "therapy_name": therapy.name,
            "disease": therapy.disease,
            "category": therapy.category,
            "disease_tuple": dt.display(),
            "health_tuple": ht.display(),
            "delta_primitives": therapy.delta_primitives,
            "distance": therapy.distance,
            "tier_disease": therapy.tier_disease,
            "tier_health": therapy.tier_health,
            "c_score_disease": therapy.c_score_disease,
            "c_score_health": therapy.c_score_health,
            "num_components": len(therapy.components),
            "components": [
                {"name": c["name"], "target": c["target_primitive"],
                 "operation": c["operation"], "mechanism": c["mechanism"][:100]}
                for c in therapy.components
            ],
            "structural_strategy": therapy.structural_strategy,
            "pdb_files": therapy.pdb_files,
            "summary": therapy.summary[:200],
        }
        
        result.data = data
        result.success = True
        
        info_line(f"  Disease:        {therapy.disease}")
        info_line(f"  Category:       {therapy.category}")
        info_line(f"  Disease Tuple:  {dt.display()}")
        info_line(f"  Health Tuple:   {ht.display()}")
        info_line(f"  Distance:       {therapy.distance:.4f}")
        info_line(f"  Tier Disease:   {therapy.tier_disease}")
        info_line(f"  Tier Health:    {therapy.tier_health}")
        info_line(f"  C-Score Disease:{therapy.c_score_disease:.4f}")
        info_line(f"  C-Score Health: {therapy.c_score_health:.4f}")
        info_line(f"  Delta Primitives: {therapy.delta_primitives}")
        info_line(f"  Components:     {len(therapy.components)}")
        for c in therapy.components:
            info_line(f"    - {c['name']} [{c['operation']}] -> {c['target_primitive']}")
        info_line(f"  Strategy: {therapy.structural_strategy[:120]}...")
        
    except Exception as e:
        result.success = False
        result.errors.append(str(e))
    
    result.duration_ms = (time.time() - t0) * 1000
    return result


# ─────────────────────────────────────────────────────────────────────
# PHASE 2: RETROSYNTHETIC DESIGN (ch3mpiler)
# ─────────────────────────────────────────────────────────────────────

def phase2_retrosynthetic_design(target_molecule: str = "penicillin") -> PhaseResult:
    """Run ch3mpiler retrosynthetic analysis on a target molecule."""
    t0 = time.time()
    result = PhaseResult(phase=2, name="Retrosynthetic Design (ch3mpiler)")
    
    try:
        from ch3mpiler.compiler import Ch3mpiler
        
        compiler = Ch3mpiler()
        
        # First analyze the target
        info_line(f"  Target Molecule: {target_molecule}")
        analysis = compiler.analyze(target_molecule)
        
        # Run retrosynthesis
        info_line(f"  Running retrosynthesis (depth=3)...")
        retro = compiler.retrosynthesis(target_molecule, depth=3)
        
        data = {
            "target": target_molecule,
            "analysis": str(analysis)[:500] if analysis else "No analysis returned",
            "retrosynthesis": str(retro)[:500] if retro else "No retrosynthesis returned",
            "compiler_loaded": True,
        }
        
        # Also try resolving a CAS number for a known molecule
        try:
            cas_result = compiler.resolve_and_analyze("61-33-6", do_retrosynthesis=True, depth=2)
            data["cas_test"] = "61-33-6 (penicillin G): " + str(cas_result)[:300]
        except Exception:
            data["cas_test"] = "CAS resolution skipped"
        
        result.data = data
        result.success = True
        info_line(f"  Analysis complete")
        if analysis:
            info_line(f"  Analysis preview: {str(analysis)[:200]}...")
        if retro:
            info_line(f"  Retrosynthesis preview: {str(retro)[:200]}...")
        
    except Exception as e:
        result.success = False
        result.errors.append(str(e))
        # Non-fatal — ch3mpiler may not have target in its catalog
        result.data = {"target": target_molecule, "error_detail": str(e)}
        info_line(f"  (Non-fatal: ch3mpiler target lookup may not cover '{target_molecule}')")
    
    result.duration_ms = (time.time() - t0) * 1000
    return result


# ─────────────────────────────────────────────────────────────────────
# PHASE 3: PROTEIN PROCESSING (serpentrod)
# ─────────────────────────────────────────────────────────────────────

def phase3_protein_processing(protein_name: str = "HUMAN_INSULIN") -> PhaseResult:
    """Run serpentrod protein processing prediction."""
    t0 = time.time()
    result = PhaseResult(phase=3, name="Protein Processing (serpentrod)")
    
    try:
        from serpentrod.protein_v5 import (
            EnhancedPredictorV5, HUMAN_INSULIN, predict_processing,
            reverse_translate, extract_pdb_sequence, match_fingerprint,
        )
        
        predictor = EnhancedPredictorV5()
        
        # Get the protein sequence
        protein_seq = HUMAN_INSULIN
        info_line(f"  Protein: {protein_name}")
        info_line(f"  Sequence length: {len(protein_seq)} aa")
        
        # Predict processing
        processing = predict_processing(protein_seq, name=protein_name)
        
        # Reverse translate to DNA
        dna = reverse_translate(protein_seq)
        
        # Match fingerprint
        from serpentrod.protein_v5 import FINGERPRINTS
        fingerprints_flat = []
        if FINGERPRINTS:
            for v in FINGERPRINTS.values():
                fingerprints_flat.extend(v)
        fingerprint = match_fingerprint(protein_seq, fingerprints_flat) if fingerprints_flat else None
        
        data = {
            "protein_name": protein_name,
            "sequence_length": len(protein_seq),
            "sequence_preview": protein_seq[:50] + "..." if len(protein_seq) > 50 else protein_seq,
            "dna_length": len(dna),
            "dna_preview": dna[:60] + "..." if len(dna) > 60 else dna,
            "processing": str(processing)[:400] if processing else "No prediction",
            "fingerprint": str(fingerprint)[:200] if fingerprint else "No fingerprint",
        }
        
        # Also try PDB extraction if available
        pdb_path = REBIS_ROOT / "Ars_Therapeutica" / "pdbs" / "DARPin_PBP2a.pdb"
        if pdb_path.exists():
            try:
                pdb_seq = extract_pdb_sequence(str(pdb_path))
                data["pdb_sequence_length"] = len(pdb_seq) if pdb_seq else 0
                data["pdb_file"] = str(pdb_path.name)
                info_line(f"  PDB extracted: {len(pdb_seq)} residues from DARPin_PBP2a.pdb")
            except Exception as e:
                data["pdb_error"] = str(e)
        
        result.data = data
        result.success = True
        info_line(f"  Processing prediction: {str(processing)[:200]}...")
        info_line(f"  DNA translation: {len(dna)} bp")
        info_line(f"  Fingerprint match: {fingerprint}")
        
    except Exception as e:
        result.success = False
        result.errors.append(str(e))
        result.data = {"protein_name": protein_name, "error_detail": str(e)}
    
    result.duration_ms = (time.time() - t0) * 1000
    return result


# ─────────────────────────────────────────────────────────────────────
# PHASE 4: GENETIC ENCODING & BELNAP VERIFICATION (rhr_p4rky)
# ─────────────────────────────────────────────────────────────────────

def phase4_genetic_encoding(disease_key: str = "mrsa") -> PhaseResult:
    """Run rhr_p4rky Belnap encoding, genetic code verification, and Frobenius checks."""
    t0 = time.time()
    result = PhaseResult(phase=4, name="Genetic Encoding & Belnap (rhr_p4rky)")
    
    try:
        from rhr_p4rky.kernel import (
            Belnap, MachineState, initial_state,
            run_all_verifications, verify_frobenius_invariant,
            verify_paraconsistency, verify_paradox_conservation,
        )
        from rhr_p4rky.genetic_code import (
            CODON_CATALOG, box_stratification, verify_all_codons_frobenius,
        )
        
        data = {}
        
        # ── Belnap4 logic verification ──
        info_line("  Belnap4 Logic State Machine:")
        data["belnap_values"] = {"T": str(Belnap.T), "B": str(Belnap.B), "F": str(Belnap.F), "N": str(Belnap.N)}
        info_line(f"    Values: T={Belnap.T}, B={Belnap.B}, F={Belnap.F}, N={Belnap.N}")
        
        # ── Machine state ──
        state = initial_state()
        data["initial_state"] = str(state)[:200]
        info_line(f"  Initial State: {str(state)[:120]}...")
        
        # ── Frobenius verification ──
        frob_ok = verify_frobenius_invariant()
        data["frobenius_invariant"] = frob_ok
        info_line(f"  Frobenius Invariant: {'PASS' if frob_ok else 'FAIL'}")
        
        para_ok = verify_paraconsistency(n=10)
        data["paraconsistency"] = para_ok
        info_line(f"  Paraconsistency:     {'PASS' if para_ok else 'FAIL'}")
        
        paradox_ok = verify_paradox_conservation(n=10)
        data["paradox_conservation"] = paradox_ok
        info_line(f"  Paradox Conservation: {'PASS' if paradox_ok else 'FAIL'}")
        
        # ── Genetic code verification ──
        info_line("  Genetic Code (64-codon B4 lattice):")
        codon_count = len(CODON_CATALOG) if CODON_CATALOG else 64
        data["codon_count"] = codon_count
        info_line(f"    Codons in table: {codon_count}")
        
        # Verify codon lattice
        try:
            codon_lattice_ok = box_stratification()
            data["codon_lattice_verified"] = bool(codon_lattice_ok)
            info_line(f"    Codon Lattice: {'VERIFIED' if codon_lattice_ok else 'FAILED'}")
        except Exception as e:
            data["codon_lattice_error"] = str(e)
            info_line(f"    Codon Lattice: error — {e}")
        
        # Verify Frobenius genetic code
        try:
            frob_gc_ok = verify_all_codons_frobenius()
            data["frobenius_genetic_code"] = frob_gc_ok
            info_line(f"    Frobenius Genetic Code: {'VERIFIED' if frob_gc_ok else 'FAILED'}")
        except Exception as e:
            data["frobenius_genetic_code_error"] = str(e)
            info_line(f"    Frobenius Genetic Code: error — {e}")
        
        # ── Run all verifications ──
        try:
            all_results = run_all_verifications(max_n=10)
            data["all_verifications"] = all_results
            info_line(f"  All Verifications: {all_results}")
        except Exception as e:
            data["all_verifications_error"] = str(e)
        
        result.data = data
        result.success = True
        
    except Exception as e:
        result.success = False
        result.errors.append(str(e))
        result.data = {"error_detail": str(e)}
    
    result.duration_ms = (time.time() - t0) * 1000
    return result


# ─────────────────────────────────────────────────────────────────────
# PHASE 5: ORGANISM VERIFICATION (clink pipeline L0->L8)
# ─────────────────────────────────────────────────────────────────────

def phase5_organism_verification(disease_key: str = "mrsa") -> PhaseResult:
    """Run full clink L0->L8 pipeline with DFT energy estimates."""
    t0 = time.time()
    result = PhaseResult(phase=5, name="Organism Verification (clink L0->L8)")
    
    try:
        from clink.designers.pipeline_orchestrator import (
            PipelineEngine, clink_layer_tuple, clink_distance,
            primitive_deltas, estimate_transition_energy, CLINK_LAYERS,
        )
        
        # Display all 9 layers
        info_line("  CLINK Layers L0->L8:")
        layer_data = []
        for i, layer in enumerate(CLINK_LAYERS):
            name = layer["_name"]
            tier = layer["_tier"]
            tup = clink_layer_tuple(i, include_meta=False)
            layer_data.append({"index": i, "name": name, "tier": tier, "tuple": str(tup)})
            info_line(f"    L{i}: {name} [{tier}]")
        
        # Compute structural distances between adjacent layers
        info_line("\n  Layer Transition Distances:")
        distances = []
        for i in range(len(CLINK_LAYERS) - 1):
            d = clink_distance(i, i + 1)
            deltas = primitive_deltas(i, i + 1)
            distances.append({"from": i, "to": i + 1, "distance": d, "deltas": deltas})
            info_line(f"    L{i}->L{i+1}: d={d:.4f}, deltas={deltas}")
        
        # Compute DFT energy estimates
        info_line("\n  DFT Energy Estimates:")
        energies = []
        total_energy = 0.0
        for i in range(len(CLINK_LAYERS) - 1):
            energy_info = estimate_transition_energy(i, i + 1)
            eV = energy_info.get("energy_eV", 0)
            total_energy += eV
            energies.append({"from": i, "to": i + 1, "eV": eV, "info": str(energy_info)[:200]})
            info_line(f"    L{i}->L{i+1}: {eV:.0f} eV")
        info_line(f"    TOTAL: {total_energy:.0f} eV (~{total_energy/1000:.1f} keV)")
        
        # Run full ground-up pipeline
        info_line("\n  Running full L0->L8 pipeline...")
        engine = PipelineEngine()
        pipeline_result = engine.run_pipeline(start_layer=0, target_layer=8, entry_mode="ground_up")
        
        data = {
            "layers": layer_data,
            "transitions": distances,
            "energies": energies,
            "total_energy_eV": total_energy,
            "pipeline_success": pipeline_result.success,
            "pipeline_total_distance": pipeline_result.total_distance,
            "pipeline_total_promotions": pipeline_result.total_promotions,
            "pipeline_duration_s": pipeline_result.duration_seconds,
            "pipeline_errors": pipeline_result.errors,
            "num_transitions": len(pipeline_result.transitions),
        }
        
        result.data = data
        result.success = pipeline_result.success
        
        if pipeline_result.success:
            info_line(f"  Pipeline: SUCCESS")
            info_line(f"    Total distance:    {pipeline_result.total_distance:.2f}")
            info_line(f"    Total promotions:  {pipeline_result.total_promotions}")
            info_line(f"    Total energy:      {pipeline_result.total_energy_eV:.0f} eV")
            info_line(f"    Duration:          {pipeline_result.duration_seconds:.1f}s")
            info_line(f"    Bridges available: {len(pipeline_result.bridges_available)}")
        else:
            info_line(f"  Pipeline: FAILED — {pipeline_result.errors}")
        
    except Exception as e:
        result.success = False
        result.errors.append(str(e))
        result.data = {"error_detail": str(e)}
    
    result.duration_ms = (time.time() - t0) * 1000
    return result


# ─────────────────────────────────────────────────────────────────────
# PHASE 6: DRUG DELIVERY MATERIAL (materials)
# ─────────────────────────────────────────────────────────────────────

def phase6_material_design(disease_key: str = "mrsa") -> PhaseResult:
    """Design a drug delivery metamaterial for the therapeutic."""
    t0 = time.time()
    result = PhaseResult(phase=6, name="Drug Delivery Material (materials)")
    
    try:
        from materials.ig_material_forge import MaterialForge, MaterialDesign
        
        forge = MaterialForge()
        
        # Design a targeted antibiotic delivery material for MRSA
        # The material targets PBP2a-expressing bacteria with pH-responsive release
        info_line("  Designing MRSA-targeted delivery material...")
        
        # Use the forge to create a material with a specific IG tuple
        # Tuple: molecule/wedge topology, bidirectional coupling, partial symmetry,
        #        quantum coherence, slow kinetics, mesoscale range, sequential composition,
        #        critical self-modeling, two-step memory, heterogeneous, Z2 protection
        mrsa_material_tuple = (
            "𐑼",  # D: infinite-dim (polymer network)
            "𐑶",  # T: box product (encapsulation)
            "𐑾",  # R: bidirectional (responsive release)
            "𐑬",  # P: partial Z2 symmetry (pH-triggered)
            "𐑐",  # F: quantum coherence (DARPin binding)
            "𐑧",  # K: slow kinetics (sustained release)
            "𐑔",  # G: mesoscale (tissue-penetrating)
            "𐑠",  # Gamma: sequential (timed release)
            "⊙",   # Phi: critical (self-regulating)
            "𐑖",  # H: two-step memory (dose tracking)
            "𐑳",  # S: heterogeneous components
            "𐑴",  # W: Z2 topological protection
        )
        
        design = forge.forge("MRSA_Hydrogel_Delivery_System", mrsa_material_tuple)
        
        data = {
            "material_name": design.name,
            "dimensionality": design.dimensionality,
            "topology": design.topology,
            "interface": design.interface,
            "symmetry": design.symmetry,
            "phase": design.phase,
            "kinetics": design.kinetics,
            "interaction_range": design.interaction_range,
            "synthesis": design.synthesis,
            "criticality": design.criticality,
            "memory": design.memory,
            "stoichiometry": design.stoichiometry,
            "topological_protection": design.topological_protection,
            "predicted_properties": design.predicted_properties,
            "target_applications": design.target_applications,
            "frobenius_score": design.frobenius_score,
            "ouroboricity_tier": design.ouroboricity_tier,
            "tuple": "".join(mrsa_material_tuple),
        }
        
        result.data = data
        result.success = True
        
        info_line(f"  Material Design: {design.name}")
        info_line(f"    IG Tuple: {''.join(mrsa_material_tuple)}")
        info_line(f"    Frobenius Score: {design.frobenius_score}")
        info_line(f"    Ouroboricity Tier: {design.ouroboricity_tier}")
        info_line(f"    Predicted Properties: {design.predicted_properties}")
        info_line(f"    Target Applications: {design.target_applications}")
        
    except Exception as e:
        result.success = False
        result.errors.append(str(e))
        result.data = {"error_detail": str(e)}
    
    result.duration_ms = (time.time() - t0) * 1000
    return result
def phase7_clinical_simulation(disease_key: str = "mrsa") -> PhaseResult:
    """Run clinical simulation of therapeutic effect with Frobenius verification."""
    t0 = time.time()
    result = PhaseResult(phase=7, name="Clinical Simulation (therapeutics)")
    
    try:
        from therapeutics.frobenius_chemotherapeutic import (
            FrobeniusChemoSim, FrobeniusChemoState, CancerReceptorModel,
        )
        
        # The FrobeniusChemoSim models targeted drug delivery with Frobenius protection.
        # Healthy cells are protected by mu circ delta = id (Frobenius symmetry, Phi = pm_sym).
        # Cancer cells with broken Frobenius symmetry accumulate drug payload.
        # This is directly analogous to MRSA PBP2a targeting: healthy flora maintain
        # Phi = pm (Frobenius-protected), MRSA breaks symmetry to Phi = super.
        
        info_line("  Initializing Frobenius-coupled chemotherapeutic simulation...")
        info_line("  Principle: Phi-symmetry (pm_sym) protects healthy cells;")
        info_line("            Phi-breaking exposes MRSA (super-critical).")
        print()
        
        # Run the standard simulation with default drug concentration
        sim = FrobeniusChemoSim(dt=0.5, drug_conc=2.0)
        
        # The simulation automatically creates:
        #   - 1 healthy cell line (Frobenius-protected, Phi = pm_sym)
        #   - 5 cancer lines at mutation strengths 0.2, 0.4, 0.6, 0.8, 1.0
        #   - Each line tracked for asymmetry, binding, tether tension,
        #     payload exposure, and cytotoxicity
        
        # Run for 30 time units (simulates drug administration cycle)
        sim.run(total_time=30.0)
        
        # Collect results
        cancer_states = []
        for rec, state in sim.cancer:
            cancer_states.append({
                "type": state.target_type,
                "asymmetry": float(state.asymmetry),
                "cytotoxicity": float(state.cytotoxicity),
                "payload_exposed": float(state.payload_exposed),
            })
        
        healthy_state = {
            "type": sim.healthy.target_type,
            "asymmetry": float(sim.healthy.asymmetry),
            "cytotoxicity": float(sim.healthy.cytotoxicity),
            "payload_exposed": float(sim.healthy.payload_exposed),
        }
        
        # Determine selectivity: ratio of cancer cytotoxicity to healthy
        max_cancer_tox = max(float(s.cytotoxicity) for _, s in sim.cancer) if sim.cancer else 0
        selectivity = max_cancer_tox / max(float(sim.healthy.cytotoxicity), 1e-10)
        
        data = {
            "drug_concentration": sim.drug_conc,
            "simulation_time": sim.time,
            "healthy_cell": healthy_state,
            "cancer_cells": cancer_states,
            "selectivity_ratio": selectivity,
            "principle": "Frobenius-protected (mu circ delta = id) healthy cell vs Phi-broken target cells",
            "mrsa_analog": "MRSA: Phi = super (broken symmetry) vs healthy flora: Phi = pm (protected)",
        }
        
        result.data = data
        result.success = True
        
        # Summary
        success_line(f"\n  Simulation Complete:")
        info_line(f"    Drug concentration: {sim.drug_conc}")
        info_line(f"    Time simulated: {sim.time}")
        info_line(f"    Healthy cytotoxicity: {healthy_state['cytotoxicity']:.4f}")
        info_line(f"    Max cancer cytotoxicity: {max_cancer_tox:.4f}")
        info_line(f"    Selectivity ratio: {selectivity:.0f}x")
        info_line(f"    Cancer lines tracked: {len(cancer_states)}")
        for cs in cancer_states:
            info_line(f"      {cs['type']}: asym={cs['asymmetry']:.4f}, cyto={cs['cytotoxicity']:.4f}, payload={cs['payload_exposed']:.4f}")
        
    except Exception as e:
        result.success = False
        result.errors.append(str(e))
        result.data = {"error_detail": str(e)}
    
    result.duration_ms = (time.time() - t0) * 1000
    return result
def run_pipeline(disease_key: str = DEFAULT_DISEASE,
                 phases: Optional[List[int]] = None,
                 verbose: bool = True) -> PipelineReport:
    """Run the complete 7-phase unified therapeutic design pipeline."""
    
    report = PipelineReport(disease=disease_key)
    
    if phases is None:
        phases = list(range(1, 8))
    
    phase_runners = {
        1: lambda: phase1_structural_diagnosis(disease_key),
        2: lambda: phase2_retrosynthetic_design("penicillin"),
        3: lambda: phase3_protein_processing("HUMAN_INSULIN"),
        4: lambda: phase4_genetic_encoding(disease_key),
        5: lambda: phase5_organism_verification(disease_key),
        6: lambda: phase6_material_design(disease_key),
        7: lambda: phase7_clinical_simulation(disease_key),
    }
    
    if verbose:
        print(BANNER)
        info_line(f"  Disease: {disease_key}")
        info_line(f"  Phases:  {phases}")
        info_line(f"  Time:    {report.timestamp}")
        print()
    
    t_start = time.time()
    
    for phase_num in phases:
        if verbose:
            banner = PHASE_BANNERS.get(phase_num, f"PHASE {phase_num}")
            info_line(f"{'='*68}")
            info_line(f"  {banner}")
            info_line(f"{'='*68}")
        
        try:
            phase_result = phase_runners[phase_num]()
        except Exception as e:
            phase_result = PhaseResult(
                phase=phase_num,
                name=PHASE_BANNERS.get(phase_num, f"Phase {phase_num}"),
                success=False,
                errors=[str(e)]
            )
        
        report.phases.append(phase_result)
        
        # ── Structure Generation Hook ──
        # After phase 2 (ch3mpiler): generate CDXML chemical structures
        # After phase 3 (serpentrod): generate PDB protein structures
        if HAS_STRUCTURE_GEN:
            if phase_num == 2 and phase_result.success:
                if verbose:
                    info_line(f"\n  Generating CDXML structures...")
                struct_result = generate_all_structures(
                    disease_key=disease_key,
                    protein_name="HUMAN_INSULIN",
                    output_dir=str(OUTPUT_DIR),
                    use_esmfold=False,
                )
                # Inject CDXML results into phase data
                phase_result.data["cdxml_generated"] = struct_result.get("cdxml", [])
                if verbose:
                    cdxml_ok = sum(1 for r in struct_result.get("cdxml", []) if "error" not in r)
                    info_line(f"  CDXML: {cdxml_ok} files generated")
            
            elif phase_num == 3 and phase_result.success:
                if verbose:
                    info_line(f"\n  Generating PDB structures...")
                struct_result = generate_all_structures(
                    disease_key=disease_key,
                    protein_name="HUMAN_INSULIN",
                    output_dir=str(OUTPUT_DIR),
                    use_esmfold=False,
                )
                # Inject PDB results into phase data
                phase_result.data["pdb_generated"] = struct_result.get("pdb", [])
                if verbose:
                    pdb_ok = sum(1 for r in struct_result.get("pdb", []) if "error" not in r)
                    info_line(f"  PDB: {pdb_ok} files generated")
        
        if verbose:
            status = "PASS" if phase_result.success else "FAIL"
            info_line(f"\n  Phase {phase_num} {status} ({phase_result.duration_ms:.0f}ms)")
            if phase_result.errors:
                for err in phase_result.errors:
                    info_line(f"    Error: {err}")
            print()
    
    report.total_duration_ms = (time.time() - t_start) * 1000
    report.all_success = all(p.success for p in report.phases)
    
    if verbose:
        info_line(f"{'='*68}")
        info_line(f"  PIPELINE COMPLETE")
        info_line(f"{'='*68}")
        info_line(f"  Disease:       {disease_key}")
        info_line(f"  Phases run:    {len(report.phases)}/7")
        passed = sum(1 for p in report.phases if p.success)
        info_line(f"  Passed:        {passed}/{len(report.phases)}")
        info_line(f"  Total time:    {report.total_duration_ms:.0f}ms")
        info_line(f"  All success:   {report.all_success}")
        
        # Summary table
        info_line(f"\n  Phase Summary:")
        info_line(f"  {'Phase':<8} {'System':<38} {'Status':<8} {'Time':<10}")
        info_line(f"  {'-'*64}")
        for p in report.phases:
            status = "PASS" if p.success else "FAIL"
            system = p.name
            info_line(f"  {p.phase:<8} {system:<38} {status:<8} {p.duration_ms:>6.0f}ms")
    
    return report


def generate_report(report: PipelineReport, output_dir: Path = DOCS_DIR):
    """Generate a markdown report documenting the entire pipeline run."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build the report
    lines = []
    lines.append(f"# Red-Hot Rebis — Unified Therapeutic Design Pipeline Report")
    lines.append(f"")
    lines.append(f"**Author:** Lando⊗⊙perator  ")
    lines.append(f"**Date:** {report.timestamp[:19]}  ")
    lines.append(f"**Disease:** {report.disease}  ")
    lines.append(f"**Pipeline Status:** {'ALL PASSED' if report.all_success else 'PARTIAL FAILURE'}  ")
    lines.append(f"**Total Duration:** {report.total_duration_ms:.0f}ms  ")
    lines.append(f"")
    lines.append(f"## Overview")
    lines.append(f"")
    lines.append(f"This report documents a complete end-to-end therapeutic design pipeline")
    lines.append(f"execution across all 7 red-hot_rebis subsystems: Ars_Therapeutica (structural")
    lines.append(f"diagnosis), ch3mpiler (retrosynthetic design), serpentrod (protein processing),")
    lines.append(f"rhr_p4rky (genetic encoding & Belnap verification), clink (organism-level L0→L8),")
    lines.append(f"materials (drug delivery design), and therapeutics (clinical simulation).")
    lines.append(f"")
    lines.append(f"## Phase Results")
    lines.append(f"")
    
    for p in report.phases:
        status_icon = "✅" if p.success else "❌"
        lines.append(f"### Phase {p.phase}: {p.name} {status_icon}")
        lines.append(f"")
        lines.append(f"- **Status:** {'PASSED' if p.success else 'FAILED'}")
        lines.append(f"- **Duration:** {p.duration_ms:.0f}ms")
        
        if p.errors:
            lines.append(f"- **Errors:** {p.errors}")
        
        if p.data:
            lines.append(f"")
            lines.append(f"```json")
            lines.append(json.dumps(p.data, indent=2, default=str, ensure_ascii=False))
            lines.append(f"```")
        
        lines.append(f"")
    
    # Summary table
    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| Phase | System | Status | Duration |")
    lines.append(f"|-------|--------|--------|----------|")
    for p in report.phases:
        status = "✅" if p.success else "❌"
        lines.append(f"| {p.phase} | {p.name} | {status} | {p.duration_ms:.0f}ms |")
    
    lines.append(f"")
    passed = sum(1 for p in report.phases if p.success)
    lines.append(f"**Total: {passed}/{len(report.phases)} phases passed**")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*There is great merit in following a problem where it leads [1].*")
    lines.append(f"")
    lines.append(f"## References")
    lines.append(f"")
    lines.append(f"[1] Harry T. Larson, \"Catch a Rising Problem and Never Ever Let It Go,\"")
    lines.append(f"*IEEE Computer*, vol. 19, no. 2, pp. 61–63, February 1986.")
    lines.append(f"DOI: 10.1109/MC.1986.1641382")
    
    report_md = "\n".join(lines)
    
    # Write report
    report_path = output_dir / f"pipeline_report_{report.disease}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(report_md)
    
    info_line(f"\n  Report written to: {report_path}")
    
    # Also save JSON
    json_path = output_dir / f"pipeline_data_{report.disease}.json"
    json_data = {
        "disease": report.disease,
        "timestamp": report.timestamp,
        "all_success": report.all_success,
        "total_duration_ms": report.total_duration_ms,
        "phases": [
            {
                "phase": p.phase,
                "name": p.name,
                "success": p.success,
                "data": p.data,
                "errors": p.errors,
                "duration_ms": p.duration_ms,
            }
            for p in report.phases
        ]
    }
    json_path.write_text(json.dumps(json_data, indent=2, default=str, ensure_ascii=False))
    info_line(f"  JSON data written to: {json_path}")
    
    return report_path


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Red-Hot Rebis Unified Therapeutic Design Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 unified_demo/demo.py                     # Full 7-phase pipeline
  python3 unified_demo/demo.py --disease hiv       # HIV instead of MRSA
  python3 unified_demo/demo.py --phase 1           # Just structural diagnosis
  python3 unified_demo/demo.py --phases 1,2,5      # Selected phases
  python3 unified_demo/demo.py --report            # Also generate ig-docs report
  python3 unified_demo/demo.py --list-diseases     # List available diseases
        """
    )
    parser.add_argument("--disease", default=DEFAULT_DISEASE,
                       help=f"Disease key (default: {DEFAULT_DISEASE})")
    parser.add_argument("--phase", type=int, choices=range(1, 8),
                       help="Run a single phase (1-7)")
    parser.add_argument("--phases", type=str,
                       help="Comma-separated phase numbers (e.g. '1,2,5')")
    parser.add_argument("--report", action="store_true",
                       help="Generate markdown report in ig-docs/")
    parser.add_argument("--list-diseases", action="store_true",
                       help="List available diseases and exit")
    parser.add_argument("--output-dir", type=str,
                       help="Output directory for report")
    
    args = parser.parse_args()
    
    # List diseases
    if args.list_diseases:
        try:
            from ars_therapeutica.types import THERAPIES

            info_line("Available diseases:")
            for key, therapy in THERAPIES.items():
                info_line(f"  {key:<20} {therapy.disease}")
        except Exception as e:
            error_line(f"Error loading therapies: {e}")
        return
    
    # Determine phases
    if args.phase:
        phases = [args.phase]
    elif args.phases:
        phases = [int(p.strip()) for p in args.phases.split(",")]
    else:
        phases = None  # All phases
    
    # Run pipeline
    report = run_pipeline(
        disease_key=args.disease,
        phases=phases,
        verbose=True,
    )
    
    # Generate report
    if args.report:
        output_dir = Path(args.output_dir) if args.output_dir else DOCS_DIR
        generate_report(report, output_dir)
    
    # Exit code
    sys.exit(0 if report.all_success else 1)


if __name__ == "__main__":
    main()
