"""Materialize deterministic BHSM v6.26.0 threading/support artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.homogeneous_threading_support_verdict import (  # noqa: E402
    materialize_artifacts,
)


def main() -> int:
    for path in materialize_artifacts(ROOT):
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
