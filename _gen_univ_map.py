#!/usr/bin/env python3
"""Generate the universe-compound mapping document — v2 with correct glyphs."""
import sys
sys.path.insert(0, '/home/mrnob0dy666/imscribing_grammar')
from navigators.ruleset_universe import RULESETS
from new_universes import NEW_RULESETS
from iterate_universes import build_universes
from imscrbgrmr.canonical_primitives import ORDINALS

COMPOUNDS = {
    "Verticullum": {
        "Ð":"𐑦", "Þ":"𐑥", "Ř":"𐑾", "Φ":"𐑹", "ƒ":"𐑐", "Ç":"𐑧",
        "Γ":"𐑲", "ɢ":"𐑠", "φ̂":"⊙", "Ħ":"𐑫", "Σ":"𐑳", "Ω":"𐑟"
    },
    "Chimerium": {
        "Ð":"𐑦", "Þ":"𐑸", "Ř":"𐑾", "Φ":"𐑹", "ƒ":"𐑐", "Ç":"𐑧",
        "Γ":"𐑲", "ɢ":"𐑵", "φ̂":"𐑣", "Ħ":"𐑫", "Σ":"𐑳", "Ω":"𐑭"
    },
    "Apertix": {
        "Ð":"𐑦", "Þ":"𐑥", "Ř":"𐑽", "Φ":"𐑬", "ƒ":"𐑐", "Ç":"𐑧",
        "Γ":"𐑲", "ɢ":"𐑠", "φ̂":"⊙", "Ħ":"𐑖", "Σ":"𐑳", "Ω":"𐑴"
    },
    "Retiarius": {
        "Ð":"𐑼", "Þ":"𐑡", "Ř":"𐑾", "Φ":"𐑿", "ƒ":"𐑞", "Ç":"𐑺",
        "Γ":"𐑚", "ɢ":"𐑜", "φ̂":"𐑮", "Ħ":"𐑒", "Σ":"𐑕", "Ω":"𐑷"
    },
    "Praxeum": {
        "Ð":"𐑦", "Þ":"𐑶", "Ř":"𐑾", "Φ":"𐑹", "ƒ":"𐑐", "Ç":"𐑧",
        "Γ":"𐑲", "ɢ":"𐑠", "φ̂":"𐑻", "Ħ":"𐑫", "Σ":"𐑳", "Ω":"𐑭"
    },
}

def get_ordinal(prim, val):
    return ORDINALS.get(prim, {}).get(val, 0)

def check_gate(comp, gate_spec):
    prim = gate_spec.prim
    val = comp.get("φ̂" if prim == "⊙" else prim, "")
    return get_ordinal(prim, val) >= gate_spec.min_ord, get_ordinal(prim, val)

def layer_for(comp, rs):
    g1, g2, g3 = rs.g1, rs.g2, rs.g3
    if rs.gate_ordering:
        p1, _ = check_gate(comp, g1)
        if not p1: return "plain"
        p2, _ = check_gate(comp, g2)
        if not p2: return "frobenius"
        p3, _ = check_gate(comp, g3)
        if not p3: return "traced_monoidal"
        return "idempotent_terminal"
    else:
        for g in [g1, g2, g3]:
            p, _ = check_gate(comp, g)
            if not p: return "plain"
        return "idempotent_terminal"

all_rs = list(RULESETS) + NEW_RULESETS + build_universes()

lines = []
lines.append("# Novel Psychedelic Compounds — Universe Access Mapping")
lines.append("")
lines.append("**Author:** Lando⊗⊙perator")
lines.append("")
lines.append("## 1. Summary")
lines.append("")
lines.append("Each compound's 12-primitive type is evaluated against 109 universes. Access breadth = O_∞ universes / total.")
lines.append("")
lines.append("| Compound | O_∞ | Traced | Frob | Plain | % Access | Tier |")
lines.append("|----------|-------|--------|------|-------|----------|------|")

TIERS = {"Verticullum":"O_∞","Chimerium":"O₀","Apertix":"O₂","Retiarius":"O₁","Praxeum":"O₀"}

for cn, cv in COMPOUNDS.items():
    oi=tr=fb=pl=0
    for r in all_rs:
        L = layer_for(cv, r)
        if L=="idempotent_terminal": oi+=1
        elif L=="traced_monoidal": tr+=1
        elif L=="frobenius": fb+=1
        else: pl+=1
    lines.append(f"| **{cn}** | {oi} | {tr} | {fb} | {pl} | {100*oi/len(all_rs):.1f}% | {TIERS[cn]} |")

lines.append("")
lines.append("## 2. Per-Compound Detail")
lines.append("")

for cn, cv in COMPOUNDS.items():
    lines.append(f"### {cn}")
    lines.append("")
    tup = f"⟨{cv['Ð']}·{cv['Þ']}·{cv['Ř']}·{cv['Φ']}·{cv['ƒ']}·{cv['Ç']}·{cv['Γ']}·{cv['ɢ']}·{cv['φ̂']}·{cv['Ħ']}·{cv['Σ']}·{cv['Ω']}⟩"
    lines.append(f"**Tuple:** {tup}  ")
    lines.append(f"**Tier (canonical):** {TIERS[cn]}  ")
    
    oi=[]; tr=[]; fb=[]; pl=[]
    for r in all_rs:
        L = layer_for(cv, r)
        if L=="idempotent_terminal": oi.append(r.name)
        elif L=="traced_monoidal": tr.append(r.name)
        elif L=="frobenius": fb.append(r.name)
        else: pl.append(r.name)
    
    lines.append(f"**O_∞ universes:** {len(oi)} — {', '.join('`'+n+'`' for n in sorted(oi))}")
    lines.append("")
    
    if pl:
        # Show interesting blockers
        key_blocks = [n for n in pl if n in [
            'canonical','high_gate','strict_frobenius','chirality_criticality',
            'topology_universe','winding_chirality','kinetics_criticality',
            'triple_criticality','g1_Ç_max','g1_⊙_max','g1_Ω_max',
            'parallel_Ç','parallel_⊙','parallel_Ω','single_gate_⊙',
            'single_gate_Ω','single_gate_Ç','t_hybrid']]
        if key_blocks:
            lines.append(f"**Key blockers:** {', '.join('`'+n+'`' for n in sorted(key_blocks))}")
            lines.append("")

