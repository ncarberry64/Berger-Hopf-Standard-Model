"""Regenerate the BHSM boundary-action closure candidate audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from boundary_action_closure_candidate import export_boundary_action_candidate_outputs


if __name__ == "__main__":
    export_boundary_action_candidate_outputs()
