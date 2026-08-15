"""Materialize the BHSM sigma saturation and ejection audit."""

from pathlib import Path

from bhsm.interface.aether_sigma_saturation_ejection_v15_19 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
