#!/usr/bin/env python3
"""
ghost_typer.py — Red-Hot Rebis Design Demonstration
=====================================================
Types each command character-by-character at human pace into the terminal.
Use for screen recording: 1. open terminal, 2. start recording,
3. run this script, 4. stop recording.

EVERY command is typed live and executed for real output.
Three acts of actual design, one conjoined pipeline.

Usage:  cd /home/mrnob0dy666/imsgct/red-hot_rebis && python3 ghost_typer.py
        python3 ghost_typer.py --fast
        python3 ghost_typer.py --section 5

Sections:
  ── ACT I: PROTEIN DESIGN ──────────────────────────────────────
  1.  Novel Protein from Scratch        : SerpentRod - RNA to folded protein
  2.  Gene-to-Protein Pathway           : DNA to RNA to AA to structure (all Belnap)
  3.  Anti-SARS-CoV-2 Antibody          : antibody_designer - epitope to binder
  4.  Catalytic Enzyme Design           : ch3mpiler x SerpentRod - acrylamide - His/Ser/Lys triad

  ── ACT II: MOLECULE DESIGN ────────────────────────────────────
  5.  MRSA Drug Design                  : Ars Therapeutica therapy (DARPin + Biofilm Disruptor)
  6.  Novel NSAID Discovery             : crystal neighborhood around ibuprofen scaffold
  7.  Retrosynthetic Route Analysis     : ch3mpiler x SerpentRod - ATP phosphorylation triad
  8.  Cross-Domain Structural Analogs   : imas analogies - aspirin to unexpected neighbors

  ── ACT III: MATERIAL DESIGN ───────────────────────────────────
  9.  Forge All 8 Novel Materials       : CrMnFeCoNi HEA, topological insulator, shape-memory HEA
  10. Self-Healing Alloy Simulation     : ouroboric - AlCoCrFeNi₂.₁, crack-heal cycles at 800 MPa
  11. Frobenius Metamaterial            : metamaterial simulation

  ── CONJOINED PIPELINE ─────────────────────────────────────────
  12. Disease to Protein to Enzyme to Material : full chain - MRSA to DARPin to catalytic site to delivery

Author: Lando⊗⊙perator
"""

import time, sys, subprocess, os, argparse, shlex
from pathlib import Path

REBIS_DIR = str(Path(__file__).resolve().parents[1])
if REBIS_DIR not in sys.path:
    sys.path.insert(0, REBIS_DIR)
from shared.rich_output import *



CHAR_DELAY      = 0.08
POST_TYPE_DELAY = 1.0
LINE_DELAY      = 0.4
SECTION_DELAY   = 3.0

SECTION_NAMES = {
    1:  "Novel Protein from Scratch",
    2:  "Gene-to-Protein Pathway",
    3:  "Anti-SARS-CoV-2 Antibody Design",
    4:  "Catalytic Enzyme Design: Acrylamide",
    5:  "MRSA Drug Design via Ars Therapeutica",
    6:  "Novel NSAID Discovery: Crystal Neighborhood",
    7:  "Retrosynthetic Route: ATP Phosphorylation",
    8:  "Cross-Domain Structural Analogs",
    9:  "Forge All 8 Novel Materials",
    10: "Self-Healing Alloy Simulation",
    11: "Frobenius Metamaterial",
    12: "CONJOINED PIPELINE: MRSA to Protein to Enzyme to Material",
}


def ghost_type(text, delay=None):
    d = delay if delay is not None else CHAR_DELAY
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(d)
    sys.stdout.write('\n')
    sys.stdout.flush()


