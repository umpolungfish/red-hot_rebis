"""
imas/ — IMASM Arrangement Engine for Red-Hot Rebis

IMASM token arrangement space provides structural fingerprinting for:
  - Compounds (molecules → 8-token arrangements → IG crystal types)
  - Reactivities (reactions → arrangement transitions → reaction classes)
  - Retrosynthetic analysis (disconnection paths → IMASM sequences)

All modules connect through the shared StructuralFingerprint → IG type bridge.
"""
import importlib as _importlib

_EXPORTS = {'Token': 'imas.arranger',
 'Family': 'imas.arranger',
 'StructuralFingerprint': 'imas.arranger',
 'compute_fingerprint': 'imas.arranger',
 'arrangement_distance': 'imas.arranger',
 'count_arrangements': 'imas.arranger',
 'analyze_molecule': 'imas.compound_imasm',
 'molecule_to_arrangement': 'imas.compound_imasm',
 'detect_functional_groups': 'imas.compound_imasm',
 'arrangement_to_tokens': 'imas.compound_imasm',
 'format_arrangement': 'imas.compound_imasm',
 'ReactionFingerprint': 'imas.reactivity_imasm',
 'identify_reaction': 'imas.reactivity_imasm',
 'reaction_to_fingerprint': 'imas.reactivity_imasm',
 'format_transition': 'imas.reactivity_imasm',
 'FrobeniusPattern': 'imas.frobenius_hunter',
 'detect_frobenius_pattern': 'imas.frobenius_hunter',
 'generate_frobenius_library': 'imas.frobenius_hunter',
 'analyze_frobenius_library': 'imas.frobenius_hunter',
 'estimate_frobenius_density': 'imas.frobenius_hunter',
 'generate_frobenius_arrangements': 'imas.frobenius_hunter',
 'analyze_compound_design_space': 'imas.molecular_crystal_designer',
 'analyze_crystal_neighborhood': 'imas.molecular_crystal_designer',
 'analyze_molecule_properties': 'imas.molecular_crystal_designer',
 'arrangement_to_fingerprint': 'imas.molecular_crystal_designer',
 'derive_position_constraints': 'imas.molecular_crystal_designer',
 'check_consistency': 'imas.molecular_crystal_designer',
 'fingerprint_to_ig': 'imas.ig_bridge',
 'describe_ig': 'imas.ig_bridge',
 'describe_full': 'imas.ig_bridge',
 'canonical_ig_types': 'imas.ig_bridge',
 'distinct_canonical_ig_types': 'imas.ig_bridge',
 'find_structural_clusters': 'imas.ig_bridge',
 'IMASM_CLINK_Link': 'imas.clink_bridge',
 'imasm_to_clink': 'imas.clink_bridge',
 'canonical_clink_map': 'imas.clink_bridge',
 'build_bridge_table': 'imas.clink_bridge',
 'frobenius_pathway_to_layer': 'imas.clink_bridge',
 'structural_activation_energy': 'imas.clink_bridge',
 'PortType': 'imas.wiring',
 'PortSpec': 'imas.wiring',
 'WiredNode': 'imas.wiring',
 'WiredGraph': 'imas.wiring',
 'all_branch_assignments': 'imas.wiring',
 'all_frob_pairings': 'imas.wiring',
 'get_smarts': 'imas.fg_exhaustive',
 'get_token': 'imas.fg_exhaustive',
 'list_by_token': 'imas.fg_exhaustive',
 'list_by_category': 'imas.fg_exhaustive',
 'token_counts': 'imas.fg_exhaustive',
 'total_patterns': 'imas.fg_exhaustive',
 'validate_patterns': 'imas.fg_exhaustive'}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(_importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
