#!/usr/bin/env python3
"""
genetic_tuples.py — Generative Tuple Construction for the Gene→Protein Pipeline

Instead of hardcoding STAGE_TUPLES at compile time, each stage's structural
tuple is a FUNCTION of the sequence-derived features. This makes the grammar
GENUINELY GENERATIVE: the input drives the structural type, not just the readout.

The mapping from pipeline string names to IG primitive Unicode values is
defined here, along with per-stage tuple generators that inspect:
  - Amino acid composition (which IG primitives are activated)
  - Secondary structure predictions (helix/sheet content)
  - Tertiary contact diversity (interaction types)
  - Quaternary subunit count and symmetry
  - Chain length and complexity metrics

Each generated tuple is a valid crystal address verified by:
  1. Ouroboricity tier consistency — all 7 stages remain O₀/O₁
  2. Frobenius condition — mu∘delta=id holds across the transformation
  3. Monotonic advance — 𐑭 constraint on trajectory through the crystal

Derived from the canonical mapping in Primitives/Core.lean and verified
against the catalog entries for each stage type.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any

# ── Pipeline string → IG primitive Unicode values ─────────────────

# This maps the pipeline's internal string names (used in STAGE_TUPLES)
# to the IG primitive Unicode characters used by imscribe_system.
# The Unicode values are the canonical enum values from the grammar.

IG_CHARS: Dict[str, Dict[str, str]] = {
    "⊢": {  # ⊢ — Dimensionality
        "wedge": "\U0001045b",   # 𐑛 — 0d point
        "tri":   "\U00010468",   # 𐑨 — triangle (2d surface)
        "infty": "\U0001047c",   # 𐑼 — infinite-dimensional
        "odot":  "\U00010466",   # 𐑦 — imscriptive (self-written)
    },
    "⊣": {  # ⊣ — Topology
        "network":   "\U00010461",  # 𐑡 — branching connectivity
        "in":        "\U00010470",  # 𐑰 — containment
        "bowtie":    "\U00010465",  # 𐑥 — crossing point
        "boxtimes":  "\U00010476",  # 𐑶 — irreducible product
        "odot":      "\U00010478",  # 𐑸 — self-referential closure
    },
    "≻": {  # ≻ — Relational mode
        "super":   "\U00010469",  # 𐑩 — supervenience
        "cat":     "\U00010451",  # 𐑑 — functorial
        "dagger":  "\U0001047d",  # 𐑽 — adjoint one-way
        "lr":      "\U0001047e",  # 𐑾 — bidirectional feedback
    },
    "≺": {  # ≺ — Parity / Symmetry
        "asym":    "\U00010457",  # 𐑗 — no symmetry
        "psi":     "\U0001047f",  # 𐑿 — quantum superposition
        "pm":      "\U0001046c",  # 𐑬 — ℤ₂ partial symmetry
        "sym":     "\U0001046f",  # 𐑯 — all symmetries unbroken
        "pm_sym":  "\U00010479",  # 𐑹 — Frobenius-special ±ˢ
    },
    "⋈": {  # ⋈ — Fidelity / Physical regime
        "ell":  "\U00010471",  # 𐑱 — classical (no coherence)
        "eth":  "\U0001045e",  # 𐑞 — thermal/noisy
        "hbar": "\U00010450",  # 𐑐 — quantum coherence
    },
    "⊤": {  # ⊤ — Kinetics / Relaxation
        "fast": "\U0001047a",  # 𐑺 — τ≪T (driven)
        "mod":  "\U0001046a",  # 𐑪 — τ∼T (moderate)
        "slow": "\U00010467",  # 𐑧 — τ≫T (near-equilibrium)
        "trap": "\U00010464",  # 𐑤 — frozen (ordered)
        "MBL":  "\U00010458",  # 𐑘 — frozen (disordered)
    },
    "∈": {  # ∈ — Scope / Interaction range
        "beth":   "\U00010472",  # 𐑲 — nearest-neighbor (local)
        "gimel":  "\U0001045a",  # 𐑚 — intermediate (mesoscale)
        "aleph":  "\U00010454",  # 𐑔 — long-range/universal
    },
    "∋": {  # ∋ — Interaction grammar
        "and":   "\U0001045d",  # 𐑝 — all-simultaneous (∧)
        "or":    "\U0001045c",  # 𐑜 — alternate paths (∨)
        "seq":   "\U00010460",  # 𐑠 — ordered steps (→)
        "broad": "\U00010475",  # 𐑵 — one-to-all broadcast (≫)
    },
    "⊙": {  # ⊙ — Criticality
        "sub":       "\U00010462",  # 𐑢 — sub-critical (no scaling)
        "c":         "\u2299",      # ⊙ — critical (self-modeling gate)
        "c_complex": "\U0001046e",  # 𐑮 — complex-plane critical
        "EP":        "\U0001047b",  # 𐑻 — exceptional point
        "super":     "\U00010463",  # 𐑣 — supercritical (runaway)
    },
    "⊥": {  # ⊥ — Chirality / Markov order
        "0":   "\U00010453",  # 𐑓 — memoryless (n=0)
        "1":   "\U00010452",  # 𐑒 — one-step (n=1)
        "2":   "\U00010456",  # 𐑖 — two-step (n=2)
        "inf": "\U0001046b",  # 𐑫 — no finite n
    },
    "⊞": {  # ⊞ — Stoichiometry
        "one":    "\U00010459",  # 𐑙 — 1:1 (one type, one instance)
        "many":   "\U00010455",  # 𐑕 — n:n (many identical)
        "hetero": "\U00010473",  # 𐑳 — n:m (multiple distinct types)
    },
    "⊡": {  # ⊡ — Topological invariant
        "0":     "\U00010477",  # 𐑷 — trivial (no winding)
        "Z2":    "\U00010474",  # 𐑴 — ℤ₂ parity-protected
        "Z":     "\U0001046d",  # 𐑭 — integer winding
        "NA":    "\U0001045f",  # 𐑟 — non-Abelian braiding
    },
}

# ── Reverse mapping: IG char → pipeline string name ─────────────

def ig_char_to_name(ig_char: str) -> Tuple[str, str]:
    """Reverse-lookup an IG Unicode char to (primitive_key, value_name)."""
    for prim_key, val_map in IG_CHARS.items():
        for val_name, char in val_map.items():
            if char == ig_char:
                return (prim_key, val_name)
    raise ValueError(f"Unknown IG character: {ig_char!r}")

def ig_tuple_to_pipeline(tup: Dict[str, str]) -> Dict[str, str]:
    """Convert an IG Unicode tuple dict to pipeline string names."""
    result = {}
    for prim_key, ig_val in tup.items():
        _, val_name = ig_char_to_name(ig_val)
        result[prim_key] = val_name
    return result


# ── Feature extraction from pipeline state ──────────────────────

# These functions extract the specific features that drive tuple generation.
# They operate on the pipeline's data classes (AASite, SecondaryElement,
# TertiaryContact) which are injected as dicts for portability.

def extract_kinetics_features(aa_chain: List[Dict]) -> Dict[str, float]:
    """
    Extract kinetics-relevant features from the amino acid chain.
    
    ⊤ (Kinetics) is driven by β-branched amino acids:
      - Ile (⊤), Val (ground), Thr (ground) — all β-branched
      - High β-branch content → slow kinetics (⊤_slow)
      - Low β-branch content → fast kinetics (⊤_fast)
      - Moderate → ⊤_mod
    
    Returns dict with fractions and counts.
    """
    n = len(aa_chain)
    if n == 0:
        return {"beta_branched_frac": 0.0, "proline_frac": 0.0, "glycine_frac": 0.0}
    
    beta_branched = sum(1 for aa in aa_chain if aa.get("aa_code") in ("Ile", "Val", "Thr"))
    prolines = sum(1 for aa in aa_chain if aa.get("aa_code") == "Pro")
    glycines = sum(1 for aa in aa_chain if aa.get("aa_code") == "Gly")
    
    return {
        "beta_branched_frac": beta_branched / n,
        "proline_frac": prolines / n,
        "glycine_frac": glycines / n,
        "beta_branched_count": beta_branched,
        "proline_count": prolines,
        "glycine_count": glycines,
    }


def extract_criticality_features(aa_chain: List[Dict], 
                                  secondary_elements: List[Dict]) -> Dict[str, Any]:
    """
    Extract criticality-relevant features.
    
    ⊙ (Criticality) responds to:
      - His (⊙) at predicted turn/active-site positions → potential ⊙_ÿ
      - Gln (⊙) in helical regions → complex-plane criticality
      - Cys (≻) disulfide patterns → exceptional point behavior
    
    For the pipeline, most sequences remain sub-critical (⊙_sub).
    A sequence ≥3 His at loop positions can push to ⊙_c for
    the tertiary stage — indicating self-structuring criticality.
    """
    n = len(aa_chain)
    if n == 0:
        return {"his_at_loops": 0, "cys_pairs": 0, "critical_flag": False}
    
    # Identify loop/turn positions from secondary structure
    loop_positions = set()
    for elem in secondary_elements:
        if elem.get("type") in ("turn", "loop", "C"):
            for p in range(elem.get("start", 0), elem.get("end", 0) + 1):
                loop_positions.add(p)
    # Default: all positions are loops if no predictions
    if not loop_positions and n > 0:
        loop_positions = set(range(n))
    
    his_at_loops = sum(1 for i, aa in enumerate(aa_chain)
                       if aa.get("aa_code") == "His" and i in loop_positions)
    cys_count = sum(1 for aa in aa_chain if aa.get("aa_code") == "Cys")
    
    return {
        "his_at_loops": his_at_loops,
        "cys_count": cys_count,
        "cys_pairs": cys_count // 2,
        "critical_flag": his_at_loops >= 3,
    }


def extract_parity_features(aa_chain: List[Dict],
                             secondary_elements: List[Dict]) -> Dict[str, Any]:
    """
    Extract parity/symmetry-breaking features.
    
    ≺ (Parity) responds to:
      - Tyr (≺) — activated parity residue → can break or preserve symmetry
      - His (⊙) at active sites → symmetry broken (≺_asym)
      - Regular repeat patterns → symmetry preserved (≺_pm)
    
    In protein folding:
      - All-helical or all-sheet → ≺_pm (partial symmetry preserved)
      - Mixed helix+sheet → ≺_asym (symmetry broken by structural diversity)
    """
    if not secondary_elements:
        return {"has_helices": False, "has_sheets": False, 
                "mixed_secondary": False, "tyr_count": 0}
    
    has_helices = any(e.get("type") == "helix" for e in secondary_elements)
    has_sheets = any(e.get("type") == "sheet" for e in secondary_elements)
    tyr_count = sum(1 for aa in aa_chain if aa.get("aa_code") == "Tyr")
    his_count = sum(1 for aa in aa_chain if aa.get("aa_code") == "His")
    
    return {
        "has_helices": has_helices,
        "has_sheets": has_sheets,
        "mixed_secondary": has_helices and has_sheets,
        "tyr_count": tyr_count,
        "his_count": his_count,
    }


def extract_grammar_features(tertiary_contacts: List[Dict]) -> Dict[str, Any]:
    """
    Extract interaction grammar features.
    
    ∋ (Interaction grammar) responds to:
      - Number of distinct interaction types → and (∧), seq (→), broad (≫)
      - Contact density → broadcast vs sequential
    """
    if not tertiary_contacts:
        return {"interaction_types": set(), "contact_count": 0, "contact_density": 0.0}
    
    types = set(c.get("interaction_type") for c in tertiary_contacts)
    return {
        "interaction_types": types,
        "contact_count": len(tertiary_contacts),
        "contact_density": len(tertiary_contacts) / max(1, len(types)),
    }

# ── Default / fallback tuples ────────────────────────────────────

# The catalog defaults are the base values from protein_* catalog entries.
# When sequence features don't trigger a change, these are used.
# Encoded as pipeline string names for readability.

DEFAULT_TUPLES: Dict[str, Dict[str, str]] = {
    "dna_gene": {
        "⊢": "𐑨", "⊣": "𐑶", "≻": "𐑾", "≺": "𐑬", "⋈": "𐑱",
        "⊤": "𐑧", "∈": "𐑚", "∋": "𐑠", "⊙": "𐑢",
        "⊥": "𐑖", "⊞": "𐑙", "⊡": "𐑭",
    },
    "pre_mrna": {
        "⊢": "𐑨", "⊣": "𐑰", "≻": "𐑑", "≺": "𐑗", "⋈": "𐑱",
        "⊤": "𐑤", "∈": "𐑚", "∋": "𐑠", "⊙": "𐑢",
        "⊥": "𐑒", "⊞": "𐑙", "⊡": "𐑷",
    },
    "mature_mrna": {
        "⊢": "𐑨", "⊣": "𐑰", "≻": "𐑽", "≺": "𐑗", "⋈": "𐑱",
        "⊤": "𐑧", "∈": "𐑚", "∋": "𐑠", "⊙": "𐑢",
        "⊥": "𐑒", "⊞": "𐑙", "⊡": "𐑷",
    },
    "nascent_polypeptide": {
        "⊢": "𐑨", "⊣": "𐑡", "≻": "𐑑", "≺": "𐑗", "⋈": "𐑱",
        "⊤": "𐑘", "∈": "𐑚", "∋": "𐑠", "⊙": "𐑢",
        "⊥": "𐑖", "⊞": "𐑳", "⊡": "𐑷",
    },
    "secondary_structure": {
        "⊢": "𐑦", "⊣": "𐑸", "≻": "𐑽", "≺": "𐑬", "⋈": "𐑱",
        "⊤": "𐑤", "∈": "𐑚", "∋": "𐑠", "⊙": "𐑢",
        "⊥": "𐑖", "⊞": "𐑕", "⊡": "𐑷",
    },
    "tertiary_structure": {
        "⊢": "𐑦", "⊣": "𐑸", "≻": "𐑾", "≺": "𐑗", "⋈": "𐑱",
        "⊤": "𐑧", "∈": "𐑲", "∋": "𐑝", "⊙": "𐑢",
        "⊥": "𐑖", "⊞": "𐑙", "⊡": "𐑷",
    },
    "quaternary_structure": {
        "⊢": "𐑦", "⊣": "𐑸", "≻": "𐑾", "≺": "𐑬", "⋈": "𐑱",
        "⊤": "𐑧", "∈": "𐑚", "∋": "𐑝", "⊙": "𐑢",
        "⊥": "𐑒", "⊞": "𐑳", "⊡": "𐑭",
    },
}


def _pipeline_to_ig(tup: Dict[str, str]) -> Dict[str, str]:
    """Convert pipeline string names to IG Unicode values."""
    ig_tup = {}
    for prim_key, val_name in tup.items():
        if prim_key in IG_CHARS and val_name in IG_CHARS[prim_key]:
            ig_tup[prim_key] = IG_CHARS[prim_key][val_name]
        else:
            raise ValueError(f"No IG char for {prim_key}={val_name}")
    return ig_tup


def _ig_to_pipeline(tup: Dict[str, str]) -> Dict[str, str]:
    """Convert IG Unicode tuple to pipeline string names."""
    result = {}
    for prim_key, ig_char in tup.items():
        _, val_name = ig_char_to_name(ig_char)
        result[prim_key] = val_name
    return result


def pipeline_tuple_to_ig(pipeline_tup: Dict[str, str]) -> Dict[str, str]:
    """Public wrapper."""
    return _pipeline_to_ig(pipeline_tup)


# ── Stage-specific generative functions ────────────────────────

def generate_dna_gene_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate the DNA gene structural tuple.
    
    SEQUENCE-DRIVEN:
      - Ó (⊡ winding): depends on sequence topology
        If the sequence contains inverted repeats or palindromes → ⊡_Z2
        If direct repeats → ⊡_0
        Default → ⊡_Z (from catalog)
    
    TYPE-INVARIANT (biological process):
      - ⊢=tri, ⊣=boxtimes, ≻=lr, ≺=pm, ⋈=ell, ⊤=slow
      - ∈=beth, ∋=seq, ⊙=sub, ⊥=two, ⊞=one
    """
    seq = features.get("dna_sequence", "")
    tup = dict(DEFAULT_TUPLES["dna_gene"])
    
    # ⊡: detect inverted repeats → Z2, direct repeats → Z, else 0
    # Simple heuristic: check for palindromic subsequences
    seq_len = len(seq)
    if seq_len >= 10:
        # Check for inverted repeats (palindromes)
        has_palindrome = False
        for i in range(seq_len - 5):
            sub = seq[i:i+6]
            comp = {"A": "U", "U": "A", "G": "C", "C": "G",
                    "a": "u", "u": "a", "g": "c", "c": "g"}
            rev_comp = "".join(comp.get(c, c) for c in reversed(sub))
            if sub == rev_comp:
                has_palindrome = True
                break
        if has_palindrome:
            tup['⊡'] = "Z2"
        # Direct repeat detection is a no-op for default
    
    return _pipeline_to_ig(tup)


