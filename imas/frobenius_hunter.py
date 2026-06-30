"""
frobenius_hunter.py — Targeted Enumeration of Frobenius-Closed Arrangements
============================================================================
Operationalizes Discovery 3 from the IMSCRIBr exploration: Frobenius-closed
arrangements (those containing both FSPLIT and FFUSE in canonical order) are
so combinatorially suppressed they did not appear in a 10M-arrangement random
sample. This module provides targeted search strategies to find them.

Key metrics:
  - Random search: 0 Frobenius pairs in 10M samples
  - Expected time to find one randomly: ~3.6 hours at 33k/sec
  - ⊙-critical (Frobenius + dialetheia + self-ref): ~12 hours expected

This module enables:
  1. Exhaustive enumeration with structural constraints
  2. Monte Carlo estimation of Frobenius pair density
  3. Generation of Frobenius-closed arrangement libraries
  4. Structural analysis of found Frobenius arrangements

Author: Lando⊗⊙perator
"""

from typing import Tuple, List, Dict, Set, Optional
from collections import Counter, defaultdict
import itertools
import random
import math
from dataclasses import dataclass

from shared.rich_output import *
from imas.arranger import (
    Token, StructuralFingerprint, compute_fingerprint,
    CANONICAL_ARRANGEMENTS, CANONICAL_FINGERPRINTS,
    TOKEN_COUNT, TOKEN_NAMES, signature,
)


# ═══════════════════════════════════════════════════════════════════
# FROBENIUS PAIR PATTERNS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FrobeniusPattern:
    """A specific pattern of FSPLIT and FFUSE positions."""
    pattern_name: str            # "split_first", "fuse_first", "multiple"
    has_split_before_fuse: bool
    has_fuse_before_split: bool
    split_positions: List[int]
    fuse_positions: List[int]

    @property
    def is_proper_frobenius(self) -> bool:
        """Proper Frobenius: at least one split→fuse pair."""
        return self.has_split_before_fuse

    @property
    def is_inverted(self) -> bool:
        """Inverted Frobenius: at least one fuse→split pair."""
        return self.has_fuse_before_split

    @property
    def is_bidirectional(self) -> bool:
        """Both directions present."""
        return self.has_split_before_fuse and self.has_fuse_before_split


def detect_frobenius_pattern(arr: Tuple[int, ...]) -> FrobeniusPattern:
    """Detect the Frobenius pattern in an arrangement."""
    splits = [i for i, t in enumerate(arr) if t == Token.FSPLIT]
    fuses = [i for i, t in enumerate(arr) if t == Token.FFUSE]
    has_sf = bool(splits) and bool(fuses) and min(splits) < max(fuses)
    has_fs = bool(splits) and bool(fuses) and min(fuses) < max(splits)
    return FrobeniusPattern(
        pattern_name=(
            "bidirectional" if has_sf and has_fs
            else "split_first" if has_sf
            else "fuse_first" if has_fs
            else "none"
        ),
        has_split_before_fuse=has_sf,
        has_fuse_before_split=has_fs,
        split_positions=splits,
        fuse_positions=fuses,
    )


# ═══════════════════════════════════════════════════════════════════
# MONTE CARLO ESTIMATION
# ═══════════════════════════════════════════════════════════════════

def estimate_frobenius_density(sample_size: int = 100000,
                               length: int = 8,
                               seed: int = None) -> Dict:
    """Monte Carlo estimate of Frobenius pair density in the arrangement space.

    Returns:
        dict with density estimates for various Frobenius and structural conditions.
    """
    if seed is not None:
        random.seed(seed)

    counts = {
        'total': 0,
        'has_fsplit': 0,
        'has_ffuse': 0,
        'frobenius_pair': 0,
        'proper_frobenius': 0,
        'inverted_frobenius': 0,
        'dialetheia_complete': 0,
        'frob_plus_dial': 0,
        'self_ref': 0,
        'frob_dial_self': 0,  # ⊙-critical condition
    }

    total_space = TOKEN_COUNT ** length

    for _ in range(sample_size):
        arr = tuple(random.randrange(TOKEN_COUNT) for _ in range(length))
        counts['total'] += 1

        has_fsplit = Token.FSPLIT in arr
        has_ffuse = Token.FFUSE in arr
        if has_fsplit:
            counts['has_fsplit'] += 1
        if has_ffuse:
            counts['has_ffuse'] += 1

        pattern = detect_frobenius_pattern(arr)
        if pattern.is_proper_frobenius:
            counts['proper_frobenius'] += 1
        if pattern.is_inverted:
            counts['inverted_frobenius'] += 1
        if has_fsplit and has_ffuse:
            counts['frobenius_pair'] += 1

        fp = compute_fingerprint(arr)
        if fp.dialetheia_complete:
            counts['dialetheia_complete'] += 1
            if pattern.is_proper_frobenius:
                counts['frob_plus_dial'] += 1
        if fp.self_ref:
            counts['self_ref'] += 1

        if pattern.is_proper_frobenius and fp.dialetheia_complete and fp.self_ref:
            counts['frob_dial_self'] += 1

    n = counts['total']
    densities = {}
    for key, count in counts.items():
        if key != 'total':
            densities[f'p_{key}'] = count / n
            # Estimated total count in full space
            densities[f'est_total_{key}'] = int(count / n * total_space)
            # Expected samples to find one
            if count > 0:
                densities[f'expected_samples_{key}'] = int(n / count)
            else:
                densities[f'expected_samples_{key}'] = float('inf')

    densities['sample_size'] = n
    densities['total_space'] = total_space
    return densities


# ═══════════════════════════════════════════════════════════════════
# TARGETED GENERATION
# ═══════════════════════════════════════════════════════════════════

