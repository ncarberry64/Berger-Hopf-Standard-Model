from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    commands = [
        [sys.executable, "tools/check_runtime_asset_manifest_v1_7.py"],
        [sys.executable, "tools/map_wolfram_runtime_v1_7.py"],
        [sys.executable, "tools/install_or_map_feynrules_v1_7.py"],
        [sys.executable, "tools/install_or_map_madgraph_v1_7.py"],
        [sys.executable, "tools/export_institutional_hep_handoff_manifest_v1_7.py"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

