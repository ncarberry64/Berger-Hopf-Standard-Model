import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    "BHSM_cp_o_int_sprint_c_manifest_v0_6.json",
    "BHSM_cp_o_int_field_action_report_v0_6.json",
    "BHSM_cp_o_int_field_action_stages_v0_6.json",
    "BHSM_cp_o_int_action_candidate_v0_6.json",
    "BHSM_cp_o_int_production_eligibility_v0_6.json",
    "BHSM_cp_o_int_formula_registry_update_v0_6.json",
    "BHSM_cp_o_int_registry_update_proposal_v0_6.json",
    "BHSM_cp_o_int_sprint_c_claim_policy_v0_6.json",
)


def test_sprint_c_artifacts_parse_and_preserve_nonproduction_status():
    payloads = {name: json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8")) for name in NAMES}
    report = payloads["BHSM_cp_o_int_field_action_report_v0_6.json"]
    assert report["candidate_status"] == "AVAILABLE_SYMBOLIC_CANDIDATE"
    assert report["status_after"] == "OPEN_MISSING_ACTION_SOURCE"
    assert report["production_eligible"] is False
    assert report["runtime_export_eligible"] is False
    proposal = payloads["BHSM_cp_o_int_registry_update_proposal_v0_6.json"]
    assert proposal["promotions_applied"] == []


def test_frozen_predictions_remain_exact():
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    }
    for path, digest in expected.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