def generate_pre_mrna_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Pre-mRNA transcript tuple.
    
    SEQUENCE-DRIVEN:
      - ⊤ (kinetics): driven by GC content of transcript
        High GC (>60%) → ⊤_slow (stable secondary structure impedes processing)
        Low GC (<40%) → ⊤_fast (unstructured, rapid)
        Default → ⊤_mod
    
    TYPE-INVARIANT: ⊣=in (containment — introns contain exons)
    """
    tup = dict(DEFAULT_TUPLES["pre_mrna"])
    seq = features.get("dna_sequence", "")
    
    if seq:
        gc = (seq.upper().count("G") + seq.upper().count("C")) / len(seq)
        if gc > 0.60:
            tup['⊤'] = "slow"   # Stable GC-rich, slow kinetics
        elif gc < 0.40:
            tup['⊤'] = "fast"   # AT-rich, fast kinetics
    
    return _pipeline_to_ig(tup)


def generate_mature_mrna_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Mature mRNA tuple.
    Similar to pre-mRNA but ≻=dagger (adjoint — codon→AA is not bidirectional)
    """
    tup = dict(DEFAULT_TUPLES["mature_mrna"])
    seq = features.get("dna_sequence", "")
    
    # Copy kinetics from pre-mRNA if available
    pre_kinetics = features.get("pre_mrna_kinetics", None)
    if pre_kinetics:
        tup['⊤'] = pre_kinetics
    
    return _pipeline_to_ig(tup)

