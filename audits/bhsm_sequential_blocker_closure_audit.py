"""Regenerate the BHSM sequential blocker closure audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_sequential_blocker_closure import export_sequential_blocker_outputs


if __name__ == "__main__":
    export_sequential_blocker_outputs()
