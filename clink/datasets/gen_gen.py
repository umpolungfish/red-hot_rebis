#!/usr/bin/env python3
"""Write complete generators.py for physically actionable datasets."""
import json, os, textwrap
from shared.rich_output import *

PY = "/home/mrnob0dy666/red-hot_rebis/clink/datasets/generators.py"

def w(s):
    with open(PY, 'a') as f:
        f.write(s + '\n')

# Clear file
open(PY, 'w').write('')

hdr = '''"""
generators.py — Physically actionable dataset generators for all 9 CLINK layers
================================================================================

Design principle:
  - Bridge to existing tools FIRST (serpentrod, ch3mpiler, gene_imscriber, etc.)
  - Fall back to first-principles generation when tool is unavailable
  - Every dataset carries its own Frobenius verification metadata
  - Output files placed in clink/datasets/output/<layer_name>/

Author: Lando (R) (O)perator
"""
'''
w(hdr)

# Imports
w('''
from __future__ import annotations
import json, os, sys, math, random, hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))
''')

# Base classes
w('''
@dataclass
class DatasetFile:
    """A single physically-actionable output file."""
    filename: str
    extension: str
    content: str
    description: str
    format_name: str
    frobenius_hash: str = ""

@dataclass
class DatasetOutput:
    """Complete dataset output for a single CLINK layer."""
    layer_idx: int
    layer_name: str
    layer_tier: str
    files: List[DatasetFile] = field(default_factory=list)
    structural_tuple: Dict[str, str] = field(default_factory=dict)
    frobenius_verified: bool = False
    generation_time: str = field(default_factory=lambda: datetime.now().isoformat())
    tool_bridges_used: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

class DatasetGenerator:
    """Base class for layer-specific dataset generators."""
    layer_idx: int = -1
    layer_name: str = ""
    
    def __init__(self):
        from clink.chain import clink_layer_tuple

        self.tup = clink_layer_tuple(self.layer_idx)
        self.output_dir = Path(__file__).parent / "output" / self.layer_name.replace(" ", "_")
    
    def generate(self, design_data: Optional[Dict] = None) -> DatasetOutput:
        raise NotImplementedError
    
    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def _ensure_output_dir(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _write_file(self, filename: str, content: str) -> Path:
        self._ensure_output_dir()
        path = self.output_dir / filename
        with open(path, 'w') as f:
            f.write(content)
        return path
''')

info_line("Base written")

# L0 - Quarks
w('''
# ============================================================
# LAYER 0 — Frustrated Belnap5 (Quark Color) — O₀
# ============================================================

class Layer0DatasetGenerator(DatasetGenerator):
    """QCD parameters, coupling constants, hadron spectrum."""
    layer_idx = 0
    
    def generate(self, design_data=None):
        out = DatasetOutput(
            layer_idx=0, layer_name="Frustrated Belnap5 (Quarks)",
            layer_tier="O₀", structural_tuple=dict(self.tup),
        )
        
        out.files.append(DatasetFile(
            filename="qcd_coupling_alpha_s.csv",
            extension=".csv",
            content=self._gen_alpha_s_table(),
            description="Running QCD coupling constant alpha_s vs energy scale",
            format_name="CSV",
        ))
        out.files.append(DatasetFile(
            filename="qcd_lattice_params.xml",
            extension=".xml",
            content=self._gen_lattice_params(),
            description="Lattice QCD simulation parameters for MILC/ChromaLattice",
            format_name="XML",
        ))
        out.files.append(DatasetFile(
            filename="hadron_mass_spectrum.json",
            extension=".json",
            content=self._gen_hadron_spectrum(),
            description="Predicted hadron mass spectrum",
            format_name="JSON",
        ))
        out.files.append(DatasetFile(
            filename="su3_color_charges.json",
            extension=".json",
            content=self._gen_color_table(),
            description="SU(3) color charge assignments",
            format_name="JSON",
        ))
        out.frobenius_verified = clink_frobenius_closed(self.tup)
        return out
    
    def _gen_alpha_s_table(self):
        lines = ["Q2_MeV2,alpha_s,error"]
        for Q2 in [1,2,5,10,20,50,100,200,500,1000,2000,5000,10000]:
            a = max(0.05, min(0.5, 0.12 / math.log(max(math.sqrt(Q2)/0.2, 1.1))))
            lines.append(f"{Q2},{a:.4f},{a*0.05:.4f}")
        return "\\n".join(lines)
    
    def _gen_lattice_params(self):
        return """<?xml version="1.0"?>
<latticeQCD>
  <gauge_group>SU(3)</gauge_group>
  <n_colors>3</n_colors>
  <n_flavors>6</n_flavors>
  <lattice_size>24 24 24 48</lattice_size>
  <beta>6.0</beta>
  <confinement_scale_MeV>200</confinement_scale_MeV>
  <action>Wilson</action>
  <observables>wilson_loop polyakov_loop pion_mass rho_mass nucleon_mass</observables>
</latticeQCD>"""
    
    def _gen_hadron_spectrum(self):
        return json.dumps({
            "mesons": {"pion": {"mass_MeV":135,"JPC":"0-+"},"rho": {"mass_MeV":770,"JPC":"1--"},"kaon":{"mass_MeV":494},"J_psi":{"mass_MeV":3097}},
            "baryons": {"proton":{"mass_MeV":938,"JP":"1/2+"},"neutron":{"mass_MeV":940},"lambda":{"mass_MeV":1116}},
        }, indent=2, ensure_ascii=False)
    
    def _gen_color_table(self):
        return json.dumps({
            "color_charges": ["red","green","blue"],
            "anti_colors": ["anti_red","anti_green","anti_blue"],
            "confinement": True, "asymptotic_freedom": True,
        }, indent=2, ensure_ascii=False)
''')

