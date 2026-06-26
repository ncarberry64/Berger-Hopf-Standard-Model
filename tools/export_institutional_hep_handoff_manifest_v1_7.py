from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_o_common import ROOT, all_artifacts, write_all_artifacts, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "artifacts"))
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    if output_dir == ROOT / "artifacts":
        write_all_artifacts()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, payload in all_artifacts().items():
            write_json(output_dir / name, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

