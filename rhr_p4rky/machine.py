"""
machine.py — ParaASM Virtual Machine built on the p4rakernel.

Implements the full ParaASM instruction set for the paraconsistent virtual
machine, using the rhr_p4rky kernel (which mirrors the Lean 4 kernel) as
its foundational Belnap logic layer.

Instruction set (from para_vm.py):
    Frobenius core: ENGAGR, FSPLIT, FFUSE, IFIX
    Register ops: MOVE, CLEAR
    Control flow: JMP, JB, JT, JF, JN, CALL, RET, HALT
    Stack: PUSH, POP
    I/O: EMIT, READ

All Belnap operations delegate to rhr_p4rky.belnap and rhr_p4rky.kernel.
"""

from __future__ import annotations
import enum
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .belnap import Belnap, band, bnot, join, meet, designated
from .kernel import MachineState, engager, fsplit, ffuse, step, initial_state


# ── Belnap FOUR re-exported for the VM ────────────────────────────────────
B4 = Belnap  # alias for backward compatibility with para_vm naming

# Re-export all Belnap function names with b4_ prefix for compatibility
b4_join = join
b4_meet = meet
b4_band = band
b4_bnot = bnot
b4_designated = designated
b4_bor = lambda a, b: (lambda r: r if r is not None else Belnap.B)(
    {  # truth-functional OR matching Belnap.lean `bor`
        (Belnap.N, Belnap.N): Belnap.N,
        (Belnap.N, Belnap.T): Belnap.T,
        (Belnap.N, Belnap.F): Belnap.N,
        (Belnap.N, Belnap.B): Belnap.B,
        (Belnap.T, Belnap.N): Belnap.T,
        (Belnap.T, Belnap.T): Belnap.T,
        (Belnap.T, Belnap.F): Belnap.T,
        (Belnap.T, Belnap.B): Belnap.T,
        (Belnap.F, Belnap.N): Belnap.N,
        (Belnap.F, Belnap.T): Belnap.T,
        (Belnap.F, Belnap.F): Belnap.F,
        (Belnap.F, Belnap.B): Belnap.B,
        (Belnap.B, Belnap.N): Belnap.B,
        (Belnap.B, Belnap.T): Belnap.T,
        (Belnap.B, Belnap.F): Belnap.B,
        (Belnap.B, Belnap.B): Belnap.B,
    }.get((a, b))
)

# ── WH2 and dialectic predicates (from belnap.py) ─────────────────────────
b4_to_wh2 = lambda a: {
    Belnap.N: (0, 0), Belnap.T: (0, 1), Belnap.F: (1, 0), Belnap.B: (1, 1)
}[a]
wh2_to_b4 = lambda ab: {
    (0, 0): Belnap.N, (0, 1): Belnap.T, (1, 0): Belnap.F, (1, 1): Belnap.B
}[ab]
b4_approx_le = lambda a, b: (
    True if a is Belnap.N else (True if b is Belnap.B else a is b)
)
b4_dialetheic = lambda a: designated(a) and designated(bnot(a))

_TO_FLUX = {
    Belnap.N: '00', Belnap.T: '01', Belnap.F: '10', Belnap.B: '11'
}


# ── Register ───────────────────────────────────────────────────────────────

class ParaRegister:
    """A single paraconsistent register with flux and paradox tracking."""

    __slots__ = ('flux', 'value', 'paradox_count')

    def __init__(self) -> None:
        self.flux: str = '00'       # Belnap as 2-bit string: N=00, T=01, F=10, B=11
        self.value: Optional[str] = None
        self.paradox_count: int = 0

    def engage(self) -> None:
        """Force register to dialetheic state (B = '11')."""
        self.flux = '11'
        self.paradox_count += 1

    @property
    def is_fixed(self) -> bool:
        return self.value == 'FIXED'

    @property
    def is_active(self) -> bool:
        return self.flux != '00' or self.value is not None

    def get_belnap(self) -> Belnap:
        """Infer Belnap value from flux string."""
        return {
            '00': Belnap.N,
            '01': Belnap.T,
            '10': Belnap.F,
            '11': Belnap.B,
        }.get(self.flux, Belnap.N)

    def set_belnap(self, b: Belnap) -> None:
        """Set flux from a Belnap value."""
        self.flux = _TO_FLUX[b]


# ── Instruction ────────────────────────────────────────────────────────────

