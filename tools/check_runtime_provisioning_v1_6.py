from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_n_common import ROOT, runtime_report, write_json


DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_runtime_provisioning_report_v1_6.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    write_json(Path(args.output), runtime_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

