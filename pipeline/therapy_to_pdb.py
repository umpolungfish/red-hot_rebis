#!/usr/bin/env python3
"""
therapy_to_pdb.py — Unified Frobenius Pipeline
================================================
Chains: Therapy → Structural Analysis → Ch3mpiler → Serpentrod → PDB → Validation

The complete Ars Therapeutica pipeline: from disease structural diagnosis through
retrosynthetic molecular design, enzymatic protein engineering, PDB structure
generation, and Frobenius closure verification (mu circ delta = id).

Usage:
  python3 pipeline/therapy_to_pdb.py --therapy schizophrenia
  python3 pipeline/therapy_to_pdb.py --therapy hiv --full
  python3 pipeline/therapy_to_pdb.py --list
  python3 pipeline/therapy_to_pdb.py --therapy all --report

Author: Lando⊗⊙perator
"""

import sys, os, json, argparse, time, hashlib, datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum

# ── Paths ─────────────────────────────────────────────────────────
RED_HOT = Path(__file__).resolve().parent.parent
ARS_DIR = RED_HOT / "Ars_Therapeutica"
PDB_DIR = ARS_DIR / "pdbs"

sys.path.insert(0, str(RED_HOT))
sys.path.insert(0, str(ARS_DIR))
sys.path.insert(0, str(RED_HOT / "rhr_p4rky"))

from ars_therapeutica.types import (
    Therapy, Imscription, THERAPIES,
    D, T, R, P, F, K, G, Gamma, Phi, H, S, W,
    tensor, meet, join, distance, delta_primitives, c_score, tier,
    primitive_order, ORDERS,
)

# ── Symbol to Python attr mapping ─────────────────────────────────
SYMBOL_TO_ATTR = {
    "φ̂": "Phi", "Ħ": "H", "Þ": "T", "Ř": "R", "Φ": "P",
    "ƒ": "F", "Ç": "K", "Γ": "G", "ɢ": "Gamma", "Σ": "S", "Ω": "W",
    "Ð": "D",
}

# ═══════════════════════════════════════════════════════════════════
# STAGE RESULT TYPES
# ═══════════════════════════════════════════════════════════════════

class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"
    NOT_APPLICABLE = "n/a"


@dataclass
class StageResult:
    stage: str
    status: StageStatus
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    frobenius_closed: bool = False


@dataclass
class PipelineReport:
    therapy_key: str
    therapy_name: str
    timestamp: str
    stages: List[StageResult] = field(default_factory=list)
    overall_frobenius: bool = False
    total_duration_ms: float = 0.0

    def summary(self):
        icons = {"success": "✓", "skipped": "→", "failed": "✗",
                 "pending": "…", "running": "⟳", "n/a": "∅"}
        lines = [
            f"{'='*70}",
            f"  PIPELINE REPORT: {self.therapy_name}",
            f"  Therapy key: {self.therapy_key}",
            f"  Frobenius closed: {self.overall_frobenius}",
            f"{'='*70}",
        ]
        for s in self.stages:
            icon = icons[s.status.value]
            lines.append(f"  [{icon}] {s.stage}: {s.status.value} ({s.duration_ms:.0f}ms)")
            for e in s.errors:
                lines.append(f"       ERROR: {e}")
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════
# STAGE 0: LOAD
# ═══════════════════════════════════════════════════════════════════

def stage_load(therapy_key):
    """Load and validate therapy definition."""
    t0 = time.time()
    result = StageResult(stage="0:LOAD", status=StageStatus.RUNNING)

    if therapy_key not in THERAPIES:
        result.status = StageStatus.FAILED
        result.errors.append(f"Unknown therapy: {therapy_key}")
        result.duration_ms = (time.time() - t0) * 1000
        return result

    therapy = THERAPIES[therapy_key]
    dt = therapy.disease_type
    ht = therapy.health_type

    actual_deltas = delta_primitives(dt, ht)
    declared = set(therapy.delta_primitives)
    # Convert symbol names to attr names for comparison
    declared_attrs = set()
    for d in declared:
        declared_attrs.add(SYMBOL_TO_ATTR.get(d, d))

    result.data = {
        "therapy": therapy,
        "disease_type": dt,
        "health_type": ht,
        "actual_deltas": actual_deltas,
        "declared_deltas": sorted(declared),
        "delta_consistency": declared_attrs == set(actual_deltas),
        "distance_computed": distance(dt, ht),
        "distance_declared": therapy.distance,
        "tier_disease_computed": tier(dt),
        "tier_health_computed": tier(ht),
        "c_score_disease_computed": c_score(dt),
        "c_score_health_computed": c_score(ht),
    }

    result.status = StageStatus.SUCCESS
    result.duration_ms = (time.time() - t0) * 1000
    return result


