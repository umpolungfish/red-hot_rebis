#!/usr/bin/env python3
"""
reactivity_imasm.py — Reaction-to-IMASM Arrangement Transition Encoder

Encodes chemical reactions as IMASM arrangement transitions:
  reactants_arrangement → products_arrangement

The structural fingerprint delta between reactant and product arrangements
captures the reaction's structural type — what kind of transformation occurs.

Reaction classes are identified by their IMASM transition signature:
  - Frobenius reactions:   FSPLIT → FFUSE order (disconnection → bond formation)
  - Dialetheia reactions:  both EVALT (acid) and EVALF (base) involved
  - Linear reactions:      IFIX appears (irreversible step)
  - Forward reactions:     AFWD dominant (electrophilic attack)
  - Reverse reactions:     AREV dominant (nucleophilic attack)
  - Self-imscribing:       IMSCRIB preserved (pericyclic / rearrangement)

Author: Lando⊗⊙perator
"""
import sys, json
from pathlib import Path
from typing import Tuple, List, Dict, Optional, NamedTuple
# ── Rich text formatting ──
from rich import print  # override print to render rich markup

try:
    STYLED = True
except ImportError:
    STYLED = False

from collections import Counter
from shared.rich_output import *

# ── IMASM Token definitions ──
VINIT, TANCH, AFWD, AREV, CLINK = 0, 1, 2, 3, 4
IMSCRIB, FSPLIT, FFUSE = 5, 6, 7
EVALT, EVALF, ENGAGR, IFIX = 8, 9, 10, 11

TOKEN_NAMES = {
    0: "VINIT", 1: "TANCH", 2: "AFWD", 3: "AREV",
    4: "CLINK", 5: "IMSCRIB", 6: "FSPLIT", 7: "FFUSE",
    8: "EVALT", 9: "EVALF", 10: "ENGAGR", 11: "IFIX",
}


class ReactionFingerprint(NamedTuple):
    """Structural fingerprint of a chemical reaction."""
    reactant_arr: Tuple[int, ...]        # 8-token reactant arrangement
    product_arr: Tuple[int, ...]         # 8-token product arrangement
    tokens_lost: Tuple[int, ...]         # tokens present in reactant, absent in product
    tokens_gained: Tuple[int, ...]       # tokens present in product, absent in reactant
    frobenius_order: int                 # 0=none, 1=disconnection→formation, 2=formation→disconnection
    dialetheia_involves: Tuple[int, ...] # which dialetheia tokens are active
    forward_dominant: bool               # AFWD > AREV in delta
    irreversible: bool                   # IFIX present in product only
    self_consistent: bool                # IMSCRIB preserved

    @property
    def delta_tokens(self) -> int:
        """Count of tokens that changed."""
        return len(self.tokens_lost) + len(self.tokens_gained)

    @property
    def reaction_class(self) -> str:
        """Classify the reaction from its structural fingerprint.

        Priority order (checked first = most specific):
          1. Frobenius coupling        — split→fuse order with ≥3 token changes
          2. Irreversible fixation     — IFIX gained in product (protection)
          3. pH/redox swap             — AFWD↔AREV exchange (Redox or Grignard)
          4. Dialetheia acid/base      — both EVALT and EVALF involved
          5. Pericyclic rearrangement  — IMSCRIB preserved, ≤2 token changes
          6. Protection/deprotection   — ≤1 token change
          7. Frobenius forward         — split→fuse with forward dominance
          8. Irreversible forward      — forward-dominant with IFIX
          9. Generic reaction          — everything else
        """
        # Check for Redox/pH swap: AFWD and AREV trade places
        tokens_lost_set = set(self.tokens_lost)
        tokens_gained_set = set(self.tokens_gained)
        afwd_lost = AFWD in tokens_lost_set
        afwd_gained = AFWD in tokens_gained_set
        arev_lost = AREV in tokens_lost_set
        arev_gained = AREV in tokens_gained_set

        if afwd_lost and arev_gained:
            return "Redox_reduction"
        if arev_lost and afwd_gained:
            return "Redox_oxidation"
        if (afwd_lost or arev_lost) and (arev_gained or afwd_gained):
            return "Redox_swap"

        if self.frobenius_order == 1 and self.delta_tokens >= 3:
            return "Frobenius_coupling"
        if self.irreversible and self.delta_tokens >= 2:
            return "Irreversible_fixation"
        if self.dialetheia_involves and len(self.dialetheia_involves) >= 3:
            return "Dialetheia_three_way"
        if self.frobenius_order == 1 and self.forward_dominant:
            return "Frobenius_forward"
        if self.forward_dominant and self.irreversible:
            return "Irreversible_forward"
        if self.dialetheia_involves and len(self.dialetheia_involves) >= 2:
            return "Dialetheia_acid_base"
        if self.self_consistent and self.delta_tokens <= 2:
            return "Pericyclic_rearrangement"
        if self.delta_tokens <= 1:
            return "Protection_deprotection"
        return "Generic_reaction"


