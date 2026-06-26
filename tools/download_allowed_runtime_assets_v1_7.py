from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_o_common import ROOT, download_attempts, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt-downloads", action="store_true")
    parser.add_argument("--output", default=str(ROOT / "artifacts" / "BHSM_runtime_download_attempts_v1_7.json"))
    args = parser.parse_args()
    write_json(Path(args.output), download_attempts(args.attempt_downloads))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

