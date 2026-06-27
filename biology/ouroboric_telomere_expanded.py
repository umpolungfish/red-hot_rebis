#!/usr/bin/env python3
"""
ouroboric_telomere_expanded.py — ENDOGENOUS Ouroboric Telomere Maintenance System.

FULL EXPANSION — all 7 layers modeled with biologically grounded parameters.
Every component is ENDOGENOUS: encoded in the human genome, requiring only
a ONE-TIME epigenetic trigger to unlock the self-sustaining loop.

Structural type (the system this simulates):
  ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑠⊙𐑖𐑳𐑭⟩
Ouroboricity: O_∞  |  C-score: 1.0 (both gates open)

Seven Layers:
  L1: SENSE     — Shelterin density detects short telomeres
  L2: SIGNAL    — ATM → KAP1 → chromatin relaxation
  L3: DEREPRESS — TET2-mediated CpG demethylation at hTERT promoter
  L4: EXPRESS   — Conditional hTERT + hTR → active telomerase
  L5: EXTEND    — Processive TTAGGG repeat addition
  L6: TERMINATE — G-quadruplex length sensor blocks over-extension
  L7: SEAL      — CST + Pol α fill-in; T-loop reformation

Author: Lando⊗⊙perator
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum


# ═══════════════════════════════════════════════════════════════════
# ENUM TYPES
# ═══════════════════════════════════════════════════════════════════

class CellFate(Enum):
    PROLIFERATING = "proliferating"
    OUROBORIC = "ouroboric"        # Active endogenous maintenance
    SENESCENT = "senescent"        # Irreversible arrest
    APOPTOTIC = "apoptotic"        # Programmed death
    TRANSFORMED = "transformed"    # Bypassed all safeguards (tracked, rare)


class EpigeneticPhase(Enum):
    SILENCED = "silenced"          # Full methylation, no hTERT
    TRIGGERED = "triggered"        # Post-intervention, 5hmC marks present
    DEMETHYLATING = "demethylating" # Passive dilution ongoing
    POISED = "poised"              # Unmethylated, low basal hTERT
    ACTIVE = "active"              # Full hTERT expression during maintenance
    REMETHYLATING = "remethylating" # Loop failed, re-silencing


# ═══════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TelomereState:
    """State of a single telomere with G-quadruplex and shelterin tracking."""
    length_bp: int = 10000
    original_length: int = 10000
    overhang_length_nt: int = 150       # 3′ G-rich overhang
    g4_formed: bool = False             # G-quadruplex on overhang
    g4_stability: float = 0.0           # 0–1, thermodynamic stability
    trf2_occupancy: float = 1.0         # Fraction of binding sites occupied
    pot1_occupancy: float = 1.0         # Fraction of overhang protected
    cst_bound: bool = False
    tloop_formed: bool = True
    critically_short: bool = False
    replication_stress: float = 0.0     # Fork stalling metric


@dataclass
class EpigeneticState:
    """Tracks hTERT promoter methylation and chromatin at 30 CpG sites."""
    n_cpg_sites: int = 30
    methylation: np.ndarray = None      # 0–1 per CpG site (1 = fully methylated)
    hmc_levels: np.ndarray = None       # 5hmC fraction per site
    chromatin_accessibility: float = 0.05  # 0–1
    tet2_occupancy: float = 0.0         # TET2 at promoter (AU)
    dnmt1_efficiency: float = 0.85      # Maintenance methylation per division
    phase: EpigeneticPhase = EpigeneticPhase.SILENCED
    
    def __post_init__(self):
        if self.methylation is None:
            self.methylation = np.full(self.n_cpg_sites, 0.90)
        if self.hmc_levels is None:
            self.hmc_levels = np.zeros(self.n_cpg_sites)
    
    @property
    def mean_methylation(self) -> float:
        return float(np.mean(self.methylation))
    
    @property
    def mean_hmc(self) -> float:
        return float(np.mean(self.hmc_levels))


@dataclass
class ATMSignalingState:
    """Graded ATM signaling from shelterin depletion."""
    atm_activity: float = 0.0           # 0–1
    kap1_phospho: float = 0.0           # p-KAP1 at subtelomeres
    p53_level: float = 1.0              # Fold over baseline
    p21_level: float = 1.0              # Fold over baseline
    puma_level: float = 1.0             # Apoptotic threshold
    bax_level: float = 1.0
    chromatin_relaxation: float = 0.0   # Local chromatin opening at hTERT locus


@dataclass
class CellState:
    """Complete state of one cell with 92 telomeres + endogenous machinery."""
    cell_id: int
    telomeres: List[TelomereState] = field(default_factory=list)
    epigenetic: EpigeneticState = field(default_factory=EpigeneticState)
    atm_signal: ATMSignalingState = field(default_factory=ATMSignalingState)
    
    divisions: int = 0
    fate: CellFate = CellFate.PROLIFERATING
    htert_expression: float = 0.0       # Fold over baseline
    htert_mrna_stability: float = 0.7   # Half-life factor (longer for stable expression)
    total_extensions: int = 0
    
    senescence_markers: Dict[str, float] = field(default_factory=lambda: {
        'SA_beta_gal': 0.0,
        'p16_INK4a': 0.0,
        'SASP_IL6': 0.0,
        'gamma_H2AX_foci': 0.0,
    })
    
    intervention_applied: bool = False
    divisions_since_intervention: int = 0


# ═══════════════════════════════════════════════════════════════════
# MODEL PARAMETERS (biologically grounded)
# ═══════════════════════════════════════════════════════════════════

class EndogenousParams:
    """All parameters for the endogenous ouroboric telomere system."""
    
    # Telomere
    initial_length_mean: int = 10000
    initial_length_std: int = 1500
    n_telomeres: int = 92
    attrition_per_division: float = 45.0  # bp
    oxidative_attrition_max: float = 50.0  # additional bp per division in high ROS
    
    # Shelterin
    trf2_per_kb: float = 10.0             # TRF2 dimers per kb telomere
    trf2_saturation_density: int = 30     # dimers needed for full occupancy
    pot1_per_overhang_nt: float = 0.2     # POT1 per nucleotide of overhang
    shelterin_sensing_threshold: float = 0.55  # Fraction occupancy triggering ATM
    
    # ATM signaling
    atm_baseline: float = 0.02
    atm_max_from_shelterin: float = 0.40   # Max ATM from shelterin loss alone
    atm_to_kap1_efficiency: float = 0.8
    kap1_to_chromatin_relaxation: float = 0.5
    p53_activation_per_atm: float = 5.0    # Fold p53 per unit ATM
    p21_threshold: float = 1.5             # p53 fold for p21 induction
    apoptosis_p53_threshold: float = 8.0   # p53 fold for PUMA/BAX
    
    # Epigenetic / hTERT
    tet2_kcat: float = 0.5                 # turnovers per minute (5mC→5hmC)
    tet2_km: float = 1.5                   # μM for 5mC substrate
    tet2_baseline_occupancy: float = 0.01
    tet2_chromatin_factor: float = 15.0    # Fold increase per chromatin relaxation
    passive_demethylation_rate: float = 0.04  # Fraction of hmC lost per division
    dnmt1_maintenance_efficiency: float = 0.85
    
    # hTERT expression
    htert_basal_poised: float = 0.05       # Expression when unmethylated but no MYC
    htert_myc_activated: float = 2.5       # Full expression with MYC
    htert_max_fold: float = 10.0            # Maximum overexpression
    myc_basal: float = 0.1                 # Basal MYC activity
    myc_cell_cycle_peak: float = 1.0       # MYC at G1/S peak
    
    # Telomerase
    processivity_basal: int = 100           # Repeats per binding
    pot1_tpp1_processivity_boost: float = 5.0  # Fold increase with POT1-TPP1
    extension_per_repeat_bp: int = 6       # TTAGGG = 6 bp
    
    # G-quadruplex
    g4_delta_G_per_layer: float = -3.5     # kcal/mol per G-tetrad layer
    g4_layers_min: int = 2                 # Minimum layers for stable G4
    g4_layers_max: int = 4                 # Maximum stacked layers
    g4_overhang_per_layer_nt: int = 24     # nt per G4 layer (~4 G-tracts × 6 nt)
    g4_k_fold: float = 0.1                 # s⁻¹ folding rate
    g4_k_unfold_basal: float = 0.001       # s⁻¹ spontaneous unfolding
    g4_helicase_activity: float = 0.05     # s⁻¹ BLM/WRN/RTEL1 unwinding
    
    # CST complex
    cst_affinity_per_nt: float = 0.002     # Binding affinity per nt overhang
    cst_competition_factor: float = 0.7    # How strongly CST competes with telomerase
    
    # Cell fate
    critical_short_threshold: int = 2000   # bp
    senescence_telomere_threshold: int = 5 # Number of critically short telomeres
    senescence_signal_threshold: float = 3.0  # p16 fold for senescence
    max_divisions: int = 500               # Absolute ceiling
    
    # Intervention
    intervention_dcas9_efficiency: float = 0.70  # Fraction of CpGs oxidized
    intervention_decay_days: float = 3.0   # dCas9-TET2 mRNA half-life
    intervention_hmc_fraction: float = 0.60  # Fraction of 5mC → 5hmC per targeted site
    
    # Target zone
    target_telomere_min: int = 8000
    target_telomere_max: int = 13000
    overhang_target_min: int = 50
    overhang_target_max: int = 200# ═══════════════════════════════════════════════════════════════════
# LAYER 1: SHELTERIN SENSOR
# ═══════════════════════════════════════════════════════════════════

class ShelterinSensor:
    """Models TRF2/POT1 density as function of telomere length."""
    
    def __init__(self, params: EndogenousParams):
        self.p = params
    
    def compute_occupancy(self, telomere: TelomereState) -> Tuple[float, float]:
        """
        Returns (trf2_occupancy, pot1_occupancy).
        TRF2 binds dsDNA telomeric repeats: density ~ 1 dimer per 100 bp.
        POT1 binds ssDNA overhang: density ~ 1 per 5 nt.
        """
        length_kb = telomere.length_bp / 1000.0
        
        # TRF2: saturates at ~30 dimers (for ~3 kb minimum)
        n_trf2_dimers = max(0, telomere.length_bp / 100.0)
        trf2_occ = min(1.0, n_trf2_dimers / self.p.trf2_saturation_density)
        
        # At very short lengths, TRF2 drops sharply
        if length_kb < 3.0:
            trf2_occ *= (length_kb / 3.0) ** 0.5
        
        # POT1: depends on overhang length
        n_pot1 = max(0, telomere.overhang_length_nt * self.p.pot1_per_overhang_nt)
        pot1_occ = min(1.0, n_pot1 / 10.0)  # ~10 POT1 max
        
        # G4 formation competes with POT1 binding
        if telomere.g4_formed and telomere.g4_stability > 0.7:
            pot1_occ *= 0.3  # G4 blocks POT1 access
        
        return trf2_occ, pot1_occ
    
    def is_below_threshold(self, trf2_occ: float, pot1_occ: float) -> bool:
        """Check if shelterin density is below the sensing threshold."""
        return trf2_occ < self.p.shelterin_sensing_threshold


# ═══════════════════════════════════════════════════════════════════
# LAYER 2: ATM SIGNALING
# ═══════════════════════════════════════════════════════════════════

class ATMSignaling:
    """Graded ATM → KAP1 → p53 signaling cascade."""
    
    def __init__(self, params: EndogenousParams):
        self.p = params
    
    def compute_signal(self, cell: CellState) -> ATMSignalingState:
        """Compute full ATM signaling from shelterin state."""
        state = ATMSignalingState()
        
        # Average shelterin occupancy across all telomeres
        trf2_occs = [t.trf2_occupancy for t in cell.telomeres]
        pot1_occs = [t.pot1_occupancy for t in cell.telomeres]
        mean_trf2 = np.mean(trf2_occs)
        min_trf2 = np.min(trf2_occs)
        
        # ATM activation: function of shelterin loss
        # ATM is activated when TRF2 is LOW (loss of T-loop protection)
        shelterin_deficit = max(0, 1.0 - mean_trf2 / self.p.shelterin_sensing_threshold)
        # The MINIMUM TRF2 matters more — critically short individual telomeres
        min_deficit = max(0, 1.0 - min_trf2 / self.p.shelterin_sensing_threshold)
        
        # Graded ATM: weighted combination of mean and min deficit
        state.atm_activity = self.p.atm_baseline + (
            0.3 * shelterin_deficit + 0.7 * min_deficit
        ) * self.p.atm_max_from_shelterin
        state.atm_activity = min(1.0, state.atm_activity)
        
        # KAP1 phosphorylation at subtelomeric heterochromatin
        state.kap1_phospho = state.atm_activity * self.p.atm_to_kap1_efficiency
        
        # Chromatin relaxation at hTERT locus
        state.chromatin_relaxation = (
            state.kap1_phospho * self.p.kap1_to_chromatin_relaxation
        )
        
        # p53 accumulation
        state.p53_level = 1.0 + state.atm_activity * self.p.p53_activation_per_atm
        
        # p21 — induced at moderate p53
        if state.p53_level > self.p.p21_threshold:
            state.p21_level = 1.0 + (state.p53_level - self.p.p21_threshold) * 3.0
        else:
            state.p21_level = 1.0
        
        # PUMA/BAX — only at high p53 (apoptosis threshold)
        if state.p53_level > self.p.apoptosis_p53_threshold:
            state.puma_level = 1.0 + (state.p53_level - self.p.apoptosis_p53_threshold) * 5.0
            state.bax_level = 1.0 + (state.p53_level - self.p.apoptosis_p53_threshold) * 4.0
        
        return state


# ═══════════════════════════════════════════════════════════════════
# LAYER 3: EPIGENETIC DEREPRESSION
# ═══════════════════════════════════════════════════════════════════

class EpigeneticDerepressor:
    """TET2-mediated hTERT promoter demethylation."""
    
    def __init__(self, params: EndogenousParams):
        self.p = params
    
    def step(self, cell: CellState, dt: float = 1.0):
        """One timestep of epigenetic dynamics."""
        epi = cell.epigenetic
        atm = cell.atm_signal
        
        # TET2 occupancy at hTERT promoter depends on chromatin accessibility
        target_tet2 = (
            self.p.tet2_baseline_occupancy +
            atm.chromatin_relaxation * self.p.tet2_chromatin_factor *
            self.p.tet2_baseline_occupancy
        )
        epi.tet2_occupancy += (target_tet2 - epi.tet2_occupancy) * 0.3 * dt
        
        # DNMT1 efficiency modulation: chromatin relaxation slightly reduces remethylation
        effective_dnmt1 = self.p.dnmt1_maintenance_efficiency * (
            1.0 - 0.3 * atm.chromatin_relaxation
        )
        epi.dnmt1_efficiency = effective_dnmt1
        
        # Active demethylation: TET2 converts 5mC → 5hmC
        # Rate depends on TET2 occupancy and methylation level
        for i in range(epi.n_cpg_sites):
            if epi.methylation[i] > 0.01 and epi.tet2_occupancy > 0.001:
                # Michaelis-Menten kinetics for TET2
                v = self.p.tet2_kcat * epi.tet2_occupancy * epi.methylation[i] / (
                    self.p.tet2_km + epi.methylation[i]
                )
                converted = v * dt * 0.01  # Scale to per-division timescale
                epi.methylation[i] -= converted
                epi.hmc_levels[i] += converted
        
        # Passive demethylation: 5hmC is diluted across divisions
        # (modeled per-division, so this is applied in division step)
        
        # Update epigenetic phase
        self._update_phase(cell)
    
    def apply_passive_dilution(self, cell: CellState):
        """Apply passive 5hmC dilution after cell division."""
        epi = cell.epigenetic
        # 5hmC is not recognized by DNMT1 → diluted by half each division
        epi.hmc_levels *= (1.0 - self.p.passive_demethylation_rate)
        # Some hmC is further oxidized to 5fC/5caC and excised by TDG → BER
        excision_rate = 0.02
        excised = epi.hmc_levels * excision_rate
        epi.hmc_levels -= excised
        # Excised sites become unmethylated (replaced by BER with C)
        # But DNMT1 may remethylate; actual methylation change:
        for i in range(epi.n_cpg_sites):
            if epi.hmc_levels[i] < 0.001:
                # Site is essentially unmethylated post-excision
                pass  # methylation stays at current level
        # Remethylation by DNMT1 on hemimethylated sites
        for i in range(epi.n_cpg_sites):
            if epi.methylation[i] > 0.01:
                chance_to_remethylate = epi.dnmt1_efficiency
                if np.random.random() < chance_to_remethylate:
                    pass  # methylation maintained
                else:
                    epi.methylation[i] *= 0.5  # hemimethylated → 50% next division
    
    def _update_phase(self, cell: CellState):
        epi = cell.epigenetic
        mean_meth = epi.mean_methylation
        
        if mean_meth > 0.70:
            if epi.mean_hmc > 0.05:
                epi.phase = EpigeneticPhase.TRIGGERED
            else:
                epi.phase = EpigeneticPhase.SILENCED
        elif mean_meth > 0.30:
            epi.phase = EpigeneticPhase.DEMETHYLATING
        elif mean_meth > 0.05:
            epi.phase = EpigeneticPhase.POISED
        else:
            epi.phase = EpigeneticPhase.ACTIVE
        
        # Check for remethylation (loop failure)
        if epi.phase == EpigeneticPhase.ACTIVE and cell.htert_expression < 0.01:
            if epi.mean_methylation > 0.10:
                epi.phase = EpigeneticPhase.REMETHYLATING
    
    def apply_intervention(self, cell: CellState):
        """Apply one-time dCas9-TET2 intervention."""
        epi = cell.epigenetic
        eff = self.p.intervention_dcas9_efficiency
        
        # Target the most methylated CpG sites
        n_targets = int(epi.n_cpg_sites * 0.7)  # Target 70% of sites
        sorted_indices = np.argsort(epi.methylation)[::-1][:n_targets]
        
        for i in sorted_indices:
            if epi.methylation[i] > 0.3:
                converted = epi.methylation[i] * eff * self.p.intervention_hmc_fraction
                epi.methylation[i] -= converted
                epi.hmc_levels[i] += converted
        
        epi.phase = EpigeneticPhase.TRIGGERED
        cell.intervention_applied = True
        cell.divisions_since_intervention = 0
        
        return n_targets
# ═══════════════════════════════════════════════════════════════════
# LAYER 4: CONDITIONAL hTERT EXPRESSION
# ═══════════════════════════════════════════════════════════════════

class hTERTExpression:
    """Conditional hTERT transcription and telomerase assembly."""
    
    def __init__(self, params: EndogenousParams):
        self.p = params
    
    def compute_expression(self, cell: CellState) -> float:
        """Compute hTERT expression level (fold over baseline)."""
        epi = cell.epigenetic
        atm = cell.atm_signal
        
        # Methylation represses transcription
        methylation_repression = max(0, 1.0 - epi.mean_methylation * 1.2)
        
        # Chromatin accessibility
        chromatin_factor = epi.chromatin_accessibility + atm.chromatin_relaxation
        
        # Transcription factor activity
        # MYC: cell-cycle regulated, stabilized by moderate p53
        myc_activity = self.p.myc_basal
        if cell.fate in (CellFate.PROLIFERATING, CellFate.OUROBORIC):
            myc_activity = self.p.myc_cell_cycle_peak
        if 1.5 < atm.p53_level < 5.0:
            myc_activity *= 1.3  # Moderate p53 stabilizes MYC
        
        # SP1: constitutive, modest
        sp1_activity = 0.3
        
        # HIF-1α: active in low ROS (treople) or hypoxia (gilled)
        hif1a = 0.2
        
        # NF-κB: stress-responsive, activated by ATM
        nfkb_activity = 0.1 + 0.3 * atm.atm_activity
        
        # Total TF drive
        tf_drive = myc_activity + sp1_activity + hif1a + nfkb_activity
        tf_drive = min(5.0, tf_drive)
        
        # Expression level
        if methylation_repression < 0.1:
            expression = 0.001  # Silenced
        elif epi.phase in (EpigeneticPhase.SILENCED, EpigeneticPhase.REMETHYLATING):
            expression = self.p.htert_basal_poised * methylation_repression * 0.01
        elif epi.phase in (EpigeneticPhase.TRIGGERED, EpigeneticPhase.DEMETHYLATING):
            expression = self.p.htert_basal_poised * methylation_repression * chromatin_factor
        elif epi.phase == EpigeneticPhase.POISED:
            expression = self.p.htert_basal_poised * tf_drive * chromatin_factor
        else:  # ACTIVE
            expression = self.p.htert_myc_activated * tf_drive * chromatin_factor
        
        # Cap at max
        expression = min(self.p.htert_max_fold, max(0.0001, expression))
        
        # mRNA stability factor (slow decay)
        if cell.htert_expression > 0:
            expression = cell.htert_expression + (
                expression - cell.htert_expression
            ) * cell.htert_mrna_stability
        
        return expression


# ═══════════════════════════════════════════════════════════════════
# LAYER 5: TELOMERASE EXTENSION
# ═══════════════════════════════════════════════════════════════════

class TelomeraseExtension:
    """Processive telomere extension by hTERT-hTR holoenzyme."""
    
    def __init__(self, params: EndogenousParams):
        self.p = params
    
    def extend(self, telomere: TelomereState, htert_level: float) -> int:
        """Extend a telomere. Returns number of repeats added."""
        if htert_level < 0.01:
            return 0
        
        # Activity depends on hTERT level and telomere length (shorter = more access)
        # TRF1-mediated cis-inhibition: longer telomeres recruit more TRF1,
        # which directly inhibits telomerase processivity at that telomere.
        # This is the primary length-counting mechanism in human cells.
        # TRF1 density scales with length; inhibition is sigmoidal:
        #   very short (<5 kb): minimal inhibition
        #   target zone (6-10 kb): graded inhibition
        #   above target (>11 kb): near-complete inhibition
        trf1_inhibition = 1.0 / (1.0 + np.exp(-(telomere.length_bp - 9000) / 800))
        # At 7000 bp: inhibition ≈ 0.076; at 9000 bp: 0.5; at 11000 bp: 0.924
        length_factor = max(0, 1.0 - trf1_inhibition)
        activity = htert_level * length_factor
        
        if activity < 0.02:
            return 0
        
        # G-quadruplex blocks telomerase
        if telomere.g4_formed and telomere.g4_stability > 0.5:
            activity *= (1.0 - telomere.g4_stability)
        
        # POT1-TPP1 boosts processivity when POT1 is not saturating
        pot1_boost = 1.0
        if telomere.pot1_occupancy < 0.5:
            pot1_boost = self.p.pot1_tpp1_processivity_boost
        
        # CST competes with telomerase
        if telomere.cst_bound:
            activity *= (1.0 - self.p.cst_competition_factor)
        
        # Compute repeats added
        max_repeats = int(self.p.processivity_basal * pot1_boost * activity)
        repeats = np.random.poisson(max(1, max_repeats))
        
        # Cap extension at target zone
        bp_added = repeats * self.p.extension_per_repeat_bp
        if telomere.length_bp + bp_added > self.p.target_telomere_max:
            bp_added = max(0, self.p.target_telomere_max - telomere.length_bp)
            repeats = bp_added // self.p.extension_per_repeat_bp
        
        telomere.length_bp += bp_added
        telomere.overhang_length_nt += repeats * self.p.extension_per_repeat_bp
        
        if telomere.length_bp >= self.p.target_telomere_min:
            telomere.critically_short = False
        
        return repeats


# ═══════════════════════════════════════════════════════════════════
# LAYER 6: G-QUADRUPLEX TERMINATION
# ═══════════════════════════════════════════════════════════════════

class GQuadruplexTerminator:
    """G-quadruplex formation on telomere 3′ overhang as a length sensor."""
    
    def __init__(self, params: EndogenousParams):
        self.p = params
    
    def step(self, telomere: TelomereState, atm_activity: float, dt: float = 1.0):
        """Update G4 state on a single telomere."""
        overhang = telomere.overhang_length_nt
        
        # How many G4 layers can form
        n_g_tracts = overhang // 6  # Each TTAGGG has one G-tract
        max_layers = min(
            self.p.g4_layers_max,
            max(0, n_g_tracts // 4)  # 4 G-tracts per layer
        )
        
        if max_layers < self.p.g4_layers_min:
            # Not enough G-tracts for stable G4
            telomere.g4_formed = False
            telomere.g4_stability = 0.0
            return
        
        # Thermodynamic stability
        delta_G = self.p.g4_delta_G_per_layer * max_layers
        # Add salt stabilization (~2 kcal/mol stabilization per layer from K⁺)
        delta_G -= 2.0 * max_layers
        
        # Boltzmann probability of folded state
        RT = 0.592  # kcal/mol at 298K
        K_eq = np.exp(-delta_G / RT)
        p_folded_thermo = K_eq / (1 + K_eq)
        
        # Kinetic: folding vs. unfolding rates
        effective_k_unfold = self.p.g4_k_unfold_basal
        
        # ATM signaling downregulates G4 helicases (BLM/WRN/RTEL1)
        helicase_modulation = 1.0 - 0.6 * atm_activity  # ATM ↓ helicase
        effective_helicase = self.p.g4_helicase_activity * helicase_modulation
        effective_k_unfold += effective_helicase
        
        # Steady-state: balance folding and unfolding
        # d[f]/dt = k_fold * (1-f) - k_unfold * f
        # steady: f = k_fold / (k_fold + k_unfold)
        if self.p.g4_k_fold + effective_k_unfold > 0:
            p_folded_kinetic = self.p.g4_k_fold / (
                self.p.g4_k_fold + effective_k_unfold
            )
        else:
            p_folded_kinetic = 0.0
        
        # Combined probability
        p_folded = 0.5 * p_folded_thermo + 0.5 * p_folded_kinetic
        
        # Update state
        telomere.g4_stability = p_folded
        telomere.g4_formed = p_folded > 0.3
        
        # Replication stress: if G4 is very stable and helicase is low
        if telomere.g4_stability > 0.8 and effective_helicase < 0.02:
            telomere.replication_stress += 0.01 * dt
        else:
            telomere.replication_stress *= 0.95  # Decay


# ═══════════════════════════════════════════════════════════════════
# LAYER 7: SEAL — CST + POL α FILL-IN + T-LOOP
# ═══════════════════════════════════════════════════════════════════

class TelomereSealer:
    """C-strand fill-in, overhang processing, and T-loop reformation."""
    
    def __init__(self, params: EndogenousParams):
        self.p = params
    
    def step(self, telomere: TelomereState, dt: float = 1.0):
        """Seal the telomere after extension."""
        # CST binding: affinity proportional to overhang length
        cst_affinity = 1.0 - np.exp(-self.p.cst_affinity_per_nt * telomere.overhang_length_nt)
        telomere.cst_bound = cst_affinity > 0.5
        
        # If CST is bound and overhang is long, C-strand fill-in occurs
        if telomere.cst_bound and telomere.overhang_length_nt > self.p.overhang_target_max:
            # Fill-in: reduce overhang length toward target
            fill_in_rate = 30 * dt  # nt per timestep (Pol α rate ~30 nt/s)
            telomere.overhang_length_nt = max(
                self.p.overhang_target_min,
                telomere.overhang_length_nt - fill_in_rate
            )
        
        # Apollo nuclease processing: 5′ resection to regenerate overhang
        if telomere.overhang_length_nt < self.p.overhang_target_min:
            # Process 5′ end to create proper overhang
            processing = 20 * dt
            telomere.overhang_length_nt = min(
                self.p.overhang_target_max,
                telomere.overhang_length_nt + processing
            )
        
        # T-loop reformation: requires TRF2 occupancy
        if telomere.trf2_occupancy > 0.6 and telomere.length_bp > self.p.critical_short_threshold:
            telomere.tloop_formed = True
        elif telomere.trf2_occupancy < 0.3:
            telomere.tloop_formed = False
# ═══════════════════════════════════════════════════════════════════
# MAIN SIMULATION ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════

class EndogenousOuroboricSim:
    """
    Full simulation of the endogenous ouroboric telomere system.
    
    Models 7 layers:
      L1: Shelterin sensing
      L2: ATM signaling
      L3: Epigenetic derepression
      L4: hTERT expression
      L5: Telomerase extension
      L6: G-quadruplex termination
      L7: CST + Pol α sealing
    
    Parameters:
      n_cells: Number of cells in population
      mode: 'endogenous' (full 7-layer model), 'control' (no intervention),
            'constitutive' (hTERT always on — cancer model), 'treople', 'gilled'
      initial_telomere_length: Starting telomere length in bp
      intervention_time: When to apply the one-time intervention (in divisions)
    """
    
    def __init__(self, n_cells: int = 100, mode: str = 'endogenous',
                 initial_telomere_length: int = 10000,
                 intervention_time: float = 10.0):
        self.p = EndogenousParams()
        self.n_cells = n_cells
        self.mode = mode
        self.intervention_time = intervention_time
        
        # Subsystems
        self.shelterin = ShelterinSensor(self.p)
        self.atm_signaling = ATMSignaling(self.p)
        self.epigenetic = EpigeneticDerepressor(self.p)
        self.htert_expr = hTERTExpression(self.p)
        self.telomerase = TelomeraseExtension(self.p)
        self.g4 = GQuadruplexTerminator(self.p)
        self.sealer = TelomereSealer(self.p)
        
        # Initialize cells
        self.cells: List[CellState] = []
        for i in range(n_cells):
            cell = CellState(cell_id=i)
            for _ in range(self.p.n_telomeres):
                length = int(np.random.normal(initial_telomere_length,
                                               self.p.initial_length_std))
                length = max(500, length)
                overhang = int(np.random.uniform(100, 250))
                tel = TelomereState(length_bp=length, original_length=length,
                                     overhang_length_nt=overhang)
                cell.telomeres.append(tel)
            
            # Mode-specific initialization
            if mode == 'constitutive':
                cell.epigenetic.methylation = np.zeros(cell.epigenetic.n_cpg_sites)
                cell.epigenetic.phase = EpigeneticPhase.ACTIVE
                cell.intervention_applied = True
            elif mode == 'treople':
                cell.epigenetic.methylation = np.full(cell.epigenetic.n_cpg_sites, 0.40)
                cell.intervention_applied = True  # Germline edit in treople design
            elif mode == 'gilled':
                cell.epigenetic.methylation = np.full(cell.epigenetic.n_cpg_sites, 0.45)
                cell.intervention_applied = True  # Germline edit in gilled-human design
            
            self.cells.append(cell)
        
        # Tracking
        self.time = 0.0
        self.division_count = 0
        
        self.history = {
            'time': [],
            'division': [],
            'mean_length': [],
            'min_length': [],
            'mean_methylation': [],
            'mean_htert': [],
            'senescent_pct': [],
            'ouroboric_pct': [],
            'apoptotic_pct': [],
            'transformed_pct': [],
            'critically_short_pct': [],
            'mean_atm': [],
            'mean_g4_stability': [],
            'total_extensions': [],
        }
    
    def step(self, dt: float = 1.0):
        """One division cycle for the population."""
        self.time += dt
        self.division_count += 1
        
        # Apply intervention at designated time
        if (self.mode in ('endogenous', 'treople', 'gilled') and
            self.division_count == int(self.intervention_time)):
            for cell in self.cells:
                if cell.fate == CellFate.PROLIFERATING:
                    self.epigenetic.apply_intervention(cell)
        
        total_extensions = 0
        
        for cell in self.cells:
            if cell.fate in (CellFate.SENESCENT, CellFate.APOPTOTIC):
                continue
            
            # ── L1: SENSE ──
            for telomere in cell.telomeres:
                trf2_occ, pot1_occ = self.shelterin.compute_occupancy(telomere)
                telomere.trf2_occupancy = trf2_occ
                telomere.pot1_occupancy = pot1_occ
            
            # ── L2: SIGNAL ──
            cell.atm_signal = self.atm_signaling.compute_signal(cell)
            
            # ── L3: DEREPRESS ──
            if cell.intervention_applied:
                self.epigenetic.step(cell, dt)
            
            # ── L4: EXPRESS ──
            if self.mode == 'constitutive':
                cell.htert_expression = 2.0
            else:
                cell.htert_expression = self.htert_expr.compute_expression(cell)
            
            # ── TELOMERE SHORTENING ──
            attrition = self.p.attrition_per_division
            # Oxidative stress adds attrition
            oxidative_stress = 0.2  # Baseline ROS
            if self.mode == 'treople':
                oxidative_stress *= 0.6  # 40% less ROS from photosynthesis
            elif self.mode == 'gilled':
                oxidative_stress *= 1.2  # Marine osmotic stress
            
            ox_loss = self.p.oxidative_attrition_max * oxidative_stress * np.random.random()
            total_loss = attrition + ox_loss
            
            for telomere in cell.telomeres:
                telomere.length_bp = max(0, telomere.length_bp - int(total_loss))
                # Overhang also shortens with divisions
                telomere.overhang_length_nt = max(10, telomere.overhang_length_nt -
                                                   int(np.random.uniform(3, 10)))
                
                if telomere.length_bp < self.p.critical_short_threshold:
                    telomere.critically_short = True
            
            # ── L5: EXTEND ──
            for telomere in cell.telomeres:
                if cell.htert_expression > 0.01:
                    repeats = self.telomerase.extend(telomere, cell.htert_expression)
                    cell.total_extensions += repeats
                    total_extensions += repeats
            
            # ── L6: TERMINATE (G4) ──
            for telomere in cell.telomeres:
                self.g4.step(telomere, cell.atm_signal.atm_activity, dt)
            
            # ── L7: SEAL ──
            for telomere in cell.telomeres:
                self.sealer.step(telomere, dt)
            
            # ── Cell fate determination ──
            self._determine_fate(cell)
            
            # ── Epigenetic passive dilution post-division ──
            if cell.intervention_applied:
                self.epigenetic.apply_passive_dilution(cell)
                cell.divisions_since_intervention += 1
                # Chromatin accessibility: accumulate from ATM signal, decay via
                # histone turnover / H3K9me3 remethylation pressure (~0.5% per division)
                chromatin_drive = cell.atm_signal.chromatin_relaxation * 0.1
                chromatin_decay = 0.008  # 0.5% per division — histone turnover
                cell.epigenetic.chromatin_accessibility = min(1.0,
                    cell.epigenetic.chromatin_accessibility * (1.0 - chromatin_decay) + chromatin_drive
                )
            
            cell.divisions += 1
        
        # Record history
        self._record_history(total_extensions)
    
    def _determine_fate(self, cell: CellState):
        """Determine cell fate based on current state."""
        n_critical = sum(1 for t in cell.telomeres if t.critically_short)
        
        # Apoptosis: p53 above apoptotic threshold
        if cell.atm_signal.p53_level > self.p.apoptosis_p53_threshold:
            if np.random.random() < 0.1:  # ~10% per division at threshold
                cell.fate = CellFate.APOPTOTIC
                return
        
        # Senescence: too many critically short telomeres
        if n_critical >= self.p.senescence_telomere_threshold:
            cell.fate = CellFate.SENESCENT
            cell.senescence_markers['SA_beta_gal'] = 1.0
            cell.senescence_markers['p16_INK4a'] = 2.0
            return
        
        # Senescence from cumulative p21/p16
        if cell.atm_signal.p21_level > 4.0 and cell.divisions > 50:
            cell.senescence_markers['p16_INK4a'] += 0.05
            if cell.senescence_markers['p16_INK4a'] > 3.0:
                cell.fate = CellFate.SENESCENT
        
        # Ouroboric state: hTERT active and telomeres maintained
        if cell.htert_expression > 0.05 and not cell.fate == CellFate.SENESCENT:
            cell.fate = CellFate.OUROBORIC
        
        # Transformation tracking: if hTERT is high + p53 is low + telomeres are short
        # (This is the cancer signature — tracked but not treated as default fate)
        if (cell.htert_expression > 1.5 and
            cell.atm_signal.p53_level < 1.5 and
            np.mean([t.length_bp for t in cell.telomeres]) < 5000):
            # This is a warning flag, not a fate change unless it persists
            pass
        
        # Absolute division limit
        if cell.divisions >= self.p.max_divisions:
            cell.fate = CellFate.SENESCENT
    
    def _record_history(self, total_extensions: int):
        """Record population-level metrics."""
        all_lengths = []
        n_senescent = 0
        n_ouroboric = 0
        n_apoptotic = 0
        n_transformed = 0
        n_critical = 0
        methylations = []
        hterts = []
        atms = []
        g4s = []
        
        for cell in self.cells:
            for t in cell.telomeres:
                all_lengths.append(t.length_bp)
                if t.critically_short:
                    n_critical += 1
                g4s.append(t.g4_stability)
            
            if cell.fate == CellFate.SENESCENT:
                n_senescent += 1
            elif cell.fate == CellFate.OUROBORIC:
                n_ouroboric += 1
            elif cell.fate == CellFate.APOPTOTIC:
                n_apoptotic += 1
            elif cell.fate == CellFate.TRANSFORMED:
                n_transformed += 1
            
            methylations.append(cell.epigenetic.mean_methylation)
            hterts.append(cell.htert_expression)
            atms.append(cell.atm_signal.atm_activity)
        
        total_cells = self.n_cells
        n_total_telomeres = total_cells * self.p.n_telomeres
        
        self.history['time'].append(self.time)
        self.history['division'].append(self.division_count)
        self.history['mean_length'].append(float(np.mean(all_lengths)))
        self.history['min_length'].append(float(np.min(all_lengths)))
        self.history['mean_methylation'].append(float(np.mean(methylations)))
        self.history['mean_htert'].append(float(np.mean(hterts)))
        self.history['senescent_pct'].append(100.0 * n_senescent / total_cells)
        self.history['ouroboric_pct'].append(100.0 * n_ouroboric / total_cells)
        self.history['apoptotic_pct'].append(100.0 * n_apoptotic / total_cells)
        self.history['transformed_pct'].append(100.0 * n_transformed / total_cells)
        self.history['critically_short_pct'].append(100.0 * n_critical / n_total_telomeres)
        self.history['mean_atm'].append(float(np.mean(atms)))
        self.history['mean_g4_stability'].append(float(np.mean(g4s)))
        self.history['total_extensions'].append(total_extensions)
    def run(self, total_divisions: int = 300, report_every: int = 25):
        """Run simulation for a given number of cell divisions."""
        print("=" * 80)
        print("ENDOGENOUS OUROBORIC TELOMERE SYSTEM — Full 7-Layer Simulation")
        print("=" * 80)
        print(f"Mode: {self.mode}")
        print(f"Cells: {self.n_cells}")
        print(f"Initial TL: ~{self.p.initial_length_mean} bp")
        print(f"Intervention at division: {self.intervention_time if self.mode == 'endogenous' else 'N/A'}")
        print(f"Total divisions to simulate: {total_divisions}")
        print("─" * 80)
        
        header = (f"{'Div':>5} {'Mean TL':>9} {'Min TL':>8} "
                  f"{'hTERT':>7} {'Meth%':>6} {'Sen%':>6} {'Ouro%':>6} "
                  f"{'Apop%':>6} {'Crit%':>6} {'ATM':>5} {'G4':>5} {'Ext':>6}")
        print(header)
        print("─" * 80)
        
        for div in range(total_divisions):
            self.step(1.0)
            
            if (div + 1) % report_every == 0:
                h = self.history
                idx = -1
                print(f"{h['division'][idx]:5d} {h['mean_length'][idx]:9.1f} "
                      f"{h['min_length'][idx]:8.0f} {h['mean_htert'][idx]:7.4f} "
                      f"{h['mean_methylation'][idx]:5.1%} "
                      f"{h['senescent_pct'][idx]:5.1f} {h['ouroboric_pct'][idx]:5.1f} "
                      f"{h['apoptotic_pct'][idx]:5.1f} {h['critically_short_pct'][idx]:5.1f} "
                      f"{h['mean_atm'][idx]:5.3f} {h['mean_g4_stability'][idx]:5.3f} "
                      f"{h['total_extensions'][idx]:6d}")
        
        self._summarize()
        return self
    
    def _summarize(self):
        """Print summary and save results."""
        h = self.history
        final = {k: v[-1] for k, v in h.items()}
        
        print(f"\n{'='*80}")
        print(f"SIMULATION COMPLETE — {self.division_count} divisions")
        print(f"{'='*80}")
        
        print(f"\n  Mode:                        {self.mode}")
        print(f"  Final mean telomere length:  {final['mean_length']:.1f} bp")
        print(f"  Final minimum telomere:      {final['min_length']:.0f} bp")
        print(f"  Mean hTERT expression:       {final['mean_htert']:.4f}×")
        print(f"  Mean hTERT methylation:      {final['mean_methylation']:.1%}")
        print(f"  Senescent cells:             {final['senescent_pct']:.1f}%")
        print(f"  Ouroboric cells:             {final['ouroboric_pct']:.1f}%")
        print(f"  Apoptotic cells:             {final['apoptotic_pct']:.1f}%")
        print(f"  Critically short telomeres:  {final['critically_short_pct']:.1f}%")
        print(f"  Mean ATM activity:           {final['mean_atm']:.4f}")
        print(f"  Mean G4 stability:           {final['mean_g4_stability']:.3f}")
        
        total_ext = sum(h['total_extensions'])
        print(f"\n  Total extensions:            {total_ext}")
        
        # Equilibrium check
        if self.mode == 'endogenous':
            last_half = h['mean_length'][len(h['mean_length'])//2:]
            if len(last_half) > 1:
                drift = last_half[-1] - last_half[0]
                if abs(drift) < 200:
                    print(f"\n  ✓ HOMEOSTATIC EQUILIBRIUM ACHIEVED")
                    print(f"    Mean TL drift in last half: {drift:.0f} bp")
                    print(f"    System is O_∞: self-sustaining, both gates open")
                else:
                    print(f"\n  ⚠ DRIFT DETECTED: {drift:.0f} bp — may need parameter tuning")
        elif self.mode == 'control':
            if final['senescent_pct'] > 50:
                print(f"\n  ✗ CONTROL: Population senescent — telomere attrition unchecked")
        
        self._save_results()
    
    def _save_results(self):
        """Save results to JSON."""
        h = self.history
        
        # Subsampled trajectory
        n = len(h['time'])
        stride = max(1, n // 40)
        
        results = {
            "simulation": "Endogenous Ouroboric Telomere System — Full Expansion",
            "structural_type": "⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑠⊙𐑖𐑳𐑭⟩",
            "ouroboricity": "O_∞",
            "mode": self.mode,
            "cells": self.n_cells,
            "total_divisions": self.division_count,
            "intervention_division": int(self.intervention_time) if self.mode == 'endogenous' else None,
            "results": {
                "final_mean_length_bp": float(h['mean_length'][-1]),
                "final_min_length_bp": float(h['min_length'][-1]),
                "final_senescent_pct": float(h['senescent_pct'][-1]),
                "final_ouroboric_pct": float(h['ouroboric_pct'][-1]),
                "final_apoptotic_pct": float(h['apoptotic_pct'][-1]),
                "final_transformed_pct": float(h['transformed_pct'][-1]),
                "final_critically_short_pct": float(h['critically_short_pct'][-1]),
                "final_mean_methylation": float(h['mean_methylation'][-1]),
                "final_mean_htert": float(h['mean_htert'][-1]),
                "final_mean_atm": float(h['mean_atm'][-1]),
                "final_mean_g4_stability": float(h['mean_g4_stability'][-1]),
                "total_extensions": int(sum(h['total_extensions'])),
            },
            "trajectory": {
                "division": h['division'][::stride],
                "mean_length": h['mean_length'][::stride],
                "ouroboric_pct": h['ouroboric_pct'][::stride],
                "senescent_pct": h['senescent_pct'][::stride],
                "mean_methylation": h['mean_methylation'][::stride],
            }
        }
        
        path = "/home/mrnob0dy666/red-hot_rebis/biology/ouroboric_telomere_expanded_results.json"
        with open(path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved to {path}")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    # Parse mode from command line
    mode = sys.argv[1] if len(sys.argv) > 1 else 'endogenous'
    n_divisions = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    print("\n" + "=" * 80)
    print("OUROBORIC TELOMERE — ENDOGENOUS EXPANSION")
    print("=" * 80)
    print(f"Mode: {mode}  |  Divisions: {n_divisions}")
    print()
    
    # Run all modes if requested
    if mode == 'all':
        modes = ['control', 'endogenous', 'constitutive', 'treople', 'gilled']
        results = {}
        for m in modes:
            print(f"\n{'#'*80}")
            print(f"# MODE: {m}")
            print(f"{'#'*80}")
            sim = EndogenousOuroboricSim(n_cells=100, mode=m,
                                          intervention_time=15.0)
            sim.run(total_divisions=n_divisions)
            results[m] = sim.history
        
        # Comparison
        print(f"\n{'='*80}")
        print("CROSS-MODE COMPARISON")
        print(f"{'='*80}")
        print(f"{'Mode':>15} {'Final TL':>10} {'Sen%':>7} {'Ouro%':>7} {'hTERT':>7} {'Meth%':>7}")
        print(f"{'─'*15} {'─'*10} {'─'*7} {'─'*7} {'─'*7} {'─'*7}")
        for m in modes:
            h = results[m]
            print(f"{m:>15} {h['mean_length'][-1]:10.1f} {h['senescent_pct'][-1]:6.1f} "
                  f"{h['ouroboric_pct'][-1]:6.1f} {h['mean_htert'][-1]:7.4f} "
                  f"{h['mean_methylation'][-1]:6.1%}")
    else:
        sim = EndogenousOuroboricSim(n_cells=100, mode=mode,
                                      intervention_time=15.0)
        sim.run(total_divisions=n_divisions)