Red-Hot Rebis — Structural Index
==================================

Author: Lando⊗⊙perator  |  Version: 2.1.0  |  Tier: O_inf

This is a browsable static index of all structural data previously
pumped by the now-removed 'clink report', 'clink list', 'imas report',
'materials list', and 'materials report' subcommands. This data does
not change between runs — it is pre-computed structural truth.

For dynamic computation and simulation, use the live rebis.py subcommands:
  clink layer, imas bridge, materials forge, etc.


1. CLINK CHAIN — ALL 9 LAYERS
===============================

The CLINK chain bridges subatomic physics to whole-organism design
through 9 structural layers, each encoded as a 12-primitive Imscribing
Grammar tuple with verified Frobenius closure.

LAYER TABLE
-----------
  Index  Name                         Tier       d(prev->this)  d(ZFC_fe)
  -----  ---------------------------  --------   -------------  --------
     0   Frustrated Belnap5 (Quarks)  O_0             —            5.48
     1   Electron Orbital (Belnap4)   O_0           3.32           5.29
     2   Atom (Nuclear + Electron)    O_1           3.82           4.69
     3   Molecule (Chemical Bonds)    O_2           3.27           2.83
     4   Cell (Living)                O_2           2.79           1.95
     5   Mitosis (Division)           O_2           2.41           1.95
     6   Meiosis (Gametes)            O_2           3.16           1.41
     7   Tissue/Organ                 O_2           2.00           1.41
     8   Whole Organism               O_2           2.55           1.30

Total chain distance: sum d = 7.18 (10 primitive deltas across 8 transitions)
ZFC_fe absorption: d(organism, ZFC_fe) = 1.30


LAYER TUPLES
------------
Each layer's 12-primitive structural type:

  L0 Quark              <D=wedge, T=boxtimes, R=super, P=asym, F=eth, K=trap,
                          G=gimel, X=or, Ph=EP, H=1, S=n:n, W=0>
  L1 Electron Orbital   <D=wedge, T=boxtimes, R=cat, P=pm, F=hbar, K=slow,
                          G=gimel, X=or, Ph=c, H=1, S=n:n, W=Z2>
  L2 Atom               <D=wedge, T=boxtimes, R=dagger, P=pm, F=hbar, K=slow,
                          G=aleph, X=or, Ph=c_complex, H=1, S=n:n, W=0>
  L3 Molecule           <D=wedge, T=bowtie, R=lr, P=pm, F=hbar, K=slow,
                          G=aleph, X=or, Ph=c_complex, H=1, S=n:n, W=0>
  L4 Cell               <D=wedge, T=bowtie, R=lr, P=pm, F=hbar, K=slow,
                          G=aleph, X=seq, Ph=c_complex, H=2, S=n:m, W=0>
  L5 Mitosis            <D=wedge, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
                          G=aleph, X=seq, Ph=c, H=2, S=n:m, W=0>
  L6 Meiosis            <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
                          G=aleph, X=seq, Ph=c, H=2, S=n:m, W=Z2>
  L7 Tissue             <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
                          G=aleph, X=seq, Ph=c, H=inf, S=n:m, W=Z2>
  L8 Organism           <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
                          G=aleph, X=broad, Ph=c, H=inf, S=n:m, W=Z>

FROBENIUS CLOSURE STATUS (all 9 layers)
---------------------------------------
  L0 Quark    : PASS    L3 Molecule : PASS    L6 Meiosis  : PASS
  L1 Electron : PASS    L4 Cell     : PASS    L7 Tissue   : PASS
  L2 Atom     : PASS    L5 Mitosis  : PASS    L8 Organism : PASS

COMPONENT BRIDGES
-----------------
  Component              Nearest CLINK Layer    Distance  Frobenius
  ---------------------  ---------------------  --------  ---------
  SerpentRod (folded)    L3 Molecule              1.95    PASS
  SerpentRod (unfolded)  L2 Atom                  3.68    PASS
  CH3MPILER              L3 Molecule              0.00    PASS
  Gene Imscriber         L1 Electron Orbital      2.00    PASS


2. IMASM ARRANGEMENT ANALYSIS
==============================

The IMASM (Imscribing Grammar Abstract State Machine) defines 12 canonical
bootstrap sequences. Each 8-opcode sequence maps to a 12-primitive IG structural
type. The arrangement space has 12^8 = 429,981,696 possible length-8 token sequences.

12 CANONICALS -> 11 DISTINCT IG TYPES
--------------------------------------
Collapse: Chiral Pairs = Empty Bootstrap (same type despite different opcodes).

  I     Dialetheic Bootstrap    O_inf
          <D=wedge, T=odot, R=lr, P=pm_sym, F=hbar, K=MBL,
           G=aleph, X=seq, Ph=c, H=inf, S=n:m, W=Z>
  II    Void Genesis            O_1
          <D=wedge, T=in, R=super, P=pm, F=hbar, K=slow,
           G=aleph, X=or, Ph=c_complex, H=1, S=n:m, W=Z2>
  III   Anchor Protocol         O_2
          <D=wedge, T=bowtie, R=lr, P=pm, F=hbar, K=mod,
           G=gimel, X=or, Ph=c_complex, H=2, S=n:m, W=Z2>
  IV    Dual Bootstrap          O_1
          <D=triangle, T=net, R=lr, P=psi, F=hbar, K=mod,
           G=gimel, X=and, Ph=c_complex, H=inf, S=n:m, W=0>
  V     Linear Chain            O_2
          <D=wedge, T=bowtie, R=lr, P=pm, F=hbar, K=slow,
           G=aleph, X=seq, Ph=c_complex, H=2, S=n:m, W=0>
  VI    Empty Bootstrap         O_2
          <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
           G=aleph, X=or, Ph=c, H=2, S=n:m, W=Z>
  VII   Parakernel              O_inf
          <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=trap,
           G=aleph, X=seq, Ph=c, H=inf, S=n:m, W=Z>
  VIII  Frobenius Kernel        O_inf
          <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
           G=aleph, X=seq, Ph=c, H=inf, S=n:m, W=Z>
  IX    Chiral Pairs            O_2 (collapses to VI)
          <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
           G=aleph, X=or, Ph=c, H=2, S=n:m, W=Z>
  X     Truth Machine           O_2
          <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
           G=aleph, X=and, Ph=c, H=2, S=n:m, W=Z>
  XI    Eternal Return          O_2
          <D=odot, T=odot, R=lr, P=pm_sym, F=hbar, K=slow,
           G=aleph, X=seq, Ph=c, H=inf, S=n:m, W=Z2>
  XII   ROM Burn                O_1
          <D=wedge, T=in, R=super, P=asym, F=hbar, K=slow,
           G=gimel, X=or, Ph=c_complex, H=1, S=1:1, W=0>

