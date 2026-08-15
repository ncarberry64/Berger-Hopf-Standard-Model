"""Materialize the deterministic BHSM v15.40 response-constraint artifact."""

from pathlib import Path

from bhsm.interface.aether_eta_sigma_response_constraint_v15_40 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
