"""Regenerate the common-scale light-up ratio tension audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from light_up_ratio_tension import export_light_up_ratio_tension_outputs


if __name__ == "__main__":
    export_light_up_ratio_tension_outputs()
