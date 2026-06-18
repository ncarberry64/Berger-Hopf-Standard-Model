"""Generate the topographic-attractor boundary-action bridge audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_topographic_attractor_bridge import (  # noqa: E402
    export_topographic_attractor_bridge_outputs,
)


if __name__ == "__main__":
    export_topographic_attractor_bridge_outputs(ROOT)
