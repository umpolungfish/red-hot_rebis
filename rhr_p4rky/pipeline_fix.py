#!/usr/bin/env python3
"""
pipeline_fix.py — Diagnosis + fix for ch3mpiler ⟲ serpentrod pipeline.

ROOT CAUSE ANALYSIS:
────────────────────
The pipeline's `bond_type_to_site_rna` encodes the reaction's bond type tuple 
into a deterministic 36-nt RNA via hash-indexed codon lookup. This produces 
AAs whose IG primitives cover only 3/6 complementary pairs:

  MESKFCSATSRK → {Dimensionality, Winding, Stoichiometry, Fidelity, Recognition}
  Pairs covered: {D↔W}, {R↔S}, {P↔F}  → 3/6  FAILS Frobenius (needs ≥4)

Additionally, the RNA is IDENTICAL for any target sharing the same bond type 
(cubane and maytansine both get sigma_single → same MESKFCSATSRK) because 
FG pair information is completely ignored.

FIX STRATEGY:
─────────────
1. FUSE bond type + FG1 type + FG2 type into a single reaction signature
2. Compute complement from the FUSED type (FG-aware → site is target-specific)
3. Select AAs DIRECTLY by their primitive activations (not hash lookups)
4. ENFORCE ≥4 complementary pair coverage for Frobenius
5. Encode resulting AAs as RNA codons directly

Author: Lando ⊗ ⊙perator
"""

# ── Primitive → AA → Codon maps ────────────────────────────────────

PRIMITIVE_TO_AA = {
    "D": "Met", "T": "Trp", "R": "Cys", "P": "Tyr", "F": "Phe",
    "K": "Ile", "G": "His", "Gm": "Asn", "Ph": "Gln",
    "H": "Asp", "S": "Lys", "W": "Glu",
}

AA_TO_PRIMITIVE = {v: k for k, v in PRIMITIVE_TO_AA.items()}

AA_CODON_POOL = {
    "Met": ["AUG"],
    "Trp": ["UGG"],
    "Cys": ["UGU", "UGC"],
    "Tyr": ["UAU", "UAC"],
    "Phe": ["UUU", "UUC"],
    "Ile": ["AUU", "AUC", "AUA"],
    "His": ["CAU", "CAC"],
    "Asn": ["AAU", "AAC"],
    "Gln": ["CAA", "CAG"],
    "Asp": ["GAU", "GAC"],
    "Lys": ["AAA", "AAG"],
    "Glu": ["GAA", "GAG"],
    "Ser": ["UCU", "UCC", "UCA", "UCG", "AGU", "AGC"],
    "Ala": ["GCU", "GCC", "GCA", "GCG"],
    "Gly": ["GGU", "GGC", "GGA", "GGG"],
    "Thr": ["ACU", "ACC", "ACA", "ACG"],
    "Val": ["GUU", "GUC", "GUA", "GUG"],
    "Leu": ["UUA", "UUG", "CUU", "CUC", "CUA", "CUG"],
    "Pro": ["CCU", "CCC", "CCA", "CCG"],
    "Arg": ["CGU", "CGC", "CGA", "CGG", "AGA", "AGG"],
    "His": ["CAU", "CAC"],
}

# Complementary pairs (index in PNAMES order)
PAIRS = [
    ("D", "W"),   # Pair 1: Dimensionality ↔ Winding
    ("T", "H"),   # Pair 2: Topology ↔ Chirality
    ("R", "S"),   # Pair 3: Recognition ↔ Stoichiometry
    ("P", "F"),   # Pair 4: Parity ↔ Fidelity
    ("K", "G"),   # Pair 5: Kinetics ↔ Granularity
    ("Gm", "Ph"), # Pair 6: Coupling ↔ Criticality
]

PNAMES = ["D", "T", "R", "P", "F", "K", "G", "Gm", "Ph", "H", "S", "W"]

# Structural AAs (non-activating, structure-supporting)
STRUCTURAL_AAS = ["Ser", "Ala", "Gly", "Thr", "Val", "Leu", "Pro"]


def ordinal_of_glyph(prim, glyph, GLYPH_ORDINALS):
    """Get ordinal value of a glyph for a given primitive."""
    return GLYPH_ORDINALS.get(prim, {}).get(glyph, 0)


def glyph_from_ordinal(prim, ordinal, ORD_TO_GLYPH):
    """Get glyph from ordinal for a given primitive."""
    return ORD_TO_GLYPH.get(prim, {}).get(ordinal, "?")


