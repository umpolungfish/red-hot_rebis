#!/usr/bin/env python3
"""
decay_chain.py — Nuclear decay as IMASM winding toward a Frobenius fixed point.

Each radioactive nuclide has ⊙≠⊙ (non-self-referential criticality). Each decay
event fires δ without a compensating μ, agitating the subatomic Belnap state. The
chain winds through IMASM type space until it reaches a daughter with ⊙=⊙ — at
which point μ∘δ=id holds and the winding terminates. The half-life is the dwell
time per winding step; stability is Frobenius-exactness, not energy exhaustion.
"""

import sys
from pathlib import Path

# Make shared/ importable
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT / "shared"))
sys.path.insert(0, str(_ROOT))

from elem2imasm import derive_tuple, SH, CRIT, ELEMENTS

# Shavian ordinal lookup
SH_ORD = {c: i for i, c in enumerate(SH)}
SH_ORD[CRIT] = 48  # ⊙ treated as ordinal 48 for distance

# ─── Known decay series ────────────────────────────────────────────────────────
# Each entry: (element_symbol, isotope_label, half_life, decay_mode)
# 'stable' half-life marks the terminal nuclide.

DECAY_SERIES = {
    'U238': {
        'name': 'Uranium-238 series (4n+2)',
        'chain': [
            ('U',  'U-238',  '4.468 Gy',  'α'),
            ('Th', 'Th-234', '24.10 d',   'β'),
            ('Pa', 'Pa-234', '1.17 m',    'β'),
            ('U',  'U-234',  '245.5 ky',  'α'),
            ('Th', 'Th-230', '75.4 ky',   'α'),
            ('Ra', 'Ra-226', '1600 y',    'α'),
            ('Rn', 'Rn-222', '3.82 d',    'α'),
            ('Po', 'Po-218', '3.05 m',    'α'),
            ('Pb', 'Pb-214', '26.8 m',    'β'),
            ('Bi', 'Bi-214', '19.7 m',    'β'),
            ('Po', 'Po-214', '164 μs',    'α'),
            ('Pb', 'Pb-210', '22.3 y',    'β'),
            ('Bi', 'Bi-210', '5.01 d',    'β'),
            ('Po', 'Po-210', '138.4 d',   'α'),
            ('Pb', 'Pb-206', 'stable',    '—'),
        ]
    },
    'U235': {
        'name': 'Uranium-235 series (4n+3)',
        'chain': [
            ('U',  'U-235',  '703.8 My',  'α'),
            ('Th', 'Th-231', '25.52 h',   'β'),
            ('Pa', 'Pa-231', '32.76 ky',  'α'),
            ('Ac', 'Ac-227', '21.77 y',   'β'),
            ('Th', 'Th-227', '18.68 d',   'α'),
            ('Ra', 'Ra-223', '11.43 d',   'α'),
            ('Rn', 'Rn-219', '3.96 s',    'α'),
            ('Po', 'Po-215', '1.78 ms',   'α'),
            ('Pb', 'Pb-211', '36.1 m',    'β'),
            ('Bi', 'Bi-211', '2.14 m',    'α'),
            ('Tl', 'Tl-207', '4.77 m',    'β'),
            ('Pb', 'Pb-207', 'stable',    '—'),
        ]
    },
    'Th232': {
        'name': 'Thorium-232 series (4n)',
        'chain': [
            ('Th', 'Th-232', '14.05 Gy',  'α'),
            ('Ra', 'Ra-228', '5.75 y',    'β'),
            ('Ac', 'Ac-228', '6.15 h',    'β'),
            ('Th', 'Th-228', '1.912 y',   'α'),
            ('Ra', 'Ra-224', '3.66 d',    'α'),
            ('Rn', 'Rn-220', '55.6 s',    'α'),
            ('Po', 'Po-216', '0.145 s',   'α'),
            ('Pb', 'Pb-212', '10.64 h',   'β'),
            ('Bi', 'Bi-212', '60.55 m',   'β/α'),
            ('Po', 'Po-212', '0.299 μs',  'α'),
            ('Pb', 'Pb-208', 'stable',    '—'),
        ]
    },
    'Ra226': {
        'name': 'Radium-226 sub-chain (U238 branch from Ra)',
        'chain': [
            ('Ra', 'Ra-226', '1600 y',    'α'),
            ('Rn', 'Rn-222', '3.82 d',    'α'),
            ('Po', 'Po-218', '3.05 m',    'α'),
            ('Pb', 'Pb-214', '26.8 m',    'β'),
            ('Bi', 'Bi-214', '19.7 m',    'β'),
            ('Po', 'Po-214', '164 μs',    'α'),
            ('Pb', 'Pb-210', '22.3 y',    'β'),
            ('Pb', 'Pb-206', 'stable',    '—'),
        ]
    },
    'Rn222': {
        'name': 'Radon-222 chain (environmental)',
        'chain': [
            ('Rn', 'Rn-222', '3.82 d',    'α'),
            ('Po', 'Po-218', '3.05 m',    'α'),
            ('Pb', 'Pb-214', '26.8 m',    'β'),
            ('Bi', 'Bi-214', '19.7 m',    'β'),
            ('Po', 'Po-214', '164 μs',    'α'),
            ('Pb', 'Pb-210', '22.3 y',    'β'),
            ('Bi', 'Bi-210', '5.01 d',    'β'),
            ('Po', 'Po-210', '138.4 d',   'α'),
            ('Pb', 'Pb-206', 'stable',    '—'),
        ]
    },
}

