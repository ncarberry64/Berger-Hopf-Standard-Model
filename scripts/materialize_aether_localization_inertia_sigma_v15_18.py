"""Materialize the BHSM localization-inertia sigma theorem."""

from pathlib import Path

from bhsm.interface.aether_localization_inertia_sigma_v15_18 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