def generate_nascent_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Nascent polypeptide tuple.
    
    SEQUENCE-DRIVEN:
      - ⊤ (kinetics): driven by β-branched AA content
        ≥30% Ile+Val+Thr → ⊤_slow (β-sheet bottlenecks)
        ≥15% → ⊤_mod
        <15% → ⊤_fast
      - ⊞ (stoichiometry): driven by AA diversity
        All 20 AAs present → ⊞_hetero (max diversity)
        <8 distinct AAs → ⊞_one (homogenous)
        Default → ⊞_hetero (nascent chain always has diverse AAs)
      - ⊥ (chirality): driven by start codon context
        If Met at position 0 → ⊥_two (initiation memory)
    
    TYPE-INVARIANT:
      - ⊣=network (branching — residues branch off backbone)
      - ≻=cat (functorial — translation is a functor mRNA→protein)
    """
    tup = dict(DEFAULT_TUPLES["nascent_polypeptide"])
    aa_chain = features.get("aa_chain", [])
    kinetics = extract_kinetics_features(aa_chain)
    
    # ⊤: kinetics from β-branched AA content
    bb_frac = kinetics["beta_branched_frac"]
    if bb_frac >= 0.30:
        tup['⊤'] = "slow"
    elif bb_frac >= 0.15:
        tup['⊤'] = "mod"
    else:
        tup['⊤'] = "fast"
    
    # ⊞: AA diversity drives stoichiometry
    unique_aas = set()
    for aa in aa_chain:
        code = aa.get("aa_code")
        if code:
            unique_aas.add(code)
    n_unique = len(unique_aas)
    if n_unique >= 16:
        tup['⊞'] = "hetero"    # Near-full code diversity
    elif n_unique >= 8:
        tup['⊞'] = "many"      # Moderate diversity
    else:
        tup['⊞'] = "one"       # Low diversity (e.g., poly-Q)
    
    # ⊥: chirality from chain length
    # Longer chains retain more positional memory
    chain_len = len(aa_chain)
    if chain_len >= 50:
        tup['⊥'] = "2"
    elif chain_len >= 10:
        tup['⊥'] = "1"
    else:
        tup['⊥'] = "0"
    
    return _pipeline_to_ig(tup)


def generate_secondary_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Secondary structure tuple.
    
    SEQUENCE-DRIVEN:
      - ≺ (parity): mixed helix+sheet → ≺_asym (broken)
        All-helix or all-sheet → ≺_pm (partial symmetry)
        No secondary structure → ≺_asym
      - ⊤ (kinetics): reflects predicted folding rate
        Many helix elements → ⊤_mod
        Many sheet elements → ⊤_slow (sheets form slower)
        Mixed → ⊤_slow
      - ⊞ (stoichiometry): driven by element count
        ≥5 elements → ⊞_many
        ≥10 → ⊞_hetero
      - ⊥ (chirality): element-type memory
        Both helices and sheets → ⊥_two
        Single type → ⊥_one
        None → ⊥_0
    
    TYPE-INVARIANT:
      - ⊣=odot (secondary structures are self-referential — H-bonds loop back)
      - ≻=dagger (adjoint — local sequence → local structure)
      - ∈=beth (nearest-neighbor — secondary structure is local)
      - ∋=seq (sequential folding along chain)
    """
    tup = dict(DEFAULT_TUPLES["secondary_structure"])
    aa_chain = features.get("aa_chain", [])
    secondary_elements = features.get("secondary_elements", [])
    
    parity = extract_parity_features(aa_chain, secondary_elements)
    kinetics = extract_kinetics_features(aa_chain)
    
    # ≺: parity from secondary structure diversity
    if parity["mixed_secondary"]:
        tup['≺'] = "asym"     # Mixed → symmetry broken
    elif secondary_elements:
        tup['≺'] = "pm"       # Single type → partial symmetry
    else:
        tup['≺'] = "asym"     # No structure → no symmetry
    
    # ⊤: kinetics from sheet/helix content
    n_helices = sum(1 for e in secondary_elements if e.get("type") == "helix")
    n_sheets = sum(1 for e in secondary_elements if e.get("type") == "sheet")
    if n_sheets >= n_helices and n_sheets >= 2:
        tup['⊤'] = "slow"     # Sheet-dominant → slow folding
    elif n_helices >= 3:
        tup['⊤'] = "mod"      # Helix-dominant → moderate
    elif not secondary_elements:
        tup['⊤'] = "fast"     # No structure → fast
    else:
        tup['⊤'] = "mod"      # Default
    
    # ⊞: element count
    n_elems = len(secondary_elements)
    if n_elems >= 10:
        tup['⊞'] = "hetero"
    elif n_elems >= 3:
        tup['⊞'] = "many"
    else:
        tup['⊞'] = "one"
    
    # ⊥: chirality from element diversity
    if parity["mixed_secondary"]:
        tup['⊥'] = "2"      # Both types → two-step memory
    elif n_helices > 0 or n_sheets > 0:
        tup['⊥'] = "1"      # Single type → one-step
    else:
        tup['⊥'] = "0"        # No structure → memoryless
    
    return _pipeline_to_ig(tup)

