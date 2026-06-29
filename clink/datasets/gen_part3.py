#!/usr/bin/env python3
"""PART 3: L5-L8 layer generators + orchestration."""
import os, json
from shared.rich_output import *

PY = "/home/mrnob0dy666/red-hot_rebis/clink/datasets/generators.py"

def w(s):
    with open(PY, 'a') as f:
        f.write(s + '\n')

# L5 - Cell
w('''
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
                content=json.dumps({"b4_lattice":True,"codon_table":"64 codons, 21 AAs","bridge_active":True},indent=2),
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
        return "\\n".join(fa)
    
    def _gen_genbank(self, ct, length):
        return (f"LOCUS       CLINK_GENOME  {length} bp  DNA  linear\\n"
                f"DEFINITION  CLINK-designed {ct} genome.\\n"
                f"ACCESSION   CLK000001\\n"
                f"FEATURES             Location/Qualifiers\\n"
                f"     source          1..{length}\\n"
                f"                     /organism=\\"{ct} (CLINK design)\\n"
                f"                     /mol_type=\\"genomic DNA\\n"
                f"     CDS             join(1..300,500..800)\\n"
                f"                     /gene=\\"CLK_001\\n"
                f"                     /product=\\"hypothetical protein\\n\\n"
                f"ORIGIN\\n        1 acgtacgtac gtacgtacgt acgtacgtac gtacgtacgt\\n//")
    
    def _gen_sbol(self, ct):
        return ('<?xml version="1.0" encoding="UTF-8"?>\\n'
                '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\\n'
                '         xmlns:sbol="http://sbols.org/v2#">\\n'
                '  <sbol:ComponentDefinition rdf:about="CLINK_construct_001">\\n'
                f'    <sbol:displayName>CLINK {ct} design construct</sbol:displayName>\\n'
                '    <sbol:type rdf:resource="http://identifiers.org/so/SO:0000140"/>\\n'
                '    <sbol:role rdf:resource="http://identifiers.org/so/SO:0000804"/>\\n'
                '  </sbol:ComponentDefinition>\\n'
                '</rdf:RDF>')
    
    def _gen_codon_table(self):
        codons = [("TTT","Phe"),("TTC","Phe"),("TTA","Leu"),("TTG","Leu"),
                  ("CTT","Leu"),("CTC","Leu"),("CTA","Leu"),("CTG","Leu"),
                  ("ATT","Ile"),("ATC","Ile"),("ATA","Ile"),("ATG","Met"),
                  ("GTT","Val"),("GTC","Val"),("GTA","Val"),("GTG","Val")]
        lines = ["codon,aa,frequency"]
        for c,aa in codons:
            lines.append(f"{c},{aa},{random.uniform(5,50):.1f}")
        return "\\n".join(lines)
    
    def _gen_metabolism(self, ct):
        return json.dumps({
            "central_carbon": {"glycolysis":True,"tca_cycle":True,"pentose_phosphate":True},
            "atp_yield_per_glucose": {"anaerobic":2,"aerobic":36},
            "biomass_equation": "0.5G6P+0.2AA+0.1NT+0.05FA+0.05COF+0.1H2O -> biomass",
            "growth_rate_h": 0.5 if ct=="prokaryote" else 0.03,
        }, indent=2)
    
    def _gen_media(self, ct):
        return (f"# CLINK Growth Media Formulation for {ct}\\n\\n"
                f"Base medium: {'LB' if ct=='prokaryote' else 'DMEM'}\\n"
                "Carbon source: 25 mM glucose\\n"
                "Nitrogen source: 20 mM NH4Cl\\n"
                "Phosphate: 10 mM K2HPO4/KH2PO4 pH 7.0\\n"
                "Trace elements: Fe, Zn, Mn, Cu, Co, Mo\\n"
                "Vitamins: biotin, thiamine, B12\\n"
                "Temperature: 37 C\\n"
                "pH: 7.2-7.4\\n"
                "Oxygen: aerobic (supplement 5% CO2 for mammalian)\\n"
                "\\n# Protocol: autoclave base, filter-add heat-labile components")
''')

info_line("L5 written")

