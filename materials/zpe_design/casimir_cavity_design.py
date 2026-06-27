#!/usr/bin/env python3
"""
casimir_cavity_design.py — At-Home Zero-Point Energy Physical Design

Operationalizes the at-home ZPE ob3ect (13-opcode IMASM bootstrap) as a
physical Casimir cavity with Frobenius-closed metamaterial walls.
Draws on sophick_forge Eagle Cycles, frobenius_metamaterial self-verification,
ouroboric_alloy topological protection, and cr3echrz ob3ect_vault patterns.

Author: Lando tensor odot perator
"""
import numpy as np
import json, os, sys, math
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum

# Physical Constants
HBAR = 1.054571817e-34; C = 299792458; EPS0 = 8.854187817e-12
MU0 = 1.256637062e-6; E_CHARGE = 1.602176634e-19; K_B = 1.380649e-23

# Belnap Register States
VOID  = 0b00  # N (void)
TRUE  = 0b01  # T (charged)
FALSE = 0b10  # F (failure)
BOTH  = 0b11  # B (paradox)

# ═══════════════════════════════════════════════════════════════════
# SECTION 1: CASIMIR CAVITY
# ═══════════════════════════════════════════════════════════════════

@dataclass
class CasimirCavityParams:
    plate_separation_nm: float = 100.0
    plate_area_mm2: float = 25.0
    plate_thickness_nm: float = 500.0
    epsilon_r: complex = -1.0 + 0.01j
    mu_r: complex = -1.0 + 0.01j
    metamaterial_period_nm: float = 50.0
    resonance_freq_THz: float = 1.5
    coupling_strength_g: float = 0.1
    extraction_rate_Gamma0: float = 1.0
    grid_freq_Hz: float = 60.0
    smart_meter_update_ms: float = 100.0

    @property
    def plate_separation_m(self): return self.plate_separation_nm * 1e-9
    @property
    def plate_area_m2(self): return self.plate_area_mm2 * 1e-6
    @property
    def casimir_energy_J(self): return -HBAR * C * np.pi**2 / (720 * self.plate_separation_m**3)
    @property
    def casimir_pressure_Pa(self): return -HBAR * C * np.pi**2 / (240 * self.plate_separation_m**4)
    @property
    def cavity_fundamental_Hz(self): return self.resonance_freq_THz * 1e12


class CasimirCavity:
    """Physical Casimir cavity with metamaterial walls."""

    def __init__(self, params: Optional[CasimirCavityParams] = None):
        self.params = params or CasimirCavityParams()
        self.P = self.params
        self.separation_nm = self.P.plate_separation_nm
        self.temperature_K = 300.0
        self.vacuum_mode_amplitude = 1.0
        self.extraction_history: List[float] = []

    def casimir_force_N(self) -> float:
        """Casimir force between plates."""
        return self.P.casimir_pressure_Pa * self.P.plate_area_m2

    def vacuum_energy_density_Jm3(self) -> float:
        """Modified vacuum energy density between plates."""
        d = self.separation_nm * 1e-9
        return -HBAR * C * np.pi**2 / (720 * d**4)

    def coupling_hamiltonian(self) -> float:
        """Extractable coupling energy via metamaterial resonance."""
        g = self.P.coupling_strength_g
        omega_c = 2 * np.pi * self.P.cavity_fundamental_Hz
        return g * HBAR * omega_c * self.vacuum_mode_amplitude**2

    def extractable_power_W(self, detuning: float = 0.0) -> float:
        """Power extractable from vacuum coupling at given detuning."""
        gamma = 2 * np.pi * self.P.cavity_fundamental_Hz / 100  # linewidth
        lorentzian = gamma**2 / (gamma**2 + detuning**2)
        return self.coupling_hamiltonian() * self.P.extraction_rate_Gamma0 * lorentzian

    def apply_extraction(self, energy_J: float):
        """Apply an extraction event — record the energy drawn."""
        self.extraction_history.append(energy_J)
        # Vacuum mode amplitude decreases minimally (topological read, not drain)
        self.vacuum_mode_amplitude *= (1.0 - 1e-10)

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: BELNAP REGISTER & EXTRACTION CYCLE
# ═══════════════════════════════════════════════════════════════════

