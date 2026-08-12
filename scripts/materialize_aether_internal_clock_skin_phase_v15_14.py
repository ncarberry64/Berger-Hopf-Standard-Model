"""Materialize the BHSM internal-clock/skin-phase theorem."""

from pathlib import Path

from bhsm.interface.aether_internal_clock_skin_phase_v15_14 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
