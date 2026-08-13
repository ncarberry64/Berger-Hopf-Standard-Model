"""Materialize deterministic BHSM v16.10 boundary transversality."""

from pathlib import Path

from bhsm.interface.aether_n3_eta_boundary_transversality_v16_10 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
