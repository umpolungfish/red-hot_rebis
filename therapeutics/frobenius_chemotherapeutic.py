#!/usr/bin/env python3
"""
frobenius_chemotherapeutic.py — 𐑹-Frobenius-Coupled Selective Chemotherapeutic.

Structural type: ⟨𐑦·𐑶·𐑾·𐑹·𐑐·𐑧·𐑲·𐑝·⊙·𐑫·𐑳·𐑭⟩
Ouroboricity: O_∞ (child of the Rebis)
C-score: predicted 0.63 (Gate 1: ⊙ open, Gate 2: 𐑧 slow kinetics)

Core insight:
  Healthy cell-surface receptors have μ∘δ=id — binding is exactly invertible.
  Cancer cells have distorted receptor geometries (mutations, overexpression,
  clustering) that BREAK Frobenius symmetry — μ∘δ≠id.

  This dimeric drug has two binding domains. On healthy cells, both bind
  reversibly with Frobenius closure — no net tension on the tether. On
  cancer cells, binding asymmetry creates tether strain that exposes a
  masked cytotoxic payload. The drug ONLY activates where 𐑹 is broken.

  𐑹-protected (healthy): μ∘δ=id  →  tether relaxed  →  payload masked
  𐑹-broken (cancer):    μ∘δ≠id  →  tether stretched →  payload exposed
"""

import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple


class CancerReceptorModel:
    """
    Models receptor binding with Frobenius-checkable asymmetry.
    
    Healthy receptor: k_on ≈ 1.0, k_off ≈ 1.0 → k_on * k_off ≈ 1.0
      μ∘δ=id holds → binding is exactly invertible
    
    Cancer receptor: k_on inflated (clustering/overexpression) and/or
    k_off reduced (conformational trapping) → k_on * k_off ≠ 1.0
      μ∘δ≠id → Frobenius symmetry is broken
    """
    
    def __init__(self, receptor_type="healthy", mutation_strength=0.0):
        self.receptor_type = receptor_type
        
        if receptor_type == "healthy":
            # Frobenius-closed: k_on * k_off ≈ 1
            self.k_on = 1.0
            self.k_off = 1.0
            self.clustering = 0.0
        else:
            # Cancer: asymmetric kinetics
            # k_on increases with mutation (clustering, overexpression)
            self.k_on = 1.0 + mutation_strength * 5.0  # up to 6x
            # k_off decreases (conformational trapping)
            self.k_off = np.exp(-mutation_strength * 3.0)  # down to ~0.05x
            # Clustering amplifies avidity
            self.clustering = mutation_strength * 3.0
        
        # Normalized Frobenius asymmetry
        product = self.k_on * self.k_off
        self.asymmetry = min(1.0, abs(product - 1.0) / 2.0)
    
    def equilibrium_bound_fraction(self, drug_conc: float) -> float:
        """Equilibrium fraction of receptors bound."""
        effective_kd = self.k_off / (self.k_on * (1.0 + self.clustering))
        return drug_conc / (drug_conc + effective_kd)


@dataclass
class FrobeniusChemoState:
    target_type: str = "healthy"
    # Domain-level binding fractions (equilibrium)
    domain1_bound_frac: float = 0.0
    domain2_bound_frac: float = 0.0
    # Probability both domains simultaneously bind
    dual_binding_prob: float = 0.0
    # Tether tension from asymmetry
    tether_tension: float = 0.0
    # Payload exposure
    payload_exposed: float = 0.0
    # Cumulative cytotoxicity delivered
    cytotoxicity: float = 0.0
    # Frobenius error at each site
    site1_frob_error: float = 0.0
    site2_frob_error: float = 0.0
    # Receptor asymmetry (from model)
    asymmetry: float = 0.0


