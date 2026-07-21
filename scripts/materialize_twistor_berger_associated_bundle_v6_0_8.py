"""Materialize deterministic BHSM v6.0.8 twistor-Berger artifacts."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.twistor_berger_associated_bundle import materialize_artifacts  # noqa: E402


if __name__ == "__main__":
    for artifact in materialize_artifacts(ROOT):
        print(artifact.relative_to(ROOT).as_posix())
