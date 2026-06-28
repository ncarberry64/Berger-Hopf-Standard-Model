from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.neutrino_spectral import POSITIVITY_ARTIFACT_PATHS


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_all_neutral_positivity_artifacts_exist_and_parse() -> None:
    assert len(POSITIVITY_ARTIFACT_PATHS) == 8
    for path in POSITIVITY_ARTIFACT_PATHS.values():
        assert json.loads((ROOT / path).read_text(encoding="utf-8"))
    report = json.loads((ROOT / POSITIVITY_ARTIFACT_PATHS["report"]).read_text(encoding="utf-8"))
    assert report["raw_psd"] is False
    assert report["positivity_proven_without_thresholding"] is True
    assert report["counterexample_found"] is False


def test_frozen_predictions_remain_exact() -> None:
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected

