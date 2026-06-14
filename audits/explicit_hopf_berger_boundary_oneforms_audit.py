"""Generate the explicit Hopf/Berger boundary one-form audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_hopf_berger_oneforms import export_explicit_hopf_berger_oneform_outputs  # noqa: E402


if __name__ == "__main__":
    export_explicit_hopf_berger_oneform_outputs(ROOT)
