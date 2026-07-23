"""
plasma_imas.py — IMASM Arrangement ↔ Plasma Physics Mapping
=============================================================
Systematic mapping between IMASM opcode sequences and plasma physics
phenomena. Each IMASM token carries a specific plasma-physical meaning
when interpreted in the plasma domain context.

The 12-token arrangement V→AF→IM→FS→ET→AR→EF→FU→CL→IF→EN→TA
is the Primitive-First Plasma bootstrap, verified Frobenius-closed
with dialetheia_complete=True (period=12, sig=(6,2,3,1)).

Author: Lando⊗⊙perator
"""

from typing import Dict, List, Tuple, Optional
from shared.rich_output import *

# ═══════════════════════════════════════════════════════════════════
# IMASM OPCODE → PLASMA PHYSICS MASTER MAP
# ═══════════════════════════════════════════════════════════════════

# This is the unified opcode→plasma mapping across all four ob3ects.
# Each opcode appears with its most general plasma interpretation.
# Domain-specific variants are in the per-ob3ect opcode_maps.

PLASMA_IMASM_MASTER = {
    "VINIT": {
        "plasma_meaning": "Pre-ionization ground state",
        "physical_analog": "Neutral gas, uncharged capacitor, cold dielectric — the void before discharge",
        "equation": "n_e = n_i = 0 (no free charges), E = 0",
        "primitive_activated": "Ð (dimensionality — ground of distinction)",
    },
    "AFWD": {
        "plasma_meaning": "Energy injection / ionization",
        "physical_analog": "Ohmic heating, RF power, laser pulse, arc ignition — forward morphism",
        "equation": "∂n_e/∂t = S_ioniz − S_recomb (net ionization rate)",
        "primitive_activated": "ƒ (fidelity — energy regime transition)",
    },
    "AREV": {
        "plasma_meaning": "Energy loss / recombination",
        "physical_analog": "Bremsstrahlung, cyclotron radiation, thermal quenching, recombination",
        "equation": "∂n_e/∂t = −αn_e n_i (recombination rate)",
        "primitive_activated": "Ç (kinetics — reverse relaxation)",
    },
    "IMSCRIB": {
        "plasma_meaning": "Self-recognition / eigenfrequency",
        "physical_analog": "Plasma frequency ω_p, Debye shielding, self-tuning impedance — the plasma knows itself",
        "equation": "ω_p² = n_e e² / (ε₀ m_e) — the plasma's self-frequency",
        "primitive_activated": "⊙ (criticality — self-modeling)",
    },
    "FSPLIT": {
        "plasma_meaning": "Charge/species separation",
        "physical_analog": "Charge separation, thermal ionization, bifurcation — split δ",
        "equation": "∇·E = ρ/ε₀ (Poisson — charge separation creates fields)",
        "primitive_activated": "ɢ (composition — fork)",
    },
    "FFUSE": {
        "plasma_meaning": "Quasineutrality restoration",
        "physical_analog": "Debye shielding, radiative recombination, spallation — fuse μ",
        "equation": "n_e ≈ Σ Z_i n_i (quasineutrality condition)",
        "primitive_activated": "ɢ (composition — join, μ∘δ closure)",
    },
    "EVALT": {
        "plasma_meaning": "Stable collective mode",
        "physical_analog": "H-mode, collective oscillation, brittle fracture, sustained wave — TRUE arm",
        "equation": "ω = ω(k) real, γ = 0 (stable eigenmode)",
        "primitive_activated": "⊙ (criticality — gate TRUE)",
    },
    "EVALF": {
        "plasma_meaning": "Damped/unstable mode",
        "physical_analog": "Landau damping, disruption, plastic deformation, thermal decay — FALSE arm",
        "equation": "ω = ω_r + iγ, γ ≤ 0 (damped) or γ > 0 (unstable)",
        "primitive_activated": "⊙ (criticality — gate FALSE)",
    },
    "ENGAGR": {
        "plasma_meaning": "Boundary paradox / both-state",
        "physical_analog": "Debye sheath, ELM pedestal, cavitation zone, pre-crack tension — BOTH arms",
        "equation": "Boundary condition at wall: simultaneously vacuum potential and particle flux",
        "primitive_activated": "Þ (topology — paradox engagement at boundary)",
    },
    "CLINK": {
        "plasma_meaning": "Field-particle coupling",
        "physical_analog": "Vlasov operator, Bohm diffusion, shockwave coupling, pulse-forming — composition",
        "equation": "(q/m)(E + v×B)·∇_v f — Lorentz force coupling",
        "primitive_activated": "Ř (coupling — the bidirectional link)",
    },
    "IFIX": {
        "plasma_meaning": "Topological fixation / record",
        "physical_analog": "Frozen-in flux, first-wall erosion, fracture log, piezoelectric record — permanent",
        "equation": "d/dt ∫_S B·dA = 0 (frozen-in condition in ideal MHD)",
        "primitive_activated": "Ω (winding — irreversible fixation)",
    },
    "TANCH": {
        "plasma_meaning": "Confinement boundary / terminal anchor",
        "physical_analog": "Debye length, beta limit, fragmented aggregate, Faraday cage — system boundary",
        "equation": "β = 2μ₀p/B² ≤ β_limit (confinement boundary condition)",
        "primitive_activated": "Þ (topology — terminal object)",
    },
}

