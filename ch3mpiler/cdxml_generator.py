#!/usr/bin/env python3
"""cdxml_generator.py — ChemDraw CDXML reaction scheme generator for ch3mpiler.

Produces fully-formed ChemDraw CDXML files matching real ChemDraw 23.1 output:
  - 2D-rendered molecules (reactants, products) via RDKit coordinates
  - Kekulé bond orders (no Order="5" which is Wedge, not aromatic)
  - Reaction arrows between steps
  - Curved arrow-pushing (GraphicType="Arc" — the CDXML-standard type)
  - Atom labels (child <t> elements) for heteroatoms (O, N, S, etc.)
  - Z-ordering, BS="N" on bonds, proper page format with sentinel right edge
  - Auto-computed page bounds (never clips or overspills)

Arrow-pushing direction is derived from the primitive type algebra:
  - Higher P (parity/electron symmetry) → nucleophile (electron donor)  
  - Lower F (more classical) → better donor
  - Higher Φ (criticality) → reaction hub
  - Bond type determines arrow kind: sigma-donation, pi-donation, lone pair

Usage:
    from cdxml_generator import generate_reaction_cdxml
    cdxml = generate_reaction_cdxml(steps, out_path="scheme.cdxml")

Author: Lando⊗⊙perator
"""

import math, os, sys
from xml.sax.saxutils import escape

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, rdchem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

# ── Globals ──
_TEXT_ID_COUNTER = [100000]

def _next_text_id():
    _TEXT_ID_COUNTER[0] += 1
    return _TEXT_ID_COUNTER[0]

# ── Helpers ──
ELEMENT_SYMBOLS = {
    1: "H", 2: "He", 3: "Li", 4: "Be", 5: "B", 6: "C", 7: "N", 8: "O",
    9: "F", 10: "Ne", 11: "Na", 12: "Mg", 13: "Al", 14: "Si", 15: "P",
    16: "S", 17: "Cl", 18: "Ar", 19: "K", 20: "Ca", 35: "Br", 53: "I"
}

def glyph_to_ord(glyph):
    if not glyph:
        return 0
    if isinstance(glyph, str) and len(glyph) == 1:
        code = ord(glyph)
        if 0x10450 <= code <= 0x1047F:
            return (code - 0x10450) + 1
    return 0

def nucleophilicity_score(fg_tuple):
    if not fg_tuple:
        return 0.0
    score = 0.0
    for p, val in fg_tuple.items():
        ordinal = glyph_to_ord(val)
        if p == "P":
            score += (5 - ordinal) * 0.5
        elif p == "F":
            if ordinal == 3:
                score += 0.5
        elif p == "K":
            score += (ordinal - 1) * 0.3
        elif p == "S":
            if ordinal <= 1:
                score += 0.3
    return score

def electrophilicity_score(fg_tuple):
    if not fg_tuple:
        return 0.0
    score = 0.0
    for p, val in fg_tuple.items():
        ordinal = glyph_to_ord(val)
        if p == "P":
            score += (ordinal - 1) * 0.75
        elif p == "K":
            score += (5 - ordinal) * 0.3
        elif p == "F":
            if ordinal == 3:
                score += 0.5
        elif p == "\U0001D711":
            score += min(ordinal, 3) * 0.2
    return score

def determine_arrow_direction(fg1_tuple, fg2_tuple, bond_name=""):
    nuc1 = nucleophilicity_score(fg1_tuple)
    nuc2 = nucleophilicity_score(fg2_tuple)
    elec1 = electrophilicity_score(fg1_tuple)
    elec2 = electrophilicity_score(fg2_tuple)
    donor1 = nuc1 - elec1
    donor2 = nuc2 - elec2
    if donor1 > donor2:
        return (0, 1, abs(donor1 - donor2))
    elif donor2 > donor1:
        return (1, 0, abs(donor1 - donor2))
    else:
        if "ester" in bond_name or "amide" in bond_name or "carbonyl" in bond_name:
            return (0, 1, 0.1)
        return (0, 1, 0.0)

# ── CDXML generation ──

_ATOM_Z_COUNTER = [1]
_BOND_Z_COUNTER = [100]

def _next_atom_z():
    _ATOM_Z_COUNTER[0] += 1
    return _ATOM_Z_COUNTER[0]

