#!/usr/bin/env python3
"""
_quick_help.py — Drop-in --help support for any standalone script.
Import and call at the top of if __name__ == '__main__':

    import sys
    if '--help' in sys.argv or '-h' in sys.argv:
        from _quick_help import show; show(__doc__, EXAMPLES); sys.exit(0)

Where EXAMPLES is a multi-line string of usage examples.
"""
import sys
import os
from shared.rich_output import *



def show(docstring, examples=""):
    """Print help from a module's __doc__ and an examples string."""
    if docstring:
        for line in docstring.strip().split('\n'):
            print(line.strip())
    print()
    if examples:
        info_line("Examples:")
        for line in examples.strip().split('\n'):
            print(line)
    else:
        info_line(f"Usage:  python3 {os.path.basename(sys.argv[0])} [args...]")
    print()
