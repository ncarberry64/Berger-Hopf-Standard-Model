"""Regenerate the boundary operator derivation audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_full_completion_candidate import generate_all_completion_outputs


if __name__ == "__main__":
    generate_all_completion_outputs()
