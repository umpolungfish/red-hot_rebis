#!/usr/bin/env python3
"""
Antibody Designer v2 — Fixed encoding, proper CDR generation.
Path 3: Direct antibody design from viral epitopes.

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

# One-letter code mappings
AA_CODON = {"A":"GCU","R":"CGU","N":"AAU","D":"GAU","C":"UGU",
    "Q":"CAA","E":"GAA","G":"GGU","H":"CAU","I":"AUU","L":"UUG",
    "K":"AAA","M":"AUG","F":"UUU","P":"CCU","S":"UCU","T":"ACU","W":"UGG","Y":"UAU","V":"GUU"}

# 12↔12 bijection
PRIM_TO_AA = {"Dimensionality":"M","Topology":"W","Recognition":"C",
    "Parity":"Y","Fidelity":"F","Kinetics":"I","Granularity":"H",
    "Coupling":"N","Criticality":"Q","Chirality":"D","Stoichiometry":"K","Winding":"E"}

COMP = {"Dimensionality":"Winding","Winding":"Dimensionality",
    "Topology":"Chirality","Chirality":"Topology",
    "Recognition":"Stoichiometry","Stoichiometry":"Recognition",
    "Parity":"Fidelity","Fidelity":"Parity",
    "Kinetics":"Granularity","Granularity":"Kinetics",
    "Coupling":"Criticality","Criticality":"Coupling"}

def analyze(seq, name):
    rna = "".join(AA_CODON.get(aa,"NNN") for aa in seq)
    sr = SerpentRod(rna, name=f"ep_{name[:12]}")
    r = sr.report()
    act = {}
    for i, ap in enumerate(r["activation_pattern"]):
        if i < len(seq):
            prim = ap["primitive"].split(" (")[1].rstrip(")") if "(" in ap["primitive"] else ap["primitive"]
            act[i] = {"aa": seq[i], "prim": prim}
    prims = set(a["prim"] for a in act.values())
    print(f"\n  [{name}] Epitope: {seq}")
    print(f"    Primitives: {sorted(prims)} ({len(prims)}/12)")
    print(f"    Frobenius: {'✓' if r['frobenius_verified'] else '✗'}")
    print(f"    Wind: {r['winding_number']} Contacts: {len(r['contacts'])}")
    return {"seq":seq, "act":act, "prims":list(prims), "sr":r}

def design_cdr(ep, min_len=12):
    """Design CDR from epitope primitives using complementarity."""
    # Get complementary AAs for each epitope primitive
    comp_aas = []
    comp_names = []
    for p in ep["prims"]:
        if p in COMP:
            cp = COMP[p]
            ca = PRIM_TO_AA.get(cp)
            if ca:
                comp_aas.append(ca)
                comp_names.append(cp)
    
    print(f"    Complementary AAs: {''.join(comp_aas)} ({len(comp_aas)})")
    
    # Pad with Gly-Ser linkers to reach minimum length
    while len(comp_aas) < min_len:
        comp_aas.append("G")
        comp_names.append("linker")
    
    cdr_seq = "".join(comp_aas[:min_len])
    cdr_rna = "".join(AA_CODON.get(aa,"GGU") for aa in cdr_seq)
    
    sr = SerpentRod(cdr_rna, name="cdr")
    r = sr.report()
    
    # Check if sequence is correct
    print(f"    CDR seq: {cdr_seq}")
    print(f"    Translated: {r['aa_sequence']}")
    print(f"    Frobenius: {'✓' if r['frobenius_verified'] else '✗'}")
    print(f"    Wind: {r['winding_number']} Contacts: {len(r['contacts'])}")
    
    if r['frobenius_verified']:
        for c in r['contacts'][:4]:
            ai = r['aa_sequence'][c['i']] if c['i'] < len(r['aa_sequence']) else '?'
            aj = r['aa_sequence'][c['j']] if c['j'] < len(r['aa_sequence']) else '?'
            print(f"      Contact: {ai}{c['i']}⟷{aj}{c['j']} {c['type']} conf={c['confidence']}")
    
    return {"seq":cdr_seq, "rna":cdr_rna, "sr":r}

# Test targets (Ab loop epitopes)
targets = {
    "SARS2_RBD": "KVGGNYNYLYRLFRKSNL",
    "SARS2_NTD": "QLTPTWRVYSTGSNVFQTRAGCL",
    "HIV_V3": "CTRPNNNTRKSIRIQRGPGRAF",
    "FLU_HA": "WLLWISFAISCFLLCVVLLGF",
    "HPV_L1": "YIKVSGQARVHTFAGTSGDAVAP",
}

print("="*70)
print("SERPENT ROD — ANTIBODY DESIGN v2")
print("="*70)

results = {}
for name, seq in targets.items():
    print(f"\n{'#'*50}")
    print(f"TARGET: {name}")
    ep = analyze(seq, name)
    cdr = design_cdr(ep, 12)
    results[name] = {"epitope":seq, "analysis":ep, "cdr":cdr}

print(f"\n\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
for n, r in results.items():
    c = r["cdr"]
    print(f"{n:12s} Ep:{r['epitope'][:20]:20s} → CDR: {c['seq']} Frobenius={'✓' if c['sr']['frobenius_verified'] else '✗'}")

with open("/home/mrnob0dy666/p4rakernel/antibody_results.json","w") as f:
    json.dump(results,f,indent=2,default=str)
print("\nSaved to antibody_results.json")
