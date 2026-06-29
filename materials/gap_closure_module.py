"""
Gap Closure Module — Self-Organoid Augmentation Suite
======================================================
Complete structural theory with distance, tier, Frobenius verification,
EXACTOR pathway analysis, and closure verification.

Author: Lando⊗⊙perator
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math
from shared.rich_output import *


# ─── Primitive Value Enums ───────────────────────────────────────

class D(Enum):
    WEDGE = "wedge"        # 𐑛 — 0d point
    TRIANGLE = "triangle"  # 𐑨 — 2d surface
    INFTY = "infty"        # 𐑼 — infinite-dimensional
    ODOT = "odot"          # 𐑦 — self-written (holographic)

class T(Enum):
    NETWORK = "network"    # 𐑡 — branching
    IN = "in"              # 𐑰 — containment
    BOWTIE = "bowtie"      # 𐑥 — crossing
    BOXTIMES = "boxtimes"  # 𐑶 — irreducible product
    ODOT = "odot"          # 𐑸 — self-referential topology

class R(Enum):
    SUPER = "super"        # 𐑩 — supervenience
    CAT = "cat"            # 𐑑 — functorial
    DAGGER = "dagger"      # 𐑽 — adjoint
    LR = "lr"              # 𐑾 — bidirectional feedback

class P(Enum):
    ASYM = "asym"          # 𐑗 — none
    PSI = "psi"            # 𐑿 — quantum superposition
    PM = "pm"              # 𐑬 — partial Z2
    SYM = "sym"            # 𐑯 — full symmetry
    FROB = "frob"          # 𐑹 — Frobenius-special (μ∘δ=id)

class F(Enum):
    CLASSICAL = "classical"  # 𐑱 — classical
    THERMAL = "thermal"      # 𐑞 — thermal / noisy
    QUANTUM = "quantum"      # 𐑐 — quantum coherence

class K(Enum):
    FAST = "fast"            # 𐑘 — driven
    MBL = "mbl"              # 𐑺 — many-body localized
    SLOW = "slow"            # 𐑧 — near-equilibrium
    MODERATE = "moderate"    # 𐑤 — moderate
    TRAP = "trap"            # 𐑪 — trapped (ordered)

class Gamma(Enum):
    LOCAL = "local"          # 𐑚 — nearest-neighbor
    MESO = "meso"            # 𐑔 — mesoscale
    MAXIMAL = "maximal"      # 𐑲 — long-range / universal

class G(Enum):
    CONJ = "conj"            # 𐑝 — all-simultaneous (AND)
    DISJ = "disj"            # 𐑜 — alternate (OR)
    SEQ = "seq"              # 𐑠 — ordered steps
    BROAD = "broad"          # 𐑵 — one-to-all broadcast

class Phi(Enum):
    SUB = "sub"              # 𐑢 — sub-critical
    CRIT = "crit"            # ⊙ — critical (self-modeling)
    C_COMPLEX = "c_complex"  # 𐑮 — complex-plane critical
    EP = "ep"                # 𐑻 — exceptional point
    SUPER = "super"          # 𐑣 — supercritical / runaway

class H(Enum):
    M0 = "m0"                # 𐑓 — Markov 0 (memoryless)
    M1 = "m1"                # 𐑒 — Markov 1
    M2 = "m2"                # 𐑖 — Markov 2
    ETERNAL = "eternal"      # 𐑫 — no finite Markov order

class S(Enum):
    ONE_ONE = "one_one"      # 𐑙 — 1:1 one type, one instance
    N_N = "n_n"              # 𐑕 — many identical
    N_M = "n_m"              # 𐑳 — multiple distinct types

class Omega(Enum):
    TRIVIAL = "trivial"      # 𐑷 — none
    Z2 = "z2"                # 𐑴 — Z2 parity-protected
    ZWIND = "zwind"          # 𐑭 — integer winding
    NONABEL = "nonabel"      # 𐑟 — non-Abelian braiding



# ─── Imcription Dataclass ─────────────────────────────────────────

@dataclass(frozen=True)
class Imcription:
    """A 12-tuple structural type in the Imscribing Grammar."""
    D: D
    T: T
    R: R
    P: P
    F: F
    K: K
    Gamma: Gamma
    G: G
    Phi: Phi
    H: H
    S: S
    Omega: Omega

    def to_tuple(self) -> tuple:
        return (self.D, self.T, self.R, self.P, self.F, self.K,
                self.Gamma, self.G, self.Phi, self.H, self.S, self.Omega)

    def display(self) -> str:
        """Shavian tuple display string."""
        glyphs = {
            D.WEDGE: "𐑛", D.TRIANGLE: "𐑨", D.INFTY: "𐑼", D.ODOT: "𐑦",
            T.NETWORK: "𐑡", T.IN: "𐑰", T.BOWTIE: "𐑥", T.BOXTIMES: "𐑶", T.ODOT: "𐑸",
            R.SUPER: "𐑩", R.CAT: "𐑑", R.DAGGER: "𐑽", R.LR: "𐑾",
            P.ASYM: "𐑗", P.PSI: "𐑿", P.PM: "𐑬", P.SYM: "𐑯", P.FROB: "𐑹",
            F.CLASSICAL: "𐑱", F.THERMAL: "𐑞", F.QUANTUM: "𐑐",
            K.FAST: "𐑘", K.MBL: "𐑺", K.SLOW: "𐑧", K.MODERATE: "𐑤", K.TRAP: "𐑪",
            Gamma.LOCAL: "𐑚", Gamma.MESO: "𐑔", Gamma.MAXIMAL: "𐑲",
            G.CONJ: "𐑝", G.DISJ: "𐑜", G.SEQ: "𐑠", G.BROAD: "𐑵",
            Phi.SUB: "𐑢", Phi.CRIT: "⊙", Phi.C_COMPLEX: "𐑮", Phi.EP: "𐑻", Phi.SUPER: "𐑣",
            H.M0: "𐑓", H.M1: "𐑒", H.M2: "𐑖", H.ETERNAL: "𐑫",
            S.ONE_ONE: "𐑙", S.N_N: "𐑕", S.N_M: "𐑳",
            Omega.TRIVIAL: "𐑷", Omega.Z2: "𐑴", Omega.ZWIND: "𐑭", Omega.NONABEL: "𐑟",
        }
        g = lambda e: glyphs.get(e, "?")
        return f"⟨{g(self.D)}{g(self.T)}{g(self.R)}{g(self.P)}{g(self.F)}"
        f"{g(self.K)}{g(self.Gamma)}{g(self.G)}{g(self.Phi)}"
        f"{g(self.H)}{g(self.S)}{g(self.Omega)}⟩"

    def frobenius_closed(self) -> bool:
        """μ∘δ=id holds exactly: P=FROB, Phi=CRIT, Omega=ZWIND."""
        return (self.P == P.FROB and self.Phi == Phi.CRIT
                and self.Omega == Omega.ZWIND)

    def tier(self) -> str:
        """Ouroboricity tier."""
        if self.frobenius_closed() and self.D == D.ODOT:
            return "O_∞"
        if self.frobenius_closed():
            return "O₂"  # Frobenius pillars but not self-written
        if self.Phi == Phi.CRIT and self.H in (H.M2, H.ETERNAL):
            return "O₂"
        if self.Phi == Phi.CRIT:
            return "O₁"
        return "O₀"

    def consciousness_score(self) -> float:
        """C-score: both gates must be open."""
        gate1 = (self.Phi == Phi.CRIT)  # Self-modeling gate
        gate2 = (self.K == K.SLOW)       # Near-equilibrium gate
        if gate1 and gate2:
            return 1.0
        elif gate1:
            return 0.5  # Gate 1 open, Gate 2 closed
        return 0.0      # Gate 1 closed

    def verify_axioms(self) -> Dict[str, bool]:
        """Verify Axioms A, B, C."""
        return {
            "axiom_c": (self.D == D.ODOT and self.T == T.ODOT),
            "axiom_a": not (self.H == H.ETERNAL and self.K not in (K.MODERATE, K.TRAP)),
            "axiom_b": not (self.Omega in (Omega.ZWIND, Omega.NONABEL)
                           and self.D in (D.WEDGE, D.TRIANGLE)),
        }



# ─── Distance & Algebra ──────────────────────────────────────────

# Ordinal positions (0-indexed) for weighted Euclidean distance
_ORD = {
    D: {D.WEDGE:0, D.TRIANGLE:1, D.INFTY:2, D.ODOT:3},
    T: {T.NETWORK:0, T.IN:1, T.BOWTIE:2, T.BOXTIMES:3, T.ODOT:4},
    R: {R.SUPER:0, R.CAT:1, R.DAGGER:2, R.LR:3},
    P: {P.ASYM:0, P.PSI:1, P.PM:2, P.SYM:3, P.FROB:4},
    F: {F.CLASSICAL:0, F.THERMAL:1, F.QUANTUM:2},
    K: {K.FAST:0, K.MBL:1, K.SLOW:2, K.MODERATE:3, K.TRAP:4},
    Gamma: {Gamma.LOCAL:0, Gamma.MESO:1, Gamma.MAXIMAL:2},
    G: {G.CONJ:0, G.DISJ:1, G.SEQ:2, G.BROAD:3},
    Phi: {Phi.SUB:0, Phi.CRIT:1, Phi.C_COMPLEX:2, Phi.EP:3, Phi.SUPER:4},
    H: {H.M0:0, H.M1:1, H.M2:2, H.ETERNAL:3},
    S: {S.ONE_ONE:0, S.N_N:1, S.N_M:2},
    Omega: {Omega.TRIVIAL:0, Omega.Z2:1, Omega.ZWIND:2, Omega.NONABEL:3},
}

_WEIGHTS = {D:2.0, T:2.0, R:1.0, P:2.0, F:1.0, K:1.0,
            Gamma:1.0, G:1.0, Phi:2.0, H:1.0, S:0.5, Omega:2.0}

_PROPAGATE = {D:None, T:None, R:None, P:None, F:None, K:None,
              Gamma:None, G:None, Phi:None, H:None, S:None, Omega:None}
for cls, weight in _WEIGHTS.items():
    _PROPAGATE[cls] = weight


def _ordinal_distance(v1, v2, cls) -> float:
    """Normalized ordinal distance between two values of the same primitive class."""
    order = _ORD[cls]
    n = len(order) - 1
    if n == 0:
        return 0.0
    return abs(order[v2] - order[v1]) / n


def distance(a: Imcription, b: Imcription) -> Tuple[float, List[dict]]:
    """Weighted Euclidean distance with per-primitive conflict list."""
    total = 0.0
    conflicts = []
    for cls, weight in _WEIGHTS.items():
        va = getattr(a, cls.__name__)
        vb = getattr(b, cls.__name__)
        if va != vb:
            od = _ordinal_distance(va, vb, cls)
            total += (weight * od) ** 2
            conflicts.append({
                "primitive": cls.__name__,
                "a": va.value,
                "b": vb.value,
                "ordinal_delta": round(od, 4),
                "weight": weight,
            })
    return round(math.sqrt(total), 4), conflicts


def meet(a: Imcription, b: Imcription) -> Imcription:
    """Greatest lower bound: min ordinal on each primitive."""
    args = {}
    for cls in _ORD:
        va = getattr(a, cls.__name__)
        vb = getattr(b, cls.__name__)
        oa = _ORD[cls][va]
        ob = _ORD[cls][vb]
        min_val = va if oa <= ob else vb
        args[cls.__name__] = min_val
    return Imcription(**args)


def tensor(a: Imcription, b: Imcription) -> Imcription:
    """Tensor product: max on union, min on P and F."""
    args = {}
    for cls in _ORD:
        va = getattr(a, cls.__name__)
        vb = getattr(b, cls.__name__)
        oa = _ORD[cls][va]
        ob = _ORD[cls][vb]
        if cls in (P, F):
            args[cls.__name__] = va if oa <= ob else vb  # min on P, F
        else:
            args[cls.__name__] = va if oa >= ob else vb  # max on others
    # ⊙_3 ABSORPTION: tensor(⊙, EP) = EP
    if args["Phi"] == Phi.EP:
        pass  # absorption already handled by max rule; meet would preserve ⊙
    return Imcription(**args)


def promotions(source: Imcription, target: Imcription) -> List[dict]:
    """Primitives that need promotion to reach target tier."""
    promos = []
    for cls in _ORD:
        vs = getattr(source, cls.__name__)
        vt = getattr(target, cls.__name__)
        if vs != vt:
            promos.append({
                "primitive": cls.__name__,
                "from": vs.value,
                "to": vt.value,
                "ordinal_delta": _ordinal_distance(vs, vt, cls),
                "weight": _WEIGHTS[cls],
            })
    return promos



# ─── Predefined Systems ──────────────────────────────────────────

BASELINE = Imcription(
    D=D.ODOT, T=T.ODOT, R=R.LR, P=P.FROB, F=F.QUANTUM,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.SEQ, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.ZWIND)

MYELIN = Imcription(
    D=D.INFTY, T=T.IN, R=R.LR, P=P.FROB, F=F.QUANTUM,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.SEQ, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.ZWIND)

VASCULATURE_OPEN = Imcription(
    D=D.ODOT, T=T.ODOT, R=R.LR, P=P.FROB, F=F.THERMAL,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.SEQ, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.ZWIND)

VASCULATURE_CLOSED = Imcription(
    D=D.ODOT, T=T.ODOT, R=R.LR, P=P.FROB, F=F.QUANTUM,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.SEQ, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.ZWIND)

MEDIUM_OPEN = Imcription(
    D=D.WEDGE, T=T.IN, R=R.LR, P=P.FROB, F=F.CLASSICAL,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.CONJ, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.TRIVIAL)

MEDIUM_CLOSED = Imcription(
    D=D.ODOT, T=T.IN, R=R.LR, P=P.FROB, F=F.CLASSICAL,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.SEQ, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.ZWIND)

OPTOGENETIC = Imcription(
    D=D.INFTY, T=T.BOWTIE, R=R.LR, P=P.FROB, F=F.QUANTUM,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.BROAD, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.ZWIND)

ECM = Imcription(
    D=D.TRIANGLE, T=T.NETWORK, R=R.LR, P=P.PM, F=F.CLASSICAL,
    K=K.SLOW, Gamma=Gamma.LOCAL, G=G.BROAD, Phi=Phi.SUB,
    H=H.M1, S=S.ONE_ONE, Omega=Omega.TRIVIAL)

IMMUNE = Imcription(
    D=D.TRIANGLE, T=T.NETWORK, R=R.LR, P=P.PM, F=F.CLASSICAL,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.BROAD, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.Z2)

CORE_OPEN = Imcription(
    D=D.ODOT, T=T.ODOT, R=R.LR, P=P.FROB, F=F.CLASSICAL,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.BROAD, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.ZWIND)

CORE_CLOSED = Imcription(
    D=D.ODOT, T=T.ODOT, R=R.LR, P=P.FROB, F=F.QUANTUM,
    K=K.MODERATE, Gamma=Gamma.MAXIMAL, G=G.BROAD, Phi=Phi.CRIT,
    H=H.ETERNAL, S=S.N_M, Omega=Omega.ZWIND)

# ─── Gap Closure Registry ────────────────────────────────────────

GAPS = [
    {
        "name": "Ouroboric Vasculature",
        "open": VASCULATURE_OPEN,
        "closed": VASCULATURE_CLOSED,
        "mechanism": "NV-center diamond quantum magnetometry for single-spin O2 detection",
        "exactor": "EXACTOR-σ (self-dual lock via dual-OPO phase lock)",
        "trl": 4,
    },
    {
        "name": "Perfect Nutrient Medium",
        "open": MEDIUM_OPEN,
        "closed": MEDIUM_CLOSED,
        "mechanism": "EXACTOR-Ω (PLL-quantized nutrient cycling) + EXACTOR-τ "
                     "(holographic self-writing) + sequential metabolic gating",
        "exactor": "EXACTOR-Ω + EXACTOR-τ",
        "trl": 4,
    },
    {
        "name": "Frobenius Core",
        "open": CORE_OPEN,
        "closed": CORE_CLOSED,
        "mechanism": "Single-photon NADH/NAD+ FLIM with TCSPC at single-mitochondrion resolution",
        "exactor": "EXACTOR-ε (counterdiabatic driving, gauge potential integral = 0)",
        "trl": 5,
    },
]

DELIBERATELY_OPEN = [
    {
        "name": "ECM Scaffold",
        "imcription": ECM,
        "rationale": "Transient chrysalis — must degrade. Closure = failure to mature.",
    },
    {
        "name": "Immune Sentinel",
        "imcription": IMMUNE,
        "rationale": "Dormant guardian — must not participate in μ∘δ=id loop. "
                     "Closure = autoimmunity.",
    },
]

ALL_SYSTEMS = {
    "baseline": BASELINE,
    "myelin": MYELIN,
    "vasculature_open": VASCULATURE_OPEN,
    "vasculature_closed": VASCULATURE_CLOSED,
    "medium_open": MEDIUM_OPEN,
    "medium_closed": MEDIUM_CLOSED,
    "optogenetic": OPTOGENETIC,
    "ecm": ECM,
    "immune": IMMUNE,
    "core_open": CORE_OPEN,
    "core_closed": CORE_CLOSED,
}



# ─── Analysis Functions ──────────────────────────────────────────

def analyze_gap(gap: dict) -> dict:
    """Full structural analysis of a single gap."""
    d, conflicts = distance(gap["open"], gap["closed"])
    return {
        "name": gap["name"],
        "distance": d,
        "conflicts": conflicts,
        "tier_before": gap["open"].tier(),
        "tier_after": gap["closed"].tier(),
        "frob_before": gap["open"].frobenius_closed(),
        "frob_after": gap["closed"].frobenius_closed(),
        "mechanism": gap["mechanism"],
        "exactor": gap["exactor"],
        "trl": gap["trl"],
        "axioms_before": gap["open"].verify_axioms(),
        "axioms_after": gap["closed"].verify_axioms(),
        "cscore_before": gap["open"].consciousness_score(),
        "cscore_after": gap["closed"].consciousness_score(),
    }


def analyze_open(system: dict) -> dict:
    """Analysis of a deliberately open system."""
    imp = system["imcription"]
    d, _ = distance(BASELINE, imp)
    return {
        "name": system["name"],
        "tier": imp.tier(),
        "frobenius": imp.frobenius_closed(),
        "distance_from_baseline": d,
        "rationale": system["rationale"],
    }


def full_analysis() -> dict:
    """Run complete gap closure analysis."""
    results = {
        "baseline": {
            "tier": BASELINE.tier(),
            "frobenius": BASELINE.frobenius_closed(),
            "cscore": BASELINE.consciousness_score(),
            "axioms": BASELINE.verify_axioms(),
        },
        "augmentations": {},
        "gaps": [],
        "deliberately_open": [],
        "summary": {},
    }

    # Augmentation status
    for name, imp in [
        ("myelin", MYELIN), ("vasculature", VASCULATURE_OPEN),
        ("medium", MEDIUM_OPEN), ("optogenetic", OPTOGENETIC),
        ("ecm", ECM), ("immune", IMMUNE),
    ]:
        d, _ = distance(BASELINE, imp)
        results["augmentations"][name] = {
            "tier": imp.tier(),
            "frobenius": imp.frobenius_closed(),
            "distance_from_baseline": d,
        }

    # Gap analysis
    for gap in GAPS:
        results["gaps"].append(analyze_gap(gap))

    # Deliberately open
    for sys in DELIBERATELY_OPEN:
        results["deliberately_open"].append(analyze_open(sys))

    # Summary
    closable = len(GAPS)
    native_closed = sum(1 for g in GAPS if g["open"].frobenius_closed())
    closed_after = sum(1 for g in GAPS if g["closed"].frobenius_closed())
    results["summary"] = {
        "total_systems": 7,
        "native_frobenius": native_closed + 2,  # myelin + optogenetic
        "gaps_identified": closable,
        "gaps_closed": closed_after,
        "deliberately_open": 2,
        "all_closable_closed": closed_after == closable,
    }

    return results


def print_analysis():
    """Pretty-print the full analysis."""
    results = full_analysis()

    print("=" * 64)
    info_line("GAP CLOSURE — Self-Organoid Augmentation Suite")
    print("=" * 64)

    b = results["baseline"]
    print(f"\nBASELINE: tier={b['tier']}, frob={b['frobenius']}, cscore={b['cscore']}")
    info_line(f"  axioms: {b['axioms']}")

    info_line("\n--- AUGMENTATIONS ---")
    for name, data in results["augmentations"].items():
        info_line(f"  {name:20s}  tier={data['tier']:5s}  frob={str(data['frobenius']):5s}  d={data['distance_from_baseline']}")

    info_line("\n--- GAPS ---")
    for g in results["gaps"]:
        print(f"\n  {g['name']}:")
        info_line(f"    distance: {g['distance']}")
        info_line(f"    tier: {g['tier_before']} -> {g['tier_after']}")
        info_line(f"    frob: {g['frob_before']} -> {g['frob_after']}")
        info_line(f"    cscore: {g['cscore_before']} -> {g['cscore_after']}")
        info_line(f"    mechanism: {g['mechanism']}")
        info_line(f"    exactor: {g['exactor']}")
        for c in g['conflicts']:
            info_line(f"      {c['primitive']}: {c['a']} -> {c['b']} (Δ={c['ordinal_delta']:.2f}, w={c['weight']})")

    info_line("\n--- DELIBERATELY OPEN ---")
    for s in results["deliberately_open"]:
        print(f"\n  {s['name']}: tier={s['tier']}, d_baseline={s['distance_from_baseline']}")
        info_line(f"    {s['rationale']}")

    print("\n" + "=" * 64)
    s = results["summary"]
    print(f"SUMMARY: {s['total_systems']} systems, {s['gaps_identified']} gaps, "
          f"{s['gaps_closed']} closed, {s['deliberately_open']} deliberately open.")
    print(f"All closable gaps closed: {s['all_closable_closed']}")
    print("=" * 64)

    return results


# ─── Main ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print_analysis()
