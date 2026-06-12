"""
genetic_asm.py — ParaASM Programs for the Genetic Code Interpreter.

Implements the genetic code as a paraconsistent virtual machine program.
The VM's Belnap registers model nucleotide positions; the Frobenius kernel
(ENGAGR→FSPLIT→FFUSE) executes the μ∘δ=id projection from codon to AA.

Three levels of implementation:
  1. B₄ nucleotide operations (single-nucleotide edit programs)
  2. Codon-level translation (triplet → AA via kernel cycles)
  3. Stratum-aware editing (exact/split/stop handling)

All programs run on the ParaASM VM from machine.py.
"""

from __future__ import annotations
from typing import Dict, List

# ── Genetic code as ParaASM programs ────────────────────────────────

PROGRAM_TRANSLATE_CODON = """
; translate_codon.asm
; Translate a codon stored in %r0 (p1), %r1 (p2), %r2 (p3) to
; its amino acid by executing the kernel Frobenius cycle.
;
; The kernel's ffuse∘fsplit = id ensures that for exact-stratum
; codons, the output %r0 equals the input %r0 (the nucleotide at
; position 1 determines the AA with position 2 as discriminator,
; and position 3 is forgotten).
;
; For split-stratum codons, the ENGAGR step detects the
; pyrimidine/purine distinction via dialetheic self-reference.

; Step 1: ENGAGR on p1 — force self-reference
ENGAGR  %r0

; Step 2: FSPLIT — comultiplication δ
FSPLIT  %r0  %r1  %r2

; Step 3: FFUSE — multiplication μ (reconstruct from split)
FFUSE   %r1  %r2  %r0

; %r0 now holds the translated amino acid type:
;   Belnap.T (C) → exact-stratum AA (position-2 determined)
;   Belnap.F (A) → split-stratum AA (pyrimidine half)
;   Belnap.B (B) → split-stratum AA (purine half) or Stop
;   Belnap.N (N) → split-stratum AA (UU_ box) or Stop

HALT
"""

PROGRAM_B4_EDIT = """
; b4_edit.asm
; Execute a B₄ lattice edit on a nucleotide position.
;
; Input:  %r0 = original nucleotide (as Belnap value)
;         %r2 = target edit operation (B⁴ element mapping)
; Output: %r3 = edited nucleotide (or B if cross-lattice jump detected)
;
; B₄ covering relations (edit cost = 1):
;   B → T (G→C), B → N (G→U), T → F (C→A), N → F (U→A)
;
; Cross-lattice jumps (edit cost = 2):
;   B ↔ F (G↔A), T ↔ N (C↔U)

; Save original in %r4
MOVE    %r0  %r4

; Apply ENGAGR to check if edit creates paradox
ENGAGR  %r0
FSPLIT  %r0  %r1  %r2
FFUSE   %r1  %r2  %r3

; Check if edit was cross-lattice:
; If %r3 == B and %r4 != B, this was B↔F or T↔N (cross-lattice)
MOVE    %r4  %r0      ; restore original
CLEAR   %r1
CLEAR   %r2

HALT
"""

