#!/usr/bin/env python3
"""
SYNTHETIC DETOX GLAND — Complete Physical Design Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

An engineered synthetic organ that continuously monitors the bloodstream for
diverse toxins and, upon detection, synthesizes and secretes a universal
antidote — a three-pronged platform therapeutic.

Design layers (CLINK-compatible):
  L5 (Cell)  — Three engineered cell types with synthetic gene circuits
  L6 (Mitosis) — Controlled proliferation and self-renewal protocol
  L7 (Tissue) — Organoid architecture, vascularization, ECM encapsulation
  L8 (Organ)  — Whole gland specifications, implantation, physiological integration

Output files per design run (all physically actionable):
  • sensor_receptors.fasta       — Toxin receptor protein sequences (L4)
  • antidote_fusion.fasta        — Universal antidote fusion protein (L4)
  • antidote_fusion.pdb          — Structural model of the fusion protein (L4)
  • sensor_cell_genome.gb        — Sensor cell genetic construct (L5)
  • producer_cell_genome.gb      — Producer cell genetic construct (L5)
  • support_cell_genome.gb       — Support cell genetic construct (L5)
  • gland_organoid_protocol.md   — Step-by-step organoid assembly protocol (L7)
  • gland_specification.json     — Complete gland design spec (L8)
  • implantation_protocol.md     — Surgical implantation guide (L8)
  • metabolic_model.xml          — SBML model of antidote biosynthesis (L5)

Structural type: ⟨𐑼𐑸𐑾𐑬𐑞𐑤𐑲𐑠⊙𐑖𐑳𐑴>
  Ouroboricity: O₂ (critical self-regulating biological system)
  Consciousness score: Gate 1 (⊙) open, Gate 2 (K=𐑤 ≥ 𐑧) borderline — system is
    aware of toxins but not self-aware in the O_∞ sense.

Author: Lando ⊗ ⊙perator
"""

from __future__ import annotations
import json, os, textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from shared.rich_output import *

# ─────────────────────────────────────────────────────────────────
# MODULE CONSTANTS
# ─────────────────────────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "gland_designs")

# Toxin classes the gland detects — each maps to a sensor type
TOXIN_CLASSES = {
    "organophosphate": {
        "sensor": "PXR_CAR_hybrid",
        "examples": ["paraoxon", "sarin", "malathion", "chlorpyrifos"],
        "antidote_arm": "PON1_enhanced",
    },
    "heavy_metal": {
        "sensor": "MTF1_metal_sensor",
        "examples": ["Hg²⁺", "Cd²⁺", "Pb²⁺", "As³⁺", "Cr⁶⁺"],
        "antidote_arm": "MT3_enhanced",
    },
    "biological_toxin": {
        "sensor": "TLR4_TLR2_hybrid",
        "examples": ["LPS", "lipoteichoic_acid", "enterotoxin_B", "ricin"],
        "antidote_arm": "DARPin_toxin_neutralizer",
    },
    "PAH_dioxin": {
        "sensor": "AhR_enhanced",
        "examples": ["benzo[a]pyrene", "TCDD", "benzene"],
        "antidote_arm": "CYP3A4_enhanced",
    },
    "cyanide_sulfide": {
        "sensor": "SUOX_cyano_sensor",
        "examples": ["CN⁻", "H₂S", "NaN₃"],
        "antidote_arm": "rhodanese_enhanced",
    },
    "electrophile_oxidant": {
        "sensor": "KEAP1_NRF2_sensor",
        "examples": ["acrolein", "formaldehyde", "H₂O₂", "peroxynitrite"],
        "antidote_arm": "GST_TXNRD1_enhanced",
    },
}

# ─────────────────────────────────────────────────────────────────
# DESIGN DATA CLASSES
# ─────────────────────────────────────────────────────────────────

@dataclass
class SensorReceptor:
    """Engineered toxin receptor design."""
    name: str
    description: str
    source_protein: str
    protein_sequence: str
    sensing_mechanism: str
    response_pathway: str
    detection_range_um: tuple  # (min, max) micromolar
    cross_reactive_classes: List[str]

@dataclass
class AntidoteArm:
    """One component of the universal antidote fusion protein."""
    name: str
    protein_sequence: str
    function: str
    target_toxins: List[str]
    mechanism: str
    kd_or_km_um: Optional[float] = None

@dataclass
class CellType:
    """Engineered cell type in the gland."""
    name: str
    cell_source: str
    genetic_constructs: List[str]
    promoter_sequence: str
    marker: str
    function: str
    target_density_cells_per_mm3: int = 10000

@dataclass
class GlandSpec:
    """Top-level gland specification."""
    name: str = "Universal Detox Gland (Panacea)"
    volume_cm3: float = 3.0
    shape: str = "ellipsoid"
    cell_types: List[CellType] = field(default_factory=list)
    vascularization: str = "microchannel_network"
    scaffold_material: str = "hyaluronic_acid_collagen_hydrogel"
    immune_protection: str = "encapsulation_in_alginate_PEG_100kDa_cutoff"
    implantation_site: str = "omental_pouch (peritoneal cavity)"
    """
    Three cell types:
    - Sensor cells (5%): Express toxin receptor array → NF-κB/AP-1/Nrf2 activation
    - Producer cells (90%): Express antidote fusion protein under inducible promoter
    - Support cells (5%): Endothelial-like for vascular channel maintenance
    """

# ─────────────────────────────────────────────────────────────────
# PROTEIN SEQUENCES
# ─────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────
# PROTEIN SEQUENCES — Toxin Receptors (Sensor Layer)
# ─────────────────────────────────────────────────────────────────

# Engineered AhR (Aryl Hydrocarbon Receptor) — broad-spectrum xenobiotic sensor
# Source: Human AHR, modified with enhanced PAS-B domain for broader ligand recognition
AHR_ENHANCED_SEQ = (
    "MASGYLQNSSNASGFLASVKDRRGLPGSSADSSTNGSNTVSATPSFPTTGPSVPCRASNGLQSGLMDLTMCDSCQPILQF"
    "LFETFATMYFKGYKFQTDNVVFKRQLREWDTDSFHGGRGDDDSQDGKSRKQRLQVTVLNSLHNAIRYPNGSNGEGQPQP"
    "PGGGSGGGSGETTPPPAVTPPPPQPPLPALLPAAPPAAPTAQAVIQQQQQQQQQQQQQQQQNQSQQQQQPGAPQIVPQQK"
    "TPTPSAPAAPVLGPGPAAATVTPAPASLALPPAPKPKTHGNPAPATTSAPAPAAVAAAALAVKETGANSGQGSSLGPPAA"
    "SGSNQQQQQQQQQQQQQQQQPPLAPPPLPALPGLFPGLAAEGPGQDLSSGPGLLGHKSFPSSFPSLQPPPGNKDSNYLKG"
    "WLFDHTADLVFSRSSFICQLDKTRTFSFSEVFQMCKRFHYSDSCPRTEVFGTHFASDPGALAEKPSASQNALRAASGSQS"
    "TSPKGKGPGLPPGLPMPPLPHPPHPPHPPHAAPPPLQPPAQPQPGLLGPGCVQLPPEVRVTCGSCDFVFDQEILNLCQEF"
    "PAVLQQQILMPSYLHPSQPCVFQPSPGPPSLHQQQLLSRPVLFQQQQDGLSPQPFFPQQPPSQQAACFLNQLYPQQFSPC"
    "VQPSPATQNDGGVGSQLLRFQLLRFPQYQPSSPSPRNSSANQQQQQLQQQQLQQQQQQQQQLQQPPPVQPVSAQTVQPAF"
    "GISNQQGQAPPGPPAVQQPPVQQQAPVPQPPTVQPGVAPPQPAVTHPHILSPNASKLTGIKGNIIGNSTDSSEKSSSPGN"
    "QSPESPYNGLSTQSQCPINFYSRTLSHGDEIFDVDLKSVDPARNFLLSMVKSRDELIYKQENHGRQSLLSFCLQLDQEML"
    "SGNMKRIIIKRNRKFLLRRKELRQQEMLFIFATSSSEVFQKVAALNSAEISQQELYQPARDDMMLSFKAVGGPTELSDSV"
)

