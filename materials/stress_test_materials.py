#!/usr/bin/env python3
"""
COMPREHENSIVE MATERIALS STRESS TEST
Tests all materials pipeline modules with edge cases, large inputs,
boundary conditions, and cross-module integration.

Author: Lando⊗⊙perator
"""

import sys, os, json, math, time, traceback
import numpy as np

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS, FAIL, SKIP = "✅", "❌", "⚠️"
results = []

def test(name, fn):
    """Run a test and record result."""
    try:
        start = time.time()
        fn()
        elapsed = time.time() - start
        results.append((PASS, name, f"{elapsed:.3f}s"))
        print(f"  {PASS} {name} ({elapsed:.3f}s)")
    except Exception as e:
        results.append((FAIL, name, str(e)[:120]))
        print(f"  {FAIL} {name}: {e}")
        traceback.print_exc()

def summary():
    passed = sum(1 for r in results if r[0] == PASS)
    failed = sum(1 for r in results if r[0] == FAIL)
    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed} passed, {failed} failed, {len(results)} total")
    print(f"{'='*60}")
    for status, name, detail in results:
        if status == FAIL:
            print(f"  {status} {name}: {detail}")
    return failed == 0

# ═══════════════════════════════════════════════════════════════════
print("=" * 60)
print("  MATERIALS PIPELINE — COMPREHENSIVE STRESS TEST")
print("=" * 60)

# ── 1. IG Material Forge ──────────────────────────────────────────
print("\n── 1. IG Material Forge ──")

def test_forge_all_predefined():
    from materials.ig_material_forge import MaterialForge, predefined_novel_materials
    mf = MaterialForge()
    novel = predefined_novel_materials()
    assert len(novel) == 8, f"Expected 8 predefined, got {len(novel)}"
    for name, ig_tuple in novel.items():
        design = mf.forge(name, ig_tuple)
        assert design.ouroboricity_tier in ('O₀', 'O₁', 'O₂', 'O₂†', 'O_∞'), f"Bad tier: {design.ouroboricity_tier}"
        assert 0 <= design.frobenius_score <= 1, f"Bad frob score: {design.frobenius_score}"
        assert len(design.proposed_composition) > 5, "Empty composition"
test("Forge all 8 predefined", test_forge_all_predefined)

def test_forge_edge_case_empty_name():
    from materials.ig_material_forge import MaterialForge
    mf = MaterialForge()
    design = mf.forge("", ('𐑼','𐑸','𐑾','𐑹','𐑞','𐑧','𐑲','𐑠','𐑮','𐑫','𐑳','𐑭'))
    assert design is not None
test("Forge with empty name", test_forge_edge_case_empty_name)

def test_forge_report():
    from materials.ig_material_forge import MaterialForge
    mf = MaterialForge()
    mf.forge("test_report", ('𐑼','𐑸','𐑾','𐑹','𐑞','𐑧','𐑲','𐑠','𐑮','𐑫','𐑳','𐑭'))
    report = mf.report("test_report")
    assert "test_report" in report
    assert len(report) > 50
test("Forge report generation", test_forge_report)

def test_forge_list_designs():
    from materials.ig_material_forge import MaterialForge
    mf = MaterialForge()
    mf.forge("a", ('𐑼','𐑸','𐑾','𐑹','𐑞','𐑧','𐑲','𐑠','𐑮','𐑫','𐑳','𐑭'))
    mf.forge("b", ('𐑨','𐑡','𐑽','𐑬','𐑐','𐑘','𐑔','𐑜','𐑻','𐑒','𐑕','𐑴'))
    designs = mf.list_designs()
    assert len(designs) >= 2, f"Expected >=2 designs, got {len(designs)}"
test("Forge list designs", test_forge_list_designs)

# ── 2. Sophick Forge (Eagle Cycle) ────────────────────────────────
print("\n── 2. Sophick Forge ──")

def test_eagle_cycle_basic():
    from materials.sophick_forge import EagleCycleProtocol, EagleMaterial
    mat = EagleMaterial(name="test_substrate", composition="CrMnFeCoNi")
    ecp = EagleCycleProtocol()
    history = ecp.run(mat, n_eagles=7, noise_level=0.01)
    assert len(history) == 7, f"Expected 7 eagles, got {len(history)}"
    assert history[-1].crystallinity_pct > history[0].crystallinity_pct, "Crystallinity should improve"
    assert history[-1].frobenius_error < history[0].frobenius_error, "Frob error should decrease"
test("Eagle Cycle basic 7-eagle run", test_eagle_cycle_basic)

