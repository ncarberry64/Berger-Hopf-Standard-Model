"""Materialize the BHSM v15.25 moving formed-branch theorem."""

from pathlib import Path

from bhsm.interface.aether_moving_formed_symplectic_v15_25 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
