"""Materialize the v18.04 complete-child-gated N=3 promotion."""
from pathlib import Path

from bhsm.interface.aether_n3_second_refreshed_complete_child_promotion_v18_04 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