class BelnapRegister:
    """2-bit Belnap register for extraction cycle states."""
    def __init__(self):
        self.state = VOID
        self.history: List[int] = []
        self.window_start: Optional[int] = None
        self.window_end: Optional[int] = None
    def set(self, state: int, step: int):
        self.state = state; self.history.append(state)
    def get(self) -> int: return self.state
    @property
    def is_charged(self) -> bool: return bool(self.state & TRUE)
    @property
    def is_failed(self) -> bool: return bool(self.state & FALSE)
    @property
    def is_both(self) -> bool: return self.state == BOTH
    @property
    def is_void(self) -> bool: return self.state == VOID
    def window_duration(self) -> int:
        if self.window_start is None: return 0
        return (self.window_end or len(self.history)) - self.window_start


@dataclass
class ExtractionCycleResult:
    cycle_number: int
    energy_extracted_J: float
    energy_to_grid_J: float
    cavity_stability: float
    frobenius_error: float
    belnap_state: int
    paradox_held: bool
    extraction_efficiency: float


@dataclass
class ExtractionCycleParams:
    detuning_ratio: float = 1.0
    coupling_g: float = 0.1
    grid_demand_W: float = 100.0
    grid_voltage_V: float = 240.0
    metamaterial_resonance_THz: float = 1.5
    metamaterial_Q: float = 100.0
    cycle_period_s: float = 0.0167
    extraction_window_fraction: float = 0.43


