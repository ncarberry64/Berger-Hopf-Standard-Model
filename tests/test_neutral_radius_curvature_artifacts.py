from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.neutrino_scale import RADIUS_CURVATURE_ARTIFACT_PATHS


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def load(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_all_radius_curvature_artifacts_exist_and_parse() -> None:
    assert len(RADIUS_CURVATURE_ARTIFACT_PATHS) == 7
    assert all(load(path) for path in RADIUS_CURVATURE_ARTIFACT_PATHS.values())
    manifest = load(RADIUS_CURVATURE_ARTIFACT_PATHS["manifest"])
    assert manifest["status"] == "DIMENSIONFUL_MASS_NOT_AVAILABLE"
    assert manifest["dimensionful_mass_output_produced"] is False


def test_frozen_prediction_hashes_remain_exact() -> None:
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected

