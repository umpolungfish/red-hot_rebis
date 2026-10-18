"""
rebis.gene — Gene Imscriber & Genetic Engineering (ADVANCED v2)
════════════════════════════════════════════════════════════════════
Full implementations using:
  - gene_imscriber: GeneticEngine, B4 lattice, codon analysis, tuples
  - rhr_p4rky: genetic_code, genetics_b4, gene_to_protein_pipeline

Callable as a command:
  rebis.gene analyze <sequence> [--translate] [--orfs]
  rebis.gene quality <sequence>
  rebis.gene tuples <sequence>
  rebis.gene translate <dna>
  rebis.gene b4 <sequence>
  rebis.gene pipeline <dna> [--skip-ch3mpile] [--skip-serpentrod]
  rebis.gene list
"""
import sys, importlib, argparse, json, io
from pathlib import Path
from rebis.file_input import parse_with_file

_REBIS_ROOT = Path(__file__).parent.parent.absolute()
for p in [str(_REBIS_ROOT), str(_REBIS_ROOT / "gene_imscriber"),
          str(_REBIS_ROOT / "rhr_p4rky"), str(_REBIS_ROOT / "shared")]:
    if p not in sys.path:
        sys.path.insert(0, p)

_EXPORTS = {'verify_all': 'gene_imscriber.engine', 'demo_b4_lattice': 'gene_imscriber.engine', 'extract_features_from_sequence': 'gene_imscriber.tuples', 'generate_all_tuples': 'gene_imscriber.tuples', 'GeneToProteinPipeline': 'rhr_p4rky.gene_to_protein_pipeline', 'verify_all_codons_frobenius': 'rhr_p4rky.genetic_code', 'BelnapCodon': 'rhr_p4rky.genetics_b4'}
__all__ = list(_EXPORTS) + ["verify_genetic_code"]


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(importlib.import_module(_EXPORTS[name]), name)
    globals()[name] = value
    return value


def verify_genetic_code():
    """Return the existing codon verification's complete-coverage result."""
    from rhr_p4rky.genetic_code import verify_all_codons_frobenius
    result = verify_all_codons_frobenius()
    return result["total_codons"] == 64 and result["frobenius_violations"] == 0


# ── Standard genetic code table ──
CODON_TABLE = {
    'TTT':'F','TTC':'F','TTA':'L','TTG':'L','CTT':'L','CTC':'L','CTA':'L','CTG':'L',
    'ATT':'I','ATC':'I','ATA':'I','ATG':'M','GTT':'V','GTC':'V','GTA':'V','GTG':'V',
    'TCT':'S','TCC':'S','TCA':'S','TCG':'S','CCT':'P','CCC':'P','CCA':'P','CCG':'P',
    'ACT':'T','ACC':'T','ACA':'T','ACG':'T','GCT':'A','GCC':'A','GCA':'A','GCG':'A',
    'TAT':'Y','TAC':'Y','TAA':'*','TAG':'*','CAT':'H','CAC':'H','CAA':'Q','CAG':'Q',
    'AAT':'N','AAC':'N','AAA':'K','AAG':'K','GAT':'D','GAC':'D','GAA':'E','GAG':'E',
    'TGT':'C','TGC':'C','TGA':'*','TGG':'W','CGT':'R','CGC':'R','CGA':'R','CGG':'R',
    'AGT':'S','AGC':'S','AGA':'R','AGG':'R','GGT':'G','GGC':'G','GGA':'G','GGG':'G',
}


def _translate_dna(dna):
    """Translate DNA to protein, stopping at first stop codon."""
    dna = dna.upper().replace('U', 'T')
    protein = []
    for i in range(0, len(dna) - 2, 3):
        codon = dna[i:i+3]
        aa = CODON_TABLE.get(codon, '?')
        if aa == '*':
            break
        protein.append(aa)
    return ''.join(protein)