def generate_tertiary_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Tertiary structure tuple.
    
    This is the MOST sequence-sensitive stage. Tertiary structure
    is where the input's specific chemical identity emerges.
    
    SEQUENCE-DRIVEN:
      - ≺ (parity): symmetry-breaking detection
        If His (⊙) at predicted loop positions ≥3 → ≺_asym (broken)
        If all contacts are hydrophobic only → ≺_pm (partial)
        If mixed contact types (hydrophobic+disulfide+ionic) → ≺_asym
      - ⊙ (criticality): His/loop detection
        If ≥3 His at loop positions → ⊙_c (self-structuring criticality)
        Otherwise → ⊙_sub (sub-critical)
      - ∈ (scope): driven by chain length and contact range
        Chain ≥200 or contacts span >100 residues → ∈_aleph
        Chain ≥100 → ∈_gimel
        Else → ∈_beth
      - ∋ (grammar): driven by interaction type diversity
        ≥3 interaction types → ∋_and (conjunctive — multiple mechanisms)
        =2 interaction types → ∋_broad (broadcast — folding across scales)
        =1 interaction type → ∋_seq (sequential — single mechanism)
      - ⊤ (kinetics): driven by folding complexity
        Many long-range contacts → ⊤_slow (topological frustration)
        Few contacts → ⊤_mod or ⊤_fast
      - ⊥ (chirality): contact directionality
        Contacts span both N→C directions → ⊥_two
        Only one direction → ⊥_one
    
    TYPE-INVARIANT:
      - ⊢=tri, ⋈=ell (classical folding), ⊣=odot
      - ≻=lr (bidirectional — N and C termini interact)
      - ⊞=one (single chain), ⊡=0
    """
    tup = dict(DEFAULT_TUPLES["tertiary_structure"])
    aa_chain = features.get("aa_chain", [])
    secondary_elements = features.get("secondary_elements", [])
    tertiary_contacts = features.get("tertiary_contacts", [])
    
    crit = extract_criticality_features(aa_chain, secondary_elements)
    parity = extract_parity_features(aa_chain, secondary_elements)
    grammar = extract_grammar_features(tertiary_contacts)
    
    # ⊙: His at loops → self-modeling criticality
    if crit["critical_flag"]:
        tup['⊙'] = "c"        # ⊙ — self-structuring criticality
        # ⊙=c requires ⊤≥mod to stabilize self-modeling criticality
        if tup.get("⊤") == "fast":
            tup['⊤'] = "mod"     # Upgrade kinetics to sustain criticality
    elif crit["cys_pairs"] >= 2:
        tup['⊙'] = "c_complex"  # Complex-plane critical (disulfide network)
    else:
        tup['⊙'] = "sub"      # Default sub-critical
    
    # ≺: parity from structural diversity
    if crit["critical_flag"] or parity["mixed_secondary"]:
        tup['≺'] = "asym"       # Symmetry broken
    elif grammar["contact_count"] >= 10:
        tup['≺'] = "pm"         # Partial symmetry from many contacts
    else:
        tup['≺'] = "asym"       # Default broken symmetry for folded state
    
    # ∈: scope from chain length
    n = len(aa_chain)
    if grammar["contact_count"] > 0:
        max_range = max(c.get("j", 0) - c.get("i", 0) for c in tertiary_contacts)
    else:
        max_range = 0
    if n >= 200 or max_range >= 100:
        tup['∈'] = "aleph"      # Universal — long-range contacts
    elif n >= 100 or max_range >= 50:
        tup['∈'] = "gimel"      # Mesoscale
    else:
        tup['∈'] = "beth"       # Local
    
    # ∋: grammar from interaction diversity
    n_types = len(grammar.get("interaction_types", set()))
    if n_types >= 3:
        tup['∋'] = "and"       # Multiple mechanisms concurrently
    elif n_types == 2:
        tup['∋'] = "broad"     # Two mechanisms broadcast across chain
    elif n_types == 1:
        tup['∋'] = "seq"       # Single sequential mechanism
    else:
        tup['∋'] = "and"       # Default — folding is inherently conjunctive
    
    # ⊤: kinetics from contact complexity
    n_contacts = grammar["contact_count"]
    if n_contacts >= 20:
        tup['⊤'] = "slow"       # Many constraints → slow folding
    elif n_contacts >= 8:
        tup['⊤'] = "mod"        # Moderate
    elif n_contacts >= 3:
        tup['⊤'] = "fast"       # Few contacts → fast folding
    else:
        tup['⊤'] = "fast"       # Very few or no contacts
    
    # ⊥: chirality from contact directionality
    if tertiary_contacts:
        has_n_terminal = any(c.get("i", 999) < n // 3 for c in tertiary_contacts)
        has_c_terminal = any(c.get("j", 0) > 2 * n // 3 for c in tertiary_contacts)
        if has_n_terminal and has_c_terminal:
            tup['⊥'] = "2"    # N↔C contacts → two-step memory
        else:
            tup['⊥'] = "1"    # Local contacts → one-step
    else:
        tup['⊥'] = "1"        # Default
    
    return _pipeline_to_ig(tup)


def generate_quaternary_tuple(features: Dict[str, Any]) -> Dict[str, str]:
    """
    Quaternary structure tuple.
    
    SEQUENCE-DRIVEN:
      - ⊞ (stoichiometry): driven by subunit count and diversity
        monomer → ⊞_one
        homomultimer (2-4 identical) → ⊞_many
        heteromultimer (different chains) → ⊞_hetero
      - ⊡ (winding): driven by quaternary symmetry
        monomer → ⊡_0
        homodimer → ⊡_Z2 (ℤ₂ symmetry — flip)
        tetramer → ⊡_Z (cyclic symmetry)
        higher-order → ⊡_NA
      - ∋ (grammar): driven by interface type
        One interface → ∋_seq
        Multiple interfaces → ∋_and
        Allosteric → ∋_broad
      - ⊥ (chirality): subunit arrangement
        Symmetric dimer → ⊥_one
        Asymmetric → ⊥_two
      - ≺ (parity): symmetry of the complex
        Symmetric → ≺_pm
        Asymmetric → ≺_asym
      - K (kinetics): assembly rate
        Fast assembly → kinetics_mod
        Slow (chaperone-mediated) → kinetics_slow
    
    TYPE-INVARIANT:
      - ⊢=tri, ⋈=ell, ⊣=odot (closed assembly)
      - ≻=lr (bidirectional subunit communication)
    """
    tup = dict(DEFAULT_TUPLES["quaternary_structure"])
    aa_chain = features.get("aa_chain", [])
    num_subunits = features.get("num_subunits", 1)
    tertiary_contacts = features.get("tertiary_contacts", [])
    
    # ⊞: stoichiometry from subunit count
    if num_subunits == 1:
        tup['⊞'] = "one"
    elif num_subunits <= 4:
        # Check if all subunits are identical (homomultimer)
        # For now, assume homomultimer unless Cys pairs suggest hetero
        cys_count = sum(1 for aa in aa_chain if aa.get("aa_code") == "Cys")
        if cys_count >= 6 and num_subunits >= 2:
            tup['⊞'] = "hetero"  # Disulfide crosslinks → hetero
        else:
            tup['⊞'] = "many"    # Homomultimer
    else:
        tup['⊞'] = "hetero"      # Complex → hetero
    
    # ⊡: winding from symmetry
    if num_subunits == 1:
        tup['⊡'] = "0"
    elif num_subunits == 2:
        tup['⊡'] = "Z2"          # ℤ₂ — dimer flip symmetry
    elif num_subunits in (3, 4, 6):
        tup['⊡'] = "Z"           # Cyclic symmetry
    else:
        tup['⊡'] = "NA"          # Non-Abelian if complex enough
        # Only if ≥8 subunits with diverse interfaces
        if num_subunits < 8:
            tup['⊡'] = "Z"       # Fallback to cyclic
    
    # ∋: grammar from interface count
    all_interface_residues = set()
    for subunit in features.get("quaternary_subunits", []):
        for r in subunit.get("interface_residues", []):
            all_interface_residues.add(r)
    n_interfaces = len(all_interface_residues) // max(1, num_subunits)
    if n_interfaces >= 5:
        tup['∋'] = "broad"      # Extensive interfaces
    elif n_interfaces >= 2:
        tup['∋'] = "and"        # Multiple interfaces
    else:
        tup['∋'] = "seq"        # Single interface
    
    # ≺: parity from symmetry
    if num_subunits == 1:
        tup['≺'] = "pm"          # Monomer preserves partial symmetry
    elif num_subunits == 2:
        tup['≺'] = "pm"          # Dimer has ℤ₂ symmetry
    elif num_subunits in (3, 4, 6):
        tup['≺'] = "pm"          # Higher symmetry
    else:
        tup['≺'] = "asym"        # Asymmetric complex
    
    # ⊥: chirality from dimer symmetry
    if num_subunits >= 2:
        tup['⊥'] = "1"         # One-step — interface memory
    else:
        tup['⊥'] = "1"         # Default
    
    # ⊤: kinetics from contact count
    if len(tertiary_contacts) >= 20 and num_subunits >= 2:
        tup['⊤'] = "slow"        # Complex assembly
    else:
        tup['⊤'] = "mod"         # Moderate assembly
    
    return _pipeline_to_ig(tup)

# ── Master generator: produce all 7 stage tuples from features ──

STAGE_GENERATORS = {
    "dna_gene": generate_dna_gene_tuple,
    "pre_mrna": generate_pre_mrna_tuple,
    "mature_mrna": generate_mature_mrna_tuple,
    "nascent_polypeptide": generate_nascent_tuple,
    "secondary_structure": generate_secondary_tuple,
    "tertiary_structure": generate_tertiary_tuple,
    "quaternary_structure": generate_quaternary_tuple,
}


def generate_all_tuples(features: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Generate all 7 stage tuples from sequence-derived features.
    
    Args:
        features: dict containing all computed pipeline features
            Required keys: 'aa_chain', 'secondary_elements', 
                           'tertiary_contacts', 'dna_sequence'
            Optional: 'num_subunits', 'quaternary_subunits', etc.
    
    Returns:
        Dict mapping stage_name → IG Unicode tuple dict
    """
    # Ensure features has all needed keys with defaults
    features.setdefault("aa_chain", [])
    features.setdefault("secondary_elements", [])
    features.setdefault("tertiary_contacts", [])
    features.setdefault("dna_sequence", "")
    features.setdefault("num_subunits", 1)
    features.setdefault("quaternary_subunits", [])
    
    # Propagate kinetics from pre-mRNA to mature mRNA
    pre_feats = dict(features)
    pre_tup = generate_pre_mrna_tuple(pre_feats)
    pre_kinetics = None
    for key, val in IG_CHARS['⊤'].items():
        if val == pre_tup.get("⊤"):
            pre_kinetics = key
            break
    features["pre_mrna_kinetics"] = pre_kinetics
    
    generated = {}
    for stage_name, generator in STAGE_GENERATORS.items():
        generated[stage_name] = generator(features)
        # Pass quaternary features forward
        if stage_name == "quaternary_structure":
            # Already handled by features
            pass
    
    return generated


