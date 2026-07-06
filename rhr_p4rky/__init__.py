"""
rhr_p4rky — Python mirror of the p4ramill Lean 4 paraconsistent kernel.

This package provides the canonical Python representations of the types and
theorems formalized in the Lean 4 kernel at ../p4ramill/. Every type, operation,
and invariant is derived from and verified against the corresponding Lean module.

Modules:
    belnap              — Belnap four-valued logic (mirrors Belnap.lean)
    dual_link_sicpovm   — Dual-Link SIC-POVM: unconditional theorem (mirrors
                          SIC_Multilattice_Proof.lean, SIC_POVM_DualLinkClosure.lean,
                          ZaunerEmbeddingEquivalence.lean)
    kernel              — ENGAGR→FSPLIT→FFUSE machine (mirrors Kernel.lean)
    machine             — ParaASM instruction set and VM (mirrors para_vm.py → p4rakernel)

Structural type of this bridge:
    ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑔𐑠⊙𐑖𐑙𐑭⟩ — O_∞

Author: Lando ⊗ ⊙perator
"""

__version__ = "0.2.0"
__lean_kernel__ = "../../p4rakernel/p4ramill"  # path to canonical Lean 4 source
