#!/usr/bin/env python3
"""
demo_formulas.py — Demonstrate molecular formula annotation on retrosynthetic fragments.

Each target is decomposed by the ch3mpiler pipeline; every fragment and synthon
now carries its Hill-order molecular formula in brackets alongside the SMILES.
"""
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE / "ch3mpiler"))
sys.path.insert(0, str(BASE))

from pipeline.reaction_pipeline import ReactionPipeline
from shared.rich_output import info_line, separator

DEMOS = [
    # (label, smiles, description)
    (
        "Aspirin",
        "CC(=O)Oc1ccccc1C(=O)O",
        "C9H8O4 — ester + carboxylic acid + aromatic ring; two strategic cuts",
    ),
    (
        "Paracetamol",
        "CC(=O)Nc1ccc(O)cc1",
        "C8H9NO2 — amide bond is the key disconnection; shows N in fragments",
    ),
    (
        "L-DOPA",
        "N[C@@H](Cc1ccc(O)c(O)c1)C(=O)O",
        "C9H11NO4 — amine + carboxylic acid + catechol; three heteroatom families",
    ),
    (
        "Ibuprofen",
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
        "C13H18O2 — arylpropionic acid; alpha to aromatic disconnection",
    ),
    (
        "Epinephrine",
        "CNC[C@@H](O)c1ccc(O)c(O)c1",
        "C9H13NO3 — catecholamine; amine + phenol + alcohol — N and O across fragments",
    ),
]


def run_demo():
    sep = "=" * 72

    for label, smiles, desc in DEMOS:
        print()
        print(sep)
        print(f"  DEMO: {label}")
        print(f"  {desc}")
        print(sep)

        pipeline = ReactionPipeline(max_depth=3)
        pipeline._target_smiles = smiles
        pipeline._visited.clear()
        tree = pipeline.deep_retrosynthesis(smiles)
        pipeline.print_tree(tree)

    print()
    print(sep)
    print("  All fragments carry Hill-order formula [CnHmNpOq...] in brackets.")
    print("  Reagent terminals show SMILES + formula: e.g. acetic_acid [CC(=O)O] [C2H4O2]")
    print(sep)


if __name__ == "__main__":
    run_demo()