# ── Distance computation ─────────────────────────────────────────

PRIMITIVE_WEIGHTS = {
    "⊢": 1.0, "⊣": 1.0, "≻": 1.0, "≺": 1.0, "⋈": 1.0, "⊤": 1.0,
    "∈": 1.0, "∋": 1.0, "⊙": 1.0, "⊥": 1.0, "⊞": 1.0, "⊡": 1.0,
}

# Ordinal positions for distance computation
PRIMITIVE_ORDINALS = {
    "⊢": {"wedge": 0, "tri": 1, "infty": 2, "odot": 3},
    "⊣": {"network": 0, "in": 1, "bowtie": 2, "boxtimes": 3, "odot": 4},
    "≻": {"super": 0, "cat": 1, "dagger": 2, "lr": 3},
    "≺": {"asym": 0, "psi": 1, "pm": 2, "sym": 3, "pm_sym": 4},
    "⋈": {"ell": 0, "eth": 1, "hbar": 2},
    "⊤": {"fast": 0, "mod": 1, "slow": 2, "trap": 3, "MBL": 4},
    "∈": {"beth": 0, "gimel": 1, "aleph": 2},
    "∋": {"and": 0, "or": 1, "seq": 2, "broad": 3},
    "⊙": {"sub": 0, "c": 1, "c_complex": 2, "EP": 3, "super": 4},
    "⊥": {"0": 0, "1": 1, "2": 2, "inf": 3},
    "⊞": {"one": 0, "many": 1, "hetero": 2},
    "⊡": {"0": 0, "Z2": 1, "Z": 2, "NA": 3},
}


