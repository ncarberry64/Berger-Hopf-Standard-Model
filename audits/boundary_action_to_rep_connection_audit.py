"""Generate the boundary-action-to-representation-connection audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_action_to_rep_connection import (  # noqa: E402
    export_boundary_action_outputs,
)


if __name__ == "__main__":
    export_boundary_action_outputs(ROOT)
