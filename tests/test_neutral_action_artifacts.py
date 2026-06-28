from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.neutrino_action import ARTIFACT_PATHS


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_neutral_action_artifacts_exist_and_parse() -> None:
    assert len(ARTIFACT_PATHS) == 9
    for path in ARTIFACT_PATHS.values():
        assert json.loads((ROOT / path).read_text(encoding="utf-8"))
    report = json.loads((ROOT / ARTIFACT_PATHS["report"]).read_text(encoding="utf-8"))
    assert report["spectral_closure"]["dimensionful_mass_available"] is False
    assert report["response_cone"]["complete_action_derived"] is False


def test_frozen_predictions_remain_unchanged() -> None:
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected

