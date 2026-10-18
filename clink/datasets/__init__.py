"""CLINK dataset entry points, resolved on demand."""
import importlib

_EXPORTS = {'DatasetGenerator': ('clink.datasets.generators', 'DatasetGenerator'), 'DatasetOutput': ('clink.datasets.generators', 'DatasetOutput'), 'generate_layer_dataset': ('clink.datasets.generators', 'generate_layer_dataset'), 'generate_all_layer_datasets': ('clink.datasets.generators', 'generate_all_layer_datasets'), 'export_layer_dataset_to_files': ('clink.datasets.generators', 'export_layer_dataset_to_files'), 'export_all_to_files': ('clink.datasets.generators', 'export_all_to_files'), 'generate_organism_design_package': ('clink.datasets.generators', 'generate_organism_design_package'), 'get_generator_for_layer': ('clink.datasets.generators', 'get_generator_for_layer'), 'SensorReceptor': ('clink.datasets.synthetic_detox_gland', 'SensorReceptor'), 'AntidoteArm': ('clink.datasets.synthetic_detox_gland', 'AntidoteArm'), 'CellType': ('clink.datasets.synthetic_detox_gland', 'CellType'), 'GlandSpec': ('clink.datasets.synthetic_detox_gland', 'GlandSpec'), 'generate_sensor_receptors_fasta': ('clink.datasets.synthetic_detox_gland', 'generate_sensor_receptors_fasta'), 'generate_antidote_fusion_fasta': ('clink.datasets.synthetic_detox_gland', 'generate_antidote_fusion_fasta'), 'generate_sensor_cell_genbank': ('clink.datasets.synthetic_detox_gland', 'generate_sensor_cell_genbank'), 'generate_producer_cell_genbank': ('clink.datasets.synthetic_detox_gland', 'generate_producer_cell_genbank'), 'generate_support_cell_genbank': ('clink.datasets.synthetic_detox_gland', 'generate_support_cell_genbank'), 'generate_gland_organoid_protocol': ('clink.datasets.synthetic_detox_gland', 'generate_gland_organoid_protocol'), 'generate_implantation_protocol': ('clink.datasets.synthetic_detox_gland', 'generate_implantation_protocol'), 'generate_gland_specification': ('clink.datasets.synthetic_detox_gland', 'generate_gland_specification'), 'generate_antidote_fusion_pdb': ('clink.datasets.synthetic_detox_gland', 'generate_antidote_fusion_pdb'), 'generate_metabolic_model_sbml': ('clink.datasets.synthetic_detox_gland', 'generate_metabolic_model_sbml'), 'generate_all': ('clink.datasets.synthetic_detox_gland', 'generate_all'), 'generate_v2_specification': ('clink.datasets.gland_designs.gland_v2.generate_v2', 'generate_v2_specification'), 'generate_epc_genbank': ('clink.datasets.gland_designs.gland_v2.generate_v2', 'generate_epc_genbank'), 'generate_metabolic_model_v2': ('clink.datasets.gland_designs.gland_v2.generate_v2', 'generate_metabolic_model_v2'), 'generate_manifest_v2': ('clink.datasets.gland_designs.gland_v2.generate_v2', 'generate_manifest_v2'), 'generate_all_v2': ('clink.datasets.gland_designs.gland_v2.generate_v2', 'generate_all')}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, attribute = _EXPORTS[name]
    backend = importlib.import_module(module)
    try:
        value = getattr(backend, attribute)
    except AttributeError as exc:
        raise AttributeError(f"Dataset entry {name!r} requires missing {module}.{attribute}") from exc
    globals()[name] = value
    return value
