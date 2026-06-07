"""
clink.datasets — Physically Actionable Dataset Generation
=========================================================

Converts CLINK structural designs into real, wet-lab-actionable output files:
  - DNA/RNA sequences (FASTA, GenBank)
  - Protein sequences (FASTA, PDB)
  - Molecular structures (SMILES, MOL, SDF)
  - SBOL documents (synthetic biology)
  - Simulation inputs (MD, QCD, DFT)
  - Protocols and formulations
  - Codon-optimized gene designs
  - Plasmid maps and construct specifications
  - Synthetic gland designs (detox, therapeutic)

Each layer's generator bridges to existing tools (serpentrod, ch3mpiler,
gene_imscriber, biology_sim, etc.) to produce real data, not just metadata.

Author: Lando ⊗ ⊙perator
"""

from .generators import (
    DatasetGenerator,
    DatasetOutput,
    generate_layer_dataset,
    generate_all_layer_datasets,
    export_layer_dataset_to_files,
    export_all_to_files,
    generate_organism_design_package,
    get_generator_for_layer,
)

from .synthetic_detox_gland import (
    SensorReceptor,
    AntidoteArm,
    CellType,
    GlandSpec,
    generate_sensor_receptors_fasta,
    generate_antidote_fusion_fasta,
    generate_sensor_cell_genbank,
    generate_producer_cell_genbank,
    generate_support_cell_genbank,
    generate_gland_organoid_protocol,
    generate_implantation_protocol,
    generate_gland_specification,
    generate_antidote_fusion_pdb,
    generate_metabolic_model_sbml,
    generate_all,
)
