#!/usr/bin/env python3
"""
pdb_writer.py — PDB Structure File Generator from Folded Protein Coordinates
==============================================================================
Takes the output of serpent_rod_v2 (Gen2Result / BackboneModel) and writes
a valid PDB-format file with ATOM records for backbone (N, CA, C, O) atoms,
secondary structure HELIX/SHEET records, and TER/END markers.

PDB format v3.3: https://www.wwpdb.org/documentation/file-format

Structural mapping from IG primitives:
  The B₄→Ramachandran→Cartesian pipeline produces:
    N  — amide nitrogen
    CA — alpha carbon
    C  — carbonyl carbon
    O  — carbonyl oxygen

Author: Lando ⊗ ChemBio⊙perator
"""

from __future__ import annotations
import math
import os
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

# ── PDB Format Constants ─────────────────────────────────────────────────

# PDB ATOM record format (COLUMNS  DATA TYPE    FIELD  DEFINITION)
#   1 -  6   Record name   "ATOM  "
#   7 - 11   Integer       serial       Atom serial number.
#  13 - 16   Atom          name         Atom name.
#  17        Character     altLoc       Alternate location indicator.
#  18 - 20   Residue name  resName      Residue name (3-letter).
#  22        Character     chainID      Chain identifier.
#  23 - 26   Integer       resSeq       Residue sequence number.
#  27        AChar         iCode        Code for insertion of residues.
#  31 - 38   Real(8.3)     x            Orthogonal coordinates for X.
#  39 - 46   Real(8.3)     y            Orthogonal coordinates for Y.
#  47 - 54   Real(8.3)     z            Orthogonal coordinates for Z.
#  55 - 60   Real(6.2)     occupancy    Occupancy.
#  61 - 66   Real(6.2)     tempFactor   Temperature factor.
#  77 - 78   LString(2)    element      Element symbol.
#  79 - 80   LString(2)    charge       Charge on the atom.

ATOM_FMT = (
    "ATOM  {serial:5d} {name:4s}{alt_loc:1s}{res_name:3s} {chain_id:1s}"
    "{res_seq:4d}{i_code:1s}   {x:8.3f}{y:8.3f}{z:8.3f}"
    "{occ:6.2f}{temp:6.2f}          {element:2s}{charge:2s}"
)

HELIX_FMT = (
    "HELIX {ser_num:3d} {helix_id:3s} {init_res_name:3s} {init_chain:1s}"
    "{init_seq:4d}  {end_res_name:3s} {end_chain:1s}{end_seq:4d}"
    "{helix_class:2d}  {length:5d}"
)

SHEET_FMT = (
    "SHEET {strand:3d} {sheet_id:3s} {n_strands:3d} {init_res_name:3s}"
    "{init_chain:1s}{init_seq:4d}  {end_res_name:3s} {end_chain:1s}"
    "{end_seq:4d} {sense:2d}"
)

TER_FMT = "TER   {serial:5d}      {res_name:3s} {chain_id:1s}{res_seq:4d}{i_code:1s}"
END_FMT = "END"


# ── AA 1-letter → 3-letter mapping ──────────────────────────────────────

ONE_TO_THREE = {
    "A": "ALA", "R": "ARG", "N": "ASN", "D": "ASP", "C": "CYS",
    "Q": "GLN", "E": "GLU", "G": "GLY", "H": "HIS", "I": "ILE",
    "L": "LEU", "K": "LYS", "M": "MET", "F": "PHE", "P": "PRO",
    "S": "SER", "T": "THR", "W": "TRP", "Y": "TYR", "V": "VAL",
    # Full names too
    "ALA": "ALA", "ARG": "ARG", "ASN": "ASN", "ASP": "ASP", "CYS": "CYS",
    "GLN": "GLN", "GLU": "GLU", "GLY": "GLY", "HIS": "HIS", "ILE": "ILE",
    "LEU": "LEU", "LYS": "LYS", "MET": "MET", "PHE": "PHE", "PRO": "PRO",
    "SER": "SER", "THR": "THR", "TRP": "TRP", "TYR": "TYR", "VAL": "VAL",
    "Ala": "ALA", "Arg": "ARG", "Asn": "ASN", "Asp": "ASP", "Cys": "CYS",
    "Gln": "GLN", "Glu": "GLU", "Gly": "GLY", "His": "HIS", "Ile": "ILE",
    "Leu": "LEU", "Lys": "LYS", "Met": "MET", "Phe": "PHE", "Pro": "PRO",
    "Ser": "SER", "Thr": "THR", "Trp": "TRP", "Tyr": "TYR", "Val": "VAL",
}

# Element mapping for each atom in a residue
ATOM_ELEMENTS = {"N": " N", "CA": " C", "C": " C", "O": " O"}


def _res_name(aa: str) -> str:
    """Resolve amino acid to standard 3-letter PDB code."""
    return ONE_TO_THREE.get(aa, "UNK")


