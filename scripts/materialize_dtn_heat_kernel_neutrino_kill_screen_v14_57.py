from __future__ import annotations

import argparse

from bhsm.interface.completion.dtn_heat_kernel_neutrino_kill_screen_v14_57 import materialize


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    for path in materialize(args.output):
        print(path)


if __name__ == "__main__":
    main()
