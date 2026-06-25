"""
cdxml/pipeline_hook.py — Auto-export retrosynthetic tree intermediates as CDXML.
Updated for two-pass scaffold-aware decomposition.

NOW GENERATES:
  1. A SINGLE target-decomposition CDXML showing the FULL target molecule
     with all strategic bond cuts annotated (colored dashed lines + labels)
  2. Replaces the dozens of per-fragment CDXML files with this single,
     scaffold-mapped diagram.

Hooks into:
  - pipeline/reaction_pipeline.py  (--cdxml flag)

Author: Lando⊗⊙perator
"""
import os
from pathlib import Path
from .generator import smiles_to_cdxml, verify_cdxml
from .target_decomposition import target_decomposition_cdxml


def _get_attr(node, attr, default=None):
    """Safely get an attribute from either a RetrosyntheticNode or a dict."""
    if isinstance(node, dict):
        return node.get(attr, default)
    return getattr(node, attr, default)


def export_tree_to_cdxml(tree, output_dir: str, prefix: str = "intermediate",
                         verbose: bool = True) -> dict:
    """Walk a retrosynthetic tree and export CDXML.

    GENERATES:
      - A SINGLE target_decomposition.cdxml showing the FULL target
        molecule with ALL strategic bond cuts annotated on it.

    Args:
        tree: The tree node (RetrosyntheticNode) from deep_retrosynthesis
        output_dir: Directory to write .cdxml files
        prefix: Filename prefix (ignored — kept for API compatibility)
        verbose: Print progress

    Returns:
        dict with counts: {'total': N, 'generated': N, 'failed': [...], 'files': [...]}
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated = 0
    failed = []
    files = []

    def _walk_for_decomp(node, depth=0):
        """Walk the tree to find the root target SMILES and scaffold decomposition data."""
        if not node:
            return None, None, None, None

        target_smiles = None
        target_name = _get_attr(node, 'name', 'target')
        strategic_bonds = _get_attr(node, 'strategic_bonds', None)
        fg_pair_bonds = _get_attr(node, 'fg_pair_bonds', None)

        # Try to extract SMILES from the root node
        frag = _get_attr(node, 'fragment_smiles', '')
        if frag and frag != '?' and frag != '' and frag != 'H':
            target_smiles = frag
        else:
            smi = _get_attr(node, 'smiles', '')
            if smi and smi != '?' and smi != '':
                target_smiles = smi

        # If root doesn't carry strategic bonds, try the pipeline's scaffold data
        if strategic_bonds is None:
            root_route = _get_attr(node, 'routes', [])
            if root_route and len(root_route) > 0:
                first_route = root_route[0]
                if isinstance(first_route, dict):
                    strategic_bonds = first_route.get('strategic_bonds', None)

        # Walk children for more data
        for key in ['child_a', 'child_b', 'child']:
            child = _get_attr(node, key)
            if child:
                cs, cn, sb, fb = _walk_for_decomp(child, depth + 1)
                if cs and not target_smiles:
                    target_smiles = cs
                if sb and not strategic_bonds:
                    strategic_bonds = sb
                if fb and not fg_pair_bonds:
                    fg_pair_bonds = fb

        return target_smiles, target_name, strategic_bonds, fg_pair_bonds

    # Walk tree for scaffold decomposition data
    target_smiles, target_name, strategic_bonds, fg_pair_bonds = _walk_for_decomp(tree)

    # Also check the tree node itself for full scaffold data
    routes = _get_attr(tree, 'routes', [])
    if not strategic_bonds:
        # Try to get from the pipeline's scaffold data stored on the tree
        # (the pipeline stores the full scaffold decomposition on tree.routes
        #  when fragment_smiles propagation is active)
        strategic_bonds = _get_attr(tree, 'strategic_bonds', None)

    # Fallback: try to extract bond info from routes
    if not strategic_bonds and routes:
        for route in routes:
            fgp = route.get('fg_pair_bonds', {}) if isinstance(route, dict) else None
            if fgp:
                all_bonds = []
                for pair, bonds in fgp.items():
                    all_bonds.extend(bonds)
                if all_bonds:
                    strategic_bonds = all_bonds
                    break

    # Generate the target decomposition CDXML
    if target_smiles:
        fname = f"{target_name}_disconnections.cdxml"
        fpath = output_path / fname

        try:
            if strategic_bonds:
                # Filter to sensible retrosynthetic cuts only.
                # Remove: double_bond (C=O), triple_bond, aromatic, hydrogen_bond,
                # single-atom fragments (leaving groups like H, Cl, Na+).
                BAD_TYPES = ('double_bond', 'triple_bond', 'aromatic', 'hydrogen_bond')
                # Keep ALL retrosynthetically scissile bonds.
                # Remove: double_bond (C=O carbonyls — not scissile),
                # triple_bond, aromatic, hydrogen_bond.
                # Single-atom fragments (C, N, O, Cl) ARE valid building blocks:
                #   'C' = methyl/methane, 'N' = ammonia, 'O' = water, 'Cl' = HCl
                sensible_bonds = [
                    b for b in strategic_bonds
                    if b.get('bond_type') not in BAD_TYPES
                ]
                cdxml = target_decomposition_cdxml(
                    target_smiles, target_name, sensible_bonds
                )
            else:
                # No strategic bonds found — render target alone
                cdxml = smiles_to_cdxml(target_smiles, target_name,
                                        f"Target: {target_name} [{target_smiles}]")

            with open(fpath, 'w') as f:
                f.write(cdxml)
            generated += 1
            files.append(str(fpath))
            if verbose:
                bond_count = len(strategic_bonds) if strategic_bonds else 0
                print(f"  >> CDXML: {fname} ({target_name} [{target_smiles}])")
                print(f"       {bond_count} disconnection(s) annotated on target scaffold")
        except Exception as e:
            if verbose:
                print(f"  >> CDXML error: {fname}: {e}")
            failed.append(fname)
    else:
        if verbose:
            print(f"  >> CDXML: No target SMILES found — cannot generate scaffold decomposition")

    return {
        'total': generated + len(failed),
        'generated': generated,
        'failed': failed,
        'files': files,
    }