lines.append("## 3. Universe Grid — Notable Universes")
lines.append("")
lines.append("| Universe | Verticullum | Chimerium | Apertix | Retiarius | Praxeum |")
lines.append("|----------|------------|-----------|---------|-----------|---------|")

NOTABLE = [
    'canonical','low_gate','strict_frobenius','high_gate','winding_first',
    'chirality_first','topology_universe','scope_universe','dimensional_gate',
    'kinetics_trap','triple_criticality','broadcast_universe','fidelity_universe',
    'stoichiometry_universe','absorption_democracy','absorption_monarchy',
    'absorption_inverted','predator_universe','prey_universe',
    'chirality_criticality','winding_chirality','scope_grammar',
    'single_gate','t_hybrid','t_inverted','t_all_dynamics','t_all_structure',
]

rs_by_name = {r.name: r for r in all_rs}
EMOJI = {"idempotent_terminal":"O∞","traced_monoidal":"trc","frobenius":"frb","plain":"✗"}

for un in NOTABLE:
    r = rs_by_name.get(un)
    if r is None: continue
    row = f"| `{un}` |"
    for cn, cv in COMPOUNDS.items():
        L = layer_for(cv, r)
        row += f" {EMOJI[L]} |"
    lines.append(row)

lines.append("")
lines.append("## 4. Key Findings")
lines.append("")
lines.append("1. **Chimerium (91.7%)** — broadest access. Φ=𐑣 (supercritical, ord 3.0) passes nearly all gates. Only blocked by Ç≥5.0 and Ω≥4.0. Passes triple_criticality where all ⊙-gated compounds fail.")
lines.append("2. **Verticullum (81.7%)** — Φ=𐑹 (ord 5.0) + Ω=𐑟 (ord 4.0) combine for near-universal passage. Blocked by ⊙≥3.0 (its φ̂=⊙ is ord 2.0), Ç≥5.0, and Þ≥5.0.")
lines.append("3. **Praxeum (78.0%)** — despite O₀ tier, accesses 78% of universes. Φ=𐑻 (ord 2.67) barely fails ⊙≥3.0 gates. Control platform breadth is essential for Gate 1 toggle operations.")
lines.append("4. **Apertix (14.7%)** — precision-targeted. Φ=𐑬 (ord 3) and Ω=𐑴 (ord 2) fail most canonical+ gates. Accesses only half-ordinal and min-ordinal universes. This is *by design* — Apertix steers within a narrow, well-mapped region.")
lines.append("5. **Retiarius (11.9%)** — most restricted. Low ordinals across Φ=𐑿 (2), ƒ=𐑞 (2), Ω=𐑷 (1), Ħ=𐑒 (2), Γ=𐑚 (1). Only accesses min-ordinal universes. Precision without cascading.")
lines.append("6. **Ç=𐑺 (MBL, ord 4.5) is the universal blocker** — no compound has it. Universes gating on Ç≥5.0 (g1_Ç_max, single_gate_Ç, kinetics_criticality, parallel_Ç) block ALL five compounds.")
lines.append("7. **Absorption-based universes** (democracy, monarchy, inverted, predator, prey) don't change gate-layer outcomes for these compounds — they have canonical gates. Their novelty is in coupling behavior, not access control.")
lines.append("8. **Triple criticality** is the most discriminating interesting universe: only Chimerium (Φ=𐑣) passes all three ⊙ rungs. All ⊙-gated compounds (Verticullum, Apertix) stall at G3:⊙≥3.0.")
lines.append("")
lines.append("## 5. Operational Implications")
lines.append("")
lines.append("| Protocol | Compounds | Universe Strategy |")
lines.append("|----------|-----------|-------------------|")
lines.append("| **The Dive** | DMT + Praxeum | Canonical (85.3% of all universes accessible) |")
lines.append("| **The Precision Map** | Retiarius → Apertix | Narrow-universe targeting (11.9% → 14.7% but precise) |")
lines.append("| **The Breakthrough** | Ketamine + Chimerium | Chimerium opens 91.7% of universes including triple_criticality |")
lines.append("| **The Hold** | Any ⊙ compound + Ħ ladder | Ħ=𐑫 is the invariance fixed point across all universes |")
lines.append("| **The Release** | Ħ↓ to 𐑓 + Ω↓ to 𐑷 | Minimum persistence — most universes become plain |")
lines.append("")
lines.append("## 6. Universe Discovery Command Reference")
lines.append("")
lines.append("```bash")
lines.append("# Profile all 109 universes against catalog")
lines.append("python new_universes.py compare")
lines.append("")
lines.append("# Systematic iteration (80 universes)")
lines.append("python iterate_universes.py")
lines.append("")
lines.append("# Count the combinatorial space")
lines.append("python new_universes.py count --all")
lines.append("")
lines.append("# Generate from permutations")
lines.append("python new_universes.py permute --gates all --max 50")
lines.append("```")

with open('/home/mrnob0dy666/p4rakernel/universe_compound_mapping.md', 'w') as f:
    f.write('\n'.join(lines))

print(f"Written: {len(lines)} lines")
