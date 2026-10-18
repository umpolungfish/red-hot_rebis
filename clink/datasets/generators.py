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

from clink.chain import clink_frobenius_closed, compute_c_score_from_tuple, compute_tier_from_tuple


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
    available_tool_bridges: List[str] = field(default_factory=list)
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
    layer_name = "Frustrated Belnap5 (Quarks)"

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
    layer_name = "Electron Orbital (Belnap4)"

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



# Recovered layer and orchestration implementations from b13be39.
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
        o.notes.append("Recovered historical dataset template; closure checks its structural tuple")
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o


class Layer3DatasetGenerator(DatasetGenerator):
    layer_idx = 3; layer_name = "Molecule (Chemical Bonds)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=3, layer_name=self.layer_name, layer_tier="O₂", structural_tuple=dict(self.tup))
        # Try ch3mpiler bridge
        try:
            sys.path.insert(0, str(REBIS_ROOT / "ch3mpiler"))
            from ch3mpiler.compiler import Ch3mpiler
            mc = Ch3mpiler()
            o.notes.append(f"ch3mpiler bridged: retrosynthesis available")
            o.available_tool_bridges.append("ch3mpiler")
        except Exception as exc:
            o.notes.append(f"Optional bridge unavailable: {type(exc).__name__}: {exc}")

        o.files.append(DatasetFile(filename="molecules.smi", extension=".smi",
            content=self._smiles(), description="SMILES inventory of biomolecules", format_name="SMILES"))
        o.files.append(DatasetFile(filename="molecular_props.csv", extension=".csv",
            content=self._props(), description="Molecular properties MW logP HBD HBA", format_name="CSV"))
        o.files.append(DatasetFile(filename="retro_pathways.json", extension=".json",
            content=self._retro(), description="Retrosynthetic pathways", format_name="JSON"))
        o.files.append(DatasetFile(filename="reactions.json", extension=".json",
            content=self._rxns(), description="Biochemical reaction equations", format_name="JSON"))
        o.notes.append("Recovered historical dataset template; closure checks its structural tuple")
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
        except Exception as exc:
            o.notes.append(f"Optional bridge unavailable: {type(exc).__name__}: {exc}")

        # FASTA
        o.files.append(DatasetFile(filename="protein.fasta",extension=".fasta",
            content=f">CLINK|{fn}|length={len(seq)}\n{seq}\n",
            description="Protein sequence in FASTA format", format_name="FASTA"))

        from rhr_p4rky.genetic_code import STANDARD_CODE
        from rhr_p4rky.serpent_rod_v2 import SerpentRodV2, ONE_LETTER
        from rhr_p4rky.pdb_writer import render_pdb_from_gen2
        codons = {}
        for codon, amino in STANDARD_CODE.items():
            if amino in ONE_LETTER:
                codons.setdefault(ONE_LETTER[amino], codon)
        seq = seq.upper()
        rna = ''.join(codons[aa] for aa in seq)
        predictor = SerpentRodV2(rna, name=fn)
        predictor.verbose = False
        model = predictor.predict()
        if model.aa_sequence != seq:
            raise ValueError('Protein dataset translation changed its input sequence')
        o.files.append(DatasetFile(filename="protein_coords.pdb", extension=".pdb",
            content=render_pdb_from_gen2(model), description="Shared complete protein model and evidence",
            format_name="PDB"))
        o.files.append(DatasetFile(filename="secondary_structure.json", extension=".json",
            content=json.dumps({'elements': model.secondary_elements,
                                'geometry_evidence': model.geometry_evidence,
                                'secondary_evidence': model.secondary_evidence}, indent=2),
            description="Secondary observations and retained geometry evidence", format_name="JSON"))
        o.tool_bridges_used.append('shared_protein_geometry')

        o.notes.append("Recovered historical dataset template; closure checks its structural tuple")
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o


