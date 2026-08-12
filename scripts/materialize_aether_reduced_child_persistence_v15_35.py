"""Materialize the deterministic BHSM v15.35 persistence artifact."""

from pathlib import Path

from bhsm.interface.aether_reduced_child_persistence_v15_35 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
