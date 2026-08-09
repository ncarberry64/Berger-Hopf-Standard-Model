"""Materialize the deterministic BHSM v11.6 completion artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.completion.completion_gate_v11_6 import materialize


if __name__ == "__main__":
    for output in materialize():
        print(output)
