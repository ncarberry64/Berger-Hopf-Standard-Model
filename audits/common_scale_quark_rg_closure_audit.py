"""Regenerate the common-scale quark RG closure audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from common_scale_quark_rg_closure import export_common_scale_quark_rg_closure_outputs


if __name__ == "__main__":
    export_common_scale_quark_rg_closure_outputs()
