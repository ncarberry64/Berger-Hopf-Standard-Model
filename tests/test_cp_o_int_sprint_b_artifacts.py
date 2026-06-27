import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    "BHSM_cp_o_int_sprint_b_manifest_v0_5.json",
    "BHSM_cp_o_int_attachment_report_v0_5.json",
    "BHSM_cp_o_int_stage_evaluation_v0_5.json",
    "BHSM_cp_o_int_proof_gates_v0_5.json",
    "BHSM_cp_o_int_registry_update_proposal_v0_5.json",
    "BHSM_cp_o_int_formula_registry_update_v0_5.json",
    "BHSM_cp_o_int_claim_policy_v0_5.json",
)


def test_sprint_b_artifacts_exist_parse_and_do_not_promote():
    payloads = {name: json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8")) for name in NAMES}
    report = payloads["BHSM_cp_o_int_attachment_report_v0_5.json"]
    assert report["status_after"] == "OPEN_MISSING_INTERACTION_ATTACHMENT"
    assert report["promoted"] is False
    assert report["empirical_derivation_inputs_used"] is False
    proposal = payloads["BHSM_cp_o_int_registry_update_proposal_v0_5.json"]
    assert proposal["promotions_applied"] == []
    assert proposal["runtime_gates_changed"] is False


def test_frozen_prediction_hashes_are_unchanged():
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    }
    for path, digest in expected.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