PRIMS = ['Ř', 'Ħ', 'Ω', 'Ð', 'Σ', 'Φ', 'Ç', 'ƒ', 'ɢ', 'Γ', 'Þ', '⊙']

# ─── Core logic ────────────────────────────────────────────────────────────────

def frobenius_fires(tup):
    """True when ⊙ slot is the self-referential criticality value."""
    return tup['⊙'] == CRIT

def tuple_distance(tA, tB):
    """L1 distance between two IMASM tuples over ordinal indices."""
    return sum(abs(SH_ORD.get(tA[p], 48) - SH_ORD.get(tB[p], 48)) for p in PRIMS)

def imasm_word(tup):
    return ''.join(tup[p] for p in PRIMS)

def analyze_chain(series_key):
    """Return list of step dicts for a decay series."""
    series = DECAY_SERIES[series_key]
    steps = []
    prev_tup = None
    for sym, isotope, half_life, mode in series['chain']:
        if sym not in ELEMENTS:
            # Unknown element — use placeholder
            tup = {p: '?' for p in PRIMS}
            tup['⊙'] = '?'
        else:
            tup = derive_tuple(sym)
        fires = frobenius_fires(tup)
        dist = tuple_distance(prev_tup, tup) if prev_tup is not None else None
        steps.append({
            'sym':       sym,
            'isotope':   isotope,
            'half_life': half_life,
            'mode':      mode,
            'tuple':     tup,
            'word':      imasm_word(tup),
            'frobenius': fires,
            'dist':      dist,
            'stable':    half_life == 'stable',
        })
        prev_tup = tup
    return series['name'], steps

def print_chain(series_key):
    name, steps = analyze_chain(series_key)
    print(f"\n{'═'*70}")
    print(f"  {name}")
    print(f"{'═'*70}")
    print(f"  {'Step':<4} {'Isotope':<10} {'T½':<12} {'Mode':<6} {'Frob':<6} {'Δ':>4}  IMASM word")
    print(f"  {'─'*4} {'─'*10} {'─'*12} {'─'*6} {'─'*6} {'─':>4}  {'─'*12}")

    winding = 0
    for i, s in enumerate(steps):
        frob_sym = '✓ FIRES' if s['frobenius'] else '·'
        dist_str = f'{s["dist"]:>4}' if s["dist"] is not None else '   —'
        stable_tag = '  ← FIXED POINT' if s['stable'] else ''
        if not s['stable']:
            winding += 1
        print(f"  {i:<4} {s['isotope']:<10} {s['half_life']:<12} {s['mode']:<6} {frob_sym:<6} {dist_str}  {s['word']}{stable_tag}")

    print()
    print(f"  Windings to closure: {winding}")
    # Find first Frobenius-exact step
    for i, s in enumerate(steps):
        if s['frobenius']:
            print(f"  Frobenius first fires at step {i}: {s['isotope']} ({s['half_life']})")
            break

def print_all_series():
    for key in DECAY_SERIES:
        print_chain(key)

def compare_series():
    """Side-by-side winding counts and first-Frobenius step for all series."""
    print(f"\n{'═'*60}")
    print("  Decay series comparison")
    print(f"{'═'*60}")
    print(f"  {'Series':<10} {'Windings':>9}  {'Frob fires at':>20}  First stable daughter")
    print(f"  {'─'*10} {'─'*9}  {'─'*20}  {'─'*20}")
    for key, data in DECAY_SERIES.items():
        _, steps = analyze_chain(key)
        windings = sum(1 for s in steps if not s['stable'])
        first_frob = next((s for s in steps if s['frobenius']), None)
        stable = next((s for s in steps if s['stable']), None)
        frob_label = f"{first_frob['isotope']} (step {steps.index(first_frob)})" if first_frob else 'never'
        stable_label = stable['isotope'] if stable else '?'
        print(f"  {key:<10} {windings:>9}  {frob_label:>20}  {stable_label}")

# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser(
        description='Nuclear decay as IMASM winding toward Frobenius fixed point.'
    )
    p.add_argument('series', nargs='?', default=None,
                   help=f'Decay series key: {", ".join(DECAY_SERIES)} (omit for summary)')
    p.add_argument('--all',     action='store_true', help='Print all decay series')
    p.add_argument('--compare', action='store_true', help='Comparison table across all series')
    p.add_argument('--list',    action='store_true', help='List available series keys')
    args = p.parse_args()

    if args.list:
        print("Available decay series:")
        for k, v in DECAY_SERIES.items():
            print(f"  {k:<10}  {v['name']}")
        return

    if args.compare or (not args.series and not args.all):
        compare_series()
        return

    if args.all:
        print_all_series()
        return

    key = args.series.upper()
    if key not in DECAY_SERIES:
        print(f"Unknown series '{args.series}'. Known: {', '.join(DECAY_SERIES)}")
        sys.exit(1)
    print_chain(key)


if __name__ == '__main__':
    main()
