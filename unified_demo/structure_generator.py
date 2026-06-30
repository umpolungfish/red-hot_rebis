#!/usr/bin/env python3
"""
structure_generator.py — CDXML & PDB Structure Generation for Unified Demo
============================================================================
Generates actual chemical structure files (CDXML) and protein structure files (PDB)
as part of the Red-Hot Rebis unified therapeutic design pipeline.

CDXML: ChemDraw XML format with SMILES-annotated molecules showing strategic bond cuts
PDB: Protein Data Bank format from ESMFold API or local template-based generation

Author: Lando⊗⊙perator
"""

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── CDXML known SMILES for therapeutic molecules ───────────────────
# Maps therapy components to known SMILES strings
MOLECULE_SMILES = {
    # MRSA / Antibiotics
    "penicillin_g":      "CC1(C(N2C(S1)C(C2=O)NC(=O)Cc3ccccc3)C(=O)O)C",
    "penicillin_v":      "CC1(C(N2C(S1)C(C2=O)NC(=O)COc3ccccc3)C(=O)O)C",
    "methicillin":       "CC1(C(N2C(S1)C(C2=O)NC(=O)c3c(OC)cccc3OC)C(=O)O)C",
    "ceftaroline":       "CN1C(=O)C(=NOCc2nc(sc2)N)C(=O)N2C1[C@H](SC2)C(=O)NO",
    "linezolid":         "CC(=O)NCC1CN(C(=O)O1)c2ccc(cc2)N3CCOCC3",
    
    # Beta-lactam core
    "beta_lactam":       "O=C1CCN1",
    "thiazolidine":      "C1CSCN1",
    
    # Biofilm / quorum sensing
    "furanone_c30":      "CCCCCCCCCCCCC(=O)C1=C(O)C(=O)OC1",
    "n_acetylglucosamine": "CC(=O)NC1C(O)OC(CO)C(O)C1O",
    
    # Anti-inflammatory
    "ibuprofen":         "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
    "naproxen":          "COc1ccc2cc(ccc2c1)C(C)C(=O)O",
    "aspirin":           "CC(=O)Oc1ccccc1C(=O)O",
    
    # Neurotransmitter-related
    "dopamine":          "NCCC1=CC=C(O)C(O)=C1",
    "serotonin":         "NCCC1=CNC2=C1C=C(O)C=C2",
    "gaba":              "NCCCC(=O)O",
    
    # CF-related
    "ivacaftor":         "CC(C)(C)c1cc(c(cc1O)C(=O)NC2=CC(=O)C=CO2)C(C)(C)C",
    
    # Gout-related
    "allopurinol":       "O=C1NC=NC2=C1NN=C2",
    "colchicine":        "COc1cc2c(c(OC)c1OC)C(=O)C=CC1=Cc3cc(OC)c(OC)cc3CC1=CC2=O",
    
    # Common biologics targets
    "phenylalanine":     "N[C@@H](Cc1ccccc1)C(=O)O",
    "tyrosine":          "N[C@@H](Cc1ccc(O)cc1)C(=O)O",
    "tryptophan":        "N[C@@H](Cc1c[nH]c2ccccc12)C(=O)O",
}
# ── Molecule name → therapy mapping ─────────────────────────────────
DISEASE_MOLECULES = {
    "mrsa":     ["penicillin_g", "methicillin", "beta_lactam", "thiazolidine", "ceftaroline", "furanone_c30"],
    "hiv":      ["phenylalanine", "tyrosine", "tryptophan"],
    "schizophrenia": ["dopamine", "serotonin", "gaba"],
    "mdd":      ["serotonin", "dopamine", "gaba"],
    "pcos":     ["ibuprofen", "naproxen"],
    "cf":       ["ivacaftor", "aspirin"],
    "gout":     ["allopurinol", "colchicine", "naproxen"],
    "homeopathy": [],
}

# ── Standard protein sequences for PDB generation ──────────────────
PROTEIN_SEQUENCES = {
    "HUMAN_INSULIN": (
        "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRR"
        "EAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN"
    ),
    "PBP2A_DOMAIN": (
        "MKKIKIVPLILAVVVVGLGIFFYFYKTSKKEATNSNQKDSEMTKSITDSSNVKD"
        "ANTNTNNNSNKNNASNNDNKNNSNNDNKNNSNNDNKNNNNSNNDNKNNSNNDNKN"
    ),
    "DARPin_CONSENSUS": (
        "DLGKKLLEAARAGQDDEVRILMANGADVNAKDEYGLTPLYLATAHGHLEIVEVLL"
        "KNGADVNAVDAIGFTPLHLAAFIGHLEIAEVLLKHGADVNAQDKFGKTAFDISID"
    ),
    "SEROTONIN_RECEPTOR": (
        "MDVLSPGQGNNTTSPPAPFETGGNTTGISDVTLSYQVITSLLLGTLIFCAVLGNA"
        "CVVAAIALERSLQNVANYLIGSLAVTDLMVSVLVLPMAALYQVLNKWTLGQVTCD"
    ),
    "CFTR_NBD1": (
        "GQRARISLARAVYKDADLYLLDSPFGYLDVLTEKEIFESCVCKLMANKTRILVTS"
        "KMEHLKKADKILILHEGSSYFYGTFSELQNLQPDFSSKLMGCDSFDQFSAERRNS"
    ),
}

