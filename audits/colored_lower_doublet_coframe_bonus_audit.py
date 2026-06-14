"""Export the BHSM colored lower-doublet coframe bonus audit."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_colored_lower_doublet_projector import export_colored_lower_outputs  # noqa: E402


if __name__ == "__main__":
    export_colored_lower_outputs(ROOT)
