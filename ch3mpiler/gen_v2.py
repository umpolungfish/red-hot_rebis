#!/usr/bin/env python3
"""Print the historical reaction-compiler header preview."""


def main():
    parts = ["#!/usr/bin/env python3", "# ch3mpiler v1.0 - Reaction Compiler", ""]
    for index, line in enumerate(parts):
        print(index, line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