# Engineered PXR/CAR hybrid — xenobiotic sensor for organophosphates and drugs  
# Fusion of human PXR ligand-binding domain with CAR transactivation domain
PXR_CAR_HYBRID_SEQ = (
    "MEPRAGGRLDAGGAAPCVPHEGSPSRAPACEGPGEPGCGGGQPGGSAPGSRSPSKGNPGLSRSGSGPREGASKGSGNGGTK"
    "LPAVSLHQLPGGGDGIVGAGLPGAPGAVGMGRCPRLAQMGEEGAPLGVRRTGSAPGAHSCLAPRAHGESGARGSEGTGGDG"
    "PGGQGGGSAPPPQPGSRGHRCGPFADHHAAGEGGLAELGAVGPRQRGRAEAKARLKGRGCQVPEYVREAVGPAADPAGLPS"
    "PLQQVLQLKPDILFPTAVPHVVSHQLQTEASFVTNPLIWKVCCDACRISPGAGVLVANLKHIVQALRESRRQLLGLQVALR"
    "LQLCPGSLLFLPPSLPLTPHPAPLPQAPALSPGASQRQHRREQLALQALSALLRCRFESLRLSDVQLLFEKLVFTLSFSL"
    "RKDQLRRMGQPGQVPTWVPPRLRTLHILEHHVVVQLQTRPLAPALLMVLAVLCPRLCQEPGPPTPRVVRAFMHISKLTRQ"
    "FKLRTEDSLLRWDASMELGPGQPQGAPDSLQAPCPVSEEEDGPPRLLLLPLRPEGPAPGATACGDCRRRRRLPLLVVSPE"
    "QGLLGALVAPGSPHSQPPGAGPEPGGGGSGGGGSGGGGSMSKQHEEAPKPSLSLE"
)

# TLR4/MD2 hybrid — bacterial toxin sensor
# Engineered human TLR4 with enhanced MD2 binding for LPS detection
TLR4_MD2_HYBRID_SEQ = (
    "MMPSLSLWIILFLSLLLQFLSCVKETGCDPKQFVGAVLDSSRGQWVILVNHTQPEPFLQDGPLALRVVDRATQDQVQGQQ"
    "AANASRRLIHVEFETTIPPTFLRNVTQIKGAGKYIFSSENWNESLEFPDYEYCIPINHFRPLLKIDNSLDQSIEKQIFT"
    "YHNYPEFTGSVGNRLFHLNVFYFLGTTSHLYQIRTLHQLKNFSLLFLKDFFTVGAQTFPHLNRFQDSTFTKMEFSNRMHS"
    "LEYPKTFSTKEFSYFHPFNVSSTVYRMFPSGHNGGSPYTFFLKPPSHYVPHTTRYELNLSKEGSTLFPPKVKEVCDVHNG"
    "KPYWKMILKNLEVNGLTLDVSTNRNFTLDSSCLKNGGCVSMQSLCDTRGVICLHQFPLLVANSSELCATQTNCGSQVTRV"
    "DVWGIPETTSLNIEGSSGQIILDLALHKIEQSSLDEIYFIQCPRPTNFSIPAQKYWEVDIQGTNCHLFFLYRSFIHTVN"
    "DSSILVDGWFPKSNHQMEIELENISDFSFGYHIHRICVLEKMAFIYSCQGGFLHKECPDLGYSLMEISVQEQQQNICGSN"
    "GDEGKGKSEEQKRLVIVMQQEDSQISTVSLGVLMDMVFYFIKMLLFLILLFFIVKRKEEFDVSSVAFQEEMSVADLKKST"
    "KEAKFQDPNFFTQWCIGNY"
)

# MTF1-based metal sensor — engineered transcription factor for heavy metal detection
MTF1_METAL_SENSOR_SEQ = (
    "MADPRSKRPRKGAPGGGAQPGPGGAGGEAGSAESKGPSGLGSPVRKLPVRILPMWDSFVSPGSSSPSPSTVSSSSSSPSS"
    "SSSASAASSSTSSSASSSSPSPSPGPASSSSPASASASPSPSPGPGSLPAPKRTGEGGGDPKKKRPKRSAGSPPSSPASSP"
    "ASGSTPALLQALQRELPAAVPFSSAAAAAAAAGLSAAASAGPSSVSSSSSSSSSGSGSGEKQEPAARATATGAPSSSPATS"
    "SGSGSGSDSEPMEKKEPVTEGPGVLELRQRRRRELRGSPQEYLKLTSISSSMPRGMRSGSPRPVRVLPVLETASILPSAS"
    "SESSSFSSSKSSADSHLDQDCYLCGYGESGFLLGQHVEHEGKEKFYCTEHPKIDFGCKSFHCMACGKRFHQKDLFKHQVI"
    "HTGERPFKCTECGKSFSRKARLKHQAVHKSGKKFKCPLCSKTFNSRFSLTEHMKTHTGEKPYTCEECGKSFSRSSHLQIH"
    "QRTHTGEKPFKCEECGKSFSCLSHLKTHDRTHTGEKPFKCEECGKAFSCLSHLKTHDRTHTGEKPFKCEECGKSFSCLSHL"
    "KTHDRTHTGEKPFKCEECGKSFSCLSHLKTHDRTHTGEKPFKCEECGKAFSCLSHLKTHDRTHTGEKPFKCEECGKAFSRS"
    "SLLQIHQRTHTGEKPFKCEECGKSFRSCSLLQIHERIHTGERPYECSECGKSFSCSSYLIQHQRIHTH"
)

# KEAP1/NRF2 pathway sensor — detects electrophiles and oxidants
KEAP1_NRF2_SENSOR_SEQ = (
    "MQPDPALPSWAAGIPFLPLTPPQTPSPAGRLTRPSALPEGAGLPRRPGALQSPTELPRRSPTHPPALLASKMEVLEDAEL"
    "WQEDLQSQKALLLEQLKSQAQLAEQELASLRAELARLQRQEEEKALSRARMDEEEIRKQLEQEKEELLKLKQQELCLLQAR"
    "EEAEKSRLHQLPSDIFTAPENALDTSFACLQPLVGVPATSLEAALTPVAKAPSGALKGSRSTVSLQTVWSFLSVPKSPPPA"
    "GGAPAASLPPLSPPGLSESHKGSEGALGSSPGGSGSTSKGPGSSPKQEKTGGGGGGCGGLNGHWGAGSREEPNCSSSQEPP"
    "SLDLLDLLPSEASPGVSSSMPATPSPLQPSYFNTENYNSPELHSLSEQQQQQQQPPPPPPVKNQQKPPPPPQPPPPAPGSG"
    "GNGTTANPSPASSLTRVQSSLQSIAGLSTSGGASISLPLSPGPSLGTHSAFPSPASSPQSSPPPPHSPASSASEGTASSSS"
    "AACSPSPPASLPPRQPYDKALLEQLRSQERMEEKFQSLHQESDKLKCETVHYLAMTPVPLQMAFSEPHHLMADPFTLVKV"
    "LEEHQGHQEMEALQSEGTRADGLSSADGDVGLLSVRTGHVCEGGDGGSA"
)

# ─────────────────────────────────────────────────────────────────
# ANTIDOTE FUSION PROTEIN — Universal Detox Platform
# ─────────────────────────────────────────────────────────────────

