"""Materialize deterministic BHSM v16.11 anchored replacement KKT seed."""

from pathlib import Path

from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
