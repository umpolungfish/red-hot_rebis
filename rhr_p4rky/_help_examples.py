#!/usr/bin/env python3
"""
_help_examples.py — Example strings for every subcommand in rebis.py.
Imported by rebis.py to keep the main file clean while providing rich --help.

Static reference data (CLINK layers, IMASM canonicals, materials catalog)
is now in INDEX.md — open with 'less INDEX.md' or any text browser.
"""

EXAMPLES = {}

EXAMPLES["status"] = """
Examples:
  rebis.py status                    # Show all component status
"""

EXAMPLES["verify"] = """
Examples:
  rebis.py verify                    # Verify Frobenius closure across all components
"""

EXAMPLES["imas"] = """
Examples:
  rebis.py imas bridge --canonical I_Dialetheic_Bootstrap   # Bridge to CLINK
  rebis.py imas bridge --canonical I_Dialetheic_Bootstrap,VII_Parakernel  # Multi-bridge
  rebis.py imas hunt --samples 100000          # Frobenius pair density estimation
  rebis.py imas hunt --samples 1000000         # Larger sample for better estimates
  rebis.py imas energy --canonical I_Dialetheic_Bootstrap --layer L8_Organism
  rebis.py imas energy --canonical V_Linear_Chain --layer L0_FrustratedBelnap5

  Static reference (canonical types, clusters, bridge table): see INDEX.md
"""

EXAMPLES["materials"] = """
Examples:
  rebis.py materials forge --all              # Forge all 8 predefined novel materials
  rebis.py materials forge --name frobenius_composite    # Forge one material by name
  rebis.py materials forge --name I_Dialetheic_Bootstrap # Forge from IMASM canonical
  rebis.py materials frobenius                # Run Frobenius metamaterial simulation
  rebis.py materials ouroboric                # Run Ouroboric alloy simulation
  rebis.py materials sophick --name eagle_9_sophick       # Run sophick on one material
  rebis.py materials sophick --name cliff                  # Frobenius Cliff analysis
  rebis.py materials sophick --name bridge                 # IMASM→Eagle bridge report
  rebis.py materials exactor --name diagnose              # Category error diagnosis
  rebis.py materials exactor --name close                 # Close Frobenius gap
  rebis.py materials exactor --name pathways              # List all exactor pathways

  Static reference (material catalog, Sophick Mercury, Eagle Cycle, gap primitives):
    see INDEX.md
"""

EXAMPLES["pipeline"] = """
Examples:
  rebis.py pipeline bridges               # List all available tool bridges
  rebis.py pipeline ground-up             # Design whole organism from quarks
  rebis.py pipeline from-layer 5 8        # Design organism starting from cell layer
  rebis.py pipeline from-layer 3 7        # Design from molecular to tissue layer
  rebis.py pipeline actionable --organism mammal    # Generate actionable outputs
  rebis.py pipeline actionable --organism human_gills  # Human+gills design package
  rebis.py pipeline actionable --organism treople     # Treople organism design
"""

EXAMPLES["clink"] = """
Examples:
  rebis.py clink layer 0                 # Show quark layer details
  rebis.py clink layer 4                 # Show cell layer details
  rebis.py clink layer 8                 # Show organism layer details
  rebis.py clink layer Organism          # Look up by name
  rebis.py clink bridge serpentrod 8     # Promotion path from SerpentRod to organism
  rebis.py clink bridge ch3mpiler 5      # Promotion path from CH3MPILER to cell
  rebis.py clink bridge gene_imscriber 6 # Promotion path from gene imscriber to tissue

  Static reference (layer table, tuples, Frobenius status, bridges): see INDEX.md
"""

EXAMPLES["run"] = """
Examples:
  rebis.py run list                      # Show all 35 discoverable targets
  rebis.py run serpentrod --seq KAL      # Run SerpentRod protein prediction
  rebis.py run serpentrod_v4 --seq ALMV  # Run SerpentRod v4
  rebis.py run ch3mpiler --help          # CH3MPILER help (passes --help through)
  rebis.py run gene_to_protein_pipeline --test   # Gene→protein pipeline (test mode)
  rebis.py run gene_to_protein_pipeline --file my.fasta  # From FASTA
  rebis.py run mito_pipeline             # Mitochondrial gene pipeline
  rebis.py run run_antibody              # Antibody designer (interactive)
  rebis.py run psychedelic_bridge        # Psychedelic bridge (intrinsics)
  rebis.py run diaschizic_iupac          # Diaschizic IUPAC generator
  rebis.py run run_gene_pipeline         # Gene imscription pipeline
  rebis.py run run_msa                   # Multiple sequence alignment
  rebis.py run run_pdb_validation        # PDB structure validation
  rebis.py run test_genetics             # Run ALL genetics tests
  rebis.py run test_genetics --b4        # B4 nucleotide lattice tests only
  rebis.py run frob_design               # Frobenius design script
  rebis.py run omonad_bridge             # Omonad bridge
  rebis.py run compute_promotions        # Promotion path computer
  rebis.py run hadron_belnap             # Hadronic Belnap-state analysis
  rebis.py run exotic_hadron_belnap      # Exotic hadronic Belnap analysis
  rebis.py run quark_belnap              # Quark Belnap analysis
"""

EXAMPLES["scripts"] = """
Examples:
  rebis.py scripts list                  # List all scripts with line counts
  rebis.py scripts run run_antibody      # Run antibody designer
  rebis.py scripts run mito_pipeline     # Run mito pipeline
  rebis.py scripts run run_msa           # Run multiple sequence alignment
  rebis.py scripts run gen_univ_map      # Generate universal map
  rebis.py scripts run frobenius_exact_design  # Run Frobenius exact design
"""
