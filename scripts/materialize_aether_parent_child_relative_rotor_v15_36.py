"""Materialize the deterministic BHSM v15.36 relative-rotor artifact."""

from pathlib import Path

from bhsm.interface.aether_parent_child_relative_rotor_v15_36 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
