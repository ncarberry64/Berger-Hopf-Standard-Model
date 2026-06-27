from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.neutrino_propagation import ARTIFACT_PATHS


ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def load(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_all_v09_artifacts_exist_and_parse() -> None:
    assert len(ARTIFACT_PATHS) == 8
    assert all(load(path) for path in ARTIFACT_PATHS.values())
    manifest = load(ARTIFACT_PATHS["manifest"])
    assert manifest["status"] == "CONDITIONAL_NUMERICAL_CLOSURE_CANDIDATE"
    assert manifest["numerical_closure"] == "dimensionless-only"
    assert manifest["frozen_predictions_changed"] is False


def test_neutrino_artifacts_use_no_empirical_derivation_inputs() -> None:
    theorem = load(ARTIFACT_PATHS["theorem"])
    assert theorem["empirical_derivation_inputs_used"] is False
    assert theorem["reference_values_used_as_theorem_inputs"] is False
    assert theorem["electron_neutrino_upper_limit_used_as_derivation_input"] is False
    assert theorem["w_mass_used_as_theorem_input"] is False


def test_frozen_prediction_hashes_remain_exact() -> None:
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
