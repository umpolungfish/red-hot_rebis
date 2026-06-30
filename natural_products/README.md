# Natural Products Collection

**What it is.** A consolidated collection of CDXML molecular structures for a set of named natural products, gathered from the former stub directories in red-hot_rebis.

**What it does.** Provides ready-to-use 2D chemical structures (one compound per subdirectory) as input for ch3mpiler retrosynthetic and structural-imscription analysis.

**Why it matters.** It is the shared substrate library for the red-hot_rebis chemistry pipeline: a single place to pull a known compound's structure rather than redrawing it per analysis.

**How to use it.**
```python
ch3mpiler.analyze('<compound_name>')   # structural imscription of any entry
```

---

## Inventory

CDXML structures for: Tetrodotoxin (`ttx/`, `tetrodo/`), Strychnine (`strychnine/`, `strych/`), Penicillin (`pen/`), Palytoxin/Ciguatoxin (`palc/`), Isopropyl Cyanide (`ipc/`), Anthracene (`anthracene/`), Acetaminophen (`aceta/`), and Caffeine (`caff/`). The `chlorophyll/` slot is a placeholder (empty).

All entries are CDXML molecular structures suitable for ch3mpiler retrosynthetic analysis.
