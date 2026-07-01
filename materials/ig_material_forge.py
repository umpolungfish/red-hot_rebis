#!/usr/bin/env python3
"""
ig_material_forge.py — IG Structural Type → Concrete Material Design Bridge
============================================================================

Maps the 12-primitive Imscribing Grammar tuple to physical material properties:
composition, structure, processing, and predicted behaviors. Each primitive
family constrains a specific material design axis.

Primitive → Material Property Mapping:
  D (dimensionality)  → structural dimensionality (0D dots, 1D wires, 2D films, bulk)
  T (topology)        → connectivity type (network, core-shell, bowtie, interpenetrating)
  R (coupling)         → interface coupling (weak vdW, covalent, ionic, dynamic bond)
  P (parity)           → symmetry class (amorphous, polycrystalline, ordered, Frobenius)
  F (fidelity)         → phase purity (defect-tolerant, thermal, quantum-coherent)
  K (kinetics)         → processing kinetics (quenched, annealed, equilibrated, trapped)
  G (cardinality)      → interaction range (short-range bond, mesoscale, long-range order)
  C (composition)      → synthesis sequence (one-pot, combinatorial, sequential, templated)
  Phi (criticality)    → critical behavior (inert, self-sensing, tunable, EP, runaway)
  H (chirality)        → memory/history (memoryless, one-step, two-step, eternal)
  S (stoichiometry)    → component count (unary, binary, multi-component)
  Omega (winding)      → topological protection (none, Z2, integer winding, non-Abelian)

This is the materials analog of clink_bridge.py — bridging the structural type
crystal to the periodic table and processing space.

Author: Lando⊗⊙perator
"""

from typing import Dict, List, Tuple, Optional
import json, math
from dataclasses import dataclass, field
from shared.rich_output import *

# ═══════════════════════════════════════════════════════════════════
# PRIMITIVE → MATERIAL PROPERTY MAPS
# ═══════════════════════════════════════════════════════════════════

D_MATERIAL = {
    '𐑛': {'dimensionality': '0D', 'structure': 'nanoparticle / quantum dot',
           'size_regime': '1-100 nm', 'synthesis': 'colloidal precipitation'},
    '𐑨': {'dimensionality': '2D', 'structure': 'thin film / membrane',
           'size_regime': 'monolayer to μm', 'synthesis': 'CVD / ALD / Langmuir-Blodgett'},
    '𐑼': {'dimensionality': '3D bulk', 'structure': 'bulk solid / composite',
           'size_regime': 'macro', 'synthesis': 'powder metallurgy / casting'},
    '𐑦': {'dimensionality': 'hierarchical', 'structure': 'self-similar metamaterial',
           'size_regime': 'nm to cm', 'synthesis': 'additive + self-assembly'},
}

T_MATERIAL = {
    '𐑡': {'connectivity': 'network', 'structure': 'percolating network / aerogel',
           'mechanical': 'high porosity, low density'},
    '𐑰': {'connectivity': 'core-shell', 'structure': 'coated / encapsulated',
           'mechanical': 'graded interface, stress-buffered'},
    '𐑥': {'connectivity': 'bowtie/crossing', 'structure': 'interpenetrating / woven',
           'mechanical': 'auxetic possible, high toughness'},
    '𐑶': {'connectivity': 'interpenetrating', 'structure': 'IPN / MOF@COF',
           'mechanical': 'synergistic, strain-sharing'},
    '𐑸': {'connectivity': 'self-referential', 'structure': 'self-similar fractal',
           'mechanical': 'scale-invariant, self-healing capable'},
}

R_MATERIAL = {
    '𐑩': {'interface': 'weak (van der Waals)', 'bond_energy': '< 50 kJ/mol',
           'reversible': True, 'fatigue': 'low cycles'},
    '𐑑': {'interface': 'moderate (H-bond, π-π)', 'bond_energy': '50-150 kJ/mol',
           'reversible': 'partially', 'fatigue': 'moderate'},
    '𐑽': {'interface': 'strong (covalent, ionic)', 'bond_energy': '150-800 kJ/mol',
           'reversible': False, 'fatigue': 'high cycles'},
    '𐑾': {'interface': 'dynamic (Diels-Alder, disulfide)', 'bond_energy': '100-300 kJ/mol',
           'reversible': True, 'fatigue': 'self-healing'},
}

