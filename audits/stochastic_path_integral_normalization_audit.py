"""Generate stochastic path-integral normalization audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_stochastic_path_integral_normalization import (  # noqa: E402
    export_stochastic_path_integral_outputs,
)


if __name__ == "__main__":
    export_stochastic_path_integral_outputs(ROOT)