def fuse_types(bond_type, fg1_type, fg2_type, GLYPH_ORDINALS, ORD_TO_GLYPH):
    """
    Fuse bond + FG1 + FG2 types into a single reaction signature.
    
    For each primitive, take the MAX ordinal across all three types.
    This captures the most demanding structural feature present.
    """
    fused = {}
    for prim in PNAMES:
        vals = []
        for t in [bond_type, fg1_type, fg2_type]:
            glyph = t.get(prim, "?")
            vals.append(ordinal_of_glyph(prim, glyph, GLYPH_ORDINALS))
        max_val = max(vals)
        fused[prim] = glyph_from_ordinal(prim, max_val, ORD_TO_GLYPH)
    return fused


def complement_type(fused_type, GLYPH_ORDINALS, ORD_TO_GLYPH):
    """
    Compute structural complement of a fused reaction type.
    
    For each complementary pair (D↔W, T↔H, etc.):
      - Take the fused reaction's ordinal on the SOURCE primitive
      - Map it proportionally to the TARGET primitive's ordinal
    """
    site = {}
    for prim_a, prim_b in PAIRS:
        src_ord = ordinal_of_glyph(prim_a, fused_type.get(prim_a, "?"), GLYPH_ORDINALS)
        tgt_ord = ordinal_of_glyph(prim_b, fused_type.get(prim_b, "?"), GLYPH_ORDINALS)
        
        src_max = len(GLYPH_ORDINALS.get(prim_a, {})) - 1
        tgt_max = len(GLYPH_ORDINALS.get(prim_b, {})) - 1
        
        # Cross-map: src ordinal → target field
        if src_max > 0:
            ratio = src_ord / src_max
            cross_o = min(tgt_max, round(ratio * tgt_max))
        else:
            cross_o = 0
        
        # Cross-map: tgt ordinal → source field
        if tgt_max > 0:
            ratio = tgt_ord / tgt_max
            cross_o_rev = min(src_max, round(ratio * src_max))
        else:
            cross_o_rev = 0
        
        # The site value on each field is the CROSS from the other field
        site[prim_a] = glyph_from_ordinal(prim_a, cross_o_rev, ORD_TO_GLYPH)
        site[prim_b] = glyph_from_ordinal(prim_b, cross_o, ORD_TO_GLYPH)
    
    return site


def select_aa_for_primitive(prim, ordinal, max_ordinal, threshold_ratio=0.5):
    """
    Select an AA for a given primitive based on its ordinal.
    
    High ordinal (above threshold) → use activating AA
    Low ordinal (below threshold) → use structural AA
    """
    if max_ordinal > 0 and ordinal / max_ordinal >= threshold_ratio:
        return PRIMITIVE_TO_AA.get(prim)
    return None  # Will be filled with structural AA


def get_activating_aas(site_type, GLYPH_ORDINALS):
    """
    From a site type, determine which AAs to include.
    Returns (activating_aa_list, structural_aa_count, pairs_covered).
    """
    aas = []
    activated_primitives = set()
    
    for prim in PNAMES:
        glyph = site_type.get(prim, "?")
        o = ordinal_of_glyph(prim, glyph, GLYPH_ORDINALS)
        max_o = len(GLYPH_ORDINALS.get(prim, {})) - 1
        aa = select_aa_for_primitive(prim, o, max_o)
        if aa:
            aas.append(aa)
            activated_primitives.add(prim)
        else:
            aas.append(None)
    
    # Count complementary pairs covered
    pairs_covered = 0
    for pa, pb in PAIRS:
        if pa in activated_primitives or pb in activated_primitives:
            pairs_covered += 1
    
    return aas, activated_primitives, pairs_covered