P_MATERIAL = {
    '𐑗': {'symmetry': 'amorphous / disordered', 'order_parameter': 0.0,
           'properties': 'isotropic, broad distributions'},
    '𐑿': {'symmetry': 'quantum superposition', 'order_parameter': 'complex',
           'properties': 'coherence-enabled, entangled'},
    '𐑬': {'symmetry': 'partially ordered (Z₂)', 'order_parameter': '< 1.0',
           'properties': 'nematic, ferroelectric domains'},
    '𐑯': {'symmetry': 'fully symmetric', 'order_parameter': 1.0,
           'properties': 'single crystal, anisotropic'},
    '𐑹': {'symmetry': 'Frobenius-closed', 'order_parameter': 'μ∘δ=id',
           'properties': 'self-verifying, closed-loop healing'},
}

F_MATERIAL = {
    '𐑱': {'phase': 'classical / defect-tolerant', 'purity': '90-99%',
           'character': 'polycrystalline, grain boundaries present'},
    '𐑞': {'phase': 'thermal / noisy', 'purity': '99-99.9%',
           'character': 'annealed, reduced defects'},
    '𐑐': {'phase': 'quantum-coherent', 'purity': '99.9999%+',
           'character': 'single crystal, ultrahigh vacuum processed'},
}
K_MATERIAL = {
    '𐑘': {'kinetics': 'driven / far-from-equilibrium', 'processing': 'quench / rapid solidification',
           'microstructure': 'fine-grained, metastable phases'},
    '𐑤': {'kinetics': 'moderate', 'processing': 'controlled cooling',
           'microstructure': 'medium grain size, equilibrium phases'},
    '𐑧': {'kinetics': 'near-equilibrium', 'processing': 'slow anneal / float zone',
           'microstructure': 'coarse, highly ordered'},
    '𐑪': {'kinetics': 'trapped (ordered)', 'processing': 'field-assisted / epitaxial',
           'microstructure': 'single domain, trapped order'},
    '𐑺': {'kinetics': 'trapped (disordered)', 'processing': 'melt-spin / glass-forming',
           'microstructure': 'metallic glass, no long-range order'},
}

G_MATERIAL = {
    '𐑚': {'interaction_range': 'local (nearest-neighbor)', 'coordination': '4-8',
           'property': 'short-range order only, sensitive to local defects'},
    '𐑔': {'interaction_range': 'mesoscale', 'coordination': 'grain-level',
           'property': 'grain-boundary-mediated, Hall-Petch applies'},
    '𐑲': {'interaction_range': 'long-range / universal', 'coordination': 'global',
           'property': 'collective modes, topological protection possible'},
}

C_MATERIAL = {
    '𐑝': {'synthesis': 'one-pot / in-situ', 'sequence': 'all precursors combined',
           'advantage': 'simplicity, scalability', 'disadvantage': 'limited control'},
    '𐑜': {'synthesis': 'combinatorial', 'sequence': 'parallel libraries',
           'advantage': 'high-throughput discovery', 'disadvantage': 'integration challenge'},
    '𐑠': {'synthesis': 'sequential / layer-by-layer', 'sequence': 'ordered deposition',
           'advantage': 'precise architecture', 'disadvantage': 'slow, expensive'},
    '𐑵': {'synthesis': 'templated / broadcast', 'sequence': 'scaffold-directed',
           'advantage': 'complex 3D geometries', 'disadvantage': 'template removal'},
}

PHI_MATERIAL = {
    '𐑢': {'criticality': 'sub-critical / inert', 'response': 'linear, no divergence',
           'sensing': 'none', 'application': 'structural material'},
    '⊙': {'criticality': 'critical (self-modeling)', 'response': 'χ ~ |T-Tc|^(-γ)',
           'sensing': 'self-sensing, extreme gain', 'application': 'sensor / actuator'},
    '𐑮': {'criticality': 'complex-plane critical', 'response': 'damped oscillations',
           'sensing': 'phase-sensitive', 'application': 'tunable filter / resonator'},
    '𐑻': {'criticality': 'exceptional point', 'response': '√ε sensitivity',
           'sensing': 'EP-enhanced', 'application': 'ultrasensitive detector'},
    '𐑣': {'criticality': 'supercritical / runaway', 'response': 'exponential growth',
           'sensing': 'threshold switch', 'application': 'trigger / fuse / one-shot'},
}

H_MATERIAL = {
    '𐑓': {'memory': 'none (Markov-0)', 'hysteresis': False,
           'history': 'no path dependence', 'fatigue': 'time-independent'},
    '𐑒': {'memory': 'one-step', 'hysteresis': 'simple loop',
           'history': 'most recent state only', 'fatigue': 'rate-dependent'},
    '𐑖': {'memory': 'two-step', 'hysteresis': 'double loop / training effect',
           'history': 'two prior states', 'fatigue': 'shake-down to steady state'},
    '𐑫': {'memory': 'eternal / shape-memory', 'hysteresis': 'persistent',
           'history': 'full path encoding', 'fatigue': 'shape-memory alloy regime'},
}

