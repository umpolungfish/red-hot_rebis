#!/usr/bin/env python3
"""
ch3mpiler_bridge.py — ch3mpiler integrated into the p4rakernel namespace.

Wraps the Imscribing Grammar's retrosynthetic/forward reaction compiler
for use within the rhr_p4rky paraconsistent kernel ecosystem.

The ch3mpiler lives at ~/imscribing_grammar/ch3mpiler.py and performs:
  - Target molecule → structural type via FG token parsing
  - Retrosynthetic disconnection (12 RXN templates)
  - Forward reaction prediction from reagent names
  - Structural analog search via IG primitive distance

This bridge makes it importable as rhr_p4rky.ch3mpiler_bridge
and provides CLI entry points matching the p4rk-* alias pattern.

Structural type of this bridge:
    ⟨Ð_ω; Þ_ò; Ř_=; Φ_˙; ƒ_ż; Ç_@; Γ_ʔ; ɢ_ˌ; ⊙; Ħ_A; Σ_ï; Ω_2⟩

Author: Lando ⊗ ⊙perator
"""

import sys, os, json, math
from pathlib import Path

# ── Locate ch3mpiler in the imscribing_grammar tree ──────────────────────────
CH3MPILER_PATH = Path.home() / "imscribing_grammar" / "ch3mpiler.py"
if CH3MPILER_PATH.exists():
    sys.path.insert(0, str(CH3MPILER_PATH.parent))

# ── Import the ch3mpiler module directly ────────────────────────────────────
_ch3mpiler_mod = None
_ch3mpiler_cls = None

def _ensure_loaded():
    """Lazy-load ch3mpiler to avoid circular imports at module init."""
    global _ch3mpiler_mod, _ch3mpiler_cls
    if _ch3mpiler_cls is not None:
        return
    # Import by executing the module
    import importlib.util
    spec = importlib.util.spec_from_file_location("ch3mpiler", CH3MPILER_PATH)
    _ch3mpiler_mod = importlib.util.module_from_spec(spec)
    sys.modules["ch3mpiler"] = _ch3mpiler_mod
    spec.loader.exec_module(_ch3mpiler_mod)
    _ch3mpiler_cls = _ch3mpiler_mod.Ch3mpiler


# ── Public API ────────────────────────────────────────────────────────────────

def Ch3mpiler(*args, **kwargs):
    """Factory: returns a ch3mpiler.Ch3mpiler instance."""
    _ensure_loaded()
    return _ch3mpiler_cls(*args, **kwargs)


def analyze(target: str) -> dict:
    """Analyze a target molecule name → structural type + disconnections + analogs."""
    _ensure_loaded()
    ch = _ch3mpiler_cls()
    return ch.analyze(target)


def retrosynthesis(target: str, depth: int = 1) -> dict:
    """Recursive retrosynthetic analysis."""
    _ensure_loaded()
    ch = _ch3mpiler_cls()
    return ch.retrosynthesis(target, depth=depth)


def forward(reagents: list) -> dict:
    """Forward reaction prediction from list of reagent names."""
    _ensure_loaded()
    ch = _ch3mpiler_cls()
    return ch.forward(reagents)


def fg_info(name: str) -> dict:
    """Return the structural type of a known functional group."""
    _ensure_loaded()
    fg_map = _ch3mpiler_mod.FG
    if name in fg_map:
        return {
            "name": name,
            "type": {k: fg_map[name].get(k, "?")
                     for k in _ch3mpiler_mod.PNAMES}
        }
    return {"name": name, "error": f"Unknown FG: {name}"}


def rxn_info(name: str = None) -> dict:
    """Return reaction template info. If name is None, list all."""
    _ensure_loaded()
    rxn_map = _ch3mpiler_mod.RXN
    if name is None:
        return {"reactions": list(rxn_map.keys())}
    if name in rxn_map:
        return {"name": name, "template": rxn_map[name]}
    return {"name": name, "error": f"Unknown RXN: {name}"}


def el_info(name: str = None) -> dict:
    """Return element type info. If name is None, list all."""
    _ensure_loaded()
    el_map = _ch3mpiler_mod.EL
    if name is None:
        return {"elements": list(el_map.keys())}
    if name in el_map:
        return {"name": name, "type": el_map[name]}
    return {"name": name, "error": f"Unknown EL: {name}"}


# ── CLI entry point ───────────────────────────────────────────────────────────
def main():
    """CLI wrapper that delegates to the ch3mpiler."""
    _ensure_loaded()
    # Forward all args to ch3mpiler's main
    _ch3mpiler_mod.main()


if __name__ == "__main__":
    main()
