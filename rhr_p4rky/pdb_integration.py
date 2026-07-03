#!/usr/bin/env python3
"""
pdb_integration.py — PDB FETCHING, PARSING, AND ENVIRONMENT CLASSIFICATION
============================================================================
Connects sidechain_algebra.py to real protein structures from the PDB.

Capabilities:
  - fetch_pdb(pdb_id): Download from RCSB (files.rcsb.org)
  - parse_pdb_residues(pdb_text): Extract residues + coordinates
  - classify_environments(residues): Per-residue environment classification
    based on local neighbor composition (8Å cutoff)
  - analyze_pdb_structure(pdb_id_or_path): Run full sidechain×environment
    algebra on every residue in a real protein structure

Author: Lando⊗⊙perator
"""

import sys
import os
import math
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field

# ── PDB residue → sidechain name mapping ─────────────────────────
RESIDUE_TO_SIDECHAIN = {
    "ALA": "alanine", "ARG": "arginine", "ASN": "asparagine",
    "ASP": "aspartate", "CYS": "cysteine", "GLN": "glutamine",
    "GLU": "glutamate", "GLY": "glycine", "HIS": "histidine",
    "ILE": "isoleucine", "LEU": "leucine", "LYS": "lysine",
    "MET": "methionine", "PHE": "phenylalanine", "PRO": "proline",
    "SER": "serine", "THR": "threonine", "TRP": "tryptophan",
    "TYR": "tyrosine", "VAL": "valine",
    # Non-standard
    "MSE": "methionine", "HYP": "proline", "SEP": "serine",
    "TPO": "threonine", "PTR": "tyrosine", "CSO": "cysteine",
}

# Residue properties for environment classification
RESIDUE_CHARGE = {
    "ALA": 0, "ARG": +1, "ASN": 0, "ASP": -1, "CYS": 0,
    "GLN": 0, "GLU": -1, "GLY": 0, "HIS": +1, "ILE": 0,
    "LEU": 0, "LYS": +1, "MET": 0, "PHE": 0, "PRO": 0,
    "SER": 0, "THR": 0, "TRP": 0, "TYR": 0, "VAL": 0,
}

RESIDUE_POLAR = {
    "ALA": False, "ARG": True, "ASN": True, "ASP": True, "CYS": False,
    "GLN": True, "GLU": True, "GLY": False, "HIS": True, "ILE": False,
    "LEU": False, "LYS": True, "MET": False, "PHE": False, "PRO": False,
    "SER": True, "THR": True, "TRP": False, "TYR": True, "VAL": False,
}

RESIDUE_HYDROPHOBICITY = {
    "ALA": 1.8, "ARG": -4.5, "ASN": -3.5, "ASP": -3.5, "CYS": 2.5,
    "GLN": -3.5, "GLU": -3.5, "GLY": -0.4, "HIS": -3.2, "ILE": 4.5,
    "LEU": 3.8, "LYS": -3.9, "MET": 1.9, "PHE": 2.8, "PRO": -1.6,
    "SER": -0.8, "THR": -0.7, "TRP": -0.9, "TYR": -1.3, "VAL": 4.2,
}

# Map 3-letter codes for non-standard
_NS_RESIDUE_CHARGE = {"MSE": 0, "HYP": 0, "SEP": -1, "TPO": -1, "PTR": -1, "CSO": 0}
_NS_RESIDUE_POLAR = {"MSE": False, "HYP": False, "SEP": True, "TPO": True, "PTR": True, "CSO": True}
_NS_RESIDUE_HYDRO = {"MSE": 1.9, "HYP": -1.6, "SEP": -0.8, "TPO": -0.7, "PTR": -1.3, "CSO": 2.5}

RESIDUE_CHARGE.update(_NS_RESIDUE_CHARGE)
RESIDUE_POLAR.update(_NS_RESIDUE_POLAR)
RESIDUE_HYDROPHOBICITY.update(_NS_RESIDUE_HYDRO)

# ── PDB fetching ──────────────────────────────────────────────────

