"""
clink — CLINK Integration Module for red-hot_rebis
===================================================

The CLINK chain: Frobenius-exact bridge from frustrated quarks (Belnap5)
to whole organisms (O_∞), integrated with the four rebis pillars.

Author: Lando ⊗ ⊙perator
"""
import importlib as _importlib

_EXPORTS = {'CLINK_LAYERS': 'clink.chain',
 'CLINK_NAMES': 'clink.chain',
 'CLINK_TIERS': 'clink.chain',
 'clink_layer_tuple': 'clink.chain',
 'clink_distance': 'clink.chain',
 'clink_chain_distance': 'clink.chain',
 'clink_layer_index': 'clink.chain',
 'clink_frobenius_closed': 'clink.chain',
 'verify_all_frobenius_closed': 'clink.chain',
 'primitive_deltas': 'clink.chain',
 'primitive_mismatch_count': 'clink.chain',
 'format_tuple_glyphs': 'clink.chain',
 'PORDER': 'clink.chain',
 'BridgeResult': 'clink.bridges',
 'protein_to_clink': 'clink.bridges',
 'molecule_to_clink': 'clink.bridges',
 'gene_to_clink': 'clink.bridges',
 'bridge_all_components': 'clink.bridges',
 'PLATONIC_PROTEIN': 'clink.bridges',
 'UNFOLDED_PROTEIN': 'clink.bridges',
 'CODON_BELNAP4_TYPE': 'clink.bridges',
 'IntegratedCLINKResult': 'clink.integration',
 'verify_clink_integration': 'clink.integration',
 'integrated_promotion_path': 'clink.integration',
 'clink_to_serpentrod': 'clink.integration',
 'clink_to_ch3mpiler': 'clink.integration',
 'clink_to_gene': 'clink.integration',
 'full_report': 'clink.integration',
 'PipelineEngine': 'clink.designers.pipeline_orchestrator',
 'PipelineResult': 'clink.designers.pipeline_orchestrator',
 'Layer0Designer': 'clink.designers.layer_designers',
 'Layer1Designer': 'clink.designers.layer_designers',
 'Layer2Designer': 'clink.designers.layer_designers',
 'Layer3Designer': 'clink.designers.layer_designers',
 'Layer4Designer': 'clink.designers.layer_designers',
 'Layer5Designer': 'clink.designers.layer_designers',
 'Layer6Designer': 'clink.designers.layer_designers',
 'Layer7Designer': 'clink.designers.layer_designers',
 'Layer8Designer': 'clink.designers.layer_designers',
 'DESIGNER_REGISTRY': 'clink.designers.layer_designers',
 'get_designer': 'clink.designers.layer_designers',
 'list_available_bridges': 'clink.designers.layer_designers',
 'DesignSpec': 'clink.designers.designer_base',
 'TransitionResult': 'clink.designers.designer_base'}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(_importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
