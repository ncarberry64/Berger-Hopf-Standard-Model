"""Materialize the deterministic BHSM v15.99 source-response artifact."""

from pathlib import Path

from bhsm.interface.aether_common_source_frechet_response_v15_99 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
