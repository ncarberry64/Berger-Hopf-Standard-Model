from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    return subprocess.run([sys.executable, "tools/check_phase_three_o_gate_status.py"], cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())