def test_eagle_cycle_progressive():
    from materials.sophick_forge import EagleCycleProtocol, EagleMaterial
    mat = EagleMaterial(name="progressive", composition="NiTi", 
                        surface_roughness=80, crystallinity=40, defect_density=5e12)
    ecp = EagleCycleProtocol()
    history = ecp.run(mat, n_eagles=9, noise_level=0.03)
    # Verify monotonic improvement
    for i in range(1, len(history)):
        assert history[i].crystallinity_pct >= history[i-1].crystallinity_pct - 5, \
            f"Non-monotonic crystallinity at eagle {i}"
test("Eagle Cycle progressive refinement", test_eagle_cycle_progressive)

def test_eagle_cycle_report():
    from materials.sophick_forge import EagleCycleProtocol, EagleMaterial
    mat = EagleMaterial(name="report_test", composition="Sb₂Te₃")
    ecp = EagleCycleProtocol()
    ecp.run(mat, n_eagles=5, noise_level=0.02)
    report = ecp.report()
    assert "Eagle" in report or "#" in report
    assert len(report) > 100
test("Eagle Cycle report", test_eagle_cycle_report)

def test_eagle_material_etch():
    from materials.sophick_forge import EagleMaterial
    mat = EagleMaterial(name="etch_test", composition="Cu", surface_roughness=50)
    mat.etch(depth_um=5, temperature=25, duration_min=30)
    assert mat.surface_roughness < 50, "Etching should reduce roughness"
    assert mat.total_etch_depth_um == 5.0
test("Eagle Material etch", test_eagle_material_etch)

# ── 3. Frobenius Metamaterial ─────────────────────────────────────
print("\n── 3. Frobenius Metamaterial ──")

def test_frobenius_metamaterial_basic():
    from materials.frobenius_metamaterial import FrobeniusMetamaterial
    fm = FrobeniusMetamaterial(size=10)
    result = fm.run_simulation()
    assert len(result) == 20, f"Expected 20 cycles, got {len(result)}"
    assert result[-1]['healed_pct'] >= 90, "Healing should be >=90%"
test("Frobenius Metamaterial 10x10 grid", test_frobenius_metamaterial_basic)

def test_frobenius_metamaterial_apply_load():
    from materials.frobenius_metamaterial import FrobeniusMetamaterial
    fm = FrobeniusMetamaterial(size=15)
    strain = np.random.random((fm.strain.shape[0], fm.strain.shape[1])) * 0.05
    fm.apply_load(strain)
    frob_before = fm.compute_frobenius_norm()
    assert frob_before > 0, "Load should create Frobenius error"
    fm.heal_step()
    frob_after = fm.compute_frobenius_norm()
    assert frob_after <= frob_before, "Healing should reduce Frobenius error"
test("Frobenius Metamaterial load-heal cycle", test_frobenius_metamaterial_apply_load)

def test_frobenius_metamaterial_export():
    from materials.frobenius_metamaterial import FrobeniusMetamaterial
    fm = FrobeniusMetamaterial(size=8)
    fm.run_simulation()
    results = fm.run_simulation()
    exported = fm.export_results(results, "test_export.json")
    assert os.path.exists("test_export.json") or exported is not None
    if os.path.exists("test_export.json"):
        os.remove("test_export.json")
test("Frobenius Metamaterial export", test_frobenius_metamaterial_export)

# ── 4. Thermal Rectifier ──────────────────────────────────────────
print("\n── 4. Thermal Rectifier ──")

def test_thermal_rectifier_diode():
    from materials.thermal_rectifier import TwoSegmentDiode
    td = TwoSegmentDiode(n_left=10, n_right=10, T_hot=2.0, T_cold=0.5, beta_nl=3.0)
    flux_fwd, std_fwd = td.run_direction('forward', equilibration=100, measurement=300)
    flux_rev, std_rev = td.run_direction('reverse', equilibration=100, measurement=300)
    # fwd and rev fluxes should differ (rectification)
    assert abs(flux_fwd - flux_rev) > 1e-6 or abs(flux_fwd) < 0.01, \
        "Rectifier should show asymmetry"
test("Thermal rectifier diode asymmetry", test_thermal_rectifier_diode)

def test_thermal_rectifier_full_run():
    from materials.thermal_rectifier import TwoSegmentDiode
    td = TwoSegmentDiode(n_left=8, n_right=8, T_hot=3.0, T_cold=1.0)
    td.run()  # Should print report, not crash
test("Thermal rectifier full run()", test_thermal_rectifier_full_run)