S_MATERIAL = {
    '𐑙': {'components': 1, 'class': 'unary (pure element / compound)',
           'complexity': 'lowest', 'example': 'pure Cu, SiO₂, Al₂O₃'},
    '𐑕': {'components': 2, 'class': 'binary (alloy / compound pair)',
           'complexity': 'moderate', 'example': 'steel, BaTiO₃, GaAs'},
    '𐑳': {'components': '3+', 'class': 'multi-component (HEA / perovskite)',
           'complexity': 'high', 'example': 'CrMnFeCoNi, PMN-PT, MAX phases'},
}

OMEGA_MATERIAL = {
    '𐑷': {'topology': 'trivial', 'protection': 'none',
           'edge_states': 'none', 'robustness': 'fragile'},
    '𐑴': {'topology': 'Z₂ (parity)', 'protection': 'symmetry-protected',
           'edge_states': 'helical / Dirac', 'robustness': 'defect-tolerant'},
    '𐑭': {'topology': 'ℤ (integer winding)', 'protection': 'topological (Chern)',
           'edge_states': 'chiral, quantized', 'robustness': 'disorder-immune'},
    '𐑟': {'topology': 'non-Abelian', 'protection': 'braiding-protected',
           'edge_states': 'Majorana / parafermion', 'robustness': 'fault-tolerant'},
}

# ═══════════════════════════════════════════════════════════════════
# MATERIAL DESIGN DATA STRUCTURE
# ═══════════════════════════════════════════════════════════════════

PRIMITIVE_ORDER = ['D', 'T', 'R', 'P', 'F', 'K', 'G', 'C', 'Φ', 'H', 'S', 'Ω']

@dataclass
class MaterialDesign:
    """Complete material specification derived from an IG structural type."""
    name: str
    ig_tuple: Tuple[str, ...]
    dimensionality: Dict
    topology: Dict
    interface: Dict
    symmetry: Dict
    phase: Dict
    kinetics: Dict
    interaction_range: Dict
    synthesis: Dict
    criticality: Dict
    memory: Dict
    stoichiometry: Dict
    topological_protection: Dict
    proposed_composition: str = ""
    proposed_processing: str = ""
    predicted_properties: Dict = field(default_factory=dict)
    target_applications: List[str] = field(default_factory=list)
    frobenius_score: float = 0.0
    ouroboricity_tier: str = ""

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'ig_tuple': '⟨' + ''.join(self.ig_tuple) + '>',
            'dimensionality': self.dimensionality,
            'topology': self.topology,
            'interface': self.interface,
            'symmetry': self.symmetry,
            'phase': self.phase,
            'kinetics': self.kinetics,
            'interaction_range': self.interaction_range,
            'synthesis': self.synthesis,
            'criticality': self.criticality,
            'memory': self.memory,
            'stoichiometry': self.stoichiometry,
            'topological_protection': self.topological_protection,
            'proposed_composition': self.proposed_composition,
            'proposed_processing': self.proposed_processing,
            'predicted_properties': self.predicted_properties,
            'target_applications': self.target_applications,
            'frobenius_score': self.frobenius_score,
            'ouroboricity_tier': self.ouroboricity_tier,
        }


# ═══════════════════════════════════════════════════════════════════
# THE FORGE
# ═══════════════════════════════════════════════════════════════════