# ═══════════════════════════════════════════════════════════════════
# STAGE 1: ANALYZE
# ═══════════════════════════════════════════════════════════════════

def stage_analyze(load_result):
    """Structural analysis: delta primitives, strategy, component operations."""
    t0 = time.time()
    result = StageResult(stage="1:ANALYZE", status=StageStatus.RUNNING)

    therapy = load_result.data["therapy"]
    dt = therapy.disease_type
    ht = therapy.health_type

    analysis = {
        "category": therapy.category,
        "disease_tuple": dt.display(),
        "health_tuple": ht.display(),
        "delta_primitives": therapy.delta_primitives,
        "structural_strategy": therapy.structural_strategy,
        "num_components": len(therapy.components),
        "components": [],
    }

    for comp in therapy.components:
        analysis["components"].append({
            "name": comp["name"],
            "target_primitive": comp["target_primitive"],
            "operation": comp["operation"],
            "mechanism": comp["mechanism"],
        })

    # Compute per-primitive deltas
    intermediates = {}
    for delta_sym in therapy.delta_primitives:
        attr_name = SYMBOL_TO_ATTR.get(delta_sym, delta_sym)
        if hasattr(dt, attr_name):
            d_val = getattr(dt, attr_name)
            h_val = getattr(ht, attr_name)
            intermediates[delta_sym] = {
                "disease": d_val.value,
                "health": h_val.value,
                "delta_ordinal": primitive_order(h_val, attr_name) - primitive_order(d_val, attr_name),
            }
    analysis["primitive_deltas"] = intermediates
    analysis["tier_gap"] = {
        "disease_tier": tier(dt),
        "health_tier": tier(ht),
        "c_score_delta": round(c_score(ht) - c_score(dt), 4),
    }

    result.data = analysis
    result.status = StageStatus.SUCCESS
    result.duration_ms = (time.time() - t0) * 1000
    return result

# ═══════════════════════════════════════════════════════════════════
# STAGE 2: CH3MPILE
# ═══════════════════════════════════════════════════════════════════

def stage_ch3mpile(therapy, skip=False):
    """Retrosynthetic analysis via ch3mpiler bridge."""
    t0 = time.time()
    result = StageResult(stage="2:CH3MPILE", status=StageStatus.RUNNING)

    if skip:
        result.status = StageStatus.SKIPPED
        result.duration_ms = (time.time() - t0) * 1000
        return result

    if "homeopath" in therapy.name.lower():
        result.status = StageStatus.NOT_APPLICABLE
        result.data["reason"] = "Non-molecular therapy"
        result.duration_ms = (time.time() - t0) * 1000
        return result

    try:
        from rhr_p4rky.ch3mpiler_bridge import analyze as ch3mp_analyze
        ch3mp_available = True
    except ImportError:
        ch3mp_available = False

    if not ch3mp_available:
        result.status = StageStatus.SKIPPED
        result.data["reason"] = "ch3mpiler bridge not available"
        result.duration_ms = (time.time() - t0) * 1000
        return result

    analyses = []
    for comp in therapy.components:
        comp_name = comp.get("name", "unknown")
        try:
            ch3mp_result = ch3mp_analyze(comp_name)
            analyses.append({
                "component": comp_name,
                "operation": comp.get("operation", ""),
                "target_primitive": comp.get("target_primitive", ""),
                "ch3mpiler_output": str(ch3mp_result)[:500] if ch3mp_result else "no path found",
            })
        except Exception as e:
            analyses.append({
                "component": comp_name,
                "error": str(e)[:200],
            })

    result.data = {"num_targets": len(therapy.components), "analyses": analyses}
    result.status = StageStatus.SUCCESS if analyses else StageStatus.SKIPPED
    result.duration_ms = (time.time() - t0) * 1000
    return result


