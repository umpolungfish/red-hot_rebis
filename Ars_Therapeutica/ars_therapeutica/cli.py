"""
Ars Therapeutica — CLI
======================
Grammar-derived optimal therapies, operationalized as a type-lattice navigator.

Usage:
  at diagnose <disease>      — structural diagnosis (tuple, deltas, distance)
  at therapy <disease>        — full therapy protocol
  at tensor <a> <b>          — compute tensor product of two types
  at meet <a> <b>             — compute meet (greatest lower bound)
  at spectrum                 — show psychiatric φ̂-spectrum
  at list                     — list all available therapies
  at compare <a> <b>          — side-by-side structural comparison
  at operate <disease> <op>   — show structural operation result (tensor|meet|join)
"""

import sys
from .types import (
    THERAPIES, DISEASE_TYPES, HEALTH_TYPES, PSYCHIATRIC_SPECTRUM,
    Imscription, D, T, R, P, F, K, G, Gamma, Phi, H, S, W,
    tensor, meet, join, distance, delta_primitives, c_score, tier,
    primitive_order, ORDERS
)


# ─────────────────────────────────────────────────────────────────────
# FORMATTING
# ─────────────────────────────────────────────────────────────────────

BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

HEADER = f"{BOLD}{CYAN}"
SUBHEAD = f"{BOLD}{MAGENTA}"
OK = f"{GREEN}"
WARN = f"{YELLOW}"
ERR = f"{RED}"


def _fmt_tuple(t: Imscription) -> str:
    vals = [t.D.value, t.T.value, t.R.value, t.P.value, t.F.value,
            t.K.value, t.G.value, t.Gamma.value, t.Phi.value, t.H.value,
            t.S.value, t.W.value]
    return f"⟨{' '.join(vals)}>"


def _fmt_primitive(name: str, val) -> str:
    """Format a primitive with its full name and value."""
    names = {
        "D": "Ð  Dimensionality", "T": "Þ  Topology", "R": "Ř  Coupling",
        "P": "Φ  Parity", "F": "ƒ  Fidelity", "K": "Ç  Kinetics",
        "G": "Γ  Cardinality", "Gamma": "ɢ  Composition", "Phi": "φ̂  Criticality",
        "H": "Ħ  Chirality", "S": "Σ  Stoichiometry", "W": "Ω  Winding"
    }
    return f"  {names.get(name, name):22s} {val.value}"


# ─────────────────────────────────────────────────────────────────────
# COMMANDS
# ─────────────────────────────────────────────────────────────────────

def cmd_list():
    """List all available therapies."""
    info_line(f"{HEADER}Ars Therapeutica — Available Therapies{RESET}\n")
    for key, th in THERAPIES.items():
        info_line(f"  {BOLD}{key}{RESET}  [{th.category}]  d={th.distance}  "
f"{th.tier_disease}→{th.tier_health}  Δ={th.delta_primitives}")
    info_line(f"\n{len(THERAPIES)} therapies available.")


def cmd_diagnose(disease: str):
    """Structural diagnosis: show disease type, health type, deltas, distance."""
    if disease not in THERAPIES:
        info_line(f"{ERR}Unknown disease: {disease}{RESET}")
        info_line(f"Available: {', '.join(THERAPIES.keys())}")
        return

    th = THERAPIES[disease]
    PRIM_MAP = {"φ̂": "Phi", "Ħ": "H", "Ð": "D", "Þ": "T", "Ř": "R",
                "Φ": "P", "ƒ": "F", "Ç": "K", "Γ": "G", "ɢ": "Gamma",
                "Σ": "S", "Ω": "W"}
    separator()

    info_line(f"{SUBHEAD}Disease Type:{RESET}")
    info_line(f"  {_fmt_tuple(th.disease_type)}")
    info_line(f"  Tier: {th.tier_disease}  C-score: {th.c_score_disease}\n")

    info_line(f"{SUBHEAD}Health Type:{RESET}")
    info_line(f"  {_fmt_tuple(th.health_type)}")
    info_line(f"  Tier: {th.tier_health}  C-score: {th.c_score_health}\n")

    info_line(f"{SUBHEAD}Structural Gap:{RESET}")
    info_line(f"  Distance: {WARN}{th.distance}{RESET}")
    info_line(f"  Differing primitives ({len(th.delta_primitives)}): {CYAN}{th.delta_primitives}{RESET}\n")

    info_line(f"{SUBHEAD}Per-Primitive Delta:{RESET}")
    for k in th.delta_primitives:
        attr = PRIM_MAP.get(k, k); dv = getattr(th.disease_type, attr)
        hv = getattr(th.health_type, attr)
        arrow = "→"
        info_line(f"  {k:5s}  {dv.value} {arrow} {hv.value}")

    if th.category == "psychiatric" and disease in ("depression", "schizophrenia", "bipolar_mania"):
        info_line(f"\n{SUBHEAD}Psychiatric Spectrum (φ̂ axis):{RESET}")
        for name, t in PSYCHIATRIC_SPECTRUM.items():
            marker = " ◀" if name == disease else ""
            info_line(f"  {t.Phi.value}  {name}{marker}")


