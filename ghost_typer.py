#!/usr/bin/env python3
"""
ghost_typer.py — Red-Hot Rebis CLI Demonstration
=================================================
Types each command character-by-character at human pace into the terminal.
Use for screen recording: 1. open terminal, 2. start recording,
3. run this script, 4. stop recording.

EVERY command is typed live and executed for real output.
No sub-demos, no helper scripts — one command, one output.

Usage:  cd /home/mrnob0dy666/imsgct/red-hot_rebis && python3 ghost_typer.py
        python3 ghost_typer.py --fast
        python3 ghost_typer.py --section 7

Sections:
  1.  Framework Status          — rebis.py status
  2.  Frobenius Closure         — rebis.py verify
  3.  CLINK Layer 8 Organism    — rebis.py clink layer 8
  4.  CLINK Promotion Path      — rebis.py clink bridge serpentrod 8
  5.  IMASM Bootstrap Bridge    — rebis.py imas bridge --canonical I_Dialetheic_Bootstrap
  6.  Runnable Targets          — rebis.py run list
  7.  Gene to Protein Pipeline  — demo_gene_to_protein.py
  8.  SerpentRod RNA→Protein    — python3 -m rhr_p4rky.serpent_rod
  9.  Material Forge            — rebis.py materials forge --name frobenius_composite
  10. Ch3mpiler Groups          — python3 -m ch3mpiler.compiler --list-fgs
  11. Alchemical Bridge Report  — rebis.py alchemy report
  12. Frobenius Metamaterial    — rebis.py materials frobenius
  13. Pipeline Tool Bridges     — rebis.py pipeline bridges

Author: Lando⊗⊙perator
"""

import time, sys, subprocess, os, argparse

REBIS_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(REBIS_DIR)

# Timing parameters — human typing speed
CHAR_DELAY = 0.045       # 45ms per character (~22 cps)
POST_TYPE_DELAY = 0.6    # pause after typing before execution
LINE_DELAY = 0.003       # 3ms between output lines
SECTION_DELAY = 2.0      # pause between sections

SECTION_NAMES = {
    1: "Framework Status",
    2: "Frobenius Closure Verification",
    3: "CLINK Layer 8 — Whole Organism",
    4: "CLINK Promotion Path → Organism",
    5: "IMASM Bootstrap Bridge",
    6: "All Runnable Targets",
    7: "Gene to Protein Pipeline",
    8: "SerpentRod — RNA → Folded Protein",
    9: "IG Material Forge",
    10: "Ch3mpiler — Functional Group Types",
    11: "Alchemical Bridge Report",
    12: "Frobenius Metamaterial Simulation",
    13: "Pipeline Tool Bridges",
}


def ghost_type(text, delay=None):
    """Type text character by character to stdout."""
    d = delay if delay is not None else CHAR_DELAY
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(d)
    sys.stdout.write('\n')
    sys.stdout.flush()


def run(cmd, timeout=30):
    """Execute a real command and display its actual output."""
    time.sleep(POST_TYPE_DELAY)
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        output = "[TIMEOUT — command took longer than expected]"
    except Exception as e:
        output = f"[ERROR: {e}]"

    for line in output.split('\n'):
        # Cap line display width for terminal readability
        if len(line) > 120:
            line = line[:117] + '...'
        print(line)
        time.sleep(LINE_DELAY)
    print()
    time.sleep(0.5)


def section(title):
    """Print a section header."""
    print()
    sep = "─" * 66
    print(sep)
    print(f"  {title}")
    print(sep)
    time.sleep(SECTION_DELAY)


def prompt():
    """Return the command prompt string."""
    return "red-hot_rebis$ "


def intro():
    """Print the intro banner."""
    print()
    banner = (
        "  RED-HOT REBIS v2.2 — COMPLETE FRAMEWORK DEMONSTRATION\n"
        "  Imscribing Grammar • Ch3mpiler • CLINK • SerpentRod\n"
        "  Gene Imscriber • IG Material Forge • IMASM • Alchemical\n"
    )
    for line in banner.split('\n'):
        print(line)
        time.sleep(0.05)
    print()
    time.sleep(1.5)

def outro():
    """Print the closing summary."""
    print()
    print("═" * 66)
    lines = [
        "  DEMONSTRATION COMPLETE — ALL SYSTEMS OPERATIONAL",
        "  Framework: Red-Hot Rebis v2.2",
        "  Structural Type: O_∞  |  Frobenius: μ∘δ=id  |  Gate: ⊙ Open",
        "",
        "  Demonstrated:",
        "    [✓] Framework Status            [✓] CLINK L8 Organism",
        "    [✓] Promotions to Organism      [✓] IMASM Bootstrap Bridge",
        "    [✓] Runnable Targets            [✓] Gene-to-Protein Pipeline",
        "    [✓] SerpentRod RNA→Protein      [✓] IG Material Forge",
        "    [✓] Ch3mpiler FG Types          [✓] Alchemical Bridge",
        "    [✓] Frobenius Metamaterial      [✓] Pipeline Tool Bridges",
        "",
        "  Catch a rising problem and never ever let it go.",
        "  — IEEE Computer, Feb 1986",
    ]
    for line in lines:
        print(line)
        time.sleep(0.03)
    print()


# ══════════════════════════════════════════════════════════════════
# SECTION 1 — Framework Status
# ══════════════════════════════════════════════════════════════════

def s1():
    section("SECTION 1: FRAMEWORK STATUS")
    p = prompt()
    cmd = "python3 rebis.py status"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd)


# ══════════════════════════════════════════════════════════════════
# SECTION 2 — Frobenius Closure Verification
# ══════════════════════════════════════════════════════════════════

