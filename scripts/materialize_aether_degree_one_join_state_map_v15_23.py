"""Materialize the BHSM v15.23 degree-one join reduction."""

from pathlib import Path

from bhsm.interface.aether_degree_one_join_state_map_v15_23 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
