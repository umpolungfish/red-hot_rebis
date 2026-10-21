#!/usr/bin/env python3
"""
nuclide_imscriber.py — Nuclide-level (A,Z,N) imscription for the Imscribing Grammar.

Extends elem2imasm.py with isotope-specific tuples incorporating:
- Neutron number N and N/Z ratio
- Nuclear shell closures (magic numbers)
- Deformation and shape coexistence
- Island of stability predictions (Z=114, N=184; Z=120,126; Z=126,N=184)

Plus excited electron state imscription (singlet vs triplet).
"""

import sys, json, math
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT / "shared"))
from elem2imasm import ELEMENTS, SH, CRIT, derive_tuple
ELEM_PRIMS = ["≻","⊥","⊡","⊢","⊞","≺","⊤","⋈","∋","∈","⊣","⊙"]

PRIMS = ["⊢","⊣","≻","≺","⋈","⊤","∈","∋","⊙","⊥","⊞","⊡"]
# Magic numbers
MAGIC_Z = {2,8,20,28,50,82,114,120,126}  # 114,120,126 predicted
MAGIC_N = {2,8,20,28,50,82,126,184}       # 184 predicted

# IG primitive glyphs (not Shavian indices — actual IG values)
dimensionality_values = {'wedge': '𐑛', 'triangle': '𐑨', 'infty': '𐑼', 'odot': '𐑦'}
topology_values = {'network': '𐑡', 'inclusion': '𐑰', 'bowtie': '𐑥', 'boxtimes': '𐑶', 'odot': '𐑸'}
coupling_values = {'super': '𐑩', 'cat': '𐑑', 'dagger': '𐑽', 'lr': '𐑾'}
parity_values = {'asym': '𐑗', 'psi': '𐑿', 'pm': '𐑬', 'sym': '𐑯', 'pm_sym': '𐑹'}
fidelity_values = {'ell': '𐑱', 'eth': '𐑞', 'hbar': '𐑐'}
kinetics_values = {'fast': '𐑺', 'mod': '𐑪', 'slow': '𐑧', 'trap_ord': '𐑤', 'trap_dis': '𐑘'}
cardinality_values = {'beth': '𐑲', 'gimel': '𐑔', 'aleph': '𐑚'}
composition_values = {'and': '𐑝', 'or': '𐑜', 'seq': '𐑠', 'broad': '𐑵'}
criticality_values = {'sub': '𐑢', 'c': '⊙', 'c_complex': '𐑮', 'EP': '𐑻', 'super': '𐑣'}
chirality_values = {'h0': '𐑓', 'h1': '𐑒', 'h2': '𐑖', 'hinf': '𐑫'}
stoichiometry_values = {'1:1': '𐑙', 'n:n': '𐑕', 'n:m': '𐑳'}
winding_values = {'Z0': '𐑷', 'Z2': '𐑴', 'Z': '𐑭', 'NA': '𐑟'}


