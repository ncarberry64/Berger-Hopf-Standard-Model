from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.neutrino_scale import ARTIFACT_PATHS


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def load(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_all_neutral_scale_artifacts_exist_and_parse() -> None:
    assert len(ARTIFACT_PATHS) == 8
    assert all(load(path) for path in ARTIFACT_PATHS.values())
    manifest = load(ARTIFACT_PATHS["manifest"])
    assert manifest["status"] == "OPEN_MISSING_NEUTRAL_SCALE"
    assert manifest["dimensionful_scale_achieved"] is False


def test_scale_artifact_records_no_forbidden_inputs_and_no_mass_output() -> None:
    scale = load(ARTIFACT_PATHS["scale_law"])
    attempt = load(ARTIFACT_PATHS["mass_attempt"])
    assert scale["empirical_derivation_inputs_used"] is False
    assert scale["reference_values_used_as_theorem_inputs"] is False
    assert scale["electron_neutrino_limit_used_as_derivation_input"] is False
    assert scale["w_mass_used_as_theorem_input"] is False
    assert attempt["dimensionful_mass_output_produced"] is False


def test_frozen_prediction_hashes_remain_exact_after_scale_audit() -> None:
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected

