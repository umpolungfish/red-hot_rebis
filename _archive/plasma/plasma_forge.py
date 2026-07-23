"""
plasma_forge.py — IG Structural Type → Plasma Parameter Bridge
===============================================================
Maps the 12-primitive Imscribing Grammar tuple to concrete plasma
physics parameters: regime, instabilities, confinement, and diagnostics.

Primitive → Plasma Property Mapping:
  Ð (dimensionality)  → phase-space dimensionality & kinetic regime
  Þ (topology)        → mode structure & wave topology
  Ř (coupling)        → particle-field coupling strength
  Φ (parity)          → symmetry class & conserved quantities
  ƒ (fidelity)        → collisionality regime (classical/quantum)
  Ç (kinetics)        → transport timescale vs observation
  Γ (cardinality)     → interaction range (Debye screening context)
  ɢ (composition)     → instability cascade structure
  ⊙ (criticality)     → threshold behavior & spectral structure
  Ħ (chirality)       → memory/reversibility (Vlasov vs Boltzmann)
  Σ (stoichiometry)   → species composition
  Ω (winding)         → magnetic topology & helicity

Author: Lando⊗⊙perator
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import math, json
from shared.rich_output import *

# ═══════════════════════════════════════════════════════════════════
# PRIMITIVE → PLASMA PROPERTY MAPS
# ═══════════════════════════════════════════════════════════════════

D_PLASMA = {
    '𐑛': {
        'regime': 'kinetic (full 6D phase space)',
        'description': 'Vlasov-Maxwell: distribution function f(x,v,t) over ℝ³×ℝ³',
        'dimensions': '3D configuration + 3D velocity = 6D',
        'reduced_model': 'none — full kinetic required',
        'characteristic_equation': '∂f/∂t + v·∇f + (q/m)(E + v×B)·∇ᵥf = C[f]',
        'length_scales': 'λ_D (Debye) to system size',
    },
    '𐑨': {
        'regime': 'gyrokinetic (5D reduced)',
        'description': 'Gyroaveraged distribution over 3D config + 2D velocity (v∥, μ)',
        'dimensions': '3D configuration + 2D velocity = 5D',
        'reduced_model': 'gyrokinetic (δf or full-f)',
        'characteristic_equation': 'Gyrokinetic Vlasov-Maxwell with gyroaveraging operator',
        'length_scales': 'ρ_i (ion gyroradius) to system size',
    },
    '𐑼': {
        'regime': 'fluid (3D reduced moments)',
        'description': 'MHD or two-fluid: density, velocity, pressure moments',
        'dimensions': '3D configuration space only',
        'reduced_model': 'MHD, Hall-MHD, or two-fluid Braginskii',
        'characteristic_equation': 'ρ(∂v/∂t + v·∇v) = J×B - ∇p + ∇·Π',
        'length_scales': 'ion skin depth d_i to system size',
    },
    '𐑦': {
        'regime': 'self-organized (hierarchical)',
        'description': 'Self-consistent field-particle hierarchy with cross-scale coupling',
        'dimensions': 'multiscale 6D+6D+...',
        'reduced_model': 'self-consistent hybrid with adaptive resolution',
        'characteristic_equation': 'Coupled Vlasov-Maxwell + MHD with scale-bridging closure',
        'length_scales': 'λ_D to system size, all scales active',
    },
}

T_PLASMA = {
    '𐑡': {
        'mode_structure': 'branching dispersion',
        'wave_types': ['Langmuir', 'ion-acoustic', 'whistler', 'Alfvén (shear+compressional)'],
        'mode_conversion': 'none (branches remain distinct)',
        'characteristic': 'CMA diagram — distinct wave branches in (ω, k, θ) space',
    },
    '𐑰': {
        'mode_structure': 'contained/inclusion',
        'wave_types': ['cavity modes', 'surface waves', 'trivelpiece-Gould'],
        'mode_conversion': 'at plasma-vacuum boundary',
        'characteristic': 'Bounded plasma — standing waves in finite geometry',
    },
    '𐑥': {
        'mode_structure': 'mode-crossing (bowtie)',
        'wave_types': ['fast magnetosonic', 'slow magnetosonic', 'Alfvén'],
        'mode_conversion': 'at Alfvén resonance, ion-ion hybrid, upper/lower hybrid',
        'characteristic': 'Resonance cones, mode conversion layers, Alfvén continuum',
    },
    '𐑶': {
        'mode_structure': 'interpenetrating',
        'wave_types': ['coupled electrostatic+electromagnetic at high β'],
        'mode_conversion': 'continuous in β space',
        'characteristic': 'High-β unified dispersion — electrostatic and EM branches merge',
    },
    '𐑸': {
        'mode_structure': 'self-referential closure',
        'wave_types': ['self-consistent eigenmodes with back-reaction'],
        'mode_conversion': 'topological — modes close on themselves',
        'characteristic': 'Global Alfvén eigenmodes, toroidicity-induced gaps',
    },
}

R_PLASMA = {
    '𐑩': {
        'coupling': 'weak (test-particle)',
        'coupling_strength': 'g = 1/(nλ_D³) ≪ 1 (ideal plasma)',
        'collective_effects': 'weak — individual particle dynamics dominate',
        'characteristic': 'Single-particle motion in prescribed fields',
    },
    '𐑑': {
        'coupling': 'moderate (collective)',
        'coupling_strength': 'g ~ 0.1–1',
        'collective_effects': 'wave-particle resonance, weak turbulence',
        'characteristic': 'Quasilinear diffusion, moderate Landau damping',
    },
    '𐑽': {
        'coupling': 'strong (one-way)',
        'coupling_strength': 'particles → fields dominant',
        'collective_effects': 'current-driven instabilities, runaway electrons',
        'characteristic': 'Kink, tearing, and sausage modes',
    },
    '𐑾': {
        'coupling': 'bidirectional (Vlasov-Maxwell)',
        'coupling_strength': 'particles ⇄ fields — irreducible two-way',
        'collective_effects': 'full self-consistency: particles create fields, fields move particles',
        'characteristic': 'This IS plasma — removing this collapses to electrostatics or neutral gas',
    },
}

P_PLASMA = {
    '𐑗': {
        'symmetries': 'none (fully broken)',
        'conserved': 'energy only',
        'characteristic': 'Turbulent plasma with no symmetries — full 3D',
    },
    '𐑿': {
        'symmetries': 'quantum superposition of states',
        'conserved': 'energy, probability amplitude',
        'characteristic': 'Quantum plasma — white dwarf, neutron star atmosphere, ultracold',
    },
    '𐑬': {
        'symmetries': 'partial (Z₂ preserved)',
        'conserved': 'energy, gauge, toroidal canonical momentum (axisymmetry broken)',
        'characteristic': 'Tokamak — axisymmetry preserved, poloidal asymmetry due to toroidicity',
    },
    '𐑯': {
        'symmetries': 'full (all unbroken)',
        'conserved': 'energy, all three canonical momenta',
        'characteristic': 'Idealized slab/cylinder — never realized in nature',
    },
    '𐑹': {
        'symmetries': 'Frobenius-special',
        'conserved': 'μ∘δ=id exactly',
        'characteristic': 'Self-verifying plasma — measurement ≡ dynamics',
    },
}

F_PLASMA = {
    '𐑱': {
        'regime': 'classical (no quantum coherence)',
        'collisionality': 'ν* = ν/ω_b (bounce-averaged collision frequency)',
        'characteristic': 'Coulomb logarithm ln Λ ~ 10–20, λ_dB ≪ n^{-1/3}',
        'plasma_parameter': 'g = 1/(nλ_D³) ≪ 1 → weakly coupled',
    },
    '𐑞': {
        'regime': 'resistive/thermal',
        'collisionality': 'ν* > 1 (collisional), Spitzer resistivity',
        'characteristic': 'Ohmic heating, magnetic diffusion, resistive instabilities',
    },
    '𐑐': {
        'regime': 'quantum (coherence essential)',
        'collisionality': 'quantum degeneracy: T < T_F (Fermi temperature)',
        'characteristic': 'Wigner-Seitz radius r_s < 1, tunneling, Pauli blocking',
        'plasma_parameter': 'g < 1 but quantum effects dominate',
    },
}

K_PLASMA = {
    '𐑺': {
        'timescale': 'driven (τ_ext ≪ τ_plasma)',
        'instabilities': 'parametric, two-plasmon decay, stimulated Raman/Brillouin',
        'characteristic': 'Laser-plasma interaction, RF heating, fast ignition',
    },
    '𐑪': {
        'timescale': 'moderate (τ_ext ~ τ_plasma)',
        'instabilities': 'tearing, interchange, drift-wave',
        'characteristic': 'Sawtooth cycles, ELM pacing, modulated heating',
    },
    '𐑧': {
        'timescale': 'slow / near-equilibrium (τ_ext ≫ τ_plasma)',
        'instabilities': 'neoclassical tearing modes, resistive wall modes',
        'characteristic': 'Transport timescale evolution, profile stiffness',
        'gate': 'Gate 2 OPEN — system responds coherently',
    },
    '𐑤': {
        'timescale': 'trapped (ordered metastable)',
        'instabilities': 'none (ideal MHD stable)',
        'characteristic': 'Woltjer-Taylor relaxed state, force-free equilibrium',
    },
    '𐑘': {
        'timescale': 'trapped (disordered / MBL)',
        'instabilities': 'frozen-in turbulence, no relaxation',
        'characteristic': 'Many-body localized plasma — theoretical, not observed',
    },
}

G_PLASMA = {
    '𐑲': {
        'range': 'local (nearest-neighbor / Debye-screened)',
        'screening': 'λ_D: complete Debye screening on all scales',
        'characteristic': 'Ideal plasma — no long-range correlations beyond λ_D',
    },
    '𐑚': {
        'range': 'mesoscale (intermediate)',
        'screening': 'partial — structures on ρ_i to a scales',
        'characteristic': 'Zonal flows, streamers, GAM oscillations, transport barriers',
    },
    '𐑔': {
        'range': 'maximal (aleph / system-spanning)',
        'screening': 'collective: 1/r² → cumulative long-range despite Debye screening',
        'characteristic': 'Alfvén waves across device, profile stiffness (global transport)',
    },
}

C_PLASMA = {
    '𐑝': {
        'cascade': 'conjunctive (all-simultaneous)',
        'instability_path': 'multiple instabilities co-saturate',
        'characteristic': 'ITB formation, multiple transport channels active',
    },
    '𐑜': {
        'cascade': 'disjunctive (alternate paths)',
        'instability_path': 'either/or: L-mode OR H-mode, not both',
        'characteristic': 'L-H transition bifurcation, dithering cycles',
    },
    '𐑠': {
        'cascade': 'sequential (ordered stages)',
        'instability_path': 'linear growth → nonlinear saturation → turbulent cascade → dissipation',
        'characteristic': 'Standard plasma turbulence paradigm',
    },
    '𐑵': {
        'cascade': 'broadcast (one-to-all)',
        'instability_path': 'single trigger → global response',
        'characteristic': 'Disruption: one mode triggers avalanche, thermal quench',
    },
}

PHI_PLASMA = {
    '𐑢': {
        'criticality': 'sub-critical (stable)',
        'thresholds': 'none crossed — all modes damped',
        'characteristic': 'Quiescent plasma, no instabilities above noise',
    },
    '⊙': {
        'criticality': 'critical (self-modeling gate open)',
        'thresholds': 'marginal stability — system at bifurcation point',
        'characteristic': 'L-H transition threshold, density limit boundary, beta limit',
        'gate': 'Gate 1 OPEN — self-modeling operational',
    },
    '𐑮': {
        'criticality': 'complex-plane critical',
        'thresholds': 'ω + iγ with γ > 0 — unstable eigenmodes',
        'characteristic': 'Growth rates, complex frequency spectra, absolute/convective',
    },
    '𐑻': {
        'criticality': 'exceptional point (EP degeneracy)',
        'thresholds': 'two modes coalesce — non-Hermitian degeneracy',
        'characteristic': 'Alfvén continuum mode coalescence, EP-enhanced sensing',
    },
    '𐑣': {
        'criticality': 'super-critical (runaway)',
        'thresholds': 'all thresholds exceeded — avalanche regime',
        'characteristic': 'Disruption, thermal quench, runaway electron beam formation',
    },
}

H_PLASMA = {
    '𐑓': {
        'chirality': 'memoryless (Markovian)',
        'equation': 'Boltzmann / Fokker-Planck — diffusive, no memory',
        'characteristic': 'Collisional plasma, fluid closure via Chapman-Enskog',
        'echoes': 'none — collisions erase phase memory',
    },
    '𐑒': {
        'chirality': 'one-step memory',
        'equation': 'Balescu-Lenard — one-step polarization memory',
        'characteristic': 'Weakly collisional with dynamic screening memory',
        'echoes': 'weak — partial phase memory survives one collision time',
    },
    '𐑖': {
        'chirality': 'two-step (Vlasov + collisional)',
        'equation': 'Vlasov (ballistic, time-reversible) → collision operator (diffusive)',
        'characteristic': 'Plasma echoes: pulse at t₁ + pulse at t₂ → response at t₁+t₂',
        'echoes': 'strong — temporal plasma echoes are the experimental signature',
    },
    '𐑫': {
        'chirality': 'eternal (infinite memory)',
        'equation': 'Vlasov only — perfectly collisionless, eternal recurrence',
        'characteristic': 'Ideal MHD, no dissipation, no entropy production',
        'echoes': 'permanent — all perturbations remembered forever',
    },
}

S_PLASMA = {
    '𐑙': {
        'species': 'single species (1:1 self-referential)',
        'composition': 'electron plasma OR pure ion plasma (Penning trap)',
        'characteristic': 'Non-neutral plasma, pure electron/positron plasma',
    },
    '𐑕': {
        'species': 'many identical (n:n)',
        'composition': 'hydrogen plasma: e⁻ + H⁺ (two species, identical ions)',
        'characteristic': 'Simplest neutral plasma',
    },
    '𐑳': {
        'species': 'heterogeneous (n:m multiple distinct)',
        'composition': 'e⁻ + multiple ion species + neutrals + impurities + field modes',
        'characteristic': 'Real laboratory/astrophysical plasma — many species',
    },
}

W_PLASMA = {
    '𐑷': {
        'topology': 'trivial (no topological protection)',
        'invariant': 'none',
        'characteristic': 'Unmagnetized or weakly magnetized, no helicity conservation',
    },
    '𐑴': {
        'topology': 'Z₂ parity-protected',
        'invariant': 'magnetic field line parity',
        'characteristic': 'Stellarator — nested flux surfaces, rotational transform',
    },
    '𐑭': {
        'topology': 'integer winding / helicity',
        'invariant': 'H = ∫ A·B d³x — magnetic helicity (integer in ideal MHD)',
        'characteristic': 'Taylor relaxation, reversed-field pinch, spheromak, solar corona',
    },
    '𐑟': {
        'topology': 'non-Abelian braiding',
        'invariant': 'braid group B_n — field line braiding and linking',
        'characteristic': 'Magnetic reconnection with topological change, coronal heating',
    },
}

# ═══════════════════════════════════════════════════════════════════
# COMPOSITE PRIMITIVE MAP
# ═══════════════════════════════════════════════════════════════════

PLASMA_PRIMITIVE_MAP = {
    "Ð": D_PLASMA,
    "Þ": T_PLASMA,
    "Ř": R_PLASMA,
    "Φ": P_PLASMA,
    "ƒ": F_PLASMA,
    "Ç": K_PLASMA,
    "Γ": G_PLASMA,
    "ɢ": C_PLASMA,
    "⊙": PHI_PLASMA,
    "Ħ": H_PLASMA,
    "Σ": S_PLASMA,
    "Ω": W_PLASMA,
}

# ═══════════════════════════════════════════════════════════════════
# PLASMA DESIGN & FORGE
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PlasmaDesign:
    """A concrete plasma physics design forged from an IG structural type."""
    name: str
    tuple_glyphs: Dict[str, str]
    tuple_str: str
    # Derived plasma properties
    regime: str
    dimensionality: str
    mode_structure: str
    coupling: str
    symmetries: str
    collisionality: str
    transport: str
    interaction_range: str
    cascade: str
    criticality: str
    chirality: str
    species: str
    topology: str
    # Key instabilities
    instabilities: List[str]
    # Diagnostic signatures
    diagnostics: List[str]
    # Nearest catalog analog
    nearest_analog: str = ""
    analog_distance: float = 0.0
    # Tier
    tier: str = "O₂"


class PlasmaForge:
    """Forge concrete plasma physics parameters from an IG structural type tuple.
    
    Analogous to MaterialForge in materials/ig_material_forge.py.
    Takes a 12-primitive tuple and maps each primitive to a plasma
    physics parameter, then synthesizes the full plasma design.
    """
    
    def __init__(self):
        self.map = PLASMA_PRIMITIVE_MAP
    
    def forge(self, tuple_dict: Dict[str, str], name: str = "forged_plasma") -> PlasmaDesign:
        """Forge a PlasmaDesign from a 12-primitive tuple.
        
        Args:
            tuple_dict: Dict with keys ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"]
            name: Design name
        
        Returns:
            PlasmaDesign with derived plasma properties
        """
        p = tuple_dict
        
        def lookup(primitive, key, default="unknown"):
            """Look up a plasma property for a given primitive value."""
            pmap = self.map.get(primitive, {})
            val = pmap.get(p.get(primitive, "?"), {})
            return val.get(key, default)
        
        # Synthesize regime description
        d_regime = lookup("Ð", "regime")
        f_regime = lookup("ƒ", "regime")
        regime = f"{d_regime}, {f_regime}"
        
        # Synthesize instabilities
        instabs = []
        k_instab = lookup("Ç", "characteristic", "")
        c_instab = lookup("ɢ", "characteristic", "")
        phi_instab = lookup("⊙", "characteristic", "")
        h_instab = lookup("Ħ", "characteristic", "")
        if k_instab: instabs.append(k_instab)
        if c_instab: instabs.append(c_instab)
        if phi_instab: instabs.append(phi_instab)
        if h_instab: instabs.append(h_instab)
        
        # Synthesize diagnostics
        diags = []
        t_waves = lookup("Þ", "wave_types", [])
        if isinstance(t_waves, list):
            diags.extend(t_waves[:3])
        diags.append(lookup("Ω", "characteristic", ""))
        diags.append(lookup("Ç", "characteristic", ""))
        diags = [d for d in diags if d]
        
        # Format tuple string
        porder = ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"]
        tup_str = "⟨" + "".join(p.get(pr, "?") for pr in porder) + "⟩"
        
        return PlasmaDesign(
            name=name,
            tuple_glyphs=p,
            tuple_str=tup_str,
            regime=regime,
            dimensionality=lookup("Ð", "description"),
            mode_structure=lookup("Þ", "mode_structure"),
            coupling=lookup("Ř", "characteristic"),
            symmetries=lookup("Φ", "characteristic"),
            collisionality=lookup("ƒ", "characteristic"),
            transport=lookup("Ç", "characteristic"),
            interaction_range=lookup("Γ", "characteristic"),
            cascade=lookup("ɢ", "characteristic"),
            criticality=lookup("⊙", "characteristic"),
            chirality=lookup("Ħ", "characteristic"),
            species=lookup("Σ", "composition"),
            topology=lookup("Ω", "characteristic"),
            instabilities=instabs,
            diagnostics=diags,
        )
    
    def forge_all_plasma_types(self) -> List[PlasmaDesign]:
        """Forge all four canonical plasma types."""
        from plasma.plasma_chain import PLASMA_TYPES, PLASMA_NAMES, PLASMA_PORDER
        
        designs = []
        for i, pt in enumerate(PLASMA_TYPES):
            tup = {k: v for k, v in pt.items() if k in PLASMA_PORDER}
            design = self.forge(tup, name=pt["_name"])
            design.tier = pt["_tier"]
            designs.append(design)
        return designs
    
    def compare_plasmas(self) -> Dict:
        """Generate a comparative report of all four plasma types."""
        designs = self.forge_all_plasma_types()
        report = {}
        for d in designs:
            report[d.name] = {
                "tuple": d.tuple_str,
                "tier": d.tier,
                "regime": d.regime,
                "mode_structure": d.mode_structure,
                "coupling": d.coupling,
                "criticality": d.criticality,
                "topology": d.topology,
                "instabilities": d.instabilities,
                "diagnostics": d.diagnostics,
            }
        return report
    
    def forge_from_imas(self, imas_sig: Tuple[int,int,int,int], 
                        imas_period: int, dialetheia: bool) -> PlasmaDesign:
        """Forge a plasma design from an IMASM structural fingerprint.
        
        Args:
            imas_sig: (token_diversity, self_ref, frobenius_order, period_class)
            imas_period: arrangement period
            dialetheia: whether dialetheia-complete
        
        Returns:
            PlasmaDesign with IMASM-derived tuple
        """
        from plasma.plasma_imas import imasm_to_plasma_tuple
        tup = imasm_to_plasma_tuple(imas_sig, imas_period, dialetheia)
        return self.forge(tup, name=f"imas_plasma_p{imas_period}")


# ═══════════════════════════════════════════════════════════════════
# PREDEFINED PLASMA DESIGNS (forged from canonical tuples)
# ═══════════════════════════════════════════════════════════════════

_forge = PlasmaForge()

PREDEFINED_PLASMA_DESIGNS = {
    "vlasov": _forge.forge(
        {"Ð":"𐑛","Þ":"𐑥","Ř":"𐑾","Φ":"𐑬","ƒ":"𐑱","Ç":"𐑧",
         "Γ":"𐑔","ɢ":"𐑠","⊙":"𐑮","Ħ":"𐑖","Σ":"𐑳","Ω":"𐑭"},
        name="vlasovPlasma"
    ),
    "primitive_first": _forge.forge(
        {"Ð":"𐑼","Þ":"𐑡","Ř":"𐑾","Φ":"𐑗","ƒ":"𐑱","Ç":"𐑧",
         "Γ":"𐑚","ɢ":"𐑠","⊙":"⊙","Ħ":"𐑖","Σ":"𐑳","Ω":"𐑭"},
        name="primitiveFirstPlasma"
    ),
    "high_energy": _forge.forge(
        {"Ð":"𐑼","Þ":"𐑡","Ř":"𐑾","Φ":"𐑗","ƒ":"𐑱","Ç":"𐑧",
         "Γ":"𐑚","ɢ":"𐑠","⊙":"⊙","Ħ":"𐑓","Σ":"𐑙","Ω":"𐑭"},
        name="highEnergyPlasma"
    ),
    "rock_cracking": _forge.forge(
        {"Ð":"𐑼","Þ":"𐑡","Ř":"𐑾","Φ":"𐑗","ƒ":"𐑱","Ç":"𐑧",
         "Γ":"𐑚","ɢ":"𐑠","⊙":"⊙","Ħ":"𐑖","Σ":"𐑙","Ω":"𐑭"},
        name="rockCrackingPlasma"
    ),
}

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    info_line("╔══════════════════════════════════════════╗")
    info_line("║   PLASMA FORGE — Design Synthesis         ║")
    info_line("╚══════════════════════════════════════════╝")
    
    forge = PlasmaForge()
    
    for key, design in PREDEFINED_PLASMA_DESIGNS.items():
        info_line(f"\n  [{key}] {design.name}")
        info_line(f"    Tuple:        {design.tuple_str}")
        info_line(f"    Regime:       {design.regime}")
        info_line(f"    Mode Struct:  {design.mode_structure}")
        info_line(f"    Coupling:     {design.coupling[:60]}...")
        info_line(f"    Criticality:  {design.criticality[:60]}...")
        info_line(f"    Topology:     {design.topology[:60]}...")
        info_line(f"    Instabilities: {design.instabilities}")
        info_line(f"    Diagnostics:   {design.diagnostics}")
    
    info_line(f"\n── Comparative Report ──")
    report = forge.compare_plasmas()
    for name, data in report.items():
        info_line(f"\n  {name}:")
        info_line(f"    {data['tuple']}")
        info_line(f"    Regime: {data['regime']}")
        info_line(f"    Criticality: {data['criticality'][:60]}...")