def fetch_pdb(pdb_id: str, cache_dir: str = None) -> str:
    """Download a PDB file from RCSB. Returns PDB text.
    Caches to /home/mrnob0dy666/.cache/sidechain_algebra/ or specified cache_dir.
    """
    pdb_id = pdb_id.strip().upper()
    if cache_dir is None:
        cache_dir = os.path.expanduser("/home/mrnob0dy666/.cache/sidechain_algebra/pdb")
    os.makedirs(cache_dir, exist_ok=True)

    cache_path = os.path.join(cache_dir, f"{pdb_id}.pdb")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return f.read()

    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "sidechain_algebra/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"PDB {pdb_id} not found on RCSB (HTTP {e.code})")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Cannot reach RCSB: {e.reason}")

    with open(cache_path, 'w') as f:
        f.write(data)
    return data

# ── PDB parsing ───────────────────────────────────────────────────

@dataclass
class Residue:
    """A single residue parsed from a PDB file."""
    res_name: str       # 3-letter code
    chain: str
    res_num: int
    ins_code: str       # insertion code
    x: float
    y: float
    z: float
    atom_count: int = 0
    b_factor_sum: float = 0.0
    b_factor: float = 0.0  # average B-factor

    @property
    def sidechain_name(self) -> Optional[str]:
        return RESIDUE_TO_SIDECHAIN.get(self.res_name)

    @property
    def charge(self) -> int:
        return RESIDUE_CHARGE.get(self.res_name, 0)

    @property
    def is_polar(self) -> bool:
        return RESIDUE_POLAR.get(self.res_name, False)

    @property
    def hydrophobicity(self) -> float:
        return RESIDUE_HYDROPHOBICITY.get(self.res_name, 0.0)


def parse_pdb_residues(pdb_text: str, model: int = 1) -> List[Residue]:
    """Extract residues from PDB text. Uses CA atoms for positioning.
    Handles multi-model NMR structures via the model parameter.
    Returns residues sorted by chain then residue number.
    """
    atoms = []
    current_model = 1

    for line in pdb_text.split('\n'):
        if line.startswith("MODEL"):
            try:
                current_model = int(line[10:14].strip())
            except (ValueError, IndexError):
                pass
            continue
        if line.startswith("ENDMDL"):
            continue

        if current_model != model:
            continue

        if line.startswith("ATOM") or line.startswith("HETATM"):
            atom_name = line[12:16].strip()
            res_name = line[17:20].strip()
            chain = line[21] if len(line) > 21 else " "
            try:
                res_num = int(line[22:26].strip())
            except ValueError:
                continue
            ins_code = line[26] if len(line) > 26 else " "
            try:
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
            except (ValueError, IndexError):
                continue

            try:
                b_factor = float(line[60:66].strip())
            except (ValueError, IndexError):
                b_factor = 0.0

            atoms.append({
                "atom_name": atom_name,
                "res_name": res_name,
                "chain": chain,
                "res_num": res_num,
                "ins_code": ins_code,
                "x": x, "y": y, "z": z,
                "b_factor": b_factor,
            })

    # Group by residue (by CA atom position)
    residues = {}
    for a in atoms:
        if a["res_name"] not in RESIDUE_TO_SIDECHAIN:
            continue  # skip water, ligands, etc.
        key = (a["chain"], a["res_num"], a["ins_code"])
        if key not in residues:
            residues[key] = Residue(
                res_name=a["res_name"],
                chain=a["chain"],
                res_num=a["res_num"],
                ins_code=a["ins_code"],
                x=a["x"], y=a["y"], z=a["z"],
                atom_count=0,
                b_factor_sum=0.0,
            )
        residues[key].atom_count += 1
        residues[key].b_factor_sum += a["b_factor"]

    result = list(residues.values())
    for r in result:
        if r.atom_count > 0:
            r.b_factor = r.b_factor_sum / r.atom_count

    # Sort by chain, then residue number
    result.sort(key=lambda r: (r.chain, r.res_num))
    return result


def dist_3d(a: Residue, b: Residue) -> float:
    """Euclidean distance between two residues (CA positions)."""
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return math.sqrt(dx*dx + dy*dy + dz*dz)

# ── Environment classification ────────────────────────────────────

# The four canonical environments mapped from structural features:
#   hydrophobic_core  → buried, apolar neighbors, low B-factor
#   polar_surface     → exposed, polar/charged neighbors, high B-factor
#   charged_interface → high charge density neighbors, moderate burial
#   interfacial       → boundary between core and surface, mixed

