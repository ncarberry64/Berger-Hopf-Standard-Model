"""Regenerate the charged-lepton eta_l derivation audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from charged_lepton_eta_derivation import export_eta_derivation_outputs


if __name__ == "__main__":
    export_eta_derivation_outputs()
