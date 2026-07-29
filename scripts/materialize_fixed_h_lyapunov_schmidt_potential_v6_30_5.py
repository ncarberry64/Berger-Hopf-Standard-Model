"""Materialize the deterministic BHSM v6.30.5 evidence artifacts."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import fixed_h_lyapunov_schmidt_potential as potential


if __name__ == "__main__":
    for path in potential.materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