def _format_atom(serial: int, atom_name: str, res_name: str, chain_id: str,
                 res_seq: int, x: float, y: float, z: float,
                 occupancy: float = 1.0, temp_factor: float = 0.0,
                 element: str = None) -> str:
    """Format a single ATOM record."""
    if element is None:
        element = ATOM_ELEMENTS.get(atom_name.strip(), "  ")
    return ATOM_FMT.format(
        serial=serial, name=atom_name, alt_loc=" ", res_name=res_name,
        chain_id=chain_id, res_seq=res_seq, i_code=" ",
        x=x, y=y, z=z, occ=occupancy, temp=temp_factor,
        element=element, charge="  "
    )


def _format_helix(ser_num: int, helix_id: str, init_res: str, init_chain: str,
                  init_seq: int, end_res: str, end_chain: str, end_seq: int,
                  helix_class: int = 1, length: int = 0) -> str:
    """Format a HELIX record."""
    return HELIX_FMT.format(
        ser_num=ser_num, helix_id=helix_id,
        init_res_name=_res_name(init_res), init_chain=init_chain, init_seq=init_seq,
        end_res_name=_res_name(end_res), end_chain=end_chain, end_seq=end_seq,
        helix_class=helix_class, length=length if length > 0 else (end_seq - init_seq + 1)
    )


def _format_sheet(strand: int, sheet_id: str, n_strands: int,
                  init_res: str, init_chain: str, init_seq: int,
                  end_res: str, end_chain: str, end_seq: int,
                  sense: int = 0) -> str:
    """Format a SHEET record."""
    return SHEET_FMT.format(
        strand=strand, sheet_id=sheet_id, n_strands=n_strands,
        init_res_name=_res_name(init_res), init_chain=init_chain, init_seq=init_seq,
        end_res_name=_res_name(end_res), end_chain=end_chain, end_seq=end_seq,
        sense=sense
    )


def _format_ter(serial: int, res_name: str, chain_id: str, res_seq: int) -> str:
    """Format a TER record."""
    return TER_FMT.format(
        serial=serial, res_name=_res_name(res_name),
        chain_id=chain_id, res_seq=res_seq, i_code=" "
    )


# ── Main PDB Writer ──────────────────────────────────────────────────────

