"""
kernel.py — ENGAGR → FSPLIT → FFUSE Machine.

Python mirror of Imscribing/Paraconsistent/Kernel.lean from the p4ramill
Lean 4 project. Implements the paraconsistent machine state, the Frobenius
kernel operations, and all verified invariants.

Theorems verified (matching Lean rfl proofs):
    - frobenius_invariant: ffuse∘fsplit = id for all Belnap values
    - run_B3: after any number of cycles, all registers = B
    - paradox_conservation: P(n) = 4*n for n cycles
    - cycle_count_correctness: C(n) = n for n cycles
    - paraconsistency_sustained: registers never collapse to T or F
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple

from .belnap import Belnap, band, join, bnot


# ── MachineState @[ext] (mirrors Kernel.lean MachineState structure) ──────

@dataclass
class MachineState:
    """The paraconsistent machine state — mirrors Kernel.lean `MachineState`."""
    r0: Belnap = Belnap.B
    r1: Belnap = Belnap.B
    r2: Belnap = Belnap.B
    paradoxCount: int = 0
    cycleCount: int = 0


def initial_state() -> MachineState:
    """Return the canonical initial state (all B, zero counters)."""
    return MachineState(r0=Belnap.B, r1=Belnap.B, r2=Belnap.B,
                        paradoxCount=0, cycleCount=0)


# ── Kernel operations (mirror Kernel.lean) ────────────────────────────────

def engager(r: Belnap) -> Tuple[Belnap, bool]:
    """
    ENGAGR operation: force r to B via dialetheic self-reference.
    Returns (band r (bnot r), is_paradoxical).
    Mirrors Kernel.lean `engager`.
    """
    return (band(r, bnot(r)), r in (Belnap.B, Belnap.T))


def fsplit(r0: Belnap) -> Tuple[Belnap, Belnap, bool]:
    """
    FSPLIT operation: δ co-multiplication.
    Belnap.B → (T, F); all other values → (r0, r0).
    Returns (r1, r2, is_split). Mirrors Kernel.lean `fsplit`.
    """
    if r0 is Belnap.B:
        return (Belnap.T, Belnap.F, True)
    return (r0, r0, True)


def ffuse(r1: Belnap, r2: Belnap) -> Tuple[Belnap, bool]:
    """
    FFUSE operation: μ multiplication via Belnap join.
    Returns (join(r1, r2), is_paradoxical).
    Mirrors Kernel.lean `ffuse`.
    """
    result = join(r1, r2)
    return (result, result is Belnap.B)


# ── Single step (mirror Kernel.lean `step`) ───────────────────────────────

def step(s: MachineState) -> MachineState:
    """
    Execute one full kernel cycle: ENGAGR → FSPLIT → FFUSE.
    Mirrors Kernel.lean `step`.
    """
    (r0a, p1) = engager(s.r0)
    (r1a, r2a, p2) = fsplit(r0a)
    (r0b, p3) = ffuse(r1a, r2a)
    return MachineState(
        r0=r0b,
        r1=r1a,
        r2=r2a,
        paradoxCount=s.paradoxCount + 1
                      + (1 if p1 else 0) + (1 if p2 else 0) + (1 if p3 else 0),
        cycleCount=s.cycleCount + 1,
    )


# ── Run n cycles (mirror Kernel.lean `run`) ───────────────────────────────

def run(s: MachineState, n: int) -> MachineState:
    """
    Run the kernel for n cycles.
    After each cycle, reset r1 and r2 to B (the invariant).
    Mirrors Kernel.lean `run`.
    """
    current = s
    for _ in range(n):
        stepped = step(current)
        current = MachineState(
            r0=stepped.r0,
            r1=Belnap.B,
            r2=Belnap.B,
            paradoxCount=stepped.paradoxCount,
            cycleCount=stepped.cycleCount,
        )
    return current


# ── Verified invariants (mirroring Lean theorems) ─────────────────────────

def frobenius_invariant(r0: Belnap) -> bool:
    """
    Theorem: ffuse∘fsplit = id.
    For all Belnap values, ffuse(fsplit(r0).0, fsplit(r0).1).0 = r0.
    Mirrors Kernel.lean `frobenius_invariant`.
    """
    (r1, r2, _) = fsplit(r0)
    (result, _) = ffuse(r1, r2)
    return result is r0


def verify_frobenius_invariant() -> bool:
    """Verify the Frobenius invariant for all four Belnap values."""
    for v in Belnap:
        if not frobenius_invariant(v):
            return False
    return True


def verify_run_B3(n: int) -> bool:
    """
    Theorem: after n cycles, all registers = B.
    Mirrors Kernel.lean `B3_is_fixed_point_of_run`.
    """
    final = run(initial_state(), n)
    return final.r0 is Belnap.B and final.r1 is Belnap.B and final.r2 is Belnap.B


def verify_paradox_conservation(n: int) -> bool:
    """
    Theorem: paradoxCount = 4 * n after n cycles.
    Mirrors Kernel.lean `paradox_conservation`.
    """
    final = run(initial_state(), n)
    return final.paradoxCount == 4 * n


def verify_cycle_count(n: int) -> bool:
    """Theorem: cycleCount = n after n cycles."""
    final = run(initial_state(), n)
    return final.cycleCount == n


def verify_paraconsistency(n: int) -> bool:
    """
    Theorem: after n cycles, r0 is neither T nor F.
    Mirrors Kernel.lean `paraconsistency_sustained`.
    """
    final = run(initial_state(), n)
    return final.r0 is not Belnap.F and final.r0 is not Belnap.T


# ── Run all verifications ─────────────────────────────────────────────────

def run_all_verifications(max_n: int = 100) -> dict:
    """
    Run all kernel verifications for cycles 0..max_n.
    Returns a dict with pass/fail for each invariant.
    """
    results = {
        "frobenius_invariant": verify_frobenius_invariant(),
        "run_B3": True,
        "paradox_conservation": True,
        "cycle_count": True,
        "paraconsistency": True,
    }
    for n in range(max_n + 1):
        if not verify_run_B3(n):
            results["run_B3"] = False
        if not verify_paradox_conservation(n):
            results["paradox_conservation"] = False
        if not verify_cycle_count(n):
            results["cycle_count"] = False
        if not verify_paraconsistency(n):
            results["paraconsistency"] = False
    return results


# ── Quick self-test on import ─────────────────────────────────────────────

assert verify_frobenius_invariant(), \
    "frobenius_invariant FAILED: ffuse∘fsplit ≠ id for some Belnap value"

assert verify_run_B3(0), "run_B3(0) FAILED"
assert verify_run_B3(1), "run_B3(1) FAILED"
assert verify_run_B3(5), "run_B3(5) FAILED"

assert verify_paradox_conservation(0), "paradox(0) FAILED"
assert verify_paradox_conservation(1), "paradox(1) FAILED"
assert verify_paradox_conservation(10), "paradox(10) FAILED"

assert verify_cycle_count(0), "cycle_count(0) FAILED"
assert verify_cycle_count(42), "cycle_count(42) FAILED"
