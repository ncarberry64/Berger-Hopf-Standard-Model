"""Generate identity/traceless stochastic protection audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_identity_traceless_stochastic import export_identity_traceless_stochastic_outputs  # noqa: E402


if __name__ == "__main__":
    export_identity_traceless_stochastic_outputs(ROOT)
