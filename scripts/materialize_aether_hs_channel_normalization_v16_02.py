"""Materialize the deterministic BHSM v16.02 HS normalization artifact."""

from pathlib import Path

from bhsm.interface.aether_hs_channel_normalization_v16_02 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