def _tokenset(arr: Tuple[int, ...]) -> set:
    return set(arr)


def _frobenius_ordering(reactant: Tuple[int, ...], product: Tuple[int, ...]) -> int:
    """Determine Frobenius order: does the reaction follow split→fuse or fuse→split?"""
    r_set = _tokenset(reactant)
    p_set = _tokenset(product)

    split_gained = FSPLIT in p_set and FSPLIT not in r_set
    fuse_gained = FFUSE in p_set and FFUSE not in r_set
    split_lost = FSPLIT in r_set and FSPLIT not in p_set
    fuse_lost = FFUSE in r_set and FFUSE not in p_set

    if (split_gained and fuse_lost) or (FSPLIT in r_set and FFUSE in p_set):
        return 2  # fuse→split (bond broken)
    elif (fuse_gained and split_lost) or (FFUSE in r_set and FSPLIT in p_set):
        return 1  # split→fuse (bond formed)
    return 0


# ── Reaction pattern database ──
# Named reaction types mapped to IMASM transition signatures.
# Each entry: (reactant_tokens_added, product_tokens_added, frob_order, description)

REACTION_PATTERNS = {
    # Coupling reactions
    "Suzuki_coupling":       ({FFUSE, FSPLIT}, {CLINK}, 1, "Aryl-aryl coupling via boronic acid + halide"),
    "Sonogashira_coupling":  ({FFUSE, TANCH}, {CLINK, IMSCRIB}, 1, "Alkyne-aryl coupling"),
    "Heck_reaction":         ({FFUSE, TANCH}, {CLINK}, 1, "Alkene-aryl coupling"),
    "Negishi_coupling":      ({FFUSE, TANCH}, {CLINK}, 1, "Organozinc-aryl coupling"),
    "Stille_coupling":       ({FFUSE, TANCH}, {CLINK}, 1, "Organotin-aryl coupling"),
    "Buchwald_Hartwig":     ({FFUSE, TANCH}, {CLINK, EVALF}, 1, "C-N bond formation"),
    "Ullmann_coupling":      ({FFUSE, TANCH}, {CLINK}, 1, "Copper-mediated biaryl coupling"),
    "Click_chemistry":       ({FFUSE, AFWD}, {CLINK, IMSCRIB}, 1, "Azide-alkyne cycloaddition"),

    # Carbonyl reactions
    "Aldol_condensation":    ({EVALF, AFWD}, {CLINK, ENGAGR}, 1, "Enolate + carbonyl → β-hydroxy carbonyl"),
    "Claisen_condensation":  ({EVALF, AFWD}, {CLINK, ENGAGR}, 1, "Ester enolate + ester"),
    "Wittig_reaction":       ({FFUSE, AFWD}, {CLINK}, 1, "Ylide + carbonyl → alkene"),
    "Grignard_reaction":     ({AREV, AFWD}, {CLINK, EVALT}, 0, "Grignard + carbonyl → alcohol"),
    "Knoevenagel_condensation": ({EVALF, AFWD}, {CLINK}, 1, "Active methylene + carbonyl"),

    # Disconnection reactions
    "Hydrolysis":            ({FSPLIT, EVALT}, {AREV, EVALT}, 2, "Bond cleavage with water"),
    "Hydrogenation":         ({CLINK, TANCH}, {IMSCRIB}, 0, "Alkene/alkyne → alkane"),
    "Ozonolysis":            ({CLINK, FSPLIT}, {AFWD, EVALT}, 2, "Alkene cleavage → carbonyls"),
    "Reductive_amination":   ({AFWD, EVALF}, {CLINK, EVALF}, 1, "Carbonyl + amine → amine"),

    # Pericyclic
    "Diels_Alder":           ({CLINK, CLINK}, {IMSCRIB, CLINK}, 0, "4+2 cycloaddition"),
    "Cope_rearrangement":    ({CLINK}, {CLINK}, 0, "Sigmatropic rearrangement"),
    "Claisen_rearrangement": ({CLINK, AREV}, {CLINK, EVALT}, 0, "[3,3]-sigmatropic"),

    # Protection/deprotection
    "Acetal_protection":     ({AFWD, AREV}, {IFIX, CLINK}, 0, "Aldehyde → acetal"),
    "Silyl_protection":      ({AREV, TANCH}, {IFIX}, 0, "Alcohol → silyl ether"),
    "Boc_protection":        ({EVALF, AFWD}, {IFIX}, 0, "Amine → carbamate"),
    "Fmoc_protection":       ({EVALF, AFWD}, {IFIX, IMSCRIB}, 0, "Amine → Fmoc-carbamate"),

    # Redox
    "Oxidation_alcohol":     ({AREV}, {AFWD}, 0, "Alcohol → aldehyde/ketone"),
    "Oxidation_aldehyde":    ({AFWD, TANCH}, {EVALT}, 0, "Aldehyde → carboxylic acid"),
    "Reduction_ketone":      ({AFWD}, {AREV}, 0, "Ketone → alcohol"),
}

