#!/usr/bin/env python3
"""
Antibody Designer — Path 3 of the Serpent on the Rod.
Designs complementary CDR sequences for viral epitope targeting.

Author: Lando ⊗ ⊙perator
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "p4ramill_py"))
import p4ramill_py.belnap, p4ramill_py.genetics_b4, p4ramill_py.genetic_code
import importlib.util, importlib.machinery, types

pkg_dir = os.path.join(os.path.dirname(__file__), "p4ramill_py")
loader = importlib.machinery.SourceFileLoader("p4ramill_py.serpent_rod",
    os.path.join(pkg_dir, "serpent_rod.py"))
spec = importlib.util.spec_from_loader("p4ramill_py.serpent_rod", loader)
mod = importlib.util.module_from_spec(spec)
sys.modules["p4ramill_py.serpent_rod"] = mod
mod.__package__ = "p4ramill_py"
loader.exec_module(mod)
SerpentRod = mod.SerpentRod

AA_PREF = {"A":"GCU","R":"CGU","N":"AAU","D":"GAU","C":"UGU",
    "Q":"CAA","E":"GAA","G":"GGU","H":"CAU","I":"AUU","L":"UUG",
    "K":"AAA","M":"AUG","F":"UUU","P":"CCU","S":"UCU","T":"ACU","W":"UGG","Y":"UAU","V":"GUU"}

PRIM_TO_AA = {"Dimensionality":"Met","Topology":"Trp","Recognition":"Cys",
    "Parity":"Tyr","Fidelity":"Phe","Kinetics":"Ile","Granularity":"His",
    "Coupling":"Asn","Criticality":"Gln","Chirality":"Asp","Stoichiometry":"Lys","Winding":"Glu"}

ONE = {"Met":"M","Trp":"W","Cys":"C","Tyr":"Y","Phe":"F","Ile":"I",
    "His":"H","Asn":"N","Gln":"Q","Asp":"D","Lys":"K","Glu":"E"}

COMP = {"Dimensionality":"Winding","Winding":"Dimensionality",
    "Topology":"Chirality","Chirality":"Topology",
    "Recognition":"Stoichiometry","Stoichiometry":"Recognition",
    "Parity":"Fidelity","Fidelity":"Parity",
    "Kinetics":"Granularity","Granularity":"Kinetics",
    "Coupling":"Criticality","Criticality":"Coupling"}

def analyze_epitope(seq, name):
    rna = "".join(AA_PREF.get(aa,"NNN") for aa in seq)
    sr = SerpentRod(rna, name=f"ep_{name}")
    r = sr.report()
    activations = {}
    for i, ap in enumerate(r["activation_pattern"]):
        if i < len(seq):
            prim = ap["primitive"].split(" (")[1].rstrip(")") if "(" in ap["primitive"] else ap["primitive"]
            activations[i] = {"aa": seq[i], "primitive": prim}
    act_prims = set(a["primitive"] for a in activations.values())
    
    print(f"\n  EPITOPE: {name}")
    print(f"  Sequence: {seq}")
    print(f"  Activations: {len(act_prims)}/12 — {sorted(act_prims)}")
    print(f"  Frobenius: {'✓' if r['frobenius_verified'] else '✗'}")
    print(f"  Winding: {r['winding_number']}")
    return {"seq": seq, "activations": activations, "activated_prims": list(act_prims), "sr": r}

def design_cdr(ep_analysis, length=12):
    act = ep_analysis["activated_prims"]
    cdr_aas = []
    cdr_prims = []
    
    for prim in act:
        if prim in COMP:
            c_prim = COMP[prim]
            c_aa = PRIM_TO_AA.get(c_prim)
            if c_aa:
                cdr_aas.append(c_aa)
                cdr_prims.append(c_prim)
    
    fw = ["Gly","Ser","Thr","Ala","Val"]
    while len(cdr_aas) < length:
        cdr_aas.append(fw[len(cdr_aas)%len(fw)])
        cdr_prims.append("framework")
    cdr_aas = cdr_aas[:length]
    cdr_prims = cdr_prims[:length]
    
    cdr_one = "".join(ONE.get(aa,"X") for aa in cdr_aas)
    cdr_rna = "".join(AA_PREF.get(aa,"NNN") for aa in cdr_aas)
    
    sr = SerpentRod(cdr_rna, name="cdr")
    r = sr.report()
    
    print(f"\n  DESIGNED CDR (len={length}):")
    print(f"  Sequence: {cdr_one}")
    for i,(aa,pr) in enumerate(zip(cdr_aas,cdr_prims)):
        print(f"    {i}: {aa} ({ONE.get(aa,'X')}) → {pr}")
    print(f"  Winding: {r['winding_number']} B4 loops")
    print(f"  Contacts: {len(r['contacts'])}")
    print(f"  Frobenius: {'✓' if r['frobenius_verified'] else '✗'}")
    
    return {"seq": cdr_one, "rna": cdr_rna, "comp": cdr_aas, "sr": r}

# ── TEST ON VIRAL TARGETS ──────────────────────────────────────────

targets = {
    "SARS-CoV-2_RBD_binding": "KVGGNYNYLYRLFRKSNLKPFERDIST",
    "HIV_gp120_CD4_loop": "FYCNSTQLFNSTWEGNCTWNSTW",
    "Influenza_HA_stem": "WLLWISFAISCFLLCVVLLGF",
    "HPV_L1_capsid": "YIKVSGQARVHTFAGTSGDAVAP",
}

print("="*70)
print("SERPENT ON THE ROD — ANTIBODY DESIGN PIPELINE")
print("="*70)

results = {}
for name, seq in targets.items():
    print(f"\n{'#'*60}")
    print(f"TARGET: {name}")
    print(f"{'#'*60}")
    ep = analyze_epitope(seq, name)
    cdr = design_cdr(ep, length=12)
    results[name] = {"epitope": seq, "analysis": ep, "cdr": cdr}

print(f"\n\n{'='*70}")
print("ANTIBODY DESIGN SUMMARY")
print(f"{'='*70}")
for name, r in results.items():
    c = r["cdr"]
    ep = r["analysis"]
    print(f"\n{name}:")
    print(f"  Epitope: {r['epitope']}")
    print(f"  Epitope activations: {len(ep['activated_prims'])}/12")
    print(f"  CDR3 designed: {c['seq']}")
    print(f"  CDR Frobenius: {'✓' if c['sr']['frobenius_verified'] else '✗'}")
    print(f"  CDR Contacts: {len(c['sr']['contacts'])}")

with open("/home/mrnob0dy666/p4rakernel/antibody_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to antibody_results.json")