class MaterialForge:
    """Forge a concrete material design from an IG structural type tuple."""

    def __init__(self):
        self._designs: Dict[str, MaterialDesign] = {}

    def forge(self, name: str, ig_tuple: Tuple[str, ...]) -> MaterialDesign:
        """Translate an IG tuple into a full MaterialDesign."""
        D, T, R, P, F, K, G, C, Phi, H, S, Omega = ig_tuple

        design = MaterialDesign(
            name=name,
            ig_tuple=ig_tuple,
            dimensionality=D_MATERIAL.get(D, D_MATERIAL['𐑨']),
            topology=T_MATERIAL.get(T, T_MATERIAL['𐑡']),
            interface=R_MATERIAL.get(R, R_MATERIAL['𐑩']),
            symmetry=P_MATERIAL.get(P, P_MATERIAL['𐑗']),
            phase=F_MATERIAL.get(F, F_MATERIAL['𐑱']),
            kinetics=K_MATERIAL.get(K, K_MATERIAL['𐑤']),
            interaction_range=G_MATERIAL.get(G, G_MATERIAL['𐑔']),
            synthesis=C_MATERIAL.get(C, C_MATERIAL['𐑝']),
            criticality=PHI_MATERIAL.get(Phi, PHI_MATERIAL['𐑢']),
            memory=H_MATERIAL.get(H, H_MATERIAL['𐑓']),
            stoichiometry=S_MATERIAL.get(S, S_MATERIAL['𐑕']),
            topological_protection=OMEGA_MATERIAL.get(Omega, OMEGA_MATERIAL['𐑷']),
        )

        self._synthesize_composition(design)
        self._synthesize_processing(design)
        self._synthesize_properties(design)
        self._synthesize_applications(design)
        self._compute_frobenius_score(design)
        self._compute_tier(design)

        self._designs[name] = design
        return design

    def _synthesize_composition(self, d: MaterialDesign):
        n_comp = d.stoichiometry['components']
        topo_prot = d.topological_protection['topology']

        if n_comp == 1:
            if topo_prot == 'ℤ (integer winding)':
                d.proposed_composition = "Bi₂Se₃ or Sb₂Te₃ (3D topological insulator)"
            elif topo_prot == 'Z₂ (parity)':
                d.proposed_composition = "Graphene / stanene (2D Z₂ topological insulator)"
            elif d.phase['phase'] == 'quantum-coherent':
                d.proposed_composition = "Si (isotopically purified ²⁸Si, single crystal)"
            elif d.criticality['criticality'] == 'critical (self-modeling)':
                d.proposed_composition = "VO₂ (metal-insulator transition @ 67°C)"
            else:
                d.proposed_composition = "Al₂O₃ (sapphire, α-phase)"
        elif n_comp == 2:
            if d.memory['memory'] == 'eternal / shape-memory':
                d.proposed_composition = "NiTi (Nitinol, equiatomic shape-memory alloy)"
            elif topo_prot == 'ℤ (integer winding)':
                d.proposed_composition = "HgTe/CdTe quantum well (topological insulator)"
            elif d.interface['interface'] == 'dynamic (Diels-Alder, disulfide)':
                d.proposed_composition = "Epoxy-amine with Diels-Alder adducts (self-healing)"
            elif d.symmetry['symmetry'] == 'partially ordered (Z₂)':
                d.proposed_composition = "BaTiO₃ (ferroelectric perovskite)"
            elif d.criticality['criticality'] == 'critical (self-modeling)':
                d.proposed_composition = "Pb(Mg₁/₃Nb₂/₃)O₃-PbTiO₃ (PMN-PT relaxor)"
            else:
                d.proposed_composition = "Ti-6Al-4V (α+β titanium alloy)"
        else:
            if d.symmetry['symmetry'] == 'Frobenius-closed':
                d.proposed_composition = "CrMnFeCoNi (Cantor HEA) + self-healing microcapsules"
            elif topo_prot == 'ℤ (integer winding)':
                d.proposed_composition = "(Bi,Sb)₂(Te,Se)₃ ternary topological insulator"
            elif d.memory['memory'] == 'eternal / shape-memory':
                d.proposed_composition = "NiTiHfPd (high-temperature shape-memory HEA)"
            elif d.criticality['criticality'] == 'critical (self-modeling)':
                d.proposed_composition = "Gd₅(SiₓGe₁₋ₓ)₄ (giant magnetocaloric)"
            else:
                d.proposed_composition = "AlCoCrFeNi₂.₁ (eutectic high-entropy alloy)"

    def _synthesize_processing(self, d: MaterialDesign):
        kin = d.kinetics['processing']
        syn = d.synthesis['synthesis']
        steps = []
        steps.append(f"1. Precursor: {d.proposed_composition}")
        steps.append(f"2. Primary: {kin} ({syn})")
        if d.interface['reversible']:
            steps.append("3. Interface engineering: dynamic bonding cycle (heat-cool 3×)")
        else:
            steps.append("3. Interface engineering: controlled atmosphere bonding")
        if d.topological_protection['topology'] != 'trivial':
            steps.append("4. Topology: ultrahigh vacuum (10⁻¹⁰ torr), epitaxial growth")
        elif d.phase['phase'] == 'quantum-coherent':
            steps.append("4. Purification: zone refining, 99.9999%+ purity target")
        if d.memory['memory'] != 'none (Markov-0)':
            steps.append(f"5. Memory training: {d.memory['history']} cycling protocol")
        d.proposed_processing = '\n'.join(steps)

    def _synthesize_properties(self, d: MaterialDesign):
        props = {}
        if d.interface['bond_energy']:
            be = d.interface['bond_energy']
            if '800' in str(be):
                props['Young_modulus_GPa'] = '200-400 (stiff)'
                props['Tensile_strength_MPa'] = '1000-3000'
            elif '300' in str(be):
                props['Young_modulus_GPa'] = '50-200 (moderate)'
                props['Tensile_strength_MPa'] = '300-1000'
            else:
                props['Young_modulus_GPa'] = '1-50 (flexible)'
                props['Tensile_strength_MPa'] = '10-300'

        if d.topological_protection['topology'] != 'trivial':
            props['Thermal_conductivity_WmK'] = '10-100 (phonon-dominated, edge-channel)'
        elif d.phase['phase'] == 'quantum-coherent':
            props['Thermal_conductivity_WmK'] = '> 1000 (ballistic, ultra-pure)'
        else:
            props['Thermal_conductivity_WmK'] = '1-50'

        if d.criticality['criticality'] == 'critical (self-modeling)':
            props['Electrical_resistivity'] = 'nonlinear, χ-divergent near Tc'
        elif d.topological_protection['topology'] == 'ℤ (integer winding)':
            props['Electrical_resistivity'] = 'surface: metallic (~h/e²), bulk: insulating'
        elif d.topological_protection['topology'] == 'Z₂ (parity)':
            props['Electrical_resistivity'] = 'edge: ~h/2e² quantized'
        else:
            props['Electrical_resistivity'] = 'ohmic, ρ ~ 10⁻⁶ to 10⁻² Ω·m'

        if d.interface['interface'] == 'dynamic (Diels-Alder, disulfide)':
            props['Self_healing_efficiency'] = '85-95% (thermal trigger)'
            props['Healing_cycles'] = '50-200'
        elif d.symmetry['symmetry'] == 'Frobenius-closed':
            props['Self_healing_efficiency'] = '> 99% (autonomous, μ∘δ=id)'
            props['Healing_cycles'] = 'unlimited (Frobenius-closed)'
        else:
            props['Self_healing_efficiency'] = 'none'

        if d.memory['memory'] != 'none (Markov-0)':
            props['Shape_memory_strain_pct'] = '4-8%'
            if d.memory['memory'] == 'eternal / shape-memory':
                props['Shape_memory_strain_pct'] = '6-10% (full recovery)'
                props['Transformation_temperature_C'] = '-50 to +200'

        if d.topological_protection['topology'] != 'trivial':
            props['Topological_invariant'] = d.topological_protection['protection']
            props['Edge_state_type'] = d.topological_protection['edge_states']
            props['Robustness'] = d.topological_protection['robustness']

        d.predicted_properties = props

    def _synthesize_applications(self, d: MaterialDesign):
        apps = []
        if d.criticality['criticality'] == 'critical (self-modeling)':
            apps.append('Ultra-sensitive strain sensor (self-referencing)')
            apps.append('Critical-point actuator (χ-divergent response)')
        elif d.criticality['criticality'] == 'exceptional point':
            apps.append('Single-molecule detector (EP-enhanced √ε)')
            apps.append('Environmental monitoring (trace analyte)')

        if d.topological_protection['topology'] != 'trivial':
            apps.append('Topological quantum computing substrate')
            apps.append('Dissipationless interconnects (edge channels)')
        elif d.topological_protection['topology'] == 'ℤ (integer winding)':
            apps.append('Quantum Hall metrology standard')

        if d.interface['reversible'] and d.interface['bond_energy']:
            apps.append('Self-healing structural composite')
        if d.symmetry['symmetry'] == 'Frobenius-closed':
            apps.append('Autonomous damage-repair coating')
            apps.append('Self-verifying critical infrastructure material')

        if d.memory['memory'] != 'none (Markov-0)':
            apps.append('Shape-memory actuator / deployable structure')
            if d.memory['memory'] == 'eternal / shape-memory':
                apps.append('Morphing aerospace structure (full path memory)')

        if d.phase['phase'] == 'quantum-coherent':
            apps.append('Quantum sensing / qubit host')
        if d.dimensionality['dimensionality'] == 'hierarchical':
            apps.append('Hierarchical impact absorber (nano to macro)')

        if not apps:
            apps.append('General structural / mechanical')
        d.target_applications = apps

    def _compute_frobenius_score(self, d: MaterialDesign):
        score = 0.0
        ig = d.ig_tuple
        if ig[3] == '𐑹': score += 0.3
        if ig[2] == '𐑾': score += 0.1
        if ig[9] == '𐑫': score += 0.2
        if ig[4] == '𐑐': score += 0.05
        if ig[7] == '𐑠': score += 0.05
        if ig[11] == '𐑭': score += 0.1
        if d.interface['interface'] == 'dynamic (Diels-Alder, disulfide)':
            score += 0.15
        if 'Self_healing_efficiency' in d.predicted_properties:
            eff = d.predicted_properties['Self_healing_efficiency']
            if '99' in str(eff):
                score += 0.05
        d.frobenius_score = round(min(score, 1.0), 2)

    def _compute_tier(self, d: MaterialDesign):
        ig = d.ig_tuple
        if ig[0] == '𐑦' and ig[1] == '𐑸' and ig[8] == '⊙' and ig[9] == '𐑫' and ig[11] == '𐑭':
            d.ouroboricity_tier = 'O_∞'
        elif ig[8] == '⊙' and ig[9] in ('𐑫', '𐑖') and ig[11] in ('𐑭', '𐑴'):
            d.ouroboricity_tier = 'O₂'
        elif ig[8] in ('⊙', '𐑮', '𐑻') and ig[9] in ('𐑖', '𐑫'):
            d.ouroboricity_tier = 'O₂'
        elif ig[8] in ('⊙', '𐑮'):
            d.ouroboricity_tier = 'O₁'
        elif ig[11] in ('𐑭', '𐑴') or ig[9] in ('𐑖', '𐑫'):
            d.ouroboricity_tier = 'O₁'
        else:
            d.ouroboricity_tier = 'O₀'

    def forge_from_imas(self, imas_name: str) -> MaterialDesign:
        """Forge a material from an IMASM canonical arrangement name."""
        import sys, os as _os
        sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
        from imas.arranger import CANONICAL_FINGERPRINTS
        from imas.ig_bridge import fingerprint_to_ig

        if imas_name not in CANONICAL_FINGERPRINTS:
            raise KeyError(f"Unknown IMASM canonical: {imas_name}. Known: {list(CANONICAL_FINGERPRINTS.keys())}")

        fp = CANONICAL_FINGERPRINTS[imas_name]
        ig = fingerprint_to_ig(fp)
        material_name = f"{imas_name}_material"
        return self.forge(material_name, ig)

    def forge_from_catalog(self, catalog_name: str) -> MaterialDesign:
        """Forge a material from a catalog entry by name."""
        import os as _os
        catalog_paths = [
            _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "shared", "IG_catalog.json"),
            _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "shared", "IG_catalog.json"),
        ]
        catalog = None
        for cp in catalog_paths:
            if _os.path.exists(cp):
                with open(cp, 'r') as f:
                    catalog = json.load(f)
                break
        if catalog is None:
            raise FileNotFoundError("IG_catalog.json not found in shared/")

        # Search by exact name, then case-insensitive
        entry = None
        for e in catalog:
            if e['name'] == catalog_name:
                entry = e
                break
        if entry is None:
            for e in catalog:
                if e['name'].lower() == catalog_name.lower():
                    entry = e
                    break
        if entry is None:
            # Partial match
            matches = [e['name'] for e in catalog if catalog_name.lower() in e['name'].lower()]
            if matches:
                raise KeyError(f"Catalog entry '{catalog_name}' not found. Did you mean: {', '.join(matches[:10])}?")
            raise KeyError(f"Catalog entry '{catalog_name}' not found in {len(catalog)} entries.")

        # Build tuple from catalog entry (uses '⊙' field for Phi)
        ig_tuple = (
            entry['Ð'], entry['Þ'], entry['Ř'], entry['Φ'],
            entry['ƒ'], entry['Ç'], entry['Γ'], entry['ɢ'],
            entry['⊙'], entry['Ħ'], entry['Σ'], entry['Ω'],
        )
        return self.forge(catalog_name, ig_tuple)

    def list_designs(self) -> List[str]:
        return sorted(self._designs.keys())

    def report(self, name: str) -> str:
        d = self._designs.get(name)
        if not d:
            return f"No design found for '{name}'"

        ig_str = '⟨' + ''.join(d.ig_tuple) + '>'
        lines = [
            "=" * 72,
            f"  MATERIAL DESIGN: {d.name}",
            f"  IG Type: {ig_str}",
            f"  Ouroboricity: {d.ouroboricity_tier}  |  Frobenius Score: {d.frobenius_score:.2f}",
            "=" * 72,
            "", "── STRUCTURE ──",
            f"  Dimensionality:   {d.dimensionality['structure']} ({d.dimensionality['size_regime']})",
            f"  Topology:         {d.topology['connectivity']} — {d.topology['structure']}",
            f"  Symmetry:         {d.symmetry['symmetry']}",
            f"  Phase:            {d.phase['character']}",
            "", "── COMPOSITION ──",
            f"  {d.proposed_composition}",
            f"  Components:       {d.stoichiometry['class']}",
            "", "── PROCESSING ──",
            d.proposed_processing,
            "", "── INTERFACES ──",
            f"  Coupling:         {d.interface['interface']} ({d.interface['bond_energy']})",
            f"  Reversible:       {d.interface['reversible']}",
            "", "── PROPERTIES ──",
        ]
        for prop, val in d.predicted_properties.items():
            lines.append(f"  {prop.replace('_', ' '):30s} {val}")
        lines += [
            "", "── TOPOLOGICAL PROTECTION ──",
            f"  Invariant:        {d.topological_protection['topology']}",
            f"  Protection:       {d.topological_protection['protection']}",
            f"  Edge states:      {d.topological_protection['edge_states']}",
            f"  Robustness:       {d.topological_protection['robustness']}",
            "", "── CRITICALITY ──",
            f"  Regime:           {d.criticality['criticality']}",
            f"  Response:         {d.criticality['response']}",
            f"  Application:      {d.criticality['application']}",
            "", "── MEMORY ──",
            f"  Type:             {d.memory['memory']}",
            f"  Hysteresis:       {d.memory['hysteresis']}",
            f"  History:          {d.memory['history']}",
            "", "── TARGET APPLICATIONS ──",
        ]
        for i, app in enumerate(d.target_applications, 1):
            lines.append(f"  {i}. {app}")
        lines.append("")
        lines.append("=" * 72)
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════════════
# PREDEFINED NOVEL MATERIALS
# ═══════════════════════════════════════════════════════════════════

