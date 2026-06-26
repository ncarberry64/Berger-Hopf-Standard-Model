from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_o_common import ROOT, phase_three_o_gate_status, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "artifacts" / "BHSM_phase_three_o_gate_status_v1_7.json"))
    args = parser.parse_args()
    write_json(Path(args.output), phase_three_o_gate_status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

