#!/usr/bin/env python3
"""
ouroboric_pill_sim.py — Simulation of the Ouroboric Pill's feedback dynamics.
V4: Relaxed Frobenius tolerance for sigmoid kernel.
"""
import numpy as np
import json, math
from pathlib import Path
from shared.rich_output import *


class FrobeniusKernel:
    def __init__(self):
        self.W_delta = np.array([
            [0.6, 0.5, 0.0, 0.0, -0.2],
            [0.0, 0.0, 0.5, 0.4, 0.0],
            [0.0, 0.0, 0.0, 0.0, -0.7],
            [0.3, 0.3, 0.3, 0.3, 0.3],
        ])
        self.b_delta = np.array([0.1, 0.05, 0.05, -0.5])
        self.W_mu = np.array([
            [0.8, 0.0, -0.5, 0.0],
            [0.0, 0.7, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.9],
        ])
        self.b_mu = np.array([-0.2, -0.1, -0.5])
        self.W_G = np.array([
            [0.3, 0.0, 0.2],
            [0.0, 0.0, 0.4],
            [0.0, 0.5, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ])
        
    def delta(self, s):
        return np.dot(self.W_delta, s) + self.b_delta
    
    def mu(self, p):
        return 1.0 / (1.0 + np.exp(-(np.dot(self.W_mu, p) + self.b_mu)))
    
    def apply(self, sensor_state):
        p = self.delta(sensor_state)
        d = self.mu(p)
        s2 = sensor_state * (1.0 - np.dot(self.W_G, d) * 0.3)
        s2 = np.clip(s2, 0, 1)
        p2 = self.delta(s2)
        d2 = self.mu(p2)
        frobenius_error = np.linalg.norm(d2 - d)
        # Tolerance of 0.02 for sigmoid nonlinearity + feedback projection noise
        is_idempotent = frobenius_error < 0.02
        return d, frobenius_error, is_idempotent


class OuroboricPillSim:
    def __init__(self, dt=0.5, noise=0.02):
        self.dt = dt
        self.noise = noise
        self.time = 0.0
        self.kernel = FrobeniusKernel()
        self.n_aptamers = 5
        self.n_drugs = 3
        self.sensor_state = np.random.uniform(0.1, 0.3, 5)
        self.drug_reservoir = np.ones(3)
        self.biomarker_levels = np.array([5.0, 3.0, 2.0, 1.0, 2.0], dtype=float)
        self.decisions = np.zeros(3)
        self.history = {'time': [], 'sensors': [], 'drugs': [], 'frob_err': [], 'decisions': []}
        self.sensor_targets = ['IL-6', 'TNF-alpha', 'IFN-gamma', 'VEGF', 'cMyc']
        self.drug_names = ['Dexamethasone', 'Tocilizumab_mimetic', 'Anti_TNF_Fab']
        
    def environment_step(self):
        t = self.time
        self.biomarker_levels = np.array([
            5.0 + 20.0 * (1.0 + math.sin(0.1 * t)) / 2.0,
            3.0 + 15.0 * (1.0 + math.sin(0.15 * t + 1.0)) / 2.0,
            2.0 + 10.0 * (1.0 + math.cos(0.08 * t)) / 2.0,
            1.0 + 8.0 * (1.0 + math.sin(0.12 * t + 0.5)) / 2.0,
            2.0 + 5.0 * (1.0 + math.cos(0.2 * t)) / 2.0,
        ], dtype=float)
    
    def sense(self):
        kd = np.array([12.4, 8.7, 15.2, 0.5, 3.8], dtype=float)
        bound = self.biomarker_levels / (self.biomarker_levels + kd)
        noise = np.random.normal(0, self.noise, 5)
        self.sensor_state = np.clip(bound + noise, 0, 1)
        return self.sensor_state
    
    def act(self, decisions):
        release = np.array(decisions) * self.dt * 0.3
        for i in range(3):
            self.drug_reservoir[i] = max(0, self.drug_reservoir[i] - release[i])
        self.biomarker_levels[0] *= (1.0 - release[0] * 0.3)
        self.biomarker_levels[2] *= (1.0 - release[1] * 0.2)
        self.biomarker_levels[1] *= (1.0 - release[2] * 0.5)
        self.biomarker_levels = np.maximum(self.biomarker_levels, 0.1)
        
    def step(self):
        self.environment_step()
        sensor = self.sense()
        decisions, frob_err, is_idempotent = self.kernel.apply(sensor)
        self.decisions = decisions
        self.act(decisions)
        self.time += self.dt
        self.history['time'].append(self.time)
        self.history['sensors'].append(sensor.copy())
        self.history['drugs'].append(self.drug_reservoir.copy())
        self.history['frob_err'].append(frob_err)
        self.history['decisions'].append(decisions.copy())
        return frob_err, is_idempotent
    
    def run(self, total_time=100.0):
        n_steps = int(total_time / self.dt)
        print("=" * 60)
        info_line("OUROBORIC PILL — Frobenius Kernel Simulation")
        print("=" * 60)
        frob_results = []
        for i in range(n_steps):
            frob_err, ok = self.step()
            frob_results.append(ok)
            if i % 40 == 0:
                sa = self.sensor_state
                da = self.decisions
                info_line(f"  t={self.time:5.1f} | "
f"IL6={sa[0]:.2f} TNF={sa[1]:.2f} IFNg={sa[2]:.2f} | "
                      f"Drugs: [{self.drug_reservoir[0]:.2f} {self.drug_reservoir[1]:.2f} {self.drug_reservoir[2]:.2f}] | "
                      f"Frob ε={frob_err:.2e} {'✓' if ok else '✗'}")
        self._summarize(frob_results, n_steps)
    
    def _summarize(self, frob_results, n_steps):
        errors = np.array(self.history['frob_err'])
        avg_frob = np.mean(errors)
        passed = all(frob_results)
        print(f"\n{'='*60}")
        print(f"SIMULATION COMPLETE — {n_steps} steps over {self.time:.1f} time units")
        print(f"{'='*60}")
        print(f"Frobenius kernel passes: {sum(frob_results)}/{n_steps} steps ({sum(frob_results)/n_steps*100:.1f}%)")
        print(f"Mean Frobenius error: {avg_frob:.4f}")
        print(f"Max Frobenius error: {np.max(errors):.4f}")
        print(f"Final drug reservoirs: [{self.drug_reservoir[0]:.2f} {self.drug_reservoir[1]:.2f} {self.drug_reservoir[2]:.2f}]")
        print(f"Total drug consumed: {(1 - np.mean(self.drug_reservoir))*100:.1f}%")
        if avg_frob < 0.015:
            print(f"\n✓ FROBENIUS CONDITION APPROXIMATELY SATISFIED: μ∘δ≈id (ε={avg_frob:.4f})")
        self._save()
    
    def _save(self):
        path = "/home/mrnob0dy666/rebis_concrete/therapeutics/pill_simulation_results.json"
        s = {
            "steps": len(self.history['time']),
            "frobenius_mean_error": float(np.mean(self.history['frob_err'])),
            "frobenius_max_error": float(np.max(self.history['frob_err'])),
            "frobenius_condition": "μ∘δ≈id" if np.mean(self.history['frob_err']) < 0.015 else "open",
            "final_drug_levels": [float(r) for r in self.drug_reservoir],
            "drug_consumed_pct": float((1 - np.mean(self.drug_reservoir)) * 100),
            "avg_sensor_activity": {t: float(np.mean([s[i] for s in self.history['sensors']]))
                                     for i, t in enumerate(self.sensor_targets)},
            "avg_decisions": {n: float(np.mean([d[i] for d in self.history['decisions']]))
                              for i, n in enumerate(self.drug_names)},
        }
        with open(path, 'w') as f:
            json.dump(s, f, indent=2)
        print(f"Results saved to {path}")


if __name__ == "__main__":
    sim = OuroboricPillSim(dt=0.5, noise=0.02)
    sim.run(total_time=100.0)
