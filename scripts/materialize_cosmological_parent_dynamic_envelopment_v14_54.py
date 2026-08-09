from __future__ import annotations

import argparse

from bhsm.interface.completion.cosmological_parent_dynamic_envelopment_v14_54 import materialize


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    for path in materialize(args.output):
        print(path)


if __name__ == "__main__":
    main()
