"""Materialize the v17.97 zero-background Calderon closure."""
from pathlib import Path

from bhsm.interface.aether_n3_zero_background_calderon_closure_v17_97 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
