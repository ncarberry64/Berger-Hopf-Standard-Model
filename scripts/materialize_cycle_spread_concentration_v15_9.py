"""Materialize the BHSM v15.9 spread-to-concentration calculation."""
from pathlib import Path

from bhsm.interface.aether_cycle_spread_concentration_v15_9 import materialize


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(materialize(root / "artifacts"))