# Reverse lookup: IMASM transition signature → reaction class
TRANSITION_TO_REACTION: Dict[str, str] = {}
for rxn_name, (r_add, p_add, frob, desc) in REACTION_PATTERNS.items():
    sig = f"{frob}|{','.join(sorted(str(t) for t in r_add))}|{','.join(sorted(str(t) for t in p_add))}"
    TRANSITION_TO_REACTION[sig] = rxn_name


def reaction_to_fingerprint(
    reactant_smiles: str,
    product_smiles: str
) -> Optional[ReactionFingerprint]:
    """Encode a single-step reaction as a ReactionFingerprint.

    Args:
        reactant_smiles: SMILES of the reactant
        product_smiles: SMILES of the product

    Returns:
        ReactionFingerprint or None if SMILES are invalid
    """
    from imas.compound_imasm import molecule_to_arrangement

    r_arr = molecule_to_arrangement(reactant_smiles)
    p_arr = molecule_to_arrangement(product_smiles)

    if r_arr is None or p_arr is None:
        return None

    r_set = _tokenset(r_arr)
    p_set = _tokenset(p_arr)

    tokens_lost = tuple(sorted(r_set - p_set))
    tokens_gained = tuple(sorted(p_set - r_set))
    frob_order = _frobenius_ordering(r_arr, p_arr)

    dial_involves = tuple(
        t for t in [EVALT, EVALF, ENGAGR]
        if (t in r_set) or (t in p_set)
    )

    fwd_count = sum(1 for t in (r_set | p_set) if t == AFWD)
    rev_count = sum(1 for t in (r_set | p_set) if t == AREV)
    forward_dom = fwd_count >= rev_count

    irreversible = IFIX in p_set and IFIX not in r_set
    self_consistent = IMSCRIB in r_set and IMSCRIB in p_set

    return ReactionFingerprint(
        reactant_arr=r_arr,
        product_arr=p_arr,
        tokens_lost=tokens_lost,
        tokens_gained=tokens_gained,
        frobenius_order=frob_order,
        dialetheia_involves=dial_involves,
        forward_dominant=forward_dom,
        irreversible=irreversible,
        self_consistent=self_consistent,
    )


