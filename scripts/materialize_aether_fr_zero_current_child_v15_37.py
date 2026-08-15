"""Materialize the deterministic BHSM v15.37 zero-current FR artifact."""

from pathlib import Path

from bhsm.interface.aether_fr_zero_current_child_v15_37 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