class FrobeniusChemoSim:
    """Equilibrium-based simulation of the Frobenius-coupled chemotherapeutic."""
    
    def __init__(self, dt: float = 0.5, drug_conc: float = 2.0):
        self.dt = dt
        self.drug_conc = drug_conc
        self.time = 0.0
        
        # Healthy cell
        self.healthy_rec = CancerReceptorModel("healthy", 0.0)
        self.healthy = FrobeniusChemoState(target_type="healthy",
                                           asymmetry=self.healthy_rec.asymmetry)
        
        # Cancer cells at various mutation strengths
        self.cancer: List[Tuple[CancerReceptorModel, FrobeniusChemoState]] = []
        for strength in [0.2, 0.4, 0.6, 0.8, 1.0]:
            rec = CancerReceptorModel("cancer", strength)
            st = FrobeniusChemoState(target_type=f"cancer_m{strength:.1f}",
                                     asymmetry=rec.asymmetry)
            self.cancer.append((rec, st))
        
        # History
        self.history = {}
    
    def _compute_binding(self, rec: CancerReceptorModel, st: FrobeniusChemoState):
        """Compute equilibrium binding and dual-occupancy probability."""
        # Domain-level binding (each domain binds independently)
        bound_frac = rec.equilibrium_bound_fraction(self.drug_conc)
        st.domain1_bound_frac = bound_frac
        st.domain2_bound_frac = bound_frac * 0.9  # slight steric hindrance
        
        # Probability both domains are simultaneously bound
        st.dual_binding_prob = st.domain1_bound_frac * st.domain2_bound_frac
        
        # Frobenius error at each site
        st.site1_frob_error = rec.asymmetry
        st.site2_frob_error = rec.asymmetry * 0.95  # slight site variation
    
    def _compute_tether_tension(self, rec: CancerReceptorModel, st: FrobeniusChemoState):
        """
        Tether tension is proportional to:
        1. Dual-binding probability (both domains must be engaged)
        2. Frobenius asymmetry (how broken is μ∘δ=id at each site)
        3. Time the system has been in the asymmetric state
        """
        if st.dual_binding_prob < 0.05:
            st.tether_tension = 0.0
            return
        
        # Tension arises from asymmetry × dual engagement
        asymmetry_force = rec.asymmetry * st.dual_binding_prob
        # Sigmoid response: below threshold = relaxed, above = stretched
        tension = 1.0 / (1.0 + np.exp(-10.0 * (asymmetry_force - 0.15)))
        st.tether_tension = tension
    
    def _expose_payload(self, st: FrobeniusChemoState):
        """
        Payload exposure dynamics.
        Tension > 0.5 exposes payload; tension < 0.3 allows re-masking.
        This creates hysteresis — once exposed, payload tends to stay exposed.
        """
        if st.tether_tension > 0.5:
            # Expose — fast
            st.payload_exposed = min(1.0, st.payload_exposed + self.dt * 0.3)
        elif st.tether_tension < 0.3:
            # Re-mask — slow
            st.payload_exposed = max(0.0, st.payload_exposed - self.dt * 0.02)
        # Between 0.3-0.5: maintain current state (hysteresis)
    
    def _deliver(self, st: FrobeniusChemoState):
        """Cytotoxicity delivery."""
        release = st.payload_exposed * self.dt * 0.5
        st.cytotoxicity += release
    
    def step(self, rec: CancerReceptorModel, st: FrobeniusChemoState):
        self._compute_binding(rec, st)
        self._compute_tether_tension(rec, st)
        self._expose_payload(st)
        self._deliver(st)
    
    def run(self, total_time: float = 30.0):
        n_steps = int(total_time / self.dt)
        
        print("=" * 70)
        print("FROBENIUS-COUPLED CHEMOTHERAPEUTIC — Equilibrium Model")
        print("=" * 70)
        print(f"Drug concentration: {self.drug_conc} (normalized)")
        print(f"Principle: 𐑹 symmetry protects healthy cells; 𐑹-breaking exposes cancer")
        print("─" * 70)
        
        for i in range(n_steps):
            self.time = i * self.dt
            
            # Step healthy
            self.step(self.healthy_rec, self.healthy)
            
            # Step cancer
            for rec, st in self.cancer:
                self.step(rec, st)
            
            # Report
            if i % 20 == 0:
                h_pay = self.healthy.payload_exposed
                c_payloads = [st.payload_exposed for _, st in self.cancer]
                c_tensions = [st.tether_tension for _, st in self.cancer]
                print(f"  t={self.time:5.1f} | "
                      f"H: {h_pay:.3f} | "
                      f"C: {[f'{p:.3f}' for p in c_payloads]} | "
                      f"T: {[f'{t:.2f}' for t in c_tensions]}")
        
        self._summarize(n_steps)
    
    def _summarize(self, n_steps):
        print(f"\n{'='*70}")
        print(f"SIMULATION COMPLETE — {n_steps} steps over {self.time:.1f} time units")
        print(f"{'='*70}")
        
        h_cyt = self.healthy.cytotoxicity
        print(f"\nHealthy Cell (Frobenius-protected):")
        print(f"  Asymmetry: {self.healthy.asymmetry:.4f}")
        print(f"  Binding: {self.healthy.domain1_bound_frac:.3f}")
        print(f"  Dual binding: {self.healthy.dual_binding_prob:.3f}")
        print(f"  Tether tension: {self.healthy.tether_tension:.4f}")
        print(f"  Payload exposed: {self.healthy.payload_exposed:.4f}")
        print(f"  Cytotoxicity: {h_cyt:.4f}")
        print(f"  𐑹 Protection: {'ACTIVE ✓' if h_cyt < 0.5 else 'COMPROMISED'}")
        
        print(f"\nCancer Cells:")
        healthy_cyt = max(h_cyt, 0.001)  # avoid div by zero
        for rec, st in self.cancer:
            ratio = st.cytotoxicity / healthy_cyt
            print(f"  {st.target_type}:")
            print(f"    Asymmetry: {st.asymmetry:.4f} | Binding: {st.domain1_bound_frac:.3f}")
            print(f"    Tether: {st.tether_tension:.4f} | Payload: {st.payload_exposed:.4f}")
            print(f"    Cytotoxicity: {st.cytotoxicity:.4f} | Selectivity vs healthy: {ratio:.1f}x")
        
        print(f"\n{'─'*70}")
        print(f"The 𐑹-Frobenius gate selectively activates therapeutics in")
        print(f"asymmetric (cancer) microenvironments while healthy tissue")
        print(f"with μ∘δ=id symmetry experiences minimal payload exposure.")
        
        # Save results
        results = {
            "simulation": "Frobenius-Coupled Chemotherapeutic",
            "principle": "Selective cytotoxicity via Frobenius-check of μ∘δ=id",
            "structural_type": "⟨𐑦·𐑶·𐑾·𐑹·𐑐·𐑧·𐑲·𐑝·⊙·𐑫·𐑳·𐑭⟩",
            "drug_conc": self.drug_conc,
            "healthy": {"cytotoxicity": h_cyt, "payload": self.healthy.payload_exposed},
            "cancer": {
                st.target_type: {
                    "asymmetry": rec.asymmetry,
                    "tether_tension": st.tether_tension,
                    "payload": st.payload_exposed,
                    "cytotoxicity": st.cytotoxicity,
                    "selectivity_vs_healthy": float(st.cytotoxicity / healthy_cyt)
                }
                for rec, st in self.cancer
            }
        }
        path = "/home/mrnob0dy666/red-hot_rebis/therapeutics/frobenius_chemo_results.json"
        with open(path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {path}")


if __name__ == "__main__":
    sim = FrobeniusChemoSim(dt=0.5, drug_conc=2.0)
    sim.run(total_time=30.0)
