#!/usr/bin/env python3
"""
neurotrophic_factor.py — Bidirectional Neurotrophic Factor (BNF).

Structural type: ⟨𐑦𐑥𐑾𐑬𐑐𐑧𐑔𐑜⊙𐑖𐑙𐑷⟩
Ouroboricity: O₂ (bidirectional feedback with neural signaling)
C-score: 0.0 (critical but not self-modeling)

Core principle:
  Standard neurotrophic factors (BDNF, NGF, GDNF) are administered as
  static doses — they cannot respond to neural activity. The BNF is an
  engineered fusion protein with:
    1. A neurotransmitter-sensing domain (ACh/glutamate binding)
    2. A neurotrophic signaling domain (TrkB agonism)
    3. A bidirectional feedback loop between them

  When neural activity is HIGH (excitotoxicity risk):
    → BNF reduces TrkB signaling (protective downregulation)
  When neural activity is LOW (atrophy risk):
    → BNF increases TrkB signaling (trophic support)

  This creates a homeostatic feedback loop that dynamically matches
  trophic support to neural demand — exactly when and where needed.

  The 𐑾 (bidirectional feedback) primitive is the core structural
  innovation: the drug does not just deliver a signal, it READS the
  environment and RESPONDS in a closed loop.

Applications:
  - Alzheimer's disease (cholinergic neuron maintenance)
  - Parkinson's disease (dopaminergic neuron support)
  - ALS (motor neuron protection during hyperexcitability)
  - Stroke recovery (activity-dependent plasticity enhancement)
"""

import numpy as np
import json
from dataclasses import dataclass
from typing import List, Tuple
from shared.rich_output import *



@dataclass
class NeuralEnvironment:
    """Models the neural microenvironment."""
    # Neurotransmitter levels (normalized 0-1)
    acetylcholine: float = 0.3    # cholinergic tone
    glutamate: float = 0.2        # excitatory tone
    dopamine: float = 0.3         # dopaminergic tone
    serotonin: float = 0.3        # serotonergic tone
    
    # Neural health markers
    bdnf_endogenous: float = 0.5  # natural BDNF level
    oxidative_stress: float = 0.1 # ROS level
    calcium: float = 0.2          # intracellular Ca²⁺
    synaptic_density: float = 0.7 # synapse count relative to healthy
    
    # Disease state
    neurodegeneration: float = 0.0  # 0=healthy, 1=severe
    inflammation: float = 0.1       # neuroinflammation


class BidirectionalFactor:
    """
    The Bidirectional Neurotrophic Factor (BNF) with feedback coupling.
    
    Architecture:
      δ (sense)  : Read neurotransmitter levels
      φ (compute): Determine required trophic response
      μ (act)    : Deliver TrkB signal
    
    The key innovation is the coupling: δ and μ are linked so that
    the system's output depends on its input in a closed loop.
    """
    
    def __init__(self):
        # Sensor affinities (Kd values)
        self.kd_ach = 0.3    # ACh binding affinity
        self.kd_glu = 0.4    # Glutamate binding affinity
        
        # Response parameters
        self.baseline_output = 0.5     # basal TrkB activation
        self.max_output = 1.0           # max activation
        self.min_output = 0.05          # min activation
        self.adaptation_rate = 0.1      # how fast response adapts
        
        # Homeostatic setpoint
        self.target_activity = 0.4      # optimal activity level
        self.response_gain = 0.8        # feedback strength
        
        # Memory (for tracking trends)
        self.prev_activity = 0.3
        self.integrated_error = 0.0
    
    def sense(self, env: NeuralEnvironment) -> float:
        """Measure net neural activity from neurotransmitter levels."""
        # ACh and glutamate are the primary drivers
        ach_bound = env.acetylcholine / (env.acetylcholine + self.kd_ach)
        glu_bound = env.glutamate / (env.glutamate + self.kd_glu)
        
        # Net activity (weighted sum)
        activity = 0.6 * ach_bound + 0.4 * glu_bound
        
        # Modulate by other neurotransmitters
        activity *= (1.0 + 0.2 * env.dopamine)
        
        return np.clip(activity, 0, 1)
    
    def compute_response(self, activity: float, dt: float) -> float:
        """
        Compute the trophic response from sensed activity.
        
        The feedback is INVERTING: high activity → low response, low → high.
        This is the 𐑾 bidirectional coupling.
        """
        # Error: deviation from target
        error = self.target_activity - activity
        
        # Integrated error (with leakage to prevent windup)
        self.integrated_error += error * dt * self.adaptation_rate
        self.integrated_error *= 0.95  # leakage
        
        # Rate of change (derivative)
        d_activity = (activity - self.prev_activity) / max(dt, 0.01)
        
        # PID response
        p_term = self.response_gain * error
        i_term = 0.3 * self.integrated_error
        d_term = 0.1 * (-d_activity)  # anticipate changes
        
        output = self.baseline_output + p_term + i_term + d_term
        
        # Memory update
        self.prev_activity = activity
        
        return np.clip(output, self.min_output, self.max_output)
    
    def act(self, output: float, env: NeuralEnvironment, dt: float) -> dict:
        """
        Apply the trophic signal to the neural environment.
        
        The output modulates:
          1. Synaptic density (via TrkB/MAPK pathway)
          2. Oxidative stress protection (via PI3K/Akt)
          3. Calcium buffering (via BDNF-induced gene expression)
        """
        # Map output to biological effects
        trophic_strength = output
        
        # Synaptic protection
        synaptic_change = (trophic_strength - 0.3) * dt * 0.05
        env.synaptic_density = np.clip(env.synaptic_density + synaptic_change, 0.1, 1.0)
        
        # Oxidative stress reduction
        stress_protection = trophic_strength * dt * 0.03
        env.oxidative_stress = np.clip(env.oxidative_stress - stress_protection, 0, 1)
        
        # Neurodegeneration reversal (slow)
        neuro_recovery = trophic_strength * dt * 0.01 * (1.0 - env.neurodegeneration)
        env.neurodegeneration = np.clip(env.neurodegeneration - neuro_recovery, 0, 1)
        
        # Inflammation modulation
        if trophic_strength > 0.6:
            env.inflammation = np.clip(env.inflammation - dt * 0.02, 0, 1)
        
        return {
            "trophic_output": trophic_strength,
            "synaptic_delta": synaptic_change,
            "stress_delta": -stress_protection
        }


