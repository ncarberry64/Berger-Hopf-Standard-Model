"""Export the BHSM sector-projector SM-ledger derivation audit."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_sector_projectors import export_sector_projector_outputs  # noqa: E402


if __name__ == "__main__":
    export_sector_projector_outputs(ROOT)