def nuclide_tuple(Z, N):
    """Return 12-primitive IG tuple for a specific nuclide (Z protons, N neutrons)."""
    A = Z + N
    nz_ratio = N / Z if Z > 0 else float('inf')
    is_doubly_magic = (Z in MAGIC_Z) and (N in MAGIC_N)
    is_magic_Z = Z in MAGIC_Z
    is_magic_N = N in MAGIC_N

    # [1] D — Dimensionality: shell closure freezes degrees of freedom
    if is_doubly_magic:
        dimensionality = dimensionality_values['triangle']  # 𐑨 — few effective d.o.f. (shell gap)
    elif is_magic_Z or is_magic_N:
        dimensionality = dimensionality_values['triangle']  # 𐑨 — partially frozen
    elif A >= 100:
        dimensionality = dimensionality_values['infty']     # 𐑼 — many collective d.o.f.
    else:
        dimensionality = dimensionality_values['triangle']  # 𐑨 — light nuclei

    # [2] T — Topology
    if is_doubly_magic:
        topology = topology_values['bowtie']    # 𐑥 — shell gap creates crossing point
    elif is_magic_Z or is_magic_N:
        topology = topology_values['network']   # 𐑡 — one closed shell, one open
    elif A >= 100:
        topology = topology_values['boxtimes']  # 𐑶 — product of proton×neutron configurations
    else:
        topology = topology_values['network']   # 𐑡

    # [3] R — Coupling between proton and neutron fluids
    if nz_ratio > 1.55:
        coupling = coupling_values['dagger']    # 𐑽 — neutron-dominant (neutron→proton potential)
    elif nz_ratio < 1.0:
        coupling = coupling_values['super']     # 𐑩 — proton-dominant
    elif 1.45 <= nz_ratio <= 1.55:
        coupling = coupling_values['lr']        # 𐑾 — balanced N/Z, bidirectional
    else:
        coupling = coupling_values['cat']       # 𐑑 — categorical functorial

    # [4] P — Symmetry/Parity
    if is_doubly_magic:
        parity = parity_values['sym']       # 𐑯 — spherical, J=0⁺
    elif is_magic_Z or is_magic_N:
        parity = parity_values['pm']        # 𐑬 — partial (one closed shell)
    elif A >= 100:
        parity = parity_values['psi']       # 𐑿 — collective superpositions
    else:
        parity = parity_values['pm']        # 𐑬

    # [5] F — Physical regime: always quantum for nuclei
    fidelity = fidelity_values['hbar']          # 𐑐

    # [6] K — Kinetics (decay rate)
    if is_doubly_magic:
        kinetics = kinetics_values['trap_ord']  # 𐑤 — shell gap traps kinetics
    elif is_magic_Z or is_magic_N:
        kinetics = kinetics_values['slow']      # 𐑧 — slowed by one shell closure
    elif Z >= 84:  # Polonium and above
        kinetics = kinetics_values['fast']      # 𐑺 — radioactive, short-lived
    elif Z >= 83:
        kinetics = kinetics_values['mod']       # 𐑪 — Bi is borderline
    else:
        kinetics = kinetics_values['slow']      # 𐑧

    # [7] G — Interaction range (nuclear force)
    if is_doubly_magic:
        cardinality = cardinality_values['gimel']     # 𐑔 — mesoscale (valence only)
    elif A >= 100:
        cardinality = cardinality_values['aleph']     # 𐑚 — maximal (all nucleons via strong force)
    else:
        cardinality = cardinality_values['gimel']     # 𐑔 — mesoscale for lighter nuclei

    # [8] ∋ — Composition
    if is_doubly_magic:
        composition = composition_values['and']     # 𐑝 — conjunctive (all shells closed simultaneously)
    elif A >= 240:
        composition = composition_values['seq']     # 𐑠 — sequential (α/β decay chain)
    elif A >= 100:
        composition = composition_values['or']      # 𐑜 — disjunctive (multiple decay paths)
    else:
        composition = composition_values['and']     # 𐑝

    # [9] ⊙ — Criticality
    if is_doubly_magic:
        criticality = criticality_values['c']       # ⊙ — self-referential (Frobenius fires)
    elif is_magic_Z or is_magic_N:
        criticality = criticality_values['c_complex']  # 𐑮 — complex-plane critical
    elif Z >= 104:  # transactinides
        criticality = criticality_values['sub']     # 𐑢 — indeterminate (ultra-short)
    elif Z >= 84:   # Po through Lr
        criticality = criticality_values['super']   # 𐑣 — supercritical (radioactive)
    elif Z in {43, 61}:  # Tc, Pm
        criticality = criticality_values['super']   # 𐑣
    else:
        criticality = criticality_values['c']       # ⊙ — stable, self-referential

    # [10] H — Chirality (Markov order)
    if is_doubly_magic:
        chirality = chirality_values['hinf']      # 𐑫 — eternal memory (stable)
    elif kinetics == kinetics_values['slow']:
        chirality = chirality_values['h2']        # 𐑖 — two-step memory
    elif kinetics == kinetics_values['mod']:
        chirality = chirality_values['h1']        # 𐑒 — one-step memory
    else:
        chirality = chirality_values['h0']        # 𐑓 — memoryless (fast decay)

    # [11] ⊞ — Stoichiometry
    if nz_ratio < 0.1:
        stoichiometry = stoichiometry_values['1:1']       # 𐑙 — pure neutron (hypothetical)
    elif is_doubly_magic:
        stoichiometry = stoichiometry_values['1:1']       # 𐑙 — both shells closed, unique identity
    elif abs(nz_ratio - 1.0) < 0.05:
        stoichiometry = stoichiometry_values['1:1']       # 𐑙 — symmetric N≈Z
    elif abs(nz_ratio - 1.5) < 0.1:
        stoichiometry = stoichiometry_values['n:n']       # 𐑕 — many identical (valley of stability)
    else:
        stoichiometry = stoichiometry_values['n:m']       # 𐑳 — heterogeneous

    # [12] ⊡ — Topological invariant
    if is_doubly_magic:
        winding = winding_values['Z']         # 𐑭 — integer winding (magic numbers)
    elif is_magic_Z or is_magic_N:
        winding = winding_values['Z2']        # 𐑴 — binary (one shell closure)
    elif A >= 100:
        winding = winding_values['Z2']        # 𐑴 — collective
    else:
        winding = winding_values['Z0']        # 𐑷 — trivial

    return {"⊢":dimensionality,"⊣":topology,"≻":coupling,"≺":parity,"⋈":fidelity,"⊤":kinetics,"∈":cardinality,"∋":composition,"⊙":criticality,"⊥":chirality,"⊞":stoichiometry,"⊡":winding}


