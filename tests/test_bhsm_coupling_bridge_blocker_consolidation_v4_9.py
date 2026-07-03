import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "BHSM_coupling_bridge_blocker_consolidation_v4_9.json"
V47 = ROOT / "artifacts" / "BHSM_gauge_coupling_action_attachment_killscreen_v4_7.json"
V48 = ROOT / "artifacts" / "BHSM_ckm_relative_current_normalization_killscreen_v4_8.json"
DOC = ROOT / "docs" / "bhsm_coupling_bridge_blocker_consolidation_v4_9.md"


def load(path=ARTIFACT):
    return json.loads(path.read_text(encoding="utf-8"))


def test_consolidation_verdict_is_exact_and_dependencies_are_locked():
    payload = load()
    assert payload["verdict"] == "COUPLING_BRIDGE_BLOCKED_PENDING_ACTION_PRINCIPLE"
    assert payload["depends_on"]["v4_7"] == "ACTION_ATTACHMENT_BLOCKED"
    assert payload["depends_on"]["v4_8"] == "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED"
    assert load(V47)["verdict"] == "ACTION_ATTACHMENT_BLOCKED"
    assert load(V48)["verdict"] == "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED"


def test_spectral_density_remains_candidate_not_physical_alpha():
    payload = load()
    assert "lambda_i=w_i/(6*pi^2) is a coherent conditional spectral covariance candidate" in payload["validated"]
    assert "lambda_i=alpha_i is not derived" in payload["invalidated_or_downgraded"]
    assert "alpha_2=lambda_2 is not derived" in payload["invalidated_or_downgraded"]
    assert "c_rel^2=4*pi is not derived" in payload["invalidated_or_downgraded"]


def test_downstream_coupling_ckm_running_and_completion_remain_open():
    payload = load()
    required = {
        "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
        "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "OPEN_MISSING_ALPHA2_ACTION_DERIVATION",
        "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        "CKM_EXPONENT_NOT_DERIVED",
        "OPEN_MISSING_SPECTRAL_CORRECTION_Z_i",
        "OPEN_MISSING_ACTION_SELECTED_RHO_i_OF_MU",
        "FULL_BHSM_NOT_COMPLETE",
    }
    assert required.issubset(payload["open_gates"])
    assert "physical running" in payload["still_open"]
    assert "full BHSM completion" in payload["still_open"]


def test_do_not_reopen_guardrail_covers_every_false_closure():
    blocked = set(load()["do_not_reopen_without_new_principle"])
    assert {
        "lambda_i=alpha_i",
        "alpha_2=lambda_2",
        "c_rel^2=4*pi",
        "g2_BH action derivation",
        "CKM coefficient value derivation",
        "CKM exponent derivation",
        "physical running from leading Weyl density",
    }.issubset(blocked)


def test_hindsight_document_has_all_three_result_classes():
    text = DOC.read_text(encoding="utf-8")
    assert "### Validated" in text
    assert "### Invalidated / downgraded" in text
    assert "### Still open" in text
    assert "w=(1,2,7)" in text
    assert "not a gauge-boson count" in text
    assert "full BHSM completion" in text


def test_pivot_is_ckm_transport_not_coupling_normalization():
    payload = load()
    assert payload["recommended_pivot"] == "CKM relative transport / mixing geometry transcription, not gauge coupling normalization"
    assert payload["operational_phase"] == "CKM_RELATIVE_TRANSPORT_TRANSCRIPTION"
    assert len(payload["next_work"]) == 4
    assert "keep weak coupling coefficients separate from CKM transport" in payload["next_work"]


def test_new_consolidation_surfaces_do_not_claim_forbidden_closures():
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ARTIFACT, DOC)
    )
    forbidden = (
        "lambda_i=alpha_i is derived",
        "alpha_2=lambda_2 is derived",
        "c_rel^2=4*pi is derived",
        "g2_BH is action-derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
        "physical running is derived from leading Weyl density",
        "full BHSM is complete",
        "w=(1,2,7) are gauge-boson counts",
        "CKM-relative CP^1/S^2 4*pi normalization is artifact-derived",
    )
    assert not any(phrase in text for phrase in forbidden)
    assert "COUPLING_BRIDGE_BLOCKED_PENDING_ACTION_PRINCIPLE" in text


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