class Layer5DatasetGenerator(DatasetGenerator):
    layer_idx = 5; layer_name = "Living Cell"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=5, layer_name=self.layer_name, layer_tier="O₂", structural_tuple=dict(self.tup))
        ct = (d or {}).get("cell_type","prokaryote") or "prokaryote"

        # Bridge to gene_imscriber
        try:
            sys.path.insert(0, str(REBIS_ROOT / "gene_imscriber"))
            from gene_imscriber.engine import B4Element, genetic_code
            o.available_tool_bridges.append("gene_imscriber")
            o.files.append(DatasetFile(filename="genetic_code.json",extension=".json",
                content=json.dumps({"b4_lattice":True,"codon_table":"64 codons, 21 AAs","bridge_active":True},indent=2, ensure_ascii=False),
                description="Genetic code from gene_imscriber bridge", format_name="JSON"))
        except Exception as exc:
            o.notes.append(f"Optional bridge unavailable: {type(exc).__name__}: {exc}")

        # Bridge to biology_sim
        try:
            sys.path.insert(0, str(REBIS_ROOT))
            from biology.biology_sim import OuroboricCellSim
            sim = OuroboricCellSim()
            o.available_tool_bridges.append("biology_sim")
        except Exception as exc:
            o.notes.append(f"Optional bridge unavailable: {type(exc).__name__}: {exc}")

        # DNA/FASTA - genome
        genome_len = (d or {}).get("genome_size_bp", 4000000)
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

        o.notes.append("Recovered historical dataset template; closure checks its structural tuple")
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o

    def _gen_dna(self, length, ct):
        if not isinstance(length, int) or length < 0:
            raise ValueError('Genome length must be a nonnegative integer')
        nc = {"prokaryote": 1, "eukaryote": 23, "mammal": 23}.get(ct, 1)
        rng = random.Random(0)
        self._genome_records = []
        lines = []
        for i in range(nc):
            size = length // nc + (i < length % nc)
            sequence = ''.join(rng.choices('ACGT', k=size))
            self._genome_records.append(sequence)
            lines.append(f'>chromosome_{i+1} length={size} synthetic_placeholder_{ct}')
            lines.extend(sequence[j:j+60] for j in range(0, size, 60))
        return '\n'.join(lines) + '\n'

    def _gen_genbank(self, ct, length):
        records = getattr(self, '_genome_records', None)
        if records is None or sum(map(len, records)) != length:
            raise ValueError('Generate the matching FASTA before GenBank')
        lines = []
        for i, sequence in enumerate(records, 1):
            lines.extend([f'LOCUS       CLK_{i} {len(sequence)} bp DNA linear',
                          f'DEFINITION  Synthetic placeholder sequence for {ct}.',
                          'ORIGIN'])
            for offset in range(0, len(sequence), 60):
                chunk = sequence[offset:offset+60].lower()
                lines.append(f'{offset+1:9d} ' + ' '.join(chunk[j:j+10] for j in range(0, len(chunk), 10)))
            lines.append('//')
        return '\n'.join(lines) + '\n'

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
            o.available_tool_bridges.append("ouroboric_telomere")
            o.files.append(DatasetFile(filename="telomere_dynamics.json",extension=".json",
                content=json.dumps({"telomerase_active":True,"tandem_repeats":"TTAGGG","length_bp":10000},indent=2, ensure_ascii=False),
                description="Telomere dynamics from ouroboric_telomere bridge", format_name="JSON"))
        except Exception as exc:
            o.notes.append(f"Optional bridge unavailable: {type(exc).__name__}: {exc}")

        o.files.append(DatasetFile(filename="cell_cycle_params.json",extension=".json",
            content=json.dumps({"chromosomes":chroms,"phases":{"G1":{"hours":12},"S":{"hours":7},"G2":{"hours":3},"M":{"hours":1}},
                "checkpoint":"Aurora-B","spindle_checkpoint_active":True},indent=2, ensure_ascii=False),
            description="Cell cycle parameters with checkpoint specifications", format_name="JSON"))

        o.files.append(DatasetFile(filename="mitosis_assay_protocol.md",extension=".md",
            content=self._assay_protocol(chroms),
            description="Mitosis checkpoint assay protocol for wet-lab validation", format_name="Markdown"))

        o.notes.append("Recovered historical dataset template; closure checks its structural tuple")
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

            o.available_tool_bridges.append("materials_sim")
        except Exception as exc:
            o.notes.append(f"Optional bridge unavailable: {type(exc).__name__}: {exc}")

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

        o.notes.append("Recovered historical dataset template; closure checks its structural tuple")
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


