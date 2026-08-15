"""Materialize deterministic BHSM v16.05 common gauge/HS pushforward."""

from pathlib import Path

from bhsm.interface.aether_common_gauge_hs_pushforward_v16_05 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