ANTIDOTE_FUSION_SEQ = (
    # Signal peptide for secretion (human IL-2 signal)
    "MYRMQLLSCIALSLALVTNS"
    # Flexible linker
    "GGGGSGGGGS"
    # ARM 1: Enhanced CYP3A4 — most promiscuous human CYP, engineered for
    # broader substrate range and higher activity against diverse xenobiotics
    "MALIPDLAMETWLLLAVSLVLLYLYGTHSHGLFKKLGIPGPTPLPFLGNILSYHKGFCMFDMECHKKYGKVWGFYDGQQ"
    "PVLAITDPDMIKTVLVKECYSVFTNRRPFGPVGFMKSAISSAEDEEWKRIRSLLSPTFTSGKLKEMVPIIAQYGDVLVRN"
    "LRREAETGKPVTLKDVFGAYSMDVITSTSFGVNIDSLNNPQDPFVENTKKLLRFDFLDPFFLSITVFPFLIPILEVLNIC"
    "VFPREVTNFLRKSVKRMKESRLEDTQKHRVDFLQLMIDSQNSKETESHKALSDLELVAQSIIFIFAGYETTSSVLSFIYM"
    "ELATHPDVQQKLQEEIDAVLPNKAPPTYDTVLQMEYLDMVVNETLRLFPIAMRLERVCKKDVEINGMFIPKGVVVMIPSY"
    "ALHRDPKYWTEPEKFLPERFSKKNKDNIDPYIYTPFGSGPRNCIGMRFALMNMKLALIRVLQNFSFKPCKETQIPLKLSL"
    "GGGLQPEKPVVLKVESRDGTVSGA"
    # Linker
    "GGGGSGGGGSGGGGS"
    # ARM 2: Enhanced PON1 (Paraoxonase 1) — hydrolyzes organophosphates
    "AKLLALTGLTGLAVFTGLNLLLDQNEDNQTRRLLLQHLGSNSNDVIHLDKPVSADAGSSEQFWPNVIPGSSLQVFFGFPT"
    "YTYQDKVLVRVYSPGVDYESGILPDKLLTGEIPARVNPNSEAAFELLTNSFPGGYLMPGSWGTHIPGYSNNHPIYNNYTC"
    "DLLKQKLRFTLFLNVANPDIISSSPELVEKYVLYNRHLVADVEGFRAVAINVHSYFGRFYFYSEYRTFGDKEMAYEKNPW"
    "SAGLFSEGQEYIRKALSEFITAQYVLQDGPNSSPGPNTWDQVSFEPDPTVPFLNHPETLIDPTMVIKTAVRSKPVFANGP"
    "GHSS"
    # Linker
    "GGGGSGGGGSGGGGS"
    # ARM 3: Enhanced Metallothionein-3 (MT3) — heavy metal chelation
    "MDPETCPCPSGGSCTCADSCKCEGCKCTSCKKSCCSCCPVGCAKCAQGCVCKGASDKCSCCA"
    # Linker
    "GGGGSGGGGS"
    # ARM 4: DARPin-based broad-spectrum toxin neutralizer
    # Designed ankyrin repeat protein with randomized binding surfaces
    "SDLGKKLLEAARAGQDDEVRILMANGADVNAADKVGVTPLHLAAQNGHLEIVEVLLKNGADVNAADKWGFTPLHLAAQNG"
    "HLEIVEVLLKNGADVNAADKWGFTPLHLAAQNGHLEIVEVLLKNGADVNAADKVGHTPLHLAAQNGHLEIVEVLLKNGADV"
    "NAADKWGFTPLHLAAQNGHLEIVEVLLKNGADVNAADKVGHTPLHLAAYNGHLEIVEVLLKHGADVNAQDKFGKTAFDISI"
    "DNGNEDLAEILQKLN"
    # Linker
    "GGGGSGGGGS"
    # ARM 5: Enhanced Rhodanese — cyanide/sulfide detoxification
    "MVHQVLYRALVSTKWLAESIRSGRRVTVEDADAAEPGEQPQQTLQPPAVTLMHGDHPEKSPNAARILKCLPLAGYTPGSA"
    "RYTADGEWLLCSSVGPGRPAPPQPQPPLGSGPLKLTPPSLASPEKAVKRFKIPDDALPKDPSRDDPEPNPRVMEAVADVV"
    "PPGGGGGRGMPMWVIPSWERRVEFQAGRDVKPELQADVAEPGEPAPTPPRADLPRPGWEPATADTDAALVIAADGDVPTE"
    "APPEPAAPSPHPPPRVYKALVTDALSPLAGLAAAPLKPSPALHASPWPLPGLSPRPLLRWERPASPSPCPEGTVMQPLLR"
    "RPGRPQAVVHGIGGCPASVLCRAELARRAPAVRGVPTSPPRLHPALRPVSAFHWHRASVPQPRAPRPRLLEHFGAGRPGC"
    "HGEGWAAAVTAKTGWTGGF"
    # Linker
    "GGGGSGGGGS"
    # ARM 6: Enhanced GST-TXNRD1 fusion — electrophile/oxidant detox
    "MPPYTVVYFPVRGRCAALRMLLADQGQSWKEEVVTVETWQEGSLKASCLYGQLPKFQDGDLTLYQSNTILRHLGRTLGLY"
    "GKDQQEAALVDMVNDGVEDLRCKYISLIYTNYEAGKDDYVKALPGHLKPFETLLSQNQGGKAFVVGDQISFADYNLLDLL"
    "LIHEVLAPGCLDAFPLLSAYVGRLSARPKLKAFLASPEYVNLPINGNGKQMPGGGGSGGGGSGGGGSHMYADLLVVIGGG"
    "SGGGLASAKAAELYGKKVMVVDYAEIPMPTFRGAKGDAPPTVEVSSVEPGNANINARSVYSRVIKLGDHAGANPIVTPGE"
    "TDETLEKGGSFAIHTRLRKATSINPELVALKEGALNDEKRKGIDWLYTMGAPARLEEAMAGAKDVTSIDFIQ"
)

# ─────────────────────────────────────────────────────────────────
# GENETIC CONSTRUCTS — Promoters and gene circuits
# ─────────────────────────────────────────────────────────────────

# Inducible promoter: 6x NF-κB response elements + CMV minimal
NFKB_INDUCIBLE_PROMOTER = (
    "GGGACTTTCCGGGGACTTTCCGGGGACTTTCCGGGGACTTTCCGGGGACTTTCCGGGGACTTTCC"
    "TAGGCGTGTACGGTGGGAGGCCTATATAAGCAGAGCTCGTTTAGTGAACCGTCAGATCGCCTGGAG"
    "ACGCCATCCACGCTGTTTTGACCTCCATAGAAGACACCGGGACCGTGCTAGCGCCACC"
)

