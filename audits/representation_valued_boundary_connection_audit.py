"""Generate the representation-valued boundary connection audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_representation_boundary_connection import (  # noqa: E402
    export_representation_boundary_connection_outputs,
)


if __name__ == "__main__":
    export_representation_boundary_connection_outputs(ROOT)