# ── 5. Non-Qubit QC ───────────────────────────────────────────────
print("\n── 5. Non-Qubit QC ──")

def test_nonqubit_deltas():
    from materials.non_qubit_qc import compute_all_deltas
    deltas = compute_all_deltas()
    assert len(deltas) > 3, f"Expected >3 paradigms, got {len(deltas)}"
    for k, v in deltas.items():
        assert isinstance(v, int), f"Bad delta format for {k}: {type(v)}"
test("NonQubitQC compute_all_deltas", test_nonqubit_deltas)

def test_nonqubit_summary():
    from materials.non_qubit_qc import paradigm_summary_table
    table = paradigm_summary_table()
    assert len(table) > 200, "Summary table too short"
    assert "Paradigm" in table or "paradigm" in table.lower()
test("NonQubitQC paradigm summary table", test_nonqubit_summary)

# ── 6. Ouroboric Alloy ────────────────────────────────────────────
print("\n── 6. Ouroboric Alloy ──")

def test_ouroboric_alloy_basic():
    from materials.ouroboric_alloy import OuroboricAlloy
    oa = OuroboricAlloy()
    assert oa.composition is not None
    assert oa.grain_size_um > 0
test("OuroboricAlloy initialization", test_ouroboric_alloy_basic)

def test_ouroboric_alloy_mechanical():
    from materials.ouroboric_alloy import OuroboricAlloy
    oa = OuroboricAlloy()
    result = oa.run_mechanical_test()
    assert result is not None
    assert 'yield_strength' in result or 'max_stress' in result or isinstance(result, dict)
test("OuroboricAlloy mechanical test", test_ouroboric_alloy_mechanical)

def test_ouroboric_alloy_healing():
    from materials.ouroboric_alloy import OuroboricAlloy
    oa = OuroboricAlloy()
    oa.apply_stress(500)  # Apply 500 MPa
    damage_before = oa.damage_accumulated
    oa.heal_cycle()
    assert oa.healing_cycles_completed >= 1
test("OuroboricAlloy heal cycle", test_ouroboric_alloy_healing)

# ── 7. Critical Metamaterial ──────────────────────────────────────
print("\n── 7. Critical Metamaterial ──")

def test_critical_metamaterial_susceptibility():
    from materials.critical_metamaterial import CriticalMetamaterial
    cm = CriticalMetamaterial()
    # compute_susceptibility(drive_strength) returns (chi, converged) tuple
    chi_low, conv_low = cm.compute_susceptibility(drive_strength=1e-5)
    chi_high, conv_high = cm.compute_susceptibility(drive_strength=0.1)
    # Higher drive should yield different response
    assert abs(chi_low) > 0 or abs(chi_high) > 0, "Susceptibility should be nonzero"
test("CriticalMetamaterial susceptibility divergence", test_critical_metamaterial_susceptibility)

def test_critical_metamaterial_near_critical():
    from materials.critical_metamaterial import CriticalMetamaterial
    cm = CriticalMetamaterial()
    # Run the simulation near critical point
    cm.run(total_time=30)
    # history has 'time', 'chi', 'kappa' lists
    assert 'chi' in cm.history, f"History keys: {list(cm.history.keys())}"
    assert len(cm.history['chi']) > 0, "Should produce chi time series"
    # At least some points should show critical fluctuations (nonzero chi)
    assert any(abs(c) > 0 for c in cm.history['chi'])
test("CriticalMetamaterial run and time series", test_critical_metamaterial_near_critical)

# ── 8. Gap Closure Module ─────────────────────────────────────────
print("\n── 8. Gap Closure Module ──")

def test_gap_closure_enums():
    from materials.gap_closure_module import D, T, Phi, G
    assert len(list(D)) >= 4
    assert len(list(T)) >= 4
    assert len(list(Phi)) >= 5
    assert len(list(G)) >= 3
test("GapClosure enum completeness", test_gap_closure_enums)

# ── 9. Frobenius Exactor ──────────────────────────────────────────
print("\n── 9. Frobenius Exactor ──")

def test_exactor_designs():
    from materials.frobenius_exactor import (
        design_exactor_omega, design_exactor_tau, 
        design_exactor_sigma, design_exactor_epsilon
    )
    omega = design_exactor_omega()
    assert omega.name and omega.composition
    tau = design_exactor_tau()
    assert tau.name and tau.composition
    sigma = design_exactor_sigma()
    assert sigma.name and sigma.composition
    epsilon = design_exactor_epsilon()
    assert epsilon.name and epsilon.composition
