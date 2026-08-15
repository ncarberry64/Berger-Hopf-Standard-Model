"""Materialize deterministic BHSM v16.01 rank-16 vertex matrices."""

from pathlib import Path

from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import materialize


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    print(materialize(repository / "artifacts"))