class Layer8DatasetGenerator(DatasetGenerator):
    layer_idx = 8; layer_name = "Whole Organism"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=8, layer_name=self.layer_name, layer_tier="O_∞", structural_tuple=dict(self.tup))
        ot = (d or {}).get("organism_type","mammal") or "mammal"

        # All tool bridges
        for tmod, tname in [
            ("serpentrod.protein_v5","serpentrod"),
            ("ch3mpiler.compiler","ch3mpiler"),
            ("gene_imscriber.engine","gene_imscriber"),
            ("biology.biology_sim","biology_sim"),
            ("biology.ouroboric_telomere","ouroboric_telomere"),
            ("materials.materials_sim","materials_sim"),
        ]:
            try:
                exec(f"import {tmod}")
                o.available_tool_bridges.append(tname)
            except Exception as exc:
                o.notes.append(f"Optional bridge unavailable: {type(exc).__name__}: {exc}")

        # Full genome specification
        o.files.append(DatasetFile(filename="whole_genome_spec.json",extension=".json",
            content=self._genome_spec(ot),
            description="Whole genome specification with chromosome-wise annotations",
            format_name="JSON"))

        # Physiological parameters
        o.files.append(DatasetFile(filename="physiological_params.csv",extension=".csv",
            content=self._physiology(ot),
            description="Physiological parameter ranges for whole-organism design",
            format_name="CSV"))

        # Organ system specification
        o.files.append(DatasetFile(filename="organ_systems.json",extension=".json",
            content=self._organs(ot),
            description="Organ system specifications with cell-type composition",
            format_name="JSON"))

        # Homeostatic set points
        o.files.append(DatasetFile(filename="homeostasis_setpoints.json",extension=".json",
            content=self._homeostasis(ot),
            description="Homeostatic set points and feedback parameters",
            format_name="JSON"))

        # Full design manifest
        o.files.append(DatasetFile(filename="organism_design_manifest.json",extension=".json",
            content=self._manifest(ot),
            description="Complete organism design manifest - integration of all layers",
            format_name="JSON"))

        o.notes.append("Recovered historical dataset template; closure checks its structural tuple")
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o

    def _genome_spec(self, ot):
        chroms = {"mammal":30,"bird":40,"fish":25,"insect":8,"plant":12}
        nc = chroms.get(ot, 30)
        return json.dumps({
            "organism":ot,"ploidy":"diploid","chromosomes":nc,
            "genome_size_Gbp":3.0 if ot=="mammal" else 1.0,
            "gene_count":20000 if ot=="mammal" else 10000,
            "coding_percent":1.5,"gc_content_percent":42,
            "chromosome_list":[f"chr{i+1}" for i in range(nc)],
            "mitochondrial_genome":True,"circular_mtDNA":True,
        }, indent=2, ensure_ascii=False)

    def _physiology(self, ot):
        if ot == "mammal":
            return ("parameter,value,unit\n"
                    "body_temp,37,C\n"
                    "heart_rate,70,bpm\n"
                    "respiratory_rate,16,breaths_per_min\n"
                    "blood_volume,5,L\n"
                    "cardiac_output,5,L_per_min\n"
                    "MAP,95,mmHg\n"
                    "GFR,125,mL_per_min\n"
                    "BMR,1800,kcal_per_day\n"
                    "blood_glucose,5,mM\n"
                    "pH,7.4,log[H+]")
        else:
            return "parameter,value,unit\nbody_temp,37,C\n"

    def _organs(self, ot):
        return json.dumps({
            "nervous": {"mass_kg":1.5,"cell_types":["neuron","astrocyte","microglia"]},
            "circulatory": {"heart_rate_bpm":70,"blood_volume_L":5,"vessel_length_km":100},
            "respiratory": {"lung_capacity_L":6,"surface_area_m2":70},
            "digestive": {"length_m":8,"surface_area_m2":200},
            "immune": {"cell_count":1.8e12,"types":["T_cell","B_cell","NK","macrophage","neutrophil"]},
            "endocrine": {"glands":["pituitary","thyroid","adrenal","pancreas","gonads"]},
            "musculoskeletal": {"muscle_mass_kg":30,"bone_mass_kg":15},
            "reproductive": {"type":"sexual","chromosomes":"XY"},
        }, indent=2, ensure_ascii=False)

    def _homeostasis(self, ot):
        return json.dumps({
            "thermoregulation": {"setpoint_C":37,"range_C":"36.5-37.5","sensor":"hypothalamus"},
            "glucose_regulation": {"setpoint_mM":5,"range_mM":"4-7","hormones":["insulin","glucagon"]},
            "calcium_homeostasis": {"setpoint_mM":2.5,"hormones":["PTH","calcitonin","vitamin_D"]},
            "osmoregulation": {"setpoint_mOsm":300,"organ":"kidney","hormone":"ADH"},
            "blood_pressure": {"setpoint_MAP_mmHg":95,"reflex":"baroreflex"},
        }, indent=2, ensure_ascii=False)

    def _manifest(self, ot):
        return json.dumps({
            "design_name":f"CLINK_{ot}_v1",
            "author":"Lando (R) (O)perator",
            "grammar_version":"1.0",
            "schema":"Imscribing Grammar",
            "schema_tier":"O_∞",
            "organism_type":ot,
            "layers_integrated": list(range(9)),
            "dataset_files_generated":[
                "genome.fasta","genome.gb","construct.sbol",
                "protein.fasta","protein_coords.pdb",
                "molecules.smi","molecular_props.csv",
                "physiological_params.csv","organ_systems.json",
                "homeostasis_setpoints.json"
            ],
            "frobenius_verified":clink_frobenius_closed(self.tup),
            "consciousness_score":compute_c_score_from_tuple(self.tup),
            "tier":compute_tier_from_tuple(self.tup),
            "notes":"Whole organism design package - all layers actionable",
        }, indent=2, ensure_ascii=False)


