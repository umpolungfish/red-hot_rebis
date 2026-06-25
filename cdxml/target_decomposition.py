"""
cdxml/target_decomposition.py — Render target scaffold with annotated disconnection cuts.

Instead of one CDXML per fragment (showing individual small molecules), generates a single
CDXML showing the FULL TARGET MOLECULE with:
- Colored dashed lines across strategic bond cuts
- Text annotations labeling each disconnection
- Fragment SMILES shown as labels

Usage:
    from cdxml.target_decomposition import target_decomposition_cdxml
    cdxml = target_decomposition_cdxml(smiles, name, strategic_bonds)
    with open("target.cdxml", "w") as f:
        f.write(cdxml)

Author: Lando⊗⊙perator
"""
from rdkit import Chem
from rdkit.Chem import AllChem

ATOMIC_SYMBOLS = {
    1: 'H', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 15: 'P',
    16: 'S', 17: 'Cl', 35: 'Br', 53: 'I', 5: 'B', 14: 'Si',
}

CDXML_HEADER = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE CDXML SYSTEM "https://static.chemistry.revvitycloud.com/cdxml/CDXML.dtd" >
<CDXML
 CreationProgram="ChemDraw 23.1.1.3"
 Name="{name}.cdxml"
 BoundingBox="{bbox}"
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
<color r="1" g="1" b="1"/>
<color r="0" g="0" b="0"/>
<color r="1" g="0" b="0"/>
<color r="0" g="1" b="0"/>
<color r="0" g="0" b="1"/>
<color r="1" g="0" b="1"/>
<color r="0" g="1" b="1"/>
<color r="1" g="1" b="0"/>
</colortable>
<fonttable>
 <font id="3" charset="iso-8859-1" name="Arial"/>
</fonttable>
<page
 id="1"
 BoundingBox="0 0 -32768 4318.50"
 bgcolor="1"
 HeaderPosition="36"
 FooterPosition="36"
 PrintTrimMarks="yes"
>
'''

CDXML_FOOTER = '''</page>
</CDXML>'''

def _cdxml_graphic_line(x1, y1, x2, y2, color_id=4, line_width=3):
    """Generate a CDXML <graphic> element drawing a colored dashed line."""
    return f'''<graphic
 GraphicType="Line"
 BoundingBox="{min(x1,x2)-2:.2f} {min(y1,y2)-2:.2f} {max(x1,x2)+2:.2f} {max(y1,y2)+2:.2f}"
 LineType="Dashed"
 LineWidth="{line_width}"
 LineCap="0"
 Color="{color_id}"
>
 <p p="{x1:.2f} {y1:.2f}"/>
 <p p="{x2:.2f} {y2:.2f}"/>
</graphic>'''


def _cdxml_annotation(text, x, y, color_id=0, font_size=10, just='Center', ann_id=0):
    """Generate a CDXML <annotation> element at position (x,y)."""
    bbox = f"{x-60:.2f} {y-14:.2f} {x+60:.2f} {y+6:.2f}"
    return f'''<annotation id="{ann_id}" BoundingBox="{bbox}"
 CaptionAlignment="{just}" CaptionJustification="{just}"
 Color="{color_id}" LabelJustification="{just}"
 VerticalOffset="0" HorizontalOffset="0"
 LabelFace="96" LabelSize="{font_size}" LabelFont="3">
 <s font="3" size="{font_size}" face="96">{text}</s>
