#!/usr/bin/env python3
"""
Antibody Designer v2 — CLI wrapper for the fixed antibody design pipeline.

Delegates to rhr_p4rky.antibody_designer for all design logic.
Provides a simpler CLI with the same options.

Author: Lando ⊗ ⊙perator
"""

import sys, os

REBIS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REBIS_ROOT)

from rhr_p4rky.antibody_designer import main as antibody_main

if __name__ == "__main__":
    sys.exit(antibody_main())
