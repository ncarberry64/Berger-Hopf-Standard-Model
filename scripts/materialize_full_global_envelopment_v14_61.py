from __future__ import annotations
import argparse
from pathlib import Path
from bhsm.interface.completion.full_global_envelopment_v14_61 import materialize

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts")
    args = parser.parse_args()
    for path in materialize(Path(args.out)):
        print(path)

if __name__ == "__main__":
    main()
