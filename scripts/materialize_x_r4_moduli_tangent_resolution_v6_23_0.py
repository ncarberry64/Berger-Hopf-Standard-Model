"""Materialize deterministic BHSM v6.23.0 X/R4 response artifacts."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import x_r4_moduli_tangent_resolution as resolution


if __name__ == "__main__":
    for artifact in resolution.materialize_artifacts(ROOT):
        print(artifact.relative_to(ROOT).as_posix())
