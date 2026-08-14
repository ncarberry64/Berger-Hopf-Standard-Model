"""Materialize the v18.02 complete-child-gated N=3 promotion."""
from pathlib import Path

from bhsm.interface.aether_n3_refreshed_complete_child_promotion_v18_02 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
