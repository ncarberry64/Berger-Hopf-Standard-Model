"""Materialize deterministic BHSM v10.0 envelopment artifacts."""

from pathlib import Path

from bhsm.interface.envelopment import materialize


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    for path in materialize(ROOT):
        print(path.relative_to(ROOT).as_posix())
