import hashlib
import json
import sys
from math import isclose, sqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import oriented_jet_heat_response_audit as jet


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
FROZEN_HASHES = {
    ROOT / "docs" / "frozen_predictions.md": (
        "9EA147C56537520C86D3C4F9B864C6BA98BAC9E64931EDAE96449F3B335A36C4"
    ),
    ROOT / "docs" / "frozen_predictions.json": (
        "F38210E0689871A25A9D5B0A1A4239883B7240CD7D0E25CDCF4C8CAB72A2CBE7"
    ),
}


def load_artifact(name: str) -> dict:
    return json.loads((ROOT / "artifacts" / name).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_berger_geometry_values_are_frozen_and_formulaic():
    a = jet.berger_a()
    assert isclose(a, 137.035999084 / (12.0 * jet.pi**2), rel_tol=0, abs_tol=1e-15)
    assert jet.lambda_berger(0, a) == 0.0
    assert isclose(jet.lambda_berger(1, a), 1.0 + a**-2, rel_tol=0, abs_tol=1e-15)
    assert isclose(jet.lambda_berger(2, a), 2.0 + 4.0 * a**-2, rel_tol=0, abs_tol=1e-15)
    assert isclose(jet.b20_magnitude(a), sqrt(2.0 + a**-4), rel_tol=0, abs_tol=1e-15)


def test_oriented_operator_uses_negative_b20_orientation():
    op = jet.oriented_jet_heat_operator(jet.berger_a())
    assert op["b20_orientation"] == "negative"
    assert op["convention"] == "positive_curvature_cost_L_Berger=-r^2 Delta_Berger"
    first = op["first_order_operator"]
    assert first[0][2] < 0
    assert first[1][1] == -op["Lambda_1"]
    assert first[2][2] == -op["Lambda_2"]


def test_response_sign_classifier_covers_required_verdicts():
    assert jet.classify_response_sign((-3.0, -2.0, -1.0)) == jet.JET_HEAT_STRENGTHENS_HIERARCHY
    assert jet.classify_response_sign((-1.0, -2.0, -3.0)) == jet.JET_HEAT_COMPRESSES_HIERARCHY
    assert jet.classify_response_sign((0.0, 0.0, 0.0)) == jet.JET_HEAT_NEUTRAL
    assert jet.classify_response_sign((-1.0, -3.0, -2.0)) == jet.JET_HEAT_MIXED_RESPONSE


def test_a_local_and_a_background_artifacts_preserve_guardrails():
    for name in (
        "oriented_jet_heat_response_audit_A_local_v1.json",
        "oriented_jet_heat_response_audit_A_background_identity_v1.json",
    ):
        payload = load_artifact(name)
        assert payload["public_status"] == PUBLIC_STATUS
        assert payload["official_predictions_changed"] is False
        assert payload["tau_fit_to_masses"] is False
        assert payload["sigma_fit_to_masses"] is False
        assert payload["observed_masses_used"] is False
        assert payload["CKM_PMNS_used"] is False
        assert payload["charged_precision_closure"] == "OPEN"
        assert payload["response_condition"] == "q_e < q_mu < q_tau"


def test_charged_lepton_clean_geometry_response_strengthens_hierarchy():
    payload = load_artifact("oriented_jet_heat_response_audit_A_background_identity_v1.json")
    lepton = payload["sector_responses"]["lepton"]
    assert lepton["q_e"] < lepton["q_mu"] < lepton["q_tau"]
    assert lepton["sector_verdict"] == jet.JET_HEAT_STRENGTHENS_HIERARCHY
    assert payload["oriented_jet_heat_response"] == "STRUCTURALLY_SUPPORTED_CANDIDATE"
    assert payload["stack_verdict"] == jet.STACK_JET_HEAT_SUPPORTED


def test_open_gate_preserves_charged_precision_open_and_k_collar_rejection():
    payload = load_artifact("full_BHSM_open_gate_ledger_v2.json")
    statuses = payload["statuses"]
    assert statuses["oriented_jet_heat_response_audit"] == "RAN"
    assert statuses["charged_lepton_clean_geometry_gate"] == "RAN"
    assert statuses["tau_from_boundary_geometry"] == "OPEN_LOCALIZABLE"
    assert statuses["tau_from_mass_fit"] == "FORBIDDEN"
    assert statuses["sigma_from_boundary_geometry"] == "OPEN_LOCALIZABLE"
    assert statuses["sigma_from_mass_fit"] == "FORBIDDEN"
    assert statuses["charged_precision_closure"] == "OPEN"
    assert statuses["minimal_diagonal_K_collar_route"] == "REJECTED_AS_PRIMARY_BY_RESPONSE_AUDIT"
    assert statuses["K_collar_stack_verdict"] == "STACK_COLLAR_REJECTED_AS_PRIMARY"


def test_source_does_not_import_empirical_closure_modules():
    text = (ROOT / "src" / "oriented_jet_heat_response_audit.py").read_text(encoding="utf-8")
    blocked = (
        "prediction_ledger",
        "residual_audit",
        "EMPIRICAL_MASS_RATIOS",
        "EMPIRICAL",
        "CKM data",
        "PMNS data",
        "target_ratio",
    )
    for token in blocked:
        assert token not in text


def test_frozen_prediction_files_unchanged():
    for path, expected in FROZEN_HASHES.items():
        assert sha256(path) == expected
