"""Materialize the BHSM v15.12 moving-interface theorem."""

from pathlib import Path

from bhsm.interface.aether_moving_interface_transfer_v15_12 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