def predefined_novel_materials() -> Dict[str, Tuple[str, ...]]:
    """Return a set of structurally novel IG material types."""
    return {
        'frobenius_composite': (
            '𐑼', '𐑸', '𐑾', '𐑹', '𐑞', '𐑧', '𐑲', '𐑠', '𐑮', '𐑫', '𐑳', '𐑭'
        ),
        'critical_sensor_metamaterial': (
            '𐑼', '𐑥', '𐑾', '𐑬', '𐑞', '𐑧', '𐑲', '𐑠', '⊙', '𐑖', '𐑳', '𐑭'
        ),
        'ep_detector': (
            '𐑨', '𐑡', '𐑽', '𐑬', '𐑐', '𐑘', '𐑔', '𐑜', '𐑻', '𐑒', '𐑕', '𐑴'
        ),
        'eternal_memory_alloy': (
            '𐑼', '𐑰', '𐑑', '𐑬', '𐑞', '𐑤', '𐑲', '𐑝', '𐑢', '𐑫', '𐑳', '𐑷'
        ),
        'topological_thermal_rectifier': (
            '𐑼', '𐑸', '𐑾', '𐑬', '𐑞', '𐑧', '𐑔', '𐑝', '⊙', '𐑖', '𐑳', '𐑭'
        ),
        'hierarchical_impact_absorber': (
            '𐑦', '𐑸', '𐑑', '𐑯', '𐑱', '𐑪', '𐑲', '𐑠', '𐑢', '𐑖', '𐑳', '𐑴'
        ),
        'quantum_topological_substrate': (
            '𐑨', '𐑡', '𐑽', '𐑯', '𐑐', '𐑪', '𐑲', '𐑠', '𐑮', '𐑫', '𐑙', '𐑭'
        ),
        'non_abelian_braiding_material': (
            '𐑦', '𐑸', '𐑾', '𐑹', '𐑐', '𐑧', '𐑲', '𐑠', '⊙', '𐑫', '𐑳', '𐑟'
        ),
    }


