"""Materialize the BHSM collective symplectic-manifold theorem."""

from pathlib import Path

from bhsm.interface.aether_collective_symplectic_manifold_v15_22 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
