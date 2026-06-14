"""Regenerate the charged-lepton dressing formula-integrity audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from charged_lepton_dressing_formula_integrity import export_formula_integrity_outputs


if __name__ == "__main__":
    export_formula_integrity_outputs()