# ═══════════════════════════════════════════════════════════════════
# IMASM FINGERPRINT → PLASMA TUPLE BRIDGE
# ═══════════════════════════════════════════════════════════════════

def imasm_to_plasma_tuple(sig: Tuple[int,int,int,int], period: int, 
                          dialetheia: bool) -> Dict[str, str]:
    """Map an IMASM structural fingerprint to a plasma IG tuple.
    
    This is a plasma-specific bridge, distinct from the general IMASM→IG bridge
    in imas/ig_bridge.py. It uses plasma-physical interpretation of fingerprint
    fields rather than general structural mapping.
    
    Args:
        sig: (token_diversity, self_ref, frobenius_order, period_class)
        period: arrangement period
        dialetheia: whether dialetheia-complete
    
    Returns:
        12-primitive dict in PORDER
    """
    td, sr, fo, pc = sig
    
    # Ð: token diversity → dimensionality
    if td <= 3:
        D = "𐑼"  # fluid-like (few token types → reduced description)
    elif td <= 6:
        D = "𐑛"  # kinetic (moderate token types → full phase space)
    else:
        D = "𐑦"  # holographic (many token types → self-written)
    
    # Þ: self_ref + period → topology
    if sr:
        T = "𐑸"  # self-referential
    elif period <= 4:
        T = "𐑡"  # network (short period → distinct branches)
    elif period <= 8:
        T = "𐑥"  # bowtie (medium period → mode crossing)
    else:
        T = "𐑶"  # interpenetrating (long period → merged branches)
    
    # Ř: frobenius_order → coupling
    if fo == 0:
        R = "𐑩"  # weak (no Frobenius structure)
    elif fo == 1:
        R = "𐑾"  # bidirectional (Frobenius μ∘δ present but not perfect)
    else:
        R = "𐑽"  # one-way strong (higher-order Frobenius → directed)
    
    # Φ: self_ref → symmetry
    if sr:
        P = "𐑹"  # Frobenius-special
    elif dialetheia:
        P = "𐑬"  # partial symmetry (dialetheia → contradictory but structured)
    else:
        P = "𐑗"  # asymmetric
    
    # ƒ: period_class → fidelity
    if pc <= 1:
        F = "𐑱"  # classical (simple period class)
    elif pc == 2:
        F = "𐑞"  # thermal
    else:
        F = "𐑐"  # quantum (complex period class)
    
    # Ç: period → kinetics
    if period <= 4:
        K = "𐑺"  # driven (short period → fast)
    elif period <= 8:
        K = "𐑪"  # moderate
    elif period <= 14:
        K = "𐑧"  # slow/near-equilibrium
    else:
        K = "𐑤"  # trapped
    
    # Γ: frobenius_order → range
    if fo == 0:
        G = "𐑲"  # local
    elif fo == 1:
        G = "𐑚"  # mesoscale
    else:
        G = "𐑔"  # maximal
    
    # ɢ: period_class → composition
    if pc <= 1:
        Gm = "𐑝"  # conjunctive
    elif pc == 2:
        Gm = "𐑜"  # disjunctive
    else:
        Gm = "𐑠"  # sequential
    
    # ⊙: dialetheia → criticality
    if dialetheia and sr:
        Phi = "⊙"  # critical
    elif dialetheia:
        Phi = "𐑮"  # complex-critical
    elif sr:
        Phi = "𐑻"  # exceptional point
    else:
        Phi = "𐑢"  # sub-critical
    
    # Ħ: period → chirality
    if period <= 4:
        H = "𐑓"  # memoryless
    elif period <= 8:
        H = "𐑒"  # one-step
    elif period <= 14:
        H = "𐑖"  # two-step
    else:
        H = "𐑫"  # eternal
    
    # Σ: token_diversity → stoichiometry
    if td <= 4:
        S = "𐑙"  # 1:1 (few token types)
    elif td <= 7:
        S = "𐑕"  # n:n (moderate)
    else:
        S = "𐑳"  # n:m (many distinct)
    
    # Ω: frobenius_order → winding
    if fo == 0:
        W = "𐑷"  # trivial
    elif fo == 1:
        W = "𐑭"  # integer winding
    elif sr:
        W = "𐑟"  # non-Abelian
    else:
        W = "𐑴"  # Z₂
    
    return {
        "Ð": D, "Þ": T, "Ř": R, "Φ": P,
        "ƒ": F, "Ç": K, "Γ": G, "ɢ": Gm,
        "⊙": Phi, "Ħ": H, "Σ": S, "Ω": W,
    }