</annotation>'''


def molecule_to_cdxml(smiles: str, molecule_name: str, strategic_bonds: list,
                       fg_pair_bonds: dict = None) -> str:
    """Wrapper: pipeline_hook-compatible entrypoint.
    
    Delegates to target_decomposition_cdxml with the same signature.
    fg_pair_bonds is accepted for API compatibility; the detailed overlay
    layer can be enriched later.
    """
    return target_decomposition_cdxml(
        smiles=smiles,
        name=molecule_name,
        strategic_bonds=strategic_bonds,
    )


def target_decomposition_cdxml(smiles: str, name: str, strategic_bonds: list) -> str:
    """Generate CDXML showing target molecule with annotated disconnection cuts.

    Args:
        smiles: Target molecule SMILES (e.g. "CC(=O)N")
        name: Molecule name for CDXML header and annotation
        strategic_bonds: List of strategic bond dicts from ScaffoldParser
            Each dict has: bond_idx, atom_a, atom_b, bond_type,
            fg1, fg2, fragment_smiles_a, fragment_smiles_b

    Returns:
        Complete CDXML string ready to write to .cdxml file
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    AllChem.Compute2DCoords(mol)
    Chem.Kekulize(mol, clearAromaticFlags=True)
    conf = mol.GetConformer()

    SCALE = 10.0
    coords = []
    for i in range(mol.GetNumAtoms()):
        p = conf.GetAtomPosition(i)
        coords.append((p.x * SCALE + 300, -p.y * SCALE + 300))

    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    atom_ids = {}
    atom_z = 2
    lines = []

    for i in range(mol.GetNumAtoms()):
        atom = mol.GetAtomWithIdx(i)
        atomic_num = atom.GetAtomicNum()
        symbol = atom.GetSymbol()
        x, y = coords[i]
        node_id = i + 2
        atom_ids[i] = node_id

        attrs = f'id="{node_id}" p="{x:.2f} {y:.2f}" Z="{atom_z}" AS="N"'

        if atomic_num != 6:
            label = ATOMIC_SYMBOLS.get(atomic_num, symbol)
            num_h = atom.GetNumImplicitHs()
            attrs += f' Element="{atomic_num}" NumHydrogens="{num_h}" NeedsClean="yes"'
            if num_h > 0:
                label += 'H' + (str(num_h) if num_h > 1 else '')
            lines.append(f'<n {attrs}>')
            tx = x - (4 + 2 * num_h)
            ty = y + 4
            tb = f"{tx-2:.2f} {ty-8:.2f} {tx+8+4*num_h:.2f} {ty+2:.2f}"
            lines.append(f'<t p="{tx:.2f} {ty:.2f}" BoundingBox="{tb}" LabelJustification="Left">')
            lines.append(f'<s font="3" size="10" color="0" face="96">{label}</s>')
            lines.append('</t>')
            lines.append('</n>')
        else:
            lines.append(f'<n {attrs}/>')

        atom_z += 1

    # Build bonds — strategic cuts get colored solid, non-strategic are normal
    bond_z = atom_z + 1
    strategic_bond_indices = {b['bond_idx'] for b in strategic_bonds}
    annotations = []
    graphics = []

    for i in range(mol.GetNumBonds()):
        bond = mol.GetBondWithIdx(i)
        begin = atom_ids[bond.GetBeginAtomIdx()]
        end = atom_ids[bond.GetEndAtomIdx()]
        btype = bond.GetBondTypeAsDouble()

        b_attrs = f'id="{i + 1000}" Z="{bond_z}" B="{begin}" E="{end}"'

        if i in strategic_bond_indices:
            b_attrs += ' BS="N" Color="6"'  # Blue bond for strategic cuts
        else:
            b_attrs += ' BS="N"'

        if btype == 2.0:
            b_attrs += ' Order="2"'
        elif btype == 3.0:
            b_attrs += ' Order="3"'

        lines.append(f'<b {b_attrs}/>')
        bond_z += 1

    # Add cut markers: colored dashed overlay lines + labels
    color_palette = [2, 4, 6, 5, 7]  # red, green, blue, teal, magenta
    ann_id = 500
    for bi, sb in enumerate(strategic_bonds):
        color_id = color_palette[bi % len(color_palette)]
        a_start = sb['atom_a']
        a_end = sb['atom_b']
        x1, y1 = coords[a_start]
        x2, y2 = coords[a_end]

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        # Dashed overlay line ORTHOGONAL to the bond (perpendicular scission mark)
        dx = x2 - x1
        dy = y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            dx, dy = -dy / length, dx / length  # rotate 90° for perpendicular
        ext = 14
        gx1 = mx - dx * ext
        gy1 = my - dy * ext
        gx2 = mx + dx * ext
        gy2 = my + dy * ext

        graphics.append(_cdxml_graphic_line(gx1, gy1, gx2, gy2, color_id=color_id))

        # Label with fragments
        frag_a = sb.get('fragment_smiles_a', '?')[:20]
        frag_b = sb.get('fragment_smiles_b', '?')[:20]
        cut_label = f"{sb['fg1']}→{frag_a} | {sb['fg2']}→{frag_b}"

        # Position label perpendicular to bond
        px = -dy * 14
        py = dx * 14
        annot_x = mx + px
        annot_y = my + py

        annotations.append(_cdxml_annotation(
            cut_label, annot_x + 5, annot_y + 8,
            color_id=color_id, font_size=8, ann_id=ann_id
        ))
        ann_id += 1

    # Add title annotation
    annotations.insert(0, _cdxml_annotation(
        f"Target: {name} [{smiles}]  |  {len(strategic_bonds)} disconnection(s)",
        (min_x + max_x) / 2, min_y - 40, color_id=0, font_size=11, ann_id=99
    ))

    # Assemble XML parts
    atoms_xml = '\n'.join(
        l for l in lines if l.startswith('<n') or l.startswith('</n>') or
        l.startswith('<t') or l.startswith('</t>') or l.startswith('<s')
    )
    bonds_xml = '\n'.join(l for l in lines if l.startswith('<b'))
    graphics_xml = '\n'.join(graphics)
    annotations_xml = '\n'.join(annotations)

    margin = 30
    bbox_str = f"{min_x-margin:.2f} {min_y-60:.2f} {max_x+200:.2f} {max_y+margin:.2f}"

    fragment = f'''<fragment
 id="1"
 BoundingBox="{bbox_str}"
 Z="1"
>{atoms_xml}
{bonds_xml}
</fragment>'''

    cdxml = CDXML_HEADER.format(name=name, bbox=bbox_str)
    cdxml += fragment + '\n'
    cdxml += graphics_xml + '\n' if graphics_xml else ''
    cdxml += annotations_xml
    cdxml += CDXML_FOOTER

    return cdxml
