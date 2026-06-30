"""Fail CI when the committed coordinate benchmark exceeds its precision gate."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_RESULTS = Path("artifacts/coordinate_benchmark/coordinate_benchmark_results.json")
DEFAULT_THRESHOLD = 1.0e-13


def maximum_numerical_delta(payload: dict[str, Any]) -> float:
    """Return the measured maximum absolute delta from the benchmark schema."""

    try:
        value = float(payload["correctness"]["maximum_absolute_difference"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("benchmark result lacks correctness.maximum_absolute_difference") from exc
    if not math.isfinite(value) or value < 0.0:
        raise ValueError("maximum numerical delta must be finite and nonnegative")
    return value


def verify_precision(path: Path, threshold: float = DEFAULT_THRESHOLD) -> float:
    """Validate equivalence metadata and return a delta within the threshold."""

    if not math.isfinite(threshold) or threshold <= 0.0:
        raise ValueError("precision threshold must be finite and positive")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("correctness", {}).get("all_kernels_equivalent") is not True:
        raise ValueError("benchmark does not mark all kernels equivalent")
    delta = maximum_numerical_delta(payload)
    if delta > threshold:
        raise ValueError(
            f"numerical drift ({delta:.17g}) exceeds allowable threshold ({threshold:.17g})"
        )
    return delta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = parser.parse_args()
    try:
        delta = verify_precision(args.results, args.threshold)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"PASS: precision gate verified ({delta:.3e} <= {args.threshold:.3e}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
