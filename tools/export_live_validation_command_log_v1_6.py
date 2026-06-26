from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_n_common import ROOT, phase_three_n_results, write_json


DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_live_validation_command_log_v1_6.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    results = phase_three_n_results(execute=False)
    write_json(Path(args.output), results["command_log"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

