"""Materialize the v17.93 required child Cauchy flux map."""
from pathlib import Path

from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
