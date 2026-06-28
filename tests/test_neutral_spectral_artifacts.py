from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.neutrino_spectral import ARTIFACT_PATHS


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_neutral_spectral_artifacts_exist_and_parse() -> None:
    assert len(ARTIFACT_PATHS) == 8
    payloads = [json.loads((ROOT / path).read_text(encoding="utf-8")) for path in ARTIFACT_PATHS.values()]
    assert all(payloads)
    report = json.loads((ROOT / ARTIFACT_PATHS["report"]).read_text(encoding="utf-8"))
    assert report["dimensionful_mass_available"] is False
    assert report["frozen_predictions_changed"] is False


def test_frozen_prediction_hashes_are_unchanged() -> None:
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected

