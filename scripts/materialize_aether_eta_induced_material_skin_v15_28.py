"""Materialize the BHSM v15.28 eta-induced material skin."""

from pathlib import Path

from bhsm.interface.aether_eta_induced_material_skin_v15_28 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