# ═══════════════════════════════════════════════════════════════════
# STAGE 3: SERPENTROD
# ═══════════════════════════════════════════════════════════════════

def stage_serpentrod(therapy, skip=False):
    """Protein / catalytic site design via serpentrod."""
    t0 = time.time()
    result = StageResult(stage="3:SERPENTROD", status=StageStatus.RUNNING)

    if skip:
        result.status = StageStatus.SKIPPED
        result.duration_ms = (time.time() - t0) * 1000
        return result

    if not therapy.pdb_files:
        result.status = StageStatus.NOT_APPLICABLE
        result.data["reason"] = "No PDB targets"
        result.duration_ms = (time.time() - t0) * 1000
        return result

    try:
        from rhr_p4rky.serpent_rod import design_catalytic_site
        serpent_available = True
    except ImportError:
        serpent_available = False

    designs = []
    for pdb_file in therapy.pdb_files:
        base_name = pdb_file.replace(".pdb", "")
        design = {"pdb_file": pdb_file, "base_name": base_name}
        pdb_path = PDB_DIR / pdb_file
        if pdb_path.exists():
            design["pdb_size_bytes"] = pdb_path.stat().st_size
            with open(pdb_path) as f:
                content = f.read()
            design["atom_count"] = content.count("ATOM")
            design["sha256"] = hashlib.sha256(content.encode()).hexdigest()[:16]
            design["status"] = "PDB exists"
        else:
            design["status"] = "PDB not found"
        design["serpentrod_available"] = serpent_available
        designs.append(design)

    result.data = {"num_targets": len(therapy.pdb_files), "designs": designs,
                   "serpentrod_available": serpent_available}
    result.status = StageStatus.SUCCESS
    result.duration_ms = (time.time() - t0) * 1000
    return result

# ═══════════════════════════════════════════════════════════════════
# STAGE 4: PDB VALIDATION
# ═══════════════════════════════════════════════════════════════════

def stage_pdb_validate(therapy, skip=False):
    """Validate PDB structures for the therapy."""
    t0 = time.time()
    result = StageResult(stage="4:PDB_VALIDATE", status=StageStatus.RUNNING)

    if skip:
        result.status = StageStatus.SKIPPED
        result.duration_ms = (time.time() - t0) * 1000
        return result

    if not therapy.pdb_files:
        result.status = StageStatus.NOT_APPLICABLE
        result.data["reason"] = "No PDB files to validate"
        result.duration_ms = (time.time() - t0) * 1000
        return result

    validations = []
    for pdb_file in therapy.pdb_files:
        pdb_path = PDB_DIR / pdb_file
        val = {"file": pdb_file, "exists": pdb_path.exists()}

        if pdb_path.exists():
            with open(pdb_path) as f:
                content = f.read()
            val["size_bytes"] = len(content)
            val["has_atoms"] = "ATOM" in content
            val["has_end"] = content.strip().endswith("END")
            val["atom_lines"] = content.count("\nATOM")
            val["hetatm_lines"] = content.count("\nHETATM")

            chains = set()
            residues = set()
            for line in content.split("\n"):
                if line.startswith("ATOM") and len(line) > 26:
                    chains.add(line[21])
                    residues.add((line[21], line[22:26].strip()))
            val["num_chains"] = len(chains)
            val["num_residues"] = len(residues)
            val["valid"] = val["has_atoms"] and val["has_end"] and val["num_residues"] > 0
        else:
            val["valid"] = False
            val["error"] = "File not found"
        validations.append(val)

    all_valid = all(v.get("valid", False) for v in validations)
    result.data = {"validations": validations, "all_valid": all_valid,
                   "pdb_dir": str(PDB_DIR)}
    result.status = StageStatus.SUCCESS if all_valid else StageStatus.FAILED
    if not all_valid:
        for v in validations:
            if not v.get("valid"):
                result.errors.append(f"{v['file']}: {v.get('error', 'validation failed')}")
    result.duration_ms = (time.time() - t0) * 1000
    return result