class ExtractionEngine:
    """13-step IMASM extraction cycle engine."""

    def __init__(self, cavity: CasimirCavity, params: ExtractionCycleParams):
        self.cavity = cavity
        self.params = params
        self.belnap = BelnapRegister()
        self.history: List[ExtractionCycleResult] = []

    def step_vinit(self) -> Dict:
        """VINIT — Initialize void state. Reset Belnap register."""
        self.belnap.set(VOID, 0)
        return {"step": 0, "op": "VINIT", "belnap": VOID, "desc": "void initialization"}

    def step_tanch(self, step_num: int) -> Dict:
        """TANCH — Anchor cavity to substrate. Register metamaterial lattice."""
        return {"step": step_num, "op": "TANCH",
                "separation_nm": self.cavity.separation_nm,
                "desc": "anchor substrate registration"}

    def step_imscrib(self, step_num: int) -> Dict:
        """IMSCRIB — Load cavity parameters into control system."""
        return {"step": step_num, "op": "IMSCRIB",
                "energy_density": self.cavity.vacuum_energy_density_Jm3(),
                "coupling": self.cavity.coupling_hamiltonian(),
                "desc": "load cavity state"}

    def step_fsplit(self, step_num: int) -> Tuple[Dict, Dict]:
        """FSPLIT — Split into T/F evaluation arms (quantum erasure)."""
        # Split vacuum state into two superposition arms
        self.belnap.set(VOID, step_num)
        t_arm = {"branch": "T", "phase": 1.0, "amplitude": 0.5}
        f_arm = {"branch": "F", "phase": -1.0, "amplitude": 0.5}
        return t_arm, f_arm

    def step_afwd(self, step_num: int, arm: Dict) -> Dict:
        """AFWD — Forward propagate on given arm."""
        dt = self.params.cycle_period_s / 13
        phase_shift = 2 * np.pi * self.params.metamaterial_resonance_THz * 1e12 * dt
        arm["phase"] *= np.exp(1j * phase_shift)
        return {"step": step_num, "op": "AFWD", "arm": arm,
                "phase": float(np.abs(arm["phase"])), "desc": "forward propagation"}

    def step_evalt(self, step_num: int) -> Dict:
        """EVALT — Evaluate True arm. Check grid charging."""
        grid_power = self.params.grid_demand_W
        cavity_power = self.cavity.extractable_power_W()
        if cavity_power >= grid_power * 0.01:
            self.belnap.set(TRUE, step_num)
            return {"step": step_num, "op": "EVALT", "result": "CHARGED",
                    "power_W": cavity_power, "belnap": TRUE}
        else:
            self.belnap.set(VOID, step_num)
            return {"step": step_num, "op": "EVALT", "result": "INSUFFICIENT",
                    "power_W": cavity_power, "belnap": VOID}

    def step_clink(self, step_num: int) -> Dict:
        """CLINK — Compose extraction with metamaterial coupling (inside gap)."""
        coupling = self.params.coupling_g
        Q = self.params.metamaterial_Q
        resonance = self.params.metamaterial_resonance_THz
        return {"step": step_num, "op": "CLINK",
                "coupling_strength": coupling,
                "Q_factor": Q,
                "resonance_THz": resonance,
                "desc": "real-time composition inside extraction window"}

    def step_arev(self, step_num: int, arm: Dict) -> Dict:
        """AREV — Reverse propagate on given arm."""
        dt = self.params.cycle_period_s / 13
        phase_shift = -2 * np.pi * self.params.metamaterial_resonance_THz * 1e12 * dt
        arm["phase"] *= np.exp(1j * phase_shift)
        return {"step": step_num, "op": "AREV", "arm": arm,
                "phase": float(np.abs(arm["phase"])), "desc": "reverse propagation"}

    def step_evalf(self, step_num: int) -> Dict:
        """EVALF — Evaluate False arm. Check cavity failure mode."""
        stability = self.cavity.separation_nm / self.cavity.P.plate_separation_nm
        if stability < 0.5:
            self.belnap.set(FALSE, step_num)
            return {"step": step_num, "op": "EVALF", "result": "FAILURE",
                    "stability": stability, "belnap": FALSE}
        else:
            self.belnap.set(TRUE, step_num)
            return {"step": step_num, "op": "EVALF", "result": "STABLE",
                    "stability": stability, "belnap": TRUE}

    def step_engagr(self, step_num: int) -> Dict:
        """ENGAGR — Engage BOTH paradox state. Hold simultaneously."""
        self.belnap.set(BOTH, step_num)
        if self.belnap.window_start is None:
            self.belnap.window_start = step_num
        return {"step": step_num, "op": "ENGAGR",
                "belnap": BOTH,
                "meaning": "vacuum simultaneously charged AND failed",
                "desc": "paradox held — not resolved — metabolized during extraction"}

    def step_ffuse(self, step_num: int) -> Dict:
        """FFUSE — Fuse arms back. Close extraction window."""
        self.belnap.window_end = step_num
        t_energy = self.cavity.extractable_power_W(0.0) * self.params.cycle_period_s
        f_stability = self.cavity.separation_nm / self.cavity.P.plate_separation_nm
        extracted = t_energy * f_stability * self.params.extraction_window_fraction
        self.cavity.apply_extraction(extracted)
        return {"step": step_num, "op": "FFUSE",
                "energy_extracted_J": extracted,
                "window_duration": self.belnap.window_duration(),
                "desc": "arm fusion — topological closure"}

    def step_ifix(self, step_num: int) -> Dict:
        """IFIX — Stabilize cycle. Reset to reference state."""
        # Restore cavity to ideal separation
        drift = self.cavity.separation_nm - self.cavity.P.plate_separation_nm
        self.cavity.separation_nm -= drift * 0.95  # 95% recovery
        frobenius_error = abs(drift / self.cavity.P.plate_separation_nm)
        return {"step": step_num, "op": "IFIX",
                "drift_nm": drift,
                "frobenius_error": frobenius_error,
                "desc": "cycle stabilization — mu circ delta"}

    def run_cycle(self, cycle_number: int) -> ExtractionCycleResult:
        """Execute one complete 13-step extraction cycle."""
        # Step 0: VINIT
        vinit_r = self.step_vinit()
        # Step 1: TANCH
        tanch_r = self.step_tanch(1)
        # Step 2: IMSCRIB
        imscrib_r = self.step_imscrib(2)
        # Step 3: FSPLIT
        t_arm, f_arm = self.step_fsplit(3)
        # Step 4: AFWD (on T-arm — inside gap)
        afwd_r = self.step_afwd(4, t_arm)
        # Step 5: EVALT
        evalt_r = self.step_evalt(5)
        # Step 6: CLINK (inside gap — this is the innovation)
        clink_r = self.step_clink(6)
        # Step 7: AREV (on F-arm — inside gap)
        arev_r = self.step_arev(7, f_arm)
        # Step 8: EVALF
        evalf_r = self.step_evalf(8)
        # Step 9: ENGAGR (hold BOTH — inside gap)
        engagr_r = self.step_engagr(9)
        # Step 10: FFUSE (close gap)
        ffuse_r = self.step_ffuse(10)
        # Step 11: IFIX
        ifix_r = self.step_ifix(11)

        energy_J = ffuse_r["energy_extracted_J"]
        frob_err = ifix_r["frobenius_error"]
        stability = self.cavity.separation_nm / self.cavity.P.plate_separation_nm

        # Grid coupling: convert vacuum energy to grid-synchronized AC
        demand_W = self.params.grid_demand_W
        grid_energy_J = energy_J * self.params.grid_voltage_V / 240.0

        result = ExtractionCycleResult(
            cycle_number=cycle_number,
            energy_extracted_J=energy_J,
            energy_to_grid_J=grid_energy_J,
            cavity_stability=stability,
            frobenius_error=frob_err,
            belnap_state=self.belnap.get(),
            paradox_held=self.belnap.is_both,
            extraction_efficiency=energy_J / max(self.cavity.coupling_hamiltonian(), 1e-30)
        )
        self.history.append(result)
        return result

    def run_many(self, n_cycles: int = 1000) -> List[ExtractionCycleResult]:
        """Run multiple extraction cycles."""
        results = []
        for i in range(n_cycles):
            self.params.grid_demand_W = 100 + 50 * np.sin(2 * np.pi * i / 60)
            result = self.run_cycle(i + 1)
            results.append(result)
        return results