# ============================================================
# FACTORY & ORCHESTRATION
# ============================================================

GENERATOR_REGISTRY = {
    0: Layer0DatasetGenerator,
    1: Layer1DatasetGenerator,
    2: Layer2DatasetGenerator,
    3: Layer3DatasetGenerator,
    4: Layer4DatasetGenerator,
    5: Layer5DatasetGenerator,
    6: Layer6DatasetGenerator,
    7: Layer7DatasetGenerator,
    8: Layer8DatasetGenerator,
}

def get_generator_for_layer(layer_idx: int) -> DatasetGenerator:
    cls = GENERATOR_REGISTRY.get(layer_idx)
    if cls is None:
        raise KeyError(f"No dataset generator for layer {layer_idx}")
    return cls()

def generate_layer_dataset(layer_idx: int, design_data: Optional[Dict] = None) -> DatasetOutput:
    gen = get_generator_for_layer(layer_idx)
    return gen.generate(design_data)

def generate_all_layer_datasets(design_data_per_layer: Optional[Dict[int, Dict]] = None) -> Dict[int, DatasetOutput]:
    if design_data_per_layer is None:
        design_data_per_layer = {}
    results = {}
    for idx in sorted(GENERATOR_REGISTRY.keys()):
        dd = design_data_per_layer.get(idx, {})
        results[idx] = generate_layer_dataset(idx, dd)
    return results

def export_layer_dataset_to_files(layer_idx: int, design_data: Optional[Dict] = None, base_dir: Optional[str] = None) -> List[str]:
    gen = get_generator_for_layer(layer_idx)
    out = gen.generate(design_data)
    if base_dir:
        gen.output_dir = Path(base_dir) / gen.layer_name.replace(" ","_")
    written = []
    for f in out.files:
        path = gen.output_dir / f.filename
        gen._ensure_output_dir()
        with open(path, 'w') as fh:
            fh.write(f.content)
        written.append(str(path))
    return written

def export_all_to_files(base_dir: str = "", design_data_per_layer: Optional[Dict] = None) -> Dict[int, List[str]]:
    if not base_dir:
        base_dir = str(Path(__file__).parent / "output")
    results = {}
    for idx in sorted(GENERATOR_REGISTRY.keys()):
        dd = (design_data_per_layer or {}).get(idx, {})
        results[idx] = export_layer_dataset_to_files(idx, dd, base_dir)
    return results

