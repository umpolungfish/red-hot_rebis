"""Repair the historical reaction-pipeline fragment hook."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline._scaffold_patch import repair_source, main as _main


def main(argv=None):
    return _main(argv, include_metadata=True)


if __name__ == '__main__':
    raise SystemExit(main())
