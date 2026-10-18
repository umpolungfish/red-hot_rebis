"""
rebis.imasm — IMASM Iterator & Fingerprint Classifier
══════════════════════════════════════════════════════
Lazy-import bridge to imasm_iterator/.
"""
import importlib

_EXPORTS = {'Token': 'imasm_iterator.tokens', 'Family': 'imasm_iterator.tokens', 'TOKEN_NAMES': 'imasm_iterator.tokens', 'TOKEN_COUNT': 'imasm_iterator.tokens', 'token_name': 'imasm_iterator.tokens', 'token_family': 'imasm_iterator.tokens', 'signature': 'imasm_iterator.tokens', 'arrangement_str': 'imasm_iterator.tokens', 'StructuralFingerprint': 'imasm_iterator.classifier', 'compute_fingerprint': 'imasm_iterator.classifier', 'CANONICAL_CLASSES': 'imasm_iterator.classifier', 'CANONICAL_FINGERPRINTS': 'imasm_iterator.classifier', 'match_canonical': 'imasm_iterator.classifier', 'fingerprint_key': 'imasm_iterator.classifier', 'SignatureClass': 'imasm_iterator.engine', 'enumerate_signatures': 'imasm_iterator.engine', 'iter_signature_arrangements': 'imasm_iterator.engine', 'count_arrangements': 'imasm_iterator.engine', 'SpaceMap': 'imasm_iterator.engine', 'map_space': 'imasm_iterator.engine', 'search_arrangements': 'imasm_iterator.engine'}
__all__ = list(_EXPORTS)

def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value

def __dir__():
    return sorted(set(globals()) | set(__all__))
