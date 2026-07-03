import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "BHSM_gauge_coupling_action_attachment_killscreen_v4_7.json"
DOC = ROOT / "docs" / "bhsm_gauge_coupling_action_attachment_killscreen_v4_7.md"
VERDICTS = {
    "ACTION_ATTACHMENT_DERIVED",
    "ACTION_ATTACHMENT_CONDITIONAL_AXIOM",
    "ACTION_ATTACHMENT_BLOCKED",
}


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_artifact_has_one_decisive_kill_screen_verdict():
    payload = load_artifact()
    assert payload["verdict"] in VERDICTS
    assert payload["verdict"] == "ACTION_ATTACHMENT_BLOCKED"
    assert payload["status"] == "SPECTRAL_GAUGE_COUPLING_ATTACHMENT_BLOCKED"
    assert len([value for value in VERDICTS if value == payload["verdict"]]) == 1


def test_blocked_verdict_distinguishes_spectral_lambda_from_physical_alpha():
    payload = load_artifact()
    assert payload["proposition_a"]["status"] == "CONDITIONAL_SPECTRAL_DENSITY_COVARIANCE_CANDIDATE"
    assert payload["proposition_c"]["status"] == "CONDITIONAL_CANDIDATE_NOT_DERIVED_FROM_EXISTING_ACTION"
    assert payload["proposition_d"]["status"] == "BLOCKED_MISSING_ACTION_ATTACHMENT"
    assert payload["proposition_d"]["derived"] is False
    assert payload["proposition_d"]["unknown_proportionality_constant_excluded"] is False
    assert "does not derive physical alpha_i" in payload["claim_boundary"]


def test_derived_verdict_would_require_a_complete_chain_without_missing_terms():
    payload = load_artifact()
    if payload["verdict"] == "ACTION_ATTACHMENT_DERIVED":
        assert payload["failed_or_missing"] == []
        assert payload["proposition_d"]["derived"] is True
        assert payload["proposition_d"]["unknown_proportionality_constant_excluded"] is True
    else:
        assert payload["failed_or_missing"]
        assert "proof that alpha_i=lambda_i rather than alpha_i=C lambda_i" in payload["failed_or_missing"]


def test_conditional_axiom_is_identified_but_not_adopted_or_misreported():
    payload = load_artifact()
    principle = payload["minimal_escape_principle"]
    assert principle["name"] == "Normalized Whitened Boundary Fluctuation Principle"
    assert principle["status"] == "NOT_PRESENT_NOT_ADOPTED_NOT_DERIVED"
    assert payload["verdict"] != "ACTION_ATTACHMENT_CONDITIONAL_AXIOM"


def test_escape_routes_fail_closed_at_action_attachment():
    routes = {row["route"]: row for row in load_artifact()["escape_routes"]}
    assert len(routes) == 6
    assert routes["existing_action_normalization"]["result"] == "BLOCKED"
    assert routes["gaussian_covariance"]["result"] == "REQUIRES_NEW_AXIOM_NOT_PRESENT_IN_BHSM_ACTION"
    assert routes["canonical_yang_mills_normalization"]["result"] == "BLOCKED_UNKNOWN_MATCHING_FACTOR"
    assert routes["spectral_action"]["result"] == "BLOCKED_NO_GAUGE_SPECTRAL_ACTION_COEFFICIENT"
    assert routes["kill_screen"]["result"] == "ACTION_ATTACHMENT_BLOCKED"


def test_downstream_g2_ckm_and_completion_statuses_remain_open():
    payload = load_artifact()
    assert payload["g2_BH_status"] == "OPEN_MISSING_G2_BH_ACTION_SOURCE"
    assert payload["ckm_value_status"] == "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"
    assert payload["ckm_exponent_status"] == "CKM_EXPONENT_NOT_DERIVED"
    assert payload["full_completion_status"] == "FULL_BHSM_NOT_COMPLETE"
    assert payload["proposition_e"]["derived"] is False
    assert payload["proposition_f"]["derived"] is False
    assert payload["proposition_g"]["derived"] is False


def test_doc_and_artifact_do_not_promote_forbidden_closures():
    text = DOC.read_text(encoding="utf-8") + "\n" + ARTIFACT.read_text(encoding="utf-8")
    forbidden = (
        "gauge couplings are fully derived",
        "g2_BH is action-derived",
        "CKM is derived",
        "full BHSM is complete",
        "lambda_i automatically equals alpha_i",
    )
    assert not any(phrase in text for phrase in forbidden)
    assert "ACTION_ATTACHMENT_BLOCKED" in text
    assert "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION" in text


def test_frozen_predictions_and_official_logic_guards_are_unchanged():
    payload = load_artifact()
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
