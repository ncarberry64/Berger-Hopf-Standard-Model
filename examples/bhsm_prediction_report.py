"""Print the deterministic offline BHSM reviewer report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import build_prediction_report  # noqa: E402


def main() -> None:
    report = build_prediction_report(
        anchor_particle="W_boson",
        particles=("W_boson", "electron_neutrino"),
        include_open_theorem_entries=True,
    )
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