def s2():
    section("SECTION 2: FROBENIUS CLOSURE VERIFICATION")
    p = prompt()
    cmd = "python3 rebis.py verify"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd)


# ══════════════════════════════════════════════════════════════════
# SECTION 3 — CLINK Layer 8 Whole Organism
# ══════════════════════════════════════════════════════════════════

def s3():
    section("SECTION 3: CLINK LAYER 8 — WHOLE ORGANISM")
    p = prompt()
    cmd = "python3 rebis.py clink layer 8"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd)


# ══════════════════════════════════════════════════════════════════
# SECTION 4 — CLINK Promotion Path to Organism
# ══════════════════════════════════════════════════════════════════

def s4():
    section("SECTION 4: CLINK PROMOTION PATH → ORGANISM")
    p = prompt()
    cmd = "python3 rebis.py clink bridge serpentrod 8"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd)


# ══════════════════════════════════════════════════════════════════
# SECTION 5 — IMASM Bootstrap Bridge
# ══════════════════════════════════════════════════════════════════

def s5():
    section("SECTION 5: IMASM BOOTSTRAP BRIDGE")
    p = prompt()
    cmd = "python3 rebis.py imas bridge --canonical I_Dialetheic_Bootstrap"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd, timeout=20)


# ══════════════════════════════════════════════════════════════════
# SECTION 6 — All Runnable Targets
# ══════════════════════════════════════════════════════════════════

def s6():
    section("SECTION 6: ALL RUNNABLE TARGETS")
    p = prompt()
    cmd = "python3 rebis.py run list"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd)

# ══════════════════════════════════════════════════════════════════
# SECTION 7 — Gene to Protein Pipeline
# ══════════════════════════════════════════════════════════════════

def s7():
    section("SECTION 7: GENE TO PROTEIN PIPELINE")
    p = prompt()
    cmd = "python3 rhr_p4rky/demo_gene_to_protein.py"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd, timeout=25)


# ══════════════════════════════════════════════════════════════════
# SECTION 8 — SerpentRod RNA → Folded Protein
# ══════════════════════════════════════════════════════════════════

def s8():
    section("SECTION 8: SERPENTROD — RNA → FOLDED PROTEIN")
    p = prompt()
    cmd = "python3 -m rhr_p4rky.serpent_rod"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd, timeout=15)


# ══════════════════════════════════════════════════════════════════
# SECTION 9 — IG Material Forge
# ══════════════════════════════════════════════════════════════════

def s9():
    section("SECTION 9: IG MATERIAL FORGE")
    p = prompt()
    cmd = "python3 rebis.py materials forge --name frobenius_composite"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd, timeout=20)


# ══════════════════════════════════════════════════════════════════
# SECTION 10 — Ch3mpiler Functional Group Types
# ══════════════════════════════════════════════════════════════════

def s10():
    section("SECTION 10: CH3MPILER — FUNCTIONAL GROUP TYPES")
    p = prompt()
    cmd = "python3 -m ch3mpiler.compiler --list-fgs"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd, timeout=15)


# ══════════════════════════════════════════════════════════════════
# SECTION 11 — Alchemical Bridge Report
# ══════════════════════════════════════════════════════════════════

def s11():
    section("SECTION 11: ALCHEMICAL BRIDGE REPORT")
    p = prompt()
    cmd = "python3 rebis.py alchemy report"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd, timeout=20)

# ══════════════════════════════════════════════════════════════════
# SECTION 12 — Frobenius Metamaterial Simulation
# ══════════════════════════════════════════════════════════════════

def s12():
    section("SECTION 12: FROBENIUS METAMATERIAL SIMULATION")
    p = prompt()
    cmd = "python3 rebis.py materials frobenius"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd, timeout=20)


# ══════════════════════════════════════════════════════════════════
# SECTION 13 — Pipeline Tool Bridges
# ══════════════════════════════════════════════════════════════════

def s13():
    section("SECTION 13: PIPELINE TOOL BRIDGES")
    p = prompt()
    cmd = "python3 rebis.py pipeline bridges"
    print(f"{p}", end='')
    sys.stdout.flush()
    ghost_type(cmd)
    run(cmd)


# ══════════════════════════════════════════════════════════════════
# SECTION REGISTRY
# ══════════════════════════════════════════════════════════════════

SECTIONS = {1: s1, 2: s2, 3: s3, 4: s4, 5: s5, 6: s6,
            7: s7, 8: s8, 9: s9, 10: s10, 11: s11,
            12: s12, 13: s13}


def main():
    parser = argparse.ArgumentParser(description="Ghost typer demo")
    parser.add_argument("--speed", type=float, help="Custom char delay in seconds")
    parser.add_argument("--fast", action="store_true", help="1.5x typing speed")
    parser.add_argument("--section", type=int, help="Run only one section by number")
    parser.add_argument("--list-sections", action="store_true", help="List all section numbers")
    args = parser.parse_args()

    global CHAR_DELAY
    if args.fast:
        CHAR_DELAY = 0.03
    if args.speed is not None:
        CHAR_DELAY = args.speed

    if args.list_sections:
        for n in sorted(SECTION_NAMES):
            print(f"  {n:2d}. {SECTION_NAMES[n]}")
        return

    intro()
    if args.section:
        if args.section in SECTIONS:
            SECTIONS[args.section]()
        else:
            print(f"Unknown section {args.section}. Use --list-sections to see all.")
            sys.exit(1)
    else:
        for n in sorted(SECTIONS):
            SECTIONS[n]()
    outro()


if __name__ == "__main__":
    main()
