from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = (
    "artifacts/BHSM_minimal_action_closure_manifest_v0_8.json",
    "artifacts/BHSM_minimal_action_report_v0_8.json",
    "artifacts/BHSM_cp_o_int_minimal_action_closure_v0_8.json",
    "artifacts/BHSM_x_ch_minimal_action_closure_v0_8.json",
    "artifacts/BHSM_neutrino_basis_scale_minimal_action_closure_v0_8.json",
    "artifacts/BHSM_minimal_action_registry_updates_v0_8.json",
    "artifacts/BHSM_minimal_action_claim_policy_v0_8.json",
    "artifacts/BHSM_author_ontology_v0_8.json",
)
FROZEN = {
    "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
    "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
}


def load(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_required_artifacts_parse_and_report_clean_statuses() -> None:
    assert all(load(path) for path in ARTIFACTS)
    manifest = load(ARTIFACTS[0])
    assert manifest["results"] == {
        "X_ch": "CONDITIONAL_ACTION_THEOREM",
        "cp_o_int": "ARTIFACT_BACKED",
        "neutrino_basis_scale": "CONDITIONAL_PROPAGATION_THEOREM",
    }
    assert manifest["promotions"] == ["X_ch", "neutrino_basis_scale"]
    assert manifest["author_ontology_status"] == "DISCOVERED"
    assert manifest["empirical_derivation_inputs_used"] is False
    assert manifest["reference_values_used_as_theorem_inputs"] is False
    assert manifest["pdg_values_used_as_theorem_inputs"] is False
    assert manifest["w_calibration_used_as_theorem_input"] is False


def test_runtime_and_production_flags_remain_unchanged() -> None:
    manifest = load(ARTIFACTS[0])
    registry = load("artifacts/BHSM_minimal_action_registry_updates_v0_8.json")
    assert manifest["production_physics_model_logic_changed"] is False
    assert manifest["external_hep_tools_required"] is False
    assert registry["runtime_gates_changed"] is False
    assert registry["frozen_predictions_changed"] is False


def test_frozen_prediction_hashes_are_exact() -> None:
    for path, expected in FROZEN.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