class BNFSim:
    """
    Simulation of Bidirectional Neurotrophic Factor in a neural environment.
    """
    
    def __init__(self, disease: str = "alzheimer", bnf_active: bool = True):
        self.bnf = BidirectionalFactor()
        self.bnf_active = bnf_active
        self.time = 0.0
        self.dt = 0.2
        
        # Initialize neural environment based on disease
        self.env = NeuralEnvironment()
        if disease == "alzheimer":
            self.env.acetylcholine = 0.15  # cholinergic deficit
            self.env.neurodegeneration = 0.4
            self.env.synaptic_density = 0.4
            self.env.inflammation = 0.5
        elif disease == "parkinson":
            self.env.dopamine = 0.08  # dopaminergic deficit
            self.env.neurodegeneration = 0.3
            self.env.synaptic_density = 0.5
        elif disease == "als":
            self.env.glutamate = 0.6  # excitotoxicity
            self.env.oxidative_stress = 0.7
            self.env.neurodegeneration = 0.5
        else:  # healthy
            pass
        
        self.disease = disease
        self.responses = []
        self.activities = []
    
    def _activity_fluctuation(self):
        """Simulate natural neural activity fluctuations (circadian, etc.)."""
        t = self.time
        # Daily rhythm
        circadian = 0.2 * np.sin(2 * np.pi * t / 24.0)
        # Burst noise
        burst = np.random.exponential(0.05) * np.random.choice([-1, 1])
        return circadian + burst * 0.1
    
    def step(self):
        """One simulation step."""
        self.time += self.dt
        
        # Natural activity fluctuation
        fluct = self._activity_fluctuation()
        
        if self.disease == "alzheimer":
            self.env.acetylcholine += fluct * self.dt * 0.1
            self.env.acetylcholine = np.clip(self.env.acetylcholine, 0.02, 0.5)
        elif self.disease == "parkinson":
            self.env.dopamine += fluct * self.dt * 0.05
            self.env.dopamine = np.clip(self.env.dopamine, 0.02, 0.4)
        elif self.disease == "als":
            self.env.glutamate += fluct * self.dt * 0.2
            self.env.glutamate = np.clip(self.env.glutamate, 0.1, 0.8)
        
        # Natural disease progression (slow worsening)
        self.env.neurodegeneration += self.dt * 0.002
        self.env.neurodegeneration = np.clip(self.env.neurodegeneration, 0, 1)
        
        if self.bnf_active:
            # BNF loop: sense → compute → act
            activity = self.bnf.sense(self.env)
            output = self.bnf.compute_response(activity, self.dt)
            effects = self.bnf.act(output, self.env, self.dt)
            
            self.responses.append(effects)
            self.activities.append(activity)
    
    def run(self, total_time: float = 100.0):
        """Run full simulation."""
        n_steps = int(total_time / self.dt)
        
        info_line("=" * 70)
        info_line(f"BIDIRECTIONAL NEUROTROPHIC FACTOR — {self.disease.upper()}")
        info_line("=" * 70)
        info_line(f"BNF system: {'ACTIVE 𐑾' if self.bnf_active else 'DISABLED'}")
        info_line(f"Initial conditions:")
        info_line(f"  ACh={self.env.acetylcholine:.2f}, Glut={self.env.glutamate:.2f}")
        info_line(f"  Synaptic density: {self.env.synaptic_density:.2f}")
        info_line(f"  Neurodegeneration: {self.env.neurodegeneration:.2f}")
        info_line("─" * 70)
        info_line(f"{'Time':>6} {'Activity':>10} {'Trophic':>10} {'SynDen':>10} {'NeuroDeg':>10} {'OxStress':>10}")
        info_line(f"{'─'*6} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
        
        for i in range(n_steps):
            self.step()
            if i % 50 == 0:
                act = self.activities[-1] if self.activities else 0
                resp = self.responses[-1] if self.responses else {}
                print(f"{self.time:6.1f} {act:10.3f} "
                      f"{resp.get('trophic_output', 0):10.3f} "
                      f"{self.env.synaptic_density:10.3f} "
                      f"{self.env.neurodegeneration:10.3f} "
                      f"{self.env.oxidative_stress:10.3f}")
        
        self._summarize()
    
    def _summarize(self):
        info_line(f"\n{'='*70}")
        success_line(f"SIMULATION COMPLETE — {self.time:.0f} time units")
        info_line(f"{'='*70}")
        
        info_line(f"\nFinal state:")
        info_line(f"  Synaptic density:     {self.env.synaptic_density:.3f} "
f"({'IMPROVED' if self.env.synaptic_density > 0.5 else 'DECLINED'})")
        info_line(f"  Neurodegeneration:    {self.env.neurodegeneration:.3f} "
f"({'REDUCED' if self.env.neurodegeneration < 0.3 else 'PROGRESSED'})")
        info_line(f"  Oxidative stress:     {self.env.oxidative_stress:.3f}")
        info_line(f"  Inflammation:         {self.env.inflammation:.3f}")
        
        if self.bnf_active:
            outputs = [r['trophic_output'] for r in self.responses]
            info_line(f"\n  BNF feedback range:  {min(outputs):.3f} - {max(outputs):.3f}")
            info_line(f"  BNF mean output:     {np.mean(outputs):.3f}")
            info_line(f"\n  𐑾 Bidirectional feedback loop is {'ACTIVE' if max(outputs)-min(outputs) > 0.2 else 'WEAK'}")
            
            if self.env.neurodegeneration < 0.3 or self.env.synaptic_density > 0.6:
                success_line(f"\n  ✓ NEUROPROTECTION CONFIRMED")
                info_line(f"    The BNF dynamically adjusts trophic support to neural demand.")
            else:
                warning_line(f"\n  ⚠ PARTIAL PROTECTION — increase dose or potency")
        
        info_line(f"\n  Mechanism: 𐑾 bidirectional feedback between neurotransmitter")
        info_line(f"  sensing and trophic signaling creates closed-loop homeostasis.")
        
        results = {
            "simulation": f"Bidirectional Neurotrophic Factor ({self.disease})",
            "structural_type": "⟨𐑦𐑥𐑾𐑬𐑐𐑧𐑔𐑜⊙𐑖𐑙𐑷⟩",
            "bnf_active": self.bnf_active,
            "final_state": {
                "synaptic_density": float(self.env.synaptic_density),
                "neurodegeneration": float(self.env.neurodegeneration),
                "oxidative_stress": float(self.env.oxidative_stress),
                "inflammation": float(self.env.inflammation),
                "acetylcholine": float(self.env.acetylcholine)
            }
        }
        path = "/home/mrnob0dy666/red-hot_rebis/therapeutics/neurotrophic_results.json"
        with open(path, 'w') as f:
            json.dump(results, f, indent=2)
        info_line(f"\nSaved to {path}")


if __name__ == "__main__":
    info_line("=" * 70)
    info_line("ALZHEIMER'S DISEASE — BNF Active")
    info_line("=" * 70)
    sim = BNFSim(disease="alzheimer", bnf_active=True)
    sim.run(total_time=80.0)
    
    info_line("\n\n" + "=" * 70)
    info_line("ALZHEIMER'S DISEASE — Control (No BNF)")
    info_line("=" * 70)
    ctrl = BNFSim(disease="alzheimer", bnf_active=False)
    ctrl.run(total_time=80.0)