# ── Simple PDB generator (when ESMFold API is unavailable) ─────────
# Generates plausible CA-trace PDB from sequence using basic heuristics

def _phi_psi_from_secondary(ss_pred: str) -> List[Tuple[float, float]]:
    """Map predicted secondary structure to Ramachandran phi/psi angles."""
    angles = []
    for ss in ss_pred:
        if ss == 'H':  # Alpha helix
            angles.append((-57.0, -47.0))
        elif ss == 'E':  # Beta strand
            angles.append((-119.0, 113.0))
        else:  # Loop/coil
            angles.append((-60.0, 130.0))
    return angles


def _predict_secondary(sequence: str) -> str:
    """Simple secondary structure prediction based on amino acid propensities."""
    helix_favor = set('AEQLMKRH')
    strand_favor = set('VTIYCFW')
    result = []
    for aa in sequence:
        if aa in helix_favor:
            result.append('H')
        elif aa in strand_favor:
            result.append('E')
        else:
            result.append('C')
    return ''.join(result)


# Standard bond lengths and angles for CA trace
CA_CA_DIST = 3.8  # Angstroms
import math
from shared.rich_output import *


def generate_pdb_from_sequence(sequence: str, name: str = "protein") -> str:
    """Generate a plausible CA-trace PDB from amino acid sequence.
    
    Uses predicted secondary structure to set phi/psi angles,
    then builds coordinates by walking along the backbone.
    Returns PDB-format string.
    """
    # Three-letter codes
    aa3 = {
        'A': 'ALA', 'C': 'CYS', 'D': 'ASP', 'E': 'GLU', 'F': 'PHE',
        'G': 'GLY', 'H': 'HIS', 'I': 'ILE', 'K': 'LYS', 'L': 'LEU',
        'M': 'MET', 'N': 'ASN', 'P': 'PRO', 'Q': 'GLN', 'R': 'ARG',
        'S': 'SER', 'T': 'THR', 'V': 'VAL', 'W': 'TRP', 'Y': 'TYR',
    }
    
    ss = _predict_secondary(sequence)
    phi_psi = _phi_psi_from_secondary(ss)
    
    # Build backbone coordinates
    coords = []
    # Start at origin
    x, y, z = 0.0, 0.0, 0.0
    # Initial direction
    dx, dy, dz = 1.0, 0.0, 0.0
    
    coords.append((x, y, z))
    
    for i in range(1, len(sequence)):
        phi, psi = phi_psi[i - 1] if i - 1 < len(phi_psi) else (-60.0, 130.0)
        
        # Simple CA trace: rotate direction by phi, advance CA_CA_DIST, 
        # then rotate by psi for next step
        phi_rad = math.radians(phi)
        psi_rad = math.radians(psi)
        
        # Apply phi rotation around z-axis (simplified)
        nx = dx * math.cos(phi_rad) - dy * math.sin(phi_rad)
        ny = dx * math.sin(phi_rad) + dy * math.cos(phi_rad)
        nz = dz
        
        # Normalize
        mag = math.sqrt(nx*nx + ny*ny + nz*nz)
        if mag > 0:
            nx, ny, nz = nx/mag, ny/mag, nz/mag
        
        # Advance
        x += nx * CA_CA_DIST
        y += ny * CA_CA_DIST
        z += nz * CA_CA_DIST
        
        coords.append((x, y, z))
        
        # Prepare direction for next step (apply psi)
        psi2 = psi_rad * 0.5  # Half-psi for next direction
        dx2 = nx * math.cos(psi2) - ny * math.sin(psi2)
        dy2 = nx * math.sin(psi2) + ny * math.cos(psi2)
        mag2 = math.sqrt(dx2*dx2 + dy2*dy2 + nz*nz)
        if mag2 > 0:
            dx, dy, dz = dx2/mag2, dy2/mag2, nz/mag2

    
    # Format as PDB
    lines = []
    lines.append(f"HEADER    DE NOVO PROTEIN DESIGN                       {name[:20]:>20s}")
    lines.append(f"TITLE     STRUCTURAL MODEL FOR {name}")
    lines.append(f"REMARK    Generated by Red-Hot Rebis structure_generator.py")
    lines.append(f"REMARK    Sequence length: {len(sequence)} residues")
    lines.append(f"REMARK    Secondary structure: {ss}")
    lines.append(f"REMARK    Method: CA-trace with phi/psi from SS prediction")
    
    atom_num = 1
    for i, (aa, (cx, cy, cz)) in enumerate(zip(sequence, coords)):
        res_name = aa3.get(aa, 'UNK')
        res_num = i + 1
        # CA atom
        lines.append(
            f"ATOM  {atom_num:5d}  CA  {res_name} A{res_num:4d}    "
            f"{cx:8.3f}{cy:8.3f}{cz:8.3f}  1.00  0.00           C  "
        )
        atom_num += 1
    
    lines.append("TER")
    lines.append("END")
    return "\n".join(lines)