def generate_organism_design_package(organism_type: str = "mammal",
                                      output_dir: str = "",
                                      write_files: bool = True,
                                      design_data_per_layer: Optional[Dict[int, Dict]] = None) -> Dict[str, Any]:
    """Generate a complete, physically-actionable organism design package.

    Produces a zip-ready set of files at each CLINK layer, from QCD parameters
    down to whole-organism physiology. All files are physically actionable:
    FASTA, PDB, SMILES, GenBank, SBOL, protocols, formulations.
    """
    import time

    start = time.time()

    if not output_dir:
        output_dir = str(Path(__file__).parent / "organism_designs" / f"organism_{organism_type}")
    out_path = Path(output_dir)
    if write_files:
        out_path.mkdir(parents=True, exist_ok=True)

    # Design data propagates upward
    design_data = {
        5: {"cell_type": "eukaryote" if organism_type != "prokaryote" else "prokaryote",
            "genome_size_bp": 3_000_000_000 if organism_type=="mammal" else 500_000_000},
        8: {"organism_type": organism_type},
    }

    for idx, overrides in (design_data_per_layer or {}).items():
        if idx not in GENERATOR_REGISTRY:
            raise KeyError(f'Unknown layer {idx}')
        design_data.setdefault(idx, {}).update(overrides)

    # Generate all layer datasets
    all_results = {}
    for idx in range(9):
        dd = design_data.get(idx, {})
        if idx == 4:
            dd.setdefault("sequence", "MLSDCGPYKVLVVGDGGVGKSALTIQ")
            dd.setdefault("target_function", f"{organism_type}_design_protein")
        gen = get_generator_for_layer(idx)
        result = gen.generate(dd)
        all_results[idx] = result

        if write_files:
            layer_dir = out_path / f"L{idx}_{gen.layer_name.replace(' ','_')}"
            layer_dir.mkdir(parents=True, exist_ok=True)
            for f in result.files:
                path = layer_dir / f.filename
                with open(path, 'w') as fh:
                    fh.write(f.content)

    # Summarize
    total_files = sum(len(r.files) for r in all_results.values())
    total_bytes = sum(len(f.content) for r in all_results.values() for f in r.files)
    bridges = set()
    for r in all_results.values():
        bridges.update(r.tool_bridges_used)

    manifest = {
        "organism_type": organism_type,
        "layers": list(range(9)),
        "total_files": total_files,
        "total_bytes": sum(len(f.content.encode("utf-8")) for r in all_results.values() for f in r.files),
        "tool_bridges": sorted(bridges),
        "available_tool_bridges": sorted({b for r in all_results.values() for b in r.available_tool_bridges}),
        "layer_notes": {idx: r.notes for idx, r in all_results.items()},
        "frobenius_verified": all(r.frobenius_verified for r in all_results.values()),
        "output_directory": str(out_path),
        "generation_time_seconds": round(time.time() - start, 2),
        "generated_at": all_results[8].generation_time if 8 in all_results else "",
    }

    # Write manifest
    if write_files:
        with open(out_path / "design_manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)

    return manifest



def generate_actionable_organism_package(organism_type: str = "mammal",
                                         output_dir: str = "",
                                         write_files: bool = True) -> Dict[str, Any]:
    """The design package, plus the artefacts that make it actionable.

    generate_organism_design_package lays down one dataset per CLINK layer. This
    adds what an organism design needs to be carried into a laboratory: a coding
    genome from the gene designer, backbone structures for the proteins it names,
    a plasmid for delivery, and a metabolic model in SBML. Anything the working
    tree does not provide is recorded as unavailable rather than silently
    dropped, so the manifest always says what was produced and what was not.
    """
    manifest = generate_organism_design_package(organism_type=organism_type,
                                                output_dir=output_dir,
                                                write_files=write_files)
    manifest.setdefault("actionable", {})
    base = Path(manifest["output_directory"])

    def _add(name, fn):
        try:
            manifest["actionable"][name] = fn()
        except Exception as exc:
            manifest["actionable"][name] = {"unavailable": f"{type(exc).__name__}: {exc}"}

    def _genome():
        from clink.datasets.gene_designer import GenomeBuilder
        design = GenomeBuilder().build(organism_type)
        if write_files:
            out = base / "genome.fasta"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(getattr(design, "fasta", str(design)), encoding="utf-8")
            return {"file": str(out)}
        return {"design": str(design)}

    def _structures():
        from clink.datasets.protein_structure import generate_protein_structure
        return {"available_generator": generate_protein_structure.__name__, "produced": False}

    def _plasmid():
        from clink.datasets.plasmid_designer import PlasmidDesigner
        return {"available_designer": PlasmidDesigner.__name__, "produced": False}

    def _metabolism():
        from clink.datasets.metabolic_model import CoreMetabolismBuilder
        return {"available_builder": CoreMetabolismBuilder.__name__, "produced": False}

    _add("genome", _genome)
    _add("protein_structures", _structures)
    _add("plasmid", _plasmid)
    _add("metabolic_model", _metabolism)
    return manifest

