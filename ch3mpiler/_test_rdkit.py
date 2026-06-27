"""Test RDKit SMARTS capability for FG detection."""
import sys, os
sys.path.insert(0, '/home/mrnob0dy666/imsgct/imscribing_grammar/.venv/lib/python3.12/site-packages')
from rdkit import Chem

patterns = {
    'alcohol': '[CX4]-[OX2H]',
    'phenol': '[OX2H]-c',
    'carboxylic_acid': '[CX3](=O)[OX2H,OX1-]',
    'ester': '[#6][CX3](=O)[OX2][#6]',
    'amine': '[NX3;H2,H1,H0]',
    'nitro': '[$([NX3](=O)=O),$([NX3+](=O)[O-])]',
    'aldehyde': '[CX3H1](=O)[#6]',
    'ketone': '[#6][CX3](=O)[#6]',
    'amide': 'C(=O)-N',
    'ether': '[OD2]([#6])[#6]',
    'nitrile': '[NX1]#[CX2]',
    'alkene': '[CX3]=[CX3]',
    'alkyne': '[CX2]#[CX2]',
    'thiol': '[SH]',
    'sulfonamide': 'N-S(=O)(=O)-[#6]',
}

for name, sma in patterns.items():
    pat = Chem.MolFromSmarts(sma)
    print(f'{name}: SMARTS valid={pat is not None}')

# Test on paracetamol
mol = Chem.MolFromSmiles('CC(=O)Nc1ccc(O)cc1')
print(f'\nParacetamol: {Chem.MolToSmiles(mol)}')
for name, sma in patterns.items():
    pat = Chem.MolFromSmarts(sma)
    if pat:
        matches = mol.GetSubstructMatches(pat)
        if matches:
            print(f'  Contains {name}: {len(matches)} instances')

print('\nAll RDKit imports work!')