def cmd_therapy(disease: str):
    """Show full therapy protocol."""
    if disease not in THERAPIES:
        info_line(f"{ERR}Unknown disease: {disease}{RESET}")
        return

    th = THERAPIES[disease]
    PRIM_MAP = {"φ̂": "Phi", "Ħ": "H", "Ð": "D", "Þ": "T", "Ř": "R",
                "Φ": "P", "ƒ": "F", "Ç": "K", "Γ": "G", "ɢ": "Gamma",
                "Σ": "S", "Ω": "W"}
    separator()
    info_line(f"{th.summary}\n")

    info_line(f"{SUBHEAD}Structural Strategy:{RESET}")
    info_line(f"  {th.structural_strategy}\n")

    info_line(f"{SUBHEAD}Components ({len(th.components)}):{RESET}")
    for i, c in enumerate(th.components, 1):
        info_line(f"\n  {BOLD}{i}. {c['name']}{RESET}")
        info_line(f"     Target: {c['target_primitive']}")
        info_line(f"     Operation: {CYAN}{c['operation']}{RESET}")
        info_line(f"     Mechanism: {c['mechanism']}")

    if th.pdb_files:
        info_line(f"\n{SUBHEAD}PDB Structures:{RESET}")
        for p in th.pdb_files:
            info_line(f"  • {p}")

    if th.lean_files:
        info_line(f"\n{SUBHEAD}Lean Verification:{RESET}")
        for l in th.lean_files:
            info_line(f"  • {l}")

    info_line(f"\n{SUBHEAD}Documentation:{RESET}  {th.doc_file}")


def cmd_tensor(a: str, b: str):
    """Compute tensor product of two named types."""
    ta = _resolve(a)
    tb = _resolve(b)
    if ta is None or tb is None:
        return
    result = tensor(ta, tb)
    info_line(f"{HEADER}tensor({a}, {b}){RESET}")
    info_line(f"  {_fmt_tuple(ta)}")
    info_line(f"  ⊗")
    info_line(f"  {_fmt_tuple(tb)}")
    info_line(f"  {BOLD}={RESET}")
    info_line(f"  {_fmt_tuple(result)}")


def cmd_meet(a: str, b: str):
    """Compute meet of two named types."""
    ta = _resolve(a)
    tb = _resolve(b)
    if ta is None or tb is None:
        return
    result = meet(ta, tb)
    info_line(f"{HEADER}meet({a}, {b}){RESET}")
    info_line(f"  {_fmt_tuple(ta)}")
    info_line(f"  ⊓")
    info_line(f"  {_fmt_tuple(tb)}")
    info_line(f"  {BOLD}={RESET}")
    info_line(f"  {_fmt_tuple(result)}")


def cmd_compare(a: str, b: str):
    """Side-by-side structural comparison."""
    ta = _resolve(a)
    tb = _resolve(b)
    if ta is None or tb is None:
        return

    d = distance(ta, tb)
    deltas = delta_primitives(ta, tb)

    separator()
    info_line(f"  {a:20s}  {b:20s}")
    info_line(f"  {'─'*20}  {'─'*20}")

    for k in ["D", "T", "R", "P", "F", "K", "G", "Gamma", "Phi", "H", "S", "W"]:
        va = getattr(ta, k)
        vb = getattr(tb, k)
        marker = f" {WARN}◀{RESET}" if va != vb else ""
        info_line(f"  {va.value:20s}  {vb.value:20s}{marker}")

    warning_line(f"\n  Distance: {WARN}{d}{RESET}")
    info_line(f"  Deltas: {CYAN}{deltas}{RESET}")


def cmd_spectrum():
    """Show the psychiatric φ̂ spectrum."""
    separator()
    info_line(f"  The φ̂ axis spans all three major psychiatric conditions:\n")
    for name, t in PSYCHIATRIC_SPECTRUM.items():
        cs = c_score(t)
        tr = tier(t)
        info_line(f"  φ̂={t.Phi.value}  {name:20s}  C={cs:.4f}  {tr}")

    info_line(f"\n{SUBHEAD}Key insight:{RESET}")
    info_line(f"  Depression (φ̂=𐑢) → Healthy (φ̂=⊙) → Schizophrenia/Mania (φ̂=𐑣)")
    info_line(f"  Distance from depression to health: {distance(DEPRESSION, HEALTHY_BRAIN)}")
    info_line(f"  Distance from schizophrenia to health: {distance(SCHIZOPHRENIA, HEALTHY_BRAIN)}")
    info_line(f"  Schizophrenia vs Mania: K differs only (𐑧 vs 𐑪), d=1.0")
    info_line(f"  HIV = Bipolar Mania structurally (d=0.0)")


