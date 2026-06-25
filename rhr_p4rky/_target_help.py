#!/usr/bin/env python3
"""Target-specific help for rebis.py run <target> --help."""

TARGET_EXAMPLES = {
    "serpent_rod":                  "  rebis.py run serpent_rod AUGGCCGACUGGAACUGCAAGAAGAUC\n  rebis.py run serpent_rod --file my.fasta -n myprotein\n  rebis.py run serpent_rod --validate",
    "antibody_designer":            "  rebis.py run antibody_designer --epitope EVQLVESGG\n  rebis.py run antibody_designer --builtin covid_spike\n  rebis.py run antibody_designer --all\n  rebis.py run antibody_designer --list",
    "gene_to_protein_pipeline":     "  rebis.py run gene_to_protein_pipeline ATGGCCGAC...\n  rebis.py run gene_to_protein_pipeline --file my.fasta\n  rebis.py run gene_to_protein_pipeline --test",
    "ch3mpiler_serpentrod_pipeline": "  rebis.py run ch3mpiler_serpentrod_pipeline --help",
    "psychedelic_bridge":           "  rebis.py run psychedelic_bridge compound Verticullum\n  rebis.py run psychedelic_bridge universe MyUniverse\n  rebis.py run psychedelic_bridge best MyUniverse",
    "diaschizic_iupac":             "  rebis.py run diaschizic_iupac\n  rebis.py run diaschizic_iupac --compound Verticullum\n  rebis.py run diaschizic_iupac --format json\n  rebis.py run diaschizic_iupac --output names.md",
    "ch3mpiler":                    "  rebis.py run ch3mpiler --target aspirin --retrosynthesis\n  rebis.py run ch3mpiler --target glucose --forward C6H12O6\n  rebis.py run ch3mpiler --interactive",
}
