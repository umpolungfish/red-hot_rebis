"""
cdxml/molecules.py — Molecular, aptamer, and material definitions for CDXML generation.

All structures automatically exported via cdxml/generator.py with correct v2 tags.

Author: Lando⊗⊙perator
"""

from pathlib import Path
from .generator import smiles_to_cdxml, aptamer_to_cdxml, material_to_cdxml, verify_cdxml


MOLECULES = [
    {
        "filename": "Dexamethasone.cdxml",
        "smiles": "C[C@@]12C[C@@H]([C@]3([C@H]([C@@H]1C[C@@H]([C@]2(C(=O)CO)O)F)CCC4=CC(=O)C=C34)C)O",
        "name": "Dexamethasone",
        "annotation": "C22H29FO5 | MW 392.46 | Ouroboric Pill Anti-inflammatory Payload"
    },
    {
        "filename": "Saxitoxin.cdxml",
        "smiles": "CN1C(=NC2=C1C(C3CNC(=N)N3)OC(=O)N2)N",
        "name": "Saxitoxin (STX)",
        "annotation": "C10H17N7O4 | MW 299.28 | Na+ channel blocker | LD50 3.0 ng/kg"
    },
    {
        "filename": "Alpha_Amanitin.cdxml",
        "smiles": "CC(C)C1C(=O)NC2CSSCC3C(=O)NC(CSSCC(NC(=O)CNC1=O)C(=O)N4CCCC4C(=O)NC(C(C)O)C(=O)NC3C(=O)N5CCCC5C(=O)NC(CC(=O)N)C(=O)NCC(=O)NC(C(C)C)C(=O)N2)C(=O)O",
        "name": "Alpha-Amanitin",
        "annotation": "C39H54N10O14S | MW 919.0 | RNA Pol II inhibitor | LD50 100 ng/kg"
    },
    {
        "filename": "Sarin.cdxml",
        "smiles": "CC(C)OP(=O)(C)F",
        "name": "Sarin (GB)",
        "annotation": "C4H10FO2P | MW 140.09 | Nerve agent | LD50 30 ng/kg"
    },
    {
        "filename": "Cyanide.cdxml",
        "smiles": "[C-]#N",
        "name": "Cyanide",
        "annotation": "CN- | MW 26.02 | Cytochrome c oxidase inhibitor | LD50 1500 ng/kg"
    },
    {
        "filename": "11_cis_Retinal.cdxml",
        "smiles": "CC1=C(C(CCC1)(C)C)/C=C/C(=C/C=C/C(=C/C=O)/C)/C",
        "name": "11-cis-Retinal",
        "annotation": "C20H28O | Cephalopod opsin chromophore | Photoisomerization switch"
    },
    {
        "filename": "Acetylcholine.cdxml",
        "smiles": "CC(=O)OCC[N+](C)(C)C",
        "name": "Acetylcholine",
        "annotation": "C7H16NO2+ | Cephalopod chromatophore NMJ neurotransmitter"
    },
    {
        "filename": "Dopachrome.cdxml",
        "smiles": "O=C1C(=O)C2=CC(=C(C=C2N1)C(=O)O)O",
        "name": "Dopachrome",
        "annotation": "C9H7NO4 | Melanin precursor | Cephalopod chromatophore pigment"
    },
    {
        "filename": "Bisphenol_A.cdxml",
        "smiles": "CC(C)(C1=CC=C(C=C1)O)C2=CC=C(C=C2)O",
        "name": "Bisphenol A (BPA)",
        "annotation": "C15H16O2 | Plastic monomer | Target of laccase/peroxidase degradation"
    },
    {
        "filename": "Glutamic_Acid.cdxml",
        "smiles": "C(CC(=O)O)C(C(=O)O)N",
        "name": "L-Glutamic Acid",
        "annotation": "C5H9NO4 | Excitatory neurotransmitter | Human metabolome"
    },
    {
        "filename": "Tryptophan.cdxml",
        "smiles": "C1=CNC=C1CC(C(=O)O)N",
        "name": "L-Tryptophan",
        "annotation": "C11H12N2O2 | Essential amino acid | 5-HT/serotonin precursor"
    },
    {
        "filename": "Proline.cdxml",
        "smiles": "C1CC(NC1)C(=O)O",
        "name": "L-Proline",
        "annotation": "C5H9NO2 | Imino acid | Collagen structure"
    },
    {
        "filename": "Asparagine.cdxml",
        "smiles": "N[C@@H](CC(=O)N)C(=O)O",
        "name": "L-Asparagine",
        "annotation": "C4H8N2O3 | Amino acid | N-glycosylation substrate"
    },
    {
        "filename": "Glutamine.cdxml",
        "smiles": "N[C@@H](CCC(=O)N)C(=O)O",
        "name": "L-Glutamine",
        "annotation": "C5H10N2O3 | Conditionally essential amino acid"
    },
    {
        "filename": "Histidine.cdxml",
        "smiles": "N[C@@H](CC1=CN=CN1)C(=O)O",
        "name": "L-Histidine",
        "annotation": "C6H9N3O2 | Basic amino acid | Metal coordination"
    },
    {
        "filename": "Phenylalanine.cdxml",
        "smiles": "N[C@@H](Cc1ccccc1)C(=O)O",
        "name": "L-Phenylalanine",
        "annotation": "C9H11NO2 | Aromatic amino acid | Dopamine precursor"
    },
    {
        "filename": "Tyrosine.cdxml",
        "smiles": "N[C@@H](Cc1ccc(O)cc1)C(=O)O",
        "name": "L-Tyrosine",
        "annotation": "C9H11NO3 | Aromatic amino acid | Melanin/catecholamine precursor"
    },
    {
        "filename": "Stearic_Acid.cdxml",
        "smiles": "CCCCCCCCCCCCCCCCCC(=O)O",
        "name": "Stearic Acid (C18:0)",
        "annotation": "C18H36O2 | Saturated fatty acid | Membrane lipid"
    },
    {
        "filename": "Oleic_Acid.cdxml",
        "smiles": "CCCCCCCC=CCCCCCCCC(=O)O",
        "name": "Oleic Acid (C18:1)",
        "annotation": "C18H34O2 | Monounsaturated fatty acid | cis-double bond"
    },
    {
        "filename": "Acetoacetate.cdxml",
        "smiles": "CC(=O)CC(=O)CC(=O)O",
        "name": "Acetoacetate",
        "annotation": "C4H6O3 | Ketone body | Energy metabolism"
    },
    {
        "filename": "Cortisol.cdxml",
        "smiles": "C[C@@]1(CC(=O)[C@H]2[C@@H]1C[C@H]3C[C@@H](C(=O)[C@]23C)O)O",
        "name": "Cortisol",
        "annotation": "C21H30O5 | Primary glucocorticoid | Stress response hormone"
    },
    {
        "filename": "Testosterone.cdxml",
        "smiles": "CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C",
        "name": "Testosterone",
        "annotation": "C19H28O2 | Primary androgen | Sex hormone"
    },
    {
        "filename": "Estradiol.cdxml",
        "smiles": "CC12CCC3C(C1CCC2=O)CCC4=C3C=CC(=C4)O",
        "name": "Estradiol",
        "annotation": "C18H24O2 | Primary estrogen | Sex hormone"
    },
    {
        "filename": "Tryptamine.cdxml",
        "smiles": "NCCC1=CNC2=C1C=CC=C2",
        "name": "Tryptamine",
        "annotation": "C10H12N2 | Monoamine alkaloid | 5-HT analog scaffold"
    },
    {
        "filename": "Lignoceric_Acid.cdxml",
        "smiles": "CCCCCCCCCCCCCCCCCCCCCCCCCC(=O)O",
        "name": "Lignoceric Acid (C24:0)",
        "annotation": "C24H48O2 | Saturated very-long-chain fatty acid | Myelin sheath"
    },
]

