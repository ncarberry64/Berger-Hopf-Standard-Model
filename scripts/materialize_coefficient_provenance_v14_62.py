from __future__ import annotations
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
SRC = HERE / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.coefficient_provenance_quotient_v14_62 import materialize

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(HERE / "artifacts"))
    args = parser.parse_args()
    for p in materialize(args.output_dir):
        print(p)

if __name__ == "__main__":
    main()