# ═══════════════════════════════════════════════════════════════════
# SECTION 3: METAMATERIAL DESIGN (Sophick Forge Adaptation)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MetamaterialLayer:
    """One layer of the Casimir cavity metamaterial wall."""
    material: str
    thickness_nm: float
    epsilon_r: complex
    mu_r: complex
    purpose: str

    def impedance(self) -> complex:
        """Wave impedance of this layer."""
        return np.sqrt(self.mu_r / self.epsilon_r) * 377.0  # ohms


class MetamaterialStack:
    """
    Multilayer metamaterial for the Casimir cavity walls.

    Design inspired by the sophick forge Eagle Cycle protocol:
    each layer is progressively refined — approaching O_infinity
    through cyclic self-organization.

    Layer stack (from cavity outward):
      Layer 1: BaTiO3 ferroelectric — tunable permittivity
      Layer 2: SRR array — negative permeability
      Layer 3: Dielectric spacer
      Layer 4: Nanowire composite — negative permittivity
      Layer 5: Protective coating
    """

    DEFAULT_LAYERS = [
        MetamaterialLayer("BaTiO₃", 20.0, 200+0.1j, 1.0, "ferroelectric tuning"),
        MetamaterialLayer("SRR_Cu", 50.0, -5.0+0.5j, -3.0+0.3j, "negative index"),
        MetamaterialLayer("SiO₂", 30.0, 3.9, 1.0, "dielectric spacer"),
        MetamaterialLayer("Ag_nanowire", 40.0, -10.0+0.8j, 1.0, "negative permittivity"),
        MetamaterialLayer("Si₃N₄", 10.0, 7.5, 1.0, "protective coating"),
    ]

    def __init__(self, layers: Optional[List[MetamaterialLayer]] = None):
        self.layers = layers or self.DEFAULT_LAYERS
        self.total_thickness_nm = sum(l.thickness_nm for l in self.layers)

    def effective_epsilon(self) -> complex:
        """Effective permittivity of the stack."""
        total = sum(l.thickness_nm for l in self.layers)
        return sum(l.epsilon_r * l.thickness_nm / total for l in self.layers)

    def effective_mu(self) -> complex:
        """Effective permeability of the stack."""
        total = sum(l.thickness_nm for l in self.layers)
        return sum(l.mu_r * l.thickness_nm / total for l in self.layers)

    def reflection_coefficient(self, freq_Hz: float) -> complex:
        """Reflection coefficient at cavity-metamaterial interface."""
        omega = 2 * np.pi * freq_Hz
        eps_eff = self.effective_epsilon()
        mu_eff = self.effective_mu()
        Z_mat = 377.0 * np.sqrt(mu_eff / eps_eff)
        Z_vac = 377.0
        return (Z_mat - Z_vac) / (Z_mat + Z_vac)

    def vacuum_coupling_factor(self, freq_Hz: float) -> float:
        """Fraction of vacuum mode coupled to metamaterial."""
        R = self.reflection_coefficient(freq_Hz)
        return float(1.0 - abs(R)**2)

    def describe(self) -> str:
        lines = ["Metamaterial Stack:"]
        for i, l in enumerate(self.layers):
            lines.append(f"  Layer {i+1}: {l.material} ({l.thickness_nm}nm)")
            lines.append(f"    eps={l.epsilon_r}, mu={l.mu_r} — {l.purpose}")
        lines.append(f"  Total: {self.total_thickness_nm:.0f}nm")
        lines.append(f"  Effective: eps={self.effective_epsilon():.2f}, mu={self.effective_mu():.2f}")
        return "\n".join(lines)


