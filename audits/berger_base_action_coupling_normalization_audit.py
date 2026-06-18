"""Generate the Berger/base action-coupling normalization audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_berger_base_action_coupling import export_berger_base_action_coupling_outputs  # noqa: E402


if __name__ == "__main__":
    export_berger_base_action_coupling_outputs(ROOT)
