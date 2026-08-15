"""Materialize the deterministic BHSM v15.39 mathematical system."""

from pathlib import Path

from bhsm.interface.bhsm_complete_child_mathematical_system_v15_39 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