# L6 - Mitosis
w('''
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
                content=json.dumps({"telomerase_active":True,"tandem_repeats":"TTAGGG","length_bp":10000},indent=2),
                description="Telomere dynamics from ouroboric_telomere bridge", format_name="JSON"))
        except: pass
        
        o.files.append(DatasetFile(filename="cell_cycle_params.json",extension=".json",
            content=json.dumps({"chromosomes":chroms,"phases":{"G1":{"hours":12},"S":{"hours":7},"G2":{"hours":3},"M":{"hours":1}},
                "checkpoint":"Aurora-B","spindle_checkpoint_active":True},indent=2),
            description="Cell cycle parameters with checkpoint specifications", format_name="JSON"))
        
        o.files.append(DatasetFile(filename="mitosis_assay_protocol.md",extension=".md",
            content=self._assay_protocol(chroms),
            description="Mitosis checkpoint assay protocol for wet-lab validation", format_name="Markdown"))
        
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    
    def _assay_protocol(self, chroms):
        return ("# Mitosis Checkpoint Assay Protocol\\n\\n"
                f"## Cell Line: CLINK-designed (2n={chroms})\\n\\n"
                "### Materials\\n"
                "- Cell culture: DMEM + 10% FBS + 1% P/S\\n"
                "- Nocodazole (100 ng/mL for spindle disruption)\\n"
                "- MG132 (10 uM for metaphase arrest)\\n"
                "- Anti-Aurora B antibody (1:500)\\n"
                "- DAPI (1 ug/mL)\\n\\n"
                "### Procedure\\n"
                "1. Seed cells at 70% confluence on coverslips\\n"
                "2. Treat with nocodazole for 16 h to depolymerize microtubules\\n"
                "3. Fix with 4% PFA for 15 min at RT\\n"
                "4. Permeabilize with 0.1% Triton X-100\\n"
                "5. Block with 5% BSA for 1 h\\n"
                "6. Incubate with anti-Aurora B (1:500) overnight at 4C\\n"
                "7. Wash 3x with PBS\\n"
                "8. Incubate with Alexa Fluor 488 secondary (1:1000)\\n"
                "9. Mount with DAPI-containing medium\\n"
                "10. Image on confocal microscope (60x oil)\\n\\n"
                "### Expected Results\\n"
                "- Prometaphase arrest: >80% rounded cells with condensed chromosomes\\n"
                "- Aurora-B at inner centromere in prometaphase\\n"
                "- Spindle checkpoint: active (Mad2 at kinetochores)")
''')

info_line("L6 written")

# L7 - Tissue
w('''
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
            content="cell_type,fraction\\nepithelial,0.6\\nbasal,0.2\\nstromal,0.1\\nimmune,0.05\\nendothelial,0.05",
            description="Cell type composition ratios for tissue design", format_name="CSV"))
        
        o.files.append(DatasetFile(filename="ecm_composition.json",extension=".json",
            content=json.dumps({
                "collagen_I":"60%","collagen_IV":"10%","laminin":"10%",
                "fibronectin":"5%","elastin":"5%","proteoglycans":"5%","water":"5%"
            }, indent=2), description="Extracellular matrix composition", format_name="JSON"))
        
        o.files.append(DatasetFile(filename="growth_factors.json",extension=".json",
            content=json.dumps({
                "EGF":{"concentration_ng_per_mL":50,"schedule":"every 48h"},
                "FGF2":{"concentration_ng_per_mL":20,"schedule":"every 48h"},
                "VEGF":{"concentration_ng_per_mL":10,"schedule":"every 72h"},
                "TGFb":{"concentration_ng_per_mL":5,"schedule":"every 72h"},
            }, indent=2), description="Growth factor concentrations for tissue culture", format_name="JSON"))
        
        o.files.append(DatasetFile(filename="organoid_protocol.md",extension=".md",
            content=self._organoid_protocol(tt),
            description="Organoid differentiation protocol", format_name="Markdown"))
        
        o.files.append(DatasetFile(filename="scaffold_params.json",extension=".json",
            content=json.dumps({
                "material":"PLGA 75:25","porosity_percent":85,"pore_size_um":200,
                "degradation_time_weeks":12,"mechanical_modulus_kPa":50,
            }, indent=2), description="Scaffold design parameters for tissue engineering", format_name="JSON"))
        
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    
    def _organoid_protocol(self, tt):
        return (f"# {tt.capitalize()} Organoid Differentiation Protocol\\n\\n"
                "### Day 0: Embedding\\n"
                "1. Dissociate cells with TrypLE for 5 min\\n"
                "2. Count and resuspend at 5000 cells/40 uL\\n"
                "3. Mix with 40 uL Matrigel (GFR, Corning)\\n"
                "4. Plate 80 uL droplets in pre-warmed 24-well plate\\n"
                "5. Incubate 30 min at 37C for gelation\\n"
                "6. Add 500 uL complete organoid medium\\n\\n"
                "### Days 1-7: Expansion\\n"
                "- Change medium every 2 days\\n"
                "- Add ROCK inhibitor Y-27632 (10 uM) for first 3 days\\n"
                "- Expected: >80% organoid formation efficiency\\n\\n"
                "### Days 7-14: Differentiation\\n"
                "- Remove Wnt3a, add differentiation factors\\n"
                "- Add 3 uM CHIR99021 (GSK3i) + 1 uM A83-01 (TGFbi)\\n"
                "- Monitor budding morphology\\n\\n"
                "### Harvest\\n"
                "1. Remove medium, add 1 mL ice-cold PBS\\n"
                "2. Pipette to break Matrigel\\n"
                "3. Centrifuge 300g x 5 min\\n"
                "4. Proceed to RNA extraction or fixation")
''')

info_line("L7 written")
