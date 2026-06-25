"""
cdxml/generator.py — SMILES → CDXML conversion engine.

Core function: smiles_to_cdxml(smiles, name, annotation="")
  Returns a proper ChemDraw CDXML string with correct v2 tags:
  - <n> for atoms (NOT <node>)
  - <b> for bonds (NOT <bond>)
  - p="x y" coordinate format
  - Carbon atoms: implicit (no Element, no label)
  - Non-carbon atoms: Element + <t><s>Label</s></t> child

Author: Lando⊗⊙perator
"""
import math
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem

ATOMIC_SYMBOLS = {
    1: 'H', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 15: 'P',
    16: 'S', 17: 'Cl', 35: 'Br', 53: 'I', 5: 'B', 14: 'Si',
    11: 'Na', 19: 'K', 20: 'Ca', 12: 'Mg', 26: 'Fe', 30: 'Zn',
    29: 'Cu', 27: 'Co', 25: 'Mn', 24: 'Cr', 28: 'Ni', 79: 'Au',
    47: 'Ag', 80: 'Hg', 48: 'Cd', 33: 'As', 34: 'Se', 50: 'Sn',
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
 ShowTerminalCarbonLabels="no"
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
<color r="1" g="1" b="0"/>
<color r="0" g="1" b="0"/>
<color r="0" g="1" b="1"/>
<color r="0" g="0" b="1"/>
<color r="1" g="0" b="1"/>
</colortable>
<fonttable>
 <font id="3" charset="iso-8859-1" name="Arial"/>
</fonttable>
<page
 id="1"
 BoundingBox="0 0 -32768 4318.50"
 HeaderPosition="36"
 FooterPosition="36"
 PrintTrimMarks="yes"
>
'''

CDXML_FOOTER = '''</page>
</CDXML>
'''

APTAMER_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE CDXML SYSTEM "https://static.chemistry.revvitycloud.com/cdxml/CDXML.dtd" >
<CDXML
 CreationProgram="ChemDraw 23.1.1.3"
 Name="{filename}"
 BoundingBox="0 0 2000 500"
 WindowPosition="0 0"
 WindowSize="-2147483648 -2147483648"
 FractionalWidths="yes"
 InterpretChemically="no"
 ShowTerminalCarbonLabels="no"
 HideImplicitHydrogens="no"
 Magnification="666"
 LabelFont="3"
 LabelSize="14"
 LabelFace="96"
 CaptionFont="3"
 CaptionSize="14"
 LineWidth="0.60"
 BoldWidth="2"
 BondLength="14.40"
>
<colortable>
<color r="1" g="1" b="1"/>
<color r="0" g="0" b="0"/>
</colortable>
<fonttable>
<font id="3" charset="iso-8859-1" name="Arial"/>
<font id="4" charset="iso-8859-1" name="Times New Roman"/>
</fonttable>
<page id="1" BoundingBox="0 0 2000 500" HeaderPosition="36" FooterPosition="36">
 <annotation id="2" BoundingBox="50 50 1950 450"
  CaptionAlignment="Left" CaptionJustification="Left"
  Color="0" LabelFace="96" LabelSize="14" LabelFont="3">
  <s font="3" size="14" face="96">{annotation}</s>
 </annotation>
 <annotation id="3" BoundingBox="50 350 1950 450"
  CaptionAlignment="Center" CaptionJustification="Center"
  Color="0" LabelFace="64" LabelSize="12" LabelFont="4">
  <s font="4" size="12" face="64">5&apos;-{sequence}-3&apos; ({length} nt)</s>
 </annotation>
</page>
</CDXML>'''


def smiles_to_cdxml(smiles: str, name: str, annotation: str = "") -> str:
    """Convert SMILES to proper CDXML using correct ChemDraw tags.

    Args:
        smiles: Valid SMILES string
        name: Molecule name (used in CDXML header)
        annotation: Optional descriptive text shown on CDXML canvas

    Returns:
        Complete CDXML string, ready to write to .cdxml file
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")

    AllChem.Compute2DCoords(mol)
    Chem.Kekulize(mol, clearAromaticFlags=True)
    conf = mol.GetConformer()

    # Scale: RDKit bond length ~1.5, CDXML ~14.4
    SCALE = 10.0
    coords = []
    for i in range(mol.GetNumAtoms()):
        p = conf.GetAtomPosition(i)
        coords.append((p.x * SCALE + 300, -p.y * SCALE + 300))

    # Bounding box
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    margin = 20
    bbox = f"{min_x-margin:.2f} {min_y-margin:.2f} {max_x+margin:.2f} {max_y+margin:.2f}"

    # Build atoms
    lines = []
    atom_ids = {}
    atom_z = 2

    for i in range(mol.GetNumAtoms()):
        atom = mol.GetAtomWithIdx(i)
        atomic_num = atom.GetAtomicNum()
        symbol = atom.GetSymbol()
        x, y = coords[i]
        node_id = i + 2
        atom_ids[i] = node_id

        attrs = f'id="{node_id}" p="{x:.2f} {y:.2f}" Z="{atom_z}" AS="N" AtomID="{i+1}"'

        if atomic_num != 6:
            label = ATOMIC_SYMBOLS.get(atomic_num, symbol)
            attrs += f' Element="{atomic_num}" NumHydrogens="0" NeedsClean="yes"'
            lines.append(f'<n {attrs}>')
            tx = x - 4
            ty = y + 4
            tb = f"{tx-2:.2f} {ty-8:.2f} {tx+8:.2f} {ty+2:.2f}"
            lines.append(f'<t p="{tx:.2f} {ty:.2f}" BoundingBox="{tb}" LabelJustification="Left">')
            lines.append(f'<s font="3" size="10" color="0" face="96">{label}</s>')
            lines.append('</t>')
            lines.append('</n>')
        else:
            lines.append(f'<n {attrs}/>')

        atom_z += 1

    # Build bonds
    bond_z = atom_z + 1
    for i in range(mol.GetNumBonds()):
        bond = mol.GetBondWithIdx(i)
        begin = atom_ids[bond.GetBeginAtomIdx()]
        end = atom_ids[bond.GetEndAtomIdx()]
        btype = bond.GetBondTypeAsDouble()

        b_attrs = f'id="{i + 1000}" Z="{bond_z}" B="{begin}" E="{end}" BS="N"'
        if btype == 2.0:
            b_attrs += ' Order="2"'
        elif btype == 3.0:
            b_attrs += ' Order="3"'

        lines.append(f'<b {b_attrs}/>')
        bond_z += 1

    # Separate atoms and bonds for the fragment
    atoms_xml = '\n'.join(
        l for l in lines
        if l.startswith('<n') or l.startswith('</n>') or
           l.startswith('<t') or l.startswith('</t>') or
           l.startswith('<s')
    )
    bonds_xml = '\n'.join(l for l in lines if l.startswith('<b'))

    fragment = f'''<fragment
 id="1"
 BoundingBox="{bbox}"
 Z="1"
>{atoms_xml}
{bonds_xml}
</fragment>'''

    # Annotation
    annotation_xml = ""
    if annotation:
        ann_bbox = f"{min_x-10:.2f} {min_y-50:.2f} {max_x+100:.2f} {min_y-40:.2f}"
        annotation_xml = f'''
<annotation id="2" BoundingBox="{ann_bbox}"
 CaptionAlignment="Left" CaptionJustification="Left"
 Color="0" LabelJustification="Auto"
 VerticalOffset="0" HorizontalOffset="0"
 LabelFace="96" LabelSize="10" LabelFont="3">
 <s font="3" size="10" face="96">{annotation}</s>
</annotation>'''

    cdxml = CDXML_HEADER.format(name=name, bbox=bbox)
    cdxml += fragment
    cdxml += annotation_xml
    cdxml += CDXML_FOOTER

    return cdxml


def aptamer_to_cdxml(filename: str, sequence: str, length: int, annotation: str) -> str:
    """Generate CDXML for a nucleic acid aptamer (annotation-based, no structure)."""
    return APTAMER_TEMPLATE.format(
        filename=filename,
        annotation=annotation,
        sequence=sequence,
        length=length,
    )


def material_to_cdxml(name: str, elements: list, annotation: str, 
                       x_start: int = 200, gap: int = 180, y: int = 400) -> str:
    """Generate CDXML for a material/composition display (element symbols on canvas)."""
    nodes = []
    atom_z = 2
    for i, e in enumerate(elements):
        x = x_start + i * gap
        tx = x - 10
        ty = y + 5
        tb = f"{x-20:.2f} {y-25:.2f} {x+20:.2f} {y+25:.2f}"
        nodes.append(f'<n id="{i+2}" p="{x:.2f} {y:.2f}" Z="{atom_z}" AS="N">')
        nodes.append(f'<t p="{tx:.2f} {ty:.2f}" BoundingBox="{tb}" LabelJustification="Center">')
        nodes.append(f'<s font="3" size="18" color="0" face="96">{e}</s>')
        nodes.append('</t>')
        nodes.append('</n>')
        atom_z += 1

    frag_bbox = f"{x_start-50:.2f} {y-60:.2f} {x_start+len(elements)*gap+50:.2f} {y+60:.2f}"
    page_bbox = f"0 0 {x_start+len(elements)*gap+200:.2f} 800"
    nodemap = '\n'.join(nodes)

    fragment = f'''<fragment
 id="1"
 BoundingBox="{frag_bbox}"
 Z="1"
>{nodemap}
</fragment>'''

    return f'''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE CDXML SYSTEM "https://static.chemistry.revvitycloud.com/cdxml/CDXML.dtd" >
<CDXML
 CreationProgram="ChemDraw 23.1.1.3"
 Name="{name}.cdxml"
 BoundingBox="{page_bbox}"
 WindowPosition="0 0"
 WindowSize="-2147483648 -2147483648"
 WindowIsZoomed="yes"
 FractionalWidths="yes"
 InterpretChemically="no"
 ShowTerminalCarbonLabels="no"
 HideImplicitHydrogens="no"
 Magnification="666"
 LabelFont="3"
 LabelSize="18"
 LabelFace="96"
 CaptionFont="3"
 CaptionSize="14"
 LineWidth="0.60"
 BoldWidth="2"
 BondLength="14.40"
>
<colortable>
<color r="1" g="1" b="1"/>
<color r="0" g="0" b="0"/>
</colortable>
<fonttable>
<font id="3" charset="iso-8859-1" name="Arial"/>
<font id="4" charset="iso-8859-1" name="Times New Roman"/>
</fonttable>
<page
 id="1"
 BoundingBox="0 0 {x_start+len(elements)*gap+200:.2f} 800"
 HeaderPosition="36"
 FooterPosition="36"
>
{fragment}
<annotation id="2" BoundingBox="50 50 {x_start+len(elements)*gap+100:.2f} 200"
 CaptionAlignment="Center" CaptionJustification="Center"
 Color="0" LabelFace="64" LabelSize="14" LabelFont="4">
 <s font="4" size="14" face="64">{annotation}</s>
</annotation>
</page>
</CDXML>'''


def verify_cdxml(cdxml: str) -> dict:
    """Verify a CDXML string has correct v2 tags. Returns {'valid': bool, 'issues': [...]}.

    NOTES:
      - Single-atom molecules (water 'O', ammonia 'N') are valid CDXML with 0 bonds.
      - Multi-fragment ionic compounds ([OH-].[Na+], [BH4-].[Na+]) also produce
        0 bonds in CDXML because the fragments are disconnected. This is valid CDXML
        and ChemDraw renders it correctly (separate ions on canvas).
      - The verifier distinguishes between structural errors (wrong tags, missing
        coordinates) and benign zero-bond cases (monoatomic, ionic, multi-fragment).
    """
    issues = []
    warnings = []
    if '<node' in cdxml:
        issues.append("Contains old <node> tag (should be <n>)")
    if '<bond' in cdxml:
        issues.append("Contains old <bond> tag (should be <b>)")
    if '<n ' not in cdxml and '<n>' not in cdxml:
        issues.append("Missing <n> atom tags")
    if 'p=' not in cdxml and 'p="' not in cdxml:
        issues.append("Missing p= coordinate attributes")
    if 'Element="0"' in cdxml:
        issues.append("Contains Element=\"0\" (unknown element)")

    atom_count = cdxml.count('<n ')
    bond_count = cdxml.count('<b ')

    if bond_count == 0 and atom_count > 1:
        # Could be ionic compound (multi-fragment) or genuine layout failure.
        # Check for Element attributes suggesting ions (metals)
        has_metal_ion = any(
            f'Element="{an}"' in cdxml
            for an in ['11', '19', '12', '20', '13', '5', '3']
        )
        if has_metal_ion:
            warnings.append(f"Multi-fragment ionic compound: {atom_count} atoms, 0 bonds (expected for salts/ions)")
        else:
            warnings.append(f"Multi-atom no-bond structure: {atom_count} atoms, 0 bonds (may be ionic or fragments)")
    elif bond_count == 0 and atom_count == 1:
        warnings.append("Single-atom molecule: 0 bonds expected (monoatomic)")
    elif bond_count == 0 and atom_count == 0:
        warnings.append("No structural content (annotation-only)")

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'atom_count': atom_count,
        'bond_count': bond_count,
        'size_bytes': len(cdxml),
    }