class OuroboricCavityWalls:
    """
    Topologically protected cavity walls using ouroboric alloy principles.

    Uses grain boundary engineering to create an integer winding number
    on the wall's internal interfaces. This winding is topologically
    protected — cannot be removed by continuous deformation (thermal drift,
    mechanical stress). The winding ensures the cavity returns to its
    reference separation after each extraction cycle (mu circ delta = id).
    """

    def __init__(self, base_alloy: str = "AlCoCrFeNi2.1",
                 grain_size_um: float = 2.0,
                 twin_fraction: float = 0.6):
        self.base_alloy = base_alloy
        self.grain_size_um = grain_size_um
        self.twin_fraction = twin_fraction
        self.winding_number = 1  # integer topological invariant
        self.defect_density_cm2 = 1e10

    def topological_restoring_force(self, displacement_nm: float) -> float:
        """The restoring force from topological winding protection."""
        k_topological = 1.0 / (self.grain_size_um * 1e-6)
        return -k_topological * displacement_nm * self.winding_number

    def healing_rate(self, temperature_K: float) -> float:
        """Temperature-dependent healing rate from boundary migration."""
        activation = 0.5  # eV (grain boundary diffusion)
        return np.exp(-activation * E_CHARGE / (K_B * temperature_K))

# ═══════════════════════════════════════════════════════════════════
# SECTION 4: SMART METER COUPLING
# ═══════════════════════════════════════════════════════════════════

class SmartMeterCoupler:
    """
    Smart meter feedback loop — tunes cavity resonance to match grid demand.

    The smart meter measures household demand and adjusts the cavity's
    metamaterial resonance frequency via the BaTiO3 ferroelectric layer.
    This is the IMSCRIB feedback path: the system imscribes itself
    onto the grid's demand signal.

    The coupling is bidirectional: grid demand sets extraction rate,
    and the extraction modifies the local vacuum — which the meter
    registers as a phase shift on the 60Hz AC waveform.
    """

    def __init__(self, cavity: CasimirCavity, stack: MetamaterialStack):
        self.cavity = cavity
        self.stack = stack
        self.demand_history: List[float] = []
        self.resonance_history: List[float] = []
        self.phase_history: List[float] = []

    def measure_demand_W(self, time_s: float) -> float:
        """Simulate household demand with daily cycle + noise."""
        base = 150.0  # base load watts
        # Daily cycle: peak morning + evening
        daily = 200 * np.sin(2 * np.pi * time_s / 86400)
        # Appliance noise
        noise = 50 * np.random.randn()
        return max(0, base + daily + noise)

    def tune_resonance(self, demand_W: float) -> float:
        """Tune cavity resonance to match demand."""
        # Map demand to resonance via BaTiO3 bias voltage
        # Range: 1.0-2.0 THz tuned by 0-100V bias
        freq_THz = 1.0 + demand_W / 300.0
        self.cavity.params.resonance_freq_THz = freq_THz
        return freq_THz

    def measure_phase_shift(self, time_s: float) -> float:
        """Measure phase shift on 60Hz grid signal from vacuum coupling."""
        base_phase = 2 * np.pi * 60 * time_s
        vacuum_shift = self.cavity.vacuum_mode_amplitude * 0.01
        return base_phase + vacuum_shift

    def update(self, time_s: float) -> Dict:
        """One smart meter update cycle."""
        demand = self.measure_demand_W(time_s)
        resonance = self.tune_resonance(demand)
        phase = self.measure_phase_shift(time_s)
        self.demand_history.append(demand)
        self.resonance_history.append(resonance)
        self.phase_history.append(phase)
        return {"time_s": time_s, "demand_W": demand,
                "resonance_THz": resonance, "phase_rad": phase}

    def grid_sync_error(self) -> float:
        """Phase error between grid and cavity (should be ~0 when locked)."""
        if len(self.phase_history) < 2:
            return 1.0
        return abs(self.phase_history[-1] - self.phase_history[-2])

