#!/usr/bin/env python3
"""cdxml_generator.py — ChemDraw CDXML reaction scheme generator for ch3mpiler.

Produces fully-formed ChemDraw CDXML files with:
  - 2D-rendered molecules (reactants, products) via RDKit coordinates
  - Reaction arrows between steps
  - Curved arrow-pushing showing electron flow from nucleophile → electrophile
  - Structural tuple annotation (optional)

Arrow-pushing direction is derived from the primitive type algebra:
  - Higher P (parity/electron symmetry) → nucleophile (electron donor)
  - Lower F (more classical) → better donor
  - Higher Φ (criticality) → reaction hub
  - Bond type determines arrow kind: σ-donation, π-donation, lone pair

Usage:
    from cdxml_generator import generate_reaction_cdxml
    cdxml = generate_reaction_cdxml(steps, out_path="scheme.cdxml")

Author: Lando⊗⊙perator
"""

import math, os, sys, xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

# ── Glyph map (same as compiler.py) ──
GLYPH_MAP = {
    "\U0001045B": "D1", "\U00010468": "D2", "\U00010461": "T1",
    "\U00010470": "T2", "\U00010465": "T3", "\U00010478": "T5",
    "\U00010469": "R1", "\U00010451": "R2", "\U0001047D": "R3",
    "\U0001047E": "R4", "\U00010457": "P1", "\U0001047F": "P2",
    "\U0001046C": "P3", "\U0001046F": "P4", "\U00010479": "P5",
    "\U00010450": "F3", "\U0001045E": "F2", "\U00010471": "F1",
    "\U00010458": "K1", "\U00010464": "K2", "\U00010467": "K3",
    "\U0001047A": "K4", "\U0001046A": "K5", "\U0001045A": "G1",
    "\U00010454": "G2", "\U00010472": "G3", "\U0001045D": "Ga1",
    "\U0001045C": "Ga2", "\U00010460": "Ga3", "\U00010475": "Ga4",
    "\U00010462": "Ph1", "\u2299": "Ph2", "\U0001046E": "Ph3",
    "\U0001047B": "Ph4", "\U00010463": "Ph5", "\U00010452": "H2",
    "\U00010456": "H3", "\U00010453": "H1", "\U0001046B": "H4",
    "\U00010459": "S1", "\U00010455": "S2", "\U00010473": "S3",
    "\U00010477": "W1", "\U00010474": "W2", "\U0001046D": "W3",
    "\U0001045F": "W4"
}

def glyph_to_ord(glyph_val):
    """Map glyph unicode to ordinal int (1-5).
    GLYPH_MAP values are strings like "D1", "Ph2", "T3".
    Ordinal is always the last character.
    """
    s = GLYPH_MAP.get(glyph_val, None)
    if s is None:
        return 1
    # s is a string like "D1", "Ph2", "T3" — ordinal is last char
    try:
        return int(s[-1])
    except (ValueError, IndexError):
        return 1

# ── Nucleophilicity / electrophilicity from structural tuple ──
# Derived from: P (electron symmetry), F (quantum coherence), K (kinetics)
# Higher score = more nucleophilic

def nucleophilicity_score(fg_tuple):
    """Score a functional group's nucleophilic character from its structural tuple.
    
    Factors:
      - P (parity): P1=asymmetric(nucleophilic lone pairs), P5(fully symmetric)
      - F (fidelity): F1(classical=best donor), F3(quantum=delocalized)
      - K (kinetics): K1(fast), K5(frozen)
      - R (coupling): R4(bidirectional=ambident)
    Returns float, higher = more nucleophilic.
    """
    if not fg_tuple:
        return 0.0
    score = 0.0
    for p, val in fg_tuple.items():
        ordinal = glyph_to_ord(val)
        if p == "P":
            # Low P (asymmetric) = nucleophilic lone pairs
            # P1(𐑗)=+3, P5(𐑹)=+0
            score += (5 - ordinal) * 0.75
        elif p == "F":
            # Low F (classical) = better electron donor
            # F1=+2, F3=+0
            score += (3 - ordinal) * 0.5
        elif p == "K":
            # Moderate K = available for reaction
            # K2(𐑧) = best balance for donation
            score -= abs(ordinal - 2) * 0.25
        elif p == "R":
            # R4 = ambident nucleophile
            if ordinal == 4:
                score += 0.5
        elif p == "S":
            # S1 (single) vs S3 (many) — lone pair availability
            if ordinal <= 1:
                score += 0.3
    return score

