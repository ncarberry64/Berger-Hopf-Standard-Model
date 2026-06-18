"""Export the BHSM sector projector operator construction audit."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_sector_projector_operator import (  # noqa: E402
    export_sector_projector_operator_outputs,
)


if __name__ == "__main__":
    export_sector_projector_operator_outputs(ROOT)