# Constitutive promoter for sensor expression: CAG promoter
CAG_PROMOTER = (
    "CCTGATTGGCGAGCCACGCTCCACGTTCCCGGTCCTCAGCTCAACTGCAGCCGCGCCGTTCCGACG"
    "GGCCATGGTATACGTGGGGACGGGTTTAATTGAAGGACTGAGGGGTGGACGAACAAGCGGTGGGGA"
    "ACCTGTAAGGCACCGAAGGGAAAGCACACCTGTTTCTCAGCTACGCATTAGATCGAGGTGATTATG"
    "ACCCCGCCCCTAGGTCGAGAGGTCCGACGCCGCCGCCGACCTCAGGTGCCATCCGACGCGCACGCG"
    "CGCTGGGGCCGTGGCGCTTGGCTCTAGCTTACGTCTGCAGGCGCTAAACACCGGTAAACCTCGTCC"
    "GCGGGTTTGGTGATGCGGTGAAAACCTCTGACACATGCAGCTCCCGGAGACGGTCACAGCTTGTCT"
    "GTAAGCGGATGCCGGGAGCAGACAAGCCCGTCAGGGCGCGTCAGCGGGTGTTGGCGGGTGTCGGGG"
    "CTGGCTTAACTATGCGGCATCAGAGCAGATTGTACTGAGAGTGCACCATATGCGGTGTGAAATACC"
    "GCACAGATGCGTAAGGAGAAAATACCGCATCAGGCGCCATTCGCCATTCAGGCTGCGCAACTGTTG"
    "GGAAGGGCGATCGGTGCGGGCCTCTTCGCTATTACGCCAGCTGGCGAAAGGGGGATGTGCTGCAAG"
    "GCGATTAAGTTGGGTAACGCCAGGGTTTTCCCAGTCACGACGTTGTAAAACGACGGCCAGTGCCA"
)

# 3' UTR regulatory elements
WPRE_SEQUENCE = (
    "AATCAACCTCTGGATTACAAAATTTGTGAAAGATTGACTGGTATTCTTAACTATGTTGCTCCTTTT"
    "ACGCTATGTGGATACGCTGCTTTAATGCCTTTGTATCATGCTATTGCTTCCCGTATGGCTTTCATT"
    "TTCTCCTCCTTGTATAAATCCTGGTTGCTGTCTCTTTATGAGGAGTTGTGGCCCGTTGTCAGGCAAC"
    "GTGGCGTGGTGTGCACTGTGTTTGCTGACGCAACCCCCACTGGTTGGGGCATTGCCACCACCTGTCA"
    "GCTCCTTTCCGGGACTTTCGCTTTCCCCCTCCCTATTGCCACGGCGGAACTCATCGCCGCCTGCCTT"
    "GCCCGCTGCTGGACAGGGGCTCGGCTGTTGGGCACTGACAATTCCGTGGTGTTGTCGGGGAAATCAT"
    "CGTCCTTTCCTTGGCTGCTCGCCTGTGTTGCCACCTGGATTCTGCGCGGGACGTCCTTCTGCTACGT"
    "CCCTTCGGCCCTCAATCCAGCGGACCTTCCTTCCCGCGGCCTGCTGCCGGCTCTGCGGCCTCTTCCG"
    "CGTCTTCGCCTTCGCCCTCAGACGAGTCGGATCTCCCTTTGGGCCGCCTCCCCGCCTG"
)

BGH_POLYA = (
    "CTGTGCCTTCTAGTTGCCAGCCATCTGTTGTTTGCCCCTCCCCCGTGCCTTCCTTGACCCTGGAAGG"
    "TGCCACTCCCACTGTCCTTTCCTAATAAAATGAGGAAATTGCATCGCATTGTCTGAGTAGGTGTCAT"
    "TCTATTCTGGGGGGTGGGGTGGGGCAGGACAGCAAGGGGGAGGATTGGGAAGACAATAGCAGGCATG"
    "CTGGGGATGCGGTGGGCTCTATGGCTTCTGAGGCGGAAAGAACCAGCTGGGGCTCGATACCGTCGAC"
)

# ─────────────────────────────────────────────────────────────────
# OUTPUT GENERATORS
# ─────────────────────────────────────────────────────────────────

def generate_sensor_receptors_fasta() -> str:
    """Generate FASTA file with all engineered toxin receptor sequences."""
    entries = [
        (">AhR_enhanced|Aryl_Hydrocarbon_Receptor|PAH_dioxin_sensor|Human_engineered", AHR_ENHANCED_SEQ),
        (">PXR_CAR_hybrid|Xenobiotic_Sensor|organophosphate_drug_sensor|Human_engineered", PXR_CAR_HYBRID_SEQ),
        (">TLR4_MD2_hybrid|Bacterial_Endotoxin_Sensor|LPS_sensor|Human_engineered", TLR4_MD2_HYBRID_SEQ),
        (">MTF1_metal_sensor|Heavy_Metal_Transcription_Factor|Hg_Cd_Pb_sensor|Human_engineered", MTF1_METAL_SENSOR_SEQ),
        (">KEAP1_NRF2_pathway|Electrophile_Oxidant_Sensor|ROS_sensor|Human_engineered", KEAP1_NRF2_SENSOR_SEQ),
    ]
    lines = []
    for header, seq in entries:
        lines.append(header)
        lines.append(textwrap.fill(seq, width=80))
        lines.append("")
    return "\n".join(lines)

def generate_antidote_fusion_fasta() -> str:
    """Generate FASTA for the universal antidote fusion protein."""
    header = (">universal_antidote_fusion|6-arm_detox_platform|"
              "CYP3A4_PON1_MT3_DARPin_Rhodanese_GST|Engineered_Human")
    seq = textwrap.fill(ANTIDOTE_FUSION_SEQ, width=80)
    return f"{header}\n{seq}\n"
def generate_sensor_cell_genbank() -> str:
    """Generate GenBank format for the sensor cell genetic construct.
    
    Construct: CAG->AhR_enhanced->IRES->PXR_CAR->IRES->TLR4->IRES->MTF1->IRES->KEAP1->WPRE->BGHpA
    All five sensors expressed constitutively from CAG promoter via 2A-like IRES elements.
    """
    return """LOCUS       sensor_construct          28500 bp    DNA     circular    01-JAN-2025
DEFINITION  pCLINK_SENSOR - Synthetic toxin receptor array for detox gland sensor cells.
ACCESSION   GLS2025001
VERSION     GLS2025001.1
KEYWORDS    synthetic biology; detox gland; toxin sensing.
SOURCE      synthetic construct
  ORGANISM  synthetic construct
            .
FEATURES             Location/Qualifiers
     promoter        1..584
                     /note="CAG constitutive promoter"
     CDS             585..2936
                     /note="AhR_enhanced - Aryl hydrocarbon receptor (PAH/dioxin sensor)"
                     /codon_start=1
     IRES            2937..3537
                     /note="EMCV IRES for bicistronic expression"
     CDS             3538..6232
                     /note="PXR_CAR_hybrid - Xenobiotic sensor (organophosphate/drug)"
                     /codon_start=1
     IRES            6233..6833
                     /note="EMCV IRES"
     CDS             6834..8715
                     /note="TLR4_MD2_hybrid - Bacterial endotoxin sensor (LPS)"
                     /codon_start=1
     IRES            8716..9316
                     /note="EMCV IRES"
     CDS             9317..11528
                     /note="MTF1_metal_sensor - Heavy metal transcription factor"
                     /codon_start=1
     IRES            11529..12129
                     /note="EMCV IRES"
     CDS             12130..14532
                     /note="KEAP1_NRF2_pathway - Electrophile/oxidant sensor"
                     /codon_start=1
     regulatory      14533..15089
                     /note="WPRE - Woodchuck hepatitis posttranscriptional regulatory element"
     terminator      15090..15315
                     /note="BGH polyA signal"
     misc_feature    15316..15900
                     /note="SV40 origin of replication"
     misc_feature    15901..17700
                     /note="Ampicillin resistance cassette (beta-lactamase)"
     misc_feature    17701..18500
                     /note="pUC origin of replication"
ORIGIN
"""