def electrophilicity_score(fg_tuple):
    """Score electrophilic character (electron-accepting).
    
    Factors:
      - P: High P = empty orbital / polarized
      - K: Low K = fast reaction (kinetically available)
      - F: F3(quantum) = conjugated accepting
    """
    if not fg_tuple:
        return 0.0
    score = 0.0
    for p, val in fg_tuple.items():
        ordinal = glyph_to_ord(val)
        if p == "P":
            # High P (symmetric) = empty orbital available
            # P5(𐑹)=+3, P1(𐑗)=+0
            score += (ordinal - 1) * 0.75
        elif p == "K":
            # Low kinetic barrier = good acceptor
            score += (5 - ordinal) * 0.3
        elif p == "F":
            # F3(quantum)=conjugation = good acceptor
            if ordinal == 3:
                score += 0.5
        elif p == "Φ":
            # Higher criticality = reactive hub
            score += min(ordinal, 3) * 0.2
    return score


def determine_arrow_direction(fg1_tuple, fg2_tuple, bond_name=""):
    """Determine which FG donates electrons (curved arrow tail → head).
    
    Returns (nucleophile_fg, electrophile_fg, confidence).
    """
    nuc1 = nucleophilicity_score(fg1_tuple)
    nuc2 = nucleophilicity_score(fg2_tuple)
    elec1 = electrophilicity_score(fg1_tuple)
    elec2 = electrophilicity_score(fg2_tuple)
    
    # Net donor strength
    donor1 = nuc1 - elec1
    donor2 = nuc2 - elec2
    
    if donor1 > donor2:
        return (0, 1, abs(donor1 - donor2))
    elif donor2 > donor1:
        return (1, 0, abs(donor1 - donor2))
    else:
        # Ambident — check bond type
        if "ester" in bond_name or "amide" in bond_name or "carbonyl" in bond_name:
            return (0, 1, 0.1)  # FG1 = alcohol/amine (nucleophile), FG2 = carbonyl (electrophile)
        return (0, 1, 0.0)



# ── CDXML generation ──

def mol_to_cdxml_fragment(mol, frag_id, offset_x=0.0, offset_y=0.0, scale=15.0):
    """Convert an RDKit Mol to a CDXML <fragment> element with atoms and bonds.
    
    Returns XML string for the fragment, positioned with offset.
    scale: RDKit coords are ~1-5 units, CDXML needs ~50-200 for ChemDraw display.
    """
    if mol is None:
        return ""
    
    # Get 2D coordinates
    conf = mol.GetConformer()
    
    lines = []
    lines.append(f'    <fragment id="{frag_id}">')
    
    # Write atoms
    atom_map = {}
    for i, atom in enumerate(mol.GetAtoms()):
        pt = conf.GetAtomPosition(i)
        x = pt.x * scale + offset_x
        y = pt.y * scale + offset_y
        aid = (frag_id * 1000) + i + 1
        atom_map[i] = aid
        
        atomic_num = atom.GetAtomicNum()
        elem = atom.GetSymbol()
        if atomic_num == 6:  # Carbon — use List (no label by default)
            elem_code = ' List="C"'
            label = ""
        elif atomic_num == 1:  # Hydrogen — usually suppressed in ChemDraw
            elem_code = ' Element="H"'
            label = ""
        else:
            elem_code = f' Element="{elem}"'
            label = ""
        
        charge = atom.GetFormalCharge()
        charge_str = f' Charge="{charge}"' if charge != 0 else ""
        
        isotope = atom.GetIsotope()
        isotope_str = f' Isotope="{isotope}"' if isotope > 0 else ""
        
        lines.append(f'      <n id="{aid}" p="{x:.1f} {y:.1f}"{elem_code}{charge_str}{isotope_str}/>')
    
    # Write bonds
    bond_id_start = (frag_id * 1000) + 100
    for i, bond in enumerate(mol.GetBonds()):
        bid = bond_id_start + i + 1
        begin = atom_map[bond.GetBeginAtomIdx()]
        end = atom_map[bond.GetEndAtomIdx()]
        order = bond.GetBondTypeAsDouble()
        
        # CDXML bond order
        if order == 1.0:
            btype = " 1"
        elif order == 2.0:
            btype = " 2"
        elif order == 3.0:
            btype = " 3"
        elif order == 1.5:
            btype = " 5"  # aromatic
        else:
            btype = f" {int(order)}"
        
        # Stereo chemistry
        stereo = bond.GetStereo()
        display = ""
        if stereo == Chem.rdchem.BondStereo.STEREOE or stereo == Chem.rdchem.BondStereo.STEREOCIS:
            display = ' Display="WedgedHashBegin"'  # up wedge
        elif stereo == Chem.rdchem.BondStereo.STEREOZ or stereo == Chem.rdchem.BondStereo.STEREOTRANS:
            display = ' Display="WedgeBegin"'  # down wedge
        
        lines.append(f'      <b id="{bid}" B="{begin} {end}{btype}"{display}/>')
    
    lines.append(f'    </fragment>')
    return "\n".join(lines)


