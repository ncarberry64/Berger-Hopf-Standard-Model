"""Materialize the v17.96 scalar complete-child boundary solution."""
from pathlib import Path

from bhsm.interface.aether_n3_scalar_complete_child_boundary_solution_v17_96 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
