from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.full_completion import ARTIFACT_PATHS, REQUIRED_STATEMENTS


ROOT = Path(__file__).resolve().parents[1]
FROZEN_HASHES = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_all_completion_artifacts_exist_and_parse() -> None:
    assert len(ARTIFACT_PATHS) == 7
    for path in ARTIFACT_PATHS.values():
        assert json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_required_claim_boundaries_are_public_and_exact() -> None:
    status = (ROOT / "docs/full_completion_status.md").read_text(encoding="utf-8")
    for statement in REQUIRED_STATEMENTS:
        assert statement in status
    combined = "\n".join(
        (ROOT / path).read_text(encoding="utf-8").lower()
        for path in (
            "docs/full_completion_blocker_ledger.md",
            "docs/full_completion_priority_map.md",
            "docs/full_completion_selected_target.md",
            "docs/full_completion_status.md",
        )
    )
    for forbidden in (
        "bhsm is fully complete",
        "bhsm is empirically validated",
        "raw neutral kernel is positive semidefinite",
        "physical ev/gev neutrino mass has been derived",
        "feynrules ready",
        "madgraph ready",
    ):
        assert forbidden not in combined


def test_frozen_predictions_remain_unchanged() -> None:
    for path, expected in FROZEN_HASHES.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
