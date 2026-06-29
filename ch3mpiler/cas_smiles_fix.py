#!/usr/bin/env python3
"""Patch: add SMILES resolution to CASResolver and propagate through pipeline.

Problem: CASResolver.resolve() fetches PubChem /compound/name/{cas}/JSON but
only extracts name and formula — never requests CanonicalSMILES. So even when
a CAS number resolves, the pipeline has no SMILES for scaffold-aware CDXML output.

Fix 1: CASResolver.resolve() — add a second PubChem call to fetch SMILES
        using the same /property/CanonicalSMILES/JSON endpoint that
        resolve_name_to_smiles() already uses for name→SMILES.

Fix 2: Pipeline main() — when --cas is provided, propagate the resolved SMILES
        to resolve_and_parse_scaffold() so Pass 1 scaffold decomposition works.
"""
import re
from shared.rich_output import *


# ── Fix path: compiler.py ──
COMPILER_PATH = "/home/mrnob0dy666/imsgct/red-hot_rebis/ch3mpiler/compiler.py"
PIPELINE_PATH = "/home/mrnob0dy666/imsgct/red-hot_rebis/pipeline/reaction_pipeline.py"

with open(COMPILER_PATH) as f:
    src = f.read()

# ── Fix 1: Add SMILES fetch to CASResolver.resolve() ──
# Replace the PubChem URL from /name/{cas}/JSON to /name/{cas}/property/.../JSON
old_url = 'url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/JSON"'
new_url = 'url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/property/CanonicalSMILES,MolecularFormula,IUPACName/JSON"'

# Replace the PC_Compounds parsing with PropertyTable parsing (simpler, gets SMILES)
old_parse = '''        try:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/JSON"
            req = urllib.request.Request(url, headers={"User-Agent": "ch3mpiler/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            props = {}
            if "PC_Compounds" in data and data["PC_Compounds"]:
                for prop in data["PC_Compounds"][0].get("props", []):
                    urn = prop.get("urn", {}).get("label", "")
                    val = prop.get("value", {}).get("sval", "")
                    props[urn] = val
            name = props.get("IUPAC Name", props.get("Molecular Formula", cas))
            formula = props.get("Molecular Formula", "")
            entry = {"cas": cas, "name": name, "formula": formula, "source": "pubchem", "type_hint": ""}
            self._cache[cas] = entry
            self._save_cache()
            return entry'''

new_parse = '''        try:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/property/CanonicalSMILES,MolecularFormula,IUPACName/JSON"
            req = urllib.request.Request(url, headers={"User-Agent": "ch3mpiler/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            props = data.get("PropertyTable", {}).get("Properties", [{}])[0]
            name = props.get("IUPACName", props.get("MolecularFormula", cas))
            formula = props.get("MolecularFormula", "")
            smiles = props.get("CanonicalSMILES", "")
            entry = {"cas": cas, "name": name, "formula": formula,
                     "smiles": smiles, "source": "pubchem", "type_hint": ""}
            self._cache[cas] = entry
            self._save_cache()
            return entry'''

assert src.count(old_url) == 1 and src.count(old_parse) == 1, \
    f"Expected exactly 1 occurrence each in compiler.py. Found: url={src.count(old_url)}, parse={src.count(old_parse)}"

src = src.replace(old_url, new_url)
src = src.replace(old_parse, new_parse)

with open(COMPILER_PATH, "w") as f:
    f.write(src)

print(f"[OK] Patched {COMPILER_PATH}")
info_line("  - CASResolver.resolve() now fetches /property/CanonicalSMILES,.../JSON")
print("  - Returns 'smiles' field in addition to name, formula")

# ── Fix 2: Pipeline --cas path: propagate SMILES to scaffold parser ──
with open(PIPELINE_PATH) as f:
    psrc = f.read()

# The problem block in main():
#   if args.cas:
#       info = pipeline.compiler.resolve_and_analyze(args.cas)
#       name = info.get("cas_info", {}).get("name", args.cas)
#       ...
#       pipeline._target_smiles = args.smiles or ""    ← never gets SMILES from CAS
#       ...
#       tree = pipeline.deep_retrosynthesis(name)        ← uses NAME, never calls resolve_and_parse_scaffold

# We need to add SMILES propagation right after the name resolution.
# Find: pipeline._target_smiles = args.smiles or ""
# Replace with SMILES propagation from CAS resolver

old_smiles_assign = '            pipeline._target_smiles = args.smiles or ""'
new_smiles_assign = '''            pipeline._target_smiles = info.get("smiles", "") or args.smiles or ""'''

assert psrc.count(old_smiles_assign) == 2, \
    f"Expected 2 occurrences of the target_smiles assignment. Found: {psrc.count(old_smiles_assign)}"

psrc = psrc.replace(old_smiles_assign, new_smiles_assign)

with open(PIPELINE_PATH, "w") as f:
    f.write(psrc)

print(f"[OK] Patched {PIPELINE_PATH}")
info_line("  - --cas path now passes SMILES to resolve_and_parse_scaffold()")
print("  - Pipeline._target_smiles = info['smiles'] from CAS resolver")
print()
info_line("=== Usage ===")
print("  p3 pipeline/reaction_pipeline.py --cas \"<CAS_NUMBER>\" --cdxml")
print()
info_line("The CAS resolver will now:")
info_line("  1. Query PubChem by CAS number → get IUPAC Name + Formula + SMILES")
info_line("  2. Pass SMILES to ScaffoldParser → real fragment CDXML files")
info_line("  3. Cache all fields (including SMILES) in CAS_cache.json")
print()
print("If the CAS isn't in PubChem, it falls back gracefully:")
info_line("  - SMILES is empty → FG-only decomposition (legacy behavior)")
info_line("  - No hard failure, no crash")
