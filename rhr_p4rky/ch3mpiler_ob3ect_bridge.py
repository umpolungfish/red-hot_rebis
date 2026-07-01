#!/usr/bin/env python3
"""p4rakernel bridge — ch3mpiler ob3ect self-verification bridge.

Usage:
  python3 -m rhr_p4rky.ch3mpiler_ob3ect_bridge        # Run verification
  python3 -m rhr_p4rky.ch3mpiler_ob3ect_bridge --quiet  # Just return code
"""
_HELP_EXAMPLES = """  rebis.py run ch3mpiler_ob3ect_bridge"""
import sys as _sys
_HELP_ARGS = set(_sys.argv[1:])

if __name__ == "__main__":
    if '--help' in _HELP_ARGS or '-h' in _HELP_ARGS:
        _doc = __doc__.strip() if __doc__ else "rhr_p4rky/ch3mpiler_ob3ect_bridge.py"
        print(_doc)
        print()
        print("Examples:")
        print(_HELP_EXAMPLES)
        print()
        _sys.exit(0)

import sys
from pathlib import Path
from shared.rich_output import *

# Add ob3ect/digital to path — ch3mpiler_ob3ect.py lives there
OB3ECT_PATH = str(Path.home() / "ob3ect/digital")
sys.path.insert(0, OB3ECT_PATH)

def run_verify(quiet=False):
    try:
        from ch3mpiler_ob3ect import Ch3mpilerOb3ect

    except ModuleNotFoundError:
        if not quiet:
            info_line("ch3mpiler_ob3ect: module not found at ob3ect/digital/ch3mpiler_ob3ect")
            info_line("Bridge unavailable — ob3ect integration not yet built")
        return 1
    ob3ect = Ch3mpilerOb3ect()
    closure = ob3ect.verify(verbose=not quiet)
    if not quiet:
        info_line(f"Closure: {closure}")
    return 0 if closure else 1
if __name__ == "__main__":
    quiet = "--quiet" in sys.argv
    sys.exit(run_verify(quiet=quiet))