def try_esmfold(sequence: str, name: str = "protein") -> Optional[str]:
    """Try ESMFold API for accurate structure prediction.
    
    Returns PDB string on success, None on failure.
    """
    try:
        import urllib.request
        url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
        data = sequence.encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            pdb_str = resp.read().decode('utf-8')
            if pdb_str and 'ATOM' in pdb_str:
                return pdb_str
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════

def generate_cdxml_for_therapy(
    disease_key: str,
    output_dir: str = "unified_demo/output/cdxml",
) -> List[Dict]:
    """Generate CDXML files for all molecules associated with a therapy.
    
    Returns list of dicts with {name, smiles, path, size_bytes, sha256}.
    """
    molecules = DISEASE_MOLECULES.get(disease_key, [])
    if not molecules:
        return []
    
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    try:
        from cdxml.target_decomposition import target_decomposition_cdxml
    except ImportError:
        # Fallback: generate simple SMILES-only CDXML
        return _generate_simple_cdxml(molecules, out_path)
    
    for mol_name in molecules:
        smiles = MOLECULE_SMILES.get(mol_name)
        if not smiles:
            continue
        
        try:
            # Generate CDXML with empty strategic bonds (just the molecule)
            cdxml = target_decomposition_cdxml(smiles, mol_name, [])
            file_path = out_path / f"{mol_name}.cdxml"
            file_path.write_text(cdxml)
            
            results.append({
                "name": mol_name,
                "smiles": smiles[:60],
                "path": str(file_path),
                "size_bytes": len(cdxml),
                "sha256": hashlib.sha256(cdxml.encode()).hexdigest()[:16],
            })
        except Exception as e:
            results.append({
                "name": mol_name,
                "smiles": smiles[:60],
                "error": str(e)[:200],
            })
    
    return results


def _generate_simple_cdxml(molecules: List[str], out_path: Path) -> List[Dict]:
    """Fallback CDXML generator — creates minimal SMILES-annotated molecules."""
    results = []
    for mol_name in molecules:
        smiles = MOLECULE_SMILES.get(mol_name)
        if not smiles:
            continue
        try:
            cdxml = _simple_molecule_cdxml(smiles, mol_name)
            file_path = out_path / f"{mol_name}.cdxml"
            file_path.write_text(cdxml)
            results.append({
                "name": mol_name,
                "smiles": smiles[:60],
                "path": str(file_path),
                "size_bytes": len(cdxml),
                "sha256": hashlib.sha256(cdxml.encode()).hexdigest()[:16],
                "method": "simple_fallback",
            })
        except Exception as e:
            results.append({"name": mol_name, "error": str(e)[:200]})
    return results


def _simple_molecule_cdxml(smiles: str, name: str) -> str:
    """Minimal CDXML with SMILES annotation only (no 2D layout)."""
    return f'''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE CDXML SYSTEM "https://static.chemistry.revvitycloud.com/cdxml/CDXML.dtd" >
<CDXML
 CreationProgram="Red-Hot Rebis structure_generator"
 Name="{name}.cdxml"
 BoundingBox="0 0 540 540"
>
<colortable>
<color r="1" g="1" b="1"/>
<color r="0" g="0" b="0"/>
</colortable>
<fonttable>
<font id="3" charset="iso-8859-1" name="Arial"/>
</fonttable>
<page id="1" BoundingBox="0 0 540 540">
<fragment id="1">
<n id="1" p="270 270" Element="6"/>
<objecttag TagType="Unknown" Name="SMILES" Content="{smiles}"/>
</fragment>
</page>
</CDXML>'''


