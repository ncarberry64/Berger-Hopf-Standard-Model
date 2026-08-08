#!/usr/bin/env python3
"""Materialize deterministic BHSM v14.35 Hopf-phase bifurcation artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from bhsm.interface.completion.hopf_phase_bifurcation_completion_gate_v14_35 import materialize


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    paths = materialize(args.output)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
