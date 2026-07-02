#!/usr/bin/env python3
"""
add_missing_enzymes.py — 45 additional landmark enzymes filling EC class gaps.
Adds to PROTEIN_LOOKUP in expanded_catalyzing_proteins.
"""

MISSING_ENZYMES = [
    # ═══ EC 1: OXIDOREDUCTASES (gaps: P450s, peroxidases, oxidases) ═══
    {
        "name": "cytochrome_p450_3a4",
        "organism": "Homo sapiens",
        "pdb": "1TQN",
        "active_site_residues": ["Cys442", "Thr309"],
        "catalytic_roles": ["heme ligand (Cys442)", "proton relay (Thr309)"],
        "reaction": "NADPH-dependent monooxygenation; metabolizes 50% of clinical drugs",
        "smiles_substrate_hint": "CC(=O)Nc1ccc(O)cc1",
    },
    {
        "name": "cytochrome_p450_2c9",
        "organism": "Homo sapiens",
        "pdb": "1OG2",
        "active_site_residues": ["Cys435", "Arg108"],
        "catalytic_roles": ["heme ligand (Cys435)", "substrate anchoring (Arg108)"],
        "reaction": "Oxidation of warfarin, NSAIDs, and sulfonylureas",
        "smiles_substrate_hint": "O=C1CC(c2ccccc2)OC2=C1C(=O)CC(C)(C)C2",
    },
    {
        "name": "cytochrome_p450_2d6",
        "organism": "Homo sapiens",
        "pdb": "3QM4",
        "active_site_residues": ["Cys443", "Phe120"],
        "catalytic_roles": ["heme ligand (Cys443)", "substrate positioning (Phe120)"],
        "reaction": "Oxidation of antidepressants, beta-blockers, codeine",
        "smiles_substrate_hint": "COc1ccc2c(c1)C(C)=C(C)N2",
    },
    {
        "name": "myeloperoxidase",
        "organism": "Homo sapiens",
        "pdb": "1D5T",
        "active_site_residues": ["His336", "Arg239", "Gln91"],
        "catalytic_roles": ["distal His (His336)", "chloride binding (Arg239)", "heme linkage (Gln91)"],
        "reaction": "H2O2-dependent oxidation of Cl- to HOCl; neutrophil antimicrobial",
        "smiles_substrate_hint": "OCl",
    },
    {
        "name": "cyclooxygenase_2",
        "organism": "Homo sapiens",
        "pdb": "1CX2",
        "active_site_residues": ["Tyr385", "Ser530", "Arg120"],
        "catalytic_roles": ["tyrosyl radical (Tyr385)", "aspirin acetylation (Ser530)", "substrate binding (Arg120)"],
        "reaction": "Arachidonic acid to PGH2; inflammatory prostaglandin synthesis",
        "smiles_substrate_hint": "CCCCCC=CCC=CCC=CCC=CCCCC(=O)O",
    },
    {
        "name": "cytochrome_c_oxidase",
        "organism": "Bos taurus",
        "pdb": "1OCC",
        "active_site_residues": ["His240", "His290", "Tyr244"],
        "catalytic_roles": ["CuB ligand (His240)", "heme a3 ligand (His290)", "cross-link to His240 (Tyr244)"],
        "reaction": "4 Cyt c(Fe2+) + O2 + 8H+ -> 4 Cyt c(Fe3+) + 4H2O",
        "smiles_substrate_hint": "O=O",
    },
    {
        "name": "dihydrofolate_reductase",
        "organism": "Homo sapiens",
        "pdb": "2DHF",
        "active_site_residues": ["Glu30", "Phe31", "Ile7"],
        "catalytic_roles": ["protonation of N5 (Glu30)", "NADPH positioning (Phe31)", "substrate pocket (Ile7)"],
        "reaction": "NADPH-dependent reduction of DHF to THF; nucleotide synthesis",
        "smiles_substrate_hint": "Nc1nc2N=C(N)NC(=O)c2nc1",
    },
    {
        "name": "aldehyde_dehydrogenase",
        "organism": "Homo sapiens",
        "pdb": "1O00",
        "active_site_residues": ["Cys302", "Glu268"],
        "catalytic_roles": ["nucleophile (Cys302)", "general base (Glu268)"],
        "reaction": "NAD+-dependent oxidation of aldehydes to carboxylic acids",
        "smiles_substrate_hint": "CC=O",
    },
    {
        "name": "monoamine_oxidase_A",
        "organism": "Homo sapiens",
        "pdb": "2BXS",
        "active_site_residues": ["Cys406", "Tyr407", "Tyr444"],
        "catalytic_roles": ["FAD attachment (Cys406)", "flavin stacking (Tyr407)", "substrate oxidation (Tyr444)"],
        "reaction": "Oxidative deamination of serotonin, norepinephrine, dopamine",
        "smiles_substrate_hint": "NCCc1c[nH]c2ccc(O)cc12",
    },
    {
        "name": "glutathione_peroxidase",
        "organism": "Homo sapiens",
        "pdb": "1GP1",
        "active_site_residues": ["Sec45", "Gln81", "Trp158"],
        "catalytic_roles": ["selenocysteine nucleophile (Sec45)", "stabilization (Gln81)", "substrate binding (Trp158)"],
        "reaction": "2 GSH + ROOH -> GSSG + ROH + H2O",
        "smiles_substrate_hint": "N[C@@H](CS)C(=O)NCC(=O)O",
    },

    # ═══ EC 2: TRANSFERASES (gaps: methyltransferases, acetyltransferases, glycosyltransferases) ═══
    {
        "name": "catechol_o_methyltransferase",
        "organism": "Homo sapiens",
        "pdb": "1VID",
        "active_site_residues": ["Asp141", "Asp169", "Lys144"],
        "catalytic_roles": ["Mg2+ binding (Asp141)", "Mg2+ binding (Asp169)", "deprotonation (Lys144)"],
        "reaction": "SAM-dependent methylation of catecholamines",
        "smiles_substrate_hint": "COc1ccc(O)c(O)c1",
    },
    {
        "name": "histone_acetyltransferase",
        "organism": "Homo sapiens",
        "pdb": "3BIY",
        "active_site_residues": ["Glu570", "Tyr616"],
        "catalytic_roles": ["general base (Glu570)", "acetyl-CoA binding (Tyr616)"],
        "reaction": "Acetyl-CoA-dependent lysine acetylation of histones",
        "smiles_substrate_hint": "CC(=O)SCCNC(=O)CCNC(=O)C(O)C(C)(C)COP(=O)(O)OP(=O)(O)OC",
    },
    {
        "name": "dna_methyltransferase",
        "organism": "Homo sapiens",
        "pdb": "3SWR",
        "active_site_residues": ["Cys1226", "Glu1266", "Arg1310"],
        "catalytic_roles": ["nucleophile (Cys1226)", "proton shuttle (Glu1266)", "DNA binding (Arg1310)"],
        "reaction": "SAM-dependent methylation of CpG cytosine C5",
        "smiles_substrate_hint": "Nc1nc(=O)[nH]c(=O)c1",
    },
    {
        "name": "glutathione_s_transferase",
        "organism": "Homo sapiens",
        "pdb": "1GSD",
        "active_site_residues": ["Tyr7", "Arg15", "Gln67"],
        "catalytic_roles": ["GSH deprotonation (Tyr7)", "GSH binding (Arg15)", "stabilization (Gln67)"],
        "reaction": "GSH conjugation to electrophilic xenobiotics; detoxification",
        "smiles_substrate_hint": "N[C@@H](CS)C(=O)NCC(=O)O",
    },
    {
        "name": "glycogen_phosphorylase",
        "organism": "Homo sapiens",
        "pdb": "1L5Q",
        "active_site_residues": ["Lys680", "His377", "Tyr573"],
        "catalytic_roles": ["PLP anchor (Lys680)", "phosphate transfer (His377)", "substrate binding (Tyr573)"],
        "reaction": "Glycogen(n) + Pi -> glycogen(n-1) + G1P",
        "smiles_substrate_hint": "OC1C(CO)OC(OC2C(CO)OC(OC3C(CO)OC(O)C(O)C3O)C(O)C2O)C(O)C1O",
    },
    {
        "name": "hexokinase",
        "organism": "Homo sapiens",
        "pdb": "1HKB",
        "active_site_residues": ["Asp657", "Lys621", "Asp208"],
        "catalytic_roles": ["general base (Asp657)", "ATP binding (Lys621)", "Mg2+ coordination (Asp208)"],
        "reaction": "Glucose + ATP -> glucose-6-phosphate + ADP",
        "smiles_substrate_hint": "OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@@H]1O",
    },
    {
        "name": "creatine_kinase",
        "organism": "Homo sapiens",
        "pdb": "3B6R",
        "active_site_residues": ["Cys283", "His296", "Asp335"],
        "catalytic_roles": ["active site (Cys283)", "proton relay (His296)", "Mg2+ binding (Asp335)"],
        "reaction": "Creatine + ATP <-> phosphocreatine + ADP; energy buffer",
        "smiles_substrate_hint": "N=C(N)N(C)CC(=O)O",
    },

    # ═══ EC 3: HYDROLASES (gaps: nucleases, lipases, glycosidases, ATPases) ═══
    {
        "name": "ribonuclease_A",
        "organism": "Bos taurus",
        "pdb": "7RSA",
        "active_site_residues": ["His12", "His119", "Lys41"],
        "catalytic_roles": ["general acid (His12)", "general base (His119)", "transition state (Lys41)"],
        "reaction": "RNA cleavage at 3' of pyrimidine nucleotides",
        "smiles_substrate_hint": "O=P(O)(OC1C(O)C(O)C(CO)O1)O",
    },
    {
        "name": "lysozyme",
        "organism": "Gallus gallus",
        "pdb": "2LYZ",
        "active_site_residues": ["Glu35", "Asp52"],
        "catalytic_roles": ["general acid (Glu35)", "electrostatic stabilization (Asp52)"],
        "reaction": "Hydrolysis of beta-1,4-glycosidic bonds in peptidoglycan",
        "smiles_substrate_hint": "O=C(N)C(O)C(N)=O",
    },
    {
        "name": "pancreatic_lipase",
        "organism": "Homo sapiens",
        "pdb": "1LPA",
        "active_site_residues": ["Ser152", "His263", "Asp176"],
        "catalytic_roles": ["nucleophile (Ser152)", "general base (His263)", "charge relay (Asp176)"],
        "reaction": "Hydrolysis of triglycerides to fatty acids + glycerol",
        "smiles_substrate_hint": "CCCCCCCCCCCCCCCCCC(=O)OCC(OC(=O)CCCCCCCCCCCCCCCCC)COC(=O)CCCCCCCCCCCCCCCCC",
    },
    {
        "name": "acetylcholinesterase",
        "organism": "Homo sapiens",
        "pdb": "4EY7",
        "active_site_residues": ["Ser203", "His447", "Glu334"],
        "catalytic_roles": ["nucleophile (Ser203)", "general base (His447)", "charge relay (Glu334)"],
        "reaction": "Hydrolysis of acetylcholine to choline + acetate",
        "smiles_substrate_hint": "CC(=O)OCC[N+](C)(C)C",
    },
    {
        "name": "beta_lactamase",
        "organism": "Escherichia coli",
        "pdb": "1BTL",
        "active_site_residues": ["Ser70", "Lys73", "Glu166"],
        "catalytic_roles": ["nucleophile (Ser70)", "general base (Lys73)", "deacylation water (Glu166)"],
        "reaction": "Hydrolysis of beta-lactam antibiotics; drug resistance",
        "smiles_substrate_hint": "O=C1N2C(C(=O)O)=C(C)CS[C@H]12",
    },
    {
        "name": "urease",
        "organism": "Helicobacter pylori",
        "pdb": "1E9Z",
        "active_site_residues": ["His320", "His322", "Lys219"],
        "catalytic_roles": ["Ni2+ ligand (His320)", "Ni2+ ligand (His322)", "carbamylated bridge (Lys219)"],
        "reaction": "Urea + H2O -> 2 NH3 + CO2; gastric survival",
        "smiles_substrate_hint": "NC(=O)N",
    },
    {
        "name": "sars_cov2_plpro",
        "organism": "SARS-CoV-2",
        "pdb": "6WX4",
        "active_site_residues": ["Cys111", "His272", "Asp286"],
        "catalytic_roles": ["nucleophile (Cys111)", "general base (His272)", "charge relay (Asp286)"],
        "reaction": "Deubiquitination and deISGylation; viral immune evasion",
        "smiles_substrate_hint": "N[C@@H](CCCNC(=N)N)C(=O)N[C@@H](Cc1ccccc1)C(=O)N[C@@H](C)C(=O)O",
    },
    {
        "name": "furin",
        "organism": "Homo sapiens",
        "pdb": "4RYD",
        "active_site_residues": ["Ser368", "His194", "Asp153"],
        "catalytic_roles": ["nucleophile (Ser368)", "general base (His194)", "charge relay (Asp153)"],
        "reaction": "Proprotein processing at R-X-K/R-R motif; viral spike activation",
        "smiles_substrate_hint": "N[C@@H](CCCN=C(N)N)C(=O)N[C@@H](CCCN=C(N)N)C(=O)O",
    },

    # ═══ EC 4: LYASES (gaps: aldolase, enolase, synthase, decarboxylase) ═══
    {
        "name": "aldolase",
        "organism": "Homo sapiens",
        "pdb": "1ALD",
        "active_site_residues": ["Lys229", "Glu187", "Lys146"],
        "catalytic_roles": ["Schiff base (Lys229)", "proton abstraction (Glu187)", "substrate binding (Lys146)"],
        "reaction": "Fructose-1,6-bisphosphate <-> DHAP + G3P",
        "smiles_substrate_hint": "O=P(O)(O)OC[C@H]1O[C@](O)(COP(=O)(O)O)[C@@H](O)[C@@H]1O",
    },
    {
        "name": "enolase",
        "organism": "Homo sapiens",
        "pdb": "3ENL",
        "active_site_residues": ["Lys345", "Lys396", "Glu211"],
        "catalytic_roles": ["proton abstraction (Lys345)", "Mg2+ ligand (Lys396)", "Mg2+ binding (Glu211)"],
        "reaction": "2-phosphoglycerate <-> phosphoenolpyruvate + H2O",
        "smiles_substrate_hint": "O=C(O)[C@H](O)COP(=O)(O)O",
    },
    {
        "name": "citrate_synthase",
        "organism": "Sus scrofa",
        "pdb": "1CTS",
        "active_site_residues": ["His274", "His320", "Asp375"],
        "catalytic_roles": ["general base (His274)", "general acid (His320)", "oxaloacetate binding (Asp375)"],
        "reaction": "Acetyl-CoA + oxaloacetate -> citrate + CoA",
        "smiles_substrate_hint": "O=C(O)CC(=O)C(=O)O",
    },
    {
        "name": "tryptophan_synthase",
        "organism": "Salmonella typhimurium",
        "pdb": "1A5S",
        "active_site_residues": ["Lys87", "Glu109", "Cys230"],
        "catalytic_roles": ["PLP anchor (Lys87)", "proton transfer (Glu109)", "alpha site (Cys230)"],
        "reaction": "Indole-3-glycerol phosphate + Ser -> Trp + G3P",
        "smiles_substrate_hint": "O=C(O)[C@@H](N)CO",
    },
    {
        "name": "ornithine_decarboxylase",
        "organism": "Homo sapiens",
        "pdb": "1D7K",
        "active_site_residues": ["Lys69", "Cys360", "His197"],
        "catalytic_roles": ["Schiff base (Lys69)", "active site (Cys360)", "PLP binding (His197)"],
        "reaction": "Ornithine -> putrescine + CO2; polyamine synthesis",
        "smiles_substrate_hint": "N[C@@H](CCCN)C(=O)O",
    },
    {
        "name": "fumarase",
        "organism": "Homo sapiens",
        "pdb": "3E04",
        "active_site_residues": ["His188", "Glu331", "Asn326"],
        "catalytic_roles": ["general acid/base (His188)", "general acid/base (Glu331)", "stabilization (Asn326)"],
        "reaction": "Fumarate + H2O <-> L-malate",
        "smiles_substrate_hint": "O=C(O)/C=C/C(=O)O",
    },
    {
        "name": "phenylalanine_ammonia_lyase",
        "organism": "Petroselinum crispum",
        "pdb": "1W27",
        "active_site_residues": ["Ser202", "Asn260", "Tyr110"],
        "catalytic_roles": ["MIO cofactor (Ser202)", "MIO cofactor (Asn260)", "base (Tyr110)"],
        "reaction": "Phe -> trans-cinnamate + NH3",
        "smiles_substrate_hint": "N[C@@H](Cc1ccccc1)C(=O)O",
    },

    # ═══ EC 5: ISOMERASES (gaps: mutases, racemases, topoisomerases) ═══
    {
        "name": "phosphoglucose_isomerase",
        "organism": "Homo sapiens",
        "pdb": "1IAT",
        "active_site_residues": ["Glu357", "His388", "Lys518"],
        "catalytic_roles": ["general base (Glu357)", "proton transfer (His388)", "phosphate binding (Lys518)"],
        "reaction": "Glucose-6-phosphate <-> fructose-6-phosphate",
        "smiles_substrate_hint": "O=P(O)(O)OC[C@H]1O[C@@H](O)[C@H](O)[C@@H](O)[C@@H]1O",
    },
    {
        "name": "triose_phosphate_isomerase",
        "organism": "Gallus gallus",
        "pdb": "1TIM",
        "active_site_residues": ["Glu165", "His95", "Lys13"],
        "catalytic_roles": ["general base (Glu165)", "general acid (His95)", "substrate binding (Lys13)"],
        "reaction": "DHAP <-> glyceraldehyde-3-phosphate",
        "smiles_substrate_hint": "O=C(CO)COP(=O)(O)O",
    },
    {
        "name": "phosphoglycerate_mutase",
        "organism": "Homo sapiens",
        "pdb": "1BQ3",
        "active_site_residues": ["His8", "His179", "Glu89"],
        "catalytic_roles": ["phosphohistidine (His8)", "phosphate transfer (His179)", "catalytic (Glu89)"],
        "reaction": "3-phosphoglycerate <-> 2-phosphoglycerate",
        "smiles_substrate_hint": "O=C(O)[C@H](O)COP(=O)(O)O",
    },
    {
        "name": "topoisomerase_II",
        "organism": "Homo sapiens",
        "pdb": "1ZXM",
        "active_site_residues": ["Tyr805", "Lys378", "Glu461"],
        "catalytic_roles": ["tyrosyl-DNA linkage (Tyr805)", "ATP binding (Lys378)", "Mg2+ binding (Glu461)"],
        "reaction": "ATP-dependent DNA double-strand passage; changes linking number by 2",
        "smiles_substrate_hint": "O=P(O)(O)OP(=O)(O)O",
    },
    {
        "name": "peptidyl_prolyl_isomerase",
        "organism": "Homo sapiens",
        "pdb": "1FKF",
        "active_site_residues": ["Phe36", "Trp59", "Tyr26"],
        "catalytic_roles": ["substrate binding (Phe36)", "transition state (Trp59)", "hydrogen bonding (Tyr26)"],
        "reaction": "cis/trans isomerization of X-Pro peptide bonds; protein folding",
        "smiles_substrate_hint": "CC(C)C[C@H](N)C(=O)N1CCC[C@H]1C(=O)O",
    },

    # ═══ EC 6: LIGASES (gaps: synthetases, carboxylases) ═══
    {
        "name": "dna_ligase",
        "organism": "Homo sapiens",
        "pdb": "1X9N",
        "active_site_residues": ["Lys568", "Asp570", "Arg573"],
        "catalytic_roles": ["AMP attachment (Lys568)", "Mg2+ coordination (Asp570)", "DNA binding (Arg573)"],
        "reaction": "ATP-dependent ligation of DNA nicks; sealing phosphodiester backbone",
        "smiles_substrate_hint": "O=P(O)(O)OP(=O)(O)OP(=O)(O)O",
    },
    {
        "name": "glutathione_synthetase",
        "organism": "Homo sapiens",
        "pdb": "2HGS",
        "active_site_residues": ["Arg125", "Lys305", "Glu144"],
        "catalytic_roles": ["gamma-Glu-Cys binding (Arg125)", "ATP binding (Lys305)", "Gly binding (Glu144)"],
        "reaction": "gamma-Glu-Cys + Gly + ATP -> GSH + ADP + Pi",
        "smiles_substrate_hint": "N[C@@H](CS)C(=O)N[C@@H](CCC(=O)O)C(=O)NCC(=O)O",
    },
    {
        "name": "ubiquitin_ligase_mdm2",
        "organism": "Homo sapiens",
        "pdb": "1YCR",
        "active_site_residues": ["Phe19", "Trp23", "Leu54"],
        "catalytic_roles": ["p53 binding (Phe19)", "p53 binding (Trp23)", "p53 binding (Leu54)"],
        "reaction": "p53 ubiquitination; targets p53 for proteasomal degradation",
        "smiles_substrate_hint": "N[C@@H](Cc1ccccc1)C(=O)N[C@@H](Cc1c[nH]c2ccccc12)C(=O)O",
    },
    {
        "name": "pyruvate_carboxylase",
        "organism": "Homo sapiens",
        "pdb": "3BG3",
        "active_site_residues": ["Lys704", "His707", "Arg571"],
        "catalytic_roles": ["biotin carrier (Lys704)", "carboxybiotin (His707)", "pyruvate binding (Arg571)"],
        "reaction": "Pyruvate + HCO3- + ATP -> oxaloacetate + ADP + Pi",
        "smiles_substrate_hint": "CC(=O)C(=O)O",
    },

    # ═══ EC 7: TRANSLOCASES (gaps: ATP synthase, transporters) ═══
    {
        "name": "atp_synthase_beta",
        "organism": "Bos taurus",
        "pdb": "1BMF",
        "active_site_residues": ["Lys162", "Glu188", "Arg189"],
        "catalytic_roles": ["nucleotide binding (Lys162)", "catalytic base (Glu188)", "phosphate binding (Arg189)"],
        "reaction": "ADP + Pi -> ATP; proton gradient-driven rotary catalysis",
        "smiles_substrate_hint": "O=P(O)(O)OP(=O)(O)OP(=O)(O)O",
    },
    {
        "name": "abc_transporter_p_gp",
        "organism": "Homo sapiens",
        "pdb": "6QEX",
        "active_site_residues": ["Glu556", "Ser557", "Lys1076"],
        "catalytic_roles": ["ATP hydrolysis (Glu556)", "catalytic (Ser557)", "ATP binding (Lys1076)"],
        "reaction": "ATP-dependent drug efflux; multidrug resistance pump",
        "smiles_substrate_hint": "COc1cc2c(cc1OC)N(C)C(=O)Cc1cc3c(c(OC)c1OC)N(C)CC3",
    },
    {
        "name": "serotonin_transporter",
        "organism": "Homo sapiens",
        "pdb": "6AWO",
        "active_site_residues": ["Asp98", "Tyr176", "Ile172"],
        "catalytic_roles": ["Na+ binding (Asp98)", "substrate binding (Tyr176)", "substrate binding (Ile172)"],
        "reaction": "Na+/Cl--coupled serotonin reuptake; SSRI target",
        "smiles_substrate_hint": "NCCc1c[nH]c2ccc(O)cc12",
    },
    {
        "name": "sodium_potassium_atpase",
        "organism": "Sus scrofa",
        "pdb": "3B8E",
        "active_site_residues": ["Asp369", "Lys719", "Asp710"],
        "catalytic_roles": ["phosphorylation (Asp369)", "ATP binding (Lys719)", "Mg2+ binding (Asp710)"],
        "reaction": "3 Na+(in) + 2 K+(out) + ATP -> 3 Na+(out) + 2 K+(in) + ADP + Pi",
        "smiles_substrate_hint": "O=P(O)(O)OP(=O)(O)OP(=O)(O)O",
    },

    # ═══ ADDITIONAL LANDMARKS: radical enzymes, flavoenzymes, moonlighting ═══
    {
        "name": "ribonucleotide_reductase",
        "organism": "Homo sapiens",
        "pdb": "2WGH",
        "active_site_residues": ["Cys439", "Cys225", "Cys462"],
        "catalytic_roles": ["thiyl radical (Cys439)", "redox shuttle (Cys225)", "redox shuttle (Cys462)"],
        "reaction": "NDP -> dNDP; radical mechanism; DNA synthesis precursor",
        "smiles_substrate_hint": "O=P(O)(O)OP(=O)(O)OC1OC(CO)C(O)C1O",
    },
    {
        "name": "ketosteroid_isomerase",
        "organism": "Pseudomonas putida",
        "pdb": "1OPY",
        "active_site_residues": ["Asp38", "Tyr14", "Tyr55"],
        "catalytic_roles": ["general base (Asp38)", "proton relay (Tyr14)", "dienolate stabilization (Tyr55)"],
        "reaction": "Delta5-3-ketosteroid <-> Delta4-3-ketosteroid; fastest known enzyme",
        "smiles_substrate_hint": "CC12CCC3C(CCC4=CC(=O)CCC34C)C1CCC2=O",
    },
    {
        "name": "nitrogenase_fe_mo",
        "organism": "Azotobacter vinelandii",
        "pdb": "1M1N",
        "active_site_residues": ["Cys62", "Cys88", "Cys154"],
        "catalytic_roles": ["Fe-S cluster (Cys62)", "FeMo-co ligand (Cys88)", "FeMo-co ligand (Cys154)"],
        "reaction": "N2 + 8H+ + 8e- + 16ATP -> 2NH3 + H2 + 16ADP + 16Pi",
        "smiles_substrate_hint": "N#N",
    },
    {
        "name": "photosystem_II",
        "organism": "Thermosynechococcus elongatus",
        "pdb": "1S5L",
        "active_site_residues": ["Tyr161", "His190", "Glu189"],
        "catalytic_roles": ["YZ tyrosine (Tyr161)", "Mn4Ca ligand (His190)", "Mn4Ca ligand (Glu189)"],
        "reaction": "2 H2O -> O2 + 4H+ + 4e-; water-splitting oxygen evolution",
        "smiles_substrate_hint": "O",
    },
    {
        "name": "reverse_transcriptase",
        "organism": "HIV-1",
        "pdb": "1RTD",
        "active_site_residues": ["Asp185", "Asp186", "Asp110"],
        "catalytic_roles": ["polymerase active site (Asp185)", "Mg2+ binding (Asp186)", "Mg2+ binding (Asp110)"],
        "reaction": "RNA-dependent DNA polymerization; retroviral replication",
        "smiles_substrate_hint": "O=P(O)(O)OP(=O)(O)OP(=O)(O)O",
    },
    {
        "name": "telomerase",
        "organism": "Homo sapiens",
        "pdb": "7BG9",
        "active_site_residues": ["Asp254", "Asp256", "Asp343"],
        "catalytic_roles": ["RT active site (Asp254)", "Mg2+ binding (Asp256)", "Mg2+ binding (Asp343)"],
        "reaction": "Telomere repeat addition (TTAGGG); chromosome end maintenance",
        "smiles_substrate_hint": "O=P(O)(O)OP(=O)(O)OP(=O)(O)O",
    },
]

