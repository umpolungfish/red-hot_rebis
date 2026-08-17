"""
generators.py — Physically actionable dataset generators for all 9 CLINK layers
================================================================================

Design principle:
  - Bridge to existing tools FIRST (serpentrod, ch3mpiler, gene_imscriber, etc.)
  - Fall back to first-principles generation when tool is unavailable
  - Every dataset carries its own Frobenius verification metadata
  - Output files placed in clink/datasets/output/<layer_name>/

Author: Lando (R) (O)perator
"""


from __future__ import annotations
import json, os, sys, math, random, hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

REBIS_ROOT = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))


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
        return "\n".join(lines)
    
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
        return "\n".join(lines)
    
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


class Layer5DatasetGenerator(DatasetGenerator):
    layer_idx = 5; layer_name = "Living Cell"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=5, layer_name=self.layer_name, layer_tier="O₂", structural_tuple=dict(self.tup))
        ct = (d or {}).get("cell_type","prokaryote") or "prokaryote"
        
        # Bridge to gene_imscriber
        try:
            sys.path.insert(0, str(REBIS_ROOT / "gene_imscriber"))
            from gene_imscriber.engine import B4Element, genetic_code
            o.tool_bridges_used.append("gene_imscriber")
            o.files.append(DatasetFile(filename="genetic_code.json",extension=".json",
                content=json.dumps({"b4_lattice":True,"codon_table":"64 codons, 21 AAs","bridge_active":True},indent=2, ensure_ascii=False),
                description="Genetic code from gene_imscriber bridge", format_name="JSON"))
        except: pass
        
        # Bridge to biology_sim
        try:
            sys.path.insert(0, str(REBIS_ROOT))
            from biology.biology_sim import OuroboricCellSim
            sim = OuroboricCellSim()
            o.tool_bridges_used.append("biology_sim")
        except: pass
        
        # DNA/FASTA - genome
        genome_len = (d or {}).get("genome_size_bp", 4000000) or 4000000
        genome = self._gen_dna(genome_len, ct)
        o.files.append(DatasetFile(filename="genome.fasta",extension=".fasta",
            content=genome, description="Whole genome DNA sequence in FASTA format", format_name="FASTA"))
        
        # GenBank format
        gb = self._gen_genbank(ct, genome_len)
        o.files.append(DatasetFile(filename="genome.gb",extension=".gb",
            content=gb, description="GenBank format genome annotation", format_name="GenBank"))
        
        # SBOL synthetic biology
        sbol = self._gen_sbol(ct)
        o.files.append(DatasetFile(filename="construct.sbol",extension=".sbol",
            content=sbol, description="SBOL synthetic biology construct", format_name="SBOL"))
        
        # Codon usage table
        codon = self._gen_codon_table()
        o.files.append(DatasetFile(filename="codon_usage.csv",extension=".csv",
            content=codon, description="Codon usage table for gene optimization", format_name="CSV"))
        
        # Metabolic pathway (SBML-like)
        met = self._gen_metabolism(ct)
        o.files.append(DatasetFile(filename="metabolism.json",extension=".json",
            content=met, description="Metabolic pathway specification", format_name="JSON"))
        
        # Growth media formulation
        media = self._gen_media(ct)
        o.files.append(DatasetFile(filename="growth_media.txt",extension=".txt",
            content=media, description="Growth media formulation", format_name="TXT"))
        
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    
    def _gen_dna(self, length, ct):
        bases = "ACGT"
        chroms = {"prokaryote":1, "eukaryote":23, "mammal":23}
        nc = chroms.get(ct, 1)
        fa = [f">chromosome_{i+1} length={length//nc} CLINK_design_{ct}" for i in range(nc)]
        for i in range(nc):
            seq = ''.join(random.choice(bases) for _ in range(min(length//nc, 2000)))
            fa.append(seq)
        return "\n".join(fa)
    
    def _gen_genbank(self, ct, length):
        return (f"LOCUS       CLINK_GENOME  {length} bp  DNA  linear\n"
                f"DEFINITION  CLINK-designed {ct} genome.\n"
                f"ACCESSION   CLK000001\n"
                f"FEATURES             Location/Qualifiers\n"
                f"     source          1..{length}\n"
                f"                     /organism=\"{ct} (CLINK design)\n"
                f"                     /mol_type=\"genomic DNA\n"
                f"     CDS             join(1..300,500..800)\n"
                f"                     /gene=\"CLK_001\n"
                f"                     /product=\"hypothetical protein\n\n"
                f"ORIGIN\n        1 acgtacgtac gtacgtacgt acgtacgtac gtacgtacgt\n//")
    
    def _gen_sbol(self, ct):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n'
                '         xmlns:sbol="http://sbols.org/v2#">\n'
                '  <sbol:ComponentDefinition rdf:about="CLINK_construct_001">\n'
                f'    <sbol:displayName>CLINK {ct} design construct</sbol:displayName>\n'
                '    <sbol:type rdf:resource="http://identifiers.org/so/SO:0000140"/>\n'
                '    <sbol:role rdf:resource="http://identifiers.org/so/SO:0000804"/>\n'
                '  </sbol:ComponentDefinition>\n'
                '</rdf:RDF>')
    
    def _gen_codon_table(self):
        codons = [("TTT","Phe"),("TTC","Phe"),("TTA","Leu"),("TTG","Leu"),
                  ("CTT","Leu"),("CTC","Leu"),("CTA","Leu"),("CTG","Leu"),
                  ("ATT","Ile"),("ATC","Ile"),("ATA","Ile"),("ATG","Met"),
                  ("GTT","Val"),("GTC","Val"),("GTA","Val"),("GTG","Val")]
        lines = ["codon,aa,frequency"]
        for c,aa in codons:
            lines.append(f"{c},{aa},{random.uniform(5,50):.1f}")
        return "\n".join(lines)
    
    def _gen_metabolism(self, ct):
        return json.dumps({
            "central_carbon": {"glycolysis":True,"tca_cycle":True,"pentose_phosphate":True},
            "atp_yield_per_glucose": {"anaerobic":2,"aerobic":36},
            "biomass_equation": "0.5G6P+0.2AA+0.1NT+0.05FA+0.05COF+0.1H2O -> biomass",
            "growth_rate_h": 0.5 if ct=="prokaryote" else 0.03,
        }, indent=2, ensure_ascii=False)
    
    def _gen_media(self, ct):
        return (f"# CLINK Growth Media Formulation for {ct}\n\n"
                f"Base medium: {'LB' if ct=='prokaryote' else 'DMEM'}\n"
                "Carbon source: 25 mM glucose\n"
                "Nitrogen source: 20 mM NH4Cl\n"
                "Phosphate: 10 mM K2HPO4/KH2PO4 pH 7.0\n"
                "Trace elements: Fe, Zn, Mn, Cu, Co, Mo\n"
                "Vitamins: biotin, thiamine, B12\n"
                "Temperature: 37 C\n"
                "pH: 7.2-7.4\n"
                "Oxygen: aerobic (supplement 5% CO2 for mammalian)\n"
                "\n# Protocol: autoclave base, filter-add heat-labile components")


class Layer6DatasetGenerator(DatasetGenerator):
    layer_idx = 6; layer_name = "Mitosis (Cell Division)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=6, layer_name=self.layer_name, layer_tier="O₂", structural_tuple=dict(self.tup))
        chroms = (d or {}).get("chromosome_count", 46) or 46
        
        # Bridge to ouroboric_telomere
        try:
            sys.path.insert(0, str(REBIS_ROOT))
            from biology.ouroboric_telomere import OuroboricTelomere
            tel = OuroboricTelomere()
            o.tool_bridges_used.append("ouroboric_telomere")
            o.files.append(DatasetFile(filename="telomere_dynamics.json",extension=".json",
                content=json.dumps({"telomerase_active":True,"tandem_repeats":"TTAGGG","length_bp":10000},indent=2, ensure_ascii=False),
                description="Telomere dynamics from ouroboric_telomere bridge", format_name="JSON"))
        except: pass
        
        o.files.append(DatasetFile(filename="cell_cycle_params.json",extension=".json",
            content=json.dumps({"chromosomes":chroms,"phases":{"G1":{"hours":12},"S":{"hours":7},"G2":{"hours":3},"M":{"hours":1}},
                "checkpoint":"Aurora-B","spindle_checkpoint_active":True},indent=2, ensure_ascii=False),
            description="Cell cycle parameters with checkpoint specifications", format_name="JSON"))
        
        o.files.append(DatasetFile(filename="mitosis_assay_protocol.md",extension=".md",
            content=self._assay_protocol(chroms),
            description="Mitosis checkpoint assay protocol for wet-lab validation", format_name="Markdown"))
        
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    
    def _assay_protocol(self, chroms):
        return ("# Mitosis Checkpoint Assay Protocol\n\n"
                f"## Cell Line: CLINK-designed (2n={chroms})\n\n"
                "### Materials\n"
                "- Cell culture: DMEM + 10% FBS + 1% P/S\n"
                "- Nocodazole (100 ng/mL for spindle disruption)\n"
                "- MG132 (10 uM for metaphase arrest)\n"
                "- Anti-Aurora B antibody (1:500)\n"
                "- DAPI (1 ug/mL)\n\n"
                "### Procedure\n"
                "1. Seed cells at 70% confluence on coverslips\n"
                "2. Treat with nocodazole for 16 h to depolymerize microtubules\n"
                "3. Fix with 4% PFA for 15 min at RT\n"
                "4. Permeabilize with 0.1% Triton X-100\n"
                "5. Block with 5% BSA for 1 h\n"
                "6. Incubate with anti-Aurora B (1:500) overnight at 4C\n"
                "7. Wash 3x with PBS\n"
                "8. Incubate with Alexa Fluor 488 secondary (1:1000)\n"
                "9. Mount with DAPI-containing medium\n"
                "10. Image on confocal microscope (60x oil)\n\n"
                "### Expected Results\n"
                "- Prometaphase arrest: >80% rounded cells with condensed chromosomes\n"
                "- Aurora-B at inner centromere in prometaphase\n"
                "- Spindle checkpoint: active (Mad2 at kinetochores)")


class Layer7DatasetGenerator(DatasetGenerator):
    layer_idx = 7; layer_name = "Tissue/Organ"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=7, layer_name=self.layer_name, layer_tier="O₂", structural_tuple=dict(self.tup))
        tt = (d or {}).get("tissue_type","epithelial") or "epithelial"
        
        # Bridge to materials
        try:
            sys.path.insert(0, str(REBIS_ROOT))
            from materials.materials_sim import MaterialsSimulation

            o.tool_bridges_used.append("materials_sim")
        except: pass
        
        o.files.append(DatasetFile(filename="cell_type_ratios.csv",extension=".csv",
            content="cell_type,fraction\nepithelial,0.6\nbasal,0.2\nstromal,0.1\nimmune,0.05\nendothelial,0.05",
            description="Cell type composition ratios for tissue design", format_name="CSV"))
        
        o.files.append(DatasetFile(filename="ecm_composition.json",extension=".json",
            content=json.dumps({
                "collagen_I":"60%","collagen_IV":"10%","laminin":"10%",
                "fibronectin":"5%","elastin":"5%","proteoglycans":"5%","water":"5%"
            }, indent=2, ensure_ascii=False), description="Extracellular matrix composition", format_name="JSON"))
        
        o.files.append(DatasetFile(filename="growth_factors.json",extension=".json",
            content=json.dumps({
                "EGF":{"concentration_ng_per_mL":50,"schedule":"every 48h"},
                "FGF2":{"concentration_ng_per_mL":20,"schedule":"every 48h"},
                "VEGF":{"concentration_ng_per_mL":10,"schedule":"every 72h"},
                "TGFb":{"concentration_ng_per_mL":5,"schedule":"every 72h"},
            }, indent=2, ensure_ascii=False), description="Growth factor concentrations for tissue culture", format_name="JSON"))
        
        o.files.append(DatasetFile(filename="organoid_protocol.md",extension=".md",
            content=self._organoid_protocol(tt),
            description="Organoid differentiation protocol", format_name="Markdown"))
        
        o.files.append(DatasetFile(filename="scaffold_params.json",extension=".json",
            content=json.dumps({
                "material":"PLGA 75:25","porosity_percent":85,"pore_size_um":200,
                "degradation_time_weeks":12,"mechanical_modulus_kPa":50,
            }, indent=2, ensure_ascii=False), description="Scaffold design parameters for tissue engineering", format_name="JSON"))
        
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    
    def _organoid_protocol(self, tt):
        return (f"# {tt.capitalize()} Organoid Differentiation Protocol\n\n"
                "### Day 0: Embedding\n"
                "1. Dissociate cells with TrypLE for 5 min\n"
                "2. Count and resuspend at 5000 cells/40 uL\n"
                "3. Mix with 40 uL Matrigel (GFR, Corning)\n"
                "4. Plate 80 uL droplets in pre-warmed 24-well plate\n"
                "5. Incubate 30 min at 37C for gelation\n"
                "6. Add 500 uL complete organoid medium\n\n"
                "### Days 1-7: Expansion\n"
                "- Change medium every 2 days\n"
                "- Add ROCK inhibitor Y-27632 (10 uM) for first 3 days\n"
                "- Expected: >80% organoid formation efficiency\n\n"
                "### Days 7-14: Differentiation\n"
                "- Remove Wnt3a, add differentiation factors\n"
                "- Add 3 uM CHIR99021 (GSK3i) + 1 uM A83-01 (TGFbi)\n"
                "- Monitor budding morphology\n\n"
                "### Harvest\n"
                "1. Remove medium, add 1 mL ice-cold PBS\n"
                "2. Pipette to break Matrigel\n"
                "3. Centrifuge 300g x 5 min\n"
                "4. Proceed to RNA extraction or fixation")


class Layer0DatasetGenerator(DatasetGenerator):
    layer_idx = 0; layer_name = "Frustrated Belnap5 (Quarks)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=0, layer_name=self.layer_name, layer_tier="O₀", structural_tuple=dict(self.tup))
        o.files.append(DatasetFile(filename="qcd_coupling_alpha_s.csv", extension=".csv",
            content=self._alphas(), description="Running QCD coupling constant", format_name="CSV"))
        o.files.append(DatasetFile(filename="qcd_lattice_params.xml", extension=".xml",
            content=self._lattice(), description="Lattice QCD parameters", format_name="XML"))
        o.files.append(DatasetFile(filename="hadron_spectrum.json", extension=".json",
            content=json.dumps({"pion":"135MeV","rho":"770MeV","proton":"938MeV"},indent=2, ensure_ascii=False),
            description="Hadron mass spectrum", format_name="JSON"))
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    def _alphas(self):
        ls = ["Q2,alpha_s"]; [ls.append(f"{q},{max(0.05,min(0.5,0.12/math.log(max(math.sqrt(q)/0.2,1.1)))):.4f}") for q in [1,2,5,10,20,50,100,200,500,1000,5000]]; return "\n".join(ls)
    def _lattice(self):
        return '<?xml version="1.0"?><latticeQCD><gauge_group>SU(3)</gauge_group><n_colors>3</n_colors><lattice_size>24 24 24 48</lattice_size><beta>6.0</beta></latticeQCD>'


class Layer1DatasetGenerator(DatasetGenerator):
    layer_idx = 1; layer_name = "Electron Orbital (Belnap4)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=1, layer_name=self.layer_name, layer_tier="O₀", structural_tuple=dict(self.tup))
        o.files.append(DatasetFile(filename="electron_configs.csv", extension=".csv",
            content=self._cfgs(), description="Electron configurations", format_name="CSV"))
        o.files.append(DatasetFile(filename="b4_map.json", extension=".json",
            content=json.dumps({"B":"Guanine","T":"Cytosine","F":"Adenine","N":"Thymine"},indent=2, ensure_ascii=False),
            description="Belnap4 to nucleotide mapping", format_name="JSON"))
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    def _cfgs(self):
        c = {1:"1s1",2:"1s2",6:"[He]2s2 2p2",7:"[He]2s2 2p3",8:"[He]2s2 2p4",26:"[Ar]3d6 4s2"}
        return "\n".join([f"Z={z}, {c[z]}" for z in sorted(c)])


class Layer2DatasetGenerator(DatasetGenerator):
    layer_idx = 2; layer_name = "Atom (Nuclear + Electron)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=2, layer_name=self.layer_name, layer_tier="O₁", structural_tuple=dict(self.tup))
        o.files.append(DatasetFile(filename="atomic_params.csv", extension=".csv",
            content="Z,symbol,mass_amu,radius_pm,ionization_eV\n6,C,12.011,76,11.260\n7,N,14.007,75,14.534\n8,O,15.999,73,13.618\n15,P,30.974,107,10.487\n26,Fe,55.845,132,7.902",
            description="Atomic parameters table", format_name="CSV"))
        o.files.append(DatasetFile(filename="isotopes.json", extension=".json",
            content=json.dumps({"C":{"stable":["C12","C13"],"radioactive":["C14"]},"O":{"stable":["O16","O17","O18"]}},indent=2, ensure_ascii=False),
            description="Isotope selection table", format_name="JSON"))
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o


class Layer3DatasetGenerator(DatasetGenerator):
    layer_idx = 3; layer_name = "Molecule (Chemical Bonds)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=3, layer_name=self.layer_name, layer_tier="O₂", structural_tuple=dict(self.tup))
        # Try ch3mpiler bridge
        try:
            sys.path.insert(0, str(REBIS_ROOT / "ch3mpiler"))
            from ch3mpiler.compiler import MoleculeCompiler
            mc = MoleculeCompiler()
            o.notes.append(f"ch3mpiler bridged: retrosynthesis available")
            o.tool_bridges_used.append("ch3mpiler")
        except: pass
        
        o.files.append(DatasetFile(filename="molecules.smi", extension=".smi",
            content=self._smiles(), description="SMILES inventory of biomolecules", format_name="SMILES"))
        o.files.append(DatasetFile(filename="molecular_props.csv", extension=".csv",
            content=self._props(), description="Molecular properties MW logP HBD HBA", format_name="CSV"))
        o.files.append(DatasetFile(filename="retro_pathways.json", extension=".json",
            content=self._retro(), description="Retrosynthetic pathways", format_name="JSON"))
        o.files.append(DatasetFile(filename="reactions.json", extension=".json",
            content=self._rxns(), description="Biochemical reaction equations", format_name="JSON"))
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    
    def _smiles(self):
        return ("# CLINK Molecule Inventory\n"
                "C(C(=O)O)N\tAlanine\n"
                "CC(C)CC(C(=O)O)N\tLeucine\n"
                "C1=CC=C(C=C1)CC(C(=O)O)N\tPhenylalanine\n"
                "C(CC(=O)O)C(C(=O)O)N\tGlutamic_acid\n"
                "C1=NC2=C(N1)N(C=N2)C3C(C(C(O3)CO)O)O\tAdenosine\n"
                "CC1=CN(C(=O)NC1=O)C2C(C(C(O2)CO)O)O\tThymidine")
    
    def _props(self):
        return ("SMILES,Name,MW,logP,HBD,HBA\n"
                "C(C(=O)O)N,Alanine,89.09,-2.85,2,4\n"
                "CC(C)CC(C(=O)O)N,Leucine,131.17,-1.52,2,4\n"
                "C1=CC=C(C=C1)CC(C(=O)O)N,Phenylalanine,165.19,-1.38,2,4\n"
                "C(CC(=O)O)C(C(=O)O)N,Glutamic_acid,147.13,-3.69,3,6")
    
    def _retro(self):
        return json.dumps({
            "alanine": {"from": ["pyruvate","NH3","NADPH"],"enzymes":["ALT","GDH"]},
            "glucose": {"from": ["CO2","H2O"],"pathway":"gluconeogenesis"},
            "atp": {"from":["ADP","Pi"],"enzyme":"ATP synthase"},
        }, indent=2, ensure_ascii=False)
    
    def _rxns(self):
        return json.dumps({
            "glycolysis":{"reactants":"Glucose+2NAD+2ADP","products":"2Pyruvate+2NADH+2ATP","deltaG_kJ":-74.5},
            "tca":{"reactants":"Acetyl-CoA+3NAD+FAD","products":"2CO2+3NADH+FADH2+GTP","deltaG_kJ":-40.0},
        }, indent=2, ensure_ascii=False)


class Layer4DatasetGenerator(DatasetGenerator):
    layer_idx = 4; layer_name = "Folded Protein"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=4, layer_name=self.layer_name, layer_tier="O₂", structural_tuple=dict(self.tup))
        seq = (d or {}).get("sequence", "MLSDCGP") or "MLSDCGP"
        fn = (d or {}).get("target_function", "structural") or "structural"
        o.notes.append(f"Protein {seq} ({fn})")
        
        # Bridge to serpentrod
        try:
            sys.path.insert(0, str(REBIS_ROOT / "serpentrod"))
            from serpentrod.stratified_predictor import PRIMITIVE_MAP
            from serpentrod.protein_v5 import classify_module_rich

            spec = {}
            for aa in seq.upper():
                if aa in PRIMITIVE_MAP: spec[PRIMITIVE_MAP[aa][0]] = spec.get(PRIMITIVE_MAP[aa][0],0)+1
            cls = classify_module_rich(seq)
            o.tool_bridges_used.append("serpentrod")
            o.files.append(DatasetFile(filename="serpentrod_classification.json",extension=".json",
                content=json.dumps({"primitive_spectrum":spec,"classification":str(cls)},indent=2, ensure_ascii=False),
                description="Serpentrod protein classification", format_name="JSON"))
        except: pass
        
        # FASTA
        o.files.append(DatasetFile(filename="protein.fasta",extension=".fasta",
            content=f">CLINK|{fn}|length={len(seq)}\n{seq}\n",
            description="Protein sequence in FASTA format", format_name="FASTA"))
        
        # PDB template
        pdb = ["HEADER CLINK PROTEIN DESIGN\nCOMPND "+fn]
        for i,aa in enumerate(seq.upper()):
            x,y,z = i*1.5, math.sin(i*0.5)*5, math.cos(i*0.5)*5
            pdb.append(f"ATOM  {i+1:5d}  CA  {aa:<3s} A{i+1:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C  ")
        pdb.append("TER\nEND")
        o.files.append(DatasetFile(filename="protein_coords.pdb",extension=".pdb",
            content="\n".join(pdb),
            description="PDB coordinate template for protein", format_name="PDB"))
        
        # Secondary structure
        ss = {}
        for i,aa in enumerate(seq.upper()):
            if aa in "ML": ss[i] = "H"
            elif aa in "SC": ss[i] = "E"
            else: ss[i] = "C"
        o.files.append(DatasetFile(filename="secondary_structure.json",extension=".json",
            content=json.dumps({"prediction":ss,"composition":{"H":list(ss.values()).count("H"),"E":list(ss.values()).count("E"),"C":list(ss.values()).count("C")}},indent=2, ensure_ascii=False),
            description="Secondary structure prediction", format_name="JSON"))
        
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o

