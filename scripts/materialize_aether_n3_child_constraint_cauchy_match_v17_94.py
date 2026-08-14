"""Materialize the v17.94 seven-constraint child Cauchy match."""
from pathlib import Path

from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
