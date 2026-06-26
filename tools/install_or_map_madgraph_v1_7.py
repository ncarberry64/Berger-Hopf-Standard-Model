from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_o_common import ROOT, madgraph_installation_status, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "artifacts" / "BHSM_madgraph_installation_status_v1_7.json"))
    args = parser.parse_args()
    write_json(Path(args.output), madgraph_installation_status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

