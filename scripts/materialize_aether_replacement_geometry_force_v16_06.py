"""Materialize deterministic BHSM v16.06 replacement geometry force."""

from pathlib import Path

from bhsm.interface.aether_replacement_geometry_force_v16_06 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
