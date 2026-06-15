"""Generate Brownian generator topographic attractor audit artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_brownian_generator_topographic import export_brownian_generator_outputs  # noqa: E402


if __name__ == "__main__":
    export_brownian_generator_outputs(ROOT)
