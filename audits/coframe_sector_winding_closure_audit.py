"""Regenerate the coframe multiplier and sector winding closure audit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coframe_sector_winding_closure import export_coframe_sector_winding_outputs


if __name__ == "__main__":
    export_coframe_sector_winding_outputs()
