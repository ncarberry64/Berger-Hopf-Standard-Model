#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.relative_anomaly_tensor_current_v14_53 import (  # noqa: E402
    materialize,
)


def main() -> int:
    for path in materialize(ROOT / "artifacts"):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
