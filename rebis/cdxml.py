"""
rebis.cdxml — CDXML Generation & Target Decomposition
══════════════════════════════════════════════════════
Lazy-import bridge to cdxml/.
"""
import sys, importlib
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "cdxml")]:
    if p not in sys.path: sys.path.insert(0, p)
__all__ = []
def _lazy(name, module, attr=None):
    try: m = importlib.import_module(module); globals()[name] = getattr(m, attr or name); __all__.append(name)
    except Exception: pass

_lazy("export_tree_to_cdxml", "cdxml.target_decomposition")
_lazy("molecule_to_cdxml", "cdxml.target_decomposition")
_lazy("target_decomposition_cdxml", "cdxml.target_decomposition")