def classify_environment(
    residue: Residue,
    all_residues: List[Residue],
    cutoff: float = 8.0,
) -> str:
    """Classify a residue's local protein environment.

    Based on:
      - Neighbor count within cutoff (proxy for solvent accessibility)
      - Neighbor polarity/charge composition
      - B-factor (flexibility)

    Returns one of: hydrophobic_core, polar_surface, charged_interface, interfacial
    """
    # Find neighbors within cutoff (same chain preferred, but include all)
    same_chain_neighbors = []
    all_neighbors = []
    for other in all_residues:
        if other is residue:
            continue
        d = dist_3d(residue, other)
        if d <= cutoff:
            all_neighbors.append(other)
            if other.chain == residue.chain:
                same_chain_neighbors.append(other)

    n_neighbors = len(all_neighbors)
    n_same_chain = len(same_chain_neighbors)

    if n_neighbors == 0:
        # Isolated residue — likely a flexible loop or terminal
        return "polar_surface"

    # Compute neighbor composition
    n_polar = sum(1 for n in all_neighbors if n.is_polar)
    n_charged = sum(1 for n in all_neighbors if n.charge != 0)
    n_hydrophobic = sum(1 for n in all_neighbors if not n.is_polar and n.charge == 0)
    avg_hydro = sum(n.hydrophobicity for n in all_neighbors) / n_neighbors if n_neighbors > 0 else 0

    polar_frac = n_polar / n_neighbors
    charged_frac = n_charged / n_neighbors
    hydro_frac = n_hydrophobic / n_neighbors

    # B-factor context
    avg_bfactor = sum(n.b_factor for n in all_neighbors) / n_neighbors if n_neighbors > 0 else 0

    # Classification logic
    # Charged interface: high charge density
    if charged_frac >= 0.30:
        return "charged_interface"

    # Hydrophobic core: dense packing, mostly apolar, low B-factor
    if n_neighbors >= 8 and hydro_frac >= 0.50 and avg_hydro > 1.0:
        return "hydrophobic_core"

    # Polar surface: many polar neighbors or sparse packing (exposed)
    if n_neighbors <= 5 or polar_frac >= 0.55:
        return "polar_surface"

    # Interfacial: everything else — mixed composition, moderate packing
    if n_neighbors >= 6 and hydro_frac >= 0.30:
        return "interfacial"

    # Default: polar surface for sparse/borderline
    return "polar_surface"


def classify_all_environments(
    residues: List[Residue],
    cutoff: float = 8.0,
) -> Dict[Tuple[str, int, str], str]:
    """Classify environment for every residue in a structure.
    Returns dict mapping (chain, res_num, ins_code) → environment name.
    """
    result = {}
    for r in residues:
        env = classify_environment(r, residues, cutoff)
        key = (r.chain, r.res_num, r.ins_code)
        result[key] = env
    return result

# ── PDB Structure Analysis ────────────────────────────────────────

@dataclass
class ResidueAnalysis:
    """Per-residue sidechain×environment analysis result."""
    chain: str
    res_num: int
    res_name: str          # 3-letter
    sidechain: str         # canonical sidechain name
    environment: str        # classified environment
    sidechain_tuple: str
    env_tuple: str
    tensor_tuple: str
    meet_tuple: str
    join_tuple: str
    pre_distance: float
    tensor_distance_sc: float
    tensor_distance_env: float
    asymmetry: float
    domination: str
    n_shared: int
    n_bottlenecks: int
    bottleneck_primitives: List[str]
    tier: str
    frustration: float
    b_factor: float
    n_neighbors: int


