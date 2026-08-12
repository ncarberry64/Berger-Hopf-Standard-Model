"""Materialize deterministic BHSM v16.04 non-Abelian de Rham response."""

from pathlib import Path

from bhsm.interface.aether_nonabelian_derham_response_v16_04 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
