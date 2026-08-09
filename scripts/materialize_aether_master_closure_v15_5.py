"""Materialize the BHSM v15.5 global master-closure package."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.aether_master_closure_v15_5 import materialize


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "artifacts"))
    args = parser.parse_args()
    for path in materialize(args.out):
        print(path)


if __name__ == "__main__":
    main()
