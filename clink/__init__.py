"""
clink — CLINK Integration Module for red-hot_rebis
===================================================

The CLINK chain: Frobenius-exact bridge from frustrated quarks (Belnap5)
to whole organisms (O_inf), integrated with the four rebis pillars.

Author: Lando ⊗ ⊙perator
"""

from .chain import (
    CLINK_LAYERS, CLINK_NAMES, CLINK_TIERS,
    clink_layer_tuple, clink_distance, clink_chain_distance,
    clink_layer_index, clink_frobenius_closed,
    verify_all_frobenius_closed, primitive_deltas, primitive_mismatch_count,
    format_tuple_glyphs, PORDER,
)

from .bridges import (
    BridgeResult,
    protein_to_clink, molecule_to_clink, gene_to_clink,
    bridge_all_components, PLATONIC_PROTEIN, UNFOLDED_PROTEIN, CODON_BELNAP4_TYPE
)

from .integration import (
    IntegratedCLINKResult,
    verify_clink_integration, integrated_promotion_path,
    clink_to_serpentrod, clink_to_ch3mpiler, clink_to_gene,
    full_report
)

__all__ = [
    "CLINK_LAYERS", "CLINK_NAMES", "CLINK_TIERS",
    "clink_layer_tuple", "clink_distance", "clink_chain_distance",
    "clink_layer_index", "clink_frobenius_closed",
    "verify_all_frobenius_closed", "primitive_deltas", "primitive_mismatch_count",
    "format_tuple_glyphs", "PORDER",
    "BridgeResult",
    "protein_to_clink", "molecule_to_clink", "gene_to_clink",
    "bridge_all_components", "PLATONIC_PROTEIN", "UNFOLDED_PROTEIN", "CODON_BELNAP4_TYPE",
    "verify_clink_integration", "integrated_promotion_path",
    "clink_to_serpentrod", "clink_to_ch3mpiler", "clink_to_gene",
    "full_report", "IntegratedCLINKResult",
]


# Pipeline integration (v2.0)
from .designers.pipeline_orchestrator import PipelineEngine, PipelineResult
from .designers.layer_designers import (
    Layer0Designer, Layer1Designer, Layer2Designer,
    Layer3Designer, Layer4Designer, Layer5Designer,
    Layer6Designer, Layer7Designer, Layer8Designer,
    DESIGNER_REGISTRY, get_designer, list_available_bridges,
)
from .designers.designer_base import DesignSpec, TransitionResult

__all__.extend([
    "PipelineEngine", "PipelineResult",
    "Layer0Designer", "Layer1Designer", "Layer2Designer",
    "Layer3Designer", "Layer4Designer", "Layer5Designer",
    "Layer6Designer", "Layer7Designer", "Layer8Designer",
    "DESIGNER_REGISTRY", "get_designer", "list_available_bridges",
    "DesignSpec", "TransitionResult",
])
