"""
rebis.imas — IMAS Molecular Arrangement Design
═══════════════════════════════════════════════
Lazy-import bridge to imas/.
"""
import sys, importlib
from pathlib import Path
_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "imas")]:
    if p not in sys.path: sys.path.insert(0, p)
__all__ = []
def _lazy(name, module, attr=None):
    try: m = importlib.import_module(module); globals()[name] = getattr(m, attr or name); __all__.append(name)
    except Exception: pass

_lazy("Token", "imas.arranger"); _lazy("Family", "imas.arranger")
_lazy("token_name", "imas.arranger"); _lazy("signature", "imas.arranger")
_lazy("IMASM_CLINK_Link", "imas.clink_bridge")
_lazy("imasm_to_clink", "imas.clink_bridge")
_lazy("smiles_to_ig", "imas.compound_catalog")
_lazy("build_catalog_entry", "imas.compound_catalog")
_lazy("register_compound", "imas.compound_catalog")
_lazy("register_all_compounds", "imas.compound_catalog")
_lazy("ig_distance", "imas.compound_imasm")
_lazy("FrobeniusPattern", "imas.frobenius_hunter")
_lazy("detect_frobenius_pattern", "imas.frobenius_hunter")
_lazy("generate_frobenius_arrangements", "imas.frobenius_hunter")
_lazy("fingerprint_to_ig", "imas.ig_bridge")
_lazy("canonical_ig_types", "imas.ig_bridge")
_lazy("ig_distance", "imas.ig_bridge")
_lazy("check_consistency", "imas.wiring")
_lazy("ReactionFingerprint", "imas.reactivity_imasm")
_lazy("identify_reaction", "imas.reactivity_imasm")