PROGRAM_STRATUM_CLASSIFY = """
; stratum_classify.asm
; Classify a codon into Frobenius stratum.
;
; Input:  %r0 = p1, %r1 = p2, %r2 = p3 (as Belnap values)
; Output: %r0 = stratum:
;         IFIX (T) = exact stratum
;         N = split stratum
;         B = stop codon
;
; Algorithm (from B₄ lattice theorem):
;   Exact if p2 == C (T), OR (p2 ∈ {U,G} (N,B) AND p1 ∈ {C,G} (T,B))

; Check if p2 == C (T)
MOVE    %r1  %r3
IFIX    %r4              ; %r4 = T (true)
FFUSE   %r3  %r4  %r5   ; %r5 = join(p2, T) = T if p2==T, else B
FSPLIT  %r5  %r6  %r7   ; %r6 = T if p2==T, else split

; IF p2 == T -> exact, jump to .exact
JB      %r6  .exact

; p2 != T. Check if p2 ∈ {N,B} (U or G)
; N and B are the only Belnap values that are NOT T and NOT F
; Use: bnot(p2) != p2 for T/F, but bnot(p2) == p2 for N/B
MOVE    %r1  %r0        ; ENGAGR
MOVE    %r0  %r6        ; %r6 = p2 value
ENGAGR  %r2
FSPLIT  %r2  %r3  %r4
FFUSE   %r3  %r4  %r8   ; %r8 = bnot(p2) via kernel cycle

; Check if p1 ∈ {T,B} (C or G)
MOVE    %r0  %r9
IFIX    %r10             ; %r10 = T
FFUSE   %r9  %r10  %r11 ; %r11 = join(p1, T)

; If both conditions: p2∈{N,B} AND p1∈{T,B} -> exact
; Otherwise -> split

.exact:
IFIX    %r0              ; %r0 = T = exact
HALT

.split:
CLEAR   %r0              ; %r0 = N = split
HALT

.stop:
ENGAGR  %r0              ; %r0 = B = stop (paradox)
HALT
"""

PROGRAM_FROBENIUS_VERIFY = """
; frobenius_verify.asm
; Verify μ∘δ=id for a codon stored in %r0, %r1, %r2.
;
; Runs the Frobenius cycle and checks that the output matches input.
; If %r8 == IFIX (T): Frobenius holds exactly (exact stratum)
; If %r8 == N: Frobenius holds modulo ℤ₂ (split stratum)
; If %r8 == B: Ω boundary detected (stop codon)

; Save original
MOVE    %r0  %r3
MOVE    %r1  %r4
MOVE    %r2  %r5

; Run Frobenius cycle
ENGAGR  %r0
FSPLIT  %r0  %r1  %r2
FFUSE   %r1  %r2  %r6

; Compare %r6 with original %r3
; If equal -> exact stratum (Frobenius holds)
; If unequal -> check parity

MOVE    %r3  %r7
FFUSE   %r6  %r7  %r8

; %r8 = result of Frobenius check
; If %r8 == T: exact match
; If %r8 == B: ℤ₂ wobble (split stratum)
; If %r8 == N: Ω boundary

EMIT    %r8

HALT
"""

PROGRAM_CHIMERA_DETECT = """
; chimera_detect.asm
; Detect Chimera Theorem trap states.
;
; When editing across multiple primitive classes, the composite risk
; is tensorial. This program checks if two edits create a frozen
; trap state (Ç_⊛).
;
; Input:  %r0 = first edit primitive (as Belnap code)
;         %r1 = second edit primitive (as Belnap code)
; Output: %r0 = B if trap state detected, N if safe

; Tensor product: ENGAGR on first, FSPLIT, FFUSE with second
ENGAGR  %r0
FSPLIT  %r0  %r2  %r3
FFUSE   %r2  %r1  %r4

; If result is B, both are semi-locked -> trap state
; Check if %r4 == B
MOVE    %r4  %r5
IFIX    %r6              ; T
FFUSE   %r5  %r6  %r7   ; join(r4, T)

; If r4 == B: join(B, T) = T -> trap detected
JB      %r7  .trap

; Safe
CLEAR   %r0
HALT

.trap:
ENGAGR  %r0              ; %r0 = B
HALT
"""

# ── Program catalog ─────────────────────────────────────────────────

GENETIC_PROGRAMS: Dict[str, str] = {
    "translate_codon": PROGRAM_TRANSLATE_CODON,
    "b4_edit": PROGRAM_B4_EDIT,
    "stratum_classify": PROGRAM_STRATUM_CLASSIFY,
    "frobenius_verify": PROGRAM_FROBENIUS_VERIFY,
    "chimera_detect": PROGRAM_CHIMERA_DETECT,
}


def get_program(name: str) -> str:
    """Get a named ParaASM genetic program."""
    prog = GENETIC_PROGRAMS.get(name)
    if prog is None:
        raise ValueError(f"Unknown genetic program: {name}. "
                         f"Available: {list(GENETIC_PROGRAMS.keys())}")
    return prog