def tuple_to_word(tup):
    return ''.join(tup[p] for p in PRIMS)


def compute_l1_distance(tA, tB):
    """L1 distance between two IG tuples using ordinal positions."""
    # Build ordinal map from IG value glyphs
    all_vals = set()
    for vdict in [dimensionality_values,topology_values,coupling_values,parity_values,fidelity_values,kinetics_values,cardinality_values,composition_values,criticality_values,chirality_values,stoichiometry_values,winding_values]:
        all_vals.update(vdict.values())
    val_list = sorted(all_vals, key=ord)
    val_ord = {v: i for i, v in enumerate(val_list)}
    return sum(abs(val_ord.get(tA[p], 0) - val_ord.get(tB[p], 0)) for p in PRIMS)

# ─── Island of Stability Predictions ────────────────────────────────────────

def island_candidates():
    """Generate predicted island of stability nuclide tuples."""
    candidates = []
    # Predicted doubly-magic: (Z, N, label)
    for Z, N, label in [
        (114, 184, 'Fl-298'),
        (120, 184, 'Ubn-304'),  # Unbinilium
        (126, 184, 'Ubh-310'),  # Unbihexium
        (114, 178, 'Fl-292'),   # Fl with N=178 (next-closest to magic)
        (112, 184, 'Cn-296'),   # Copernicium with N=184
        (108, 162, 'Hs-270'),   # Hassium (Z=108, N=162 predicted deformed shell)
        (114, 172, 'Fl-286'),   # Fl with N=172
    ]:
        tup = nuclide_tuple(Z, N)
        word = tuple_to_word(tup)
        candidates.append({
            'label': label,
            'Z': Z, 'N': N, 'A': Z+N,
            'nz_ratio': N/Z,
            'tuple': tup,
            'word': word,
            'doubly_magic': (Z in MAGIC_Z) and (N in MAGIC_N),
            'magic_Z': Z in MAGIC_Z,
            'magic_N': N in MAGIC_N,
        })
    return candidates


