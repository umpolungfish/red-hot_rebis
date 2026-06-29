#!/usr/bin/env python3
"""smiles_to_cdxml.py — Generate validated CDXML from SMILES using RDKit.

Strategy: RDKit computes 2D coordinates, we write minimal valid CDXML.
Round-trip: generate → parse back → verify atom counts match.

Usage:
    python3 smiles_to_cdxml.py "CC(=O)OC1=CC=CC=C1C(=O)O" -o aspirin.cdxml
    python3 smiles_to_cdxml.py --multi targets.json -o output.cdxml
"""

import sys, json
from rdkit import Chem
from rdkit.Chem import rdDepictor
from shared.rich_output import *

# ── Periodic table ──
ELEMENT_SYMBOLS = {
    1: "H", 5: "B", 6: "C", 7: "N", 8: "O", 9: "F",
    15: "P", 16: "S", 17: "Cl", 35: "Br", 53: "I"
}


def get_hetero_label(mol, atom_idx):
    """Get the display label for a heteroatom. Returns (label_text, num_hydrogens)."""
    atom = mol.GetAtomWithIdx(atom_idx)
    elem = atom.GetAtomicNum()
    if elem == 6:
        return ("", 0)  # Carbon: no label
    
    symbol = ELEMENT_SYMBOLS.get(elem, f"#{elem}")
    total_h = atom.GetTotalNumHs()  # includes implicit + explicit
    
    # Build label: for non-carbon, show element symbol + H count if > 0
    if total_h == 0:
        return (symbol, 0)
    elif total_h == 1:
        return (f"{symbol}H", 1)
    elif total_h == 2:
        return (f"{symbol}H2", 2)
    elif total_h == 3:
        return (f"{symbol}H3", 3)
    else:
        return (f"{symbol}H{total_h}", total_h)


def mol_to_cdxml(mol, name="molecule"):
    """Convert RDKit Mol to valid CDXML string with 2D coordinates."""
    # Compute 2D coordinates
    rdDepictor.Compute2DCoords(mol)
    conf = mol.GetConformer()
    
    num_atoms = mol.GetNumAtoms()
    num_bonds = mol.GetNumBonds()
    
    # Scale: RDKit units → ChemDraw points (~9.6 ratio for 14.4 pt bond length)
    scale = 9.6
    atoms_xy = []
    for i in range(num_atoms):
        pos = conf.GetAtomPosition(i)
        cx = pos.x * scale + 500
        cy = -pos.y * scale + 800  # negate Y (ChemDraw Y-down)
        atoms_xy.append((cx, cy))
    
    # Bounding box
    xs = [a[0] for a in atoms_xy]
    ys = [a[1] for a in atoms_xy]
    pad = 50
    min_x, max_x = min(xs) - pad, max(xs) + pad
    min_y, max_y = min(ys) - pad, max(ys) + pad
    bbox = f"{min_x:.0f} {min_y:.0f} {max_x:.0f} {max_y:.0f}"
    
    # Kekulize for bond orders
    mol_k = Chem.Mol(mol)
    Chem.Kekulize(mol_k)
    
    lines = []
    # ── Header ──
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<!DOCTYPE CDXML SYSTEM "https://static.chemistry.revvitycloud.com/cdxml/CDXML.dtd">')
    lines.append(f'<CDXML\n CreationProgram="smiles_to_cdxml v1"\n Name="{name}"\n BoundingBox="{bbox}"\n Magnification="666"\n LabelFont="3"\n LabelSize="10"\n LabelFace="96"\n BondLength="14.40"\n ChainAngle="120"\n LineWidth="0.60"\n BoldWidth="2"\n HashSpacing="2.50"\n>')
    lines.append('<colortable><color r="0" g="0" b="0"/><color r="1" g="0" b="0"/><color r="1" g="1" b="0"/><color r="0" g="0" b="1"/><color r="0" g="1" b="0"/></colortable>')
    lines.append('<fonttable><font id="3" charset="iso-8859-1" name="Arial"/></fonttable>')
    
    # ── Page ──
    page_height = max_y - min_y + 2 * pad
    lines.append(f'<page id="1" BoundingBox="0 0 -32768 {page_height:.0f}" bgcolor="1">')
    
    # Title
    title_y = max_y + pad
    lines.append(f'<t id="100001" p="{min_x:.0f} {title_y:.0f}" BoundingBox="{min_x:.0f} {title_y-10:.0f} {min_x+200:.0f} {title_y+10:.0f}" Justification="Left" Font="3" Size="14" Bold="1">{name}</t>')
    
    # ── Fragment ──
    lines.append(f'<fragment id="1" BoundingBox="{bbox}" Z="2">')
    
    # Atoms
    aid_map = {}
    for i in range(num_atoms):
        aid = 1001 + i
        aid_map[i] = aid
        x, y = atoms_xy[i]
        atom = mol.GetAtomWithIdx(i)
        elem = atom.GetAtomicNum()
        label, nh = get_hetero_label(mol, i)
        
        if elem == 6:
            lines.append(f'<n id="{aid}" p="{x:.1f} {y:.1f}" Z="{3+i}" AS="N"/>')
        else:
            nh_attr = f' NumHydrogens="{nh}"' if nh > 0 else ''
            lbl_x, lbl_y = x - 4, y + 4
            lbl_pad = 12 + len(label) * 3
            lbl_bbox = f"{x-lbl_pad:.0f} {y-8:.0f} {x+lbl_pad:.0f} {y+8:.0f}"
            lines.append(f'<n id="{aid}" p="{x:.1f} {y:.1f}" Z="{3+i}" AS="N" Element="{elem}"{nh_attr}>')
            lines.append(f'<t p="{lbl_x:.1f} {lbl_y:.1f}" BoundingBox="{lbl_bbox}" LabelJustification="Left">')
            lines.append(f'<s font="3" size="10" color="0" face="96">{label}</s>')
            lines.append('</t>')
            lines.append('</n>')
    
    # Bonds (from Kekulized mol)
    for j, bond in enumerate(mol_k.GetBonds()):
        bid = 1101 + j
        b = aid_map.get(bond.GetBeginAtomIdx())
        e = aid_map.get(bond.GetEndAtomIdx())
        bo = bond.GetBondTypeAsDouble()
        order_attr = {2.0: ' Order="2"', 3.0: ' Order="3"'}.get(bo, '')
        lines.append(f'<b id="{bid}" Z="{101+j}" B="{b}" E="{e}" BS="N"{order_attr}/>')
    
    lines.append('</fragment>')
    lines.append('</page>')
    lines.append('</CDXML>')
    
    return '\n'.join(lines)


