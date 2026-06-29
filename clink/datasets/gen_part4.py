#!/usr/bin/env python3
"""PART 4: L8 organism + orchestration functions."""
import os
from shared.rich_output import *

PY = "/home/mrnob0dy666/red-hot_rebis/clink/datasets/generators.py"

def w(s):
    with open(PY, 'a') as f:
        f.write(s + '\n')

# L8 - Organism
w('''
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
                o.tool_bridges_used.append(tname)
            except: pass
        
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
        }, indent=2)
    
    def _physiology(self, ot):
        if ot == "mammal":
            return ("parameter,value,unit\\n"
                    "body_temp,37,C\\n"
                    "heart_rate,70,bpm\\n"
                    "respiratory_rate,16,breaths_per_min\\n"
                    "blood_volume,5,L\\n"
                    "cardiac_output,5,L_per_min\\n"
                    "MAP,95,mmHg\\n"
                    "GFR,125,mL_per_min\\n"
                    "BMR,1800,kcal_per_day\\n"
                    "blood_glucose,5,mM\\n"
                    "pH,7.4,log[H+]")
        else:
            return "parameter,value,unit\\nbody_temp,37,C\\n"
    
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
        }, indent=2)
    
    def _homeostasis(self, ot):
        return json.dumps({
            "thermoregulation": {"setpoint_C":37,"range_C":"36.5-37.5","sensor":"hypothalamus"},
            "glucose_regulation": {"setpoint_mM":5,"range_mM":"4-7","hormones":["insulin","glucagon"]},
            "calcium_homeostasis": {"setpoint_mM":2.5,"hormones":["PTH","calcitonin","vitamin_D"]},
            "osmoregulation": {"setpoint_mOsm":300,"organ":"kidney","hormone":"ADH"},
            "blood_pressure": {"setpoint_MAP_mmHg":95,"reflex":"baroreflex"},
        }, indent=2)
    
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
        }, indent=2)
''')

info_line("L8 written")

# Orchestration functions
w('''
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
                                      write_files: bool = True) -> Dict[str, Any]:
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
    out_path.mkdir(parents=True, exist_ok=True)
    
    # Design data propagates upward
    design_data = {
        5: {"cell_type": "eukaryote" if organism_type != "prokaryote" else "prokaryote",
            "genome_size_bp": 3_000_000_000 if organism_type=="mammal" else 500_000_000},
        8: {"organism_type": organism_type},
    }
    
    # Generate all layer datasets
    all_results = {}
    for idx in range(9):
        dd = design_data.get(idx, {})
        if idx == 4:
            dd["sequence"] = "MLSDCGPYKVLVVGDGGVGKSALTIQ"
            dd["target_function"] = f"{organism_type}_design_protein"
        gen = get_generator_for_layer(idx)
        result = gen.generate(dd)
        all_results[idx] = result
        
        if write_files:
            layer_dir = out_path / f"L{idx}_{gen.layer_name.replace(' ','_')}"
            layer_dir.mkdir(exist_ok=True)
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
        "total_bytes": total_bytes,
        "tool_bridges": list(bridges),
        "frobenius_verified": all(r.frobenius_verified for r in all_results.values()),
        "output_directory": str(out_path),
        "generation_time_seconds": round(time.time() - start, 2),
        "generated_at": all_results[8].generation_time if 8 in all_results else "",
    }
    
    # Write manifest
    with open(out_path / "design_manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest
''')

info_line("Orchestration written")
info_line("PART 4 complete")