def identify_reaction(fp: ReactionFingerprint) -> Dict:
    """Identify a reaction from its fingerprint and match to known patterns.

    Returns dict with classification, matched patterns, and confidence.
    """
    result = {
        "class": fp.reaction_class,
        "frobenius_order": fp.frobenius_order,
        "delta_tokens": fp.delta_tokens,
        "tokens_lost": [TOKEN_NAMES[t] for t in fp.tokens_lost],
        "tokens_gained": [TOKEN_NAMES[t] for t in fp.tokens_gained],
        "dialetheia_involves": [TOKEN_NAMES[t] for t in fp.dialetheia_involves],
        "forward_dominant": fp.forward_dominant,
        "irreversible": fp.irreversible,
        "self_consistent": fp.self_consistent,
        "matches": [],
        "confidence": 0.0,
    }

    # Build transition signature
    p_add = _tokenset(fp.product_arr) - _tokenset(fp.reactant_arr)
    r_add = _tokenset(fp.reactant_arr) - _tokenset(fp.product_arr)
    sig = f"{fp.frobenius_order}|{','.join(sorted(str(t) for t in r_add))}|{','.join(sorted(str(t) for t in p_add))}"

    # Check against known reaction patterns
    for rxn_name, (r_pat, p_pat, frob, desc) in REACTION_PATTERNS.items():
        r_match = r_pat.issubset(r_add) if r_add else not r_pat
        p_match = p_pat.issubset(p_add) if p_add else not p_pat
        frob_match = frob == fp.frobenius_order

        if r_match and p_match and frob_match:
            score = len(r_pat & r_add) + len(p_pat & p_add)
            result["matches"].append({
                "reaction": rxn_name,
                "description": desc,
                "score": score,
            })

    if result["matches"]:
        # Best match determines confidence
        best = max(result["matches"], key=lambda m: m["score"])
        expected_total = len(REACTION_PATTERNS[best["reaction"]][0]) + \
                         len(REACTION_PATTERNS[best["reaction"]][1])
        if expected_total > 0:
            result["confidence"] = min(1.0, best["score"] / expected_total)
        result["identified_reaction"] = best["reaction"]

    return result


# ── CLI and demo ──