@dataclass
class Instr:
    op: str
    args: List[str] = field(default_factory=list)
    source_line: str = ''

    def __str__(self) -> str:
        parts = [self.op] + self.args
        return '  ' + '  '.join(parts)


# ── Control-flow instruction names ────────────────────────────────────────

_CTRL_FLOW = frozenset({
    'jmp', 'jb', 'jt', 'jf', 'jn', 'call', 'ret', 'halt'
})


# ── Assembler (mirrors para_vm.py function) ───────────────────────────────

_LABEL_RE = re.compile(r'^\s*(\.\w+)\s*:(.*)')

def assemble(text: str) -> Tuple[List[Instr], Dict[str, int]]:
    """
    Parse ParaASM source text into (program, label_map).
    label_map maps '.label' strings to instruction indices.
    """
    program: List[Instr] = []
    label_map: Dict[str, int] = {}

    for raw in text.splitlines():
        line = raw.split(';', 1)[0].strip()
        if not line:
            continue
        m = _LABEL_RE.match(line)
        if m:
            label, rest = m.groups()
            label_map[label] = len(program)
            line = rest.strip()
            if not line:
                continue
        parts = line.split()
        program.append(Instr(op=parts[0].upper(), args=parts[1:],
                             source_line=raw.strip()))
    return program, label_map


# ── ParaVM — the virtual machine ──────────────────────────────────────────

