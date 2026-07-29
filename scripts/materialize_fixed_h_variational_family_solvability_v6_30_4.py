"""Materialize deterministic BHSM v6.30.4 solvability artifacts."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import fixed_h_variational_family_solvability as solvability


def main() -> int:
    for path in solvability.materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