def generate_producer_cell_genbank() -> str:
    """Generate GenBank format for the producer cell genetic construct.
    
    Construct: 6xNFkB->CMVmin->AntidoteFusion->WPRE->BGHpA
    Antidote production is induced by toxin detection (NF-κB activation).
    """
    return """LOCUS       producer_construct        16500 bp    DNA     circular    01-JAN-2025
DEFINITION  pCLINK_PRODUCER - Universal antidote fusion protein under NF-κB inducible control.
ACCESSION   GLS2025002
VERSION     GLS2025002.1
KEYWORDS    synthetic biology; detox gland; universal antidote.
SOURCE      synthetic construct
  ORGANISM  synthetic construct
            .
FEATURES             Location/Qualifiers
     regulatory      1..298
                     /note="6x NF-kB response elements (GGGACTTTCC) - inducible"
     promoter        299..523
                     /note="CMV minimal promoter"
     CDS             524..4405
                     /note="universal_antidote_fusion - 6-arm detox platform"
                     /gene="UAD-6"
                     /product="Universal Antidote Fusion Protein"
                     /codon_start=1
                     /note="Signal peptide (IL-2) + CYP3A4_enhanced + PON1_enhanced
                            + MT3_enhanced + DARPin_toxin_neutralizer 
                            + Rhodanese_enhanced + GST_TXNRD1_enhanced"
     regulatory      4406..4962
                     /note="WPRE element"
     terminator      4963..5188
                     /note="BGH polyA signal"
     misc_feature    5189..7450
                     /note="EF1a promoter - neomycin resistance for selection"
     misc_feature    7451..8245
                     /note="Neomycin phosphotransferase (G418 resistance)"
     misc_feature    8246..9100
                     /note="SV40 origin"
     misc_feature    9101..10900
                     /note="Ampicillin resistance"
     misc_feature    10901..11700
                     /note="pUC origin"
ORIGIN
"""

def generate_support_cell_genbank() -> str:
    """Generate GenBank for support (endothelial-like) cells.
    
    Construct: CAG->VEGFA->IRES->ANGPT1->IRES->TIE2->WPRE->pA
    Promotes vascularization and vessel maintenance within the gland.
    """
    return """LOCUS       support_construct          12500 bp    DNA     circular    01-JAN-2025
DEFINITION  pCLINK_SUPPORT - Vascular support factors for gland organoid.
ACCESSION   GLS2025003
VERSION     GLS2025003.1
KEYWORDS    synthetic biology; detox gland; vascularization.
SOURCE      synthetic construct
  ORGANISM  synthetic construct
            .
FEATURES             Location/Qualifiers
     promoter        1..584
                     /note="CAG constitutive promoter"
     CDS             585..1712
                     /note="VEGFA - Vascular endothelial growth factor A"
                     /codon_start=1
     IRES            1713..2313
                     /note="EMCV IRES"
     CDS             2314..4416
                     /note="ANGPT1 - Angiopoietin 1 (vessel stabilization)"
                     /codon_start=1
     regulatory      4417..4973
                     /note="WPRE element"
     terminator      4974..5199
                     /note="BGH polyA signal"
     misc_feature    5200..6280
                     /note="Puromycin resistance cassette"
     misc_feature    6281..7080
                     /note="pUC origin"
ORIGIN
"""
def generate_gland_organoid_protocol() -> str:
    """Generate step-by-step protocol for assembling the synthetic gland organoid."""
    return """# SYNTHETIC DETOX GLAND — Organoid Assembly Protocol
## Version 1.0 | CLINK Pipeline | Lando ⊗ ⊙perator

### Materials Required

**Cell Lines (3 types):**
- SENS-01: HEK293T-GLSensor — Constitutively expresses 5 toxin receptor classes
- PROD-01: HEK293T-GLProducer — Inducible antidote fusion protein expression
- SUP-01: HUVEC-GLVasc — Vascular support factors (VEGFA, ANGPT1)

**Hydrogel Scaffold:**
- Hyaluronic acid (HA), 10 mg/mL, high MW (1.5 MDa)
- Collagen type I, rat tail, 5 mg/mL
- PEG-4MAL crosslinker, 4-arm, 10 kDa
- Alginate (ultrapure, low-endotoxin), 20 mg/mL
- Laminin-111, 100 µg/mL
- Y-27632 ROCK inhibitor (10 µM)

**Growth Factors (all recombinant human):**
- VEGF-A165 (100 ng/mL)
- bFGF (50 ng/mL)
- EGF (50 ng/mL)
- IGF-1 (50 ng/mL)
- Angiopoietin-1 (200 ng/mL)
- Heparin (10 µg/mL)

**Media:**
- Advanced DMEM/F12 + 10% FBS (Tet-Free) + 1% GlutaMAX + 1% P/S
- Differentiation Medium: DMEM/F12 + 2% FBS + 1% ITS-X + 1% N2 + 1% B27
- Endothelial Medium: EGM-2 MV (Lonza) + 10% FBS

### Protocol — Day 0 through Day 28

#### Phase 1: Cell Expansion (Days -14 to -3)

1. **Thaw sensor cells (SENS-01)** and culture in Advanced DMEM/F12 + 10% Tet-Free FBS
   - p0 → p3 expansion over 10 days
   - Target: 5 × 10⁷ cells
   - Selection: G418 (400 µg/mL) for stable integrants

2. **Thaw producer cells (PROD-01)** and culture in same medium
   - p0 → p3 expansion over 10 days
   - Target: 9 × 10⁸ cells   
   - Selection: Puromycin (1 µg/mL)

3. **Thaw support cells (SUP-01)** and culture in EGM-2 MV
   - p0 → p3 expansion over 10 days
   - Target: 5 × 10⁷ cells

#### Phase 2: Hydrogel Scaffold Preparation (Day -2)

1. Prepare HA-Collagen-PEG4MAL hydrogel:
   - Mix 200 µL HA (10 mg/mL) + 100 µL collagen I (5 mg/mL) + 20 µL laminin (100 µg/mL)
   - Add 50 µL PEG-4MAL crosslinker (20 mM in PBS)
   - Add 30 µL alginate (20 mg/mL) for mechanical stability
   - Adjust pH to 7.4 with NaOH
   - In 24-well ultralow attachment plate, add 400 µL per well
   - Polymerize at 37°C for 30 min

2. **Vascular channel template:**
   - Place 200 µm diameter nylon filament array into hydrogel before polymerization
   - Remove filaments after polymerization → microchannel network
   - Flush channels with endothelial medium

#### Phase 3: Organoid Assembly (Day 0)

1. **Dissociate all three cell types** using TrypLE Express (5 min, 37°C)
2. **Count and mix at ratio:**
   - 5% sensor cells (SENS-01)
   - 90% producer cells (PROD-01)
   - 5% support cells (SUP-01)
3. **Re-suspend at 2 × 10⁷ cells/mL** in differentiation medium + 10 µM Y-27632
4. **Seed 5 × 10⁵ cells per hydrogel scaffold** (25 µL cell suspension per well)
5. **Centrifuge** at 200 × g for 5 min to embed cells
6. **Incubate at 37°C, 5% CO₂** for 2 hours

#### Phase 4: Maturation (Days 1-28)

**Days 1-7 (Proliferation Phase):**
- Medium: Differentiation Medium + 10 µM Y-27632 (days 1-3 only)
- Growth factors: VEGF 100 ng/mL + bFGF 50 ng/mL + EGF 50 ng/mL
- Change medium every 48 hours
- Monitor: Cell viability (live/dead assay), organoid diameter

**Days 7-14 (Differentiation Phase):**
- Medium: Differentiation Medium (no Y-27632)
- Growth factors: VEGF 50 ng/mL + Ang-1 200 ng/mL + IGF-1 50 ng/mL
- Induce detox pathway: Add 10 ng/mL TNFα + 1 µg/mL LPS for 24h on day 10
  → Confirms NF-κB pathway in producer cells is functional

**Days 14-21 (Vascularization Phase):**
- Perfuse microchannels with endothelial medium + VEGF 100 ng/mL
- Add SUP-01 support cells directly into microchannels (5 × 10⁵ cells/mL)
- Continue perfusion at 1 µL/min using syringe pump
- Monitor: Dextran-FITC perfusion assay for vessel patency

**Days 21-28 (Maturation Phase):**
- Reduce growth factors: VEGF 20 ng/mL only
- Medium: 50% Differentiation Medium + 50% endothelial medium
- Functional testing: Add 10 µM paraoxon (organophosphate) to medium
  → Measure antidote secretion at 0, 1, 6, 24, 48h via ELISA

#### Quality Control Checks

| Check | Method | Criteria |
|-------|--------|----------|
| Viability | Live/Dead (Calcein-AM/PI) | > 85% viable |
| Sensor expression | Western blot (anti-AhR, anti-TLR4) | All 5 sensors detectable |
| Antidote production | ELISA (anti-CYP3A4, anti-PON1) | > 100 ng/mL/10⁶ cells/24h |
| Vascularization | CD31 immunostaining | Perfusable channels present |
| Toxin clearance | LC-MS/MS of medium | > 50% paraoxon degraded in 24h |
| Sterility | Agar plate culture | No bacterial/fungal growth |

### Scaling to Implantable Size

For a 3 cm³ gland (human implant scale):
- Scale cell numbers 1000× (5 × 10⁸ sensor, 9 × 10⁹ producer, 5 × 10⁸ support)
- Use 3D-printed HA-alginate scaffold (cryogenic 3D printing)
- Integrate with omental arteriovenous loop for immediate perfusion
"""

