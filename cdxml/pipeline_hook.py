"""Pipeline hook: bridges RetrosyntheticNode tree -> CDXML export.
Called by reaction_pipeline.py when --cdxml flag is set."""

import os
import sys
import hashlib
from typing import Dict, Optional

MAX_FILENAME_LEN = 100  # safe well under 255-char filesystem limit


def _safe_name(raw: str, max_len: int = 60) -> str:
    """Sanitize a string to a safe filesystem name fragment.

    Returns empty string if raw is empty. Callers handle fallback.
    """
    if not raw:
        return ""
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in raw)
    while "__" in safe:
        safe = safe.replace("__", "_")
    safe = safe[:max_len].rstrip("_-.")
    return safe if safe else ""


def export_tree_to_cdxml(
    tree: object,
    output_dir: str = "cdxml_output",
    verbose: bool = False,
    prefix: str = "",
) -> Dict:
    """Export a retrosynthetic tree root node to a SINGLE annotated CDXML file.

    Filename is truncated to avoid filesystem overflow (MAX_FILENAME_LEN=100).
    If the prefix already contains the target name (as in --demo mode where
    prefix = f"demo_{target_name}_"), the duplicate is removed. A short hash
    suffix is appended if truncation would lose uniqueness.

    Args:
        tree: RetrosyntheticNode root - carries name, smiles, strategic_bonds,
              fg_pair_bonds on the root node.
        output_dir: Target directory for CDXML output.
        verbose: Print progress.
        prefix: Filename prefix (e.g. "demo_aspirin_").

    Returns:
        Dict with keys: generated, failed, error, path.
    """
    os.makedirs(output_dir, exist_ok=True)

    target_name = getattr(tree, "name", "unknown")
    smiles = getattr(tree, "smiles", None) or getattr(tree, "fragment_smiles", None) or ""
    strategic_bonds = getattr(tree, "strategic_bonds", [])
    fg_pair_bonds = getattr(tree, "fg_pair_bonds", {})

    if not smiles:
        msg = f"No SMILES on root node '{target_name}' - cannot generate CDXML"
        if verbose:
            print(f"  [cdxml] {msg}")
        return {"generated": 0, "failed": 1, "error": msg, "path": ""}

    if not strategic_bonds and verbose:
        print(f"  [cdxml] No strategic bonds for '{target_name}'; generating plain molecule CDXML")

    # ── Build a truncated, deduplicated filename ─────────────────────
    # The demo mode passes prefix=f"demo_{d}_" where d == target_name.
    # Detect this: if the name appears inside prefix (after stripping
    # non-alnum separators), don't repeat it.

    prefix_stripped = prefix.strip("_- ")
    name_stripped = target_name.strip("_- ")

    # Normalize both for comparison: lowercase, collapse non-alnum
    def norm(s: str) -> str:
        return "".join(c.lower() if c.isalnum() else "" for c in s)

    prefix_norm = norm(prefix_stripped)
    name_norm = norm(name_stripped)

    if name_norm and name_norm in prefix_norm:
        # prefix already contains the name (e.g. demo mode) — use prefix only
        stem = _safe_name(prefix_stripped, max_len=MAX_FILENAME_LEN)
    else:
        prefix_clean = _safe_name(prefix_stripped, max_len=35)
        name_clean = _safe_name(name_stripped, max_len=55)
        if prefix_clean and name_clean:
            stem = f"{prefix_clean}_{name_clean}"
        elif prefix_clean:
            stem = prefix_clean
        elif name_clean:
            stem = name_clean
        else:
            stem = "molecule"

    # ── Fallback if stem is somehow empty ────────────────────────────
    if not stem:
        stem = "molecule"

    # ── Final length check with hash fallback ────────────────────────
    if len(stem) > MAX_FILENAME_LEN:
        short_hash = hashlib.md5(stem.encode()).hexdigest()[:8]
        stem = stem[: MAX_FILENAME_LEN - 9].rstrip("_-.") + f"_{short_hash}"

    filename = f"{stem}.cdxml"
    out_path = os.path.join(output_dir, filename)

    try:
        from cdxml.target_decomposition import molecule_to_cdxml
        cdxml_str = molecule_to_cdxml(
            smiles=smiles,
            molecule_name=target_name,
            strategic_bonds=strategic_bonds,
            fg_pair_bonds=fg_pair_bonds,
        )
        with open(out_path, "w") as f:
            f.write(cdxml_str)

        if verbose:
            fg_count = len(fg_pair_bonds)
            bond_count = len(strategic_bonds)
            print(f"  [cdxml] Written: {out_path}  ({bond_count} strategic bonds, {fg_count} FG pairs)")

        return {"generated": 1, "failed": 0, "path": out_path}

    except Exception as e:
        msg = f"CDXML generation failed for '{target_name}': {e}"
        if verbose:
            print(f"  [cdxml] ERROR: {msg}")
        import traceback
        traceback.print_exc()
        return {"generated": 0, "failed": 1, "error": msg, "path": out_path}
