"""Export the BHSM boundary connection holonomy construction audit."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_connection_holonomy import export_boundary_connection_outputs  # noqa: E402


if __name__ == "__main__":
    export_boundary_connection_outputs(ROOT)
