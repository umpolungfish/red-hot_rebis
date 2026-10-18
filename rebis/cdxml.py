"""
rebis.cdxml — CDXML Generation & Target Decomposition
══════════════════════════════════════════════════════
Lazy-import bridge to cdxml/.
"""
import importlib

_EXPORTS = {'molecule_to_cdxml': 'cdxml.target_decomposition', 'target_decomposition_cdxml': 'cdxml.target_decomposition'}
__all__ = list(_EXPORTS)

def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value

def __dir__():
    return sorted(set(globals()) | set(__all__))