def cdxml_header(page_width=15000, page_height=10000):
    """Generate CDXML header with color table and font table."""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE CDXML SYSTEM "http://www.cambridgesoft.com/xml/cdxml.dtd">
<CDXML
  CreationProgram="ch3mpiler Lando⊗⊙perator"
  ChemDrawVersion="23.1.1"
  BoundingBox="0 0 ''' + str(page_width) + ' ' + str(page_height) + '''"
>
  <colortable>
    <color r="0" g="0" b="0"/>
    <color r="1" g="0" b="0"/>
    <color r="1" g="1" b="0"/>
    <color r="0" g="0" b="1"/>
  </colortable>
  <fonttable>
    <font id="1" charset="iso" name="Arial"/>
    <font id="2" charset="iso" name="Times New Roman"/>
  </fonttable>
'''


def cdxml_footer():
    return '</CDXML>\n'


def reaction_arrow(arrow_id, x1, y1, x2, y2, 
                    arrowhead="Full", arrowtype="Solid"):
    """Generate a CDXML reaction arrow element."""
    return (f'    <arrow id="{arrow_id}" '
            f'BoundingBox="{x1} {y1-50} {x2} {y1+50}" '
            f'HeadSize="432" '
            f'LineWidth="4" '
            f'ArrowheadHead="{arrowhead}" '
            f'ArrowheadType="{arrowtype}" '
            f'p="{(x1+x2)/2:.1f} {y1:.1f}" '
            f'End="{x2} {y1:.1f}" '
            f'Start="{x1} {y1:.1f}"/>')


def curved_arrow(graphic_id, start_x, start_y, end_x, end_y, 
                 color=1, line_width=4, arrow_head="Full"):
    """Generate a CDXML curved arrow graphic for electron-pushing.
    
    The arrow curves from start (tail, nucleophile) to end (head, electrophile).
    Control point is offset perpendicular to midpoint for the curve.
    """
    # Calculate midpoint for control point
    mid_x = (start_x + end_x) / 2
    mid_y = (start_y + end_y) / 2
    
    # Perpendicular offset for curve
    dx = end_x - start_x
    dy = end_y - start_y
    length = math.sqrt(dx*dx + dy*dy)
    if length > 0:
        perp_x = -dy / length * 20.0  # curve magnitude
        perp_y = dx / length * 20.0
    else:
        perp_x, perp_y = 10.0, 10.0
    
    # The control point is offset from midpoint
    cp_x = mid_x + perp_x
    cp_y = mid_y + perp_y
    
    return (f'    <graphic id="{graphic_id}" '
            f'GraphicType="CurvedArrow" '
            f'BoundingBox="{min(start_x,end_x,cp_x)-20} {min(start_y,end_y,cp_y)-20} '
            f'{max(start_x,end_x,cp_x)+20} {max(start_y,end_y,cp_y)+20}" '
            f'ArrowheadHead="{arrow_head}" '
            f'ArrowheadType="Solid" '
            f'HeadSize="288" '
            f'LineWidth="{line_width}" '
            f'Color="{color}" '
            f'p1="{start_x:.1f} {start_y:.1f}" '
            f'p2="{cp_x:.1f} {cp_y:.1f}" '
            f'p3="{end_x:.1f} {end_y:.1f}"/>')


def curved_arrow_3point(point_a, point_b, point_c, graphic_id,
                         color=1, line_width=4, arrow_head="Full"):
    """Curved arrow defined by three explicit Bezier control points.
    point_a = tail (nucleophile), point_b = curve control, point_c = head (electrophile)
    """
    xs = [point_a[0], point_b[0], point_c[0]]
    ys = [point_a[1], point_b[1], point_c[1]]
    return (f'    <graphic id="{graphic_id}" '
            f'GraphicType="CurvedArrow" '
            f'BoundingBox="{min(xs)-20} {min(ys)-20} {max(xs)+20} {max(ys)+20}" '
            f'ArrowheadHead="{arrow_head}" '
            f'ArrowheadType="Solid" '
            f'HeadSize="288" '
            f'LineWidth="{line_width}" '
            f'Color="{color}" '
            f'p1="{point_a[0]:.1f} {point_a[1]:.1f}" '
            f'p2="{point_b[0]:.1f} {point_b[1]:.1f}" '
            f'p3="{point_c[0]:.1f} {point_c[1]:.1f}"/>')


def curved_arrow_tailhead(tail_x, tail_y, head_x, head_y, graphic_id,
                          color=1, bulge=0.3):
    """Curved arrow from tail to head with automatic bulge.
    
    bulge > 0 = clockwise curve, bulge < 0 = anticlockwise.
    Returns CDXML graphic string.
    """
    dx = head_x - tail_x
    dy = head_y - tail_y
    
    # Control point: offset perpendicular to the tail→head direction
    cx = (tail_x + head_x) / 2 - dy * bulge
    cy = (tail_y + head_y) / 2 + dx * bulge
    
    return curved_arrow_3point(
        (tail_x, tail_y), (cx, cy), (head_x, head_y),
        graphic_id, color=color
    )


def text_label(text, x, y, font_id=1, size=12, color=0, justification="Left", bold=False):
    """Generate a CDXML <t> text element."""
    bold_attr = ' Bold="1"' if bold else ''
    return (f'    <t id="{hash(text) % 100000 + 10000}" '
            f'p="{x:.1f} {y:.1f}" '
            f'Justification="{justification}" '
            f'Font="{font_id}" '
            f'Size="{size}"'
            f'{bold_attr}>'
            f'{escape(text)}'
            f'</t>')


def generate_reaction_cdxml(steps, out_path="reaction_scheme.cdxml",
                             title=None, show_tuples=False):
    """Generate a full CDXML reaction scheme from ch3mpiler path steps.
    
    Args:
        steps: list of dicts with keys:
            - step: int
            - bond: str (bond type name)
            - reaction: str (description)
            - fg1: str (functional group 1)
            - fg2: str (functional group 2)
            - product: str (product name)
            - smiles_reactant: str (optional SMILES of reactant for this step)
            - smiles_product: str (optional SMILES of product)
            - fg1_tuple: dict (optional structural tuple for FG1)
            - fg2_tuple: dict (optional structural tuple for FG2)
        out_path: path for output .cdxml file
        title: optional reaction scheme title
        show_tuples: annotate with structural tuple glyphs
    
    Returns: path to generated file, or None on failure.
    """
    if not HAS_RDKIT:
        print("WARNING: RDKit not available. Cannot generate CDXML with 2D coordinates.")
        return None
    
    page_width = 15000
    page_height = 8000 + (len(steps) * 2000)
    
    # Build CDXML
    cdxml = cdxml_header(page_width, page_height)
    cdxml += f'  <page BoundingBox="0 0 {page_width} {page_height}" HeightPages="1" WidthPages="1">\n'
    
    if title:
        cdxml += text_label(title, 200, page_height - 300, size=20, bold=True) + "\n"
    
    elem_id = 1
    arrow_id = 1
    graphic_id = 1
    
    # Layout: each step gets a horizontal row
    # reactant |---arrow---> product
    step_spacing_y = 2500
    base_y = page_height - 1000
    
    for i, step in enumerate(steps):
        step_id = i + 1
        y_pos = base_y - (i * step_spacing_y)
        
        # Step label
        cdxml += text_label(f"Step {step['step']}: {step['bond']}",
                            200, y_pos + 600, size=14, bold=True) + "\n"
        cdxml += text_label(step.get('reaction', ''),
                            200, y_pos + 400, size=11) + "\n"
        cdxml += text_label(f"{step.get('fg1', '?')} + {step.get('fg2', '?')}",
                            200, y_pos + 200, size=11) + "\n"
        
        # Parse molecules
        frags = []
        reactant_smiles = step.get('smiles_reactant', '')
        product_smiles = step.get('smiles_product', '')
        
        # Generate fragment from SMILES
        react_mol = None
        prod_mol = None
        
        if reactant_smiles:
            try:
                react_mol = Chem.MolFromSmiles(reactant_smiles)
                if react_mol:
                    react_mol = Chem.RemoveHs(react_mol)
                    AllChem.Compute2DCoords(react_mol)
            except Exception:
                pass
        
        if product_smiles:
            try:
                prod_mol = Chem.MolFromSmiles(product_smiles)
                if prod_mol:
                    prod_mol = Chem.RemoveHs(prod_mol)
                    AllChem.Compute2DCoords(prod_mol)
            except Exception:
                pass
        
        # Place molecules: reactant on the left, product on the right
        react_x = 800
        prod_x = 5000
        
        if react_mol:
            f_id = elem_id
            cdxml += mol_to_cdxml_fragment(react_mol, f_id, react_x, y_pos) + "\n"
            elem_id += 1
            frags.append(('reactant', f_id, react_mol, react_x, y_pos))
            
            # Label
            cdxml += text_label(step.get('fg1', step.get('product', '?')),
                                react_x, y_pos - 400, size=10) + "\n"
        
        # Arrow from reactant to product
        arrow_x1 = react_x + 1200
        arrow_y1 = y_pos - 200
        arrow_x2 = prod_x - 300
        
        if react_mol and prod_mol:
            # Check if we have full 2D bounding boxes
            conf_r = react_mol.GetConformer()
            conf_p = prod_mol.GetConformer()
            
            if react_mol.GetNumAtoms() > 0:
                max_rx = max(conf_r.GetAtomPosition(a).x for a in range(react_mol.GetNumAtoms())) * 15 + react_x
                arrow_x1 = max_rx + 300
            
            if prod_mol.GetNumAtoms() > 0:
                min_px = min(conf_p.GetAtomPosition(a).x for a in range(prod_mol.GetNumAtoms())) * 15 + prod_x
                arrow_x2 = min_px - 300
        
        cdxml += reaction_arrow(arrow_id, arrow_x1, arrow_y1, arrow_x2, arrow_y1) + "\n"
        arrow_id += 1
        
        if prod_mol:
            f_id = elem_id
            cdxml += mol_to_cdxml_fragment(prod_mol, f_id, prod_x, y_pos) + "\n"
            elem_id += 1
            frags.append(('product', f_id, prod_mol, prod_x, y_pos))
            
            # Product name
            prod_name = step.get('product', '')
            cdxml += text_label(prod_name, prod_x, y_pos - 400, size=10) + "\n"
        
        # Arrow-pushing: atom-resolution curved arrow(s) between reaction centers
        if react_mol and react_mol.GetNumAtoms() > 0:
            # Build a list for the arrow-pushing graphics
            arrow_graphics = []
            graphic_id = add_arrow_pushing_to_step(
                arrow_graphics, step, react_mol, elem_id, react_x, y_pos, graphic_id, scale=15.0
            )
            for g in arrow_graphics:
                cdxml += g + "\n"
    
    cdxml += '  </page>\n'
    cdxml += cdxml_footer()
    
    # Write to file
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(cdxml)
        print(f"CDXML written to: {out_path}")
        return out_path
    except Exception as e:
        print(f"ERROR writing CDXML: {e}")
        return None


def generate_reaction_scheme_simple(reactant_smiles, product_smiles,
                                     out_path="reaction.cdxml",
                                     title="Reaction", bond_desc=""):
    """Simplified: generate single-reaction CDXML from SMILES strings."""
    steps = [{
        'step': 1,
        'bond': bond_desc or 'reaction',
        'reaction': title,
        'fg1': 'reactant',
        'fg2': 'product',
        'product': 'product',
        'smiles_reactant': reactant_smiles,
        'smiles_product': product_smiles,
    }]
    return generate_reaction_cdxml(steps, out_path, title=title)


# ── CLI entry point ──
def main():
    """CLI: generate CDXML from SMILES or ch3mpiler path."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate CDXML reaction schemes")
    parser.add_argument("--reactant", help="Reactant SMILES")
    parser.add_argument("--product", help="Product SMILES")
    parser.add_argument("--output", default="reaction.cdxml", help="Output path")
    parser.add_argument("--title", default="Reaction", help="Title")
    parser.add_argument("--multi", nargs="+", 
                        help="Multi-step: RXN SMILES 1, RXN SMILES 2, ...")
    args = parser.parse_args()
    
    if args.multi:
        steps = []
        for i, rxn_smi in enumerate(args.multi):
            parts = rxn_smi.split(">>")
            if len(parts) == 2:
                steps.append({
                    'step': i+1,
                    'bond': f'step_{i+1}',
                    'reaction': '',
                    'fg1': 'reactant',
                    'fg2': 'product',
                    'product': f'product_{i+1}',
                    'smiles_reactant': parts[0],
                    'smiles_product': parts[1],
                })
        generate_reaction_cdxml(steps, args.output, title=args.title)
    elif args.reactant and args.product:
        generate_reaction_scheme_simple(args.reactant, args.product, args.output, args.title)
    else:
        # Demo: benzaldehyde → n_benzoyl_phenylisoserine (aldol step)
        print("Demo: Aldol reaction benzaldehyde → phenylisoserine precursor")
        steps = [{
            'step': 1,
            'bond': 'sigma_single',
            'reaction': 'Asymmetric aldol: benzaldehyde + chiral acetate',
            'fg1': 'aldehyde',
            'fg2': 'amine',
            'product': 'n_benzoyl_phenylisoserine',
            'smiles_reactant': 'C1=CC=C(C=C1)C=O',  # benzaldehyde
            'smiles_product': 'C1=CC=C(C=C1)C(C(=O)O)NC(=O)C2=CC=CC=C2',  # approximate
            'fg1_tuple': {"P": "\U00010457", "F": "\U00010450", "K": "\U00010467"},
            'fg2_tuple': {"P": "\U00010457", "F": "\U00010450", "K": "\U00010467"},
        }]
        generate_reaction_cdxml(steps, args.output, title="Taxol Semi-Synthesis: Step 1")


if __name__ == "__main__":
    main()


# ── Enhanced Arrow-Pushing: Atom-Resolution Electron Flow ──

# SMARTS patterns for reaction centers (nucleophilic/electrophilic atoms per FG)
# Maps FG name → (nucleophilic_atom_smarts, electrophilic_atom_smarts, arrow_kind)
REACTION_CENTER_SMARTS = {
    "aldehyde": (
        None,  # aldehyde is electrophilic (C=O carbon is electron-deficient)
        r"[CX3H1](=O)",  # carbonyl carbon
        "pi_donation"
    ),
    "ketone": (
        None,
        r"[CX3](=O)",
        "pi_donation"
    ),
    "amine": (
        r"[NX3;H2,H1;!$(N=*)]",  # lone pair on nitrogen
        None,
        "lone_pair"
    ),
    "alcohol": (
        r"[OX2H]",  # lone pair on oxygen
        None,
        "lone_pair"
    ),
    "enolate": (
        r"[CX3]=[C,c][OX1-]",  # enolate carbon (negative charge resonance)
        None,
        "pi_donation"
    ),
    "carbonyl": (
        None,
        r"[CX3]=[OX1]",  # carbonyl carbon (electrophilic)
        "pi_donation"
    ),
    "carboxylic_acid": (
        r"[OX2H]",  # OH oxygen can donate
        r"[CX3](=O)",  # carbonyl carbon is electrophilic
        "lone_pair"
    ),
    "ester": (
        r"[OX2H0;!$(O=C)]",  # alkoxy oxygen
        r"[CX3](=O)",  # carbonyl carbon
        "lone_pair"
    ),
    "aromatic_ring": (
        None,  # π system
        None,  # depends on substitution
        "pi_donation"
    ),
    "thiol": (
        r"[SX2H]",
        None,
        "lone_pair"
    ),
    "alkene": (
        r"[CX3]=[CX3]",  # π bond
        None,
        "pi_donation"
    ),
    "alkyne": (
        r"[CX2]#[CX2]",  # π bond
        None,
        "pi_donation"
    ),
    "alkyl_halide": (
        None,
        r"[CX4][Cl,Br,I]",  # carbon attached to leaving group
        "sigma_donation"
    ),
    "epoxide": (
        None,
        r"O1[CX4][CX4]1",  # strained ring carbon
        "sigma_donation"
    ),
}


def find_reaction_centers(mol, fg_name, role="nucleophile"):
    """Find specific atoms in a molecule that participate in arrow-pushing.
    
    Args:
        mol: RDKit Mol
        fg_name: name of the functional group
        role: "nucleophile" or "electrophile"
    
    Returns: list of atom indices (0-based) that are reactive centers.
    """
    from rdkit import Chem
    if mol is None:
        return []
    
    smarts_info = REACTION_CENTER_SMARTS.get(fg_name)
    if smarts_info is None:
        return []
    
    smarts = smarts_info[0] if role == "nucleophile" else smarts_info[1]
    if smarts is None:
        return []
    
    try:
        pat = Chem.MolFromSmarts(smarts)
        if pat is None:
            return []
        matches = mol.GetSubstructMatches(pat)
        if matches:
            # Return first atom of each match (typically the reactive center)
            return [m[0] for m in matches]
    except Exception:
        pass
    return []


def add_arrow_pushing_to_step(cdxml, step_info, react_mol, frag_id, offset_x, offset_y, 
                               graphic_id_start, scale=15.0):
    """Add atom-resolution curved arrow(s) for arrow-pushing on the reactant.
    
    Uses SMARTS to find exact reaction centers, then draws curved arrows
    from nucleophilic atom to electrophilic atom.
    
    Returns: updated graphic_id_start (next available ID).
    """
    if react_mol is None or not HAS_RDKIT:
        return graphic_id_start
    
    fg1 = step_info.get('fg1', '')
    fg2 = step_info.get('fg2', '')
    fg1_tup = step_info.get('fg1_tuple', {})
    fg2_tup = step_info.get('fg2_tuple', {})
    
    if not fg1 or not fg2:
        return graphic_id_start
    
    # Determine direction: which FG is nucleophile, which is electrophile
    nuc_score1 = nucleophilicity_score(fg1_tup) if fg1_tup else 0
    nuc_score2 = nucleophilicity_score(fg2_tup) if fg2_tup else 0
    elec_score1 = electrophilicity_score(fg1_tup) if fg1_tup else 0
    elec_score2 = electrophilicity_score(fg2_tup) if fg2_tup else 0
    
    net1 = nuc_score1 - elec_score1
    net2 = nuc_score2 - elec_score2
    
    conf = react_mol.GetConformer()
    
    if net1 >= net2:
        nuc_fg, elec_fg = fg1, fg2
    else:
        nuc_fg, elec_fg = fg2, fg1
    
    # Find specific atoms
    nuc_atoms = find_reaction_centers(react_mol, nuc_fg, "nucleophile")
    elec_atoms = find_reaction_centers(react_mol, elec_fg, "electrophile")
    
    # Determine arrow kind
    smarts_info = REACTION_CENTER_SMARTS.get(nuc_fg)
    arrow_kind = smarts_info[2] if smarts_info else "lone_pair"
    
    if nuc_atoms and elec_atoms:
        # We have specific atoms - draw curved arrows between them
        for aidx, nuc_atom in enumerate(nuc_atoms[:2]):  # Max 2 arrows
            for bidx, elec_atom in enumerate(elec_atoms[:1]):  # Electrophile target
                # Get atom positions (RDKit coords → CDXML scaled coords)
                nuc_pos = conf.GetAtomPosition(nuc_atom)
                elec_pos = conf.GetAtomPosition(elec_atom)
                
                tail_x = nuc_pos.x * scale + offset_x
                tail_y = nuc_pos.y * scale + offset_y
                head_x = elec_pos.x * scale + offset_x
                head_y = elec_pos.y * scale + offset_y
                
                # Different colors/line widths for different arrow kinds
                if arrow_kind == "lone_pair":
                    color = 1  # Red for lone pair donation
                    line_w = 3
                    bulge = 0.35
                    # Offset tail slightly from atom center (lone pair sits outside)
                    dx = head_x - tail_x
                    dy = head_y - tail_y
                    length = math.sqrt(dx*dx + dy*dy)
                    if length > 0:
                        tail_x -= dx/length * 15
                        tail_y -= dy/length * 15
                elif arrow_kind == "pi_donation":
                    color = 2  # Yellow for π donation
                    line_w = 4
                    bulge = -0.3  # Opposite curve direction
                else:
                    color = 3  # Blue for σ donation
                    line_w = 4
                    bulge = 0.3
                
                gid = graphic_id_start + aidx * 10 + bidx
                cdxml.append(curved_arrow_tailhead(
                    tail_x, tail_y, head_x, head_y,
                    gid, color=color, bulge=bulge
                ))
                graphic_id_start += 1
    
    elif nuc_atoms and not elec_atoms:
        # Have nucleophile atoms but not electrophile — draw to molecule center
        nuc_pos = conf.GetAtomPosition(nuc_atoms[0])
        # Find centroid of molecule as approximate target
        all_x = [conf.GetAtomPosition(a).x for a in range(react_mol.GetNumAtoms())]
        all_y = [conf.GetAtomPosition(a).y for a in range(react_mol.GetNumAtoms())]
        centroid_x = (min(all_x) + max(all_x)) / 2 * scale + offset_x
        centroid_y = (min(all_y) + max(all_y)) / 2 * scale + offset_y
        
        tail_x = nuc_pos.x * scale + offset_x
        tail_y = nuc_pos.y * scale + offset_y
        
        gid = graphic_id_start
        cdxml.append(curved_arrow_tailhead(
            tail_x, tail_y, centroid_x + 50, centroid_y,
            gid, color=1, bulge=0.3
        ))
        graphic_id_start += 1
    
    else:
        # Fallback: use molecule centroid, draw arrow between FGs
        all_x = [conf.GetAtomPosition(a).x for a in range(react_mol.GetNumAtoms())]
        all_y = [conf.GetAtomPosition(a).y for a in range(react_mol.GetNumAtoms())]
        c_x = (min(all_x) + max(all_x)) / 2 * scale + offset_x
        c_y = (min(all_y) + max(all_y)) / 2 * scale + offset_y
        
        # Net direction determines which side of molecule to place each FG
        if net1 >= net2:
            tail_x, tail_y = c_x - 100, c_y + 80
            head_x, head_y = c_x + 100, c_y - 80
        else:
            tail_x, tail_y = c_x + 100, c_y - 80
            head_x, head_y = c_x - 100, c_y + 80
        
        gid = graphic_id_start
        cdxml.append(curved_arrow_tailhead(tail_x, tail_y, head_x, head_y, gid, color=1))
        graphic_id_start += 1
    
    return graphic_id_start
