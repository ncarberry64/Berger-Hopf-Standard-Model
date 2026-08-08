from __future__ import annotations

import argparse

from bhsm.interface.completion.pair_wake_neutrino_bvp_v14_55 import materialize


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    for path in materialize(args.output):
        print(path)


if __name__ == "__main__":
    main()