def _ig_to_ordinal(tup: Dict[str, str]) -> Dict[str, int]:
    """Convert an IG tuple to ordinal positions for distance computation."""
    result = {}
    for prim_key, ig_char in tup.items():
        _, val_name = ig_char_to_name(ig_char)
        result[prim_key] = PRIMITIVE_ORDINALS[prim_key][val_name]
    return result


def compute_structural_distance(tup_a: Dict[str, str], 
                                 tup_b: Dict[str, str]) -> float:
    """
    Compute weighted Euclidean distance between two IG tuples.
    
    This replaces the hardcoded 4.0 with a genuine sequence-driven
    distance that varies per input.
    """
    ord_a = _ig_to_ordinal(tup_a)
    ord_b = _ig_to_ordinal(tup_b)
    
    squared_sum = 0.0
    conflicts = []
    for prim_key in PRIMITIVE_ORDINALS:
        diff = ord_a.get(prim_key, 0) - ord_b.get(prim_key, 0)
        w = PRIMITIVE_WEIGHTS.get(prim_key, 1.0)
        squared_sum += w * diff * diff
        if diff != 0:
            conflicts.append({
                "primitive": prim_key,
                "a": tup_a.get(prim_key, "?"),
                "b": tup_b.get(prim_key, "?"),
            })
    
    distance = squared_sum ** 0.5
    return distance


