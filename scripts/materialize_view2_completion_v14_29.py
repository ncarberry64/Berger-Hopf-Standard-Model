#!/usr/bin/env python3
"""Materialize the deterministic v14.29 View 2 artifact set."""

from __future__ import annotations

import argparse
from pathlib import Path

from bhsm.interface.completion.view2_completion_gate_v14_29 import materialize, status_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.status:
        print(status_text())
    else:
        for path in materialize(args.output):
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