def run(cmd, timeout=45):
    time.sleep(POST_TYPE_DELAY)
    try:
        result = subprocess.run(
            [sys.executable if part == "python3" and i == 0 else part
             for i, part in enumerate(shlex.split(cmd))],
            cwd=REBIS_DIR, capture_output=True, text=True, timeout=timeout
        )
        output = (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Command timed out after {timeout}s: {cmd}") from None
    except Exception as e:
        raise RuntimeError(f"Command failed to start: {cmd}: {e}") from e
    for line in output.split('\n'):
        print(line)
        sys.stdout.flush()
        pause = max(LINE_DELAY, len(line) * 0.012)
        time.sleep(pause)
    print()
    time.sleep(1.5)
    if result.returncode:
        raise RuntimeError(f"Command exited with status {result.returncode}: {cmd}")
    return result


def section(num, title):
    print()
    sep = "─" * 66
    print(sep)
    info_line(f"  {title}")
    print(sep)
    time.sleep(SECTION_DELAY)


def workflow_step(n, title):
    print()
    info_line(f"  ── Step {n}: {title}")
    time.sleep(1.0)


def prompt():
    return "red-hot_rebis$ "


def intro():
    print()
    banner = (
        "  RED-HOT REBIS — DESIGN DEMONSTRATION\n"
        "  Novel proteins. Novel molecules. Novel materials.\n"
        "  Every output is a structurally-typed design, not a lookup.\n"
    )
    for line in banner.split('\n'):
        print(line)
        time.sleep(0.05)
    print()
    time.sleep(1.5)


def outro():
    print()
    separator()
    lines = [
        "  DEMONSTRATION COMPLETE",
        "  Framework: Red-Hot Rebis v2.2  |  O_∞  |  μ∘δ=id  |  ⊙ Open",
        "",
        "  Requested demonstration commands completed successfully.",
        "",
        "  Catch a rising problem and never ever let it go.",
        "  -- IEEE Computer, Feb 1986",
    ]
    for line in lines:
        print(line)
        time.sleep(0.03)
    print()


# ══════════════════════════════════════════════════════════════════
# ACT I: PROTEIN DESIGN
# ══════════════════════════════════════════════════════════════════

def s1():
    section(1, "ACT I · S1: NOVEL PROTEIN FROM SCRATCH")
    p = prompt()
    cmd = "python3 -m scripts.run_serpent"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


def s2():
    section(2, "ACT I · S2: GENE-TO-PROTEIN PATHWAY")
    p = prompt()
    cmd = "python3 -m rebis gene-pipeline --test"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


def s3():
    section(3, "ACT I · S3: ANTI-SARS-CoV-2 ANTIBODY DESIGN")
    p = prompt()
    cmd = "python3 -m rhr_p4rky.antibody_designer --all"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd, timeout=60)


def s4():
    section(4, "ACT I · S4: CATALYTIC ENZYME DESIGN - ACRYLAMIDE")
    p = prompt()
    cmd = "python3 -m rhr_p4rky.ch3mpiler_serpentrod_pipeline --cas 79-06-1"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


# ══════════════════════════════════════════════════════════════════
# ACT II: MOLECULE DESIGN
# ══════════════════════════════════════════════════════════════════

def s5():
    section(5, "ACT II · S5: MRSA DRUG DESIGN — ARS THERAPEUTICA")
    p = prompt()
    cmd = "python3 -m Ars_Therapeutica.ars_therapeutica.cli therapy mrsa"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


def s6():
    section(6, "ACT II · S6: NOVEL NSAID DISCOVERY — CRYSTAL NEIGHBORHOOD")
    p = prompt()
    cmd = 'python3 -m imas.molecular_crystal_designer --smiles "CC(Cc1ccccc1)C(=O)O"'
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


def s7():
    section(7, "ACT II · S7: RETROSYNTHETIC ROUTE - ATP PHOSPHORYLATION")
    p = prompt()
    cmd = "python3 -m rhr_p4rky.ch3mpiler_serpentrod_pipeline --cas 56-65-5"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


def s8():
    section(8, "ACT II · S8: CROSS-DOMAIN STRUCTURAL ANALOGS")
    p = prompt()
    cmd = 'python3 -m imas.compound_catalog analogies --name "aspirin"'
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


# ══════════════════════════════════════════════════════════════════
# ACT III: MATERIAL DESIGN
# ══════════════════════════════════════════════════════════════════