def _next_bond_z():
    _BOND_Z_COUNTER[0] += 1
    return _BOND_Z_COUNTER[0]

def mol_to_cdxml_fragment(mol, frag_id, offset_x=0.0, offset_y=0.0, scale=40.0):
    """Convert RDKit Mol to CDXML fragment with proper ChemDraw format.
    
    CRITICAL FIXES:
      - Kekulized bonds (no Order="5" = Wedge)  
      - Atom labels as child <t> elements for heteroatoms (O, N, S, etc.)
      - Z-ordering on all atoms, bonds, and the fragment itself
      - BS="N" on all bonds (Bond Stereo = Normal)
      - No Order attribute on single bonds (default in CDXML)
    """
    if mol is None or mol.GetNumAtoms() == 0:
        return "", (0, 0, 0, 0)
    
    # Kekulize aromatic bonds for CDXML compatibility
    mol_k = Chem.Mol(mol)
    try:
        Chem.Kekulize(mol_k)
    except Exception:
        mol_k = mol
    
    conf = mol.GetConformer()
    
    # Compute bounds
    xs, ys = [], []
    for i in range(mol.GetNumAtoms()):
        pt = conf.GetAtomPosition(i)
        xs.append(pt.x * scale + offset_x)
        ys.append(pt.y * scale + offset_y)
    
    frag_min_x = min(xs) - 100.0 if xs else offset_x
    frag_min_y = min(ys) - 100.0 if ys else offset_y
    frag_max_x = max(xs) + 100.0 if xs else offset_x + 200
    frag_max_y = max(ys) + 100.0 if ys else offset_y + 200
    
    lines = []
    frag_z = _next_atom_z()
    lines.append(f'    <fragment id="{frag_id}" BoundingBox="{frag_min_x:.1f} {frag_min_y:.1f} {frag_max_x:.1f} {frag_max_y:.1f}" Z="{frag_z}">')
    
    # Atoms
    atom_map = {}
    for i, atom in enumerate(mol.GetAtoms()):
        pt = conf.GetAtomPosition(i)
        x = pt.x * scale + offset_x
        y = pt.y * scale + offset_y
        aid = (frag_id * 1000) + i + 1
        atom_map[i] = aid
        
        atomic_num = atom.GetAtomicNum()
        if atomic_num == 1:
            continue  # skip H (implicit in ChemDraw)
        
        az = _next_atom_z()
        charge = atom.GetFormalCharge()
        charge_str = f' Charge="{charge}"' if charge != 0 else ""
        isotope = atom.GetIsotope()
        isotope_str = f' Isotope="{isotope}"' if isotope > 0 else ""
        
        elem_str = f' Element="{atomic_num}"' if atomic_num != 6 else ''
        
        # Non-carbon atoms need explicit label and NumHydrogens
        nh = atom.GetTotalNumHs(includeNeighbors=False)
        nh_str = f' NumHydrogens="{nh}"' if (atomic_num not in (1, 6) and nh > 0) else ''
        as_str = ' AS="N"'
        
        lines.append(f'      <n id="{aid}" p="{x:.1f} {y:.1f}" Z="{az}"{as_str}{elem_str}{nh_str}{charge_str}{isotope_str}>')
        
        # Add text label for heteroatoms (non-C, non-H)
        if atomic_num not in (1, 6):
            symbol = ELEMENT_SYMBOLS.get(atomic_num, f'U{atomic_num}')
            label = symbol
            if charge != 0:
                label += '+' if charge > 0 else '\u2212'
            if nh > 0:
                label = symbol + 'H' + (str(nh) if nh > 1 else '')
                if charge != 0:
                    label += '+' if charge > 0 else '\u2212'
            tx = x - 4.0
            ty = y + 4.0
            lb = f'{tx-4:.1f} {ty-4:.1f} {tx+12:.1f} {ty+4:.1f}'
            lines.append(f'        <t p="{tx:.1f} {ty:.1f}" BoundingBox="{lb}" LabelJustification="Left">')
            lines.append(f'          <s font="3" size="10" color="0" face="96">{escape(label)}</s>')
            lines.append(f'        </t>')
        
        lines.append(f'      </n>')
    
    # Bonds from KEKULIZED molecule
    bond_id_start = (frag_id * 1000) + 100
    for i, bond in enumerate(mol_k.GetBonds()):
        bid = bond_id_start + i + 1
        begin = atom_map.get(bond.GetBeginAtomIdx())
        end = atom_map.get(bond.GetEndAtomIdx())
        if begin is None or end is None:
            continue
        
        order = bond.GetBondTypeAsDouble()
        if order == 1.0:
            order_str = ''  # single bond is default — omit Order
        elif order == 2.0:
            order_str = ' Order="2"'
        elif order == 3.0:
            order_str = ' Order="3"'
        else:
            order_str = ''
        
        bz = _next_bond_z()
        stereo = bond.GetStereo()
        bs_val = "N"  # default: normal bond
        
        if stereo in (rdchem.BondStereo.STEREOCIS, rdchem.BondStereo.STEREOE):
            bs_val = "W"  # Wedged Hash Begin (up)
        elif stereo in (rdchem.BondStereo.STEREOTRANS, rdchem.BondStereo.STEREOZ):
            bs_val = "B"  # Wedge Begin (down)
        
        bs_str = f' BS="{bs_val}"' if bs_val != "N" else ' BS="N"'
        
        lines.append(f'      <b id="{bid}" Z="{bz}" B="{begin}" E="{end}"{bs_str}{order_str}/>')
    
    lines.append('    </fragment>')
    return "\n".join(lines), (frag_min_x, frag_min_y, frag_max_x, frag_max_y)

