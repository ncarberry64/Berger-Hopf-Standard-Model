"""Materialize deterministic BHSM v16.03 non-Abelian coexact vertices."""

from pathlib import Path

from bhsm.interface.aether_nonabelian_coexact_vertex_v16_03 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
