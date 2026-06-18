"""Generate physical boundary channel-space identification audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_physical_boundary_channel_space import export_physical_channel_space_outputs  # noqa: E402


if __name__ == "__main__":
    export_physical_channel_space_outputs(ROOT)