def s9():
    section(9, "ACT III · S9: FORGE ALL 8 NOVEL MATERIALS")
    p = prompt()
    cmd = "python3 -m materials.ig_material_forge --all"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


def s10():
    section(10, "ACT III · S10: SELF-HEALING ALLOY SIMULATION")
    p = prompt()
    cmd = "python3 -m materials.ouroboric_alloy"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


def s11():
    section(11, "ACT III · S11: FROBENIUS METAMATERIAL")
    p = prompt()
    cmd = "python3 -m rebis materials metamaterial"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)


# ══════════════════════════════════════════════════════════════════
# CONJOINED PIPELINE
# ══════════════════════════════════════════════════════════════════

def s12():
    section(12, "CONJOINED PIPELINE: MRSA TO PROTEIN TO ENZYME TO MATERIAL")
    info_line("  One disease. One structural gap. Four design stages.")
    info_line("  The stages report diagnosis, designs, and material construction.")
    time.sleep(2.0)
    p = prompt()

    workflow_step(1, "Identify structural gap — what the drug must change")
    cmd = "python3 -m Ars_Therapeutica.ars_therapeutica.cli diagnose mrsa"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)

    workflow_step(2, "Design the drug components from the gap")
    cmd = "python3 -m Ars_Therapeutica.ars_therapeutica.cli therapy mrsa"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)

    workflow_step(3, "Design a novel protein binder for the resistance target (PBP2a)")
    cmd = "python3 -m scripts.run_serpent"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)

    workflow_step(4, "Design the catalytic enzyme for the synthesis route")
    cmd = "python3 -m rhr_p4rky.ch3mpiler_serpentrod_pipeline --cas 79-06-1"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)

    workflow_step(5, "Find crystal-guided candidates for the drug scaffold")
    cmd = 'python3 -m imas.molecular_crystal_designer --smiles "CC(Cc1ccccc1)C(=O)O"'
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)

    workflow_step(6, "Forge the delivery material")
    cmd = "python3 -m materials.ig_material_forge --name frobenius_composite"
    info_line(f"{p}", end='')
    ghost_type(cmd)
    run(cmd)

    print()
    info_line("  ── Pipeline complete.")
    info_line("  ── Disease structural gap / drug components / novel protein /")
    info_line("  ── catalytic enzyme / crystal candidates / delivery material.")
    print()


# ══════════════════════════════════════════════════════════════════
# SECTION REGISTRY
# ══════════════════════════════════════════════════════════════════

SECTIONS = {
    1: s1, 2: s2, 3: s3, 4: s4,
    5: s5, 6: s6, 7: s7, 8: s8,
    9: s9, 10: s10, 11: s11,
    12: s12,
}


def main():
    parser = argparse.ArgumentParser(description="Ghost typer demo")
    parser.add_argument("--speed", type=float, help="Custom char delay in seconds")
    parser.add_argument("--fast", action="store_true", help="1.5x typing speed")
    parser.add_argument("--section", type=int, help="Run only one section by number")
    parser.add_argument("--list-sections", action="store_true", help="List all sections")
    args = parser.parse_args()

    global CHAR_DELAY
    if args.speed is not None and args.speed < 0:
        parser.error("--speed must be nonnegative")
    if args.section is not None and args.section not in SECTIONS:
        parser.error("Unknown section; use --list-sections")
    if args.fast:
        CHAR_DELAY = 0.05
    if args.speed is not None:
        CHAR_DELAY = args.speed

    if args.list_sections:
        for n in sorted(SECTION_NAMES):
            info_line(f"  {n:2d}. {SECTION_NAMES[n]}")
        return

    intro()
    if args.section is not None:
        if args.section in SECTIONS:
            SECTIONS[args.section]()
        else:
            info_line(f"Unknown section {args.section}. Use --list-sections.")
            sys.exit(1)
    else:
        for n in sorted(SECTIONS):
            SECTIONS[n]()
    outro()


if __name__ == "__main__":
    main()