def cdxml_header(content_bbox="200 200 5000 3000", page_height=10000):
    """CDXML header matching real ChemDraw 23.1 format."""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE CDXML SYSTEM "https://static.chemistry.revvitycloud.com/cdxml/CDXML.dtd">
<CDXML
 CreationProgram="ch3mpiler Lando\u2297\u2299perator v2"
 Name="reaction_scheme.cdxml"
 BoundingBox="{content_bbox}"
 WindowPosition="0 0"
 WindowSize="-2147483648 -2147483648"
 WindowIsZoomed="yes"
 FractionalWidths="yes"
 InterpretChemically="yes"
 ShowAtomQuery="yes"
 ShowAtomStereo="no"
 ShowAtomEnhancedStereo="yes"
 ShowAtomNumber="no"
 ShowResidueID="no"
 ShowBondQuery="yes"
 ShowBondRxn="yes"
 ShowBondStereo="no"
 ShowNonTerminalCarbonLabels="no"
 HideImplicitHydrogens="no"
 Magnification="666"
 LabelFont="3"
 LabelSize="10"
 LabelFace="96"
 CaptionFont="3"
 CaptionSize="10"
 HashSpacing="2.50"
 MarginWidth="1.60"
 LineWidth="0.60"
 BoldWidth="2"
 BondLength="14.40"
 BondSpacing="18"
 ChainAngle="120"
 LabelJustification="Auto"
 CaptionJustification="Left"
 PrintMargins="36 36 36 36"
>
<colortable>
<color r="0" g="0" b="0"/>
<color r="1" g="0" b="0"/>
<color r="1" g="1" b="0"/>
<color r="0" g="0" b="1"/>
<color r="0" g="1" b="0"/>
</colortable>
<fonttable>
 <font id="3" charset="iso-8859-1" name="Arial"/>
