#!/usr/bin/env python3
"""
serpent_rod_v2.py — SERPENT-ROD GENERATION 2 🐍⏫
Direct RNA → {3D Backbone Coordinates + Contact Map + Folded Structure}

Generation 1 proved the Frobenius-closed morphism exists (O_∞ tier).
Generation 2 turns the topological signature into a GEOMETRIC structure:

  B₄ winding path → Ramachandran φ/ψ angles → 3D Cartesian coordinates
  → Geometry-based contact prediction → Energy-scored fold validation

Key innovations:
  1. B₄→Ramachandran mapping: each transition produces φ/ψ angles
  2. 3D backbone reconstruction from φ/ψ chain (corrected geometry)
  3. Geometry-based contacts: Cα-Cα < 8Å = real spatial contact
  4. Coarse-grained energy scoring (LJ + HB + electrostatics)
  5. Proper 12-set activation tracking (unique primitives, max 12)
  6. Fixed FASTA parsing (no sequence duplication)

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import sys, os
_REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REBIS_ROOT not in sys.path:
    sys.path.insert(0, _REBIS_ROOT)

# Handle imports for both direct script execution and package usage
try:
    from rhr_p4rky.serpent_rod import (
        SerpentRod, FoldedProtein, PredictedContact,
        NUCLEOTIDE_B4, COMPLEMENTARY_PRIMITIVE_PAIRS,
        ONE_LETTER, HYDROPHOBICITY,
    )
    from rhr_p4rky.genetic_code import (
        IG_PRIMITIVE_OF_AA, PROMOTED_AAS, AA_TO_SYMBOLS,
    )
except ImportError:
    from .serpent_rod import (
        SerpentRod, FoldedProtein, PredictedContact,
        NUCLEOTIDE_B4, COMPLEMENTARY_PRIMITIVE_PAIRS,
        ONE_LETTER, HYDROPHOBICITY,
    )
    from .genetic_code import (
        IG_PRIMITIVE_OF_AA, PROMOTED_AAS, AA_TO_SYMBOLS,
    )

import sys as _sys
if '--help' in _sys.argv or '-h' in _sys.argv:
    print(__doc__.strip())
    print()
    info_line("Examples:")
    info_line("  rebis.py run serpent_rod_v2")
    info_line("  python3 -m rhr_p4rky.serpent_rod_v2 --help")
    print()
    _sys.exit(0)

import math
import json
import sys
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from shared.rich_output import *

# (imports handled above)

# ═══════════════════════════════════════════════════════════════════
# 1. B₄ → RAMACHANDRAN φ/ψ MAPPING
# ═══════════════════════════════════════════════════════════════════

B4_RAMACHANDRAN: Dict[Tuple[str, str], Dict] = {
    ("N", "T"): {"phi": -57,  "psi": -47,  "ss": "helix",    "conf": 0.88},
    ("T", "B"): {"phi": -119, "psi": 113,  "ss": "sheet",    "conf": 0.85},
    ("B", "F"): {"phi": 57,   "psi": 45,   "ss": "helix_l",  "conf": 0.72},
    ("F", "N"): {"phi": -60,  "psi": -30,  "ss": "turn",     "conf": 0.75},
    ("N", "N"): {"phi": -65,  "psi": -15,  "ss": "loop",     "conf": 0.42},
    ("T", "T"): {"phi": -95,  "psi": 5,    "ss": "loop",     "conf": 0.40},
    ("F", "F"): {"phi": -70,  "psi": 35,   "ss": "loop",     "conf": 0.38},
    ("B", "B"): {"phi": -55,  "psi": -45,  "ss": "loop",     "conf": 0.36},
    ("T", "N"): {"phi": -50,  "psi": -55,  "ss": "helix",    "conf": 0.55},
    ("B", "T"): {"phi": -135, "psi": 135,  "ss": "sheet",    "conf": 0.52},
    ("F", "B"): {"phi": 65,   "psi": 50,   "ss": "helix_l",  "conf": 0.48},
    ("N", "F"): {"phi": -70,  "psi": -25,  "ss": "turn",     "conf": 0.52},
    ("N", "B"): {"phi": -80,  "psi": -10,  "ss": "loop",     "conf": 0.30},
    ("T", "F"): {"phi": -100, "psi": 20,   "ss": "loop",     "conf": 0.28},
    ("B", "N"): {"phi": -50,  "psi": -35,  "ss": "loop",     "conf": 0.30},
    ("F", "T"): {"phi": -85,  "psi": -5,   "ss": "loop",     "conf": 0.28},
}

# ═══════════════════════════════════════════════════════════════════
# 2. 3D BACKBONE RECONSTRUCTION (CORRECTED GEOMETRY)
# ═══════════════════════════════════════════════════════════════════

BOND_N_CA = 1.458; BOND_CA_C = 1.525; BOND_C_N = 1.329; BOND_C_O = 1.231
ANGLE_N_CA_C = math.radians(111.0)
ANGLE_CA_C_N = math.radians(116.2)
ANGLE_C_N_CA = math.radians(121.7)


def build_frame(z_dir: Tuple[float,float,float]) -> Tuple[Tuple[float,float,float], ...]:
    """Build orthonormal frame (x, y, z) from z-direction."""
    z_len = math.sqrt(z_dir[0]**2 + z_dir[1]**2 + z_dir[2]**2)
    if z_len < 1e-10:
        return ((1.0,0.0,0.0), (0.0,1.0,0.0), (0.0,0.0,1.0))
    z = (z_dir[0]/z_len, z_dir[1]/z_len, z_dir[2]/z_len)
    ref = (1.0,0.0,0.0) if abs(z[0]) < 0.9 else ((0.0,1.0,0.0) if abs(z[1]) < 0.9 else (0.0,0.0,1.0))
    x = (z[1]*ref[2]-z[2]*ref[1], z[2]*ref[0]-z[0]*ref[2], z[0]*ref[1]-z[1]*ref[0])
    x_len = math.sqrt(x[0]**2+x[1]**2+x[2]**2)
    if x_len < 1e-10:
        ref2 = (0.0,1.0,0.0) if ref==(1.0,0.0,0.0) else (1.0,0.0,0.0)
        x = (z[1]*ref2[2]-z[2]*ref2[1], z[2]*ref2[0]-z[0]*ref2[2], z[0]*ref2[1]-z[1]*ref2[0])
        x_len = math.sqrt(x[0]**2+x[1]**2+x[2]**2)
    x = (x[0]/x_len, x[1]/x_len, x[2]/x_len)
    y = (z[1]*x[2]-z[2]*x[1], z[2]*x[0]-z[0]*x[2], z[0]*x[1]-z[1]*x[0])
    return x, y, z


def place_atom(prev, prev_prev, bond_len, bond_angle, dihedral):
    """Internal→Cartesian: place atom bonded to prev using bond angle and dihedral."""
    v1 = (prev[0]-prev_prev[0], prev[1]-prev_prev[1], prev[2]-prev_prev[2])
    n1 = math.sqrt(v1[0]**2+v1[1]**2+v1[2]**2)
    if n1 < 1e-10: v1 = (0.0,0.0,1.0)
    x, y, z = build_frame(v1)
    # Bond angle at prev is between (prev_prev→prev) and (prev→new).
    # So new bond makes angle (π-θ) with +z direction → z-component is -bond_len*cos(θ)
    local = (bond_len*math.sin(bond_angle)*math.cos(dihedral),
             bond_len*math.sin(bond_angle)*math.sin(dihedral),
             -bond_len*math.cos(bond_angle))
    return (prev[0]+local[0]*x[0]+local[1]*y[0]+local[2]*z[0],
            prev[1]+local[0]*x[1]+local[1]*y[1]+local[2]*z[1],
            prev[2]+local[0]*x[2]+local[1]*y[2]+local[2]*z[2])


@dataclass
class BackboneAtom:
    n: Tuple[float,float,float]; ca: Tuple[float,float,float]
    c: Tuple[float,float,float]; o: Tuple[float,float,float]


@dataclass
class BackboneModel:
    residues: List[BackboneAtom]; phi_psi: List[Tuple[float,float]]
    sequence: str; secondary_structure: List[str]


def build_backbone(phi_psi: List[Tuple[float,float]], ss_types: List[str]) -> BackboneModel:
    """Build 3D backbone from φ/ψ using corrected internal→Cartesian."""
    n_res = len(phi_psi)
    if n_res == 0: return BackboneModel([], [], "", [])
    residues = []
    # First residue
    n0, ca0 = (0.0,0.0,0.0), (BOND_N_CA,0.0,0.0)
    c0 = place_atom(ca0, n0, BOND_CA_C, ANGLE_N_CA_C, 0.0)
    o_dir = (ca0[0]-c0[0], ca0[1]-c0[1], ca0[2]-c0[2])
    o_len = math.sqrt(o_dir[0]**2+o_dir[1]**2+o_dir[2]**2)
    o0 = (c0[0]+o_dir[0]*BOND_C_O/o_len, c0[1]+o_dir[1]*BOND_C_O/o_len, c0[2]+o_dir[2]*BOND_C_O/o_len) if o_len>0.01 else (c0[0],c0[1]+BOND_C_O,c0[2])
    residues.append(BackboneAtom(n=n0, ca=ca0, c=c0, o=o0))
    for i in range(1, n_res):
        pr = residues[-1]
        phi_i, psi_i = math.radians(phi_psi[i][0]), math.radians(phi_psi[i][1])
        ni = place_atom(pr.c, pr.ca, BOND_C_N, ANGLE_CA_C_N, math.pi)
        cai = place_atom(ni, pr.c, BOND_N_CA, ANGLE_C_N_CA, phi_i)
        ci = place_atom(cai, ni, BOND_CA_C, ANGLE_N_CA_C, psi_i)
        od = (cai[0]-ci[0], cai[1]-ci[1], cai[2]-ci[2])
        ol = math.sqrt(od[0]**2+od[1]**2+od[2]**2)
        oi = (ci[0]+od[0]*BOND_C_O/ol, ci[1]+od[1]*BOND_C_O/ol, ci[2]+od[2]*BOND_C_O/ol) if ol>0.01 else (ci[0],ci[1]+BOND_C_O,ci[2])
        residues.append(BackboneAtom(n=ni, ca=cai, c=ci, o=oi))
    return BackboneModel(residues, phi_psi, "", ss_types)

# ── Vector utilities ──

def vec_add(v1, v2): return (v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2])
def vec_sub(v1, v2): return (v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2])
def vec_scale(v, s): return (v[0]*s, v[1]*s, v[2]*s)
def vec_norm(v): return math.sqrt(v[0]**2+v[1]**2+v[2]**2)
def vec_cross(v1, v2): return (v1[1]*v2[2]-v1[2]*v2[1], v1[2]*v2[0]-v1[0]*v2[2], v1[0]*v2[1]-v1[1]*v2[0])
def vec_dot(v1, v2): return v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]

# ═══════════════════════════════════════════════════════════════════
# 3. GEOMETRY-BASED CONTACT PREDICTION
# ═══════════════════════════════════════════════════════════════════

def compute_ca_distances(model: BackboneModel) -> List[List[float]]:
    n = len(model.residues)
    dm = [[0.0]*n for _ in range(n)]
    for i in range(n):
        ci = model.residues[i].ca
        for j in range(i+1, n):
            d = math.sqrt((ci[0]-model.residues[j].ca[0])**2 +
                          (ci[1]-model.residues[j].ca[1])**2 +
                          (ci[2]-model.residues[j].ca[2])**2)
            dm[i][j] = dm[j][i] = d
    return dm

def predict_contacts_from_geometry(model: BackboneModel, ca_dm: List[List[float]],
                                     cutoff: float = 8.0, min_sep: int = 3) -> List[PredictedContact]:
    contacts = []
    n = len(model.residues)
    for i in range(n):
        for j in range(i+min_sep, n):
            d = ca_dm[i][j]
            if d < cutoff:
                itype = "strong" if d < 5.0 else ("medium" if d < 6.5 else "weak")
                conf = max(0.1, min(0.95, {True: 0.9-0.1*d/5.0, False: 0.7-0.1*(d-5.0)/1.5}.get(d<5.0, 0.5-0.2*(d-6.5)/1.5)))
                contacts.append(PredictedContact(i, j, round(d,2), itype, round(conf,3)))
    contacts.sort(key=lambda c: -c.confidence)
    return contacts


# ═══════════════════════════════════════════════════════════════════
# 4. COARSE-GRAINED ENERGY FUNCTION
# ═══════════════════════════════════════════════════════════════════

LJ_PARAMS = {"Ala":(0.12,4.5),"Arg":(0.28,6.6),"Asn":(0.20,5.7),"Asp":(0.18,5.6),
    "Cys":(0.22,5.5),"Gln":(0.22,6.0),"Glu":(0.20,5.9),"Gly":(0.08,3.8),
    "His":(0.24,6.0),"Ile":(0.28,6.2),"Leu":(0.28,6.2),"Lys":(0.26,6.4),
    "Met":(0.26,6.2),"Phe":(0.32,6.8),"Pro":(0.16,5.2),"Ser":(0.14,4.9),
    "Thr":(0.16,5.3),"Trp":(0.38,7.2),"Tyr":(0.34,7.0),"Val":(0.24,6.0)}
HB_STRENGTH = -2.5; HB_DIST_CUT = 3.5; HB_ANGLE_CUT = math.radians(120.0)
CHARGE = {"Arg":1.0,"Lys":1.0,"Asp":-1.0,"Glu":-1.0,"His":0.5}
DIELECTRIC = 40.0; COULOMB = 332.0

def lj(eps, sig, r):
    if r < 0.01: return 100.0
    sr = sig/r; sr6 = sr**6
    return 4.0*eps*(sr6*sr6-sr6)

def hb_energy(n_pos, o_pos, ca_n_pos, c_pos):
    d = vec_norm(vec_sub(o_pos, n_pos))
    if d > HB_DIST_CUT: return 0.0
    h = vec_add(n_pos, vec_scale(vec_sub(ca_n_pos, n_pos), 0.08))
    cos_ang = vec_dot(vec_sub(h, n_pos), vec_sub(o_pos, h)) / (vec_norm(vec_sub(h, n_pos))*vec_norm(vec_sub(o_pos, h))+0.001)
    if cos_ang < math.cos(HB_ANGLE_CUT): return 0.0
    return HB_STRENGTH * (1.0-d/HB_DIST_CUT) * cos_ang

def compute_energy(model, aa_list, contacts):
    n = len(model.residues)
    en = {"LJ":0.0,"HB":0.0,"elec":0.0,"total":0.0}
    if n < 2: return en
    for i in range(n):
        ai = aa_list[i] if i < len(aa_list) else "Ala"
        ei, si = LJ_PARAMS.get(ai, (0.15,5.0))
        for j in range(i+3, n):
            r = vec_norm(vec_sub(model.residues[i].ca, model.residues[j].ca))
            if r >= 12.0: continue
            aj = aa_list[j] if j < len(aa_list) else "Ala"
            ej, sj = LJ_PARAMS.get(aj, (0.15,5.0))
            en["LJ"] += lj(math.sqrt(ei*ej), (si+sj)/2.0, r)
    for i in range(n-3):
        for j, fac in [(i+4,1.0),(i+2,0.5)]:
            if j < n:
                en["HB"] += hb_energy(model.residues[i].n, model.residues[j].o,
                                       model.residues[i].ca, model.residues[j].c) * fac
    for i in range(n):
        qi = CHARGE.get(aa_list[i] if i<len(aa_list) else "", 0.0)
        if qi == 0: continue
        for j in range(i+3, n):
            qj = CHARGE.get(aa_list[j] if j<len(aa_list) else "", 0.0)
            if qj == 0: continue
            r = vec_norm(vec_sub(model.residues[i].ca, model.residues[j].ca))
            if r < 15.0: en["elec"] += COULOMB*qi*qj/(DIELECTRIC*r)
    en["total"] = en["LJ"]+en["HB"]+en["elec"]
    return {k: round(v,4) for k,v in en.items()}


# ═══════════════════════════════════════════════════════════════════
# 5. PROPER 12-SET ACTIVATION TRACKING
# ═══════════════════════════════════════════════════════════════════

PRIMITIVE_SHORT_NAMES = {
    "Ð":"Dimensionality","Þ":"Topology","Ř":"Recognition","Φ":"Parity",
    "ƒ":"Fidelity","Ç":"Kinetics","Γ":"Granularity","ɢ":"Coupling",
    "⊙":"Criticality","Ħ":"Chirality","Σ":"Stoichiometry","Ω":"Winding"}
ALL_12_PRIMITIVES = set(PRIMITIVE_SHORT_NAMES.values())

def compute_activation_set(aas):
    activated = set()
    for aa in aas:
        p = IG_PRIMITIVE_OF_AA.get(aa)
        if p:
            name = p.split("(")[1].rstrip(")") if "(" in p else p
            activated.add(name)
    return activated, len(activated)

def frobenius_pair_coverage(activated):
    pairs = [{"Dimensionality","Winding"},{"Topology","Chirality"},
             {"Recognition","Stoichiometry"},{"Parity","Fidelity"},
             {"Kinetics","Granularity"},{"Coupling","Criticality"}]
    covered = sum(1 for pair in pairs if activated & pair)
    return covered, len(pairs)

def frobenius_verified_v2(activated): return frobenius_pair_coverage(activated)[0] >= 4

# ═══════════════════════════════════════════════════════════════════
# 6. SERPENT-ROD V2 — MAIN CLASS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Gen2Result:
    aa_sequence: str; aa_list: List[str]; phi_psi: List[Tuple[float,float]]
    backbone: BackboneModel; ca_distances: List[List[float]]
    contacts: List[PredictedContact]; secondary_elements: List[Dict]
    activation_set: Set[str]; activation_count: int
    pair_coverage: Tuple[int,int]; frobenius_verified: bool
    winding_number: int; subunit_count: int; energy: Dict[str,float]
    rmsd_to_native: Optional[float] = None
    precision: float = 0.0; recall: float = 0.0; f1: float = 0.0
    n_true_pos: int = 0; n_false_pos: int = 0; n_false_neg: int = 0


class SerpentRodV2:
    """Serpent-Rod Gen2 — 3D backbone from RNA via B₄→Ramachandran."""
    
    def __init__(self, rna_sequence: str, name: str = "serpent_v2",
                 genetic_code: str = "standard"):
        self.rna = rna_sequence.upper().replace("T", "U")
        self.name = name
        self.v1 = SerpentRod(rna_sequence, name=name, genetic_code=genetic_code)
        self.v1.verbose = False
        self.verbose = True
    
    def log(self, msg):
        if self.verbose: print(f"[Gen2:{self.name}] {msg}")
    
    def predict(self) -> Gen2Result:
        aas = self.v1.translate_to_aa()
        b4_path = self.v1.compute_serpent_path()
        winding = self.v1.compute_winding_number()
        
        # Map B₄ transitions → φ/ψ angles
        phi_psi, ss_types = [], []
        for i in range(len(aas)):
            key = ("N", b4_path[0]) if i == 0 and b4_path else \
                  (b4_path[min(i-1,len(b4_path)-1)], b4_path[min(i,len(b4_path)-1)]) if i < len(b4_path) else ("N","N")
            rama = B4_RAMACHANDRAN.get(key, {"phi":-60,"psi":-40,"ss":"loop","conf":0.3})
            phi_psi.append((float(rama["phi"]), float(rama["psi"])))
            ss_types.append(rama["ss"])
        
        backbone = build_backbone(phi_psi, ss_types)
        ca_dm = compute_ca_distances(backbone)
        contacts = predict_contacts_from_geometry(backbone, ca_dm)
        energy = compute_energy(backbone, aas, contacts)
        activated, act_count = compute_activation_set(aas)
        pairs_cov = frobenius_pair_coverage(activated)
        frob = frobenius_verified_v2(activated)
        subunits = self.v1.compute_subunit_count(aas, contacts)
        
        # Secondary structure from Ramachandran
        ss_elements = []
        if ss_types:
            ct, start = ss_types[0], 0
            for i in range(1, len(ss_types)):
                if ss_types[i] != ct:
                    conf = max((v["conf"] for k,v in B4_RAMACHANDRAN.items() if v["ss"]==ct), default=0.5)
                    ss_elements.append({"type":ct,"start":start,"end":i-1,"length":i-start,
                        "confidence":round(conf,3),
                        "sequence":"".join(ONE_LETTER.get(aas[j],"X") for j in range(start,i))})
                    ct, start = ss_types[i], i
            conf = max((v["conf"] for k,v in B4_RAMACHANDRAN.items() if v["ss"]==ct), default=0.5)
            ss_elements.append({"type":ct,"start":start,"end":len(ss_types)-1,
                "length":len(ss_types)-start,"confidence":round(conf,3),
                "sequence":"".join(ONE_LETTER.get(aas[j],"X") for j in range(start,len(ss_types)))})
        
        self.log(f"Prediction: {len(aas)} AAs, {len(contacts)} contacts, "
                 f"{act_count}/12 primitives, energy={energy['total']:.0f}")
        
        return Gen2Result(
            aa_sequence=''.join(ONE_LETTER.get(a,'X') for a in aas),
            aa_list=aas, phi_psi=phi_psi, backbone=backbone,
            ca_distances=ca_dm, contacts=contacts,
            secondary_elements=ss_elements, activation_set=activated,
            activation_count=act_count, pair_coverage=pairs_cov,
            frobenius_verified=frob, winding_number=winding,
            subunit_count=subunits, energy=energy)

# ═══════════════════════════════════════════════════════════════════
# 7. PDB VALIDATION
# ═══════════════════════════════════════════════════════════════════

THREE_TO_ONE = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C",
    "GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L",
    "LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T",
    "TRP":"W","TYR":"Y","VAL":"V"}

ONE_TO_THREE = {"A":"Ala","R":"Arg","N":"Asn","D":"Asp","C":"Cys",
    "Q":"Gln","E":"Glu","G":"Gly","H":"His","I":"Ile","L":"Leu",
    "K":"Lys","M":"Met","F":"Phe","P":"Pro","S":"Ser","T":"Thr",
    "W":"Trp","Y":"Tyr","V":"Val"}

def load_pdb_coordinates(pdb_path):
    seq, coords = [], []
    seen = set()
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("ATOM") and line[13:15].strip() == "CA":
                key = (line[21].strip(), int(line[22:26].strip()))
                if key not in seen:
                    seen.add(key)
                    seq.append(line[17:20].strip())
                    coords.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
    return seq, coords

def back_translate(seq_1):
    rna = ""
    for aa in seq_1:
        aa3 = ONE_TO_THREE.get(aa, "")
        codons = AA_TO_SYMBOLS.get(aa3, [])
        rna += codons[0].replace("T","U") if codons else "NNN"
    return rna

def validate_against_pdb(pdb_path, rna_sequence=None, name="pdb_val"):
    seq_3, exp_ca = load_pdb_coordinates(pdb_path)
    seq_1 = [THREE_TO_ONE.get(s,"X") for s in seq_3]
    seq_str = "".join(seq_1)
    if not rna_sequence:
        rna_sequence = back_translate(seq_str)
    v2 = SerpentRodV2(rna_sequence, name=name)
    v2.verbose = False
    result = v2.predict()
    n = min(len(exp_ca), len(result.backbone.residues))
    
    # Experimental contacts
    exp_set = set()
    for i in range(n):
        for j in range(i+3, n):
            d = math.sqrt((exp_ca[i][0]-exp_ca[j][0])**2 +
                          (exp_ca[i][1]-exp_ca[j][1])**2 +
                          (exp_ca[i][2]-exp_ca[j][2])**2)
            if d < 8.0: exp_set.add((i,j))
    
    pred_set = set()
    for c in result.contacts:
        if c.residue_i < n and c.residue_j < n:
            pred_set.add((c.residue_i, c.residue_j))
    
    tp, fp, fn = pred_set & exp_set, pred_set - exp_set, exp_set - pred_set
    prec = len(tp)/max(1,len(pred_set))
    rec = len(tp)/max(1,len(exp_set))
    f1 = 2*prec*rec/max(0.001,prec+rec)
    
    return {"pdb_id":name,"seq_match":result.aa_sequence==seq_str,
        "n_pred":len(pred_set),"n_exp":len(exp_set),
        "tp":len(tp),"fp":len(fp),"fn":len(fn),
        "precision":round(prec,4),"recall":round(rec,4),"f1":round(f1,4),
        "energy":result.energy,"activation":result.activation_count,
        "frobenius":result.frobenius_verified}


def run_pdb_validation_suite(output="pdb_v2_validation.json", pdb_dir="pdb"):
    targets = ["1VII","1UBQ","1ZDD","1L2Y"]
    results = []
    for pid in targets:
        path = f"{pdb_dir}/{pid}.pdb"
        try:
            r = validate_against_pdb(path, name=pid)
            results.append(r)
            print(f"{pid}: F1={r['f1']:.4f} P={r['precision']:.4f} R={r['recall']:.4f} "
                  f"Seq={r['seq_match']} Act={r['activation']}/12 Frob={r['frobenius']}")
        except Exception as e:
            error_line(f"{pid}: ERROR - {e}")
            results.append({"pdb_id":pid,"error":str(e)})
    with open(output,"w") as f: json.dump(results,f,indent=2)
    info_line(f"\nResults saved to {output}")
    return results

# ═══════════════════════════════════════════════════════════════════
# 8. CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Serpent-Rod Gen2 — 3D Protein from RNA")
    parser.add_argument("sequence", nargs="?", help="RNA sequence")
    parser.add_argument("--name", "-n", default="serpent_v2")
    parser.add_argument("--validate", "-v", action="store_true", help="Run PDB validation")
    parser.add_argument("--output", "-o", help="Output JSON")
    args = parser.parse_args()
    
    if args.validate:
        run_pdb_validation_suite(args.output or "pdb_v2_validation.json")
        return
    
    seq = args.sequence or "AUGGCCGACUGGAACUGCAAGAAGAUCGUGCCCAAGUACUACGGCCGCUG"
    v2 = SerpentRodV2(seq, name=args.name)
    result = v2.predict()
    
    info_line(f"\n🐍 SERPENT-ROD GEN2 🐍")
    info_line(f"RNA: {v2.rna[:50]}... ({len(v2.rna)} nt)")
    info_line(f"AA:  {result.aa_sequence} ({len(result.aa_list)} AAs)")
    info_line(f"Winding: {result.winding_number} loops")
    info_line(f"Backbone: {len(result.backbone.residues)} CA positions")
    info_line(f"Contacts: {len(result.contacts)}")
    info_line(f"Energy: {result.energy['total']:.1f} kcal/mol")
    info_line(f"Activation: {result.activation_count}/12 unique primitives")
    info_line(f"Pair coverage: {result.pair_coverage[0]}/{result.pair_coverage[1]}")
    info_line(f"Frobenius: {'YES' if result.frobenius_verified else 'NO'}")
    info_line(f"Secondary elements: {len(result.secondary_elements)}")
    for el in result.secondary_elements:
        info_line(f"  {el['type']:8s} [{el['start']:3d}-{el['end']:3d}] {el['sequence']}")
    
    if args.output:
        out = {"name":args.name,"aa":result.aa_sequence,
               "n_contacts":len(result.contacts),"energy":result.energy,
               "activation":result.activation_count,"frobenius":result.frobenius_verified}
        with open(args.output,"w") as f: json.dump(out,f,indent=2)
if __name__ == "__main__":
    main()