def compare_to_pb():
    """Compare island candidates to Pb-208 (doubly-magic Z=82, N=126)."""
    pb208 = nuclide_tuple(82, 126)
    pb_word = tuple_to_word(pb208)

    print("="*80)
    print("  ISLAND OF STABILITY — Structural Comparison to Pb-208")
    print("  Pb-208 (Z=82, N=126): " + pb_word)
    print("="*80)

    # Also compute element-level Pb tuple for reference
    pb_elem = derive_tuple('Pb')
    PRIMS_ELEM = ['≻','⊥','⊡','⊢','⊞','≺','⊤','⋈','∋','∈','⊣','⊙']
    pb_elem_word = ''.join(pb_elem[p] for p in PRIMS_ELEM)
    print(f"  Pb (element-level, elem2imasm): {pb_elem_word}")
    print()

    header = f"  {'Nuclide':<12} {'Z':>3} {'N':>3} {'N/Z':>6} {'DM':>4} {'d(Pb-208)':>10}  Word"
    print(header)
    print("  " + "-"*len(header))

    for c in island_candidates():
        dist = compute_l1_distance(c['tuple'], pb208)
        dm = 'YES' if c['doubly_magic'] else 'no'
        print(f"  {c['label']:<12} {c['Z']:>3} {c['N']:>3} {c['nz_ratio']:>6.2f} {dm:>4} {dist:>10}  {c['word']}")

    print()
    print("  Primitive key: ⊢ ⊣ ≻ ≺ ⋈ ⊤ ∈ ∋ ⊙ ⊥ ⊞ ⊡")
    print("  DM = Doubly-Magic")
    print()

    # Also show Pb-208 distance to other key nuclides
    print("-"*80)
    print("  Pb-208 distance to key nuclides (nuclide-level):")
    print()
    key_nuclides = [
        (92, 146, 'U-238'), (92, 143, 'U-235'), (90, 142, 'Th-232'),
        (88, 138, 'Ra-226'), (86, 136, 'Rn-222'), (84, 126, 'Po-210'),
        (83, 126, 'Bi-209'), (114, 175, 'Fl-289'), (118, 176, 'Og-294'),
        (104, 163, 'Rf-267'),
    ]
    for Z, N, label in key_nuclides:
        tup = nuclide_tuple(Z, N)
        dist = compute_l1_distance(tup, pb208)
        is_dm = (Z in MAGIC_Z) and (N in MAGIC_N)
        dm_tag = ' [DM]' if is_dm else ''
        print(f"  {label:<12} Z={Z:>3} N={N:>3}  d(Pb-208)={dist:>4}  {tuple_to_word(tup)}{dm_tag}")

# ─── Excited Electron States — Singlet vs Triplet ──────────────────────────

