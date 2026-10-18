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
_EXPORTS = {'Token': ('imas.arranger', 'Token'), 'Family': ('imas.arranger', 'Family'), 'token_name': ('imas.arranger', 'token_name'), 'signature': ('imas.arranger', 'signature'), 'IMASM_CLINK_Link': ('imas.clink_bridge', 'IMASM_CLINK_Link'), 'imasm_to_clink': ('imas.clink_bridge', 'imasm_to_clink'), 'smiles_to_ig': ('imas.compound_catalog', 'smiles_to_ig'), 'build_catalog_entry': ('imas.compound_catalog', 'build_catalog_entry'), 'register_compound': ('imas.compound_catalog', 'register_compound'), 'register_all_compounds': ('imas.compound_catalog', 'register_all_compounds'), 'ig_distance': ('imas.ig_bridge', 'ig_distance'), 'FrobeniusPattern': ('imas.frobenius_hunter', 'FrobeniusPattern'), 'detect_frobenius_pattern': ('imas.frobenius_hunter', 'detect_frobenius_pattern'), 'generate_frobenius_arrangements': ('imas.frobenius_hunter', 'generate_frobenius_arrangements'), 'fingerprint_to_ig': ('imas.ig_bridge', 'fingerprint_to_ig'), 'canonical_ig_types': ('imas.ig_bridge', 'canonical_ig_types'), 'check_consistency': ('imas.molecular_crystal_designer', 'check_consistency'), 'ReactionFingerprint': ('imas.reactivity_imasm', 'ReactionFingerprint'), 'identify_reaction': ('imas.reactivity_imasm', 'identify_reaction')}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module, attribute = _EXPORTS[name]
    value = getattr(importlib.import_module(module), attribute)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
