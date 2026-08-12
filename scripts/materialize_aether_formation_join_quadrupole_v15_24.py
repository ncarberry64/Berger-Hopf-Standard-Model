"""Materialize the BHSM v15.24 formation-to-join quadrupole bridge."""

from pathlib import Path

from bhsm.interface.aether_formation_join_quadrupole_v15_24 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
