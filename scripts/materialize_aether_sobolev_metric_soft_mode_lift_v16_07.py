"""Materialize deterministic BHSM v16.07 Sobolev-metric soft-mode lift."""

from pathlib import Path

from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
