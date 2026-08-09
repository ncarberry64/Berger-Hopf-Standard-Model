from __future__ import annotations

import argparse

from bhsm.interface.completion.exact_berger_dirac_cap_obstruction_v14_59 import materialize


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    for path in materialize(args.output):
        print(path)


if __name__ == "__main__":
    main()
