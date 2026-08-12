"""Materialize the BHSM formation-imbalance equivariance audit."""

from pathlib import Path

from bhsm.interface.aether_formation_imbalance_equivariance import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
