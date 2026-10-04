#!/usr/bin/env python3
"""
hiv_arms_race.py — HIV gp120 surface-antigen escape prediction + counter-antibody.

The friend's question: HIV mutates its surface peptide so fast the body never
catches up. Can we (a) pre-build a cocktail of antibodies against the
predictable escape space, and (b) predict WHICH peptide it will mutate into
AND the corresponding binding antibody?

This driver runs the red-hot_rebis kernel for real:
  Phase 1  WT gp120 C4 epitope -> 12-primitive activation profile -> CDR3
  Phase 2  Full 570-mutant single-point landscape (30 pos x 19 AAs):
             escape score = primitives CLEARED from the CDR's recognition set
                            (SerpentRod activation diff, live re-fold per mutant)
             viability    = codon-level MutationReport (genetic_code B4 lattice)
  Phase 3  Top predicted escape peptide -> design_full_antibody (the binder)
  Phase 4  Cocktail vector DNA = WT-CDR3 + escape-CDR3 (+linker),
           run through the live 7-stage gene pipeline
Output: data/hiv_arms_race_results.json + console report.
"""
import sys, os, json, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import rhr_p4rky.belnap as belnap
from rhr_p4rky.antibody_designer import (
    analyze_epitope, design_cdr, design_full_antibody,
    CODON_TABLE, PRIMITIVE_TO_AA_1L, COMPLEMENTARY, VIRAL_EPITOPES)
import rhr_p4rky.genetic_code as gc
from rhr_p4rky.serpent_rod import SerpentRod

AA20 = "ACDEFGHIKLMNPQRSTVWY"
RISK_ORDER = {"low": 0, "moderate": 1, "high": 2, "critical": 3}

def P(msg):
    print(msg, flush=True)

def quiet_analysis(seq, name):
    """SerpentRod activation profile without console noise."""
    rna = "".join(CODON_TABLE.get(a, "NNN") for a in seq)
    sr = SerpentRod(rna, name=name)
    res = sr.report()
    act = {}
    pat = res.get("activation_pattern", [])
    for i, aa_full in enumerate(pat):
        if i >= len(seq):
            break
        pf = aa_full.get("primitive", "")
        pshort = pf.split(" (")[1].rstrip(")") if "(" in pf else pf
        act[i] = pshort
    return {
        "seq": seq, "rna": rna,
        "activations": act,
        "activated_primitives": sorted(set(act.values())),
        "winding": res.get("winding_number", 0),
        "contacts": len(res.get("contacts", [])),
        "frob": bool(res.get("frobenius_verified", False)),
        "conf": float(res.get("confidence", 0.0)),
        "dG": res.get("folding_dG", res.get("fold_dG", None)),
    }