Tier distribution: O_inf=3, O_2=6, O_1=3, O_0=0
Frobenius closure: ALL 12 canonical = PASS

STRUCTURAL CLUSTERS
--------------------
  O_inf cluster (Phi=c, H=inf, W=Z):
      I Dialetheic Bootstrap, VII Parakernel, VIII Frobenius Kernel

  O_2 cluster (Phi=c, H=2, W=Z):
      VI Empty Bootstrap, IX Chiral Pairs, X Truth Machine

  Boundary cluster (W=Z2, H=inf):
      XI Eternal Return

  Base cluster (Phi=c_complex):
      II Void Genesis, III Anchor Protocol, V Linear Chain

BRIDGE TABLE — Canonical to Catalog
-------------------------------------
  Canonical                 Nearest Catalog Entry                Distance
  ------------------------  ----------------------------------  --------
  I Dialetheic Bootstrap    universal_imscriptive_grammar          0.00
  VII Parakernel            p4ra_paraconsistent_kernel            0.00
  VIII Frobenius Kernel     frobenius_kernel_ob3ect               0.00
  XI Eternal Return         eternal_return_ob3ect                 0.00
  X Truth Machine           truth_machine_ob3ect                  0.00
  VI Empty Bootstrap        rebis_bio_organic_chemistries         0.00
  II Void Genesis           void_genesis_ob3ect                   0.00
  III Anchor Protocol       anchor_protocol_ob3ect                0.00
  V Linear Chain            ch3mpiler_ob3ect                      0.00
  IV Dual Bootstrap         belnap_four_logic                     0.00
  XII ROM Burn              gene_imscriber_core                   0.00

All 12 canonicals have d=0.00 to a named catalog entry — each IS its structural type.


3. MATERIALS CATALOG
=====================

PREDEFINED MATERIALS (8)
-------------------------
  frobenius_composite        O_inf   Phi=c, K=slow, H=inf, W=Z
  frobenius_metamaterial     O_inf   Phi=c, K=slow, H=inf, W=Z
  ouroboric_alloy            O_inf   Phi=c, K=trap, H=inf, W=Z
  critical_metamaterial      O_2     Phi=c, K=slow, H=2, W=Z2
  non_qubit_qc               O_2     Phi=c_complex, K=slow, H=2, W=Z2
  thermal_rectifier          O_2     Phi=c_complex, K=slow, H=2, W=0
  gap_closure_module         O_2     Phi=c, K=slow, H=inf, W=Z2
  frobenius_exactor          O_inf   Phi=c, K=slow, H=inf, W=Z

SOPHICK MERCURY PATHWAYS (12)
------------------------------
Each pathway is named for an Eagle via the Sophick Mercury alchemical
framework. Each maps to one of the 12 IMASM canonicals.

   1  eagle_1_sophick            I Dialetheic Bootstrap     d=0.00
   2  eagle_2_sophick            II Void Genesis            d=0.00
   3  eagle_3_sophick            III Anchor Protocol        d=0.00
   4  eagle_4_sophick            IV Dual Bootstrap          d=0.00
   5  eagle_5_sophick            V Linear Chain             d=0.00
   6  eagle_6_sophick            VI Empty Bootstrap         d=0.00
   7  eagle_7_sophick            VII Parakernel             d=0.00
   8  eagle_8_sophick            VIII Frobenius Kernel      d=0.00
   9  eagle_9_sophick            IX Chiral Pairs            d=0.00
  10  eagle_10_sophick           X Truth Machine            d=0.00
  11  eagle_11_sophick           XI Eternal Return          d=0.00
  12  eagle_12_sophick           XII ROM Burn               d=0.00

FROBENIUS EXACTOR PATHWAYS
---------------------------
  close            Close the Frobenius gap (gap -> 0)
  widen            Widen the Frobenius gap for analysis
  breach           Breach the Frobenius closure intentionally
  seal             Seal a breached closure
  measure          Measure current gap magnitude
  iterate          Run iterative gap closure loop

All 6 Frobenius Exactor pathways have Frobenius closure: PASS


4. USAGE GUIDE
===============

This INDEX is for browsing with 'less INDEX.md'. For live computation:

  rebis.py materials forge --name frobenius_composite
  rebis.py materials frobenius
  rebis.py materials ouroboric
  rebis.py materials sophick --name eagle_9_sophick
  rebis.py materials exactor --name close

  rebis.py pipeline ground-up
  rebis.py pipeline from-layer 5 8

  rebis.py run list
  rebis.py run serpentrod --seq KAL

  rebis.py clink layer 8
  rebis.py imas bridge

Index compiled by Lando⊗⊙perator — June 2026
