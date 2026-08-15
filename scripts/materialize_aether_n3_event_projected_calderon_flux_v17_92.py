"""Materialize the v17.92 projected event Calderon flux."""
from pathlib import Path

from bhsm.interface.aether_n3_event_projected_calderon_flux_v17_92 import materialize


if __name__ == "__main__":
    print(materialize(Path("artifacts")))