def analyze_pdb_structure(
    pdb_id_or_path: str,
    cutoff: float = 8.0,
    verbose: bool = True,
) -> Dict:
    """Full sidechain×environment algebra on a real PDB structure.

    Args:
        pdb_id_or_path: PDB ID (4 chars, e.g. '1LYZ') or path to .pdb file
        cutoff: Neighbor distance cutoff in Angstroms for environment classification
        verbose: Print progress

    Returns:
        Dict with keys: pdb_id, n_residues, residues (list of ResidueAnalysis),
        environment_counts, tier_counts, bottlenecks_summary, chain_summary,
        frustration_avg, top_frustrated, top_compatible
    """
    # Import sidechain algebra (lazy to avoid circular import at module load)
    from sidechain_algebra import SIDECHAINS, ENVIRONMENTS, analyze_composition

    # Load PDB
    if os.path.exists(pdb_id_or_path):
        if verbose:
            print(f"Reading PDB from file: {pdb_id_or_path}")
        with open(pdb_id_or_path, 'r') as f:
            pdb_text = f.read()
        pdb_id = os.path.splitext(os.path.basename(pdb_id_or_path))[0].upper()
    else:
        pdb_id = pdb_id_or_path.strip().upper()
        if verbose:
            print(f"Fetching PDB {pdb_id} from RCSB...")
        pdb_text = fetch_pdb(pdb_id)

    # Parse residues
    residues = parse_pdb_residues(pdb_text)
    if verbose:
        print(f"Parsed {len(residues)} residues from {pdb_id}")

    # Classify environments
    env_map = classify_all_environments(residues, cutoff)

    # Count neighbors per residue
    neighbor_counts = {}
    for r in residues:
        n_neighbors = 0
        for other in residues:
            if other is not r and dist_3d(r, other) <= cutoff:
                n_neighbors += 1
        neighbor_counts[(r.chain, r.res_num, r.ins_code)] = n_neighbors

    # Run sidechain×environment algebra per residue
    results: List[ResidueAnalysis] = []
    skipped = 0

    for r in residues:
        sc_name = r.sidechain_name
        if sc_name is None:
            skipped += 1
            continue
        if sc_name not in SIDECHAINS:
            if verbose:
                print(f"  Skipping {r.res_name}{r.res_num} — no sidechain tuple")
            skipped += 1
            continue

        env_name = env_map.get((r.chain, r.res_num, r.ins_code), "polar_surface")
        key = (r.chain, r.res_num, r.ins_code)
        n_nbrs = neighbor_counts.get(key, 0)

        analysis = analyze_composition(sc_name, env_name)

        if "error" in analysis:
            skipped += 1
            continue

        ra = ResidueAnalysis(
            chain=r.chain,
            res_num=r.res_num,
            res_name=r.res_name,
            sidechain=sc_name,
            environment=env_name,
            sidechain_tuple=analysis.get("tuple_sc", "?"),
            env_tuple=analysis.get("tuple_env", "?"),
            tensor_tuple=analysis.get("tensor_str", "?"),
            meet_tuple=analysis.get("meet_str", "?"),
            join_tuple=analysis.get("join_str", "?"),
            pre_distance=analysis.get("distance_pre", 0.0),
            tensor_distance_sc=analysis.get("distance_tensor_sc", 0.0),
            tensor_distance_env=analysis.get("distance_tensor_env", 0.0),
            asymmetry=analysis.get("asymmetry", 1.0),
            domination=analysis.get("domination", "?"),
            n_shared=analysis.get("n_shared", 0),
            n_bottlenecks=analysis.get("n_bottlenecks", 0),
            bottleneck_primitives=[b["primitive"] for b in analysis.get("bottlenecks", [])],
            tier=analysis.get("tier_tensor", "?"),
            frustration=analysis.get("frustration", 0.0),
            b_factor=r.b_factor,
            n_neighbors=n_nbrs,
        )
        results.append(ra)

    # Summaries
    env_counts = defaultdict(int)
    tier_counts = defaultdict(int)
    chain_summary = defaultdict(lambda: {"n_res": 0, "env_counts": defaultdict(int), "tier_counts": defaultdict(int)})

    total_frustration = 0.0
    total_bottlenecks = 0
    bottleneck_primitives = defaultdict(int)

    for ra in results:
        env_counts[ra.environment] += 1
        tier_counts[ra.tier] += 1
        total_frustration += ra.frustration
        total_bottlenecks += ra.n_bottlenecks
        for bp in ra.bottleneck_primitives:
            bottleneck_primitives[bp] += 1

        cs = chain_summary[ra.chain]
        cs["n_res"] += 1
        cs["env_counts"][ra.environment] += 1
        cs["tier_counts"][ra.tier] += 1

    avg_frustration = total_frustration / len(results) if results else 0

    # Top frustrated and compatible
    sorted_by_frustration = sorted(results, key=lambda r: r.frustration, reverse=True)
    sorted_by_compatible = sorted(results, key=lambda r: (r.n_shared, -r.frustration), reverse=True)

    if verbose:
        print(f"\nAnalyzed {len(results)} residues (skipped {skipped})")
        print(f"Environment distribution: {dict(env_counts)}")
        print(f"Tier distribution: {dict(tier_counts)}")
        print(f"Average frustration: {avg_frustration:.3f}")
        print(f"Total bottlenecks: {total_bottlenecks}")
        if bottleneck_primitives:
            print(f"Bottleneck primitives: {dict(bottleneck_primitives)}")

    return {
        "pdb_id": pdb_id,
        "n_residues": len(results),
        "n_skipped": skipped,
        "cutoff": cutoff,
        "environment_counts": dict(env_counts),
        "tier_counts": dict(tier_counts),
        "chain_summary": {k: {"n_res": v["n_res"],
                               "env_counts": dict(v["env_counts"]),
                               "tier_counts": dict(v["tier_counts"])}
                          for k, v in chain_summary.items()},
        "frustration_avg": round(avg_frustration, 3),
        "total_bottlenecks": total_bottlenecks,
        "bottleneck_primitives": dict(bottleneck_primitives),
        "top_frustrated": [
            {"chain": r.chain, "res_num": r.res_num, "res_name": r.res_name,
             "sidechain": r.sidechain, "environment": r.environment,
             "frustration": r.frustration, "pre_distance": r.pre_distance,
             "n_bottlenecks": r.n_bottlenecks, "tier": r.tier}
            for r in sorted_by_frustration[:10]
        ],
        "top_compatible": [
            {"chain": r.chain, "res_num": r.res_num, "res_name": r.res_name,
             "sidechain": r.sidechain, "environment": r.environment,
             "n_shared": r.n_shared, "pre_distance": r.pre_distance,
             "n_bottlenecks": r.n_bottlenecks, "tier": r.tier}
            for r in sorted_by_compatible[:10]
        ],
        "residues": [{
            "chain": r.chain, "res_num": r.res_num, "res_name": r.res_name,
            "sidechain": r.sidechain, "environment": r.environment,
            "sidechain_tuple": r.sidechain_tuple, "env_tuple": r.env_tuple,
            "tensor_tuple": r.tensor_tuple, "meet_tuple": r.meet_tuple,
            "join_tuple": r.join_tuple,
            "pre_distance": r.pre_distance,
            "tensor_distance_sc": r.tensor_distance_sc,
            "tensor_distance_env": r.tensor_distance_env,
            "asymmetry": r.asymmetry, "domination": r.domination,
            "n_shared": r.n_shared, "n_bottlenecks": r.n_bottlenecks,
            "bottleneck_primitives": r.bottleneck_primitives,
            "tier": r.tier, "frustration": r.frustration,
            "b_factor": r.b_factor, "n_neighbors": r.n_neighbors,
        } for r in results],
    }

