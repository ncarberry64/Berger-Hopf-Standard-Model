from __future__ import annotations

import argparse

from bhsm.interface.completion.round_collar_spectral_baseline_v14_58 import materialize


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    for path in materialize(args.output):
        print(path)


if __name__ == "__main__":
    main()
