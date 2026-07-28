"""Materialize deterministic BHSM v6.22.0 obstruction artifacts."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.m4_x_metric_tangent_fold_schur import (  # noqa: E402
    materialize_artifacts,
)


if __name__ == "__main__":
    for path in materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