def _find_orfs(dna, min_len=30):
    """Find complete start-to-stop ORFs on both strands.

    Coordinates are zero-based half-open intervals on the supplied sequence.
    Frame is the offset (0, 1, 2) on the indicated strand. The minimum length
    counts coding bases before the stop codon; length_bp includes that codon.
    """
    if min_len < 0:
        raise ValueError("Minimum ORF length must be nonnegative")
    dna = dna.upper().replace('U', 'T')
    reverse = dna.translate(str.maketrans('ACGT', 'TGCA'))[::-1]
    orfs = []
    for strand, sequence in (('+', dna), ('-', reverse)):
        for frame in range(3):
            starts = []
            for i in range(frame, len(sequence) - 2, 3):
                codon = sequence[i:i+3]
                if codon == 'ATG':
                    starts.append(i)
                elif CODON_TABLE.get(codon) == '*':
                    for start in starts:
                        if i - start < min_len:
                            continue
                        end = i + 3
                        protein = _translate_dna(sequence[start:i])
                        left, right = ((start, end) if strand == '+' else
                                       (len(dna) - end, len(dna) - start))
                        orfs.append({
                            "start": left, "end": right, "frame": frame,
                            "strand": strand, "length_bp": end - start,
                            "protein": protein, "protein_length": len(protein),
                        })
                    starts = []
    return orfs


def _json_or_str(obj):
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, default=str, ensure_ascii=False)
    if hasattr(obj, '__dict__'):
        try:
            return json.dumps(vars(obj), indent=2, default=str, ensure_ascii=False)
        except Exception:
            return str(obj)
    return str(obj)


def _cmd_analyze(args):
    """Analyze genetic sequence — codons, ORFs, base composition, B4 lattice."""
    if not args.sequence:
        print("Error: DNA/RNA sequence required.")
        print("Example:  rebis.gene analyze ATGGCGTAA")
        return 1
    seq = args.sequence.upper().replace('U', 'T')
    print(f"═ Genetic Sequence Analysis ═")
    print(f"  Length: {len(seq)} bp")

    bases = {b: seq.count(b) for b in 'ATGC'}
    gc = round((bases.get('G', 0) + bases.get('C', 0)) / max(len(seq), 1), 4)

    output = {
        "sequence": args.sequence,
        "length": len(seq),
        "base_composition": bases,
        "gc_content": gc,
    }

    # Find ORFs
    if args.orfs or args.translate:
        print("  Scanning ORFs (6 frames)...")
        orfs = _find_orfs(seq)
        output["orfs"] = orfs
        output["n_orfs"] = len(orfs)
        if orfs:
            longest = max(orfs, key=lambda o: o["protein_length"])
            output["longest_orf"] = longest
            print(f"  Found {len(orfs)} ORFs — longest: {longest['protein_length']} aa")

    # Translate
    if args.translate:
        protein = _translate_dna(seq)
        output["translation"] = protein
        output["protein_length"] = len(protein)
        print(f"  Translation: {protein[:50]}{'...' if len(protein) > 50 else ''}")

    # B4 lattice via rhr_p4rky
    try:
        print("  Verifying B4 lattice (64-codon Frobenius)...")
        b4_result = verify_genetic_code()
        output["b4_lattice"] = "verified" if b4_result else "failed"
    except Exception as exc:
        output["b4_lattice"] = {"error": str(exc)}

    print(_json_or_str(output))
    return int(output["b4_lattice"] != "verified")


def _cmd_quality(args):
    """Compute genetic quality score."""
    if not args.sequence:
        print("Error: DNA/RNA sequence required.")
        return 1
    seq = args.sequence.upper().replace('U', 'T')
    print(f"═ Genetic Quality Score ═")
    print(f"  Length: {len(seq)} bp")

    # Base composition
    gc = (seq.count('G') + seq.count('C')) / max(len(seq), 1)

    # ORF quality
    orfs = _find_orfs(seq)
    longest_orf = max((o["protein_length"] for o in orfs), default=0)

    # Codon usage
    codon_counts = {}
    for i in range(0, len(seq) - 2, 3):
        c = seq[i:i+3]
        codon_counts[c] = codon_counts.get(c, 0) + 1

    # Advanced quality via gene_imscriber
    ig_quality = None
    try:
        from gene_imscriber.genetics_qs import compute_quality_score
        ig_quality = compute_quality_score(seq)
    except Exception:
        pass

    output = {
        "sequence_length": len(seq),
        "gc_content": round(gc, 4),
        "gc_percent": round(gc * 100, 1),
        "n_orfs": len(orfs),
        "longest_orf_aa": longest_orf,
        "codon_diversity": len(codon_counts),
        "codon_counts": codon_counts,
        "ig_quality_score": ig_quality if isinstance(ig_quality, (int, float, dict, list)) else str(ig_quality) if ig_quality else None,
    }
    print(_json_or_str(output))
    return 0


