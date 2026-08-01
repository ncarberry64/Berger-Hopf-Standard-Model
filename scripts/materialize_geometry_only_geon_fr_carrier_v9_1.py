"""Materialize the deterministic BHSM v9.1 geometry-only audit."""

from pathlib import Path

from bhsm.interface.master_action.geometry_only_geon_fr_carrier_completion import (
    materialize,
)


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    for path in materialize(ROOT):
        print(path.relative_to(ROOT).as_posix())
