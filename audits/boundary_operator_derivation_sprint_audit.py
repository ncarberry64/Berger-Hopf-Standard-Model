"""Regenerate the focused boundary-operator derivation sprint audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from boundary_operator_derivation_sprint import export_boundary_operator_derivation_sprint_outputs


if __name__ == "__main__":
    export_boundary_operator_derivation_sprint_outputs()