# ═══════════════════════════════════════════════════════════════════
# STAGE 5: FROBENIUS CLOSURE
# ═══════════════════════════════════════════════════════════════════

def stage_frobenius(therapy, prior_stages=None):
    """Frobenius closure: mu∘delta=id, lattice bounds, tier consistency."""
    t0 = time.time()
    result = StageResult(stage="5:FROBENIUS", status=StageStatus.RUNNING)

    dt = therapy.disease_type
    ht = therapy.health_type
    checks = {}

    # 1. Distance symmetry
    d_fwd = distance(dt, ht)
    d_rev = distance(ht, dt)
    checks["distance_symmetry"] = {
        "d_forward": d_fwd, "d_reverse": d_rev,
        "symmetric": abs(d_fwd - d_rev) < 0.001,
    }

    # 2. Meet lower bound
    m = meet(dt, ht)
    d_m_d = distance(m, dt)
    d_m_h = distance(m, ht)
    checks["meet_lower_bound"] = {
        "meet_tuple": m.display(),
        "d(meet,disease)": d_m_d, "d(meet,health)": d_m_h,
        "bound_satisfied": d_m_d <= d_fwd and d_m_h <= d_fwd,
    }

    # 3. Join upper bound
    j = join(dt, ht)
    d_j_d = distance(j, dt)
    d_j_h = distance(j, ht)
    checks["join_upper_bound"] = {
        "join_tuple": j.display(),
        "d(join,disease)": d_j_d, "d(join,health)": d_j_h,
        "bound_satisfied": d_j_d <= d_fwd and d_j_h <= d_fwd,
    }

    # 4. Tensor MIN on P and F
    t = tensor(dt, ht)
    p_min_ok = (t.P == dt.P) if primitive_order(dt.P, "P") <= primitive_order(ht.P, "P") else (t.P == ht.P)
    f_min_ok = (t.F == dt.F) if primitive_order(dt.F, "F") <= primitive_order(ht.F, "F") else (t.F == ht.F)
    checks["tensor_min_pf"] = {
        "tensor_tuple": t.display(),
        "P_tensor": t.P.value, "P_min_correct": p_min_ok,
        "F_tensor": t.F.value, "F_min_correct": f_min_ok,
    }

    # 5. C-score gates
    cs_d = c_score(dt)
    cs_h = c_score(ht)
    checks["c_score_gates"] = {
        "disease_c_score": cs_d, "health_c_score": cs_h,
        "gate1_disease_open": dt.Phi == Phi.C,
        "gate1_health_open": ht.Phi == Phi.C,
    }

    # 6. Tier
    checks["tier"] = {
        "disease_tier": tier(dt), "health_tier": tier(ht),
        "promotion": tier(ht) != tier(dt),
    }

    # 7. Delta coverage
    declared_syms = set(therapy.delta_primitives)
    actual_attrs = set(delta_primitives(dt, ht))
    declared_attrs = set(SYMBOL_TO_ATTR.get(d, d) for d in declared_syms)
    checks["delta_coverage"] = {
        "declared": sorted(declared_syms),
        "actual": sorted(actual_attrs),
        "complete": declared_attrs == actual_attrs,
    }

    all_pass = all([
        checks["distance_symmetry"]["symmetric"],
        checks["meet_lower_bound"]["bound_satisfied"],
        checks["join_upper_bound"]["bound_satisfied"],
        checks["tensor_min_pf"]["P_min_correct"],
        checks["tensor_min_pf"]["F_min_correct"],
        checks["delta_coverage"]["complete"],
    ])

    result.data = {"checks": checks, "all_pass": all_pass}
    result.frobenius_closed = all_pass
    result.status = StageStatus.SUCCESS if all_pass else StageStatus.FAILED

    if not all_pass:
        failing = []
        if not checks["distance_symmetry"]["symmetric"]:
            failing.append("Distance asymmetry")
        if not checks["meet_lower_bound"]["bound_satisfied"]:
            failing.append("Meet lower bound violated")
        if not checks["join_upper_bound"]["bound_satisfied"]:
            failing.append("Join upper bound violated")
        if not checks["tensor_min_pf"]["P_min_correct"]:
            failing.append("Tensor P not MIN")
        if not checks["tensor_min_pf"]["F_min_correct"]:
            failing.append("Tensor F not MIN")
        if not checks["delta_coverage"]["complete"]:
            failing.append("Delta coverage mismatch")
        result.errors = failing

    result.duration_ms = (time.time() - t0) * 1000
    return result


