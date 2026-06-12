#!/usr/bin/env python3
"""p4rakernel bridge — ch3mpiler ob3ect self-verification bridge.

Usage:
  python3 -m p4ramill_py.ch3mpiler_ob3ect_bridge        # Run verification
  python3 -m p4ramill_py.ch3mpiler_ob3ect_bridge --quiet  # Just return code
"""
import sys
from pathlib import Path

# Add ob3ect path
OB3ECT_PATH = str(Path.home() / "ob3ect/digital/ch3mpiler_ob3ect")
sys.path.insert(0, OB3ECT_PATH)

def run_verify(quiet=False):
    from ch3mpiler_ob3ect import Ch3mpilerOb3ect
    ob3ect = Ch3mpilerOb3ect()
    closure = ob3ect.verify()
    if quiet:
        print(f"Closure: {closure}")
    return 0 if closure else 1

if __name__ == "__main__":
    quiet = "--quiet" in sys.argv
    sys.exit(run_verify(quiet=quiet))