def cmd_operate(disease: str, operation: str):
    """Show what happens when a structural operation is applied to a disease."""
    if disease not in THERAPIES:
        info_line(f"{ERR}Unknown disease: {disease}{RESET}")
        return

    th = THERAPIES[disease]
    PRIM_MAP = {"φ̂": "Phi", "Ħ": "H", "Ð": "D", "Þ": "T", "Ř": "R",
                "Φ": "P", "ƒ": "F", "Ç": "K", "Γ": "G", "ɢ": "Gamma",
                "Σ": "S", "Ω": "W"}
    dt = th.disease_type
    ht = th.health_type

    info_line(f"{HEADER}Structural Operation: {operation}({disease}){RESET}\n")

    if operation == "distance":
        d = distance(dt, ht)
        info_line(f"  d({disease}, health) = {WARN}{d}{RESET}")
        return

    info_line(f"  Disease:  {_fmt_tuple(dt)}")
    info_line(f"  Health:   {_fmt_tuple(ht)}")

    if operation == "tensor":
        result = tensor(dt, ht)
        info_line(f"  Tensor:   {_fmt_tuple(result)}")
        d = distance(result, ht)
        info_line(f"  d(tensor, health) = {d}")
    elif operation == "meet":
        result = meet(dt, ht)
        info_line(f"  Meet:     {_fmt_tuple(result)}")
        d = distance(result, ht)
        info_line(f"  d(meet, health) = {d}")
    elif operation == "join":
        result = join(dt, ht)
        info_line(f"  Join:     {_fmt_tuple(result)}")
        d = distance(result, ht)
        info_line(f"  d(join, health) = {d}")
    else:
        info_line(f"{ERR}Unknown operation: {operation}. Use: tensor, meet, join, distance{RESET}")


# ─────────────────────────────────────────────────────────────────────
# RESOLVER
# ─────────────────────────────────────────────────────────────────────

def _resolve(name: str):
    """Resolve a type name to an Imscription."""
    if name in DISEASE_TYPES:
        return DISEASE_TYPES[name]
    if name in HEALTH_TYPES:
        return HEALTH_TYPES[name]
    if name in PSYCHIATRIC_SPECTRUM:
        return PSYCHIATRIC_SPECTRUM[name]
    # Try therapy keys
    if name in THERAPIES:
        return THERAPIES[name].disease_type
    # Try specific known types
    known = {
        "art": ART, "nmda": NMDA_SYSTEM, "dopamine": DOPAMINE_MESOLIMBIC,
        "normal_flora": NORMAL_FLORA, "normal_ovarian": NORMAL_OVARIAN,
        "normal_cftr": NORMAL_CFTR, "normal_urate": NORMAL_URATE,
        "normal_immune": NORMAL_IMMUNE, "homeopathic": HOMEOPATHIC_REMEDY,
    }
    if name in known:
        return known[name]
    info_line(f"{ERR}Unknown type: {name}{RESET}")
    return None


# Import these for resolver
from shared.rich_output import *
from .types import (
    ART, NMDA_SYSTEM, DOPAMINE_MESOLIMBIC, NORMAL_FLORA, NORMAL_OVARIAN,
    NORMAL_CFTR, NORMAL_URATE, NORMAL_IMMUNE, HOMEOPATHIC_REMEDY,
    HEALTHY_BRAIN, DEPRESSION, SCHIZOPHRENIA, BIPOLAR_MANIA,
)


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ["list"]

    if not args:
        cmd_list()
        return

    cmd = args[0]

    try:
        if cmd == "list":
            cmd_list()
        elif cmd == "diagnose" and len(args) >= 2:
            cmd_diagnose(args[1])
        elif cmd == "therapy" and len(args) >= 2:
            cmd_therapy(args[1])
        elif cmd == "tensor" and len(args) >= 3:
            cmd_tensor(args[1], args[2])
        elif cmd == "meet" and len(args) >= 3:
            cmd_meet(args[1], args[2])
        elif cmd == "compare" and len(args) >= 3:
            cmd_compare(args[1], args[2])
        elif cmd == "spectrum":
            cmd_spectrum()
        elif cmd == "operate" and len(args) >= 3:
            cmd_operate(args[1], args[2])
        elif cmd in ("help", "-h", "--help"):
            print(__doc__)
        else:
            info_line(f"{ERR}Unknown command: {cmd}{RESET}")
            print(__doc__)
    except Exception as e:
        error_line(f"{ERR}Error: {e}{RESET}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
