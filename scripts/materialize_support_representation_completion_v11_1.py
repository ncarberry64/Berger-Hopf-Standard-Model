"""Materialize deterministic BHSM v11.1 completion artifacts."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.final_completion_gate_v11_1 import materialize


if __name__ == "__main__":
    for artifact_path in materialize():
        print(artifact_path.relative_to(artifact_path.parents[1]))
