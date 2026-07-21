"""Materialize BHSM v5.12 primordial boundary-tension artifacts."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.primordial_boundary_tension_action_source_closure import materialize_artifacts


def main() -> int:
    for path in materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
