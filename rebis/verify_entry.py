#!/usr/bin/env python3
"""
rebis.verify_entry — CL entry point for rebis.verify
Package import verification
"""
import sys

from rebis.file_input import parse_with_file


def main():
    import argparse
    parser = argparse.ArgumentParser(prog="rebis.verify")
    args = parse_with_file(parser)
    from rebis.cli import cmd_verify
    return cmd_verify(args)


if __name__ == "__main__":
    sys.exit(main())