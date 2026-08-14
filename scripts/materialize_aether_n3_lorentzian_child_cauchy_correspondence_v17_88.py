"""Materialize the v17.88 Lorentzian event-to-child correspondence."""
from pathlib import Path

from bhsm.interface.aether_n3_lorentzian_child_cauchy_correspondence_v17_88 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
