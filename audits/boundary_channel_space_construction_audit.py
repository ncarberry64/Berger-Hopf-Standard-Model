"""Export the BHSM boundary channel-space construction audit."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_channel_space import export_boundary_channel_space_outputs  # noqa: E402


if __name__ == "__main__":
    export_boundary_channel_space_outputs(ROOT)