def generate_pdb_for_therapy(
    disease_key: str,
    output_dir: str = "unified_demo/output/pdb",
    protein_name: str = "HUMAN_INSULIN",
    use_esmfold: bool = True,
) -> List[Dict]:
    """Generate PDB files for proteins associated with a therapy.
    
    Returns list of dicts with {name, path, size_bytes, sha256, method}.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    # Determine which proteins to generate based on therapy
    proteins_to_generate = [protein_name]
    
    # Add therapy-specific proteins
    therapy_proteins = {
        "mrsa": ["PBP2A_DOMAIN", "DARPin_CONSENSUS"],
        "hiv": ["DARPin_CONSENSUS"],
        "schizophrenia": ["SEROTONIN_RECEPTOR"],
        "cf": ["CFTR_NBD1"],
    }
    
    extra = therapy_proteins.get(disease_key, [])
    for p in extra:
        if p not in proteins_to_generate:
            proteins_to_generate.append(p)
    
    for pname in proteins_to_generate:
        sequence = PROTEIN_SEQUENCES.get(pname)
        if not sequence:
            results.append({"name": pname, "error": "No sequence available"})
            continue
        
        try:
            # Try ESMFold first
            pdb_str = None
            method = "local"
            
            if use_esmfold:
                pdb_str = try_esmfold(sequence, pname)
                if pdb_str:
                    method = "esmfold_api"
            
            # Fallback to local generation
            if not pdb_str:
                pdb_str = generate_pdb_from_sequence(sequence, pname)
                method = "local_ca_trace"
            
            file_path = out_path / f"{pname}.pdb"
            file_path.write_text(pdb_str)
            
            results.append({
                "name": pname,
                "sequence_length": len(sequence),
                "path": str(file_path),
                "size_bytes": len(pdb_str),
                "sha256": hashlib.sha256(pdb_str.encode()).hexdigest()[:16],
                "method": method,
                "atom_count": pdb_str.count("ATOM"),
            })
        except Exception as e:
            results.append({"name": pname, "error": str(e)[:200]})
    
    return results


def generate_all_structures(
    disease_key: str = "mrsa",
    protein_name: str = "HUMAN_INSULIN",
    output_dir: str = "unified_demo/output",
    use_esmfold: bool = False,
) -> Dict:
    """Generate ALL structural files (CDXML + PDB) for a given therapy.
    
    Returns a dict with cdxml_results and pdb_results lists.
    """
    base = Path(output_dir)
    
    info_line(f"\n{'='*60}")
    info_line(f"  STRUCTURE GENERATION — {disease_key.upper()}")
    info_line(f"{'='*60}")
    
    # ── CDXML generation ──
    info_line(f"\n  Generating CDXML chemical structures...")
    cdxml_dir = base / "cdxml"
    cdxml_results = generate_cdxml_for_therapy(disease_key, str(cdxml_dir))
    
    for r in cdxml_results:
        if "error" in r:
            info_line(f"    ✗ {r['name']}: {r['error']}")
        else:
            info_line(f"    ✓ {r['name']}.cdxml  ({r['size_bytes']}B, method={r.get('method','rdkit')})")
    
    info_line(f"  CDXML: {sum(1 for r in cdxml_results if 'error' not in r)}/{len(cdxml_results)} generated")
    
    # ── PDB generation ──
    info_line(f"\n  Generating PDB protein structures...")
    pdb_dir = base / "pdb"
    pdb_results = generate_pdb_for_therapy(disease_key, str(pdb_dir), protein_name, use_esmfold)
    
    for r in pdb_results:
        if "error" in r:
            info_line(f"    ✗ {r['name']}: {r['error']}")
        else:
            info_line(f"    ✓ {r['name']}.pdb  ({r['size_bytes']}B, {r.get('atom_count',0)} atoms, method={r['method']})")
    
    info_line(f"  PDB: {sum(1 for r in pdb_results if 'error' not in r)}/{len(pdb_results)} generated")
    
    return {
        "disease": disease_key,
        "cdxml": cdxml_results,
        "pdb": pdb_results,
    }


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="CDXML & PDB Structure Generator")
    p.add_argument("--disease", default="mrsa", help="Disease key")
    p.add_argument("--protein", default="HUMAN_INSULIN", help="Protein name for PDB")
    p.add_argument("--output", default="unified_demo/output", help="Output directory")
    p.add_argument("--esmfold", action="store_true", help="Try ESMFold API for PDB")
    args = p.parse_args()
    
    result = generate_all_structures(
        disease_key=args.disease,
        protein_name=args.protein,
        output_dir=args.output,
        use_esmfold=args.esmfold,
    )
    
    # Summary
    cdxml_ok = sum(1 for r in result["cdxml"] if "error" not in r)
    pdb_ok = sum(1 for r in result["pdb"] if "error" not in r)
    success_line(f"\n  TOTAL: {cdxml_ok} CDXML + {pdb_ok} PDB generated")