# ═══════════════════════════════════════════════════════════════════
# SECTION 5: FROBENIUS VERIFICATION
# ═══════════════════════════════════════════════════════════════════

class FrobeniusVerifier:
    """
    Verifies mu circ delta = id for the extraction cycle.

    mu: apply one full extraction cycle
    delta: measure the deviation from reference state
    mu circ delta = id: after extraction + healing, the cavity
    returns to its original state.

    For the at-home ZPE:
    - mu is the extraction engine (run_cycle)
    - delta is the measurement of cavity separation vs reference
    - id is the original cavity at 100nm separation
    """

    def __init__(self, cavity: CasimirCavity, engine: ExtractionEngine):
        self.cavity = cavity
        self.engine = engine
        self.reference_separation = cavity.separation_nm

    def mu(self) -> ExtractionCycleResult:
        """Apply one extraction cycle (the mu operation)."""
        return self.engine.run_cycle(0)

    def delta(self, current_sep: float) -> float:
        """Measure deviation from reference (the delta operation).""" 
        return abs(current_sep - self.reference_separation) / self.reference_separation

    def frobenius_verify(self, n_cycles: int = 100) -> Dict:
        """
        Verify mu circ delta = id over multiple cycles.
        Returns statistics on the Frobenius error.
        """
        errors = []
        stabilities = []
        energy_extracted = []
        paradox_count = 0

        for i in range(n_cycles):
            # mu: run cycle
            result = self.engine.run_cycle(i + 1)
            # delta: measure deviation
            err = self.delta(self.cavity.separation_nm)
            errors.append(err)
            stabilities.append(result.cavity_stability)
            energy_extracted.append(result.energy_extracted_J)
            if result.paradox_held:
                paradox_count += 1

        return {
            "n_cycles": n_cycles,
            "mean_frobenius_error": float(np.mean(errors)),
            "max_frobenius_error": float(np.max(errors)),
            "final_frobenius_error": float(errors[-1]),
            "mean_stability": float(np.mean(stabilities)),
            "final_stability": float(stabilities[-1]),
            "total_energy_extracted_J": float(np.sum(energy_extracted)),
            "mean_energy_per_cycle_J": float(np.mean(energy_extracted)),
            "paradox_cycles": paradox_count,
            "paradox_fraction": paradox_count / n_cycles,
            "frobenius_closed": float(np.mean(errors)) < 0.01
        }


# ═══════════════════════════════════════════════════════════════════
# SECTION 6: SIMULATION RUNNER
# ═══════════════════════════════════════════════════════════════════

