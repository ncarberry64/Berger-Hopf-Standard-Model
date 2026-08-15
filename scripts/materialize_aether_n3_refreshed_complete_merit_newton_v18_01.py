"""Materialize the v18.01 refreshed complete-merit Newton step."""
from pathlib import Path

from bhsm.interface.aether_n3_refreshed_complete_merit_newton_v18_01 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
