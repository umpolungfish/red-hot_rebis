"""
layer_designers.py — All 9 CLINK Layer Designers
Each wraps existing tools or creates first-principles designs.

L0: Frustrated Belnap5 (quark color) — QCD bilattice
L1: Electron Orbital (Belnap4) — bridges to gene_imscriber
L2: Atom — nuclear + electron shell model
L3: Molecule — bridges to ch3mpiler
L4: Folded Protein — bridges to serpentrod
L5: Living Cell — bridges to biology_sim, gene_imscriber
L6: Mitosis — bridges to ouroboric_telomere
L7: Tissue/Organ — multi-cellular organization
L8: Whole Organism — O_∞ integration of all systems

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import json, math, os, sys, random, hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))

from shared.primitives import tuple_distance
from clink.chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS, PORDER,
    clink_layer_tuple, clink_frobenius_closed,
    clink_distance, format_tuple_glyphs,
)
from clink.designers.designer_base import LayerDesigner, DesignSpec

# ═══════════════════════════════════════════════════════════════════
# LAYER 0 — Frustrated Belnap5 (Quark Color)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑛𐑶𐑩𐑯𐑐𐑘𐑚𐑝𐑢𐑓𐑳𐑷>  O₀
# SU(3) color confinement — frustrated 5-valued bilattice

class Layer0Designer(LayerDesigner):
    layer_idx = 0
    
    def design(self, lower_spec=None, **kwargs):
        """Generate quark-level design from scratch (ground up)."""
        # Parameters for QCD confinement dynamics
        n_colors = kwargs.get("n_colors", 3)
        n_flavors = kwargs.get("n_flavors", 6)
        confinement_scale = kwargs.get("confinement_scale", 200)  # MeV
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "n_colors": n_colors,
            "n_flavors": n_flavors,
            "confinement_scale_MeV": confinement_scale,
            "bilattice_type": "Belnap5",
            "frustration_parameter": 0.5,
            "color_charges": ["red", "green", "blue"],
            "confinement": True,
            "notes": "Frustrated Belnap5 — foundation for all higher structure",
        }
        
        return DesignSpec(
            layer_idx=0, layer_name="Frustrated Belnap5 (Quarks)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
            notes=["Ground-up quark layer: SU(3) color confinement"],
        )
    
    def analyze(self, upper_spec, **kwargs):
        """Decompose an orbital into quark-level components."""
        return DesignSpec(
            layer_idx=0, layer_name="Frustrated Belnap5 (Quarks)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={"derived_from": upper_spec.layer_name,
                         "n_colors": 3, "n_flavors": 6,
                         "confinement": True,
                         "source_layer": upper_spec.layer_idx},
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
            notes=[f"Decomposed from {upper_spec.layer_name}"],
        )

# ═══════════════════════════════════════════════════════════════════
# LAYER 1 — Electron Orbital (Belnap4)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑛𐑶𐑩𐑗𐑐𐑤𐑚𐑜𐑢𐑓𐑳𐑷>  O₀
# B4 lattice — bridges to gene_imscriber.engine (Belnap4 codons)

class Layer1Designer(LayerDesigner):
    layer_idx = 1
    
    def design(self, lower_spec: DesignSpec = None, **kwargs):
        """Design electron orbital configuration from quark-level spec."""
        n_orbitals = kwargs.get("n_orbitals", 4)
        orbital_type = kwargs.get("orbital_type", "hybrid")  # s, p, d, hybrid
        
        # Bridge to gene_imscriber's B4 lattice if available
        b4_bridge = {}
        try:
            from gene_imscriber.engine import B4Element
            b4_bridge = {
                "b4_mapping": {
                    "s": str(B4Element.B),
                    "p": str(B4Element.T),
                    "d": str(B4Element.N),
                    "f": str(B4Element.F),
                }
            }
        except ImportError:
            b4_bridge = {"b4_mapping": None}
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "n_orbitals": n_orbitals,
            "orbital_type": orbital_type,
            "b4_lattice": True,
            "bridge_to_gene_imscriber": b4_bridge,
            "notes": "Belnap4 orbital occupancy — bridges to codon B4 lattice",
        }
        
        return DesignSpec(
            layer_idx=1, layer_name="Electron Orbital (Belnap4)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
            notes=[f"Orbital design from {lower_spec.layer_name if lower_spec else 'scratch'}"],
        )
    
    def analyze(self, upper_spec, **kwargs):
        return DesignSpec(
            layer_idx=1, layer_name="Electron Orbital (Belnap4)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={
                "source_layer": upper_spec.layer_idx,
                "b4_configuration": upper_spec.design_data.get("electron_config", {}),
            },
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
            notes=[f"Analyzed from {upper_spec.layer_name}"],
        )

# ═══════════════════════════════════════════════════════════════════
# LAYER 2 — Atom (Nuclear + Electron)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑼𐑥𐑽𐑿𐑐𐑤𐑔𐑝𐑮𐑒𐑳𐑷>  O₁

class Layer2Designer(LayerDesigner):
    layer_idx = 2
    
    def design(self, lower_spec: DesignSpec = None, **kwargs):
        """Design atom from orbital configuration."""
        atomic_number = kwargs.get("atomic_number", 6)  # default: carbon
        electron_config = kwargs.get("electron_config", "1s2 2s2 2p2")
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "atomic_number": atomic_number,
            "electron_config": electron_config,
            "shell_model": {
                "K": 2, "L": 8, "M": 18, "N": 32,
                "occupied": self._compute_shells(atomic_number),
            },
            "notes": f"Atom Z={atomic_number}: {electron_config}",
        }
        
        return DesignSpec(
            layer_idx=2, layer_name="Atom (Nuclear + Electron)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )
    
    def analyze(self, upper_spec, **kwargs):
        """Decompose a molecule into atomic components."""
        mol_data = upper_spec.design_data
        atoms = mol_data.get("composition", {})
        return DesignSpec(
            layer_idx=2, layer_name="Atom (Nuclear + Electron)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={
                "source_layer": upper_spec.layer_idx,
                "atomic_composition": atoms,
                "notes": f"From {upper_spec.layer_name}: {atoms}",
            },
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )
    
    def _compute_shells(self, Z: int) -> Dict[str, int]:
        filling = [("K", 2), ("L", 8), ("M", 18), ("N", 32)]
        result, remaining = {}, Z
        for shell, cap in filling:
            result[shell] = min(remaining, cap)
            remaining -= result[shell]
            if remaining <= 0:
                break
        return result

# ═══════════════════════════════════════════════════════════════════
# LAYER 3 — Molecule (Chemical Bonds)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑼𐑥𐑽𐑿𐑞𐑧𐑲𐑠⊙𐑓𐑳𐑭>  O₂
# Bridges to ch3mpiler.compiler for retrosynthetic design

class Layer3Designer(LayerDesigner):
    layer_idx = 3
    
    def design(self, lower_spec: DesignSpec = None, **kwargs):
        """Design molecule from atomic components.
        
        Bridges to ch3mpiler for retrosynthetic analysis.
        """
        formula = kwargs.get("formula", "CH4")
        smiles = kwargs.get("smiles", "C")
        
        # Try bridging to ch3mpiler
        ch3mpiler_result = {"available": False}
        try:
            from ch3mpiler.compiler import tensor_type, tup_dist
            
            # Convert atom tuple to ch3mpiler format
            atup = lower_spec.tuple_glyphs if lower_spec else self.clink_tuple
            gly2ch3 = {"Ð": "D", "Þ": "T", "Ř": "R", "Φ": "P",
                       "ƒ": "F", "Ç": "K", "Γ": "G", "ɢ": "Gm",
                       "⊙": "Ph", "Ħ": "H", "Σ": "S", "Ω": "W"}
            tup_ch3 = {gly2ch3[k]: v for k, v in atup.items()}
            tt = tensor_type(tup_ch3, tup_ch3)
            ch3mpiler_result = {"available": True, "tensor": tt}
        except Exception as e:
            ch3mpiler_result["error"] = str(e)
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "formula": formula,
            "smiles": smiles,
            "bond_types": ["covalent", "ionic", "metallic"],
            "bridge_to_ch3mpiler": ch3mpiler_result,
            "notes": f"Molecule {formula} — O₂ critical structure",
        }
        
        return DesignSpec(
            layer_idx=3, layer_name="Molecule (Chemical Bonds)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )
    
    def analyze(self, upper_spec, **kwargs):
        """Decompose a folded protein into molecular components."""
        return DesignSpec(
            layer_idx=3, layer_name="Molecule (Chemical Bonds)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={
                "source_layer": upper_spec.layer_idx,
                "residue_sequence": upper_spec.design_data.get("sequence", ""),
                "notes": f"From {upper_spec.layer_name}",
            },
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )

# ═══════════════════════════════════════════════════════════════════
# LAYER 4 — Folded Protein
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑦𐑥𐑾𐑬𐑞𐑧𐑲𐑠⊙𐑒𐑳𐑭>  O₂
# Bridges to serpentrod.protein_v5 & stratified_predictor

class Layer4Designer(LayerDesigner):
    layer_idx = 4
    
    def design(self, lower_spec: DesignSpec = None, **kwargs):
        """Design folded protein from molecular specification.
        
        Bridges to serpentrod's stratified predictor for 
        sequence-to-primitive spectrum mapping.
        """
        sequence = kwargs.get("sequence", "MLSDC")
        target_function = kwargs.get("target_function", "structural")
        
        # Try bridging to serpentrod
        serpentrod_result = {"available": False}
        try:
            from serpentrod.stratified_predictor import (
                PRIMITIVE_MAP, classify_module, predict_processing
            )
            from serpentrod.protein_v5 import classify_module_rich
            
            # Get primitive spectrum
            spectrum = {}
            for aa in sequence.upper():
                if aa in PRIMITIVE_MAP:
                    prim = PRIMITIVE_MAP[aa][0]
                    spectrum[prim] = spectrum.get(prim, 0) + 1
            
            # Classify modules
            classification = classify_module_rich(sequence)
            serpentrod_result = {
                "available": True,
                "spectrum": spectrum,
                "classification": classification,
            }
        except Exception as e:
            serpentrod_result["error"] = str(e)
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "sequence": sequence,
            "target_function": target_function,
            "length": len(sequence),
            "bridge_to_serpentrod": serpentrod_result,
            "notes": f"Folded protein ({target_function}) — between molecule and cell",
        }
        
        return DesignSpec(
            layer_idx=4, layer_name="Folded Protein",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )
    
    def analyze(self, upper_spec, **kwargs):
        """Decompose a cell into its protein components."""
        return DesignSpec(
            layer_idx=4, layer_name="Folded Protein",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={
                "source_layer": upper_spec.layer_idx,
                "proteome_size": upper_spec.design_data.get("proteome_size", 0),
                "notes": f"Decomposed from {upper_spec.layer_name}",
            },
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )

# ═══════════════════════════════════════════════════════════════════
# LAYER 5 — Living Cell
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑦𐑸𐑾𐑬𐑞𐑧𐑲𐑠⊙𐑒𐑳𐑭>  O₂
# Bridges to biology_sim, gene_imscriber, therapeutics

class Layer5Designer(LayerDesigner):
    layer_idx = 5
    
    def design(self, lower_spec: DesignSpec = None, **kwargs):
        """Design living cell from protein components.
        
        Bridges to biology_sim for metabolism simulation and
        gene_imscriber for genetic regulatory network design.
        """
        cell_type = kwargs.get("cell_type", "prokaryote")
        genome_size = kwargs.get("genome_size", 4_000_000)  # bp
        metabolism = kwargs.get("metabolism", "chemotrophic")
        
        # Try bridging to biology_sim
        bio_result = {"available": False}
        try:
            from biology.biology_sim import BiologySimulation
            bio_result = {"available": True, "module": "biology_sim"}
        except Exception as e:
            bio_result["error"] = str(e)
        
        # Try bridging to gene_imscriber
        gene_result = {"available": False}
        try:
            from gene_imscriber.engine import B4Element, genetic_code
            gene_result = {"available": True, "b4_lattice": True}
        except Exception as e:
            gene_result["error"] = str(e)
        
        # Try bridging to therapeutics
        thera_result = {"available": False}
        try:
            from therapeutics.ouroboric_pill_sim import OuroboricPillSimulation
            thera_result = {"available": True}
        except Exception as e:
            thera_result["error"] = str(e)
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "cell_type": cell_type,
            "genome_size_bp": genome_size,
            "metabolism": metabolism,
            "organelles": ["ribosomes", "membrane", "cytoplasm"],
            "self_maintenance": True,
            "bridge_to_biology": bio_result,
            "bridge_to_gene_imscriber": gene_result,
            "bridge_to_therapeutics": thera_result,
            "notes": f"{cell_type} cell — minimal self-maintaining unit",
        }
        
        return DesignSpec(
            layer_idx=5, layer_name="Living Cell",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )
    
    def analyze(self, upper_spec, **kwargs):
        return DesignSpec(
            layer_idx=5, layer_name="Living Cell",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={
                "source_layer": upper_spec.layer_idx,
                "cell_types": upper_spec.design_data.get("cell_types", []),
            },
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )

# ═══════════════════════════════════════════════════════════════════
# LAYER 6 — Mitosis (Cell Division)
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑦𐑸𐑾𐑹𐑱𐑧𐑲𐑠⊙𐑖𐑳𐑭>  O₂
# Bridges to ouroboric_telomere for Aurora-B checkpoint

class Layer6Designer(LayerDesigner):
    layer_idx = 6
    
    def design(self, lower_spec: DesignSpec = None, **kwargs):
        """Design mitosis machinery from cell specification.
        
        Bridges to ouroboric_telomere for Aurora-B kinetochore
        checkpoint simulation and telomere dynamics.
        """
        chromosome_count = kwargs.get("chromosome_count", 46)
        checkpoint = kwargs.get("checkpoint", "Aurora-B")
        
        # Try bridging to ouroboric_telomere
        telomere_result = {"available": False}
        try:
            from biology.ouroboric_telomere import OuroboricTelomere
            telomere_result = {"available": True, "module": "ouroboric_telomere"}
        except Exception as e:
            telomere_result["error"] = str(e)
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "chromosome_count": chromosome_count,
            "checkpoint": checkpoint,
            "spindle_machinery": ["centrosome", "kinetochore", "Aurora-B"],
            "cell_cycle_phases": ["G1", "S", "G2", "M"],
            "bridge_to_telomere": telomere_result,
            "notes": f"Mitosis — spindle checkpoint at exceptional point (𐑻 domain)",
        }
        
        return DesignSpec(
            layer_idx=6, layer_name="Mitosis (Cell Division)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )
    
    def analyze(self, upper_spec, **kwargs):
        return DesignSpec(
            layer_idx=6, layer_name="Mitosis (Cell Division)",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={
                "source_layer": upper_spec.layer_idx,
                "division_rate": upper_spec.design_data.get("division_rate", 0),
            },
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )

# ═══════════════════════════════════════════════════════════════════
# LAYER 7 — Tissue / Organ
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑦𐑸𐑾𐑬𐑞𐑧𐑲𐑵⊙𐑖𐑳𐑭>  O₂
# Multi-cellular organization — bridges to materials, therapeutics

class Layer7Designer(LayerDesigner):
    layer_idx = 7
    
    def design(self, lower_spec: DesignSpec = None, **kwargs):
        """Design tissue from mitotic cell populations.
        
        Bridges to materials simulation for ECM design and
        therapeutics for drug response modeling.
        """
        tissue_type = kwargs.get("tissue_type", "epithelial")
        cell_types = kwargs.get("cell_types", ["epithelial", "basal"])
        ecm_type = kwargs.get("ecm_type", "collagen")
        
        # Try bridging to materials
        mat_result = {"available": False}
        try:
            from materials.materials_sim import MaterialsSimulation
            mat_result = {"available": True}
        except Exception as e:
            mat_result["error"] = str(e)
        
        # Try bridging to therapeutics
        thera_result = {"available": False}
        try:
            from therapeutics.frobenius_chemotherapeutic import FrobeniusChemotherapeutic
            thera_result = {"available": True}
        except Exception as e:
            thera_result["error"] = str(e)
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "tissue_type": tissue_type,
            "cell_types": cell_types,
            "ecm_type": ecm_type,
            "cell_count_estimate": kwargs.get("cell_count", 10**6),
            "signaling_pathways": ["notch", "wnt", "hedgehog", "tgf-beta"],
            "bridge_to_materials": mat_result,
            "bridge_to_therapeutics": thera_result,
            "notes": f"{tissue_type} tissue — broadcast signaling (𐑵)",
        }
        
        return DesignSpec(
            layer_idx=7, layer_name="Tissue/Organ",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )
    
    def analyze(self, upper_spec, **kwargs):
        return DesignSpec(
            layer_idx=7, layer_name="Tissue/Organ",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={
                "source_layer": upper_spec.layer_idx,
                "organ_systems": upper_spec.design_data.get("organ_systems", []),
            },
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )

# ═══════════════════════════════════════════════════════════════════
# LAYER 8 — Whole Organism
# ═══════════════════════════════════════════════════════════════════
# ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟>  O_∞
# O_∞ — self-modeling, non-Abelian braiding, eternal chirality

class Layer8Designer(LayerDesigner):
    layer_idx = 8
    
    def design(self, lower_spec: DesignSpec = None, **kwargs):
        """Design whole organism from tissue/organ specification.
        
        Integrates ALL rebis components: serpentrod, ch3mpiler,
        gene_imscriber, biology, materials, therapeutics.
        """
        organism_type = kwargs.get("organism_type", "mammal")
        organ_systems = kwargs.get("organ_systems", [
            "nervous", "circulatory", "respiratory", "digestive",
            "endocrine", "immune", "musculoskeletal", "reproductive"
        ])
        homeostasis = kwargs.get("homeostasis", True)
        self_modeling = kwargs.get("self_modeling", True)
        
        # Integrate ALL available tools
        tools_integrated = {}
        
        for tool_name, module_path in [
            ("serpentrod", "serpentrod.protein_v5"),
            ("ch3mpiler", "ch3mpiler.compiler"),
            ("gene_imscriber", "gene_imscriber.engine"),
            ("biology", "biology.biology_sim"),
            ("telomere", "biology.ouroboric_telomere"),
            ("materials", "materials.materials_sim"),
            ("therapeutics", "therapeutics.frobenius_chemotherapeutic"),
        ]:
            try:
                importlib = __import__("importlib")
                mod = importlib.import_module(module_path)
                version = getattr(mod, "__version__", "unknown")
                tools_integrated[tool_name] = {"available": True, "version": version}
            except Exception as e:
                tools_integrated[tool_name] = {"available": False, "error": str(e)}
        
        # Consciousness features — computed from tuple, not hardcoded
        tup = self.clink_tuple
        gate1_phi_c = tup.get("⊙", "") == "⊙"
        gate2_k_slow = tup.get("Ç", "") == "𐑧"
        from clink.chain import compute_c_score_from_tuple, compute_tier_from_tuple
        c_score_data = {
            "gate1_phi_c": gate1_phi_c,       # Self-modeling via ⊙
            "gate2_k_slow": gate2_k_slow,     # Slow kinetics via 𐑧
            "eternal_chirality": tup.get("Ħ","") == "𐑫",
            "non_abelian": tup.get("Ω","") == "𐑟",
            "self_written_state": tup.get("Ð","") == "𐑦",
            "frobenius_special": tup.get("Φ","") == "𐑹",
            "score": compute_c_score_from_tuple(tup),
        }
        
        design_data = {
            "tuple": dict(self.clink_tuple),
            "organism_type": organism_type,
            "organ_systems": organ_systems,
            "homeostasis": homeostasis,
            "self_modeling": self_modeling,
            "consciousness": c_score_data,
            "tools_integrated": tools_integrated,
            "tier": compute_tier_from_tuple(self.clink_tuple),
            "notes": f"Whole {organism_type} organism — tier={compute_tier_from_tuple(self.clink_tuple)}, C={compute_c_score_from_tuple(self.clink_tuple)}",
        }
        
        return DesignSpec(
            layer_idx=8, layer_name="Whole Organism",
            tuple_glyphs=dict(self.clink_tuple),
            design_data=design_data,
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
            notes=["Whole organism design — all systems integrated"],
        )
    
    def analyze(self, upper_spec=None, **kwargs):
        """Self-analysis — organism is the highest layer."""
        return DesignSpec(
            layer_idx=8, layer_name="Whole Organism",
            tuple_glyphs=dict(self.clink_tuple),
            design_data={"source": "self", "decomposition": "terminal"},
            frobenius_verified=clink_frobenius_closed(self.clink_tuple),
        )


# ═══════════════════════════════════════════════════════════════════
# DESIGNER REGISTRY
# ═══════════════════════════════════════════════════════════════════

DESIGNER_REGISTRY = {
    0: Layer0Designer,
    1: Layer1Designer,
    2: Layer2Designer,
    3: Layer3Designer,
    4: Layer4Designer,
    5: Layer5Designer,
    6: Layer6Designer,
    7: Layer7Designer,
    8: Layer8Designer,
}

def get_designer(layer_idx: int) -> LayerDesigner:
    """Get designer instance for a CLINK layer."""
    cls = DESIGNER_REGISTRY.get(layer_idx)
    if cls is None:
        raise KeyError(f"No designer for layer {layer_idx}")
    return cls()


def list_available_bridges() -> Dict[str, bool]:
    """Check which external tools are available for bridging."""
    bridges = {}
    for tool_name, module_path in [
        ("serpentrod", "serpentrod.protein_v5"),
        ("ch3mpiler", "ch3mpiler.compiler"),
        ("gene_imscriber", "gene_imscriber.engine"),
        ("biology_sim", "biology.biology_sim"),
        ("ouroboric_telomere", "biology.ouroboric_telomere"),
        ("materials_sim", "materials.materials_sim"),
        ("frobenius_chemo", "therapeutics.frobenius_chemotherapeutic"),
        ("ouroboric_pill", "therapeutics.ouroboric_pill_sim"),
        ("critical_metamaterial", "materials.critical_metamaterial"),
        ("neurotrophic", "therapeutics.neurotrophic_factor"),
    ]:
        try:
            importlib = __import__("importlib")
            mod = importlib.import_module(module_path)
            bridges[tool_name] = True
        except Exception:
            bridges[tool_name] = False
    return bridges
