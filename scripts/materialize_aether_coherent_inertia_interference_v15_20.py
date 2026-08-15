"""Materialize the BHSM coherent-inertia interference theorem."""

from pathlib import Path

from bhsm.interface.aether_coherent_inertia_interference_v15_20 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