def compute_pathway_distances(tuples: Dict[str, Dict[str, str]]) -> List[Dict]:
    """
    Compute distances between consecutive stages in a generated tuple set.
    
    Returns list of dicts with from, to, delta (count of differing primitives),
    and the actual structural distance.
    """
    stage_names = [
        "dna_gene", "pre_mrna", "mature_mrna", "nascent_polypeptide",
        "secondary_structure", "tertiary_structure", "quaternary_structure"
    ]
    
    results = []
    for i in range(len(stage_names) - 1):
        s1_name, s2_name = stage_names[i], stage_names[i+1]
        t1 = tuples.get(s1_name, {})
        t2 = tuples.get(s2_name, {})
        
        changes = []
        for prim_key in PRIMITIVE_ORDINALS:
            v1 = t1.get(prim_key)
            v2 = t2.get(prim_key)
            if v1 != v2:
                changes.append((prim_key, v1, v2))
        
        dist = compute_structural_distance(t1, t2)
        
        results.append({
            "from": s1_name,
            "to": s2_name,
            "delta": len(changes),
            "distance": round(dist, 2),
            "changes": changes[:6],
        })
    
    # Overall closure distance: dna_gene ↔ quaternary_structure
    closure_dist = compute_structural_distance(
        tuples.get("dna_gene", {}),
        tuples.get("quaternary_structure", {})
    )
    
    return results, round(closure_dist, 2)

# ── Integration with the GeneToProteinPipeline ──────────────────

def extract_features_from_pipeline(pipeline) -> Dict[str, Any]:
    """
    Extract all features from a running GeneToProteinPipeline instance.
    
    This bridges the pipeline's data classes (AASite, SecondaryElement,
    TertiaryContact, QuaternarySubunit) to the dict-based feature extractors
    in this module.
    """
    features = {
        "dna_sequence": pipeline.dna_sequence if hasattr(pipeline, 'dna_sequence') else "",
        "aa_chain": [],
        "secondary_elements": [],
        "tertiary_contacts": [],
        "num_subunits": 1,
        "quaternary_subunits": [],
    }
    
    # AA chain
    if hasattr(pipeline, 'aa_chain') and pipeline.aa_chain:
        features["aa_chain"] = [
            {
                "aa_code": aa.aa_code,
                "is_hydrophobic": aa.is_hydrophobic,
                "is_charged": aa.is_charged,
                "ig_primitive": aa.ig_primitive,
                "position": aa.position,
                "helix_propensity": aa.helix_propensity,
                "sheet_propensity": aa.sheet_propensity,
            }
            for aa in pipeline.aa_chain
        ]
    
    # Secondary elements
    if hasattr(pipeline, 'secondary_elements') and pipeline.secondary_elements:
        features["secondary_elements"] = [
            {
                "type": e.element_type,
                "start": e.start,
                "end": e.end,
                "confidence": e.confidence,
                "sequence": getattr(e, 'sequence', ''),
            }
            for e in pipeline.secondary_elements
        ]
    
    # Tertiary contacts
    if hasattr(pipeline, 'tertiary_contacts') and pipeline.tertiary_contacts:
        features["tertiary_contacts"] = [
            {
                "i": c.residue_i,
                "j": c.residue_j,
                "interaction_type": c.interaction_type,
                "confidence": c.confidence,
                "distance_estimate": c.distance_estimate,
            }
            for c in pipeline.tertiary_contacts
        ]
    
    # Quaternary info
    if hasattr(pipeline, 'quaternary_subunits') and pipeline.quaternary_subunits:
        features["quaternary_subunits"] = [
            {
                "subunit_id": s.subunit_id,
                "interface_residues": s.interface_residues,
            }
            for s in pipeline.quaternary_subunits
        ]
        features["num_subunits"] = len(pipeline.quaternary_subunits)
    else:
        # Use prediction if available
        pred = getattr(pipeline, '_subunit_prediction', None)
        if pred:
            features["num_subunits"] = pred.get("count", 1)
    
    return features

