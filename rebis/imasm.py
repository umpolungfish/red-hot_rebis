"""
rebis.imasm — IMASM Iterator & Fingerprint Classifier
══════════════════════════════════════════════════════
Lazy-import bridge to imasm_iterator/.
"""
import sys, importlib
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "imasm_iterator")]:
    if p not in sys.path: sys.path.insert(0, p)
__all__ = []
def _lazy(name, module, attr=None):
    try: m = importlib.import_module(module); globals()[name] = getattr(m, attr or name); __all__.append(name)
    except Exception: pass

_lazy("StructuralClassifier", "imasm_iterator.classifier")
_lazy("classify_fingerprint", "imasm_iterator.classifier")
_lazy("IMASMIterator", "imasm_iterator.engine")
_lazy("iterate_arrangements", "imasm_iterator.engine")
_lazy("TOKENS", "imasm_iterator.tokens")
_lazy("TOKEN_NAMES", "imasm_iterator.tokens")
_lazy("token_for", "imasm_iterator.tokens")
_lazy("resolve_token", "imasm_iterator.tokens")
_lazy("token_catalog", "imasm_iterator.tokens")
