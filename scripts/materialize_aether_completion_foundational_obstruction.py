"""Materialize the BHSM foundational completion obstruction."""

from pathlib import Path

from bhsm.interface.aether_completion_foundational_obstruction import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
