"""Materialize the BHSM coupled-skin selector theorem."""

from pathlib import Path

from bhsm.interface.aether_coupled_skin_selector_v15_16 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