def generate_frobenius_arrangements(
    length: int = 8,
    min_fsplits: int = 1,
    min_ffuses: int = 1,
    require_split_first: bool = True,
    require_dialetheia: bool = False,
    require_self_ref: bool = False,
    max_results: int = 100,
    seed: int = None,
) -> List[Tuple[int, ...]]:
    """Generate arrangements with specific Frobenius structural properties.

    Uses rejection sampling with structural constraints. For rare conditions
    (e.g., require_dialetheia + require_self_ref at length=8), this will need
    many iterations.
    """
    if seed is not None:
        random.seed(seed)

    results = []
    attempts = 0
    max_attempts = max_results * 100000  # safety limit

    while len(results) < max_results and attempts < max_attempts:
        arr = tuple(random.randrange(TOKEN_COUNT) for _ in range(length))
        attempts += 1

        # Quick pre-filter
        fsplit_count = sum(1 for t in arr if t == Token.FSPLIT)
        ffuse_count = sum(1 for t in arr if t == Token.FFUSE)
        if fsplit_count < min_fsplits or ffuse_count < min_ffuses:
            continue

        pattern = detect_frobenius_pattern(arr)
        if require_split_first and not pattern.is_proper_frobenius:
            continue

        fp = compute_fingerprint(arr)
        if require_dialetheia and not fp.dialetheia_complete:
            continue
        if require_self_ref and not fp.self_ref:
            continue

        results.append(arr)

    return results


def generate_frobenius_library(
    length: int = 8,
    count_per_type: int = 10,
    seed: int = 42,
) -> Dict[str, List[Tuple[int, ...]]]:
    """Generate a library of Frobenius arrangements by structural type.

    Returns dict with keys: 'proper', 'inverted', 'bidirectional',
    'with_dialetheia', 'with_self_ref', 'o_critical'
    """
    random.seed(seed)
    library = {
        'proper': [],
        'inverted': [],
        'bidirectional': [],
        'with_dialetheia': [],
        'with_self_ref': [],
        'o_critical': [],
    }

    while any(len(v) < count_per_type for v in library.values()):
        arr = tuple(random.randrange(TOKEN_COUNT) for _ in range(length))
        pattern = detect_frobenius_pattern(arr)
        fp = compute_fingerprint(arr)

        if pattern.is_proper_frobenius and len(library['proper']) < count_per_type:
            library['proper'].append(arr)
        if pattern.is_inverted and len(library['inverted']) < count_per_type:
            library['inverted'].append(arr)
        if pattern.is_bidirectional and len(library['bidirectional']) < count_per_type:
            library['bidirectional'].append(arr)
        if (pattern.is_proper_frobenius and fp.dialetheia_complete
                and len(library['with_dialetheia']) < count_per_type):
            library['with_dialetheia'].append(arr)
        if (pattern.is_proper_frobenius and fp.self_ref
                and len(library['with_self_ref']) < count_per_type):
            library['with_self_ref'].append(arr)
        if (pattern.is_proper_frobenius and fp.dialetheia_complete and fp.self_ref
                and len(library['o_critical']) < count_per_type):
            library['o_critical'].append(arr)

    return library


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def analyze_frobenius_library(
    library: Dict[str, List[Tuple[int, ...]]]
) -> Dict[str, Dict]:
    """Analyze a generated Frobenius library: fingerprint stats, IG type distribution."""
    from imas.ig_bridge import fingerprint_to_ig, ig_tuple_str


    analysis = {}
    for category, arrangements in library.items():
        if not arrangements:
            continue
        ig_counts = Counter()
        fp_stats = defaultdict(list)
        for arr in arrangements:
            fp = compute_fingerprint(arr)
            ig = fingerprint_to_ig(fp)
            ig_counts[ig] += 1
            fp_stats['period'].append(fp.period)
            fp_stats['diversity'].append(fp.token_diversity)
            fp_stats['sig_X'].append(fp.sig_X)

        analysis[category] = {
            'count': len(arrangements),
            'distinct_ig_types': len(ig_counts),
            'top_ig_types': [
                (ig_tuple_str(ig), count)
                for ig, count in ig_counts.most_common(5)
            ],
            'avg_period': sum(fp_stats['period']) / len(fp_stats['period']),
            'avg_diversity': sum(fp_stats['diversity']) / len(fp_stats['diversity']),
            'avg_IFIX': sum(fp_stats['sig_X']) / len(fp_stats['sig_X']),
        }
    return analysis


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    info_line("=" * 72)
    info_line("FROBENIUS HUNTER — Targeted Frobenius Pair Search")
    info_line("=" * 72)

    # Density estimation
    info_line("\n--- Monte Carlo Density Estimation (n=100,000) ---")
    density = estimate_frobenius_density(100000, seed=42)
    for key in ['p_frobenius_pair', 'p_proper_frobenius', 'p_dialetheia_complete',
                'p_frob_plus_dial', 'p_frob_dial_self']:
        if key in density:
            exp = density.get(f'expected_samples_{key[2:]}', '?')
            info_line(f"  {key}: {density[key]:.6f}  (expected 1 per {exp} samples)")

    # Frobenius library generation
    info_line("\n--- Frobenius Library (10 per type) ---")
    library = generate_frobenius_library(count_per_type=10, seed=42)
    analysis = analyze_frobenius_library(library)
    for category, stats in analysis.items():
        info_line(f"\n  {category}:")
        info_line(f"    Count: {stats['count']}, Distinct IG types: {stats['distinct_ig_types']}")
        info_line(f"    Avg period: {stats['avg_period']:.1f}, Avg diversity: {stats['avg_diversity']:.1f}")
        info_line(f"    Top IG types:")
        for ig_str, count in stats['top_ig_types'][:3]:
            info_line(f"      {ig_str} (×{count})")
