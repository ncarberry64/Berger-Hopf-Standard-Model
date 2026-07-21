"""Materialize BHSM v6.0.2 B8 geometry-energy action artifacts."""

from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))

from bhsm.interface.b8_geometry_energy_parent_action import materialize_artifacts


def main() -> int:
    for path in materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__=="__main__":
    raise SystemExit(main())
