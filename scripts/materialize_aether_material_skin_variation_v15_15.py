"""Materialize the BHSM material-skin variation theorem."""

from pathlib import Path

from bhsm.interface.aether_material_skin_variation_v15_15 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
