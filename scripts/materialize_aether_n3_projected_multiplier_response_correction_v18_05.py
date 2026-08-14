"""Materialize the v18.05 projected-multiplier response correction."""
from pathlib import Path

from bhsm.interface.aether_n3_projected_multiplier_response_correction_v18_05 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