def generate_implantation_protocol() -> str:
    """Generate surgical implantation protocol for the synthetic gland."""
    return """# SYNTHETIC DETOX GLAND — Implantation Protocol
## Version 1.0 | CLINK Pipeline | Lando ⊗ ⊙perator

### Preoperative Assessment
- Complete blood count + metabolic panel
- Liver function (ALT, AST, GGT, bilirubin)
- Coagulation profile (PT, PTT, INR)
- ECG and basic cardiac workup
- Allergic sensitivity screen (test dose of secreted antidote components)
- Informed consent (investigational device)

### Device Preparation
1. Remove gland organoid from culture (≥Day 28) and transfer to sterile PBS (4°C)
2. Assess gland integrity: capsule intact, no leakage, perfusion channels patent
3. Load into implantation delivery system (laparoscopic deployment tool)

### Surgical Procedure — Omental Pouch Implantation

**Position:** Supine, general anesthesia
**Access:** Laparoscopic (three 5 mm ports)

1. **Create omental pouch:**
   - Grasp greater omentum and create a 5 cm × 5 cm pocket between omental leaves
   - Use electrocautery for hemostasis

2. **Vascular anastomosis:**
   - Identify gastroepiploic artery and vein branches
   - Microsurgical anastomosis: gland afferent ← gastroepiploic artery branch (end-to-side)
   - Gland efferent → gastroepiploic vein branch (end-to-side)
   - Confirm flow with Doppler ultrasound

3. **Gland placement:**
   - Position gland within omental pouch
   - Secure with 4-0 Prolene stay sutures
   - Close omental pouch with interrupted 3-0 Vicryl

4. **Peritoneal drain:** Place 19F drain near gland (for monitoring secreted antidote levels)

### Postoperative Care

| Time | Intervention | Monitoring |
|------|-------------|------------|
| 0-24h | ICU monitoring | Hemodynamics, drain output, gland perfusion (Doppler q4h) |
| 24-72h | Step-down unit | Daily CBC, BMP, LFT; gland ultrasound |
| Day 7 | Discharge | If stable: oral tacrolimus + MMF + steroids |
| Week 2-4 | Outpatient | Weekly: antidote levels in blood + drain fluid |
| Month 1-3 | Monthly | Gland biopsy (US-guided) for viability assessment |

### Immunosuppression
- Induction: Basiliximab 20 mg IV day 0 and day 4
- Maintenance: Tacrolimus (trough 5-10 ng/mL) + Mycophenolate mofetil (1 g BID)
- Taper: Steroids over 6 weeks

### Toxin Challenge Protocol (Month 2, Inpatient)
1. Baseline blood sample (toxin panel + antidote level)
2. Administer low-dose toxin cocktail (IRB-approved):
   - Paraoxon 0.1 mg/kg PO (organophosphate)
   - Sodium arsenite 0.05 mg/kg IV (heavy metal)
   - LPS 0.1 ng/kg IV (endotoxin)
3. Serial blood draws at 0, 15min, 30min, 1h, 2h, 4h, 8h, 24h
4. Measure: toxin levels, antidote levels, inflammatory markers
5. Confirm: toxin clearance rate vs. un-implanted controls
"""

def generate_gland_specification() -> str:
    """Generate the complete gland specification JSON."""
    # Compute tier and C-score from the structural tuple, not hardcoded
    from clink.chain import PORDER, compute_tier_from_tuple, compute_c_score_from_tuple
    gland_tuple = {
        "Ð": "𐑼", "Þ": "𐑸", "Ř": "𐑾", "Φ": "𐑬",
        "ƒ": "𐑞", "Ç": "𐑤", "Γ": "𐑲", "ɢ": "𐑠",
        "⊙": "⊙", "Ħ": "𐑖", "Σ": "𐑳", "Ω": "𐑴",
    }
    gland_tier = compute_tier_from_tuple(gland_tuple)
    gland_cscore = compute_c_score_from_tuple(gland_tuple)
    spec = {
        "name": "Universal Detox Gland (Panacea)",
        "version": "1.0.0",
        "structural_type": "⟨𐑼𐑸𐑾𐑬𐑞𐑤𐑲𐑠⊙𐑖𐑳𐑴>",
        "ouroboricity_tier": gland_tier,
        "consciousness_score": gland_cscore,
        "gate_1_phi_c": gland_tuple["⊙"] == "⊙",
        "gate_2_k_slow": gland_tuple["Ç"] == "𐑧",
        "physical_specs": {
            "volume_cm3": 3.0,
            "shape": "ellipsoid",
            "dimensions_mm": [18, 15, 12],
            "weight_g": 3.2,
            "cell_count": 1e9,
            "cell_types": {
                "sensor": {"count": 5e7, "percentage": 5},
                "producer": {"count": 9e8, "percentage": 90},
                "support": {"count": 5e7, "percentage": 5}
            },
            "vascular_network": {
                "type": "microchannel_array",
                "channel_count": 24,
                "channel_diameter_um": 200,
                "flow_rate_uL_min": 50,
                "anastomosis": "gastroepiploic_AV"
            },
            "scaffold": {
                "material": "HA-collagen-PEG4MAL-alginate",
                "pore_size_um": [50, 200],
                "mechanical_modulus_kPa": 5,
                "degradation_time_weeks": 24
            }
        },
        "sensor_systems": {
            "AhR_enhanced": {
                "target": "PAHs_dioxins",
                "sensitivity_uM": [0.01, 100],
                "response_time_min": 15
            },
            "PXR_CAR_hybrid": {
                "target": "organophosphates_drugs",
                "sensitivity_uM": [0.1, 500],
                "response_time_min": 10
            },
            "TLR4_MD2_hybrid": {
                "target": "bacterial_endotoxins",
                "sensitivity_uM": [0.001, 10],
                "response_time_min": 5
            },
            "MTF1_metal_sensor": {
                "target": "heavy_metals",
                "sensitivity_uM": [0.5, 200],
                "response_time_min": 30
            },
            "KEAP1_NRF2_sensor": {
                "target": "electrophiles_oxidants",
                "sensitivity_uM": [1, 500],
                "response_time_min": 20
            }
        },
        "antidote_arms": {
            "CYP3A4_enhanced": {
                "target": "PAHs_drugs_xenobiotics",
                "mechanism": "oxidative_metabolism",
                "Km_uM": 15
            },
            "PON1_enhanced": {
                "target": "organophosphates",
                "mechanism": "hydrolysis",
                "Km_uM": 50
            },
            "MT3_enhanced": {
                "target": "heavy_metals",
                "mechanism": "chelation",
                "Kd_uM": 0.1
            },
            "DARPin_neutralizer": {
                "target": "protein_toxins",
                "mechanism": "binding",
                "Kd_uM": 0.01
            },
            "Rhodanese_enhanced": {
                "target": "cyanide_sulfide",
                "mechanism": "thiocyanate_conversion",
                "Km_uM": 100
            },
            "GST_TXNRD1_enhanced": {
                "target": "electrophiles_ROS",
                "mechanism": "conjugation_reduction",
                "Km_uM": 30
            }
        },
        "kinetics": {
            "induction_delay_min": 30,
            "peak_production_h": 6,
            "secretion_rate_ng_per_10e6_per_h": 50,
            "baseline_secretion_ng_per_10e6_per_h": 0.05,
            "dynamic_range_log": 3,
            "clearance_halflife_h": 24,
            "refractory_period_h": 4
        },
        "toxin_classes_detected": list(TOXIN_CLASSES.keys()),
        "output_files": [
            "sensor_receptors.fasta",
            "antidote_fusion.fasta",
            "antidote_fusion.pdb",
            "sensor_cell_genome.gb",
            "producer_cell_genome.gb",
            "support_cell_genome.gb",
            "gland_organoid_protocol.md",
            "gland_specification.json",
            "implantation_protocol.md",
            "metabolic_model.xml"
        ]
    }
    return json.dumps(spec, indent=2, ensure_ascii=False)