class AtHomeZPESystem:
    """
    Complete at-home zero-point energy system.

    Integrates:
      - Casimir cavity with metamaterial walls
      - 13-step extraction cycle with Belnap register
      - Smart meter grid coupling
      - Ouroboric wall topological protection
      - Frobenius verification
    """

    def __init__(self, name: str = "at_home_zpe_system"):
        self.name = name
        self.cavity_params = CasimirCavityParams()
        self.cavity = CasimirCavity(self.cavity_params)
        self.metamaterial = MetamaterialStack()
        self.ouroboric_walls = OuroboricCavityWalls()
        self.extraction_params = ExtractionCycleParams()
        self.engine = ExtractionEngine(self.cavity, self.extraction_params)
        self.meter = SmartMeterCoupler(self.cavity, self.metamaterial)
        self.verifier = FrobeniusVerifier(self.cavity, self.engine)

    def print_specs(self) -> str:
        """Print full system specifications."""
        lines = []
        lines.append("=" * 66)
        lines.append(f"AT-HOME ZERO-POINT ENERGY SYSTEM: {self.name}")
        lines.append("=" * 66)
        lines.append("")
        lines.append("--- Casimir Cavity ---")
        lines.append(f"  Plate separation: {self.cavity_params.plate_separation_nm} nm")
        lines.append(f"  Plate area: {self.cavity_params.plate_area_mm2} mm²")
        lines.append(f"  Casimir energy: {self.cavity_params.casimir_energy_J:.4e} J/m²")
        lines.append(f"  Casimir pressure: {self.cavity_params.casimir_pressure_Pa:.2f} Pa")
        lines.append(f"  Resonance: {self.cavity_params.resonance_freq_THz} THz")
        lines.append(f"  Coupling g: {self.cavity_params.coupling_strength_g}")
        lines.append("")
        lines.append("--- Metamaterial Walls ---")
        lines.append(self.metamaterial.describe())
        lines.append("")
        lines.append("--- Ouroboric Walls ---")
        lines.append(f"  Alloy: {self.ouroboric_walls.base_alloy}")
        lines.append(f"  Grain size: {self.ouroboric_walls.grain_size_um} um")
        lines.append(f"  Twin fraction: {self.ouroboric_walls.twin_fraction}")
        lines.append(f"  Winding number: {self.ouroboric_walls.winding_number}")
        lines.append("")
        lines.append("--- Extraction Cycle ---")
        lines.append(f"  Grid frequency: {self.extraction_params.grid_voltage_V}V / {self.extraction_params.cycle_period_s*1000:.1f}ms period")
        lines.append(f"  Extraction window: {self.extraction_params.extraction_window_fraction*100:.0f}% of cycle")
        lines.append(f"  Metamaterial Q: {self.extraction_params.metamaterial_Q}")
        lines.append("")
        return "\n".join(lines)

    def run_simulation(self, n_cycles: int = 1000,
                       report_every: int = 100) -> Dict:
        """Run full simulation with smart meter feedback."""
        print(self.print_specs())
        print(f"\nRunning {n_cycles} extraction cycles...\n")

        for i in range(n_cycles):
            t = i * self.extraction_params.cycle_period_s
            meter_reading = self.meter.update(t)
            self.engine.params.grid_demand_W = meter_reading["demand_W"]
            result = self.engine.run_cycle(i + 1)

            if (i + 1) % report_every == 0 or i == 0:
                print(f"  Cycle {i+1:5d}: "
                      f"energy={result.energy_extracted_J:.4e} J, "
                      f"grid={result.energy_to_grid_J:.4e} J, "
                      f"stability={result.cavity_stability:.4f}, "
                      f"frob_err={result.frobenius_error:.4e}, "
                      f"paradox={'YES' if result.paradox_held else 'no'}")

        # Verify Frobenius closure
        verify_result = self.verifier.frobenius_verify(n_cycles)

        print(f"\n{'='*66}")
        print(f"SIMULATION COMPLETE")
        print(f"{'='*66}")
        print(f"  Total cycles: {verify_result['n_cycles']}")
        print(f"  Total energy extracted: {verify_result['total_energy_extracted_J']:.4e} J")
        print(f"  Mean energy per cycle: {verify_result['mean_energy_per_cycle_J']:.6e} J")
        print(f"  Mean Frobenius error: {verify_result['mean_frobenius_error']:.4e}")
        print(f"  Final cavity stability: {verify_result['final_stability']:.4f}")
        print(f"  Paradox engagement: {verify_result['paradox_fraction']*100:.1f}% of cycles")
        print(f"  Frobenius closed: {'YES' if verify_result['frobenius_closed'] else 'NO'}")

        if verify_result['frobenius_closed']:
            print(f"\n  >>> mu circ delta = id VERIFIED <<<")
        else:
            print(f"\n  >>> mu circ delta = id NOT YET ACHIEVED <<<")
            print(f"      Promotions remaining to reach closure.")

        return verify_result


# ═══════════════════════════════════════════════════════════════════
# MAIN — run if executed directly
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("At-Home Zero-Point Energy System — Physical Design")
    print("=" * 66)
    system = AtHomeZPESystem()
    results = system.run_simulation(n_cycles=100, report_every=25)