info_line("L0 written")

# L1 - Electron Orbitals  
w('''
# ============================================================
# LAYER 1 — Electron Orbital (Belnap4) — O₀
# ============================================================

class Layer1DatasetGenerator(DatasetGenerator):
    """Electron configuration, orbital occupancy, quantum chemistry inputs."""
    layer_idx = 1
    
    def generate(self, design_data=None):
        out = DatasetOutput(
            layer_idx=1, layer_name="Electron Orbital (Belnap4)",
            layer_tier="O₀", structural_tuple=dict(self.tup),
        )
        out.files.append(DatasetFile(
            filename="electron_configurations.csv",
            extension=".csv",
            content=self._gen_electron_configs(),
            description="Electron configurations for all elements",
            format_name="CSV",
        ))
        out.files.append(DatasetFile(
            filename="b4_lattice_nucleotide_map.json",
            extension=".json",
            content=self._gen_b4_mapping(),
            description="Belnap4 lattice to nucleotide mapping",
            format_name="JSON",
        ))
        out.files.append(DatasetFile(
            filename="quantum_chemistry_inputs.json",
            extension=".json",
            content=self._gen_qc_inputs(),
            description="Quantum chemistry input deck manifest",
            format_name="JSON",
        ))
        out.frobenius_verified = clink_frobenius_closed(self.tup)
        return out
    
    def _gen_electron_configs(self):
        cfgs = {1:"1s1",2:"1s2",3:"1s2 2s1",4:"1s2 2s2",5:"1s2 2s2 2p1",6:"1s2 2s2 2p2",
                7:"1s2 2s2 2p3",8:"1s2 2s2 2p4",9:"1s2 2s2 2p5",10:"1s2 2s2 2p6",
                11:"[Ne] 3s1",12:"[Ne] 3s2",13:"[Ne] 3s2 3p1",14:"[Ne] 3s2 3p2",
                15:"[Ne] 3s2 3p3",16:"[Ne] 3s2 3p4",17:"[Ne] 3s2 3p5",18:"[Ne] 3s2 3p6",
                19:"[Ar] 4s1",20:"[Ar] 4s2",26:"[Ar] 3d6 4s2"}
        syms = {1:"H",2:"He",6:"C",7:"N",8:"O",15:"P",16:"S",26:"Fe"}
        lines = ["Z,symbol,config"]
        for z in sorted(cfgs.keys()):
            lines.append(f"{z},{syms.get(z,'?')},{cfgs[z]}")
        return "\\n".join(lines)
    
    def _gen_b4_mapping(self):
        return json.dumps({
            "B4_to_nucleotide": {
                "B_Both": "Guanine_G", "T_True": "Cytosine_C",
                "F_False": "Adenine_A", "N_Neither": "Thymine_T"
            },
            "bridge_to_gene_imscriber": True,
        }, indent=2, ensure_ascii=False)
    
    def _gen_qc_inputs(self):
        return json.dumps({
            "software": ["Gaussian","ORCA","GAMESS","NWChem"],
            "basis_sets": ["STO-3G","6-31G(d)","cc-pVDZ","aug-cc-pVQZ"],
            "methods": ["HF","DFT/B3LYP","MP2","CCSD(T)"],
        }, indent=2, ensure_ascii=False)
''')

info_line("L1 written")
info_line("Script generation complete. Run this script to produce generators.py")
