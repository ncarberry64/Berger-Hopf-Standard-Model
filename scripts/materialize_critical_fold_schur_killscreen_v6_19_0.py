"""Materialize deterministic BHSM v6.19.0 artifacts."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bhsm.interface.critical_fold_schur_killscreen import materialize_artifacts  # noqa: E402

if __name__ == "__main__":
    for path in materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
