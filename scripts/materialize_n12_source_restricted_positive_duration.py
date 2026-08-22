"""Materialize the N12 source-restricted positive-duration theorem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bhsm.interface.n12_source_restricted_positive_duration import (
    source_restricted_positive_duration_theorem,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "artifacts/n12_source_restricted_positive_duration/"
            "BHSM_N12_SOURCE_RESTRICTED_POSITIVE_DURATION_THEOREM.json"
        ),
    )
    args = parser.parse_args()
    result = source_restricted_positive_duration_theorem()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
