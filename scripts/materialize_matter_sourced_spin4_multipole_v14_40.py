from __future__ import annotations

import argparse
from pathlib import Path

from bhsm.interface.completion.matter_sourced_spin4_multipole_v14_40 import materialize


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    for path in materialize(args.output_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
