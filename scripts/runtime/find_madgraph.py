from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from phase_three_n_common import find_madgraph  # noqa: E402


def main() -> int:
    detected, path, version = find_madgraph()
    print(json.dumps({"detected": detected, "path": path, "version": version}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

