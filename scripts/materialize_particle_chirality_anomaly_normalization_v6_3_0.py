"""Materialize deterministic BHSM v6.3.0 particle/chirality artifacts."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.particle_chirality_anomaly_normalization import (  # noqa: E402
    materialize_artifacts,
)


if __name__ == "__main__":
    for artifact in materialize_artifacts(ROOT):
        print(artifact.relative_to(ROOT).as_posix())
