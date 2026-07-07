#!/usr/bin/env python3
"""
rebis.verify_entry — CL entry point for rebis.verify
Frobenius closure verification
"""
import sys

from rebis.file_input import add_file_input


def main():
    import argparse
    parser = argparse.ArgumentParser(prog="rebis.verify")
    add_file_input(parser)
    args = parser.parse_args()
    from rebis.cli import cmd_verify
    return cmd_verify(args)


if __name__ == "__main__":
    sys.exit(main())