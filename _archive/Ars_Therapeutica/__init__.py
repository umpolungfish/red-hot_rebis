"""
Ars Therapeutica — Structural grammar-derived optimal therapies.
Operationalized as a type-lattice navigator with disease-to-health promotion pathways.

Usage:
  at list              — list all available therapies
  at diagnose <disease> — structural diagnosis
  at therapy <disease>  — full therapy protocol
  at compare <a> <b>    — side-by-side structural comparison
  at tensor <a> <b>     — compute tensor product
  at meet <a> <b>       — compute meet (greatest lower bound)
  at spectrum           — show psychiatric φ̂-spectrum
  at operate <d> <op>   — run structural operation on disease

Integration:
  rebis.py at list      — accessible through the Red-Hot Rebis orchestrator
"""
__version__ = "1.1.0"
