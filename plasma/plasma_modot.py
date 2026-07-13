#!/usr/bin/env python3
"""plasma_modot.py — read a MoDoT / IG catalog entry as a plasma design.

The plasma register is not a separate substance: a catalog entry's 12-primitive
tuple IS the plasma tuple, so the plasma reading is another lossless face of the
same object (R and W and X), exactly like the chem and math faces MoDoT already
prints. This bridge loads the live IG catalog (the same file MoDoT reads), pulls
the named entry's tuple, and forges its plasma parameters.

Usage: plasma_modot.py <entry_name> [catalog_path]
"""
import sys
import os
import json

# The repo root (parent of plasma/) must lead sys.path so `import plasma.*` and
# `import shared.*` resolve when this file is run as a script (its own dir would
# otherwise shadow the package).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AXES = ["Ð", "Þ", "Ř", "Φ", "ƒ", "Ç", "Γ", "ɢ", "⊙", "Ħ", "Σ", "Ω"]


def _load_catalog(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return list(data.values()) if isinstance(data, dict) else data


def main(argv):
    if len(argv) < 2:
        print("plasma: needs a catalog entry name — plasma <entry_name>")
        return 2
    name = argv[1]
    if len(argv) < 3:
        print("plasma: no catalog path supplied by the caller")
        return 2
    entries = _load_catalog(argv[2])

    match = next((e for e in entries if e.get("name") == name), None)
    if match is None:
        print(f"plasma: '{name}' not found in the catalog")
        return 1

    tup = {k: match[k] for k in AXES if k in match}
    if len(tup) < len(AXES):
        missing = [k for k in AXES if k not in tup]
        print(f"plasma: '{name}' has an incomplete tuple (missing {' '.join(missing)})")
        return 1

    from plasma.plasma_forge import PlasmaForge

    d = PlasmaForge().forge(tup, name=name)

    lines = [
        f"plasma reading of {name}  {d.tuple_str}  (tier {d.tier})",
        f"  regime:          {d.regime}",
        f"  dimensionality:  {d.dimensionality}",
        f"  mode structure:  {d.mode_structure}",
        f"  coupling (Ř):    {d.coupling}",
        f"  symmetries (Φ):  {d.symmetries}",
        f"  collisionality:  {d.collisionality}",
        f"  transport (Ç):   {d.transport}",
        f"  interaction (Γ): {d.interaction_range}",
        f"  cascade (ɢ):     {d.cascade}",
        f"  criticality (⊙): {d.criticality}",
        f"  chirality (Ħ):   {d.chirality}",
        f"  species (Σ):     {d.species}",
        f"  magnetic top(Ω): {d.topology}",
    ]
    if d.instabilities:
        lines.append("  instabilities:")
        lines.extend(f"    — {x}" for x in d.instabilities)
    if d.diagnostics:
        lines.append("  diagnostics:")
        lines.extend(f"    — {x}" for x in d.diagnostics)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
