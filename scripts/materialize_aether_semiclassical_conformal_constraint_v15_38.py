"""Materialize the deterministic BHSM v15.38 constraint artifact."""

from pathlib import Path

from bhsm.interface.aether_semiclassical_conformal_constraint_v15_38 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
