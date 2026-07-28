"""Materialize deterministic BHSM v6.20.0 lapse--Weyl artifacts."""

from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src"))

from bhsm.interface.critical_lapse_weyl_hessian import materialize_artifacts  # noqa: E402


if __name__ == "__main__":
    for path in materialize_artifacts(root):
        print(path.relative_to(root))
