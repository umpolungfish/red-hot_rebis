#!/usr/bin/env python3
"""Target-specific help for rebis.py run <target> --help."""
import sys
from pathlib import Path

REBIS_ROOT = Path(__file__).parent.absolute()

TARGET_EXAMPLES = {
    "serpentrod":           "  rebis.py run serpentrod --seq KAL\n  rebis.py run serpentrod --seq ALMVL",
    "serpentrod_v4":        "  rebis.py run serpentrod_v4 --seq ALMV",
    "serpentrod_pred":      "  rebis.py run serpentrod_pred --seq KAL",
    "ch3mpiler":            "  rebis.py run ch3mpiler --help\n  rebis.py run ch3mpiler --target aspirin --retrosynthesis",
    "gene":                 "  rebis.py run gene --help\n  rebis.py run gene --rna AUGGCC...",
    "gene_to_protein_pipeline": "  rebis.py run gene_to_protein_pipeline --test\n  rebis.py run gene_to_protein_pipeline AAAAATGGCT...\n  rebis.py run gene_to_protein_pipeline --file my.fasta",
    "run_gene_pipeline":    "  rebis.py run run_gene_pipeline --test\n  rebis.py run run_gene_pipeline ATG...\n  rebis.py run run_gene_pipeline --file my.fasta -n mygene",
    "demo_gene_to_protein": "  rebis.py run demo_gene_to_protein",
    "test_genetics":        "  rebis.py run test_genetics\n  rebis.py run test_genetics --b4\n  rebis.py run test_genetics --codons\n  rebis.py run test_genetics --pipeline\n  rebis.py run test_genetics --quick\n  rebis.py run test_genetics --phi\n  rebis.py run test_genetics --kernel",
    "run_serpent":          "  rebis.py run run_serpent",
    "serpent_rod":          "  rebis.py run serpent_rod",
    "serpent_rod_v2":       "  rebis.py run serpent_rod_v2",
    "run_antibody":         "  rebis.py run run_antibody",
    "run_msa":              "  rebis.py run run_msa",
    "run_pdb_validation":   "  rebis.py run run_pdb_validation",
    "mito_pipeline":        "  rebis.py run mito_pipeline",
    "msa_analysis":         "  rebis.py run msa_analysis",
    "psychedelic_bridge":   "  rebis.py run psychedelic_bridge",
    "diaschizic_iupac":     "  rebis.py run diaschizic_iupac",
    "frob_design":          "  rebis.py run frob_design",
    "frobenius_exact_design": "  rebis.py run frobenius_exact_design",
    "gen_univ_map":         "  rebis.py run gen_univ_map",
    "omonad_bridge":        "  rebis.py run omonad_bridge",
    "compute_promotions":   "  rebis.py run compute_promotions",
    "analyze_validation":   "  rebis.py run analyze_validation",
    "hadron_belnap":        "  rebis.py run hadron_belnap",
    "exotic_hadron_belnap": "  rebis.py run exotic_hadron_belnap",
    "quark_belnap":         "  rebis.py run quark_belnap",
    "ch3mpiler_bridge":     "  rebis.py run ch3mpiler_bridge",
    "ch3mpiler_ob3ect_bridge": "  rebis.py run ch3mpiler_ob3ect_bridge",
    "ch3mpiler_serpentrod_pipeline": "  rebis.py run ch3mpiler_serpentrod_pipeline",
    "clu_power_law":        "  rebis.py run clu_power_law",
    "frobenius_filtration": "  rebis.py run frobenius_filtration",
    "genetic_code":         "  rebis.py run genetic_code",
    "pdb_validator":        "  rebis.py run pdb_validator",
    "antibody_designer":    "  rebis.py run antibody_designer",
}
