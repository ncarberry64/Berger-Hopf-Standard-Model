"""Materialize the effective N12 continuum-inverse localization theorem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bhsm.interface.n12_effective_inverse_localization import (
    effective_inverse_localization,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "artifacts/n12_continuum_majorant_effectiveness/"
            "BHSM_N12_EFFECTIVE_INVERSE_LOCALIZATION.json"
        ),
    )
    args = parser.parse_args()
    result = effective_inverse_localization()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
