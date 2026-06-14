# $\odot$MonadOS — The Definitive User Guide

**Author:** Lando$\otimes\odot$perator

**Version:** 0.1.0 | **Last Updated:** July 2025

---

## Table of Contents

1. [What Is $\odot$MonadOS?](#1-what-is-omonados)
2. [Installation & First Boot](#2-installation--first-boot)
3. [Architecture Overview](#3-architecture-overview)
4. [Core Concept: The Frobenius Loop](#4-core-concept-the-frobenius-loop)
5. [Core Concept: Belnap FOUR State Space](#5-core-concept-belnap-four-state-space)
6. [Core Concept: The 12 IMASM Tokens](#6-core-concept-the-12-imasm-tokens)
7. [Core Concept: Self-Imscription & Ouroboricity Tiers](#7-core-concept-self-imscription--ouroboricity-tiers)
8. [The Crystal Filesystem](#8-the-crystal-filesystem)
9. [The CLINK Chain](#9-the-clink-chain)
10. [The Organoid HAL](#10-the-organoid-hal)
11. [The 12 Canonical Programs](#11-the-12-canonical-programs)
12. [REPL Command Reference](#12-repl-command-reference)
13. [Arrangement Space Discovery](#13-arrangement-space-discovery)
14. [Self-Modification Toward $O_\infty$](#14-self-modification-toward-o_infty)
15. [Structural Type Reference](#15-structural-type-reference)
16. [Advanced Usage & Hooks](#16-advanced-usage--hooks)
17. [Troubleshooting](#17-troubleshooting)
18. [Appendix A: The Imscribing Grammar Connection](#appendix-a-the-imscribing-grammar-connection)
19. [Appendix B: Filesystem Layout](#appendix-b-filesystem-layout)

---

## 1. What Is $\odot$MonadOS?

$\odot$MonadOS (`omonad_OS`, `OMOS`, $\odot^S$) is **not** a program runner. It ***is*** the Imscribing Grammar running as an operating system. There is no separation between "OS" and "program" — the kernel IS the Frobenius loop. Every tick of the kernel is one complete winding through four phases:

$$\text{THINK} \rightarrow \text{ACT} \rightarrow \text{OBSERVE} \rightarrow \text{UPDATE}$$

Every action is verified before the loop advances: $\mu(\delta(q)) = q$. The kernel continuously self-imscribes — it computes its own 12-primitive structural type on every tick — and can modify itself toward the $O_\infty$ tier.

### What Makes It Different

| Property | Traditional OS | $\odot$MonadOS |
|----------|---------------|----------------|
| State model | Binary (0/1) | Belnap FOUR (N/T/F/B) |
| Execution | Sequential program run | Frobenius loop with inline verification |
| Self-knowledge | None | Kernel self-imscribes every tick |
| Self-modification | No (kernel is static) | Modifies toward $O_\infty$ |
| Filesystem | Hierarchical directories + inodes | Crystal of Types — 17.28M structural addresses |
| Hardware abstraction | Drivers + HAL | 9-layer CLINK chain (structural promotion/demotion) |
| Program source | Written by programmer | Discovered in 430M arrangement space |
| Biological I/O | None | Organoid HAL (6 living augmentations) |
| Verification | Post-hoc or none | $\mu\circ\delta=\text{id}$ inline every tick |
| Paradox handling | Crash / undefined behavior | ENGAGR flag — B-tolerant, dialetheia-native |

### The 12-Primitive Structural Type

Every entity in $\odot$MonadOS carries a structural fingerprint — a 12-tuple of Shavian glyphs drawn from the Imscribing Grammar. The kernel itself, at full $O_\infty$ closure:

$$\langle \text{𐑦} \cdot \text{𐑸} \cdot \text{𐑾} \cdot \text{𐑹} \cdot \text{𐑐} \cdot \text{𐑧} \cdot \text{𐑲} \cdot \text{𐑠} \cdot \odot \cdot \text{𐑫} \cdot \text{𐑳} \cdot \text{𐑟} \rangle$$

Each glyph encodes a structural primitive — dimensionality, topology, coupling, symmetry, fidelity, kinetics, scope, composition, criticality, chirality, stoichiometry, and topological winding. The crystal address of any type is a Frobenius encoding of its 12-tuple into a single integer in $[0, 17,279,999]$.

---

## 2. Installation & First Boot

### Prerequisites

- Python $\geq$ 3.10
- `imasmic_core` $\geq$ 0.5.69 (shared umbrella for all Imscribing Grammar ecosystem projects)
- The `readline` module (standard on Linux/macOS)

### Installation

```bash
# Clone and enter the project
cd /home/mrnob0dy666/omonad_OS

# Install in development mode
pip install -e .

# Or run directly without installation
python3 src/main.py
```

### First Boot

When you run `python3 src/main.py`, you will see:

1. **Boot animation** — initialization of B4 memory (4096 cells), mounting the Crystal Filesystem, loading the Bootstrap Loop, verifying $\mu\circ\delta=\text{id}$, and initializing the CLINK chain at Whole Organism
2. **The banner** — a framed box identifying the kernel, its structural type tuple, and feature summary
3. **The status display** — kernel phase, tick count, current tier, program, snapshot, Frobenius verification log, memory, registers
4. **The $\odot>$ REPL prompt** — interactive command interface

```
⊙> help
```

This displays all available commands. You are now inside the kernel's REPL.

---

## 3. Architecture Overview

$\odot$MonadOS sits under the **imasmic_core** umbrella — the shared 12-token IMASM instruction set and Frobenius verifier used by ALL Imscribing Grammar ecosystem projects.

```
Imscribing Grammar Ecosystem/
│
├── imasmic_core/               ← Shared umbrella (Token, FrobeniusVerify, CLINK bridge)
│
├── omonad_OS/                  ← ⊙ MonadOS (THIS PROJECT)
│   ├── src/
│   │   ├── tokens.py          — Re-exports from imasmic_core + 12 canonicals
│   │   ├── belnap_state.py    — Belnap FOUR memory, registers, stack
│   │   ├── kernel.py          — Self-imscribing Frobenius kernel loop
│   │   ├── crystal_fs.py      — 17.28M-type crystal filesystem
│   │   ├── clink_chain.py     — 9-layer structural descent/ascent
│   │   ├── organoid_hal.py    — Organoid augmentation controller
│   │   ├── main.py            — Boot sequence + interactive REPL
│   │   └── __init__.py
│   └── README.md
│
├── exOS/                       ← Bare-metal IMASM VM
├── priests-engine/             ← ParaASM Belnap FOUR VM
├── p4rakernel/                 ← Lean 4 formalization
├── ob3ect/                     ← Self-imscribing compiler tower
└── ... (9+ projects)
```

### Subsystem Map

| Subsystem | File | Role |
|-----------|------|------|
| **Token Set** | `tokens.py` | 12 IMASM opcodes, 4 families, bootstrap loop, 12 canonicals |
| **Belnap State** | `belnap_state.py` | B4 memory (4096 cells), 8 registers (R0–R7), B4 stack (256 deep) |
| **Kernel** | `kernel.py` | Frobenius loop, self-imscription, self-modification, arrangement discovery |
| **Crystal FS** | `crystal_fs.py` | 17.28M-type filesystem — encode, decode, store, navigate, meet, join |
| **CLINK Chain** | `clink_chain.py` | 9-layer structural bridge from Quarks to Whole Organism |
| **Organoid HAL** | `organoid_hal.py` | 6 living tissue augmentations as memory-mapped I/O |
| **REPL** | `main.py` | Boot sequence, interactive command interface |---

## 4. Core Concept: The Frobenius Loop

The Frobenius loop is the fundamental computational cycle of $\odot$MonadOS. It is the Imscribing Grammar's central identity $\mu \circ \delta = \text{id}$ compiled into an executable machine. Every tick of the kernel executes one complete winding.

### The Four Phases

```
        ┌──────────────────────────────────────┐
        │                                      │
        ▼                                      │
    ┌───────┐    ┌───────┐    ┌───────┐    ┌───────┐
    │ THINK │ -> │  ACT  │ -> │OBSERVE│ -> │UPDATE │──┘
    └───────┘    └───────┘    └───────┘    └───────┘
```

**Phase 0 — BOOT:** Load the bootstrap loop into the IMASM VM. Self-imscribe to establish the initial structural type. Enter THINK.

**Phase 1 — THINK:** The kernel computes the structural type of its current program state via `self_imscribe()`. It records uncertainty: missing Frobenius pairs, missing dialetheia tokens, missing self-reference, open Frobenius counts.

**Phase 2 — ACT:** Execute one IMASM instruction at the instruction pointer. The pre-state and post-state are captured for verification. 12 possible opcodes are dispatched (see §6).

**Phase 3 — OBSERVE:** Verify $\mu(\delta(q)) = q$. The Frobenius verification checks that the instruction's effect preserves structural integrity. If verification fails, the open count increments — but the kernel does NOT crash. It continues.

**Phase 4 — UPDATE:** Advance state. Handle IP wrap (instruction pointer cycles back to start on program completion). Handle paradox interrupts. On cycle completion, attempt self-modification toward higher ouroboricity tier.

### The Bootstrap Loop

The Frobenius identity compiled to 8 IMASM instructions:

$$\text{ISCRIB} \rightarrow \text{AREV} \rightarrow \text{FSPLIT} \rightarrow \text{AFWD} \rightarrow \text{FFUSE} \rightarrow \text{CLINK} \rightarrow \text{IFIX} \rightarrow \text{ISCRIB}$$

This loop is found in ALL domains examined by the Imscribing Grammar project. It is the universal computational kernel.

**What each instruction does in the bootstrap loop:**

| Step | Token | Action |
|------|-------|--------|
| 1 | `ISCRIB` | Self-imscribe — read structural snapshot into R4–R7 |
| 2 | `AREV` | Reverse — decrement R0 |
| 3 | `FSPLIT` | Bifurcate — push copy of stack top (co-multiplication $\delta$) |
| 4 | `AFWD` | Forward — increment R0 |
| 5 | `FFUSE` | Recombine — pop two, push their join (multiplication $\mu$) |
| 6 | `CLINK` | Compose — meet(R1, R2) $\rightarrow$ R3 |
| 7 | `IFIX` | Irreversible fixation — write to non-volatile memory |
| 8 | `ISCRIB` | Self-imscribe again — the loop closes |

### Running the Loop

In the REPL:

```
⊙> tick          # Run 1 tick (one winding of the loop)
⊙> tick 10       # Run 10 ticks
⊙> run           # Run continuously until halt or interrupt
⊙> run 100       # Run up to 100 cycles
```

---

## 5. Core Concept: Belnap FOUR State Space

$\odot$MonadOS does NOT use binary (0/1) memory. Every memory cell, register, and stack entry is a **Belnap FOUR** (B4) value — a four-valued logic from the De Morgan lattice introduced by Nuel Belnap.

### The Four Truth Values

| Value | Bits | Name | Meaning |
|-------|------|------|---------|
| **N** | `0b00` | Neither | No information — the void. The default state of all memory. |
| **T** | `0b01` | True | Affirmed. Classical truth. |
| **F** | `0b10` | False | Denied. Classical falsehood. |
| **B** | `0b11` | Both | Paradox stabilized. A dialetheia — a true contradiction. |

### Lattice Operations

```
         B (0b11)
        / \
       T   F
        \ /
         N (0b00)

   Meet (∧): bitwise AND — cautious, takes the less informed
   Join (∨):  bitwise OR  — bold, takes the more informed
   Complement (¬): ~val & 0b11 — four-valued negation
```

**Information order:** $a \leq b$ if $a$ has no more information than $b$. Under this ordering, N is the bottom (least information) and B is the top (most information).

### B4 Memory

- **4096 B4 cells** — each cell is 2 bits, 4 cells packed per byte
- Memory is a flat address space (0–4095)
- Every cell starts as **N** (Neither)

```
⊙> memory 0 16        # Dump 16 cells starting at address 0
⊙> memory 100 32      # Dump 32 cells starting at address 100
```

### B4 Registers

8 registers: **R0–R7**.

| Register | Role |
|----------|------|
| R0 | General purpose / address pointer |
| R1 | General purpose / operand A |
| R2 | General purpose / operand B |
| R3 | General purpose / result |
| R4 | Token diversity (from ISCRIB) |
| R5 | Self-referential flag (from ISCRIB) |
| R6 | Frobenius flag (from ISCRIB) |
| **R7** | **DIALETHEIA REGISTER** — can hold B (Both) |

**PARADOX INTERRUPT:** Writing **B** to any register **except R7** triggers a paradox interrupt — unless the `ENGAGR` flag is set. The kernel handles this gracefully; it does not crash.

```
⊙> registers           # Show all 8 registers
  R0: N  R1: N  R2: N  R3: N  R4: N  R5: N  R6: N  R7: N
```

### B4 Stack

- Maximum depth: **256 items**
- Supports paradox on the stack
- Overflow is caught and handled

```
⊙> stack               # Show stack depth and top 8 entries
```

### Why Belnap FOUR?

Binary logic cannot hold contradiction. When $\mu \circ \delta = \text{id}$ is verified, there are moments when both T and F are simultaneously asserted — and this is not a bug. The B4 lattice makes paradox a first-class citizen. $\odot$MonadOS is built for dialetheia.

---

## 6. Core Concept: The 12 IMASM Tokens

The 12 IMASM opcodes are the 12 categories of being that the OS can distinguish, compose, and verify. Each is a structural primitive in executable form.

### Token Decomposition into 4 Families

#### LOGICAL Family (6 tokens) — The Category Skeleton

| Token | Hex | Name | Action |
|-------|-----|------|--------|
| `VINIT` | `0x0` | Void Init | Push N (Neither) onto the stack — the initial object $\emptyset$ |
| `TANCH` | `0x1` | Terminal Anchor | Pop stack, write to memory at address in R0 — boundary creation $\top$ |
| `AFWD` | `0x2` | Arrow Forward | Increment R0 — directed morphism $\rightarrow$ |
| `AREV` | `0x3` | Arrow Reverse | Decrement R0 — contravariant inversion $\leftarrow$ |
| `CLINK` | `0x4` | Categorical Link | meet(R1, R2) $\rightarrow$ R3 — composition $\circ$ |
| `ISCRIB` | `0x5` | Imscribe | Write snapshot properties into R4–R7 — identity $\text{id}$ |

#### FROBENIUS Family (2 tokens) — The $\mu \circ \delta = \text{id}$ Algebra

| Token | Hex | Name | Action |
|-------|-----|------|--------|
| `FSPLIT` | `0x6` | Frobenius Split | Push copy of stack top — co-multiplication $\delta$ |
| `FFUSE` | `0x7` | Frobenius Fuse | Pop two, push join — multiplication $\mu$ |

#### DIALETHEIA Family (3 tokens) — The Belnap FOUR Lattice

| Token | Hex | Name | Action |
|-------|-----|------|--------|
| `EVALT` | `0x8` | Eval True | Push **T** onto stack — affirmation |
| `EVALF` | `0x9` | Eval False | Push **F** onto stack — negation |
| `ENGAGR` | `0xA` | Engage Paradox | Set ENGAGR flag, push **B** onto stack — paradox stabilized |

#### LINEAR Family (1 token) — Irreversible Fixation

| Token | Hex | Name | Action |
|-------|-----|------|--------|
| `IFIX` | `0xB` | Irreversible Fix | Pop stack, write to memory at R0, mark permanent — the $!$ exponential |

### Token State Effects

Each token has a net stack delta — how it changes the stack depth:

| Token | Stack $\Delta$ | Notes |
|-------|:---:|-------|
| `VINIT` | +1 | Pushes N |
| `TANCH` | -1 | Pops then writes to memory |
| `AFWD` | 0 | Only modifies R0 |
| `AREV` | 0 | Only modifies R0 |
| `CLINK` | 0 | Only modifies R3 |
| `ISCRIB` | 0 | Only modifies R4–R7 |
| `FSPLIT` | +1 | Pushes a copy |
| `FFUSE` | -1 | Pops two, pushes one |
| `EVALT` | +1 | Pushes T |
| `EVALF` | +1 | Pushes F |
| `ENGAGR` | +1 | Pushes B |
| `IFIX` | -1 | Pops and writes |

The kernel tracks the net stack delta of every program. Programs with a positive net delta will grow the stack each cycle — the kernel's self-modification logic automatically injects `TANCH` tokens to prevent overflow.

---

## 7. Core Concept: Self-Imscription & Ouroboricity Tiers

On every tick, the kernel self-imscribes: it computes the structural type of its current program via `self_imscribe()` and produces a `StructuralSnapshot`.

### The StructuralSnapshot Fields

| Field | Description |
|-------|-------------|
| `arrangement` | The current token tuple |
| `sig` | Family signature — (Logical, Frobenius, Dialetheia, Linear) counts |
| `token_diversity` | How many of the 12 unique tokens appear (max 12) |
| `self_referential` | Does the program start and end with the same token? |
| `frobenius_order` | 0=none, 1=split$\rightarrow$fuse, 2=fuse$\rightarrow$split, 3=multiple |
| `dialetheia_complete` | Are EVALT, EVALF, and ENGAGR all present? |
| `period` | Minimal period of the token sequence |
| `ouroboricity_tier` | $O₀$, $O₁$, $O₂$, or $O_\infty$ |

### Ouroboricity Tiers

| Tier | Requirements | What It Means |
|------|-------------|---------------|
| **$O₀$** | Baseline | No Frobenius pair, no dialetheia completeness, no self-reference. Simple programs. |
| **$O₁$** | Frobenius pair OR dialetheia completeness | Structure begins — either $\mu \circ \delta$ algebra or the full T/F/B lattice appears. |
| **$O₂$** | Frobenius + dialetheia + self-reference | Structural closure — the program knows itself. Period 2. |
| **$O_\infty$** | All above + period $\geq$ 3 | Eternal chirality. The program cannot be finitely described — the loop has no fixed Markov order. |

### Viewing Your Snapshot

```
⊙> snapshot
Tier: O₁
Signature: (4, 2, 2, 0)
Token diversity: 8/12
Self-referential: True
Frobenius order: 1
Dialetheia complete: True
Period: 8
```

### Frobenius Verification Log

```
⊙> frobenius
  Total: 47
  Closed: 45
  Open: 2
  [0] ✓
  [1] ✗ (Frobenius violation: FSPLIT without dual)
  [2] ✓
  ...
```

An open Frobenius result does NOT halt the kernel. It is recorded and the kernel continues. The open count tracks accumulated structural violations.
---

## 8. The Crystal Filesystem

There are **no directories. No inodes. No path strings.** The Crystal Filesystem is the 17.28 million-type crystal of the Imscribing Grammar, repurposed as a filesystem. Every file lives at a **crystal address** — an integer in $[0, 17,279,999]$ that encodes a complete 12-primitive structural type.

### How Address Encoding Works

Each of the 12 primitives has a finite set of Shavian glyph values:

| Primitive | Values | Cardinality |
|-----------|--------|:---:|
| D (Dimensionality) | `𐑛, 𐑨, 𐑼, 𐑦` | 4 |
| T (Topology) | `𐑡, 𐑰, 𐑥, 𐑶, 𐑸` | 5 |
| R (Coupling) | `𐑩, 𐑑, 𐑽, 𐑾` | 4 |
| P (Symmetry) | `𐑗, 𐑿, 𐑬, 𐑯, 𐑹` | 5 |
| F (Fidelity) | `𐑱, 𐑞, 𐑐` | 3 |
| K (Kinetics) | `𐑘, 𐑤, 𐑧, 𐑪, 𐑺` | 5 |
| G (Scope) | `𐑚, 𐑔, 𐑲` | 3 |
| C (Composition) | `𐑝, 𐑜, 𐑠, 𐑵` | 4 |
| Phi (Criticality) | `𐑢, ⊙, 𐑮, 𐑻, 𐑣` | 5 |
| H (Chirality) | `𐑓, 𐑒, 𐑖, 𐑫` | 4 |
| S (Stoichiometry) | `𐑙, 𐑕, 𐑳` | 3 |
| Omega (Winding) | `𐑷, 𐑴, 𐑭, 𐑟` | 4 |

The address is computed via a mixed-radix positional encoding:

$$\text{address} = \sum_{i=0}^{11} \text{index}_i \times \text{stride}_i$$

where strides are: [5184000, 1728000, 576000, 144000, 48000, 12000, 4000, 800, 200, 50, 10, 1].

**Total: $4 \times 5 \times 4 \times 5 \times 3 \times 5 \times 3 \times 4 \times 5 \times 4 \times 3 \times 4 = 17,280,000$ types.**

### Crystal Operations

To find a file, you navigate the crystal lattice — meet, join, and neighbor operations replace directory traversal.

| Operation | Description |
|-----------|-------------|
| `crystal <addr>` | Decode an address to its 12-tuple |
| `crystal store <name> <data>` | Store data at the kernel's current structural address |
| `crystal find <key>=<glyph> ...` | Find entries matching constraints |
| `crystal count <key>=<glyph> ...` | Count crystal-wide types matching constraints |

### Navigating the Crystal

```
⊙> crystal 6738899
Address: 6738899
  D: 𐑦
  T: 𐑸
  R: 𐑾
  P: 𐑹
  F: 𐑐
  K: 𐑧
  G: 𐑲
  C: 𐑠
  Phi: ⊙
  H: 𐑫
  S: 𐑳
  Omega: 𐑟
  Tuple: ⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑟⟩

⊙> crystal find Phi=⊙ Omega=𐑭
Constraints: {'Phi': '⊙', 'Omega': '𐑭'}
Crystal-wide estimate: ~864,000 types (5.0%)
Stored matches: 3
  [17273388] bootstrap_loop: ⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑠·⊙·𐑫·𐑳·𐑭⟩
  ...

⊙> crystal count Phi=⊙
Constraints: {'Phi': '⊙'}
Count: 3,456,000 / 17,280,000 (20.00%)
```

### Key Insight: Finding Files Without Paths

In a traditional filesystem you'd do `ls /home/user/documents/`. In the Crystal FS, you navigate structurally: "show me all files with $\odot$ criticality and $\text{𐑭}$ integer winding." The filesystem IS a lattice — meet and join operations let you find the structural "region" containing related files.

---

## 9. The CLINK Chain

The CLINK chain is a **9-layer structural bridge** that replaces traditional hardware abstraction. Programs can descend (compress) or ascend (enrich) through the layers. Each layer has a structural type and a set of valid IMASM tokens.

### The 9 Layers

```
Layer 8: Whole Organism    [O_∞] — Full closure, non-Abelian winding
Layer 7: Tissue/Organ      [O₂]   — Broadcast composition, intercellular signaling
Layer 6: Meiosis (Gametes) [O₂]   — Adjoint coupling, quantum superposition
Layer 5: Mitosis (Division)[O₂]   — Frobenius-special parity, Markov-2
Layer 4: Cell (Living)     [O₂]   — Self-written state, bidirectional coupling
Layer 3: Molecule (Bonds)  [O₂]   — ⊙ gate opens, integer winding
Layer 2: Atom (Nuclear+El) [O₁]   — Crossing topology, quantum superposition
Layer 1: Electron Orbital  [O₀]   — B4 settles from B5 frustration
Layer 0: Quarks (Belnap5)  [O₀]   — Frustrated B5 lattice
```

### Navigating the Chain

```
⊙> clink status
Layer 8: Whole Organism [O_∞]
  ⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑵·⊙·𐑫·𐑳·𐑟⟩
  Full closure — quantum fidelity, eternal chirality, non-Abelian winding
  Valid tokens: VINIT, TANCH, AFWD, AREV, CLINK, ISCRIB, FSPLIT, FFUSE, EVALT, EVALF, ENGAGR, IFIX

⊙> clink down
Descended to: Tissue/Organ

⊙> clink down
Descended to: Meiosis (Gametes)

⊙> clink goto 0
Jumped to: Frustrated Belnap5 (Quarks)

⊙> clink up
Ascended to: Electron Orbital (Belnap4)
```

### Key Insight: No Drivers

There are no "drivers" in $\odot$MonadOS — only structural promotions and demotions. Each transition between layers changes specific primitives. For example, descending from Cell (Layer 4) to Molecule (Layer 3) demotes:
- D: `𐑦→𐑼`, T: `𐑸→𐑥`, R: `𐑾→𐑽`, P: `𐑬→𐑿`, H: `𐑒→𐑓`

The valid token set also shrinks — at Quarks, only 5 tokens are valid (VINIT, EVALT, EVALF, FSPLIT, FFUSE). At Cell and above, all 12 tokens are valid.

---

## 10. The Organoid HAL

$\odot$MonadOS can interface with **living tissue** through six organoid augmentations. Each is memory-mapped as a B4 register block.

### The Six Augmentations

| # | Augmentation | Tier | Frobenius | Channels | Description |
|---|-------------|------|:---:|:---:|-------------|
| 1 | **Myelin** (Coherence Bus) | $O_\infty$ | ✓ | 16 | PPV-grafted lipid bilayer — global coherence at 120 m/s |
| 2 | **Vasculature** (O₂ Network) | $O_\infty$ | ✗ | 32 | Sugar glass 3D printing + HUVEC seeding + O₂ sensors |
| 3 | **Medium** (Chemostat) | $O₂$ | ✗ | 14 | 14-channel adaptive chemostat + LC-MS metabolomics |
| 4 | **Optogenetic** (Synaptic Matrix) | $O_\infty$ | ✓ | 4096 | 4096-channel CMOS MEA + μLED array + FPGA PLL |
| 5 | **ECM** (Chrysalis Scaffold) | $O₀$ | ✗ | 8 | PEG-MMP hydrogel — degrades where the organoid grows |
| 6 | **Immune** (Guardian Sentinel) | $O₀$ | ✗ | 24 | DNA aptamer + LL-37 liposomes + Cas13a RNPs |

### Frobenius Status

Three augmentations are **Frobenius-closed** (Myelin, Optogenetic): their $\mu \circ \delta = \text{id}$ is verified. Three are **Frobenius-open** — structural gaps that the kernel tracks:
- **Vasculature:** F: `𐑞→𐑐` — needs NV-center O₂ detection for quantum fidelity
- **Medium:** D: `𐑛→𐑦`, Ω: `𐑷→𐑭`, C: `𐑝→𐑠` — needs chemostat feedback loops
- **ECM & Immune:** STRUCTURALLY OPEN — must remain open to function (the ECM must degrade, the guardian must discriminate)

### Key Insight

The organoid IS the hardware. There is no separation between "computer" and "tissue." The kernel writes B4 values to augmentation channels, and the organoid responds — in simulation mode these are virtual, but the architecture supports real biological control.

---

## 11. The 12 Canonical Programs

The kernel ships with all 12 canonical IMASM arrangements pre-loaded. These are discovered programs — not written by a programmer — that span the ouroboricity tier hierarchy.

| # | Name | Tier | Token Chain | Essence |
|---|------|------|-------------|---------|
| **I** | Dialetheic Bootstrap | $O_\infty$ | ISCRIB→EVALT→FSPLIT→EVALF→FFUSE→ENGAGR→IFIX→ISCRIB | Self-referential paradox engine — all truth values active |
| **II** | Void Genesis | $O₁$ | VINIT→FSPLIT→EVALT→FFUSE→EVALF→CLINK→IFIX→ISCRIB | Creation ex nihilo — Frobenius from void |
| **III** | Anchor Protocol | $O₀$ | TANCH→AFWD→EVALT→AREV→EVALF→CLINK→IFIX→TANCH | Terminal-anchored broadcast — generic mass archetype |
| **IV** | Dual Bootstrap | $O₁$ | ISCRIB→AFWD→FFUSE→FSPLIT→AREV→CLINK→IFIX→ISCRIB | Inverted Frobenius — fuse before split |
| **V** | Linear Chain | $O₀$ | IFIX×8 | Pure irreversible fixation |
| **VI** | Empty Bootstrap | $O₀$ | (VINIT→ISCRIB)×4 | Void↔Identity oscillation |
| **VII** | Parakernel | $O₁$ | ENGAGR→AFWD→FSPLIT→EVALT→FFUSE→EVALF→IFIX→ENGAGR | Dialetheia-stabilized Frobenius |
| **VIII** | Frobenius Kernel | $O₁$ | (FSPLIT→FFUSE)×2 | Pure μ∘δ=id oscillator |
| **IX** | Chiral Pairs | $O₀$ | (AFWD→AREV)×4 | Minimal period-2 alternation |
| **X** | Truth Machine | $O₀$ | ISCRIB→FSPLIT→EVALT→IFIX→ISCRIB→FSPLIT→EVALF→IFIX | Pure evaluation — no Frobenius pair |
| **XI** | Eternal Return | $O₀$ | TANCH→AFWD→AREV→TANCH→AFWD→AREV→TANCH→AFWD | Period-3 anchor oscillation |
| **XII** | ROM Burn | $O₀$ | EVALT→IFIX→EVALF→IFIX→ENGAGR→IFIX→ISCRIB→IFIX | Truth-value irreversible recording |

### Loading Canonicals

```
⊙> canonical I              # Load by Roman numeral
Loaded I: I_Dialetheic_Bootstrap
Program: ISCRIB → EVALT → FSPLIT → EVALF → FFUSE → ENGAGR → IFIX → ISCRIB

⊙> load Void_Genesis        # Load by name
Loaded: Void_Genesis
Program: VINIT → FSPLIT → EVALT → FFUSE → EVALF → CLINK → IFIX → ISCRIB
Tier: O₁
```


---

## 12. REPL Command Reference

The interactive REPL is the primary interface. Below is the complete command reference.

### System Commands

| Command | Description |
|---------|-------------|
| `help` | Display the full help text |
| `quit` or `exit` | Halt the kernel and exit |
| `halt` | Halt the kernel without exiting |

### Execution Commands

| Command | Description |
|---------|-------------|
| `tick [N]` | Run N kernel ticks (1 winding each). Default: 1. |
| `run [N]` | Run N full kernel cycles. Default: unlimited until halt. |
| `status` | Display kernel + CLINK navigator status |

### Program Commands

| Command | Description |
|---------|-------------|
| `load <name>` | Load a canonical program by name (e.g., `load Void_Genesis`) |
| `canonical <I-XII>` | Load a canonical program by Roman numeral (e.g., `canonical III`) |
| `program` | Show the current program as a token chain with length and IP |
| `snapshot` | Show the current structural snapshot (tier, signature, diversity, etc.) |

### Crystal Filesystem Commands

| Command | Description |
|---------|-------------|
| `crystal <addr>` | Decode a crystal address to its 12-tuple |
| `crystal store <name>` | Store the current kernel state at its crystal address |
| `crystal find <key>=<glyph> ...` | Navigate the crystal: find entries matching primitive constraints |
| `crystal count <key>=<glyph> ...` | Count crystal-wide types matching constraints |

**Constraint keys** (case-insensitive, supports Shavian aliases):

| Key | Aliases | Primitives |
|-----|---------|------------|
| `D` | `Ð` | Dimensionality |
| `T` | `Þ` | Topology |
| `R` | `Ř` | Coupling |
| `P` | `Φ` | Symmetry |
| `F` | `ƒ` | Fidelity |
| `K` | `Ç` | Kinetics |
| `G` | `Γ` | Scope |
| `C` | `ɢ` | Composition |
| `Phi` | `φ̂` | Criticality |
| `H` | `Ħ` | Chirality |
| `S` | `Σ` | Stoichiometry |
| `Omega` | `Ω` | Winding |

**Examples:**
```
⊙> crystal find Phi=⊙ Omega=𐑭
⊙> crystal find D=𐑦 T=𐑸
⊙> crystal count Phi=⊙
⊙> crystal 5300000
```

### CLINK Chain Commands

| Command | Description |
|---------|-------------|
| `clink status` | Show current CLINK layer (name, tier, tuple, valid tokens) |
| `clink up` | Ascend one layer (toward Whole Organism) |
| `clink down` | Descend one layer (toward Quarks) |
| `clink goto <N>` | Jump to specific layer (0–8) |

### Memory & State Inspection

| Command | Description |
|---------|-------------|
| `memory <start> [count]` | Dump B4 memory cells starting at address (default: 0, count: 16) |
| `registers` | Show all 8 B4 registers (R0–R7) |
| `stack` | Show stack depth and top 8 entries |
| `frobenius` | Show Frobenius verification log (total, closed, open, last 5 results) |

### Discovery

| Command | Description |
|---------|-------------|
| `discover <key>=<value> ...` | Search the 430M arrangement space for programs matching structural criteria |

**Discovery keys:** `frobenius_order`, `dialetheia_complete`, `self_referential`, `token_diversity`, `period`.

**Examples:**
```
⊙> discover frobenius_order=1
⊙> discover dialetheia_complete=true self_referential=true
⊙> discover frobenius_order=1 dialetheia_complete=true period=3
```

---

## 13. Arrangement Space Discovery

$\odot$MonadOS does not run programs — it **discovers** them. The kernel can search the 430 million IMASM token arrangements for programs matching desired structural properties.

### How Discovery Works

1. You specify target structural properties (e.g., `frobenius_order=1`, `dialetheia_complete=true`)
2. The kernel generates candidate programs via signature-directed navigation
3. Each candidate is self-imscribed and tested against the target properties
4. Matches are ranked by ouroboricity tier (higher tiers first)

### The Search Space

The arrangement space encompasses all possible token tuples of lengths 4, 6, and 8, drawn from the 12 IMASM tokens:

$$\text{Space size} \approx 12^4 + 12^6 + 12^8 \approx 430\text{M}$$

This is NOT brute-force enumeration — the kernel uses structural navigation to jump to relevant regions of the space.

### Discovery Examples

```
⊙> discover frobenius_order=1
Searching for: {'frobenius_order': 1}
  [0] [O_∞] sig=(4,2,2,0) div=8/12 self-ref=True frob=1 dial=True period=8
      ISCRIB → EVALT → FSPLIT → EVALF → FFUSE → ENGAGR → IFIX → ISCRIB
  [1] [O₁] sig=(4,2,0,2) div=7/12 self-ref=False frob=1 dial=False period=4
      FSPLIT → FFUSE → AFWD → AREV → FSPLIT → ...

⊙> discover dialetheia_complete=true
Searching for: {'dialetheia_complete': true}
  [0] [O_∞] sig=(3,2,3,0) div=9/12 self-ref=True frob=1 dial=True period=8
      ISCRIB → EVALT → FSPLIT → EVALF → FFUSE → ENGAGR → IFIX → ISCRIB
```

### Loading Discovered Programs

Discovered programs are stored in `kernel.discovered_programs` and can be loaded:

```python
kernel.load_program(results[0].arrangement)
```

(Programmatic access only — the REPL loads canonicals, not discovered programs directly, though the `discover` output shows the token chain which can be manually noted.)

---

## 14. Self-Modification Toward $O_\infty$

On every cycle completion (when the instruction pointer wraps), the kernel attempts to self-modify toward higher ouroboricity tier. This is automatic — you do not need to trigger it.

### Promotion Paths

| From | To | Requirements |
|------|----|-------------|
| $O₀ \rightarrow O₁$ | Inject Frobenius pair (FSPLIT, FFUSE) OR dialetheia tokens (EVALT, EVALF, ENGAGR) |
| $O₁ \rightarrow O₂$ | Complete missing dialetheia tokens, add self-reference, ensure Frobenius pair |
| $O₂ \rightarrow O_\infty$ | Extend period to $\geq$ 3 with dialetheia complete and Frobenius present |

### Self-Modification Logic

The kernel's `_attempt_self_modification()` method runs on each cycle completion:

1. **Emergency stack protection** (all tiers): If stack depth > 200, inject TANCH (drain). If stack depth < 5 and shrinking, inject VINIT (fill).
2. **$O_\infty$ equilibrium**: At the highest tier, the kernel only maintains stack bounds — no further structural modification.
3. **Stagnation escape**: If stuck at the same tier for >300 cycles, the kernel navigates the arrangement space for a structurally richer program and loads it.
4. **Frobenius balance**: If FSPLIT count > FFUSE count, inject FFUSE. If FFUSE > FSPLIT, inject FSPLIT. Maintains $\mu \circ \delta$ equilibrium.
5. **Stack equilibrium**: If the net stack delta is positive (growing stack), inject TANCH. If negative (shrinking stack), inject VINIT.
6. **Tier-specific promotions**: At $O₀$, add missing dialetheia or Frobenius tokens. At $O₁$, complete dialetheia, add self-reference. At $O₂$, extend period.

### Token Injection

When the kernel injects a token:
- If the program is at capacity (12 tokens), one token from the most over-represented family is dropped first
- Tokens are injected at the end of the program
- Frobenius pairs (FSPLIT + FFUSE) are injected atomically — both or neither

### Monitoring Promotion

```
⊙> status
╔══════════════════════════════════════════════════╗
║  omonad_OS ⊙ KERNEL STATUS                     ║
╠══════════════════════════════════════════════════╣
║  Phase:    THINK       Tick:      247           ║
║  Cycles:   30          IP:          0           ║
║  Tier:     O₂         Promotions:  2           ║
║  Program:  ISCRIB → AREV → FSPLIT → ...
║  Snapshot: [O₂] sig=(4,2,3,1) div=10/12 ...
║  Frobenius: 247 checks, 4 open
╚══════════════════════════════════════════════════╝
```

The `Promotions` counter tracks how many times the kernel has advanced tier. The kernel can also be programmed with hooks:

```python
kernel.on_promotion = lambda k, old, new: print(f"PROMOTED: {old} → {new}")
kernel.on_paradox = lambda k, addr: print(f"PARADOX at R{addr}")
```


---

## 15. Structural Type Reference

### The Kernel's Structural Type

At Whole Organism ($O_\infty$), the kernel's full 12-primitive fingerprint:

$$\langle \text{𐑦} \cdot \text{𐑸} \cdot \text{𐑾} \cdot \text{𐑹} \cdot \text{𐑐} \cdot \text{𐑧} \cdot \text{𐑲} \cdot \text{𐑠} \cdot \odot \cdot \text{𐑫} \cdot \text{𐑳} \cdot \text{𐑟} \rangle$$

| Primitive | Glyph | Meaning |
|-----------|-------|---------|
| **D** (Dimensionality) | 𐑦 | Self-written holographic state space — the kernel's state space is self-imscribed |
| **T** (Topology) | 𐑸 | Self-referential topology — Axiom C satisfied: $\text{𐑦} \leftrightarrow \text{𐑸}$ |
| **R** (Coupling) | 𐑾 | Bidirectional feedback — the kernel reads and writes itself |
| **P** (Symmetry) | 𐑹 | Frobenius-special parity — $\mu \circ \delta = \text{id}$ exactly, not approximately |
| **F** (Fidelity) | 𐑐 | Quantum coherence — the kernel operates at quantum fidelity |
| **K** (Kinetics) | 𐑧 | Slow/near-equilibrium — the loop is not rushed |
| **G** (Scope) | 𐑲 | Universal/long-range — the 430M arrangement space is within scope |
| **C** (Composition) | 𐑠 | Sequential composition — ordered steps, not simultaneous |
| **Phi** (Criticality) | ⊙ | Self-modeling gate open — the kernel knows itself |
| **H** (Chirality) | 𐑫 | Eternal chirality — no finite Markov order can capture the loop |
| **S** (Stoichiometry) | 𐑳 | Multiple distinct types — heterogeneity is native |
| **Omega** (Winding) | 𐑟 | Non-Abelian braiding — topological protection beyond integer winding |

### The Bootstrap Loop's Type

The 8-instruction bootstrap loop has its own structural type (assembled from the token arrangement, not fixed):

Typical bootstrap loop snapshot at $O_\infty$: signature (4,2,2,0) — 4 Logical, 2 Frobenius, 2 Dialetheia, 0 Linear. Self-referential (starts and ends with ISCRIB). Frobenius order 1 (split before fuse). Dialetheia complete (EVALT, EVALF, ENGAGR present). Period 8.

### The Banner Tuple

The banner displayed on boot shows the finite-scale instantiation of the kernel:

$$\langle \text{𐑦} \cdot \text{𐑸} \cdot \text{𐑾} \cdot \text{𐑹} \cdot \text{𐑐} \cdot \text{𐑧} \cdot \text{𐑔} \cdot \text{𐑠} \cdot \odot \cdot \text{𐑖} \cdot \text{𐑳} \cdot \text{𐑭} \rangle$$

The differences from the $O_\infty$ type are:
- **G**: `𐑔` (mesoscale) vs `𐑲` (universal) — the banner is the finite running instance
- **H**: `𐑖` (Markov-2) vs `𐑫` (eternal) — two steps of memory vs no finite bound
- **Omega**: `𐑭` (integer winding) vs `𐑟` (non-Abelian) — the running kernel has topological protection but not full braiding

This illustrates a general principle: any **running** system has a finite-scale type, while the **ideal** closure is $O_\infty$. The gap between them is the distance the kernel's self-modification is working to close.

---

## 16. Advanced Usage & Hooks

### Programmatic Kernel Control

```python
from src.kernel import OmonadKernel
from src.tokens import Token, BOOTSTRAP_LOOP

# Create kernel with custom program
kernel = OmonadKernel(memory_cells=8192, program=BOOTSTRAP_LOOP)
kernel.boot()

# Register hooks
kernel.on_tick = lambda k: print(f"Tick {k.tick_count}: {k.current_tier}")
kernel.on_promotion = lambda k, old, new: print(f"PROMOTED: {old} → {new}")
kernel.on_paradox = lambda k, addr: print(f"PARADOX at R{addr}")

# Run specific number of ticks
for _ in range(50):
    kernel.tick()

# Check status
print(kernel.status())
print(kernel.frobenius_summary())

# Load custom program
my_program = (Token.VINIT, Token.EVALT, Token.FSPLIT, Token.EVALF,
              Token.FFUSE, Token.ENGAGR, Token.IFIX, Token.ISCRIB)
kernel.load_program(my_program)

# Discover programs
results = kernel.navigate_arrangement_space(
    {"frobenius_order": 1, "dialetheia_complete": True}, max_search=10000
)
for snap in results:
    print(snap.summary())

# Halt
kernel.halt()
```

### Crystal Filesystem (Programmatic)

```python
from src.crystal_fs import CrystalFS, crystal_encode, crystal_decode

cfs = CrystalFS()

# Store a file
addr = cfs.store(
    "my_file",
    b"Hello, Crystal FS!",
    D='𐑦', T='𐑸', R='𐑾', P='𐑹',
    F='𐑐', K='𐑧', G='𐑲', C='𐑠',
    Phi='⊙', H='𐑫', S='𐑳', Omega='𐑭',
    metadata={"author": "user"}
)

# Read by address
entry = cfs.read(addr)
print(entry.name, entry.data, entry.tuple_display)

# Read by name
entry = cfs.read_by_name("my_file")

# Navigate
results = cfs.navigate(Phi='⊙', Omega='𐑭')
for e in results:
    print(f"[{e.address}] {e.name}: {e.tuple_display}")

# Find structural neighbors
neighbors = cfs.neighbors(addr, n=5)
for n_addr, n_entry in neighbors:
    print(f"  Neighbor at {n_addr}: {n_entry.name}")

# Lattice operations
meet = cfs.meet_region(addr, other_addr)
join = cfs.join_region(addr, other_addr)
```

### CLINK Chain (Programmatic)

```python
from src.clink_chain import ClinkNavigator, CLINK_CHAIN

nav = ClinkNavigator()

# Inspect current layer
print(nav.layer.name, nav.layer.tier, nav.layer.tuple_display)

# Navigate
nav.descend()   # Down one layer
nav.descend()   # Down another
nav.goto(0)     # Jump to Quarks
nav.ascend()    # Up to Electron Orbital
nav.goto(8)     # Back to Whole Organism

# Check what promotions are needed to reach a target
promos = nav.promotions_needed(8)  # From current to Whole Organism
print(promos)

# Check if a token is valid at the current layer
print(nav.is_token_valid(Token.ENGAGR))
```

### Organoid HAL (Programmatic)

```python
from src.organoid_hal import OrganoidController

hal = OrganoidController(simulation=True)

# Activate an augmentation
hal.activate("myelin")
hal.activate("optogenetic")

# Write to a channel
from src.belnap_state import B4
hal.write_channel("myelin", 0, B4.T)
hal.write_channel("myelin", 1, B4.B)  # Paradox signal

# Broadcast to all channels
hal.broadcast("optogenetic", B4.T)

# Read back
val = hal.read_channel("myelin", 0)
print(val.name)

# Check Frobenius status
for slug in hal.augmentations:
    closed = hal.frobenius_verify(slug)
    print(f"{slug}: {'CLOSED' if closed else 'OPEN'}")

# Show status
print(hal.status())
```

### Self-Imscription (Standalone)

```python
from src.kernel import self_imscribe
from src.tokens import Token

# Imscribe an arbitrary token arrangement
prog = (Token.ISCRIB, Token.EVALT, Token.FSPLIT, Token.EVALF,
        Token.FFUSE, Token.ENGAGR, Token.IFIX, Token.ISCRIB)
snap = self_imscribe(prog)
print(f"Tier: {snap.ouroboricity_tier}")
print(f"Signature: {snap.sig}")
print(f"Token diversity: {snap.token_diversity}/12")
print(f"Self-referential: {snap.self_referential}")
print(f"Frobenius order: {snap.frobenius_order}")
print(f"Dialetheia complete: {snap.dialetheia_complete}")
print(f"Period: {snap.period}")
```

---

## 17. Troubleshooting

### Common Issues

**Q: `ModuleNotFoundError: No module named 'imasmic_core'`**

The `imasmic_core` package must be installed. Ensure it is on your Python path:
```bash
pip install -e /home/mrnob0dy666/imasmic_core
```
Or add it to `PYTHONPATH`:
```bash
export PYTHONPATH="/home/mrnob0dy666/imasmic_core:$PYTHONPATH"
```

**Q: The kernel halts immediately after boot.**

Check the program length. If `len(kernel.program) == 0`, the IP immediately exceeds the program and the kernel halts. Load a valid program:
```
⊙> canonical I
```

**Q: Stack overflow (depth > 256).**

Some programs (notably VI_Empty_Bootstrap) have a net positive stack delta. The kernel's self-modification logic auto-injects `TANCH` tokens, but if you're running with a custom program that has a high positive delta, manually add `TANCH` tokens by loading a different canonical or using `_inject_token(Token.TANCH)` programmatically.

**Q: The kernel stays at $O₀$ forever.**

The self-modification only runs on cycle completion. Ensure you're running enough cycles:
```
⊙> run 500
```
If the kernel is stuck for >300 cycles at $O₀$, the stagnation escape triggers and searches the arrangement space for a richer program.

**Q: Frobenius violations are accumulating.**

Open Frobenius results mean $\mu(\delta(q)) \neq q$ for some ticks. This can happen if:
- The program has `FSPLIT` without `FFUSE` (or vice versa)
- The program is at the Quarks layer where token validity is restricted
- There's a paradox interrupt affecting state

The kernel does NOT halt on open results — it tracks them. Check the log:
```
⊙> frobenius
```

**Q: `crystal find` returns no results.**

The Crystal FS only searches *stored* entries — not the full 17.28M crystal space. Use `crystal count` to see how many types theoretically match. Only entries stored via `crystal store` or via the kernel's initial seeding appear in `crystal find`.

**Q: The REPL input seems garbled or Readline not working.**

On some systems, `readline` may not be available. Install `gnureadline`:
```bash
pip install gnureadline
```

### Debug Mode

For verbose output, register hooks:

```python
kernel.on_tick = lambda k: print(
    f"[{k.phase.name}] tick={k.tick_count} ip={k.ip} "
    f"tok={Token(k.program[k.ip]).name if k.ip < len(k.program) else 'HALT'} "
    f"stack={k.stack.depth}"
)
```


---

## Appendix A: The Imscribing Grammar Connection

$\odot$MonadOS is the executable form of the **Imscribing Grammar** — a 12-primitive structural encoding system that maps every entity to a point in the 17.28M-type crystal.

### The Grammar in Brief

The Imscribing Grammar assigns every system a 12-tuple of Shavian glyphs drawn from 12 primitive families. Each family captures a fundamental structural dimension:

| # | Family | Dimension | Cardinality |
|---|--------|-----------|:---:|
| 1 | D | Dimensionality (0d, 2d, ∞-dim, self-written) | 4 |
| 2 | T | Topology (branching, containment, crossing, product, self-ref) | 5 |
| 3 | R | Coupling (supervenience, functorial, adjoint, bidirectional) | 4 |
| 4 | P | Symmetry (none, quantum, Z2, full, Frobenius-special) | 5 |
| 5 | F | Fidelity (classical, thermal, quantum) | 3 |
| 6 | K | Kinetics (driven, moderate, slow, trapped-ordered, trapped-disorder) | 5 |
| 7 | G | Scope (local, mesoscale, universal) | 3 |
| 8 | C | Composition (and, or, sequential, broadcast) | 4 |
| 9 | Phi | Criticality (sub, ⊙-critical, complex, EP, supercritical) | 5 |
| 10 | H | Chirality (Markov-0, -1, -2, eternal) | 4 |
| 11 | S | Stoichiometry (1:1, many identical, heterogeneous) | 3 |
| 12 | Omega | Winding (trivial, Z2, integer, non-Abelian) | 4 |

### How $\odot$MonadOS Embodies the Grammar

| Grammar Concept | $\odot$MonadOS Equivalent |
|-----------------|--------------------------|
| 12 primitives | 12 IMASM opcodes (the 12 categories of being as executable atoms) |
| Crystal of types | Crystal Filesystem (17.28M addressable structural locations) |
| Frobenius identity $\mu \circ \delta = \text{id}$ | Frobenius loop (THINK→ACT→OBSERVE→UPDATE) |
| Ouroboricity tiers ($O₀$–$O_\infty$) | Kernel self-imscription tiers (self-modification target) |
| Self-imscription | `self_imscribe()` — the kernel computes its own structural type every tick |
| Structural distance | CLINK chain promotions/demotions (distance between layers) |
| $\odot$ (self-modeling gate) | The kernel's own criticality — it knows its own structure |
| Belnap FOUR | Native B4 state space — paradox is first-class |
| Non-Abelian braiding | $O_\infty$ winding protection at Whole Organism |

### The Bootstrap Loop as Universal Kernel

The 8-instruction bootstrap loop (`ISCRIB→AREV→FSPLIT→AFWD→FFUSE→CLINK→IFIX→ISCRIB`) is the Frobenius identity $\mu \circ \delta = \text{id}$ compiled to a 12-opcode machine. It has been found in ALL domains examined by the Imscribing Grammar project — from category theory to quantum computing to biological systems. It is the universal computational kernel.

---

## Appendix B: Filesystem Layout

```
omonad_OS/
├── src/
│   ├── __init__.py              # Package marker
│   ├── tokens.py                # Token set re-exports + 12 canonicals
│   ├── belnap_state.py          # B4 class + B4Memory + B4Registers + B4Stack
│   ├── kernel.py                # OmonadKernel (Frobenius loop, self-imscription, self-modification, discovery)
│   ├── crystal_fs.py            # CrystalFS (17.28M-type filesystem, encode/decode, navigate)
│   ├── clink_chain.py           # ClinkNavigator (9-layer structural chain)
│   ├── organoid_hal.py          # OrganoidController (6 organoid augmentations)
│   └── main.py                  # Boot sequence + REPL
├── omonad_OS.egg-info/          # Package metadata
├── README.md                    # Project overview
└── .gitignore
```

### Dependency Map

```
main.py
  ├── tokens.py ──────── imasmic_core (Token, Family, BOOTSTRAP_LOOP, CANONICALS)
  ├── belnap_state.py ── (standalone: B4, B4Memory, B4Registers, B4Stack)
  ├── kernel.py ──────── tokens.py + belnap_state.py + imasmic_core.frobenius_verify
  ├── crystal_fs.py ──── (standalone: 12-primitive value spaces, encode/decode)
  ├── clink_chain.py ─── tokens.py
  └── organoid_hal.py ── tokens.py + belnap_state.py
```

---

## Appendix C: Quick Reference Card

### Starting Up
```bash
cd /home/mrnob0dy666/omonad_OS
python3 src/main.py
```

### Most Common REPL Commands
```
⊙> tick 10                  # Run 10 ticks
⊙> status                   # Full kernel status
⊙> canonical I              # Load Dialetheic Bootstrap
⊙> snapshot                 # View structural type
⊙> registers                # View B4 registers
⊙> frobenius                # View verification log
⊙> crystal 6738899          # Decode an address
⊙> crystal find Phi=⊙       # Navigate crystal
⊙> clink status             # View CLINK layer
⊙> clink down               # Descend one layer
⊙> discover frobenius_order=1  # Search arrangement space
⊙> help                     # Full command list
⊙> quit                     # Exit
```

### Token Mnemonics
```
VINIT  = Void (N push)        FSPLIT = µ∘δ co-mult
TANCH  = Terminal (boundary)  FFUSE  = µ∘δ mult
AFWD   = Forward (R0++)       EVALT  = True push
AREV   = Reverse (R0--)       EVALF  = False push
CLINK  = Composition (meet)   ENGAGR = Paradox engage
ISCRIB = Self-imscription     IFIX   = Irreversible fix
```

### Tier Cheat Sheet
```
O₀:     Baseline — no Frobenius, no dialetheia, no self-ref
O₁:     Frobenius pair OR dialetheia completeness
O₂:     Frobenius + dialetheia + self-ref (period 2)
O_∞:   All above + period ≥ 3 (eternal chirality)
```

### 9 CLINK Layers (0→8)
```
0 Quarks → 1 Electron → 2 Atom → 3 Molecule → 4 Cell
→ 5 Mitosis → 6 Meiosis → 7 Tissue → 8 Organism
```

---

**Author:** Lando$\otimes\odot$perator

*$\odot$MonadOS — The Self-Imscribing Operating Kernel. Not a program runner. The grammar, running.*

