import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "BHSM_rare_b_afb_zero_forward_prediction_v5_0.json"
DOC = ROOT / "docs" / "bhsm_rare_b_afb_zero_forward_prediction_v5_0.md"
STATUS = ROOT / "STATUS.md"
CLAIMS = ROOT / "CLAIMS.md"

PRIMARY_VERDICTS = {
    "RARE_B_AFB_ZERO_PREDICTION_DERIVED",
    "RARE_B_AFB_ZERO_PREDICTION_CONDITIONAL",
    "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
}
SECONDARY_VERDICTS = {
    "RARE_B_MICROPLATEAU_NODE_PREDICTION_DERIVED",
    "RARE_B_MICROPLATEAU_NODE_PREDICTION_CONDITIONAL",
    "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED",
}


def load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def combined_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ARTIFACT, DOC)
    )


def test_artifact_has_allowed_primary_and_secondary_verdicts():
    payload = load()
    assert payload["primary_verdict"] in PRIMARY_VERDICTS
    assert payload["secondary_verdict"] in SECONDARY_VERDICTS


def test_primary_verdict_fail_closed_rules_are_satisfied():
    payload = load()
    prediction = payload["bhsm_prediction"]
    if payload["primary_verdict"] == "RARE_B_AFB_ZERO_PREDICTION_DERIVED":
        assert prediction["q0_squared_GeV2"] is not None or (
            prediction["dimensionless_coordinate"] is not None
            and prediction["physical_q2_bridge"] is not None
        )
        assert prediction["falsification_criterion"]
    elif payload["primary_verdict"] == "RARE_B_AFB_ZERO_PREDICTION_CONDITIONAL":
        assert payload["open_gates"]
    else:
        assert prediction["prediction_claimed"] is False
        assert "No forward q0^2 prediction is claimed." in prediction["blocked_statement"]
        assert prediction["q0_squared_GeV2"] is None
        assert prediction["dimensionless_coordinate"] is None


def test_secondary_verdict_requires_exact_nodes_for_prediction():
    payload = load()
    micro = payload["microplateau_prediction"]
    if payload["secondary_verdict"] == "RARE_B_MICROPLATEAU_NODE_PREDICTION_DERIVED":
        assert micro["node_coordinates"]
    else:
        assert micro["node_coordinates"] == []
        assert micro["qualitative_teeth_language_is_not_prediction"] is True
        assert "not a BHSM prediction" in micro["blocked_statement"]


def test_observable_interface_and_no_fit_discipline_are_explicit():
    payload = load()
    interface = payload["observable_interface"]
    assert interface["decay"] == "B0 -> K*0 mu+ mu-"
    assert interface["transition"] == "b -> s mu+ mu-"
    assert interface["zero_condition"] == "A_FB(q0^2)=0"
    assert interface["q2_units"] == "GeV^2"
    assert payload["bhsm_prediction"]["no_fit_statement"] is True
    assert payload["rare_b_data_fitting_used"] is False
    assert "not treated as uncertainty-free" in interface["benchmark_note"]


def test_audit_propositions_match_blocked_killscreen():
    props = load()["audit_propositions"]
    assert props["A_b_to_s_mumu_map"] == "blocked"
    assert props["B_afb_null_balance_condition"] == "blocked"
    assert props["C_numeric_q0_squared_without_fit"] == "blocked"
    assert props["D_exact_dimensionless_null_coordinate_without_q2_bridge"] == "false"
    assert props["E_q0_depends_on_blocked_gauge_coupling_normalization"] == "unknown"
    assert props["F_microplateau_exact_node_coordinates"] == "blocked"
    assert props["G_nodes_from_geometry_not_fitted_residuals"] == "blocked"
    assert props["H_frozen_predictions_changed"] is False


def test_required_open_gates_and_preserved_blockers_are_present():
    gates = set(load()["open_gates"])
    assert {
        "RARE_B_AFB_ZERO_PREDICTION_BLOCKED",
        "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED",
        "OPEN_MISSING_RARE_B_OBSERVABLE_MAP",
        "OPEN_MISSING_B_TO_S_MUMU_TRANSITION_OPERATOR",
        "OPEN_MISSING_AFB_NULL_BALANCE_EQUATION",
        "OPEN_MISSING_RARE_B_Q2_PHYSICAL_BRIDGE",
        "OPEN_MISSING_WILSON_COEFFICIENT_INTERFACE",
        "OPEN_MISSING_HADRONIC_FORM_FACTOR_INTERFACE",
        "OPEN_MISSING_EXACT_MICROPLATEAU_NODE_MAP",
        "COUPLING_BRIDGE_BLOCKED_PENDING_ACTION_PRINCIPLE",
        "ACTION_ATTACHMENT_BLOCKED",
        "CKM_RELATIVE_CURRENT_NORMALIZATION_BLOCKED",
        "OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT",
        "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "OPEN_MISSING_ALPHA2_ACTION_DERIVATION",
        "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        "CKM_EXPONENT_NOT_DERIVED",
        "FULL_BHSM_NOT_COMPLETE",
    }.issubset(gates)


def test_hindsight_sections_are_present_in_doc():
    text = DOC.read_text(encoding="utf-8")
    assert "### Validated" in text
    assert "### Invalidated / downgraded" in text
    assert "### Still open" in text
    assert "BHSM currently lacks an artifact-backed rare-B observable map" in text
    assert "Micro-plateau structure remains qualitative/exploratory" in text


def test_status_and_claim_ledgers_include_rare_b_blocked_boundary():
    status = STATUS.read_text(encoding="utf-8")
    claims = CLAIMS.read_text(encoding="utf-8")
    assert "RARE_B_AFB_ZERO_PREDICTION_BLOCKED" in status
    assert "OPEN_MISSING_RARE_B_OBSERVABLE_MAP" in status
    assert "OPEN_MISSING_AFB_NULL_BALANCE_EQUATION" in status
    assert "RARE_B_MICROPLATEAU_NODE_PREDICTION_BLOCKED" in claims
    assert "No forward `q0^2` prediction is claimed." in claims


def test_no_forbidden_rare_b_or_coupling_overclaims_are_introduced():
    text = combined_text()
    forbidden = (
        "BHSM predicts A_FB zero",
        "BHSM predicts q0^2",
        "BHSM predicts micro-plateaus",
        "rare-B data were used to fit the prediction",
        "gauge-coupling normalization is solved",
        "alpha_i=lambda_i is derived",
        "alpha_2=lambda_2 is derived",
        "g2_BH is action-derived",
        "CKM coefficient value is derived",
        "CKM exponent is derived",
        "full BHSM is complete",
        "LHCb endorses BHSM",
        "CMS endorses BHSM",
        "ATLAS endorses BHSM",
        "Belle II endorses BHSM",
        "QFT is falsified by BHSM",
    )
    assert not any(phrase in text for phrase in forbidden)


def test_frozen_predictions_crlf_and_official_logic_guards_remain_unchanged():
    payload = load()
    assert payload["frozen_predictions_changed"] is False
    assert payload["official_prediction_logic_changed"] is False
    assert payload["physics_model_logic_changed"] is False
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
        "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
    }
    for relative, digest in expected.items():
        raw = (ROOT / relative).read_bytes()
        if relative == "src/bhsm_model.py":
            assert b"\r\n" not in raw
        assert hashlib.sha256(raw).hexdigest() == digest
