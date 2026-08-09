from __future__ import annotations
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.action_attachment_wentzell_v14_67 import materialize


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ROOT / "artifacts"))
    args = parser.parse_args()
    for p in materialize(Path(args.out)):
        print(p)


if __name__ == "__main__":
    main()
