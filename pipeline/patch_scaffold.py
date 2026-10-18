"""Repair historical scaffold setup without import-time writes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline._scaffold_setup_patch import repair_setup as repair_source
from pipeline._scaffold_patch import main as _main


def main(argv=None):
    return _main(argv, repairer=repair_source)


if __name__ == '__main__':
    raise SystemExit(main())
