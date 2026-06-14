"""Regenerate the BHSM completion manual theory-delta audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_completion_manual_theory_delta import export_manual_theory_delta_outputs


if __name__ == "__main__":
    export_manual_theory_delta_outputs()
