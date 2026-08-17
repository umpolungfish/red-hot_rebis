"""
imas/ — IMASM Arrangement Engine for Red-Hot Rebis

IMASM token arrangement space provides structural fingerprinting for:
  - Compounds (molecules → 8-token arrangements → IG crystal types)
  - Reactivities (reactions → arrangement transitions → reaction classes)
  - Retrosynthetic analysis (disconnection paths → IMASM sequences)

All modules connect through the shared StructuralFingerprint → IG type bridge.
"""

# Every engine in this package is reachable from the package itself, as the other
# domains are. Nothing here was exposed, so a census of the toolchain reported the
# arrangement engine as empty while all nine modules imported cleanly.
import importlib as _importlib

__all__ = []

_EXPORTS = {
    "imas.arranger": ["Token", "Family", "StructuralFingerprint", "compute_fingerprint",
                       "arrangement_distance", "count_arrangements"],
    "imas.compound_imasm": ["analyze_molecule", "molecule_to_arrangement",
                             "detect_functional_groups", "arrangement_to_tokens",
                             "format_arrangement"],
    "imas.reactivity_imasm": ["ReactionFingerprint", "identify_reaction",
                               "reaction_to_fingerprint", "format_transition"],
    "imas.frobenius_hunter": ["FrobeniusPattern", "detect_frobenius_pattern",
                               "generate_frobenius_library", "analyze_frobenius_library",
                               "estimate_frobenius_density", "generate_frobenius_arrangements"],
    "imas.molecular_crystal_designer": ["analyze_compound_design_space",
                                         "analyze_crystal_neighborhood",
                                         "analyze_molecule_properties",
                                         "arrangement_to_fingerprint",
                                         "derive_position_constraints", "check_consistency"],
    "imas.ig_bridge": ["fingerprint_to_ig", "describe_ig", "describe_full",
                        "canonical_ig_types", "distinct_canonical_ig_types",
                        "find_structural_clusters"],
    "imas.clink_bridge": ["IMASM_CLINK_Link", "imasm_to_clink", "canonical_clink_map",
                           "build_bridge_table", "frobenius_pathway_to_layer",
                           "structural_activation_energy"],
    "imas.wiring": ["PortType", "PortSpec", "WiredNode", "WiredGraph",
                     "all_branch_assignments", "all_frob_pairings"],
    "imas.fg_exhaustive": ["get_smarts", "get_token", "list_by_token", "list_by_category",
                            "token_counts", "total_patterns"],
}

for _mod, _names in _EXPORTS.items():
    try:
        _m = _importlib.import_module(_mod)
    except Exception:
        continue
    for _n in _names:
        if hasattr(_m, _n):
            globals()[_n] = getattr(_m, _n)
            __all__.append(_n)
