"""Materialize deterministic BHSM v6.30.7 scalar quartic audit artifacts."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.scalar_wall_quartic_source import materialize


if __name__ == "__main__":
    for output in materialize(ROOT):
        print(output.relative_to(ROOT).as_posix())