APTAMERS = [
    {
        "filename": "IL6_Aptamer.cdxml",
        "sequence": "GCGAAUUCGUGGAAGGGUCGAUCCGGAGCUAGUUAGGGCUCCUAGCUA",
        "length": 58,
        "annotation": "IL-6 Aptamer | 58 nt | KD = 12.4 nM | Ouroboric Pill cytokine sensor"
    },
    {
        "filename": "TNFalpha_Aptamer.cdxml",
        "sequence": "CGUGCAGUCCGGCGUAGGGCGAUCGAUCGAUCGAUCGAUCGUAGGCUCGGAUCCUAGCUAGCU",
        "length": 62,
        "annotation": "TNF-alpha Aptamer | 62 nt | KD = 8.7 nM | Ouroboric Pill"
    },
    {
        "filename": "IFNgamma_Aptamer.cdxml",
        "sequence": "GGGAGCUCAGCCUUCACUUCUCCGAGCUAGCUAGCUAGCUAGGGAUCCGAUAGCU",
        "length": 60,
        "annotation": "IFN-gamma Aptamer | 60 nt | KD = 15.2 nM | Ouroboric Pill"
    },
    {
        "filename": "VEGF_Aptamer.cdxml",
        "sequence": "CGCAUCGUAUGGUUGGUGUGGUUUGGGAGCUAGCUAGCUAGCUAGGAUCCGAUAGCUA",
        "length": 55,
        "annotation": "VEGF Aptamer | 55 nt | KD = 0.5 nM | Ouroboric Pill angiogenesis sensor"
    },
    {
        "filename": "cMyc_Aptamer.cdxml",
        "sequence": "GGAUGGAUGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAUGGAU",
        "length": 60,
        "annotation": "cMyc Aptamer | 60 nt | KD = 3.8 nM | Ouroboric Pill oncogene sensor"
    },
]