def excited_state_tuple(state_type, orbital_label=None):
    """
    Return 12-primitive IG tuple for an excited electron state.

    state_type: 'singlet' | 'triplet' | 'ground_singlet' | 'ground_triplet'
    orbital_label: e.g. 'S1', 'T1', 'S0', 'T0'

    Key structural differences between singlet and triplet:
    - Singlet: total spin ⊞=0, antisymmetric spin fn, symmetric spatial fn
    - Triplet: total spin ⊞=1, symmetric spin fn, antisymmetric spatial fn

    The Pauli principle forces spatial part to be antisymmetric for triplet,
    which keeps electrons apart → lower Coulomb repulsion → lower energy (Hund).
    """
    is_excited = orbital_label and orbital_label[0] in ('S', 'T') and orbital_label[1:] not in ('0',)
    is_ground = orbital_label and (orbital_label == 'S0' or orbital_label == 'T0')

    # [1] D — Dimensionality
    # Excited state accesses more orbital space → higher dimensionality
    # Triplet always has 3 spin substates; singlet has 1
    if 'triplet' in state_type:
        dimensionality = dimensionality_values['infty']     # 𐑼 — 3 degenerate substates (m=-1,0,1)
    else:
        dimensionality = dimensionality_values['triangle']  # 𐑨 — single state (m=0)

    # [2] T — Topology
    # Triplet: spin and spatial degrees of freedom cross (exchange interaction)
    # Singlet: spin paired, topology collapses
    if 'triplet' in state_type:
        topology = topology_values['bowtie']    # 𐑥 — crossing point: spin ⇌ spatial via exchange
    else:
        topology = topology_values['network']   # 𐑡 — no crossing, spin is paired off

    # [3] R — Coupling between spin and spatial parts
    if 'triplet' in state_type:
        coupling = coupling_values['lr']        # 𐑾 — bidirectional: spin determines spatial (Pauli), spatial modifies spin (exchange)
    else:
        coupling = coupling_values['super']     # 𐑩 — spin supervenes on spatial (spin is paired, doesn't drive)

    # [4] P — Parity/Symmetry
    if 'triplet' in state_type:
        parity = parity_values['psi']       # 𐑿 — 3 degenerate spin substates (quantum superposition)
    else:
        parity = parity_values['sym']       # 𐑯 — full: ⊞=0 is a unique singlet state

    # [5] F — Physical regime
    # Excited states: fluorescence/phosphorescence involve quantum coherence
    # Ground triplet (e.g. O₂): quantum coherence (unpaired spins, magnetic)
    if is_ground:
        fidelity = fidelity_values['hbar']      # 𐑐 — ground states are quantum-coherent
    elif 'triplet' in state_type:
        fidelity = fidelity_values['eth']       # 𐑞 — thermal/noisy: triplet has longer lifetime, interacts with environment
    else:
        fidelity = fidelity_values['hbar']      # 𐑐 — quantum coherence (fluorescence is fast, coherent)

    # [6] K — Kinetics (excited state lifetime)
    if is_ground:
        kinetics = kinetics_values['trap_ord']  # 𐑤 — ground state, permanently trapped
    elif state_type == 'triplet':
        kinetics = kinetics_values['slow']      # 𐑧 — phosphorescence: spin-forbidden, slow (μs to s)
    elif is_excited:
        kinetics = kinetics_values['fast']      # 𐑺 — fluorescence: spin-allowed, fast (ns)
    else:
        kinetics = kinetics_values['slow']      # 𐑧

    # [7] G — Interaction range
    if state_type == 'triplet':
        cardinality = cardinality_values['gimel']     # 𐑔 — mesoscale: exchange interaction is short-range
    else:
        cardinality = cardinality_values['beth']      # 𐑲 — local: paired electrons are local

    # [8] ∋ — Composition
    if 'triplet' in state_type:
        composition = composition_values['or']      # 𐑜 — disjunctive: 3 degenerate substates (choose one upon measurement)
    else:
        composition = composition_values['and']     # 𐑝 — conjunctive: single state

    # [9] ⊙ — Criticality
    if is_ground:
        criticality = criticality_values['c']       # ⊙ — self-referential (ground state is the reference)
    elif state_type == 'triplet':
        criticality = criticality_values['EP']      # 𐑻 — exceptional point: singlet→triplet crossing (ISC)
    else:
        criticality = criticality_values['super']   # 𐑣 — supercritical: decays radiatively

    # [10] H — Chirality (memory of excitation pathway)
    if is_ground:
        chirality = chirality_values['hinf']      # 𐑫 — ground state, eternal memory
    elif 'triplet' in state_type:
        chirality = chirality_values['hinf']      # 𐑫 — long memory: phosphorescence remembers excitation
    elif is_excited:
        chirality = chirality_values['h1']        # 𐑒 — one-step: fluorescence
    else:
        chirality = chirality_values['hinf']      # 𐑫

    # [11] ⊞ — Stoichiometry
    if 'triplet' in state_type:
        stoichiometry = stoichiometry_values['n:m']       # 𐑳 — 3 spin substates + spatial = heterogeneous
    else:
        stoichiometry = stoichiometry_values['1:1']       # 𐑙 — one spin configuration, one spatial

    # [12] ⊡ — Topological invariant
    if 'triplet' in state_type:
        winding = winding_values['Z2']        # 𐑴 — spin parity protection (triplet has odd parity under exchange)
    else:
        winding = winding_values['Z0']        # 𐑷 — no topological protection (singlet is exchange-even)

    return {"⊢":dimensionality,"⊣":topology,"≻":coupling,"≺":parity,"⋈":fidelity,"⊤":kinetics,"∈":cardinality,"∋":composition,"⊙":criticality,"⊥":chirality,"⊞":stoichiometry,"⊡":winding}