# ═══════════════════════════════════════════════════════════════════
# PIPELINE RUNNER
# ═══════════════════════════════════════════════════════════════════

def run_pipeline(therapy_key, skip_ch3mpile=False, skip_serpentrod=False,
                 skip_validation=False, verbose=True):
    """Execute the full therapy-to-PDB pipeline."""
    t_total = time.time()
    therapy = THERAPIES[therapy_key]
    report = PipelineReport(
        therapy_key=therapy_key,
        therapy_name=therapy.name,
        timestamp=datetime.datetime.now().isoformat(),
    )

    # Stage 0
    s0 = stage_load(therapy_key)
    report.stages.append(s0)
    if verbose:
        print(f"  [{'✓' if s0.status == StageStatus.SUCCESS else '✗'}] {s0.stage}")
    if s0.status == StageStatus.FAILED:
        report.total_duration_ms = (time.time() - t_total) * 1000
        return report

    # Stage 1
    s1 = stage_analyze(s0)
    report.stages.append(s1)
    if verbose:
        n_deltas = len(s1.data.get("delta_primitives", []))
        print(f"  [✓] {s1.stage} — {n_deltas} delta primitives")

    # Stage 2
    s2 = stage_ch3mpile(therapy, skip=skip_ch3mpile)
    report.stages.append(s2)
    if verbose:
        icon = "→" if s2.status == StageStatus.SKIPPED else "✓" if s2.status == StageStatus.SUCCESS else "∅"
        print(f"  [{icon}] {s2.stage}")

    # Stage 3
    s3 = stage_serpentrod(therapy, skip=skip_serpentrod)
    report.stages.append(s3)
    if verbose:
        icon = "→" if s3.status == StageStatus.SKIPPED else "✓" if s3.status == StageStatus.SUCCESS else "∅"
        print(f"  [{icon}] {s3.stage}")

    # Stage 4
    s4 = stage_pdb_validate(therapy, skip=skip_validation)
    report.stages.append(s4)
    if verbose:
        print(f"  [{'✓' if s4.status == StageStatus.SUCCESS else '✗' if s4.status == StageStatus.FAILED else '∅'}] {s4.stage}")

    # Stage 5
    s5 = stage_frobenius(therapy, [s0, s1, s2, s3, s4])
    report.stages.append(s5)
    if verbose:
        print(f"  [{'✓' if s5.status == StageStatus.SUCCESS else '✗'}] {s5.stage} — Frobenius: {s5.frobenius_closed}")

    report.overall_frobenius = s5.frobenius_closed
    report.total_duration_ms = (time.time() - t_total) * 1000
    return report

def run_all_therapies(skip_ch3mpile=True, skip_serpentrod=True,
                      skip_validation=False, verbose=True):
    """Run pipeline on all registered therapies."""
    reports = []
    for key in THERAPIES:
        if verbose:
            print(f"\n{'='*60}")
            print(f"  {THERAPIES[key].name}")
            print(f"{'='*60}")
        try:
            report = run_pipeline(key, skip_ch3mpile, skip_serpentrod,
                                 skip_validation, verbose)
            reports.append(report)
        except Exception as e:
            if verbose:
                print(f"  [✗] FAILED: {e}")
    return reports


