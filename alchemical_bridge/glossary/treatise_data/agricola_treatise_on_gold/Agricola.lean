/-
# Joannes Agricola — Treatise on Gold
## Lean 4 Companion

Author: Lando⊗⊙perator
Date: 2026-06-25
Tuple: ⟨𐑨𐑡𐑩𐑿𐑞𐑧𐑲𐑜𐑢𐑒𐑳𐑷⟩
Tier: O₀
-/

import Primitives.Core
import Primitives.Imscription

open Primitives

def agricola_treatise_on_gold : Imscription :=
  { Ð := .D_triangle
    Þ := .T_net
    Ř := .R_super
    Φ := .P_psi
    ƒ := .F_eth
    Ç := .K_slow
    Γ := .G_beth
    ɢ := .Gm_or
    φ̂ := .Phi_sub
    Ħ := .H1
    Σ := .S_n_m
    Ω := .Omega_0
  }

#eval agricola_treatise_on_gold

def tier : String := "O₀"
