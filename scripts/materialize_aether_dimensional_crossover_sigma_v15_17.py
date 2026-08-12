"""Materialize the BHSM dimensional-crossover sigma audit."""

from pathlib import Path

from bhsm.interface.aether_dimensional_crossover_sigma_v15_17 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
