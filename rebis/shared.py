"""
rebis.shared — Shared Primitives, Weights & IG Catalog
═══════════════════════════════════════════════════════
Exposes shared/ under rebis.shared.<x>.
Uses importlib to avoid name conflict with rebis package.

Structural Type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩
"""

import sys
import importlib
import io
from pathlib import Path

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
_sys_path_restored = False

def _ensure_sys_path():
    global _sys_path_restored
    if not _sys_path_restored:
        sys.path.insert(0, str(_REBIS_ROOT))
        _sys_path_restored = True

def _load_mod(mod_name, unique_name=None):
    """Load a module from the shared/ directory using importlib."""
    _ensure_sys_path()
    target = unique_name or f"_shared_{mod_name}"
    if target in sys.modules:
        return sys.modules[target]
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = io.StringIO()
    try:
        mod = importlib.import_module(f"shared.{mod_name}")
        sys.modules[target] = mod
        return mod
    finally:
        sys.stdout, sys.stderr = old_out, old_err

# Load shared modules
_prim = _load_mod("primitives")
_rich = _load_mod("rich_output")

# ── Primitives ──
ORDINALS = _prim.ORDINALS
WEIGHTS = _prim.WEIGHTS
PRIMITIVE_ORDER = _prim.PRIMITIVE_ORDER
SUBSCRIPT_TO_DESERET = _prim.SUBSCRIPT_TO_DESERET
resolve_ordinal_key = _prim.resolve_ordinal_key
to_vector = _prim.to_vector
weight_vector = _prim.weight_vector
tuple_distance = _prim.tuple_distance
directed_distance = _prim.directed_distance
breakdown = _prim.breakdown
build_metric_tensor = _prim.build_metric_tensor
mahalanobis_distance = _prim.mahalanobis_distance

# ── Derived exports ──
PRIMITIVE_NAMES = PRIMITIVE_ORDER  # alias
GLYPH_MAP = {}
for p, mapping in ORDINALS.items():
    for glyph in mapping:
        GLYPH_MAP.setdefault(p, []).append(glyph)

PRIMITIVE_CARDINALITIES = {p: len(m) for p, m in ORDINALS.items()}

def primitive_weight(prim):
    return WEIGHTS.get(prim, 1.0)

def glyph_for(prim, idx=0):
    glyphs = GLYPH_MAP.get(prim, [])
    if not glyphs:
        return "?"
    if isinstance(idx, str):
        return idx if idx in ORDINALS.get(prim, {}) else glyphs[0]
    return glyphs[idx % len(glyphs)] if glyphs else "?"

def primitives_list():
    return [{"name": p, "ordinals": ORDINALS[p], "weight": WEIGHTS[p]}
            for p in PRIMITIVE_ORDER]

def catalog_path():
    candidates = [
        _REBIS_ROOT / "IG_catalog.json",
        _REBIS_ROOT / "shared" / "IG_catalog.json",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return str(candidates[0])

# ── Rich output (names differ from shared/rich_output.py) ──
def reaction_header(title, width=66):
    return _rich.header(title, width)

def section_header(title, width=66):
    return _rich.header(title, width)

def subsection_header(title):
    return _rich.subheader(title)

info_line = _rich.info_line
success_line = _rich.success_line
error_line = _rich.error_line
warning_line = _rich.warning_line
separator = _rich.separator

__all__ = [
    "ORDINALS", "WEIGHTS", "PRIMITIVE_ORDER", "PRIMITIVE_NAMES",
    "GLYPH_MAP", "PRIMITIVE_CARDINALITIES", "SUBSCRIPT_TO_DESERET",
    "resolve_ordinal_key", "to_vector", "weight_vector",
    "tuple_distance", "directed_distance", "breakdown",
    "build_metric_tensor", "mahalanobis_distance",
    "primitive_weight", "glyph_for", "primitives_list", "catalog_path",
    "reaction_header", "info_line", "success_line", "error_line",
    "warning_line", "separator", "section_header", "subsection_header",
]


def parse_numerical_tuple(tup_str):
    """Parse a numerical 12-tuple string into a glyph dict.

    Accepts formats:
      1-based:  "4,5,4,5,3,5,3,4,2,4,3,3"   (matches ORDINALS convention)
      0-based:  "3,3,3,4,0,2,1,2,1,2,0,2"
      Space-sep: "4 5 4 5 3 5 3 4 2 4 3 3"
      Semicolon: "4;5;4;5;3;5;3;4;2;4;3;3"

    Returns dict {prim_name: glyph} or None if not a valid numerical tuple.
    """
    import re
    if not tup_str or not isinstance(tup_str, str):
        return None
    cleaned = tup_str.strip().replace("⟨", "").replace("⟩", "")
    # Split on commas, semicolons, or whitespace
    parts = re.split(r"[,;\s]+", cleaned.strip())
    parts = [p for p in parts if p]
    if len(parts) != 12:
        return None
    # Must all be integers
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    # Determine if 0-based or 1-based: if any value is 0, it's 0-based
    is_zero_based = any(n == 0 for n in nums)
    result = {}
    for i, n in enumerate(nums):
        prim = PRIMITIVE_ORDER[i]
        glyphs = GLYPH_MAP[prim]
        idx = n if is_zero_based else n - 1
        if idx < 0 or idx >= len(glyphs):
            return None  # Out of range — not a valid numerical tuple
        result[prim] = glyphs[idx]
    return result


__all__.append("parse_numerical_tuple")