def validate_cdxml(cdxml_str, expected_atoms):
    """Validate CDXML by round-trip parsing with RDKit."""
    try:
        mols = Chem.MolsFromCDXML(cdxml_str)
        if mols and len(mols) > 0:
            mol = mols[0]
            actual = mol.GetNumAtoms()
            if actual == expected_atoms:
                return True, f"OK: {actual} atoms (expected {expected_atoms})"
            else:
                return False, f"MISMATCH: {actual} atoms, expected {expected_atoms}"
        return False, "No molecules parsed from CDXML"
    except Exception as e:
        return False, f"Parse error: {e}"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert SMILES to validated CDXML")
    parser.add_argument("smiles", nargs="?", help="SMILES string")
    parser.add_argument("-o", "--output", default="output.cdxml", help="Output file")
    parser.add_argument("-n", "--name", default="molecule", help="Molecule name")
    parser.add_argument("--multi", help="JSON file [{smiles, name}] for multi-molecule")
    args = parser.parse_args()
    
    if args.multi:
        with open(args.multi) as f:
            molecules = json.load(f)
        results = []
        for item in molecules:
            s = item["smiles"]
            nm = item.get("name", "mol")
            m = Chem.MolFromSmiles(s)
            if m is None:
                print(f"SKIP {nm}: bad SMILES")
                continue
            cdx = mol_to_cdxml(m, nm)
            ok, msg = validate_cdxml(cdx, m.GetNumAtoms())
            print(f"{nm}: {'✅' if ok else '❌'} {msg}")
            if ok:
                results.append(cdx)
        if results:
            with open(args.output, 'w') as f:
                f.write(results[0])
            print(f"Wrote {args.output} ({len(results)} molecules)")
        return
    
    if not args.smiles:
        parser.print_help()
        return
    
    mol = Chem.MolFromSmiles(args.smiles)
    if mol is None:
        print(f"ERROR: Cannot parse SMILES: {args.smiles}")
        sys.exit(1)
    
    cdxml = mol_to_cdxml(mol, args.name)
    ok, msg = validate_cdxml(cdxml, mol.GetNumAtoms())
    print(f"{args.name}: {'✅' if ok else '❌'} {msg}")
    
    if ok:
        with open(args.output, 'w') as f:
            f.write(cdxml)
        print(f"Wrote {args.output} ({len(cdxml)} bytes, {mol.GetNumAtoms()} atoms, {mol.GetNumBonds()} bonds)")
    else:
        with open(args.output + ".debug", 'w') as f:
            f.write(cdxml)
        print(f"Wrote debug file: {args.output}.debug")


if __name__ == "__main__":
    main()
