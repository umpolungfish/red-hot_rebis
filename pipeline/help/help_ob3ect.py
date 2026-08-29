#!/usr/bin/env python3
"""
--help

Auto-imscribed on 2026-08-28
"""
import os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frob import identity_phase
from shared.rich_output import *

class helpOb3ect:
    def __init__(self):
        self.source = pathlib.Path(__file__).read_text()

    def verify(self) -> bool:
        info_line(f"=== {self.__class__.__name__} ===")
        frob_ok = identity_phase(self.source)
        success_line(f"Closure: {frob_ok}")
        return frob_ok

if __name__ == "__main__":
    sys.exit(0 if helpOb3ect().verify() else 1)
