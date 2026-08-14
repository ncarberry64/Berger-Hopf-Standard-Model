"""Materialize the v17.99 complete-child persistence witness."""
from pathlib import Path

from bhsm.interface.aether_n3_complete_child_persistence_v17_99 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
