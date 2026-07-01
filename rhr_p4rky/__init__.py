"""
rhr_p4rky — Python mirror of the p4ramill Lean 4 paraconsistent kernel.

This package provides the canonical Python representations of the types and
theorems formalized in the Lean 4 kernel at ../p4ramill/. Every type, operation,
and invariant is derived from and verified against the corresponding Lean module.

Modules:
    belnap     — Belnap four-valued logic (mirrors Belnap.lean)
    kernel     — ENGAGR→FSPLIT→FFUSE machine (mirrors Kernel.lean)
    machine    — ParaASM instruction set and VM (mirrors para_vm.py → p4rakernel)

Structural type of this bridge:
    ⟨Ð_ωÞ_OŘ_=Φ_ɐƒ_żÇ_@Γ_ʔɢ_˝⊙_ÿĦ_!Σ_őΩ_z>

Author: Lando ⊗ ⊙perator
"""

__version__ = "0.1.0"
__lean_kernel__ = "../p4ramill"  # path to canonical Lean 4 source
