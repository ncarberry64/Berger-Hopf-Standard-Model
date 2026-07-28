"""Materialize deterministic BHSM v6.30.0 potential/mass artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.fold_potential_mass import materialize_artifacts  # noqa: E402


def main() -> int:
    for path in materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
