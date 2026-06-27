from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bhsm.interface.predictions import PredictionStatus, default_prediction_registry

ROOT = Path(__file__).resolve().parents[1]
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def test_registry_contains_required_entries_and_statuses() -> None:
    registry = default_prediction_registry()
    required = {
        "W_boson", "electron_neutrino", "CKM_matrix_BHSM", "PMNS_matrix_BHSM",
        "charged_boundary_response_matrix", "neutral_operator_kernel_BH",
        "cp_holonomy_phase_attachment", "minimal_collider_interface_subset",
        "feynrules_minimal_model", "ufo_export", "madgraph_smoke_test",
    }
    assert required <= set(registry.entries)
    assert registry.require("W_boson").can_be_calibration_anchor
    assert not registry.require("W_boson").independent_prediction_allowed
    assert registry.require("electron_neutrino").comparison_kind == "upper_limit"
    assert registry.require("CKM_matrix_BHSM").default_status is PredictionStatus.FROZEN_INTERNAL_PREDICTION
    assert registry.require("PMNS_matrix_BHSM").default_status is PredictionStatus.FROZEN_INTERNAL_PREDICTION
    for key in ("charged_boundary_response_matrix", "neutral_operator_kernel_BH", "cp_holonomy_phase_attachment"):
        assert registry.require(key).default_status is PredictionStatus.OPEN_THEOREM_REQUIRED
    for key in ("feynrules_minimal_model", "ufo_export", "madgraph_smoke_test"):
        assert registry.require(key).default_status is PredictionStatus.DISABLED_UNTIL_RUNTIME_VALIDATED


def test_registry_artifact_parses_and_matches_runtime_registry() -> None:
    payload = json.loads((ROOT / "artifacts/BHSM_prediction_registry_v0_1.json").read_text())
    runtime = default_prediction_registry().to_dict()
    assert payload == runtime
    assert "CALIBRATION_ANCHOR" in payload["status_taxonomy"]


def test_registry_policy_and_frozen_files_are_intact() -> None:
    policy = json.loads((ROOT / "artifacts/BHSM_prediction_registry_policy_v0_1.json").read_text())
    assert policy["frozen_predictions_changed"] is False
    assert policy["empirical_derivation_inputs_used"] is False
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