# ── Merge with existing lookup ──
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from expanded_catalyzing_proteins import EXPANDED_PROTEIN_LOOKUP as PROTEIN_LOOKUP

def merge_missing():
    """Add missing enzymes to PROTEIN_LOOKUP, avoiding duplicates by pdb code."""
    existing_pdbs = {v.get('pdb','') for v in PROTEIN_LOOKUP.values()}
    added = 0
    skipped = 0
    for entry in MISSING_ENZYMES:
        if entry['pdb'] in existing_pdbs:
            skipped += 1
            continue
        PROTEIN_LOOKUP[entry['name']] = entry
        existing_pdbs.add(entry['pdb'])
        added += 1
    print(f"Merge: {added} added, {skipped} already present, total={len(PROTEIN_LOOKUP)}")
    return PROTEIN_LOOKUP

def list_all_pdb_codes():
    """Return sorted unique PDB codes from merged lookup."""
    merge_missing()
    return sorted({v.get('pdb','') for v in PROTEIN_LOOKUP.values() if v.get('pdb','')})

def run_ligand_pipeline(pdb_codes, outfile):
    """Run the ligand pipeline on every PDB code and collect results."""
    import subprocess, time, json
    results = []
    total = len(pdb_codes)
    for i, pdb in enumerate(pdb_codes):
        t0 = time.time()
        try:
            proc = subprocess.run(
                ['python3', '-m', 'rebis.p4ra', 'ligands', pdb],
                capture_output=True, text=True, timeout=120,
                cwd='/home/mrnob0dy666/imsgct/red-hot_rebis',
                env={**os.environ, 'PYTHONPATH': '/home/mrnob0dy666/imsgct/red-hot_rebis'}
            )
            stdout = proc.stdout[-2000:] if len(proc.stdout) > 2000 else proc.stdout
            n_smiles = stdout.count('SMILES:') or stdout.count('SMILES')
            elapsed = time.time() - t0
            results.append({
                'pdb': pdb, 'n_smiles': n_smiles,
                'ok': proc.returncode == 0, 'time_s': round(elapsed,1),
                'err': proc.stderr[-200:] if proc.stderr else ''
            })
            print(f"[{i+1}/{total}] {pdb}: {n_smiles} SMILES in {elapsed:.1f}s {'OK' if proc.returncode==0 else 'ERR'}")
        except subprocess.TimeoutExpired:
            results.append({'pdb': pdb, 'n_smiles': 0, 'ok': False, 'time_s': 120, 'err': 'timeout'})
            print(f"[{i+1}/{total}] {pdb}: TIMEOUT")
        except Exception as e:
            results.append({'pdb': pdb, 'n_smiles': 0, 'ok': False, 'time_s': 0, 'err': str(e)[:200]})
            print(f"[{i+1}/{total}] {pdb}: ERROR {e}")
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} results to {outfile}")
    return results

if __name__ == '__main__':
    if '--list' in sys.argv:
        codes = list_all_pdb_codes()
        print('\n'.join(codes))
        print(f"\n{len(codes)} total unique PDB codes")
    elif '--run' in sys.argv:
        codes = list_all_pdb_codes()
        outfile = sys.argv[sys.argv.index('--run')+1] if '--run' in sys.argv else '/tmp/ligand_results.json'
        run_ligand_pipeline(codes, outfile)
    else:
        merge_missing()
        codes = list_all_pdb_codes()
        print(f"Merged: {len(codes)} unique PDB codes ready")
        print("Use --list to see codes, --run <out.json> to run pipeline")
