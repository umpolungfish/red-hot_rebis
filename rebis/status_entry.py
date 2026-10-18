#!/usr/bin/env python3
"""
rebis.status_entry — CL entry point for rebis.status
"""
import sys

from rebis.file_input import parse_with_file


def main():
    import argparse
    parser = argparse.ArgumentParser(prog="rebis.status")
    args = parse_with_file(parser)
    from rebis.cli import cmd_status
    return cmd_status(args)


if __name__ == "__main__":
    sys.exit(main())