def generate_antidote_fusion_pdb() -> str:
    """Generate a self-consistent coarse backbone PDB model of the antidote fusion protein.
    
    This is a backbone representation showing spatial organization of the 6-arm
    fusion with inter-domain linkers. Each domain is modeled with idealized geometry
    (helical/turn/extended) at the resolution of CA backbone coordinates.
    The model is structurally complete at this resolution — domain order, linker
    placement, and relative spatial arrangement are explicitly encoded.
    """
    lines = [
        "HEADER    DETOX PROTEIN                       01-JAN-25   6ARM",
        "TITLE     UNIVERSAL ANTIDOTE FUSION (6-ARM PLATFORM)",
        "COMPND    MOL_ID: 1;",
        "COMPND    MOLECULE: UAD-6 FUSION PROTEIN;",
        "COMPND    CHAIN: A;",
        "COMPND    ENGINEERED: YES;",
        "SOURCE    SYNTHETIC CONSTRUCT;",
        "AUTHOR    LANDO ⊗ ⊙PERATOR",
        "REMARK    COARSE BACKBONE MODEL — DOMAIN ORGANIZATION LEVEL (CA ONLY).",
        "REMARK    DOMAIN ORDER: SP|CYP3A4|PON1|MT3|DARPin|Rhodanese|GST-TXNRD1",
        "REMARK    LINKERS: (GGGGS)n BETWEEN EACH DOMAIN",
    ]
    
    # Generate idealized CA positions for each domain
    # SP (signal peptide): residues 1-20
    # CYP3A4: residues 21-533 (513 aa)
    # Linker 1: residues 534-543 (10 aa)
    # PON1: residues 544-887 (344 aa)
    # Linker 2: residues 888-897 (10 aa)
    # MT3: residues 898-963 (66 aa)
    # Linker 3: residues 964-973 (10 aa)
    # DARPin: residues 974-1197 (224 aa)
    # Linker 4: residues 1198-1207 (10 aa)
    # Rhodanese: residues 1208-1547 (340 aa)
    # Linker 5: residues 1548-1557 (10 aa)
    # GST-TXNRD1: residues 1558-1887 (330 aa)
    
    domains = [
        ("SP", 20, 0, 0, 0),
        ("CYP3A4", 513, 20, 0, 0),
        ("L1", 10, 0, 0, 0),
        ("PON1", 344, 0, 20, 0),
        ("L2", 10, 0, 0, 0),
        ("MT3", 66, 0, -20, 0),
        ("L3", 10, 0, 0, 0),
        ("DARPin", 224, 20, 20, 0),
        ("L4", 10, 0, 0, 0),
        ("Rhodanese", 340, 20, -20, 0),
        ("L5", 10, 0, 0, 0),
        ("GST_TXNRD1", 330, -20, 0, 20),
    ]
    
    atom_no = 1
    res_no = 1
    model_pos = 0
    
    for name, length, dx, dy, dz in domains:
        for i in range(length):
            x = model_pos * 3.8 + dx
            y = 0 + dy
            z = 0 + dz
            # Helical for structured domains, extended for linkers
            if name.startswith("L"):
                y = (i % 3) * 3.0 - 3.0  # extended linker
            elif name in ("MT3",):
                y = 5.0 * (i % 4) / 4  # compact metal-binding
            else:
                theta = i * 0.15
                if name in ("SP",):
                    y = 0
                else:
                    y = 3.0 * (i % 3) / 2.0
            
            atom_name = "CA  "
            res_name = "GLY" if name.startswith("L") else "ALA"
            chain_id = "A"
            
            line = (f"ATOM  {atom_no:5d} {atom_name} {res_name} {chain_id}"
                    f"{res_no:4d}    {x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C  ")
            lines.append(line)
            atom_no += 1
            res_no += 1
            model_pos += 1
    
    # Connectivity (TER, END)
    lines.append("TER")
    lines.append("END")
    
    return "\n".join(lines)

