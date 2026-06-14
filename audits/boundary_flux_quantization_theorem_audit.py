"""Export the BHSM boundary flux quantization theorem audit."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_flux_quantization import export_boundary_flux_outputs  # noqa: E402


if __name__ == "__main__":
    export_boundary_flux_outputs(ROOT)