def compare_excited_states():
    """Compare singlet vs triplet excited state structural types."""
    S0 = excited_state_tuple('ground_singlet', 'S0')
    S1 = excited_state_tuple('singlet', 'S1')
    T1 = excited_state_tuple('triplet', 'T1')
    T0 = excited_state_tuple('ground_triplet', 'T0')

    print("="*80)
    print("  EXCITED ELECTRON STATES — Singlet vs Triplet")
    print("="*80)
    print()

    for label, tup in [('S0 (ground singlet)', S0), ('S1 (excited singlet)', S1),
                        ('T0 (ground triplet)', T0), ('T1 (excited triplet)', T1)]:
        word = tuple_to_word(tup)
        print(f"  {label:<24s}  {word}")
        print(f"    ⊢={tup['⊢']} ⊣={tup['⊣']} ≻={tup['≻']} ≺={tup['≺']} ⋈={tup['⋈']} ⊤={tup['⊤']}")
        print(f"    ∈={tup['∈']} ∋={tup['∋']} ⊙={tup['⊙']} ⊥={tup['⊥']} ⊞={tup['⊞']} ⊡={tup['⊡']}")
        print()

    print("-"*80)
    print("  Key structural differences (S1 → T1):")
    print()

    diffs = []
    for p in PRIMS:
        if S1[p] != T1[p]:
            diffs.append(f"  {p}: {S1[p]} → {T1[p]}")
    for d in diffs:
        print(d)

    print()
    print("  Distance S1→T1:", compute_l1_distance(S1, T1))
    print("  Distance S0→S1:", compute_l1_distance(S0, S1))
    print("  Distance T0→T1:", compute_l1_distance(T0, T1))
    print()

    # Intersystem crossing: S1 → T1
    print("-"*80)
    print("  INTERSYSTEM CROSSING (S1 → T1):")
    print("  Spin-orbit coupling mediates the singlet-triplet crossing.")
    print("  The S1→T1 structural delta identifies which primitives must")
    print("  shift for ISC to occur: D, T, R, P, F, K, G, Gm, Ph, H, S, W")
    print("  The ⊙ shift (super→EP) marks the crossing point itself.")

# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    p = argparse.ArgumentParser(
        description='Nuclide-level imscription: Island of Stability + Excited States'
    )
    p.add_argument('--island', action='store_true', help='Island of stability analysis')
    p.add_argument('--excited', action='store_true', help='Excited electron state analysis')
    p.add_argument('--nuclide', type=str, default=None,
                   help='Compute tuple for Z,N (e.g. "114,184")')
    p.add_argument('--all', action='store_true', help='Run all analyses')
    args = p.parse_args()

    if args.nuclide:
        parts = args.nuclide.split(',')
        Z, N = int(parts[0]), int(parts[1])
        tup = nuclide_tuple(Z, N)
        word = tuple_to_word(tup)
        A = Z + N
        dm = (Z in MAGIC_Z) and (N in MAGIC_N)
        print(f"Nuclide Z={Z} N={N} A={A} N/Z={N/Z:.3f}  Doubly-Magic: {dm}")
        print(f"Tuple: {word}")
        print(f"Per-primitive: ⊢={tup['⊢']} ⊣={tup['⊣']} ≻={tup['≻']} ≺={tup['≺']} ⋈={tup['⋈']} ⊤={tup['⊤']} ∈={tup['∈']} ∋={tup['∋']} ⊙={tup['⊙']} ⊥={tup['⊥']} ⊞={tup['⊞']} ⊡={tup['⊡']}")
        # Distance to Pb-208
        pb208 = nuclide_tuple(82, 126)
        dist = compute_l1_distance(tup, pb208)
        print(f"Distance to Pb-208: {dist}")
        return

    if args.island or args.all:
        compare_to_pb()
    if args.excited or args.all:
        print()
        compare_excited_states()


if __name__ == '__main__':
    main()
