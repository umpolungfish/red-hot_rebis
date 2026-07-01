"""
rebis — Red-Hot Rebis Namespace Package
───────────────────────────────────────
rebis.<x> nomenclature for ALL red-hot_rebis tools.

Access any tool as:  rebis.<domain>.<function>(...)

Domains:
  rebis.p4ra        — p4ra paraconsistent kernel (belnap, genetics, machine, filtration)
  rebis.ch3mpiler   — Molecular compiler & retrosynthesis
  rebis.clink       — CLINK chain organism pipeline
  rebis.materials   — Materials science & metamaterial design
  rebis.therapeutics — Therapeutic design pipeline
  rebis.biology     — Biological simulations & telomere design
  rebis.serpentrod  — Protein design & stratified prediction
  rebis.imas        — IMAS molecular arrangement design
  rebis.pipeline    — Imscription pipeline & Frobenius verification
  rebis.cdxml       — CDXML generation & target decomposition
  rebis.gene        — Gene imscriber & genetic engineering
  rebis.alchemy     — Alchemical treatise bridge & operations
  rebis.shared      — Shared primitives, weights, IG catalog
  rebis.demo        — Demonstration scripts
  rebis.scripts     — Utility scripts
  rebis.imasm       — IMASM iterator & fingerprint classifier
  rebis.cli         — rebis command-line interface

Callable from anywhere:  pip install -e .  →  rebis status

Structural Type: ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩
"""

import importlib
import sys as _sys
from pathlib import Path as _Path

__version__ = "3.0.0"
__author__ = "Lando⊗⊙perator"

# Lazy submodule loading — import on first attribute access only
_SUBMODULES = {
    "p4ra", "ch3mpiler", "clink", "materials", "therapeutics",
    "biology", "serpentrod", "imas", "pipeline", "cdxml",
    "gene", "alchemy", "shared", "demo", "scripts", "imasm", "cli",
}

_module_cache = {}


def __getattr__(name):
    if name in _SUBMODULES:
        if name not in _module_cache:
            _module_cache[name] = importlib.import_module(f"rebis.{name}")
        return _module_cache[name]
    raise AttributeError(f"module 'rebis' has no attribute '{name}'")


def __dir__():
    return list(_SUBMODULES) + ["__version__", "__author__"]