</fonttable>
'''

def cdxml_footer():
    return '</CDXML>\n'

def reaction_arrow(arrow_id, x1, y1, x2, y2, arrowhead="Full", arrowtype="Solid"):
    bb = f"{x1:.1f} {y1 - 50:.1f} {x2:.1f} {y1 + 50:.1f}"
    p_mid = (x1 + x2) / 2
    return (f'    <arrow id="{arrow_id}" BoundingBox="{bb}" '
            f'HeadSize="432" LineWidth="4" '
            f'ArrowheadHead="{arrowhead}" ArrowheadType="{arrowtype}" '
            f'p="{p_mid:.1f} {y1:.1f}" '
            f'End="{x2:.1f} {y1:.1f}" Start="{x1:.1f} {y1:.1f}"/>')

def curved_arrow_3point(point_a, point_b, point_c, graphic_id,
                        color=1, line_width=4, arrow_head="Full"):
    """Curved arrow using proper CDXML GraphicType='Arc' (NOT 'CurvedArrow')."""
    xs = [point_a[0], point_b[0], point_c[0]]
    ys = [point_a[1], point_b[1], point_c[1]]
    margin_local = 30
    bb = f"{min(xs)-margin_local:.1f} {min(ys)-margin_local:.1f} {max(xs)+margin_local:.1f} {max(ys)+margin_local:.1f}"
    return (f'    <graphic id="{graphic_id}" GraphicType="Arc" '
            f'BoundingBox="{bb}" '
            f'ArrowheadHead="{arrow_head}" ArrowheadType="Solid" '
            f'HeadSize="288" LineWidth="{line_width}" Color="{color}" ArcType="Arc">\n'
            f'      <n p="{point_a[0]:.1f} {point_a[1]:.1f}"/>\n'
            f'      <n p="{point_b[0]:.1f} {point_b[1]:.1f}"/>\n'
            f'      <n p="{point_c[0]:.1f} {point_c[1]:.1f}"/>\n'
            f'    </graphic>')

def curved_arrow_tailhead(tail_x, tail_y, head_x, head_y, graphic_id,
                          color=1, bulge=0.3):
    dx = head_x - tail_x
    dy = head_y - tail_y
    cx = (tail_x + head_x) / 2 - dy * bulge
    cy = (tail_y + head_y) / 2 + dx * bulge
    return curved_arrow_3point((tail_x, tail_y), (cx, cy), (head_x, head_y),
                               graphic_id, color=color)

def text_label(text, x, y, font_id=3, size=12, bold=False):
    tid = _next_text_id()
    bold_attr = ' Bold="1"' if bold else ''
    lb = f'{x-4:.1f} {y-4:.1f} {x+len(text)*7:.1f} {y+4:.1f}'
    return (f'    <t id="{tid}" p="{x:.1f} {y:.1f}" '
            f'BoundingBox="{lb}" '
            f'Justification="Left" Font="{font_id}" Size="{size}"{bold_attr}>'
            f'{escape(text)}</t>')

# ── SMARTS patterns for reaction centers ──
REACTION_CENTER_SMARTS = {
    "aldehyde": (None, r"[CX3H1](=O)", "pi_donation"),
    "ketone": (None, r"[CX3](=O)", "pi_donation"),
    "amine": (r"[NX3;H2,H1;!$(N=*)]", None, "lone_pair"),
    "alcohol": (r"[OX2H]", None, "lone_pair"),
    "enolate": (r"[CX3]=[C,c][OX1-]", None, "pi_donation"),
    "carbonyl": (None, r"[CX3]=[OX1]", "pi_donation"),
    "carboxylic_acid": (r"[OX2H]", r"[CX3](=O)", "lone_pair"),
    "ester": (r"[OX2H0;!$(O=C)]", r"[CX3](=O)", "lone_pair"),
    "aromatic_ring": (None, None, "pi_donation"),
    "thiol": (r"[SX2H]", None, "lone_pair"),
    "alkene": (r"[CX3]=[CX3]", None, "pi_donation"),
    "alkyne": (r"[CX2]#[CX2]", None, "pi_donation"),
    "alkyl_halide": (None, r"[CX4][Cl,Br,I]", "sigma_donation"),
    "epoxide": (None, r"O1[CX4][CX4]1", "sigma_donation"),
    "hydroxyl": (r"[OX2H]", None, "lone_pair"),
    "phenol": (r"[OX2H]", r"[cX3]1[cX3][cX3][cX3][cX3][cX3]1", "lone_pair"),
}

def find_reaction_centers(mol, fg_name, role="nucleophile"):
    if mol is None or not HAS_RDKIT:
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
        return [m[0] for m in matches] if matches else []
    except Exception:
        return []

def add_arrow_pushing_to_step(cdxml_list, step_info, react_mol, frag_id,
                               offset_x, offset_y, graphic_id_start, scale=40.0):
    """Add curved arrow(s) for arrow-pushing on the reactant."""
    if react_mol is None or not HAS_RDKIT:
        return graphic_id_start
    
    fg1 = step_info.get('fg1', '')
    fg2 = step_info.get('fg2', '')
    fg1_tup = step_info.get('fg1_tuple', {})
    fg2_tup = step_info.get('fg2_tuple', {})
    if not fg1 or not fg2:
        return graphic_id_start
    
    nuc1 = nucleophilicity_score(fg1_tup) if fg1_tup else 0
    nuc2 = nucleophilicity_score(fg2_tup) if fg2_tup else 0
    elec1 = electrophilicity_score(fg1_tup) if fg1_tup else 0
    elec2 = electrophilicity_score(fg2_tup) if fg2_tup else 0
    
    if (nuc1 - elec1) >= (nuc2 - elec2):
        nuc_fg, elec_fg = fg1, fg2
    else:
        nuc_fg, elec_fg = fg2, fg1
    
    nuc_atoms = find_reaction_centers(react_mol, nuc_fg, "nucleophile")
    elec_atoms = find_reaction_centers(react_mol, elec_fg, "electrophile")
    
    smarts_info = REACTION_CENTER_SMARTS.get(nuc_fg, (None, None, "lone_pair"))
    arrow_kind = smarts_info[2] if smarts_info else "lone_pair"
    conf = react_mol.GetConformer()
    
    if nuc_atoms and elec_atoms:
        for aidx, nuc_atom in enumerate(nuc_atoms[:2]):
            for bidx, elec_atom in enumerate(elec_atoms[:1]):
                np_ = conf.GetAtomPosition(nuc_atom)
                ep_ = conf.GetAtomPosition(elec_atom)
                tx = np_.x * scale + offset_x
                ty = np_.y * scale + offset_y
                hx = ep_.x * scale + offset_x
                hy = ep_.y * scale + offset_y
                
                if arrow_kind == "lone_pair":
                    color, lw, bulge = 1, 3, 0.35
                    dx_ = hx - tx
                    dy_ = hy - ty
                    length_ = math.sqrt(dx_*dx_ + dy_*dy_)
                    if length_ > 0:
                        tx -= dx_/length_ * 15
                        ty -= dy_/length_ * 15
                elif arrow_kind == "pi_donation":
                    color, lw, bulge = 2, 4, -0.3
                else:
                    color, lw, bulge = 3, 4, 0.3
                
                gid = graphic_id_start + aidx * 10 + bidx
                cdxml_list.append(curved_arrow_tailhead(tx, ty, hx, hy, gid, color=color, bulge=bulge))
                graphic_id_start += 1
    
    elif nuc_atoms and not elec_atoms:
        np_ = conf.GetAtomPosition(nuc_atoms[0])
        all_x = [conf.GetAtomPosition(a).x for a in range(react_mol.GetNumAtoms())]
        all_y = [conf.GetAtomPosition(a).y for a in range(react_mol.GetNumAtoms())]
        cx_ = (min(all_x) + max(all_x)) / 2 * scale + offset_x + 50
        cy_ = (min(all_y) + max(all_y)) / 2 * scale + offset_y
        tx = np_.x * scale + offset_x
        ty = np_.y * scale + offset_y
        cdxml_list.append(curved_arrow_tailhead(tx, ty, cx_, cy_, graphic_id_start, color=1, bulge=0.3))
        graphic_id_start += 1
    
    else:
        all_x = [conf.GetAtomPosition(a).x for a in range(react_mol.GetNumAtoms())]
        all_y = [conf.GetAtomPosition(a).y for a in range(react_mol.GetNumAtoms())]
        cx_ = (min(all_x) + max(all_x)) / 2 * scale + offset_x
        cy_ = (min(all_y) + max(all_y)) / 2 * scale + offset_y
        if (nuc1 - elec1) >= (nuc2 - elec2):
            tx, ty, hx, hy = cx_ - 100, cy_ + 80, cx_ + 100, cy_ - 80
        else:
            tx, ty, hx, hy = cx_ + 100, cy_ - 80, cx_ - 100, cy_ + 80
        cdxml_list.append(curved_arrow_tailhead(tx, ty, hx, hy, graphic_id_start, color=1))
        graphic_id_start += 1
    
    return graphic_id_start
def generate_reaction_cdxml(steps, out_path="reaction_scheme.cdxml",
                             title=None, show_tuples=False):
    """Generate a full CDXML reaction scheme from ch3mpiler path steps.
    
    FIXES (v3):
      - GraphicType="Arc" instead of invalid "CurvedArrow" (was "not understood")
      - Atom labels via child <t> elements for heteroatoms (O, N, S)
      - Z-ordering on all atoms, bonds, fragments
      - BS="N" on all bonds (Bond Stereo = Normal)  
      - Proper ChemDraw root attributes matching 23.1 format
      - Page sentinel right edge (-32768) like real ChemDraw
      - Kekulized aromatic bonds (no Order="5" = Wedge)
      - Dynamic page title/content positioning
    
    Returns: path to generated file, or None on failure.
    """
    if not HAS_RDKIT:
        print("WARNING: RDKit not available. Cannot generate CDXML.")
        return None
    
    global _TEXT_ID_COUNTER, _ATOM_Z_COUNTER, _BOND_Z_COUNTER
    _TEXT_ID_COUNTER = [100000]
    _ATOM_Z_COUNTER = [1]
    _BOND_Z_COUNTER = [100]
    
    margin = 500
    step_spacing_y = 2200
    base_y = 9000  # starting Y
    
    # Pre-process molecules with 2D coords
    step_mols = []
    for i, step in enumerate(steps):
        y_pos = base_y - (i * step_spacing_y)
        react_mol = prod_mol = None
        
        smi_r = step.get('smiles_reactant', '')
        smi_p = step.get('smiles_product', '')
        
        if smi_r:
            try:
                m = Chem.MolFromSmiles(smi_r)
                if m and m.GetNumAtoms() > 0:
                    m = Chem.RemoveHs(m)
                    AllChem.Compute2DCoords(m)
                    react_mol = m
            except Exception:
                pass
        
        if smi_p:
            try:
                m = Chem.MolFromSmiles(smi_p)
                if m and m.GetNumAtoms() > 0:
                    m = Chem.RemoveHs(m)
                    AllChem.Compute2DCoords(m)
                    prod_mol = m
            except Exception:
                pass
        
        step_mols.append((react_mol, prod_mol, y_pos))
    
    # Compute global bounds
    g_min_x, g_min_y = float('inf'), float('inf')
    g_max_x, g_max_y = float('-inf'), float('-inf')
    
    for react_mol, prod_mol, y_pos in step_mols:
        for mol, ox in [(react_mol, 800), (prod_mol, 5000)]:
            if mol and mol.GetNumAtoms() > 0:
                conf = mol.GetConformer()
                for a in range(mol.GetNumAtoms()):
                    pt = conf.GetAtomPosition(a)
                    x = pt.x * 40.0 + ox
                    y = pt.y * 40.0 + y_pos
                    g_min_x = min(g_min_x, x)
                    g_min_y = min(g_min_y, y)
                    g_max_x = max(g_max_x, x)
                    g_max_y = max(g_max_y, y)
        
        label_y_top = y_pos + 800
        arrow_y_mid = y_pos - 200
        g_min_y = min(g_min_y, label_y_top + 40, arrow_y_mid + 40)
        g_max_y = max(g_max_y, y_pos - 500, label_y_top - 400)
    
    if g_min_x == float('inf'):
        g_min_x, g_min_y = 0, 0
        g_max_x, g_max_y = 15000, 8000
    
    # Normalize Y so content sits near page top
    y_offset = margin - g_min_y + 200
    
    page_w = int(g_max_x - g_min_x + 2 * margin)
    page_h = int(g_max_y - g_min_y + 4 * margin)
    page_w = max(page_w, 3000)
    page_h = max(page_h, 2000)
    
    # Content bounding box for CDXML root
    n_min_y = g_min_y + y_offset
    n_max_y = g_max_y + y_offset
    content_bbox = f"{g_min_x:.1f} {n_min_y:.1f} {g_max_x:.1f} {n_max_y:.1f}"
    # Page bounding box: left=0 bottom=0 right=sentinel(-32768) top=page_h
    page_bbox = f"0 0 -32768 {page_h}"
    
    # Build CDXML
    cdxml = cdxml_header(content_bbox, page_h)
    cdxml += f'  <page id="1" BoundingBox="{page_bbox}" bgcolor="1" HeaderPosition="36" FooterPosition="36" PrintTrimMarks="yes">\n'
    
    if title:
        cdxml += text_label(title, margin, page_h - margin, size=20, bold=True) + "\n"
    
    elem_id = 1
    arrow_id = 1
    graphic_id = 1
    
    for i, (step, (react_mol, prod_mol, y_pos)) in enumerate(zip(steps, step_mols)):
        yd = y_pos + y_offset
        
        # Labels
        cdxml += text_label(f"Step {step['step']}: {step['bond']}", margin, yd + 800, size=14, bold=True) + "\n"
        cdxml += text_label(step.get('reaction', ''), margin, yd + 600, size=11) + "\n"
        cdxml += text_label(f"{step.get('fg1', '?')} + {step.get('fg2', '?')}", margin, yd + 400, size=11) + "\n"
        
        # Reactant molecule (left)
        react_x = 800
        if react_mol and react_mol.GetNumAtoms() > 0:
            frag_str, _ = mol_to_cdxml_fragment(react_mol, elem_id, react_x, yd)
            cdxml += frag_str + "\n"
            elem_id += 1
            cdxml += text_label(step.get('fg1', '?'), react_x, yd - 400, size=10) + "\n"
        
        # Arrow
        prod_x = 5000
        if react_mol and react_mol.GetNumAtoms() > 0:
            conf_r = react_mol.GetConformer()
            max_rx = max(conf_r.GetAtomPosition(a).x for a in range(react_mol.GetNumAtoms())) * 40.0 + react_x
            ax1 = max_rx + 300
        else:
            ax1 = react_x + 1200
        
        if prod_mol and prod_mol.GetNumAtoms() > 0:
            conf_p = prod_mol.GetConformer()
            min_px = min(conf_p.GetAtomPosition(a).x for a in range(prod_mol.GetNumAtoms())) * 40.0 + prod_x
            ax2 = min_px - 300
        else:
            ax2 = prod_x - 300
        
        cdxml += reaction_arrow(arrow_id, ax1, yd - 200, ax2, yd - 200) + "\n"
        arrow_id += 1
        
        # Product molecule (right)
        if prod_mol and prod_mol.GetNumAtoms() > 0:
            frag_str, _ = mol_to_cdxml_fragment(prod_mol, elem_id, prod_x, yd)
            cdxml += frag_str + "\n"
            elem_id += 1
            cdxml += text_label(step.get('product', ''), prod_x, yd - 400, size=10) + "\n"
        
        # Arrow-pushing
        if react_mol and react_mol.GetNumAtoms() > 0:
            arrow_gfx = []
            graphic_id = add_arrow_pushing_to_step(arrow_gfx, step, react_mol, elem_id,
                                                    react_x, yd, graphic_id, scale=40.0)
            for g in arrow_gfx:
                cdxml += g + "\n"
    
    cdxml += '  </page>\n' + cdxml_footer()
    
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(cdxml)
        print(f"CDXML written to: {out_path}")
        print(f"  CDXML BoundingBox: {content_bbox}")
        print(f"  Page: sentinel right edge, top={page_h}")
        print(f"  Steps: {len(steps)}")
        return out_path
    except Exception as e:
        print(f"ERROR writing CDXML: {e}")
        return None

def generate_reaction_scheme_simple(reactant_smiles, product_smiles,
                                     out_path="reaction.cdxml",
                                     title="Reaction", bond_desc=""):
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

def main():
    """CLI: generate CDXML from SMILES or ch3mpiler path."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate CDXML reaction schemes")
    parser.add_argument("--reactant", help="Reactant SMILES")
    parser.add_argument("--product", help="Product SMILES")
    parser.add_argument("--output", default="reaction.cdxml", help="Output path")
    parser.add_argument("--title", default="Reaction", help="Title")
    parser.add_argument("--multi", nargs="+",
                        help="Multi-step: RXN_SMILES_1 RXN_SMILES_2 ...")
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
        # Demo: aspirin synthesis
        print("Demo: Aspirin synthesis (salicylic acid -> aspirin)")
        steps = [{
            'step': 1,
            'bond': 'ester_link',
            'reaction': 'Acetylation (Ac2O/H3PO4)',
            'fg1': 'carboxylic_acid',
            'fg2': 'carbonyl',
            'product': 'aspirin',
            'smiles_reactant': 'c1ccc(c(c1)C(=O)O)O',  # salicylic acid
            'smiles_product': 'CC(=O)Oc1ccccc1C(=O)O',  # aspirin
        }]
        generate_reaction_cdxml(steps, args.output, title="Aspirin Synthesis")

if __name__ == "__main__":
    main()
