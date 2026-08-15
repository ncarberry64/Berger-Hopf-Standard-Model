"""Materialize the v17.95 admissible child Cauchy germ."""
from pathlib import Path

from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
