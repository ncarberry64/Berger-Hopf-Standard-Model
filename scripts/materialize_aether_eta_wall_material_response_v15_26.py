"""Materialize the BHSM v15.26 eta-wall material-response completion."""

from pathlib import Path

from bhsm.interface.aether_eta_wall_material_response_v15_26 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
