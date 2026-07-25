"""Materialize deterministic BHSM v6.1.5 scalar-wall artifacts."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.scalar_wall_junction_audit import materialize_artifacts  # noqa: E402


if __name__ == "__main__":
    for artifact in materialize_artifacts(ROOT):
        print(artifact.relative_to(ROOT).as_posix())