def main():
    t0 = time.time()
    wt_info = VIRAL_EPITOPES["HIV_gp120_C4"]
    WT = wt_info["seq"]
    P("=" * 70)
    P("HIV gp120 C4 — ARMS RACE: escape prediction + counter-antibody")
    P("=" * 70)
    P(f"WT epitope : {WT}  ({len(WT)} AA)")
    P(f"Source     : {wt_info['desc']}")

    # ── PHASE 1: WT epitope + first antibody ─────────────────────────
    P("\n── PHASE 1: WT epitope analysis + antibody design ──")
    wt = quiet_analysis(WT, "epitope_WT_C4")
    P(f"WT primitives: {wt['activated_primitives']}")
    P(f"WT winding={wt['winding']}  contacts={wt['contacts']}  frob={wt['frob']}  conf={wt['conf']:.2f}")

    wt_an = analyze_epitope(WT, "HIV_gp120_C4_WT")
    wt_cdr = design_cdr(wt_an, cdr_length=12, cdr_name="VH_CDR3")
    wt_full = design_full_antibody(wt_an, chain_type="VH")
    cdr3_wt = wt_cdr["cdr_sequence"]
    cdr_prims_wt = set(wt_cdr["complementary_primitives"])
    P(f"\nWT CDR3 = {cdr3_wt}   engages primitives: {sorted(cdr_prims_wt)}")

    # ── PHASE 2: full single-point escape landscape ──────────────────
    P("\n── PHASE 2: mutation landscape (570 single-point mutants) ──")
    P("Scoring: escape = CDR-engaged primitives CLEARED by the mutant (live re-fold)")
    P("         viability = codon-level B4 MutationReport (genetic_code)")
    landscape = []
    n_escape = 0
    for i, orig in enumerate(WT):
        for new in AA20:
            if new == orig:
                continue
            mut = WT[:i] + new + WT[i + 1:]
            ma = quiet_analysis(mut, f"mut{i}_{new}")
            cleared = [p for p in wt["activations"].get(i, "") and [wt["activations"][i]]
                       if p in cdr_prims_wt and p != ma["activations"].get(i)]
            # also: any primitive the CDR engages anywhere in the epitope that this
            # mutation removes from the global set (contact anywhere on the patch)
            global_cleared = [p for p in (set(wt["activated_primitives"]) & cdr_prims_wt)
                              if p not in set(ma["activated_primitives"])]
            rep = gc.analyze_aa_mutation(orig, new)
            # BINDER GAP: how much the current CDR is broken by this mutant.
            #   loss   = CDR-engaged primitives that lost their epitope target
            #   unmet  = new epitope primitives whose complement the CDR does not carry
            loss = cdr_prims_wt - set(ma["activated_primitives"])
            new_prims = set(ma["activated_primitives"]) - set(wt["activated_primitives"])
            unmet = sorted(p for p in new_prims if COMPLEMENTARY.get(p) not in cdr_prims_wt)
            gap = len(loss) + len(unmet)
            escape = gap
            viable = RISK_ORDER.get(rep.risk_class, 1) <= 1  # low|moderate tolerated
            if escape > 0 and viable:
                n_escape += 1
            landscape.append({
                "pos": i, "wt": orig, "mut": new,
                "seq": mut,
                "pos_primitive_wt": wt["activations"].get(i),
                "pos_primitive_mut": ma["activations"].get(i),
                "cleared_local": sorted(set(cleared)),
                "cleared_global": sorted(set(global_cleared)),
                "primitives_mut": ma["activated_primitives"],
                "n_prims_mut": len(ma["activated_primitives"]),
                "winding_mut": ma["winding"],
                "frob_mut": ma["frob"],
                "conf_mut": ma["conf"],
                "risk_class": rep.risk_class,
                "risk_score": rep.risk_score,
                "primitive_changed": rep.primitive_changed,
                "stratum_crossing": rep.stratum_crossing,
                "viable": viable,
                "loss": sorted(loss),
                "unmet": unmet,
                "escape": escape,
            })
    landscape.sort(key=lambda r: (-r["escape"], -len(r["unmet"]),
                                   -r["risk_score"] if r["viable"] else 0,
                                   r["pos"], r["mut"]))
    P(f"Scanned 570 mutants in {time.time()-t0:.1f}s")
    P(f"Escape-capable (clears CDR primitive, codon-viable): {n_escape}")
    risk_counts = {}
    for r in landscape:
        risk_counts[r["risk_class"]] = risk_counts.get(r["risk_class"], 0) + 1
    P(f"Risk-class census: {risk_counts}")
    top = landscape[:8]
    P("\nTOP PREDICTED ESCAPES:")
    for r in top:
        P(f"  pos {r['pos']:2d} {r['wt']}->{r['mut']}  "
          f"gap={r['escape']}  loss={r['loss'] or '-'}  unmet={r['unmet'] or '-'}  "
          f"risk={r['risk_class']}({r['risk_score']})  "
          f"winding={r['winding_mut']}  frob={r['frob_mut']}  conf={r['conf_mut']:.2f}")
        P(f"     seq: {r['seq']}")

    best = landscape[0]
    P(f"\nPREDICTED ESCAPE: position {best['pos']} {best['wt']}->{best['mut']}")
    P(f"Escape peptide: {best['seq']}")

    # ── PHASE 3: the binder for the predicted escape ─────────────────
    P("\n── PHASE 3: counter-antibody against the predicted escape ──")
    esc_an = analyze_epitope(best["seq"], "HIV_gp120_C4_ESCAPE")
    esc_cdr = design_cdr(esc_an, cdr_length=12, cdr_name="VH_CDR3")
    esc_full = design_full_antibody(esc_an, chain_type="VH")
    cdr3_esc = esc_cdr["cdr_sequence"]
    P(f"\nEscape CDR3 = {cdr3_esc}   engages: {sorted(esc_cdr['complementary_primitives'])}")
    P(f"Escape VH full: {esc_full['full_sequence']}  (frob={'OK' if esc_full.get('frobenius_verified') else 'FAIL'}, conf={esc_full.get('confidence',0):.2f})")

    # ── PHASE 4: the cocktail vector (idea (a)) ──────────────────────
    P("\n── PHASE 4: multi-epitope cocktail vector ──")
    LINKER = "GGGGS"
    cocktail = cdr3_wt + LINKER + cdr3_esc
    P(f"Vector CDR payload: [{cdr3_wt}] {LINKER} [{cdr3_esc}]  =  {cocktail}  ({len(cocktail)} AA)")
    vector_rna = "".join(CODON_TABLE.get(a, "NNN") for a in cocktail)
    vector_dna = vector_rna.replace("U", "T")
    P(f"Vector DNA ({len(vector_dna)} nt):")
    for j in range(0, len(vector_dna), 60):
        P(f"  {vector_dna[j:j+60]}")
    with open(os.path.join(ROOT, "hiv_cocktail_vector.dna"), "w") as f:
        f.write(vector_dna + "\n")
    P("Written: hiv_cocktail_vector.dna")

    # ── save results ─────────────────────────────────────────────────
    out = {
        "wt": {"seq": WT, "primitives": wt["activated_primitives"],
               "winding": wt["winding"], "cdr3": cdr3_wt,
               "cdr3_primitives": sorted(cdr_prims_wt),
               "vh_full": wt_full.get("full_sequence"),
               "vh_frob": wt_full.get("frobenius_verified"),
               "vh_conf": wt_full.get("confidence")},
        "landscape": landscape,
        "predicted_escape": best,
        "escape_antibody": {"cdr3": cdr3_esc,
                            "cdr3_primitives": sorted(esc_cdr["complementary_primitives"]),
                            "vh_full": esc_full.get("full_sequence"),
                            "vh_frob": esc_full.get("frobenius_verified"),
                            "vh_conf": esc_full.get("confidence")},
        "cocktail_vector": {"cdrs": [cdr3_wt, cdr3_esc], "linker": LINKER,
                            "payload": cocktail, "dna": vector_dna},
        "wall_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(ROOT, "data", "hiv_arms_race_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    P(f"\nSaved: data/hiv_arms_race_results.json   (total {time.time()-t0:.1f}s)")

if __name__ == "__main__":
    main()
