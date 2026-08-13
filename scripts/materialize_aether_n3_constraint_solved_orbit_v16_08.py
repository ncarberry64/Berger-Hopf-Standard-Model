"""Materialize deterministic BHSM v16.08 independent N=3 orbit witness."""

from pathlib import Path

from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
