"""Materialize the v18.03 refreshed complete-merit Newton candidate."""
from pathlib import Path

from bhsm.interface.aether_n3_second_refreshed_complete_merit_newton_v18_03 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
