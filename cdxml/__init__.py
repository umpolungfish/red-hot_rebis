"""
cdxml/ — Automatic CDXML generation for red-hot_rebis pipelines.

Hooks into:
  - rebis.py cdxml generate           (standalone command)
  - pipeline/reaction_pipeline.py     (auto-export intermediates)
  - ch3mpiler/compiler.py             (auto-export analyzed molecules)

Uses RDKit SMILES → proper ChemDraw CDXML format.
All tags are CDXML-v2 correct: <n> for atoms, <b> for bonds, p="x y" coords.

Author: Lando⊗⊙perator
"""

from .generator import smiles_to_cdxml, verify_cdxml
from .molecules import MOLECULES, APTAMERS, MATERIALS, generate_all
from .pipeline_hook import export_tree_to_cdxml

__all__ = [
    "smiles_to_cdxml", "verify_cdxml",
    "MOLECULES", "APTAMERS", "MATERIALS", "generate_all",
    "export_tree_to_cdxml",
]