def ensure_frobenius(aas, activated_primitives, pairs_covered, GLYPH_ORDINALS, ORD_TO_GLYPH):
    """
    Ensure at least 4 complementary pairs are covered for Frobenius.
    If <4, bump some low-ordinal primitives' AAs to activating.
    Returns (modified_aas, modified_primitives, new_pairs_covered).
    """
    if pairs_covered >= 4:
        return aas, activated_primitives, pairs_covered
    
    # Find pairs not yet covered
    missing_pairs = []
    for i, (pa, pb) in enumerate(PAIRS):
        if pa not in activated_primitives and pb not in activated_primitives:
            missing_pairs.append((pa, pb))
    
    # For each missing pair, activate the first primitive
    modified_aas = list(aas)
    modified_primitives = set(activated_primitives)
    
    for pa, pb in missing_pairs:
        if pairs_covered >= 4:
            break
        # Find an empty slot near this primitive's position
        for idx, prim in enumerate(PNAMES):
            if prim == pa and modified_aas[idx] is None:
                modified_aas[idx] = PRIMITIVE_TO_AA.get(pa)
                modified_primitives.add(pa)
                pairs_covered += 1
                break
        else:
            # If pa slot is taken, try pb
            for idx, prim in enumerate(PNAMES):
                if prim == pb and modified_aas[idx] is None:
                    modified_aas[idx] = PRIMITIVE_TO_AA.get(pb)
                    modified_primitives.add(pb)
                    pairs_covered += 1
                    break
    
    return modified_aas, modified_primitives, pairs_covered


def fill_structural_aas(aas):
    """Fill None slots with structure-supporting AAs."""
    result = []
    for aa in aas:
        if aa is not None:
            result.append(aa)
        else:
            # Pick a structural AA (cycle through options)
            idx = len(result) % len(STRUCTURAL_AAS)
            result.append(STRUCTURAL_AAS[idx])
    return result


def aas_to_rna(aas):
    """Encode an AA sequence into RNA codons."""
    codons = []
    for aa in aas:
        pool = AA_CODON_POOL.get(aa, ["UCU"])
        # Pick codon deterministically based on position
        idx = len(codons) % len(pool)
        codons.append(pool[idx])
    return "".join(codons)


def design_rna_from_reaction(reaction_sig, GLYPH_ORDINALS, ORD_TO_GLYPH):
    """
    Full RNA design pipeline:
    1. Fuse bond + FG1 + FG2 types
    2. Compute complement
    3. Select AAs
    4. Ensure Frobenius (≥4 pairs)
    5. Fill structural AAs
    6. Encode as RNA
    
    Returns (rna, aa_sequence, site_type, pairs_covered, fused_type)
    """
    import math
    
    # Step 1: Fuse
    fused = fuse_types(
        reaction_sig.bond_type,
        reaction_sig.fg1_type,
        reaction_sig.fg2_type,
        GLYPH_ORDINALS, ORD_TO_GLYPH
    )
    
    # Step 2: Complement
    site_type = complement_type(fused, GLYPH_ORDINALS, ORD_TO_GLYPH)
    
    # Step 3: Select AAs
    aas, activated, pairs_covered = get_activating_aas(site_type, GLYPH_ORDINALS)
    
    # Step 4: Ensure Frobenius
    aas, activated, pairs_covered = ensure_frobenius(
        aas, activated, pairs_covered, GLYPH_ORDINALS, ORD_TO_GLYPH
    )
    
    # Step 5: Fill structural AAs
    aas = fill_structural_aas(aas)
    
    # Step 6: Encode as RNA
    rna = aas_to_rna(aas)
    
    return rna, aas, site_type, pairs_covered, fused


def verify_frobenius(aa_list, from_genetic_code_module=True):
    """
    Verify Frobenius coverage of an AA list using the same 
    logic as serpentrod_v2.frobenius_pair_coverage.
    """
    if from_genetic_code_module:
        from p4ramill_py.genetic_code import IG_PRIMITIVE_OF_AA
    else:
        IG_PRIMITIVE_OF_AA = {
            "Met": "Ð (Dimensionality)", "Trp": "Þ (Topology)",
            "Cys": "Ř (Recognition)", "Tyr": "Φ (Parity)",
            "Phe": "ƒ (Fidelity)", "Ile": "Ç (Kinetics)",
            "His": "Γ (Granularity)", "Asn": "ɢ (Coupling)",
            "Gln": "⊙ (Criticality)", "Asp": "Ħ (Chirality)",
            "Lys": "Σ (Stoichiometry)", "Glu": "Ω (Winding)",
        }
    
    pairs = [{"Dimensionality","Winding"},{"Topology","Chirality"},
             {"Recognition","Stoichiometry"},{"Parity","Fidelity"},
             {"Kinetics","Granularity"},{"Coupling","Criticality"}]
    
    activated = set()
    for aa in aa_list:
        p = IG_PRIMITIVE_OF_AA.get(aa)
        if p:
            name = p.split("(")[1].rstrip(")") if "(" in p else p
            activated.add(name)
    
    covered = sum(1 for pair in pairs if activated & pair)
    return covered, covered >= 4, activated