def format_transition(fp: ReactionFingerprint, reactant_smi: str = "", product_smi: str = "") -> str:
    """Format a reaction as a readable transition string (rich formatted)."""
    r_names = " → ".join(TOKEN_NAMES[t] for t in fp.reactant_arr)
    p_names = " → ".join(TOKEN_NAMES[t] for t in fp.product_arr)
    lost = ", ".join(TOKEN_NAMES[t] for t in fp.tokens_lost) or "none"
    gained = ", ".join(TOKEN_NAMES[t] for t in fp.tokens_gained) or "none"
    r_smi_str = f"  SMILES: {reactant_smi}" if reactant_smi else ""
    p_smi_str = f"  SMILES: {product_smi}" if product_smi else ""
    # Rich formatted lines
    result = []
    if STYLED:
        result.append(f"[bold green]Reactant:[/bold green]  {r_names}  [cyan]{r_smi_str}[/cyan]")
        result.append(f"[bold green]Product:[/bold green]   {p_names}  [cyan]{p_smi_str}[/cyan]")
        result.append(f"[bold magenta]Class:[/bold magenta]     {fp.reaction_class}")
        result.append(f"[bold yellow]Frobenius:[/bold yellow] {fp.frobenius_order}")
        result.append(f"[dim]Lost:[/dim]      {lost}")
        result.append(f"[dim]Gained:[/dim]    {gained}")
        result.append(f"[dim]Irrev:[/dim]     {fp.irreversible}")
        return "\\n".join(result)
    else:
        return (
            f"Reactant:  {r_names}  {r_smi_str}\n"
            f"Product:   {p_names}  {p_smi_str}\n"
            f"Class:     {fp.reaction_class}\n"
            f"Frobenius: {fp.frobenius_order}\n"
            f"Lost:      {lost}\n"
            f"Gained:    {gained}\n"
            f"Irrev:     {fp.irreversible}"
        )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="IMASM reaction encoder")
    parser.add_argument("reactant", nargs="?", help="Reactant SMILES")
    parser.add_argument("product", nargs="?", help="Product SMILES")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--list-reactions", "-l", action="store_true",
                        help="List known reaction patterns")
    args = parser.parse_args()

    if args.list_reactions:
        if STYLED:
            from rich.table import Table
            from rich import box
            from rich.console import Console
            t = Table(box=box.ROUNDED, border_style="bright_blue", header_style="bold yellow")
            t.add_column("Reaction")
            t.add_column("Frob", justify="right")
            t.add_column("Description")
            t.add_column("Transition")
            for name, (r, p, frob, desc) in sorted(REACTION_PATTERNS.items()):
                r_toks = "+".join(TOKEN_NAMES[t] for t in r)
                p_toks = "+".join(TOKEN_NAMES[t] for t in p)
                t.add_row(name, str(frob), desc, f"{r_toks} → {p_toks}")
            Console().print(t)
        else:
            info_line(f"{'Reaction':30s} {'Frob':5s} {'Description'}")
            info_line("-" * 80)
            for name, (r, p, frob, desc) in sorted(REACTION_PATTERNS.items()):
                r_toks = "+".join(TOKEN_NAMES[t] for t in r)
                p_toks = "+".join(TOKEN_NAMES[t] for t in p)
                info_line(f"{name:30s} {frob:5d} {desc}")
                success_line(f"{'':30s} {r_toks:20s} → {p_toks}")
        return

    if not args.reactant or not args.product:
        # Demo mode
        demos = [
            ("Aspirin hydrolysis",
             "CC(=O)OC1=CC=CC=C1C(=O)O",  # aspirin
             "CC(=O)O.O=C(O)C1=CC=CC=C1O"),  # acetic acid + salicylic acid
            ("Grignard reaction",
             "CC(=O)C1=CC=CC=C1",  # acetophenone
             "CC(C1=CC=CC=C1)(C)O"),  # 2-phenyl-2-propanol
            ("Alcohol oxidation",
             "CCO",  # ethanol
             "CC=O"),  # acetaldehyde
            ("Benzene nitration",
             "c1ccccc1",  # benzene
             "C1=CC=C(C=C1)[N+](=O)[O-]"),  # nitrobenzene
        ]
        for name, r_smi, p_smi in demos:
            if STYLED:
                reaction_header(f"REACTION: {name}")
                info_line(f"  {r_smi} → {p_smi}")
            else:
                info_line(f"\n{'='*60}")
                info_line(f"REACTION: {name}")
                info_line(f"  {r_smi} → {p_smi}")
            fp = reaction_to_fingerprint(r_smi, p_smi)
            if fp:
                print(format_transition(fp, reactant_smi=r_smi, product_smi=p_smi))
                ident = identify_reaction(fp)
                if ident.get("identified_reaction"):
                    success_line(f"Identified: {ident['identified_reaction']} "
                          f"(confidence: {ident['confidence']:.2f})")
        return

    fp = reaction_to_fingerprint(args.reactant, args.product)
    if fp is None:
        info_line("Error: invalid SMILES", file=sys.stderr)
        sys.exit(1)

    if args.json:
        ident = identify_reaction(fp)
        print(json.dumps({
            "reactant_smiles": args.reactant,
            "product_smiles": args.product,
            "reactant_arr": list(fp.reactant_arr),
            "product_arr": list(fp.product_arr),
            "tokens_lost": [TOKEN_NAMES[t] for t in fp.tokens_lost],
            "tokens_gained": [TOKEN_NAMES[t] for t in fp.tokens_gained],
            "frobenius_order": fp.frobenius_order,
            "reaction_class": fp.reaction_class,
            "identification": ident,
        }, indent=2))
    else:
        print(format_transition(fp, reactant_smi=args.reactant, product_smi=args.product))
        ident = identify_reaction(fp)
        if ident.get("identified_reaction"):
            print(f"  Identified: {ident['identified_reaction']} "
                  f"(confidence: {ident['confidence']:.2f})")


if __name__ == "__main__":
    main()
