"""Materialize the v17.90 dynamic event-to-child Cauchy law."""
from pathlib import Path

from bhsm.interface.aether_n3_dynamic_child_wentzell_cauchy_v17_90 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
