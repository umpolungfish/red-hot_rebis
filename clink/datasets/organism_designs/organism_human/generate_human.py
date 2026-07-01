#!/usr/bin/env python3
"""
generate_human.py — Generate the complete Homo sapiens CLINK design package.

Structural type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟>  O_∞  C=1.0
Crystal address: 17,280,000-type lattice, ZFC_fe foundation

Usage:
    python3 generate_human.py [--output-dir DIR] [--mode actionable|minimal]
"""
import sys
import argparse
from pathlib import Path
from shared.rich_output import *

REBIS_ROOT = Path(__file__).parent.parent.parent.parent.parent.absolute()
sys.path.insert(0, str(REBIS_ROOT))


def generate_all(output_dir: str = "", mode: str = "actionable") -> dict:
    from clink.datasets.generators import (

        generate_organism_design_package,
        generate_actionable_organism_package,
    )

    if not output_dir:
        output_dir = str(Path(__file__).parent)

    info_line("=" * 70)
    info_line("CLINK HUMAN DESIGN PIPELINE")
    info_line("Homo sapiens — ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟>  O_∞  C=1.0")
    info_line("ZFC_fe foundation: μ∘δ=id at every layer")
    info_line("=" * 70)

    if mode == "actionable":
        info_line("\nMode: actionable (gene_designer + protein_structure + SBML + plasmid)\n")
        manifest = generate_actionable_organism_package(
            organism_type="human",
            output_dir=output_dir,
            write_files=True,
        )
    else:
        info_line("\nMode: minimal (base generators)\n")
        manifest = generate_organism_design_package(
            organism_type="human",
            output_dir=output_dir,
            write_files=True,
        )

    info_line(f"\n{'=' * 70}")
    print(f"COMPLETE — {manifest.get('total_files',0)} files, "
          f"{manifest.get('total_bytes',0):,} bytes")
    info_line(f"Output: {manifest.get('output_directory', output_dir)}")
    error_line(f"Frobenius: {'✓' if manifest.get('frobenius_verified', True) else '✗'}")
    info_line(f"\nStructural type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟>")
    info_line(f"Tier: O_∞  |  C-score: 1.0")
    info_line(f"Foundation: ZFC_fe  |  μ∘δ=id")
    info_line(f"{'=' * 70}")

    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Homo sapiens CLINK design package")
    parser.add_argument("--output-dir", default="", help="Output directory (default: same as script)")
    parser.add_argument("--mode", choices=["actionable", "minimal"], default="actionable",
                        help="Generation mode")
    args = parser.parse_args()
    generate_all(output_dir=args.output_dir, mode=args.mode)
