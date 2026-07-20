"""Materialize BHSM v5.6 scalar/topographic vacuum action artifacts."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.scalar_topographic_vacuum_action import materialize_artifacts


def main() -> int:
    for path in materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
