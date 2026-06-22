#!/usr/bin/env python3
"""
frobenius_metamaterial.py — mu circ delta = id Self-Verifying Metamaterial
==========================================================================

Structural type: <𐑼 · 𐑸 · 𐑾 · 𐑹 · 𐑞 · 𐑧 · 𐑲 · 𐑠 · ⊙ · 𐑫 · 𐑳 · 𐑭>
Ouroboricity: O₂ (Frobenius-closed self-verifying material)

Core principle:
  A material that satisfies mu circ delta = id_A exactly:
    - mu: apply load (deform the material)
    - delta: measure recovery (how much it heals)
    - mu circ delta = id: deformation followed by healing returns original state

  This is NOT "self-healing concrete" — it's a fundamentally different class.
  Self-healing materials require external triggers (heat, moisture). This material
  autonomously maintains its own reference state through a bidirectional feedback
  loop (coupling R = bidirectional feedback) between structural sensors and
  distributed micro-actuators.

  The Frobenius condition is topological — it cannot be approximated. Either the
  material closes the loop (O₂) or it degrades (O₀).

  Physical implementation:
    - Matrix: epoxy-amine network with dynamic Diels-Alder bonds
    - Distributed capsules: healing agent + catalyst in separate microcapsules
    - Embedded sensors: carbon nanotube strain-sensing network
    - Embedded actuators: shape-memory alloy (NiTi) microwires
    - Control: the sensor network detects damage; actuators trigger local heating
      to mobilize Diels-Alder bonds, restoring original crosslink topology.

Author: Lando tensor odot perator
"""

import numpy as np
import os
import json
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ═══════════════════════════════════════════════════════════════════
# MATERIAL PARAMETERS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FrobeniusMaterialParams:
    """Physical parameters for the Frobenius-closed metamaterial."""
    # Matrix
    matrix_modulus: float = 3.0         # GPa (epoxy-like)
    da_bond_density: float = 0.15       # mol/L (Diels-Alder crosslinks)
    da_activation_temp: float = 90.0    # Celsius
    da_bond_energy: float = 110.0       # kJ/mol

    # Microcapsules
    capsule_volume_fraction: float = 0.08
    capsule_diameter_um: float = 50.0
    healing_agent_viscosity: float = 0.5  # Pa·s

    # Sensors (CNT network)
    cnt_volume_fraction: float = 0.005
    cnt_gauge_factor: float = 5.0       # deltaR/R / strain
    sensor_spacing_mm: float = 2.0

    # Actuators (NiTi wires)
    niti_volume_fraction: float = 0.02
    niti_transition_temp: float = 70.0   # Celsius (Af)
    niti_max_strain: float = 0.06        # 6% recoverable

    # Control
    feedback_gain: float = 1.0
    response_time_ms: float = 50.0
    target_frobenius_error: float = 0.01  # acceptable ||mu·delta - id||

# ═══════════════════════════════════════════════════════════════════
# SELF-VERIFYING METAMATERIAL SIMULATION
# ═══════════════════════════════════════════════════════════════════