def _cmd_tuples(args):
    """Compute genetic IG tuples."""
    if not args.sequence:
        print("Error: DNA/RNA sequence required.")
        return 1
    seq = args.sequence.upper().replace('U', 'T')
    print(f"═ Genetic IG Tuples ═")
    try:
        from gene_imscriber.tuples import extract_features_from_sequence, generate_all_tuples
        from rhr_p4rky.genetic_code import SYMBOL_TO_AA
        aas = []
        for i in range(0, len(seq) - 2, 3):
            codon = seq[i:i+3].replace('T', 'U')
            aa = SYMBOL_TO_AA[codon]
            if aa == "Stop":
                break
            aas.append({"aa_code": aa})
        features = extract_features_from_sequence(
            aas, gc_content=(seq.count('G') + seq.count('C')) / len(seq))
        result = generate_all_tuples(features)
        print(_json_or_str(result))
    except Exception as e:
        # Fallback: compute basic tuples from codon analysis
        print(f"  Advanced tuples unavailable ({e}), computing basic tuples...")
        protein = _translate_dna(seq)
        output = {
            "sequence": args.sequence,
            "protein": protein,
            "protein_length": len(protein),
            "aa_composition": {aa: protein.count(aa) for aa in set(protein)},
        }
        output["error"] = str(e)
        print(_json_or_str(output))
        return 1
    return 0


def _cmd_translate(args):
    """Translate DNA to protein."""
    if not args.dna:
        print("Error: DNA sequence required.")
        return 1
    dna = args.dna.upper().replace('U', 'T')
    print(f"═ DNA → Protein Translation ═")
    print(f"  DNA length: {len(dna)} bp")
    protein = _translate_dna(dna)
    orfs = _find_orfs(dna)
    output = {
        "dna": args.dna,
        "protein": protein,
        "protein_length": len(protein),
        "n_codons": len(protein),
        "n_orfs_found": len(orfs),
        "molecular_weight_kda": round(len(protein) * 110.0 / 1000, 2),
    }
    print(_json_or_str(output))
    return 0


def _cmd_b4(args):
    """Run B4 lattice verification (64-codon Frobenius)."""
    print("═ B4 Lattice — 64-Codon Frobenius Verification ═")
    try:
        print("  Verifying all 64 codons...")
        result = verify_genetic_code()
        output = {
            "b4_verified": result,
            "n_codons": 64,
            "message": "All 64 codons satisfy Frobenius closure" if result else "B4 lattice verification failed",
        }
        print(_json_or_str(output))
    except Exception as e:
        import traceback
        print(f"B4 lattice verification failed: {e}")
        traceback.print_exc()
        return 1
    return int(not result)

def _cmd_pipeline(args):
    """Run full gene-to-protein pipeline."""
    if not args.dna:
        print("Error: DNA sequence required.")
        print("Example:  rebis.gene pipeline ATGGCGTAA")
        return 1
    dna = args.dna.upper().replace('U', 'T')
    print(f"═ Gene → Protein Pipeline ═")
    print(f"  DNA: {dna[:50]}{'...' if len(dna) > 50 else ''}")
    print(f"  Length: {len(dna)} bp")
    try:
        from rhr_p4rky.gene_to_protein_pipeline import GeneToProteinPipeline
        # The pipeline takes its sequence at construction; run() takes the
        # subunit count and an optional structure path, not the sequence.
        pipeline = GeneToProteinPipeline(dna)
        result = pipeline.run()
        print(_json_or_str(result))
    except Exception as e:
        import traceback
        print(f"  Advanced pipeline unavailable ({e}), using built-in translation...")
        traceback.print_exc()
        # Fallback: manual gene→protein
        protein = _translate_dna(dna)
        orfs = _find_orfs(dna)
        output = {
            "error": str(e),
            "completed_pipeline": False,
            "dna": args.dna,
            "stages": {
                "transcription": {"mrna": dna.replace('T', 'U'), "length": len(dna)},
                "translation": {"protein": protein, "length": len(protein)},
                "orfs": orfs,
                "molecular_weight_kda": round(len(protein) * 110.0 / 1000, 2),
            },
        }
        print(_json_or_str(output))
        return 1
    return 0


def _cmd_list(args):
    print("rebis.gene — Exports:")
    failed = False
    for name in sorted(__all__):
        try:
            getattr(sys.modules[__name__], name)
            print(f"  ✓ {name}")
        except Exception as exc:
            print(f"  ✗ {name}: {exc}")
            failed = True
    print("\nCommands:")
    print("  analyze <seq>      — Full sequence analysis (codons, ORFs, B4)")
    print("  quality <seq>      — Genetic quality score")
    print("  tuples <seq>       — IG genetic tuples")
    print("  translate <dna>    — DNA → protein translation")
    print("  b4                 — B4 lattice 64-codon verification")
    print("  pipeline <dna>     — Full gene→protein pipeline")
    print("  list               — List exports")
    return int(failed)