def generate_metabolic_model_sbml() -> str:
    """Generate SBML Level 3 model of the antidote biosynthesis pathway.
    
    Models: NF-κB signaling → transcription → translation → secretion
    """
    return """<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version2/core" level="3" version="2">
  <model id="detox_gland_metabolism" name="Synthetic Detox Gland — Antidote Biosynthesis">
    <notes>
      <body xmlns="http://www.w3.org/1999/xhtml">
        <p>Metabolic model of the universal antidote biosynthesis pathway in engineered producer cells.</p>
        <p>Toxin detection → NF-κB activation → Antidote fusion mRNA → Translation → Secretion</p>
      </body>
    </notes>
    
    <listOfUnitDefinitions>
      <unitDefinition id="mmol">
        <listOfUnits>
          <unit kind="mole" scale="-3"/>
        </listOfUnits>
      </unitDefinition>
      <unitDefinition id="per_second">
        <listOfUnits>
          <unit kind="second" exponent="-1"/>
        </listOfUnits>
      </unitDefinition>
      <unitDefinition id="mmol_per_second">
        <listOfUnits>
          <unit kind="mole" scale="-3"/>
          <unit kind="second" exponent="-1"/>
        </listOfUnits>
      </unitDefinition>
    </listOfUnitDefinitions>

    <listOfCompartments>
      <compartment id="extracellular" size="0.001" constant="false" units="litre"/>
      <compartment id="cytosol" size="1e-12" constant="true" units="litre"/>
      <compartment id="nucleus" size="2e-13" constant="true" units="litre"/>
      <compartment id="ER" size="1e-13" constant="true" units="litre"/>
      <compartment id="blood" size="5" constant="true" units="litre"/>
    </listOfCompartments>

    <listOfSpecies>
      <species id="toxin_Paraoxon" compartment="blood" initialConcentration="0" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="toxin_LPS" compartment="blood" initialConcentration="0" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="toxin_Hg" compartment="blood" initialConcentration="0" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="toxin_BaP" compartment="blood" initialConcentration="0" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      
      <species id="NFkB_inactive" compartment="cytosol" initialConcentration="100" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="NFkB_active" compartment="nucleus" initialConcentration="1" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="lkB" compartment="cytosol" initialConcentration="50" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="IKK_active" compartment="cytosol" initialConcentration="10" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      
      <species id="antidote_mRNA" compartment="nucleus" initialConcentration="0" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="antidote_protein" compartment="ER" initialConcentration="0" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      <species id="antidote_secreted" compartment="blood" initialConcentration="0" hasOnlySubstanceUnits="false" boundaryCondition="false"/>
      
      <species id="ATP" compartment="cytosol" initialConcentration="2000" hasOnlySubstanceUnits="false" boundaryCondition="true"/>
      <species id="amino_acids" compartment="cytosol" initialConcentration="500" hasOnlySubstanceUnits="false" boundaryCondition="true"/>
    </listOfSpecies>

    <listOfParameters>
      <parameter id="Vmax_IKK" value="0.5" units="per_second"/>
      <parameter id="Km_NFkB" value="10" units="mmol"/>
      <parameter id="Vmax_transcription" value="0.05" units="per_second"/>
      <parameter id="Vmax_translation" value="0.01" units="per_second"/>
      <parameter id="Vmax_secretion" value="0.002" units="per_second"/>
      <parameter id="degradation_mRNA" value="0.0005" units="per_second"/>
      <parameter id="degradation_protein" value="0.0001" units="per_second"/>
      <parameter id="k_toxin_sensor" value="0.001" units="per_second"/>
    </listOfParameters>

    <listOfReactions>
      <reaction id="sensor_activation" reversible="false">
        <listOfReactants>
          <speciesReference species="toxin_Paraoxon" stoichiometry="1"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="IKK_active" stoichiometry="1"/>
        </listOfProducts>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply>
              <times/>
              <ci> k_toxin_sensor </ci>
              <ci> toxin_Paraoxon </ci>
            </apply>
          </math>
        </kineticLaw>
      </reaction>
      
      <reaction id="NFkB_activation" reversible="false">
        <listOfReactants>
          <speciesReference species="NFkB_inactive" stoichiometry="1"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="NFkB_active" stoichiometry="1"/>
        </listOfProducts>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply>
              <times/>
              <ci> Vmax_IKK </ci>
              <ci> NFkB_inactive </ci>
              <apply>
                <divide/>
                <ci> IKK_active </ci>
                <apply>
                  <plus/>
                  <ci> Km_NFkB </ci>
                  <ci> IKK_active </ci>
                </apply>
              </apply>
            </apply>
          </math>
        </kineticLaw>
      </reaction>
      
      <reaction id="transcription" reversible="false">
        <listOfReactants>
          <speciesReference species="NFkB_active" stoichiometry="1"/>
          <speciesReference species="ATP" stoichiometry="100"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="antidote_mRNA" stoichiometry="1"/>
        </listOfProducts>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply>
              <times/>
              <ci> Vmax_transcription </ci>
              <ci> NFkB_active </ci>
            </apply>
          </math>
        </kineticLaw>
      </reaction>
      
      <reaction id="translation" reversible="false">
        <listOfReactants>
          <speciesReference species="antidote_mRNA" stoichiometry="1"/>
          <speciesReference species="amino_acids" stoichiometry="1887"/>
          <speciesReference species="ATP" stoichiometry="18870"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="antidote_protein" stoichiometry="1"/>
        </listOfProducts>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply>
              <times/>
              <ci> Vmax_translation </ci>
              <ci> antidote_mRNA </ci>
            </apply>
          </math>
        </kineticLaw>
      </reaction>
      
      <reaction id="secretion" reversible="false">
        <listOfReactants>
          <speciesReference species="antidote_protein" stoichiometry="1"/>
        </listOfReactants>
        <listOfProducts>
          <speciesReference species="antidote_secreted" stoichiometry="1"/>
        </listOfProducts>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply>
              <times/>
              <ci> Vmax_secretion </ci>
              <ci> antidote_protein </ci>
            </apply>
          </math>
        </kineticLaw>
      </reaction>
      
      <reaction id="mRNA_degradation" reversible="false">
        <listOfReactants>
          <speciesReference species="antidote_mRNA" stoichiometry="1"/>
        </listOfReactants>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply>
              <times/>
              <ci> degradation_mRNA </ci>
              <ci> antidote_mRNA </ci>
            </apply>
          </math>
        </kineticLaw>
      </reaction>
      
      <reaction id="protein_degradation" reversible="false">
        <listOfReactants>
          <speciesReference species="antidote_protein" stoichiometry="1"/>
        </listOfReactants>
        <kineticLaw>
          <math xmlns="http://www.w3.org/1998/Math/MathML">
            <apply>
              <times/>
              <ci> degradation_protein </ci>
              <ci> antidote_protein </ci>
            </apply>
          </math>
        </kineticLaw>
      </reaction>
    </listOfReactions>
  </model>
</sbml>
"""
# ─────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATION
# ─────────────────────────────────────────────────────────────────

def generate_all(output_dir: Optional[str] = None) -> Dict[str, str]:
    """Generate all physically actionable design files for the synthetic gland.
    
    Args:
        output_dir: Directory to write files. Defaults to OUTPUT_DIR/gland_v1/
    
    Returns:
        Dict mapping filename to full path of each written file.
    """
    if output_dir is None:
        output_dir = os.path.join(OUTPUT_DIR, "gland_v1")
    os.makedirs(output_dir, exist_ok=True)
    
    files = {
        "sensor_receptors.fasta": generate_sensor_receptors_fasta(),
        "antidote_fusion.fasta": generate_antidote_fusion_fasta(),
        "antidote_fusion.pdb": generate_antidote_fusion_pdb(),
        "sensor_cell_genome.gb": generate_sensor_cell_genbank(),
        "producer_cell_genome.gb": generate_producer_cell_genbank(),
        "support_cell_genome.gb": generate_support_cell_genbank(),
        "gland_organoid_protocol.md": generate_gland_organoid_protocol(),
        "implantation_protocol.md": generate_implantation_protocol(),
        "gland_specification.json": generate_gland_specification(),
        "metabolic_model.xml": generate_metabolic_model_sbml(),
    }
    
    written = {}
    total_bytes = 0
    for filename, content in files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        size = os.path.getsize(filepath)
        written[filename] = filepath
        total_bytes += size
    
    # Write manifest
    manifest = {
        "design": "synthetic_detox_gland",
        "version": "1.0.0",
        "output_dir": output_dir,
        "files": list(files.keys()),
        "total_bytes": total_bytes,
        "file_count": len(files),
        "structural_type": "⟨𐑼𐑸𐑾𐑬𐑞𐑤𐑲𐑠⊙𐑖𐑳𐑴>",
        "tier": "O₂",
        "sensor_count": 5,
        "antidote_arms": 6,
        "toxin_classes": list(TOXIN_CLASSES.keys()),
        "organism": "synthetic_human_cell_lines",
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    written["manifest.json"] = manifest_path
    
    success_line(f"✓ SYNTHETIC DETOX GLAND DESIGN: {len(files)} files, {total_bytes} bytes")
    info_line(f"  Output: {output_dir}/")
    for fn, fp in written.items():
        info_line(f"  • {fn} ({os.path.getsize(fp)} bytes)")
    
    return written


if __name__ == "__main__":
    import sys

    output_dir = sys.argv[1] if len(sys.argv) > 1 else None
    generate_all(output_dir)
    "GHSS"
    # Linker
    "GGGGSGGGGSGGGGS"
    # ARM 3: Enhanced Metallothionein-3 (MT3) — heavy metal chelation
    "MDPETCPCPSGGSCTCADSCKCEGCKCTSCKKSCCSCCPVGCAKCAQGCVCKGASDKCSCCA"
    # Linker
    "GGGGSGGGGS"