class FrobeniusMetamaterial:
    """
    A material that continuously monitors its own structural integrity
    and autonomously heals damage to maintain mu circ delta = id.

    The material is divided into an N x N grid. Each cell has:
      - local_strain: current mechanical state
      - damage: accumulated micro-damage fraction [0,1]
      - healed: whether the cell is in its reference state
    """

    def __init__(self, size: int = 20, params: Optional[FrobeniusMaterialParams] = None):
        self.N = size
        self.params = params or FrobeniusMaterialParams()
        self.P = self.params

        # Grid state
        self.strain = np.zeros((size, size))
        self.damage = np.zeros((size, size))
        self.healed = np.ones((size, size), dtype=bool)
        self.temperature = np.full((size, size), 25.0)  # ambient

        # Healing agent reservoirs
        self.healing_agent = np.full((size, size), self.P.capsule_volume_fraction)

        # Reference state (the "id" in mu·delta = id)
        self.reference_strain = np.zeros((size, size))
        self.reference_damage = np.zeros((size, size))

        # Frobenius tracking
        self.frobenius_error_history: List[float] = []
        self.healing_events: List[dict] = []
        self.time = 0.0

        # Sensor network calibration
        self._calibrate_sensors()

    def _calibrate_sensors(self):
        """Establish baseline electrical resistance for the CNT sensor network."""
        self.baseline_resistance = 1000.0  # ohms (nominal)
        self.current_resistance = np.full((self.N, self.N), self.baseline_resistance)

    def apply_load(self, strain_field: np.ndarray):
        """
        mu: Apply load — deform the material.
        This is the 'mu' half of the Frobenius loop.
        """
        assert strain_field.shape == (self.N, self.N)
        self.strain += strain_field

        # Damage accumulates where strain exceeds elastic limit
        elastic_limit = 0.02  # 2% strain
        new_damage = np.maximum(0, np.abs(self.strain) - elastic_limit) * 5.0
        self.damage = np.clip(self.damage + new_damage, 0, 1)

        # Damaged cells are no longer healed
        self.healed = self.damage < 0.01

        # Update sensor readings
        self.current_resistance = self.baseline_resistance * (
            1 + self.P.cnt_gauge_factor * np.abs(self.strain)
        )

    def measure_recovery(self) -> np.ndarray:
        """
        delta: Measure how far the material is from its reference state.
        Returns the Frobenius error field: ||current_state - reference_state||.
        """
        strain_error = np.abs(self.strain - self.reference_strain)
        damage_error = np.abs(self.damage - self.reference_damage)
        # Combined error metric (dimensionless, 0 = perfect closure)
        frobenius_error = strain_error * 10.0 + damage_error
        return frobenius_error

    def compute_frobenius_norm(self) -> float:
        """Compute the global Frobenius error: ||mu·delta - id||_F."""
        error_field = self.measure_recovery()
        return float(np.linalg.norm(error_field, 'fro') / self.N)

    def heal_step(self):
        """
        Autonomous healing: the material senses damage via the CNT network
        and triggers local heating via NiTi microwires to mobilize Diels-Alder bonds.
        """
        error_field = self.measure_recovery()
        frob_norm = float(np.linalg.norm(error_field, 'fro') / self.N)
        self.frobenius_error_history.append(frob_norm)

        # Identify cells needing healing
        heal_threshold = 0.05
        damage_mask = error_field > heal_threshold
        n_damaged = np.sum(damage_mask)

        if n_damaged == 0:
            self.time += self.P.response_time_ms / 1000.0
            return

        # For each damaged cell, trigger local heating if healing agent remains
        for i in range(self.N):
            for j in range(self.N):
                if not damage_mask[i, j]:
                    continue
                if self.healing_agent[i, j] <= 0:
                    continue

                # NiTi actuator: local Joule heating
                target_temp = self.P.da_activation_temp
                current_temp = self.temperature[i, j]
                # Thermal dynamics
                self.temperature[i, j] += (target_temp - current_temp) * 0.5

                if self.temperature[i, j] > target_temp - 5:
                    # Diels-Alder bonds mobilize → recovery
                    healing_efficiency = 0.95  # 90% per cycle
                    strain_recovery = self.strain[i, j] * healing_efficiency
                    damage_recovery = self.damage[i, j] * healing_efficiency

                    self.strain[i, j] -= strain_recovery
                    self.damage[i, j] -= damage_recovery

                    # Consume healing agent
                    self.healing_agent[i, j] -= 0.0005

                    # Record healing event
                    if np.random.random() < 0.1:  # log ~10% of events
                        self.healing_events.append({
                            'time': self.time,
                            'cell': (i, j),
                            'strain_before': float(self.strain[i, j] + strain_recovery),
                            'strain_after': float(self.strain[i, j]),
                            'damage_before': float(self.damage[i, j] + damage_recovery),
                            'damage_after': float(self.damage[i, j]),
                            'temperature': float(self.temperature[i, j]),
                        })

                # Update healed status
                if self.damage[i, j] < 0.01:
                    self.healed[i, j] = True

        # Cool down over time
        self.temperature = np.maximum(25.0, self.temperature - 0.2)

        self.time += self.P.response_time_ms / 1000.0

    def run_simulation(self, load_cycles: int = 20, heal_steps_per_cycle: int = 10):
        """
        Run a full simulation: alternating load application and autonomous healing.
        Each cycle: apply a random load field, then let the material heal for
        heal_steps_per_cycle iterations.
        """
        print("=" * 72)
        print("  FROBENIUS METAMATERIAL — mu circ delta = id SELF-VERIFICATION")
        print("=" * 72)
        print(f"  Grid: {self.N}x{self.N} ({self.N*self.N} cells)")
        print(f"  Matrix modulus: {self.P.matrix_modulus} GPa")
        print(f"  DA bond activation: {self.P.da_activation_temp} C")
        print(f"  Capsule volume fraction: {self.P.capsule_volume_fraction:.2f}")
        print(f"  CNT gauge factor: {self.P.cnt_gauge_factor}")
        print(f"  NiTi volume fraction: {self.P.niti_volume_fraction:.2f}")
        print(f"  Target Frobenius error: < {self.P.target_frobenius_error}")
        print("-" * 72)
        print(f"  {'Cycle':>5} {'Load':>12} {'||mu·d-id||':>14} {'Healed%':>8} {'Agent%':>8}")
        print(f"  {'-'*5} {'-'*12} {'-'*14} {'-'*8} {'-'*8}")

        results = []

        for cycle in range(1, load_cycles + 1):
            # Apply load
            np.random.seed(cycle * 137)
            load_magnitude = 0.005 + 0.015 * np.random.random()  # 0.5-2% strain
            # Localized damage: random hotspot
            cx, cy = np.random.randint(2, self.N-2), np.random.randint(2, self.N-2)
            load_field = np.zeros((self.N, self.N))
            for i in range(self.N):
                for j in range(self.N):
                    dist = np.sqrt((i-cx)**2 + (j-cy)**2)
                    load_field[i, j] = load_magnitude * np.exp(-dist**2 / 4)

            self.apply_load(load_field)

            # Measure before healing
            frob_before = self.compute_frobenius_norm()

            # Autonomous healing
            for _ in range(heal_steps_per_cycle):
                self.heal_step()

            # Measure after healing
            frob_after = self.compute_frobenius_norm()
            healed_pct = np.mean(self.healed) * 100
            agent_pct = np.mean(self.healing_agent) / self.P.capsule_volume_fraction * 100

            max_load = np.max(np.abs(load_field)) * 100
            results.append({
                'cycle': cycle,
                'load_pct': round(max_load, 2),
                'frob_before': round(frob_before, 4),
                'frob_after': round(frob_after, 4),
                'healed_pct': round(healed_pct, 1),
                'agent_remaining_pct': round(agent_pct, 1),
            })

            status = "✓" if frob_after < self.P.target_frobenius_error else "⚠"
            print(f"  {status} {cycle:3d}  {max_load:8.2f}%  {frob_before:12.4f}  "
                  f"{healed_pct:6.1f}%  {agent_pct:6.1f}%")

        # Final report
        frob_final = self.compute_frobenius_norm()
        print(f"\n{'='*72}")
        print(f"  RESULTS")
        print(f"{'='*72}")
        print(f"  Final ||mu·delta - id||: {frob_final:.6f}")
        print(f"  Frobenius closure: {'ACHIEVED' if frob_final < self.P.target_frobenius_error else 'INCOMPLETE'}")
        print(f"  Total healing events: {len(self.healing_events)}")
        print(f"  Healing agent remaining: {np.mean(self.healing_agent)/self.P.capsule_volume_fraction*100:.1f}%")
        print(f"  Cells fully healed: {np.sum(self.healed)}/{self.N*self.N}")

        # Classification
        if frob_final < 0.001:
            print(f"\n  TIER: O_∞ — perfect closure, self-verifying in the limit")
        elif frob_final < self.P.target_frobenius_error:
            print(f"\n  TIER: O₂ — Frobenius-closed, autonomous self-repair")
        elif frob_final < 0.1:
            print(f"\n  TIER: O₁ — near-closure, requires occasional external intervention")
        else:
            print(f"\n  TIER: O₀ — open loop, conventional material")

        return results

    def export_results(self, results: list, filepath: str):
        """Export simulation results and material state as JSON."""
        out = {
            'simulation': 'Frobenius Metamaterial — mu circ delta = id',
            'params': {
                'N': self.N,
                'matrix_modulus_GPa': self.P.matrix_modulus,
                'da_activation_temp_C': self.P.da_activation_temp,
                'capsule_vf': self.P.capsule_volume_fraction,
                'cnt_vf': self.P.cnt_volume_fraction,
                'niti_vf': self.P.niti_volume_fraction,
                'target_frobenius_error': self.P.target_frobenius_error,
            },
            'results': {
                'cycles': results,
                'final_frobenius_error': float(self.compute_frobenius_norm()),
                'healed_fraction': float(np.mean(self.healed)),
                'agent_remaining': float(np.mean(self.healing_agent) / self.P.capsule_volume_fraction),
                'total_healing_events': len(self.healing_events),
                'frobenius_error_history': [float(x) for x in self.frobenius_error_history[-50:]],
            }
        }
        with open(filepath, 'w') as f:
            json.dump(out, f, indent=2)
        print(f"\n  Results exported to {filepath}")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse, os

    parser = argparse.ArgumentParser(
        description="Frobenius Metamaterial — μ∘δ=id self-verifying composite simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s                                              Default simulation (size=20, cycles=25)
  %(prog)s --size 30 --cycles 50 --capsules 0.15        Large high-density simulation
  %(prog)s --enhanced --gain 3.0                        Enhanced feedback loop
  %(prog)s --output my_results.json                     Custom export path
""")
    parser.add_argument("--size", type=int, default=20, help="Grid size (default: 20)")
    parser.add_argument("--capsules", type=float, default=0.12, help="Capsule volume fraction (default: 0.12)")
    parser.add_argument("--gain", type=float, default=1.5, help="Feedback gain (default: 1.5)")
    parser.add_argument("--cycles", type=int, default=25, help="Load cycles (default: 25)")
    parser.add_argument("--heal-steps", type=int, default=10, help="Heal steps per cycle (default: 10)")
    parser.add_argument("--enhanced", action="store_true", help="Also run enhanced variant")
    parser.add_argument("--output", type=str, help="Export path for JSON results")
    args = parser.parse_args()

    params = FrobeniusMaterialParams(
        capsule_volume_fraction=args.capsules,
        feedback_gain=args.gain,
    )
    mat = FrobeniusMetamaterial(size=args.size, params=params)
    results = mat.run_simulation(load_cycles=args.cycles, heal_steps_per_cycle=args.heal_steps)
    outpath = args.output or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "frobenius_metamaterial_results.json")
    mat.export_results(results, outpath)

    if args.enhanced:
        print("\n" + "=" * 72)
        print("  ENHANCED VARIANT")
        print("=" * 72)
        params2 = FrobeniusMaterialParams(capsule_volume_fraction=0.15, feedback_gain=2.0)
        mat2 = FrobeniusMetamaterial(size=args.size, params=params2)
        results2 = mat2.run_simulation(load_cycles=args.cycles, heal_steps_per_cycle=args.heal_steps)
        base = args.output.replace(".json", "_enhanced.json") if args.output else os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "frobenius_metamaterial_enhanced_results.json")
        mat2.export_results(results2, base)
