"""Materialize the deterministic BHSM v15.34 child-Routhian artifact."""

from pathlib import Path

from bhsm.interface.aether_complete_child_localized_fiber_v15_34 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