# ── CLI ────────────────────────────────────────────────────────────

def print_pdb_analysis(result: Dict, verbose: bool = False):
    """Pretty-print PDB structure analysis results."""
    print("═" * 72)
    print(f"PDB STRUCTURE ANALYSIS: {result['pdb_id']}")
    print("═" * 72)
    print(f"\n  Residues analyzed: {result['n_residues']} (skipped: {result['n_skipped']})")
    print(f"  Neighbor cutoff:   {result['cutoff']} Å")
    print(f"\n  Environment distribution:")
    for env, count in sorted(result['environment_counts'].items()):
        pct = 100 * count / result['n_residues'] if result['n_residues'] > 0 else 0
        print(f"    {env:25s} {count:4d} ({pct:5.1f}%)")

    print(f"\n  Tier distribution:")
    for tier, count in sorted(result['tier_counts'].items()):
        pct = 100 * count / result['n_residues'] if result['n_residues'] > 0 else 0
        print(f"    {tier:6s} {count:4d} ({pct:5.1f}%)")

    print(f"\n  Average frustration: {result['frustration_avg']:.3f}")
    print(f"  Total bottlenecks:   {result['total_bottlenecks']}")
    if result['bottleneck_primitives']:
        print(f"  Bottleneck primitives:")
        for bp, count in sorted(result['bottleneck_primitives'].items(), key=lambda x: -x[1]):
            print(f"    {bp}: {count}")

    print(f"\n  ── Chain summaries ──")
    for ch, cs in sorted(result['chain_summary'].items()):
        print(f"  Chain {ch}: {cs['n_res']} residues")
        print(f"    Environments: {cs['env_counts']}")
        print(f"    Tiers: {cs['tier_counts']}")

    if result['top_frustrated']:
        print(f"\n  ── Top 10 most frustrated residues ──")
        print(f"  {'Res':8s} {'SC':14s} {'Env':22s} {'Frust':>6s} {'d_pre':>6s} {'Bn':>3s} {'Tier':>6s}")
        print(f"  {'─'*8} {'─'*14} {'─'*22} {'─'*6} {'─'*6} {'─'*3} {'─'*6}")
        for r in result['top_frustrated']:
            label = f"{r['chain']}:{r['res_name']}{r['res_num']}"
            print(f"  {label:8s} {r['sidechain']:14s} {r['environment']:22s} "
                  f"{r['frustration']:6.3f} {r['pre_distance']:6.3f} "
                  f"{r['n_bottlenecks']:3d} {r['tier']:>6s}")

    if result['top_compatible']:
        print(f"\n  ── Top 10 most compatible residues ──")
        print(f"  {'Res':8s} {'SC':14s} {'Env':22s} {'Shared':>6s} {'d_pre':>6s} {'Tier':>6s}")
        print(f"  {'─'*8} {'─'*14} {'─'*22} {'─'*6} {'─'*6} {'─'*6}")
        for r in result['top_compatible']:
            label = f"{r['chain']}:{r['res_name']}{r['res_num']}"
            print(f"  {label:8s} {r['sidechain']:14s} {r['environment']:22s} "
                  f"{r['n_shared']:6d} {r['pre_distance']:6.3f} {r['tier']:>6s}")

    if verbose and result.get('residues'):
        print(f"\n  ── Full per-residue listing ({len(result['residues'])} residues) ──")
        print(f"  {'Res':8s} {'SC':14s} {'Env':22s} {'d_pre':>6s} {'Bn':>3s} {'Tier':>6s} {'Domination'}")
        print(f"  {'─'*8} {'─'*14} {'─'*22} {'─'*6} {'─'*3} {'─'*6} {'─'*40}")
        for r in result['residues']:
            label = f"{r['chain']}:{r['res_name']}{r['res_num']}"
            print(f"  {label:8s} {r['sidechain']:14s} {r['environment']:22s} "
                  f"{r['pre_distance']:6.3f} {r['n_bottlenecks']:3d} "
                  f"{r['tier']:>6s} {r['domination'][:40]}")


