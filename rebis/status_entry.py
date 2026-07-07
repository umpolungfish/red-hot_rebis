#!/usr/bin/env python3
"""
rebis.status_entry — CL entry point for rebis.status
"""
import sys

from rebis.file_input import add_file_input


def main():
    import argparse
    parser = argparse.ArgumentParser(prog="rebis.status")
    add_file_input(parser)
    args = parser.parse_args()
    from rebis.cli import cmd_status
    return cmd_status(args)


if __name__ == "__main__":
    sys.exit(main())