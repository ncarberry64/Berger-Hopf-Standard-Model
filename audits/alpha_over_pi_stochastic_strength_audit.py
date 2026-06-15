"""Generate alpha-over-pi stochastic strength audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_alpha_over_pi_stochastic_strength import export_alpha_over_pi_outputs  # noqa: E402


if __name__ == "__main__":
    export_alpha_over_pi_outputs(ROOT)