if __name__ == "__main__":
    import sys
    import json as _json

    # Adjust path for sidechain_algebra import
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    if len(sys.argv) < 2:
        print("PDB INTEGRATION — sidechain×environment algebra on real structures")
        print("=" * 72)
        print("\nUsage:")
        print("  python pdb_integration.py <PDB_ID>              e.g. 1LYZ")
        print("  python pdb_integration.py <PDB_ID> --json        JSON output")
        print("  python pdb_integration.py <PDB_ID> --verbose     Per-residue listing")
        print("  python pdb_integration.py <PDB_ID> --cutoff 6.0  Custom cutoff")
        print("  python pdb_integration.py <path/to/file.pdb>     Local PDB file")
        print("\nCache: /home/mrnob0dy666/.cache/sidechain_algebra/pdb/")
        sys.exit(0)

    pdb_target = sys.argv[1]
    as_json = "--json" in sys.argv
    verbose = "--verbose" in sys.argv
    cutoff = 8.0
    for i, arg in enumerate(sys.argv):
        if arg == "--cutoff" and i + 1 < len(sys.argv):
            cutoff = float(sys.argv[i + 1])
            break

    result = analyze_pdb_structure(pdb_target, cutoff=cutoff, verbose=not as_json)

    if as_json:
        print(_json.dumps(result, indent=2, default=str))
    else:
        print_pdb_analysis(result, verbose=verbose)
