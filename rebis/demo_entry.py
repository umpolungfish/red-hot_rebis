#!/usr/bin/env python3
"""
rebis.demo_entry — CL entry point for rebis.demo
"""
import argparse
import sys
from rebis.file_input import parse_with_file


def main():
    parser = argparse.ArgumentParser(
        prog="rebis.demo",
        description="Run a named demo from rebis.demo module")
    parser.add_argument("demo", nargs="?", default="list",
                        help="Demo name (or 'list' to see options)")
    args = parse_with_file(parser)

    from rebis.cli import cmd_demo
    return cmd_demo(args)


if __name__ == "__main__":
    sys.exit(main())