class ParaVM:
    """
    Paraconsistent Universal Virtual Machine.

    Runs ParaASM programs with a Belnap FOUR register file, Frobenius kernel,
    control flow, stack, and I/O. All Belnap operations delegate to the
    rhr_p4rky kernel (mirroring the Lean 4 formalization).
    """

    def __init__(self, nregs: int = 16) -> None:
        self.regs: List[ParaRegister] = [ParaRegister() for _ in range(nregs)]
        self.pc: int = 0
        self.program: List[Instr] = []
        self.labels: Dict[str, int] = {}
        self.stack: List[int] = []
        self.halted: bool = False
        self.step_count: int = 0
        self.paradox_count: int = 0
        # Kernel machine state for Frobenius tracking
        self._kstate: MachineState = initial_state()

    def reset(self) -> None:
        """Reset VM to initial state."""
        self.regs = [ParaRegister() for _ in range(len(self.regs))]
        self.pc = 0
        self.program = []
        self.labels = {}
        self.stack = []
        self.halted = False
        self.step_count = 0
        self.paradox_count = 0
        self._kstate = initial_state()

    def load(self, text: str) -> None:
        """Load and assemble a ParaASM program."""
        self.program, self.labels = assemble(text)
        self.pc = 0
        self.halted = False

    def _rd(self, arg: str) -> int:
        """Parse register argument: %rN → int N."""
        m = re.match(r'%r(\d+)', arg)
        if not m:
            raise ValueError(f"Expected register (e.g. %r0), got '{arg}'")
        return int(m.group(1))

    def step_one(self) -> Optional[str]:
        """
        Execute one instruction. Returns a status message or None.
        Fully compatible with the original para_vm.py interface.
        """
        if self.halted:
            return "HALTED"
        if self.pc < 0 or self.pc >= len(self.program):
            self.halted = True
            return "HALTED (PC out of bounds)"

        instr = self.program[self.pc]
        op = instr.op
        args = instr.args
        next_pc = self.pc + 1
        msg = None

        try:
            if op == 'ENGAGR':
                r = self._rd(args[0])
                b = self.regs[r].get_belnap()
                (result, is_paradox) = engager(b)
                self.regs[r].set_belnap(result)
                if is_paradox:
                    self.regs[r].engage()
                    self.paradox_count += 1
                msg = f"ENGAGR %r{r}: {b.value} → {result.value}"

            elif op == 'FSPLIT':
                r_src = self._rd(args[0])
                r_dst1 = self._rd(args[1])
                r_dst2 = self._rd(args[2])
                b = self.regs[r_src].get_belnap()
                (r1, r2, _) = fsplit(b)
                self.regs[r_dst1].set_belnap(r1)
                self.regs[r_dst2].set_belnap(r2)
                msg = f"FSPLIT %r{r_src} → %r{r_dst1}={r1.value} %r{r_dst2}={r2.value}"

            elif op == 'FFUSE':
                r_src1 = self._rd(args[0])
                r_src2 = self._rd(args[1])
                r_dst = self._rd(args[2])
                b1 = self.regs[r_src1].get_belnap()
                b2 = self.regs[r_src2].get_belnap()
                (result, _) = ffuse(b1, b2)
                self.regs[r_dst].set_belnap(result)
                msg = f"FFUSE %r{r_src1}({b1.value}) %r{r_src2}({b2.value}) → %r{r_dst}={result.value}"

            elif op == 'IFIX':
                r = self._rd(args[0])
                self.regs[r].set_belnap(Belnap.T)
                msg = f"IFIX %r{r} → T"

            elif op == 'MOVE':
                r_src = self._rd(args[0])
                r_dst = self._rd(args[1])
                self.regs[r_dst].flux = self.regs[r_src].flux
                msg = f"MOVE %r{r_src} → %r{r_dst}"

            elif op == 'CLEAR':
                r = self._rd(args[0])
                self.regs[r].set_belnap(Belnap.N)
                msg = f"CLEAR %r{r} → N"

            elif op == 'JMP':
                next_pc = self.labels.get(args[0], self.pc)
                msg = f"JMP {args[0]}"

            elif op in ('JB', 'JT', 'JF', 'JN'):
                r = self._rd(args[0])
                b = self.regs[r].get_belnap()
                target_map = {'JB': Belnap.B, 'JT': Belnap.T,
                              'JF': Belnap.F, 'JN': Belnap.N}
                if b is target_map[op]:
                    next_pc = self.labels.get(args[1], self.pc)
                    msg = f"{op} %r{r} ({b.value}) → {args[1]}"
                else:
                    msg = f"{op} %r{r} ({b.value}) not taken"

            elif op == 'CALL':
                self.stack.append(next_pc)
                next_pc = self.labels.get(args[0], self.pc)
                msg = f"CALL {args[0]}"

            elif op == 'RET':
                if self.stack:
                    next_pc = self.stack.pop()
                    msg = f"RET → PC={next_pc}"
                else:
                    self.halted = True
                    msg = "RET (empty stack) → HALT"

            elif op == 'HALT':
                self.halted = True
                msg = "HALT"

            elif op == 'PUSH':
                r = self._rd(args[0])
                b = self.regs[r].get_belnap()
                self.stack.append(b.to_nat())
                msg = f"PUSH %r{r} ({b.value})"

            elif op == 'POP':
                r = self._rd(args[0])
                if self.stack:
                    val = self.stack.pop()
                    b = [Belnap.N, Belnap.T, Belnap.F, Belnap.B][val]
                    self.regs[r].set_belnap(b)
                    msg = f"POP %r{r} → {b.value}"
                else:
                    self.regs[r].set_belnap(Belnap.N)
                    msg = f"POP %r{r} (empty stack) → N"

            elif op == 'EMIT':
                r = self._rd(args[0])
                b = self.regs[r].get_belnap()
                msg = f"EMIT %r{r}: {b.value}"

            elif op == 'READ':
                # Simplified: reads from stdin are handled by the REPL
                pass

            else:
                msg = f"Unknown op: {op}"

        except (ValueError, IndexError, KeyError) as e:
            msg = f"ERROR at PC={self.pc} ({op} {' '.join(args)}): {e}"

        self.pc = next_pc
        self.step_count += 1
        return msg

    def run(self, steps: int = 1) -> List[str]:
        """Execute a number of steps, returning log messages."""
        msgs = []
        for _ in range(steps):
            m = self.step_one()
            if m:
                msgs.append(m)
            if self.halted:
                break
        return msgs

    def get_belnap_counts(self) -> Dict[Belnap, int]:
        """Count Belnap values across all registers."""
        counts = {v: 0 for v in Belnap}
        for r in self.regs:
            b = r.get_belnap()
            counts[b] += 1
        return counts

    def snapshot(self) -> dict:
        """Return full VM state snapshot."""
        return {
            "pc": self.pc,
            "halted": self.halted,
            "step_count": self.step_count,
            "paradox_count": self.paradox_count,
            "registers": [
                {"flux": r.flux, "value": r.value, "paradox": r.paradox_count,
                 "belnap": r.get_belnap().value}
                for r in self.regs
            ],
            "stack": list(self.stack),
            "belnap_counts": {k.value: v for k, v in self.get_belnap_counts().items()},
            "kernel_state": {
                "r0": self._kstate.r0.value,
                "r1": self._kstate.r1.value,
                "r2": self._kstate.r2.value,
                "paradoxCount": self._kstate.paradoxCount,
                "cycleCount": self._kstate.cycleCount,
            }
        }