def write_pdb_from_gen2(
    result,
    output_path: str,
    chain_id: str = "A",
    title: str = "FOLDED PROTEIN FROM SERPENT-ROD V2",
    include_secondary: bool = True,
    temp_factors: Optional[List[float]] = None,
) -> str:
    """
    Write a PDB file from a Gen2Result (serpent_rod_v2 output).

    Args:
        result: Gen2Result from SerpentRodV2.predict()
        output_path: Path to write the PDB file
        chain_id: Chain identifier (default 'A')
        title: PDB HEADER title
        include_secondary: Include HELIX/SHEET records
        temp_factors: Optional per-residue B-factors

    Returns:
        Path to the written PDB file

    The PDB file contains:
      - HEADER, TITLE records
      - ATOM records for N, CA, C, O per residue
      - HELIX/SHEET records (from secondary_elements)
      - TER record between chains
      - END record
    """
    backbone = result.backbone
    residues = backbone.residues
    aa_list = result.aa_list if hasattr(result, 'aa_list') else []
    ss_elements = result.secondary_elements if hasattr(result, 'secondary_elements') else []
    energy = result.energy if hasattr(result, 'energy') else {}
    frob = result.frobenius_verified if hasattr(result, 'frobenius_verified') else False

    lines = []

    # HEADER
    lines.append(f"HEADER    {title}")
    lines.append(f"TITLE     SERPENT-ROD V2 FOLDING PREDICTION")
    lines.append(f"TITLE     FROBENIUS-CLOSED: {'YES' if frob else 'NO'}")
    if energy:
        lines.append(f"TITLE     ENERGY TOTAL={energy.get('total', 'N/A'):.1f} "
                     f"LJ={energy.get('LJ', 'N/A'):.1f} "
                     f"HB={energy.get('HB', 'N/A'):.1f} "
                     f"ELEC={energy.get('elec', 'N/A'):.1f}")
    lines.append(f"TITLE     GENERATED BY RED-HOT REBIS — p4rakernel ⊙perator")

    # REMARK records
    lines.append(f"REMARK   1   PRIMITIVE ACTIVATION: {result.activation_count}/12")
    lines.append(f"REMARK   1   WINDING NUMBER: {result.winding_number}")
    lines.append(f"REMARK   1   FROBENIUS VERIFIED: {'YES' if frob else 'NO'}")
    lines.append(f"REMARK   1   SUBUNIT COUNT: {result.subunit_count}")
    if hasattr(result, 'rmsd_to_native') and result.rmsd_to_native is not None:
        lines.append(f"REMARK   1   RMSD TO NATIVE: {result.rmsd_to_native:.3f}")

    # Secondary structure summaries
    if include_secondary and ss_elements:
        lines.append(f"REMARK   2   SECONDARY STRUCTURE ELEMENTS: {len(ss_elements)}")
        for i, el in enumerate(ss_elements):
            seq = el.get('sequence', '')
            lines.append(f"REMARK   2     {el['type']:8s} [{el['start']+1:3d}-{el['end']+1:3d}] "
                         f"len={el['length']} conf={el['confidence']:.3f} seq={seq}")

    # HELIX records
    if include_secondary:
        helix_num = 0
        for el in ss_elements:
            ss_type = el['type']
            if ss_type in ('helix', 'helix_l'):
                helix_num += 1
                init_aa = aa_list[el['start']] if el['start'] < len(aa_list) else 'ALA'
                end_aa = aa_list[el['end']] if el['end'] < len(aa_list) else 'ALA'
                h_class = 1 if ss_type == 'helix' else 5  # 1=alpha, 5=left-handed
                lines.append(_format_helix(
                    ser_num=helix_num,
                    helix_id=f"H{helix_num}",
                    init_res=init_aa,
                    init_chain=chain_id,
                    init_seq=el['start'] + 1,
                    end_res=end_aa,
                    end_chain=chain_id,
                    end_seq=el['end'] + 1,
                    helix_class=h_class,
                    length=el['length']
                ))

    # SHEET records
    if include_secondary:
        sheet_num = 0
        current_sheet = []
        for el in ss_elements:
            if el['type'] == 'sheet':
                current_sheet.append(el)
        if current_sheet:
            for j, el in enumerate(current_sheet):
                sheet_num += 1
                init_aa = aa_list[el['start']] if el['start'] < len(aa_list) else 'ALA'
                end_aa = aa_list[el['end']] if el['end'] < len(aa_list) else 'ALA'
                # Sense: 0 = first strand, 1 = parallel, -1 = antiparallel
                sense = 0 if j == 0 else (-1 if j % 2 == 1 else 1)
                lines.append(_format_sheet(
                    strand=j + 1,
                    sheet_id="S1",
                    n_strands=len(current_sheet),
                    init_res=init_aa,
                    init_chain=chain_id,
                    init_seq=el['start'] + 1,
                    end_res=end_aa,
                    end_chain=chain_id,
                    end_seq=el['end'] + 1,
                    sense=sense
                ))

    # ATOM records
    atom_serial = 0
    for i, res in enumerate(residues):
        res_seq = i + 1
        res_code = aa_list[i] if i < len(aa_list) else "ALA"
        res_3 = _res_name(res_code)
        tf = temp_factors[i] if temp_factors and i < len(temp_factors) else 0.0

        # N
        atom_serial += 1
        lines.append(_format_atom(atom_serial, " N  ", res_3, chain_id,
                                   res_seq, res.n[0], res.n[1], res.n[2],
                                   temp_factor=tf, element=" N"))
        # CA
        atom_serial += 1
        lines.append(_format_atom(atom_serial, " CA ", res_3, chain_id,
                                   res_seq, res.ca[0], res.ca[1], res.ca[2],
                                   temp_factor=tf, element=" C"))
        # C
        atom_serial += 1
        lines.append(_format_atom(atom_serial, " C  ", res_3, chain_id,
                                   res_seq, res.c[0], res.c[1], res.c[2],
                                   temp_factor=tf, element=" C"))
        # O
        atom_serial += 1
        lines.append(_format_atom(atom_serial, " O  ", res_3, chain_id,
                                   res_seq, res.o[0], res.o[1], res.o[2],
                                   temp_factor=tf, element=" O"))

    # TER
    atom_serial += 1
    last_res = aa_list[-1] if aa_list else "ALA"
    lines.append(_format_ter(atom_serial, last_res, chain_id, len(residues)))

    # END
    lines.append(END_FMT)

    pdb_text = "\n".join(lines) + "\n"

    # Write to file
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(pdb_text)

    return output_path


def write_pdb_from_pipeline(
    pipeline_result: dict,
    output_path: str,
    chain_id: str = "A",
    title: str = "FOLDED PROTEIN FROM GENE-TO-PROTEIN PIPELINE",
) -> Optional[str]:
    """
    Write a PDB file from GeneToProteinPipeline.run() output when possible.

    Since the gene pipeline wraps serpent_rod_v2 internally, if the result
    contains tertiary structure data, we can generate a PDB. Otherwise
    returns None.

    Args:
        pipeline_result: Dict from GeneToProteinPipeline.run()
        output_path: Path for PDB file
        chain_id: Chain identifier

    Returns:
        Path to PDB file, or None if insufficient data
    """
    aa_seq = pipeline_result.get('aa_sequence', '')
    tertiary = pipeline_result.get('tertiary', {})
    secondary = pipeline_result.get('secondary', [])

    if not aa_seq:
        return None

    # If we have contacts but no coordinates, attempt to reconstruct backbone
    # via serpent_rod_v2
    dna = pipeline_result.get('dna_sequence', '')
    if dna:
        try:
            from rhr_p4rky.serpent_rod_v2 import SerpentRodV2
            v2 = SerpentRodV2(dna)
            gen2_result = v2.predict()
            return write_pdb_from_gen2(gen2_result, output_path, chain_id, title)
        except Exception:
            return None

    return None