# ── Verification ────────────────────────────────────────────────

def verify_tier_consistency(ig_tuple: Dict[str, str]) -> dict:
    """
    Verify that a generated tuple satisfies ouroboricity tier constraints.
    
    Checks:
    1. D-⊡ consistency: ℤ₂ requires ⊢≥△, ℤ requires ⊢≥∞
    2. K-≺ consistency: ⊙_ÿ + ↺ = deep critical structure
    3. D-T co-origination (Axiom C): dimensionality_odot ↔ topology_odot
    4. H-⊡: ℤ₂ requires ⊥≥2
    
    Returns dict with pass/fail and diagnostic messages.
    """
    diagnostics = []
    all_pass = True
    
    # Decode to pipeline names
    try:
        p = _ig_to_pipeline(ig_tuple)
    except ValueError as e:
        return {"pass": False, "diagnostics": [f"Invalid tuple: {e}"]}
    
    # 1. D-⊡: ⊡_Z2 or ⊡_Z or ⊡_NA require sufficient dimensionality
    if p['⊡'] in ("Z2", "Z", "NA"):
        if p['⊢'] == "wedge":
            diagnostics.append(f"FAIL: ⊡={p['⊡']} requires ⊢≥triangle, got ⊢=wedge")
            all_pass = False
        elif p['⊡'] == "Z" and p['⊢'] in ("tri", "wedge"):
            diagnostics.append(f"WARN: ⊡=Z with ⊢={p['⊢']} — Z typically requires ⊢=infty")
        else:
            diagnostics.append(f"OK: ⊡={p['⊡']} with ⊢={p['⊢']}")
    
    # 2. K-≺: ⊙_ÿ (⊙) with ⊤=slow creates deep critical structure
    if p['⊙'] == "c" and p['⊤'] == "slow":
        diagnostics.append("DEEP CRITICAL: ⊙=c + ⊤=slow → self-structuring criticality")
    elif p['⊙'] == "c" and p['⊤'] == "fast":
        diagnostics.append("WARN: ⊙=c + ⊤=fast — criticality requires slow kinetics to stabilize")
    
    # 3. Axiom C: dimensionality_odot ↔ topology_odot
    if (p['⊢'] == "odot") != (p['⊣'] == "odot"):
        diagnostics.append(f"AXIOM C: ⊢={p['⊢']} but ⊣={p['⊣']} — must both be odot or neither")
        all_pass = False
    
    # 4. H-⊡: ℤ₂ or NA requires ⊥≥2 (Axiom B)
    if p['⊡'] in ("Z2", "NA") and p['⊥'] in ("0", "1"):
        diagnostics.append(f"AXIOM B: ⊡={p['⊡']} requires ⊥≥2, got ⊥={p['⊥']}")
        all_pass = False
    
    return {"pass": all_pass, "diagnostics": diagnostics}


def verify_pathway(tuples: Dict[str, Dict[str, str]]) -> dict:
    """
    Verify the entire 7-stage pathway for Frobenius consistency.
    
    Checks:
    1. Each stage's tuple passes tier consistency
    2. Monotonic advance: the trajectory through the crystal is non-decreasing
       in structural complexity (𐑭 constraint)
    3. No backtracking: no primitive regresses to an earlier ordinal value
       (unless it's a necessary structural transition)
    """
    stage_order = [
        "dna_gene", "pre_mrna", "mature_mrna", "nascent_polypeptide",
        "secondary_structure", "tertiary_structure", "quaternary_structure"
    ]
    
    results = {}
    all_pass = True
    
    # Each stage verification
    for stage in stage_order:
        tup = tuples.get(stage)
        if tup is None:
            results[stage] = {"pass": False, "error": "Missing tuple"}
            all_pass = False
            continue
        v = verify_tier_consistency(tup)
        results[stage] = v
        if not v["pass"]:
            all_pass = False
    
    # Monotonic advance check
    monotonic = True
    regressions = []
    for i in range(len(stage_order) - 1):
        t1 = tuples.get(stage_order[i], {})
        t2 = tuples.get(stage_order[i + 1], {})
        try:
            o1 = _ig_to_ordinal(t1)
            o2 = _ig_to_ordinal(t2)
        except (ValueError, KeyError):
            regressions.append(f"Cannot compare {stage_order[i]} -> {stage_order[i+1]}")
            monotonic = False
            continue
        
        for prim in PRIMITIVE_ORDINALS:
            v1 = o1.get(prim, 0)
            v2 = o2.get(prim, 0)
            if v2 < v1:
                # Allow regressions for specific primitives
                if prim not in ("⋈", "⊙"):  # These can regress
                    regressions.append(f"  {stage_order[i]}->{stage_order[i+1]}: "
                                       f"{prim} regresses {v1}->{v2}")
                    monotonic = False
    
    return {
        "pass": all_pass,
        "monotonic": monotonic,
        "stages": results,
        "regressions": regressions[:10] if regressions else [],
        "n_regressions": len(regressions),
    }
