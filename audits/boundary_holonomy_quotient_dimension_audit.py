"""Generate boundary holonomy quotient dimension audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_holonomy_dimension import export_boundary_holonomy_dimension_outputs  # noqa: E402


if __name__ == "__main__":
    export_boundary_holonomy_dimension_outputs(ROOT)
