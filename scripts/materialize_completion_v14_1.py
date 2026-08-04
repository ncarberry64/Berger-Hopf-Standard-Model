from __future__ import annotations

import argparse
from pathlib import Path

from bhsm.interface.completion.eta_su3_connection_fork_v14_1 import materialize


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize the BHSM v14.1 eta/SU3 fork audit.")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    for path in materialize(args.output_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