def main():
    """CLI: rebis.gene <command> [args]"""
    parser = argparse.ArgumentParser(
        prog="rebis.gene",
        description="rebis.gene — Gene Imscriber & Genetic Engineering",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    sub = parser.add_subparsers(dest="command", metavar="COMMAND",
                                help="Sub-command (run with COMMAND --help for details)")

    p_ana = sub.add_parser("analyze",
        help="Analyze genetic sequence (codons, ORFs, base composition, B4)",
        description="Full genetic sequence analysis:\n"
                    "  - Base composition + GC content\n"
                    "  - Open reading frame detection (6 frames)\n"
                    "  - DNA→protein translation\n"
                    "  - B4 lattice 64-codon Frobenius verification",
        epilog="Examples:  rebis.gene analyze ATGGCGTAA --translate --orfs\n"
               "           rebis.gene analyze -f gene.fasta --orfs",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ana.add_argument("sequence", nargs="?", default="",
                       help="DNA/RNA sequence (A, T/U, G, C)")
    p_ana.add_argument("--translate", action="store_true",
                       help="Include DNA→protein translation")
    p_ana.add_argument("--orfs", action="store_true",
                       help="Scan all 6 reading frames for ORFs")
    p_ana.set_defaults(func=_cmd_analyze)

    p_qual = sub.add_parser("quality",
        help="Compute genetic quality score",
        description="Compute IG genetic quality score — evaluates\n"
                    "codon optimality, GC content, ORF quality, and\n"
                    "structural stability via B4 lattice metrics.",
        epilog="Example:  rebis.gene quality ATGGCGTAA",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_qual.add_argument("sequence", nargs="?", default="",
                        help="DNA/RNA sequence")
    p_qual.set_defaults(func=_cmd_quality)

    p_tup = sub.add_parser("tuples",
        help="Compute IG genetic tuples from sequence",
        description="Compute 12-primitive IG tuples for a genetic sequence\n"
                    "using the gene_imscriber tuple extraction pipeline.",
        epilog="Example:  rebis.gene tuples ATGGCGTAA",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_tup.add_argument("sequence", nargs="?", default="",
                       help="DNA/RNA sequence")
    p_tup.set_defaults(func=_cmd_tuples)

    p_tra = sub.add_parser("translate",
        help="Translate DNA to protein",
        description="Translate a DNA sequence to protein using the\n"
                    "standard genetic code (64-codon table).",
        epilog="Example:  rebis.gene translate ATGGCGGCGTAA",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_tra.add_argument("dna", nargs="?", default="",
                       help="DNA sequence")
    p_tra.set_defaults(func=_cmd_translate)

    p_b4 = sub.add_parser("b4",
        help="Run B4 lattice 64-codon Frobenius verification",
        description="Verify that all 64 codons satisfy Frobenius closure\n"
                    "in the B4 lattice structure.",
        epilog="Example:  rebis.gene b4",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_b4.set_defaults(func=_cmd_b4)

    p_pipe = sub.add_parser("pipeline",
        help="Run full gene-to-protein pipeline",
        description="Run the full gene→protein pipeline:\n"
                    "  DNA → mRNA → polypeptide → folded protein\n"
                    "Uses rhr_p4rky GeneToProteinPipeline (7-stage\n"
                    "Frobenius-verified translation).",
        epilog="Example:  rebis.gene pipeline ATGGCGGCGAAATAA",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_pipe.add_argument("dna", nargs="?", default="",
                        help="DNA sequence")
    p_pipe.add_argument("--skip-ch3mpile", action="store_true",
                        help="Skip ch3mpiler stage")
    p_pipe.add_argument("--skip-serpentrod", action="store_true",
                        help="Skip serpentrod stage")
    p_pipe.set_defaults(func=_cmd_pipeline)

    p_ls = sub.add_parser("list",
        help="List all exported symbols",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_ls.set_defaults(func=_cmd_list)

    p_inf = sub.add_parser("info",
        help="Show available tools (alias for list)",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p_inf.set_defaults(func=_cmd_list)

    sub.add_parser("help",
        help="Show this help message",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    args = parse_with_file(parser)

    if not args.command or args.command == "help":
        parser.print_help()
        return 0

    if hasattr(args, 'func'):
        return args.func(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