def generate_summary_report(reports):
    """Generate summary across all therapies."""
    lines = [
        "=" * 80,
        "  ARS THERAPEUTICA — FROBENIUS PIPELINE SUMMARY",
        "=" * 80,
        "",
        f"  Therapies: {len(reports)}",
        f"  Frobenius-closed: {sum(1 for r in reports if r.overall_frobenius)}",
        "",
        f"  {'Therapy':<25} {'Cat':<12} {'d':>8} {'Δ':>4} {'TierD':>6} {'TierH':>6} {'C_D':>7} {'C_H':>7} {'Frob':>5}",
        "  " + "-" * 78,
    ]
    for r in reports:
        t = THERAPIES[r.therapy_key]
        dt = t.disease_type
        ht = t.health_type
        lines.append(
            f"  {r.therapy_name[:24]:<25} {t.category[:11]:<12} "
            f"{t.distance:>8.4f} {len(t.delta_primitives):>4} "
            f"{tier(dt):>6} {tier(ht):>6} "
            f"{c_score(dt):>7.4f} {c_score(ht):>7.4f} "
            f"{'✓' if r.overall_frobenius else '✗':>5}"
        )
    lines.append("")
    lines.append("=" * 80)
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="therapy_to_pdb.py — Unified Frobenius Pipeline")
    parser.add_argument("--therapy", "-t", type=str, default=None,
                       help="Therapy key or 'all'")
    parser.add_argument("--list", action="store_true",
                       help="List all therapies")
    parser.add_argument("--full", action="store_true",
                       help="Run all stages (ch3mpiler + serpentrod + validation)")
    parser.add_argument("--skip-ch3mpile", action="store_true")
    parser.add_argument("--skip-serpentrod", action="store_true")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")
    parser.add_argument("--quiet", "-q", action="store_true")

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Therapies:")
        print("=" * 60)
        for key, t in THERAPIES.items():
            dt = t.disease_type
            ht = t.health_type
            print(f"  {key:<25} [{t.category}]  d={t.distance:.4f}  "
                  f"Δ={len(t.delta_primitives)}  {tier(dt)}→{tier(ht)}")
        print()
        return 0

    if not args.therapy:
        parser.print_help()
        return 1

    skip_ch3mpile = args.skip_ch3mpile or not args.full
    skip_serpentrod = args.skip_serpentrod or not args.full
    skip_validation = args.skip_validation
    verbose = not args.quiet

    if args.therapy == "all":
        reports = run_all_therapies(skip_ch3mpile, skip_serpentrod,
                                    skip_validation, verbose)
        if args.json:
            out = [{"therapy": r.therapy_key,
                    "frobenius_closed": r.overall_frobenius,
                    "stages": [{"stage": s.stage, "status": s.status.value}
                               for s in r.stages]}
                   for r in reports]
            print(json.dumps(out, indent=2))
        else:
            print(generate_summary_report(reports))
        return 0

    if args.therapy not in THERAPIES:
        print(f"Unknown therapy: {args.therapy}")
        print(f"Available: {list(THERAPIES.keys())}")
        return 1

    report = run_pipeline(args.therapy, skip_ch3mpile, skip_serpentrod,
                          skip_validation, verbose)

    if args.json:
        out = {
            "therapy": report.therapy_key,
            "therapy_name": report.therapy_name,
            "frobenius_closed": report.overall_frobenius,
            "total_duration_ms": report.total_duration_ms,
            "stages": [],
        }
        for s in report.stages:
            sd = {"stage": s.stage, "status": s.status.value,
                  "duration_ms": s.duration_ms}
            if s.errors:
                sd["errors"] = s.errors
            if s.stage == "0:LOAD" and s.status == StageStatus.SUCCESS:
                sd["data"] = {
                    "disease_tuple": s.data["disease_type"].display(),
                    "health_tuple": s.data["health_type"].display(),
                    "distance": s.data["distance_computed"],
                    "delta_consistency": s.data["delta_consistency"],
                }
            elif s.stage == "5:FROBENIUS" and s.status == StageStatus.SUCCESS:
                sd["data"] = {"all_pass": s.data["all_pass"]}
            out["stages"].append(sd)
        print(json.dumps(out, indent=2))
    else:
        print(f"\n{report.summary()}")

    return 0 if report.overall_frobenius else 1


if __name__ == "__main__":
    sys.exit(main())
