"""Materialize the BHSM v15.10 sigma-coefficient response audit."""

from pathlib import Path

from bhsm.interface.aether_cycle_sigma_coefficient_reconstruction_v15_10 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
