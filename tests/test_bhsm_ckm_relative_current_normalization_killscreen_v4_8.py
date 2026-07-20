import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "BHSM_ckm_relative_current_normalization_killscreen_v4_8.json"
V47_ARTIFACT = ROOT / "artifacts" / "BHSM_gauge_coupling_action_attachment_killscreen_v4_7.json"
DOC = ROOT / "docs" / "bhsm_ckm_relative_current_normalization_killscreen_v4_8.md"
VERDICTS = {
    "CKM_RELATIVE_CURRENT_NORMALIZATION_DERIVED",
    "CKM_RELATIVE_CURRENT_NORMALIZATION_CONDITIONAL_AXIOM",
    "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED",
}


def load(path=ARTIFACT):
    return json.loads(path.read_text(encoding="utf-8"))


def test_artifact_has_one_decisive_verdict():
    payload = load()
    assert payload["verdict"] in VERDICTS
    assert payload["verdict"] == "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED"
    assert payload["status"] == "WEAK_LAMBDA_TO_ALPHA2_BRIDGE_BLOCKED"
    assert len([verdict for verdict in VERDICTS if verdict == payload["verdict"]]) == 1


def test_bridge_equation_and_required_four_pi_condition_are_explicit():
    bridge = load()["weak_bridge"]
    assert bridge["lambda_2"] == "2/(6*pi^2)"
    assert bridge["amplitude_factorization"] == "A_ab = sqrt(lambda_2) * c_rel * V_ab"
    assert bridge["alpha_2_relation"] == "alpha_2 = [c_rel^2/(4*pi)] lambda_2"
    assert bridge["required_bridge"] == "c_rel^2 = 4*pi"
    assert bridge["derived"] is False


def test_blocked_verdict_records_missing_geometry_measure_and_current_norm():
    payload = load()
    assert payload["proposition_b"]["status"] == "UNSUPPORTED"
    assert payload["proposition_c"]["status"] == "UNSUPPORTED"
    assert payload["proposition_d"]["status"] == "UNSUPPORTED"
    assert payload["proposition_d"]["unknown_normalization_excluded"] is False
    assert "does not derive c_rel^2=4*pi" in payload["claim_boundary"]


def test_derived_or_axiomatic_verdicts_would_require_stronger_evidence():
    payload = load()
    if payload["verdict"] == "CKM_RELATIVE_CURRENT_NORMALIZATION_DERIVED":
        assert payload["proposition_c"]["status"] == "DERIVED"
        assert payload["proposition_d"]["derived"] is True
        assert payload["proposition_d"]["unknown_normalization_excluded"] is True
    elif payload["verdict"] == "CKM_RELATIVE_CURRENT_NORMALIZATION_CONDITIONAL_AXIOM":
        assert payload["minimal_unadopted_principle"]["status"] == "ASSUMED_NOT_DERIVED"
    else:
        assert payload["minimal_unadopted_principle"]["status"] == "NOT_PRESENT_NOT_ADOPTED_NOT_DERIVED"


def test_all_six_routes_preserve_the_block_and_sqrt2_separation():
    routes = {row["route"]: row for row in load()["routes_audited"]}
    assert len(routes) == 6
    assert routes["pairwise_su2_transition"]["result"] == "UNSUPPORTED_ANALOGY"
    assert routes["global_ckm_manifold"]["result"] == "UNSUPPORTED_NO_ACTION_SELECTED_MANIFOLD_OR_VOLUME"
    assert routes["charged_current_coefficient_convention"]["result"] == "FORM_ARTIFACT_BACKED_VALUE_OPEN"
    assert "sqrt(2)" in routes["charged_current_coefficient_convention"]["evidence"]
    assert routes["kill_screen"]["result"] == "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED"


def test_v47_and_all_downstream_statuses_remain_open():
    payload = load()
    assert load(V47_ARTIFACT)["verdict"] == "ACTION_ATTACHMENT_BLOCKED"
    assert "ACTION_ATTACHMENT_BLOCKED" in payload["open_gates"]
    assert "OPEN_MISSING_ALPHA2_ACTION_DERIVATION" in payload["open_gates"]
    assert payload["proposition_g"]["status"] == "OPEN_MISSING_G2_BH_ACTION_SOURCE"
    assert payload["proposition_h"]["status"] == "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE"
    assert payload["proposition_i"]["status"] == "CKM_EXPONENT_NOT_DERIVED"
    assert "FULL_BHSM_NOT_COMPLETE" in payload["open_gates"]


def test_doc_has_hindsight_and_no_downstream_overclaims():
    text = DOC.read_text(encoding="utf-8")
    for heading in ("**Validated:**", "**Invalidated / downgraded:**", "**Still open:**"):
        assert heading in text
    forbidden = (
        "all gauge couplings are derived",
        "g2_BH is action-derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
        "full BHSM is complete",
    )
    assert not any(phrase in text for phrase in forbidden)
    assert "1/sqrt(2)" in text
    assert "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED" in text


def test_frozen_predictions_and_official_logic_guards_are_unchanged():
    payload = load()
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
