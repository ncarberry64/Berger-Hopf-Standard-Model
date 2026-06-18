"""Generate full BHSM candidate theory-line catch-up artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_full_theory_line_catchup import export_full_theory_line_outputs  # noqa: E402


if __name__ == "__main__":
    export_full_theory_line_outputs(ROOT)
