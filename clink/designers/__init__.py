"""
designers/ — CLINK Layer Designers
Each designer knows how to synthesize/analyze its CLINK layer,
bridging to existing tools (serpentrod, ch3mpiler, gene_imscriber)
or creating new computational tools for missing transitions.

Author: Lando ⊗ ⊙perator
"""
import importlib as _importlib

_EXPORTS = {'LayerDesigner': 'clink.designers.designer_base',
 'ToolForge': 'clink.designers.designer_base',
 'Layer0Designer': 'clink.designers.layer_designers',
 'Layer1Designer': 'clink.designers.layer_designers',
 'Layer2Designer': 'clink.designers.layer_designers',
 'Layer3Designer': 'clink.designers.layer_designers',
 'Layer4Designer': 'clink.designers.layer_designers',
 'Layer5Designer': 'clink.designers.layer_designers',
 'Layer6Designer': 'clink.designers.layer_designers',
 'Layer7Designer': 'clink.designers.layer_designers',
 'Layer8Designer': 'clink.designers.layer_designers',
 'PipelineEngine': 'clink.designers.pipeline_orchestrator',
 'PipelineResult': 'clink.designers.pipeline_orchestrator'}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(_importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