# ═══════════════════════════════════════════════════════════════════
# MAIN — argparse CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse, os, sys

    # Resolve REBIS_ROOT for IMASM bridge
    _here = os.path.dirname(os.path.abspath(__file__))
    _rebis_root = os.path.dirname(_here)

    parser = argparse.ArgumentParser(
        description="IG Material Forge — structural type → concrete material design",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                          List all predefined materials
  %(prog)s --all                            Forge all 8 predefined novel materials
  %(prog)s --name frobenius_composite       Forge one predefined material
  %(prog)s --tuple '𐑼,𐑸,𐑾,𐑹,𐑞,𐑧,𐑲,𐑠,𐑮,𐑫,𐑳,𐑭'
  %(prog)s --catalog riemann_zeta_function  Forge from catalog entry
  %(prog)s --imas I_Dialetheic_Bootstrap    Forge from IMASM canonical
  %(prog)s --tuple '𐑼,𐑸,𐑾,𐑹,𐑞,𐑧,𐑲,𐑠,𐑮,𐑫,𐑳,𐑭' --name my_material --output my_mat.json
"""
    )
    parser.add_argument("--name", type=str, help="Predefined material name or name for custom tuple")
    parser.add_argument("--tuple", type=str,
                        help="Comma-separated 12-tuple: D,T,R,P,F,K,G,C,Phi,H,S,Omega (IG primitives)")
    parser.add_argument("--catalog", type=str, help="Catalog entry name to forge from IG_catalog.json")
    parser.add_argument("--imas", type=str, help="IMASM canonical name to forge from")
    parser.add_argument("--all", action="store_true", help="Forge all predefined materials")
    parser.add_argument("--list", action="store_true", help="List all available predefined materials")
    parser.add_argument("--output", type=str, help="Export path for JSON results")
    parser.add_argument("--json", action="store_true", help="Output single design as JSON to stdout")

    args = parser.parse_args()
    forge = MaterialForge()

    # --list
    if args.list:
        novel = predefined_novel_materials()
        info_line("Predefined materials:")
        for name, tup in novel.items():
            info_line(f"  {name:40s} ⟨{''.join(tup)}>")
        info_line(f"\n  {len(novel)} predefined materials")
        info_line("\nAlso try: --imas I_Dialetheic_Bootstrap (12 IMASM canonicals)")
        info_line("          --catalog <name> (3300+ catalog entries)")
        return 0

    # --all
    if args.all:
        novel = predefined_novel_materials()
        designs = {}
        for name, ig_tuple in novel.items():
            design = forge.forge(name, ig_tuple)
            designs[name] = design
            info_line(f"  {name:40s} {design.ouroboricity_tier:6s} Frob={design.frobenius_score:.2f}  "
                  f"{design.proposed_composition[:70]}")
        info_line(f"\n  Total: {len(designs)} materials forged")

        if args.output:
            out = {name: d.to_dict() for name, d in designs.items()}
            with open(args.output, 'w') as f:
                json.dump(out, f, indent=2)
            info_line(f"  Exported to {args.output}")
        return 0

    # Determine what to forge
    ig_tuple = None
    design_name = args.name

    if args.tuple:
        parts = [p.strip() for p in args.tuple.split(',')]
        if len(parts) != 12:
            error_line(f"Error: --tuple requires exactly 12 comma-separated primitives, got {len(parts)}")
            info_line("Expected: D,T,R,P,F,K,G,C,Phi,H,S,Omega")
            info_line("Example: '𐑼,𐑸,𐑾,𐑹,𐑞,𐑧,𐑲,𐑠,𐑮,𐑫,𐑳,𐑭'")
            return 1
        ig_tuple = tuple(parts)
        if design_name is None:
            design_name = "custom_material"

    elif args.catalog:
        try:
            design = forge.forge_from_catalog(args.catalog)
            print(forge.report(design.name))
            if args.json:
                print(json.dumps(design.to_dict(), indent=2))
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(design.to_dict(), f, indent=2)
                info_line(f"\n  Exported to {args.output}")
            return 0
        except (KeyError, FileNotFoundError) as e:
            error_line(f"Error: {e}")
            return 1

    elif args.imas:
        try:
            sys.path.insert(0, _rebis_root)
            design = forge.forge_from_imas(args.imas)
            print(forge.report(design.name))
            if args.json:
                print(json.dumps(design.to_dict(), indent=2))
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(design.to_dict(), f, indent=2)
                info_line(f"\n  Exported to {args.output}")
            return 0
        except Exception as e:
            error_line(f"Error: {e}")
            return 1

    elif args.name:
        novel = predefined_novel_materials()
        if args.name in novel:
            ig_tuple = novel[args.name]
        else:
            info_line(f"Unknown material: '{args.name}'")
            info_line(f"Predefined: {', '.join(novel.keys())}")
            info_line("Use --list to see all options, --tuple for custom, or --catalog for catalog lookup.")
            return 1

    # Forge the tuple (from --name or --tuple)
    if ig_tuple:
        design = forge.forge(design_name, ig_tuple)
        print(forge.report(design_name))
        if args.json:
            print(json.dumps(design.to_dict(), indent=2))
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(design.to_dict(), f, indent=2)
            info_line(f"\n  Exported to {args.output}")
        return 0

    # No action specified
    parser.print_help()
    return 1


if __name__ == "__main__":
    import sys; sys.exit(main())

