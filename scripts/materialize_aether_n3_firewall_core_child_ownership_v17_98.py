"""Materialize the v17.98 firewall core ownership audit."""
from pathlib import Path

from bhsm.interface.aether_n3_firewall_core_child_ownership_v17_98 import (
    materialize,
)


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
