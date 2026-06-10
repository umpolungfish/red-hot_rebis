#!/usr/bin/env python3
"""PART 2: L0-L4 layer generators."""
import os, json

PY = "/home/mrnob0dy666/red-hot_rebis/clink/datasets/generators.py"

def w(s):
    with open(PY, 'a') as f:
        f.write(s + '\n')

# L0
w('''
class Layer0DatasetGenerator(DatasetGenerator):
    layer_idx = 0; layer_name = "Frustrated Belnap5 (Quarks)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=0, layer_name=self.layer_name, layer_tier="O₀", structural_tuple=dict(self.tup))
        o.files.append(DatasetFile(filename="qcd_coupling_alpha_s.csv", extension=".csv",
            content=self._alphas(), description="Running QCD coupling constant", format_name="CSV"))
        o.files.append(DatasetFile(filename="qcd_lattice_params.xml", extension=".xml",
            content=self._lattice(), description="Lattice QCD parameters", format_name="XML"))
        o.files.append(DatasetFile(filename="hadron_spectrum.json", extension=".json",
            content=json.dumps({"pion":"135MeV","rho":"770MeV","proton":"938MeV"},indent=2),
            description="Hadron mass spectrum", format_name="JSON"))
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    def _alphas(self):
        ls = ["Q2,alpha_s"]; [ls.append(f"{q},{max(0.05,min(0.5,0.12/math.log(max(math.sqrt(q)/0.2,1.1)))):.4f}") for q in [1,2,5,10,20,50,100,200,500,1000,5000]]; return "\\n".join(ls)
    def _lattice(self):
        return '<?xml version="1.0"?><latticeQCD><gauge_group>SU(3)</gauge_group><n_colors>3</n_colors><lattice_size>24 24 24 48</lattice_size><beta>6.0</beta></latticeQCD>'
''')

# L1
w('''
class Layer1DatasetGenerator(DatasetGenerator):
    layer_idx = 1; layer_name = "Electron Orbital (Belnap4)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=1, layer_name=self.layer_name, layer_tier="O₀", structural_tuple=dict(self.tup))
        o.files.append(DatasetFile(filename="electron_configs.csv", extension=".csv",
            content=self._cfgs(), description="Electron configurations", format_name="CSV"))
        o.files.append(DatasetFile(filename="b4_map.json", extension=".json",
            content=json.dumps({"B":"Guanine","T":"Cytosine","F":"Adenine","N":"Thymine"},indent=2),
            description="Belnap4 to nucleotide mapping", format_name="JSON"))
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
    def _cfgs(self):
        c = {1:"1s1",2:"1s2",6:"[He]2s2 2p2",7:"[He]2s2 2p3",8:"[He]2s2 2p4",26:"[Ar]3d6 4s2"}
        return "\\n".join([f"Z={z}, {c[z]}" for z in sorted(c)])
''')

# L2
w('''
class Layer2DatasetGenerator(DatasetGenerator):
    layer_idx = 2; layer_name = "Atom (Nuclear + Electron)"
    def generate(self, d=None):
        o = DatasetOutput(layer_idx=2, layer_name=self.layer_name, layer_tier="O₁", structural_tuple=dict(self.tup))
        o.files.append(DatasetFile(filename="atomic_params.csv", extension=".csv",
            content="Z,symbol,mass_amu,radius_pm,ionization_eV\\n6,C,12.011,76,11.260\\n7,N,14.007,75,14.534\\n8,O,15.999,73,13.618\\n15,P,30.974,107,10.487\\n26,Fe,55.845,132,7.902",
            description="Atomic parameters table", format_name="CSV"))
        o.files.append(DatasetFile(filename="isotopes.json", extension=".json",
            content=json.dumps({"C":{"stable":["C12","C13"],"radioactive":["C14"]},"O":{"stable":["O16","O17","O18"]}},indent=2),
            description="Isotope selection table", format_name="JSON"))
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
''')

# L3 - Molecule
w('''
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
        return ("# CLINK Molecule Inventory\\n"
                "C(C(=O)O)N\\tAlanine\\n"
                "CC(C)CC(C(=O)O)N\\tLeucine\\n"
                "C1=CC=C(C=C1)CC(C(=O)O)N\\tPhenylalanine\\n"
                "C(CC(=O)O)C(C(=O)O)N\\tGlutamic_acid\\n"
                "C1=NC2=C(N1)N(C=N2)C3C(C(C(O3)CO)O)O\\tAdenosine\\n"
                "CC1=CN(C(=O)NC1=O)C2C(C(C(O2)CO)O)O\\tThymidine")
    
    def _props(self):
        return ("SMILES,Name,MW,logP,HBD,HBA\\n"
                "C(C(=O)O)N,Alanine,89.09,-2.85,2,4\\n"
                "CC(C)CC(C(=O)O)N,Leucine,131.17,-1.52,2,4\\n"
                "C1=CC=C(C=C1)CC(C(=O)O)N,Phenylalanine,165.19,-1.38,2,4\\n"
                "C(CC(=O)O)C(C(=O)O)N,Glutamic_acid,147.13,-3.69,3,6")
    
    def _retro(self):
        return json.dumps({
            "alanine": {"from": ["pyruvate","NH3","NADPH"],"enzymes":["ALT","GDH"]},
            "glucose": {"from": ["CO2","H2O"],"pathway":"gluconeogenesis"},
            "atp": {"from":["ADP","Pi"],"enzyme":"ATP synthase"},
        }, indent=2)
    
    def _rxns(self):
        return json.dumps({
            "glycolysis":{"reactants":"Glucose+2NAD+2ADP","products":"2Pyruvate+2NADH+2ATP","deltaG_kJ":-74.5},
            "tca":{"reactants":"Acetyl-CoA+3NAD+FAD","products":"2CO2+3NADH+FADH2+GTP","deltaG_kJ":-40.0},
        }, indent=2)
''')

# L4 - Protein  
w('''
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
                content=json.dumps({"primitive_spectrum":spec,"classification":str(cls)},indent=2),
                description="Serpentrod protein classification", format_name="JSON"))
        except: pass
        
        # FASTA
        o.files.append(DatasetFile(filename="protein.fasta",extension=".fasta",
            content=f">CLINK|{fn}|length={len(seq)}\\n{seq}\\n",
            description="Protein sequence in FASTA format", format_name="FASTA"))
        
        # PDB template
        pdb = ["HEADER CLINK PROTEIN DESIGN\\nCOMPND "+fn]
        for i,aa in enumerate(seq.upper()):
            x,y,z = i*1.5, math.sin(i*0.5)*5, math.cos(i*0.5)*5
            pdb.append(f"ATOM  {i+1:5d}  CA  {aa:<3s} A{i+1:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C  ")
        pdb.append("TER\\nEND")
        o.files.append(DatasetFile(filename="protein_coords.pdb",extension=".pdb",
            content="\\n".join(pdb),
            description="PDB coordinate template for protein", format_name="PDB"))
        
        # Secondary structure
        ss = {}
        for i,aa in enumerate(seq.upper()):
            if aa in "ML": ss[i] = "H"
            elif aa in "SC": ss[i] = "E"
            else: ss[i] = "C"
        o.files.append(DatasetFile(filename="secondary_structure.json",extension=".json",
            content=json.dumps({"prediction":ss,"composition":{"H":list(ss.values()).count("H"),"E":list(ss.values()).count("E"),"C":list(ss.values()).count("C")}},indent=2),
            description="Secondary structure prediction", format_name="JSON"))
        
        o.frobenius_verified = clink_frobenius_closed(self.tup); return o
''')

print("L0-L4 written")
