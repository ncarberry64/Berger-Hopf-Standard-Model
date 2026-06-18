"""Export the BHSM boundary projection-channel theorem sprint audit."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_projection_channels import (  # noqa: E402
    export_boundary_projection_channel_outputs,
)


if __name__ == "__main__":
    export_boundary_projection_channel_outputs(ROOT)
