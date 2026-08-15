"""Materialize the BHSM v15.13 boundary-identity/ejection theorem."""

from pathlib import Path

from bhsm.interface.aether_boundary_identity_ejection_v15_13 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