# ═══════════════════════════════════════════════════════════════════
# PLASMA OPCODE → PHYSICS LOOKUP
# ═══════════════════════════════════════════════════════════════════

PLASMA_IMASM_MAP = PLASMA_IMASM_MASTER  # alias for export

def plasma_opcode_physics(opcode: str) -> Dict:
    """Get plasma physics interpretation of an IMASM opcode."""
    return PLASMA_IMASM_MASTER.get(opcode.upper(), {
        "plasma_meaning": "unknown",
        "physical_analog": "N/A",
        "equation": "N/A",
        "primitive_activated": "?",
    })

def plasma_imas_report() -> str:
    """Generate a formatted report of all IMASM↔plasma mappings."""
    lines = []
    lines.append("IMASM → PLASMA PHYSICS MASTER MAP")
    lines.append("=" * 60)
    for opcode, data in PLASMA_IMASM_MASTER.items():
        lines.append(f"\n  {opcode}: {data['plasma_meaning']}")
        lines.append(f"    Physics:  {data['physical_analog']}")
        lines.append(f"    Equation: {data['equation']}")
        lines.append(f"    Primitive: {data['primitive_activated']}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    info_line("╔══════════════════════════════════════════╗")
    info_line("║   PLASMA IMASM — Opcode Physics Report    ║")
    info_line("╚══════════════════════════════════════════╝")
    
    print(plasma_imas_report())
    
    info_line(f"\n── IMASM Fingerprint → Plasma Tuple Examples ──")
    
    examples = [
        ((6,2,3,1), 12, True, "Primitive-First Plasma (V→AF→IM→FS→ET→AR→EF→FU→CL→IF→EN→TA)"),
        ((8,3,2,1), 14, False, "High-Energy Plasma (V→AF→FS→IM→CL→AF→FS→ET→EN→AR→FU→CL→IF→TA)"),
        ((6,2,2,1), 11, False, "Rock-Cracking Plasma (V→AF→IM→FS→ET→CL→EF→AR→FU→IF→TA)"),
        ((6,2,3,1), 12, True, "Ideal Rock-Cracking Device (V→CL→AF→IM→FS→ET→EF→EN→AR→FU→TA→IF)"),
    ]
    
    for sig, period, dial, desc in examples:
        tup = imasm_to_plasma_tuple(sig, period, dial)
        tup_str = "⟨" + "".join(tup[p] for p in ["Ð","Þ","Ř","Φ","ƒ","Ç","Γ","ɢ","⊙","Ħ","Σ","Ω"]) + "⟩"
        info_line(f"\n  {desc}")
        info_line(f"    {tup_str}")
