"""Materialize the v18.00 complete-child merit promotion."""
from pathlib import Path

from bhsm.interface.aether_n3_complete_child_merit_promotion_v18_00 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