MATERIALS = {
    "Frobenius_Composite_HEA.cdxml": {
        "name": "CrMnFeCoNi Cantor HEA",
        "elements": ["Cr","Mn","Fe","Co","Ni"],
        "annotation": "CrMnFeCoNi Cantor HEA | O2 | Frobenius Score 0.90 | Self-healing composite"
    },
    "BiSbTeSe_Topological_Insulator.cdxml": {
        "name": "(Bi,Sb)2(Te,Se)3 TI",
        "elements": ["Bi","Sb","Te","Se"],
        "annotation": "(Bi,Sb)2(Te,Se)3 Ternary TI | O2 | Critical Sensor Metamaterial | Frobenius Score 0.40"
    },
    "AlCoCrFeNi_HEA.cdxml": {
        "name": "AlCoCrFeNi2.1 Eutectic HEA",
        "elements": ["Al","Co","Cr","Fe","Ni"],
        "annotation": "AlCoCrFeNi2.1 Eutectic HEA | O2 | Ouroboric Self-Healing Alloy | Integer Winding Protection"
    },
    "CdSe_ZnS_QuantumDot.cdxml": {
        "name": "CdSe/ZnS Core/Shell QD",
        "elements": ["Cd","Se","Zn","S"],
        "annotation": "CdSe/ZnS Core/Shell Quantum Dot | 4.2 nm core | Ouroboric Pill Logic Gate"
    },
    "Sophick_Mercury.cdxml": {
        "name": "Sophick Mercury O_inf",
        "elements": ["Hg","Au","Ag","S"],
        "annotation": "Sophick Mercury O_inf | <odot.odot.odot.odot.odot.odot> | Eagle Cycle Terminal"
    },
}


def generate_molecules(output_dir, molecules=MOLECULES, verbose=True):
    """Generate CDXML for all small molecules."""
    generated = 0
    failed = []
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print("--- Small Molecules ---")
    for m in molecules:
        path = output_dir / m["filename"]
        try:
            cdxml = smiles_to_cdxml(m["smiles"], m["name"], m["annotation"])
            v = verify_cdxml(cdxml)
            if not v['valid']:
                raise ValueError(f"Verification failed: {v['issues']}")
            with open(path, 'w') as f:
                f.write(cdxml)
            if verbose:
                print(f"  ✓ {m['filename']} ({v['atom_count']} atoms, {v['bond_count']} bonds, {v['size_bytes']}b)")
            generated += 1
        except Exception as e:
            if verbose:
                print(f"  ✗ {m['filename']}: {e}")
            failed.append(m['filename'])
    return generated, failed


def generate_aptamers(output_dir, aptamers=APTAMERS, verbose=True):
    """Generate CDXML for all aptamers."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if verbose:
        print("--- Nucleic Acid Aptamers ---")
    for a in aptamers:
        path = output_dir / a["filename"]
        cdxml = aptamer_to_cdxml(
            a["filename"], a["sequence"], a["length"], a["annotation"]
        )
        with open(path, 'w') as f:
            f.write(cdxml)
        if verbose:
            print(f"  ✓ {a['filename']} ({a['length']} nt aptamer)")
    return len(aptamers), []


def generate_materials(output_dir, materials=MATERIALS, verbose=True):
    """Generate CDXML for all materials/complexes."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if verbose:
        print("--- Materials ---")
    for fn, m in materials.items():
        path = output_dir / fn
        cdxml = material_to_cdxml(m["name"], m["elements"], m["annotation"])
        with open(path, 'w') as f:
            f.write(cdxml)
        if verbose:
            print(f"  ✓ {fn} ({len(cdxml)} bytes)")
    return len(materials), []


def generate_all(output_dir, verbose=True):
    """Generate ALL CDXML files (molecules + aptamers + materials)."""
    from datetime import datetime
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    total_failed = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if verbose:
        print("=" * 70)
        print(f"RED-HOT REBIS CDXML GENERATOR (v2-integrated)")
        print(f"Output: {output_dir.resolve()}")
        print(f"Time:   {timestamp}")
        print("=" * 70)

    n, failed = generate_molecules(output_dir, verbose=verbose)
    total += n
    total_failed.extend(failed)

    n, failed = generate_aptamers(output_dir, verbose=verbose)
    total += n
    total_failed.extend(failed)

    n, failed = generate_materials(output_dir, verbose=verbose)
    total += n
    total_failed.extend(failed)

    if verbose:
        print(f"\n{'='*70}")
        print(f"TOTAL GENERATED: {total} CDXML files")
        if total_failed:
            print(f"FAILED: {len(total_failed)} — {'; '.join(total_failed)}")
        print(f"{'='*70}")

    return total, total_failed
