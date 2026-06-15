"""Generate charged-lepton partial derivation consolidation artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_charged_lepton_consolidation import (  # noqa: E402
    export_charged_lepton_consolidation_outputs,
)


if __name__ == "__main__":
    export_charged_lepton_consolidation_outputs(ROOT)
