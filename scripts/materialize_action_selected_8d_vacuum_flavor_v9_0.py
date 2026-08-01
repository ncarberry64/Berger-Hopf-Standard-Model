"""Materialize the integrated BHSM v8.4--v9.0 deterministic artifacts."""

from pathlib import Path

from bhsm.interface.master_action.eight_dimensional_vacuum_flavor_completion import (
    materialize,
)


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    for path in materialize(ROOT):
        print(path.relative_to(ROOT).as_posix())
