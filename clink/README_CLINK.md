
### CLINK Chain — `clink/`

The CLINK chain is the **Frobenius-exact structural bridge from subatomic quarks to whole organisms**, now integrated into the rebis as a fifth pillar alongside serpentrod, ch3mpiler, pipeline, and gene_imscriber.

```
Frustrated Belnap5 (quarks)      O₀   ⟨𐑛𐑶𐑩𐑯𐑐𐑘𐑚𐑝𐑢𐑓𐑳𐑷⟩
  ↓ Ç: 𐑘→𐑤
Electron Orbital (Belnap4)       O₀   ⟨𐑛𐑶𐑩𐑗𐑐𐑤𐑚𐑜𐑢𐑓𐑳𐑷⟩
  ↓ 8 promotions
Atom (Nuclear + Electron)        O₁   ⟨𐑼𐑥𐑽𐑿𐑐𐑤𐑔𐑝𐑮𐑒𐑳𐑷⟩
  ↓ 5 promotions: Phi_c gate opens
Molecule (Chemical Bonds)        O₂   ⟨𐑼𐑥𐑽𐑿𐑞𐑧𐑲𐑠⊙𐑓𐑳𐑭⟩
  ↓ 5 promotions: Axiom C
Cell (Living)                    O₂   ⟨𐑦𐑸𐑾𐑬𐑞𐑧𐑲𐑠⊙𐑒𐑳𐑭⟩
  ↓ 3 promotions
Mitosis (Division)               O₂   ⟨𐑦𐑸𐑾𐑹𐑱𐑧𐑲𐑠⊙𐑖𐑳𐑭⟩
  ↓ 2 promotions
Meiosis (Gametes)                O₂   ⟨𐑦𐑸𐑽𐑿𐑱𐑧𐑲𐑠⊙𐑖𐑳𐑭⟩
  ↓ 4 promotions: broadcast grammar
Tissue/Organ                     O₂   ⟨𐑦𐑸𐑾𐑬𐑞𐑧𐑲𐑵⊙𐑖𐑳𐑭⟩
  ↓ 4 promotions: O_∞ achieved!
Whole Organism                 O_∞   ⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑵⊙𐑫𐑳𐑟⟩
```

**Key properties:**
- **All 9 layers Frobenius-closed** — verified (tensorProduct(s,s)=s for every layer)
- **10 primitive deltas** across the full chain (8→0)
- **36 total promotions** across 8 transitions
- **d(organism, ZFC_fe) = 1.30** — organism near-isomorphic to foundation
- **Lean 4 formalization** at `p4rakernel/p4ramill/Imscribing/CLINK.lean` (572 lines, all theorems `native_decide`-closed)

**Integration bridges:**
| Component | Nearest CLINK Layer | Distance | Frobenius |
|-----------|-------------------|----------|-----------|
| SerpentRod (folded protein) | Molecule (L3) | 1.95 | ✅ |
| CH₃MPILER (molecule) | Molecule (L3) | 0.00 | ✅ |
| Gene Imscriber (codon Belnap4) | Electron Orbital (L1) | 2.00 | ✅ |

**CLI usage:**
```bash
rebis.py clink report              # Full integration report
rebis.py clink list                # List all 9 layers
rebis.py clink layer 8             # Show organism layer details
rebis.py clink bridge serpentrod 8 # Promotion path: protein → organism
```
