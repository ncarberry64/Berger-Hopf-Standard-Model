"""Regenerate the charged-lepton precision dressing candidate audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from charged_lepton_precision_closure import export_charged_lepton_precision_outputs


if __name__ == "__main__":
    export_charged_lepton_precision_outputs()