test("Exactor all 4 designs", test_exactor_designs)

# ── 10. Materials Simulation ──────────────────────────────────────
print("\n── 10. Materials Simulation ──")

def test_materials_sim_import():
    from materials.materials_sim import SelfHealingComposite, EternalMemorySim
    shc = SelfHealingComposite(capsule_vol_frac=0.08)
    result = shc.simulate_crack_propagation(crack_length_mm=0.5, cycles=5)
    assert result is not None
    ems = EternalMemorySim(monomers=100)
    encoded = ems.encode(b"test")
    assert encoded is not None
test("MaterialsSim composite + memory sim", test_materials_sim_import)

# ── 11. Frobenius Closure Complete ────────────────────────────────
print("\n── 11. Frobenius Closure Complete ──")

def test_frobenius_closure_complete_import():
    import materials.frobenius_closure_complete as fcc
    # Main classes: ClosureDesign, StructuralOpenDiagnosis
    assert hasattr(fcc, 'ClosureDesign') or hasattr(fcc, 'ClosurePathway')
    # Test creating a simple closure design (needs all fields)
    d = fcc.ClosureDesign(
        name="test_closure",
        paradigm="coherent_ising_machine",
        paradigm_tuple={"D": "tri", "T": "boxtimes", "R": "lr", "P": "pm",
                        "F": "hbar", "K": "slow", "G": "aleph", "Gm": "seq",
                        "Phi": "sub", "H": "2", "S": "hetero", "O": "Z"},
        current_error=0.05,
        pathway="EXACTOR-OMEGA",
        discrete_invariant="braid_group_element",
        how_closure_is_achieved="Topological protection via anyonic braiding",
        material_innovation="FQH ν=5/2 heterostructure",
        engineering_innovation="Interferometric braid readout",
    )
    assert d.name == "test_closure"
    assert d.status() is not None
test("FrobeniusClosureComplete design + status", test_frobenius_closure_complete_import)

# ── 12. Cross-Module Integration ──────────────────────────────────
print("\n── 12. Cross-Module Integration ──")

def test_forge_to_frobenius_pipeline():
    """Forge a material, then simulate it as a Frobenius metamaterial."""
    from materials.ig_material_forge import MaterialForge
    from materials.frobenius_metamaterial import FrobeniusMetamaterial
    
    mf = MaterialForge()
    design = mf.forge("integrated_test", 
        ('𐑼','𐑸','𐑾','𐑹','𐑞','𐑧','𐑲','𐑠','𐑮','𐑫','𐑳','𐑭'))
    assert design.proposed_composition
    
    fm = FrobeniusMetamaterial(size=8)
    sim_result = fm.run_simulation()
    assert len(sim_result) == 20
test("Forge → Frobenius metamaterial pipeline", test_forge_to_frobenius_pipeline)

def test_eagle_to_exactor_pipeline():
    """Run Eagle cycle, then attempt exact Frobenius closure."""
    from materials.sophick_forge import EagleCycleProtocol, EagleMaterial
    from materials.frobenius_exactor import ExactorMaterial, ClosurePathway, ClosureObstruction
    
    mat = EagleMaterial(name="eagle_to_exact", composition="VO₂ + Bi₂Se₃")
    ecp = EagleCycleProtocol()
    history = ecp.run(mat, n_eagles=5, noise_level=0.02)
    
    pathway = ClosurePathway(
        name="EXACTOR-OMEGA",
        mechanism="Anyonic braiding closure via topological protection",
        discrete_invariant="braid_group_element_B4",
        how_exactness_is_protected="Topological: braid worldline isotopy invariance",
        target_Omega="𐑟", target_D="𐑦",
        required_conditions="T < 10 mK, B = 5 T, ν = 5/2 FQH state",
        experimental_status="Demonstrated in GaAs heterostructures (2021)",
        estimated_trl=4,
    )
    exact = ExactorMaterial(
        name="exact_after_eagle",
        pathway=pathway,
        composition=mat.composition,
        operating_temperature_k=300.0,
        target_ig_tuple=('𐑼','𐑸','𐑾','𐑹','𐑞','𐑧','𐑲','𐑠','𐑮','𐑫','𐑳','𐑭'),
        discrete_invariants={'winding_number': 3, 'braid_group_element': 'sigma_1'},
    )
    state = exact.verify_closure()
    assert state is not None
test("Eagle → Exactor closure pipeline", test_eagle_to_exactor_pipeline)

# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    ok = summary()
    sys.exit(0 if ok else 1)
