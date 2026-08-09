"""Materialize the deterministic 2026-08-03 Downloads review."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.download_progress_review_2026_08_03 import materialize


if __name__ == "__main__":
    print(materialize().relative_to(ROOT))
